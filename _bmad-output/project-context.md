# Project Context — RAG_Pipeline_AC

## What this is
The **curriculum machine room** for AviationChat. It turns CFI-authored teaching content into the
machine artifacts the app consumes, and ingests them into the production stores. It is **upstream of
and separate from** the app repo (`../AGY_AVIATIONCHAT/`) — sync direction is pipeline → app; the
app only ever consumes what is produced here.

## The three stations
1. **Google Drive** (`AVIAIONCHAT/ACS Modules`) — authoring surface + heavy media (podcast audio,
   video, research). Deliberately outside cloud storage to keep costs down.
2. **This repo** — transform + validate + ingest. Masters land in
   `curriculum_components/curriculum_modules/`, get split into `pipeline/curriculum/elements/`, and
   drive the RKP manifests + quiz banks.
3. **The app** — reads DB1/DB2/Firestore at runtime. Never authors content.

## Stores (these ARE production — no staging tier)
| Store | Holds | Fed by |
|---|---|---|
| Vertex **DB1** `aviation-curriculum-v2` | 184 teaching micro-lessons | `src/gcp/reimport_db1_keys.py` |
| Vertex **DB2** `aviation-library-v2` | 27 FAA source documents | `src/gcp/import_db2_docs.py` |
| Firestore `aviationchat-database` | 48 RKP manifests · 48 quiz banks (384 questions) | `upload_manifests.py` · `ingest_quiz_banks.py` |

**The runtime contract:** the app filters DB2 with an exact `document_tags: ANY(manifest.bridge_keys)`
(`backend/tools/librarian.py::_search_db2_bridge_hop`). Bridge keys are the API between the teams.

## Coverage (as of the 2026-07-22 audit)
Live: Areas I, III, VI, VII, IX, XI = 48 lessons, 184 DB1 documents, 48/48 lessons returning ≥1 DB2
hit, structural element coverage 171/184, offline gate 33 tests green.
Not started: Areas **II, IV, V, VIII, XII** (X is N/A for single-engine PPL).

## How work is gated
- **Authoring:** `rkp-manifest-creation` / `quiz-bank-generation`, both bound by
  `faa-grounding-gate` (ACS + FAA sources only, never model memory). Daniel verifies citations.
- **Ingesting:** every `src/gcp/` tool is dry-run by default; `--execute` needs a reviewed dry-run
  in the same session (`.agents/rules/constitution.project.md`).
- **Proving:** `probe_bridge_hop.py` (live, read-only) + `pytest src/tests/` + `generate_state_map.py`.

## Known debt (see `_my_resources/open_tasks/todo_list.md`)
34 podcast scripts are orphaned (no ingest script) · 13 lessons cite sources not in DB2 · the two
data trees (`pipeline/` + `curriculum_components/`) await a Phase-2 merge under one `data/` root ·
the quiz corpus has a positional answer skew (67% "B") that needs a decision.

## Tech
Python. No `.venv` committed and none present — create one before running tests
(`requirements.txt` is unpinned by design; see its header). Path/credential resolution flows through
`src/config.py`; credentials live in gitignored `auth_keys/`.
