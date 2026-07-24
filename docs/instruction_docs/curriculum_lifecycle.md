---
title: "Curriculum Lifecycle + Coverage Map"
type: instruction
date: 2026-06-16
audience: "Ingestion Pipeline team, Daniel (CFI), Woz (app side)"
owner_split: "Content/data artifacts = ingestion team. Rendering/serving/UI = app team. Media assets + which citations are correct = Daniel."
companion: "Sits above the four authoring guides in this folder — it is the index that ties them together."
---

# Curriculum Lifecycle + Coverage Map

> **The bird's-eye view.** Every other doc in this folder governs *one* artifact. This one shows the
> *whole* surface: what a lesson is made of, who owns each piece, which guide governs it, and what
> forces a re-build. Read `get_back_on_track.md` for the current recovery work; read this when you
> need to know "where does X fit, and is it covered?"

> ### ⚠️ Verified & corrected (2026-06-18, measured against the LIVE stores — aligns with bridge_key_guide v2.8)
> Earlier notes here described tools and a mechanism that don't match reality. Corrections:
>
> 1. **The DB1→DB2 bridge filters on the RKP MANIFEST `bridge_keys`, not DB1 `structData.doc_keys`**
>    (`app: backend/tools/librarian.py::_search_db2_bridge_hop`), and it matches the DB2 field
>    `document_tags` — which had to be created (no DB2 doc had it before 2026-06-18). The phantom
>    `src/gcp/reimport_with_metadata.py` referenced in older drafts **does not exist**. The real DB1 writer
>    is `src/gcp/reimport_db1_keys.py` (pull-clean-augment-upsert); the live store was built by the LLM
>    extractor, not a regex. See `bridge_key_guide.md` v2.8 for the verified mechanism.
> 2. **Quiz ingest is `src/gcp/ingest_quiz_banks.py`** (this repo) → Firestore `quiz_banks/{lesson}/questions/{q}`.
>    The old `src/gcp/upload_quiz_banks.py` (wrong layout) is superseded.

---

## 1. The whole pipeline in one flow

Everything derives from the **master-module markdown**. From it, three machine artifacts are produced
in parallel, then everything is ingested to two stores.

```
  ┌─────────────────────────────────────┐
  │  MASTER-MODULE MARKDOWN              │   curriculum_modules/Area X Task Y PPL.md
  │  (the "Task Markdown" — the source)  │   ← human-authored
  └───────────────┬─────────────────────┘
                  │
        ┌─────────┼──────────────────────────────────┐
        ▼         ▼                                   ▼
  ┌───────────┐  ┌──────────────────────────┐  ┌──────────────────────┐
  │ RKP        │  │ QUIZ BANK                 │  │ BRIDGE-KEY METADATA   │
  │ MANIFEST   │  │ 8 questions               │  │ reg_keys / doc_keys   │
  │            │  │                           │  │ (LLM-extracted)       │
  │ • RKPs     │  └──────────────┬────────────┘  └───────────┬──────────┘
  │ • overview │                 │                            │
  │ • far_refs │                 │                            │
  └─────┬──────┘                 │                            │
        │  run generate_knowledge_formatted.py                │
        ▼                        │                            │
  ┌───────────────┐              │                            │
  │ FLASHCARDS    │              │                            │
  │ (knowledge_   │              │                            │
  │  formatted)   │              │                            │
  └─────┬─────────┘              │                            │
        │                        │                            │
        ▼                        ▼                            ▼
  ┌──────────────────────────────────────┐   ┌──────────────────────────────┐
  │ FIRESTORE                             │   │ VERTEX AI SEARCH              │
  │ • quiz_banks/{lesson}/questions/{q}   │   │ • DB1 aviation-curriculum-v2  │
  │ • RKP manifests / lesson cache        │   │   (structData: reg/doc keys)  │
  │   (flashcards served from here)       │   │ • DB2 aviation-library-v2     │
  └──────────────────────────────────────┘   │   (FAA PDFs — verification)   │
                                              └──────────────────────────────┘
```

Media assets (audio/video/notes) hang off the manifest but are produced by a **separate process**
(see the table) — they are not part of the team's authoring loop.

