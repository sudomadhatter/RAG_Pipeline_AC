---
name: bridge-key-verification
description: >
  Skill for verifying that bridge keys (reg_keys/doc_keys) in RKP manifests and
  DB1 structData are non-empty, document-level, match DB2's vocabulary, and survive
  a live round-trip probe. Activates after any RKP creation, ingestion batch, or
  when Daniel says "verify bridge keys" or "check DB1-DB2 connectivity".
---

# Bridge Key Verification Skill

> **Owner:** Woz (Agent) — pipeline-side verification.
> **Trigger:** After any RKP creation batch, after any Vertex AI ingestion, or on-demand.
> **Companion:** [bridge_key_guide.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/_docs/instruction_docs/bridge_key_guide.md) — the standing contract from the app team.

---

## 1. Why This Exists

Two Vertex AI Search stores power the RAG pipeline:

| Store | Name | Role |
|---|---|---|
| **DB1** | `aviation-curriculum-v2` | **Teaching** — 184+ micro-lessons |
| **DB2** | `aviation-library-v2` | **Verification** — FAA PDFs (FAR/AIM, PHAK, AFH, ACs) |

A student question hits DB1. The matched lesson's **bridge keys** (`reg_keys` + `doc_keys`)
are used to search DB2 for the authoritative FAA source. **Empty bridge keys → the
verification step returns nothing** — an unverifiable answer that looks fine to any test
that only checks "did it error?"

This silence is how Area IX (12 emergency-ops lessons) shipped with zero DB2 connectivity.

---

## 2. The Standing Contract (Definition of Done)

Every micro-lesson shipped to DB1 must satisfy **ALL** of:

1. **Non-empty `doc_keys` (≥1)** in DB1 `structData`. `reg_keys` may be empty for
   non-regulatory topics; `doc_keys` may **never** be.
2. **Document-level key tokens** matching DB2's `document_tags` vocabulary:
   - ✅ `14 CFR 91`, `FAA-H-8083-25C`, `AIM`, `AC 61-98D`
   - ❌ `FAA-H-8083-25C (PHAK Ch 6)`, `AIM 8-1-5` (chapter granularity)
3. **Manifest and structData agree.** The RKP manifest's `far_references`/`bridge_keys`
   and the DB1 `structData` `reg_keys`/`doc_keys` describe the same sources.
4. **Proven, not assumed.** A live DB1→DB2 round-trip returns `count >= 1`, top-hit
   `score >= floor`, and the returned doc maps back to the lesson's own Area.
5. **Offline schema gate runs** over all lessons — the next batch can't regress.

---

## 3. The Three Verification Layers

### Layer 1: Offline Schema Gate (Pre-Ingestion)

Run this BEFORE any Vertex AI import. This catches empty/malformed keys at the source.

**What to check on every RKP manifest:**

```
For each RKP in manifest.required_knowledge_points:
  ✅ bridge_keys is a non-empty list (len >= 1)
  ✅ bridge_keys contains NO chapter/section granularity
  ✅ bridge_keys contains NO literal "N/A" strings
  ✅ far_references contains NO literal "N/A" strings
  ✅ far_references uses format "14 CFR {part}.{section}" or "14 CFR Part {N}"
  ✅ bridge_keys tokens match DB2 vocabulary (see §4)
```

**What to check on DB1 structData (post-metadata-generation):**

```
For each lesson in the JSONL manifest:
  ✅ structData.doc_keys is non-empty (len >= 1)
  ✅ structData.doc_keys are document-level tokens
  ✅ structData.reg_keys contains no "N/A" or chapter-level entries
  ✅ structData.doc_keys and manifest bridge_keys describe the same sources
```

### Layer 2: Cross-Reference Consistency

The RKP manifest and the DB1 structData are produced by different processes (manual authoring
vs. LLM metadata extraction). They MUST agree:

| RKP Manifest Field | DB1 structData Field | Must Match? |
|---|---|---|
| `far_references` | `reg_keys` | YES — same regulatory citations |
| `bridge_keys` | `doc_keys` | YES — same document references |

**Root cause of past failures:** The LLM metadata generator (`src/utils/generate_metadata.py`)
extracts keys from the master module markdown. If the Bridge Keys section is thin, ambiguous,
or says "N/A", the LLM returns empty lists. The schema (`src/utils/schema.py`) silently
accepts empty `doc_keys` because `default_factory=list` has no `min_length` validator.

**The fix (already documented in bridge_key_guide.md §6):**
- `schema.py` → `doc_keys: List[str] = Field(min_length=1)`
- `generate_metadata.py` → post-generation check that normalizes keys to document level
  and fails on empty `doc_keys`

### Layer 3: Live Round-Trip Probe (Post-Ingestion)

After importing to Vertex AI, fire the real DB1→DB2 path and assert on **content**, not
just "no error":

```python
# Pseudocode for the probe
for lesson in newly_imported_lessons:
    db1_doc = search_db1(lesson.acs_code)
    bridge_keys = db1_doc.structData.doc_keys + db1_doc.structData.reg_keys

    for key in bridge_keys:
        db2_hits = search_db2(
            query=f"{lesson.title} {key}",
            filter=f"document_tags: ANY('{key}')"
        )

        assert len(db2_hits) >= 1, f"FAIL: {lesson.id} key '{key}' → 0 DB2 hits"
        assert db2_hits[0].score >= SCORE_FLOOR, f"FAIL: {lesson.id} key '{key}' → low score"
```

