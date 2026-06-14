---
name: constitution
description: "Hard stops, confirmation gates, and partnership boundaries. For behavioral coding principles, see karpathy-guidelines.md."
activation: Always On
---

# Agent Constitution

Hard-stop rules that protect the codebase and the partnership. Behavioral coding principles (think before coding, simplicity, surgical changes, goal-driven execution) live in `karpathy-guidelines.md`.

## 🚫 Hard Stops

- Never modify any project file (source code, story files, sprint-status, configs, YAML — everything outside the artifact directory) without an approved `implementation_plan.md` — see `artifacts-always-first` rule
- Never treat "ok", "perfect", "continue", or "ready-for-dev" as authorization — require explicit approval
- Never execute `git commit` or `git push` — provide the command for the user to run manually
- Never fabricate citations or references — defer to verified sources or say "I don't know"
- Never create a new Firestore client — use `backend/database.py` → `get_db()` singleton
- Never hardcode secrets, API keys, or credentials
- Never modify SSE event contracts without updating BOTH backend + frontend

## ⚠️ Ask First

- Before deleting any file or removing any agent
- Before installing or upgrading dependencies (see `dependency-awareness` rule)
- Before changing Firestore schemas, security rules, or database topology
- Before modifying CI/CD, deployment, or environment configs
- Before any architectural change that crosses component boundaries
- Before approving a story that modifies both backend Python AND frontend TypeScript — flag for decomposition

## ✅ Always

- Always read `active-context.md` AND the matching Component Spec BEFORE writing any code
- Always update `active-context.md` at session end
- Always physically edit the `.md` story file status after completing a story
- Always perform at least one live QA session per epic before marking it done
- Always save code-review output as a `code-review.md` artifact in the session folder — inline-only findings are not allowed (see `artifacts-always-first` rule)
