---
name: constitution-project
description: "RAG_Pipeline_AC data-side hard stops — loads ALWAYS in this repo alongside the shared constitution. The live stores are production; these gates are what protect them."
---

# Project Constitution — RAG_Pipeline_AC (data-side hard stops)

The shared `constitution.md` still applies in full. These are THIS repo's additional hard stops —
the live stores (Vertex DB1/DB2, Firestore) **are production** and have no staging tier.

## 🚫 Hard Stops

- **Never run any `src/gcp/` tool with `--execute` without a dry-run reviewed in the SAME session.**
  Paste the dry-run output in chat; the approval must cover exactly that scope.
- **Never commit generated import manifests** — `pipeline/curriculum/curriculum.jsonl`,
  `pipeline/library/library_metadata.jsonl`. A partial manifest + FULL reconciliation **wipes the
  live store** (the `.gitignore` comment is law; the pipeline regenerates these at import time).
- **Never let a `*.pdf` into git** (`.gitignore` enforces it; do not add negations). Heavy sources
  live on local disk + Google Drive; the cloud stores serve the app.
- **Never invent an FAA fact, citation, or regulatory reference.** Every claim must trace to a
  permitted grounding source: the ACS PDFs in `docs/`, `pipeline/curriculum/1 ACS Curriculum
  Key.json`, or an FAA document in `pipeline/library/` / the DB2 vocabulary. Unverifiable ⇒ flag
  for Daniel — never fill the gap from model memory. (Enforced by the `faa-grounding-gate` skill.)
- **Never mark an ingest "done" without proof:** `pytest src/tests/` green AND
  `probe_bridge_hop.py` returning ≥1 DB2 hit for every touched lesson — actual output pasted,
  never fabricated.
- **Never overwrite a master module in `curriculum_components/curriculum_modules/` outside an
  explicit Drive-pull session.** Google Drive is the authoring surface; the repo `.md` is machine
  truth. A pull session diffs before it overwrites.
- **Never create a `main_debug` branch here.** Single `main` **by design** (Daniel, 2026-07-22):
  workhorse repo, deployed nowhere — the protected surface is the data, not a branch.

## ⚠️ Ask First

- Bulk operations: `--all` flags, FULL-reconciliation imports, any multi-lesson repair.
- Changing `src/utils/schema.py` — it mirrors the app's `backend/schemas/quiz.py` contract; a
  unilateral change breaks the consumer silently.
- Adding/removing DB2 documents or changing the tag vocabulary (the bridge-key hop depends on it).
- Deleting any curriculum asset (manifest, quiz bank, element, sidecar, podcast script).

## ✅ Always

- Resolve paths/credentials through `src/config.py` — never hardcode machine paths (see
  `credential-resolution.md`).
- Regenerate the state map (`python scripts/generate_state_map.py`) after any ingest and read its
  drift section; use `--live` when store counts matter.
- Update `_artifacts/active-context.md` at session end.
