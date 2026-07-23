---
IsArtifact: true
ArtifactMetadata:
  title: Quiz answer re-balance + Firestore truth reconciliation (board story 6-3)
  type: implementation_plan
  date: 2026-07-23
---

# Implementation Plan — Quiz Re-balance & Firestore Truth Reconciliation

## Goal

Fix the answer-key positional skew across all 48 quiz banks / 384 questions so correct answers are
evenly distributed with **no positional meaning**, reconcile the one repo↔live difference found, and
leave a permanent test gate so the skew can never silently return. Daniel's prescribed flow
(2026-07-23): legacy-snapshot the old banks → adopt the verified truth → fix → re-ingest → verify →
delete the legacy copies.

## What the 2026-07-23 read-only audit established (evidence for every step below)

Pulled the complete live store (48 `quiz_banks` parents + `questions` subcollections, 48
`rkp_manifests`) — saved at the session scratchpad `firestore_pull/` (audit script:
`firestore_readonly_audit.py`).

| Finding | Number | Consequence |
|---|---|---|
| **The skew IS live** — students see it | Live `correct_answer`: **B 258/384 (67%)** · C 70 (18%) · D 37 (9%) · A 19 (4%). Identical counts repo-side. Safety questions: **zero** correct-D | Yes, the problem exists in Firebase — fix both rungs |
| Content drift repo↔live | **NONE on any shared field.** 34 banks "differ" only because live carries `sjt_rationale: ""` (empty) on **206** questions the repo files don't have | Repo files ARE the current content truth — no store-side edits to rescue. "Pull the real ones" is satisfied by the saved pull; the fossils get deleted, not adopted |
| Fossil mechanism | `ingest_quiz_banks.py` writes with `merge=True` — a field removed from repo JSON survives live forever | The re-ingest must actively `DELETE_FIELD` the empties (R5) or they outlive the fix |
| RKP manifests | **48/48 byte-identical** repo↔live | Manifests need NOTHING this remediation |
| App reads `sjt_rationale` | `backend/routers/quiz.py:217` serves it (Chain-of-Cues); schema `Optional[str]` | The 92 real SJT rationales are student-facing prose — they must survive re-lettering coherently |
| Letter-anchored prose | **263/384 `explanation`** + the 92 `sjt_rationale` texts reference options by letter ("Option A chases…") | A mechanical shuffle breaks two-thirds of the feedback text — prose re-anchor (R3) is the real workload |
| Position-locked option texts | **1** in the whole corpus ("all/none of the above" style) | Pin it; everything else moves freely |
| App rotation state | `seen_by` non-empty on **0** questions | No student rotation state to protect yet — cleanest possible moment to do this |
| Corpus shape | Banks per ACS area: I 35 · III 3 · VI 3 · VII 2 · IX 2 · XI 3 | Batch R3 by area; Area I is the bulk |

## Phases

### R1 — Legacy snapshot (Daniel's safety net)

| Action | Detail |
|---|---|
| Copy `curriculum_components/quiz_banks/*.json` → `curriculum_components/quiz_banks_legacy_2026-07-23/` | Plain copy, NOT `git mv` — `config.QUIZ_BANKS_DIR` keeps pointing at the live folder; legacy sits beside it, invisible to every tool's glob |
| 3-line `README.md` in the legacy folder | What it is · why it exists · "delete after R6 verification on Daniel's word (R7)" |
| Level-2 `INDEX.md` row | Keep the conformance lint green |

### R2 — Deterministic re-letter (script, no prose edits)

| Action | Detail |
|---|---|
| NEW `scripts/rebalance_quiz_answers.py` | Per bank of 8: target multiset **{A,A,B,B,C,C,D,D}** — exact 2-each per bank ⇒ exactly 96 per letter corpus-wide. Deterministic (seed = `lesson_id`, no wall-clock), so re-runs are stable and reviewable |
| Mechanic | Permute option **texts** among labels so each question's correct text lands on its target letter; set `correct_answer`; options stay sorted A→D. The 1 position-locked option is pinned (its letter is consumed from the multiset first) |
| Output | Rewrites `quiz_banks/*.json` in place + prints an old→new letter table per question (goes in the walkthrough) |
| NOT touched | `explanation`, `sjt_rationale`, question `text`, ids, perspectives — R2 is pure mechanics |

