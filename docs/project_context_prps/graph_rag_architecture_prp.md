# AviationChat Graph RAG Architecture — Product Requirements Package

**Version:** 1.0
**Date:** 2026-05-27
**Author:** Steve Wozniak (Architecture)
**Status:** 📋 Draft for Review

---

## 1. Executive Summary

The AviationChat Graph RAG is a **self-improving prerequisite knowledge graph** that connects ACS concepts through empirically discovered pedagogical relationships. Unlike traditional Graph RAG (which uses Neo4j/vector stores for retrieval), our graph is a **curriculum intelligence layer** — it doesn't retrieve documents, it **routes students through corrective interventions** before they hit known knowledge gaps.

The graph has three growth channels:
1. **Hand-Curated Edges** — CFI-authored prerequisite relationships in `curriculum_key.json`
2. **Auto-Discovered Edges** — Statistical correlations from cross-student failure data
3. **Golden Transcripts** — Proven teaching strategies promoted to permanent intervention nodes

All automated growth is gated by **human-in-the-loop review** before affecting the live curriculum.

---

## 2. System Overview

```mermaid
flowchart TD
    subgraph DataCollection ["Data Collection Layer"]
        SAR["SAR Interactions\nper-turn telemetry"]
        QUIZ["Quiz Results\npass/fail per ACS"]
        MISC["Misconception Log\nper-student per-ACS"]
        AFFIN["Tool Affinity Weights\n16 weights per student per ACS"]
    end

    subgraph Graph ["The Knowledge Graph"]
        HAND["Hand-Curated Edges\ncurriculum_key.json\n33/34 lessons populated"]
        AUTO["Auto-Discovered Edges\ndiscovered_edges.json\nRR > 3.0, N >= 10"]
        GOLDEN["Golden Transcripts\nProven tool+ACS pairings\nN >= 10 flawless"]
        TRAPS["Curriculum Traps\nACS codes where nothing works\nall tools below 0.15"]
        GLOBALS["Global Tool Defaults\nInstitutional weight averages\ncold-start seeding"]
    end

    subgraph Batch ["Nightly Overseer - 4AM UTC"]
        OVERSEER["NightlyOverseerService\nrun_nightly method"]
    end

    subgraph Runtime ["Runtime Consumption"]
        PREBUNK["PrebunkService\ncheck_prebunk at lesson start"]
        ROULETTE["Strategy Roulette\nepsilon-greedy tool selection"]
        PLANNER["Lesson Planner - Agent 1\ntop_3_global_traps injection"]
        SEED["Cold-Start Seeder\nnew student gets global defaults"]
    end

    subgraph HumanReview ["Human-in-the-Loop Gates"]
        CFI["CFI / Admin Review\nApprove or Reject"]
    end

    SAR --> OVERSEER
    QUIZ --> OVERSEER
    MISC --> OVERSEER
    AFFIN --> OVERSEER

    OVERSEER --> AUTO
    OVERSEER --> GOLDEN
    OVERSEER --> TRAPS
    OVERSEER --> GLOBALS

    GOLDEN --> CFI
    CFI -- "Approved" --> GOLDEN
    CFI -- "Rejected" --> GOLDEN

    HAND --> PREBUNK
    AUTO --> PREBUNK
    GLOBALS --> SEED
    TRAPS --> PLANNER
    AFFIN --> ROULETTE
```

---

## 3. The Graph Topology

### 3.1 Nodes (ACS Concepts)

Every node in the graph is an **ACS Knowledge Point** — one of the ~100 knowledge elements tracked across the 34 PPL lessons.

| Field | Source | Example |
|---|---|---|
| `acs_code` | `curriculum_key.json` | `PA.I.A.K1` |
| `lesson_id` | `curriculum_key.json` | `PPL_PA_I_A_01` |
| `knowledge_type` | **NEW — Universal Taxonomy** | `RECALL_FACTUAL` |
| `mastery_status` | Per-student ledger | `seen`, `rote_level`, etc. |
| `tool_affinity_weights` | Per-student, 16 tools | `{ANALOGICAL_BRIDGING: 0.12, ...}` |
| `misconception_log` | Per-student, rolling 10 | Recent knowledge gaps |
| `scored_interaction_count` | Per-student | Drives epsilon decay |

### 3.2 Edge Types

