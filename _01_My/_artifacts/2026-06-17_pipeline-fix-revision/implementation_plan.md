---
IsArtifact: true
ArtifactMetadata:
  title: Curriculum Pipeline Fix — Revision Plan
  type: implementation_plan
  date: 2026-06-17
---

# Curriculum Pipeline Fix — Revision Plan

> **Based on:** [code-review.md](../2026-06-17_pipeline-qa-code-review/code-review.md) (QA of commit `f702ed7`).
> Resolves the 3 blockers, 3 HIGH, 5 MEDIUM, and 4 LOW findings from that review.
>
> **STATUS: awaiting Daniel's "approved" before any project file is touched.**

---

## Goal

Take the dev team's refactor (which is directionally right) from "green on a hollow run" to "actually
verified and safe to ingest." Concretely, when this is done:

1. **No silent dead bridge keys** — every `doc_key` in the curriculum is confirmed against the *live* DB2
   `document_tags`, not a hand-curated guess.
2. **The Area 9 data is produced by the unified LLM extractor**, not the regex scripts the refactor was
   supposed to retire.
3. **The manifest is the full 184**, proven by a dry-run count before any FULL-reconciliation import — so we
   can never wipe the store with a 12-entry stub.
4. **The code is honest about success/failure** — exit codes, validated offline path, no overclaiming.
5. **The docs match the code** (v1, not v2), and there are **tests** that fail red when any of the above regresses.

---

## Resolved with Daniel (decisions locked)

**Datastore name: stay on `v1`.** Confirmed by the real `auth_keys/.env`
(`VERTEX_SEARCH_DB1_ID=aviation-curriculum-v1`, `DB2_ID=aviation-library-v1`), `config.py`, the app's
`.env.example`, and the app's RAG query code — all agree on **v1**, and Daniel confirmed the live stores are
v1 and untouched. A Vertex AI Search data-store ID is **immutable**, so "renaming" to v2 would mean a full
migration (new stores + re-ingest all 184 curriculum docs *and* the entire DB2 FAA library + re-point the app
+ re-verify the bridge hop + tear down v1) — real risk for a cosmetic label. **Decision: do not migrate.**
B-1 is therefore a *documentation* fix — correct **v2 → v1** across `Master_Curriculum_Pipeline.md`,
`bridge_key_guide.md`, `curriculum_lifecycle.md`, and the dev-story (the v2 naming was my error). (One stray
`aviation-library-v2` mention lives in the app's `_docs/vertex_ai_search_widget.html` — flagged for the app
team, out of our scope.)

**Versioning: the curriculum is `v1` and unchanged; we are fixing the pipeline so it correctly serves the
`2.6` app system.** The curriculum has NOT been updated — it stays v1. The app being on 2.6 is the consumer
we're fixing *for*; the curriculum's own version does not inherit it. Strip every `v2` / `v2.8` / `2.6`
reference from the instruction docs and make it all **v1** — datastores, doc bodies, and revision labels alike.

**`.env` good practice:** stop hardcoding the datastore IDs in `config.py`; read them from the real `.env`
(`VERTEX_SEARCH_DB1_ID` / `DB2_ID`, which already exist there), with `.env.example` as the committed
template. Single source of truth, no drift.

**Credentials exist locally:** `auth_keys/service-account.json` + `auth_keys/.env` (with `GEMINI_API_KEY`
and `GOOGLE_APPLICATION_CREDENTIALS`) are present. So the dev's "default credentials were not found" was the
**cwd path bug (M-1)**, not a missing key — fixing M-1 should unblock the live steps. I'll run an auth
smoke-test at the top of execution; if the SA happens to lack IAM, the live-only steps (P5 probe, P6 import)
become your manual action and everything else still lands.

---

## Execution order (phased)

### Phase 0 — Ground truth & safety net (no live calls)
- **P0.1** Correct `v2 → v1` across `_01_My/Master_Curriculum_Pipeline.md`, `bridge_key_guide.md`,
  `curriculum_lifecycle.md`, and the dev-story, and fix the revision label `2.8 → 2.6`. Add a one-line
  "store names are v1" note so this can't drift again.
- **P0.2** `.gitignore` the generated `pipeline/curriculum/curriculum.jsonl` and delete the committed
  **12-entry stub** so it can never be hand-uploaded into a FULL reconciliation. *(Addresses B-2, half.)*

