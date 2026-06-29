---
description: Kills existing node/python processes and starts the frontend and backend development servers.
---

# Restart Dev Environment Workflow

This workflow safely cleans up any stalled or zombie processes on your development ports and starts up both the FastAPI backend and Next.js frontend in one motion. It's best practice to run this after major changes or when you suspect zombie processes are holding ports 8000 or 3000.

## Step 0: Session Boot (G1)

Before touching anything, load current project state.

// turbo
Read `_bmad-output/active-context/active-context.md` and output a brief `<context>` summary confirming:
- Current sprint objective
- What's stable vs. broken
- Files currently in play

If any component spec is flagged as "In Scope" in the active context, note which spec(s) to be aware of during this session.

## Step 1: Kill Existing Processes

We first ensure no zombie processes are running.

```powershell
// turbo-all
taskkill /F /IM uvicorn.exe
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

## Step 2: Start Backend Server

Launch the FastAPI backend using the project venv.

```powershell
// turbo
cd c:\Sudo_Hatter_Command\Projects\aviationChat-AGY
backend\.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Step 3: Start Frontend Server

Launch the Next.js development server. We introduce a small sleep to ensure ports have gracefully exited `TIME_WAIT` states from the kill command.

```powershell
// turbo
cd c:\Sudo_Hatter_Command\Projects\aviationChat-AGY\frontend
Start-Sleep -Seconds 5
npm run dev
```

## Step 4: Confirm & Hand Off

After both servers report healthy output, confirm to the user with the link:

> "Dev environment is up → [http://localhost:3000](http://localhost:3000). Current context: [sprint objective from Step 0]. Ready to work."

If the user's next task involves modifying code, remind them of relevant guardrails:
- **G2**: Check component specs before modifying spec'd components
- **G3**: Targeted edits only — no full-file rewrites
- **G8**: Research-first — read files before editing them
