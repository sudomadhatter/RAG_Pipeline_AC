# Implementation Plan: Update Artifact Creation Rules & Destination

Add rules to `.gemini/GEMINI.md`, `CLAUDE.md`, `.claude/rules/artifacts-always-first.md`, and `AGENTS.md` to save session plans, walkthroughs, task lists, and other artifacts in `_01_My/_artifacts/<YYYY-MM-DD>_<summary>/` instead of the root `_artifacts/` or `_claude_artifacts/`.

## User Review Required

> [!IMPORTANT]
> - Artifacts will now be saved within the repository under the path `_01_My/_artifacts/<YYYY-MM-DD>_<summary>/` (e.g., `_01_My/_artifacts/2026-06-16_add-artifact-rules/`).
> - This ensures they are tracked in git and persisted with the codebase.

## Open Questions

None.

## Proposed Changes

---

### Configuration & Rule Updates

#### [MODIFY] [GEMINI.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/.gemini/GEMINI.md)
Update Rule 6 to specify the new save location: `_01_My/_artifacts/<YYYY-MM-DD>_<summary>/`.

#### [MODIFY] [AGENTS.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/AGENTS.md)
Update Section 2 ("Artifacts Protocol") to replace the root `_artifacts/` with `_01_My/_artifacts/`.

#### [MODIFY] [CLAUDE.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/CLAUDE.md)
Update Section "Artifacts Protocol" to replace `_claude_artifacts/` with `_01_My/_artifacts/`.

#### [MODIFY] [artifacts-always-first.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/.claude/rules/artifacts-always-first.md)
Update references to the artifact directory from `_claude_artifacts/` to `_01_My/_artifacts/`.

#### [MODIFY] [000-PLAN-FIRST-GATE.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/.agent/rules/000-PLAN-FIRST-GATE.md)
Update the exception path in Section "What Counts as a Project File" to point to the new location `_01_My/_artifacts/` in addition to the IDE/system artifact directory.

## Verification Plan

### Manual Verification
- Review updated rule files to verify correctness.
- Verify that directory paths are consistent across Gemini, Claude, and Agent rules.
- Test by creating the directories and saving the current session's artifacts in the new folder: `_01_My/_artifacts/2026-06-16_add-artifact-rules/`.
