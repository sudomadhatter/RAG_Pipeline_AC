---
IsArtifact: true
ArtifactMetadata:
  title: "Bridge Key Guide — How to Author the Meta Keys (for the Ingestion Team)"
  type: reference
  date: 2026-06-14
audience: "Ingestion Pipeline team (ingestion-Pipeline-AC) + any CFI authoring a Master Document"
companion: "_01_My/Lesson_Plans/ingestion_team_guide.md §4, §8 (this guide drills into the Bridge Keys that §8 only summarizes)"
---

# Bridge Key Guide — How to Author the Meta Keys

> **Why this exists.** The last batch (Area IX, the 12 emergency-ops micro-lessons) shipped with
> **EMPTY bridge keys in Vertex** — `structData.reg_keys` and `structData.doc_keys` came out blank
> because the Area IX Master Document wrote its Bridge Keys block in a **different format** than the
> rest of the curriculum. Empty bridge keys silently break the DB1→DB2 verification hop: the lesson
> still teaches, but the answer can no longer be ground-truth-checked against the FAA library. This
> guide is the canonical spec so it never happens again — and the exact steps to backfill Area IX.
>
> This is the deep-dive companion to `ingestion_team_guide.md` §4 (Bridge Keys formatting) and §8
> (the dual-store RAG). If you only read one doc before touching bridge keys, read **this** one.

---

## 1. TL;DR — the 4 rules that would have prevented the Area IX miss

1. **Heading must be H3, exactly `### 4. Bridge Keys (Metadata)`** — not `#### 4.` (H4). The metadata
   extractor only sees H3 sub-sections; an H4 block is invisible.
2. **The colon goes INSIDE the bold: `**Regs:**`, `**Docs:**`, `**Keywords:**`** — not `**Regs**:`
   (colon outside). The extractor regex matches the bolded label *including* its trailing colon.
3. **Keys must be DOCUMENT-LEVEL tokens that match the DB2 tag vocabulary** (`14 CFR 91`,
   `FAA-H-8083-25C`, `AIM`, `AC 61-98D`) — see §5. Chapter/section detail (`Ch 17`, `8-1-5`) is for
   humans; it must NOT be the machine key, or the strict DB2 filter misses.
4. **Never write the literal string `N/A` as a key.** A non-regulatory topic gets an *empty* Regs
   list, not `N/A`. Docs must **always** carry at least one handbook/AC key.

If you do nothing else, do those four. The rest of this doc explains why and how to prove it.

---

## 2. What a "bridge key" actually is (the dual-store RAG, in 60 seconds)

There are **two** Vertex AI Search data stores:

| Store | Name | Role | Holds |
|---|---|---|---|
| **DB1** | `aviation-curriculum-v2` | **Teaching** | the micro-lessons (markdown) |
| **DB2** | `aviation-library-v2` | **Verification** | the FAA PDFs (FAR/AIM, PHAK, AFH, ACs) |

The flow:

```
Student question
   │
   ▼  search DB1 (curriculum)
matched micro-lesson  ──►  extract its bridge keys: reg_keys + doc_keys
                                   │
                                   ▼  search DB2 (library) FILTERED to those keys
                           FAA source chunks  ──►  Verified answer = pedagogy (DB1) + authority (DB2)
```

**Bridge keys are the join.** They are the only thing that lets a curriculum chunk say "verify me
against *these specific* FAA documents." Empty keys = the join returns nothing = an unverifiable
answer that *looks* fine to any test that only checks "did it error?" (it didn't — it just returned
nothing). That silence is exactly how Area IX slipped through.

---

## 3. Bridge keys live in TWO places — and BOTH must be populated

This is the subtlety that bit Area IX. A bridge key is written into two artifacts, and they are
produced by **different steps**:

| Where | Field names | Produced by | Read by |
|---|---|---|---|
| **RKP manifest** (`{lesson_id}_rkp.json`, per RKP) | `far_references` (Regs), `bridge_keys` (Docs) | RKP authoring (Phase 3) | the app's RKP-First Q&A path — `librarian._search_db2_bridge_hop` |
| **Vertex DB1 `structData`** (per micro-lesson) | `reg_keys`, `doc_keys` | the **splitter + metadata extractor** at import (Phase 5) | the DB1→DB2 hop in the lesson-generation path |

**What went wrong in Area IX, precisely:** the *manifests* were hand-corrected, so
`far_references` / `bridge_keys` came out fine — verified live:

```
PPL_PA_IX_B_01  RKP_01  far_references=['14 CFR 91.3']    bridge_keys=['AC 120-71B', 'FAA-H-8083-3C']
PPL_PA_IX_B_01  RKP_02  far_references=['14 CFR 91.103']  bridge_keys=['FAA-H-8083-25C', 'FAA-H-8083-3C']
PPL_PA_IX_C_01  RKP_03  far_references=['14 CFR 91.3']    bridge_keys=['FAA-H-8083-3C', 'AC 120-80']
```

