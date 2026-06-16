# Walkthrough: Updated Artifact Rules and Directory Location

We updated the rules and configurations for both Gemini (Antigravity) and Claude Code to save artifacts (plans, checklists, walkthroughs, etc.) under `_01_My/_artifacts/` instead of `_artifacts/` or `_claude_artifacts/`.

## Changes Made

### Configuration & Rules

- **[.gemini/GEMINI.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/.gemini/GEMINI.md)**
  Updated Rule 6 to mandate saving plans, checklists, walkthroughs, and code review artifacts under `_01_My/_artifacts/<YYYY-MM-DD>_<summary>/`.
- **[AGENTS.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/AGENTS.md)**
  Updated the file/folder structure layout under Section 2 ("Artifacts Protocol") to use `_01_My/_artifacts/`.
- **[CLAUDE.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/CLAUDE.md)**
  Updated the section "Artifacts Protocol" to replace `_claude_artifacts/` with `_01_My/_artifacts/`.
- **[.claude/rules/artifacts-always-first.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/.claude/rules/artifacts-always-first.md)**
  Updated three references of `_claude_artifacts/` to `_01_My/_artifacts/`.
- **[.agent/rules/000-PLAN-FIRST-GATE.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/.agent/rules/000-PLAN-FIRST-GATE.md)**
  Added the repository's `_01_My/_artifacts/` folder as an allowed exception to the file modification rules.

### Workspace Verification

- Created the directory `_01_My/_artifacts/2026-06-16_add-artifact-rules/`.
- Saved the session's `implementation_plan.md`, `task.md`, and `walkthrough.md` files there as a permanent record.

## Your Actions

Run git status and commit the changes:

```bash
git add .gemini/GEMINI.md AGENTS.md CLAUDE.md .claude/rules/artifacts-always-first.md .agent/rules/000-PLAN-FIRST-GATE.md _01_My/_artifacts/
git commit -m "docs: relocate artifact directory rules to _01_My/_artifacts"
```
