# Pipeline State Map

> **GENERATED FILE — do not hand-edit.** Regenerate with `python scripts/generate_state_map.py [--live]`.
> Last generated: 2026-06-19 14:00  ·  mode: offline (local files only — pass `--live` for database state)

## Local asset inventory

| Asset | Count |
|---|---|
| curriculum_modules (.md) | 13 |
| rkp_manifests (*_rkp.json) | 48 |
| quiz_banks (*_quiz.json) | 48 |
| faa_docs (PDFs) | 12 |
| lesson_podcasts (.md) | 34 |
| curriculum/elements (.md) | 184 |
| curriculum/sidecars (.json) | 12 |
| curriculum.jsonl (entries) | 184 |

## Drift checks (offline)

- ✅ **RKP ↔ quiz pairing** — every RKP has a quiz and vice-versa.
- ✅ **elements ↔ curriculum.jsonl** — 184 element .md vs 184 manifest entries.
- ⚠️ **podcasts ingestion** — 34 podcast .md in curriculum_components/lesson_podcasts/ are **not ingested by any script** (authored, not deployed — informational).

## Deployed database state

_Offline run — rerun with `--live` to query Firestore + DB1/DB2._
