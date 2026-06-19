# Prerequisite DAG & Pre-Bunking Directive

## The Problem: The "House of Cards" Failure Mode

In aviation training, concepts build sequentially upon each other. A student cannot effectively learn **Airspace Cloud Clearances (Concept B)** if they harbor a fundamental misunderstanding of **Airspace Classes (Concept A)**.

If an AI instructor tries to teach Concept B while the student's foundation is broken, the student will experience cognitive overload, frustration, and failure. We call this the "House of Cards" failure mode.

---

## What We Have Today (V2)

### ✅ The Data Layer — Prerequisite DAG in `curriculum_key.json`

The Directed Acyclic Graph (DAG) of concept dependencies is **fully authored** in the curriculum data. Every lesson in `curriculum_key.json` declares a `prerequisite_acs_nodes` array listing the ACS codes a student must understand before starting.

```mermaid
graph TD
    classDef ready fill:#16A34A,stroke:#15803D,color:#fff
    classDef data fill:#2563EB,stroke:#1D4ED8,color:#fff

    CK["curriculum_key.json<br/>prerequisite_acs_nodes field"]:::data

    subgraph ExampleDAG["Example: Area I Dependencies"]
        A01["PA_I_A_01<br/>Privileges<br/>prereqs: none"]:::ready
        A02["PA_I_A_02<br/>Medical Certs<br/>prereqs: PA.I.A.K1"]:::ready
        B01["PA_I_B_01<br/>ARROW Docs<br/>prereqs: PA.I.A.K1"]:::ready
        B02["PA_I_B_02<br/>AVIATES<br/>prereqs: PA.I.B.K1"]:::ready
        E01["PA_I_E_01<br/>Airspace A,B,C<br/>prereqs: PA.I.A.K1"]:::ready
        E03["PA_I_E_03<br/>VFR Minimums<br/>prereqs: PA.I.E.K1"]:::ready
    end

    A01 --> A02
    A01 --> B01
    B01 --> B02
    A01 --> E01
    E01 --> E03
    CK --> ExampleDAG
```

**Status:** ✅ All 33+ Area I lessons have their `prerequisite_acs_nodes` authored. The DAG is complete and machine-readable.

### ✅ The Study Queue — Implicit Ordering

The Study Queue service already uses lesson ordering from the curriculum to present lessons in dependency order. This means a student will *naturally* encounter prerequisites before dependent topics in the standard learning path.

---

## What's Coming (V3): Active Pre-Bunking

> [!IMPORTANT]
> **V3 Feature — Not Yet Implemented.** The sections below describe the planned runtime pre-bunking system. The data layer (DAG) is ready; the execution layer (checking + clearing) needs to be built.

### The Vision: Pre-Bunking

**Pre-Bunking** is the act of proactively identifying and clearing a foundational misconception *before* teaching a new, dependent concept. This transforms the Socratic pipeline from a reactive system (fixing mistakes as they happen) into a **proactive** pedagogical engine.

### V3 Architectural Flow

```mermaid
graph TD
    classDef data fill:#2d3748,stroke:#4a5568,color:#fff
    classDef process fill:#3182ce,stroke:#2b6cb0,color:#fff
    classDef agent fill:#805ad5,stroke:#6b46c1,color:#fff
    classDef state fill:#38a169,stroke:#2f855a,color:#fff
    classDef v3 fill:#B45309,stroke:#78350F,color:#fff

    A["Student clicks Start Lesson"]:::process

    subgraph Phase1["V3: Background Prep Cache"]
        B["Check curriculum_key.json<br/>prerequisite_acs_nodes"]:::data
        C["Query Student's ACS Ledger<br/>for Active Misconceptions"]:::data
        D{"Misconceptions<br/>Found?"}:::process
        E["Select Highest Priority<br/>Misconception"]:::v3
        F["Generate Pre-Bunk Directive"]:::v3
    end

    B --> C --> D
    D -->|Yes| E --> F
    D -->|No| G("Agent 1 generates<br/>standard 4-Node Plan"):::agent
    F --> H("Agent 1 generates<br/>5-Node Plan with Pre-Bunk"):::agent

    A --> B

    subgraph Phase2["V3: Socratic Session"]
        H --> I["Orchestrator starts at<br/>node_index = -1"]:::v3
        G --> J["Orchestrator starts at<br/>node_index = 0"]:::state

        I --> K["Conversational Pre-Bunk Check"]:::process
        K -.->|EVAL_CORRECT| J
        K -.->|EVAL_INCORRECT| L["Strategy Roulette<br/>clears misconception"]:::process
        L -.-> J

        J --> M["Standard 4 Pillars<br/>Legal, Safety, App, RM"]:::state
    end
```

### V3 Implementation Requirements

#### 1. The Prerequisite Check (Data Layer)
When the background prep task builds the lesson plan, it cross-references `prerequisite_acs_nodes` with the student's **ACS Knowledge Ledger** (Tier 2 dossier). If a severe, unresolved misconception exists on a prerequisite ACS code, it generates a **[PRE-BUNK DIRECTIVE]**.

#### 2. The Clearing Node (Execution Layer)
Agent 1 receives the directive and constructs a **Pre-Bunk Node** (`node_index = -1`). This node is injected at the very beginning of the lesson plan. The Orchestrator processes this first. If the student answers correctly, the lesson proceeds normally. If they struggle, Strategy Roulette engages to resolve the historical misconception.

#### 3. The Student Experience (UX)
The student never sees a clinical alert. The pre-bunk check is **completely conversational**:

> **Specialist:** *"Hey Daniel, before we dive into cloud clearances today, I just want to make sure we're squared away on something from last time. Remind me, what are the dimensions of Class C airspace?"*
>
> **Daniel:** *"Uh, it's a 5nm inner circle and 10nm outer shelf, right?"*
>
> **Specialist:** *"Spot on. Okay, so with that in mind, let's look at cloud clearances..."*

If Daniel gets it wrong, the Specialist tutors him until it clicks. Once resolved, the seamless transition into the primary lesson occurs.

### V3 Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| `prerequisite_acs_nodes` in curriculum_key.json | ✅ Complete | All 33+ lessons authored |
| ACS Knowledge Ledger (Tier 2 dossier) | ✅ Built | Firestore per-student misconception tracking |
| Pre-Bunk Directive injection into Agent 1 | ❌ Not built | Needs prompt engineering + orchestrator logic |
| `node_index = -1` handling in Orchestrator | ❌ Not built | Needs routing logic for the clearing node |
| SAR telemetry for pre-bunk effectiveness | ❌ Not built | Track if pre-bunking reduces downstream failures |
