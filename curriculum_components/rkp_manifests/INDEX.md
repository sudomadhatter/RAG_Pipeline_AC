# rkp_manifests/ — INDEX

48 RKP manifests (`{lesson_id}_rkp.json`): 3–6 Required Knowledge Points each
(title/why/knowledge/acs_elements/far_references/bridge_keys) + a 500–1000-word `lesson_overview`.
Flashcards are the `knowledge_formatted` field inside each RKP — filled ONLY by
`curriculum_components/scripts/generate_knowledge_formatted.py` (script-owned; leave empty when
authoring). `bridge_keys` must exist in the DB2 tag vocabulary — the app filters DB2 on them
(`bridge-key-verification` skill proves the hop).

Authoring: `rkp-manifest-creation` skill + `_docs/instruction_docs/rkp_creation_guide.md`.
Ingest (gated): `python src/gcp/upload_manifests.py [--execute]` → Firestore `rkp_manifests/{lesson_id}`.
