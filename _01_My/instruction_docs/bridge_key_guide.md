---
title: "Bridge Key Guide — How the Meta Keys Work and How to Get Them Right"
type: reference
date: 2026-06-14
revision: "v2 — corrected root cause (LLM extractor + schema-allows-empty, NOT a regex/format mismatch)"
audience: "Ingestion Pipeline team (this repo) + any CFI authoring a Master Document"
companion: "rkp_creation_guide.md (how to build RKPs/quizzes). This guide is the bridge-key / DB2-verification contract that rkp_creation_guide does not yet cover."
---

# Bridge Key Guide — The Meta Keys (corrected v2)

> **Read this first (correction notice).** An earlier draft of this guide blamed the empty Area IX
> bridge keys on a **markdown format / regex mismatch** (`#### 4.` vs `### 4.`, `**Regs**:` vs
> `**Regs:**`). **That was wrong and it sent people chasing the wrong fix.** The metadata is extracted
> by an **LLM**, not a regex — so markdown punctuation is not the mechanism. The real causes are in §3.
> Clean, consistent formatting still *helps the model*, but it is not the lever. This v2 is the accurate version.

---

## 0. The standing contract — what the app team needs from you (READ THIS)

> This is the durable request from the app/consumer team. This repo already owns master lessons, RKP
> manifests, quizzes, sharding, and the DB1 import — that part works. **The piece that has never been
> on the radar is the bridge-key / DB2 verification half.** From now on, treat the following as the
> definition of done for *every* lesson and *every* batch — not a one-time Area IX fix.

**Every micro-lesson shipped to DB1 (`aviation-curriculum-v2`) must satisfy ALL of:**

1. **Non-empty `doc_keys` (≥1) in DB1 `structData`.** Enforce it with a schema guard so an empty one
   **fails loudly at ingest** (today it passes silently — §3). `reg_keys` may be empty for a
   non-regulatory topic; `doc_keys` may never be.
2. **Document-level key tokens** that match DB2's `document_tags` vocabulary — `14 CFR 91`,
   `FAA-H-8083-25C`, `AIM`, `AC 61-98D`. **NOT** chapter/section granularity (`FAA-H-8083-25C (PHAK
   Ch 6)`, `AIM 8-1-5`). Chapter detail goes in the prose, never in the machine key. *(The
   `rkp_creation_guide.md` examples were corrected to this document-level form — match them.)*
3. **The manifest and the structData agree.** The RKP manifest's `far_references`/`bridge_keys` and the
   DB1 `structData` `reg_keys`/`doc_keys` describe the same sources.
4. **Proven, not assumed.** A live DB1→DB2 round-trip for the lesson's keys returns **`count >= 1`**,
   top-hit **score ≥ floor**, and the returned doc maps back to the lesson's own Area. "No error" is
   not proof (§5).
5. **The offline schema gate runs in CI** over all 184 lessons, so the next batch can't regress.

