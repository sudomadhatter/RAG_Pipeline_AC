---
title: "Master Curriculum & Ingestion Pipeline — PRD"
type: prd
version: "2.8"
date: 2026-06-16
status: "Living document — source of truth for the ingestion/curriculum pipeline"
audience: "Daniel (CFI/product), the Ingestion Pipeline team (Woz), and any app-team engineer consuming our artifacts"
owner_split: "Pipeline/tooling/layout/schema = engineering (Woz). Which regs/citations are correct + media = Daniel (CFI). App rendering/serving = app team."
companion_docs: "instruction_docs/{get_back_on_track, bridge_key_guide (v2.8), quiz_authoring_guide, rkp_creation_guide, flashcard_creation_guide, curriculum_lifecycle}.md"
---

# Master Curriculum & Ingestion Pipeline — PRD

> **What this is.** One authoritative document that explains *how a PPL lesson is made, ingested, and
> consumed* — the artifacts, the tools, the data stores, the flow, and the contracts. It is both a product
> requirements doc and a visual walkthrough (mermaid diagrams throughout) so the whole system can be
> understood end to end. Everything here was measured against the live code on 2026-06-16.
>
> **How to read it:** §1–§3 are the mental model. §4–§7 are the full walkthrough (make a lesson → ingest →
> how it connects at runtime) with diagrams. §8–§12 are the reference (tools, schemas, ownership, current
> state, gates). If you read nothing else, read §3 (the big picture diagram) and §6 (making a lesson).

---

## 1. Vision & purpose

We are building the **knowledge spine** for an AI flight instructor. Every PPL lesson must be:

- **Teachable** — a student studies flashcards (from RKPs) and a narrative overview, then proves mastery
  on a quiz.
- **Verifiable** — when the AI tutor answers a question, it grounds the answer in the *actual FAA source*
  (FAR/AIM/PHAK/AFH/AC), not just the lesson prose. That grounding is the **bridge-key / DB1→DB2** hop.
- **Maintainable** — one canonical source (this pipeline repo) that multiple app branches pull from, with
  every derived artifact rebuildable from the master module by a script.

The pipeline's job is to turn a CFI's teaching content into the machine artifacts the app consumes, and to
**guarantee** (with schema gates and live probes) that nothing ships dark or unverifiable.

### Goals
1. Every lesson serves a valid **8-question quiz** from the per-lesson Firestore subcollection.
2. Every lesson carries non-empty, document-level **bridge keys** that return real DB2 hits.
3. Every lesson renders **flashcards** from its RKP `knowledge`.
4. The pipeline is **idempotent, gated, and provable** — re-runs are safe, bad data fails loud, and "done"
   means measured hit counts, not "no error."

### Non-goals
- The app's UI/serving (flashcard flip, quiz router, tutor, unlock gates) — owned by the app team.
- Media production (audio/video) — a separate process owned by Daniel; the manifest only references the
  filenames.
- Deciding *which* citation is correct — that's the CFI's call; engineering owns that the key is present,
  well-formed, and verified.

---

## 2. Key concepts in 60 seconds

| Term | Meaning |
|---|---|
| **Master-module markdown** | The human-authored lesson source (`curriculum_modules/Area X Task Y PPL.md`). Everything derives from it. |
| **RKP** | "Required Knowledge Point" — one atomic teaching fact. A lesson's RKP manifest holds 3–5 RKPs + a narrative overview. One RKP → one flashcard. |
| **Quiz bank** | 8 questions per lesson (2 legal / 2 safety / 2 application / 2 risk_management-SJT), authored *from* the RKP `knowledge`. |
| **Bridge keys** | `reg_keys` + `doc_keys` — document-level tokens (`14 CFR 91`, `FAA-H-8083-25C`, `AIM`, `AC 61-98D`) that link a DB1 lesson to its DB2 FAA source. |
| **DB1** | Vertex AI Search store `aviation-curriculum-v2` — the 184 teaching micro-lessons. |
| **DB2** | Vertex AI Search store `aviation-library-v2` — the FAA PDF library (verification). |
| **Firestore** | `aviationchat-database` — serves quizzes (`quiz_banks/{lesson}/questions/{q}`) and RKP/flashcard data. |
| **Pipeline repo** | THIS repo — canonical authoring + ingestion tooling. |
| **App repo** | `AGY_AVIATIONCHAT` — consumes our artifacts; owns the real quiz schema + quiz-ingest tool. |

