---
IsArtifact: true
ArtifactMetadata:
  title: Curriculum RAG — Upload & Wire Everything (Verified Ground-Truth Plan)
  type: implementation_plan
  date: 2026-06-18
---

# Curriculum RAG — Upload & Wire It All, End to End

> **STATUS: awaiting Daniel's explicit "approved." The two gating decisions are now locked (below);
> the only thing left before execution is your thumbs-up on the FAA download shortlist + "approved."**
>
> Every number below was measured on **2026-06-18** against the **live** Vertex stores and the **real**
> code/manifests in both repos. Nothing is assumed.

## The job (your definition of done)

We own the entire RAG layer. The content is authored. The job is: **every lesson's full artifact set —
the DB1 teaching doc, its DB2 FAA sources, its RKP manifest, and its quiz bank — is uploaded to the right
store and *proven* to resolve, so the app can pull it and teach a student.** The app is a pure consumer.

## Decisions locked (Daniel, 2026-06-18)

1. **Stock DB2 with the critical FAA documents.** Not all ~25 — the important ones. Stage the PDFs in
   `curriculum_components/faa_docs/`. I find each document's **most up-to-date edition on faa.gov**
   (authoritative — no guessed edition), you confirm the set, then we upload + import to DB2.
2. **Keep every reference key.** The keys are also the student-facing references, so non-database items
   (PAVE/IMSAFE, FAA forms, weather sites like NOTAMs / tfr.faa.gov / aviationweather.gov, aircraft POH
   sections, legal interpretations) are **kept as reference keys** even though they're not in DB2. We only
   strip the **corruption** off them (`**` prefixes, `[cite: 1453]`, orphaned `Ch 8`/`Ch 9)` fragments).
   The bridge filter simply uses whichever keys exist in DB2; the rest ride along as citations.

## The four destinations and where each stands (verified)

| Artifact | Count | Store | Current state |
|---|---|---|---|
| **DB1 teaching docs** (per ACS element) | 184 | Vertex `aviation-curriculum-v2` | Uploaded, keys **corrupt** (231 with `**`/parens) + **12 Area IX empty** |
| **DB2 FAA source library** | **16** | Vertex `aviation-library-v2` | Missing the critical handbooks/ACs below; **no `document_tags`** so the bridge filter matches nothing |
| **RKP manifests** (per lesson) | 47 | Firestore | `bridge_keys` corrupt; Firestore state unverified |
| **Quiz banks** (per lesson, 8 Q) | 47 | Firestore `quiz_banks/{lesson}/questions/{q}` | Authored; ingest state unverified |

## The FAA download shortlist — confirm this set

Measured by how many lessons/RKPs cite each. Editions shown are my best current knowledge and will be
**re-confirmed against faa.gov at fetch time** before download.

**Tier 1 — core, high-coverage (strongly recommend):**

| Document | Edition (confirm at fetch) | Used by |
|---|---|---|
| Airplane Flying Handbook | FAA-H-8083-3C | ~20 lessons |
| Aviation Weather Services | AC 00-45H | ~13 RKPs |
| Stall & Spin Awareness | AC 61-67C | ~9 lessons |
| Instrument Flying Handbook | FAA-H-8083-15B | ~6 |
| Minimum Equipment / inop equipment (Part 91) | AC 91-67 | ~6 |
| Pilots' Role in Collision Avoidance | AC 90-48E | ~5 |
| Weight & Balance Handbook | FAA-H-8083-1B | ~4 |
| Private Pilot – Airplane ACS | FAA-S-ACS-6C | ~3 |

**Tier 2 — valuable, your call:**

| Document | Edition (confirm) | Used by |
|---|---|---|
| Electronic Flight Bags (consolidate AC 91-78 / AC 120-76) | AC 91-78 | ~4 |
| Mitigating Runway Overrun Risk | AC 91-79A | ~3 |
| Aviation Weather | AC 00-6B | ~1 |
| Cockpit Displays of Digital Weather | AC 00-63A | ~2 |
| Airworthiness Directives | AC 39-7D | ~1 |
| Maintenance Records | AC 43-9C | ~1 |
| Aeronautical Chart User's Guide | current | ~1–4 |
| Certification: Pilots & Instructors (endorsements) | AC 61-65H | ~1 |

