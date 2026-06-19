---
description: End-of-session save — updates active-context tasks, captures learnings into component specs, and prunes stale data. Run after ANY session (dev, brainstorm, party mode, retro, research).
---

# Save Session (`/1_update-active-context`)

Run this before closing any session to save task state and learnings.

## Step 1: Read Current State & Artifacts
// turbo
Read these files:
1. `_bmad-output/active-context/active-context.md` — current tasks and pitfalls
2. `_bmad-output/project-context.md` — architecture rules
3. List `_bmad-output/component-specs/` — available specs
4. `_bmad-output/implementation-artifacts/sprint-status.yaml` — current sprint
5. Check for any recent `walkthrough.md`, `task.md`, `implementation_plan.md`, or updated story files in the conversation artifacts directory.
6. **Cross-reference `implementation_plan.md` vs `walkthrough.md`:** Compare what was *planned* against what was *actually built*. Deltas between these two artifacts reveal scope changes, discovered complexities, and implicit learnings that should be captured.

Display: how many active tasks, sprint objective, known pitfalls, and any plan-vs-walkthrough deltas.

## Step 2: Artifact & Code Verify Active Tasks
// turbo
Before making updates, **cross-check each active task against the actual codebase and recent artifacts:**

For each task in `## Active Tasks`:
1. Read the files listed in `Files In Play`
2. Grep for the fix/feature described in the task
3. Determine status: `✅ Code-Verified (Fixed)`, `❌ Not Found`, or `⚠️ Partial`

**Auto-move**: Any task marked `✅ Code-Verified` → prep to move to `## Completed Tasks` with today's date. 

## Step 3: Autonomous Learning Extraction
// turbo
Analyze the session's artifacts (`walkthrough.md`, `task.md`, updated code) to identify implicitly generated learnings that the system should remember. 

Catigorize automatically:
- **New architectural rule** → `project-context.md` (`## Critical Architecture Rules`)
- **New pitfall / gotcha / invariant** → `component-specs/[spec].md`
- **New bug discovered** → `active-context.md` (`## Active Tasks`)

## Step 4: Apply All Updates
// turbo
Execute the changes immediately without waiting for approval:
- **Completed tasks**: Move to `## Completed Tasks` with `- **Resolved:** YYYY-MM-DD`
- **Story Close-Out (Safety Net — MANDATORY)**: For every story worked this session, check its status. If the dev left it at `review` (or earlier) but the work is **code-verified complete**, the dev *missed the close-out* — finish it here. **Code review / QA is NOT always run**, so this workflow is the last line of defense for closure: set BOTH the story file AND the `sprint-status.yaml` entry to `done`. Story files may live in `_bmad/bmm/stories/` OR `_bmad-output/implementation-artifacts/epic-*/` — check both locations. The ONE exception: if the story is genuinely still mid-flight or failing verification, leave its status and flag it in the Step 6 summary. When the close-out call is ambiguous, confirm with the user in the Step 6 prompt before flipping to `done`.
- **Learnings**: Append to the appropriate specs/rules using format: `- **YYYY-MM-DD**: [Description]. (Source: Extracted from session artifacts)`
- **Last Updated**: Set to today's date in `active-context.md`

## Step 5: Housekeeping
// turbo
Prune stale data from `active-context.md`:
- Completed tasks over 5 → delete oldest
- Pitfalls already in a component spec → remove from here
- Duplicate entries → remove

**Pitfall Staleness Verification (MANDATORY):**
For each entry in `## Known V2 Pitfalls`:
1. If the pitfall references a **story dependency** (e.g., "depends on Story X"), check sprint-status. If the dependency is `done`, the pitfall is **stale** → remove it.
2. If the pitfall describes a **temporary degraded state** (e.g., "degraded until Story Y"), check if Story Y is `done`. If yes → **stale** → remove it.
3. If the pitfall references a **code pattern**, grep for it. If the pattern no longer exists in the codebase → **stale** → remove it.
4. If the pitfall is a **permanent architectural invariant** (e.g., "Firestore uses named DB"), it stays.
Log all removals in the Step 6 summary under `🧹 Housekeeping: Pruned stale pitfalls`.

**Size caps & Compression:** 
- If any component spec exceeds 120 lines, prune oldest pitfalls/failure modes (keep 8 most recent). 
- For `project-context.md`, optimal max is 150 lines; if it exceeds a hard cap of 200 lines, flag for review and sharding. 
- **CRITICAL:** *Always* attempt to autonomously optimize and compress `project-context.md` formatting by grouping rules and using highly effective, concise prompting to reduce line counts WITHOUT losing any semantic context.

## Step 6: End-of-Session Summary & Final Prompt

Show a clear summary of everything the workflow just did automatically:
> **Automated Updates Applied:**
> - ✅ Moved to Completed: [Tasks]
> - 🧠 Learnings Extracted: [Rule/Pitfall] → added to [File]
> - 🧹 Housekeeping: [Pruned items]

**Wait for User Input:**
Ask the user: 
> *"I have catigorized and saved the session updates based on the codebase and artifacts. Do you have any additional manual learnings, new bugs, or sprint objective changes to add before we close?"*

If the user provides additions, apply them to the appropriate files. Otherwise, the session save is complete.
