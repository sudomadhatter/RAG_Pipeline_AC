# 🛩️ The Specialist Agent — Complete Product Requirements Document

> **Owner:** Daniel Lohn | **Version:** V2.7 | **Status:** Living Document
>
> This is the master reference for the Specialist Agent — AviationChat's primary text-based learning engine. It synthesizes the Talker, 6-Search Librarian, Socratic Teacher, Quiz Tutor, Quiz Loop, Cognitive Load Monitoring, and Mastery Progression systems into a single unified PRD.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [The Three-Lane Expert Witness Architecture](#2-the-three-lane-expert-witness-architecture)
3. [The Talker Agent (Sub-Agent 1)](#3-the-talker-agent)
4. [The 6-Search Librarian (Sub-Agent 2)](#4-the-6-search-librarian)
5. [The Reasoner (Sub-Agent 3)](#5-the-reasoner)
6. [Cognitive Load Theory Foundation](#6-cognitive-load-theory-foundation)
7. [The Socratic Teacher Pipeline](#7-the-socratic-teacher-pipeline)
8. [Core Pedagogical Features](#8-core-pedagogical-features)
9. [The Quiz System & 4-Strike Failsafe](#9-the-quiz-system--4-strike-failsafe)
10. [The Socratic Quiz Tutor](#10-the-socratic-quiz-tutor)
11. [Mastery Progression & Learning Decay](#11-mastery-progression--learning-decay)
12. [Dashboard Rollup & Igor Unlock](#12-dashboard-rollup--igor-unlock)
13. [Prerequisite DAG & Pre-Bunking](#13-prerequisite-dag--pre-bunking)

---

## 1. System Overview

The Specialist Agent is the central orchestrator for all text-based student interactions. It is **not** a single LLM — it is a multi-agent system coordinating 6+ sub-agents and services through a stateless webhook pattern.

```mermaid
graph TD
    Student(["Student Message"]) --> Orchestrator["SpecialistOrchestrator<br/>(Python — owns ALL state)"]

    subgraph SubAgents["Sub-Agent Fleet"]
        Talker["Talker<br/>(Fast Acknowledger)"]
        Librarian["6-Search<br/>Librarian"]
        Reasoner["Reasoner<br/>(Fact-Checker)"]
        Teacher["Socratic Teacher<br/>(Agent 1 + Agent 2)"]
        QuizTutor["Quiz Tutor<br/>(Post-Quiz Remediation)"]
        Chat["ChatAgent<br/>(Conversational Router)"]
    end

    subgraph Services["Backend Services"]
        LCC["Learning Context Cache"]
        Roulette["Strategy Roulette"]
        QuizSvc["Quiz Service"]
        MasterySvc["Mastery Service"]
        Router["Semantic Router<br/>(Phase 0)"]
    end

    Orchestrator --> SubAgents
    Orchestrator --> Services
```

**Key Invariant:** The Python Orchestrator owns ALL state. Every sub-agent is stateless — they receive context, produce structured output, and exit. The Orchestrator decides what happens next.

---

## 2. The Three-Lane Expert Witness Architecture

When a student asks a technical aviation question, the Specialist fires three parallel lanes:

```mermaid
graph LR
    Q(["Student Question"]) --> Phase0["Phase 0: Semantic Router<br/>(Maps query → lesson_id)"]

    Phase0 --> Lane1["Lane 1: Talker<br/>Streams fast answer<br/>(< 500ms)"]
    Phase0 --> Lane2["Lane 2: Librarian<br/>Builds evidence dossier<br/>(2-4 sec)"]

    Lane1 --> Stream(["Student sees answer<br/>immediately"])
    Lane2 --> Lane3["Lane 3: Reasoner<br/>Fact-checks Lane 1<br/>against Lane 2 dossier"]
    Lane3 --> Verify(["Verification badge<br/>appears on answer"])
```

| Lane | Agent | Model | Purpose | Latency |
|------|-------|-------|---------|---------|
| 1 | Talker | Flash Lite | Stream a fast, curriculum-grounded answer | < 500ms |
| 2 | Librarian | Vertex AI Search | Build a multi-source evidence dossier | 2-4s |
| 3 | Reasoner | Pro | Fact-check Lane 1 against Lane 2 evidence | 1-2s |

> [!IMPORTANT]
> **Phase 0 (Semantic Router)** runs in parallel with Lane 1. It maps the student's free-text question to a specific `lesson_id` in the curriculum. This determines whether the question is on-syllabus or off-syllabus, which controls how many RAG lanes fire.

---

## 3. The Talker Agent

The Talker is the student's first point of contact. It handles 4 distinct sub-flows depending on the student's intent:

```mermaid
graph TD
    Msg(["Student Message"]) --> Classify{"ChatAgent<br/>Intent Classifier"}

    Classify -- "Aviation Question" --> RAG["RAG Flow<br/>Talker + Librarian + Reasoner"]
    Classify -- "Start Lesson" --> Lesson["Lesson Flow<br/>Load curriculum, emit lesson_card"]
    Classify -- "Platform Question" --> Help["Help Flow<br/>Answer from mission knowledge"]
    Classify -- "Off-Topic During Lesson" --> Redirect["Socratic Redirect<br/>Polite redirect back to lesson"]
```

### Sub-Flow Summary

| Flow | Trigger | Agents Involved | RAG? |
|------|---------|----------------|------|
| **RAG Flow** | Student asks aviation question | Talker → Librarian → Reasoner | ✅ Full 6-Search |
| **Lesson Flow** | Student says "I'm ready to study" | ChatAgent → Lesson Card UI | ❌ |
| **Help Flow** | Student asks "How does this work?" | ChatAgent (internal knowledge) | ❌ |
| **Socratic Redirect** | Student goes off-topic mid-lesson | Socratic Teacher intercepts | ❌ |

---

## 4. The 6-Search Librarian

The Librarian uses a **Dual-DB Topology** executing up to 6 parallel search lanes to build an evidence dossier.

```mermaid
graph TD
    Orchestrator["Orchestrator"] --> LibrarianEngine["6-Search Librarian<br/>perform_investigation()"]

    subgraph DB1["DB1: Curriculum (Deterministic)"]
        FetchK["Lane 1: K/S Elements"]
        FetchR["Lane 2: RM Elements"]
    end

    subgraph DB2["DB2: Source Library (Semantic)"]
        Legal["Lane 3: Legal (FARs)"]
        Safety["Lane 4: Safety (Hazards)"]
        App["Lane 5: Application (Practical)"]
        Bridge["Lane 6: Bridge Hop (Cross-discipline)"]
    end

    LibrarianEngine --> FetchK & FetchR
    LibrarianEngine --> Legal & Safety & App & Bridge

    FetchK & FetchR --> Combine["Combine Results"]
    Legal & Safety & App & Bridge --> Rerank["Re-rank: Keep Top 3 per lane"]
    Rerank --> Combine
    Combine --> Dossier["InvestigationDossier"]
```

### Operating Modes

| Mode | Lanes | When Used |
|------|-------|-----------|
| **Full Curriculum (6-Lane)** | DB1 + DB2 | Main Socratic Teacher flow |
| **RKP-First Q&A (4-Lane)** | DB2 only | Mid-lesson student questions |
| **Off-Syllabus (6-Search)** | DB2 (Legal, Safety, App) | Random aviation questions |

---

## 5. The Reasoner

The Reasoner (Lane 3) is the fact-checker. It receives the Talker's fast answer and the Librarian's evidence dossier, then:
1. Cross-references claims against source documents
2. Flags hallucinations or inaccuracies
3. Emits a verification badge (`verified`, `corrected`, or `unverified`)
4. Attaches source citations (FAR §, AIM sections, PHAK chapters)

---

## 6. Cognitive Load Theory Foundation

The entire Socratic architecture is built on **John Sweller's Cognitive Load Theory (CLT)**, targeting **Germane Load maximization**.

```mermaid
graph TD
    subgraph CLT["Cognitive Load Theory"]
        Intrinsic["🔵 Intrinsic Load<br/>(Manage)"]
        Extraneous["🔴 Extraneous Load<br/>(Minimize)"]
        Germane["🟢 Germane Load<br/>(MAXIMIZE)"]
    end

    subgraph Implementation["AviationChat Implementation"]
        AtomicP["Atomic Principle"]
        RuleOf4["Rule of 4"]
        Scaffold["Q1→Q2 Scaffold"]
        MercyRule["Mercy Rule"]
        Radioactive["Radioactive Target"]
        DoubleBan["Double-Barrel Ban"]
        Extraction["Extraction Engine"]
        Roulette["Strategy Roulette"]
        AntiAmnesia["Anti-Amnesia Protocol"]
    end

    Intrinsic --> AtomicP & RuleOf4 & Scaffold & MercyRule
    Extraneous --> Radioactive & DoubleBan
    Germane --> Extraction & Roulette & AntiAmnesia

    classDef intrinsic fill:#2563EB,stroke:#1D4ED8,color:#fff
    classDef extraneous fill:#DC2626,stroke:#991B1B,color:#fff
    classDef germane fill:#16A34A,stroke:#15803D,color:#fff

    class Intrinsic,AtomicP,RuleOf4,Scaffold,MercyRule intrinsic
    class Extraneous,Radioactive,DoubleBan extraneous
    class Germane,Extraction,Roulette,AntiAmnesia germane
```

### Real-Time Monitoring: The `confusion_score`

The `confusion_score` (0.0–1.0) is a float output by Agent 2 on every evaluation. It maps to 3 cognitive zones:

```mermaid
graph LR
    subgraph Z1["Zone 1: Under-Loaded (0.0 - 0.3)"]
        style Z1 fill:#064E3B,stroke:#047857,color:#fff
        S1["Confident / Minor Error<br/>Action: Advance or Scaffold"]
    end
    subgraph Z2["Zone 2: Germane Load (0.4 - 0.6)"]
        style Z2 fill:#B45309,stroke:#D97706,color:#fff
        S2["Sweet Spot: Productive Struggle<br/>Action: Strategy Roulette"]
    end
    subgraph Z3["Zone 3: Overload (0.7 - 1.0)"]
        style Z3 fill:#7F1D1D,stroke:#DC2626,color:#fff
        S3["Task Saturation / Panic<br/>Action: Block pressure, Trigger Mercy"]
    end
    Z1 --> Z2 --> Z3
```

**Orchestrator Rules:**
- **Zone 3 blocks Devil's Advocate** — a stressed student needs a Confidence Reset, not pressure
- **Rapid spikes trigger early Mercy** — even before the 4-attempt limit
- **We never write "maximize Germane Load" in prompts** — LLMs misinterpret it as "make questions harder"

---

## 7. The Socratic Teacher Pipeline

The Socratic Teacher is a **two-agent pipeline** communicating via strict Pydantic schemas.

| Agent | Role | Model | Output |
|-------|------|-------|--------|
| **Agent 1** (Lesson Planner) | Decides *what* to teach | Pro | `LessonPlan` with 4 `SocraticNode`s |
| **Agent 2** (Executor) | Decides *how* to respond | Pro | `SocraticExecutorResponse` with `routing_tag` + `confusion_score` |

```mermaid
graph TD
    Student(["Student types an answer"]) --> Executor{"Agent 2: Evaluate<br/>Against Target"}

    Executor -- "EVAL_CORRECT" --> Correct["Praise student"]
    Correct --> CheckNext{"More RKP nodes?"}
    CheckNext -- YES --> Planner["Agent 1: Plan next node"]
    Planner --> Student
    CheckNext -- NO --> TriggerQuiz["Trigger Final Quiz"]

    Executor -- "EVAL_PARTIAL" --> Partial["Acknowledge correct part,<br/>ask probing question"]
    Partial --> Student

    Executor -- "EVAL_INCORRECT" --> AttemptCheck{"Attempt #?"}
    AttemptCheck -- "1" --> Q2["Serve Q2 Scaffold"]
    Q2 --> Student
    AttemptCheck -- "2" --> R1["Strategy Roulette #1"]
    R1 --> Student
    AttemptCheck -- "3" --> R2["Strategy Roulette #2"]
    R2 --> Student
    AttemptCheck -- "≥4" --> Mercy["Dynamic T/F Mercy Lifeline"]
    Mercy --> Student

    Executor -- "EVAL_RESOLVED" --> Reveal["Reveal answer + rationale,<br/>advance to next node"]
    Reveal --> Student
```

### 7.1 Session Resumption & State Persistence

The Socratic Teacher incorporates a highly resilient state hydration mechanism to respect adult learners' time and prevent loss of progress. When a student navigates to a lesson, the frontend calls `GET /api/lessons/{lesson_id}/progress`. This endpoint computes the exact `resumed_step` (1-4) by resolving two systems:
1. **The Volatile Session Document:** (`socratic_sessions/{lesson_id}`) Tracks mid-session progression (`node_index`, `attempt`).
2. **The Durable Plan Cache:** (`lesson_plan_cache/{lesson_id}`) Holds the `socratic_completed_at` timestamp. This survives intentional resets (e.g., clicking "Retake Socratic") and prevents completed sessions from regressing the UI.

The React frontend uses a `STATE_RANK` merger pattern to guarantee that any incoming `/progress` hydration will NEVER downgrade a step the user has already unlocked locally. This architecture natively supports N-node RKP manifests without hardcoded constraints.

---

## 8. Core Pedagogical Features

Both the Socratic Teacher and the Quiz Tutor share the same feature suite:

### 1. Extraction Engine (Prime Directive)
The AI must **never give the answer**. It forces the student to articulate the correct response themselves. *Saying it* is the learning event.

### 2. Radioactive Target Protocol
The `target_answer` is treated as radioactive — Agent 2 cannot use its core nouns/verbs in hints. This prevents the "Illusion of Competence" where the student parrots without understanding.

### 3. Strategy Roulette
On attempts 2-3, the Orchestrator injects a `roulette_directive` forcing Agent 2 to pivot its teaching angle:

| Strategy | Example |
|----------|---------|
| **Devil's Advocate** | *"The FAA manual says [distractor]. Defend your answer."* |
| **Socratic Analogy** | *"Think of the electrical system like plumbing..."* |
| **Inverted Scenario** | *"If you WANTED to cause this emergency, what would you do?"* |
| **Explain Like I'm 5** | *"How would you explain it to a non-pilot passenger?"* |

### 4. Anti-Amnesia Protocol
The orchestrator maintains a `node_history` transcript (last 6 turns) injected into Agent 2's prompt so it can reference partial progress and avoid repeating rejected hints.

### 5. Dynamic Mercy Rule (T/F Lifeline)
When `attempt >= 4` or `confusion_score > 0.7`:
1. Agent 2 scans `node_history` for the student's **closest** past answer
2. Warm acknowledgment: *"Earlier you mentioned [X] — solid instinct."*
3. Generates a contextual True/False question isolating one fact
4. T/F correct → advance | T/F incorrect → reveal answer and advance

---

## 9. The Quiz System & 4-Strike Failsafe

After the Socratic conversation completes, the system generates a Scenario-Based Judgment Test (SJT) with 5 questions from the quiz bank. The student must score **80%+** to pass.

```mermaid
flowchart TD
    TakeQuiz(["Student Submits Quiz"]) --> Score["QuizService Grades"]
    Score --> Passed{"Score >= 80%?"}

    Passed -- Yes --> Mastery["Mastery → ROTE_LEVEL<br/>🔓 Unlock Sully"]
    Passed -- No --> Inc["Increment quiz_attempts"]

    Inc --> Check{"Attempt #?"}

    Check -- "1 (Fail)" --> Retry1["Show Retry Button"] --> TakeQuiz
    Check -- "2 (Fail)" --> Tutor["→ Quiz Tutor Agent<br/>Reviews missed concepts"]
    Tutor --> TakeQuiz
    Check -- "3 (Fail)" --> Retry2["Show Retry Button"] --> TakeQuiz
    Check -- "4 (Fail)" --> Stop["🛑 4-Strike Hard Stop"]
    Stop --> Defer["Mark Deferred<br/>24hr Cooldown → Study Queue"]
```

### Deferred Lesson Management
When the 4-strike failsafe fires:
- Lesson flagged `deferred = True` with timestamp
- After **24 hours**, the system re-injects the lesson into the `review` bucket of the Study Queue
- The Socratic Tutor gives a compassionate close-out: *"Great effort — your brain needs time to absorb this. We'll circle back."*

---

## 10. The Socratic Quiz Tutor

The Quiz Tutor is the "brother agent" of the Socratic Teacher. It activates on **Fail 2** and **Fail 4** to walk the student through their specific missed questions.

| Property | Socratic Teacher | Quiz Tutor |
|----------|-----------------|------------|
| **Trigger** | Lesson start | Quiz failure |
| **Input** | RKP Manifest + Lesson Plan | Missed quiz questions |
| **Model** | Gemini 3.1 Pro | Gemini 3.1 Flash Lite |
| **Pydantic Schema** | `SocraticExecutorResponse` | Same — shared schema |
| **Features** | Full suite (Roulette, Mercy, etc.) | Full suite (inherited) |
| **`confusion_score`** | ✅ Tracked per turn | ✅ Tracked per turn |

### Context Loading

```mermaid
flowchart LR
    subgraph Sources["Data Sources"]
        LCC[("Learning Context Cache")]
        State[("Session State")]
        Curriculum[("RKP Manifests")]
    end

    LCC --> MissedQ["Missed Question Dict"]
    State --> NodeHist["Node History Transcript"]
    Curriculum --> RKP["RKP Ground Truth"]

    MissedQ & NodeHist & RKP --> Agent2["Quiz Tutor Agent 2<br/>(Flash Lite)"]
```

---

## 11. Mastery Progression & Learning Decay

### The 5-Phase Grading Waterfall

Each micro-lesson progresses through 5 cognitive phases:

```mermaid
graph TD
    subgraph P1["🔴 Phase 1: DISCOVERY"]
        style P1 fill:#1a0000,stroke:#FF0000,color:#fff
        NEW["NEW (0%)"]
    end
    subgraph P2["🟡 Phase 2: EXPOSURE"]
        style P2 fill:#1a1400,stroke:#FF9900,color:#fff
        SEEN["SEEN (0%)"]
    end
    subgraph P3["🟣 Phase 3: RETENTION"]
        style P3 fill:#1a001a,stroke:#AA00FF,color:#fff
        ROTE["ROTE_LEVEL (50%)<br/>🔓 Unlocks Sully"]
    end
    subgraph P4["🔵 Phase 4: APPLICATION"]
        style P4 fill:#00001a,stroke:#00AAFF,color:#fff
        APP["APPLICATION (75%)"]
    end
    subgraph P5["✅ Phase 5: MASTERY"]
        style P5 fill:#0a1a0a,stroke:#24FF00,color:#fff
        MASTERED["MASTERED (100%)<br/>Permanent"]
    end

    NEW -->|"Student asks question"| SEEN
    SEEN -->|"Quiz pass (80%+)"| ROTE
    ROTE -->|"Sully voice PASS"| APP
    APP -->|"Igor checkride PASS"| MASTERED
```

### Gate Responsibilities

| Gate | Who Teaches | Who Grades |
|------|-------------|------------|
| `new` → `seen` | Specialist (Talker) | *None — exposure only* |
| `seen` → `rote_level` | Socratic Teacher | Quiz Engine (auto-graded) |
| `rote_level` → `application` | Sully (CFI Voice) | **Admin Agent** (transcript) |
| `application` → `mastered` | Igor (DPE Voice) | **Admin Agent** (transcript) |

> [!IMPORTANT]
> **Teaching agents NEVER grade.** The Admin Agent is the sole grading authority for all voice sessions. This prevents personality bias from affecting mastery transitions.

### Learning Decay (The Vault Keeper)

```mermaid
graph LR
    R["🟣 ROTE_LEVEL<br/>Timer: 14 Days"] -.->|"Expires"| S["🟡 SEEN"]
    A["🔵 APPLICATION<br/>Timer: 21 Days"] -.->|"Expires"| R2["🟣 ROTE_LEVEL"]
    M["✅ MASTERED"] -->|"∞ Permanent"| M
```

- **14-Day Cliff** (`rote_level` → `seen`): Lose Sully access, must re-pass quiz
- **21-Day Cliff** (`application` → `rote_level`): Drop back, must redo Sully session
- **Permanent**: Once mastered via Igor, never decays

### Study Queue Priority

| Priority | Bucket | Description |
|----------|--------|-------------|
| 1st | 🔴 **Review** | Decayed/failed lessons (plug leaks first) |
| 2nd | 🟡 **New** | Untouched lessons |
| 3rd | 🟢 **Maintenance** | Safe-zone lessons with active timers |

---

## 12. Dashboard Rollup & Igor Unlock

```mermaid
graph TB
    subgraph Layer1["Layer 1: Per-Lesson Firestore State"]
        L1["Lesson 01: rote (50%)"]
        L2["Lesson 02: seen (0%)"]
        L3["Lesson 03: mastered (100%)"]
    end
    subgraph Layer2["Layer 2: Curriculum Key Mapping"]
        MAP["curriculum_key.json<br/>Maps lesson_id → ACS codes"]
    end
    subgraph Layer3["Layer 3: Dashboard"]
        Score["Weighted Average: 50%"]
        Igor["Igor Unlock: 60%"]
    end
    L1 & L2 & L3 --> MAP --> Score --> Igor
```

### Weight Table

| State | Weight | Color |
|-------|--------|-------|
| `new` | 0% | 🔴 Red |
| `seen` | 0% | 🟡 Yellow |
| `rote_level` | 50% | 🟣 Purple |
| `application` | 75% | 🔵 Blue |
| `mastered` | 100% | ✅ Green |

**Igor unlocks at 60% overall** — most lessons need at least `rote_level` (50%) to cross the threshold.

---

## 13. Prerequisite DAG & Pre-Bunking

The curriculum is not a flat list — concepts build on each other. Every lesson in `curriculum_key.json` declares a `prerequisite_acs_nodes` array forming a Directed Acyclic Graph (DAG).

### ✅ What's Built (V2): The Data Layer

```mermaid
graph TD
    classDef ready fill:#16A34A,stroke:#15803D,color:#fff

    A01["Privileges<br/>prereqs: none"]:::ready
    A02["Medical Certs<br/>prereqs: PA.I.A.K1"]:::ready
    B01["ARROW Docs<br/>prereqs: PA.I.A.K1"]:::ready
    B02["AVIATES<br/>prereqs: PA.I.B.K1"]:::ready
    E01["Airspace A,B,C<br/>prereqs: PA.I.A.K1"]:::ready
    E03["VFR Minimums<br/>prereqs: PA.I.E.K1"]:::ready

    A01 --> A02
    A01 --> B01
    B01 --> B02
    A01 --> E01
    E01 --> E03
```

- ✅ All 33+ Area I lessons have `prerequisite_acs_nodes` authored
- ✅ The Study Queue implicitly presents lessons in dependency order

### 🔶 V3 Vision: Active Pre-Bunking

When a lesson starts, the system will cross-reference `prerequisite_acs_nodes` with the student's ACS Knowledge Ledger. If a misconception exists on a prerequisite, Agent 1 generates a **5-Node Plan** with a Pre-Bunk clearing node at `node_index = -1`.

The student experience is completely conversational — no clinical alerts:

> **Specialist:** *"Before we dive into cloud clearances, remind me — what are the dimensions of Class C airspace?"*

If correct, proceed normally. If wrong, Strategy Roulette clears the misconception before the main lesson begins.

| V3 Dependency | Status |
|--------------|--------|
| `prerequisite_acs_nodes` data | ✅ Complete |
| ACS Knowledge Ledger | ✅ Built |
| Pre-Bunk Directive injection | ❌ Not built |
| `node_index = -1` orchestrator routing | ❌ Not built |
| SAR telemetry for pre-bunk effectiveness | ❌ Not built |
