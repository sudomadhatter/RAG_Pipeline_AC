---
IsArtifact: true
ArtifactMetadata:
  title: "pipeline/curriculum cleanup — walkthrough"
  type: walkthrough
  date: 2026-06-19
---

# pipeline/curriculum cleanup — walkthrough

## What this did

Turned `pipeline/curriculum/` from a confusing hybrid (real DB1 source + an aspirational
`new/active/superseded`/`_v2_split` lifecycle that was never used + duplicates + a misfiled artifact)
into an honest DB1 source store whose layout matches what's actually deployed and what the docs say.

## The verification that drove it (read-only)

Before touching anything, I reconciled the folder against the live build manifest:

- `curriculum.jsonl` = **184 entries** = the DB1 import manifest (matches live DB1 = 184 docs).
- `active/` = 172 split lessons + 13 byte-identical master-module dupes + 1 stray `library_v2_import.jsonl`.
- `new/` = 12 Area IX lessons (`.md` + `.json`), already live, never promoted.
- `_v2_split/` = empty (the docs claimed it held the 184 micro-lessons).
- **172 (active) + 12 (new) = 184 = every manifest id, 0 orphans, 0 missing.** The folder is a 1:1 match
  for DB1, so it was safe to reorganize.

## Final structure

```
pipeline/curriculum/
├── elements/   (184 .md)   DB1 content — was active/, + the 12 Area IX .md from new/
├── sidecars/   (12 .json)  Area IX authored metadata sidecars — was new/*.json
├── new/        (README)    authoring inbox, now empty
├── curriculum.jsonl        GENERATED manifest (unchanged path, gitignored)
└── README.md               front-door explainer
```

## Step by step

**Phase 1 — folder reorg (all `git mv`, history preserved).** `active/ → elements/`; the 12 Area IX
`.md` moved into `elements/`; the 12 Area IX `.json` moved into a new `sidecars/`. Deleted the 13
duplicate master modules (canonical copies live in `curriculum_components/curriculum_modules/` —
verified byte-identical), the empty `_v2_split/`, and the stray/stale `library_v2_import.jsonl`
(confirmed zero code/config references first). Result: `elements/` = 184 `.md`, `sidecars/` = 12 `.json`,
`new/` empty.

**What fought back:** `git rm` of the master modules errored the first time (`changes staged in the
index`) because the `active→elements` rename was already staged — re-ran with `-f` and it was clean.

**Phase 2 — repoint the real consumers.** `src/config.py`: renamed `CURRICULUM_ACTIVE → CURRICULUM_ELEMENTS`,
added `CURRICULUM_SIDECARS` and a derived `CURRICULUM_JSONL`, kept `CURRICULUM_NEW`, removed the fictional
filesystem constants (`CURRICULUM_SUPERSEDED`, `CURRICULUM_MANIFEST`, all `LIBRARY_*` lifecycle paths,
`LIBRARY_JSONL_FILE`) while keeping the real GCP target constants (`LIBRARY_BUCKET`/`_DATA_STORE_ID`/`_LOCATION`,
used by `import_db2_docs.py`/`probe_bridge_hop.py`/`derive_db2_vocabulary.py`). `reimport_db1_keys.py`:
`AREA_IX_SIDECARS → config.CURRICULUM_SIDECARS`, `OUT_JSONL → config.CURRICULUM_JSONL` (+ docstring path).
`import_db2_docs.py`: `CURRICULUM_JSONL → config.CURRICULUM_JSONL`. `audit_sidecars.py`: scans
`[CURRICULUM_NEW, CURRICULUM_SIDECARS]` (the `.json` now live in `sidecars/`).

