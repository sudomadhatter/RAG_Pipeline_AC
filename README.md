# AviationChat — Ingestion & Curriculum Pipeline

The **canonical** authoring + ingestion pipeline for AviationChat's Private Pilot (PPL) curriculum.
This repo turns a CFI's teaching content into the machine artifacts the app consumes — RKP manifests,
quiz banks, flashcards, and the bridge keys that link a lesson to its authoritative FAA source — and
ingests them into the production data stores.

> This repo is **separate from, and upstream of, the app repo** (`AGY_AVIATIONCHAT`). Sync direction
> is **pipeline → app**. The app only ever *consumes* what is produced here.

For the full mental model — how a lesson is made, ingested, and consumed end to end — read
[docs/docs_prds/Master_Curriculum_Pipeline.md](docs/docs_prds/Master_Curriculum_Pipeline.md) (the
PRD). For *current* counts and live deployment state, run the state map (below) and read the
generated [docs/docs_prds/STATE.md](docs/docs_prds/STATE.md).

---

## Repository structure

```text
.
├── src/                      # Python application code
│   ├── config.py             # path + env resolution (single source of truth; no hardcoded paths)
│   ├── gcp/                  #  ingestion tools — GCS / Vertex AI Search / Firestore (the real entry points)
│   ├── utils/                #  schema, metadata extraction, db2 tags
│   └── tests/                #  offline gate (pytest)
│
├── pipeline/curriculum/      # DB1 SOURCE STORE (read by src/config.py)
│   ├── elements/             #  184 split micro-lesson .md (one per live DB1 doc)
│   ├── sidecars/             #  12 Area IX metadata .json
│   ├── new/                  #  authoring inbox
│   └── curriculum.jsonl      #  GENERATED DB1 import manifest
│
├── curriculum_components/    # authored ASSETS (read by src/gcp/*) — see curriculum_components/README.md
│                             #  master modules · RKP manifests · quiz banks · FAA PDFs · podcasts
│
├── scripts/                  # standalone utilities (state map, repo map, vocab derivation, fallbacks)
├── docs/                     # ALL documentation, one folder (no _docs/ — merged 2026-07-23)
│   ├── SOP_curriculum_operations.md  # ** the two-team operating guide **
│   ├── docs_prds/            #  reference: PRD, asset_registry, STATE.md (generated), repo-map (generated)
│   ├── instruction_docs/     #  the 6 authoring guides (rkp, quiz, bridge_key, flashcard, lifecycle, recovery)
│   ├── project_context_prps/ #  broader product / architecture context (what the downstream app is)
│   ├── *.pdf                 #  the 3 ACS books (private · instrument · commercial) — grounding sources
│   └── repo-map.md
│
├── auth_keys/                # credentials (GITIGNORED): .env + service-account.json
├── _artifacts/               # session artifacts (per-session folders + INDEX.md)
├── _bmad-output/             # BMAD-lite board state + active-context
├── _my_resources/            # Daniel's PROTECTED personal area — agents keep out
│
├── README.md  ·  requirements.txt  ·  .env.example  ·  .gitignore
└── CLAUDE.md  ·  AGENTS.md  ·  .gemini/GEMINI.md   # agent-tool governance (Claude / opencode / Gemini)
```

> **Heads-up for new contributors.** Curriculum data lives in *two* trees that a planned **Phase 2**
> will merge under one `data/` root: `pipeline/curriculum/` (the DB1 source store, read by
> `config.py`) and `curriculum_components/` (authored assets, read by `src/gcp/*`). Until then, run
> `python scripts/generate_state_map.py` to see exactly what is where. Note **`pipeline/` is *data*,
> not code** — the old `src/pipeline/` 6-phase lifecycle was removed as never-used; the real entry
> points are the gated tools in `src/gcp/`.

---

## The two data folders (how the databases get fed)

| Authored source | Lives in | Ingestion script | Lands in |
|---|---|---|---|
| Master modules (`.md`) | `curriculum_components/curriculum_modules/` | split → `curriculum/elements/` | (feeds DB1) |
| Split lessons (`.md`) | `pipeline/curriculum/elements/` | `reimport_db1_keys.py` | **DB1** (`aviation-curriculum-v2`) |
| Area IX metadata (`.json`) | `pipeline/curriculum/sidecars/` | `reimport_db1_keys.py` | **DB1** (bridge keys) |
| FAA PDFs | `curriculum_components/faadocs/` | `import_db2_docs.py` | **DB2** (`aviation-library-v2`) |
| RKP manifests (`.json`) | `curriculum_components/rkp_manifests/` | `upload_manifests.py` | **Firestore** `rkp_manifests` |
| Quiz banks (`.json`) | `curriculum_components/quiz_banks/` | `ingest_quiz_banks.py` | **Firestore** `quiz_banks` |

