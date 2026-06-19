---
IsArtifact: true
ArtifactMetadata:
  title: Curriculum RAG Wiring — Walkthrough
  type: walkthrough
  date: 2026-06-18
---

# Curriculum RAG Wiring — Walkthrough

## What this session did

Took the curriculum RAG from "authored but unwired" to "cleaned, staged, and ready to go live,"
grounded entirely in the **live** stores (verified 2026-06-18, never config files). All transforms are
done and proven **offline**; the four live writes are built as gated `--execute` tools awaiting Daniel's
trigger.

## The diagnosis (verified, not assumed)

- DB1 `aviation-curriculum-v2` = 184 docs, keys markdown-corrupted (231 with `**`/parens), 12 Area IX empty.
- DB2 `aviation-library-v2` = 16 docs, **no `document_tags` field** → the app's bridge filter matched nothing.
- The app (`librarian.py:246`) filters DB2 on the **RKP manifest `bridge_keys`**, exact `document_tags: ANY()`.
- `schema.py` `DB2_VOCABULARY` was fictional (~50 invented tokens); the curriculum cites ~40 docs, DB2 had 16.

## What changed, by workstream

- **WS-A — vocabulary & schema.** `scripts/derive_db2_vocabulary.py` derives the vocabulary from the live
  DB2 (no hand-authoring). Rewrote `src/utils/schema.py`: live vocabulary, `normalize_key`/`is_garbage`/
  `to_family`/`is_document_level`/`to_document_level`/`coverage`, and a `clean_keys` validator that strips
  corruption but keeps every real reference. Shared tag logic in `src/utils/db2_tags.py`.
- **WS-B — DB2 buildout.** Confirmed + downloaded 8 current-edition FAA PDFs (faa.gov) into
  `curriculum_components/faa_docs/` (365 MB, integrity-checked). `src/gcp/import_db2_docs.py` (gated)
  uploads → INCREMENTAL-imports → patches **rich** `document_tags` (exact + family + curriculum edition
  variants), so the app's exact filter matches across edition suffixes with no app-code change.
- **WS-C — DB1 key repair.** `src/gcp/reimport_db1_keys.py` (gated) pulls the 184 live docs, cleans keys,
  augments sub-document refs with their document-level token, fills the 12 Area IX from their authored
  sidecars, validates all 184, and re-imports INCREMENTAL (upsert — no wipe).
- **WS-D — RKP manifests.** Fixed `src/gcp/upload_manifests.py` (config paths, gated) → Firestore
  `rkp_manifests`. Manifests were already clean.
- **WS-E — quiz banks.** `src/gcp/ingest_quiz_banks.py` (gated) → Firestore `quiz_banks/{lesson}/questions/{q}`
  with rotation fields; all 48 banks / 384 questions validate (47 in the first run + `PPL_PA_I_H_04`
  added as a follow-up — see "Follow-up correction" below).
- **WS-F — verification.** `src/tests/` offline gate (33 tests) + `src/gcp/probe_bridge_hop.py` live probe.
- **WS-G — docs.** Rewrote `bridge_key_guide.md` (v2.8, verified) and corrected `curriculum_lifecycle.md`.

## Actual output (pasted)

Offline test suite:
```
$ python -m pytest src/tests/ -q
.................................                                        [100%]
33 passed in 0.23s
```

DB1 key repair dry-run:
```
$ python src/gcp/reimport_db1_keys.py
Built 184 entries (target 184).
  145 lessons resolve to >=1 DB2-covered doc_key, 39 reference-only.
```

Coverage projection after the DB2 import:
```
now (16-doc DB2):  145/184
after DB2 import:  171/184
reference-only after import: 13  (AME Guide, FCC forms, legal interpretations, FAA Orders, Startle briefing)
```

Bridge probe BEFORE any live write (honest dead state — DB2 has no tags yet):
```
$ python src/gcp/probe_bridge_hop.py --limit 5
0/5 lessons returned >=1 DB2 bridge hit.
```

## Deviations from the plan

- **Area IX needed no LLM regen** — the 12 authored sidecars in `pipeline/curriculum/new/` already had
  clean, grounded keys; we clean-and-apply them.
- **Added rich-tagging + document-level augmentation** (not in the original plan) once the live data showed
  the app does *exact* matching and the curriculum cites editions/chapters the library doesn't. This is what
  makes the bridge work without touching app code.
- **INCREMENTAL, not FULL, reconciliation** everywhere — safer (no wipe risk) and correct for upsert.

## LIVE EXECUTION (run 2026-06-18/19, authorized "run them")

All writes executed. What actually happened (and what fought back):

- **Firestore landed first, clean:** 47/47 manifests, 376/376 quiz questions.
- **The Vertex imports failed — wrong `data_schema`.** I used `data_schema="custom"`; unstructured
  docs with `structData`+content URI require `data_schema="document"`. The "custom" ops failed every
  doc (DB1 184/184, DB2 8/8) instantly. INCREMENTAL means nothing was wiped.
