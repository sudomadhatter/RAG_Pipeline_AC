---
description: Safely merges the current feature branch into main, pushes to GitHub to trigger CI/CD, and manually deploys the backend to Cloud Run.
---

# Push to Main & Deploy Workflow

Use this workflow to merge changes from your current feature branch into `main`, trigger the official GitHub Actions and Firebase App Hosting pipelines, and optionally execute a manual deployment of the FastAPI backend to Cloud Run to bypass queue delays or verify container secrets.

## Context: Why We Manually Deploy

1. **Fast Feedback Loop**: Pushing to `main` triggers GitHub Actions CI/CD (backend) and Firebase App Hosting (frontend). The full build/deploy process takes 5–8 minutes. If you are actively debugging or testing a configuration change (such as Google Secret Manager bindings), waiting for CI/CD bottlenecks development.
2. **Infrastructure Validation**: Executing a manual `gcloud run deploy` command prints errors directly in your terminal, making it immediately clear if the service fails to bind secrets or crashes on startup.
3. **Control over Secrets**: The backend depends on third-party API keys and secrets (e.g. `GEMINI_API_KEY`, `JWT_ADMIN_SECRET`, `DEEPGRAM_API_KEY`). Direct deployments ensure these bindings are active and validated on the Cloud Run container.

---

## Step 0: Pre-Flight Verification

Before pushing anything to `main`, ensure that all local tests pass and the frontend compiles without TypeScript errors.

### 0a. Verify Backend Tests
Run the pytest suite, filtering out known voice-agent mock exclusions:
```powershell
python -m pytest backend/tests/ -v --tb=short -k "not test_orchestrator_mercy_rule_on_attempt_4 and not TestMercyMCQHelpers and not test_mercy_rule_emits_mcq and not test_surrender_triggers_mcq and not test_mcq_correct_answer_advances and not test_start_prep_idempotent"
```

### 0b. Verify Frontend Production Build
Confirm the Next.js frontend builds cleanly. This prevents pushing code that will crash the Firebase App Hosting pipeline:
```powershell
npx next build
```

---

## Step 1: Save Feature Branch Progress

Ensure your local feature branch is committed and pushed to remote origin.

```powershell
# Get your current branch name
git branch --show-current

# Stage, commit, and push your work
git add .
git commit -m "feat: complete active task changes"
git push origin <your-feature-branch>
```

---

## Step 2: Merge into Main Branch

Switch to `main`, sync the remote repo to avoid divergence, and merge your branch.

```powershell
# 1. Switch to main
git checkout main

# 2. Pull down the latest remote main
git pull origin main

# 3. Merge your feature branch (use --no-ff to preserve history)
git merge <your-feature-branch> --no-ff -m "merge: sync <your-feature-branch> into main"
```

> [!CAUTION]
> ### 🛑 MANDATORY HUMAN GATE — NO EXCEPTIONS
> **You MUST stop and ask the user (Steve Jobs) for permission before running the `git push` command on `main`.**
> Present a summary of:
> 1. Which commits are about to be pushed.
> 2. What files were changed.
> 3. Ask: *"Ready to push to main? Please confirm."* and wait for explicit confirmation.

Once approved, push to main:
```powershell
git push origin main
```

---

## Step 3: Switch back to Feature Branch
To keep your workspace isolated, return to your working feature branch:
```powershell
git checkout <your-feature-branch>
```

---

## Step 4: Manual Backend Deploy to Cloud Run (Optional / Debug)

If the CI/CD pipeline is slow or if you are debugging container startup, deploy the backend service manually to Cloud Run using the last successfully compiled Docker image from Artifact Registry.

```powershell
gcloud run deploy aviationchat-backend `
  --image us-east1-docker.pkg.dev/aviationchat/aviationchat-repo/aviationchat-backend:latest `
  --region=us-east1 `
  --project=aviationchat `
  --allow-unauthenticated `
  --set-env-vars "GCP_PROJECT_ID=aviationchat" `
  --set-env-vars "CORS_ORIGINS=https://aviationchat.org" `
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest,JWT_ADMIN_SECRET=JWT_ADMIN_SECRET:latest,DEEPGRAM_API_KEY=DEEPGRAM_API_KEY:latest" `
  --memory 1Gi `
  --cpu 1 `
  --timeout 3600 `
  --session-affinity `
  --concurrency 40 `
  --min-instances 1 `
  --max-instances 5
```

---

## Step 5: Verification & Health Checks

Verify that both the backend and frontend are healthy.

### 5a. Check Active Revisions
Ensure the latest revision on Cloud Run is active:
```powershell
gcloud run revisions list --service=aviationchat-backend --region=us-east1 --project=aviationchat --limit=3
```

### 5b. Health Endpoint Check
Query the backend health route:
```powershell
Invoke-RestMethod -Uri "https://aviationchat-backend-856831340418.us-east1.run.app/health" -Method GET
```
*(Expects `{"status":"ok"}`)*

### 5c. Fetch Live Application Logs
If the deployment fails or /health returns an error, retrieve the container startup logs:
```powershell
gcloud run services logs read aviationchat-backend --region=us-east1 --project=aviationchat --limit=20
```

### 5d. Firebase App Hosting Frontend Deployment
Firebase App Hosting automatically triggers on pushing to `main`. Verify the deployment status on the live site:
- Live URL: [https://aviationchat.org](https://aviationchat.org)
- Status checks can be verified on the Firebase Console or by checking [apphosting.yaml](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/frontend/apphosting.yaml) parameters.

---

## Step 6: Post-Deployment Sync

Finally, update the project status tracking documents to keep active context clean:
- Update [active-context.md](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/_bmad-output/active-context/active-context.md).
- Reference the deploy skill details in the main [SKILL.md](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/.agent/skills/deploy-backend/SKILL.md) if needed.
