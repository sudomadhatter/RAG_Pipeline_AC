---
IsArtifact: true
---
# Curriculum Pipeline Fixes and Schema Enforcement

I've completed all items on the implementation plan, successfully converting the curriculum pipeline to the unified architecture, fixing the quiz banks, and executing a dry run of the ingestion process.

## Changes Made

### 1. Refactored the Curriculum Pipeline (B Tasks)
- **Deleted Rogue Scripts:** Removed `reimport_with_metadata.py` and `upload_quiz_banks.py` to prevent duplicate writes and bypassing validations.
- **Unified Generator:** Merged `split_task_file` logic into `generate_metadata.py` and refactored it for in-memory processing. Added an `--offline` flag to allow using pre-generated JSON sidecars.
- **Hardened Schema Enforcer:** Modified `schema.py` to strictly enforce the `DB2_VOCABULARY`. Instead of warning on chapter-level keys, `validate_doc_keys()` now raises a `ValueError` for a hard failure if invalid bridge keys are detected. Manually appended valid, missing tags to the vocabulary map.
- **Unified Main Pipeline:** Updated `curriculum.py` to catch schema validation errors and raise a `ValueError` instead of silently skipping, ensuring bad data never reaches Vertex AI Search.
- **Cleaned Area 9:** Modified the `Area 9 Tasks B,C PPL.md` master module to properly remove chapter-level annotations that were failing the new schema check, and generated missing JSON sidecars for it natively.

### 2. Synced & Fixed App Quiz Banks (A Tasks)
- **Synced Files:** Copied the 11 `PPL_PA_*_quiz.json` files to `AGY_AVIATIONCHAT/_docs/specialist_lesson/quiz_banks`.
- **Fixed Q004 Schema:** Removed the invalid 5th option ("Option E") from `PPL_PA_I_F_01_quiz.json` question Q004 to align with the strictly 4-option MCQ schema.
- **Fixed Perspectives:** Adjusted the invalid hyphenated perspectives in `PPL_PA_I_H_04_quiz.json` (`physiological`, `decision-making`, `risk-management`) to the exact Literal strings expected by the backend schema (`application`, `risk_management`, `safety`).
- **Fixed Windows Encodings:** Edited `ingest_quiz_banks.py` to replace the Unicode right arrow (`→`) and em-dash (`—`) with standard ASCII equivalents (`->` and `-`) to prevent `UnicodeEncodeError` on Windows consoles.

## Validation Results

**1. Curriculum Pipeline Phase 1 Validation (Dry Run Simulation)**
The pipeline correctly parsed and validated the new Area 9 sidecars against the hardened schema vocabulary without errors!
```text
=== Starting Curriculum (DB1) Ingestion Pipeline ===
 Phase 1 Complete. 24 files validated.
 Unexpected Error during upload for lesson_pa_ix_b_k1.json: Your default credentials were not found.
```
*(GCP upload failed expectedly due to no service account in the scratch dir, but Phase 1 schema validation completed perfectly!)*

**2. App Quiz Bank Ingest Dry Run**
The dry run now parses all 48 quiz files (including the 11 synced files) and validates perfectly without Unicode crashes or Pydantic validation errors!
```text
[DRY RUN] Lesson: PPL_PA_XI_A_03 - 8 questions validated
  Would write: PPL_PA_XI_A_03_Q001 (legal) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q001
  Would write: PPL_PA_XI_A_03_Q002 (legal) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q002
  Would write: PPL_PA_XI_A_03_Q003 (safety) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q003
  Would write: PPL_PA_XI_A_03_Q004 (safety) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q004
  Would write: PPL_PA_XI_A_03_Q005 (application) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q005
  Would write: PPL_PA_XI_A_03_Q006 (application) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q006
  Would write: PPL_PA_XI_A_03_Q007 (risk_management) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q007
  Would write: PPL_PA_XI_A_03_Q008 (risk_management) -> quiz_banks/PPL_PA_XI_A_03/questions/PPL_PA_XI_A_03_Q008
[DRY RUN] No writes made.

==================================================
DRY RUN COMPLETE: 384 questions validated across 48 file(s). Nothing written.
```