---

## 2. The artifact / owner / guide / trigger table

This is the heart of the map. Seven artifacts per lesson:

| # | Artifact | Where it lives | Who authors it | Who renders / consumes it | Governing guide | Re-build trigger |
|---|---|---|---|---|---|---|
| 1 | **Master-module markdown** (Task Markdown) | `curriculum_components/curriculum_modules/Area X Task Y PPL.md` | Ingestion team | The metadata extractor (machine) | `rkp_creation_guide.md` §4 (thin — see §4 below) | Source facts/regs change |
| 2 | **RKP manifest** (RKPs, `lesson_overview`, `far_references`, `bridge_keys`, `knowledge`) | `curriculum_components/rkp_manifests/PPL_PA_*_rkp.json` | Ingestion team | Specialist tutor + flashcard UI | `rkp_creation_guide.md` | Any knowledge/ACS change |
| 3 | **Flashcards** (`knowledge_formatted`) | a field inside the RKP manifest; written by `curriculum_components/scripts/generate_knowledge_formatted.py` (Gemini 2.5 Pro) | Ingestion team (run the script) | **App** — `FlashcardDeck` / `FlashcardCard` UI | **`flashcard_creation_guide.md`** | Whenever `knowledge` changes |
| 4 | **Quiz bank** (8 questions) | `curriculum_components/quiz_banks/PPL_PA_*_quiz.json` | Ingestion team | App quiz router + tutor | `quiz_authoring_guide.md` | RKP facts change |
| 5 | **Bridge keys** — DB1 `structData.doc_keys` (display refs) + DB2 `document_tags` (the match target) + RKP manifest `bridge_keys` (what the app filters on) | DB1 via `src/gcp/reimport_db1_keys.py`; DB2 tags via `src/gcp/import_db2_docs.py`; manifests via `src/gcp/upload_manifests.py` | Ingestion team (pipeline) | The DB1→DB2 RAG verification hop | `bridge_key_guide.md` (v2.8) | Sources/regs change |
| 6 | **Media assets** (`audio_file`, `video_file`, `notes_file`) | referenced in the RKP manifest | **Separate process / Daniel** (NOT the team) | App lesson player | none (out of team scope) | Overview re-recorded |
| 7 | **Curriculum Key** (ACS entries) | the curriculum key (Step 3, "Manual" in `rkp_creation_guide.md`) | Ingestion team / Woz | Lesson planner / mastery map | none (manual step) | New lesson added |

---

## 3. Where it all lands — two destinations

- **Firestore** (`aviationchat-database`): the per-lesson quiz subcollection the app *reads*
  (`quiz_banks/{lesson_id}/questions/{q}` — written with `seen_by`/`last_seen_at` rotation fields), plus
  RKP manifests / lesson cache. **Flashcards are served from here**, via the app's flashcard-decks endpoint.
  Ingest with the pipeline tool — `src/gcp/ingest_quiz_banks.py --execute` (validates structure, writes the
  subcollection + `seen_by`/`last_seen_at`, merge-upsert by question id). Note: questions must land in the
  **subcollection** the app reads, not only an embedded array on the parent doc — that exact gap left
  `I_H_04` dark until 2026-06-19. The old `src/gcp/upload_quiz_banks.py` is **deleted**.
- **Vertex AI Search**: **DB1** `aviation-curriculum-v2` (the teaching store — carries the structData
  `reg_keys`/`doc_keys`) and **DB2** `aviation-library-v2` (the FAA PDF library used to verify
  answers). The bridge keys are what connect a DB1 lesson to its DB2 source — empty keys = a silent
  unverifiable answer (`bridge_key_guide.md`).

---

## 4. Coverage — what has a guide, and what doesn't (the "did I miss anything?" answer)

