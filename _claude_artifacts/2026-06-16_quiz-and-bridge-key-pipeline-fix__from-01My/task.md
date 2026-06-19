--
IsArtifact: true
--
# Curriculum Pipeline Fix — Task Tracker

- `[ ]` **B0 — Expand DB2_VOCABULARY against live DB2**
  - `[ ]` Write `scripts/expand_vocabulary.py` to query live DB2 `document_tags`
  - `[ ]` Update `schema.py`'s `DB2_VOCABULARY` with any missing tags

- `[ ]` **B3 — Retire Duplicate Writer / Refactor Extractor**
  - `[ ]` Delete `src/gcp/reimport_with_metadata.py`
  - `[ ]` Update `src/utils/generate_metadata.py` to port `split_task_file()` logic
  - `[ ]` Refactor `generate_curriculum_metadata()` to accept string content and support `--offline` flag
  - `[ ]` Ensure deterministic output (`temperature=0.0`) and utf-8 writing

- `[ ]` **B1 & B4 — Global Schema Guard & Hard Stop**
  - `[ ]` Update `src/pipeline/curriculum.py` to raise exception instead of skipping invalid lessons (B1)
  - `[ ]` Update `src/utils/schema.py` to enforce global DB2 vocabulary validation without strict mode toggle (B4)
  - `[ ]` Add `scripts/audit_sidecars.py` to clean existing metadata sidecars
  - `[ ]` Write unit and integration tests in `src/tests/test_schema_guard.py`

- `[ ]` **A1 & A6 — Quizzes Tooling & Content Fix**
  - `[ ]` Delete `src/gcp/upload_quiz_banks.py`
  - `[ ]` Evaluate `I_F_01 Q004` (5th option) and present drop/split decision

- `[ ]` **B5 & B6 — Offline Gate & Live Probe**
  - `[ ]` Write `src/tests/test_bridge_key_offline_gate.py` with vocabulary containment test
  - `[ ]` Write `scripts/probe_db1_db2_roundtrip.py`

- `[ ]` **A3-A8 — Content Gate (Needs Daniel)**
  - `[ ]` Verify citations (Daniel)
  - `[ ]` Sync 11 pipeline quiz banks to app repo
  - `[ ]` Author `I_H_04` canonical copy with perspective remap
  - `[ ]` Fix Windows `cp1252` encoding crash in `scripts/ingest_quiz_banks.py` (App Repo)
  - `[ ]` Run App Ingest

- `[ ]` **B7 & B8 — Area IX Overlap & Pipeline Execution**
  - `[ ]` Clean Area 9 module bridge keys
  - `[ ]` Run unified generator to create valid sidecars for Area 9 chunks
  - `[ ]` Execute `python src/main.py curriculum` (DB1 Import)
  - `[ ]` Confirm DB1 doc count stays 184

- `[ ]` **Housekeeping**
  - `[ ]` Update instruction docs (`_01_My/instruction_docs/`)
  - `[ ]` Write `walkthrough.md` with action steps and commit command