…but the **Vertex `structData.reg_keys` / `doc_keys` stayed EMPTY**, because the metadata extractor
that builds `structData` from the Master Document never matched the Area IX Bridge Keys block (wrong
heading level + wrong colon placement — §4). So the manifest-driven path limped along while the
DB1→DB2 structData hop was dead.

> **The lesson:** fixing the manifest by hand is NOT enough. The Master Document must be in the
> canonical format so the **automated extractor** populates `structData` too. Author once, correctly,
> at the source — don't patch downstream.

---

## 4. The canonical Bridge Keys block (copy this exactly)

Every `## PA.X.Y.Z:` element in a Master Document ends with this **H3** sub-section:

```markdown
### 4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 91.3, 14 CFR 91.103
* **Docs:** FAA-H-8083-3C, AC 120-71B
* **Keywords:** Emergency Authority, Memory Items, ADM, PAVE
```

### Side-by-side: what Area IX did (WRONG) vs the standard (RIGHT)

| | Area IX (broke the extractor) | Canonical (Task G standard) |
|---|---|---|
| Heading level | `#### 4. Bridge Keys (Metadata)` ← **H4** | `### 4. Bridge Keys (Metadata)` ← **H3** |
| Label + colon | `* **Regs**: 14 CFR 91.3` ← colon **outside** the bold | `* **Regs:** 14 CFR 91.3` ← colon **inside** the bold |
| Empty regs | `* **Regs**: N/A` ← literal "N/A" | `* **Regs:**` *(empty)* — or omit the value, never "N/A" |

Both Area IX divergences defeat the extractor's regex, which is shaped like
`^\*\s+\*\*Regs:\*\*\s*(.+)$` under an H3 heading. `#### ` fails the heading gate; `**Regs**:` fails
the label gate. Either one alone yields empty `reg_keys`.

### Field rules

| Field | Required? | Format | Notes |
|---|---|---|---|
| **Regs** | optional (may be empty) | comma-separated 14 CFR citations | Empty is OK for non-regulatory topics (aerodynamics, physiology). **Never write "N/A".** |
| **Docs** | **mandatory — ≥1** | comma-separated handbook/AC/AIM tokens | This is the verification backbone. A lesson with no Docs key cannot be verified. |
| **Keywords** | recommended | supplementary search terms | Feeds hybrid search; not used for the strict DB2 filter. |

---

## 5. The keying convention — match the DB2 tag vocabulary (the other half of the contract)

A key that is *present* but doesn't *match anything in DB2* is almost as useless as an empty one. The
app applies a **strict metadata filter** against DB2's `document_tags` array
(`backend/tools/librarian.py:237` → `_search_db2_bridge_hop`):

```python
filter_spec = 'document_tags: ANY("14 CFR 91.3", "FAA-H-8083-25C Chapter 17", ...)'
```

DB2's `document_tags` are derived from the FAA PDF **filenames** by `scripts/patch_db2_metadata.py`,
and they are deliberately **coarse / document-level**:

| FAA source | DB2 `document_tags` token (what your key must equal) |
|---|---|
| Advisory Circular | `AC 61-98D`, `AC 120-71B` (space, not underscore) |
| Handbook | `FAA-H-8083-25C`, `FAA-H-8083-3C`, `FAA-H-8083-2A` (no chapter suffix) |
| 14 CFR part | `14 CFR 61`, `14 CFR 91` (PART level — not `14 CFR 91.103`) |
| AIM | `AIM` (just the manual — no section) |

> **Authoring rule:** the **machine key** must be the document-level token from the table above. Put
> the human-useful chapter/section detail in the prose of sub-section 2 (Expert Deep Dive), **not** in
> the key. `FAA-H-8083-25C Chapter 17` as a `doc_key` will **not** strict-match the DB2 tag
> `FAA-H-8083-25C`; author it as `FAA-H-8083-25C`. Likewise prefer the part token `14 CFR 91` for the
> reg key when the matching DB2 PDF is the whole part. (When a section-specific PDF exists in DB2,
> match its tag exactly — check the DB2 store first.)
>
> Mismatched-granularity keys don't *crash* — the bridge hop degrades to an unfiltered semantic query
> — but you lose the high-precision strict filter, which is the entire point of bridge keys.

---

## 6. Pre-flight authoring checklist (run this before every import)

**Master Document (per element):**
- [ ] Bridge Keys heading is `### 4. Bridge Keys (Metadata)` (H3, not H4).
- [ ] Labels are `**Regs:**`, `**Docs:**`, `**Keywords:**` — colon **inside** the bold.
- [ ] **Docs** has ≥1 entry. (Regs may be empty for non-reg topics — but never "N/A".)
- [ ] Every key is a **document-level token** from the §5 vocabulary (no `Chapter`/section suffix on
      the machine key).
