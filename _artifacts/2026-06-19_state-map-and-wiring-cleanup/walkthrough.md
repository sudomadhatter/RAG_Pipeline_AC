---
IsArtifact: true
ArtifactMetadata:
  title: State Map + Two-Folder Wiring Cleanup — Walkthrough
  type: walkthrough
  date: 2026-06-19
---

# Walkthrough — State Map + Two-Folder Wiring Cleanup

## What this session did

Audited how `curriculum_components/` (authored assets) and `pipeline/curriculum/` (the DB1 source
store) feed the three databases, found the flow correct but the *connective tissue* stale, and fixed
it three ways: a generated state map (Daniel's idea), a truth-up of the stale docs, and symmetric
path wiring. **No data moved, no docs deleted, repo stays canonical** — per Daniel's three scoping
decisions during planning.

## How it went, step by step

1. **Baseline first.** Ran the offline suite to capture the "before" — `33 passed`.
2. **Config constants (Part C).** Added a single authored-asset block to `src/config.py`
   (`COMPONENTS_ROOT`, `MODULES_DIR`, `RKP_MANIFESTS_DIR`, `QUIZ_BANKS_DIR`, `FAA_DOCS_DIR`,
   `PODCASTS_DIR`) so `curriculum_components/` is wired the same way `pipeline/curriculum/` already is.
3. **Rewired the four GCP scripts** (`upload_manifests`, `ingest_quiz_banks`, `probe_bridge_hop`,
   `import_db2_docs`) from copy-pasted `config.PROJECT_ROOT / "curriculum_components" / ...` strings
   to the constants. **Fixed the two CWD-relative paths** in `scripts/fallback_generator.py` and
   `fallback_generator2.py` (added the missing `import config` to the first). These are byte-identical
   path swaps — referential only.
4. **Proved zero behavior change** immediately: `33 passed`, all six constants resolve to existing
   dirs, and all four edited GCP modules import cleanly (which confirms the constants they reference
   exist). This is why the rewire came before the new feature — a bad swap surfaces in one command.
5. **Built `scripts/generate_state_map.py`** — the centerpiece. Offline: inventories both folders and
   cross-references RKP↔quiz pairing, elements↔manifest count, and the podcast orphan. `--live`:
   reuses the exact `firebase_admin` pattern from `upload_manifests.py` and the `discoveryengine`
   client from `reimport_db1_keys.py` to count Firestore/DB1/DB2 docs and **diff local lesson-ids
   against Firestore** (the repo == Firestore auto-verify). Every live probe is wrapped — missing
   creds degrade to "skipped", the offline map still writes.
6. **Generated `_docs/docs_prds/STATE.md`** and added a pointer banner to `asset_registry.md` (kept,
   not deleted) directing readers to the generated map for live counts.
7. **Rewrote the stale `README.md`** and **added the missing `curriculum_components/README.md`**.

## What fought back

- **My own wrong claim, caught before it shipped.** I was about to tell Daniel that deleting the
  local RKP/quiz files would break the offline test gate. I verified instead of asserting — the
  offline tests (`test_schema_keys.py`, `test_bridge_key_offline_gate.py`) only touch pure functions
  and `curriculum.jsonl`, *not* `curriculum_components/`. Corrected the record before recommending.
- **Scope reshaped three times mid-planning.** Daniel pushed on "delete the docs / use Firebase as
  the store." Rather than comply blindly, surfaced the real tradeoff (Firestore has no version
  history; the repo-is-canonical model would invert; quiz subcollections round-trip lossily). Landed
  on: keep the repo canonical, make `--live` auto-prove repo == Firestore. The plan absorbed each
  decision before any code was written.
- **A stale `unused-import` hint** appeared on `fallback_generator.py` — it was captured *between* my
  two edits (after adding `import config`, before using it). The final `config.MODULES_DIR` reference
  clears it; `py_compile` confirms.

## File-by-file

**New:**
- `scripts/generate_state_map.py` — the offline+live state map / drift checker.
- `curriculum_components/README.md` — documents each subfolder, its ingestion script, destination, and the podcast orphan.
- `_docs/docs_prds/STATE.md` — generated output (committed like `repo-map.md`).

