---
title: "Curriculum Quiz Pipeline — Get Back On Track (START HERE)"
type: reference
date: 2026-06-16
audience: "Ingestion Pipeline team + any engineer touching the quiz pipeline. Verified live against aviationchat-database on 2026-06-16."
owner_split: "tooling/layout/diagnosis = Woz (app side). Quiz/RKP/lesson CONTENT + which citations are correct = Daniel (CFI) and the ingestion team."
companion: "bridge_key_guide.md (RAG/metadata) · quiz_authoring_guide.md (quiz quality) · rkp_creation_guide.md (RKP mechanics) — all in this folder."
---

# Curriculum Quiz Pipeline — Get Back On Track

> **Read this first, then the files in §6.** Everything below was *measured*, not assumed: a dry-run
> of the real ingest schema over all 48 bank files, plus a live read of `quiz_banks` in
> `aviationchat-database` on 2026-06-16. Don't re-derive it — act on it.

> ### The docs in this folder (the whole set — no contradictions)
> This is the **front door** for the quiz thread. The four docs here are now a coherent set; the team is
> blocked until Daniel, Woz, and the team agree on it:
> - **`get_back_on_track.md`** (this doc) — what's broken in the quiz pipeline, why, and the ordered fix.
> - **`bridge_key_guide.md`** — the *other* thread: DB1→DB2 bridge keys / metadata (Area IX worst). Root
>   cause + the standing contract + how to prove it. Anything `reg_keys`/`doc_keys` lives there.
> - **`quiz_authoring_guide.md`** — the quiz **quality** bar (SJT design, four perspectives, the
>   explanation/citation standard). **Corrected:** the SJT answer is **not** always "D" — see its §3.
> - **`rkp_creation_guide.md`** — RKP manifest mechanics + schema.

> ### ⚠️ Update (2026-06-16, measured against BOTH repos + Daniel's decisions locked)
> Three measured corrections that change the *order of attack* and shrink the content work, plus the
> decisions Daniel signed off on. Full task breakdown:
> `_artifacts/2026-06-16_quiz-and-bridge-key-pipeline-fix/implementation_plan.md`.
>
> 1. **The citations already exist — this is verify-and-sync, not author-from-scratch.** The "12 failing
>    banks" were measured on the **app repo** copy (`AGY_AVIATIONCHAT/docs/specialist_lesson/quiz_banks/`),
>    which has `null` citations. **This pipeline repo's copy** (`curriculum_components/quiz_banks/`) has a
>    citation on **every question of all 48 files — zero nulls.** Verified on `IX_B_01`: six `null`s in the
>    app copy, all six already filled here. So the fix is: Daniel **verifies** the pipeline citations are
>    in-scope → sync **pipeline → app** → re-ingest. (Three to eyeball per `quiz_authoring_guide.md` §5.4:
>    `VII_A_01 Q001` & `VII_D_01 Q001` cite `14 CFR 23.2150` (Part 23 cert, not an operating rule);
>    `IX_C_01 Q004` cites `AC 120-111` (air-carrier upset training); `IX_C_01 Q003` cites `14 CFR 91.411`
>    (IFR altimeter tests).)
> 2. **Canonical source = THIS pipeline repo, kept separate from the app.** Multiple app branches all pull
>    from this documentation, so this repo is the single upstream. Sync is always **pipeline → app**, never
>    reverse. Keep the instruction docs current with every finding as we go.
> 3. **Thread 2's "highest-value fix" is already in the code — but wired to nothing.** `src/utils/schema.py`
>    is already hardened; the real bug is that `src/gcp/reimport_with_metadata.py` bypasses it (see
>    `bridge_key_guide.md` v2.8 banner).
>
> **Locked decisions (Daniel, 2026-06-16):** (Q4) **delete** `upload_quiz_banks.py` and any other broken
> pre-scope artifacts — don't neuter-and-keep. (Q2) `I_H_04` is **not special** — remap its perspectives
> like any other bank AND author a canonical copy back into this pipeline repo so it stops drifting.
> (Q3) `I_F_01`'s illegal 5th option — fix it the **best** way (drop the weakest distractor, or split into
> two questions) in the canonical copy, then sync. (Q5/Q6) Thread 2 → top industry standard, no shortcuts.

---

## 1. TL;DR (the situation in six lines)

