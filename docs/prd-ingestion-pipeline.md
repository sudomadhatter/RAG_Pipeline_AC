# Product Requirements Document — Ingestion Pipeline

**Project:** AviationChat Ingestion Pipeline  
**Author:** Daniel + Woz  
**Date:** 2026-02-27  
**Parent Project:** aviationChat-AGY

---

## 1. Problem Statement

AviationChat's AI agents (Specialist, Verification Swarm) depend on two Vertex AI Search data stores populated with curated aviation content. The original ingestion pipeline was lost during a hard wipe. Without it, we cannot:

1. Add new ACS lesson plans (currently only 23 of ~100+ tasks exist)
2. Add missing FAA regulatory documents
3. Update documents when FAA regulations change annually
4. Rebuild the data stores if they are corrupted or need migration

This PRD defines the requirements for a **reproducible, versioned ingestion pipeline** that transforms local source documents into searchable Vertex AI Search data stores.

---

## 2. Success Criteria

| Metric | Target |
|---|---|
| **Pipeline Reproducibility** | Any developer can run the full pipeline from scratch with a single command |
| **Data Integrity** | 100% of uploaded documents are retrievable via Vertex AI Search queries |
| **Bridge Key Integrity** | Every `reg_key` and `doc_key` in DB1 lesson metadata resolves to an actual document in DB2 |
| **Version Tracking** | Every ingestion run is logged with timestamp, file manifest, and document counts |
| **Update Turnaround** | A new lesson or regulation can be added in < 10 minutes |

---

## 3. Scope

### In Scope (V1)

1. **DB1 Pipeline (Curriculum):** Ingest ACS lesson plans (JSON metadata + Markdown content) into `aviationchat-curriculum-cms` GCS bucket and Vertex AI Search
2. **DB2 Pipeline (Library):** Ingest FAA documents (PDF) with metadata into `aviationchat-library` GCS bucket and Vertex AI Search
3. **Metadata Generation:** Auto-generate `curriculum.jsonl` and `library_metadata.jsonl` from source files
4. **Validation:** Pre-upload checks for schema compliance, bridge key integrity, and duplicate detection
5. **Versioning:** Date-stamped ingestion tracking so we know which version of each document is live
6. **CLI Interface:** Command-line tool to run individual pipelines or full rebuild

### Out of Scope (V1)

