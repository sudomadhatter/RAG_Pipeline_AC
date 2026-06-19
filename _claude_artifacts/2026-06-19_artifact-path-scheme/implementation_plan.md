---
IsArtifact: true
ArtifactMetadata:
  title: Per-tool artifact folders + Claude command migration
  type: implementation_plan
  date: 2026-06-19
---

# Implementation Plan — Per-tool separation (folders + commands)

## Final target state

**Artifact folders (per tool):**
- `_claude_artifacts/` — Claude (keep; absorbs the retired `_01_My/_artifacts/` history)
- `_opencode_artifacts/` — opencode (new)
- **Gemini / Antigravity → no repo folder.** It uses the IDE's built-in artifact feature
  (the `IsArtifact: true` Artifacts panel, per GEMINI.md Rule 6).
- `_01_My/_artifacts/` — **RETIRED** entirely.

**Command homes:**
- `.claude/` — Claude's rules + skills + workflows
- `.agent/` — Gemini's rules + skills + workflows (left intact for Gemini)

## Part 1 — Folders & history migration
1. Create `_opencode_artifacts/README.md` (self-describing placeholder, mirrors the others).
2. `git mv` the four non-colliding session folders from `_01_My/_artifacts/` → `_claude_artifacts/`:
   `2026-06-16_add-artifact-rules`, `2026-06-17_pipeline-fix-revision`,
   `2026-06-17_pipeline-qa-code-review`, `2026-06-18_bridge-ground-truth-fix`.
3. Collision: both folders already have `2026-06-16_quiz-and-bridge-key-pipeline-fix/` and they
   diverged. Preserve both — move the `_01_My/` copy in as
   `_claude_artifacts/2026-06-16_quiz-and-bridge-key-pipeline-fix__from-01My/`.
4. Remove the now-empty `_01_My/_artifacts/` (its `README.md` is redundant with `_claude_artifacts/README.md`).

## Part 2 — Governance doc edits

| File | Change |
|---|---|
| `CLAUDE.md:22` | `_01_My/_artifacts/` → `_claude_artifacts/` |
| `.claude/rules/artifacts-always-first.md` | every `_01_My/_artifacts/` → `_claude_artifacts/` (incl. the L36 "ONLY exception" line, L52 folder path, L100 code-review path) |
| `.claude/rules/prose-formatting.md:24` | already `_claude_artifacts/*` — no change |
| `AGENTS.md:26` | `_01_My/_artifacts/` → `_opencode_artifacts/` |
| `.gemini/GEMINI.md:31` | **delete** the "Additionally … MUST be saved in `_01_My/_artifacts/…`" paragraph. Rule 6's `IsArtifact`/IDE-panel instruction stays — that IS Gemini's artifact mechanism. |
| `.agent/rules/000-PLAN-FIRST-GATE.md:30` | drop the "and the repository's `_01_My/_artifacts/` folder" clause; keep the Antigravity system artifact dir as the sole exception |
| `.agent/rules/prose-formatting.md:24` | `_claude_artifacts/*` → "the Antigravity artifact directory" (Gemini's, not a repo path) |

## Part 3 — Command migration (`.agent/workflows/` → `.claude/workflows/`), COPY
Copy the CLAUDE.md-listed slash commands into `.claude/workflows/` so Claude uses its own copies.
`1_update_repo_map.md` is already there → leave it. Copy the other nine:
`1_ccps_boot-context`, `1_ccps_update-active-context`, `1_run-restart-dev-env`,
`1_run-all-tests-back_front`, `1_check-for-tech-stack-updates`, `1_clean-test-scripts`,
`1_live_testing_team`, `1_make-workflow-from-chat`, `1_self-audit-stress-test`.

- Normalize any artifact-path reference inside the copies to `_claude_artifacts/`.
- **COPY, not move** — `.agent/workflows/` stays intact so Gemini keeps its command set
  (reversible; veto if you want a clean move instead).
- The 4 non-listed `.agent` workflows (`1_firebase-user-cleanup`, `1_push-to-main-and-deploy`,
  `slash_command_updating`, `webm-alpha-video`) are Gemini-only → left in `.agent/` only.

## Part 4 — This session's artifacts
Already live in `_claude_artifacts/2026-06-19_artifact-path-scheme/`. Add `walkthrough.md` + `task-list.md` at the end.

## Verification
- `grep _01_My/_artifacts` → zero hits in any governance doc (CLAUDE.md, `.claude/rules/*`, AGENTS.md, `.gemini/GEMINI.md`, `.agent/rules/*`).
- `_01_My/_artifacts/` no longer exists; the 5 sessions are under `_claude_artifacts/`.
- `.claude/workflows/` holds all 10 Claude commands.
- `_opencode_artifacts/` exists.
- Commit staged with an **explicit file list** (never `git add -A` — unrelated curriculum work is in the tree).

## Decisions baked in (veto any before approval)
- Gemini gets **no** repo folder (uses IDE built-in artifacts).
- Old history migrates to `_claude_artifacts/`; the diverged quiz folder preserved as `…__from-01My`.
- Commands are **copied** (not moved) so Gemini keeps them.

## Out of scope (unchanged)
- `.agent/skills/` and `.claude/skills/` (no skill migration requested).
- Cross-repo `AGY_AVIATIONCHAT/_claude_artifacts/…` citations.