**Tier 3 — keep as reference, do NOT add to DB2** (frequently-updated, regional, or already covered):
Chart Supplement U.S. (56-day regional cycle), Pilot/Controller Glossary (already inside AIM), FAA Order
JO 7110.65 (controller-facing), plus all forms / websites / legal interpretations / aircraft POHs.

> Tell me to trim or add anything. I'll fetch only what you confirm.

---

## Workstreams

### WS-A — Vocabulary, schema, coverage (derived from the live library)
- `scripts/derive_db2_vocabulary.py` emits DB2's real token set; rebuild `schema.py` `DB2_VOCABULARY` from
  it (kill the fictional list), document-**family** match (`AC 61-98D`≈`AC 61-98E`, `…-25C`≈`…-25`).
- Schema now validates **cleanliness + format** (no `**`, no garbage, document-level) and emits a
  **coverage report** (in-DB2 vs reference-only). It does **not** hard-reject reference-only keys
  (decision #2). Re-run derivation every time DB2 grows so the vocabulary stays a fact.

### WS-B — Build out DB2 (the real unblock)
- For each confirmed document: resolve the current edition on faa.gov, download to
  `curriculum_components/faa_docs/`, upload to the `aviationchat-library` bucket, import into
  `aviation-library-v2`. Then apply **`document_tags`** to every DB2 doc (the `patch_db2_metadata.py`
  logic — never successfully run; live DB2 has none). Re-run WS-A after.

### WS-C — Clean DB1 keys + fill the gaps, re-import
- Normalizer strips `**`/parentheticals/`[cite:]`/orphaned-`Ch` garbage while **preserving the real
  reference**. Regenerate the **12 empty Area IX** via the LLM extractor (temp 0.0). Validate all 184
  through the cleanliness schema. Fix `import_db1_v2.py`'s hardcoded `c:\Sudo_Hatter_Command\...` paths to
  `config.py` resolution + schema-validate before writing. **FULL re-import is gated — your trigger.**

### WS-D — RKP manifests → clean + ingest
- Same normalize (keep references) across all 47 manifests' `bridge_keys`. Ingest manifests to Firestore.

### WS-E — Quiz banks → ingest
- Ingest all 47 quiz banks to Firestore `quiz_banks/{lesson_id}/questions/{q}` with the validated layout,
  idempotent by question id.

### WS-F — Prove it, end to end (gated live writes)
- Offline: cleanliness gate + coverage report green over all 184; quiz/manifest schema-valid. Paste output.
- Live, per lesson: DB1 returns the doc; the `document_tags: ANY(...)` bridge hop returns **≥1** real DB2
  hit for keys that should resolve; RKP + quiz present in Firestore. Live Vertex re-import and Firestore
  writes are **your trigger**, on dry-run proof.

### WS-G — Correct the docs to verified reality
- Rewrite `bridge_key_guide.md` + `curriculum_lifecycle.md`: v2 stores; DB2 needs `document_tags`; app
  filters on **manifest `bridge_keys`**; the real (growing) vocabulary; family-level match; references-are-
  kept policy. Remove the phantom `reimport_with_metadata.py` and the fictional vocabulary.

---

## Files touched (this repo)

| File | Action | WS |
|---|---|---|
| `scripts/derive_db2_vocabulary.py` | NEW | A |
| `src/utils/schema.py` | MODIFY (real vocab, cleanliness+coverage, family match) | A |
| `curriculum_components/faa_docs/*.pdf` | NEW (confirmed set) | B |
| `src/gcp/` import tooling (DB2 import, `document_tags` patch) | MODIFY/NEW | B |
| `src/utils/generate_metadata.py` | MODIFY (normalizer, Area IX regen) | C |
| `src/gcp/import_db1_v2.py` | MODIFY (config paths, schema-validate) | C |
| RKP-manifest + quiz ingest tooling | MODIFY/NEW | D, E |
| `src/tests/*` (cleanliness gate, coverage, probe) | NEW | F |
| `_01_My/instruction_docs/bridge_key_guide.md`, `curriculum_lifecycle.md` | MODIFY | G |
| artifacts: `walkthrough.md`, `task-list.md` | NEW | — |

## Hard stops I will respect
- No project file touched until you say **"approved."**
- Live Vertex re-import and Firestore writes are **not** auto-run — dry-run proof first, your explicit go.
- I will **not** invent an FAA citation or download an edition I haven't confirmed on faa.gov.
- No `git commit` / `git push` — I provide the commands.
