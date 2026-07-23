---
IsArtifact: true
ArtifactMetadata:
  title: State Map + Two-Folder Wiring Cleanup — Task List
  type: task_list
  date: 2026-06-19
---

# Task List (final snapshot)

- [x] Get `implementation_plan.md` approved by Daniel (gate) — approved.
- [x] Add authored-asset path constants to `src/config.py` (`COMPONENTS_ROOT`, `MODULES_DIR`, `RKP_MANIFESTS_DIR`, `QUIZ_BANKS_DIR`, `FAA_DOCS_DIR`, `PODCASTS_DIR`).
- [x] Wire the 4 GCP scripts to the constants + fix the 2 `fallback_generator` CWD paths.
- [x] Verify `pytest src/tests/` stays green after rewiring — **33 passed**.
- [x] Build `scripts/generate_state_map.py` (offline inventory + drift flags; `--live` adds Firestore/DB1/DB2 counts + repo-vs-Firestore diff).
- [x] Generate `_docs/docs_prds/STATE.md` (first run) + add pointer banner to `asset_registry.md`.
- [x] Rewrite stale root `README.md` (removed `src/main.py` + `src/pipeline/`, fixed `docs/` → `_docs/` links, added STATE.md + the data-flow table).
- [x] Add `curriculum_components/README.md` (missing sibling; documents the podcast orphan).
- [x] Final verification — `pytest` 33 passed, `py_compile` all 8 touched files OK, state map runs clean.
- [x] Write `walkthrough.md` + `task-list.md`.

**Deferred (out of scope by Daniel's decisions):**
- [ ] Phase 2 `data/` consolidation (merge both trees) — still pending, needs its own plan.
- [ ] Resolve the 34 orphaned podcasts (wire ingestion or relocate) — documented + auto-flagged, not fixed.
- [ ] Reconcile the CLAUDE.md session ritual's missing `active-context.md` / `docs/reference/` references.
