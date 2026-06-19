---
IsArtifact: true
ArtifactMetadata:
  title: "Quiz/RKP authoring skills — correctness + read-first gate"
  type: implementation_plan
  date: 2026-06-19
---

# Quiz/RKP authoring skills — make them correct + enforce "read references first"

## Goal

The governing **guides** (`_docs/instruction_docs/quiz_authoring_guide.md` §0, `rkp_creation_guide.md`)
are correct and already say "read the source before authoring." The **SKILL files** that activate when
Daniel asks for a quiz/RKP are stale: they route the agent to a renamed folder, the wrong docs root, and
a deleted tool, and they don't gate on reading the guide. Fix the skills so the rule actually fires.

Done = every quiz/RKP SKILL (a) opens with a "read these first" step pointing at the correct guides +
source, (b) has zero stale paths, and (c) names the real deploy tool.

## Files to edit (the guides are already correct — not touched)

| File | Changes |
|---|---|
| `.claude/skills/quiz-bank-generation/SKILL.md` | paths + tool + read-first gate |
| `.agent/skills/1_quiz-bank-generation/SKILL.md` | paths + tool + read-first gate |
| `.claude/skills/rkp-manifest-creation/SKILL.md` | paths + read-first gate |
| `.agent/skills/2_rkp-manifest-creation/SKILL.md` | paths + read-first gate |
| `.claude/skills/bridge-key-verification/SKILL.md` | paths only |
| `.agent/skills/3_bridge-key-verification/SKILL.md` | paths only |
| `_docs/project_context_prps/quiz_generator_prompt.md` | paths (referenced by the quiz skill §12) |

> The two skill copies (`.agent/` vs `.claude/`) have diverged in prose verbosity. I will apply the
> **same** path/tool/gate fixes to both, preserving each copy's existing wording — not unify their content.

## The changes (applied per file, surgically)

1. **Path fixes** (replace_all where safe):
   - `specialist_curriculum/` → `curriculum_components/`
   - `docs/instruction_docs/` → `_docs/instruction_docs/`
   - `docs/project_context_prps/` → `_docs/project_context_prps/`
   - `docs/docs_prds/` → `_docs/docs_prds/`
   - the RKP skill's `cd specialist_curriculum/scripts` → `cd curriculum_components/scripts`
   - the RKP skill's `specialist_curriculum/quiz_schema.md` (ACS→lesson mapping) → `curriculum_components/quiz_schema.md`

2. **Wrong/deleted tool (quiz skills only):**
   - `upload_quiz_banks.py` → `ingest_quiz_banks.py` (§7 step 7, §8 deployment block, checklist)
   - Note it writes the **`questions/` subcollection** the app reads (per `curriculum_lifecycle.md` §3), gated `--execute`
   - Auth key `auth_keys/librarian-service-account.json` → `auth_keys/service-account.json` (the config default)

3. **Add a "Step 0 — Read these first (before authoring anything)" gate** at the top of each skill's
   Execution Pipeline:
   - **RKP skill:** read `_docs/instruction_docs/rkp_creation_guide.md` (schema + reverse-contract) and
     `_docs/instruction_docs/bridge_key_guide.md` (bridge-key contract); read the source master module in
     `curriculum_components/curriculum_modules/`. Don't write JSON until these are read.
   - **Quiz skill:** read `_docs/instruction_docs/quiz_authoring_guide.md` **§0** (author from the RKP) and
     the target `{lesson_id}_rkp.json` `knowledge` fields in `curriculum_components/rkp_manifests/`. Build
     the fact inventory before writing questions.

4. **Remove the stale "13 sub-par non-Area-I banks" claim** (CONFIRMED by Daniel 2026-06-19 — those banks
   were since updated). Strip the warning from the quiz skill's YAML `description`, §10 ("Quiz Banks Needing
   Rewrite"), §0/§1 gold-standard notes, and the "never pushed to Firebase" line. Replace with the guide's
   verified statement: **all 48 banks meet the standard (verified 2026-06-19); Area I is the style reference
   for new banks.** Apply to both the `.agent` and `.claude` quiz skill copies.

## Verification

- Re-grep all 6 skills for `specialist_curriculum`, `docs/instruction_docs`, `docs/project_context_prps`,
  `upload_quiz_banks`, `librarian-service-account` → expect **0**.
- Confirm each quiz/RKP skill's Execution Pipeline opens with the read-first step naming the correct guide.
- `git grep` the skills for `ingest_quiz_banks.py` → present in both quiz skills.

## Out of scope (flag, don't touch here)

- The repo-wide `docs/ → _docs/` migration (belongs to the prior `repo-structure-cleanup` session).
- General staleness in `curriculum_lifecycle.md` / `get_back_on_track.md` not related to quiz/RKP authoring.
- Reconciling the `.agent` vs `.claude` prose divergence (content merge — separate effort if wanted).

## Open question

- ~~Item 4 status~~ — **RESOLVED 2026-06-19:** Daniel confirmed the banks were updated, so the "13 sub-par"
  warning is stale. Skill will be aligned to "all 48 verified to standard." No open questions remain.
