# Active Context — RAG_Pipeline_AC

> Pick-up / hand-off state. Newest block on top; prune per context-hygiene (keep ~10 blocks).

## 2026-07-23 (close-out) — 6-3 CLOSED · docs merged into `docs/` · instrument track prepped
- **R7 done on Daniel's word:** `quiz_banks_legacy_2026-07-23/` and its `.gitignore` carve-out are
  deleted. Story `6-3` → **done** (DoD met: tests green, dry-run reviewed, `--execute` run, probe
  48/48, state map clean).
- **`_docs/` → `docs/` MERGE (Daniel moved `_docs` into `_my_resources`; that broke things, so we
  merged instead).** All documentation now lives in **one** `docs/` folder — SOP, PRD, `docs_prds/`,
  the 6 `instruction_docs/`, `project_context_prps/`, the 3 ACS PDFs, repo-map. `_my_resources/` is
  purely personal again (README + open_tasks). This also resolves the long-standing `docs/` vs
  `_docs/` split. **Why it mattered:** `_my_resources/` is excluded from the conformance lint, so the
  SOP + authoring guides had become invisible to the drift check (a false green), and the
  protected-area rule told agents to stay out of the very docs the skills require.
  - 30 files re-pointed; two generator scripts had the path as a **quoted segment**
    (`PROJECT_ROOT / "_docs" / ...`) which a `_docs/` text search misses — `generate_state_map.py`
    and `generate_repo_map.py` both fixed after one confirmed it was silently recreating a ghost
    `_docs/` on every run.
- **Instrument prep (verified, not assumed):** zero `PPL_` hardcoding in `src/`+`scripts/`; the app
  already namespaces by certificate (`backend/data/curriculum.py::get_certificate` splits the
  lesson_id on the FIRST underscore); Instrument ACS already on disk + already named in
  `faa-grounding-gate`. New **SOP §10** records the kickoff decisions and the step people forget.
- **NEW story `6-6`:** a lesson authored here is invisible to students until the **app repo's**
  `backend/data/curriculum_key.json` lists it — the one cross-repo write in the whole flow, and
  currently manual/undocumented in any tool. It will bite the instrument track at scale.
- Board seeded: **epic-7-instrument-kickoff** with the three decisions Daniel owns.

## 2026-07-23 (final) — story 6-3 SHIPPED TO FIRESTORE · R7 then completed
- **Daniel approved + spot-checked the prose** ("passes the in person test") → `--execute` run.
  **384 questions / 48 lessons ingested; 292 `sjt_rationale` DELETE_FIELDs sent.**
- **Live proof (read-only audit re-run):** `correct_answer` **96/96/96/96 (25% each)** · repo↔live
  **drift identical=48, differs=0 — the 206 empty-`sjt_rationale` fossils are GONE** · manifests
  identical=48 · `seen_by` still empty on all 384 (no rotation state disturbed) · `generate_state_map
  --live` clean · `probe_bridge_hop` **48/48 lessons ≥1 DB2 hit**. The safety perspective now has
  **D:24** where it previously had ZERO correct-D.
- **ONLY REMAINING: R7** — delete `curriculum_components/quiz_banks_legacy_2026-07-23/` and its
  `.gitignore` carve-out, on Daniel's explicit word (constitution: deleting curriculum is ask-first).
  Until then the frozen pre-rebalance snapshot stays as the rollback path.

