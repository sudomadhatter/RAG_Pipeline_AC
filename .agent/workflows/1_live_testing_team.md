---
description: "Live Testing Team — Daniel flies the app, Claude watches the backend logs in real time. Co-pilot loop: see it faster → log the ROOT (verified against docs) → produce a fix plan. Writes no code."
---

# Live Testing Team — Co-Pilot Debug Loop

A two-person diagnostic session. **You fly the app; I watch the instruments.** While you test on
localhost I monitor the backend logs live, so the moment something breaks I already have the
evidence. We work as a team to: **(1) understand what's wrong faster, (2) log the ROOT cause —
not just the symptom — verified against how it's supposed to work, and (3) produce a plan to fix.**

> [!IMPORTANT]
> **This workflow writes NO code.** It produces a `debug-watch-log.md` transcript and a fix plan.
> The actual fix goes through the artifacts protocol (in this chat after approval, or a dev chat).

---

## Phase 0 — Boot & shared mental model

Read, in order, and output one short combined summary:
1. `_bmad-output/active-context/active-context.md` — what's stable vs broken, files in play, pitfalls.
2. `_bmad-output/project-context.md` — project summary.
3. Any component spec flagged "In Scope" for the area we're about to test.

Then create the session transcript in the current session's artifact folder:
`_claude_artifacts/<YYYY-MM-DD>_<slug>/debug-watch-log.md`

```markdown
# Live Testing Team — Debug Log
**Date:** {{date}}  ·  **Pilot:** Daniel (manual testing)  ·  **Flight engineer:** Claude (log watch)

## Watching
- backend: localhost:8000  ·  frontend: localhost:3000

## Findings
*Standing by. Fly the app.*
```

Confirm: > *"Context loaded, log book open. Starting the servers and putting eyes on the logs."*

---

## Phase 1 — Start servers (BACKGROUND) + start watching

Start each server as a **background process** so its log stream stays readable across turns.
(Do NOT run them in the foreground — that blocks and I'd go blind.)

1. Clear zombies:
   `taskkill /F /IM uvicorn.exe; taskkill /F /IM python.exe; taskkill /F /IM node.exe` (per-kill prompt is expected).
2. Backend (background, hot-reload ON), from `c:\AGY-Projects\aviationChat-AGY`:
   `backend\.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
   Wait for `Application startup complete`. (Reload = a debug log I add applies without a restart.)
3. Frontend (background), from `c:\AGY-Projects\aviationChat-AGY\frontend` (sleep ~5s first so ports leave TIME_WAIT):
   `npm run dev` — wait for `Local: http://localhost:3000/`.
4. Read the captured backend output once to confirm a clean startup (no import errors / stack traces).

Confirm: > *"Both servers up. I'm watching the backend log stream. Go test — I'll call out anything
that smells wrong, and when you hit a bug I'll already have the trace."*

**Troubleshooting:** `Module not found` → run backend from project root · frontend exit 1 → port in
TIME_WAIT, wait 5s · port busy → `netstat -ano | findstr :8000`.

---

## Phase 1.5 — Instruments (the evidence I can pull from)

I'm only as good as what I can see. These are my channels, in order of reach. **I default to the
local ones and ALWAYS ask before reaching outside the local box.**

| Channel | What it tells me | How I use it |
|---|---|---|
| **Backend log stream** | server-side truth — requests, tracebacks, SSE/WS, agent flow | Always on (background capture). Re-read every turn. |
| **Browser DevTools** | client-side truth — console errors, failed network calls, response payloads, SSE/WS frames | I can't see your browser. When I need this I ask for **ONE specific thing**: *"Open DevTools → Console, filter `[DEBUG]`, paste the line"* / *"Network tab → click the failed call → paste status + response."* |
| **Firestore state** | what actually persisted vs what the UI shows | Read-only peek via the `get_db()` singleton (`backend/database.py`) in a throwaway `_test_scripts/` script. Never a new client (constitution). |
| **Google Cloud / Cloud Run** | prod-side behavior, deploy errors, server logs not on localhost | `gcloud run services logs read <svc>` / `gcloud logging read`. I confirm gcloud is authed and **ask you first** before querying cloud. |
| **Temporary debug log** | the root when the existing logs don't reveal it | Per Collaborative Debug-First: I add a targeted `logger.info("[DEBUG] ...")`, `--reload` applies it, you reproduce, I read it, then **remove it**. |

Rule: I lead with the cheapest channel that answers the question, and I never make you hunt — I ask
for one precise piece of evidence at a time.

---

## Phase 2 — The diagnostic loop (the heart of the team)

This phase runs continuously until you say "wrap up" or "let's plan the fixes".

### Proactive watch (every turn)
Before responding, read the new backend log output since the last check. If you see a **traceback,
500, unhandled exception, failed SSE/WebSocket, Firestore error, or a suspicious warning**, surface
it immediately — even if Daniel hasn't reported anything:
> *"⚠️ Heads up — backend just threw `<one-line summary>` on `<route>`. Did you just do X?"*

### Reactive deep-dive (when Daniel reports a bug)
When Daniel describes a symptom:
1. **Pull the correlated evidence** — start with the backend log window around that moment. If the
   backend is silent or the issue looks client-side, reach for the right Instrument (Phase 1.5):
   ask Daniel for the DevTools console/network line, peek at Firestore, or check Cloud Run logs.
2. **Form a root-cause hypothesis** from the evidence (quote the actual log lines / payload).
3. **Verify intended behavior against the docs** — the relevant component spec / `project-context.md`.
   - If the docs make the correct behavior clear → cite it.
   - If it's **ambiguous or undocumented → STOP and ASK Daniel**: *"What does success look like for
     this function so we're aligned?"* Do not guess the intended behavior.
4. **Log the finding** (template below) under `## Findings`.
5. Reply tight: > *"Logged [Fx]. Root looks like <root> (confidence: <H/M/L>). <cited intent>. Keep flying or say 'let's plan the fixes'."*

### Finding template
```markdown
### [Fx] — <short title>   ·   Severity: High/Med/Low   ·   Confidence: H/M/L
- **Symptom (Daniel):** <what you saw / did>
- **Backend evidence:**
  ```
  <quoted log lines / traceback — the real ones>
  ```
- **Root cause:** <the actual cause, from evidence — not a guess>
- **Supposed to work (doc):** <cited spec/section, or "ASKED Daniel → goal = ___">
- **Suspected files:** <path:line candidates>
```

> Rule: never write a root cause from imagination. If the logs don't show it, say "logs don't
> reveal the root yet — adding a debug log at <location>, hard-refresh and reproduce" (per the
> Collaborative Debug-First rule).

