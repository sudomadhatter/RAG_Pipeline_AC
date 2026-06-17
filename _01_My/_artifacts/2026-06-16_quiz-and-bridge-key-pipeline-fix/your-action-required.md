---
IsArtifact: true
---
# Action Required

The curriculum pipeline and quiz banks have been fully refactored, synced, and validated! Before we call this complete, please review and execute the following manual steps:

## 1. Cloud Infrastructure
The cloud ingestion pipeline (GCS upload + Vertex AI Document Import) is fully operational. It is now properly configured to use your local `.env` and `service-account.json` automatically, and the IAM permissions have been verified.

## 2. Commit and Push Changes
You have modifications across **both repositories** (the ingestion pipeline and the AGY_AVIATIONCHAT app).

### For the Ingestion Pipeline Repository
Run these commands in `Ingestion_pipeline_AvCh` to commit the pipeline and credential fixes:
```bash
git add src/utils/schema.py src/pipeline/curriculum.py src/utils/generate_metadata.py
git add src/main.py src/config.py AGENTS.md
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
