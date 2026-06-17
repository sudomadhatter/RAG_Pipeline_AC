---
IsArtifact: true
ArtifactMetadata:
  title: "Curriculum Pipeline Fix — Quizzes (Thread 1) + Bridge Keys (Thread 2)"
  type: implementation_plan
  date: 2026-06-16
---

# Implementation Plan — Curriculum Pipeline Fix (Two Threads)

> **STATUS: Decisions locked (§9, 2026-06-16). Instruction docs updated. Code build AWAITING "approved".**
> Daniel answered all six questions; §9 now records the locked decisions and they drive the task gates.
> The instruction docs have been refreshed with these findings per his standing directive. **No code,
> tooling, schema, or quiz-content file will be touched until Daniel says "approved".**
> Everything below was *measured* against both repos on this machine on 2026-06-16, not taken on faith
> from the instruction docs. Where the measurement corrects a doc, it is flagged **[CORRECTION]**.

Sources read end-to-end first: [get_back_on_track.md](_01_My/instruction_docs/get_back_on_track.md),
[bridge_key_guide.md](_01_My/instruction_docs/bridge_key_guide.md),
[quiz_authoring_guide.md](_01_My/instruction_docs/quiz_authoring_guide.md),
[rkp_creation_guide.md](_01_My/instruction_docs/rkp_creation_guide.md).

---

## 1. Goal & Definition of Done

Two independent threads, one of which (Area IX) overlaps both. Done means:

- **Thread 1 — Quizzes:** all **47/48** lessons serve **8 valid questions** from the per-lesson
  `quiz_banks/{id}/questions` subcollection the app actually reads. Proven by taking a quiz on a
  previously-dark lesson in the running app.
- **Thread 2 — Bridge keys:** **every** lesson carries non-empty, **document-level** `doc_keys` in DB1
  `structData` that return **real DB2 hits** — `count ≥ 1`, top score ≥ floor, owning-area match —
  proven **live with the numbers shown**. "No error" is not proof.

---

## 2. What I measured — and where it corrects the docs

The instruction docs are directionally right, but four measured facts change the *order of attack* and
shrink the content work substantially. These are the Woz findings Daniel should see before approving.

### [CORRECTION 2a] The pipeline repo is AHEAD of the app repo — the citations already exist
The docs say "12 banks fail; the CFI must add the correct `far_reference`." Measured reality:

- The **app repo** ingest copy (`AGY_AVIATIONCHAT/_docs/specialist_lesson/quiz_banks/`, 48 files) is what
  the dry-run validated. It has **11 banks with `null` `far_reference`** on one or more questions —
  the real failures.
- **This pipeline repo** (`curriculum_components/quiz_banks/`, 47 files) has **zero** null/empty/`N/A`
  citations across **all 47 files, every question**. I verified `IX_B_01` directly: in the app copy
  six questions are `null`; in the pipeline copy all six already carry a citation.

So for the 11 null banks the fix is **not authoring 33 new citations — it is verifying the citations
the pipeline repo already holds and syncing pipeline → app, then re-ingesting.** Daniel's job collapses
from "write" to "verify/approve," which is the correct CFI gate anyway.

### [CORRECTION 2b] The Thread-2 schema guard is already in the code — but it is wired to nothing
[bridge_key_guide.md](_01_My/instruction_docs/bridge_key_guide.md) calls hardening
[src/utils/schema.py](src/utils/schema.py) "the single highest-value fix." Measured: it is **already
done** — `doc_keys: List[str] = Field(min_length=1)` plus a strip-`N/A` validator, a non-empty
validator, and a chapter-level warning validator (schema.py:33, 36-68). The post-generation check in
[src/utils/generate_metadata.py](src/utils/generate_metadata.py:82) exists too.

**But the production re-import tool [src/gcp/reimport_with_metadata.py](src/gcp/reimport_with_metadata.py)
imports nothing from `utils.schema`.** It builds the JSONL `structData` dicts by hand
(reimport_with_metadata.py:155-170) and ships them straight to Vertex. **The guard never runs on the
path that actually writes DB1.** An empty `doc_keys` still ships silently today — the bug the guide
believes is fixed is *not* fixed on the real path. **This is the true open work for Thread 2**, and it
is more important than re-hardening a schema that's already hard.

