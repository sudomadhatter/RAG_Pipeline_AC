---
description: Interactive Firestore user data cleanup. List users, wipe learning data, or delete orphan accounts from the aviationchat-database.
---

# Firebase User Cleanup Workflow

Interactive data management for the Firestore `users` collection. Use this when you need to clean up test accounts, wipe a student's progress for re-testing, or remove orphan users whose Firebase Auth accounts were deleted.

## Step 1: Audit Current Users

Run the user manager in `list` mode to show every user document, their profile data, and subcollection inventory:

```powershell
// turbo
python -m backend.scripts.firebase_user_manager list
```

Present the results to the user as a clean summary table.

## Step 2: Ask What Needs Cleaning

After showing the inventory, ask the user which operation they need. Use the `ask_question` tool with these options:

- **Wipe a user's data (keep profile)** — Clears learning progress, session logs, quiz results, etc. but keeps the user's name, call sign, and profile fields. Good for resetting a test user for fresh testing.
- **Delete a user completely** — Removes the user document AND all subcollections. Use for orphan accounts or test users that should no longer exist.
- **Delete multiple orphan users** — Batch-delete users that have no real Firebase Auth account (test UIDs, deleted accounts).
- **Selective wipe (specific data only)** — Wipe only a specific category of data: `learning` (mastery, lesson plans, socratic sessions), `activity` (quizzes, session logs, SAR interactions, chat history), `personal` (notebook, dossier, profile), or `system` (media engagement, usage).

## Step 3: Identify Target User(s)

Based on the user's choice, ask which UID(s) to operate on. Reference the audit table from Step 1 so they can pick by name or number.

## Step 4: Dry Run First

**Always dry-run first.** Run the command WITHOUT `--confirm` to show what WOULD be deleted:

For **wipe** (full):
```powershell
python -m backend.scripts.firebase_user_manager wipe <UID>
```

For **wipe** (group-specific):
```powershell
python -m backend.scripts.firebase_user_manager wipe <UID> --group learning
```

For **wipe** (specific subcollections):
```powershell
python -m backend.scripts.firebase_user_manager wipe <UID> --subcollections quiz_results,session_logs
```

For **delete**:
```powershell
python -m backend.scripts.firebase_user_manager delete <UID>
```

Show the dry-run output to the user and ask for explicit confirmation before proceeding.

## Step 5: Execute with Confirmation

Only after the user explicitly approves the dry-run output, add `--confirm` to execute:

```powershell
python -m backend.scripts.firebase_user_manager wipe <UID> --confirm
```
or
```powershell
python -m backend.scripts.firebase_user_manager delete <UID> --confirm
```

For batch operations on multiple UIDs, run each one sequentially and report results after each.

## Step 6: Verify

Run the `list` command again to confirm the cleanup was successful:

```powershell
// turbo
python -m backend.scripts.firebase_user_manager list
```

Report the before/after state to the user.

---

## Reference: Subcollection Groups

The `--group` flag targets these categories:

| Group | Subcollections | What It Clears |
|-------|---------------|----------------|
| `learning` | mastery_state, learning_context, lesson_plan_cache, socratic_sessions, quiz_tutor_sessions, acs_knowledge_ledger | All lesson progress, mastery states, cached plans, Socratic/tutor sessions, ACS knowledge ledger |
| `activity` | quiz_results, session_logs, sar_interactions, chat_history, sully_sessions | Quiz scores, session telemetry, SAR reward data, conversation history, voice CFI sessions |
| `personal` | notebook, cognitive_dossier, global_profile | Saved notes, AI personality model, profile extensions |
| `system` | media_engagement, usage | Video watch tracking, daily usage counters |

## Reference: Script Location

The backing script lives at `backend/scripts/firebase_user_manager.py` and uses the `auth_keys/service-account.json` credential. It connects to the `aviationchat-database` Firestore database.
