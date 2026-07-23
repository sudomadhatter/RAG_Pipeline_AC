---
IsArtifact: true
ArtifactMetadata:
  title: State Map + Two-Folder Wiring Cleanup
  type: implementation_plan
  date: 2026-06-19
---

# Implementation Plan — State Map + Two-Folder Wiring Cleanup

## Goal

Make the `curriculum_components/` ↔ `pipeline/curriculum/` flow **self-documenting and
drift-proof for a new developer**, without moving any data or changing any live database behavior.

Concretely, "done" looks like:

1. `python scripts/generate_state_map.py` exists and turns "is this stale?" into a command —
   it inventories both folders and flags drift (offline), and optionally reports live
   Firestore/DB1/DB2 counts (`--live`).
2. The root `README.md` no longer lies (no `src/main.py` / `src/pipeline/`, no broken `docs/` links).
3. `curriculum_components/` has a README, matching its sibling `pipeline/curriculum/README.md`.
4. The four GCP scripts read `curriculum_components/` through **config constants**, the same way
   they already read `pipeline/curriculum/` — one place to change a path, not four copy-pasted strings.
5. The offline test suite (33 tests) stays green — proving zero behavior change.

**Scope guardrails (from Daniel's decisions):**
- Docs + wiring only. **No folder moves** (no `data/` consolidation — that stays Phase 2).
- **Keep all existing docs.** The 21 `project_context_prps/` PRDs stay as app-context. The six
  instruction guides stay. Nothing is deleted or archived. We only *add* the map and *fix* the
  stale README.
- **The git repo stays the canonical source of truth** for the 48 RKP manifests + 48 quiz banks —
  they are NOT deleted in favor of Firestore (Firestore has no version history; the repo keeps
  diff/review/revert on every answer-key edit). Instead, `generate_state_map.py --live` **auto-proves
  repo == Firestore** on each run, so the multi-copy drift that `asset_registry.md` hand-reconciles
  becomes a command, not a chore.

---

## What I found (the "why" behind this plan)

The flow itself is correct and live. The rot is in the connective tissue a new dev hits first:

- **`README.md` is stale at the front door** — documents `src/main.py` and `src/pipeline/` (both
  deleted), tells you to run `python -m src.main` (fails), and every `docs/...` doc link is broken
  because the tree was renamed to `_docs/`.
- **`asset_registry.md` is a hand-typed snapshot of live DB counts** — born stale by design.
- **34 podcasts in `curriculum_components/lesson_podcasts/` are orphaned** — no script ingests them.
- **Asymmetric wiring** — `pipeline/curriculum/` uses named `config.py` constants; `curriculum_components/`
  is hardcoded inline as `config.PROJECT_ROOT / "curriculum_components" / "..."` in 4 scripts.
- **CWD-relative paths** in `scripts/fallback_generator.py:81` and `fallback_generator2.py:92`
  (`Path("curriculum_components/curriculum_modules/Area 9 Tasks B,C PPL.md")`) break unless run from
  repo root — violates the `Path(__file__)` rule.

---

## Files touched

### Part A — The live map (new)

| File | Action |
|---|---|
| [scripts/generate_state_map.py](scripts/generate_state_map.py) | **NEW.** Offline (default): inventory both folders + cross-reference drift. `--live`: add Firestore + DB1/DB2 counts. |
| [_docs/docs_prds/STATE.md](_docs/docs_prds/STATE.md) | **NEW (generated).** First run output, committed next to `repo-map.md`. Header marks it auto-generated. |
| [_docs/docs_prds/asset_registry.md](_docs/docs_prds/asset_registry.md) | **EDIT (1 banner line).** Point readers to `STATE.md` / the map command for live counts. Doc kept, not deleted. |

`generate_state_map.py` design (lean, simplicity-first):

- **Offline section (default, no creds):** counts `curriculum_components/{curriculum_modules,
  rkp_manifests,quiz_banks,faa_docs,lesson_podcasts}` and `pipeline/curriculum/{elements,sidecars}`
  + `curriculum.jsonl` lines. Cross-references: RKP lesson-ids vs quiz lesson-ids (which lack a pair),
  podcasts flagged as **not ingested**, element count vs manifest entries. Writes a Markdown table to
  `STATE.md`. Pure stdlib + `config.py` paths — runs in CI, no network.
- **`--live` section (needs creds, degrades gracefully):** Firestore `rkp_manifests` / `quiz_banks`
  doc counts via the **exact** `firebase_admin` pattern in `upload_manifests.py:48-54`; DB1/DB2 doc
  counts via the same `discoveryengine` client `reimport_db1_keys.py` already uses. **Drift check
  (the repo == Firestore auto-verify):** compare the local RKP/quiz `lesson_id` set against the
  Firestore doc-id set and flag any local-only or Firestore-only ids — this is what replaces the
  hand-typed "zero discrepancies" line in `asset_registry.md`. Wrapped in try/except — if
  creds/services are missing it prints "live section skipped" and still emits the offline map. No new
  Firestore client topology; reuses existing patterns (constitution-safe).

### Part B — Truth-up the docs (edit / new, no deletions)

| File | Action |
|---|---|
| [README.md](README.md) | **EDIT.** Remove `src/main.py` + `src/pipeline/` from the structure block; fix all `docs/` → `_docs/` links; drop the two `python -m src.main` rows; update the Phase-2 note (`src/pipeline/` no longer exists); add `STATE.md` + the map command to the docs index. |
| [curriculum_components/README.md](curriculum_components/README.md) | **NEW.** Mirror `pipeline/curriculum/README.md`: each subfolder, which script ingests it, where it lands. Documents the podcast orphan honestly. |

### Part C — Symmetric wiring (config constants, behavior-preserving)

| File | Action |
|---|---|
| [src/config.py](src/config.py) | **EDIT.** Add authored-asset constants: `COMPONENTS_ROOT`, `RKP_MANIFESTS_DIR`, `QUIZ_BANKS_DIR`, `FAA_DOCS_DIR`, `MODULES_DIR`, `PODCASTS_DIR`. |
| [src/gcp/upload_manifests.py](src/gcp/upload_manifests.py) | **EDIT** `:20` → `config.RKP_MANIFESTS_DIR`. |
| [src/gcp/probe_bridge_hop.py](src/gcp/probe_bridge_hop.py) | **EDIT** `:18` → `config.RKP_MANIFESTS_DIR`. |
| [src/gcp/import_db2_docs.py](src/gcp/import_db2_docs.py) | **EDIT** `:27/:29` → `config.FAA_DOCS_DIR` / `config.RKP_MANIFESTS_DIR`. |
| [src/gcp/ingest_quiz_banks.py](src/gcp/ingest_quiz_banks.py) | **EDIT** `:21` → `config.QUIZ_BANKS_DIR`. |
| [scripts/fallback_generator.py](scripts/fallback_generator.py) | **EDIT** `:81` → `config.MODULES_DIR / "Area 9 Tasks B,C PPL.md"` (add `sys.path` + `import config`). |
| [scripts/fallback_generator2.py](scripts/fallback_generator2.py) | **EDIT** `:92` → same. |

> The values are byte-identical to today's hardcoded strings — this is a *referential* refactor, so
> the 33-test suite passing is the proof of zero behavior change.

---

## Execution order

1. Add the config constants (Part C, `config.py`) — everything else can lean on them.
2. Wire the 4 GCP scripts + 2 fallback generators to the constants.
3. Run `python -m pytest src/tests/ -q` → confirm still 33 green (catches a bad rewire immediately).
4. Build `generate_state_map.py`; run it offline; commit the generated `STATE.md`.
5. Rewrite `README.md`; add `curriculum_components/README.md`; banner-edit `asset_registry.md`.
6. Final `pytest` + final `generate_state_map.py` run; paste both outputs into `walkthrough.md`.

## Verification plan

- `python -m pytest src/tests/ -q` — **before and after** (must stay 33 passed / 0 failed).
- `python scripts/generate_state_map.py` (offline) — must produce `STATE.md` and flag the podcast
  orphan + any RKP/quiz mismatch. Actual output pasted into the walkthrough.
- `--live` + `python src/gcp/probe_bridge_hop.py` — **optional, Daniel-run** (needs creds); listed
  in "Your Actions," not blocking.

## Open questions

1. **`STATE.md` location** — I'm defaulting to `_docs/docs_prds/STATE.md` (sits beside the
   auto-generated `repo-map.md`). Say the word if you'd rather it be a discoverable root `STATE.md`.
2. **Config constant names** — proposing bare `RKP_MANIFESTS_DIR` etc. (no prefix). If you prefer an
   `AUTHORED_` / `COMPONENTS_` prefix to visually separate authored-assets from the DB1-store
   `CURRICULUM_*` constants, I'll use it.
3. **Commit `STATE.md`?** — yes by default (like `repo-map.md`, it's a readable generated artifact).
   It will drift in git between regens; that's expected and fine.

---

*No project file will be modified until Daniel replies **"approved."***
