# quiz_banks/ — INDEX

48 quiz banks (`{lesson_id}_quiz.json`), 8 questions each (2 legal / 2 safety / 2 application /
2 risk_management), authored **from** the lesson's RKP `knowledge` — see
`_docs/instruction_docs/quiz_authoring_guide.md` and the `quiz-bank-generation` skill.
`correct` flag marks the answer; there is **no positional rule** (the old "SJT answer is always D"
is retired). Schema mirror: the app's `backend/schemas/quiz.py` is the consuming contract.

Ingest (gated): `python src/gcp/ingest_quiz_banks.py [--execute]` → Firestore
`quiz_banks/{lesson}/questions/{q}`.