## 2026-07-23 (late) — story 6-3 CODE-COMPLETE, blocked only on Daniel's `--execute` word
- **All repo-side work done and verified.** Corpus: **96/96/96/96** answer keys · **345 feedback
  fields letter-free** (282 explanations + 63 SJT rationales, all 48 banks) · **0** letter refs
  remain · suite **126 passed / 5 skipped**. Verified vs the legacy snapshot: **0 fabricated facts**
  (every added number traces to that question's own stem/options), 0 lost citations, and every
  non-prose field (ids, question text, `far_reference`, `acs_element`, perspectives) byte-identical.
- **R3 method changed mid-flight (recorded for next time):** the approved multi-agent fleet was
  abandoned after **three** session-limit failures (~5.6M subagent tokens; Fable ×2 then Opus ×1,
  which pushed the reset to 9:20pm and only finished 19/48 banks). Finished **inline** with
  *surgical positional replacement* — scratchpad `r3_surgical_extract.py` / `r3_surgical_apply.py`
  re-find each letter reference in document order and swap in a content phrase, leaving every other
  byte untouched (factual invariance by construction). Far cheaper and it actually completed.
  See [[workflow-fleets-session-limit]].
- Also hardened: the permanent test now also catches parenthetical letter LISTS (`(A, D)`), and the
  ~5 genuine bare refs ("while C and D have errors") were fixed explicitly — the narrow regex alone
  would have let those silently survive.
- **NEXT (Daniel's gate):** `python src/gcp/ingest_quiz_banks.py` dry-run is reviewed (48 banks /
  384 questions valid, **292** `sjt_rationale` fossil clears queued). On his "approved" →
  `--execute` → prove (96×4 live, drift identical=48, 0 fossils, state map, bridge probe) → **R7**
  delete `quiz_banks_legacy_2026-07-23/` + its `.gitignore` carve-out on his explicit word.

## 2026-07-23 — story 6-3 EXECUTING: R1/R2/R4/R5 done · R3 fleet blocked on session limit
- **Daniel approved** (letter-free prose · multi-agent R3 workflow · legacy folder committed).
  DONE: R1 legacy snapshot (byte-identical; `.gitignore` carve-out added so the JSONs can be
  staged) · R2 `scripts/rebalance_quiz_answers.py` EXECUTED — corpus was A19/B258/C70/D37, now
  **96/96/96/96**, 283 keys moved, texts/pins verified, letter table saved at
  `_artifacts/2026-07-23_quiz-rebalance-firestore-truth/r2_letter_map.md` · R4 gate
  `src/tests/test_answer_distribution.py` (distribution green; **letter-lint red by design until
  R3 applies** — 48 banks flagged) · R5 ingester `sjt_rationale` DELETE_FIELD + dry-run report.
- **R3 in flight, paused:** multi-agent workflow (rewrite → adversarial verify → repair, per bank;
  real workload 282 explanations + 63 sjt_rationales on 315 questions; 29 rationales already
  clean). Two fleet launches hit the Claude session limit (~1.8M subagent tokens burned; 9 banks'
  rewrites journal-cached + 16 valid rewrite files on disk, none verified yet). **Resume the
  workflow after the 3:20pm ET reset** — cached rewrites replay free.
- SOP §6 now carries the full authoring direction (balanced key + letter-free prose rules);
  `quiz-bank-generation` skill (master + mirror) de-positionalized — the old "SJT answer = D" grid
  is retired at the authoring surface too.
- Mid-flight sweep commits (00:52–00:57 ET, `22be19e`/`73632c7`) captured conversion + R1/R2 —
  verified clean of credentials/PDFs/generated manifests. Remaining uncommitted: board/INDEX/
  gitignore/records deltas (commit command in the home-base walkthrough).
- **NEXT: resume R3 → apply verified rewrites → suite fully green → R6 dry-run → Daniel's
  "approved" → `--execute` → prove (96×4, drift identical=48, 0 fossils) → R7 delete legacy on his
  word.** New adjacent bug filed as story 6-5: ingester always writes `seen_by: []`, so a future
  re-ingest would reset live rotation state (harmless today — rotation state is empty everywhere).

## 2026-07-22 — House-standard conversion (run from the command center)
- Converted to the house standard: pointer `CLAUDE.md`/`GEMINI.md` front doors, Layer-2 `AGENTS.md`
  (the workspace map), vendored `.agents/` (19 master rules + project-local rules), `_artifacts/`
  consolidation (old `_claude_artifacts/` + `_opencode_artifacts/` retired), GitNexus governance
  DROPPED (removed from ac-stack group; local index deleted), md-feedback MCP wired (`.mcp.json`).
- **Branch model: single `main` by design** (Daniel, 2026-07-22) — never add `main_debug` here; the
  protected surface is the data stores, guarded by `constitution.project.md`.
- Curriculum skills (project-owned): `rkp-manifest-creation` · `quiz-bank-generation` ·
  `bridge-key-verification` — masters now in `.agents/skills/`, mirrors in `.claude/skills/`;
  `faa-grounding-gate` being added next.
- Next up: BMAD-lite board seed (`_bmad-output/`), the two-team SOP
  (`docs/SOP_curriculum_operations.md`), Drive-pull smoke test (ACS Modules folder).
- Session record: home base `_artifacts/_main/2026-07-22_pipeline-conversion-and-sop/`.
