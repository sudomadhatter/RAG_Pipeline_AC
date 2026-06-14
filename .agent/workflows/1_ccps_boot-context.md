---
description: Session boot — reads active-context, identifies in-scope component specs, and confirms current sprint state before work begins.
---

# Boot Context (G1)

Quick-start command to ground yourself at the beginning of any session. This is the manual trigger for Guardrail G1.

## Step 1: Read Active Context

// turbo
Read `_bmad-output/active-context/active-context.md` and output a `<context>` block summarizing:
- **Sprint Objective**: What are we working on?
- **Stable**: What's tested and working?
- **Broken**: What's known-broken or in review?
- **In Play**: Which files are currently being modified?
- **Pitfalls**: Any gotchas from recent bugs?

## Step 2: Identify In-Scope Component Specs

// turbo
Check the "Component Specs In Scope" section of active-context. For each listed spec, read the spec from `_bmad-output/component-specs/` and note its **Invariants** section.

If no specs are listed, say:
> "No component specs flagged as in-scope. I'll load specs as needed based on what we work on."

## Step 3: Confirm Guardrails

Remind the user which guardrails are active for this session:
- **G2**: Component spec compliance — check specs before modifying spec'd components
- **G3**: Targeted edits only — no full-file rewrites
- **G5**: Agent authority boundaries — each agent has a single responsibility
- **G6**: Firestore singleton — all access through `get_db()`
- **G8**: Research-first — read files before editing them

## Step 4: Ready

Say:
> "Context loaded. [Sprint objective]. [N bugs in review / all clear]. Ready to work — what's the plan?"