**Critical assertion:** `len(db2_hits) >= 1` — NOT `response is not None`.
An empty hit list is not `None`. That silence is how Area IX slipped through.

---

## 4. DB2 Vocabulary Reference

DB2's `document_tags` are derived from PDF filenames by the app repo's
`scripts/patch_db2_metadata.py`. These are the **only tokens that will match**
a `document_tags: ANY(...)` filter:

### Regulations (reg_keys)
```
14 CFR 1        14 CFR 43       14 CFR 61       14 CFR 68
14 CFR 71       14 CFR 91       14 CFR 93       14 CFR 119
14 CFR 135      49 CFR 830
```

### Handbooks & Manuals (doc_keys)
```
FAA-H-8083-1B    (Weight & Balance Handbook)
FAA-H-8083-2A    (Risk Management Handbook)
FAA-H-8083-3C    (Airplane Flying Handbook — AFH)
FAA-H-8083-13A   (Glider Flying Handbook)
FAA-H-8083-15B   (Instrument Flying Handbook)
FAA-H-8083-25C   (Pilot's Handbook — PHAK)
AIM              (Aeronautical Information Manual)
```

### Advisory Circulars (doc_keys)
```
AC 00-6B         AC 00-45H       AC 20-43C        AC 23-8C
AC 39-7D         AC 43-9C        AC 43.13-1B      AC 43.13-2B
AC 60-22         AC 61-65H       AC 61-67C        AC 61-98D
AC 61-107B       AC 61-134A      AC 61-142        AC 68-1
AC 68-1A         AC 90-48D       AC 90-109A       AC 91-67A
AC 91-73B        AC 91-74B       AC 120-12A       AC 120-71B
```

> [!IMPORTANT]
> If a bridge key you need is NOT in this vocabulary, it means DB2 doesn't have
> that document indexed. Flag it to Daniel — the document needs to be added to
> the DB2 library before the key will work.

---

## 5. Execution Procedure

### When Triggered After RKP Creation

1. **Load all new/modified RKP manifests** from `curriculum_components/rkp_manifests/`.
2. **Run Layer 1 checks** on each manifest:
   - Flag any RKP with empty `bridge_keys`.
   - Flag any key that contains chapter/section granularity.
   - Flag any key not in the DB2 vocabulary (§4).
3. **Report findings** to Daniel before proceeding to ingestion.

### When Triggered After Ingestion

1. **Load the generated JSONL** from the pipeline output.
2. **Run Layer 2 cross-reference** — compare manifest keys to structData keys.
3. **Run Layer 3 live probe** (if DB access is available).
4. **Report results** with pass/fail per lesson.

### Reporting Format

```
=== Bridge Key Verification Report ===
Date: {timestamp}
Scope: {N} lessons checked

PASS: PPL_PA_I_A_01 — doc_keys: [FAA-H-8083-25C, AC 61-98D] — all verified
PASS: PPL_PA_I_A_02 — doc_keys: [AC 68-1A] — all verified
FAIL: PPL_PA_IX_B_01 — doc_keys: [] — EMPTY (must have ≥1)
FAIL: PPL_PA_IX_C_01 — doc_keys: [FAA-H-8083-25C (PHAK Ch 17)] — NOT document-level
WARN: PPL_PA_I_H_03 — doc_keys: [AC 20-43C] — not in DB2 vocab (may not return hits)

Summary: {passed}/{total} passed, {failed} failed, {warnings} warnings
```

---

## 6. Known Failure Modes

| Failure | Root Cause | Fix |
|---|---|---|
| Empty `doc_keys` in DB1 | LLM metadata generator returned `[]`; schema accepted it silently | Harden `schema.py` with `min_length=1`; ensure master module has populated Bridge Keys section |
| Chapter-level keys (`PHAK Ch 6`) | Author habit — humans think in chapters, DB2 thinks in documents | Normalize to document-level at authoring time |
| Key not in DB2 vocabulary | DB2 doesn't have that PDF indexed | Add the document to DB2 library, then re-run `patch_db2_metadata.py` |
| Manifest ≠ structData | LLM extracted different keys than what the manifest has | Post-generation cross-reference check; regenerate metadata if mismatch |
| `"N/A"` in keys | Author wrote "N/A" instead of leaving empty | Strip "N/A" strings; never write them |

---

## 7. Code References

| File | Role |
|---|---|
| [schema.py](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/src/utils/schema.py) | `CurriculumStructData` — where `reg_keys`/`doc_keys` are validated (or not) |
| [generate_metadata.py](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/src/utils/generate_metadata.py) | LLM metadata extractor — produces the structData from master module text |
| [bridge_key_guide.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/_docs/instruction_docs/bridge_key_guide.md) | Standing contract from the app team — the authoritative reference |

---

## 8. Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|---|---|
| Assert `response is not None` as proof | Assert `len(hits) >= 1 AND score >= floor` |
| Accept empty `doc_keys` as valid | Fail loud — empty = broken RAG hop |
| Use `PHAK Ch 6` as a bridge key | Use `FAA-H-8083-25C` (document-level) |
| Write `"N/A"` in any key field | Use empty array `[]` |
| Skip verification after ingestion | Always run Layer 3 probe on new batches |
| Assume "no error" means "working" | Silence is the failure mode — prove with hit counts |
