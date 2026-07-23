# _artifacts/ — session artifacts (project-local)

Every non-trivial session in this repo lands here. **This project owns its history** — artifacts
live project-local so they travel with the repo (the home base finds them here).

## Placement
- Normal session → `_artifacts/<YYYY-MM-DD>_<slug>/` (date FIRST so folders sort chronologically)
- BMAD story → `_artifacts/epic_<E>/<story>/` (create the epic folder if missing)
- NEVER `_claude_artifacts/` or `_opencode_artifacts/` — retired 2026-07-22 (their history was
  consolidated here via `git mv`)

## The session set (full protocol → `.agents/rules/artifacts-always-first.md`)
`implementation_plan.md` (approved before any project file is touched) → execute → ONE
`walkthrough.md` ending in `## Task Checklist` + `## Your Actions` (+ `code-review.md` whenever a
review runs). Frontmatter `IsArtifact: true` + `ArtifactMetadata` on every artifact file.

## Continuity
The pick-up/hand-off state file is **`_bmad-output/active-context/active-context.md`** (the BMAD
convention — it does NOT live here). `INDEX.md` in this folder is the session ledger — append one
row per session, newest at the bottom.
