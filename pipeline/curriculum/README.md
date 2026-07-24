# pipeline/curriculum/ — the DB1 source store

This folder holds the **source content for DB1** (`aviation-curriculum-v2`, the Vertex AI Search
teaching store) plus the generated import manifest. Every `.md` here corresponds 1:1 to a live DB1
document (184 of them, verified against the live store).

```
pipeline/curriculum/
├── elements/          # 184 split-lesson .md — the DB1 content (one .md per live doc)
├── sidecars/          # 12 Area IX *.json — locally-authored metadata sidecars
├── new/               # authoring inbox: new lessons land here, then get promoted to elements/
├── curriculum.jsonl   # GENERATED import manifest — do not hand-edit (gitignored)
└── README.md          # this file
```

## What each piece is

- **`elements/`** — the split "micro-lesson" markdown, one file per ACS element
  (`lesson_pa_{area}_{task}_{element}.md`). These are uploaded to
  `gs://aviationchat-curriculum-cms/v2/elements/` and indexed into DB1. This is the source of truth
  for lesson *content*.

- **`sidecars/`** — authored `.json` metadata (reg_keys / doc_keys) for the **Area IX** lessons only.
  The other 172 lessons carry their metadata in the live store; Area IX needed its keys repaired from
  these local sidecars (see `src/gcp/reimport_db1_keys.py`, which reads `sidecars/{doc_id}.json`).

- **`new/`** — the authoring inbox. `src/utils/generate_metadata.py` and
  `scripts/fallback_generator2.py` write freshly-extracted lesson sidecars here. Promote finished
  lessons into `elements/` (content) + `sidecars/` (metadata). Normally empty.

- **`curriculum.jsonl`** — the DB1 import manifest, **regenerated** by `reimport_db1_keys.py` (it pulls
  the live store, normalizes the keys, fills Area IX from `sidecars/`, and writes the 184-entry JSONL).
  Never hand-edit it; it's gitignored because a partial manifest + a FULL reconciliation could wipe DB1.

## How DB1 actually gets built

The live stores were **not** built by a generic `new → active → superseded` pipeline (that scaffolding
was removed 2026-06-19 — it never matched reality). The real path is:

1. `python src/gcp/reimport_db1_keys.py` (dry run) → rebuilds `curriculum.jsonl` + prints a report.
2. `python src/gcp/reimport_db1_keys.py --execute` → uploads + INCREMENTAL-imports into DB1.
3. `python src/gcp/probe_bridge_hop.py` → live DB1→DB2 bridge verification.

See `docs/docs_prds/asset_registry.md` and `docs/instruction_docs/curriculum_lifecycle.md` for the
full picture.
