---
description: List and clean up accumulated temp files in _test_scripts/. Shows what's there, asks what to keep, deletes only what you approve.
---

# Clean Test Scripts Directory

This workflow helps you take out the trash from `_test_scripts/`. It lists everything, lets you decide what stays, and removes the rest.

## Steps

1. **List contents** of the `_test_scripts/` directory with file sizes and last-modified dates:
// turbo
```powershell
Get-ChildItem -Path "_test_scripts" -Recurse | Format-Table Name, Length, LastWriteTime -AutoSize
```

2. **Report the inventory** to the user. Present the file list as a table and ask:
   > "Here's what's currently in `_test_scripts/`. Which files should I **keep**? Everything else will be deleted."

3. **Wait for the user's response.** Do NOT proceed until the user explicitly identifies which files to keep or delete. If the user says "delete all", confirm once before proceeding.

4. **Delete only the approved files** using `Remove-Item`:
```powershell
Remove-Item -Path "_test_scripts/<filename>" -Force
```
Repeat for each file approved for deletion. Do NOT delete files the user wants to keep.

5. **Report final state** — list the directory again to confirm the cleanup:
// turbo
```powershell
Get-ChildItem -Path "_test_scripts" -Recurse | Format-Table Name, Length, LastWriteTime -AutoSize
```

6. **Done.** Report what was removed and what remains.