| Artifact | Guide status |
|---|---|
| RKP manifest | ✅ `rkp_creation_guide.md` |
| Quiz bank | ✅ `quiz_authoring_guide.md` |
| Bridge keys / metadata | ✅ `bridge_key_guide.md` |
| Flashcards | ✅ `flashcard_creation_guide.md` (**new** — closes the prior gap) |
| Master-module markdown | ⚠️ **Thin.** Covered only by `rkp_creation_guide.md` §4 ("follow the gold-standard example"). Either way the real requirement is *content completeness*: **the markdown must explicitly name its FAA regs and documents** (in a clean `Bridge Keys` block), or `doc_keys` comes back empty. (Corrected 2026-07-22 — this paragraph previously described a phantom regex extractor `reimport_with_metadata.py`, contradicting this doc's own v2.8 banner above. **That script does not exist.**) The real DB1 writer is `src/gcp/reimport_db1_keys.py`, and the live store was built by the LLM extractor — but format still matters: name regs/documents at document granularity in a clean `Bridge Keys` block or `doc_keys` comes back empty. Note the schema gate only catches an empty `doc_keys` once it is **wired into the write path** (v2.8 task) — until then an empty one still ships silently. |
| Media assets (audio/video/notes) | ⛔ **No guide — and not the team's job.** Owned by a separate process / Daniel. |
| Curriculum Key | ⛔ **No guide.** A manual step today. Low risk, but undocumented. |

> **Note (corrected v2.8, 2026-06-19):** Area IX was empty in DB1 because the keys never reached the live
> store — not a heading/regex mismatch (the live DB1 was LLM-extracted, with `type`/`ancestral_context`).
> It was fixed by cleaning + filling keys from the authored Area IX sidecars and writing them with
> `reimport_db1_keys.py` (`update_document`). The durable rule still holds: **name the regs/documents at
> document granularity in the source** (`FAA-H-8083-25C`, not a chapter), and let
> `derive_db2_vocabulary.py` keep the vocabulary honest against the live DB2.

---

## 5. Upkeep cascade — one edit, these ripples

- **Edit an RKP `knowledge` field** ⇒ re-run `generate_knowledge_formatted.py` (card back) **and**
  re-check that RKP's quiz questions (the quiz author reads `knowledge` — the two-way contract).
- **Edit the master markdown's sources** (regs/documents named in the prose / `Bridge Keys` block) ⇒
  regenerate the metadata so the bridge keys match, then repair DB1 in place via
  `src/gcp/reimport_db1_keys.py --execute` (`update_document`, queue-free) — and prove the DB1→DB2 hit with
  `src/gcp/probe_bridge_hop.py` (see `bridge_key_guide.md` §5/§7).
- **Add or change a quiz bank** ⇒ re-ingest with `src/gcp/ingest_quiz_banks.py` (dry-run, then `--execute`; it writes the `quiz_banks/{lesson}/questions/{q}` subcollection the app reads — never the retired `scripts/`-level or app-repo variants).
- **Add a brand-new lesson** ⇒ all of the above **plus** the Curriculum Key entry (artifact #7).

---

## 6. The ownership line (one sentence each)

- **Ingestion team:** authors the *content/data* — master markdown, RKP manifest, flashcards (run
  the formatter), quiz bank, bridge-key metadata, Curriculum Key. Owns the pipeline/tooling/schema.
- **App team (Woz, app repo):** owns *rendering and serving* — the flashcard UI, the quiz router,
  the tutor, the ingest tool, the unlock gates. Consumes the team's artifacts; never authors content.
- **Daniel (CFI):** owns *truth* — which FAA citations are correct, and the media assets
  (audio/video). When a citation is ambiguous, the team stops and asks him.

---

## 7. The doc set (reading order)

0. `../Master_Curriculum_Pipeline.md` — the master PRD: the whole pipeline, the flow, mermaid diagrams,
   tooling, schemas, current state. Read it first for the big picture; the docs below are the per-artifact detail.
1. `get_back_on_track.md` — START HERE: the current recovery work (quiz thread).
2. `bridge_key_guide.md` — the DB1→DB2 bridge-key / metadata contract.
3. `quiz_authoring_guide.md` — the quiz quality bar (read §3 — two SJT archetypes).
4. `rkp_creation_guide.md` — RKP manifest mechanics + schema.
5. `flashcard_creation_guide.md` — the card derived from each RKP.
6. **`curriculum_lifecycle.md`** — this map: the whole surface + coverage.
