---
IsArtifact: true
ArtifactMetadata:
  title: Repo structure cleanup to industry standard (Phase 1)
  type: implementation_plan
  date: 2026-06-19
---

# Implementation Plan — Repo structure cleanup (Phase 1)

## Goal

Make this repo navigable to an outside developer **without breaking the verified-working pipeline
(48/48 bridge, 33 offline tests green)**. Daniel approved a **phased** approach: Phase 1 is the
high-ROI, low-risk work that touches **no working code path**; the structural directory moves
(`data/` consolidation, `src/pipeline/` rename) are deferred to a separately-gated **Phase 2**.

Decisions locked (this session):
- **Scope:** phased — low-risk first.
- **Data trees:** consolidate under `data/` — *Phase 2*.
- **Docs roof:** rename `_01_My/` → `docs/`, keep the internal layout Daniel just set up
  (`docs_prds/`, `instruction_docs/`, `project_context_prps/`). Daniel confirmed the docs move was
  "the only change" he made manually; the rest of the tree matches the repo map.

## Why this is safe (the core constraint)

`src/config.py:7` resolves all curriculum/library data from `pipeline/` (`PIPELINE_ROOT`), and
`src/gcp/*` reads authored assets from `curriculum_components/`. **Phase 1 does not move, rename, or
touch either of those trees, nor any file under `src/`.** It only renames a docs folder, adds
front-door files, and fixes doc/skill references. Nothing the pipeline executes against changes.

---

## Phase 1 — what changes

### 1. Rename `_01_My/` → `docs/` (history-preserving)

`git mv _01_My docs`. Internal layout is preserved exactly:

