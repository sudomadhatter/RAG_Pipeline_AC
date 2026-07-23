---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — Per-tool artifact folders + Claude command migration
  type: walkthrough
  date: 2026-06-19
---

# Walkthrough — Per-tool separation

## What you asked
You started by noticing artifacts landing in two places. The real intent turned out bigger: each
agent tool should have its **own** artifact home so Claude, Gemini/Antigravity, and opencode never
collide in a shared folder. Claude → `_claude_artifacts/`, opencode → `_opencode_artifacts/`, and
Gemini uses its built-in IDE artifact panel (no repo folder). You also wanted Claude's slash
commands to live under `.claude/` rather than borrowing Gemini's `.agent/` copies.

## The detour worth recording
My first pass went the wrong direction — I consolidated everything onto `_01_My/_artifacts/` and
deleted `_claude_artifacts/`, the opposite of what you wanted. Nothing was committed, and
`_claude_artifacts/` was git-tracked, so `git reset` + `git checkout HEAD --` reversed it cleanly
and your unrelated curriculum work stayed put. Lesson logged: Claude's home is `_claude_artifacts/`.

## What I did, in order

**1. Folders & history.** Created `_opencode_artifacts/` (with a README). Retired
`_01_My/_artifacts/` entirely: `git mv`'d its five session folders into `_claude_artifacts/`. One
folder (`2026-06-16_quiz-and-bridge-key-pipeline-fix`) existed in both and had diverged, so the
`_01_My` copy was preserved as `…__from-01My/` rather than overwriting. The empty
`_01_My/_artifacts/` and its redundant README were removed.

**2. Governance docs** — each tool now points only at its own destination:

| File | Change |
|---|---|
| `CLAUDE.md` | artifact folder → `_claude_artifacts/` |
| `.claude/rules/artifacts-always-first.md` | every `_01_My/_artifacts/` → `_claude_artifacts/` (3 spots) |
| `.claude/rules/prose-formatting.md` | already `_claude_artifacts/*` — untouched |
| `AGENTS.md` | artifact folder → `_opencode_artifacts/` |
| `.gemini/GEMINI.md` | dropped the repo-folder instruction; clarified the IDE Artifacts panel IS Gemini's store |
| `.agent/rules/000-PLAN-FIRST-GATE.md` | dropped the `_01_My/_artifacts/` exception; Antigravity uses the IDE panel |
| `.agent/rules/prose-formatting.md` | carve-out now names "the Antigravity artifact panel" |

**3. Command migration.** Copied the nine CLAUDE.md slash commands that only lived in
`.agent/workflows/` into `.claude/workflows/` (`1_update_repo_map` was already there → left as is).
Copied, not moved, so Gemini keeps its set in `.agent/`. The only artifact-path references in the
copies (`1_live_testing_team.md`) already said `_claude_artifacts/`, so nothing needed rewriting. The
four Gemini-only workflows (`1_firebase-user-cleanup`, `1_push-to-main-and-deploy`,
`slash_command_updating`, `webm-alpha-video`) stayed in `.agent/` only.

## Verification (actual output)

```
=== any _01_My/_artifacts left in governance docs? ===
  CLEAN — no _01_My/_artifacts in any governance doc

=== per-tool folders present ===
_claude_artifacts
_opencode_artifacts
ls: cannot access '_01_My/_artifacts': No such file or directory   <- retired, as intended

=== each tool's doc points at its own folder ===
-- CLAUDE.md --   _claude_artifacts/
-- AGENTS.md --   _opencode_artifacts/
-- GEMINI.md --   IDE Artifacts panel  (+ notes the other tools' folders)

=== .claude/workflows count (expect 10) ===
10
```

Git recorded the history move as proper renames (`R`), so `git log --follow` still works on the
moved artifacts.

## Deviations from plan
None of substance. The `_01_My/_artifacts/` directory removal came "for free" when `git rm` took the
last tracked file (the `rmdir` reported non-zero only because the dir was already gone).

## Your Actions

**1. Commit — explicit paths only** (the tree also holds unrelated curriculum work; do NOT `git add -A`):

```bash
git add \
  CLAUDE.md AGENTS.md .gemini/GEMINI.md \
  .claude/rules/artifacts-always-first.md \
  .agent/rules/000-PLAN-FIRST-GATE.md .agent/rules/prose-formatting.md \
  .claude/workflows/ _claude_artifacts/ _opencode_artifacts/ \
  "_01_My/_artifacts"
git commit -m "Per-tool artifact folders: Claude=_claude_artifacts, opencode=_opencode_artifacts, Gemini=IDE panel; migrate Claude commands to .claude/workflows"
```

(The quoted `_01_My/_artifacts` path stages the rename/deletes out of the retired folder.)

**2. Optional cleanup:** if you don't want the preserved divergent copy, delete
`_claude_artifacts/2026-06-16_quiz-and-bridge-key-pipeline-fix__from-01My/` — its content overlaps
the sibling `…-pipeline-fix/` folder.

**3. Decide later (not done here):** whether Claude also needs the 40+ `.agent/skills/` mirrored into
`.claude/skills/`. You only asked for commands this round; skills were left untouched.
