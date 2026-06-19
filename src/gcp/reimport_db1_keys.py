"""Fix the bridge keys on every DB1 (aviation-curriculum-v2) document, in place.

The live store is the source of truth for lesson CONTENT (its 184 docs already point at the
GCS element .md files). This tool only repairs the metadata: it pulls every doc, runs the
`schema.clean_keys` normalizer over reg_keys/doc_keys/keywords (stripping `**`, `[cite:]`,
parenthetical/chapter junk while KEEPING every real reference), fills the 12 empty Area IX
docs from their authored sidecars in pipeline/curriculum/new/, validates each entry through
CurriculumLessonSchema, and re-imports with INCREMENTAL reconciliation (upsert by id — same
ids + same content URIs = update, never a wipe).

GATED: dry run by default (writes a local JSONL + report, mutates nothing). --execute imports.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402
from utils.schema import (  # noqa: E402
    CurriculumStructData, normalize_key, is_garbage, coverage,
    is_document_level, to_document_level,
)

from google.cloud import discoveryengine_v1 as discoveryengine  # noqa: E402
from google.protobuf.json_format import MessageToDict  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

AREA_IX_SIDECARS = config.PROJECT_ROOT / "pipeline" / "curriculum" / "new"
OUT_JSONL = config.PROJECT_ROOT / "pipeline" / "curriculum" / "curriculum.jsonl"
GCS_URI = f"gs://{config.CURRICULUM_BUCKET}/v2/curriculum_v2_import.jsonl"


def clean_list(v):
    out = []
    for x in (v or []):
        k = normalize_key(x)
        if not is_garbage(k) and k not in out:
            out.append(k)
    return out


def augment_doc_keys(doc):
    """Keep every cleaned reference, and for any sub-document key (chapter/section) append its
    whole-document token so the lesson has a matchable bridge key. Order: references first, then
    appended document-level tokens. Idempotent and de-duped."""
    out = list(doc)
    for k in doc:
        if not is_document_level(k):
            dl = to_document_level(k)
            if dl and dl not in out:
                out.append(dl)
    return out


def build_entries():
    client = discoveryengine.DocumentServiceClient()
    parent = client.branch_path(
        project=config.GCP_PROJECT_ID, location=config.CURRICULUM_LOCATION,
        data_store=config.CURRICULUM_DATA_STORE_ID, branch="default_branch",
    )
    docs = list(client.list_documents(request=discoveryengine.ListDocumentsRequest(parent=parent, page_size=1000)))

    entries, report, problems = [], [], []
    for d in docs:
        sd = MessageToDict(d._pb.struct_data) if d._pb.struct_data else {}
        content_uri = d._pb.content.uri if d._pb.content and d._pb.content.uri else None

        reg = clean_list(sd.get("reg_keys"))
        doc = clean_list(sd.get("doc_keys"))
        kw = clean_list(sd.get("keywords"))

        # Fill empty Area IX from its authored sidecar
        if not doc:
            sidecar = AREA_IX_SIDECARS / f"{d.id}.json"
            if sidecar.exists():
                s = json.loads(sidecar.read_text(encoding="utf-8"))
                ssd = s.get("structData", s)
                doc = clean_list(ssd.get("doc_keys"))
                if not reg:
                    reg = clean_list(ssd.get("reg_keys"))

        doc = augment_doc_keys(doc)
        struct = {
            "acs_code": sd.get("acs_code", ""),
            "title": sd.get("title", ""),
            "type": sd.get("type", "lesson_chunk"),
            "ancestral_context": sd.get("ancestral_context", ""),
            "reg_keys": reg,
            "doc_keys": doc,
            "keywords": kw,
        }
        try:
            CurriculumStructData(**struct)
        except Exception as e:
            problems.append((d.id, str(e)))
            continue

        if not content_uri:
            problems.append((d.id, "no content URI on live doc"))
            continue

        entries.append({"id": d.id, "structData": struct,
                        "content": {"mimeType": "text/plain", "uri": content_uri}})
        cov, ref = coverage(doc)
        report.append((d.id, len(sd.get("doc_keys") or []), doc, cov, ref))
    return entries, report, problems


def summarize(entries, report, problems):
    covered = sum(1 for _, _, _, cov, _ in report if cov)
    refonly = sum(1 for _, _, d, cov, _ in report if d and not cov)
    print(f"Built {len(entries)} entries (target 184).")
    print(f"  {covered} lessons resolve to >=1 DB2-covered doc_key, {refonly} reference-only.")
    if problems:
        print(f"\n  {len(problems)} PROBLEM docs (excluded — need attention):")
        for did, msg in problems:
            print(f"    {did}: {msg}")
    print("\n  Sample before -> after (first 6 that changed):")
    shown = 0
    for did, raw_n, doc, cov, ref in report:
        if shown >= 6:
            break
        print(f"    {did}: doc_keys={doc}  covered={cov}  ref_only={ref}")
        shown += 1


def dry_run():
    entries, report, problems = build_entries()
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    print("=== DRY RUN — wrote local JSONL, no import ===")
    summarize(entries, report, problems)
    print(f"\n  JSONL: {OUT_JSONL} ({len(entries)} lines)")
    print("  Re-run with --execute to upload + INCREMENTAL-import into aviation-curriculum-v2.")


def execute():
    entries, report, problems = build_entries()
    if problems:
        print(f"ABORT: {len(problems)} problem docs — resolve before importing.")
        for did, msg in problems:
            print(f"  {did}: {msg}")
        sys.exit(1)
    # Repair via update_document (metadata-only, queue-free). The live docs already exist with
    # parsed content; we only replace the cleaned key fields in struct_data. This sidesteps the
    # serial ImportDocuments queue (and its non-cancellable jams) entirely.
    client = discoveryengine.DocumentServiceClient()
    parent = client.branch_path(
        project=config.GCP_PROJECT_ID, location=config.CURRICULUM_LOCATION,
        data_store=config.CURRICULUM_DATA_STORE_ID, branch="default_branch",
    )
    by_id = {e["id"]: e["structData"] for e in entries}
    updated, errs = 0, []
    for d in client.list_documents(request=discoveryengine.ListDocumentsRequest(parent=parent, page_size=1000)):
        st = by_id.get(d.id)
        if not st:
            continue
        d.struct_data.update({"reg_keys": st["reg_keys"], "doc_keys": st["doc_keys"], "keywords": st["keywords"]})
        try:
            client.update_document(discoveryengine.UpdateDocumentRequest(
                document=d, update_mask=field_mask_pb2.FieldMask(paths=["struct_data"])))
            updated += 1
        except Exception as e:  # noqa: BLE001
            errs.append((d.id, str(e)[:100]))
    print(f"Updated {updated}/{len(entries)} DB1 docs via update_document.")
    if errs:
        print(f"  {len(errs)} errors:")
        for did, msg in errs[:10]:
            print(f"    {did}: {msg}")
    summarize(entries, report, problems)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Repair DB1 bridge keys in place (gated).")
    ap.add_argument("--execute", action="store_true", help="Upload + INCREMENTAL import (default: dry run).")
    args = ap.parse_args()
    execute() if args.execute else dry_run()