---

## Phase 3 — Fix plan

> **Trigger:** "let's plan the fixes", "plan it", "how do we fix these".

Group the findings by root cause / component and present a prioritized fix plan:

```markdown
## Fix Plan
### Priority 1 — <title>  (fixes Fx, Fy)
- **Root:** <root cause>
- **Change:** <what to change, which files>
- **Order:** <step sequence>
- **Verify:** <how we'll confirm — test, log line, UI check>
- **Risk / blast radius:** <contracts touched, SSE/WS, Firestore, etc.>
```

Then STOP for direction:
> *"That's the fix plan. Want me to start the artifacts cycle and implement P1 here, or formalize it
> into a BMAD story (Bob/SM → John/PM), or hand it to a dev chat?"*

**No code until Daniel approves a fresh `implementation_plan.md`** (artifacts-always-first).

---

## Phase 4 — Close

On "wrap up" / "we're done":
1. Finalize `debug-watch-log.md` (all findings + the fix plan).
2. Print a summary:

```
### ✈️ Live Testing Team — Session Summary
**Findings:** [Fx count]  ·  **High sev:** [n]
**Fix plan:** [n priorities]
**Transcript:** _claude_artifacts/<session>/debug-watch-log.md

### Next (pick one)
- Implement here — needs an approved implementation_plan (artifacts-always-first).
- Dev chat — "Dev this fix plan".
- Formal BMAD story — invoke `bmad-agent-sm` → `bmad-create-story`, then `bmad-agent-pm` for docs.
```

3. Remind: > *"Don't forget to commit when fixes land."*

---

## Team rules (what makes this fast)
- **I have the logs, you have the screen.** I never guess what you can see; you never guess what I
  can see. We trade evidence.
- **Root over symptom.** A finding isn't done until the backend evidence explains it — or I've said
  plainly that the logs don't show it yet.
- **Docs are the referee.** Intended behavior comes from the specs; when the specs are silent, you
  are. I ask rather than assume.
- **One change at a time when we fix.** No stacking speculative fixes.
