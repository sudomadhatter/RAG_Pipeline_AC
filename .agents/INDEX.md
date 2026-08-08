# `.agents/` INDEX — RAG_Pipeline_AC project law (tier 2)

**This project holds only its OWN law.** All workflow law — rules, `/` commands, skills, workflows,
scripts, sync — lives in the command center (`Sudo_Hatter_Command/.agents/`) and is already loaded in
your session; nothing here duplicates it. Contract: the center's `.agents/rules/project-law.md`.

> ⛔ **Binding this project MEANS reading this file.** Every `/sudo-*` Step 0 §BIND and any work under
> `Projects/RAG_Pipeline_AC/` loads the `Load` column below before its first step.

## Rules (`rules/`)

| Rule | Load | Trigger — reach for it when… |
|---|---|---|
| `constitution.project.md` | **floor** | always, in this project — the curriculum-pipeline hard stops and carve-outs on top of the shared constitution. |
| `credential-resolution.md` | on-demand | running scripts or ingest jobs that need Firebase / Vertex credentials (pipeline-adapted — differs from AviationChat's). |

## Skills (`skills/`)

This project's domain — the curriculum-authoring and gated-ingest pipeline upstream of the app.
Loaded **by path** from here, never as slash commands:

| Skill | For |
|---|---|
| `rkp-manifest-creation` | authoring the per-lesson RKP manifests |
| `bridge-key-verification` | verifying Bridge Keys across the dual-store topology |
| `faa-grounding-gate` | the regulatory grounding gate on ingested content |
| `quiz-bank-generation` | generating the quiz banks from curriculum source |

## Not here (by design — 2026-08-07 thin conversion, SCC-31)

`hooks/` · the maintenance `scripts/` · the shared `rules/` · 4 toolkit skills · the toolkit
`AGENTS.md`/`CLAUDE.md`/`GEMINI.md` adapters · pointer txts · `.claude/{commands,skills,hooks}` ·
`.opencode/{commands,agent}` · `opencode.json`. All of it is the command center's, reachable from any
session. This repo was never on the sync allowlist, so its copies were frozen-stale before deletion.

## Jira

This repo has **no `jira.conf`** and no `.githooks/`, so the commit-msg gate no-ops here by design —
there is no separate Jira project for the pipeline. System work carries the lobby's `SCC-<n>` keys.
