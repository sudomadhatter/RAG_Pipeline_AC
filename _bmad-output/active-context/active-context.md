# Active Context — RAG_Pipeline_AC

> Pick-up / hand-off state. Newest block on top; prune per context-hygiene (keep ~10 blocks).

## 2026-07-23 — SOP shipped · live quiz audit · re-balance plan awaiting approval
- **The two-team SOP is live:** `_docs/SOP_curriculum_operations.md` — stations & ownership, the
  Drive-intake STANDING RULE (new curriculum is pulled from Drive `ACS Modules`, base64-decode
  mechanic documented), per-lesson lifecycle w/ owners, quiz answer policy (NO positional meaning),
  live-store discipline, mirror policy. Lobby `router.md` (status → converted) and app `AGENTS.md`
  §6 (upstream row) now point here.
- **Read-only Firestore audit (evidence in scratchpad `firestore_pull/`):** skew confirmed live —
  `correct_answer` B 258/384 (67%), safety perspective has ZERO correct-D; repo↔live content drift
  NONE; only diff = 206 empty `sjt_rationale` fossils live-side (merge=True never deletes);
  manifests 48/48 identical; rotation state (`seen_by`) untouched everywhere — cleanest moment to fix.
- **Next action: Daniel reviews `_artifacts/2026-07-23_quiz-rebalance-firestore-truth/`**
  `implementation_plan.md` (story 6-3, now ready-for-dev). Blocked on "approved" + its 3 open
  questions (letter-free prose rewrite? batch cadence? legacy folder in git?).
- App-side fact for R3: `backend/routers/quiz.py:217` serves `sjt_rationale` to students — the 92
  real rationales + 263 letter-referencing explanations are the actual rewrite workload.

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
  (`_docs/SOP_curriculum_operations.md`), Drive-pull smoke test (ACS Modules folder).
- Session record: home base `_artifacts/_main/2026-07-22_pipeline-conversion-and-sop/`.