### R3 — Prose re-anchor (the real work — agent batches, grounding-gated)

Rewrite the **263 letter-referencing explanations + 92 SJT rationales** to reference option
*content*, never letters ("The sectional chart is the definitive source…" not "Option B is
correct"). This permanently removes the fragility — any future shuffle becomes free.

| Rule | Detail |
|---|---|
| Factual invariance | No claim added, dropped, or altered — `faa-grounding-gate` discipline; `far_reference`/`acs_element` untouched |
| SJT rationales | Keep the Chain-of-Cues structure (why each wrong path fails) but name the *behavior* ("chasing the destination under time pressure"), not the letter |
| Batching | By ACS area (I in ~3 chunks of ~12 banks, then III/VI/VII/IX/XI in one) — reviewable diffs per batch |
| Sampling gate | Daniel spot-checks ~5 rewritten questions per batch before the next batch starts |

### R4 — Permanent test gate (additive, `src/tests/`)

| New test | Asserts |
|---|---|
| `test_answer_distribution.py` | Every bank: exactly 2 correct answers per letter · corpus: 96/96/96/96 |
| letter-reference lint (same file) | No `Option A`-style letter reference in any `explanation`/`sjt_rationale` (whitelisting airspace-class phrases like "Class B" via the option-context patterns) |
| Existing suite | `python -m pytest src/tests/ -q` stays green throughout |

### R5 — Ingester hygiene delta (kills the 206 fossils)

| Action | Detail |
|---|---|
| `src/gcp/ingest_quiz_banks.py` | When a question has no `sjt_rationale`, write `sjt_rationale: firestore.DELETE_FIELD` in the merge payload; dry-run report gains "would delete N fossil sjt_rationale fields" |
| Scope guard | No schema change — `src/utils/schema.py` and the app's `backend/schemas/quiz.py` (Optional field) are untouched |

### R6 — Ingest + prove (constitution gates)

1. `python src/gcp/ingest_quiz_banks.py` — **dry-run reviewed in-session** (expect: 48 banks / 384
   questions valid, ~206 fossil deletions announced).
2. **Daniel: "approved"** → `--execute`.
3. Re-run the audit script — expect: distribution **96/96/96/96**, drift `identical=48`, fossil
   fields **0**. Plus `generate_state_map.py --live` clean and `probe_bridge_hop.py` ≥1 hit
   (bridge untouched; cheap proof nothing else moved).

### R7 — Delete legacy + close out

Only after R6 proof AND Daniel's explicit word (constitution: deleting curriculum assets is
ask-first): remove `quiz_banks_legacy_2026-07-23/`, story `6-3` → `done`, walkthrough with the
before/after tables, commit command.

## Execution order

R1 → R2 → R3 (batched, sampling gate per batch) → R4 → R5 → R6 → R7. Natural pauses: after R2
(letter table reviewable), after each R3 batch, at the R6 dry-run.

## Open questions (answer at approval)

1. **R3 style — letter-free prose (my recommendation, encoded above)** vs. mechanically remapping
   letters in the text (cheaper, but stays fragile and regex-remapping letters in aviation prose is
   booby-trapped — "Class B airspace", "taxiway B"). Confirm letter-free.
2. **R3 volume:** ~355 prose rewrites is the bulk of the effort — OK to run as per-area batches
   across 1–2 sessions with your 5-question spot-check between batches? (Alternative: a multi-agent
   workflow pass — faster wall-clock, more tokens; say "use a workflow" if you want that.)
3. **Legacy folder in git:** commit it with the re-balance (safety net survives a machine loss,
   deleted in the R7 commit) — my recommendation — or keep it untracked so it never enters history?

## Verification plan

R4 tests green · R6 audit numbers (96×4, drift 48/48 identical, 0 fossils) · state map `--live`
clean · probe ≥1 hit · conformance lint exit 0 · walkthrough carries the full before/after
distribution table.

## Deliberate non-changes

RKP manifests (48/48 identical — untouched) · question `text`/mix/perspectives (pedagogy, not
remediation) · `src/utils/schema.py` + app schema (no contract change) · DB1/DB2 (quiz-only work) ·
`_my_resources/` everywhere.
