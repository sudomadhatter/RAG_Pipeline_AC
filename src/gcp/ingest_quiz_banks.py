"""Ingest quiz banks into Firestore at quiz_banks/{lesson_id}/questions/{question_id}.

The app's quiz router reads questions from this subcollection and rotates them via the
`seen_by` / `last_seen_at` fields, which we initialize here. Idempotent: re-running upserts
each question by its id (set with merge=True so rotation state isn't clobbered on re-ingest).

Fossil hygiene: merge=True never deletes, so a field removed from repo JSON survives live
forever (the 2026-07-23 audit found 206 empty-string `sjt_rationale` fossils). Every question
without `sjt_rationale` in the repo therefore sends an explicit DELETE_FIELD for it — a no-op
where the field is already absent live.

GATED: dry run by default (validates + reports, writes nothing). --execute performs the writes.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

import firebase_admin  # noqa: E402
from firebase_admin import credentials, firestore  # noqa: E402

QUIZ_DIR = config.QUIZ_BANKS_DIR
DATABASE_ID = "aviationchat-database"
COLLECTION = "quiz_banks"


def validate(data: dict, fname: str) -> list[str]:
    """Light structural checks — NOT a re-implementation of the app's quiz schema."""
    errs = []
    if not data.get("lesson_id"):
        errs.append(f"{fname}: missing lesson_id")
    for i, q in enumerate(data.get("questions", [])):
        labels = {o.get("label") for o in q.get("options", [])}
        if not q.get("id"):
            errs.append(f"{fname} q#{i}: missing id")
        if not q.get("text"):
            errs.append(f"{fname} q#{i}: missing text")
        if q.get("correct_answer") not in labels:
            errs.append(f"{fname} q{q.get('id', i)}: correct_answer {q.get('correct_answer')!r} not in options {sorted(labels)}")
    return errs


def load_all():
    banks, all_errs = [], []
    for fp in sorted(QUIZ_DIR.glob("*_quiz.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        all_errs += validate(data, fp.name)
        banks.append(data)
    return banks, all_errs


def dry_run():
    banks, errs = load_all()
    total_q = sum(len(b.get("questions", [])) for b in banks)
    print(f"=== DRY RUN — {len(banks)} quiz banks, {total_q} questions -> {DATABASE_ID}/{COLLECTION} ===")
    for b in banks[:5]:
        print(f"  {b['lesson_id']:18s} {len(b.get('questions', []))} questions")
    print(f"  ... ({len(banks)} total)")
    if errs:
        print(f"\n  {len(errs)} VALIDATION ERRORS:")
        for e in errs[:20]:
            print(f"    {e}")
    else:
        print("\n  Validation: all banks structurally valid.")
    no_sjt = sum(1 for b in banks for q in b.get("questions", []) if "sjt_rationale" not in q)
    print(f"\n  Fossil hygiene: --execute will send `sjt_rationale` DELETE_FIELD on {no_sjt} "
          f"questions where the repo has none (clears stale empty-string fossils; no-op elsewhere).")
    print("\nRe-run with --execute to write to Firestore.")


def execute():
    banks, errs = load_all()
    if errs:
        print(f"ABORT: {len(errs)} validation errors — fix before ingest.")
        for e in errs[:20]:
            print(f"  {e}")
        sys.exit(1)

    cred = credentials.Certificate(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",
                       str(config.PROJECT_ROOT / "auth_keys" / "service-account.json")))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {"projectId": config.GCP_PROJECT_ID})
    db = firestore.client(database_id=DATABASE_ID)

    total = 0
    cleaned_parents = 0
    fossil_clears = 0
    for b in banks:
        lesson_id = b["lesson_id"]
        parent = db.collection(COLLECTION).document(lesson_id)
        # The app reads ONLY the questions SUBCOLLECTION (quiz_bank_service._fetch_all_questions).
        # The parent doc must carry just lesson_id/title — strip any legacy embedded `questions`
        # array (cruft from the old ingester) so there is one source of truth.
        snap = parent.get()
        if snap.exists and isinstance((snap.to_dict() or {}).get("questions"), list):
            cleaned_parents += 1
        parent.set(
            {"lesson_id": lesson_id, "title": b.get("title", ""), "questions": firestore.DELETE_FIELD},
            merge=True,
        )
        qcol = parent.collection("questions")
        for q in b["questions"]:
            payload = dict(q)
            payload.setdefault("seen_by", [])
            payload.setdefault("last_seen_at", None)
            if "sjt_rationale" not in q:
                payload["sjt_rationale"] = firestore.DELETE_FIELD
                fossil_clears += 1
            qcol.document(q["id"]).set(payload, merge=True)
            total += 1
        print(f"  [OK] {lesson_id}: {len(b['questions'])} questions")
    print(f"\nIngested {total} questions across {len(banks)} lessons.")
    print(f"Stripped legacy embedded `questions` array from {cleaned_parents} parent docs.")
    print(f"Sent `sjt_rationale` DELETE_FIELD on {fossil_clears} questions (fossil hygiene).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ingest quiz banks to Firestore (gated).")
    ap.add_argument("--execute", action="store_true", help="Write to Firestore (default: dry run).")
    args = ap.parse_args()
    execute() if args.execute else dry_run()
