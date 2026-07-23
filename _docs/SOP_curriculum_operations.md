# SOP — Curriculum Operations Across the Two Teams

**Canonical copy.** Lives in `Projects/RAG_Pipeline_AC/_docs/` — the pipeline owns the process, so it
owns the document. The lobby `router.md` and the app's `AGENTS.md` point here; do not fork this file.
Deep how-to detail stays in `_docs/instruction_docs/` (the six authoring guides) and the PRD
(`_docs/docs_prds/Master_Curriculum_Pipeline.md`); this SOP is the **operating contract between the
stations** — who owns what, in what order, and where the hard gates sit.

| | |
|---|---|
| Established | 2026-07-23 (session `_artifacts/_main/2026-07-22_pipeline-conversion-and-sop/` at the command center) |
| Owner | Daniel (content truth) · agents (everything mechanical) |
| Applies to | `Projects/RAG_Pipeline_AC/` (pipeline) · `Projects/AGY_AVIATIONCHAT/` (app) · Google Drive `AVIAIONCHAT/` (authoring) |

---

## 1. The three stations

Curriculum work happens in three places, deliberately separated (Daniel, by design) so the heavy
files never enter git or paid cloud storage, and the app never carries authoring machinery.

| Station | Where | Owns | Never does |
|---|---|---|---|
| **Authoring** | Google Drive `AVIAIONCHAT/` (masters in `ACS Modules`, folder id `1eiHjhYBd1bb2h7-M-8DTz3DjxGYVs5-S`) | Daniel's hand-written master modules (`Area N Task X PPL`, Google Doc + `.md` export side by side) · podcast audio · heavy media | Machine artifacts. Nothing in Drive is ever ingested directly. |
| **Pipeline** (this repo) | `Projects/RAG_Pipeline_AC/` | Everything machine-made: split micro-lessons, sidecars, **RKP manifests, quiz banks**, flashcards, bridge keys, FAA library metadata — and ALL writes to the live stores via the gated tools in `src/gcp/` | Serving students. Nothing here is deployed. |
| **App** | `Projects/AGY_AVIATIONCHAT/` | Consuming the stores at runtime (lesson planner, specialist teacher, quiz agent, librarian bridge-hop) | Authoring or editing curriculum. Sync direction is **pipeline → stores → app, one-way.** |

