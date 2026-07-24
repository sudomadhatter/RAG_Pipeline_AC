# faadocs/ — INDEX

Staging area for FAA PDFs bound for **DB2** (`aviation-library-v2`) via
`src/gcp/import_db2_docs.py`. PDFs are **gitignored** (`*.pdf`) — only `_db2_import.jsonl`
(the import manifest) is tracked. The actual source PDFs currently sit in
`pipeline/library/new/` (~365 MB local-only); GCS `gs://aviationchat-library/` is the upload
target, the live store is DB2.
