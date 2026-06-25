---
IsArtifact: true
ArtifactMetadata:
  title: "DEV STORY — Curriculum Pipeline Fix (Quizzes + Bridge Keys)"
  type: dev_story
  date: 2026-06-16
  version: "2.8"
status: "Ready for dev — Daniel's 6 decisions locked. Code build pending Daniel's 'approved'."
owner_split: "Engineering owns tooling/layout/schema/sync. Daniel (CFI) owns which citations are correct."
---

# DEV STORY — Curriculum Pipeline Fix

**Two independent work streams. Story A (Quizzes) and Story B (Bridge Keys) can be assigned to two
different developers. They overlap on Area IX only — sync there (see §6).** Everything in this story was
*measured* against both repos on a dev machine on 2026-06-16; the file:line references are real. Do not
re-derive — build from this.

---

## 1. Context — what's broken and why

The PPL curriculum is live and teaching, but two things shipped broken.

- **Quizzes:** 34 Area I lessons serve quizzes correctly. **14 lessons are dark** (the app serves no
  questions): Areas III, VI, VII, IX, XI + `I_H_04`. Root cause = a wrong ingest tool wrote a Firestore
  layout the app never reads, **plus** a set of bank files that fail the app's real schema (mostly a
  required citation field left `null`).
- **Bridge keys:** some lessons (Area IX worst) shipped with empty `doc_keys` in their DB1 `structData`,
  so the FAA-library verification hop returns nothing — silently. Answers can't be ground-truth-checked.

**Area IX (`IX_B_01`, `IX_C_01`) is broken on BOTH** — fix it once across both stories.

### Two databases (Vertex AI Search)
| Store | Name | Role |
|---|---|---|
| **DB1** | `aviation-curriculum-v2` | Teaching — the 184 micro-lessons |
| **DB2** | `aviation-library-v2` | Verification — the FAA PDFs (FAR/AIM, PHAK, AFH, ACs) |

A student question hits DB1; the matched lesson's **bridge keys** (`reg_keys` + `doc_keys`) search DB2 for
the authoritative FAA source. Empty bridge keys → the verification step returns nothing.

### Two repos (THIS is critical)
| Repo | Path | Role |
|---|---|---|
| **Pipeline** (this repo) | `Ingestion_pipeline_AvCh` | **CANONICAL** source: authoring, RKPs, quiz banks, DB1 import tooling, schema guards |
| **App** (consumer) | `AGY_AVIATIONCHAT` | Serves the app; has the real quiz schema + the real quiz-ingest tool; multiple branches |

**Decision (locked):** the **pipeline repo is canonical**. Multiple app branches all pull from it. **Sync
direction is always pipeline → app, never reverse.**

---

## 2. Locked decisions (Daniel, 2026-06-16) — do not relitigate

1. **Canonical source = pipeline repo, kept separate from the app.** Sync pipeline → app. Keep the
   instruction docs in `_01_My/instruction_docs/` current with findings as you go.
2. **`I_H_04` is not special** — remap its perspectives like any other bank **and** author a canonical copy
   back into the pipeline repo so it stops drifting (it's currently app-only).
3. **`I_F_01`** — fix the illegal 5th option the *best* way (drop the weakest distractor if the five
   collapse cleanly to four, or split into two questions if it genuinely tests two facts) in the canonical
   copy, then sync.
4. **Delete the wrong tool** (`src/gcp/upload_quiz_banks.py`) and any other broken pre-scope artifacts —
   delete, do not neuter-and-keep.
5. **Bridge-key extractor → top industry standard, no shortcuts:** unify on ONE extractor (the LLM path +
   the hardened schema guard); retire the divergent regex extractor.
6. **Add a hard DB2-vocabulary membership check** so a `doc_key` outside DB2's tag set fails the gate (not
   just a warning).

---

## 3. Non-goals / out of scope

- ❌ Do **not** re-run or "fix" `upload_quiz_banks.py` — it's being deleted (wrong layout, inert writes).
- ❌ Do **not** rewrite Area I banks to force "SJT correct = D." The real schema has no positional rule and
  Area I serves correctly. (The 13 non-Area-I SJTs that currently answer "D" are a separate **quality**
  rewrite — out of scope here; they pass the schema.)
