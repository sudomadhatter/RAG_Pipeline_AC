# quiz_banks/ — INDEX

48 quiz banks (`{lesson_id}_quiz.json`), 8 questions each (2 legal / 2 safety / 2 application /
2 risk_management), authored **from** the lesson's RKP `knowledge` — see
`docs/instruction_docs/quiz_authoring_guide.md` and the `quiz-bank-generation` skill.
`correct_answer` marks the answer; per bank the key is **exactly {A,A,B,B,C,C,D,D}** and feedback
prose is **letter-free** (SOP §6, 2026-07-23; enforced by `src/tests/test_answer_distribution.py`,
re-lettered only via `scripts/rebalance_quiz_answers.py`). Schema mirror: the app's
`backend/schemas/quiz.py` is the consuming contract.

Ingest (gated): `python src/gcp/ingest_quiz_banks.py [--execute]` → Firestore
`quiz_banks/{lesson}/questions/{q}`.
