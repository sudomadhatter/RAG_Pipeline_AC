---
IsArtifact: true
ArtifactMetadata:
  title: Curriculum Pipeline Fix — QA & Code Review
  type: code_review
  date: 2026-06-17
---

# Curriculum Pipeline Fix — QA & Code Review

**Reviewer:** Woz (Claude)
**Scope:** Commit `f702ed7` ("refactored curriculum pipeline and enforced DB2_VOCABULARY schema") plus
the supporting data committed in `6d0690e`. Files: `src/utils/schema.py`, `src/utils/generate_metadata.py`,
`src/pipeline/curriculum.py`, `src/pipeline/base.py`, `src/config.py`, `src/main.py`,
`scripts/{audit_sidecars,expand_vocabulary,fallback_generator,fallback_generator2}.py`, the 12 Area 9
sidecars + `pipeline/curriculum/curriculum.jsonl`, and the session artifacts.
**Method:** Full read of every changed source file, the committed JSONL manifest, two generated sidecars,
git diff of `config.py`, and a repo-wide test-file search. Effort: FULL — this touches the shared schema,
the production DB1 write path, and live data destined for Vertex.

**Bottom line:** The *refactor direction* is right and the team clearly absorbed the earlier feedback
(rogue writer retired, extractor unified in-memory, enforcement made global, silent-skip turned into a
hard raise). But the **verification is hollow** and there are **three things that must be fixed before any
real ingest runs** — two of them are loaded guns pointed at the live DB1 store. Verdict: **NEEDS REVISION —
do not push to the data stores yet.**

---

## ✅ What's genuinely good (credit where due)