### [CORRECTION 2c] The "extractor is an LLM, not a regex" claim is only half true
The guide's v2 root cause says markdown formatting is "not the lever" because an LLM
(`generate_metadata.py`) does the extraction. Measured: the **import tool that writes DB1**
(`reimport_with_metadata.py:77-91`) extracts `reg_keys`/`doc_keys` with a **regex** over the master
doc's `Bridge Keys` block — `Regs:` / `Docs:` lines. There are **two** extractors and the production
one **is** regex-based. For that path, clean markdown *is* a lever. We must pick one source of truth
(decision in §9).

### [CORRECTION 2d] `reimport_with_metadata.py` cannot run on this machine as-is
It hardcodes a different repo root and a service-account path from another machine
(`c:\AGY-Projects\ingestion-Pipeline-AC\...`, reimport_with_metadata.py:10, 20) and reads
`pipeline/curriculum/new/Area *.md`, which does not exist here (our modules live in
[curriculum_components/curriculum_modules/](curriculum_components/curriculum_modules/)). This violates
the repo's own `credential-resolution.md` and `code-standards.md` (use `Path(__file__).parent`). It
must be path-fixed before any Area IX regenerate/re-import can happen.

### Confirmed-as-written (no correction)
- The wrong quiz tool [src/gcp/upload_quiz_banks.py](src/gcp/upload_quiz_banks.py) does write one parent
  doc with a `questions[]` field (line 113), has the positional `SJT correct_answer == "D"` validator
  (lines 50-51), **and** now points at `specialist_curriculum/quiz_banks` (line 16) — a directory git
  shows as deleted. It is doubly dead. **Retire it.**
- The app's real schema [`backend/schemas/quiz.py`](../AGY_AVIATIONCHAT/backend/schemas/quiz.py)
  confirms the gates: `far_reference: str` (required → `null` fails, `""` passes), `options` min 3 /
  **max 4** (so `I_F_01`'s 5th option fails), `perspective` is a 4-value `Literal` (so `I_H_04`'s
  `physiological`/`decision-making`/`risk-management` fail), and `correct_answer` is normalized with
  **no positional D rule**. All 34 Area I banks pass it.
- `I_F_01` carries a 5th (`E`) option in **both** repos' disk JSON — a sync won't fix it; the content
  must be edited.
- `I_H_04` exists **only** in the app repo (pipeline has no source for it).
- The IX RKP manifests are fine — [PPL_PA_IX_B_01_rkp.json](curriculum_components/rkp_manifests/PPL_PA_IX_B_01_rkp.json)
  carries `bridge_keys` on every RKP. The empty layer was DB1 `structData`, exactly as the guide says.

---

## 3. Thread 1 — Quizzes (ordered)

Owner split: pipeline/tooling/sync = us; *which citation is correct* = Daniel (CFI).