- [ ] Every Docs/Regs token actually exists as a `document_tags` value in DB2 (spot-check the store).

**RKP manifest (per RKP) — these mirror the Master Document keys:**
- [ ] `far_references` = the Regs tokens (empty list `[]` allowed; never `["N/A"]`).
- [ ] `bridge_keys` = the Docs tokens (≥1).

**After import (Vertex structData — the step Area IX skipped):**
- [ ] Pull 2–3 of the freshly-imported micro-lessons' `structData` and confirm `reg_keys` /
      `doc_keys` are **non-empty and well-formed** (this is AC-1 of Story 12.2 — the offline gate).

---

## 7. How we PROVE it works (the verification contract — Story 12.2)

The single most dangerous shortcut is a probe that checks `response is not None`. **An empty hit list
is not `None`.** That distinction *is* the Area IX bug. The verification has three layers:

1. **AC-1 — Offline schema gate (the IX-prevention guard).** Over **all 184** DB1 micro-lessons,
   assert each `structData` has a **non-empty, well-formed** `reg_keys`/`doc_keys`. Network-free; runs
   in CI. Assert on *content*, not `is not None`.
2. **AC-2 — Live round-trip (the real proof).** For each backfilled Area IX key, fire the actual
   DB1→DB2 path and assert **`len(db2_hits) >= 1`** AND **top hit score ≥ a defined floor** AND the
   returned doc maps back to the **queried Area** (no IX→VII cross-wire). `@pytest.mark.live`; must run
   before the story closes.
3. **AC-3 — Golden set.** Freeze 2–3 hand-verified Area IX micro-lessons → expected FAA reference, as
   canary fixtures against future reindex drift.

---

## 8. Backfilling Area IX — the procedure (12 micro-lessons)

The Master Document is `_docs/modules_master_lessons/Area 9 Tasks B,C PPL.md` (local mirror; the live
source lives in the `ingestion-Pipeline-AC` repo under `specialist_curriculum/`).

1. **Fix the Master Document.** In every `### 4. Bridge Keys` block of Area 9:
   - change `#### 4.` → `### 4.`
   - change `**Regs**:` → `**Regs:**`, `**Docs**:` → `**Docs:**`, `**Keywords**:` → `**Keywords:**`
   - replace each `**Regs:** N/A` with an empty value (delete the `N/A`)
   - normalize every key to the §5 document-level vocabulary.
2. **Re-split** the Area IX Master Document into its micro-lessons (the `## PA.` splitter).
3. **Re-import** the 12 micro-lessons into DB1 with **`FULL` reconciliation** (idempotent) per
   `ingestion_team_guide.md` §5 / `src/gcp/reimport_with_metadata.py`. Confirm in the Vertex console
   that the 12 docs now carry non-empty `reg_keys` + `doc_keys`.
4. **(If the manifests drifted)** re-confirm each Area IX `_rkp.json` `far_references`/`bridge_keys`
   match the corrected Master Document, and re-ingest with `scripts.ingest_rkp_manifests --file ...`.
5. **Run the probes** (§7): offline AC-1 over all 184; live AC-2 over the 12 IX keys; freeze AC-3.
   Paste the real hit counts + scores into the Story 12.2 walkthrough.
6. **Spot-check the other 5 content Areas** (I, III, VI, VII, XI) still resolve — prove the re-import
   didn't regress them (AC-4).

> **One-time hardening (recommended):** make the extractor regex tolerant of *both* colon placements
> and warn (don't silently pass) on an empty `doc_keys`. A loud failure at import time is what turns
> "silent Area IX" into "caught in 30 seconds." But tolerance is a backstop — the **format above is
> the contract**; author to it.

---

## 9. Quick reference card

```
HEADING   ### 4. Bridge Keys (Metadata)          (H3 — never H4)
LABELS    * **Regs:**  * **Docs:**  * **Keywords:**   (colon INSIDE the bold)
REGS      0+ tokens, part-level: 14 CFR 91        (empty OK; NEVER "N/A")
DOCS      1+ tokens, doc-level:  FAA-H-8083-25C, AC 61-98D, AIM   (NO chapter suffix on the key)
MIRRORS   manifest far_references = Regs ;  manifest bridge_keys = Docs
PROVE IT  offline: structData reg_keys/doc_keys non-empty over all 184
          live:    DB1→DB2 returns count>=1 AND score>=floor AND owning-area match
```

**Owner questions:** pipeline/format → Woz · content/citations → Daniel (CFI).
**App read path:** `backend/tools/librarian.py:237` `_search_db2_bridge_hop`.
**DB2 tag source:** `scripts/patch_db2_metadata.py`.
