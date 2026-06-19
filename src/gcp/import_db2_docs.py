"""Add the staged FAA source PDFs to DB2 (aviation-library-v2) and apply document_tags.

Two live-write actions, both GATED behind --execute (default is a dry run that mutates nothing):
  1. Upload curriculum_components/faa_docs/*.pdf to the library bucket, then INCREMENTAL-import
     them into aviation-library-v2 (INCREMENTAL = upsert by id; the existing 16 docs are NOT
     touched — never FULL here, which would wipe the store).
  2. Patch `document_tags` onto EVERY DB2 document (existing 16 have none) using the shared
     extract_tags logic, so the bridge filter has a target.

Run `python src/gcp/import_db2_docs.py` first (dry run) and read the plan, then `--execute`.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402  (resolves creds + datastore IDs via .env)
from utils.db2_tags import extract_tags  # noqa: E402
from utils.schema import to_family, normalize_key, is_garbage, is_document_level  # noqa: E402

from google.cloud import storage, discoveryengine_v1 as discoveryengine  # noqa: E402
from google.protobuf.json_format import MessageToDict, ParseDict  # noqa: E402
from google.protobuf import field_mask_pb2, struct_pb2  # noqa: E402

FAA_DOCS_DIR = config.PROJECT_ROOT / "curriculum_components" / "faa_docs"
CURRICULUM_JSONL = config.PROJECT_ROOT / "pipeline" / "curriculum" / "curriculum.jsonl"
RKP_MANIFESTS = config.PROJECT_ROOT / "curriculum_components" / "rkp_manifests"
GCS_PREFIX = "v2"  # gs://aviationchat-library/v2/<filename>


def build_family_variants() -> dict[str, set[str]]:
    """Map each document-family -> the set of exact edition tokens the curriculum uses for it
    (e.g. 'FAA-H-8083-25' -> {'FAA-H-8083-25C'}). Read from the cleaned DB1 JSONL (run
    reimport_db1_keys.py first) and the RKP manifests. Used to make DB2 document_tags a rich
    superset so the app's EXACT `document_tags: ANY(...)` filter matches across edition suffixes."""
    fam: dict[str, set[str]] = {}

    def add(key: str):
        k = normalize_key(key)
        if is_garbage(k) or not is_document_level(k):
            return
        fam.setdefault(to_family(k), set()).add(k)

    if CURRICULUM_JSONL.exists():
        for line in CURRICULUM_JSONL.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            sd = json.loads(line).get("structData", {})
            for k in sd.get("doc_keys", []):
                add(k)
    for p in RKP_MANIFESTS.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in d.get("required_knowledge_points", []):
            for k in (r.get("bridge_keys") or []):
                add(k)
    return fam


def rich_tags(filename: str, fam_variants: dict[str, set[str]]) -> list[str]:
    """Exact filename token(s) + their family token(s) + every curriculum edition variant that
    maps to the same family, so an exact-match filter hits regardless of edition suffix."""
    base = extract_tags(filename)
    tags: set[str] = set(base)
    for t in base:
        f = to_family(t)
        tags.add(f)
        tags |= fam_variants.get(f, set())
    return sorted(tags)

# The 8 confirmed Tier-1 documents. category must satisfy LibraryStructData
# ({regulation, handbook, advisory_circular}); the ACS is filed as a handbook.
NEW_DOCS = [
    # AFH (FAA-H-8083-3C) is 273 MB > Vertex's 200,000,000-byte cap, so it's split into parts
    # (each <200 MB), all tagged FAA-H-8083-3C — the bridge filter matches any part.
    ("FAA-H-8083-3C (AFH part 1a).pdf",       "handbook",          "handbooks"),
    ("FAA-H-8083-3C (AFH part 1b).pdf",       "handbook",          "handbooks"),
    ("FAA-H-8083-3C (AFH part 2).pdf",        "handbook",          "handbooks"),
    ("FAA-H-8083-3C (AFH part 3).pdf",        "handbook",          "handbooks"),
    ("FAA-H-8083-15B (IFH).pdf",              "handbook",          "handbooks"),
    ("FAA-H-8083-1B (W&B).pdf",               "handbook",          "handbooks"),
    ("FAA-S-ACS-6C (Private Pilot ACS).pdf",  "handbook",          "handbooks"),
    ("AC 00-45H.pdf",                         "advisory_circular", "advisory_circulars"),
    ("AC 61-67C.pdf",                         "advisory_circular", "advisory_circulars"),
    ("AC 91-67.pdf",                          "advisory_circular", "advisory_circulars"),
    ("AC 90-48E.pdf",                         "advisory_circular", "advisory_circulars"),
]


def _poll(op, budget: int = 1500, interval: int = 20):
    """Poll an import LRO with progress, instead of a single hard 1800s block. Returns when done
    or the budget elapses (the op keeps running server-side either way)."""
    import time
    start = time.time()
    while not op.done() and time.time() - start < budget:
        m = op.metadata
        print(f"  ... running: success={getattr(m, 'success_count', '?')} "
              f"failure={getattr(m, 'failure_count', '?')} ({int(time.time() - start)}s)")
        time.sleep(interval)
    m = op.metadata
    print(f"  import done={op.done()} success={getattr(m, 'success_count', '?')} "
          f"failure={getattr(m, 'failure_count', '?')}")


def slug(filename: str) -> str:
    base = filename.replace(".pdf", "")
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", base.lower())).strip("_")