Sessions are normally driven **from the command center** (`c:\Sudo_Hatter_Command\`) — the sudo flow
and the BMAD module live at the lobby, and cross-repo work needs the lobby's vantage. A repo-local
session is fine for pure authoring inside the pipeline. Either way the pipeline's own
artifacts protocol and gates (`AGENTS.md` §5/§8) apply.

## 2. Source-of-truth ladder

When two copies of a thing disagree, the higher rung wins — fix downward, never upward, with one
exception noted in §7.

1. **Daniel's masters in Drive** — the teaching content itself. Only Daniel writes here.
2. **This repo's committed artifacts** (`curriculum_components/` + `pipeline/curriculum/`) — the
   canonical machine form. Every store write originates from a file here.
3. **The live stores** — Vertex DB1 `aviation-curriculum-v2` · DB2 `aviation-library-v2` · Firestore
   `aviationchat-database` (`rkp_manifests`, `quiz_banks`). What students actually receive. Must
   equal rung 2; drift is a defect (§7).
4. **Any copy in the app repo** — reference snapshot only, never consumed by code, may lag freely (§8).

## 3. Intake — new curriculum comes from Drive (STANDING RULE, 2026-07-23)

Daniel authors in Drive; agents **pull** — never retype, reconstruct from memory, or accept pasted
fragments as a master. When Daniel says a new Area/Task is ready:

1. `search_files` the `ACS Modules` folder (id above) for `Area N Task X PPL` — prefer the `.md`
   export beside the Doc.
2. `download_file_content` / `read_file_content` on the `.md`. **⚠ The connector returns raw
   (non-Google-Docs) files base64-encoded** — decode before use, or you are diffing garbage
   (verified 2026-07-22: decoded output is byte-identical to the repo master, md5-matched; the
   masters use CRLF line endings — keep the decoded bytes exactly as-is, do not "normalize").
   Sanity check: decoded byte count must equal the Drive `fileSize` metadata.
3. Land it at `curriculum_components/curriculum_modules/<same name>.md`. Overwriting an existing
   master is allowed **only** in an explicit Drive-pull session (constitution.project) — say so in
   the session artifact, and show Daniel the diff against the old master before continuing.
4. From there the per-lesson lifecycle (§5) takes over.

Google-Docs-native files export as plain text without the base64 step; everything raw (`.md`,
sidecar `.json`, audio) arrives encoded. The FAA/ACS source PDFs also live in Drive (Daniel keeps
them there already) — same pull mechanic on the rare day a new FAA edition drops; record that
folder's id here on first pull, then land PDFs in `pipeline/library/new/` (gitignored) for the DB2
import flow.

## 4. Ownership in one line each

- **Daniel** — writes masters; verifies every citation (the ONE human content gate); answers
  "approved" at the dry-run gate; runs all git commits/pushes; decides pedagogy (question mix,
  answer balance, what an Area covers).
- **Agents (pipeline)** — pull, split, author manifests + quiz banks *through the skills*
  (`rkp-manifest-creation`, `quiz-bank-generation`, both hard-wired through `faa-grounding-gate` —
  every fact traces to an on-disk/DB2 FAA source, never model memory), run tests, dry-run, execute
  ingests after approval, prove with the probe + state map, keep the board current.
- **Agents (app)** — consume. A curriculum bug found app-side gets *reported upstream* (board story
  in the pipeline), never patched in the app.

## 5. Per-lesson lifecycle (the checklist)

Run top to bottom for every lesson; each row names its owner. Deep detail lives in
`_docs/instruction_docs/curriculum_lifecycle.md`.

| # | Step | Owner | Gate / proof |
|---|---|---|---|
| 1 | Author master in Drive (`Area N Task X PPL`) | Daniel | — |
| 2 | Pull master → `curriculum_components/curriculum_modules/` (§3 mechanic) | agent | byte-count = Drive `fileSize` |
| 3 | Split → micro-lessons in `pipeline/curriculum/elements/` (+ `sidecars/` if metadata Area) | agent | lesson ids follow `PPL_PA_<Area>_<Task>_<nn>` |
| 4 | RKP manifest → `curriculum_components/rkp_manifests/` | agent authors · **Daniel verifies citations** | `rkp-manifest-creation` + `faa-grounding-gate`; bridge keys ⊂ DB2 24-tag vocabulary |
| 5 | Quiz bank (8 Qs: 2 legal / 2 safety / 2 application / 2 risk_management) → `curriculum_components/quiz_banks/` | agent authors · Daniel spot-checks | `quiz-bank-generation` + gate; **correct answers carry NO positional pattern (§6)** |
| 6 | Offline gate | agent | `python -m pytest src/tests/ -q` green |
| 7 | Dry-run every ingest tool touched; review output **in the same session** | agent | constitution.project hard stop |
| 8 | Approval to write | **Daniel** | the word "approved" |
| 9 | `--execute` — `reimport_db1_keys.py` / `upload_manifests.py` / `ingest_quiz_banks.py` | agent | gated tools only, never ad-hoc writes |
| 10 | Prove it | agent | `probe_bridge_hop.py` ≥1 hit per touched lesson · `generate_state_map.py --live` drift zero |
| 11 | Board + records | agent | story → `done` in `_bmad-output/.../sprint-status.yaml`; walkthrough + commit command for Daniel |

## 6. Quiz answer policy + feedback prose (STANDING RULES, 2026-07-23)

**Answer keys.** Correct answers land on the exact per-bank multiset **{A,A,B,B,C,C,D,D}** — no
positional meaning, ever. The old "SJT answer is always D" convention is dead (PRD §7.1/§11), and
the app **does not shuffle options at render** — a positional skew is directly visible to students.
Position-locked option texts ("All of the above", "None of the above") may not be relocated
mechanically; they stay pinned and the key is balanced around them. Re-lettering an existing bank
is script work, never hand work: `scripts/rebalance_quiz_answers.py` (deterministic, seeded per
`lesson_id`, format-faithful). Measured 2026-07-22 the corpus sat at 67% "B"; fixed by story `6-3`.

**Feedback prose (`explanation`, `sjt_rationale`) is LETTER-FREE.** Never reference an option by
its letter ("Option A…", "choice B", "(C)") — name the option's *content* or the *behavior* it
represents: "The 'gift' defense is explicitly rejected by FAA legal interpretations…", "Delegating
a PIC responsibility to the ferry pilot is a Macho pattern…". Letters inside proper aviation names
("Class B airspace", "taxiway B", "A&P", "W&B") are fine — they are not option references. Why:
letter-free prose survives any re-letter or future shuffle untouched, while letter-anchored prose
silently lies to students the moment options move. `sjt_rationale` keeps the Chain-of-Cues shape —
why each wrong *path* fails, named by its behavior/hazardous attitude, then why the correct path
wins. All feedback prose stays factually grounded per the `faa-grounding-gate` skill: every claim
and citation traceable to the source docs, nothing invented, rewrites never add or drop a claim.

**Enforcement:** `src/tests/test_answer_distribution.py` fails the suite on any per-bank letter
imbalance OR any option-letter reference in feedback prose. New banks pass it from day one; the
`quiz-bank-generation` skill carries the same rules at the authoring surface.

## 7. Live-store discipline & drift

- The stores ARE production — there is no staging tier. Every write goes through a gated `src/gcp/`
  tool: **dry-run by default, `--execute` only after Daniel's approval, never a partial manifest
  with FULL reconciliation** (that combination wipes the live store — constitution.project).
- **Drift check** (repo rung 2 vs stores rung 3): `python scripts/generate_state_map.py --live`.
  Run it at session boot for any ingest session and after every `--execute`.
- If repo and store disagree: **STOP.** Diagnose which rung is stale before touching either. The
  one sanctioned upward fix: when the store provably holds the newer truth (e.g. a hand-edit made
  directly in Firestore), pull the store copy down into the repo *first*, commit it, then resume
  normal downward flow. Never leave the two disagreeing at session end.
- Bridge keys are a **three-layer contract** that must stay aligned: DB1 `structData` keys · DB2
  `document_tags` · manifest `bridge_keys`. The app's librarian
  (`backend/tools/librarian.py::_search_db2_bridge_hop`) filters DB2 with exact
  `document_tags: ANY(manifest.bridge_keys)` — one misspelled tag silently returns nothing.
  Prove with `probe_bridge_hop.py`; vocabulary changes are ask-first.

## 8. App-side consumption map (what breaks downstream)

| Store | App consumer | Contract that must hold |
|---|---|---|
| DB1 `aviation-curriculum-v2` | specialist teaching agents (lesson retrieval) | lesson ids + structData bridge keys |
| DB2 `aviation-library-v2` | `librarian.py` bridge-hop (FAA citations shown to students) | `document_tags` vocabulary (24 tags) |
| Firestore `rkp_manifests` | lesson planner / specialist (per-`lesson_id` manifest) | manifest schema; `bridge_keys` layer |
| Firestore `quiz_banks` | quiz agent — serves options **in stored order** | `src/utils/schema.py` **mirrors** app `backend/schemas/quiz.py` — change together or not at all (ask-first) |

**Mirror policy:** the app repo's copy of 48 manifests + 48 quiz banks lives at
`_my_resources/_docs/specialist_lesson/` — inside Daniel's **protected personal area**, so agents
neither read, edit, nor sync it (house rule). It is his reference snapshot; it may lag freely;
source of truth is rung 2 of this repo. No app code reads it.

## 9. Debt register

The **live** register is the board — `_bmad-output/implementation-artifacts/sprint-status.yaml`
(epic 6 = infrastructure). Standing items as of 2026-07-23: podcast ingestion tool (`6-1`) · DB2
source gaps / 13 reference-only lessons (`6-2`) · quiz answer-key re-balance + Firestore truth
reconciliation (`6-3`) · `data/` root merge of the two data trees (`6-4`) · `docs/` vs `_docs/`
split · `specialist_curriculum/` fate · repo `.venv` missing · `pypdf` proposal (would unlock local
PDF reading for the grounding gate — ask-first). Update the board, not this list; this paragraph is
a pointer, not a second tracker.
