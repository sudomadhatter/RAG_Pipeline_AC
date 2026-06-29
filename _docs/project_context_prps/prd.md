---
version: 'V2.1'
previousVersion: 'V2.0'
classification:
  projectType: 'Web App (SaaS/PWA)'
  domain: 'Aviation EdTech'
  complexity: 'High'
  projectContext: 'Brownfield (V2 Reset)'
sourceDocuments:
  - 'prd-v1.md (V1 PRD — archived)'
  - 'prd_addendum_meta-learning.md (Admin Agent & Growth)'
  - 'prd_addendum_pedagogical-engine-v2.md (Engineering Specification)'
  - '_01_My/Docs/Specialist/V2 Master PRD & Architecture (Mentor Blueprint)'
  - 'v1-to-v2-delta-analysis.md (Change Inventory + Consultant Rulings)'
  - 'prd_addendum_v2.1.md (RKP Pedagogical Spine & 6-Search Architecture — Correct Course)'
---

# Product Requirements Document — AviationChat V2.1

**Author:** Daniel Lohner  
**Date:** 2026-04-03 (V2.1 Correct Course — RKP Pedagogical Spine)  
**Audience:** Engineering, Product, QA, & Investors

> [!IMPORTANT]
> **V2.1 Correct Course — RKP Pedagogical Spine.** This PRD supersedes V2.0. All new stories, epics, and development MUST reference this document. The V2.1 Correct Course adds the RKP manifest system, 6-Search RAG architecture, 4-step lesson flow, and Agent 1/Agent 2 data injection split. See the [V2.1 Addendum](file:///C:/Users/dlohn/.gemini/antigravity/brain/5681ffcf-dd74-402a-aa96-aa0e69c0d149/prd_addendum_v2.1.md) for change traceability.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Problem & Market Gap](#2-the-problem--market-gap)
3. [Success Criteria](#3-success-criteria)
4. [Product Scope — The Four Core Pillars](#4-product-scope--the-four-core-pillars)
5. [The AI Agent Ecosystem](#5-the-ai-agent-ecosystem)
6. [The Multi-Agent Toolbelts](#6-the-multi-agent-toolbelts)
7. [State Management — The Two-Tiered Cognitive Dossier](#7-state-management--the-two-tiered-cognitive-dossier)
8. [The Data Moat — SAR Telemetry & The Evolution Engine](#8-the-data-moat--sar-telemetry--the-evolution-engine)
9. [User Journeys](#9-user-journeys)
10. [Functional Requirements](#10-functional-requirements)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Domain-Specific Requirements](#12-domain-specific-requirements)
13. [Business KPIs & Competitive Moat](#13-business-kpis--competitive-moat)
14. [Engineering Execution — Brownfield Rules](#14-engineering-execution--brownfield-rules)
15. [The 13 Locked Architectural Decisions](#15-the-13-locked-architectural-decisions)
16. [Growth Features & Future Vision](#16-growth-features--future-vision)

---

## 1. Executive Summary

The objective of this engineering initiative is to build a multi-agent educational pipeline that algorithmically forces aviation students into their Zone of Proximal Development (ZPD). We are replacing static prompt engineering with a dynamic, data-driven flywheel. By equipping our AI agents with a "Pedagogical Toolbelt" of distinct teaching strategies and tracking their efficacy via State-Action-Reward (SAR) telemetry, the platform will continuously A/B test itself. Over time, the system will mathematically discover the optimal teaching methods for every FAA concept and autonomously update its own curriculum.

**Context:** AviationChat solves a problem affecting ~60,000 new student pilots annually: inefficient, unverified, unstructured oral exam prep that wastes thousands of dollars and produces pilots who pass checkrides without truly understanding the regulations. AviationChat replaces fragmented self-study with a coordinated team of AI tutors that deliver verified, structured, Socratic-method instruction — mapped directly to the FAA's Airman Certification Standards (ACS).

**This is not a chatbot. It's a deterministic curriculum engine with an AI instructor team built on top of it.**

---

## 2. The Problem & Market Gap

### What Student Pilots Actually Experience

| Pain Point | Real-World Impact |
|-----------|------------------|
| Decision Paralysis | Students spend more time deciding what to study than actually studying. |
| No Mastery Tracking | No tool maps progress against the specific ACS tasks a DPE will test. |
| Surface-Level Learning | Existing tools teach memorization, not the reasoning DPEs actually evaluate. |
| Hallucination Risk | Generic AI confidently cites wrong regulations — a literal safety risk. |
| High Retake Cost | Failed oral exams cost $800+ and derail training momentum. |

### The Competitive Landscape

| Solution | What It Does | What It Misses |
|----------|-------------|---------------|
| Sheppard Air | Written test memorization | Zero oral prep, no conceptual understanding. |
| Sporty's / King | High-quality video content | Flight portion only; no oral prep structure. |
| Generic AI (ChatGPT) | Fast, conversational | Hallucinated regulations; no curriculum; no verification. |
| CFI Ground School | Personalized, Socratic | $50–80/hr; not scalable; no data tracking. |
| **AviationChat** | ✅ Structured + Verified + Socratic + Measurable | The ultimate checkride & career companion. |

---

## 3. Success Criteria

### User Success

* **The "Confidence" Metric:** Users report feeling "ahead of the airplane" during their oral exam, specifically citing the ability to reason through regulations rather than just memorizing answers.
* **The "North Star":** **Completion Rate.** A user is successful when they log **100% ACS Application-Mastery** across the 11 study areas and unlock the DPE Voice Agent (Egor).
* **Emotional "Aha!" Moment:** The moment a user sees the Specialist answer from memory and then successfully verifies it against a specific FAR/AIM citation in real-time, building trust that differs from a standard search engine.
* **Study Consistency:** Users engage in daily active study sessions averaging **45 minutes**, validating the "1 hour a day to stay ready" value proposition.
* **Retention Rate:** >85% accuracy on "Review" items (expired topics), validating the spacing effect.

### Business Success

* **DPE Unlock Rate:** 80% of active users reach 60% ACS completion (This is the "Magic Moment" — if they get here, they don't churn).
* **Daily Active Study:** 45 minutes/day average.
* **Beta Validation:** Acquire **50+ active beta users** from the Flight Club partner community with activity spanning > 2 weeks.
* **Commercial Validation:** Convert the initial interested Flight School from "demo viewer" to "paid institutional customer."

### Technical Success

* **Regulatory Accuracy (CRITICAL):** **99%+ accuracy rate** on verified citations. Zero hallucination on cited regulations.
* **Voice Latency:** End-to-end voice response latency **< 800ms** to maintain conversational flow.
* **System Stability:** The verification swarm must operate reliably, handling parallel research agent execution without hanging or timing out.

---

## 4. Product Scope — The Four Core Pillars

### Pillar 1: The ACS Curriculum Engine, RKP Manifests & Prerequisite DAG

The FAA's Airman Certification Standards (ACS) is the live state machine. Every study session maps to a specific ACS task code.

**The "Rule of 4":** Every lesson must cover 4 perspectives:
1. **Legal** (The Rule)
2. **Safety** (The Consequence)
3. **Application** (The Scenario)
4. **Risk Management** (The Human Factors / ADM)

> [!IMPORTANT]
> **V2.1: RKP Manifests as Primary Curriculum Skeleton.** Each of the 34 active PPL lessons has a deterministic `{lesson_id}_rkp.json` manifest authored by the CFI team. RKPs define WHAT to teach; the 6-Search RAG provides HOW to teach it and WITH WHAT authority. The Swarm RAG Agent fetches content for all 4 pillars using the RKP manifest as query source. See FR36 for full specification.

**Terminology:** The curriculum uses a two-level hierarchy: **Modules** (full ACS Task teaching plans, stored in DB1) and **Lessons** (the 34 micro-units within Modules, defined in `curriculum_key.json`). A Module like "I-A: Pilot Qualifications" contains Lessons `PPL_PA_I_A_01` through `_04`. Always "Module" for the ACS Task level, "Lesson" for the 34 micro-units.

**ACS State Machine:** PPL ACS Area I coverage: **34 Lessons** across 10 Modules (oral exam scope). Areas II–XII (flight test practical standards) are out of V1 scope.

**Prerequisite DAG (V2 NEW):** The ACS list is flat — it doesn't tell you that a student must understand AGL/MSL before Cloud Clearances. We are building that Directed Acyclic Graph (DAG) ourselves to enable "Pre-Bunking" (predicting a student's failure before it happens).
- **V1:** 34 Traps (one per lesson) manually hardcoded by CFI (see Engineering Addendum §6)
- **V2:** Full DAG via LLM-assisted generation
- **V3:** Emergent dependencies from aggregate SAR data
- **Schema:** `prerequisite_acs_nodes` string array on curriculum key

---

### Pillar 2: The "Expert Witness" Verification Pipeline

When a student asks a direct question, the platform runs a parallel verification process:

1. **A Fast Tutor (Lane 1 — Talker)** streams an immediate answer (sub-1 second), like a real CFI answering from the lesson plan.
2. **A Research Agent (Lane 2 — Librarian)** simultaneously searches our proprietary dual-database (curated lesson content DB1 + official FAA legal library DB2) using Bridge Key metadata.
3. **A Fact-Checker (Lane 3 — Verifier)** compares the output, issuing citations or corrections. Produces "Living Text" citation snap transitions.

**Engineering Invariant:** Zero hallucination on cited regulations. Every cited regulation traces to a specific document section via Bridge Keys.

**Chat Agent (Intent Classification):** Before routing to the Expert Witness pipeline, the system classifies incoming queries as `CONVERSATIONAL` or `AVIATION_RAG`. Conversational queries are handled directly without invoking RAG.

---

### Pillar 3: The 4-Step Lesson Flow, Socratic Teaching & Strategy Roulette

> [!IMPORTANT]
> **V2.1 Correct Course:** The single "Teach Me" button (FR5) is replaced by a 4-step pedagogical progression: Overview → Flashcards → Socratic → Quiz. See FR39 for full specification.

**The 4-Step Lesson Flow (V2.1):**

| Step | Name | Surface | Description |
|------|------|---------|-------------|
| ① | Lesson Overview | Chat | Agent generates brief overview + explains flashcard system |
| ② | Flashcard Deck | Drawer | Anki-style swipe deck from RKP manifest (see FR37) |
| ③ | Socratic Understanding | Chat | Agent 2 runs 4-pillar Q&A using cached lesson plan |
| ④ | Mastery Quiz | Drawer | MCQ + SJT, 80% pass gate |

**State-Based Unlocking (FR39-B):**
- `mastery_status == "not_started"`: Strict linear (1→2→3→4). Buttons unlock sequentially.
- `mastery_status >= "seen"`: All 4 buttons visible, unlocked from start. Respects adult learners' time.

**The Flashcard Buffer (Architectural Innovation):** The flashcard step isn't just pedagogical — it's an **architectural buffer**. The 6-Search RAG triggers the millisecond the student starts the deck. The 2-5 minutes of active study gives the backend uncontested compute time to run all searches, build the lesson plan, and cache it. By "Begin Socratic," the plan is already cached and waiting. Zero latency. No spinner.

**Agent 1 / Agent 2 Responsibility Split (V2.1):**
- **Agent 1 (Lesson Planner):** Batch job. Receives RKP manifest + 6-Search RAG results. Does NOT receive student struggle data. Builds curriculum-grounded `LessonPlan` with 4 `SocraticNode`s.
- **Agent 2 (Socratic Teacher):** Real-time. Receives cached `LessonPlan` + Tier 2 ACS Ledger + Tier 1 Global Profile + Pre-Bunk (FR34) + Global Traps (FR35). Facilitates Socratic conversation, adapts based on struggle history.

**Planning-First Architecture:** The Socratic Teacher operates on a pre-generated `LessonPlan` (sourced from RKP manifests + 6-Search RAG by Agent 1: Lesson Planner). The plan contains **4 Core Topics** mapped to ACS Perspectives (Legal, Safety, Application, Risk Management) with answer→question pairs. Agent 2 (Executor) facilitates discovery of target answers without improvisation.

> [!IMPORTANT]
> **The Answer-First Doctrine (CRITICAL PEDAGOGY — Non-Negotiable)**
>
> The Socratic Teacher is NOT a question-generating machine. It is a **reverse-engineering engine.**
>
> **Agent 1 (Lesson Planner) builds every node in this order — backwards:**
> 1. **Lock the target answer first.** For each of the 4 Core Topics, Agent 1 identifies the exact knowledge statement the student must be able to articulate — in their own words or verbatim.
> 2. **Then work backwards to the questions.** Knowing the destination, Agent 1 crafts `q1_primary` (the opening question pointing toward the answer) and `q2_scaffold` (the fallback if the student doesn't arrive via Q1).
> 3. **The student must SAY it.** Agent 2 (Executor) is forbidden from revealing the target answer — even after repeated failures. The platform guides the student to the answer through questions, hints, and teaching tools — never by stating it. The student voicing the correct answer is the measurable learning event.
>
> **Why this is the psychology that works:** If Agent 2 explains the answer instead of extracting it, the Bipartite Reward System will detect the failure — student didn't know it, AI told them, quiz pass = Illusion of Competence → reward penalty of `-1.0`. The architecture is built to catch and penalize this exact behavior.
>
> **Connection to the Strategy Roulette:** When Q1 and Q2 fail to guide the student to the target answer, the Strategy Roulette (see below) is the mechanism for upholding this doctrine. Each teaching tool (Analogical Bridging, First Principles, Boundary Testing, The Protégé Effect) is a different path to the same destination — the student saying the correct answer. The tools do not replace the doctrine; they serve it.

**Strategy Roulette (V2 NEW):** If a student answers incorrectly (`EVAL_INCORRECT`), the backend triggers a Strategy Roulette to dynamically inject one of 4 pedagogical tools (Tool 5 is voice-only, excluded from the Roulette):
1. **Analogical Bridging** ("Everyday Life") — Map concept to a non-technical phenomenon
2. **First-Principles Deconstruction** ("The Engineer") — Strip to smallest physical variable, ask binary question
3. **Boundary Testing** ("Absurd Extreme") — Push incorrect premise to catastrophic extreme
4. **The Protégé Effect** ("Role Reversal") — Have student explain to AI (acting as nervous passenger)
5. **Devil's Advocate** ("Confidence Stress-Test") — **FORBIDDEN for Agent 2** — voice agents only (Sully/Egor)

**EVAL_PARTIAL Routing (V2 — Consultant Ruling):** On `EVAL_PARTIAL` (student ~80% correct), the Roulette **does NOT fire**. Agent 2 uses standard Colloquial Validation / Implicit Repair to gently bridge the final 20% gap.

**Colloquial Validation (V2 NEW):** Validate a student's plain-English logic BEFORE injecting FAA terminology. Accept correct reasoning in any vocabulary → seamlessly upgrade to official terms.

**Quiz Bank:** A separate, pre-authored system of multiple-choice questions served AFTER the Socratic session, used exclusively as the mastery gate. Includes **Situational Judgment Tests (SJTs)** for the Risk Management/ADM pillar — 3 options are FAR-compliant (legal), each introducing a different risk; option D is the safest aeronautical decision.

---

### Pillar 4: The Mastery Gate & Bipartite Reward Signal

Students cannot skip ahead. To advance, they must pass through structured gates:

| State | Requirement | Decay |
|-------|------------|-------|
| **Seen** | Complete Socratic Session | — |
| **Rote** | Pass curated MCQ quiz (≥ 80%) | Expires in 14 days |
| **Application** | Pass voice coaching session with Sully | Expires in 21 days |
| **Mastered** | Pass adversarial mock oral with Egor | Permanent |

**Mastery Weights:** `new=0%, seen=0%, rote_level=50%, application=75%, mastered=100%`

**The Bipartite Reward Signal (V2 NEW):** If the AI makes the Socratic chat too easy (giving away hints) and the student subsequently fails the quiz, this is flagged as the **Illusion of Competence**. The database heavily penalizes that specific teaching tool.

**Reward Math Bounds (Consultant Ruling — Locked):**

| State | Score | Meaning |
|-------|-------|---------|
| 🟢 Fast Socratic + Quiz Pass | `1.0` | Perfect tool — max exploit |
| 🟡 Slow Socratic + Quiz Pass | `0.5` | Productive Struggle — valuable for complex topics |
| 🔴 Fast Socratic + Quiz Fail | `-1.0` | **Illusion of Competence** — heavy penalty |
| ⚫ Slow Socratic + Quiz Fail | `0.0` | Neutral — curriculum gap, not tool failure |

---

## 5. The AI Agent Ecosystem

Tasks are strictly siloed across specialized agents to prevent LLM drift.

| Agent | Persona / Role | Architectural Constraints & Mechanics |
|-------|---------------|--------------------------------------|
| **Chuck** | Sales Agent | Pre-auth landing page only. Redirects to signup, never answers technical questions. |
| **Mrs. Coleman** | Onboarding Agent | Chat-based profile setup. Direct `genai.Client` with function-calling tool for in-chat persistence. |
| **Chat Agent** | Intent Classifier | Routes `CONVERSATIONAL` vs `AVIATION_RAG`. Also serves as sole in-app support channel. |
| **Specialist** | The Tutor | Fast answers + multi-step verification pipeline (The "Expert Witness"). |
| **Socratic Teacher** | Formative Coach (Text) | **V2.1: Two-agent architecture.** Agent 1 (Lesson Planner): batch job, receives RKP manifest + 6-Search RAG, builds LessonPlan. Agent 2 (Executor): real-time, receives cached plan + student struggle data. Executes Strategy Roulette. Uses Colloquial Validation. |
| **Sully** | CFI Voice Agent (Application) | Patient coaching. Unlocks after Rote Quiz. Uses the Consequence Engine. |
| **Egor (Igor)** | DPE Voice Agent (Evaluation) | Adversarial mock oral exams. Unlocks at 60% ACS completion. Also available in untracked practice mode. |
| **Admin Agent** | Async Meta-Grader | Grades transcripts asynchronously. Analyzes NLP markers to detect true confusion vs. lucky guesses. Sole authority for Mastery transitions (non-quiz). |

### Agent Context Protocol (ACP)

Every student-facing agent MUST receive a unified `StudentContext` object on session open. Context includes: student profile, mastery summary, and prioritized study queue. Fetched once via `get_student_context(uid)`, cached per session, injected via `{student_context_block}` template variable.

**Data Taxonomy:** `StudentContext` (who they are) ≠ `LearningContext` (what happened this conversation) ≠ `SessionLog` (official record on close).

### Voice AI Overrides

**Algorithmic Latency — "Winding the Clock" (V2 NEW):** Intercept Sully's Voice Activity Detection (VAD). Enforce a hard 3-5 second lock where Sully cannot interrupt the user's silence. A 3-second pause followed by a cohesive answer yields a high ADM score.

> [!WARNING]
> **The Hard Override (V2):** Because VAD interruption is disabled to enforce pedagogical silence, the user must have a safe word to break the loop. The only way Sully will stop talking or allow an interruption is if the user says the exact phrase **"Captain Sully."** This instantly kills the TTS audio buffer and opens the microphone.

**Sully's Consequence Engine — Delayed Didactic Correction (V2 NEW):** Sully is **strictly forbidden** from saying "Wrong" or immediately correcting a procedural error. If the student makes a mistake, Sully must organically calculate the downstream effect and degrade the aircraft's state (e.g., *"Noted. You pulled the mixture. The engine dies. What now?"*).

---

## 6. The Multi-Agent Toolbelts

### Agent 2 (Socratic Teacher) — Strategy Roulette

When Agent 2 detects a student failure (`EVAL_INCORRECT`), the Roulette randomly selects one of the first 4 tools (Devil's Advocate excluded):

1. **Analogical Bridging** ("Everyday Life") — Map the concept to a non-technical physical phenomenon.
2. **First-Principles Deconstruction** ("The Engineer") — Strip the scenario to its absolute smallest physical/mechanical variable. Ask a binary question.
3. **Boundary Testing** ("Absurd Extreme") — Push the user's incorrect premise to a catastrophic extreme.
4. **The Protégé Effect** ("Role Reversal") — Drop the tutor persona. Request the user explain the concept to the AI.
5. **Devil's Advocate** ("Confidence Stress-Test") — **(FORBIDDEN for Agent 2)** Used ONLY by voice agents after Rote mastery proven.

**Negative Primacy Fail-Safe (V2 — Consultant Ruling):** If a voice agent uses Devil's Advocate and the student **folds** (changes their correct answer to the dangerous distractor), the AI **MUST immediately** trigger Tool 2 (First Principles Deconstruction) on the very next turn to aggressively re-establish the correct legal truth.

### Egor (The DPE Evaluator)

Egor does not teach; he stress-tests Pilot-in-Command (PIC) authority. His 4 tools are **completely separate** from Agent 2's teaching tools:

1. **Induced Frustration** ("Career Killer") — Deliver blunt negative feedback, then pivot to a critical ADM question to test emotional compartmentalization.
2. **Weaponized Doubt** ("Are You Sure?") — Respond to a 100% correct answer with deadpan skepticism.
3. **Task Saturation** (The Rapid Pivot) — Interrupt mid-explanation with a compounding emergency.
4. **The "Deep Hole"** (The BS Detector) — Keep asking "Why?" into obscure minutiae. Pass condition: They confidently admit "I don't know, I'll check the POH" (`knowledge_boundary_acknowledged: true`).

### UX Safety Matrix for Egor (from UX Design)

| Egor Tool | UX Risk | Required Safety Design |
|-----------|---------|----------------------|
| Induced Frustration | Genuine upset | "Take a break" soft prompt if session >15 min + rage-quit detection |
| Weaponized Doubt | Must feel SAFE being wrong | **"PRACTICE MODE"** badge visible at all times |
| Task Saturation | Must feel urgent, not buggy | **Voice-only** (no text), organic audio transition |
| The Deep Hole | "I don't know" should feel like VICTORY | Positive reinforcement audio cue, Egor's tone shifts to respectful |

---

## 7. State Management — The Two-Tiered Cognitive Dossier

To protect LLM token limits and prevent context degradation ("Lost in the Middle"), memory uses **Just-In-Time (JIT) Prompt Injection**.

> [!IMPORTANT]
> **V2 Replaces V1 Sliding Window.** The V1 5-entry rolling window (`CognitiveDossierService`) is replaced by a Two-Tiered architecture. The sliding window concept lives on inside each ACS node's `misconception_log` array.

### Tier 1: The Global Profile (~100 tokens, always injected)

```
users/{uid}/global_profile/
├── baseline_frustration_tolerance: float (0.0–1.0, where 0.0 = very patient, 1.0 = easily frustrated)
├── vocabulary_level: "basic" | "standard" | "technical"
├── dpe_stress_resilience_score: float (0.0–1.0, updated by Egor's siloed telemetry)
├── affective_state: "neutral" | "confident" | "confused" | "frustrated" | "anxious"
├── created_at: timestamp
└── updated_at: timestamp
```

### Tier 2: The ACS Knowledge Ledger (JIT per-lesson, ~100-200 tokens)

```
users/{uid}/acs_knowledge_ledger/{acs_code}/
├── acs_topic: "Density Altitude"
├── mastery_status: "not_started" | "in_progress" | "rote" | "application" | "mastered"
├── optimal_tool: "tool_1_analogical"
├── tool_affinity_weights: {           ← PER-NODE, not global (4 tools only — Tool 5 excluded)
│   "tool_1_analogical": 0.85,
│   "tool_2_first_principles": 0.10,
│   "tool_3_boundary_testing": 0.03,
│   "tool_4_protege": 0.02
│ }
├── misconception_log: [               ← Append-only, archived on mastery
│   { "date": "2026-10-12", "note": "Confused high density altitude with high air pressure" }
│ ]
├── total_sar_interactions: int
└── last_interaction: timestamp
```

### JIT Retrieval — Exactly 2 Firestore Reads on Lesson Start

```
Student clicks "Start Lesson: Density Altitude"
  → Read 1: users/{uid}/global_profile/           → inject into ALL agent prompts
  → Read 2: users/{uid}/acs_knowledge_ledger/PA.I.C.K2  → inject into Agent 1 + Agent 2
Total injected context: ~200-300 tokens (constant, regardless of history)
= Infinite memory at constant prompt cost
```

### Service Refactor Map

| Current (V1) | New (V2) | Change |
|-------------|---------|--------|
| `CognitiveDossierService` (5-entry sliding window) | `GlobalProfileService` (Tier 1) | REPLACE |
| — | `ACSKnowledgeLedgerService` (Tier 2 — per-node CRUD + JIT) | NEW |
| `append_dossier_entry()` | `update_global_profile()` + `update_acs_node()` | REPLACE |
| `Learning Context Cache` (per-session) | Tier 2 ACS Ledger (per-ACS-code, permanent) | EXTEND |
| `Agent Context Protocol` (single injection) | Two-phase injection (global + JIT) | REFINE |

---

## 8. The Data Moat — SAR Telemetry & The Evolution Engine

We must stop logging standard chat histories. Every time Agent 2 or Sully speaks, the backend must log a hidden State-Action-Reward (SAR) JSON payload.

### Agent 2 Structured Output — Production JSON Schema (V2)

All Agent 2 responses use Gemini native `response_schema` with the **Sequence Trick** (force `internal_reasoning_log` first):

```json
{
  "internal_reasoning_log": "string — hidden CoT reasoning (SAR telemetry, never shown)",
  "routing_tag": "EVAL_CORRECT | EVAL_INCORRECT | EVAL_PARTIAL",
  "confusion_score": "float 0.0–1.0 (feeds Cognitive Dossier affective_state)",
  "deployed_tool": "tool_1_analogical | tool_2_first_principles | tool_3_boundary | tool_4_protege | tool_5_devils_advocate",
  "user_facing_response": "string — the ONLY field sent to the frontend"
}
```

### Three Siloed Telemetry Stores

> [!CAUTION]
> **Zero cross-contamination.** Teaching optimization, stress testing, and institutional memory — each physically isolated. (Consultant Ruling: Separate DB collections, not tagged in same collection.)

**Store 1: SAR Telemetry (Agent 2 — Teaching Loop)**
```
sar_interactions/{interaction_id}
├── student_id, lesson_id, perspective
├── state_pre_turn_confusion_score: float
├── action_strategy_deployed: "tool_1_analogical" | ...
├── turns_to_mastery: int
├── reward_status: "pending" | "scored" | "timeout"
├── reward_score: float | null
├── reward_reason: "quiz_pass" | "quiz_fail" | "quiz_timeout"
└── scored_at: timestamp | null
```

**Store 2: Egor Telemetry (DPE — Checkride Readiness) [SILOED]**
```
egor_checkride_telemetry/{evaluation_id}
├── student_id, lesson_id
├── tool_deployed: "induced_frustration" | "weaponized_doubt" | "task_saturation" | "deep_hole"
├── knowledge_boundary_acknowledged: boolean
├── emotional_compartmentalization_score: float
├── conviction_score, prioritization_score: float
├── response_latency_ms: int
└── checkride_readiness_delta: float
```

**Store 3: Golden Transcripts (Firestore Vector Search)**
```
golden_transcripts/{transcript_id}
├── lesson_id, perspective, deployed_tool
├── transcript_text, transcript_embedding: vector(768)
├── confusion_delta (pre → post), turns_to_mastery: 1
├── sentiment_score, reward_score
├── flagged_by: "admin_agent", usage_count: int
└── created_at: timestamp
```

**Store 4: Lesson-Level Institutional Memory (FR35 — Mid-Level Evolution Loop)**

> [!IMPORTANT]
> **Token Protection Guardrail:** The raw `session_feedback_log` subcollection is WRITE-ONLY from the Admin Agent's perspective. It is NEVER read directly by any teaching agent. Only the `top_3_global_traps` field (written by the Nightly Overseer) is injected into Agent 1. This separation prevents the lesson record from growing unbounded and cratering prompt costs at scale.

```
lessons/{lesson_id}
├── acs_code: "PA.I.C.K2"
├── top_3_global_traps: [           ← READ BY AGENT 1 only (max 3 items, updated daily by Nightly Overseer)
│   "Students consistently apply Magnetic North instead of True North.",
│   "Students assume high temperature means high air density."
│ ]
└── session_feedback_log/           ← SUBCOLLECTION (Append-only. WRITE by Admin Agent only. NEVER injected raw.)
    ├── {log_id}: { "date": "<ISO>", "uid": "<student_uid>", "note": "Stuck on ISA deviation math." }
    └── {log_id}: { "date": "<ISO>", "uid": "<student_uid>", "note": "Failed to grasp pressure altitude." }
```

**Data Flow:**
```
Admin Agent (async) → session_feedback_log/{log_id}    [raw append — happens every session]
Nightly Overseer    → top_3_global_traps               [daily aggregation — LLM distillation of raw log]
Agent 1 (lesson start) ← lessons/{lesson_id}           [reads top_3_global_traps — 1 Firestore read]
Agent 1 → LessonPlan                                   [q1_primary / q2_scaffold pre-empt the 3 traps]
```

### The Evolution Loop

**Micro-Evolution (Per-Student — Epsilon-Greedy):** Once the DB calculates which tool resolves confusion fastest for a specific user, it updates their Dossier. Agent 2 is then deterministically prompted to use that preferred tool **85% of the time** (Exploitation), 15% exploration.

**Macro-Evolution (Global — Curriculum Auto-Healing):** If aggregate data proves 82% of users master Airspace fastest using Tool 4, Roulette is disabled for that node. Furthermore, if a prerequisite triggers high confusion globally, Agent 1 automatically rewrites the lesson to include a "Pre-Bunking" phase.

**The "Golden Transcript" RAG Database:** Admin Agent flags "Miracle Sessions" (Fast Socratic pass + high sentiment). Exact explanation extracted and embedded into Firestore Vector DB. Future agents recall via RAG.

**The "Nightly Overseer" (Human-in-the-Loop for V1):** At 2:00 AM, a batch-processing LLM critiques the worst-performing sessions and drafts a new constraint. A human engineer/CFI clicks [Merge] or [Reject] on the Admin Dashboard. Zero autonomous prompt changes.

**48-Hour SAR TTL:** Pending SAR entries timeout to `reward: null`, `reason: quiz_timeout`. **Critical:** Use `null` (NOT `0.0`) — zero tells the ML model the tool failed; null drops it from weights, preventing "Data Rot."

---

## 9. User Journeys

### Journey 1: The "Panic Study" Session (Alex)

**Persona:** Alex (32), Part 61 Student, Checkride in 60 days.

1. Types: *"Can I legally change the tire on my Cessna 172?"*
2. **Talker (Lane 1):** Instant answer with FAR Part 43 reference.
3. **Verifier (Lane 3):** Turns green: *Verified against 14 CFR Part 43 App A*.
4. **Socratic Pivot:** The Lesson Plan Generator builds a 4-topic plan (Legal, Safety, Application, Risk Management).
5. **Legal Q1:** *"What logbook entry must you make?"* → Guided to signature + certificate number.
6. **Safety Q1:** *"Why must a private pilot know preventive maintenance limits?"* → Q2 skipped.
7. **Application Q1+Q2:** Walk-through scenario + buddy scenario.
8. **Risk Management (V2 — SJT):** *"Your buddy says he'll change the tire. What's the safest decision?"*
9. **Resolution:** 5 questions. Mastery Quiz from pre-authored bank. Dashboard updated.

### Journey 2: The "Gap Filler" (Maria)

**Persona:** Maria (21), Part 141 Student.

1. Dashboard highlights: *"Finish Microbursts to unlock Egor."*
2. **Sully (Voice):** *"Maria, sudden airspeed increase then sharp drop. What's happening?"*
3. Maria: *"Wind shear?"*
4. **Sully (Consequence Engine):** *"You maintained course. The aircraft enters the downdraft. You're descending at 1500 fpm. Now what?"*
5. Maria: *"Go around immediately."*
6. Dashboard updates. *"2 more tasks to unlock Egor."*

### Journey 3: The "Resume State" (Tom)

**Persona:** Tom (47), Weekend Warrior, returns after 2 weeks.

1. Tutor Loop greets with call sign, references last session's stuck point.
2. Quick win quiz question → correct.
3. 15-minute session, feels like progress.

### Journey 4: The Admin/CFI (Captain Miller)

**Persona:** Chief Instructor monitoring student roster.

1. Sees alert: *"David has attempted 'Cross Country Planning' 5 times with <50%."*
2. Views David's Cognitive Dossier — confusion between True vs. Magnetic course.
3. Proactive intervention before wasted flight time.

---

## 10. Functional Requirements

### FR1–FR5: Expert Witness (Text/RAG)

* **FR1:** Student can ask natural language questions about FAA regulations.
  * **FR1-A:** Specialist covers "Rote" phase testing and deep retrieval from Curriculum (DB1).
  * **FR1-B:** All regulatory claims must cite DB2 (Library) via Bridge Key.
  * **FR1-C:** Dynamic Context Injection — agents retrieve context at instantiation, inject into `system_instruction`.
  * **FR1-D:** Agent Context Protocol (ACP) — unified `StudentContext` on session open. (Supersedes FR1-C.)
* **FR2:** "Verifying..." indicator while Swarm (Lane 2) processes.
* **FR3:** Verified citations in collapsible UI block.
* **FR4:** Pin/Save verified Q&A to personal Notebook.
* **FR5: ⚠️ SUPERSEDED BY FR39 (V2.1).** The single "Teach Me" button is retired. Replaced by the 4-Step Lesson Flow (FR39). Sub-requirements remapped:
  * **FR5-A:** Verification Swarm remains active during all teaching loops. *(Unchanged — still active in FR39 Step ③)*
  * **FR5-B:** Lesson Plan Generator — **V2.1 UPDATE:** Agent 1 input is now RKP manifest + 6-Search RAG results (no student data). See FR36.
  * **FR5-C (V2 UPDATE):** 4-Perspective Socratic Flow — Legal, Safety, Application, **Risk Management**. One question per pillar, sequential. *(Unchanged)*
  * **FR5-D:** Session range: **4–6 questions** with server hard cap at 6. *(Unchanged)*
  * **FR5-E:** Application perspective always requires both Q1 AND Q2. *(Unchanged)*
  * **FR5-F:** RAG→Lesson Credit Mapping — **V2.1 UPDATE:** `resolve_lesson_id()` simplified. `lesson_id` is now known from RKP manifest (no semantic guessing).

### FR6–FR10: Voice Interaction (Audio)

* **FR6:** Voice interaction with VAD (Silero VAD, dynamic pause detection).
  * **FR6-A:** Dynamic VAD threshold — ~1.5s after sentence, ~3.0s during thinking.
* **FR7:** Mute toggle.
* **FR8:** Personality differentiation — Sully (Coaching) vs Egor (Examiner).
* **FR9:** Voice latency < 800ms.
* **FR10:** Interrupt/Barge-in support.
  * **FR10-A:** Log `filler_word_count` and `hesitation_duration`.
  * **FR10-B:** Immediate visual acknowledgment during barge-in.
* **FR10-C (V2 NEW):** "Winding the Clock" — 3-5 second VAD lock for pedagogical silence.
* **FR10-D (V2 NEW):** "Captain Sully" wake-word override kills TTS buffer, opens mic.
* **FR10-E (V2 NEW):** Sully's Consequence Engine — Delayed Didactic Correction. Never say "Wrong," organically degrade aircraft state.

### FR11–FR15: Pedagogical Engine (ACS State)

* **FR11:** Track progress per-Lesson (34 micro-units) with dual-layer rollup to ACS.
* **FR12: Proprietary RKP-Grounded Quiz Bank** — Quizzes are served from a pre-authored, proprietary database, **NOT** the legacy FAA knowledge test bank.
  * **FR12-A (Generation — V2.1 UPDATE):** The Quiz Bank is generated offline by the Question Generator Agent using **RKP knowledge fields as grounding source** plus supplementary 6-Search RAG context. Each question traces to specific RKPs and their `acs_elements`. Human CFIs review and approve all drafts before DB ingestion. The ingestion script (`ingest_quiz_banks.py`) is the only code path permitted to write to `quiz_banks/` Firestore collection (Architecture Rule #9 — unchanged).
  * **FR12-B (Structure):** Every lesson must contain exactly **8 questions**: 2 Legal, 2 Safety, 2 Application, 2 Risk Management (SJT). No more, no fewer.
  * **FR12-C (Schema):** Each question record includes an `interaction_failure_rate: int = 0` field. Starts at zero. In V3, the Auto-Healing loop increments this field via SAR telemetry. When the rate exceeds a threshold, the system autonomously flags the question for CFI-reviewed rewrite (see §16 Autonomous Assessment Tuning).
  * **FR12-D:** Unseen-first, oldest-seen-second rotation algorithm (unchanged).
  * **FR12-E:** Explanations shown for missed questions only (unchanged).
  * **FR12-F (SJT Schema):** Risk Management questions use `question_type: "sjt"` with `sjt_partial_credit_index` (index of the acceptable-but-not-optimal option) and `sjt_rationale` (ADM reasoning explanation). See Story 4.17.3 for full schema definition.

> [!IMPORTANT]
> **CFI Review Gate:** The Question Generator Agent produces a draft. No question enters the `quiz_banks/` Firestore collection without Daniel's (CFI) explicit approval. The staging folder (`docs/quiz_bank_staging/`) holds all drafts awaiting review.
* **FR13:** 80% passing score for `rote_level`.
* **FR14:** Zero-Blind-Spot dashboard (Red/Yellow/Purple/Blue/Green-Checkmark).
  * **FR14-A:** Per-Lesson drill-down with lazy-loaded mastery detail.
* **FR15:** Persist "Stuck Points" and prioritize in future sessions.
  * **FR15-A:** Priority: Review (Expired/Failed) > New (Discovery) > Maintenance (Safe Zone).
  * **FR15-B:** `rote_level` expires 14 days; `application` expires 21 days; `mastered` permanent.

### FR16–FR20: Compliance & Identity

* **FR16:** Log every study session: Date, Duration, ACS Codes, Performance Grade.
* **FR17:** Part 141 Compliance Report export (PDF/CSV).
* **FR18:** Email + Google Auth (Firebase).
* **FR19:** School Code linking.
* **FR20:** Concurrent session prevention.
  * **FR20-A:** IP-based rate limiting on unauthenticated endpoints.
  * **FR20-B:** Daily message quota (50 messages/day).

### FR21–FR23: Data Model (Schema Critical Path)

* **FR21:** Dual-Layer Mastery Schema — Layer 1 per `lesson_id` in Firestore, Layer 2 computed ACS rollup.
  * **FR21-A:** Atomic Firestore batch writes for state transitions.
  * **FR21-B:** StudentContext Object — static profile data (`call_sign`, `target_checkride`, `name`, `school_code`) cached at session level.
  * **FR21-C:** Certificate Namespace — `PPL_` prefix on all `lesson_id` values.
* **FR22:** Session Telemetry — `hesitation_duration`, `filler_word_count`.
* **FR23:** Learning Context Cache — per-task verified citations, dossier, corrections, wrong answers.
  * **FR23-A (V2.1 UPDATE — Mastery Lifecycle Cache):** Cache lifecycle is event-driven by mastery transitions. On login → pre-cache top study queue lesson. On flashcard start → verify cache or trigger 6-Search RAG. On "Begin Socratic" → serve cached plan. On lesson completed → cache CLEARED. On retake → generate FRESH plan with updated struggle data. No TTL timers. See V2.1 Addendum §3.4 for full lifecycle.

### FR24: Agent Output Delivery (Talker-Reasoner UI)

* **FR24:** Auto-Opening Drawer for structured output (quiz, table, report card).
  * **FR24-A:** CFI Simulation Pipeline — dual in-chat thinking bubbles (Talker + Thinker).
  * **FR24-B:** Tier Unlock Toasts — Sully (per-lesson on quiz pass), Egor (60% global).
  * **FR24-C:** Apple Standard UI — glassmorphism, border beam animations.
  * **FR24-D:** Animated Agent Avatars — VP9 `.webm` with alpha transparency.

### FR25–FR26: Admin Agent & Grading Authority

* **FR25:** Admin Agent is single evaluation authority for non-quiz interactions. Teaching agents do NOT grade.
  * **FR25-A:** Quiz→Dossier Write with missed questions for organic reinforcement.
* **FR26:** Untracked DPE practice mode — no mastery updates, available anytime.

### FR27–FR34: V2 NEW Requirements

* **FR27 (Strategy Roulette):** Backend middleware intercepts `EVAL_INCORRECT`, rolls Roulette, injects tool directive. Bypasses on `EVAL_PARTIAL`.
* **FR28 (Agent 2 Structured Output):** All Agent 2 responses use Gemini native `response_schema` (5-field JSON). Sequence Trick enforced.
* **FR29 (SAR Telemetry):** Hidden SAR JSON payload logged on every Agent 2 / Sully turn. `sar_interactions/` collection.
* **FR30 (Bipartite Reward):** `score_sar_interactions()` fires on quiz completion. 4-state conflict matrix with locked reward bounds.
* **FR31 (48h SAR TTL):** Cron job — pending SAR → `reward: null`, `reason: quiz_timeout`. NOT `0.0`.
* **FR32 (Two-Tiered Cognitive Dossier):** `GlobalProfileService` (Tier 1) + `ACSKnowledgeLedgerService` (Tier 2). JIT injection with 2 Firestore reads.
* **FR33 (Egor Siloed Telemetry):** Physically separate `egor_checkride_telemetry/` collection. Feeds Checkride Readiness Score, NOT curriculum optimization.
* **FR34 (Pre-Bunking):** On lesson start, check `prerequisite_acs_nodes` for active misconceptions. Inject `[PRE-BUNK DIRECTIVE]` into Agent 1. Seamless UX — no clinical UI.
* **FR35 (Dual-Destination Admin Feedback — The Mid-Level Evolution Loop):** The Admin Agent MUST write its async grading feedback to two distinct destinations:
  * **Destination A (Micro / Student-Specific):** `users/{uid}/acs_knowledge_ledger/{acs_code}/misconception_log` — student's personal JIT-injected record of current struggles (existing FR32). Written per student, read by agents teaching that student on that ACS code.
  * **Destination B (Global / Lesson-Level):** `lessons/{lesson_id}/session_feedback_log/{log_id}` — append-only institutional record of confusion observed across ALL students on that lesson. Each entry: `{ "date": ISO, "uid": str, "note": str }`. **CRITICAL: This raw subcollection is NEVER injected into any agent prompt directly** — token bloat protection.
  * **The Nightly Overseer (Story 8.5)** aggregates `session_feedback_log` across all sessions and writes a concise `top_3_global_traps: [str]` array (max 3 items) back to the parent `lessons/{lesson_id}` document.
  * **Agent 1 (Lesson Planner) reads `top_3_global_traps`** on lesson start (1 additional Firestore read). If the array is non-empty, Agent 1 is directed to explicitly design its `q1_primary` and `q2_scaffold` questions to pre-empt those historical traps. This is the Answer-First Doctrine applied institutionally — not per-student, but per-lesson.
  * **This feature MUST NOT be wired to Agent 2's prompt** — it stops at Agent 1 scaffolding generation only. Protecting token budget on the teaching loop is non-negotiable.

### FR36–FR39: V2.1 NEW Requirements (RKP Pedagogical Spine)

* **FR36 (RKP Manifest — V2.1 NEW):** Each of the 34 active PPL lessons has one `{lesson_id}_rkp.json` manifest authored by the CFI team containing 3–6 Required Knowledge Points.
  * **FR36-A:** RKP manifests are the **single source of truth** for lesson content. All downstream systems (flashcards, Librarian searches, lesson planning, quiz generation, audio) are driven by the RKP manifest.
  * **FR36-B (Graceful Failure):** If a malformed RKP JSON is loaded → student sees *"This lesson is currently undergoing a scheduled curriculum update from our Chief Flight Instructors. Please try another module."* Backend fires P1 webhook. System does NOT fall back to RAG-only mode.
  * **FR36-C (Schema):** Each RKP: `id`, `title`, `why`, `knowledge`, `acs_elements[]`, `far_references[]`, `bridge_keys[]`. See V2.1 Addendum §3.2.
  * **FR36-D (Coverage):** 3–6 RKPs per lesson (target 4). Every ACS element mapped to the lesson must be covered by at least one RKP.

* **FR37 (Flashcard Deck — V2.1 NEW):** Each lesson has an Anki-style flashcard deck rendered in the Drawer panel, derived from the RKP manifest.
  * **FR37-A:** Card Front = RKP `title` + `why`. Card Back = RKP `knowledge` + `far_references`.
  * **FR37-B (Swipe):** Right = "I know this" (removed). Left = "Don't know" (back to stack). Completion = all swiped right.
  * **FR37-C (Gating):** Not enforced. Students can skip. V3 may use swipe-left data to inform Agent 1.
  * **FR37-D (Flashcard Buffer):** Flashcard study provides 2-5 minutes of "free" compute time for the 6-Search RAG to run. Zero-latency architecture.

* **FR38 (Audio Lesson — V2.1 NEW):** Optional 5-10 minute podcast per lesson. Two virtual flight instructors cover all RKPs.
  * **FR38-A:** Supplementary — not required, not gated. If `audio_file` is `null`, player is hidden.
  * **FR38-B:** Production: NotebookLM → MP3 → Firebase Storage (`lesson_audio/{lesson_id}_audio.mp3`). V3: Google Cloud TTS.

* **FR39 (4-Step Lesson Flow — V2.1 NEW, SUPERSEDES FR5):** The 4-step pedagogical progression replaces the single "Teach Me" button.
  * **FR39-A (The Flow):** ① Overview (Chat) → ② Flashcards (Drawer) → ③ Socratic (Chat) → ④ Quiz (Drawer).
  * **FR39-B (State-Based Unlocking):** `not_started` = strict linear (1→2→3→4). `seen` or higher = all unlocked.
  * **FR39-C (Retake):** Every retake generates a FRESH lesson plan using updated struggle data.

---

## 11. Non-Functional Requirements

### Performance

* **NFR1:** Verification latency < 10 seconds. Stream Fast Answer if >10s.
* **NFR2:** Voice response < 2 seconds time-to-first-byte.
* **NFR6:** 99%+ verified accuracy on all regulatory citations.

### Security & Compliance

* **NFR3:** AES-256 at rest, TLS 1.3 in transit.
* **NFR5:** Best effort SLA (business hours support for beta).

### Scalability & Reliability

* **NFR4:** 50+ concurrent active sessions without degradation.
* **NFR7:** WCAG 2.1 AA accessibility compliance.

---

## 12. Domain-Specific Requirements

### Compliance & Regulatory (Aviation EdTech)

* **Mandatory Training Logs:** Study session duration, exact topics (ACS Codes), and quiz performance must be logged for Part 141 compliance.
* **Operational Scope:** Explicitly "Ground School / Oral Prep Only." Must NOT provide flight planning or operational decision support.
* **The Compliance Story:** *"Every curriculum change is reviewed by a human CFI before it goes live. The AI recommends. Humans approve."*

---

## 13. Business KPIs & Competitive Moat

### Three Un-Copyable Assets (Compound Over Time)

1. **CFI-validated prerequisite graph** — years of domain expertise. No textbook contains this cognitive dependency mapping.
2. **SAR telemetry dataset** — every student interaction = training data. Impossible to replicate without equivalent user base.
3. **Emergent dependencies** — relationships no human instructor has ever documented.

### The Flywheel

Every hour a student uses the app → graph becomes more accurate → teaching improves → more students attracted → more data generated → graph becomes even more accurate. **Exponentially harder to compete with over time.**

### Two Products from One Architecture

| Product | Audience | Revenue Model | Data Source |
|---------|----------|--------------|-------------|
| **AviationChat** | B2C student pilots | Subscription ($10-30/mo) | SAR Telemetry + Cognitive Dossier |
| **Checkride Readiness Report** | B2B flight schools / CFIs | Enterprise ($150+/mo per school) | Egor's siloed telemetry + ACS Ledger |

### Multi-Certificate Data Model

Every piece of student data is namespaced with a certificate prefix (`PPL_`, `IR_`, `CPL_`). When they start Instrument training, the Cognitive Dossier carries forward automatically. **We own the full career.**

---

## 14. Engineering Execution — Brownfield Rules

### Data Bankruptcy

Legacy unstructured chat logs **cannot** be converted into SAR telemetry. They lack pedagogical tool tags and quiz-pass reward links. **Archive them. ML weights start at exactly 0 on launch day.**

### Strangler Fig Routing

1. Build new JSON-based Gemini agents alongside legacy text agents
2. Route 10% of internal test traffic → new engine
3. Verify SAR telemetry logging correctness
4. Scale to 100% → "strangle" legacy codebase

### Database Schema Priority Order

> [!WARNING]
> **Do not write LLM prompts until these schemas are active:**
> 1. `global_profile/` schema
> 2. `acs_knowledge_ledger/{acs_code}/` schema
> 3. `sar_interactions/{interaction_id}` schema
> 4. `prerequisite_acs_nodes` array on curriculum key
> 5. THEN write Agent 2 structured output prompts

---

## 15. The 17 Locked Architectural Decisions

| # | Component | Decision |
|---|-----------|----------|
| 1 | Scope | V1 all layers, simplest form. Brownfield reset for open beta. |
| 2 | Structured Output | Gemini native JSON `response_schema`. NO XML parsing. Force `internal_reasoning_log` key first. |
| 3 | Golden Transcripts | Firestore Vector Search. Small curated corpus (50-200/mo). Do NOT index all sessions. |
| 4 | Nightly Overseer | Human-in-the-Loop (V1). Autonomous scripts output Draft Recommendations only. |
| 5 | ADM/Risk Mgmt | Situational Judgment Tests (SJTs) for quizzes. "Chain of Cues" Socratic prompting. |
| 6 | "I Don't Know" Rule | Egor: confident "I'll check the POH" = PASS (`knowledge_boundary_acknowledged: true`). |
| 7 | Egor Telemetry | **Physically separate collection** (consultant ruling). Feeds Checkride Readiness Score, NOT tool optimization. |
| 8 | Pending SAR TTL | 48-hour timeout. `reward: null`, NOT `0.0`. Prevents Data Rot. |
| 9 | Devil's Advocate | Forbidden for Agent 2. Voice-only. If student folds → immediately trigger Tool 2 (First Principles). |
| 10 | Egor's Toolbelt | 4 distinct DPE tools. Completely separate from Agent 2's teaching tools. |
| 11 | Cognitive Dossier | Two-Tiered: Global Profile + ACS Ledger with JIT prompt injection. |
| 12 | Prerequisite Graph | `prerequisite_acs_nodes` array. V1: 34 Traps (one per lesson). V2: Full DAG via LLM. |
| 13 | Admin Dashboard | **Streamlit** (consultant ruling). 4 views: Telemetry Matrix, Overseer Inbox, RAG Vault, Fleet Risk Board. |
| 14 | Lesson Institutional Memory | **Two-document separation** (consultant ruling). Admin Agent appends to raw `session_feedback_log/` subcollection. Nightly Overseer distills to `top_3_global_traps` array (max 3 items). Agent 1 reads ONLY `top_3_global_traps`. Raw subcollection is NEVER injected into any agent prompt. |
| 15 | RKP Manifests (V2.1) | **Deterministic curriculum skeleton.** Each lesson's `{lesson_id}_rkp.json` is the single source of truth. Malformed RKP = hard stop ("Lesson Unavailable" + P1 webhook). No silent RAG-only fallback. |
| 16 | 6-Search RAG Architecture (V2.1) | **Dual-database, 6-search topology.** DB1: 2 searches (RKP Lesson + RM Module, 5 chunks each). DB2: 4 searches (Legal, Safety, Application, RM Bridge Hop — fetch 5, keep top 3 via hybrid re-rank). Total max 22 chunks to Agent 1. |
| 17 | Agent Data Injection Split (V2.1) | **Agent 1 builds the map, Agent 2 drives the car.** Agent 1 (batch) receives RKP + RAG only. Agent 2 (real-time) receives cached plan + student struggle data (Tier 1/2, Pre-Bunk, Global Traps). Clean separation — Agent 1 doesn't need student data. |

For deep-dive rationale on each decision, see the [V2 Master PRD & Architecture Blueprint](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/_01_My/Docs/Specialist/V2%20Master%20PRD%20%26%20Architecture) and the [V2.1 Addendum](file:///C:/Users/dlohn/.gemini/antigravity/brain/5681ffcf-dd74-402a-aa96-aa0e69c0d149/prd_addendum_v2.1.md).

---

## 16. Growth Features & Future Vision

### V3 Architectural Foresight (Constraints for V2)

To prevent V2 tech debt from blocking our V3 Enterprise scale goals, all V2 development MUST adhere to the following future-proofing constraints. Developers must build defensively to ensure V3 ML engines do not require database teardowns.

1. **The Autonomous Prerequisite DAG (Emergent Dependencies)**
   * **V3 Goal:** The AI dynamically discovers pedagogical links (e.g., failing Crosswind Landings guarantees failure in Aileron Drag) and draws its own DAG edges based on massive student failure datasets.
   * **V2 Constraint:** The `prerequisite_acs_nodes` array must be strictly schema-enforced mapping to relational node IDs, NEVER unstructured text constraints. The V2 graph math must allow a V3 ML algorithm to eventually traverse, append, and prune edges autonomously.
2. **Bayesian Knowledge Tracing (Upward Progression)**
   * **V3 Goal:** If a student crushes an advanced checkride scenario, V3 auto-completes all underlying foundational nodes by running tree-traversal backwards.
   * **V2 Constraint:** The `acs_knowledge_ledger` must remain strictly hierarchical and schema-enforced. Developers absolutely cannot inject loose JSON blobs. The structure must remain pristine for future recursive algorithms.
3. **Checkride Readiness Predictor (Fleet Risk Board)**
   * **V3 Goal:** A high-ticket B2B SaaS dashboard predicting a student's FAA checkride pass rate (0-100) allowing schools to intervene and protect their 141 certifications.
   * **V2 Constraint:** This justifies Arch Decision #7. Egor's adversarial stress-test telemetry (emotional compartmentalization, latency, conviction) MUST remain physically isolated from Sully's standard study logs in V2. Mixing them corrupts the historical regression data required to train the V3 predictor.

### Strategic Onboarding — "Warm Intro / Hard Reality"

* **Sully Intro (Free, Pre-Unlocked):** Meta-lesson teaching new users *how to use AviationChat and the Socratic method*. Builds trust and prevents early churn.
* **Egor Reality Check (2 Free Tokens):** Untracked adversarial mock oral to reveal "Skill Gap." Ultimate B2B demo — hand a device to a Chief Flight Instructor.

### Post-Beta Growth

* **Instructor Dashboards:** Admin views for Flight Schools (student progress rosters).
* **Advanced Psychometrics:** VAD-based confidence scoring.
* **Creator Economy — "Greeting Agents":** YouTube CFI co-branded landing pages.
* **"Ground-School ROI" Calculator:** Hours in AI dialogue × CFI ground rate = dollar savings.
* **"Instructor Bottleneck" Alerts:** Macro-aggregated failure detection across cohorts.

### Multi-Certificate Expansion (IR → CPL → ATP)

The architecture is **certificate-agnostic**. Only the content pipeline and ACS mapping are certificate-specific. Each certificate extends customer lifetime from 3-6 months to 2-3 years.

### Mission Control — Admin Dashboard (V2 NEW)

Tech decision: **Streamlit** (consultant ruling). 4 views:
1. **Telemetry Matrix:** Heatmap — "Turns-to-Mastery" per ACS code vs. Pedagogical Tool
2. **Overseer Inbox:** Human-in-the-Loop prompt update approvals
3. **Golden Transcript Vault:** CFI approval queue for Miracle Sessions
4. **Fleet Risk Board:** B2B dashboard ranking students by Checkride Readiness Score

### Autonomous Assessment Tuning (V3 Roadmap)

Once the Macro-Evolution engine (Story 8.7) collects sufficient SAR telemetry, the **Question Generator Agent** is hooked directly into the Auto-Healing loop:

1. **Trigger:** A quiz question's `interaction_failure_rate` (FR12-C) crosses a statistically-significant threshold — e.g., students are consistently passing the Socratic session (`EVAL_CORRECT` ≥ 3 pillars) but failing that specific question at a rate > 60%.
2. **Detection:** The Admin Agent's lesson-level feedback (`FR35` — `session_feedback_log/`) surfaces the pattern to the Nightly Overseer.
3. **Generation:** The Question Generator Agent automatically re-runs the Swarm RAG fetch for that lesson and drafts a replacement question.
4. **Review:** The new draft is pushed to the CFI approval queue in Mission Control (Overseer Inbox). No question is auto-ingested — human approval is always required.
5. **Ingestion:** On CFI approval, the ingestion script replaces the old question, resets `interaction_failure_rate` to 0.

> [!NOTE]
> **The human is always in the loop.** This is not autonomous replacement — it is autonomous *drafting*. The CFI is the final authority on what students learn.

---

## Source Document Registry

| Document | Location | Status |
|----------|---------|--------|
| V1 PRD (archived) | `planning-artifacts/prd-v1.md` | Archived — reference only |
| Meta-Learning Addendum | `planning-artifacts/prd_addendum_meta-learning.md` | Merged into this document |
| V2 Engineering Addendum | `planning-artifacts/prd_addendum_pedagogical-engine-v2.md` | Merged into this document |
| V2 Master PRD (Mentor) | `_01_My/Docs/Specialist/V2 Master PRD & Architecture` | Strategic source of truth |
| **V2.1 RKP Addendum** | `brain/prd_addendum_v2.1.md` | **Merged into this document (V2.1 CC)** |
| Delta Analysis | `planning-artifacts/v1-to-v2-delta-analysis.md` | Active change tracker |
| UX Design Spec | `planning-artifacts/ux-design-specification.md` | Pending V2.1 update |
| Architecture Doc | `planning-artifacts/architecture/` | Pending V2.1 update |
| Brain Storm (Final) | `brain/brain_storm.md` | Closed — all 17 decisions final |
| ACS Coverage Gap Analysis | `brain/acs_coverage_gap_analysis.md` | Consumed by V2.1 addendum |

---

*AviationChat PRD V2.1 — Correct Course 2026-04-03*  
*Supersedes V2.0. All new work references this document.*