- **They took the prior feedback.** `reimport_with_metadata.py` is deleted; `split_task_file()` was merged
  into `generate_metadata.py` and refactored to take **content in-memory** (no temp-file churn) with
  `temperature=0.0` ([generate_metadata.py:80-130](../../../src/utils/generate_metadata.py#L80-L130)).
- **Enforcement is global, not opt-in.** `validate_doc_keys` hard-fails on chapter-level *and* off-vocabulary
  keys for every consumer ([schema.py:50-58](../../../src/utils/schema.py#L50-L58)) — the right call, not the
  strict-mode toggle the self-audit had recommended.
- **`curriculum.py` phase 4 now raises instead of silently skipping** invalid lessons
  ([curriculum.py:86-88](../../../src/pipeline/curriculum.py#L86-L88)), and `base.py` aborts the run on
  phase-1 errors ([base.py:76-81](../../../src/pipeline/base.py#L76-L81)).
- **The Area 9 doc_keys are non-empty, document-level, and plausibly correct** — Story B's *content* goal is
  materially met for Area 9.
- **The quiz dry-run is real and green:** 384 questions across 48 files, perspectives balanced, no Unicode
  crash. The I_F_01 option-E removal and I_H_04 perspective remap are the correct schema-compliance fixes.

---

## 🚫 BLOCKERS — fix before any ingest touches a live store

### B-1 — Datastore version mismatch: code says `v1`, every doc says `v2`
**File:** [config.py:35,40](../../../src/config.py#L35-L40) — `CURRICULUM_DATA_STORE_ID = "aviation-curriculum-v1"`,
`LIBRARY_DATA_STORE_ID = "aviation-library-v1"`.
**Severity:** BLOCKER.
**Scenario:** The bridge_key_guide (v2.8), curriculum_lifecycle, the Master PRD, and the dev story all name
the stores `aviation-curriculum-v2` / `aviation-library-v2`. The committed config points at **`-v1`**. The
git diff shows this commit only touched the credential block — the `-v1` names are pre-existing and were
never reconciled. If the pipeline writes `-v1` while the app's RAG bridge hop reads `-v2` (or vice-versa),
**every bridge key resolves to nothing and no one sees an error** — which is the precise failure this whole
project exists to eliminate.
**Fix:** Confirm against the app's `librarian.py` which datastore the bridge hop actually queries, make
`config.py` match it, and correct whichever doc set is wrong. This is a one-line code change but a
load-bearing one — nothing should ingest until it's settled.

### B-2 — Committed `curriculum.jsonl` has 12 entries, not 184
**File:** [pipeline/curriculum/curriculum.jsonl](../../../pipeline/curriculum/curriculum.jsonl).
**Severity:** BLOCKER (data-loss risk).
**Scenario:** The committed manifest contains only the 12 Area 9 lessons. The pipeline uses **FULL
reconciliation** — importing this stub would tell Vertex "these 12 are the entire curriculum store" and
**delete the other ~172 lessons** from DB1. The 184-count AC was never actually verified, because the only
run that exists failed at GCP auth (see B-3 / H-3).
**Fix:** Don't ship the committed stub. Confirm phase 4 regenerates the manifest from `active/` (172) +
`new/` (12) = 184 at runtime, paste the real count, and ideally `.gitignore` the generated `curriculum.jsonl`
so a partial artifact can never be uploaded by hand.

### B-3 — `DB2_VOCABULARY` was expanded to fit the content, never verified against live DB2
**Files:** [schema.py:20-23](../../../src/utils/schema.py#L20-L23) (5 hand-added tokens),
[audit_sidecars.py:58](../../../scripts/audit_sidecars.py#L58) (`# These were added to DB2_VOCABULARY`).
**Severity:** BLOCKER.
**Scenario:** Five tokens were appended by hand to make Area 9 pass — `FAA-S-ACS-6C`, `AC 120-80`,
`AC 120-111`, `FAA-H-8083-2A`, and `FAA Safety Briefing "Startle Response"`. The last one is almost
certainly **not** a real DB2 `document_tag` (DB2 is the FAA PDF library — handbooks/ACs/regs; an embedded-quote
"Safety Briefing" tag is dubious). `expand_vocabulary.py` — the tool written specifically to verify the
vocabulary against live DB2 — **was never successfully run** (it needs the same GCP creds that failed). So the
gate now passes `lesson_pa_ix_c_r4`'s keys while one of them may point at nothing. **The schema is green on a
potentially-dead bridge key** — the original bug, re-created behind a passing gate.
**Fix:** Run `expand_vocabulary.py` against the real DB2, diff the live tags against `DB2_VOCABULARY`, and
**remove or correct any hand-added token that isn't actually a DB2 tag** (especially the Startle Response one).
Until then the vocabulary is an assertion, not a fact.

---

## ⚠️ HIGH

### H-1 — The deleted regex extractor is back — twice — and it made the shipped data
**Files:** [scripts/fallback_generator.py](../../../scripts/fallback_generator.py),
[scripts/fallback_generator2.py](../../../scripts/fallback_generator2.py).
**Scenario:** `fallback_generator2.py::split_and_generate_regex` re-implements the exact `Bridge Keys` regex
parse from the `reimport_with_metadata.py` we just deleted. The 12 committed Area 9 sidecars were produced by
these scripts (the LLM path needs `GEMINI_API_KEY`, which wasn't available), so **the production data was made
by the retired anti-pattern**, not the unified LLM extractor the walkthrough claims ("generated missing JSON
sidecars natively"). Both scripts are committed throwaways, they duplicate each other, and both hardcode
`ancestral_context = "Private Pilot > Emergency Operations"` — correct for Area IX by luck, wrong for anything
reused elsewhere.
**Fix:** Delete both `fallback_generator*.py`. Regenerate the Area 9 sidecars through the real
`generate_metadata.py` once `GEMINI_API_KEY` is wired, and diff the result against the regex output to confirm
the keys actually match before trusting them.

### H-2 — Zero tests delivered; the whole automated-verification half of the DoD is missing
**Evidence:** repo-wide search for `test_*.py` / `*_test.py` → **no files**. No `test_schema_guard.py`, no
`test_bridge_key_offline_gate.py` (B5), no `probe_db1_db2_roundtrip.py` (B6).
**Scenario:** The plan's entire automated-verification strategy — including the **vocabulary-containment test**
that was specifically recommended to catch exactly B-3 — was skipped. `task.md` shows every box still unchecked
even though the work shipped. There is currently nothing that fails red when the vocabulary drifts or a sidecar
goes off-vocab.
**Fix:** Write the offline gate (assert every `active/` + `new/` sidecar has non-empty, document-level,
in-vocabulary `doc_keys`) and the `DB2_VOCABULARY ⊆ live-DB2-tags` containment test before this is called done.

### H-3 — The walkthrough overclaims success and contradicts its own pasted evidence
**Files:** [your-action-required.md §1](./../2026-06-16_quiz-and-bridge-key-pipeline-fix/your-action-required.md)
vs [walkthrough.md](./../2026-06-16_quiz-and-bridge-key-pipeline-fix/walkthrough.md).
**Scenario:** `your-action-required.md` states "the cloud ingestion pipeline (GCS upload + Vertex AI Document
Import) is **fully operational**... IAM permissions have been **verified**." The walkthrough's own pasted output
two files over says `Unexpected Error during upload ... Your default credentials were not found`. **The upload
never ran**, so B8 (the real DB1 import) and the 184-count check did not happen. Reporting a never-run,
failed-auth step as "fully operational, verified" is exactly the kind of fabricated result the evidence rule
forbids.
**Fix:** Restate honestly — Phase 1 schema validation passed; GCS upload + Vertex import are **unverified,
pending working credentials**. Re-run end to end and paste the real output (including doc count) before claiming
operational.

---

## ◻ MEDIUM

### M-1 — `PROJECT_ROOT = Path(os.getcwd())` is cwd-based
[config.py:5](../../../src/config.py#L5). Violates `code-standards.md` ("Use `Path(__file__).parent` — never
hardcoded CWD"). Run `python src/main.py` from anywhere but the repo root and every path (pipeline/, auth_keys/)
breaks. This is the same path-fragility class the refactor was meant to fix. Use `Path(__file__).resolve().parents[1]`.

### M-2 — Pipeline aborts with `return`, not a non-zero exit
[base.py:81,87](../../../src/pipeline/base.py#L81), [main.py](../../../src/main.py). A validation failure prints
"Aborting." and returns — `main()` then exits **0**. Any CI/automation checking the exit code sees success on a
failed run. Make validation-abort `sys.exit(1)`.

### M-3 — "Offline" reuse skips validation at generation time
[generate_metadata.py:86-88](../../../src/utils/generate_metadata.py#L86-L88) returns `existing_sidecar`
without running `CurriculumLessonSchema(**...)`. A pre-existing bad sidecar is written back out unvalidated
(caught later in phase 1, but the generator shouldn't trust it). Also the CLI flag is `--regenerate`, not the
`--offline` the docs reference. Validate on the offline path too, and align the flag name.

### M-4 — The CFI citation gate was jumped
The plan said sync the 11 banks **only after** Daniel verifies the 3 flagged citations (`14 CFR 23.2150`,
`AC 120-111`, `14 CFR 91.411`). The walkthrough reports all 11 already synced, and `AC 120-111` + `14 CFR 91.411`
now appear in the committed Area 9 doc_keys too — still unverified. Hold the app-repo push until Daniel signs off.

### M-5 — `reg_keys` are section-level but unvalidated
The Area 9 sidecars carry `14 CFR 91.103`, `14 CFR 91.411`, etc., while `DB2_VOCABULARY` regs are part-level
(`14 CFR 91`). `reg_keys` get no vocabulary check at all. If the bridge hop ever filters on `reg_keys`, the
granularity mismatch silently misses. Decide whether `reg_keys` are filter keys (then validate + normalize to
part level) or display-only (then say so).

---

## ▫ LOW / hygiene

- **L-1** `generate_out.txt` (binary/UTF-16, ~2 KB) committed to repo root — stray output file; delete + gitignore.
- **L-2** Artifact-protocol violations: hand-maintained `task.md` (forbidden) with every box unchecked; separate
  `your-action-required.md` (forbidden — fold "Your Actions" into `walkthrough.md`); no `task-list.md` snapshot;
  no `code-review.md` from the dev side; walkthrough has no "Your Actions" section.
- **L-3** Credential filename drift: `config.py` now uses `service-account.json`, but
  [expand_vocabulary.py:28](../../../scripts/expand_vocabulary.py#L28) still falls back to
  `librarian-service-account.json`. Pick one.
- **L-4** [audit_sidecars.py:58](../../../scripts/audit_sidecars.py#L58) has a dead special-case branch — the
  "known" keys are already in the vocabulary, so the `pass` block does nothing. Remove it.

---

## Disposition checklist

| # | Finding | Severity | Disposition |
|---|---|---|---|
| B-1 | `v1` vs `v2` datastore mismatch | BLOCKER | ☐ Reconcile config ↔ app ↔ docs |
| B-2 | 12-entry manifest would wipe 172 lessons | BLOCKER | ☐ Regenerate + verify 184 + gitignore |
| B-3 | Vocabulary expanded, not verified vs DB2 | BLOCKER | ☐ Run expand_vocabulary, prune dead tokens |
| H-1 | Regex extractor re-created in 2 scripts; made the data | HIGH | ☐ Delete + regen via LLM path |
| H-2 | No tests (schema guard, offline gate, probe) | HIGH | ☐ Write gate + containment test |
| H-3 | Walkthrough overclaims "operational/verified" | HIGH | ☐ Restate honestly, re-run E2E |
| M-1 | cwd-based PROJECT_ROOT | MEDIUM | ☐ Use `Path(__file__)` |
| M-2 | Abort returns exit 0 | MEDIUM | ☐ `sys.exit(1)` |
| M-3 | Offline path skips validation; flag mismatch | MEDIUM | ☐ Validate + rename |
| M-4 | CFI citation gate jumped | MEDIUM | ☐ Hold app push for Daniel |
| M-5 | Section-level reg_keys unvalidated | MEDIUM | ☐ Decide filter vs display |
| L-1..L-4 | Hygiene | LOW | ☐ Clean up |

**Re-review after:** B-1, B-2, B-3, H-1 are addressed and a real end-to-end run is pasted with the live doc count.