| # | Task | Files | Gate |
|---|---|---|---|
| 1.1 | **Retire the wrong tool.** Delete [src/gcp/upload_quiz_banks.py](src/gcp/upload_quiz_banks.py) (constitution requires asking before deleting — see §9 Q4). | `src/gcp/upload_quiz_banks.py` | Daniel OKs delete-vs-neuter |
| 1.2 | **Fix the Windows crash in the right tool.** Add `sys.stdout.reconfigure(encoding="utf-8")` (or replace `→` with `->`) so `--all` survives the cp1252 console without `PYTHONIOENCODING`. | `AGY_AVIATIONCHAT/scripts/ingest_quiz_banks.py` | dry-run runs clean |
| 1.3 | **Decide canonical source & set the sync direction.** Evidence says pipeline repo is canonical and ahead. Confirm, then sync the 11 drifted banks pipeline → app ingest dir. | both `quiz_banks/` dirs | §9 Q1 |
| 1.4 | **CFI citation verification (Daniel).** The 11 banks' citations already exist in the pipeline copy — Daniel verifies they're correct & in-scope. Concrete table in §9. **No fabrication.** | the 11 pipeline bank JSONs | Daniel sign-off per bank |
| 1.5 | **`I_H_04` perspective remap (app-only).** Map the 5 non-canonical `perspective` values → the 4 canonical, and restore 2/2/2/2. No pipeline source exists; decide whether to also author it into the canonical pipeline repo. | `AGY_AVIATIONCHAT/_docs/.../PPL_PA_I_H_04_quiz.json` (+ optional pipeline copy) | §9 Q2 |
| 1.6 | **`I_F_01` 5th-option fix.** Drop option `E` (or split into two questions) so it is ≤4, in whichever copy is canonical. It is served fine today; only a re-ingest would break it. | `PPL_PA_I_F_01_quiz.json` (both copies) | §9 Q3 |
| 1.7 | **Re-ingest with the right tool**, idempotent (keyed by question id): `python -m scripts.ingest_quiz_banks --all`. The 14 dark lessons light up; Area I refreshes harmlessly. | app repo | dry-run = 0 fails first |
| 1.8 | **Verify live.** Take a quiz on a previously-dark lesson (`XI_A_01`, then an Area IX one) in the running app, end-to-end; confirm 8 questions served. | running app | screenshot/output in walkthrough |
| 1.9 | *(Housekeeping, optional)* clear the 48 stray parent-doc `questions[]` fields the wrong tool left. | Firestore | non-blocking |

---

## 4. Thread 2 — Bridge keys (ordered)

The schema is already hard (§2b); the work is to make the guard *actually protect the write path*,
build the proofs the contract demands, then fix Area IX.

| # | Task | Files | Gate |
|---|---|---|---|
| 2.1 | **Wire the guard into the production path.** Make [src/gcp/reimport_with_metadata.py](src/gcp/reimport_with_metadata.py) validate every entry through `CurriculumLessonSchema`/`CurriculumStructData` before writing the JSONL, so an empty `doc_keys` fails loud at ingest instead of shipping silently. | `src/gcp/reimport_with_metadata.py`, `src/utils/schema.py` | unit test: empty `doc_keys` raises |
| 2.2 | **Fix the stale/hardcoded paths.** Replace the `c:\AGY-Projects\...` root and SA path with `Path(__file__).parent` + the `GOOGLE_APPLICATION_CREDENTIALS` resolution pattern from `credential-resolution.md`; point the module reader at `curriculum_components/curriculum_modules/`. | `src/gcp/reimport_with_metadata.py` | runs on this machine |
| 2.3 | **Resolve the extractor contradiction (§2c).** Pick ONE source of truth — route the import through the LLM `generate_metadata.py`, **or** keep the regex but pass output through the schema guard and treat the master-doc `Bridge Keys` block as the contract. | `reimport_with_metadata.py`, `generate_metadata.py` | §9 Q5 |
| 2.4 | **Build the offline schema gate (CI, permanent).** Iterate all 184 DB1 docs and assert non-empty, well-formed, document-level `doc_keys`. This is the guard that stops the next silent batch. | new `src/tests/` (or `scripts/`) gate | green over 184 |
| 2.5 | **Build the live DB1→DB2 round-trip probe.** Assert `len(db2_hits) ≥ 1` **and** top score ≥ floor **and** returned doc maps back to the queried Area (no IX→VII cross-wire). The `bridge-key-verification` skill covers this. | new probe script | numbers captured |
| 2.6 | **Fix Area IX content + regenerate.** Ensure the master module [Area 9 Tasks B,C PPL.md](curriculum_components/curriculum_modules/Area%209%20Tasks%20B%2CC%20PPL.md) has a clean, populated `Bridge Keys` block (no "N/A"), regenerate metadata for the IX split lessons, confirm non-empty document-level keys. | Area 9 module, generated JSON | keys non-empty |
| 2.7 | **Re-import to DB1** via the now-guarded `reimport_with_metadata.py` with **FULL** reconciliation; confirm the 12 IX docs carry non-empty keys and the doc count stays **184**. | `reimport_with_metadata.py` | count == 184 |
| 2.8 | **Prove it (§2.4 + §2.5 + golden set).** Freeze 2-3 hand-verified lessons as canaries; spot-check the other 5 content Areas didn't regress. | probes | hit counts shown |

