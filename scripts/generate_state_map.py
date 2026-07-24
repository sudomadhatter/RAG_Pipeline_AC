"""Generate `docs/docs_prds/STATE.md` — the live state map of the ingestion pipeline.

This turns "is the pipeline stale?" from a hand-maintained doc into a command.

OFFLINE (default): inventories `curriculum_components/` (authored assets) and `pipeline/curriculum/`
(the DB1 source store), then cross-references them for drift — orphaned podcasts, RKP<->quiz
mismatches, and elements-vs-manifest count skew. Pure stdlib + config paths, so it runs in CI with
no credentials and no network.

--live: additionally queries the deployed databases and DIFFS them against the local files —
Firestore (`rkp_manifests`, `quiz_banks`) doc-id sets vs the local lesson ids (the repo == Firestore
auto-verify that replaces the hand-typed "zero discrepancies" line in `asset_registry.md`), plus
DB1/DB2 (Vertex AI Search) document counts. Every live call is wrapped — if creds or a service are
unavailable the section degrades to "skipped" and the offline map is still written.

Usage:
    python scripts/generate_state_map.py            # offline map only
    python scripts/generate_state_map.py --live     # + deployed database state
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import config  # noqa: E402  (resolves paths + creds)

OUT_FILE = config.PROJECT_ROOT / "docs" / "docs_prds" / "STATE.md"
FIRESTORE_DATABASE_ID = "aviationchat-database"


# ── Offline inventory ──────────────────────────────────────────────────────────

def _lesson_ids(directory: Path, pattern: str) -> dict[str, str]:
    """Map lesson_id -> filename for every JSON file matching `pattern` in `directory`.

    Prefers the JSON `lesson_id` field; falls back to the filename stem so a malformed file still
    shows up in the inventory instead of silently vanishing.
    """
    out: dict[str, str] = {}
    for fp in sorted(directory.glob(pattern)):
        lesson_id = fp.stem
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            lesson_id = data.get("lesson_id") or fp.stem
        except (json.JSONDecodeError, OSError):
            pass
        out[lesson_id] = fp.name
    return out


def _count(directory: Path, pattern: str) -> int:
    return len(list(directory.glob(pattern)))


def _jsonl_lines(fp: Path) -> int:
    if not fp.exists():
        return 0
    return sum(1 for line in fp.read_text(encoding="utf-8").splitlines() if line.strip())


def gather_offline() -> dict:
    rkp = _lesson_ids(config.RKP_MANIFESTS_DIR, "*_rkp.json")
    quiz = _lesson_ids(config.QUIZ_BANKS_DIR, "*_quiz.json")
    rkp_ids, quiz_ids = set(rkp), set(quiz)

    # Lesson audio is linked from each RKP manifest's `audio_file` field; the audio itself lives in
    # a Firebase Storage bucket (deployed out-of-band, NOT ingested by this repo). Not every lesson
    # has one and that's expected — this is informational, not drift.
    audio_have, audio_missing = [], []
    for fp in sorted(config.RKP_MANIFESTS_DIR.glob("*_rkp.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        target = audio_have if data.get("audio_file") else audio_missing
        target.append(data.get("lesson_id") or fp.stem)

    return {
        "counts": {
            "curriculum_modules (.md)": _count(config.MODULES_DIR, "*.md"),
            "rkp_manifests (*_rkp.json)": len(rkp),
            "quiz_banks (*_quiz.json)": len(quiz),
            "faa_docs (PDFs)": _count(config.FAA_DOCS_DIR, "*.pdf"),
            "lesson_podcasts (.md)": _count(config.PODCASTS_DIR, "*.md"),
            "curriculum/elements (.md)": _count(config.CURRICULUM_ELEMENTS, "*.md"),
            "curriculum/sidecars (.json)": _count(config.CURRICULUM_SIDECARS, "*.json"),
            "curriculum.jsonl (entries)": _jsonl_lines(config.CURRICULUM_JSONL),
        },
        "rkp_ids": rkp_ids,
        "quiz_ids": quiz_ids,
        "rkp_without_quiz": sorted(rkp_ids - quiz_ids),
        "quiz_without_rkp": sorted(quiz_ids - rkp_ids),
        "podcasts": _count(config.PODCASTS_DIR, "*.md"),
        "audio_have": len(audio_have),
        "audio_missing": sorted(audio_missing),
        "rkp_total": len(rkp_ids),
        "elements": _count(config.CURRICULUM_ELEMENTS, "*.md"),
        "jsonl_entries": _jsonl_lines(config.CURRICULUM_JSONL),
    }


# ── Live database state (--live) ───────────────────────────────────────────────

def firestore_doc_ids() -> dict[str, set[str]]:
    """Return {collection: {doc_id, ...}} for the two authored-content collections."""
    import firebase_admin
    from firebase_admin import credentials, firestore

    cred = credentials.Certificate(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",
                       str(config.PROJECT_ROOT / "auth_keys" / "service-account.json")))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {"projectId": config.GCP_PROJECT_ID})
    db = firestore.client(database_id=FIRESTORE_DATABASE_ID)
    return {
        coll: {d.id for d in db.collection(coll).stream()}
        for coll in ("rkp_manifests", "quiz_banks")
    }


def vertex_doc_count(location: str, data_store: str) -> int:
    """Count documents in a Vertex AI Search data store (the same client reimport_db1_keys uses)."""
    from google.cloud import discoveryengine_v1 as discoveryengine

    client = discoveryengine.DocumentServiceClient()
    parent = client.branch_path(
        project=config.GCP_PROJECT_ID, location=location,
        data_store=data_store, branch="default_branch",
    )
    req = discoveryengine.ListDocumentsRequest(parent=parent, page_size=1000)
    return sum(1 for _ in client.list_documents(request=req))


def gather_live(offline: dict) -> dict:
    """Best-effort live state. Each probe is independent so one failure doesn't sink the rest."""
    live: dict = {"errors": []}
    try:
        fs = firestore_doc_ids()
        live["firestore"] = {coll: len(ids) for coll, ids in fs.items()}
        live["rkp_only_local"] = sorted(offline["rkp_ids"] - fs["rkp_manifests"])
        live["rkp_only_remote"] = sorted(fs["rkp_manifests"] - offline["rkp_ids"])
        live["quiz_only_local"] = sorted(offline["quiz_ids"] - fs["quiz_banks"])
        live["quiz_only_remote"] = sorted(fs["quiz_banks"] - offline["quiz_ids"])
    except Exception as e:  # noqa: BLE001 — any creds/network/SDK failure → skip, don't crash
        live["errors"].append(f"Firestore: {type(e).__name__}: {str(e)[:160]}")
    for label, loc, ds in (
        ("DB1 (aviation-curriculum)", config.CURRICULUM_LOCATION, config.CURRICULUM_DATA_STORE_ID),
        ("DB2 (aviation-library)", config.LIBRARY_LOCATION, config.LIBRARY_DATA_STORE_ID),
    ):
        try:
            live.setdefault("vertex", {})[label] = vertex_doc_count(loc, ds)
        except Exception as e:  # noqa: BLE001
            live["errors"].append(f"{label}: {type(e).__name__}: {str(e)[:160]}")
    return live