1. There are **two** quiz-ingest scripts pointing at the **same** Firestore DB. One is correct; one is wrong and is the source of the "everything's broken" confusion.
2. The **wrong** tool (`Ingestion_pipeline_AvCh/src/gcp/upload_quiz_banks.py`) has an over-strict, *positional* SJT validator **and** writes to the wrong Firestore layout. Its "16 uploaded / 31 rejected" run was **inert** — the app never reads what it writes.
3. The **right** tool (`scripts/ingest_quiz_banks.py`, app repo) validates with the real Pydantic schema and writes the layout the app actually reads.
4. **All 34 Area I lessons are LIVE and servable today.** Area I was never the problem.
5. **14 lessons are dark** (app serves nothing): Areas III, VI, VII, IX, XI + `I_H_04`. 2 are ready to ingest; 12 fail the real schema and need a content fix first.
6. **Do NOT** patch the wrong tool, and **do NOT** rewrite Area I to force "SJT answer = D." Fix the *real* broken set and ingest with the *right* tool.

---

## 2. Live evidence (measured 2026-06-16, `aviationchat-database`)

**Dry-run of the REAL schema** (`python -m scripts.ingest_quiz_banks --all --dry-run`, with
`PYTHONIOENCODING=utf-8`): **280 questions validated across 48 files; 35 files pass, 13 fail.**

**Live `quiz_banks` audit** (per-lesson subcollection the app reads):

- **Servable now (populated subcollection): 34 lessons — every Area I bank `A_01`–`H_03`.**
- **Dark (empty subcollection — app serves nothing): 14 lessons.**
- **All 48 parent docs carry a stray `questions[]` array field** = residue of the wrong tool's writes (harmless, ignored by the app, but clutter).

### The dark 14, split by cause

| Lesson | Why dark | Fix needed before ingest |
|---|---|---|
| `III_A_02`, `XI_A_01` | valid, just never ingested | **none** — ingest as-is |
| `III_A_01`, `III_B_01`, `VI_B_01`, `VI_B_02`, `VI_B_03`, `VII_A_01`, `VII_D_01`, `IX_B_01`, `IX_C_01`, `XI_A_02`, `XI_A_03` | **null `far_reference`** on one or more questions (schema requires a string) | add the correct FAA citation (CFI owns which) |
| `I_H_04` | non-canonical `perspective` values (`physiological`, `decision-making`, `risk-management`) | map to the 4 canonical: `legal` / `safety` / `application` / `risk_management` |

### One drifted file (served, but disk is broken)

- `I_F_01` — **served** (8 questions live in Firestore) but its **disk JSON drifted** to a question
  with **5 options** (schema max is 4). Disk ≠ DB. Reconcile before any re-ingest of that file.

> Note: Area IX (`IX_B_01`, `IX_C_01`) is **double-broken** — dark quizzes **and** empty bridge keys
> (see §7). Fix both together for Area IX.

---

## 3. Root cause — two ingest tools, one wrong

The app **reads** quiz questions from `quiz_banks/{lesson_id}/questions/{question_id}` — a per-question
**subcollection** with rotation fields (`backend/services/quiz_bank_service.py:76`).

| | RIGHT tool — `scripts/ingest_quiz_banks.py` (app) | WRONG tool — `src/gcp/upload_quiz_banks.py` (pipeline) |
|---|---|---|
| Validates with | the real Pydantic `QuizBankRecord` (`backend/schemas/quiz.py`) | a hand-rolled checker with a **positional** SJT rule (`correct_answer == "D"`, strict 2/2/2/2) |
| Writes | `quiz_banks/{lesson}/questions/{q}` **(what the app reads)** + `seen_by` rotation | `quiz_banks/{lesson}` as **one parent doc** with a `questions[]` field **(app never reads this)** |
| Result | the 34 Area I subcollections that are live today | 48 inert parent-doc blobs; the "31 rejected" noise |

The pipeline tool's positional rule is also pedagogically wrong: most of Area I's SJTs are
**legal-reasoning** SJTs (correct answer is the defensible synthesis — **verified `B` in the
overwhelming majority** of the live bank), not the **go/no-go ADM** archetype the "answer = D, never
C = cancel" doctrine was written for (only `A_01`–`A_03` use D). The real schema correctly does **not**
enforce position — so all 34 Area I banks pass it. The right move is to **retire the wrong tool, not
patch its validator.** (The two SJT archetypes are now documented in `quiz_authoring_guide.md` §3.)

---

## 4. The plan to get back on track (ordered)

1. **Delete `upload_quiz_banks.py`** *(decision locked 2026-06-16 — delete, not neuter).* The app already
   has the correct tool; two tools writing one collection is the root of the mess, and Daniel's standing
   rule is to delete broken pre-scope artifacts outright rather than keep a half-fixed path around.
2. **Fix the Windows crash in `scripts/ingest_quiz_banks.py`.** It prints a `→` (U+2192) that crashes
   on the cp1252 console mid-run. Add `sys.stdout.reconfigure(encoding="utf-8")` at the top (the
   pipeline script already does this), or replace the arrow with `->`. Until then, `--all` only
   survives with `PYTHONIOENCODING=utf-8` set.
