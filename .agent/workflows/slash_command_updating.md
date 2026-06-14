---
name: slash_command_updating
description: Sync local workflows to the global menu, fixing the Antigravity ghost bug perfectly.
---

# Slash Command Updating

**Goal**: Fix the Antigravity `.agent` file-watcher bug by forcibly copying local workflows and skills to the global Antigravity `global_workflows` cache. This ensures new commands appear instantly and old, deleted ghosts are purged.

## System Execution (AI ONLY)

When the user runs this command, the AI is instructed to execute the following PowerShell `run_command`:

```powershell
# Paths
$LocalWorkflows = "$env:CD\.agent\workflows"
$GlobalDir = "$env:USERPROFILE\.gemini\antigravity\global_workflows"

# 1. Get the list of names of all valid local workflows
$LocalFiles = Get-ChildItem -Path $LocalWorkflows -Filter "*.md" | Select-Object -ExpandProperty Name

# 2. Identify global ghosts: files in Global that aren't 'bmad-*' and aren't in the local list
Get-ChildItem -Path $GlobalDir -Filter "*.md" | Where-Object {
    ($_.Name -notmatch '^bmad-') -and ($LocalFiles -notcontains $_.Name)
} | Remove-Item -Force

# 3. Force-copy the active local workflows to the global directory
Copy-Item -Path "$LocalWorkflows\*.md" -Destination $GlobalDir -Force

Write-Host "✅ Slash commands synced to global cache successfully. The ghosts are purged!"
```

Execute this script unconditionally to clean the slash command registry for the user in a single, clean process.
