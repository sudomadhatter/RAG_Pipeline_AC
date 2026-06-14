# Workflow: Update Repo Map

> **Trigger:** User types `/1_update_repo_map`

1. **Acknowledge the command:**
   "Generating the latest repository map..."

2. **Execute the generator script:**
   Run the following terminal command (ask for permission if required, but ideally just run it if allowed):
   ```bash
   python scripts/generate_repo_map.py
   ```

3. **Verify the output:**
   Briefly check that `docs/repo-map.md` was successfully written and updated.

4. **Confirm to user:**
   "✅ Repo Map successfully updated in `docs/repo-map.md`. The AI context is now fully up to date with the latest code structure."
