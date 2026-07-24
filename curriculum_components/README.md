# curriculum_components/ — the authored-asset store

This folder holds the **human/CFI-authored source assets** — the inputs everything else derives
from. It is the counterpart to [`pipeline/curriculum/`](../pipeline/curriculum/README.md) (the
*processed* DB1 source store): authored content lives here, derived content lives there.

```
curriculum_components/
├── curriculum_modules/   # 13 CFI master modules (.md) — "Area N Task X PPL.md"
├── rkp_manifests/        # 48 RKP manifest JSON      → Firestore  rkp_manifests
├── quiz_banks/           # 48 quiz bank JSON         → Firestore  quiz_banks
├── faadocs/             # 12 FAA source PDFs        → DB2 (aviation-library-v2)
├── lesson_podcasts/      # 34 authored podcast .md   → (not ingested by any script — see below)
├── scripts/              # generate_knowledge_formatted.py (RKP knowledge_formatted helper)
├── quiz_schema.md        # the quiz-bank JSON schema reference
└── README.md             # this file
```

## What each piece is, and where it goes

- **`curriculum_modules/`** — the CFI's master teaching modules, one markdown file per ACS Task.
  These are split into the micro-lessons in `pipeline/curriculum/elements/` (the DB1 content). The
  `scripts/fallback_generator*.py` tools parse a module into split lessons + sidecars.

- **`rkp_manifests/`** — Required Knowledge Point manifests (`PPL_PA_*_rkp.json`), one per lesson.
  `src/gcp/upload_manifests.py` ingests them into Firestore `rkp_manifests` (doc id = `lesson_id`).
  Their `bridge_keys` are also read by `src/gcp/import_db2_docs.py` (to tag DB2) and
  `src/gcp/probe_bridge_hop.py` (to verify the bridge). **This repo's git copy is the source of
  truth** — Firestore is the deployment target, not the source.

- **`quiz_banks/`** — quiz bank JSON (`PPL_PA_*_quiz.json`), one per lesson, 8 questions each.
  `src/gcp/ingest_quiz_banks.py` explodes them into Firestore `quiz_banks/{lesson_id}/questions/{id}`.
  See [`quiz_schema.md`](quiz_schema.md) for the schema.

- **`faadocs/`** — the authoritative FAA source PDFs (ACs, handbooks, the ACS). `src/gcp/import_db2_docs.py`
  uploads them to the library bucket and INCREMENTAL-imports them into DB2. The `_db2_import.jsonl`
  here is a **generated** import manifest, not a source PDF.

- **`lesson_podcasts/`** — authored podcast scripts. **⚠️ Currently orphaned: no script ingests
  these.** They are authored content the app may consume by another path, or pending an ingestion
  step. `generate_state_map.py` flags this automatically — don't assume they're deployed.

## Paths are centralized

Every path above is a named constant in [`src/config.py`](../src/config.py) (`MODULES_DIR`,
`RKP_MANIFESTS_DIR`, `QUIZ_BANKS_DIR`, `FAA_DOCS_DIR`, `PODCASTS_DIR`) — the same way
`pipeline/curriculum/` is wired. Change a folder name in one place, not in five scripts.

## How to check what's actually deployed

```bash
python scripts/generate_state_map.py --live
```

This inventories this folder, cross-references RKP↔quiz pairing, flags the orphaned podcasts, and
diffs the local files against Firestore/DB1/DB2 — writing [docs/docs_prds/STATE.md](../docs/docs_prds/STATE.md).
It replaces hand-counting whether the repo and the live databases agree.
