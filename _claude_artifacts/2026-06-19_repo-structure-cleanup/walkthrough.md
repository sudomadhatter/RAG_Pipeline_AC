---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — Repo structure cleanup (Phase 1)
  type: walkthrough
  date: 2026-06-19
---

# Walkthrough — Repo structure cleanup (Phase 1)

## What you asked
"Assess my file structure and improve it to industry standard so other devs can navigate it." We
agreed a **phased** approach: Phase 1 = high-ROI, low-risk work that touches **no working code
path**; the structural directory moves (data → `data/`, `src/pipeline/` rename) are a separately
gated Phase 2.

## The decisions that shaped it
- **Scope:** phased, low-risk first.
- **Data trees:** consolidate under `data/` — deferred to Phase 2.
- **Docs roof:** rename `_01_My/` → `docs/`, keeping your internal layout.

Mid-session you moved `docs/` into `_01_My/docs_prds/` by hand and said "keep all docs under my."
I pushed back: a folder named `_01_My` is the least navigable name in the repo for an outsider, and
it conflicts with the exact goal. We reconciled by keeping your consolidation but naming the roof
`docs/` — both goals met. That turned out clean: git's rename detection even reconnected the
manual move you'd made.

## What I did, in order

**1. Renamed `_01_My/` → `docs/`.** A single filesystem move of the whole folder, then a scoped
`git add docs _01_My`. Git recorded **30 renames** (3 core docs + 6 instruction guides + 21 PRDs),
so `git log --follow` still works on everything — including the three core docs you'd moved by hand
(reconnected as `docs/X.md → docs/docs_prds/X.md`). Internal layout preserved exactly:
`docs/docs_prds/`, `docs/instruction_docs/`, `docs/project_context_prps/`.

**2. Repointed every `_01_My/` reference → `docs/`** across 8 files: the 6 skill files (3
`.claude/skills/*`, 3 `.agent/skills/*` — the latter use absolute `file:///` URLs, handled by
substring replace), plus `docs/docs_prds/asset_registry.md` and
`docs/docs_prds/Master_Curriculum_Pipeline.md`. In the PRD I also fixed a frontmatter relative path
(`instruction_docs/…` → `../instruction_docs/…`, since it now sits in `docs_prds/`) and a
**double-stale** reference (`_01_My/_artifacts/2026-06-18…` → `_claude_artifacts/2026-06-18…` — that
path had moved in the prior session). The three `_01_My` hits left in `prd.md` are **app-repo
cross-links** (`c:/AGY-Projects/aviationChat-AGY/_01_My/…`) — a different repo, intentionally left.

**3. Added `README.md`** — the front door this repo never had: what it is, a structure map, a
quickstart (venv → deps → `auth_keys/.env` → run → test), a common-operations table, a docs index,
and the agent-tool governance map. It also openly flags the two known warts (the two data trees and
the `pipeline/` vs `src/pipeline/` name clash) so a newcomer isn't confused before Phase 2 lands.

**4. Added `requirements.txt`** — the real direct deps derived from `src/` imports (firebase-admin,
the three `google-cloud-*` / `google-genai` libs, protobuf, pydantic, python-dotenv, pytest).
Intentionally **unpinned** (see Your Actions §2).

**5. Added `.env.example`** — documents the six vars `config.py` loads from `auth_keys/.env`, with
placeholders only and clear copy-to instructions.

**6. Gitignored `.pytest_cache/`** — one line; it wasn't tracked, so no removal needed.

**7. Fixed + reran the repo-map generator.** `scripts/generate_repo_map.py` still wrote to the old
`docs/repo-map.md` and its `IGNORE_DIRS` listed the retired `_artifacts` but not the new
`_claude_artifacts` / `_opencode_artifacts` / `.pytest_cache`. I updated the output path to
`docs/docs_prds/repo-map.md` and the ignore set, then regenerated. The map is now accurate and no
longer clutters itself with artifact folders.

## Verification (actual output)

