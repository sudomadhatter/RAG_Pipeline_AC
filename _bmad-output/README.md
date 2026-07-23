# _bmad-output/ — the board (BMAD-LITE, by decision)

This repo runs **BMAD-lite**: the *state* files only. There is deliberately **no `_bmad/` module
here** — no BMAD agents, no workflows, no `bmad-*` skills, and none of the TEA/testing family
(Daniel, 2026-07-22: "we don't need it heavy like this").

**How it works:** the sudo flow lives at the **command center** (`c:\Sudo_Hatter_Command`), which
has the full BMAD install. You run `/sudo-boot-sprint-memory`, `/sudo-create-epic-sprint`, etc.
*from there*, pointed at this project; those commands read and write the files below. This repo
only has to hold honest state.

| File | What |
|---|---|
| `project-context.md` | What this project is, its stores, its gates — the orientation doc |
| `active-context/active-context.md` | **The continuity file.** "pick up" / "hand off" reads and writes this (matches the AGY convention — NOT `_artifacts/active-context.md`) |
| `implementation-artifacts/sprint-status.yaml` | The board: epic + story statuses |

Session artifacts (plans, walkthroughs) do **not** live here — they go to `_artifacts/`.

## Definition of done (curriculum work)
This project's stories close on **its own gates**, not the app's test tiers: `pytest src/tests/`
green · dry-run reviewed · `--execute` run · `probe_bridge_hop.py` ≥1 hit for every touched lesson ·
`generate_state_map.py --live` counts matching intent. No ATDD red-phase, no TEA gate.
