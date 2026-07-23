# pipeline/curriculum/ — INDEX  (DB1 source store — DATA, not code)

Read by `src/config.py`; feeds **DB1** (`aviation-curriculum-v2`).

| Item | What |
|---|---|
| `elements/` | 184 split micro-lesson `.md` — one per live DB1 document |
| `sidecars/` | 12 Area IX metadata `.json` (bridge keys) |
| `new/` | authoring inbox for freshly split lessons |
| `active/` · `superseded/` | lifecycle stages |
| `1 ACS Curriculum Key.json` | the ACS Area/Task/element → lesson-code key |
| `curriculum.jsonl` | **GENERATED** DB1 import manifest — **NEVER commit** (partial manifest + FULL reconciliation wipes the live store) |
| `manifest.json` | store manifest |

Repair/import tool (gated): `python src/gcp/reimport_db1_keys.py [--execute]`.
