# CFI RKP Authoring Workbook

**Purpose:** Everything Daniel needs to author the Required Knowledge Point (RKP) manifests for all 34 active PPL lessons.  
**Output:** One JSON file per lesson → `docs/lesson_rkps/{lesson_id}_rkp.json`

---

## Quick Reference: The JSON Template

Copy this for each lesson and fill it in:

```json
{
  "lesson_id": "PPL_PA_I_A_01",
  "title": "Privileges & Limitations",
  "acs_task_reference": "Area I, Task A",
  "acs_element_keys": ["PA.I.A.K1", "PA.I.A.K2", "PA.I.A.R1"],
  
  "required_knowledge_points": [
    {
      "id": "RKP_01",
      "title": "Short headline of the knowledge point",
      "why": "Brief reason this knowledge matters (1 sentence)",
      "knowledge": "The actual knowledge the student must articulate. 2-4 sentences. Include FAR numbers.",
      "acs_elements": ["PA.I.A.K1"],
      "far_references": ["14 CFR 61.1"],
      "bridge_keys": ["PHAK Ch 1"]
    }
  ],

  "audio_file": null
}
```

### Field Guide

| Field | What to Write | Keep It... |
|-------|--------------|-----------|
| `id` | Sequential: `RKP_01`, `RKP_02`, etc. | Automated |
| `title` | **Flashcard front headline.** What's the topic? | Short — 5-8 words max |
| `why` | Why this knowledge matters. Not "the DPE will ask" — state the practical importance. | 1 sentence |
| `knowledge` | **Flashcard back.** The answer you'd accept in an oral exam. Include FAR numbers. | 2-4 sentences |
| `acs_elements` | Which ACS codes this RKP covers | From the table below |
| `far_references` | Specific FARs cited in the knowledge | What you reference |
| `bridge_keys` | Source documents (PHAK chapters, AC numbers) | What backs it up |
| `audio_file` | Podcast filename. Set `null` until produced. | `null` or `"PPL_PA_I_A_01_audio.mp3"` |

### Rules of Thumb
- **3-6 RKPs per lesson** (target 4)
- **Every ACS element must be covered** by at least one RKP
- **One RKP can cover multiple ACS elements** if they're closely related
- **Think from the DPE's chair:** "What would I fail a student for not knowing?"

---

## The Master Lesson List — All 34 Active Lessons

> [!IMPORTANT]
> These are the 34 lessons with `status != "draft"` in `curriculum_key.json`. Each needs one `{lesson_id}_rkp.json` file. The ACS elements, prerequisites, and suggested RKP count are provided.

---

### Area I, Task A — Pilot Qualifications

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 1 | `PPL_PA_I_A_01` | `PPL_PA_I_A_01_rkp.json` | Privileges & Limitations | `PA.I.A.K1`, `PA.I.A.K2`, `PA.I.A.R1` | _(none)_ | 3-4 |
| 2 | `PPL_PA_I_A_02` | `PPL_PA_I_A_02_rkp.json` | Medical Certificates (Classes & BasicMed) | `PA.I.A.K3`, `PA.I.A.K4` | K1 | 3-4 |
| 3 | `PPL_PA_I_A_03` | `PPL_PA_I_A_03_rkp.json` | Currency vs. Proficiency | `PA.I.A.K5`, `PA.I.A.R2` | K1 | 3-4 |
| 4 | `PPL_PA_I_A_04` | `PPL_PA_I_A_04_rkp.json` | Required Pilot Documents | `PA.I.A.K6`, `PA.I.A.S1` | K1 | 3-4 |

---

### Area I, Task B — Airworthiness Requirements

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 5 | `PPL_PA_I_B_01` | `PPL_PA_I_B_01_rkp.json` | Required Aircraft Documents (ARROW) | `PA.I.B.K1`, `PA.I.B.S1` | K1 | 3-4 |
| 6 | `PPL_PA_I_B_02` | `PPL_PA_I_B_02_rkp.json` | Required Inspections (AVIATES) | `PA.I.B.K2` | B.K1 | 3-4 |
| 7 | `PPL_PA_I_B_03` | `PPL_PA_I_B_03_rkp.json` | Airworthiness Directives (ADs) | `PA.I.B.K3`, `PA.I.B.K3a`, `PA.I.B.K3b` | B.K2 | 4-5 |
| 8 | `PPL_PA_I_B_04` | `PPL_PA_I_B_04_rkp.json` | Flying with Inoperative Equipment (91.213) | `PA.I.B.K4`, `PA.I.B.R1`, `PA.I.B.S2` | B.K1 | 4-5 |