def build_new_entries(fam_variants: dict[str, set[str]]) -> list[dict]:
    entries = []
    for filename, category, subfolder in NEW_DOCS:
        title = filename.replace(".pdf", "")
        tags = rich_tags(filename, fam_variants)
        entries.append({
            "id": slug(filename),
            "structData": {
                "category": category,
                "title": title,
                "subfolder": subfolder,
                "filename": filename,
                "document_tags": tags,
            },
            "content": {
                "mimeType": "application/pdf",
                "uri": f"gs://{config.LIBRARY_BUCKET}/{GCS_PREFIX}/{filename}",
            },
        })
    return entries


def list_existing(client) -> list:
    parent = client.branch_path(
        project=config.GCP_PROJECT_ID, location=config.LIBRARY_LOCATION,
        data_store=config.LIBRARY_DATA_STORE_ID, branch="default_branch",
    )
    return list(client.list_documents(request=discoveryengine.ListDocumentsRequest(parent=parent, page_size=1000)))


def dry_run():
    fam = build_family_variants()
    entries = build_new_entries(fam)
    print("=== DRY RUN — no GCS upload, no import, no patch ===\n")
    if not CURRICULUM_JSONL.exists():
        print("  NOTE: pipeline/curriculum/curriculum.jsonl not found — run reimport_db1_keys.py first")
        print("        for full edition-variant tags. Showing base+manifest tags only.\n")
    print(f"NEW documents to add to {config.LIBRARY_DATA_STORE_ID} ({len(entries)}):")
    for e in entries:
        print(f"  {e['id']:34s} tags={e['structData']['document_tags']}")
        print(f"  {'':34s} <- {FAA_DOCS_DIR / e['structData']['filename']}")
        print(f"  {'':34s} -> {e['content']['uri']}")

    missing = [e for e in entries if not (FAA_DOCS_DIR / e["structData"]["filename"]).exists()]
    if missing:
        print(f"\n  ERROR: {len(missing)} staged PDFs missing on disk: {[m['structData']['filename'] for m in missing]}")

    client = discoveryengine.DocumentServiceClient()
    existing = list_existing(client)
    print(f"\nEXISTING {len(existing)} docs — document_tags to be patched in:")
    for d in existing:
        sd = MessageToDict(d._pb.struct_data) if d._pb.struct_data else {}
        has = sd.get("document_tags")
        tags = rich_tags(sd.get("filename", "") or sd.get("title", ""), fam)
        flag = "(already has)" if has else ""
        print(f"  {d.id:34s} {tags} {flag}")
    print(f"\nTotal after import: {len(existing) + len(entries)} docs, all tagged.")
    print("\nRe-run with --execute to apply. Then re-run scripts/derive_db2_vocabulary.py.")


def execute():
    fam = build_family_variants()
    entries = build_new_entries(fam)
    for e in entries:
        if not (FAA_DOCS_DIR / e["structData"]["filename"]).exists():
            print(f"ABORT: staged PDF missing: {e['structData']['filename']}")
            sys.exit(1)

    # 1. Upload PDFs to GCS
    gcs = storage.Client()
    bucket = gcs.bucket(config.LIBRARY_BUCKET)
    for e in entries:
        fn = e["structData"]["filename"]
        blob = bucket.blob(f"{GCS_PREFIX}/{fn}")
        if blob.exists():
            print(f"Skipping upload (already in GCS): {fn}")
            continue
        print(f"Uploading {fn} ...")
        blob.upload_from_filename(str(FAA_DOCS_DIR / fn))

    # 2. Create each new doc directly (create_document triggers async PDF parse). This bypasses
    #    the serial, non-cancellable ImportDocuments queue.
    client = discoveryengine.DocumentServiceClient()
    parent = client.branch_path(
        project=config.GCP_PROJECT_ID, location=config.LIBRARY_LOCATION,
        data_store=config.LIBRARY_DATA_STORE_ID, branch="default_branch",
    )
    created, skipped, errs = 0, 0, []
    for e in entries:
        sd = struct_pb2.Struct()
        ParseDict(e["structData"], sd)
        doc = discoveryengine.Document(
            struct_data=sd,
            content=discoveryengine.Document.Content(
                uri=e["content"]["uri"], mime_type="application/pdf"),
        )
        try:
            client.create_document(request=discoveryengine.CreateDocumentRequest(
                parent=parent, document=doc, document_id=e["id"]))
            created += 1
            print(f"  created {e['id']} tags={e['structData']['document_tags']}")
        except Exception as ex:  # noqa: BLE001
            msg = str(ex).lower()
            if "already_exists" in msg or "already exists" in msg or "same name" in msg or "409" in msg:
                skipped += 1
                print(f"  exists, skipping {e['id']}")
            else:
                errs.append((e["id"], str(ex)[:140]))
    print(f"Created {created}, existed {skipped}, errors {len(errs)} of {len(entries)}.")
    for did, msg in errs:
        print(f"   {did}: {msg}")

    # 3. Patch document_tags onto every DB2 doc that lacks them
    patched = 0
    for d in list_existing(client):
        sd = MessageToDict(d._pb.struct_data) if d._pb.struct_data else {}
        if sd.get("document_tags"):
            continue
        tags = rich_tags(sd.get("filename", "") or sd.get("title", ""), fam)
        if not tags:
            print(f"  WARNING: no tag derivable for {d.id} (filename={sd.get('filename')!r}) — skipped")
            continue
        d.struct_data.update({"document_tags": tags})
        client.update_document(discoveryengine.UpdateDocumentRequest(
            document=d, update_mask=field_mask_pb2.FieldMask(paths=["struct_data"]),
        ))
        patched += 1
    print(f"Patched document_tags on {patched} docs. DONE.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Add FAA docs to DB2 + apply document_tags (gated).")
    ap.add_argument("--execute", action="store_true", help="Perform the live writes (default: dry run).")
    args = ap.parse_args()
    execute() if args.execute else dry_run()
