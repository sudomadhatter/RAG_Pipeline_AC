---
title: "Bridge Key Guide — How the DB1→DB2 Bridge Actually Works"
type: reference
revision: "v2.8 (rewritten 2026-06-18/19 against the LIVE stores + the real code in both repos). Corrects the earlier 2026-06-16 v2.8 draft, which described a phantom tool, a fictional vocabulary, and the wrong filter field."
audience: "Ingestion Pipeline team (this repo, owns the whole RAG layer) + any CFI authoring sources"
companion: "rkp_creation_guide.md (RKP/quiz authoring). This is the bridge-key / DB2-verification contract."
---

# Bridge Key Guide (v2.8 — verified rewrite)

> **Why this was rewritten.** The earlier v2.8 draft was measured against config files and assumptions,
> both of which lied. This rewrite was measured on 2026-06-18/19 by querying the **live** Vertex AI Search stores
> and reading the **real** `librarian.py` in the app repo. Where this doc states a fact, it was observed
> in the live data or the running code — not inferred.

---

## 1. The two stores (live, verified)

| Store | Name | Holds | Role |
|---|---|---|---|
| **DB1** | `aviation-curriculum-v2` | 184 per-ACS-element teaching docs | Pedagogy — what a student is taught |
| **DB2** | `aviation-library-v2` | the FAA source PDFs (handbooks, ACs, CFR, AIM, ACS) | Authority — the source that verifies an answer |

Both are **v2**. There is no v1 (it 404s). The team owns **both** stores, all their metadata, and
every key — the app is a pure consumer.

## 2. How the bridge actually fires (this is the part that was wrong before)

A student question hits DB1; the matched lesson's **RKP manifest** drives a second search against DB2.
The strict hop is in the app at `backend/tools/librarian.py` → `_search_db2_bridge_hop`:

```python
filter_spec = f'document_tags: ANY({quoted_keys})'   # quoted_keys = manifest.bridge_keys
```

Three facts that follow from the real code, each of which broke the bridge before this rewrite:

1. **The filter matches `document_tags` on the DB2 documents.** If a DB2 doc has no `document_tags`
   field, it can never match. *(Until 2026-06-18 NO DB2 doc had this field — the bridge matched nothing.)*
2. **The keys it filters on come from the RKP MANIFEST (`bridge_keys`), not the DB1 `structData.doc_keys`.**
   No app code reads DB1 `doc_keys`. They are a parallel, display-side reference set — keep them clean and
   correct, but understand the *filter* runs off the manifests.
3. **The match is EXACT (`ANY`), not fuzzy.** `AC 61-98D` does not match `AC 61-98E`. We solve the
   edition-suffix gap by **rich-tagging DB2** (see §4), not by hoping Vertex normalizes.

> The other DB2 lanes (`_search_db2_legal` / `_safety` / `_application`) use **no filter** — pure semantic
> search. So a missing bridge hit degrades *targeted* retrieval; it is not a total verification blackout.

## 3. The vocabulary is machine-derived, never hand-authored

`src/utils/schema.py::DB2_VOCABULARY` must always be the output of `scripts/derive_db2_vocabulary.py`,
which lists the live DB2 and runs `utils/db2_tags.extract_tags` over each filename. **Re-run it after any
DB2 change and paste the result.** A hand-written vocabulary is how v2.8 ended up listing ~50 documents
that aren't in the library.

## 4. Editions: rich tags bridge the suffix gap (no app change needed)

The curriculum cites `FAA-H-8083-25C`; the library file is `FAA-H-8083-25`. To make the app's exact filter
hit, `src/gcp/import_db2_docs.py` tags each DB2 doc with a **rich set**: its exact token, its document
*family* (`utils/schema.to_family`, edition-letter stripped), **and** every edition variant the curriculum
actually uses. So the PHAK doc carries `["FAA-H-8083-25", "FAA-H-8083-25C"]` and matches both. Tags are
kept **document-level only** (`is_document_level`) — chapter/section refs like `AIM 8-1-5` never become tags.

## 5. Keys are references too — we clean, we don't drop

Decision (Daniel, 2026-06-18): a key is also the student-facing citation, so references that aren't in DB2
(`PAVE`, FCC forms, `tfr.faa.gov`, POH sections, legal interpretations) are **kept**. The pipeline only
**cleans corruption** (`** ` bleed, `[cite: N]`, closed/unclosed `(annotation)`, orphaned `Ch 8`) via
`utils/schema.normalize_key`, and **augments** every sub-document reference with its whole-document token
(`AIM 5-1-4` → also `AIM`) so the lesson always has a matchable bridge key. Reference-only keys ride along
and are covered by the semantic lanes.

## 6. The pipeline (every tool resolves paths via `config.py`, all live writes gated by `--execute`)

| Step | Tool | What it does |
|---|---|---|
| Derive vocabulary | `scripts/derive_db2_vocabulary.py` | live DB2 → token set (paste into schema.py) |
| Build out DB2 | `src/gcp/import_db2_docs.py` | stage `curriculum_components/faa_docs/*.pdf` → GCS → INCREMENTAL import → patch `document_tags` (rich) |
| Repair DB1 keys | `src/gcp/reimport_db1_keys.py` | pull 184 live, clean + augment keys in place, INCREMENTAL upsert |
| RKP manifests | `src/gcp/upload_manifests.py` | 48 manifests → Firestore `rkp_manifests` |
| Quiz banks | `src/gcp/ingest_quiz_banks.py` | 48 banks (384 questions) → Firestore `quiz_banks/{lesson}/questions/{q}` |

> `src/gcp/import_db1_v2.py` is the OLD regex splitter (hardcoded foreign paths, writes the wrong
> `element_type` shape). It did **not** build the live store and is superseded by `reimport_db1_keys.py`.

## 7. How to PROVE it (assert on content, never on "no error")

1. **Offline gate (`src/tests/`, permanent):** `pytest src/tests/ -v` — over all 184 built entries, assert
   non-empty, document-level, corruption-free `doc_keys`. This is the test that would have caught the
   original silent Area IX empties.
2. **Live round-trip:** for a fixed key set, fire the real `document_tags: ANY(...)` filter against DB2 and
   assert `len(hits) >= 1`. An empty hit list is not `None` — assert on the count. Last run 2026-06-19:
   `probe_bridge_hop.py` → **48/48 lesson manifests return ≥1 DB2 hit** (was 0/48 before DB2 was tagged).

## 8. Coverage reality (measured 2026-06-18, post-fix)

After cleaning, Area IX fill, and the 8-document DB2 buildout: **171 / 184 lessons resolve to ≥1 DB2
document.** The remaining **13** are reference-only — they cite documents genuinely not in the library
(AME Guide, FCC Form 605, FAA legal interpretations, FAA Orders, the Startle-Response briefing). Their keys
stay as citations; the semantic lanes cover the content. Growing DB2 with those sources is the lever to
push past 171 — re-run §3 and §8 after.

## 9. Owner line
Pipeline team: both stores, all keys/tags, the tooling, the vocabulary. **Daniel (CFI):** which FAA
citation is *correct* for a piece of content. When a citation is ambiguous, stop and ask — never let the
model guess into a key.