- ❌ Do **not** fabricate or stretch a `far_reference` or a bridge key to pass a gate. If a citation looks
  wrong, escalate to Daniel (CFI) — never invent.
- ⏸️ Deferred (not this story): SJT-quality rewrites of the 13 non-Area-I banks, missing
  `hazardous_attitude` tags, exact 2/2/2/2 polish on Area I. They serve fine.

---

## 4. STORY A — Quizzes (light the 14 dark lessons)

**Goal:** all **47/48** lessons serve **8 valid questions** from the per-lesson
`quiz_banks/{lesson_id}/questions` subcollection the app reads.

### Key facts (measured)
- **Wrong tool (delete):** `src/gcp/upload_quiz_banks.py` — writes ONE parent doc with a `questions[]`
  field (`upload_quiz_banks.py:113`, the app never reads this), has a positional SJT validator
  (`correct_answer == "D"`, `upload_quiz_banks.py:50-51`), and points at `specialist_curriculum/quiz_banks`
  (`:16`), a directory that no longer exists. Doubly dead.
- **Right tool:** `AGY_AVIATIONCHAT/scripts/ingest_quiz_banks.py` — validates with the real Pydantic
  `QuizBankRecord` and writes `quiz_banks/{lesson}/questions/{q}` + `seen_by` rotation (what the app reads).
- **Real schema (source of truth):** `AGY_AVIATIONCHAT/backend/schemas/quiz.py` —
  `QuizBankQuestion.far_reference: str` (required → `null` FAILS, `""` passes), `options` `min_length=3,
  max_length=4` (so a 5th option FAILS), `perspective: Literal["legal","safety","application",
  "risk_management"]` (so other values FAIL), `correct_answer` normalized via `@model_validator` (**no
  positional D rule**).
- **App read path:** `AGY_AVIATIONCHAT/backend/services/quiz_bank_service.py:76`; delivery/scoring
  `AGY_AVIATIONCHAT/backend/routers/quiz.py` (options served unshuffled; answer key sanitized).
- **Canonical bank dir:** `curriculum_components/quiz_banks/` (47 files; **every question has a
  `far_reference` — zero nulls**).
- **App bank dir (ingest input, drifted):** `AGY_AVIATIONCHAT/_docs/specialist_lesson/quiz_banks/`
  (48 files incl `I_H_04`; **11 files contain `null` citations**).

### Tasks

| ID | Task | Files / commands | Done when |
|---|---|---|---|
| **A1** | **Delete the wrong tool.** | remove `src/gcp/upload_quiz_banks.py` | file gone; nothing references it |
| **A2** | **Fix the Windows-console crash in the right tool.** It prints `→` (U+2192) and crashes on the cp1252 console mid-`--all`. Add `sys.stdout.reconfigure(encoding="utf-8")` at the top, or replace the arrow with `->`. | `AGY_AVIATIONCHAT/scripts/ingest_quiz_banks.py` | `--all --dry-run` runs without `PYTHONIOENCODING` set |
| **A3** | **CFI citation verification (Daniel — see §7).** The pipeline copies of the 11 drifted files already carry a citation on every question. Daniel confirms in-scope; 3 are flagged. No fabrication. | the 11 pipeline bank JSONs | Daniel signs off per file |
| **A4** | **Sync pipeline → app** for the 11 drifted banks (only after A3). | `curriculum_components/quiz_banks/*` → `AGY_AVIATIONCHAT/_docs/specialist_lesson/quiz_banks/*` | app copies match canonical; no `null` citations remain |
| **A5** | **`I_H_04` perspective remap (app-only today).** Map the 5 non-canonical `perspective` values (`physiological`, `decision-making`, `risk-management`) → the 4 canonical, restore **2 legal / 2 safety / 2 application / 2 risk_management**, AND author a canonical copy into `curriculum_components/quiz_banks/`. | `AGY_AVIATIONCHAT/_docs/.../PPL_PA_I_H_04_quiz.json` + new pipeline copy | dry-run passes for `I_H_04`; canonical copy exists |
| **A6** | **`I_F_01` 5th-option fix** (option `E` exists in **both** copies). Drop the weakest distractor or split into two questions so it's ≤4; fix in canonical, then sync. Served fine today — only a re-ingest would break it. | `curriculum_components/quiz_banks/PPL_PA_I_F_01_quiz.json` (+ sync) | ≤4 options; dry-run passes |
| **A7** | **Re-ingest with the right tool** (idempotent, keyed by question id). | `cd AGY_AVIATIONCHAT && python -m scripts.ingest_quiz_banks --all` | dry-run = **48/48 pass, 0 fail** BEFORE the real run |
| **A8** | **Verify live.** Take a quiz for a previously-dark lesson in the running app, end-to-end. | running app: `XI_A_01`, then `IX_B_01` | 8 questions served each; screenshot/log captured |
| **A9** | *(Housekeeping, non-blocking)* clear the 48 stray parent-doc `questions[]` fields the wrong tool left in `quiz_banks`. | Firestore | parent docs cleaned |