**Phase 3 — retired the dead scaffolding.** Confirmed it was a closed island (only `main.py` +
`pipeline/curriculum.py` + `pipeline/library.py` referenced it) and deleted `src/main.py`,
`src/pipeline/{base,curriculum,library}.py`, `src/utils/lifecycle.py`, and the broken
`src/gcp/upload_and_import_v2.py` (it hardcoded `c:\AGY-Projects\…` machine paths — couldn't run here).
Re-grepped: **zero dangling references** to any removed config constant.

**Phase 4 — docs.** Fixed the three `_v2_split` references in `asset_registry.md` (→ `elements/`),
added a `sidecars/` row, removed four table rows pointing at deleted files (`upload_and_import_v2.py`,
`src/pipeline/curriculum.py`, `src/pipeline/library.py`, `python -m src.main`). Regenerated
`_docs/docs_prds/repo-map.md`. Added `pipeline/curriculum/README.md` + `new/README.md`.

## Verification (actual output)

**Offline test gate** — `python -m pytest src/tests/ -q`:
```
.................................                                        [100%]
33 passed in 0.20s
```

**Live read-only probe** — `python src/gcp/reimport_db1_keys.py` (dry run, no `--execute`):
```
=== DRY RUN — wrote local JSONL, no import ===
Built 184 entries (target 184).
  171 lessons resolve to >=1 DB2-covered doc_key, 13 reference-only.
  ...
  JSONL: .../pipeline/curriculum/curriculum.jsonl (184 lines)
```
This pulled the live DB1, read the 12 Area IX sidecars **from the new `sidecars/` path**, and rebuilt
all 184 entries with no problem docs — proving the path repoint works end-to-end against the live store.
171 covered + 13 reference-only matches the asset registry.

**Sidecar audit** — `python scripts/audit_sidecars.py`: scanned the 12 sidecars at the new path
(`Total files checked: 12`). It flags 14 "unknown key" lines — these are **pre-existing** Area IX
reference-only citations (`AC 120-80`, `FAA-H-8083-25C` vs the family tag, legal interpretations) that
the strict linter doesn't family-normalize. The same files produced identical flags when they were in
`new/`; nothing regressed, and `reimport_db1_keys.py` correctly classifies them as the expected 13
reference-only lessons.

## Findings noted, not acted on (out of scope)

- **`curriculum.jsonl` drift:** a fresh live rebuild produced a 3-line diff vs the committed copy — the
  reg-key normalizer rendering `14 CFR 61.23(c)→61.23`, `91.213(d)(2)→91.213(d)`, `91.205(b)→91.205` for
  three **Area I** lessons (none Area IX, none from my path change). I reverted the manifest to keep this
  reorg's change set clean. The committed `curriculum.jsonl` is slightly stale vs a fresh build — refresh
  it whenever DB1 is next re-imported.
- **`curriculum.jsonl` is gitignored (`.gitignore:43`) yet tracked** (committed before the ignore rule).
  If you want it untracked, `git rm --cached pipeline/curriculum/curriculum.jsonl`.
- **`docs/` vs `_docs/`:** the repo is mid-migration from the earlier repo-structure-cleanup session; a
  few docs still say `docs/instruction_docs/...`. Left alone — it belongs to that migration, not this task.
- No `active-context.md` exists in this repo, so there was nothing to update (CLAUDE.md references one
  that was never created here).

## Your Actions

### 1. Review
- New folder: [pipeline/curriculum/](pipeline/curriculum/) — `elements/` (184), `sidecars/` (12), `new/`, README.
- Config: [src/config.py](src/config.py); script repoints in [reimport_db1_keys.py](src/gcp/reimport_db1_keys.py), [import_db2_docs.py](src/gcp/import_db2_docs.py), [audit_sidecars.py](scripts/audit_sidecars.py).
- Doc fixes: [asset_registry.md](_docs/docs_prds/asset_registry.md).

### 2. Commit (heads-up on entanglement)
The working tree already had uncommitted work from the prior repo-structure-cleanup (the `docs/ → _docs/`
rename, skill edits, `README.md`/`requirements.txt`/`.env.example`). To keep **this** reorg as its own
clean commit, stage just the code + data (the renames/deletes are already staged from `git mv`/`git rm`):

```bash
git add pipeline/curriculum \
        src/config.py src/gcp/reimport_db1_keys.py src/gcp/import_db2_docs.py \
        scripts/audit_sidecars.py \
        _claude_artifacts/2026-06-19_pipeline-curriculum-cleanup

git commit -m "Cleanup pipeline/curriculum: active->elements, sidecars/, drop dead lifecycle scaffolding

- Rename active/ -> elements/ (184 DB1 split lessons); move Area IX .json -> sidecars/
- Delete duplicate master modules, empty _v2_split/, stray library_v2_import.jsonl
- Repoint config.py + reimport_db1_keys.py + import_db2_docs.py + audit_sidecars.py
- Remove vestigial 6-phase pipeline (src/main.py, src/pipeline/*, lifecycle.py, upload_and_import_v2.py)
- Verified: pytest 33 passed; reimport dry-run rebuilds 184 entries from sidecars/

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

> **The doc edits** (`_docs/docs_prds/asset_registry.md` + the regenerated `repo-map.md`) live inside the
> still-uncommitted `_docs/` tree from the prior session. Don't cherry-pick them — let them ride along
> when you commit the `docs/ → _docs/` migration, so the doc set lands consistently. (If you'd rather
> fold everything into one commit, add `_docs` and the other prior-session paths to the `git add` above.)
