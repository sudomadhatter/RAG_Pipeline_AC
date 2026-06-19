---
IsArtifact: true
ArtifactMetadata:
  title: "pipeline/curriculum cleanup — collapse to reality"
  type: implementation_plan
  date: 2026-06-19
---

# pipeline/curriculum cleanup — collapse to reality

## Goal

`pipeline/curriculum/` currently mixes three things — real DB1 source content, an aspirational
`new/active/superseded` + `_v2_split` lifecycle that was never actually used, and duplicate/misfiled
cruft. New devs can't tell what's canonical, and the docs point at folders that are empty or wrong.

**Done = the folder reflects exactly what's true and deployed**, code path-references match, the
fictional scaffolding is gone, and the docs describe the real structure.

## Verified ground truth (read-only, done)

- `curriculum.jsonl` = **184 entries** = the built DB1 import manifest. Already gitignored as a
  generated artifact (`.gitignore:43`). Matches live DB1 (184 docs, per `asset_registry.md`, verified today).
- `active/` (186 files) = **172 split lessons** (`lesson_pa_*.md`) + **13 master-module copies**
  (byte-identical dupes of `curriculum_components/curriculum_modules/`) + **1 stray** `library_v2_import.jsonl`.
- `new/` (24 files) = **12 Area IX** lessons (`.md` + `.json` sidecar pairs) — already live, never cleared.
- `_v2_split/` = **empty** (docs claim it holds the 184 micro-lessons).
- Reconciliation: 172 (active) + 12 (new) = **184 = every manifest entry, 0 orphans, 0 missing.**
- `reimport_db1_keys.py` reads the Area IX **`.json` sidecars by doc-id** (`AREA_IX_SIDECARS/{id}.json`);
  it does NOT read the Area IX `.md`. The 172 non-Area-IX lessons have **no local `.json`** — their
  metadata lives only in the live store + the built `curriculum.jsonl`.
- `new/` + `active/` are **real** authoring paths (`generate_metadata.py`, `fallback_generator2.py`,
  `audit_sidecars.py` use `config.CURRICULUM_NEW`/`CURRICULUM_ACTIVE`).