```mermaid
flowchart LR
    subgraph EdgeTypes ["Three Edge Types"]
        direction TB
        E1["PREREQUISITE\nHand-curated by CFI\ncurriculum_key.json"]
        E2["DISCOVERED\nStatistical correlation\nRR > 3.0, N >= 10"]
        E3["GOLDEN_INTERVENTION\nProven teaching pattern\nN >= 10 flawless"]
    end

    A["PA.I.A.K1\nAirplane Categories"] -- "PREREQUISITE" --> B["PA.I.C.K1\nAirspace"]
    C["PA.I.B.K2\nCertificates"] -- "DISCOVERED\nRR=4.2, N=23" --> D["PA.I.C.K1\nAirspace"]
    E["BROKEN_MACHINE\ntool"] -- "GOLDEN_INTERVENTION\n14 flawless, CFI-approved" --> F["PA.I.A.K1\nAirplane Categories"]
```

| Edge Type | Source | Trust Level | Growth Channel |
|---|---|---|---|
| `PREREQUISITE` | `prerequisite_acs_nodes` in `curriculum_key.json` | **High** — human authored | Manual (CFI edits JSON) |
| `DISCOVERED` | `DagDiscoveryService` — relative risk analysis | **Medium** — statistical | Nightly batch, cycle-checked |
| `GOLDEN_INTERVENTION` | `NightlyOverseerService` — reward aggregation | **High after approval** | Nightly batch + **CFI review gate** |

### 3.3 Cycle Prevention

```mermaid
flowchart TD
    PROPOSE["Proposed Edge\nA -> B"] --> PK["Pearce-Kelly Engine\ntry_add_edge(A, B)\nincremental topological sort"]
    PK -- "returns True (accepted)" --> ACCEPT["Accept Edge\nWrite to discovered_edges.json"]
    PK -- "returns False (cycle)" --> REJECT["Reject Edge\nset last_cycle_path + log warning"]
```

Every new edge — whether auto-discovered or manually added — passes through the **incremental
Pearce-Kelly** topological sort (`PearceKellyEngine.try_add_edge`, Story 8.18), which keeps the graph
a **Directed Acyclic Graph** at all times. The engine bootstraps from `PREREQ_MAP` +
`discovered_edges.json`, accepts forward edges in O(1), and **returns `False` on a cycle — it never
raises in the hot path** (the un-guarded `_filter_cycles` call site relies on this). At small scale
this is equivalent to the original batch Kahn's sort; at multi-certificate scale (IR/CPL/ATP →
thousands of nodes) the incremental approach is what scales.

---

## 4. Data Collection Layer — What We Capture

### 4.1 SAR Interactions (per-turn)

Written by `_write_sar_telemetry()` in the Specialist orchestrator on every Socratic turn.

| Field | Type | Purpose | Story |
|---|---|---|---|
| `user_id` | string | Student identifier | 8.1 |
| `session_id` | string | Session correlation | 8.1 |
| `lesson_id` | string | Which lesson | 8.1 |
| `acs_element_key` | string | Which ACS concept | 8.1 |
| `deployed_tool` | string | Which teaching tool was used | 8.1 |
| `evaluation` | string | `EVAL_CORRECT`, `EVAL_INCORRECT`, etc. | 8.1 |
| `confusion_score` | float | How confused the student seemed | 8.1 |
| `turns_to_resolution` | int | How many turns to resolve | 8.1 |
| `reward_score` | float | Bipartite reward (-1.0 to +1.5) | 8.1 |
| `reward_status` | string | `pending` / `scored` | 8.1 |
| `explore_vs_exploit` | string | `explore_20` / `exploit_80` / `exploit_90` | 8.2 |
| `is_quiz_tutor_remediation` | bool | Was this a retry teaching session | 8.1 |
| `pre_bunk_active` | bool | Auto-derived from `node_index == -1` | 8.3 |
| `cognitive_zone` | string | `zone_1` / `zone_2` / `zone_3` | 4.32 |
| `wall_clock_response_ms` | int | Student response latency | 8.1 |
| `created_at` | datetime | SAR creation timestamp | 8.1 |

**Firestore path:** `users/{uid}/sar_interactions/{interaction_id}`

### 4.2 Bipartite Reward Matrix

The reward connects teaching effectiveness to quiz outcomes:

