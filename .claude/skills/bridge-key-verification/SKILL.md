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
> **Companion:** `_01_My/bridge_key_guide.md` — the standing contract from the app team.

---

## 1. Why This Exists

Two Vertex AI Search stores power the RAG pipeline:

| Store | Name | Role |
|---|---|---|
| **DB1** | `aviation-curriculum-v2` | **Teaching** — 184+ micro-lessons |
| **DB2** | `aviation-library-v2` | **Verification** — FAA PDFs |

Empty bridge keys → verification step returns nothing → unverifiable answer.
This silence is how Area IX shipped broken.

---

## 2. The Standing Contract

Every micro-lesson shipped to DB1 must satisfy ALL of:

1. **Non-empty `doc_keys` (≥1)** in DB1 `structData`.
2. **Document-level key tokens** matching DB2's `document_tags` vocabulary.
3. **Manifest and structData agree.**
4. **Proven via live round-trip** — `count >= 1`, score ≥ floor, correct Area.
5. **Offline schema gate runs** over all lessons.

---

## 3. The Three Verification Layers

### Layer 1: Offline Schema Gate (Pre-Ingestion)

Check every RKP manifest:
- `bridge_keys` is non-empty (len >= 1)
- No chapter/section granularity in keys
- No literal "N/A" strings
- `far_references` format: `"14 CFR {part}.{section}"`
- All keys match DB2 vocabulary (§4)

Check DB1 structData:
- `structData.doc_keys` non-empty (len >= 1)
- Document-level tokens only
- Agrees with manifest `bridge_keys`

### Layer 2: Cross-Reference Consistency

| RKP Manifest Field | DB1 structData Field | Must Match? |
|---|---|---|
| `far_references` | `reg_keys` | YES |
| `bridge_keys` | `doc_keys` | YES |

### Layer 3: Live Round-Trip Probe (Post-Ingestion)

Assert on **content**, not "no error":
```
assert len(db2_hits) >= 1  # NOT: response is not None
assert db2_hits[0].score >= SCORE_FLOOR
```

---

## 4. DB2 Vocabulary Reference

### Regulations (reg_keys)
```
14 CFR 1    14 CFR 43    14 CFR 61    14 CFR 68
14 CFR 71   14 CFR 91    14 CFR 93    14 CFR 119
14 CFR 135  49 CFR 830
```

### Handbooks (doc_keys)
```
FAA-H-8083-1B   FAA-H-8083-2A   FAA-H-8083-3C   FAA-H-8083-13A
FAA-H-8083-15B  FAA-H-8083-25C  AIM
```

### Advisory Circulars (doc_keys)
```
AC 00-6B    AC 00-45H    AC 20-43C    AC 23-8C     AC 39-7D
AC 43-9C    AC 43.13-1B  AC 43.13-2B  AC 60-22     AC 61-65H
AC 61-67C   AC 61-98D    AC 61-107B   AC 61-134A   AC 61-142
AC 68-1     AC 68-1A     AC 90-48D    AC 90-109A   AC 91-67A
AC 91-73B   AC 91-74B    AC 120-12A   AC 120-71B
```

> [!IMPORTANT]
> If a bridge key is NOT in this vocabulary, DB2 doesn't have that PDF.
> Flag it to Daniel — the document needs to be added to DB2.

---

## 5. Execution Procedure

### After RKP Creation
1. Load new/modified manifests from `specialist_curriculum/rkp_manifests/`.
2. Run Layer 1 checks. Flag empty/malformed keys.
3. Report findings to Daniel.

### After Ingestion
1. Load generated JSONL.
2. Run Layer 2 cross-reference.
3. Run Layer 3 live probe (if DB access available).
4. Report results per lesson.

### Report Format
```
=== Bridge Key Verification Report ===
Date: {timestamp}
Scope: {N} lessons checked

PASS: PPL_PA_I_A_01 — doc_keys: [FAA-H-8083-25C, AC 61-98D]
FAIL: PPL_PA_IX_B_01 — doc_keys: [] — EMPTY
FAIL: PPL_PA_IX_C_01 — doc_keys: [FAA-H-8083-25C (PHAK Ch 17)] — NOT document-level
WARN: PPL_PA_I_H_03 — doc_keys: [AC 20-43C] — not in DB2 vocab

Summary: {passed}/{total} passed, {failed} failed, {warnings} warnings
```

---

## 6. Known Failure Modes

| Failure | Root Cause | Fix |
|---|---|---|
| Empty `doc_keys` | LLM generator returned `[]`; schema accepted silently | `schema.py` → `min_length=1` |
| Chapter-level keys | Author habit | Normalize to document-level |
| Key not in DB2 vocab | PDF not indexed | Add to DB2 library |
| Manifest ≠ structData | LLM extracted different keys | Cross-reference check |
| `"N/A"` in keys | Author wrote literal "N/A" | Strip and reject |

---

## 7. Code References

| File | Role |
|---|---|
| `src/utils/schema.py` | `CurriculumStructData` — `reg_keys`/`doc_keys` validation |
| `src/utils/generate_metadata.py` | LLM metadata extractor |
| `_01_My/bridge_key_guide.md` | Standing contract |

---

## 8. Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|---|---|
| Assert `response is not None` | Assert `len(hits) >= 1 AND score >= floor` |
| Accept empty `doc_keys` | Fail loud |
| Use `PHAK Ch 6` as a key | Use `FAA-H-8083-25C` |
| Write `"N/A"` | Use `[]` |
| Skip verification after ingestion | Always run Layer 3 probe |
