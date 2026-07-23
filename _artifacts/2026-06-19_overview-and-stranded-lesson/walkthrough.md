---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — I_H_04 overview + I_B_05 stranded-lesson fix
  type: walkthrough
  date: 2026-06-19
---

# Walkthrough — two QA bugs the app team caught

## What these were

1. **`PPL_PA_I_H_04` had no `lesson_overview`.** Not blank — the key was *absent* from the JSON. The
   three RKPs were fully authored; only the top-level overview never got written.
2. **`PPL_PA_I_B_05` (Inoperative Equipment — 91.213(d)) was stranded.** Live in Firestore with
   manifest/quiz/flashcards/bridge keys, but never added to `curriculum_key.json`, so `ALL_LESSON_IDS`
   was 47 instead of 48 and the lesson was invisible to the router, title resolver, prereq DAG, and
   Igor's checkride plan (12.3.1).

Both are the same failure mode: an app surface is wrong because an authoring artifact is incomplete.
The Curriculum Key is **artifact #7 in the lifecycle, owned by "Ingestion team / Woz"** — our upkeep,
even though the file physically lives in the app tree.

## What I changed (file by file)

**Pipeline repo (`Ingestion_pipeline_AvCh`)**
- `curriculum_components/rkp_manifests/PPL_PA_I_H_04_rkp.json` — added a 3,369-char `lesson_overview`
  in the same slot every sibling uses (after `required_knowledge_points`). The prose is synthesized
  **only** from the three RKPs already in the file (symptom→cause→correction; IMSAFE & the No-Go;
  hazard→risk→mitigation) and the regs they already cite (61.53, Part 68, PHAK Ch 17, AIM 8-1-2). No
  new citations — constitution hard-stop on fabricated references.

**App repo (`AGY_AVIATIONCHAT`)**
- `backend/data/curriculum_key.json` — inserted the `PPL_PA_I_B_05` entry after I_B_04, matching the
  file's exact 7-field schema. `acs_element_keys` copied verbatim from the manifest
  (`PA.I.B.K3a/R1/S3`); `prerequisite_acs_nodes: [PA.I.B.K1, PA.I.B.K2]` (your approved value,
  mirroring I_B_04); no `status` field → defaults to `active` → lands in `ALL_LESSON_IDS`.
- `backend/tests/data/test_curriculum_activation.py` — added `test_every_manifest_is_activated()`,
  the **reverse guard**: every manifest in the mirror must map to an active lesson. This is the check
  that was missing — the existing guards only verify active→manifest, never manifest→active.
- `_docs/specialist_lesson/rkp_manifests/PPL_PA_I_H_04_rkp.json` — synced the mirror copy to match the
  pipeline manifest (the mirror is a Firestore-derived test fixture; I confirmed it was byte-identical
  to the pipeline manifest apart from the overview before overwriting).

## What fought back

- **Windows console encoding.** A verification `diff` printed a false "IDENTICAL" because both Python
  subprocesses crashed on cp1252 trying to print the `→` glyph, sending empty strings to `diff`. Re-ran
  with `PYTHONUTF8=1` and confirmed the files are genuinely identical apart from the overview. The
  files themselves are clean UTF-8 (verified first bytes: `[`/`{`/`"`, not the `255 254` UTF-16 BOM).
- **The dry-run was (correctly) blocked.** I tried `upload_manifests.py` (dry-run, writes nothing) to
  show the Firestore push was ready; the harness classifier denied it as production ingestion tooling.
  That matches the approved plan — Firestore re-ingestion is your gated step. Handed off below.
- **Otherwise clean.** No surprises in the edits or the tests.

## Test output (actual, pasted)

App — data-level activation + acyclic + prereq guards (the async router test, which needs live
Firebase, deselected):
```
$ python -m pytest backend/tests/data/test_curriculum_activation.py \
    backend/tests/services/evolution/test_curriculum_acyclic.py \
    backend/tests/utils/test_curriculum_resolver_prereq.py -q -k "not routable"
........................................................................ [ 66%]
....................................                                     [100%]
108 passed, 1 deselected in 0.74s
```

The new guard, by name + the self-validating count + I_B_05's quiz integrity:
```
backend/tests/data/test_curriculum_activation.py::test_active_count_self_validating PASSED
backend/tests/data/test_curriculum_activation.py::test_every_manifest_is_activated PASSED
backend/tests/data/test_curriculum_activation.py::test_all_lessons_quiz_integrity[PPL_PA_I_B_05] PASSED
3 passed, 99 deselected in 0.44s
```