---

## 5. Area IX — fix once, across both threads

`IX_B_01` and `IX_C_01` are the overlap: dark quizzes (Thread 1) **and** the empty-`structData` history
(Thread 2). Sequence them together — sync+verify the IX quiz citations (1.3-1.4), then run the IX
metadata regenerate/re-import (2.6-2.7), then prove both with one pass: a live quiz on `IX_B_01` and a
live DB1→DB2 round-trip on the IX keys.

---

## 6. Combined execution order

1. **Thread 2 plumbing first** (2.1 → 2.2 → 2.3): wire the guard, fix paths, settle the extractor. This
   makes every later re-import safe and is pure engineering (no CFI gate).
2. **Thread 1 tooling** (1.1 → 1.2): retire wrong tool, fix the Windows crash.
3. **Canonical-source + citation gate** (1.3 → 1.4, needs Daniel): sync direction + CFI verification.
4. **Area I specials** (1.5 → 1.6): `I_H_04` remap, `I_F_01` option fix.
5. **Build proofs** (2.4 → 2.5): offline gate + live probe.
6. **Area IX combined** (2.6 → 2.7, then 1.7 re-ingest): regenerate/re-import keys, re-ingest quizzes.
7. **Verify everything live** (1.8 + 2.8): quiz on a dark lesson; DB1→DB2 hit counts; golden set.

Each numbered task still gets its own touch-point; this is the spine, not a license to skip per-step
review.

---

## 7. Files touched (every one, with links)

**This pipeline repo (ours):**
- [src/gcp/upload_quiz_banks.py](src/gcp/upload_quiz_banks.py) — **retire** (1.1)
- [src/gcp/reimport_with_metadata.py](src/gcp/reimport_with_metadata.py) — guard + path fix + extractor decision (2.1-2.3, 2.7)
- [src/utils/schema.py](src/utils/schema.py) — read/import only; possibly add DB2-vocabulary membership check (see §9 Q6)
- [src/utils/generate_metadata.py](src/utils/generate_metadata.py) — only if 2.3 routes through the LLM path
- the 11 drifted bank JSONs in [curriculum_components/quiz_banks/](curriculum_components/quiz_banks/) — CFI verify (1.4); `I_F_01` option fix (1.6)
- [curriculum_components/curriculum_modules/Area 9 Tasks B,C PPL.md](curriculum_components/curriculum_modules/Area%209%20Tasks%20B%2CC%20PPL.md) — clean Bridge Keys (2.6)
- new offline gate + live probe scripts/tests (2.4, 2.5)

**App repo (`AGY_AVIATIONCHAT`, cross-repo — separate commit):**
- `scripts/ingest_quiz_banks.py` — Windows-crash fix (1.2)
- `_docs/specialist_lesson/quiz_banks/` — receive the synced 11 banks (1.3); `I_H_04` remap (1.5); `I_F_01` option fix (1.6)

> **Cross-repo flag:** this work spans two git repos. The quiz *re-ingest* runs from the app repo; the
> bridge-key *re-import* runs from this pipeline repo. Two separate commits, two separate "Your Actions"
> blocks at the end.

---

## 8. Verification plan (evidence, not claims)

- **Quiz dry-run:** `python -m scripts.ingest_quiz_banks --all --dry-run` (with `PYTHONIOENCODING=utf-8`
  until 1.2 lands) must report **48/48 pass, 0 fail** before any real ingest.
- **Quiz live:** take `XI_A_01` and `IX_B_01` quizzes in the running app; confirm 8 questions each. Paste
  output into `walkthrough.md`.
- **Bridge offline gate:** run over all 184 DB1 docs; assert every `doc_keys` non-empty + document-level.
- **Bridge live round-trip:** for each fixed IX key, fire the real DB1→DB2 path; record `count`, top
  score, and owning-area match. Numbers go in the walkthrough — **if the hit counts aren't shown, it
  isn't done.**
- **Golden set:** 2-3 frozen lessons → expected FAA reference, as canaries.