### Story A — Acceptance criteria
- `python -m scripts.ingest_quiz_banks --all --dry-run` reports **48 pass / 0 fail**.
- All 47/48 lessons serve **8 questions** from `quiz_banks/{id}/questions`.
- A previously-dark lesson (`XI_A_01`) and an Area IX lesson (`IX_B_01`) each serve a full quiz in the app.
- `upload_quiz_banks.py` is deleted; no second writer to `quiz_banks` remains.

### The 14 dark lessons (for tracking)
`III_A_01`, `III_A_02`, `III_B_01`, `VI_B_01`, `VI_B_02`, `VI_B_03`, `VII_A_01`, `VII_D_01`, `IX_B_01`,
`IX_C_01`, `XI_A_01`, `XI_A_02`, `XI_A_03`, `I_H_04`.
- `III_A_02`, `XI_A_01` — valid, just never ingested (ingest as-is).
- 11 files (`III_A_01`, `III_B_01`, `VI_B_01/02/03`, `VII_A_01`, `VII_D_01`, `IX_B_01`, `IX_C_01`,
  `XI_A_02`, `XI_A_03`) — `null` citations in the app copy; pipeline copy already filled → A3+A4.
- `I_H_04` — perspective remap → A5.

---

## 5. STORY B — Bridge keys (make DB1→DB2 verifiable, and prove it)

**Goal:** every lesson carries non-empty, **document-level** `doc_keys` in DB1 `structData` that return
**real DB2 hits** — proven live with the numbers.

### Key facts (measured)
- **The schema is ALREADY hardened** (do not redo): `src/utils/schema.py` →
  `doc_keys: List[str] = Field(min_length=1)` + `strip_invalid_keys` (drops `N/A`/blank) +
  `validate_doc_keys_non_empty` + `warn_chapter_level_keys` (`schema.py:33, 36-68`). It also defines a
  `DB2_VOCABULARY` set (`schema.py:7-21`) but only **warns** on chapter-level keys — it does **not**
  enforce membership.
- **The LLM extractor** `src/utils/generate_metadata.py` (Gemini 2.5 Flash, structured output) already has
  a post-generation empty-`doc_keys` check (`generate_metadata.py:82-91`).
- **THE BUG:** the production DB1 writer `src/gcp/reimport_with_metadata.py`:
  - imports **nothing** from `utils.schema` and builds the JSONL `structData` **by hand**
    (`reimport_with_metadata.py:155-170`) → **the guard never runs on the path that writes DB1**;
  - extracts keys with a **regex** over the master-doc `Bridge Keys` block (`:77-91`) — NOT the LLM;
  - has **hardcoded foreign paths**: SA path `:10` and repo root `:20` point at
    `c:\Sudo_Hatter_Command\Projects\ingestion-Pipeline-AC\...`, and it reads `pipeline/curriculum/new/Area *.md`, which
    does not exist in this repo (our modules are in `curriculum_components/curriculum_modules/`). It cannot
    run here as-is.
- **App-side reference (read-only, for understanding):** the bridge hop is
  `AGY_AVIATIONCHAT/backend/tools/librarian.py:237` (`_search_db2_bridge_hop`), filtering DB2 with
  `document_tags: ANY(<keys>)`; DB2 tags are produced by `AGY_AVIATIONCHAT/scripts/patch_db2_metadata.py`.
- The IX **RKP manifests are fine** — `curriculum_components/rkp_manifests/PPL_PA_IX_B_01_rkp.json` carries
  `bridge_keys` on every RKP. The empty layer was DB1 `structData`.

