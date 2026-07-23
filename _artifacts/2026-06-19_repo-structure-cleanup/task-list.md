---
IsArtifact: true
ArtifactMetadata:
  title: Task list — Repo structure cleanup (Phase 1)
  type: task_list
  date: 2026-06-19
---

# Task List (final snapshot)

- [x] Rename `_01_My/` → `docs/` (git mv; 30 renames detected, history preserved)
- [x] Update all `_01_My/` references → `docs/` — 6 skill files + 2 core docs (+ frontmatter relative path; fixed double-stale `_artifacts` ref). App-repo cross-links in `prd.md` left intentionally.
- [x] Add root `README.md` (what-it-is, structure map, quickstart, ops table, docs index, governance)
- [x] Add `requirements.txt` (direct deps, intentionally unpinned — pin from env)
- [x] Add `.env.example` (six `auth_keys/.env` vars, placeholders)
- [x] Gitignore `.pytest_cache/`
- [x] Repoint `generate_repo_map.py` output → `docs/docs_prds/` + extend `IGNORE_DIRS`; regenerate
- [x] Verify: 33 pytest passed, `_01_My` sweep clean (only app-repo links), files exist, 30 git renames
- [x] Write `walkthrough.md` + `task-list.md`

## Deferred (not this phase)
- [ ] Pin `requirements.txt` versions — needs your working venv (`pip freeze`); flagged in Your Actions
- [ ] Phase 2: consolidate data under `data/`, rename `src/pipeline/` → `src/stages/`, hoist `tests/` — separately gated
- [ ] Fix hardcoded cred paths in `src/gcp/create_v2_stores.py` + `upload_and_import_v2.py` — flagged, own gate
- [ ] `specialist_curriculum/` stale refs in skill files — fold into Phase 2 data rename
