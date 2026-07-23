# pipeline/library/ — INDEX  (FAA source PDF lifecycle — DATA, not code)

The FAA document library staged for **DB2** (`aviation-library-v2`). PDFs are **gitignored** —
this tree is local-disk only (~365 MB); durable copies live in Drive / faa.gov, the live store is DB2.

| Stage | What |
|---|---|
| `new/` | downloaded, not yet uploaded (CFRs, ACs, handbooks — incl. the 4-part AFH split, each under Vertex's 200 MB/doc cap) |
| `active/` | live in DB2 (`regulations/` · `handbooks/` · `advisory_circulars/`) |
| `superseded/` | replaced editions |
| `manifest.json` | library manifest |
| `library_metadata.jsonl` | **GENERATED** import manifest — **NEVER commit** |

Upload tool (gated): `python src/gcp/import_db2_docs.py [--execute]` (rich-tags each doc so
edition-variant bridge keys still match).