---

## 3. System overview (the big picture)

Everything flows from the master module into three machine artifacts, then into two data stores the app
reads.

```mermaid
flowchart TD
    A["Master-module markdown<br/>curriculum_modules/Area X Task Y PPL.md<br/>human-authored: CFI + ingestion team"]

    A --> B["RKP manifest<br/>rkp_manifests/PPL_PA_star_rkp.json<br/>RKPs, why, knowledge, far_references, bridge_keys, overview"]
    A --> C["Quiz bank<br/>quiz_banks/PPL_PA_star_quiz.json<br/>8 questions, 4 perspectives"]
    A --> D["Bridge-key metadata<br/>reg_keys / doc_keys<br/>extracted at ingest"]

    B -->|"generate_knowledge_formatted.py (Gemini 2.5 Pro)"| E["Flashcards<br/>knowledge_formatted field<br/>one card per RKP"]

    C -->|"ingest_quiz_banks.py (app repo)"| F[("Firestore<br/>aviationchat-database")]
    B --> F
    E --> F
    D -->|"reimport_with_metadata.py (FULL reconcile)"| G[("Vertex DB1<br/>aviation-curriculum-v2")]

    G -.->|"bridge keys link lesson to source"| H[("Vertex DB2<br/>aviation-library-v2<br/>FAA PDFs")]

    F --> APP["APP: tutor, quiz router, flashcard UI"]
    G --> APP
    H --> APP
```

**Read it as:** one source (top) → three artifacts (RKP, quiz, bridge keys) → flashcards are a 4th derived
from the RKP → two stores (Firestore for serving, Vertex DB1/DB2 for RAG) → the app consumes all three.

---

## 4. Data store topology — what lives where

```mermaid
flowchart LR
    subgraph FS["Firestore — aviationchat-database (serving)"]
      Q["quiz_banks/{lesson}/questions/{q}<br/>+ seen_by, last_seen_at rotation"]
      RKPC["RKP manifests / lesson cache<br/>(flashcards served from here)"]
    end
    subgraph V["Vertex AI Search (RAG)"]
      DB1["DB1 aviation-curriculum-v2<br/>184 micro-lessons<br/>structData: reg_keys / doc_keys"]
      DB2["DB2 aviation-library-v2<br/>FAA PDFs: FAR, AIM, PHAK, AFH, ACs<br/>document_tags vocabulary"]
    end
    DB1 -.->|"document_tags: ANY(doc_keys)"| DB2
```

- **Firestore** answers "give me this lesson's quiz / flashcards" — fast, per-lesson reads.
- **DB1** answers "which lesson is this student question about?" and carries the bridge keys.
- **DB2** answers "what does the FAA actually say?" — filtered by the matched lesson's `doc_keys`.

---

## 5. The seven artifacts per lesson

| # | Artifact | Lives in | Built by | Governing guide |
|---|---|---|---|---|
| 1 | Master-module markdown | `curriculum_modules/` | Human (CFI + team) | `rkp_creation_guide.md` §4 |
| 2 | RKP manifest | `rkp_manifests/*_rkp.json` | Team (hand) | `rkp_creation_guide.md` |
| 3 | Flashcards (`knowledge_formatted`) | field in the RKP manifest | `generate_knowledge_formatted.py` (Gemini 2.5 Pro) | `flashcard_creation_guide.md` |
| 4 | Quiz bank | `quiz_banks/*_quiz.json` | Team (hand, from RKP knowledge) | `quiz_authoring_guide.md` |
| 5 | Bridge keys / `structData` | DB1 structData | extraction at ingest (see §7) | `bridge_key_guide.md` (v2.8) |
| 6 | Media (audio/video/notes) | referenced in manifest | separate process / Daniel | — (out of team scope) |
| 7 | Curriculum Key (ACS entries) | curriculum key | Team (manual) | — |

