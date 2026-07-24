# Pipeline State Map

> **GENERATED FILE — do not hand-edit.** Regenerate with `python scripts/generate_state_map.py [--live]`.
> Last generated: 2026-07-23 22:23  ·  mode: offline (local files only — pass `--live` for database state)

## Local asset inventory

| Asset | Count |
|---|---|
| curriculum_modules (.md) | 14 |
| rkp_manifests (*_rkp.json) | 48 |
| quiz_banks (*_quiz.json) | 48 |
| faa_docs (PDFs) | 0 |
| lesson_podcasts (.md) | 35 |
| curriculum/elements (.md) | 184 |
| curriculum/sidecars (.json) | 12 |
| curriculum.jsonl (entries) | 0 |

## Drift checks (offline)

- ✅ **RKP ↔ quiz pairing** — every RKP has a quiz and vice-versa.
- ⚠️ **elements ↔ curriculum.jsonl** — 184 element .md vs 0 manifest entries — MISMATCH (rerun reimport_db1_keys.py to rebuild).
- ℹ️ **lesson audio** — 47/48 lessons reference an `audio_file`; the audio lives in a Firebase Storage bucket (deployed out-of-band, not via this repo). 35 transcript .md in lesson_podcasts/. New lessons may have no podcast — expected, not drift. Lessons without audio: ['PPL_PA_I_H_04'].

## Deployed database state

_Offline run — rerun with `--live` to query Firestore + DB1/DB2._
