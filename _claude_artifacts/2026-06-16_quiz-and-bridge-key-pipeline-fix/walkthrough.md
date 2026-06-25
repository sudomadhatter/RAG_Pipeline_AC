---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — Plan + Decision Lock + Doc Reconciliation (no code yet)"
  type: walkthrough
  date: 2026-06-16
---

# Walkthrough — Planning & Doc Reconciliation Pass

> Scope of THIS session: research → implementation plan → lock Daniel's 6 decisions → refresh the
> instruction docs with measured findings. **No code, tooling, schema, or quiz-content file was touched.**
> The code build (Threads 1 & 2) is still gated on Daniel saying **"approved"**.

## What I did, step by step

1. **Read the four instruction docs end-to-end** in the prescribed order (get_back_on_track →
   bridge_key_guide → quiz_authoring_guide → rkp_creation_guide).
2. **Verified every load-bearing claim against the actual code in both repos.** The app repo
   (`AGY_AVIATIONCHAT`) is on this machine, so I could check the cross-repo claims directly rather than
   trust the docs. This is where the docs turned out to be partly stale.
3. **Wrote the implementation plan** (`implementation_plan.md`) structured as two threads with a combined
   execution order, a files-touched map, a verification plan, and the open questions.
4. **Presented inline and stopped for the gate.** Daniel answered all six questions and added a standing
   instruction to keep the docs current.
5. **Locked the six decisions into the plan** (§9 now reads "RESOLVED") and updated the status banner.
6. **Refreshed the four instruction docs** with the measured corrections + locked decisions (details
   below), matching each doc's existing dated-correction-banner style.
7. **Saved two durable memories** (pipeline-is-canonical/doc-upkeep; delete-broken-pre-scope-artifacts).

## What fought back (and the correction it produced)

The docs read as authoritative, but four things did not survive contact with the code:

- **The "12 failing banks" needed measuring, not believing.** The dry-run that found them ran against the
  **app repo** copy. I grepped both repos: the app copy has 11 banks with `null` citations; **this pipeline
  repo's copy has zero nulls across all 47 files.** I confirmed on `IX_B_01` (six nulls in app, all six
  filled here). That flips the content task from "author 33 citations" to "verify + sync."
- **Thread 2's "highest-value fix" was already done.** `src/utils/schema.py` already enforces
  `doc_keys min_length=1` + strip-`N/A`. The real, still-open bug is that `src/gcp/reimport_with_metadata.py`
  imports nothing from `utils.schema` and builds the Vertex payload by hand — the guard never runs on the
  path that writes DB1. I confirmed the import list directly (it pulls `os/json/re/sys`, `storage`,
  `discoveryengine`, `pathlib` — and nothing from the schema).
- **"Extractor is an LLM, not a regex" is half true.** The production import tool uses a regex over the
  master-doc `Bridge Keys` block. There are two extractors; the one that writes DB1 is the regex.
- **`reimport_with_metadata.py` can't run on this machine** — hardcoded `c:\Sudo_Hatter_Command\...` repo root and
  SA path, reading a `pipeline/curriculum/new/` dir that doesn't exist here.

It went clean otherwise — no dead ends, just measurement correcting documentation.

## Files changed this session

| File | Change |
|---|---|
| `_claude_artifacts/2026-06-16_.../implementation_plan.md` | Created; §9 decisions locked; status banner updated |
| `_claude_artifacts/2026-06-16_.../walkthrough.md` | This file |
| `_claude_artifacts/2026-06-16_.../task-list.md` | Final task-list snapshot |
| `_01_My/instruction_docs/bridge_key_guide.md` | v2.8 correction banner; §3 root-cause rewritten (schema already hard, guard bypassed, regex vs LLM); §3.3 vocab-enforcement note; §6 step 1 reframed; §7 quick-ref updated; stale module path fixed |
| `_01_My/instruction_docs/get_back_on_track.md` | Update banner (citations already exist, canonical=pipeline, schema already hard); §4 steps 1/3/4 reframed to verify-and-sync + locked decisions |
| `_01_My/instruction_docs/quiz_authoring_guide.md` | Dated note: canonical bank location + verify-not-author + scope-trap reminder |
| `_01_My/instruction_docs/rkp_creation_guide.md` | Dated note: bridge keys now enforced at ingest (+ coming DB2-vocab membership check) |
| `~/.claude/.../memory/*` | Two memories + MEMORY.md index (outside the repo) |

No test output to paste — no code ran this session by design (plan-gate).

## Your Actions

1. **Verify the three flagged citations** (CFI call) so Thread 1 can sync + re-ingest:
   - `VII_A_01 Q001` & `VII_D_01 Q001` → `14 CFR 23.2150` (Part 23 cert standard — right for an operating
     question?)
   - `IX_C_01 Q004` → `AC 120-111` (air-carrier upset training); `IX_C_01 Q003` → `14 CFR 91.411` (IFR
     altimeter tests)
2. **Say "approved"** to start the code build (retire the wrong tool, wire the Thread-2 guard, fix paths,
   sync banks, build the gate + live probe, fix Area IX, prove with live hit counts). Nothing in code moves
   until then.
3. **Commit this planning + doc-reconciliation pass** (docs + artifacts only — no code):

```bash
git add _01_My/instruction_docs/ _claude_artifacts/2026-06-16_quiz-and-bridge-key-pipeline-fix/
git commit -m "Reconcile curriculum-fix instruction docs with measured findings; lock decisions; add implementation plan

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
