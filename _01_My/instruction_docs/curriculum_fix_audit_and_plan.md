---
title: "PPL Curriculum — Audit & Fix Plan (for the Ingestion Team)"
type: implementation_plan
date: 2026-06-15
from: "App / Consumer team (Daniel + Woz)"
to: "Ingestion Pipeline team (Ingestion_pipeline_AvCh)"
reference_docs: "_01_My/bridge_key_guide.md · _01_My/quiz_authoring_guide.md · _01_My/rkp_creation_guide.md"
---

# PPL Curriculum — Audit & Fix Plan

## The ask (read first)

The PPL curriculum is live (47 lessons), but an audit turned up a set of issues in the **RAG/bridge-key**
and **quiz-ingestion** layers that make parts of it silently broken. **Please use this as the basis to
organize a fix plan and assign owners.** The *how* for each item is already written up in the two guides
now in your `_01_My/` folder — this doc is the *what* and the *order*. Nothing here needs new authoring
from us except where noted (Daniel is rewriting the new-lesson questions).

---

## The Audit — what's broken

| # | Finding | Impact | Evidence |
|---|---|---|---|
| **F1** | **DB1 `structData` bridge keys are empty** for a set of lessons — **Area IX (12 emergency-ops lessons) worst.** | The DB1→DB2 verification hop returns nothing → answers can't be ground-truth-checked against the FAA library. **Silent** — looks fine to any "did it error?" check. | `reg_keys`/`doc_keys` blank in Vertex `aviation-curriculum-v2`. |
| **F2** | **The metadata schema allows empty keys silently.** `src/utils/schema.py` → `reg_keys`/`doc_keys` default to `[]` with no validation. | This is the root cause that let F1 ship and will let it recur on every future batch. | `CurriculumStructData` has no `min_length`/validator. |
| **F3** | **Keys (where present) are the wrong granularity.** Chapter/section-level (`FAA-H-8083-25C (PHAK Ch 6)`) instead of document-level. | Won't strict-match DB2's `document_tags` (`FAA-H-8083-25C`, `AC 61-98D`, `AIM`, `14 CFR 91`) → verification misses even when keys exist. | `rkp_creation_guide.md` examples (now corrected) taught the chapter form. |
| **F4** | **The 13 new lessons (III/VI/VII/IX/XI) have NO quizzes in Firestore** — empty `quiz_banks/{id}/questions`. | Those lessons' quizzes don't exist for students. | Firestore pull: those lesson IDs return `n: 0` questions. |
| **F5** | **Quiz ingestion only ever processed Area I.** The `--all` path globbed `PPL_PA_I_*` (Area I only) from a removed directory. | Root cause of F4 — new areas were never ingested. | App-side `scripts/ingest_quiz_banks.py` (now fixed on our side; confirm your pipeline path does the same). |
| **F6** | **The new-lesson quiz files are invalid + sub-par.** `far_reference: null` (fails schema) and below the quality bar. | Won't ingest even once F5 is fixed; and shouldn't until rewritten. | Dry-run validation error; Daniel is **rewriting** these. |

---

## The Plan — three workstreams (run F2 before any re-import)

### Workstream A — Bridge keys / RAG verification (fixes F1, F2, F3)
*Full how-to: `bridge_key_guide.md`.*
1. **Harden the schema FIRST** (so this can't recur): `src/utils/schema.py` → `doc_keys: Field(min_length=1)`
   + a validator that drops `"N/A"`/blank and rejects empty. Add a post-generation check in
   `src/utils/generate_metadata.py` that normalizes keys to **document-level** and fails on empty `doc_keys`.
2. **Audit all 184** DB1 docs → list every empty/weak `doc_keys` (Area IX first).
3. **Regenerate + re-import** the affected lessons via `src/gcp/reimport_with_metadata.py` (`FULL`
   reconciliation). Keys must be document-level (match DB2 `document_tags`).
4. **Prove it** (not "no error"): live DB1→DB2 round-trip returns **count ≥ 1 + score ≥ floor +
   owning-area match**; offline schema gate over all 184 in CI; freeze 2–3 golden fixtures.

### Workstream B — Quiz ingestion (fixes F4, F5)
1. **Ensure your quiz-ingestion path covers EVERY area**, not just Area I. (Our app-side
   `scripts/ingest_quiz_banks.py` `--all` is fixed — dir → `_docs/specialist_lesson/quiz_banks`, glob →
   `PPL_PA_*_quiz.json`. Confirm the pipeline's `src/gcp/upload_quiz_banks.py` / your Firestore writer
   does the same.)
2. **Add a schema-valid gate** so an invalid quiz file (e.g. `far_reference: null`) fails loudly at
   ingest instead of silently skipping.
3. After Workstream C delivers valid files: **ingest all areas** → confirm `quiz_banks/{id}/questions`
   has 8 docs for every one of the 47 lessons.

### Workstream C — Quiz quality (fixes F6) — *Daniel owns the rewrite*
1. Daniel rewrites the 13 new-lesson quiz banks to the **`quiz_authoring_guide.md`** standard (real SJTs,
   4 perspectives, document-level `far_reference`, real accident-data explanations).
2. Team validates each against the guide's §9 self-check + the schema gate (B2), then ingests (B3).

---

## Definition of done

- [ ] Schema rejects empty `doc_keys` and invalid quiz files (loud failure, not silent skip).
- [ ] All 184 DB1 lessons carry non-empty, **document-level** bridge keys; live DB1→DB2 returns real
      hits (count ≥ 1 + score floor) for the fixed lessons; offline gate green in CI.
- [ ] All 47 lessons have 8 valid quiz questions in Firestore `quiz_banks/{id}/questions`.
- [ ] The rewritten new-lesson questions pass the `quiz_authoring_guide.md` §9 self-check.

## Reference (the "how")

| Doc (in your `_01_My/`) | Covers |
|---|---|
| `bridge_key_guide.md` | Bridge-key root cause, document-level keying, schema guard, verification probe, Area IX procedure |
| `quiz_authoring_guide.md` | The quiz quality bar — SJT design, 4 perspectives, difficulty levers, explanation standard, templates |
| `rkp_creation_guide.md` | RKP/quiz mechanics + schema (now corrected to document-level keys) |

> Questions: pipeline/format → Woz · content/citations + question rewrites → Daniel (CFI).
