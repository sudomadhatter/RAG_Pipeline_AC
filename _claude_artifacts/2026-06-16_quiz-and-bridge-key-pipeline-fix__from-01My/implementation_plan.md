--
IsArtifact: true
--
# Curriculum Pipeline Fix — Implementation Plan (v3)

> **Based on:** [Daniel's Code Review](file:///c:/Users/dlohn/.gemini/antigravity/scratch/AGY_AVIATIONCHAT/_claude_artifacts/2026-06-16_story-11-12-behavioral-eval-harness/code-review.md)
>
> **All 6 Daniel decisions locked.** This plan implements the true fix: unifying on a single DB1 writer and globally enforcing the bridge key guard.

---

## Goal

- **Story A (Quizzes):** All **47/48** lessons serve **8 valid questions** from `quiz_banks/{id}/questions`. Proven by a live quiz on a previously-dark lesson.
- **Story B (Bridge Keys):** Every lesson carries non-empty, **document-level** `doc_keys` in DB1 `structData` that return **real DB2 hits** — proven live with hit counts shown.

---

## User Review Required

> [!IMPORTANT]
> **I_F_01 Option E (Q004)** — 5 options (A-E). I'll evaluate the content and present the drop-vs-split decision before editing.

> [!IMPORTANT]
> **CFI Citation Verification** — 3 flagged citations need Daniel's sign-off before pipeline→app sync:
> - `VII_A_01 Q001` & `VII_D_01 Q001`: cite `14 CFR 23.2150` (Part 23 aircraft-certification)
> - `IX_C_01 Q004`: cites `AC 120-111` (air-carrier upset training)
> - `IX_C_01 Q003`: cites `14 CFR 91.411` (IFR altimeter tests)

---

## Proposed Changes

### Story B — Bridge Keys (Plumbing)

#### [NEW] `scripts/expand_vocabulary.py`
**B0 — Expand `DB2_VOCABULARY` against live DB2:**
- One-off script to query DB2 (`aviation-library-v2`) for all `document_tags`.
- Cross-reference with `DB2_VOCABULARY` in `schema.py`.
- Update `schema.py` to include any missing live tags.

#### [DELETE] `src/gcp/reimport_with_metadata.py`
**B3a — Retire the duplicate writer:**
- Delete this file entirely. It is a rogue, unguarded parallel path. The intended pipeline is `main.py curriculum`.

#### [MODIFY] `src/utils/generate_metadata.py`
**B3b — Unify the extractor pipeline (The True Fix):**
- **Port `split_task_file()`**: Move the regex parsing logic from `reimport_with_metadata.py` here.
- **Refactor `generate_curriculum_metadata()`**:
  - Accept `content: str` instead of a file path to avoid temp-file churn.
  - Set `temperature=0.0` for deterministic metadata generation.
  - Accept an `--offline` flag (default True). When True, skip the LLM call if the `<id>.json` sidecar already exists.
- **New Workflow**: When run on a master module (e.g., `Area 9 Tasks B,C PPL.md`), it:
  1. Splits the file into ACS chunks using `split_task_file()`.
  2. For each chunk:
     - Extracts metadata via `generate_curriculum_metadata(content)`.
     - Writes `pipeline/curriculum/new/<id>.md` (`encoding="utf-8"`).
     - Writes `pipeline/curriculum/new/<id>.json` (`encoding="utf-8"`).

#### [MODIFY] `src/pipeline/curriculum.py`
**B1 — Remove the silent skip:**
- In `run_phase_4_manifest_gen`, replace the `except Exception` block (lines 86-87) that silently skips invalid lessons.
- Raise the exception to cause a **hard stop**. The pipeline must fail loud if any metadata is invalid.

#### [MODIFY] `src/utils/schema.py`
**B4 — Global Vocabulary Enforcement:**
- Update `warn_chapter_level_keys` to `validate_doc_keys`.
- Hard fail on empty `doc_keys` (already exists).
- Hard fail if any `doc_key` is not in `DB2_VOCABULARY`.
- Rejects chapter-level annotations (strips `(PHAK Ch 6)` etc. and checks base token).
- **No `strict_mode` toggle.** The rule is enforced globally for all 3 consumers.

#### [NEW] `scripts/audit_sidecars.py`
**B4b — Clean Existing Metadata:**
- Before running the pipeline, audit `pipeline/curriculum/active/*.json` against the newly expanded vocabulary.
- Clean up any invalid keys directly in the JSON files.

#### [NEW] `src/tests/test_schema_guard.py`
**B4c — Guard Tests:**
- Unit tests for the global validator in `schema.py`.
- **Integration Test**: Feed a deliberately broken JSON sidecar (with an off-vocab key) to `curriculum.py` and assert it raises an exception instead of skipping.

#### [NEW] `src/tests/test_bridge_key_offline_gate.py`
**B5 — Offline schema & vocabulary gate:**
- Iterate all 184 DB1 docs (from `active/`).
- Assert non-empty, document-level, in-vocabulary.
- Add a test asserting `DB2_VOCABULARY` (in `schema.py`) is a true subset of DB2 `document_tags` (if possible offline, otherwise assert no regressions from the known set). *Note: Expected to fail until Area IX is cleaned.*

#### [NEW] `scripts/probe_db1_db2_roundtrip.py`
**B6 — Live DB1→DB2 round-trip probe:**
- Fire the real bridge hop against Vertex AI Search for a golden set of lessons.
- Assert hit count ≥ 1, top score ≥ floor, area match.

#### [MODIFY] `curriculum_components/curriculum_modules/Area 9 Tasks B,C PPL.md`
**B7 — Clean Area 9 Bridge Keys:**
- Clean/populate the Bridge Keys blocks where needed.
- Run `generate_metadata.py` on this module to generate valid, in-vocabulary `.json` sidecars in `pipeline/curriculum/new/`.

#### [EXECUTE] Run the Pipeline
**B8 — DB1 Import:**
- Run `python src/main.py curriculum` (which runs `curriculum.py`).
- This will validate the JSONs, upload to GCS, build the manifest, and import to DB1.
- Confirm doc count = 184.

---

### Story A — Quizzes

#### [DELETE] `src/gcp/upload_quiz_banks.py`
**A1 — Delete the wrong tool:**
- Deleted.

#### [MODIFY] `scripts/ingest_quiz_banks.py` (App Repo)
**A2 — Windows Encoding Fix:**
- Fix the `cp1252` crash when reading JSON files on Windows.

#### [MODIFY] `PPL_PA_I_F_01_quiz.json`
**A6 — Fix Q004's 5th option (E):**
- Evaluate question content and present drop-vs-split decision to Daniel. Edit the canonical copy.

#### Content Gate (Needs Daniel)
**A3/A4 — Citation verify + sync:**
- Sync the 11 drifted quiz banks from the pipeline repo to the app repo (after CFI sign-off).
**A5 — I_H_04 perspective remap:**
- Map non-canonical perspectives to canonical values and author canonical copy.
**A7 — App Ingest:**
- Run `ingest_quiz_banks.py` in the app repo to import the fixed quizzes.
**A8 — Live Verify:**
- Take a live quiz on `XI_A_01` and `IX_B_01` to confirm 8 questions serve.

---

### Housekeeping

- Write `walkthrough.md` with test output pasted. Fold "Your Actions Required" into this file.
- Update instruction docs in `_01_My/instruction_docs/` with the unified pipeline architecture.
- Save as `code-review.md` artifact.

---

## Verification Plan

### Automated Tests
```bash
# Schema guard unit tests + integration test (B4c)
python -m pytest src/tests/test_schema_guard.py -v

# Offline bridge key gate (B5)
python -m pytest src/tests/test_bridge_key_offline_gate.py -v

# Quiz dry-run (app repo, after sync)
cd AGY_AVIATIONCHAT && python -m scripts.ingest_quiz_banks --all --dry-run
# Expected: 48/48 pass, 0 fail
```

### Manual Verification
- **B0:** DB2_VOCABULARY verified against live DB2 tags — expansion documented.
- **Quiz live:** Take `XI_A_01` and `IX_B_01` quizzes — 8 questions each.
- **Bridge probe:** Run `probe_db1_db2_roundtrip.py` — hit counts pasted in walkthrough.
- **Doc count:** DB1 stays **184** after FULL re-import (`main.py curriculum`).
- **Regression:** Spot-check 5 other Areas.

