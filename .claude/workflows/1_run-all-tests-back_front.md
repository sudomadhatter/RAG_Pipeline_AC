---
description: Run the complete backend (pytest) and frontend (vitest/jest) test suites and report results.
---

# Run All Tests

This workflow runs the complete test suite for both backend and frontend of AviationChat.

## Step 0: Session Boot (G1)

// turbo
Read `_bmad-output/active-context/active-context.md` to understand:
- What's currently broken (tests may reflect known issues)
- Files currently in play (to relate failures to recent changes)

This prevents false alarm investigations on known broken areas.

---

## Steps

### 1. Run Backend Unit Tests
Navigate to the backend and run pytest:

// turbo
```powershell
cd c:\Sudo_Hatter_Command\Projects\aviationChat-AGY
.\backend\.venv\Scripts\pytest backend/tests/ -v
```

**Expected Output:** All tests should pass with detailed output

### 2. Run Backend Tests (Alternative - backend venv)
If the root venv is not configured:

```powershell
cd c:\Sudo_Hatter_Command\Projects\aviationChat-AGY\backend
..\.venv\Scripts\pytest tests/ -v
```

### 3. Run Frontend Tests
Navigate to the frontend and run tests:

// turbo
```powershell
cd c:\Sudo_Hatter_Command\Projects\aviationChat-AGY\frontend
npm test
```

**Expected Output:** All frontend tests should pass

### 4. Check Test Coverage (Optional)
Generate a coverage report for the backend:

```powershell
cd c:\Sudo_Hatter_Command\Projects\aviationChat-AGY
.\backend\.venv\Scripts\pytest backend/tests/ --cov=backend --cov-report=html
```

View the coverage report at `htmlcov/index.html`

---

## Step 5: Analyze Failures Against Component Specs

If any tests fail:
1. **Cross-reference with active-context** — is this a known broken area?
2. **Check the relevant component spec (G2)** to understand the expected behavior:
   - Backend agent test failures → `specialist-pipeline.md`, `socratic-teaching.md`, `admin-grading.md`
   - Frontend component test failures → `frontend-sse.md`, `dashboard-mastery-ui.md`
3. **Check invariants** — does the failure indicate an invariant violation?
4. **Report to user** with component spec context:
   > "3 tests failed. 1 is a known issue from active-context (Bug 3). The other 2 involve the SSE pipeline — checking `frontend-sse.md` invariants..."

---

## Step 6: Update Active Context (if needed)

If tests reveal NEW issues not already in active-context:
- Add them to the "What's Broken" section of `_bmad-output/active-context/active-context.md`
- Note the failing test name and suspected root cause

---

## Test Organization

### Backend Tests
- **Location:** `backend/tests/`
- **Pattern:** `test_*.py` for unit tests
- **Run individual:** `.\backend\.venv\Scripts\pytest backend/tests/test_<module>.py -v`

### Frontend Tests
- **Location:** `frontend/src/__tests__/` or adjacent to components
- **Pattern:** `*.test.tsx` or `*.spec.tsx`
- **Run individual:** `npm test <test-name>`

## Notes

- Always run tests before committing code
- Add tests for new features and bug fixes
- Aim for high test coverage on critical business logic (agents, auth, RAG pipeline)
- Use `/1_adk-agent-testing` for interactive ADK agent testing