```
$ python -m pytest src/tests/ -q
.................................                                        [100%]
33 passed in 0.21s

=== files exist ===
.env.example
README.md
requirements.txt

=== docs subdirs ===
docs/docs_prds   docs/instruction_docs   docs/project_context_prps

=== _01_My sweep (md/py, excl _claude_artifacts) ===
docs/project_context_prps/prd.md:13   _01_My/Docs/Specialist/...   <- app-repo cross-link (left)
docs/project_context_prps/prd.md:733  .../aviationChat-AGY/_01_My/...   <- app-repo cross-link (left)
docs/project_context_prps/prd.md:800  _01_My/Docs/Specialist/...   <- app-repo cross-link (left)

=== regenerated repo-map ===
_01_My in new map?        0
_claude/_opencode/pytest  none (good)
docs/ + subdirs           present
README.md / requirements  present

=== git (rename-aware) ===
renames detected: 30
RM docs/Master_Curriculum_Pipeline.md -> docs/docs_prds/Master_Curriculum_Pipeline.md
RM docs/asset_registry.md            -> docs/docs_prds/asset_registry.md
RM docs/repo-map.md                  -> docs/docs_prds/repo-map.md
 M .agent/skills/{1,2,3}_*/SKILL.md ·  M .claude/skills/{3 files}/SKILL.md
 M .gitignore ·  M scripts/generate_repo_map.py
?? README.md ?? requirements.txt ?? .env.example
```

The 33-test green run is the proof Phase 1 changed nothing executable: `src/`, the tests, and both
data trees were never touched.

## Deviations from plan
- **Generator hardening (beyond the literal plan, inside the "regenerate" task):** I also extended
  `IGNORE_DIRS` to drop the new artifact folders + `.pytest_cache` from the map. Without it the map
  would have regrown the clutter we just removed.
- **`specialist_curriculum/` stale refs left in place:** the skill files also point at
  `specialist_curriculum/…` (the old name for `curriculum_components/`). That's outside the approved
  `_01_My`→`docs` scope, and Phase 2 will rename that data tree anyway — fixing it now would be churn
  I'd redo. Flagged for Phase 2.

## Your Actions

**1. Commit — explicit paths only** (the tree is otherwise clean, but per repo rule never `git add -A`):

```bash
git add \
  README.md requirements.txt .env.example .gitignore \
  scripts/generate_repo_map.py \
  .claude/skills .agent/skills \
  docs _01_My \
  _claude_artifacts/2026-06-19_repo-structure-cleanup
git commit -m "Repo cleanup Phase 1: rename _01_My/ -> docs/, add README + requirements + .env.example, gitignore pytest cache, fix repo-map generator"
```

(`git add docs _01_My` stages the new tree **and** the deletion of the old paths so git records the
30 renames. `.claude/skills .agent/skills` stage only the 6 modified SKILL.md files.)

**2. Pin dependencies** (the one open item): there's no committed `.venv`, so I shipped
`requirements.txt` **unpinned** rather than invent versions. From your working environment:

```bash
pip freeze > requirements.lock.txt     # then copy the resolved == versions into requirements.txt
```

**3. Phase 2 (next, separately gated):** consolidate `curriculum_components/` + `pipeline/curriculum/`
under a single `data/` root (de-duplicating the master modules), rename `src/pipeline/` → `src/stages/`
to kill the name collision, and hoist `src/tests/` → `tests/`. Each step gated behind the 33-test
suite + a dry-run `probe_bridge_hop.py`. Say the word and I'll write the Phase 2 plan.

**4. Flagged, not done — hardcoded credential bug:** `src/gcp/create_v2_stores.py:6` and
`src/gcp/upload_and_import_v2.py:6` hardcode `c:\AGY-Projects\ingestion-Pipeline-AC\auth_keys\…json`,
which breaks on any other machine and violates `credential-resolution.md`. Worth fixing next (its own
small gate) since it directly blocks "other devs can run this."
