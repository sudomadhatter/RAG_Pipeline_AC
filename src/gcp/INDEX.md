# src/gcp/ — INDEX  (the gated ingestion tools — the ONLY live-write entry points)

Every tool here is **dry-run by default**; `--execute` performs the live write. The constitution
(`.agents/rules/constitution.project.md`) requires a reviewed dry-run in the same session before any
`--execute`, and proof (`probe_bridge_hop` + tests) before calling an ingest done.

| Tool | What it writes | Target |
|---|---|---|
| `reimport_db1_keys.py` | repairs/imports curriculum keys in place (`update_document`) | **DB1** `aviation-curriculum-v2` |
| `import_db2_docs.py` | uploads FAA PDFs + rich `document_tags` (`create_document`) | **DB2** `aviation-library-v2` |
| `upload_manifests.py` | RKP manifests | Firestore `rkp_manifests/{lesson_id}` |
| `ingest_quiz_banks.py` | quiz banks | Firestore `quiz_banks/{lesson}/questions/{q}` |
| `probe_bridge_hop.py` | **read-only** — proves the live DB1→DB2 bridge hop | (verification) |

Writes deliberately bypass Vertex's `ImportDocuments` queue (it jams at `done=False` on a failed op
and ignores cancel) by using per-document `update_document` / `create_document`.
