---
IsArtifact: true
ArtifactMetadata:
  title: Curriculum RAG Wiring — Task List (final)
  type: task_list
  date: 2026-06-19
---

# Task List — final state (all executed live)

- [x] WS-A: `derive_db2_vocabulary.py` + rewrite `schema.py` (live vocab, family match, clean/coverage)
- [x] WS-A: shared `utils/db2_tags.py` (extract_tags) in lockstep with deriver + importer
- [x] WS-B fetch: 8 FAA PDFs downloaded to `curriculum_components/faa_docs/` (current editions)
- [x] WS-B: `import_db2_docs.py` — rich `document_tags`; pivoted to `create_document` (queue-free)
- [x] WS-C: `reimport_db1_keys.py` — clean + augment + Area IX fill; pivoted to `update_document`
- [x] WS-D: `upload_manifests.py` fixed (config paths)
- [x] WS-E: `ingest_quiz_banks.py`
- [x] WS-F: `src/tests/` offline gate — 33 passing; `probe_bridge_hop.py` live probe
- [x] WS-G: `bridge_key_guide.md` v3.0; `curriculum_lifecycle.md` corrected
- [x] Deleted dead `src/gcp/import_db1_v2.py` (per Daniel OK)
- [x] LIVE: manifests 47/47 + quizzes 376 → Firestore
- [x] LIVE: DB1 184/184 keys repaired (0 corrupt, 0 empty)
- [x] LIVE: DB2 → 27 docs, all tagged (16 patched + 7 + 4 AFH split parts)
- [x] LIVE: AFH split via pypdf into 4 parts (<200 MB each) to clear Vertex's 200 MB cap
- [x] LIVE probe: **47/47 lessons return ≥1 DB2 bridge hit** (was 0); structural coverage 171/184

## Follow-ups
- [ ] Track `pypdf==6.13.3` as a dependency (no requirements.txt in repo yet)
- [ ] Optional: delete orphan `gs://aviationchat-library/v2/FAA-H-8083-3C.pdf` (273 MB, unused)
- [ ] Daniel runs the git commit (command in walkthrough.md)
- [ ] Tier-2 FAA docs (AC 91-78/91-79/00-6/00-63/39-7/43-9, Chart User's Guide, AC 61-65H) to push the
      13 reference-only lessons toward coverage — when wanted