```mermaid
flowchart TD
    subgraph Matrix ["4-State Reward Matrix"]
        CC["Socratic Correct + Quiz Pass\n= +1.0 Clear Success"]
        CI["Socratic Correct + Quiz Fail\n= -0.3 Illusion of Competence"]
        IC["Socratic Incorrect + Quiz Pass\n= +0.4 Socratic Recovery"]
        II["Socratic Incorrect + Quiz Fail\n= -1.0 Complete Miss"]
    end

    subgraph Modifiers ["3 Modifiers"]
        M1["Quiz Tutor Remediation\nx1.5, capped at 1.5"]
        M2["5-Day Time Decay\nDay 1: x1.0 ... Day 5: x0.2\nDay 6+: excluded"]
        M3["Velocity Constraint\nN < 5: delta capped at 0.02\nN >= 5: full velocity"]
    end

    Matrix --> Modifiers
    Modifiers --> FINAL["Final reward_score\nWritten to SAR doc"]
```

### 4.3 Tool Affinity Weights (per-student, per-ACS)

16 normalized weights on `ACSKnowledgeNode.tool_affinity_weights`:

| Tool Pool | Tools | Count |
|---|---|---|
| **Text** (Specialist Socratic) | `ANALOGICAL_BRIDGING`, `FIRST_PRINCIPLES`, `BOUNDARY_TESTING`, `CONTRASTING_CASES`, `REVERSE_CHAINING`, `BROKEN_MACHINE`, `MISSING_LINK`, `TRIAGE` | 8 |
| **Voice** (Sully CFI) | `CONSEQUENCE_ENGINE`, `DEVILS_ADVOCATE`, `PROTEGE_EFFECT`, `COLLOQUIAL_VALIDATION`, `SCENARIO_EXTENSION`, `KNOWLEDGE_ANCHORING`, `PERSPECTIVE_SHIFT`, `CONFIDENCE_CALIBRATION` | 8 |

**Invariants:** Sum = 1.0 | Floor = 0.01 (no permanent tool death) | Renormalized after every update

---

## 5. Nightly Overseer — The Macro-Evolution Engine

```mermaid
flowchart TD
    TRIGGER["Cloud Scheduler\n4:00 AM UTC daily\nOR manual POST /api/admin/run-overseer"] --> OVERSEER["NightlyOverseerService.run_nightly"]

    OVERSEER --> PHASE1["Phase 1: Global Weight Aggregation\nAverage tool_affinity_weights\nacross students with N >= 5"]
    OVERSEER --> PHASE2["Phase 2: Curriculum Trap Detection\nFlag ACS codes where >60%\nof students have ALL tools < 0.15"]
    OVERSEER --> PHASE3["Phase 3: DAG Edge Discovery\nDagDiscoveryService.discover_edges\nRR > 3.0, N >= 10, cycle-free"]
    OVERSEER --> PHASE4["Phase 4: Golden Transcript Discovery\nTool+ACS pairings with\n>= 10 flawless outcomes"]
    OVERSEER --> PHASE5["Phase 5: Fleet Risk Board\nPer-student risk signals\nfor Mission Control"]

    PHASE1 --> WRITE1["Write: lessons/lesson_id\n.global_tool_defaults"]
    PHASE2 --> WRITE2["Write: lessons/lesson_id\n.curriculum_traps\n.top_3_global_traps"]
    PHASE3 --> WRITE3["Write: discovered_edges.json"]
    PHASE4 --> WRITE4["Write: dashboard_metadata/\ngolden_candidates/auto_id\nreview_status = pending"]
    PHASE5 --> WRITE5["Write: dashboard_metadata/\nstudent_risk/uid"]

    WRITE1 --> CONSUMERS1["Cold-Start Seeder\nnew students get\ninstitutional defaults"]
    WRITE2 --> CONSUMERS2["Lesson Planner - Agent 1\nreads top_3_global_traps"]
    WRITE3 --> CONSUMERS3["PrebunkService\nreads discovered edges\nat every lesson start"]
    WRITE4 --> GATE["CFI Review Gate\nPATCH approved/rejected"]
    WRITE5 --> CONSUMERS5["Future: Mission Control\nDashboard UI"]

    OVERSEER --> REPORT["OverseerReport\ndashboard_metadata/\noverseer_reports/date"]
```

---

## 6. Runtime Consumption — How the Graph Serves Students

### 6.1 Pre-Bunking Pipeline (Lesson Start)

