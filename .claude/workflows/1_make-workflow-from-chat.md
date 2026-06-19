---
description: # SYSTEM DIRECTIVE: CHAT-TO-WORKFLOW EXTRACTION
---

# SYSTEM DIRECTIVE: CHAT-TO-WORKFLOW EXTRACTION

## OBJECTIVE
Analyze the entirety of the preceding chat history. Distill the complex problem-solving process, architectural decisions, and finalized code into a structured, reusable, and reproducible workflow document.

## INSTRUCTIONS
1. Context Parsing: Review the chat history to identify the core problem statement, the iterative debugging/refinement phases, and the final verified solution. Disregard conversational filler and dead-end approaches unless they highlight crucial edge cases.
2. Component Extraction: Isolate the essential technical elements required to execute the solution, including:
   - Environment configurations, dependencies, and file structures.
   - Core architectural decisions and rules.
   - Final, working code blocks (omitting deprecated iterations).
3. Workflow Construction: Translate the extracted information into a sequential, actionable guide. The workflow must be written so that an autonomous agent or another developer can recreate the exact solution from scratch.
4. Formatting Constraint: Output the finalized workflow strictly in Markdown format, adhering exactly to the template structure provided below.

---

## EXPECTED OUTPUT TEMPLATE
Generate the response using the exact structure below. Do not include introductory or concluding conversational text.

### Workflow: [Insert Descriptive Title of the Solved Problem]

**Objective:** [Provide a clear, 1-2 sentence summary of what this workflow achieves based on the chat's final outcome.]

**Prerequisites & Context:**
- [List required dependencies, packages, or specific IDE environment setups]
- [List crucial file paths or repository structures discussed]
- [State any overriding architectural rules or agentic standards applied]

**Execution Steps:**
1. **[Phase 1 Name - e.g., Setup / Scaffold]**: 
   [Clear, imperative instruction for the agent/developer]
   [Insert Associated Code Snippet Here]

2. **[Phase 2 Name - e.g., Implementation]**: 
   [Clear, imperative instruction]
   [Insert Associated Code Snippet Here]

*(Continue sequence until the full solution is documented)*

**Verification & Expected Output:**
- [Provide the specific command, test, or visual check required to verify the implementation was successful based on our chat.]

**Historical Context / Edge Cases Avoided:**
- [Briefly document any major roadblocks we encountered in the chat and the specific strategy we used to bypass them, ensuring future agents do not repeat the same mistakes.]