---

## 6. WALKTHROUGH — how we make a lesson

This is the authoring loop, start to finish.

### 6.1 The narrative

1. **Daniel (CFI) provides the inputs:** which ACS Area/Task and element codes the lesson covers, the raw
   teaching content per knowledge point, the correct FAA citations, and a lesson title. (He can hand full
   content, or just topic + codes and let the team draft from the existing module markdown.)
2. **The team writes the master-module markdown** in `curriculum_modules/` — the single source. It names
   the regs and FAA documents explicitly (in a clean `Bridge Keys` block) because the metadata extractor
   reads that.
3. **The team builds the RKP manifest** (`*_rkp.json`): 3–5 RKPs, each with `title`, `why`, `knowledge`
   (the textbook-complete source of truth — *never* auto-modified), `acs_elements`, `far_references`, and
   document-level `bridge_keys`; plus a 500–1000 word `lesson_overview`. `knowledge_formatted` is left
   empty.
4. **The team authors the 8-question quiz bank** *from the RKP `knowledge`* (the two-way contract): every
   correct answer must trace to a sentence the student actually studied. 2 legal / 2 safety / 2 application
   / 2 risk_management (SJT). Citations must be in-scope.
5. **Daniel verifies the citations** are correct and in-scope (the one human gate — engineering never
   guesses a reg).
6. **Run the flashcard formatter:** `generate_knowledge_formatted.py` turns each `knowledge` field into
   scannable card-back markdown with Gemini 2.5 Pro. It writes only `knowledge_formatted`.
7. **Ingest** (see §7): quizzes → Firestore; bridge keys → DB1.
8. **Prove it:** quiz serves 8 questions in the app; the DB1→DB2 round-trip returns real hits. Only then is
   the lesson "done."

### 6.2 The authoring sequence

```mermaid
sequenceDiagram
    participant D as Daniel (CFI)
    participant T as Ingestion team (Woz)
    participant S as Pipeline scripts
    participant FS as Firestore
    participant V as Vertex DB1/DB2

    D->>T: ACS task + element codes + teaching content + correct citations
    T->>T: Write master-module markdown (curriculum_modules/)
    T->>T: Build RKP manifest (knowledge, why, far_references, bridge_keys, overview)
    T->>T: Author 8-question quiz bank FROM the RKP knowledge
    D-->>T: Verify citations correct and in-scope
    T->>S: generate_knowledge_formatted.py --all --write
    S-->>T: knowledge_formatted populated (flashcard backs)
    T->>S: ingest_quiz_banks.py --all  (validate vs schema, write subcollection)
    S->>FS: quiz_banks/{lesson}/questions/{q} (+ seen_by rotation) and RKP data
    T->>S: reimport_with_metadata.py  (extract bridge keys, FULL reconcile)
    S->>V: DB1 structData (reg_keys / doc_keys)
    T->>V: Live DB1 to DB2 round-trip probe (count >= 1, score >= floor)
    V-->>T: Hit counts = proof of done
```

### 6.3 The reverse contract (why order matters)

The quiz is authored *from* the RKP, so a testable fact must live in a `knowledge` field, **not** only in
the `lesson_overview`. If you want a question and the supporting fact isn't in `knowledge`, you **enrich the
RKP**, you don't invent the test. Likewise, editing a `knowledge` fact ripples to both the flashcard back
(re-run the formatter) and the quiz (re-check the answers/distractors). See §9.

---

## 7. WALKTHROUGH — ingestion (the two paths)

Two artifacts get ingested by two different tools into two different stores.

### 7.1 Quiz ingestion → Firestore

The app reads quiz questions from a **per-question subcollection**. The correct tool validates against the
real Pydantic schema and writes that layout, idempotently (keyed by question id).

