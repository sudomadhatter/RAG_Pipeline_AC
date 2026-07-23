---
name: credential-resolution
description: "How scripts find GCP/Firestore credentials in this repo — activates when writing or debugging any script that needs cloud auth."
---

# Environment & Credential Resolution (RAG_Pipeline_AC)

All path + credential resolution flows through **`src/config.py`** — the single source of truth.
Scripts must work from ANY working directory on any machine that checks out this repo.

- Credentials live at `auth_keys/` (**gitignored**): `auth_keys/.env` +
  `auth_keys/service-account.json`. `.env.example` at the root documents every variable — keep it
  current when you add one.
- `src/config.py` resolves the repo root dynamically and exports `GOOGLE_APPLICATION_CREDENTIALS`
  when unset; a developer can override via their own environment / `.env`.
- When writing a NEW script: route through the config (import it, or replicate its resolution
  pattern). **Never** hardcode a relative `auth_keys/...` path — it breaks the moment the script
  runs from a subdirectory — and **never** hardcode machine-absolute paths.
- Tests are the offline gate: `src/tests/` must run with **no cloud access and no credentials**
  (mock at the boundary). A test that needs a live key is in the wrong tier.