Verify the whole thing end to end with `probe_bridge_hop.py` (read-only DB1→DB2 bridge probe), and
get a live inventory + repo-vs-Firestore drift check from `generate_state_map.py --live`.

---

## Quickstart

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/Scripts/activate          # Windows (Git Bash);  .venv/bin/activate on macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up credentials (see .env.example for every variable)
cp .env.example auth_keys/.env         # then fill in real values
#   ...and place your service-account key at auth_keys/service-account.json

# 4. Run the offline test suite (no cloud access needed)
python -m pytest src/tests/ -q

# 5. See the current state of the pipeline (offline; add --live for database counts)
python scripts/generate_state_map.py
```

All path/credential resolution flows through [src/config.py](src/config.py) — scripts work from any
working directory and never hardcode machine paths.

### Common operations

Every live-write tool is **gated**: dry-run by default, `--execute` to write.

| Task | Command |
|---|---|
| Offline gate (schema + bridge-key tests) | `python -m pytest src/tests/ -q` |
| Generate the state map (live inventory + drift) | `python scripts/generate_state_map.py [--live]` |
| Repair DB1 keys (Vertex curriculum store) | `python src/gcp/reimport_db1_keys.py [--execute]` |
| Upload FAA PDFs → DB2 + tag | `python src/gcp/import_db2_docs.py [--execute]` |
| Upload RKP manifests → Firestore | `python src/gcp/upload_manifests.py [--execute]` |
| Upload quiz banks → Firestore | `python src/gcp/ingest_quiz_banks.py [--execute]` |
| Prove the DB1→DB2 bridge (read-only) | `python src/gcp/probe_bridge_hop.py [--limit N]` |
| Re-derive DB2 vocabulary from live store | `python scripts/derive_db2_vocabulary.py` |
| Regenerate this repo map | `python scripts/generate_repo_map.py` |

---

## Documentation index

| Doc | What it is |
|---|---|
| [docs/SOP_curriculum_operations.md](docs/SOP_curriculum_operations.md) | **The two-team SOP** — stations & ownership, Drive intake, per-lesson lifecycle, live-store discipline |
| [docs/docs_prds/Master_Curriculum_Pipeline.md](docs/docs_prds/Master_Curriculum_Pipeline.md) | The PRD — full end-to-end walkthrough with diagrams |
| [docs/docs_prds/STATE.md](docs/docs_prds/STATE.md) | **Generated** live inventory + repo-vs-Firestore drift (run `generate_state_map.py`) |
| [docs/docs_prds/asset_registry.md](docs/docs_prds/asset_registry.md) | Narrative inventory of every asset + how it flows |
| [docs/docs_prds/repo-map.md](docs/docs_prds/repo-map.md) | Auto-generated AST map of the codebase |
| [docs/instruction_docs/](docs/instruction_docs/) | The 6 authoring guides (RKP, quiz, bridge key, flashcard, lifecycle, recovery) |
| [docs/project_context_prps/](docs/project_context_prps/) | Broader product / architecture context |

---

## Agent-tool governance

**[AGENTS.md](AGENTS.md) is the single source of truth** — the workspace map every AI tool reads.
[CLAUDE.md](CLAUDE.md) and [GEMINI.md](GEMINI.md) are one-line pointers to it (one front door per
LLM, one brain). Codex reads `AGENTS.md` natively.

- **Rules** → `.agents/rules/` — the shared house set plus this repo's own
  `constitution.project.md` (the data-side hard stops: dry-run before `--execute`, never commit
  generated import manifests, no PDFs in git, no invented FAA facts).
- **Skills** → `.agents/skills/` (mirrored to `.claude/skills/`) — deliberately **lean**: curriculum
  authoring (`rkp-manifest-creation`, `quiz-bank-generation`, `bridge-key-verification`,
  `faa-grounding-gate`) plus a few hygiene skills. The full house library and the whole `sudo-*`
  dev flow live at the command center and are driven from there.
- **Artifacts** → `_artifacts/` (session plans + walkthroughs; the retired `_claude_artifacts/` and
  `_opencode_artifacts/` were consolidated here on 2026-07-22).
- **Board / continuity** → `_bmad-output/` (BMAD-lite: state files only, no `_bmad/` module).
