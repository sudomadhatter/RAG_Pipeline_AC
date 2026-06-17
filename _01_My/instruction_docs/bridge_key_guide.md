---
title: "Bridge Key Guide — How the Meta Keys Work and How to Get Them Right"
type: reference
date: 2026-06-16
revision: "v2.8 (2026-06-16) — measured against the live code: schema is ALREADY hardened, but the production re-import tool bypasses it AND uses a regex extractor. v2 — corrected root cause (LLM extractor + schema-allows-empty, NOT a regex/format mismatch)"
audience: "Ingestion Pipeline team (this repo) + any CFI authoring a Master Document"
companion: "rkp_creation_guide.md (how to build RKPs/quizzes). This guide is the bridge-key / DB2-verification contract that rkp_creation_guide does not yet cover."
---

# Bridge Key Guide — The Meta Keys (corrected v2.8)

> **Read this first (correction notice).** An earlier draft of this guide blamed the empty Area IX
> bridge keys on a **markdown format / regex mismatch** (`#### 4.` vs `### 4.`, `**Regs**:` vs
> `**Regs:**`). **That was wrong and it sent people chasing the wrong fix.** The metadata is extracted
> by an **LLM**, not a regex — so markdown punctuation is not the mechanism. The real causes are in §3.
> Clean, consistent formatting still *helps the model*, but it is not the lever. This v2 is the accurate version.