---

### Area I, Task C — Weather Information

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 9 | `PPL_PA_I_C_01` | `PPL_PA_I_C_01_rkp.json` | Reading & Decoding METARs | `PA.I.C.K2`, `PA.I.C.K2a` | A.K6 | 3-4 |
| 10 | `PPL_PA_I_C_02` | `PPL_PA_I_C_02_rkp.json` | Reading & Decoding TAFs | `PA.I.C.K2`, `PA.I.C.K2b` | C.K2a | 3-4 |
| 11 | `PPL_PA_I_C_03` | `PPL_PA_I_C_03_rkp.json` | PIREPs & Winds Aloft | `PA.I.C.K2c`, `PA.I.C.K2d` | C.K2 | 3-4 |
| 12 | `PPL_PA_I_C_04` | `PPL_PA_I_C_04_rkp.json` | AIRMETs, SIGMETs & Convective SIGMETs | `PA.I.C.K2e`, `PA.I.C.K2f` | C.K2 | 3-4 |
| 13 | `PPL_PA_I_C_05` | `PPL_PA_I_C_05_rkp.json` | Weather Hazards (Thunderstorms & Icing) | `PA.I.C.K3`, `PA.I.C.R1`, `PA.I.C.R2` | C.K2 | 4-5 |

---

### Area I, Task D — Cross-Country Flight Planning

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 14 | `PPL_PA_I_D_01` | `PPL_PA_I_D_01_rkp.json` | Selecting VFR Cruising Altitudes | `PA.I.D.K2`, `PA.I.D.S2` | C.K3 | 3-4 |
| 15 | `PPL_PA_I_D_02` | `PPL_PA_I_D_02_rkp.json` | Calculating Time, Speed, Distance & Fuel | `PA.I.D.K3`, `PA.I.D.S3`, `PA.I.D.S4` | G.K1 | 4-5 |
| 16 | `PPL_PA_I_D_03` | `PPL_PA_I_D_03_rkp.json` | Choosing an Alternate Airport | `PA.I.D.K4`, `PA.I.D.R2` | C.K2 | 3-4 |
| 17 | `PPL_PA_I_D_04` | `PPL_PA_I_D_04_rkp.json` | Filing a VFR Flight Plan | `PA.I.D.K5`, `PA.I.D.S8` | D.K3 | 3-4 |

---

### Area I, Task E — National Airspace System

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 18 | `PPL_PA_I_E_01` | `PPL_PA_I_E_01_rkp.json` | Class A, B, and C Airspace | `PA.I.E.K1`, `PA.I.E.K1a`, `PA.I.E.K1b`, `PA.I.E.K1c` | A.K1 | **5-6** |
| 19 | `PPL_PA_I_E_02` | `PPL_PA_I_E_02_rkp.json` | Class D, E, and G Airspace | `PA.I.E.K1d`, `PA.I.E.K1e`, `PA.I.E.K1f` | E.K1 | 4-5 |
| 20 | `PPL_PA_I_E_03` | `PPL_PA_I_E_03_rkp.json` | VFR Weather Minimums (91.155) | `PA.I.E.K2`, `PA.I.E.S1` | E.K1 | 3-4 |
| 21 | `PPL_PA_I_E_04` | `PPL_PA_I_E_04_rkp.json` | Special Use Airspace | `PA.I.E.K3`, `PA.I.E.S2` | E.K1 | 3-4 |

---

### Area I, Task F — Performance & Limitations

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 22 | `PPL_PA_I_F_01` | `PPL_PA_I_F_01_rkp.json` | Atmospheric Pressure & Density Altitude | `PA.I.F.K1`, `PA.I.F.K1a`, `PA.I.F.K1b` | C.K2 | 4-5 |
| 23 | `PPL_PA_I_F_02` | `PPL_PA_I_F_02_rkp.json` | Calculating Weight & Balance | `PA.I.F.K2`, `PA.I.F.S1` | F.K2 | 3-4 |
| 24 | `PPL_PA_I_F_03` | `PPL_PA_I_F_03_rkp.json` | Takeoff & Landing Distances | `PA.I.F.K3`, `PA.I.F.S2` | F.K1 | 3-4 |
| 25 | `PPL_PA_I_F_04` | `PPL_PA_I_F_04_rkp.json` | Effects of Forward vs. Aft CG | `PA.I.F.K2`, `PA.I.F.R1` | F.S1 | 3-4 |