3. **Fix the 12 schema-failing banks (CONTENT — CFI/team own this):**
   - Null `far_reference` (11 files): **the pipeline copies already carry a citation on every question
     (zero nulls).** So this is **verify-and-sync, not author:** Daniel confirms the pipeline citations are
     in-scope (3 flagged in the Update banner above), then sync **pipeline → app**. **Never fabricate** —
     if a flagged citation is wrong, get the right reg from Daniel (constitution: never invent citations).
   - `I_H_04` *(decision locked)*: remap the 5 non-canonical perspectives to the 4 allowed values **and**
     author a canonical copy into this pipeline repo (it's currently app-only) so it stops drifting.
   - `I_F_01` *(decision locked)*: fix the illegal 5th option the **best** way — drop the weakest distractor
     if the five collapse cleanly to four, or split into two questions if it tests two facts — in the
     canonical (pipeline) copy, then sync. (`I_F_01` carries the 5th option in **both** copies' disk JSON.)
4. **Reconcile drift** *(canonical source decided: this pipeline repo; sync pipeline → app):* (a) `I_F_01`
   disk vs DB; (b) the **pipeline repo** `curriculum_components/quiz_banks/` (48 banks, all citations
   filled) is canonical vs the **app repo** `docs/specialist_lesson/quiz_banks/` (48 — app has `I_H_04`,
   pipeline doesn't, and the app has the `null`-citation drift). Sync the pipeline copies into the app's
   ingest input dir. Keep this repo as the single upstream all app branches pull from.
5. **Re-ingest with the right tool:** `python -m scripts.ingest_quiz_banks --all`. Idempotent (keyed by
   question id). The 14 dark lessons light up; Area I refreshes harmlessly.
6. **Verify:** take a quiz for a previously-dark lesson (e.g. `XI_A_01`) in the running app, end-to-end.
7. **(Optional housekeeping)** clear the 48 stray parent-doc `questions[]` fields the wrong tool left.

---

## 5. What NOT to do

- ❌ **Don't re-run `upload_quiz_banks.py`** — wrong layout, inert writes.
- ❌ **Don't rewrite Area I banks to force "SJT correct = D."** That was the wrong tool's positional
  rule; the real schema doesn't require it and Area I already serves correctly.
- ❌ **Don't fabricate `far_reference` citations** to make the validator pass — get the correct reg
  from the CFI.
- ⏸️ **Deferred quality (NOT blocking "make it work"):** some Area I SJTs are missing a few
  `hazardous_attitude` tags / aren't 2/2/2/2. The real schema tolerates this and they serve fine; it's
  post-grading-feedback polish, not a fix. The quality bar (tags, distribution, SJT structure) lives in
  `quiz_authoring_guide.md` (§1, §3.3, §9).

---

## 6. Files to reference (the map)

**The right tooling + contract (app repo):**
- `scripts/ingest_quiz_banks.py` — the canonical ingest tool (writes the `…/questions/{q}` subcollection).
- `backend/schemas/quiz.py` — **the source of truth for valid quiz JSON** (`QuizBankRecord`,
  `QuizBankQuestion`, `QuizOption`; `correct_answer` → `correct` normalization at `:131`).
- `backend/services/quiz_bank_service.py` — the app's read path (`_fetch_all_questions`, `:76`).
- `backend/routers/quiz.py` — quiz delivery + scoring (options served in stored order; answer key sanitized).

**The wrong tool (retire):**
- `Ingestion_pipeline_AvCh/src/gcp/upload_quiz_banks.py`.

**The bank JSON sources (reconcile — they drifted):**
- app: `docs/specialist_lesson/quiz_banks/*.json` (48 banks)
- pipeline: `Ingestion_pipeline_AvCh/curriculum_components/quiz_banks/*.json` (48 banks)

**Authoring guides (this folder — ingestion team owns content):**
- `quiz_authoring_guide.md` (quiz quality bar), `rkp_creation_guide.md` (RKP mechanics),
  `bridge_key_guide.md` (RAG / bridge keys).

---

## 7. Companion thread — bridge keys / metadata (separate, already documented)

Distinct from the quiz pipeline: the per-lesson DB1 `structData.reg_keys`/`doc_keys` (the "metadata")
are empty for a set of lessons (Area IX worst). That work is already specced — do not re-investigate.
The full spec, the standing contract (§0), the root cause, the document-level keying rules, and the
proof procedure all live in **`bridge_key_guide.md`** (same folder).

**Overlap:** Area IX (`IX_B_01`, `IX_C_01`) is broken on **both** fronts — dark quizzes (null
`far_reference`) and empty bridge keys. Fix Area IX in one pass across both threads.