- **The failed ops then JAMMED the queue.** Discovery Engine runs imports serially per store and the
  failed ops sat at `done=False` indefinitely; `cancel_operation` is accepted but not honored.
- **Pivot to direct document writes (bypasses the import queue entirely):**
  - DB1 keys repaired via **`update_document`** per doc (metadata-only — the right tool anyway):
    **184/184 updated, 0 corrupt, 0 empty** (verified live).
  - DB2 existing 16 tagged via `update_document`; 7 new docs created via **`create_document`**.
- **AFH hit Vertex's 200,000,000-byte per-doc cap** (it's 273 MB). Installed **pypdf** and split it
  into 4 parts (each <200 MB), all tagged `FAA-H-8083-3C`. `create_document` parses each async.

### Final live state (verified)
```
DB1: 184 docs | corrupt keys=0 | empty doc_keys=0 | resolve >=1 DB2 doc: 171/184
DB2: 27 docs  | tagged=27/27
Firestore: 48 RKP manifests + 384 quiz questions (48 banks)
Offline tests: 33 passed
```
Live bridge probe — **48/48 lessons return >=1 DB2 hit** (was 0/48), re-run 2026-06-19 after `I_H_04`:
```
$ python src/gcp/probe_bridge_hop.py
  [HIT 3] PPL_PA_I_H_04      keys=['FAA-H-8083-25', 'AIM', 'FAA-H-8083-2']
  ...
48/48 lessons returned >=1 DB2 bridge hit.
```
The 13 lessons still reference-only cite documents genuinely not in the library (AME Guide, FCC forms,
legal interpretations, FAA Orders) — kept as citations, covered by the semantic lanes.

### Follow-up correction (`PPL_PA_I_H_04`, 2026-06-19)

After the main run (which covered 47 lessons), `PPL_PA_I_H_04` surfaced as a **Firestore-only skeleton**:
its 8 questions lived ONLY in the parent doc's embedded `questions` array, never in the
`quiz_banks/{lesson_id}/questions/*` subcollection the app actually reads (`quiz_bank_service._fetch_all_questions`)
— so the app saw zero questions for it. Fix:

- Copied the canonical `PPL_PA_I_H_04` quiz + RKP from the app repo into the pipeline (now 48 lessons).
- Hardened `ingest_quiz_banks.py` to also **strip the legacy embedded `questions` array** from every
  parent doc (`firestore.DELETE_FIELD`), so the subcollection is the single source of truth.
- Re-ran `--execute`: `Ingested 384 questions across 48 lessons. Stripped legacy embedded questions
  array from 48 parent docs.` Verified: parents still carrying the array = **0**; `I_H_04` subcollection = **8**.
- Re-ran the bridge probe → **48/48** (the `I_H_04` HIT shown above).

> Note: `I_H_04`'s RKP manifest has 3 RKPs but **no `lesson_overview`** field, and the lesson has no podcast
> — both tracked as gaps in `docs/asset_registry.md` (§2 row 35, §5 inventory).

## Your Actions

**1. New dependency:** `pypdf` was installed (used to split the oversized AFH). Add it wherever this
repo tracks deps (no `requirements.txt` exists yet — consider creating one): `pypdf==6.13.3`.

**2. Optional cleanup:** an orphan `gs://aviationchat-library/v2/FAA-H-8083-3C.pdf` (273 MB, the
un-split full AFH) sits unused in the bucket — safe to delete to reclaim space. Say the word.

**3. Commit** (pipeline repo is canonical; `faa_docs/*.pdf` are gitignored via `*.pdf`):

```bash
git checkout -b fix/curriculum-rag-wiring
git add .gitignore src/ scripts/ \
  _01_My/Master_Curriculum_Pipeline.md _01_My/instruction_docs/ docs/asset_registry.md \
  _01_My/_artifacts/2026-06-18_bridge-ground-truth-fix \
  curriculum_components/quiz_banks/ curriculum_components/rkp_manifests/ pipeline/curriculum/new/
git rm --cached --ignore-unmatch src/gcp/import_db1_v2.py
git commit -m "Wire curriculum RAG: live-derived vocab, DB2 buildout (incl. split AFH) + document_tags, DB1 key repair, Firestore ingest (48 lessons incl. I_H_04 subcollection fix), docs→v2.8, verified bridge 48/48"
```

**Why these paths:** the `.gitignore` fix now tracks the canonical curriculum sources
(`curriculum_components/{quiz_banks,rkp_manifests}` + `pipeline/curriculum/new` Area IX sidecars) that
were previously ignored by the broad `*.json` rule — including the I_H_04 files brought in this session.

(Note: the dead `src/gcp/import_db1_v2.py` was deleted this session per your OK.)
