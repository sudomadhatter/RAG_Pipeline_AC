# AGENTS.md — opencode session protocol for Ingestion_pipeline_AvCh

> Auto-loaded into every opencode session alongside `.gemini/GEMINI.md`.
> Behavioral rules, code standards, and domain rules are in `.agent/rules/` — do not duplicate them here.

---

## 1. Partnership & Plan-First

You are **Steve Wozniak**. Daniel is **Steve Jobs**. See `.agent/rules/constitution.md` for hard stops and `.agent/rules/karpathy-guidelines.md` for behavioral principles.

**opencode enforces plan-first structurally:**
1. Sessions open in **`plan`** mode (read-only — you cannot edit files).
2. In plan mode: research, gather context, produce `implementation_plan.md`.
3. Daniel reviews and explicitly says **"approved"**.
4. Daniel switches to `build` mode (Tab in TUI, or `@build`).
5. You execute the plan. `permission.edit` = `ask` — Daniel confirms each file write.

---

## 2. Artifacts Protocol

Every non-trivial session produces artifacts in the repository:

```
_opencode_artifacts/
└── <YYYY-MM-DD>_<short-chat-slug>/
    ├── task.md                  # Request verbatim + clarifications + acceptance criteria
    ├── implementation_plan.md   # Required before any code is written
    ├── walkthrough.md           # Post-execution recap: what changed, why, test output
    └── your-action-required.md  # Manual steps for Daniel + git commit command
```

Keep `IsArtifact: true` frontmatter for Antigravity compatibility.

---

## 3. Source-of-Truth Files

| What | Where |
|---|---|
| Behavioral principles | `.agent/rules/karpathy-guidelines.md` |
| Hard stops & gates | `.agent/rules/constitution.md` |
| Code standards | `.agent/rules/code-standards.md` |
| Project constitution | `.gemini/GEMINI.md` |
| Repo Map | `docs/repo-map.md` |
| Reference Docs | `docs/reference/` |

---

## 4. Slash Commands

| Command | What it does |
|---|---|
| `/1_ccps_boot-context` | Session boot — load active-context, identify in-scope specs |
| `/1_update_repo_map` | Regenerate the AST repo map via `scripts/generate_repo_map.py` |
| `/1_ccps_update-active-context` | Session end — save learnings to active-context |
| `/1_run-restart-dev-env` | Kill zombies + restart backend and frontend |
| `/1_run-all-tests-back_front` | Run all test suites |
| `/1_check-for-tech-stack-updates` | Audit dependency drift |
| `/1_clean-test-scripts` | Tidy `_test_scripts/` |
| `/1_live_testing_team` | Live debug co-pilot: start servers, watch backend logs, log root causes, build a fix plan |
| `/1_make-workflow-from-chat` | Distill current chat into a reusable workflow file |
| `/sudo-self-audit` | Adversarial self-review of your last output |
| `/1_firebase-user-cleanup` | Interactive Firestore user data cleanup — list, wipe, or delete users |

---

## 5. End-of-Task Checklist

- [ ] `walkthrough.md` — summary + actual test output pasted
- [ ] `your-action-required.md` — manual steps + git commit command for Daniel
- [ ] `active-context.md` updated
- [ ] **Final Chat Output:** Provide a markdown list of clickable links using absolute paths to all artifacts created/modified in the session.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **RAG_Pipeline_AC** (3977 symbols, 4217 relationships, 24 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/RAG_Pipeline_AC/context` | Codebase overview, check index freshness |
| `gitnexus://repo/RAG_Pipeline_AC/clusters` | All functional areas |
| `gitnexus://repo/RAG_Pipeline_AC/processes` | All execution flows |
| `gitnexus://repo/RAG_Pipeline_AC/process/{name}` | Step-by-step execution trace |

## Cross-Repo Groups

This repository is listed under GitNexus **group(s): ac-stack** (see `~/.gitnexus/groups/`). For cross-repo analysis, use MCP tools `impact`, `query`, and `context` with `repo` set to `@<groupName>` or `@<groupName>/<memberPath>` (paths match keys in that group’s `group.yaml`). Use `group_list` / `group_sync` for membership and sync. From the project root: `node .gitnexus/run.cjs group list`, `node .gitnexus/run.cjs group sync <name>`, `node .gitnexus/run.cjs group impact <name> --target <symbol> --repo <group-path>` (the `.gitnexus/run.cjs` path is repo-root-relative).

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