### Phase 1 — Code-path correctness (offline, fast)
- **P1.1** `config.py`: `PROJECT_ROOT = Path(__file__).resolve().parents[1]` instead of `Path(os.getcwd())`
  *(M-1)*; and read `CURRICULUM_DATA_STORE_ID` / `LIBRARY_DATA_STORE_ID` from `os.getenv("VERTEX_SEARCH_DB1_ID")` /
  `DB2_ID` (the real `.env`), defaulting to the v1 names, instead of hardcoding them. *(.env good practice)*
- **P1.2** `base.py` / `main.py`: validation-abort path calls `sys.exit(1)`, not bare `return`, so CI sees the
  failure. *(M-2)*
- **P1.3** `generate_metadata.py`: validate the offline/sidecar path through `CurriculumLessonSchema` before
  returning, and rename the CLI flag so it matches the docs (`--offline` semantics). *(M-3)*
- **P1.4** Hygiene: delete `generate_out.txt`; reconcile the `service-account.json` vs
  `librarian-service-account.json` reference in `expand_vocabulary.py`; remove the dead branch in
  `audit_sidecars.py:58`. *(L-1, L-3, L-4)*

### Phase 2 — Vocabulary integrity (the core blocker, B-3)
- **P2.1** Run `expand_vocabulary.py` against **live DB2** (`aviation-library-v1`). Capture the real
  `document_tags` set.
- **P2.2** Diff the live tags against `DB2_VOCABULARY`. For each of the 5 hand-added tokens
  (`FAA-S-ACS-6C`, `AC 120-80`, `AC 120-111`, `FAA-H-8083-2A`, `FAA Safety Briefing "Startle Response"`):
  if it **is** a live tag → keep; if it is **not** → remove it from the vocabulary and escalate the
  affected lesson's `doc_keys` to you (the key points at nothing; the content needs a real source, not a
  vocabulary patch). I expect the Startle Response token to fail.
- **P2.3** Rebuild `DB2_VOCABULARY` from the verified live set (with a comment noting it was machine-derived
  on 2026-06-17), so it's a fact, not an assertion.

### Phase 3 — Regenerate Area 9 the right way (H-1)
- **P3.1** Delete `scripts/fallback_generator.py` and `scripts/fallback_generator2.py` (the resurrected regex
  extractors).
- **P3.2** Run the unified `generate_metadata.py --regenerate` on `Area 9 Tasks B,C PPL.md` to produce the 12
  sidecars via the **LLM path** (temperature=0.0), writing into `pipeline/curriculum/new/`.
- **P3.3** Diff the LLM `doc_keys`/`reg_keys` against the current regex-made sidecars. Where they differ,
  trust the LLM output **only if** the keys pass the verified vocabulary (P2); anything ambiguous goes to you.
  Replace the hardcoded `ancestral_context` with the real LLM-derived value.

### Phase 4 — Manifest correctness (B-2, rest)
- **P4.1** Confirm `curriculum.py` phase 4 merges `active/` (172) + `new/` (12). Run `python src/main.py
  curriculum --dry-run` and assert the manifest line count is **184**. Paste the real number.

### Phase 5 — Tests (H-2) — `src/tests/`
- **P5.1** `test_schema_guard.py` — empty `doc_keys` fails; off-vocabulary fails; chapter-level fails;
  valid document-level passes; `N/A`/blank stripped.
- **P5.2** `test_bridge_key_offline_gate.py` — iterate every `active/` + `new/` sidecar; assert non-empty,
  document-level, in-vocabulary `doc_keys`. Runs offline. **This is the test that would have caught B-3.**
- **P5.3** `test_vocabulary_containment.py` — assert `DB2_VOCABULARY ⊆ live DB2 tags` (network-gated; skips
  cleanly without creds) so the vocabulary can never silently drift again.
- **P5.4** `scripts/probe_db1_db2_roundtrip.py` — for each lesson, fire the bridge hop and assert ≥1 DB2 hit.

### Phase 6 — Live verification (gated, needs your go)
- **P6.1** Run P5.4 probe against live DB1→DB2; paste hit counts.
- **P6.2** **The real FULL-reconciliation import into DB1 is NOT auto-run.** I'll present the dry-run proof
  (count = 184, probe green) and you pull the trigger, or give explicit "run the import" — because it's a
  destructive, irreversible write to the live store.

