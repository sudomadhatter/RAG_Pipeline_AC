# src/utils/ — INDEX

Shared helpers for the ingestion tools:

- **`schema.py`** — the artifact schema gate (RKP manifests, quiz banks). ⚠️ It mirrors the app's
  consuming contract (`AGY_AVIATIONCHAT/backend/schemas/quiz.py`) — **ask before changing it**; a
  unilateral edit breaks the consumer silently.
- metadata extraction + DB2 tag helpers (incl. `to_family()` edition-variant matching, which is why
  `AC 61-98D` still hits `AC 61-98E`).

Path/credential resolution belongs in `src/config.py`, not here.
