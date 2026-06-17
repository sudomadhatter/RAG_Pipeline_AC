---
IsArtifact: true
---
# Action Required

The curriculum pipeline and quiz banks have been fully refactored, synced, and validated! Before we call this complete, please review and execute the following manual steps:

## 1. Cloud Credentials for Local Ingestion
The local pipeline validation (Phase 1) succeeded perfectly, but the actual upload to GCP failed because the `librarian-service-account.json` key is not present in your local scratch directory. 
If you want to run the live `curriculum` pipeline locally to push the new Area 9 sidecars to Vertex AI Search, you will need to add your service account key to:
`C:\Users\dlohn\.gemini\antigravity\scratch\Ingestion_pipeline_AvCh\auth_keys\librarian-service-account.json`

## 2. Commit and Push Changes
You have modifications across **both repositories** (the ingestion pipeline and the AGY_AVIATIONCHAT app).

### For the Ingestion Pipeline Repository
Run these commands in `Ingestion_pipeline_AvCh` to commit the pipeline fixes:
```bash
git add src/utils/schema.py src/pipeline/curriculum.py src/utils/generate_metadata.py
git add curriculum_components/curriculum_modules/Area\ 9\ Tasks\ B,C\ PPL.md
git add scripts/audit_sidecars.py scripts/fallback_generator2.py
git rm src/gcp/reimport_with_metadata.py src/gcp/upload_quiz_banks.py
git commit -m "fix: refactored curriculum pipeline and enforced DB2_VOCABULARY schema"
git push
```

### For the App Repository
Run these commands in `AGY_AVIATIONCHAT` to commit the quiz bank sync and ingest script fixes:
```bash
git add _docs/specialist_lesson/quiz_banks/
git add scripts/ingest_quiz_banks.py
git commit -m "fix: synced 11 quiz banks and resolved Windows ingest encoding errors"
git push
```