### Tasks

| ID | Task | Files | Done when |
|---|---|---|---|
| **B1** | **Wire the guard into the production write path.** Validate every entry through `CurriculumLessonSchema`/`CurriculumStructData` before writing the JSONL, so empty/invalid `doc_keys` fail loud at ingest. | `src/gcp/reimport_with_metadata.py` (+ import from `src/utils/schema.py`) | unit test: an entry with empty `doc_keys` raises before any write |
| **B2** | **Fix the hardcoded/stale paths.** Replace the `c:\Sudo_Hatter_Command\...` root and SA path with `Path(__file__).parent` resolution + the `GOOGLE_APPLICATION_CREDENTIALS` pattern from `.claude/rules/credential-resolution.md`; point the module reader at `curriculum_components/curriculum_modules/`. | `src/gcp/reimport_with_metadata.py` | runs end-to-end on a clean clone, no hardcoded user paths |
| **B3** | **Unify on one extractor (retire the regex).** Route key extraction through the LLM path (`generate_metadata.py`) feeding the schema guard; remove the divergent `split_task_file` regex extraction from the production path. | `src/gcp/reimport_with_metadata.py`, `src/utils/generate_metadata.py` | one extractor; the guard always runs; tests cover it |
| **B4** | **Add the hard DB2-vocabulary membership check.** Upgrade `warn_chapter_level_keys` (or add a validator) so a `doc_key` not in `DB2_VOCABULARY` FAILS, not warns. | `src/utils/schema.py` | unit test: an off-vocabulary `doc_key` raises |
| **B5** | **Build the offline schema gate (CI, permanent).** Iterate all 184 DB1 docs; assert every `doc_keys` is non-empty, document-level, and in-vocabulary. | new test/script under `src/tests/` or `scripts/` | green over 184; wired into CI |
| **B6** | **Build the live DB1→DB2 round-trip probe.** For each fixed key, fire the real bridge hop; assert `len(db2_hits) ≥ 1` AND top score ≥ a defined floor AND the returned doc maps back to the lesson's own Area (no IX→VII cross-wire). (The `bridge-key-verification` skill covers this.) | new probe script | numbers captured for the fixed lessons |
| **B7** | **Fix Area IX content + regenerate.** Ensure `curriculum_components/curriculum_modules/Area 9 Tasks B,C PPL.md` has a clean, populated `Bridge Keys` block (no "N/A"); regenerate metadata for the IX split lessons; confirm non-empty document-level keys. | Area 9 module + generated JSON | IX keys non-empty + document-level |
| **B8** | **Re-import to DB1 + prove.** Run the now-guarded `reimport_with_metadata.py` with **FULL** reconciliation (idempotent); confirm the 12 IX docs carry non-empty keys and the doc count stays **184**; then run B5 + B6 + a frozen golden set; spot-check the other 5 content Areas didn't regress. | `reimport_with_metadata.py`, probes | count == 184; live hit counts shown |

### Story B — Acceptance criteria
- The offline gate is green over all 184 DB1 docs (non-empty, document-level, in-vocabulary `doc_keys`).
- An empty or off-vocabulary `doc_keys` **fails at ingest** (proven by a unit test), on the path that
  actually writes DB1.
- For the Area IX lessons (and the golden set), the live DB1→DB2 round-trip returns **count ≥ 1**, top
  score ≥ floor, owning-area match — **numbers pasted into the PR/walkthrough.**
- DB1 doc count remains **184** after the FULL re-import.
- Exactly one extractor remains; the regex path is gone.

---

## 6. Area IX — the overlap (fix once)

`IX_B_01` and `IX_C_01` are in **both** stories. Sequence them together:
1. (Story A) verify + sync the IX quiz citations (A3→A4).
2. (Story B) regenerate + re-import the IX bridge keys (B7→B8).
3. Prove both in one pass: a live quiz on `IX_B_01` **and** a live DB1→DB2 round-trip on the IX keys.

Assign Area IX to whoever takes the second story to finish, or coordinate so it isn't done twice.

---

## 7. OPEN — needs Daniel (CFI) before Story A content sync

