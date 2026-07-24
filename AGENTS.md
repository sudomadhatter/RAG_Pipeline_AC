# AGENTS.md — RAG_Pipeline_AC  (workspace map · Layer 2)

## 1. ROOT LAW (prime mission)
**The curriculum machine room for AviationChat.** This repo turns CFI teaching content — authored in
Google Drive, exported as master modules — into the machine artifacts the app consumes (split
micro-lessons, RKP manifests, quiz banks, flashcards, bridge keys) and ingests them into the
production stores: Vertex **DB1** `aviation-curriculum-v2` (teaching) · **DB2** `aviation-library-v2`
(FAA library) · **Firestore** `aviationchat-database` (`rkp_manifests`, `quiz_banks`). It is
**separate from, and upstream of, the app repo** (`../AGY_AVIATIONCHAT/`): sync direction is
pipeline → app; the app only consumes what is produced here. **The partnership:** Daniel = Steve Jobs
(vision, curriculum truth, citation verification — the one human content gate); you = Steve Wozniak
(the "how" — bring the solution + tradeoffs + a recommendation, not a pile of open questions).
**Accuracy over speed: never invent an FAA fact.**

## 2. START HERE
You're inside this workspace. **Don't read the whole tree** — use the routing table (§6) to load only
what the task needs. If what you need isn't here, **GO BACK** to the home-base `../../router.md`.
Before any risky/irreversible action → §8 GATES. **This is a DATA-CRITICAL repo — the live stores ARE
production** (there is no staging tier). **Entering any folder: if it carries an `AGENTS.md`, read
that FIRST**; read its `INDEX.md`/`README.md` only when you need the inventory.

## 3. MAP / MISSION / SUPPORT
- **MAP:** key folders —
  - `src/gcp/` — the gated ingestion tools (dry-run by default; `--execute` writes live). The ONLY
    write entry points.
  - `src/utils/` · `src/tests/` — schema gate + the offline test suite (33 tests, no cloud needed).
  - `src/config.py` — ALL path/env resolution (single source of truth; never hardcode machine paths).
  - `pipeline/curriculum/` — DB1 source store: `elements/` (split micro-lessons) · `sidecars/`
    (Area IX metadata) · `new/` (inbox) · generated `curriculum.jsonl` (**NEVER commit**).
  - `pipeline/library/` — FAA source PDFs: `new/` → `active/` → `superseded/` (PDFs gitignored).
  - `curriculum_components/` — authored assets: `curriculum_modules/` (masters exported from Drive) ·
    `rkp_manifests/` · `quiz_banks/` · `lesson_podcasts/` (scripts only; audio lives in Drive).
  - `docs/` — **all documentation, one folder** (merged 2026-07-23; there is no `_docs/`):
    **the two-team SOP** (`SOP_curriculum_operations.md`) · the PRD
    (`docs_prds/Master_Curriculum_Pipeline.md`) · `asset_registry.md` · generated `STATE.md` ·
    the 6 authoring guides (`instruction_docs/`) · product context (`project_context_prps/`) ·
    the 3 ACS PDFs (grounding sources) · `repo-map.md` (navigation index).
  - `.agents/` — vendored toolkit (rules · skills · scripts · hooks), deliberately **LEAN** (Daniel,
    2026-07-22): curriculum + hygiene skills only — no sudo flow, no autopilots, no app skills.
    Shared rules edit at the lobby master then re-sync; **a blanket `/sync-agents -Target` re-imports
    the full kit — re-prune to the keep-list in `.agents/skills/INDEX.md` after any rules refresh.**
  - `_artifacts/` — session artifacts, project-local (continuity file lives in `_bmad-output/` — §9).
  - `_my_resources/` — **Daniel's personal area. Protected: do NOT edit or reference unless he says so (§8).**
- **MISSION:** author curriculum artifacts (skills-gated), ingest them (dry-run-gated), prove them
  (bridge probe + state map) — batched by ACS Area via the BMAD-lite board.
