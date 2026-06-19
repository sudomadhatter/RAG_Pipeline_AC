# 🎓 AviationChat Mastery Pipeline — Grading Progression Waterfall

## The Student Journey (One Micro-Lesson)

This chart shows how a single micro-lesson (e.g., `PA_I_A_01: Privileges & Limitations`) progresses from first contact to permanent mastery.

```mermaid
graph TD
    subgraph DISCOVERY["🔴 PHASE 1: DISCOVERY"]
        style DISCOVERY fill:#1a0000,stroke:#FF0000,color:#fff
        NEW["🔴 NEW<br/>Student hasn't touched this lesson<br/><i>Dashboard: Red blind spot</i>"]
    end

    subgraph EXPOSURE["🟡 PHASE 2: EXPOSURE"]
        style EXPOSURE fill:#1a1400,stroke:#FF9900,color:#fff
        SEEN["🟡 SEEN<br/>Specialist answered a question<br/>tagged to this lesson's ACS elements<br/><i>Dashboard: Yellow — started</i>"]
    end

    subgraph RETENTION["🟣 PHASE 3: RETENTION"]
        style RETENTION fill:#1a001a,stroke:#AA00FF,color:#fff
        ROTE["🟣 ROTE_LEVEL<br/>Passed text quiz (80%+)<br/>🔓 Unlocks Sully for this lesson<br/><i>Decay: 14 days</i>"]
    end

    subgraph APPLICATION["🔵 PHASE 4: APPLICATION"]
        style APPLICATION fill:#00001a,stroke:#00AAFF,color:#fff
        APP["🔵 APPLICATION<br/>Passed Sully voice coaching<br/>Admin Agent grades transcript<br/><i>Decay: 21 days</i>"]
    end

    subgraph MASTERY["✅ PHASE 5: MASTERY"]
        style MASTERY fill:#0a1a0a,stroke:#24FF00,color:#fff
        MASTERED["✅ MASTERED<br/>Passed Igor DPE checkride<br/>Admin Agent grades transcript<br/><i>Permanent — no decay</i>"]
    end

    NEW -->|"Student asks question<br/>Phase 0 classifies → lesson_id"| SEEN
    SEEN -->|"Rote Quiz: 80%+ pass<br/>Atomic Firestore batch write"| ROTE
    ROTE -->|"Sully voice session<br/>Admin Agent grades → PASS"| APP
    APP -->|"Igor DPE checkride<br/>Admin Agent grades → PASS"| MASTERED

    ROTE -.->|"⚠️ 14-day decay<br/>Drops to SEEN"| SEEN
    APP -.->|"⚠️ 21-day decay<br/>Drops to ROTE_LEVEL"| ROTE
```

---

## Who Does What at Each Gate

| Gate | Trigger | Who Teaches | Who Grades | Mastery Write |
|------|---------|-------------|------------|---------------|
| `new` → `seen` | Student asks a question | **Specialist** (Talker) | *None — exposure only* | `mastery_service.transition(lesson_id, "seen")` |
| `seen` → `rote_level` | Student passes quiz (80%+) | **Socratic Teacher** | **Quiz Engine** (auto-graded) | `mastery_service.transition(lesson_id, "rote_level")` |
| `rote_level` → `application` | Student completes Sully voice session | **Sully** (CFI Voice) | **Admin Agent** (transcript) | `mastery_service.transition(lesson_id, "application")` |
| `application` → `mastered` | Student passes Igor checkride | **Igor** (DPE Voice) | **Admin Agent** (transcript) | `mastery_service.transition(lesson_id, "mastered")` |

> [!IMPORTANT]
> **Teaching agents NEVER grade.** Sully teaches, Igor examines — but the Admin Agent is the sole grading authority for all voice sessions. This prevents personality bias from affecting mastery transitions.

---

## Decay Cascade (The Vault Keeper)

```mermaid
graph LR
    subgraph TIMER["⏱️ DECAY TIMERS"]
        R["rote_level<br/>14 days"] -.->|"expired"| S["→ seen"]
        A["application<br/>21 days"] -.->|"expired"| RL["→ rote_level"]
        M["mastered"] -->|"∞ permanent"| M
    end
```

**Study Queue Priority (FR15-A):**
1. 🔴 **Review** — Expired/failed lessons (FIRST)
2. 🟡 **New** — Untouched lessons (SECOND)
3. 🟢 **Maintenance** — Safe zone lessons (LAST)

---

## The Dual-Layer Rollup (Lesson → Dashboard)

```mermaid
graph TB
    subgraph LAYER1["LAYER 1: Firestore per-lesson state"]
        L1["PA_I_A_01: rote_level"]
        L2["PA_I_A_02: seen"]
        L3["PA_I_A_03: new"]
        L4["PA_I_A_04: mastered"]
    end

    subgraph LAYER2["LAYER 2: Curriculum Key mapping"]
        MAP["curriculum_key.json<br/>PA_I_A_01 → PA.I.A.K1, K2, R1<br/>PA_I_A_02 → PA.I.A.K3, K4<br/>PA_I_A_03 → PA.I.A.K5, R2<br/>PA_I_A_04 → PA.I.A.K6, S1"]
    end

    subgraph LAYER3["LAYER 3: Dashboard rollup"]
        TASK["Task PA.I.A: 4 lessons<br/>Weights: 50% + 0% + 0% + 100% = 37.5%"]
        AREA["Area I: 33 lessons<br/>Overall: weighted average"]
        IGOR["Igor Unlock: 60% overall?"]
    end

    L1 & L2 & L3 & L4 --> MAP
    MAP --> TASK --> AREA --> IGOR
```

**Weight Table:**

| State | Dashboard Weight | Dashboard Color |
|-------|-----------------|-----------------|
| `new` | 0% | 🔴 Red |
| `seen` | 0% | 🟡 Yellow |
| `rote_level` | 50% | 🟣 Purple |
| `application` | 75% | 🔵 Blue |
| `mastered` | 100% | ✅ Green + checkmark |

**Igor unlocks at 60% overall** — meaning most lessons need at least `rote_level` (50% each) to cross the threshold.

---

## Full Example: Student Alex Studies "Privileges & Limitations"

| Step | What Happens | State Change | Dashboard |
|------|-------------|--------------|-----------|
| 1 | Alex types: "Can I fly with an expired medical?" | `PA_I_A_01`: `new` → `seen` | Yellow dot appears |
| 2 | Specialist answers with citations, Socratic Teacher asks follow-ups | *No change* | Still yellow |
| 3 | Alex clicks "Ready to lock this in?" → Quiz appears in Drawer | *No change* | Still yellow |
| 4 | Alex scores 90% on the quiz | `PA_I_A_01`: `seen` → `rote_level` | 🟣 Purple, 🔔 "Sully unlocked for Privileges & Limitations!" |
| 5 | ⏳ *14 days pass without review* | `PA_I_A_01`: `rote_level` → `seen` (decay) | ⚠️ Back to yellow, prioritized for review |
| 6 | Alex retakes quiz, scores 85% | `PA_I_A_01`: `seen` → `rote_level` | 🟣 Purple again, timer resets |
| 7 | Alex does Sully voice session, Admin grades PASS | `PA_I_A_01`: `rote_level` → `application` | 🔵 Blue |
| 8 | Alex reaches 60% overall → Igor unlocks | *Global threshold crossed* | 🔔 "Igor DPE Mock Checkride is now available!" |
| 9 | Alex does Igor checkride, Admin grades PASS | `PA_I_A_01`: `application` → `mastered` | ✅ Permanent checkmark |