> ### ⚠️ v2.8 correction (2026-06-16, measured against the live code — read before acting)
> Two things in v2 are now out of date, verified by reading the repo:
>
> 1. **The schema is ALREADY hardened.** `src/utils/schema.py` already has
>    `doc_keys: List[str] = Field(min_length=1)` + a strip-`N/A` validator + a non-empty validator +
>    a chapter-level warning (schema.py:33, 36-68), and `src/utils/generate_metadata.py` already has the
>    post-generation check. So §3.2 and §6 step 1 ("the single highest-value fix is to make `doc_keys`
>    non-empty-required") are **done**. Do not redo them.
> 2. **The real, still-open bug is that the guard is wired to nothing.** The production re-import tool
>    `src/gcp/reimport_with_metadata.py` imports **nothing** from `utils.schema` — it builds the Vertex
>    JSONL `structData` dicts by hand (reimport_with_metadata.py:155-170) and ships them straight to DB1.
>    An empty `doc_keys` **still ships silently** on the path that actually writes DB1.
> 3. **"Extractor is an LLM, not a regex" is only half true.** There are **two** extractors: the LLM one
>    (`generate_metadata.py`, standalone) and a **regex** one inside the production import tool
>    (`reimport_with_metadata.py:77-91`, parsing the master-doc `Bridge Keys` block). The path that
>    writes DB1 in production is the **regex** — so for *that* path, clean markdown *is* a lever.
> 4. **`reimport_with_metadata.py` can't even run here** — it hardcodes another machine's repo root and
>    SA path (`c:\AGY-Projects\ingestion-Pipeline-AC\...`, reimport_with_metadata.py:10, 20) and reads a
>    `pipeline/curriculum/new/` dir that doesn't exist in this repo.
>
> **Locked decisions (Daniel, 2026-06-16), top industry standard, no shortcuts:** unify on **one**
> extractor — the LLM path feeding the hardened schema guard — and **retire the regex extractor**; **wire
> the guard into the production write path** so empty `doc_keys` fails loud at ingest; **fix the hardcoded
> paths** (`Path(__file__)` + `GOOGLE_APPLICATION_CREDENTIALS` resolution); and add a **hard DB2-vocabulary
> membership check** (a `doc_key` not in DB2's `document_tags` set fails the gate, not just a warning).
> Full task breakdown in `_claude_artifacts/2026-06-16_quiz-and-bridge-key-pipeline-fix/implementation_plan.md`.

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

## 3. The REAL root cause (verified in this repo's code — updated v2.8 2026-06-16)

1. **There are TWO extractors, and the production one is a regex.** `src/utils/generate_metadata.py`
   (LLM, Gemini 2.5 Flash, structured output) is the *standalone* extractor. But the tool that actually
   writes DB1, `src/gcp/reimport_with_metadata.py`, does **not** call it — it **regex-parses** the
   master-doc `Bridge Keys` block (`Regs:` / `Docs:` lines, reimport_with_metadata.py:77-91). So on the
   production path, thin/ambiguous/"N/A"/absent bridge text → empty keys, **and markdown cleanliness does
   matter for that path.** *(Decision: we are unifying on the LLM extractor + guard and retiring the
   regex — see the v2.8 banner. Once that lands, this item becomes "the LLM extractor, validated.")*
2. **The schema is now hardened — but the production write path BYPASSES it (this is the live bug).**
   `src/utils/schema.py` → `CurriculumStructData` already enforces it:
   ```python
   reg_keys: List[str] = Field(default_factory=list)        # empty allowed (non-regulatory topics)
   doc_keys: List[str] = Field(min_length=1)                 # empty FAILS — hardened
   # + strip_invalid_keys (drops 'N/A'/blank) + validate_doc_keys_non_empty + warn_chapter_level_keys
   ```
   So the validation exists. **The problem is `reimport_with_metadata.py` imports nothing from
   `utils.schema` and builds the JSONL by hand (reimport_with_metadata.py:155-170)** — an empty
   `doc_keys` from the regex parser sails straight to DB1, never touching the guard. **The single
   highest-value fix is no longer "harden the schema" (done) — it is "wire the guard into the import
   path so it actually runs."**
3. **Keys must match DB2's tag vocabulary or they hit nothing.** The app filters DB2 with
   `document_tags: ANY(<your keys>)` (app repo: `backend/tools/librarian.py:237`). DB2's `document_tags`
   are **document-level** tokens, derived from PDF filenames by the app repo's
   `scripts/patch_db2_metadata.py`: `14 CFR 91`, `FAA-H-8083-25C`, `AIM`, `AC 61-98D`. A fine-grained
   key (`FAA-H-8083-25C Chapter 17`, `AIM 8-1-5`) will **not** strict-match. Author at **document granularity**.
   *(v2.8 decision: `schema.py` already lists the `DB2_VOCABULARY` set but currently only **warns** on
   chapter-level keys — we are upgrading this to a **hard membership check** so a `doc_key` outside DB2's
   tag vocabulary FAILS the gate, closing the "passes `min_length` but hits nothing in DB2" gap.)*

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

1. **Wire the guard into the write path (the actual fix — the schema is already hard).** The schema
   (`src/utils/schema.py`) and the standalone LLM check (`src/utils/generate_metadata.py`) already reject
   empty `doc_keys`. What's missing is that the production tool `src/gcp/reimport_with_metadata.py`
   bypasses them. Make that tool validate every entry through `CurriculumLessonSchema`/`CurriculumStructData`
   before writing JSONL, fix its hardcoded `c:\AGY-Projects\...` paths (`Path(__file__)` +
   `GOOGLE_APPLICATION_CREDENTIALS` resolution), retire its regex extractor in favor of the LLM path, and
   add the hard DB2-vocabulary membership check (§3.3). Now an empty/invalid `doc_keys` fails LOUD at ingest.
2. **Clean the source:** ensure the master module (`curriculum_components/curriculum_modules/Area 9
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
ROOT BUG  (v2.8) schema.py is HARDENED, but reimport_with_metadata.py bypasses it (builds JSONL by hand,
          regex extractor, hardcoded paths) → empty doc_keys still ships silently on the real write path
THE FIX   (v2.8) wire the guard into reimport_with_metadata.py + retire the regex (unify on LLM extractor) +
          fix hardcoded paths + hard DB2-vocab membership check + regenerate + re-import + PROVE
KEYS      document-level only: 14 CFR 91 · FAA-H-8083-25C · AIM · AC 61-98D   (no chapter/section on the key)
PROVE     live DB1→DB2 count>=1 AND score>=floor AND owning-area match  (NOT "no error")
```

**This repo (pipeline):** `src/utils/generate_metadata.py`, `src/utils/schema.py`, `src/gcp/reimport_with_metadata.py`.
**App repo (consumer, for reference):** read path `backend/tools/librarian.py:237` `_search_db2_bridge_hop`;
DB2 tag source `scripts/patch_db2_metadata.py` (`extract_tags`).
**Owner:** pipeline/format → Woz · content/citations → Daniel (CFI).