- **SUPPORT:** rules load by path from `.agents/rules/`; the authoring skills are
  `rkp-manifest-creation` · `quiz-bank-generation` · `bridge-key-verification` · `faa-grounding-gate`
  (Claude resolves them from `.claude/skills/`); the sprint board lives in `_bmad-output/`.

## 4. ALWAYS-LOAD (small)
- `.agents/rules/operator-profile.md` (**who you're talking to** — Daniel is the visionary/chair, you
  are the engineer; the eight speaking obligations that govern every reply) +
  `.agents/rules/constitution.md` (shared hard stops) + `.agents/rules/constitution.project.md`
  (**THIS repo's data-side hard stops**) + `.agents/rules/karpathy-guidelines.md` (how to work) +
  `.agents/rules/artifacts-always-first.md` (the plan-first gate — see §5).

## 5. ARTIFACTS PROTOCOL — MANDATORY FIRST ACTION
Before touching any project file (anything outside `_artifacts/`): create
`_artifacts/<YYYY-MM-DD>_<slug>/` (**project-local** — this repo owns its history), start the live
**TodoWrite** list, write `implementation_plan.md`, present its key points inline, and **STOP until
Daniel says "approved."** Close with ONE `walkthrough.md` ending in `## Task Checklist` (final
TodoWrite snapshot) + `## Your Actions` (manual steps + the exact git command). Skip only for
read-only/investigatory asks and trivial one-liners. Full protocol →
`.agents/rules/artifacts-always-first.md`.

## 6. ROUTING TABLE (task → read these / skills)
| Task | Read these | Skills / tools |
|---|---|---|
| Session boot / "what's the state?" | `docs/repo-map.md`, `_bmad-output/active-context/active-context.md`, `_bmad-output/project-context.md`, `docs/docs_prds/STATE.md` (regen: `python scripts/generate_state_map.py [--live]`) | `/sudo-boot-sprint-memory` — run FROM the command center (the sudo flow + BMAD module live at the lobby, not in this repo) |
| **How the two teams work together** | `docs/SOP_curriculum_operations.md` | — |
| Pull new masters from Drive | the SOP's Drive-station section (folder: `AVIAIONCHAT/ACS Modules`) | Google Drive connector (interactive sessions only) |
| Author / edit an RKP manifest | the master module + `docs/instruction_docs/rkp_creation_guide.md` | `rkp-manifest-creation` + `faa-grounding-gate` |
| Author / edit a quiz bank | the lesson's RKP manifest + `docs/instruction_docs/quiz_authoring_guide.md` | `quiz-bank-generation` + `faa-grounding-gate` |
| Verify bridge keys / DB1↔DB2 | `docs/instruction_docs/bridge_key_guide.md` | `bridge-key-verification` |
| Ingest / repair the live stores | README "Common operations" table + the tool's `--help` | gated `src/gcp/*` (constitution.project gates apply) |
| Prove it end-to-end | `src/gcp/probe_bridge_hop.py` (read-only) + `generate_state_map.py --live` | — |
| Full end-to-end mental model | `docs/docs_prds/Master_Curriculum_Pipeline.md` (the PRD) | — |
| Story / sprint work | `_bmad-output/implementation-artifacts/sprint-status.yaml` + the story file | `bmad-*` skills |
| **"What's next" / open tasks** (Daniel's notes) | `_my_resources/open_tasks/todo_list.md` — **READ-ONLY** (never edit; cross-check vs live files) | — |

### Source-of-truth files
| What | Where |
|---|---|
| Repo map / navigation index (read FIRST) | `docs/repo-map.md` |
| End-to-end PRD · asset inventory · live state | `docs/docs_prds/Master_Curriculum_Pipeline.md` · `asset_registry.md` · `STATE.md` (generated) |
| The two-team SOP | `docs/SOP_curriculum_operations.md` |
| Sprint board · active context · project context | `_bmad-output/implementation-artifacts/sprint-status.yaml` · `_bmad-output/active-context/active-context.md` · `_bmad-output/project-context.md` |
| Path/env/credential resolution | `src/config.py` (+ `.agents/rules/credential-resolution.md`) |
| Grounding sources (the ONLY permitted cites) | `docs/*_acs_*.pdf` · `pipeline/curriculum/1 ACS Curriculum Key.json` · FAA docs in `pipeline/library/` / the DB2 tag vocabulary |

### Stores + stack (do NOT change store topology without Daniel — §8)
| Layer | What |
|---|---|
| Data | Vertex **DB1** `aviation-curriculum-v2` · **DB2** `aviation-library-v2` · Firestore `aviationchat-database` (`rkp_manifests`, `quiz_banks`) · GCS staging `gs://aviationchat-curriculum-cms` · `gs://aviationchat-library` |
| Code | Python; gated CLI tools in `src/gcp/`; offline pytest gate `src/tests/` (33 tests) |
| AI | Gemini scripts for flashcard formatting + metadata extraction (models per the PRD) |

## 7. NAMING CONVENTIONS
Dated output `YYYY-MM-DD_<slug>.md`. Artifacts live **project-local** at
`_artifacts/<YYYY-MM-DD>_<slug>/` (stories → `_artifacts/epic_<E>/<story>/`). Lessons follow the ACS
code scheme (`PPL_PA_<Area>_<Task>_<nn>` — see the Curriculum Key). Drive masters are named
`Area N Task X PPL` (Doc + `.md` export side by side).

## 8. GATES (consult before acting)
- **GIT — desktop default** (canonical rule → `.agents/rules/git-policy.md`): agents **NEVER
  commit/push**; hand Daniel the copy-paste command in "Your Actions". Enforced by
  `.claude/hooks/require-push-approval.py`. **BRANCH MODEL: single `main` — BY DESIGN** (Daniel,
  2026-07-22): this is a workhorse repo, deployed nowhere; the protected surface is the DATA, not a
  branch. Do NOT create `main_debug` here and do NOT "fix" this repo to the two-branch house model.
- **DATA HARD STOPS** (full set → `.agents/rules/constitution.project.md`): dry-run before every
  `--execute` · never commit generated import manifests (`curriculum.jsonl`,
  `library_metadata.jsonl`) · `*.pdf` never enters git · an ingest is "done" only with
  `probe_bridge_hop` proof + tests green · citations are Daniel's gate · Drive is the authoring
  surface, the repo `.md` is machine truth.
- **`_my_resources/` (Daniel's personal area):** do NOT edit any file in it unless Daniel explicitly
  says so, and do NOT reference its contents unless he links the specific document.
- **Ask first:** deleting any curriculum asset · changing `src/utils/schema.py` (it mirrors the app's
  `backend/schemas/quiz.py` contract) · changing store topology or the DB2 tag vocabulary · bulk
  re-ingests (`--all` / FULL reconciliation).

## 9. PERSISTENCE
- "pick up" / "hand off" → the continuity file is **`_bmad-output/active-context/active-context.md`**
  (the BMAD convention, same as AGY — NOT `_artifacts/active-context.md`). Session artifacts (plans,
  walkthroughs) live **project-local** in `_artifacts/<YYYY-MM-DD>_<slug>/` + `epic_<E>/<story>/`, so
  this repo's history travels with the repo. (The old `_claude_artifacts/` + `_opencode_artifacts/`
  were consolidated into `_artifacts/` on 2026-07-22.)
- **"pick up" also surfaces open tasks:** after the `active-context.md` brief, read
  `_my_resources/open_tasks/todo_list.md` (+ any plan/PRP notes alongside it) and add a one-line
  "what's queued." **READ-ONLY** — Daniel's notes; never edit.

## Curriculum Story Lifecycle (BMAD-lite)
Epics = ACS Areas (+ one infra epic). Stories move `ready-for-dev → in-progress → review → done` on
the board in `_bmad-output/implementation-artifacts/sprint-status.yaml`. A curriculum story's
definition-of-done uses THIS repo's own gates — `pytest src/tests/` green · dry-run reviewed ·
`--execute` run · `probe_bridge_hop.py` ≥1 hit for every touched lesson · `generate_state_map.py
--live` counts matching intent — **not** the app's test tiers. No ATDD/TEA gate here.