### Phase 7 — Honest closeout (H-3) & artifact hygiene
- **P7.1** Rewrite the closing docs into protocol-compliant form: a single `walkthrough.md` with a real
  **"Your Actions"** section + pasted test/run output, a `task-list.md` snapshot, and **remove** the
  forbidden `task.md` / `your-action-required.md`. State plainly what ran and what didn't. *(H-3, L-2)*
- **P7.2** **App-repo CFI gate (M-4):** the 3 flagged citations (`14 CFR 23.2150`, `AC 120-111`,
  `14 CFR 91.411`) remain **unverified**. The app-side quiz-bank push stays on hold until you sign off on
  them. I'll list them for you; I will not author or "guess" a citation.
- **P7.3** `reg_keys` granularity (M-5): confirm whether the app's bridge hop filters on `reg_keys` or only
  `doc_keys`. If display-only, document it; if it filters, normalize section-level (`14 CFR 91.103`) to the
  part level DB2 actually tags. (Low risk — likely just a documented decision.)

---

## Files touched (this repo)

| File | Action | Phase |
|---|---|---|
| `_01_My/Master_Curriculum_Pipeline.md`, `bridge_key_guide.md`, `curriculum_lifecycle.md`, dev-story | EDIT (v2→v1) | P0.1 |
| `.gitignore` + delete `pipeline/curriculum/curriculum.jsonl` stub | EDIT/DELETE | P0.2 |
| `src/config.py` | MODIFY (path) | P1.1, P1.4 |
| `src/pipeline/base.py`, `src/main.py` | MODIFY (exit code) | P1.2 |
| `src/utils/generate_metadata.py` | MODIFY (offline validate, flag) | P1.3, P3.2 |
| `src/utils/schema.py` | MODIFY (verified vocabulary) | P2.3 |
| `scripts/audit_sidecars.py`, `scripts/expand_vocabulary.py` | MODIFY (hygiene) | P1.4 |
| `scripts/fallback_generator.py`, `fallback_generator2.py`, `generate_out.txt` | DELETE | P3.1, P1.4 |
| `pipeline/curriculum/new/lesson_pa_ix_*.{json,md}` (12) | REGEN via LLM | P3.2 |
| `src/tests/test_schema_guard.py`, `test_bridge_key_offline_gate.py`, `test_vocabulary_containment.py` | NEW | P5 |
| `scripts/probe_db1_db2_roundtrip.py` | NEW | P5.4 |
| artifacts: `walkthrough.md`, `task-list.md`; delete `task.md`, `your-action-required.md` | NEW/DELETE | P7.1 |

**App repo (separate, gated):** the 11 quiz-bank sync + `ingest_quiz_banks.py` fix stay **held** behind the
CFI citation sign-off (P7.2). Not pushed in this pass.

---

## Verification plan

- **Offline (I run, paste output):** `pytest src/tests/ -v` (schema guard + offline gate green over all
  ~184 sidecars); `python src/main.py curriculum --dry-run` shows **184** manifest lines.
- **Live (needs creds; gated):** `expand_vocabulary.py` prints the real DB2 tag set; `probe_db1_db2_roundtrip.py`
  shows ≥1 hit per lesson with counts pasted.
- **Not done by me without explicit go:** the FULL-reconciliation DB1 import (P6.2).

---

## Open questions for Daniel

*(v1-vs-v2 resolved: stay on v1, fix docs. Doc label → 2.6. Both locked above.)*

1. **The Startle Response source** — if `FAA Safety Briefing "Startle Response"` turns out not to be in DB2
   (likely), what should `PA.IX.C.R4`'s `doc_key` point at instead? (I'll bring you the live-DB2 answer first.)
2. **The live import (P6.2)** — do you want to pull the trigger yourself, or authorize me to run it once the
   dry-run proves count = 184 and the probe is green?

---

## Hard stops I will respect

- No project file touched until you say **"approved."**
- The live FULL-reconciliation import is **not** auto-run — dry-run proof first, then your explicit go.
- I will **not** invent an FAA citation or a DB2 source token — anything that can't be verified comes to you.
- No `git commit` / `git push` — I provide the commands.
