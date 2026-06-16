# Quiz Bank Schema — V2.1 (LOCKED)
## Consultant-Approved: 2026-04-05

> [!IMPORTANT]
> **This schema is LOCKED.** All 5 open questions were resolved by the consultant. No field changes without explicit approval.

---

## Rulings Summary

| # | Question | Ruling |
|---|---|---|
| 1 | Scoring schema | `correct_answer: "B"` — single string, not booleans |
| 2 | SJT partial credit | **NO** — binary right/wrong. D is correct, A/B/C are wrong |
| 3 | `tested_rkp_id` | **YES** — mandatory on all 272 questions |
| 4 | Missing ACS element types | **YES** — Application can use K/R elements (Bloom's Taxonomy) |
| 5 | Hazardous attitude labels | **YES** — `hazardous_attitude` field on each incorrect SJT option |

---

## Question Count (Non-Negotiable — FR12-B)

| Perspective | Count | question_type |
|---|---|---|
| `legal` | **2** | `mcq` |
| `safety` | **2** | `mcq` |
| `application` | **2** | `mcq` |
| `risk_management` | **2** | `sjt` (preferred) or `mcq` (if SJT doesn't fit) |
| **TOTAL** | **8** | — |

---

## MCQ Schema (Legal, Safety, Application)

```json
{
  "id": "PPL_PA_I_A_01_Q001",
  "perspective": "legal",
  "question_type": "mcq",
  "tested_rkp_id": "RKP_01",
  "text": "Question text shown to the student",
  "options": [
    {"label": "A", "text": "Option A text"},
    {"label": "B", "text": "Option B text"},
    {"label": "C", "text": "Option C text"},
    {"label": "D", "text": "Option D text"}
  ],
  "correct_answer": "B",
  "explanation": "Post-answer explanation citing the specific FAR or source.",
  "far_reference": "14 CFR 61.56(c)",
  "acs_element": "PA.I.A.K1"
}
```

### MCQ Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | YES | `{lesson_id}_Q{number}` — unique across all questions |
| `perspective` | string | YES | `legal`, `safety`, `application`, or `risk_management` |
| `question_type` | string | YES | `mcq` or `sjt` |
| `tested_rkp_id` | string | YES | Links to the specific RKP this question evaluates |
| `text` | string | YES | The question shown to the student |
| `options` | array | YES | 4 options with `label` (A/B/C/D) and `text` |
| `correct_answer` | string | YES | The label of the correct option (`"A"`, `"B"`, `"C"`, or `"D"`) |
| `explanation` | string | YES | Post-answer explanation citing the source |
| `far_reference` | string | YES | Specific FAR, AC, or handbook reference |
| `acs_element` | string | YES | ACS element code (e.g., `PA.I.A.K1`) |

---

## SJT Schema (Risk Management)

**Core Principle: ALL FOUR OPTIONS ARE TECHNICALLY LEGAL/POSSIBLE.**

The student must identify the **safest PIC decision**, not the only legal one. Each wrong option maps to a specific FAA hazardous attitude from FAA-H-8083-2A:

| Option | Hazardous Attitude | What It Tempts |
|---|---|---|
| A | `get_there_itis` | Pressure to complete the flight despite risk |
| B | `macho` | Overconfidence — "I can handle it" |
| C | `resignation` | Passivity — "nothing I can do" |
| **D** | — | **Safest PIC Decision (always correct)** |

```json
{
  "id": "PPL_PA_I_A_01_Q007",
  "perspective": "risk_management",
  "question_type": "sjt",
  "tested_rkp_id": "RKP_03",
  "text": "SJT scenario text",
  "options": [
    {"label": "A", "text": "Option A text", "hazardous_attitude": "get_there_itis"},
    {"label": "B", "text": "Option B text", "hazardous_attitude": "macho"},
    {"label": "C", "text": "Option C text", "hazardous_attitude": "resignation"},
    {"label": "D", "text": "Option D text"}
  ],
  "correct_answer": "D",
  "sjt_rationale": "Why D is safest and how A/B/C represent hazardous attitudes.",
  "explanation": "Post-answer explanation.",
  "far_reference": "FAA-H-8083-2A",
  "acs_element": "PA.I.A.R1"
}
```

### Additional SJT Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `hazardous_attitude` | string | YES (on options A/B/C only) | `get_there_itis`, `macho`, or `resignation` |
| `sjt_rationale` | string | YES | Why D mitigates risk better than A/B/C |

> [!CAUTION]
> If the topic does NOT support 4 equally legal options with distinct hazardous attitudes, use `question_type: "mcq"` instead. **Do not force SJT.**

---

## ACS Element to Lesson ID Mapping

| ACS Element | lesson_id | Title |
|---|---|---|
| PA.I.A.K1, K2, R1 | `PPL_PA_I_A_01` | Privileges & Limitations |
| PA.I.A.K3, K4 | `PPL_PA_I_A_02` | Medical Certificates |
| PA.I.A.K5, R2 | `PPL_PA_I_A_03` | Currency vs. Proficiency |
| PA.I.A.K6, S1 | `PPL_PA_I_A_04` | Required Pilot Documents |
| PA.I.B.K1, S1 | `PPL_PA_I_B_01` | Required Aircraft Documents (ARROW) |
| PA.I.B.K2 | `PPL_PA_I_B_02` | Required Inspections (AVIATES) |
| PA.I.B.K3, K3a, K3b | `PPL_PA_I_B_03` | Airworthiness Directives (ADs) |
| PA.I.B.K4, R1, S2 | `PPL_PA_I_B_04` | Flying with Inoperative Equipment (91.213) |
| PA.I.C.K2, K2a | `PPL_PA_I_C_01` | Reading & Decoding METARs |
| PA.I.C.K2, K2b | `PPL_PA_I_C_02` | Reading & Decoding TAFs |
| PA.I.C.K2c, K2d | `PPL_PA_I_C_03` | PIREPs & Winds Aloft |
| PA.I.C.K2e, K2f | `PPL_PA_I_C_04` | AIRMETs, SIGMETs & Convective SIGMETs |
| PA.I.C.K3, R1, R2 | `PPL_PA_I_C_05` | Weather Hazards (Thunderstorms & Icing) |
| PA.I.D.K2, S2 | `PPL_PA_I_D_01` | Selecting VFR Cruising Altitudes |
| PA.I.D.K3, S3, S4 | `PPL_PA_I_D_02` | Calculating Time, Speed, Distance & Fuel |
| PA.I.D.K4, R2 | `PPL_PA_I_D_03` | Choosing an Alternate Airport |
| PA.I.D.K5, S8 | `PPL_PA_I_D_04` | Filing a VFR Flight Plan |
| PA.I.E.K1, K1a, K1b, K1c | `PPL_PA_I_E_01` | Class A, B, and C Airspace |
| PA.I.E.K1d, K1e, K1f | `PPL_PA_I_E_02` | Class D, E, and G Airspace |
| PA.I.E.K2, S1 | `PPL_PA_I_E_03` | VFR Weather Minimums (91.155) |
| PA.I.E.K3, S2 | `PPL_PA_I_E_04` | Special Use Airspace |
| PA.I.F.K1, K1a, K1b | `PPL_PA_I_F_01` | Atmospheric Pressure & Density Altitude |
| PA.I.F.K2, S1 | `PPL_PA_I_F_02` | Calculating Weight & Balance |
| PA.I.F.K3, S2 | `PPL_PA_I_F_03` | Takeoff & Landing Distances |
| PA.I.F.K2, R1 | `PPL_PA_I_F_04` | Effects of Forward vs. Aft CG |
| PA.I.G.K1, K1a | `PPL_PA_I_G_01` | Primary Flight Controls & Trim |
| PA.I.G.K1b, K1c | `PPL_PA_I_G_02` | The Powerplant & Propeller |
| PA.I.G.K1d, K1e | `PPL_PA_I_G_03` | Fuel & Oil Systems |
| PA.I.G.K1f, K1g | `PPL_PA_I_G_04` | The Electrical System |
| PA.I.G.K1h, K1i | `PPL_PA_I_G_05` | Pitot-Static & Vacuum Systems |
| PA.I.H.K1, K2 | `PPL_PA_I_H_01` | Hypoxia & Hyperventilation |
| PA.I.H.K4, K5 | `PPL_PA_I_H_02` | Spatial Disorientation & Motion Sickness |
| PA.I.H.K6, K8 | `PPL_PA_I_H_03` | Carbon Monoxide & Scuba Rules |
| PA.I.H.S1, R1 | `PPL_PA_I_H_04` | Aeronautical Decision Making (PAVE & IMSAFE) |

---

## File Structure
- **Location:** `quizzes/banks/`
- **Naming:** `PPL_PA_I_A_01.json`, `PPL_PA_I_A_02.json`, etc.
- **Total:** 34 files, 8 questions each = 272 questions

## Deliverable
34 JSON files in `quizzes/banks/`. Each reviewed and approved by CFI before ingestion.