# ── Rendering ──────────────────────────────────────────────────────────────────

def _flag(ok: bool) -> str:
    return "✅" if ok else "⚠️"


def render(offline: dict, live: dict | None) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Pipeline State Map",
        "",
        "> **GENERATED FILE — do not hand-edit.** Regenerate with "
        "`python scripts/generate_state_map.py [--live]`.",
        f"> Last generated: {ts}"
        + ("  ·  mode: **live** (queried deployed databases)" if live else
           "  ·  mode: offline (local files only — pass `--live` for database state)"),
        "",
        "## Local asset inventory",
        "",
        "| Asset | Count |",
        "|---|---|",
    ]
    lines += [f"| {name} | {n} |" for name, n in offline["counts"].items()]

    lines += ["", "## Drift checks (offline)", ""]
    rkp_quiz_ok = not offline["rkp_without_quiz"] and not offline["quiz_without_rkp"]
    lines.append(f"- {_flag(rkp_quiz_ok)} **RKP ↔ quiz pairing** — "
                 + ("every RKP has a quiz and vice-versa." if rkp_quiz_ok else
                    f"RKPs with no quiz: {offline['rkp_without_quiz'] or 'none'}; "
                    f"quizzes with no RKP: {offline['quiz_without_rkp'] or 'none'}."))
    elements_ok = offline["elements"] == offline["jsonl_entries"]
    lines.append(f"- {_flag(elements_ok)} **elements ↔ curriculum.jsonl** — "
                 f"{offline['elements']} element .md vs {offline['jsonl_entries']} manifest entries"
                 + ("." if elements_ok else " — MISMATCH (rerun reimport_db1_keys.py to rebuild)."))
    lines.append(
        f"- ℹ️ **lesson audio** — {offline['audio_have']}/{offline['rkp_total']} lessons reference an "
        "`audio_file`; the audio lives in a Firebase Storage bucket (deployed out-of-band, not via "
        f"this repo). {offline['podcasts']} transcript .md in lesson_podcasts/. New lessons may have "
        "no podcast — expected, not drift."
        + (f" Lessons without audio: {offline['audio_missing']}." if offline['audio_missing'] else ""))

    lines += ["", "## Deployed database state", ""]
    if live is None:
        lines.append("_Offline run — rerun with `--live` to query Firestore + DB1/DB2._")
    else:
        if "firestore" in live:
            lines.append("**Firestore** (`aviationchat-database`):")
            lines.append("")
            lines.append("| Collection | Deployed docs | Local files | repo == Firestore |")
            lines.append("|---|---|---|---|")
            rkp_ok = not live["rkp_only_local"] and not live["rkp_only_remote"]
            quiz_ok = not live["quiz_only_local"] and not live["quiz_only_remote"]
            lines.append(f"| rkp_manifests | {live['firestore']['rkp_manifests']} | "
                         f"{len(offline['rkp_ids'])} | {_flag(rkp_ok)} |")
            lines.append(f"| quiz_banks | {live['firestore']['quiz_banks']} | "
                         f"{len(offline['quiz_ids'])} | {_flag(quiz_ok)} |")
            if not rkp_ok or not quiz_ok:
                lines.append("")
                lines.append(f"- rkp local-only: {live['rkp_only_local'] or 'none'} · "
                             f"remote-only: {live['rkp_only_remote'] or 'none'}")
                lines.append(f"- quiz local-only: {live['quiz_only_local'] or 'none'} · "
                             f"remote-only: {live['quiz_only_remote'] or 'none'}")
        if live.get("vertex"):
            lines += ["", "**Vertex AI Search:**", ""]
            lines += [f"- {label}: {n} documents" for label, n in live["vertex"].items()]
        if live["errors"]:
            lines += ["", "**Skipped probes** (creds/network/service unavailable):", ""]
            lines += [f"- {e}" for e in live["errors"]]

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the pipeline state map (STATE.md).")
    ap.add_argument("--live", action="store_true",
                    help="Also query Firestore + DB1/DB2 and diff against local files.")
    args = ap.parse_args()

    offline = gather_offline()
    live = gather_live(offline) if args.live else None

    md = render(offline, live)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(md, encoding="utf-8")

    print(f"Wrote {OUT_FILE}")
    print(f"  Inventory: {offline['counts']}")
    if offline["rkp_without_quiz"] or offline["quiz_without_rkp"]:
        print(f"  DRIFT — rkp_without_quiz={offline['rkp_without_quiz']} "
              f"quiz_without_rkp={offline['quiz_without_rkp']}")
    if live and live["errors"]:
        print(f"  Live probes skipped: {live['errors']}")


if __name__ == "__main__":
    main()