- Web scraping from FAA.gov (documents uploaded manually)
- Automatic FAA regulation change detection
- Firestore writes (handled by the app's agents, not the pipeline)
- Vertex AI Search data store creation (one-time manual setup)

---

## 4. Data Architecture (Reverse-Engineered)

### 4.1 DB1: Curriculum (Lesson Plans)

```
Source: local/pipeline/curriculum/
  ├── new/                         <- Drop new/updated files here
  │   ├── lesson_pa_ii_a_k1.json
  │   └── lesson_pa_ii_a_k1.md
  ├── active/                      <- Currently live (pipeline moves files here)
  │   ├── lesson_pa_i_a_k1.json
  │   ├── lesson_pa_i_a_k1.md
  │   └── ...
  ├── superseded/                  <- Old versions replaced by newer ones
  │   └── lesson_pa_i_a_k1_2025-01-21.json
  └── (auto-generated) curriculum.jsonl
         ↓
GCS: gs://aviationchat-curriculum-cms/
         ↓
Vertex AI Search: [Curriculum Data Store]
```

**Lesson Metadata Schema** (JSON):
```json
{
  "id": "lesson_pa_i_a_k1",
  "structData": {
    "acs_code": "PA.I.A.K1",
    "title": "Certification requirements, recent flight experience, and recordkeeping.",
    "type": "lesson_chunk",
    "ancestral_context": "Private Pilot > General",
    "reg_keys": ["14 CFR 61.56", "14 CFR 61.57"],
    "doc_keys": ["AC 61-98E (Currency & Flight Review)", "FAA-H-8083-25C (PHAK)"],
    "keywords": ["Flight Review", "Sole Manipulator"]
  },
  "content": {
    "mimeType": "text/markdown",
    "uri": "gs://aviationchat-curriculum-cms/lessons/lesson_pa_i_a_k1.md"
  }
}
```

> **Bridge Keys**: `reg_keys` + `doc_keys` are the critical link between DB1 and DB2. The Specialist Agent uses these to tell the Verification Swarm *where to look* in the Library. Every bridge key must resolve to an actual DB2 document.

### 4.2 DB2: Library (FAA Documents)

```
Source: local/pipeline/library/
  ├── new/                   <- Drop new/updated docs here
  │   └── regulations/
  │       └── 14 CFR Part 91 (2026).pdf
  ├── active/                <- Currently live (pipeline moves files here)
  │   ├── advisory_circulars/
  │   ├── handbooks/
  │   └── regulations/
  ├── superseded/            <- Old versions (auto-moved on replacement)
  │   └── regulations/
  │       └── 14 CFR Part 91 (2025).pdf
  └── (auto-generated) library_metadata.jsonl
         ↓
GCS: gs://aviationchat-library/
         ↓
Vertex AI Search: [Library Data Store]
```

**Library Metadata Schema** (JSON):
```json
{
  "id": "regulation_14_cfr_part_91_2025",
  "structData": {
    "category": "regulation",
    "title": "14 CFR part 91 (2025)",
    "subfolder": "regulations",
    "filename": "14 CFR part 91 (2025).pdf"
  },
  "content": {
    "mimeType": "application/pdf",
    "uri": "gs://aviationchat-library/regulations/14 CFR part 91 (2025).pdf"
  }
}
```

Categories: `regulation` | `handbook` | `advisory_circular`

---

## 5. Functional Requirements

### 5.1 Core Pipeline

| FR | Requirement |
|---|---|
| **FR-IP1** | Pipeline reads source documents from a local directory structure |
| **FR-IP2** | Pipeline auto-generates the JSONL metadata manifest from individual JSON metadata files |
| **FR-IP3** | Pipeline uploads files to the correct GCS bucket preserving folder structure |
| **FR-IP4** | Pipeline triggers Vertex AI Search data store import using the JSONL manifest |
| **FR-IP5** | Pipeline supports **incremental updates** — upload only new/changed files |
| **FR-IP6** | Pipeline supports **full rebuild** — purge and re-upload everything |

### 5.2 Validation & Safety

| FR | Requirement |
|---|---|
| **FR-IP7** | Before upload, validate every lesson JSON against the schema (required fields, types) |
| **FR-IP8** | Before upload, validate that every `.json` has a matching `.md` file (and vice versa) |
| **FR-IP9** | Before upload, validate bridge key integrity: every `reg_key` and `doc_key` should map to a known library document |
| **FR-IP10** | Warn (not block) on bridge keys that reference documents not yet in the library — these represent known gaps |
| **FR-IP11** | Detect and reject duplicate document IDs |

### 5.3 Versioning & Tracking

| FR | Requirement |
|---|---|
| **FR-IP12** | Each ingestion run logs: timestamp, pipeline type (curriculum/library), files uploaded, files skipped, errors |
| **FR-IP13** | Source documents should encode the document date/year in metadata (e.g., `"14 CFR Part 91 (2025)"`) so we can track when regulations are superseded |
| **FR-IP14** | Maintain a local manifest file (`ingestion_log.jsonl`) tracking all runs |

### 5.4 Document Lifecycle Management

The pipeline manages a three-stage file workflow. This is automated — the pipeline agent moves files between stages during ingestion.

| Stage | Directory | Description |
|---|---|---|
| **New** | `new/` | User drops new or updated source files here. Pipeline picks them up on next run. |
| **Active** | `active/` | Currently live in GCS and Vertex AI Search. Pipeline moves files here after successful upload. |
| **Superseded** | `superseded/` | Old versions automatically moved here when replaced by a newer version. Timestamped for audit trail. |

| FR | Requirement |
|---|---|
| **FR-IP15** | On ingestion, files in `new/` are validated, uploaded, then moved to `active/` |
| **FR-IP16** | If a file in `new/` has the same `id` as an existing `active/` file, the old version is moved to `superseded/` with a date suffix (e.g., `_2025-01-21`) before the new one takes its place |
| **FR-IP17** | Superseded files are never deleted automatically — they serve as an audit trail |
| **FR-IP18** | The pipeline rebuilds the JSONL manifest from `active/` contents only (superseded files are excluded) |
| **FR-IP19** | Pipeline generates a `manifest.json` in each pipeline's root tracking: active file count, superseded file count, last ingestion timestamp |

### 5.5 CLI Interface

| FR | Requirement |
|---|---|
| **FR-IP20** | `python pipeline.py curriculum` — run DB1 curriculum pipeline |
| **FR-IP21** | `python pipeline.py library` — run DB2 library pipeline |
| **FR-IP22** | `python pipeline.py all` — run both pipelines |
| **FR-IP23** | `python pipeline.py validate` — run all validation checks without uploading |
| **FR-IP24** | `--dry-run` flag to show what would be uploaded without doing it |
| **FR-IP25** | `--force` flag to force full rebuild (purge + re-upload) |
| **FR-IP26** | `python pipeline.py status` — show current active/new/superseded counts per pipeline |

---

## 6. Current State & Gap Analysis

### DB1 (Curriculum) — 23 of ~100+ Tasks

Currently covering only **ACS Area I** (Tasks A and B). Remaining areas:

| ACS Area | Status |
|---|---|
| I. General (A, B) | 23 lessons exist |
| II. Preflight Procedures | **MISSING** |
| III. Airport & Seaplane Base Ops | **MISSING** |
| IV. Takeoffs, Landings, Go-Arounds | **MISSING** |
| V. Performance & Ground Reference | **MISSING** |
| VI. Navigation | **MISSING** |
| VII. Slow Flight & Stalls | **MISSING** |
| VIII. Basic Instrument Maneuvers | **MISSING** |
| IX. Emergency Operations | **MISSING** |
| X. Multiengine Operations | **MISSING** |
| XI. Night Operations | **MISSING** |

### DB2 (Library) — 19 of ~30+ Expected

| Category | Have | Missing (Referenced in Lessons) |
|---|---|---|
| Regulations | Parts 1, 43, 61, 67, 68, 91 | Part 71, 73, 97, NTSB 830 |
| Handbooks | PHAK, AFH, RMH, AWH, AIM | FAA-H-8083-13 (IFH) |
| Advisory Circulars | 8 ACs | AC 61-65H (Endorsements), AC 120-12A |

---

## 7. User Action Required (Vertex AI Search)

> **CAUTION:** The service account `firebase-adminsdk-fbsvc@aviationchat.iam.gserviceaccount.com` does NOT have `discoveryengine.dataStores.list` permission. I need you to either:
> 1. **Grant the role** `Discovery Engine Admin` to the service account in GCP IAM, OR
> 2. **Tell me the Vertex AI Search data store names/IDs** so I can reference them directly in the pipeline

I also need to confirm:
- Are the Vertex AI Search data stores still populated, or do they need a full re-import?
- What is the import method the old pipeline used? (JSONL with GCS URIs is the standard approach — matches the existing metadata files)

---

## 8. Non-Functional Requirements

| NFR | Requirement |
|---|---|
| **Idempotency** | Running the pipeline twice with the same source files produces the same result |
| **Error Recovery** | Pipeline logs failures per-file and continues (no "fail all on first error") |
| **Performance** | Full curriculum rebuild (23 lessons) completes in < 2 minutes |
| **Portability** | Pipeline runs on any machine with Python 3.11+ and GCP service account access |
| **Security** | Service account keys are never committed to Git; loaded from env var / config |

---

## BMAD Backfill

> **NOTE:** No BMAD story existed for this pipeline work. This PRD serves as the reverse-engineered story. After implementation, a formal BMAD story should be created to document the pipeline as part of the DevOps/Infrastructure epic.
