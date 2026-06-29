---
IsArtifact: true
ArtifactMetadata:
  title: "Quiz/RKP authoring skills correction + small fixes — walkthrough"
  type: walkthrough
  date: 2026-06-19
---

# Quiz/RKP authoring skills correction + the two small fixes — walkthrough

## Two small fixes (the items flagged in the first walkthrough)

1. **`src/gcp/create_v2_stores.py`** hardcoded `os.environ['GOOGLE_APPLICATION_CREDENTIALS'] =
   r'c:\Sudo_Hatter_Command\Projects\ingestion-Pipeline-AC\auth_keys\librarian-service-account.json'` → replaced with the
   standard `import config` credential resolution (auth_keys/.env + service-account.json), matching every
   other `src/gcp/*` script. Also sourced `PROJECT_ID`/`LOCATION` from `config` (removes duplication and
   makes the import "used"). Compiles clean. This was the **last** hardcoded `c:\Sudo_Hatter_Command\…` path in the repo.
2. **`curriculum.jsonl`** was gitignored yet tracked → `git rm --cached` (staged; file stays on disk). It's a
   generated artifact, so it's now properly untracked.

## The audit verdict (your question)

**Is there a rule telling the agent to read the right reference docs before authoring?** Yes — in the
**guides**, which are correct and current:
- `_docs/instruction_docs/quiz_authoring_guide.md` **§0 "Author from the RKP first"**.
- `_docs/instruction_docs/rkp_creation_guide.md` (schema + reverse-contract).

But the agent-facing **SKILL files** undercut it: they pointed at the old `specialist_curriculum/` folder,
the wrong `docs/` root, and the **deleted** `upload_quiz_banks.py`, and they buried the "read the guide"
step at the bottom. So the rule existed but the skills routed the agent to broken paths and never forced
the read. Fixed.

## What changed in the skills (6 SKILL files + 1 prompt)

**Mechanical (all 7 files, via `sed`):**
- `specialist_curriculum/` → `curriculum_components/`
- `docs/instruction_docs|project_context_prps` → `_docs/…`
- `upload_quiz_banks` → `ingest_quiz_banks`
- `librarian-service-account` → `service-account`

**Structural (quiz skills, both `.agent` + `.claude`):**
- Added **"Step 0 — Read these references FIRST"** to the execution pipeline: read
  `quiz_authoring_guide.md §0` + the target RKP's `knowledge` fields before writing any question.
- Rewrote the deploy section to reality: `python src/gcp/ingest_quiz_banks.py [--execute]` writing the
  **`quiz_banks/{lesson_id}/questions/{q}` subcollection** (not the old `set()`-overwrite on the parent),
  gated behind `--execute`; removed the bogus "ingest_quiz_banks.py line 10 hardcoded path" warnings.
- Removed the stale **"13 non-Area-I banks are sub-par / rewrite / never pushed"** claim (you confirmed those
  were updated) → replaced with "all 48 verified to standard (2026-06-19); Area I is the style reference."

**Structural (RKP skills, both copies):**
- Added **"Step 0 — Read these references FIRST"**: `rkp_creation_guide.md` + `bridge_key_guide.md` + the
  source master module in `curriculum_components/curriculum_modules/`, before building any JSON.

**Bridge-key skills (both copies):** path corrections only (per plan).

## Verification (actual output)

```
=== A. residual stale tokens (expect NONE) ===
.agent/.../1_quiz-bank-generation/SKILL.md:281: ... never the old `upload_quiz_banks.py` (deleted ...
.claude/.../quiz-bank-generation/SKILL.md:126:  ... (never the old `upload_quiz_banks.py`).
  (end — nothing above = clean)
```
The only two `upload_quiz_banks` hits are the **intentional** "do not use the deleted tool" warnings.
```
=== B. 'Step 0: Read these references FIRST' present in quiz+rkp skills (expect 4) === 4
=== C. ingest_quiz_banks.py refs ===  .agent quiz=6  .claude quiz=3
       quiz_authoring_guide.md present in both quiz skills; rkp_creation_guide.md present in both rkp skills
```
`create_v2_stores.py` compiles (`python -m py_compile` OK). `curriculum.jsonl` untracked (0 tracked, on disk).

## Note

The `.agent/` and `.claude/` skill copies have **diverged in prose** (the `.agent` ones are more verbose).
I applied the same path/tool/gate/status fixes to both but did **not** unify their wording — that's a
separate content-merge if you ever want a single source.

## Your Actions

These skill files were **already uncommitted from the prior repo-structure session**; my edits layer on top.
The cleanly-committable parts of *this* follow-up:

```bash
git add .agent/skills .claude/skills \
        src/gcp/create_v2_stores.py \
        _claude_artifacts/2026-06-19_pipeline-curriculum-cleanup

# curriculum.jsonl untrack is already staged (git rm --cached). Confirm with: git status --short
git commit -m "Correct quiz/RKP authoring skills + small fixes

- Skills: fix stale paths (specialist_curriculum->curriculum_components, docs->_docs),
  deleted tool (upload_quiz_banks->ingest_quiz_banks + subcollection reality),
  add 'Step 0 read references first' gate, drop stale '13 banks need rewrite' claim
- create_v2_stores.py: hardcoded cred path -> config resolution (last Sudo_Hatter_Command path)
- Untrack generated curriculum.jsonl (git rm --cached)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

> `_docs/project_context_prps/quiz_generator_prompt.md` (the quiz-skill's referenced prompt) was also
> path-corrected, but it lives inside the still-uncommitted `_docs/` tree from the prior session — let it
> ride along with that `docs/ → _docs/` migration commit, same as the earlier `asset_registry.md` edits.