---

### Area I, Task G — Operation of Systems

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 26 | `PPL_PA_I_G_01` | `PPL_PA_I_G_01_rkp.json` | Primary Flight Controls & Trim | `PA.I.G.K1`, `PA.I.G.K1a` | C.K2 | 3-4 |
| 27 | `PPL_PA_I_G_02` | `PPL_PA_I_G_02_rkp.json` | The Powerplant & Propeller | `PA.I.G.K1b`, `PA.I.G.K1c` | G.K1 | 3-4 |
| 28 | `PPL_PA_I_G_03` | `PPL_PA_I_G_03_rkp.json` | Fuel & Oil Systems | `PA.I.G.K1d`, `PA.I.G.K1e` | G.K1b | 3-4 |
| 29 | `PPL_PA_I_G_04` | `PPL_PA_I_G_04_rkp.json` | The Electrical System | `PA.I.G.K1f`, `PA.I.G.K1g` | G.K1 | 3-4 |
| 30 | `PPL_PA_I_G_05` | `PPL_PA_I_G_05_rkp.json` | Pitot-Static & Vacuum Systems | `PA.I.G.K1h`, `PA.I.G.K1i` | G.K1 | 3-4 |

---

### Area I, Task H — Human Factors

| # | Lesson ID | File Name | Title | ACS Elements | Prereq | Suggested RKPs |
|---|-----------|-----------|-------|-------------|--------|---------------|
| 31 | `PPL_PA_I_H_01` | `PPL_PA_I_H_01_rkp.json` | Hypoxia & Hyperventilation | `PA.I.H.K1`, `PA.I.H.K2` | F.K1 | 3-4 |
| 32 | `PPL_PA_I_H_02` | `PPL_PA_I_H_02_rkp.json` | Spatial Disorientation & Motion Sickness | `PA.I.H.K4`, `PA.I.H.K5` | H.K1 | 3-4 |
| 33 | `PPL_PA_I_H_03` | `PPL_PA_I_H_03_rkp.json` | Carbon Monoxide & Scuba Rules | `PA.I.H.K6`, `PA.I.H.K8` | H.K1 | 3-4 |
| 34 | `PPL_PA_I_H_04` | `PPL_PA_I_H_04_rkp.json` | Aeronautical Decision Making (PAVE & IMSAFE) | `PA.I.H.S1`, `PA.I.H.R1` | H.K2 | 3-4 |

---

## Summary Stats

| Metric | Value |
|--------|-------|
| **Total active lessons** | 34 |
| **Total ACS elements across all lessons** | 79 |
| **Estimated total RKPs to author** | 120-140 |
| **Lessons with 4+ ACS elements (highest priority)** | 5 (E_01, E_02, B_03, B_04, F_01) |
| **Lessons with ≤ 2 ACS elements (quickest)** | 14 |

---

## Suggested Authoring Order

> [!TIP]
> **Start with the highest-risk lessons** (most ACS elements) so the pipeline has the most impactful data first.

**Batch 1 — High-Risk (4+ elements, 5 lessons):**
1. `PPL_PA_I_E_01` — Class A, B, C Airspace (4 elements)
2. `PPL_PA_I_E_02` — Class D, E, G Airspace (3 elements)
3. `PPL_PA_I_B_03` — Airworthiness Directives (3 elements)
4. `PPL_PA_I_B_04` — Inoperative Equipment (3 elements)
5. `PPL_PA_I_F_01` — Density Altitude (3 elements)

**Batch 2 — Medium-Risk (3 elements, 9 lessons):**
- I_A_01, I_C_05, I_D_02, I_A_03, I_D_01, I_D_03, I_F_02, I_F_03, I_F_04

**Batch 3 — Standard (2 elements, 20 lessons):**
- All remaining lessons

---

## Completed RKP File Checklist

Check off as you complete each file:

