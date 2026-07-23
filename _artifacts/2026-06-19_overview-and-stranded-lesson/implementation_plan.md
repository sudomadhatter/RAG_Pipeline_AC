---
IsArtifact: true
ArtifactMetadata:
  title: Fix missing I_H_04 overview + stranded lesson I_B_05
  type: implementation_plan
  date: 2026-06-19
---

# Implementation Plan — Two QA bugs the app team caught

Two defects, both "the app surface is wrong because an authoring artifact is incomplete."
This plan spans **two repos** (this pipeline repo + the sibling `AGY_AVIATIONCHAT` app repo), which is
correct: the Curriculum Key is **artifact #7 in the lifecycle, owned by "Ingestion team / Woz"**
(`_docs/instruction_docs/curriculum_lifecycle.md` line 87) — it is our job to keep current, it just
physically lives in the app tree.

---

## Definition of done

1. **Bug 1** — `PPL_PA_I_H_04` carries a gold-standard `lesson_overview` (3–5k chars), grounded
   strictly in its three existing RKPs, placed in the same structural slot every sibling uses.
2. **Bug 2** — `PPL_PA_I_B_05` appears in `curriculum_key.json`, so `ALL_LESSON_IDS` goes 47 → 48 and
   the lesson becomes visible to the router, title resolver, prereq DAG, and Igor's checkride plan.
3. **The gap that hid Bug 2** — the activation test gets a **reverse-direction check** so a stranded
   manifest can never ship silently again.
4. Both pass their tests; deployment steps are handed to Daniel (I do not run `--execute` or deploy).

---

## Ground truth (verified, not assumed)

| Claim | Verified |
|---|---|
| I_H_04 overview is "empty" | **Worse — the `lesson_overview` key is entirely absent** from the JSON. The 3 RKPs are fully authored. |
| I_B_05 missing from the key | Confirmed — `grep 'I_B_05' curriculum_key.json` → nothing; I_B_01..04 present. |
| Roster is built from the key | `curriculum.py:68` — `ALL_LESSON_IDS` = every key entry with `status != "draft"`. Default is `"active"`. |
| Why 47 not 93 | The key has 93 entries; 45 are `draft` skeletons (Areas II/IV/V/VI/VII/VIII/IX/X/XII), excluded from the roster. |
| Blast radius | manifests (48) vs key diff: **I_B_05 is the ONLY stranded manifest.** 45 key entries are drafts with no manifest (expected). |

---

## Fix A — author I_H_04 `lesson_overview` (THIS repo)

**File:** `curriculum_components/rkp_manifests/PPL_PA_I_H_04_rkp.json`
**Change:** add a single top-level `"lesson_overview"` key after `required_knowledge_points` (the exact
slot I_B_05 uses at line 88), holding a ~3–5k-char ADM / PAVE & IMSAFE overview.

**Grounding rule (hard):** the prose is synthesized **only** from the three RKPs already in the file
(symptom→cause→correction; IMSAFE & the No-Go; aeromedical hazard→risk→mitigation) and the regs they
already cite (91.211, 61.53, Part 68, PHAK Ch 17, AIM 8-1-2). **No new citations** — constitution
hard-stop on fabricated references. Format follows the gold-standard I_B_05 overview (bolded
sub-headers, the DPE-trap framing).

**Prompt-architecture note:** lesson_overview authoring is covered by the `rkp-manifest-creation`
skill; I'll apply it rather than freelancing the structure.

---

## Fix B — un-strand I_B_05 + close the test gap (APP repo: `AGY_AVIATIONCHAT`)

**B1 — add the key entry.** `AGY_AVIATIONCHAT/backend/data/curriculum_key.json`, inserted after the
I_B_04 entry, matching the exact 7-field schema the file uses:

```json
{
  "lesson_id": "PPL_PA_I_B_05",
  "acs_task_reference": "Area I, Task B",
  "title": "Flying with Inoperative Equipment — 91.213(d) Flowchart",
  "acs_element_keys": ["PA.I.B.K3a", "PA.I.B.R1", "PA.I.B.S3"],
  "certificate": "PPL",
  "prerequisite_acs_nodes": ["PA.I.B.K1", "PA.I.B.K2"],
  "keywords": ["...4 lesson-derived keywords..."]
}
```

No `status` field → defaults to `"active"` → lands in `ALL_LESSON_IDS`. `acs_element_keys` are copied
verbatim from the manifest. **`prerequisite_acs_nodes` is the one judgment call — see Risk R1.**

