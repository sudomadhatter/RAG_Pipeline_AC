---
IsArtifact: true
ArtifactMetadata:
  title: Task list — I_H_04 overview + I_B_05 stranded-lesson fix
  type: task_list
  date: 2026-06-19
---

# Task list (final state)

- [x] Research both bugs read-only + verify ground truth across both repos
- [x] Write `implementation_plan.md` with worries + risks
- [x] Get Daniel's approval + prereq confirmation (GATE — approved; prereqs `[K1,K2]` confirmed)
- [x] Fix A: author + insert I_H_04 `lesson_overview` (pipeline manifest) + sync app mirror
- [x] Fix B1: add `PPL_PA_I_B_05` entry to `curriculum_key.json` (app repo) → roster 47→48
- [x] Fix B2: add `test_every_manifest_is_activated` reverse guard (app repo)
- [x] Run test suites + paste actual output (app: 108 + 35 passed; pipeline: 33 passed; reverse
      guard passed + teeth-proven; 1 infra-gated failure documented, not a regression)
- [x] Write `walkthrough.md` + `task-list.md` with deploy/commit commands

## Firestore
- [x] Ran `upload_manifests.py --execute` (Daniel-authorized) → 48/48 uploaded; read-back confirms
      I_H_04 overview live (3369 chars) and I_B_05 present (3703 chars)

## Handed to Daniel (cannot be done by agent)
- [ ] Commit pipeline repo (manifest + artifacts)
- [ ] Commit app repo (ONLY the 3 changed files — unrelated load-test work is uncommitted in that tree)
- [ ] Run `test_all_lessons_routable` in a credentialed env / live QA (confirms I_B_05 router catalog)

## Flagged, not fixed (approved to defer)
- [ ] I_B_04 title/keywords mismatch (Area I.B labeling) — separate look
- [ ] Promote `derive_curriculum_key.py` to the real generator (durable anti-stranding fix)