- **Fictional / dead:** `superseded/`, `manifest.json`, the entire `pipeline/library/` tree, the 6-phase
  `src/pipeline/{base,curriculum,library}.py` + `src/main.py` + `src/utils/lifecycle.py` (a closed island
  imported only by each other), and `src/gcp/upload_and_import_v2.py` (hardcodes `c:\AGY-Projects\...`
  machine paths — can't run in this repo). The live stores were built by the `src/gcp/*` scripts, not this pipeline.

## Target structure

```
pipeline/curriculum/
├── elements/          # 184 split-lesson .md — the DB1 source content
│                      #   (172 from active/ + 12 Area IX .md from new/)
├── sidecars/          # 12 Area IX *.json — the only locally-authored metadata sidecars
├── new/               # authoring inbox (empty now; generate_metadata.py writes here) + README
├── curriculum.jsonl   # GENERATED DB1 import manifest (path unchanged, stays gitignored)
└── README.md          # explains: elements = content, sidecars = metadata, jsonl = generated, new = inbox
```

Gone: `active/` (renamed → `elements/`), `_v2_split/` (deleted), 13 duplicate master modules (deleted),
`library_v2_import.jsonl` (deleted after confirming unreferenced).

## Execution plan

### Phase 1 — Reorganize the data folder (pure file moves; no live impact)
1. `git mv pipeline/curriculum/active → pipeline/curriculum/elements` (carries the 172 `lesson_*.md`).
2. Delete the 13 `Area * PPL.md` master-module copies from `elements/` (canonical home is
   `curriculum_components/curriculum_modules/` — verified byte-identical).
3. Move the 12 Area IX `.md` from `new/` → `elements/` (completes the 184-element set).
4. Move the 12 Area IX `.json` from `new/` → new `sidecars/`.
5. Delete the empty `_v2_split/`.
6. Delete `elements/library_v2_import.jsonl` (stray DB2 artifact, stale, unreferenced — re-grep to confirm
   zero `.py`/config references before deleting).
7. `new/` is now empty — keep it as the authoring inbox; add a one-line `.gitkeep`/README note.

### Phase 2 — Repoint the real consumers
- `src/config.py`: rename `CURRICULUM_ACTIVE` → `CURRICULUM_ELEMENTS` (= `.../elements`); add
  `CURRICULUM_SIDECARS` (= `.../sidecars`); keep `CURRICULUM_NEW`; **remove** `CURRICULUM_SUPERSEDED`,
  `CURRICULUM_MANIFEST`, and the filesystem `LIBRARY_*` lifecycle paths
  (`LIBRARY_ROOT/NEW/ACTIVE/SUPERSEDED/MANIFEST`). Keep the GCP target constants
  (`LIBRARY_BUCKET`/`_DATA_STORE_ID`/`_LOCATION`) — verify each is still referenced before touching.
- `src/gcp/reimport_db1_keys.py:29`: `AREA_IX_SIDECARS` → `config.CURRICULUM_SIDECARS`. (`OUT_JSONL` unchanged.)
- `scripts/audit_sidecars.py:16`: `[CURRICULUM_NEW, CURRICULUM_ACTIVE]` → `[CURRICULUM_NEW, CURRICULUM_SIDECARS]`.
- No change needed: `import_db2_docs.py` + `test_bridge_key_offline_gate.py` (both read `curriculum.jsonl`,
  whose path is unchanged); `generate_metadata.py` + `fallback_generator2.py` (write to `CURRICULUM_NEW`, unchanged).

### Phase 3 — Retire the dead scaffolding (RECOMMENDED, but separable — see note)
Delete the closed dead island (git history preserves it):
- `src/main.py`, `src/pipeline/base.py`, `src/pipeline/curriculum.py`, `src/pipeline/library.py`
  (+ any `src/pipeline/__init__.py`)
- `src/utils/lifecycle.py` (used only by the above)
- `src/gcp/upload_and_import_v2.py` (broken hardcoded paths)

> **Opt-out:** if you'd rather keep the pipeline package as an intended-future skeleton, we stop after
> Phase 2 and instead just neutralize the fictional `config` paths + leave the code. I recommend deletion —
> it's dead relative to how DB1/DB2 were actually built, and it's the main source of new-dev confusion.

### Phase 4 — Update docs to match reality
- `_docs/docs_prds/asset_registry.md`: fix the 3 `_v2_split/` references (lines ~34, ~76, ~222) →
  `pipeline/curriculum/elements/`; note the count is populated, not aspirational. Drop the duplicate-master-module
  implication. If Phase 3 ran, fix the "Run full curriculum pipeline `python -m src.main`" rows.
- Add `pipeline/curriculum/README.md` (the front-door explainer for the folder).
- Regenerate `_docs/docs_prds/repo-map.md` via `python scripts/generate_repo_map.py`.
- Scan `Master_Curriculum_Pipeline.md` for stale refs (grep showed none, but confirm).

### Phase 5 — Verify (paste real output in walkthrough)
- `python -m pytest src/tests/ -q` → expect the offline gate + schema tests to pass (curriculum.jsonl path unchanged).
- `python src/gcp/reimport_db1_keys.py` **(dry run, no `--execute`)** → reads `sidecars/` for Area IX,
  rebuilds `curriculum.jsonl`, prints **"Built 184 entries (target 184)."** This is a live **read-only**
  DB1 probe — it doubles as the on-the-wire "what's actually live" confirmation, and mutates nothing.
- `python scripts/audit_sidecars.py` → audits `new/` (empty) + `sidecars/` (12 Area IX) clean.
- (If creds/network unavailable, the offline pytest + the 184-entry manifest reconciliation already prove
  correctness; the live read can be run by Daniel.)

## Risk / safety
- **No live mutation anywhere.** DB1 is rebuilt from GCS on a gated `--execute` only; nothing here touches it.
- Local file moves only affect path references, all traced and fixed in Phase 2.
- `git mv` preserves history; deletions are recoverable from git.

## Open questions
1. **Phase 3 deletion** — delete the dead `src/pipeline` + `src/main.py` + `upload_and_import_v2.py`, or
   keep them? (Recommend delete.)
2. **`new/` naming** — keep `new/` as the inbox name, or rename to something clearer (e.g. `_inbox/`)?
   (Recommend keep `new/` — minimal churn, `generate_metadata.py` already targets it.)
