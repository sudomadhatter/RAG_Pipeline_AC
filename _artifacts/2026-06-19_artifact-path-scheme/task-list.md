---
IsArtifact: true
ArtifactMetadata:
  title: Task list — Per-tool artifact folders + command migration
  type: task_list
  date: 2026-06-19
---

# Task List (final snapshot)

- [x] Create `_opencode_artifacts/` + README
- [x] Migrate the 5 `_01_My/_artifacts/` session folders into `_claude_artifacts/` (diverged quiz folder preserved as `…__from-01My`)
- [x] Retire `_01_My/_artifacts/` entirely
- [x] CLAUDE.md → `_claude_artifacts/`
- [x] `.claude/rules/artifacts-always-first.md` → `_claude_artifacts/` (3 refs)
- [x] AGENTS.md → `_opencode_artifacts/`
- [x] `.gemini/GEMINI.md` + `.agent/rules/000-PLAN-FIRST-GATE.md` + `.agent/rules/prose-formatting.md` → IDE panel, no repo folder
- [x] Copy 9 Claude commands `.agent/workflows/` → `.claude/workflows/` (10 total now)
- [x] Verify: zero `_01_My/_artifacts` refs in governance docs; folders + counts correct
- [x] Write walkthrough.md + task-list.md
- [ ] Mirror `.agent/skills/` → `.claude/skills/` — deferred (not requested this round)