The pipeline copies already carry a citation on every question that is `null` in the app copy, so this is
**verify**, not author. Three to confirm per the scope rule in `quiz_authoring_guide.md` §5.4 (a real reg
cited outside its scope is as wrong as an invented one):

- `VII_A_01 Q001` and `VII_D_01 Q001` cite **`14 CFR 23.2150`** — a Part 23 *aircraft-certification*
  airworthiness standard, not an operating rule. Correct for a PPL operational question?
- `IX_C_01 Q004` cites **`AC 120-111`** (air-carrier / Part 121-135 upset-recovery training).
- `IX_C_01 Q003` cites **`14 CFR 91.411`** (IFR altimeter/static-system tests).

Everything else (the `91.3` / `91.103` / `91.113` / `91.126` / `AC 61-67C` family) reads in-scope.

---

## 8. Definition of Done (both stories)

- **Quizzes:** all 47/48 lessons serve 8 valid questions from `quiz_banks/{id}/questions`; dry-run 48/48;
  proven by a live quiz on a previously-dark lesson. The wrong tool is deleted.
- **Bridge keys:** every lesson carries non-empty, document-level `doc_keys` that return real DB2 hits
  (count ≥ 1, score ≥ floor, owning-area match), proven **live with the numbers shown**; offline gate green
  over 184; the guard runs on the real write path; one extractor. **If you can't show the hit counts, it
  isn't done.**
- Instruction docs in `_01_My/instruction_docs/` updated with anything new you learn.

---

## 9. Risks & gotchas

- **Windows encoding (real prior incident):** PowerShell `>`/`>>` write UTF-16LE and break Linux CI. Use
  the tools/`git checkout`, never redirect file content. See `.claude/rules/powershell-encoding-safety.md`.
- **Cross-repo:** quiz re-ingest runs from the **app** repo; the bridge-key re-import runs from **this**
  repo. Two repos, two commits, two sets of manual steps.
- **Network-gated:** B6/B8 need live Vertex (DB1/DB2) credentials. The offline gate (B5) de-risks the rest.
- **Idempotency:** quiz re-ingest is keyed by question id (safe); the DB1 re-import uses FULL reconciliation
  (idempotent) — confirm the doc count stays 184 after.
- **Credentials:** never hardcode `auth_keys/service-account.json` relative paths — use the
  `GOOGLE_APPLICATION_CREDENTIALS` resolution in `.claude/rules/credential-resolution.md`.

---

## 10. Reference appendix (verified file:line)

**Pipeline repo (this repo):**
- `src/gcp/upload_quiz_banks.py` — wrong tool: parent-doc write `:113`; positional SJT rule `:50-51`; stale dir `:16`
- `src/gcp/reimport_with_metadata.py` — hand-built JSONL `:155-170`; regex extractor `:77-91`; hardcoded paths `:10, :20`
- `src/utils/schema.py` — `DB2_VOCABULARY` `:7-21`; `doc_keys min_length=1` `:33`; validators `:36-68`
- `src/utils/generate_metadata.py` — LLM extractor + post-gen check `:82-91`
- `curriculum_components/quiz_banks/` — 47 canonical banks (zero null citations)
- `curriculum_components/rkp_manifests/PPL_PA_IX_B_01_rkp.json` — IX manifest, bridge_keys populated
- `curriculum_components/curriculum_modules/Area 9 Tasks B,C PPL.md` — IX master module

**App repo (`AGY_AVIATIONCHAT`):**
- `scripts/ingest_quiz_banks.py` — the correct ingest tool (Windows-crash fix needed)
- `backend/schemas/quiz.py` — real quiz schema (`QuizBankRecord`/`QuizBankQuestion`/`QuizOption`)
- `backend/services/quiz_bank_service.py:76` — app read path
- `backend/routers/quiz.py` — delivery + scoring (options unshuffled)
- `_docs/specialist_lesson/quiz_banks/` — 48 ingest-input banks (11 with null citations)
- `backend/tools/librarian.py:237` — `_search_db2_bridge_hop`
- `scripts/patch_db2_metadata.py` — DB2 `document_tags` source

**Companion docs (`_01_My/instruction_docs/`):** `get_back_on_track.md`, `bridge_key_guide.md` (v2.8),
`quiz_authoring_guide.md`, `rkp_creation_guide.md`.
