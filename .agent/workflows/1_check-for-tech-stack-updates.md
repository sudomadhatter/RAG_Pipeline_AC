---
description: Audit and update the core tech stack (Antigravity, BMAD, ADK, MCPs) to ensure everything is on the latest version.
---

# Tech Stack Audit Workflow

This workflow checks for updates across all core tools and frameworks used in the AGY Projects.

## Step 1: Check Antigravity (BMAD Method)
Run a `git pull` on the BMAD method repository to ensure we have the latest workflows, agents, and slash commands.

// turbo
```powershell
cd c:\AGY-Projects\aviationChat-AGY\.agent && git status
```

Check if the `.agent/` folder is tracking a git remote. If yes, pull. If not, note it so the user can manually sync.

## Step 2: Check Google ADK Version
Check the currently installed ADK version and compare against the latest published release.

// turbo
```powershell
cd c:\AGY-Projects\aviationChat-AGY && .\.venv\Scripts\pip show google-adk
```

Then search for the latest version:
```powershell
.\.venv\Scripts\pip index versions google-adk
```

Report: Current version vs Latest version. If outdated, flag as a **Collaboration Required** item since upgrading may require the user to test manually.

## Step 3: Check Google Generative AI / Vertex SDK
```powershell
.\.venv\Scripts\pip show google-generativeai
.\.venv\Scripts\pip show google-cloud-aiplatform
```

## Step 4: Check MCP Servers
Review the active MCP servers configured in the project:
- **Firestore MCP** 
- **Cloud Run MCP**

Check if there are newer versions available via `npm` or the relevant package source.

## Step 5: Check Firebase Admin SDK
```powershell
.\.venv\Scripts\pip show firebase-admin
```

## Step 6: Check Frontend (JetChat / AviationChat Next.js)
```powershell
cd c:\AGY-Projects\aviationChat-AGY\frontend && npm outdated
cd c:\AGY-Projects\jetChat-AGY\frontend && npm outdated
```

## Step 7: Report
Produce a **Tech Stack Audit Report** artifact with:

| Package             | Current | Latest  | Action Required |
| ------------------- | ------- | ------- | --------------- |
| google-adk          | x.x.x   | x.x.x   | Upgrade / OK    |
| google-generativeai | x.x.x   | x.x.x   | Upgrade / OK    |
| firebase-admin      | x.x.x   | x.x.x   | Upgrade / OK    |
| BMAD workflows      | date    | latest  | Pull / OK       |
| Antigravity         | version | version | Update / OK     |

Flag anything outdated as a **Collaboration Required** item for the user to approve before upgrading, since package upgrades can break things.

## Step 8: Notify User
Present the full report and wait for approval before executing any upgrades.
