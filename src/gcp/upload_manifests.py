"""Ingest RKP manifests into Firestore (collection `rkp_manifests`, doc id = lesson_id).

The app reads these for the RKP-First Q&A path and the flashcard UI; the manifest `bridge_keys`
are what the app filters DB2 on. Paths resolve via config.py (no hardcoded machine paths).

GATED: dry run by default (lists what would upload, writes nothing). --execute performs the writes.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402  (sets GOOGLE_APPLICATION_CREDENTIALS)

import firebase_admin  # noqa: E402
from firebase_admin import credentials, firestore  # noqa: E402

MANIFESTS_DIR = config.RKP_MANIFESTS_DIR
DATABASE_ID = "aviationchat-database"
COLLECTION = "rkp_manifests"


def load_all() -> list[tuple[str, dict]]:
    out = []
    for fp in sorted(MANIFESTS_DIR.glob("*_rkp.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        doc_id = data.get("lesson_id")
        if not doc_id:
            print(f"  [SKIP] {fp.name} missing 'lesson_id'")
            continue
        out.append((doc_id, data))
    return out


def dry_run():
    items = load_all()
    print(f"=== DRY RUN — {len(items)} manifests would upload to {DATABASE_ID}/{COLLECTION} ===")
    for doc_id, data in items:
        n = len(data.get("required_knowledge_points", []))
        print(f"  {doc_id:18s} ({n} RKPs)")
    print("\nRe-run with --execute to write to Firestore.")


def execute():
    items = load_all()
    cred = credentials.Certificate(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",
                       str(config.PROJECT_ROOT / "auth_keys" / "service-account.json")))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {"projectId": config.GCP_PROJECT_ID})
    db = firestore.client(database_id=DATABASE_ID)
    col = db.collection(COLLECTION)

    ok = 0
    for doc_id, data in items:
        col.document(doc_id).set(data)
        print(f"  [OK] {doc_id}")
        ok += 1
    print(f"\nUploaded {ok}/{len(items)} manifests.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ingest RKP manifests to Firestore (gated).")
    ap.add_argument("--execute", action="store_true", help="Write to Firestore (default: dry run).")
    args = ap.parse_args()
    execute() if args.execute else dry_run()
