---
IsArtifact: true
ArtifactMetadata:
  title: "pipeline/curriculum cleanup — task list"
  type: task_list
  date: 2026-06-19
---

# pipeline/curriculum cleanup — final task list

- [x] Research & verify ground-truth state (local breakdown + 184-entry manifest reconciliation; 0 orphans)
- [x] Write `implementation_plan.md`; got Daniel's **"approved"** (target: Collapse to reality)
- [x] **Phase 1** — Reorg folder: `active→elements` (172), Area IX `.md→elements` (12) + `.json→sidecars` (12); deleted 13 dup master modules, empty `_v2_split/`, stray `library_v2_import.jsonl`
- [x] **Phase 2** — Repoint consumers: `config.py` (ELEMENTS/SIDECARS/JSONL; dropped fictional paths), `reimport_db1_keys.py`, `import_db2_docs.py`, `audit_sidecars.py`
- [x] **Phase 3** — Retire dead scaffolding: deleted `src/main.py`, `src/pipeline/*`, `src/utils/lifecycle.py`, `src/gcp/upload_and_import_v2.py`; zero dangling refs confirmed
- [x] **Phase 4** — Docs: fixed `asset_registry.md` (`_v2_split`→`elements`, removed 4 dead-file rows), regenerated `repo-map.md`, added folder READMEs
- [x] **Phase 5** — Verify: `pytest` 33 passed; `reimport_db1_keys.py` dry-run rebuilt 184 entries from `sidecars/` (171 covered + 13 ref-only); `audit_sidecars.py` scans new path

All planned work completed. Commit left for Daniel (see walkthrough "Your Actions").