| After | Holds |
|---|---|
| `docs/docs_prds/` | `repo-map.md`, `asset_registry.md`, `Master_Curriculum_Pipeline.md` (this repo's core docs) |
| `docs/instruction_docs/` | the 6 authoring guides (bridge_key, curriculum_lifecycle, flashcard, get_back_on_track, quiz_authoring, rkp_creation) |
| `docs/project_context_prps/` | the ~21 PRD / architecture / product-context docs |

> Internal subfolder names are left as-is per Daniel's choice. (Optional future tidy: `docs_prds/`
> isn't a natural home for `repo-map.md`; could flatten later — not in this phase.)

### 2. Update every `_01_My/` reference → `docs/`

Found via grep; all are docs/skill text, **zero are code**:

| File | Refs | Change |
|---|---|---|
| [.claude/skills/rkp-manifest-creation/SKILL.md](.claude/skills/rkp-manifest-creation/SKILL.md) | L208–209 | `_01_My/instruction_docs/` → `docs/instruction_docs/` |
| [.claude/skills/quiz-bank-generation/SKILL.md](.claude/skills/quiz-bank-generation/SKILL.md) | L207–208 | `_01_My/...` → `docs/...` |
| [.claude/skills/bridge-key-verification/SKILL.md](.claude/skills/bridge-key-verification/SKILL.md) | L14, L154 | `_01_My/instruction_docs/` → `docs/instruction_docs/` |
| [.agent/skills/3_bridge-key-verification/SKILL.md](.agent/skills/3_bridge-key-verification/SKILL.md) | L14, L222 | absolute `file:///…/_01_My/…` → `…/docs/…` |
| [.agent/skills/2_rkp-manifest-creation/SKILL.md](.agent/skills/2_rkp-manifest-creation/SKILL.md) | L228–229 | absolute `file:///…/_01_My/…` → `…/docs/…` |
| [.agent/skills/1_quiz-bank-generation/SKILL.md](.agent/skills/1_quiz-bank-generation/SKILL.md) | L339–340 | absolute `file:///…/_01_My/…` → `…/docs/…` |
| `docs/docs_prds/Master_Curriculum_Pipeline.md` | L385, L439 | L385 `_01_My/_artifacts/2026-06-18…` → `_claude_artifacts/2026-06-18…` (double-stale); L439 `_01_My/instruction_docs/` → `docs/instruction_docs/` |
| `docs/docs_prds/asset_registry.md` | L90 | `_01_My/instruction_docs/` → `docs/instruction_docs/` |
| `docs/docs_prds/Master_Curriculum_Pipeline.md` | L9 (frontmatter) | `companion_docs: "instruction_docs/…"` → `"../instruction_docs/…"` (corrects relative path from `docs_prds/`) |

**Left intentionally untouched:** `docs/project_context_prps/prd.md` L13/L733/L800 — those point to
`c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/_01_My/…`, a **different (app) repo's** `_01_My`, not ours.

> A fresh repo-wide grep for `_01_My` will be run after edits to confirm zero stragglers (excluding
> the app-repo cross-links above and `_claude_artifacts/` history).

### 3. Add root `README.md` (NEW — the front door)

What a newcomer reads first: one-paragraph "what this repo is" (the **canonical** ingestion/curriculum
pipeline for AviationChat, separate from the app repo), a **structure map** of the current tree, a
**Quickstart** (venv → `pip install -r requirements.txt` → set up `auth_keys/.env` +
`service-account.json` per `.env.example` → `python -m src.main` → `python -m pytest src/tests/`), a
**docs index** (points at `docs/docs_prds/` for reference, `docs/instruction_docs/` for authoring),
and a pointer to the agent-governance files (`CLAUDE.md`, `AGENTS.md`, `.gemini/GEMINI.md`). It will
note that **Phase 2** (data → `data/`, `src/pipeline/` → `src/stages/`) is planned.

### 4. Add `requirements.txt` (NEW)

Direct third-party deps, derived from actual imports across `src/`:

```
firebase-admin
google-cloud-discoveryengine
google-cloud-storage
google-genai
protobuf
pydantic
python-dotenv
pytest
```

> **Open question (precision):** there is no `.venv` at the repo root, so I cannot `pip freeze` to
> pin exact versions (the `dependency-awareness` rule wants `==` pins). I'll ship this accurate but
> **unpinned** list, and the README/Your-Actions will tell you to pin from your working environment
> (`pip freeze`). If you point me at the venv, I'll pin it instead. I will **not** invent version
> numbers.

### 5. Add `.env.example` (NEW, repo root)

Documents the variables `src/config.py` loads from `auth_keys/.env` (which is gitignored, so the
example lives at root and the README explains placement): `GCP_PROJECT_ID`, `VERTEX_SEARCH_DB1_ID`,
`VERTEX_SEARCH_DB2_ID`, `VERTEX_SEARCH_LOCATION`, `GEMINI_API_KEY`, and the optional
`GOOGLE_APPLICATION_CREDENTIALS` override — placeholder values only, no secrets.

### 6. Gitignore `.pytest_cache/`

Add `.pytest_cache/` to `.gitignore`. It is **not** git-tracked (verified), so no `git rm` needed —
purely a one-line ignore so it stops showing up in the tree/map.

### 7. Repoint + regenerate the repo map

`scripts/generate_repo_map.py` writes to a hardcoded output path that assumed the old `docs/` (now
`docs/docs_prds/repo-map.md`). I'll read the script, update its output path constant to the new
location, then run it so `repo-map.md` reflects the post-Phase-1 tree. (Small contained path edit in
a non-pipeline script.)

---

## Verification (Phase 1)

Phase 1 changes no executable pipeline path, but I will prove nothing regressed:

```bash
python -m pytest src/tests/ -q          # expect 33 passed (unchanged)
grep -rn "_01_My" --exclude-dir=_claude_artifacts .   # expect only app-repo cross-links
ls README.md requirements.txt .env.example            # exist
ls docs/docs_prds docs/instruction_docs docs/project_context_prps   # moved intact
git status                                             # _01_My renames show as R (history kept)
```

Actual output will be pasted into `walkthrough.md`.

---

## Phase 2 — roadmap (NOT executed now; needs its own approval)

Documented here so the direction is on record; each gets its own plan + "approved" gate:

1. **Consolidate data under `data/`** — `curriculum_components/` → `data/authored/`;
   `pipeline/curriculum/` + `pipeline/library/` → `data/curriculum/` + `data/library/`; de-duplicate
   the master modules to one canonical copy. Requires editing `src/config.py`, `src/gcp/*`,
   `scripts/*`, `.gitignore`, and the living docs.
2. **Rename `src/pipeline/` → `src/stages/`** — kills the `pipeline/` (data) vs `src/pipeline/`
   (code) collision. Requires updating intra-`src` imports + `python -m` references in docs.
3. **Hoist `src/tests/` → `tests/`** — conventional top-level test dir.

Each Phase 2 step is gated behind the 33-test suite + a dry-run `probe_bridge_hop.py` to prove the
verified pipeline still works.

---

## Out of scope / flagged (not in this plan)

- **Hardcoded credential bug** (recommend fixing next, own gate): `src/gcp/create_v2_stores.py:6`
  and `src/gcp/upload_and_import_v2.py:6` hardcode
  `c:\Sudo_Hatter_Command\Projects\ingestion-Pipeline-AC\auth_keys\librarian-service-account.json` — violates
  `credential-resolution.md` and breaks on any other machine. Directly relevant to "other devs can
  run this," but it's a behavioral code change, so it gets its own approval rather than riding along.
- **Pruning stale PRDs** in `docs/project_context_prps/` (e.g. "V2.1 Master PRD" vs the live v2.8) —
  a content decision for Daniel, not a structure move. Deferred.

## Open questions

1. **Dependency pinning** (see §4): ship unpinned now + you pin from your venv, or point me at the
   venv so I pin exact versions in this phase?