```mermaid
flowchart TD
    START["Student clicks Begin Socratic\nfor lesson PPL_PA_I_C_01"] --> READ1["Read curriculum_key.json\nprerequisite_acs_nodes:\nPA.I.A.K1, PA.I.B.K2"]

    READ1 --> READ2["Read discovered_edges.json\nauto-discovered prereqs\nfor PPL_PA_I_C_01"]

    READ2 --> MERGE["Merge all prerequisite\nACS codes"]

    MERGE --> SCAN["Batch-read student's\nACSKnowledgeLedger\nfor each prerequisite"]

    SCAN --> CHECK{"Any active\nmisconceptions?"}

    CHECK -- "No" --> NORMAL["Start at node_index=0\nNormal Socratic flow"]

    CHECK -- "Yes" --> DIRECTIVE["Build PRE-BUNK DIRECTIVE\nHighest-priority misconception\n+ best tool for this student"]

    DIRECTIVE --> PREBUNK["Inject prebunk_node\nat node_index=-1\nBefore Core Topics"]

    PREBUNK --> SERVE["Orchestrator serves\nprebunk node first\nConversational framing:\nBefore we begin..."]

    SERVE --> EVAL{"Student resolves\nprebunk?"}

    EVAL -- "EVAL_CORRECT" --> ADVANCE["Advance to node_index=0\nNormal lesson begins"]
    EVAL -- "EVAL_INCORRECT" --> ROULETTE["Strategy Roulette fires\nSame as any node"]
```

### 6.2 Cold-Start Seeding (New Student)

```mermaid
flowchart TD
    NEW["New student opens lesson\nfor ACS code PA.I.A.K1"] --> LOOKUP["ACSKnowledgeLedgerService\nget_acs_node"]

    LOOKUP --> EXISTS{"ACS node exists\nin Firestore?"}

    EXISTS -- "Yes" --> USE["Use existing weights\nStudent has history"]

    EXISTS -- "No" --> GLOBAL["Check lessons/PA.I.A.K1\n.global_tool_defaults"]

    GLOBAL --> HAS{"Global defaults\nexist?"}

    HAS -- "Yes" --> SEED["Seed tool_affinity_weights\nwith institutional averages\nStudent benefits from\ncollective intelligence"]

    HAS -- "No" --> UNIFORM["Use uniform defaults\n0.0625 per tool\nFirst student or no data yet"]

    SEED --> ROULETTE["Strategy Roulette\nimmediately biased toward\nproven effective tools"]

    UNIFORM --> ROULETTE
```

### 6.3 Epsilon-Greedy Tool Selection

```mermaid
flowchart TD
    TRIGGER["EVAL_INCORRECT received\nStrategy Roulette fires"] --> READ["Read ACSKnowledgeNode\ntool_affinity_weights\nscored_interaction_count"]

    READ --> EPSILON{"N >= 50?"}

    EPSILON -- "N < 50" --> E20["epsilon = 0.20\n80/20 exploit/explore"]
    EPSILON -- "N >= 50" --> E10["epsilon = 0.10\n90/10 exploit/explore"]

    E20 --> ROLL{"random < epsilon?"}
    E10 --> ROLL

    ROLL -- "Yes: EXPLORE" --> RANDOM["Random tool\nfrom available pool"]
    ROLL -- "No: EXPLOIT" --> BEST["Highest-weighted tool\nfrom affinity weights"]

    RANDOM --> TAG1["Tag: explore_20 or explore_10"]
    BEST --> TAG2["Tag: exploit_80 or exploit_90"]

    TAG1 --> SAR["Written to SAR\nexplore_vs_exploit field"]
    TAG2 --> SAR
```

---

## 7. Human-in-the-Loop Review Gates

```mermaid
flowchart TD
    subgraph Automated ["Fully Automated - No Human Review"]
        A1["Global Weight Aggregation\nStatistical averages"]
        A2["Curriculum Trap Detection\nFlagging only"]
        A3["Fleet Risk Signals\nData computation"]
        A4["Cold-Start Seeding\nUses approved globals"]
        A5["Pre-Bunking\nUses approved edges"]
        A6["Tool Affinity Updates\nPer-student micro-evolution"]
    end

    subgraph Gated ["Human Review Required"]
        G1["Golden Transcript Candidates\nreview_status: pending\nAdmin PATCH to approve/reject"]
        G2["Hand-Curated Prerequisites\nCFI edits curriculum_key.json\nDirectly committed to repo"]
    end

    subgraph NotYetGated ["Auto-Accepted - Future Gate"]
        N1["Discovered DAG Edges\nCurrently auto-written\nCycle detection only guard\nFuture: admin approval"]
    end
```

### Review Workflow — Golden Transcripts