**Definition of done for a batch:** nothing is "shipped" until the live probe (#4) passes for the new
lessons and the offline gate (#5) is green. If you can't show the hit counts, it isn't done.

**Who owns what:** you (pipeline) own the keys being present, well-formed, document-level, and
verified in DB2. Daniel (CFI) owns which regs/docs are *correct* for the content. When a citation is
ambiguous, ask Daniel — don't let the model guess into an empty list.

---

## 1. What a bridge key is (60 seconds)

Two Vertex AI Search stores:

| Store | Name | Role |
|---|---|---|
| **DB1** | `aviation-curriculum-v2` | **Teaching** — the 184 micro-lessons |
| **DB2** | `aviation-library-v2` | **Verification** — the FAA PDFs (FAR/AIM, PHAK, AFH, ACs) |

A student question hits **DB1**; the matched lesson's **bridge keys** (`reg_keys` + `doc_keys`) are
used to search **DB2** for the authoritative FAA source. The final answer = pedagogy (DB1) + authority
(DB2). **Empty bridge keys → the verification step returns nothing** — an unverifiable answer that
looks fine to any test that only checks "did it error?" That silence is how Area IX (the 12
emergency-ops lessons) slipped through.

---

## 2. Bridge keys live in TWO places — keep them straight

| Where | Field names | Produced by | Read by |
|---|---|---|---|
| **RKP manifest** (`{lesson_id}_rkp.json`, per RKP) | `far_references`, `bridge_keys` | RKP authoring | the app's RKP-First Q&A path (`librarian._search_db2_bridge_hop`) |
| **Vertex DB1 `structData`** (per micro-lesson) | `reg_keys`, `doc_keys` | the **LLM metadata generator** at ingest | the DB1→DB2 hop |

**Area IX, precisely:** the **manifests were fine** (`far_references`/`bridge_keys` populated — verified),
but the **DB1 `structData.reg_keys`/`doc_keys` were empty.** So fixing the manifest by hand did nothing
for the RAG hop — the empty layer is the **Vertex `structData`**, produced by the generator below.

---

## 3. The REAL root cause (verified in this repo's code)

1. **The extractor is an LLM, not a parser.** `src/utils/generate_metadata.py` sends the master-doc
   text to **Gemini 2.5 Flash** with a structured-output schema and asks it to produce `reg_keys` /
   `doc_keys`. If the model returns empty lists — because the source bridge info was thin/ambiguous,
   said "N/A", or the step wasn't run for that batch — the keys are empty. No markdown regex is involved.
2. **The schema accepts empty SILENTLY (this is the bug that let it ship).**
   `src/utils/schema.py` → `CurriculumStructData`:
   ```python
   reg_keys: List[str] = Field(default_factory=list)   # empty is "valid"
   doc_keys: List[str] = Field(default_factory=list)   # empty is "valid"
   ```
   No `min_length`, no validator. An empty `doc_keys` passes validation and gets indexed. **This is the
   single highest-value fix:** make `doc_keys` non-empty-required so an empty one fails LOUD at ingest.
3. **Keys must match DB2's tag vocabulary or they hit nothing.** The app filters DB2 with
   `document_tags: ANY(<your keys>)` (app repo: `backend/tools/librarian.py:237`). DB2's `document_tags`
   are **document-level** tokens, derived from PDF filenames by the app repo's
   `scripts/patch_db2_metadata.py`: `14 CFR 91`, `FAA-H-8083-25C`, `AIM`, `AC 61-98D`. A fine-grained
   key (`FAA-H-8083-25C Chapter 17`, `AIM 8-1-5`) will **not** strict-match. Author at **document granularity**.

---

## 4. What "good" looks like

**In the master doc** — a clean, populated Bridge Keys block so the LLM has unambiguous source to read
(consistency *helps the model*, it is not a regex gate):

```markdown
### Bridge Keys (Metadata)
* Regs: 14 CFR 91.3, 14 CFR 91.103
* Docs: FAA-H-8083-3C, AC 120-71B
* Keywords: Emergency Authority, Memory Items, ADM, PAVE
```

Rules:
- **Docs is mandatory (≥1).** Regs may be empty for non-regulatory topics (aerodynamics, physiology) —
  but **never write the literal "N/A"**; leave it empty.
- **Use document-level tokens** that match the DB2 vocabulary (§3.3): `FAA-H-8083-25C`, `AC 61-98D`,
  `AIM`, `14 CFR 91`. Put chapter/section detail in the prose, not in the key.

**In the resulting DB1 `structData`** — non-empty, document-level:
```json
{ "reg_keys": ["14 CFR 91.3"], "doc_keys": ["FAA-H-8083-3C", "AC 120-71B"], "keywords": [...] }
```

---

## 5. How to PROVE it (the part skipped last time)

The single most dangerous shortcut is a probe that checks `response is not None`. **An empty hit list
is not `None`.** Assert on content:

1. **Offline schema gate (CI, permanent):** over all 184 DB1 docs, assert non-empty, well-formed
   `doc_keys`. This is the guard that stops the next silent batch.
2. **Live round-trip:** for each fixed key, fire the real DB1→DB2 path; assert **`len(db2_hits) >= 1`**
   AND top-hit score ≥ a defined floor AND the returned doc maps back to the queried Area (no IX→VII
   cross-wire). Network-gated; run before closing.
3. **Golden set:** freeze 2–3 hand-verified lessons → expected FAA reference as canaries.

---

## 6. Fixing Area IX (and any empty batch) — procedure

1. **Harden first (so it can't recur):** `src/utils/schema.py` → `doc_keys: List[str] = Field(min_length=1)`
   (+ a validator that strips `"N/A"`/blank and rejects if empty). Add a post-generation check in
   `src/utils/generate_metadata.py` that normalizes keys to document level and fails on empty `doc_keys`.
2. **Clean the source:** ensure the master module (`specialist_curriculum/curriculum_modules/Area 9
   Tasks B,C PPL.md`) has populated, unambiguous Bridge Keys (no "N/A").
3. **Regenerate** the metadata for the affected split lessons (`generate_metadata.py` / the curriculum
   pipeline). Confirm non-empty, document-level `reg_keys`/`doc_keys`.
4. **Re-import** to DB1 via `src/gcp/reimport_with_metadata.py` with **`FULL` reconciliation**
   (idempotent). Confirm the 12 IX docs now carry non-empty keys; doc count stays 184.
5. **Verify** with §5 (offline gate + live round-trip + golden). Spot-check the other 5 content Areas
   didn't regress.

---

## 7. Quick reference

```
LAYERS    manifest far_references/bridge_keys  AND  DB1 structData reg_keys/doc_keys  (both must be non-empty)
EXTRACTOR LLM (generate_metadata.py, Gemini 2.5 Flash) — NOT a regex
ROOT BUG  schema.py lets reg_keys/doc_keys default to [] with no validation → empty ships silently
THE FIX   doc_keys min_length=1 + drop "N/A" + document-level tokens + regenerate + re-import + PROVE
KEYS      document-level only: 14 CFR 91 · FAA-H-8083-25C · AIM · AC 61-98D   (no chapter/section on the key)
PROVE     live DB1→DB2 count>=1 AND score>=floor AND owning-area match  (NOT "no error")
```

**This repo (pipeline):** `src/utils/generate_metadata.py`, `src/utils/schema.py`, `src/gcp/reimport_with_metadata.py`.
**App repo (consumer, for reference):** read path `backend/tools/librarian.py:237` `_search_db2_bridge_hop`;
DB2 tag source `scripts/patch_db2_metadata.py` (`extract_tags`).
**Owner:** pipeline/format → Woz · content/citations → Daniel (CFI).