```mermaid
flowchart TD
    QB["quiz bank JSON<br/>(8 questions)"] --> ING["ingest_quiz_banks.py --all<br/>(app repo)"]
    ING --> VAL{"Validates vs<br/>QuizBankRecord<br/>(backend/schemas/quiz.py)"}
    VAL -->|fail| ERR["Reject: far_reference null,<br/>5th option, bad perspective..."]
    VAL -->|pass| WR["Write quiz_banks/{lesson}/questions/{q}<br/>plus seen_by and last_seen_at rotation fields"]
    WR --> FS[("Firestore")]
    FS --> APPQ["App quiz router serves 8 questions"]
```

**Schema gates (the real ones):** `far_reference` is a required string (so `null` fails, `""` passes);
`options` is 3–4 (a 5th option fails); `perspective` is one of `legal/safety/application/risk_management`;
`correct_answer` is normalized to a `correct` flag with **no positional rule** (the old "SJT answer must be
D" was a wrong tool's invention — retired). The deprecated `upload_quiz_banks.py` wrote the wrong layout and
is **deleted**.

### 7.2 Bridge-key extraction → DB1 (current vs target)

This is the part under active hardening (v2.8). The bridge keys are extracted from the master module and
written into DB1 `structData`. There are currently **two** extractors, and the production one needs work.

```mermaid
flowchart TD
    M["Master-module markdown<br/>Bridge Keys block"]
    subgraph TODAY["TODAY — production path (being fixed)"]
      M --> RX["regex split_task_file<br/>in reimport_with_metadata.py"]
      RX --> J1["JSONL built by hand<br/>BYPASSES the schema guard"]
      J1 --> DB1a[("DB1")]
    end
    subgraph TARGET["TARGET — v2.8 (top standard, no shortcuts)"]
      M --> LLM["LLM generate_metadata.py<br/>Gemini 2.5 Flash"]
      LLM --> GUARD["CurriculumStructData guard<br/>doc_keys min_length=1<br/>+ strip N/A + DB2-vocab membership"]
      GUARD --> DB1b[("DB1")]
    end
```

**The v2.8 fix:** unify on the LLM extractor + the hardened schema guard, **wire the guard into the write
path** (today it's never invoked there), add a hard DB2-vocabulary membership check, fix the tool's
hardcoded paths, and retire the regex. Then an empty/invalid `doc_keys` fails **loud at ingest** instead of
shipping silently.

---

## 8. WALKTHROUGH — how it all connects at runtime (the RAG hop)

This is *why* bridge keys matter. When the AI tutor answers, pedagogy comes from DB1 and authority from DB2,
joined by the matched lesson's bridge keys.

```mermaid
flowchart LR
    Q["Student question"] --> DB1{{"DB1 search<br/>aviation-curriculum-v2"}}
    DB1 --> L["Matched micro-lesson<br/>+ bridge keys (reg_keys / doc_keys)"]
    L -->|"document_tags: ANY(doc_keys)"| DB2{{"DB2 search<br/>aviation-library-v2"}}
    DB2 --> SRC["Authoritative FAA source<br/>FAR / AIM / PHAK / AFH / AC"]
    L --> PED["Pedagogy (DB1 lesson)"]
    SRC --> AUTH["Authority (DB2 source)"]
    PED --> ANS["Final answer = pedagogy + authority"]
    AUTH --> ANS
    L -.->|"if doc_keys EMPTY"| EMPTY["DB2 returns nothing →<br/>unverifiable answer that<br/>looks fine to a no-error test"]
```

The flashcards and quizzes connect on the **learning** side: the student studies the flashcards (RKP
`knowledge_formatted`), then the quiz (authored from the same `knowledge`) gates mastery. Same source of
truth, three consumers (tutor, flashcards, quiz).

---

## 9. Upkeep cascade — one edit, these ripples

A lesson is never "done forever" — changing a fact forces specific rebuilds. This is the maintenance
contract.

```mermaid
stateDiagram-v2
    [*] --> Authored: master markdown written
    Authored --> ArtifactsBuilt: RKP + quiz + flashcards + bridge keys
    ArtifactsBuilt --> Ingested: scripts run (Firestore + DB1)
    Ingested --> Live: quiz served + flashcards served + DB2 verified
    Live --> NeedsRebuild: knowledge / regs / quiz changed
    NeedsRebuild --> ArtifactsBuilt: re-run only the affected scripts
    Live --> [*]
```

| You change... | ...you must re-run |
|---|---|
| An RKP `knowledge` field | the flashcard formatter (card back) **and** re-check that RKP's quiz questions |
| The master module's named sources (regs/docs) | regenerate metadata → re-import to DB1 → **prove the DB1→DB2 hit** |
| A quiz bank | re-ingest with `ingest_quiz_banks.py` (never the deleted tool) |
| Add a brand-new lesson | all of the above **plus** the Curriculum Key entry |

---

## 10. Tooling reference

| Tool | Repo | Purpose | Notes |
|---|---|---|---|
| `curriculum_components/scripts/generate_knowledge_formatted.py` | pipeline | RKP `knowledge` → `knowledge_formatted` | Gemini 2.5 Pro; default = single dry-run; `--all --write` for the set; never edits `knowledge` |
| `src/utils/generate_metadata.py` | pipeline | LLM bridge-key extractor (target path) | Gemini 2.5 Flash; validates vs hardened schema |
| `src/utils/schema.py` | pipeline | `CurriculumStructData` guard + `DB2_VOCABULARY` | `doc_keys min_length=1` + strip-`N/A`; vocab check being upgraded to hard-fail |
| `src/gcp/reimport_with_metadata.py` | pipeline | Production DB1 re-import (FULL reconcile) | **v2.8 work:** wire in the guard, fix hardcoded paths, retire regex |
| `scripts/ingest_quiz_banks.py` | app | Quiz ingest → Firestore subcollection | validates vs `backend/schemas/quiz.py`; idempotent by question id; fix the `→` cp1252 crash |
| `src/gcp/upload_quiz_banks.py` | pipeline | — | **DELETED** (wrong layout, inert writes) |

---

## 11. Schemas & contracts (the gates)

**Quiz (`backend/schemas/quiz.py`, app repo) — `QuizBankQuestion`:** `perspective ∈
{legal,safety,application,risk_management}`; `question_type ∈ {mcq,sjt}`; `options` 3–4 each with
`label ∈ {A,B,C,D}`; `far_reference: str` (required); `correct_answer` normalized to `correct=True` on the
matching option (no positional rule). `QuizBankRecord` wraps `lesson_id` + `questions`.

**Bridge keys (`src/utils/schema.py`, pipeline) — `CurriculumStructData`:** `reg_keys` may be empty
(non-regulatory topics); `doc_keys` must be non-empty (`min_length=1`), `N/A`/blank stripped, and
(target v2.8) a hard member of `DB2_VOCABULARY` at **document granularity** — `FAA-H-8083-25C`, not
`FAA-H-8083-25C (PHAK Ch 6)`.

**RKP manifest (`rkp_creation_guide.md`):** `lesson_id`, `title`, `acs_task_reference`,
`acs_element_keys[]`, `required_knowledge_points[]` (each: `id`, `title`, `why`, `knowledge`,
`acs_elements[]`, `far_references[]`, `bridge_keys[]`, `knowledge_formatted`), `lesson_overview`.

**The proof contract (definition of done):** quizzes — 47/48 lessons serve 8 valid questions; bridge keys —
every lesson's `doc_keys` returns DB2 `count ≥ 1`, top score ≥ floor, owning-area match, **shown live with
numbers.** "No error" is not proof.

---

## 12. Ownership model

```mermaid
flowchart LR
    subgraph ENG["Engineering (Woz) — pipeline repo"]
      E1["Tooling, Firestore layout, schemas, gates"]
      E2["Keys present, well-formed, document-level, verified"]
    end
    subgraph CFI["Daniel (CFI)"]
      C1["Which regs/citations are correct"]
      C2["Media assets (audio/video)"]
    end
    subgraph APP["App team — app repo"]
      A1["Flashcard UI, quiz router, tutor, unlock gates"]
      A2["Consumes artifacts; never authors content"]
    end
```

When a citation is ambiguous, engineering **stops and asks Daniel** — never guesses a reg into a gate.

---

## 13. Current state & active remediation (v2.8)

The pipeline is live and teaching (34 Area I lessons), but two threads are mid-fix. Full task breakdown:
`_claude_artifacts/2026-06-16_quiz-and-bridge-key-pipeline-fix/dev-story_curriculum-pipeline-fix.md`.

- **Thread 1 — Quizzes:** 14 lessons are dark (Areas III/VI/VII/IX/XI + `I_H_04`). Cause = the deleted
  wrong tool + drift between the pipeline copies (canonical, citations filled) and the app copies (had
  `null` citations). Fix = delete the wrong tool, fix the Windows crash, verify + sync pipeline → app,
  remap `I_H_04` perspectives, fix `I_F_01`'s illegal 5th option, re-ingest, prove live.
- **Thread 2 — Bridge keys:** the schema guard exists but the production re-import bypasses it. Fix = wire
  the guard into the write path, unify on the LLM extractor, add the DB2-vocab hard check, fix paths,
  regenerate Area IX, re-import, prove with live hit counts.
- **Overlap:** Area IX (`IX_B_01`, `IX_C_01`) is broken on both — fix once across both threads.

### Locked decisions (2026-06-16)
1. Pipeline repo is **canonical**, kept separate from the app; sync is **pipeline → app**; keep the
   instruction docs current with findings.
2. `I_H_04` is not special — fix it like any bank and bring a canonical copy into the pipeline.
3. `I_F_01` — fix the 5th option the best way (drop weakest distractor or split) in the canonical copy.
4. Delete broken pre-scope artifacts (e.g. `upload_quiz_banks.py`) — don't neuter-and-keep.
5. Bridge-key extractor → one path (LLM + guard), top industry standard, no shortcuts.
6. Add a hard DB2-vocabulary membership check.

---

## 14. Definition of done (the standing bar for every lesson & batch)

- [ ] Quiz: 8 valid questions served from `quiz_banks/{id}/questions` (dry-run passes the real schema).
- [ ] Flashcards: every RKP has `knowledge_formatted` (or a knowingly-accepted raw fallback).
- [ ] Bridge keys: non-empty, document-level `doc_keys` in DB1 `structData`, in DB2 vocabulary.
- [ ] Proven live: DB1→DB2 returns `count ≥ 1`, score ≥ floor, owning-area match — **numbers shown.**
- [ ] Citations verified in-scope by Daniel; none invented.
- [ ] Instruction docs updated with anything new learned.

---

## 15. Appendix — file map (verified)

**Pipeline repo (this repo):**
- `curriculum_components/curriculum_modules/` — master modules
- `curriculum_components/rkp_manifests/*_rkp.json` — RKP manifests (47)
- `curriculum_components/quiz_banks/*_quiz.json` — quiz banks (47, canonical, citations filled)
- `curriculum_components/scripts/generate_knowledge_formatted.py` — flashcard formatter
- `src/utils/generate_metadata.py` · `src/utils/schema.py` · `src/gcp/reimport_with_metadata.py`
- `_01_My/instruction_docs/` — the six guides

**App repo (`AGY_AVIATIONCHAT`):**
- `scripts/ingest_quiz_banks.py` — quiz ingest tool
- `backend/schemas/quiz.py` — real quiz schema
- `backend/services/quiz_bank_service.py` · `backend/routers/quiz.py` — read/serve path
- `backend/tools/librarian.py` (`_search_db2_bridge_hop`) · `scripts/patch_db2_metadata.py` — DB2 tags
- `frontend/src/components/lesson/FlashcardDeck.tsx`, `FlashcardCard.tsx` — flashcard UI

> **Living document.** Update this PRD whenever the pipeline changes — it is the single map the team and the
> app branches navigate by.