| Step | Actor | Action |
|---|---|---|
| 1 | **Nightly Overseer** | Discovers tool+ACS pairing with >= 10 flawless outcomes (reward=1.0, turns<=3) |
| 2 | **System** | Writes to `dashboard_metadata/golden_candidates/{id}` with `review_status: "pending"` |
| 3 | **Admin/CFI** | `GET /api/admin/golden-candidates` — reviews pending list |
| 4 | **Admin/CFI** | `PATCH /api/admin/golden-candidates/{id}` — approves or rejects |
| 5 | **System** | Approved candidates become permanent institutional knowledge |

> [!IMPORTANT]
> **No automated curriculum changes fire without human review.** The Overseer produces recommendations. Humans decide.

---

## 8. Universal Knowledge Type Taxonomy

Every node, edge, and SAR record carries a `knowledge_type` field classifying the **cognitive demand** — NOT the subject matter.

| `knowledge_type` | What The Brain Does | Aviation Example | Portable To |
|---|---|---|---|
| `RECALL_FACTUAL` | Retrieve a number, limit, or definition | "Class B visibility minimums?" | Medical licensing, Bar exam |
| `CONCEPTUAL_WHY` | Explain WHY a principle works | "Why does density altitude reduce performance?" | Engineering, Physics |
| `PROCEDURAL` | Execute ordered steps correctly | "Engine failure on takeoff checklist" | Nursing protocols, IT ops |
| `APPLIED_JUDGMENT` | Decide under competing pressures | "Engine out at 500 AGL — what do you do?" | Emergency medicine, Law |
| `REGULATORY` | Know the rule, cite the source | "14 CFR 61.113 limitations" | Legal compliance, Finance |
| `RISK_ASSESSMENT` | Identify what could go wrong | "Hazards in this METAR" | Cybersecurity, Construction |
| `SYSTEMS_INTEGRATION` | Connect how parts interact | "How pitot-static feeds instruments" | Software architecture |
| `HUMAN_FACTORS` | Recognize how humans fail | "Hazardous attitudes, ADM, CRM" | Healthcare, Military |

### Why This Matters (Tier 4 Monetization Unlock)

A student who struggles with `REGULATORY` recall in PPL will struggle with it in medical licensing. The affinity weights can be seeded from cross-domain `knowledge_type` performance — making the **entire Evolution Engine portable across verticals**.

---

## 9. Firestore Data Model

```mermaid
flowchart TD
    subgraph PerStudent ["Per-Student Data"]
        US["users/{uid}"]
        US --> AKL["acs_knowledge_ledger/{acs_code}\ntool_affinity_weights\nmisconception_log\nscored_interaction_count\nmastery_status"]
        US --> SARI["sar_interactions/{interaction_id}\ndeployed_tool, reward_score\nturns_to_resolution\ncognitive_zone, knowledge_type"]
        US --> QR["quiz_results/{quiz_id}\nscore, passed, answers"]
    end

    subgraph PerLesson ["Per-Lesson Data"]
        LS["lessons/{lesson_id}"]
        LS --> GD[".global_tool_defaults\nInstitutional weight averages"]
        LS --> CT[".curriculum_traps\nFlagged dead-end ACS codes"]
        LS --> T3[".top_3_global_traps\nLowest quiz scores globally"]
    end

    subgraph Dashboard ["Dashboard Metadata"]
        DM["dashboard_metadata/"]
        DM --> OR["overseer_reports/{date}\nOverseerReport"]
        DM --> GC["golden_candidates/{auto_id}\ntool, acs_code, flawless_count\nreview_status, reviewed_by"]
        DM --> SR["student_risk/{uid}\nsocratic_avg_time\nquiz_tutor_frequency\nsession_abandonment_count"]
    end

    subgraph Static ["Static Files - Repo"]
        CK["backend/data/curriculum_key.json\nprerequisite_acs_nodes\nHand-curated edges"]
        DE["backend/data/discovered_edges.json\nAuto-discovered edges\nRR, N, confidence"]
    end
```

---

## 10. File Inventory — Current State