**B2 — close the forward-only gap.** `backend/tests/data/test_curriculum_activation.py` currently only
asserts forward (every active lesson has a manifest). Add the **reverse** assertion (every manifest is
activated). Implementation detail to confirm first: I must read that test to see what it treats as the
"manifest" source of truth (Firestore query vs a local dir vs a fixture) and mirror that exact
mechanism — I won't invent a second source of truth.

---

## What I'm worried about

- **The prereq DAG is CFI truth, not mine.** `prerequisite_acs_nodes` for I_B_05 is a pedagogical
  claim about what a student must know first. I'm proposing `[PA.I.B.K1, PA.I.B.K2]` by mirroring
  I_B_04, but this is exactly the kind of call the ownership line reserves for Daniel (CFI owns truth).
  I want a yes/no on the proposed prereqs before I commit them.
- **A pre-existing labeling oddity, not part of these bugs.** In the key, I_B_04 is *titled* "Flying
  with Inoperative Equipment (91.213)" but its keywords are all about **Special Flight Permits** —
  while I_B_05's manifest is the real inoperative-equipment flowchart. I will NOT touch I_B_04, but
  flagging it: the Area I.B numbering may have a deeper title/scope mismatch worth a separate look.
- **Editing the JSON doesn't fix production by itself.** Bug 1's manifest must be re-ingested to
  Firestore (`upload_manifests.py --execute`) before students see the overview; Bug 2's key edit only
  takes effect when the backend reloads/redeploys. Both are gated, Daniel-run steps — I'll spell them
  out, but "files edited" ≠ "app fixed."
- **Two-repo session.** I'll be editing a second git repo. I'll keep each change surgical and give you
  separate commit commands per repo — no cross-repo commit.

## Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Wrong `prerequisite_acs_nodes` corrupts the DAG / trips `test_curriculum_acyclic.py` | **High** | Propose `[K1,K2]` (mirrors I_B_04), get Daniel's confirm, then run the acyclic test before declaring done. K1,K2→K3a/R1/S3 has no cycle. |
| R2 | Reverse-check test built on the wrong manifest source → false greens/reds | Med | Read `test_curriculum_activation.py` first; reuse its existing manifest source, don't introduce a new one. |
| R3 | I_H_04 overview drifts into unverified claims | Med | Synthesize only from the 3 in-file RKPs + their existing citations; zero new regs. |
| R4 | Files edited but not deployed → "fixed" but app still wrong | Med | Explicit "Your Actions": re-ingest manifest + redeploy/reload backend, with exact commands. |
| R5 | Other stranded lessons lurking | **Low/closed** | Diff already run: I_B_05 is the only one; the new reverse test will keep it that way. |

---

## Execution order

1. Fix A — author + insert I_H_04 `lesson_overview`; eyeball against I_B_05 for register/length.
2. Fix B1 — insert I_B_05 key entry (pending Daniel's prereq confirm).
3. Fix B2 — read the activation test, add the reverse assertion.
4. Run the app-repo curriculum tests (activation, acyclic, resolver) + paste output.
5. Write `walkthrough.md` + `task-list.md`; hand Daniel the deploy + commit commands.

## Verification plan

- App repo: `python -m pytest backend/tests/data/test_curriculum_activation.py backend/tests/services/evolution/test_curriculum_acyclic.py backend/tests/test_curriculum_resolver.py -q` — all green, and the new reverse assertion present.
- Pipeline repo: `python -m pytest src/tests/ -q` (schema gate still green after the manifest edit).
- Confirm `len(ALL_LESSON_IDS) == 48` and `"PPL_PA_I_B_05" in ALL_LESSON_IDS`.

## Out of scope (recommended follow-up, not now)

The durable fix for "a lesson can be stranded" is to stop hand-maintaining the key and **derive it from
the canonical roster** — there's already a `_test_scripts/derive_curriculum_key.py` +
`curriculum_key.derived.json` scaffold in the app repo. I recommend a separate session to promote that
to the real generator. Doing it now would be scope creep on a QA fix.

## Open questions for Daniel

1. Approve `prerequisite_acs_nodes: [PA.I.B.K1, PA.I.B.K2]` for I_B_05? (or give the correct set)
2. OK to leave the I_B_04 title/keywords mismatch untouched and just flag it?
3. Confirm I should edit the app repo directly (vs. handing you a patch to apply there).