**Modified:**
- `src/config.py` — added the authored-asset path constants.
- `src/gcp/upload_manifests.py` · `ingest_quiz_banks.py` · `probe_bridge_hop.py` · `import_db2_docs.py` — use the constants.
- `scripts/fallback_generator.py` · `fallback_generator2.py` — replaced CWD-relative module path with `config.MODULES_DIR`.
- `README.md` — removed deleted `src/main.py` / `src/pipeline/` refs, fixed all `docs/` → `_docs/` links, updated the Phase-2 note, added the state map + STATE.md.
- `_docs/docs_prds/asset_registry.md` — added a banner pointing to the generated STATE.md.

## Test output (actual)

Baseline (before any change):
```
$ python -m pytest src/tests/ -q
.................................                                         [100%]
33 passed in 0.20s
```

After rewiring + new script:
```
$ python -m pytest src/tests/ -q
.................................                                         [100%]
33 passed in 0.35s

$ python -m py_compile src/config.py src/gcp/*.py scripts/fallback_generator*.py scripts/generate_state_map.py
all compiled OK
```

State map (offline run):
```
$ python scripts/generate_state_map.py
Wrote .../_docs/docs_prds/STATE.md
  Inventory: {'curriculum_modules (.md)': 13, 'rkp_manifests (*_rkp.json)': 48,
  'quiz_banks (*_quiz.json)': 48, 'faa_docs (PDFs)': 12, 'lesson_podcasts (.md)': 34,
  'curriculum/elements (.md)': 184, 'curriculum/sidecars (.json)': 12, 'curriculum.jsonl (entries)': 184}
```
Generated STATE.md correctly flagged: ✅ RKP↔quiz (48/48 paired), ✅ elements↔jsonl (184/184),
⚠️ 34 podcasts not ingested.

## Deviations from the plan

None of substance. The three plan "open questions" were resolved with the stated defaults:
STATE.md lives in `_docs/docs_prds/` (next to repo-map.md), constants use bare names
(`RKP_MANIFESTS_DIR`), and STATE.md is committed. The `--live` path was not exercised this session
(needs your creds) — it is wrapped to degrade gracefully and is yours to run.

## Your Actions

**1. Review** the generated [STATE.md](../../_docs/docs_prds/STATE.md) and the rewritten
[README.md](../../README.md).

**2. Run the live map** (optional, needs `auth_keys/`) to populate the deployed-database section and
the repo-vs-Firestore drift check:
```bash
python scripts/generate_state_map.py --live
```

**3. Commit — scoped to THIS session's files only.** ⚠️ The working tree also contains substantial
*uncommitted prior work* (the Phase 1 `docs/`→`_docs/` rename, and the pipeline-curriculum cleanup
that deleted `src/main.py`, `src/pipeline/*`, `src/utils/lifecycle.py`, and modified
`reimport_db1_keys.py`, `create_v2_stores.py`, `audit_sidecars.py`, `generate_repo_map.py`). Decide
how to commit those separately. To commit only this session:

```bash
git add \
  src/config.py \
  src/gcp/upload_manifests.py src/gcp/ingest_quiz_banks.py \
  src/gcp/probe_bridge_hop.py src/gcp/import_db2_docs.py \
  scripts/fallback_generator.py scripts/fallback_generator2.py \
  scripts/generate_state_map.py \
  curriculum_components/README.md \
  README.md \
  _docs/docs_prds/STATE.md _docs/docs_prds/asset_registry.md

git commit -m "Add pipeline state map + symmetric curriculum_components wiring; truth-up README

- New scripts/generate_state_map.py: offline inventory + RKP/quiz/podcast drift checks;
  --live diffs local files against Firestore/DB1/DB2 (repo == Firestore auto-verify)
- config.py: centralize curriculum_components paths (RKP_MANIFESTS_DIR, QUIZ_BANKS_DIR,
  FAA_DOCS_DIR, MODULES_DIR, PODCASTS_DIR); 4 gcp scripts + 2 fallback generators use them
- Fix CWD-relative paths in fallback_generator{,2}.py
- README: drop deleted src/main.py + src/pipeline refs, fix docs/ -> _docs/ links
- Add curriculum_components/README.md; banner asset_registry.md -> STATE.md
- Offline suite green throughout (33 passed)"
```

**4. Note:** this repo has no `active-context.md` (the CLAUDE.md session ritual references one, plus
`docs/reference/`, that don't exist here — template leftovers worth reconciling later).