| File | Status | Role in Graph RAG |
|---|---|---|
| [curriculum_resolver.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/utils/curriculum_resolver.py) | ✅ Built | Loads `PREREQ_MAP` from `curriculum_key.json` at import time |
| [prebunk_service.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/services/prebunk_service.py) | ✅ Built (8.3) | Runtime pre-bunk check — reads both edge sources |
| [dag_discovery_service.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/services/evolution/dag_discovery_service.py) | ✅ Built (8.3) | Auto edge discovery — RR analysis + Pearce-Kelly incremental cycle detection (8.18; `try_add_edge` returns `False` on cycle, bootstraps from `PREREQ_MAP`) |
| [reward_service.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/services/evolution/reward_service.py) | ✅ Built (8.1) | Bipartite reward scoring — feeds affinity updates |
| [affinity_service.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/services/evolution/affinity_service.py) | ✅ Built (8.2) | Per-student tool weight updates with velocity constraints |
| [cognitive_dossier.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/schemas/cognitive_dossier.py) | ✅ Built | `ACSKnowledgeNode` with 16-tool weights, migration validators |
| [lesson_plan.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/schemas/lesson_plan.py) | ✅ Built | `prebunk_node` field on `LessonPlan` |
| [lesson_planner/agent.py](file:///c:/Sudo_Hatter_Command/Projects/aviationChat-AGY/backend/agents/specialist/sub_agents/lesson_planner/agent.py) | ✅ Built | Reads `top_3_global_traps` at plan generation |
| `backend/services/evolution/nightly_overseer.py` | 🔜 Story 8.4 | Batch aggregation — the macro-evolution brain |
| `backend/schemas/evolution.py` | 🔜 Story 8.4 | `OverseerReport`, `GoldenCandidate`, `StudentRisk` schemas |
| `backend/routers/admin_evolution.py` | 🔜 Story 8.4 | Admin API for manual trigger + Golden Transcript review |

---

## 11. What Story 8.4 Completes

| Capability | Without 8.4 | With 8.4 |
|---|---|---|
| Pre-bunking | ✅ Works with hand-curated edges only | ✅ Works with hand-curated + auto-discovered |
| Edge discovery | Code exists, never called | ✅ Called nightly at 4AM |
| Golden Transcripts | Not tracked | ✅ Discovered, nominated, gated by CFI review |
| Cold-start seeding | Uniform 0.0625 for all new students | ✅ Global institutional defaults |
| Curriculum traps | Unknown | ✅ Flagged and written to `top_3_global_traps` |
| Fleet risk | No data | ✅ Per-student risk signals computed |
| Admin visibility | None | ✅ 4 REST endpoints for oversight |

---

## 12. Future Extensions (Not in Story 8.4)

| Extension | Description | Dependency |
|---|---|---|
| `knowledge_type` taxonomy | Add cognitive demand tags to `SocraticNode`, SAR, edges | Schema migration story |
| **Curriculum Graph Dashboard** | 3D neon "brain" graph of the 34-lesson DAG + macro↔individual toggle + click-to-read panel showing the tools & questions that worked vs. didn't | **Story 8.12** (depends on 8.11) |
| Cross-vertical seeding | Port `knowledge_type` affinities across certificates | Multi-certificate architecture |
| Neo4j / graph DB | Move from JSON edges to a proper graph database | Scale trigger (~10K students) |
| Discovered edge review gate | Admin approval before auto-edges go live | Admin UI story |

> [!IMPORTANT]
> **Known capture gap (2026-06-01) — Story 8.11.** The Golden RAG's core unit, the Pedagogical
> Fingerprint (`tool` + **`tutor_question`** + outcome), is **designed but not captured in code**.
> SAR persists `deployed_tool` and `reward_score` but **not** the question text or the student's
> words; `GoldenCandidate` groups by `(tool, acs)` only. So today the graph can show *which tools*
> worked, but not *the questions that worked*. **Story 8.11 (Golden RAG Pedagogical Fingerprint
> Capture)** fixes the capture + widens the Overseer grouping; **Story 8.12** renders it. See
> `admin_agent_dag_prp.md` §5.2 / §5.5 for the corrected implementation status.

### Epic 8 — Golden RAG Story Map (2026-06-01)

| Story | Scope | Status |
|---|---|---|
| **8.11** | Capture the winning fingerprint (tool + question + student response) on breakthrough turns — *start small* | ready-for-dev |
| **8.12** | Admin Curriculum Graph Dashboard — 3D neon "brain" map, macro↔individual toggle, click-to-read worked/didn't panel | ready-for-dev |
| **8.13** | Durable **"double win"** promotion (turn breakthrough **+** quiz-confirmed +1.0) — TTL holding-pen, loss-count denominators, `breakthrough_rate` gate | backlog |
| **8.14** | **Automated Teaching-Quality Grader** — agent grades winning questions (good Socratic vs. gave-away-answer), records verdicts → which prompts/tools to fix | backlog |
| **8.15** | **Golden RAG retrieval & injection** — reuse CFI-approved proven questions as Socratic bias; `knowledge_type` tagging; voice/text isolation; optional vector store | backlog |