---

## 9. Decisions — RESOLVED by Daniel 2026-06-16

All six questions answered. Locked decisions below now drive the task gates above.

- **Q1 — Canonical source → PIPELINE REPO, kept separate from the app.** This repo is the single
  upstream; multiple app branches all pull from this documentation. Sync direction is **pipeline → app**.
  Keep ingestion/curriculum upkeep decoupled from app development, and **keep the instruction docs current
  with every finding/fix** as we go until the pipeline is streamlined.
- **Q2 — `I_H_04` is not special → fix it like everything else.** Remap its perspectives to the 4
  canonical values **and** author a canonical copy back into the pipeline repo so it stops being app-only
  and stops drifting.
- **Q3 — `I_F_01` → fix it the best way so we don't have recurring issues.** Evaluate the question;
  preserve the tested fact; produce a schema-valid ≤4-option result — drop the weakest distractor if the
  five collapse cleanly to four, or split into two questions if it genuinely tests two facts. Fix it in
  the canonical (pipeline) copy, then sync.
- **Q4 — Wrong tool → DELETE.** Delete `upload_quiz_banks.py` outright (and any other clearly
  pre-scope/broken artifacts found), don't neuter-and-keep. "We lost days of work due to this stuff."
- **Q5 — Extractor → top industry standard, no shortcuts.** Unify on a **single** extractor: the LLM
  path (`generate_metadata.py`) feeding the **hardened schema guard**, with the divergent regex extractor
  in `reimport_with_metadata.py` retired. One source of truth, validated, fail-loud, tested.
- **Q6 — Vocabulary enforcement → YES, the best, no shortcuts.** Add a hard membership check: a `doc_key`
  not in DB2's `document_tags` vocabulary fails the gate (closes the "passes `min_length` but hits
  nothing in DB2" gap).

**Citation verification (Thread 1) — still owed by Daniel before content sync.** The pipeline repo
already carries a citation on every question that is `null` in the app copy, so this is *verify*, not
*author*. Three to look at per the guide's scope warning
([quiz_authoring_guide.md §5.4](_01_My/instruction_docs/quiz_authoring_guide.md)):
`VII_A_01 Q001` & `VII_D_01 Q001` cite **`14 CFR 23.2150`** (Part 23 aircraft-certification, not an
operating rule); `IX_C_01 Q004` cites **`AC 120-111`** (air-carrier upset training) and `IX_C_01 Q003`
cites **`14 CFR 91.411`** (IFR altimeter tests). Everything else (the `91.3`/`91.103`/`91.113`/`91.126`/
`AC 61-67C` family) reads in-scope. These are content-gate items for task 1.4, not blockers for the
engineering tasks.

---

## 10. What NOT to do (hard rules, carried from the docs)

- ❌ Do **not** re-run `upload_quiz_banks.py` — wrong layout, inert writes.
- ❌ Do **not** rewrite Area I banks to force "SJT correct = D." The real schema has no positional rule;
  Area I serves correctly today. (The 13 non-Area-I SJTs that *do* answer "D", e.g. both `IX_B_01` SJTs,
  are a **deferred quality** item — they pass the schema and are out of scope here.)
- ❌ Do **not** fabricate or stretch a `far_reference` or a bridge key to pass a gate. A precise-but-wrong
  reg is worse than a missing one — bring it to Daniel.
- ⏸️ **Deferred (not this plan):** SJT-quality rewrites of the 13 non-Area-I banks, missing
  `hazardous_attitude` tags, 2/2/2/2 polish on Area I. They serve fine; that's post-grading polish.

---

## 11. Risks

- **Cross-repo drift recurs** if we sync once and don't fix the source-of-truth process. Q1/Q2 address it.
- **Re-import path is network-gated** (Vertex Discovery Engine); 2.7/2.8 need live credentials and a real
  DB1/DB2. The offline gate (2.4) de-risks the parts that don't need the network.
- **Idempotency:** quiz re-ingest is keyed by question id (safe); the DB1 re-import uses FULL
  reconciliation (idempotent) — confirm doc count stays 184 after.