```
[ ] PPL_PA_I_A_01_rkp.json — Privileges & Limitations
[ ] PPL_PA_I_A_02_rkp.json — Medical Certificates
[ ] PPL_PA_I_A_03_rkp.json — Currency vs. Proficiency
[ ] PPL_PA_I_A_04_rkp.json — Required Pilot Documents
[ ] PPL_PA_I_B_01_rkp.json — Required Aircraft Documents (ARROW)
[ ] PPL_PA_I_B_02_rkp.json — Required Inspections (AVIATES)
[ ] PPL_PA_I_B_03_rkp.json — Airworthiness Directives (ADs)
[ ] PPL_PA_I_B_04_rkp.json — Flying with Inoperative Equipment
[ ] PPL_PA_I_C_01_rkp.json — Reading & Decoding METARs
[ ] PPL_PA_I_C_02_rkp.json — Reading & Decoding TAFs
[ ] PPL_PA_I_C_03_rkp.json — PIREPs & Winds Aloft
[ ] PPL_PA_I_C_04_rkp.json — AIRMETs, SIGMETs & Convective SIGMETs
[ ] PPL_PA_I_C_05_rkp.json — Weather Hazards
[ ] PPL_PA_I_D_01_rkp.json — Selecting VFR Cruising Altitudes
[ ] PPL_PA_I_D_02_rkp.json — Calculating Time, Speed, Distance & Fuel
[ ] PPL_PA_I_D_03_rkp.json — Choosing an Alternate Airport
[ ] PPL_PA_I_D_04_rkp.json — Filing a VFR Flight Plan
[ ] PPL_PA_I_E_01_rkp.json — Class A, B, and C Airspace
[ ] PPL_PA_I_E_02_rkp.json — Class D, E, and G Airspace
[ ] PPL_PA_I_E_03_rkp.json — VFR Weather Minimums
[ ] PPL_PA_I_E_04_rkp.json — Special Use Airspace
[ ] PPL_PA_I_F_01_rkp.json — Atmospheric Pressure & Density Altitude
[ ] PPL_PA_I_F_02_rkp.json — Calculating Weight & Balance
[ ] PPL_PA_I_F_03_rkp.json — Takeoff & Landing Distances
[ ] PPL_PA_I_F_04_rkp.json — Effects of Forward vs. Aft CG
[ ] PPL_PA_I_G_01_rkp.json — Primary Flight Controls & Trim
[ ] PPL_PA_I_G_02_rkp.json — The Powerplant & Propeller
[ ] PPL_PA_I_G_03_rkp.json — Fuel & Oil Systems
[ ] PPL_PA_I_G_04_rkp.json — The Electrical System
[ ] PPL_PA_I_G_05_rkp.json — Pitot-Static & Vacuum Systems
[ ] PPL_PA_I_H_01_rkp.json — Hypoxia & Hyperventilation
[ ] PPL_PA_I_H_02_rkp.json — Spatial Disorientation & Motion Sickness
[ ] PPL_PA_I_H_03_rkp.json — Carbon Monoxide & Scuba Rules
[ ] PPL_PA_I_H_04_rkp.json — Aeronautical Decision Making (PAVE & IMSAFE)
```

---

## Validation

Once you've authored a batch, hand the files to the agent. The agent will:
1. Validate JSON syntax
2. Validate against the Pydantic schema (`backend/schemas/rkp.py`)
3. Cross-reference ACS elements against `curriculum_key.json` to ensure full coverage
4. Flag any lessons with missing ACS element coverage

---

## ⚠️ Authoring Tooling Notes (Agent SOP)

> [!CAUTION]
> **The native `write_to_file` tool consistently stalls and times out** when writing
> JSON files to `docs/lesson_rkps/`. All models tested (Gemini, GPT, Claude) hit this.
> The root cause appears to be the tool's internal directory-creation logic hanging on
> this workspace.

**What works:** Use PowerShell's `[System.IO.File]::WriteAllText()` via `run_command`:

```powershell
$json = @'
{ ... your JSON here ... }
'@
New-Item -ItemType Directory -Force -Path "c:\Sudo_Hatter_Command\Projects\ingestion-Pipeline-AC\docs\lesson_rkps" | Out-Null
[System.IO.File]::WriteAllText("c:\Sudo_Hatter_Command\Projects\ingestion-Pipeline-AC\docs\lesson_rkps\PPL_PA_I_A_01_rkp.json", $json)
Write-Host "SUCCESS: File written."
```

**Also works:** The `write_to_file` tool succeeds for the `rkps_podcast/` directory (markdown files). Only the `docs/lesson_rkps/` path (JSON files) is affected.

**Pipeline per lesson (execute one at a time):**
1. Write `docs/lesson_rkps/{id}_rkp.json` via PowerShell `run_command`
2. Write `rkps_podcast/{id}.md` via `write_to_file` (this one works)
3. FAA document grounding (web search / DB search)
4. SJT quiz generation (only after step 3)