Teeth proof — the new guard genuinely catches this class of bug:
```
stranded the guard WOULD have caught: ['PPL_PA_I_B_05']   # if the fix were absent
stranded with the fix applied      : []
```

Roster + mirror sanity:
```
ALL_LESSON_IDS count: 48          (was 47)
I_B_05 in roster   : True
I_B_05 status/acs  : active ['PA.I.B.K3a', 'PA.I.B.R1', 'PA.I.B.S3']
mirror I_H_04 overview chars: 3369
```

App — other consumers of `ALL_LESSON_IDS`:
```
$ python -m pytest backend/tests/data/test_curriculum.py backend/tests/test_curriculum_resolver.py \
    backend/tests/utils/test_curriculum_resolver_prereq.py -q
35 passed in 0.17s
```

Pipeline — offline schema + bridge-key gate (validates the edited I_H_04 manifest):
```
$ python -m pytest src/tests/ -q
33 passed in 0.31s
```

One **environment-gated** failure, NOT a regression:
```
backend/tests/data/test_curriculum_activation.py::test_all_lessons_routable
  RuntimeError: Firebase Admin not initialized. ...
1 failed in 7.59s
```
This test calls `get_db()` and needs live Firebase credentials this offline run doesn't have — it
fails identically regardless of curriculum content. Run it in a credentialed env (or via live QA) to
also confirm I_B_05 is in the semantic-router catalog, which depends on I_B_05 being in Firestore
(you confirmed it is; the mirror being Firestore-derived corroborates it).

## Deviations from the plan

- Added one step the plan implied but didn't spell out: **syncing the app's I_H_04 mirror** so the
  Firestore-derived test fixture matches the new overview. Surgical, safe, reversible.
- I did NOT run the Firestore `--execute` (blocked by the harness, and reserved for you per the plan).

---

## Your Actions

### 1. Firestore push — DONE (you authorized it; I ran it)
On your explicit go-ahead I ran `python src/gcp/upload_manifests.py --execute` — full `.set()` of all
48 manifest docs to `aviationchat-database/rkp_manifests`. Result + read-back verification:
```
Uploaded 48/48 manifests.

# read-back from Firestore:
PPL_PA_I_H_04: exists=True | lesson_overview chars=3369 | RKPs=3
PPL_PA_I_B_05: exists=True | lesson_overview chars=3703 | RKPs=4
```
The I_H_04 overview is now live in Firestore. I_B_05 was already live (confirmed above). No further DB
action needed.

### 2. Commit — PIPELINE repo (clean tree, only the manifest + artifacts)
```bash
cd "c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh"
git add curriculum_components/rkp_manifests/PPL_PA_I_H_04_rkp.json \
        _claude_artifacts/2026-06-19_overview-and-stranded-lesson/
git commit -m "fix(curriculum): author missing lesson_overview for PPL_PA_I_H_04"
```

### 3. Commit — APP repo (⚠️ add ONLY these 3 files)
The app tree has unrelated uncommitted work from another session (load-test story, sprint-status,
runbooks, stray `.out` files). **Do NOT `git add -A`.** Add exactly my three files:
```bash
cd "c:/Users/dlohn/.gemini/antigravity/scratch/AGY_AVIATIONCHAT"
git add backend/data/curriculum_key.json \
        backend/tests/data/test_curriculum_activation.py \
        _docs/specialist_lesson/rkp_manifests/PPL_PA_I_H_04_rkp.json
git commit -m "fix(curriculum): activate stranded lesson PPL_PA_I_B_05 + add reverse activation guard"
```

### 4. Flagged, not fixed (your call, per plan)
- **I_B_04 title/keywords mismatch:** in the key, I_B_04 is titled "Flying with Inoperative Equipment
  (91.213)" but its keywords are all Special Flight Permits, while I_B_05 is the real inoperative-
  equipment flowchart. Left untouched as you approved — worth a separate look at Area I.B labeling.
- **Durable fix (follow-up session):** promote `_test_scripts/derive_curriculum_key.py` to the real
  generator so the key is *derived* from the canonical roster and a lesson can't be hand-stranded again.
