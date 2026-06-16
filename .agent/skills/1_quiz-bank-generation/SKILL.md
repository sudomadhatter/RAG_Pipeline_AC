---
name: quiz-bank-generation
description: >
  Skill for creating 8-question quiz banks grounded in RKP manifests. Covers the
  4-perspective structure (Legal/Safety/Application/Risk Management), SJT authoring
  rules, difficulty levers, explanation standards, and Firebase deployment.
  Activates when an RKP manifest is ready and Daniel requests quiz generation.
  Gold standard: Area I quiz banks (PPL_PA_I_*). The 13 non-Area-I quiz files
  (III/VI/VII/IX/XI) are sub-par and being rewritten — do NOT model on them.
---

# Quiz Bank Generation Skill

> **Owner:** Woz (Agent) — generates quiz banks from completed RKP manifests.
> **Trigger:** An RKP manifest exists and Daniel requests quiz creation.
> **Output:** `{lesson_id}_quiz.json` in `specialist_curriculum/quiz_banks/` + pushed to Firebase.
> **Gold Standard:** Area I quiz banks (`PPL_PA_I_*`) ONLY. The 13 non-Area-I files are being rewritten.

---

## 1. The Structural Contract (Non-Negotiable)

| Rule | Value |
|---|---|
| Questions per lesson | **8** |
| Distribution | **2 legal · 2 safety · 2 application · 2 risk_management** |
| `risk_management` type | **SJT** (Situational Judgment Test) preferred; `mcq` only if SJT doesn't fit |
| Other three perspectives | `mcq` |
| Options | 4 (A–D) — one correct, three plausible |
| Pass threshold | **80%** (every distractor must *earn* its place) |
| Every question links to an RKP | `tested_rkp_id` is mandatory |
| Every RKP in the manifest | Must be tested by at least one question |

---

## 2. The Four Perspectives — What Each One Tests

Each perspective tests a **different layer of knowing**. All four for one lesson forces
the student to know the rule, its consequence, its application, AND the judgment around it.

### Legal — "What does the rule actually say?"
- Tests the **precise regulatory fact**.
- Frame in a **scenario** (ramp check, logbook question), NOT "According to 14 CFR..."
- Distractors are real aviation items that *sound* plausible.

> **Gold example (PPL_PA_I_A_01):** Ramp-checked, you show certificate + medical — what's the
> third required item? (Answer: government photo ID. Distractors: registration, logbook,
> flight-review endorsement — all real documents, none required on your person.)

### Safety — "Beyond the rule, why does it matter?" (second-order consequence)
- **This is NOT another legal question.** Safety asks for the **downstream real-world
  consequence** the regulation exists to prevent.
- The stem should literally say "Beyond the regulatory violation..." or similar.

> **Gold example (PPL_PA_I_A_01):** Pilot takes full payment for sightseeing flight —
> *beyond* the 61.113 violation, what compounding safety risk? (Answer: **voids the insurance**,
> leaving everyone financially exposed.)

### Application — "Apply the rule to this concrete situation"
- Usually a **calculation or specific fact pattern**.
- The student can't recall a sentence; they must *use* the rule.

> **Gold example (PPL_PA_I_A_01):** 3 people, $300 total, friend offers to pay all — max
> you can accept? (Answer: $200 = two passengers' pro-rata share.)

### Risk Management — the SJT (see §3 below)
- "All options are legal — which is the **safest** decision?"
- Tests judgment / human factors, not rules.

---

## 3. The SJT — The Crown Jewel

**Every option is legal and possible. The student must choose the safest aeronautical
decision.** This tests ADM and the five hazardous attitudes — the thing that actually
kills pilots.

### The Anatomy (Follow This Exactly)

```
STEM:    A specific scenario with time pressure or temptation.
         End with: "All four actions below are legal. Which is the SAFEST
         aeronautical decision?"

OPTION A → hazardous_attitude: "get_there_itis"   (chase the destination/schedule)
OPTION B → hazardous_attitude: "macho"            (overconfidence — "I can handle it")
OPTION C → hazardous_attitude: "resignation"      (give up entirely — cancel when middle path exists)
OPTION D → hazardous_attitude: null  ✅ CORRECT    (the ACTIVE professional middle path)

correct_answer: "D"
sjt_rationale:  Chain-of-Cues — name each option's attitude and WHY D is safest.
explanation:    Teach the principle + cite FAR/handbook + real accident data.
```

### The Rule That Makes a Real SJT (Most-Failed Test)

**D is NEVER "cancel the flight."** Cancelling is option **C — resignation.**

The correct answer is the **active, professional middle path**: introduce a
*self-assessment or objective test*, then a *risk mitigation plan*.

> **Gold example (PPL_PA_I_A_02, sinus congestion):** D = "Test equalization with a
> **Valsalva maneuver on the ground first** — if it fails or hurts, cancel; if it clears,
> depart but **plan a lower cruise altitude**." That's a *test* + a *mitigation*.

> **Gold example (PPL_PA_I_A_01, 80 days no-fly):** D = "**Fly a few solo patterns** this
> morning to shake off the rust, then **honestly assess** whether you're sharp enough."
> Test + honest self-assessment.

### The Five Hazardous Attitudes (FAA Standard Names)
`get_there_itis` · `macho` · `resignation` · `impulsivity` · `invulnerability`

The gold bank uses the first three for A/B/C. If impulsivity/invulnerability fit better
for a topic, swap them in — but keep **three distinct attitudes on A/B/C, safe path on D**.

### SJT Quality Gate — If Any Is False, It's Not a Real SJT
- [ ] Are **all four options actually legal/possible**?
- [ ] Does **D require active judgment** (a test + a mitigation), not just "be cautious / cancel"?
- [ ] Does **each of A/B/C embody a different, recognizable hazardous attitude**?
- [ ] Could a **rote student who memorized the reg still pick wrong**?

---

## 4. The Difficulty Levers

1. **Plausible distractors only.** Every wrong option = a mistake a real student makes.
   If you can eliminate an option because it's obviously silly, the question is easier than it looks.
2. **No rote-recall-only.** "What is Vx?" is trivia. "On a hot/high day with an obstacle,
   why does the stated Vx still apply but your margin shrinks?" tests understanding.
3. **Second-order reasoning.** Safety perspective especially: ask for the *consequence of
   the consequence* (insurance voids → personal liability), not the rule.
4. **Scenario specificity.** Real numbers, real airports (KPDK→KTYS), a named passenger,
   a concrete timeline. Specificity removes hand-waving.
5. **The "two right-looking answers" trap.** The best MCQs have a distractor that's
   *correct in a different context* — the student must catch the detail that makes it wrong *here*.
6. **Make rote knowledge necessary but not sufficient.** Need the fact AND the judgment.

---

## 5. The Explanation Standard (Half the Learning)

Every `explanation` must do three things:

1. **Teach the principle** — explain *why* the right answer is right and *why each tempting
   wrong answer fails*.
2. **Cite the authority** — specific FAR + handbook chapter (`14 CFR 61.3(a)`,
   `FAA-H-8083-2A Ch 2`).
3. **Ground in the real world** — cite actual accident/enforcement data. Examples from the
   gold bank: "NTSB Safety Alert SA-019", "NTSB CAROL search: 'proficiency'+'currency'+'fatal'",
   "FAA Order 2150.3C documents 61.3 as a top ramp-check enforcement citation."
   **Use real, verifiable references — never invent an NTSB number or accident.**

For SJTs, also write `sjt_rationale` — the **Chain-of-Cues**: walk option-by-option naming
the hazardous attitude and explaining why D's active path beats all three.

---

## 6. The `far_reference` Field — FAA Regulations ONLY

The `far_reference` field must contain **ONLY** official FAA regulatory citations:
- ✅ `14 CFR 61.56(c)`, `AC 91-67A`
- ❌ `Chero Interpretation (2015)`, `NTSB ERA19LA155`, `FAA Order 2150.3C`

Legal interpretations, NTSB numbers, and enforcement data go in the `explanation` prose ONLY.

---

## 7. JSON Schemas

### MCQ Schema (Legal, Safety, Application)

```json
{
  "id": "PPL_PA_I_A_01_Q001",
  "perspective": "legal",
  "question_type": "mcq",
  "tested_rkp_id": "RKP_01",
  "text": "Scenario stem that forces the concept",
  "options": [
    {"label": "A", "text": "Plausible mistake"},
    {"label": "B", "text": "The correct, non-obvious answer"},
    {"label": "C", "text": "Correct-in-another-context distractor"},
    {"label": "D", "text": "A real misconception"}
  ],
  "correct_answer": "B",
  "explanation": "Why B; why A/C/D fail; FAR + handbook; real accident data",
  "far_reference": "14 CFR 61.3(a)",
  "acs_element": "PA.I.A.K1"
}
```

### SJT Schema (Risk Management)

```json
{
  "id": "PPL_PA_I_A_01_Q007",
  "perspective": "risk_management",
  "question_type": "sjt",
  "tested_rkp_id": "RKP_03",
  "text": "Scenario with time pressure. All four actions below are legal. Which is the SAFEST aeronautical decision?",
  "options": [
    {"label": "A", "text": "Chase the goal", "hazardous_attitude": "get_there_itis"},
    {"label": "B", "text": "Overconfidence", "hazardous_attitude": "macho"},
    {"label": "C", "text": "Cancel/give up", "hazardous_attitude": "resignation"},
    {"label": "D", "text": "Active test + mitigation"}
  ],
  "correct_answer": "D",
  "sjt_rationale": "Chain-of-Cues: name each option's attitude; why D is safest",
  "explanation": "The ADM principle + FAA-H-8083-2A + real accident pattern",
  "far_reference": "14 CFR ...",
  "acs_element": "PA.I.A.R1"
}
```

### Quiz File Wrapper

```json
{
  "lesson_id": "PPL_PA_I_A_01",
  "title": "Privileges & Limitations",
  "questions": [ ... the 8 question objects ... ]
}
```

---

## 8. Execution Pipeline

### Step 1: Load the RKP Manifest
- Read the `{lesson_id}_rkp.json` from `specialist_curriculum/rkp_manifests/`.
- List all RKPs and their `knowledge`, `acs_elements`, `far_references`.

### Step 2: Plan the Coverage
- Map each of the 8 questions to an RKP via `tested_rkp_id`.
- Ensure **every RKP** appears in at least one `tested_rkp_id`.
- Distribute across perspectives: 2L / 2S / 2A / 2RM.

### Step 3: Author the Questions
For each question:
1. **Read the target RKP's `knowledge` field.** This is your source of truth.
2. **Write the scenario stem.** Specific, concrete, no hand-waving.
3. **Write the correct answer.** Ground it in the RKP + cited FAR.
4. **Write three plausible distractors.** Each = a real student mistake.
5. **Write the explanation.** Teach why + cite authority + cite real accident data.
6. **Run the pre-ship self-check** (§10) on each question.

### Step 4: Run the Pre-Ship Self-Check
See §10 below. Every checkbox must pass.

### Step 5: Present to Daniel for CFI Review
- **No question enters the quiz bank without Daniel's explicit approval.**
- Show all 8 questions with RKP mapping and coverage summary.

### Step 6: Write the Quiz JSON
- Save to `specialist_curriculum/quiz_banks/{lesson_id}_quiz.json`.

### Step 7: Push to Firebase
After Daniel approves, push to the live Firestore database:

```bash
cd src/gcp
python upload_quiz_banks.py
```

This script:
- Reads all `*_quiz.json` files from `specialist_curriculum/quiz_banks/`
- Connects to Firestore database `aviationchat-database`
- Writes each quiz to the `quiz_banks` collection using `lesson_id` as the document ID
- Uses `set()` which creates or overwrites the existing document
- Requires `auth_keys/librarian-service-account.json`

> [!IMPORTANT]
> The upload script path in `upload_quiz_banks.py` line 10 currently points to
> `c:\AGY-Projects\ingestion-Pipeline-AC`. This may need to be updated to match
> the current workspace path. Verify before running.

### Step 8: Also Push RKP Manifests (if not already done)
If the corresponding RKP manifest hasn't been pushed to Firebase yet:

```bash
cd src/gcp
python upload_manifests.py
```

This pushes `*_rkp.json` files to the `rkp_manifests` Firestore collection.

---

## 9. Anti-Patterns — Reject Any Question That Does These

| Anti-pattern | Why it's bad | Fix |
|---|---|---|
| Distractors that are obviously absurd | Turns 4-option into 2-option | Every distractor = real student mistake |
| Pure trivia / definition recall | Tests memory, not understanding | Put in scenario; ask "why/when/so what" |
| "Safety" that's just another legal Q | Wastes the perspective | Ask the second-order consequence |
| SJT where one option is illegal | It's not an SJT | All four must be legal |
| SJT where D = "cancel / don't fly" | That's resignation (C) | D = test + mitigation (active middle path) |
| Invented references / fake NTSB numbers | Destroys trust | Cite real FARs/handbooks/accident data only |
| Two options both fully correct | Ambiguous; student guesses | Exactly one correct; distractors wrong *here* |
| Correct answer noticeably longer than distractors | "Too Long To Be Wrong" — students pick longest | All 4 options within 10% character length |
| `far_reference` with legal interpretations | Pollutes the regulatory field | Legal interp → `explanation` prose only |

---

## 10. Pre-Ship Self-Check (Run on Every 8-Question Bank)

- [ ] Exactly 8 questions: 2 legal, 2 safety, 2 application, 2 risk_management.
- [ ] The 2 risk_management are real SJTs (all-legal options, A/B/C attitudes, D = active middle path).
- [ ] No distractor is obviously eliminable; each is a real student mistake.
- [ ] Each "safety" question asks a second-order consequence, not a restated rule.
- [ ] Every `explanation` teaches the why + cites a real FAR/handbook + real accident/enforcement data (no invented references).
- [ ] Every question has a valid `tested_rkp_id` pointing at an RKP in this lesson.
- [ ] Every RKP in the manifest appears in at least one `tested_rkp_id`.
- [ ] All 4 options in every question are within 10% character length of each other.
- [ ] A rote student who memorized the reg could *still* miss the SJTs and safety questions.

> If you can't honestly check the last box, the bank is too easy — a 4× retry student
> will pass on memory alone, and the 80% gate means nothing.

---

## 11. Naming Convention

| Component | Pattern | Example |
|---|---|---|
| Quiz File | `{lesson_id}_quiz.json` | `PPL_PA_I_A_01_quiz.json` |
| Question ID | `{lesson_id}_Q{NNN}` | `PPL_PA_I_A_01_Q001` |
| Firestore Collection | `quiz_banks` | — |
| Firestore Doc ID | `{lesson_id}` | `PPL_PA_I_A_01` |

---

## 12. Gold Standards (Read These First)

| File | Why |
|---|---|
| [PPL_PA_I_A_01_quiz.json](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/specialist_curriculum/quiz_banks/PPL_PA_I_A_01_quiz.json) | The original gold standard — all 4 perspectives, real SJTs |
| [quiz_schema.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/specialist_curriculum/quiz_schema.md) | Locked JSON schema + field reference |
| [quiz_authoring_guide.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/_01_My/quiz_authoring_guide.md) | Daniel's quality bar — difficulty levers + SJT rules |
| [quiz_generator_prompt.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/_01_My/project_context_prps/quiz_generator_prompt.md) | System prompt + 12 Lessons Learned |

---

## 13. Which Quiz Banks Need Rewriting

The **Area I** banks (`PPL_PA_I_A_*` through `PPL_PA_I_H_*`) are the gold standard — **do NOT rewrite these**.

The following 13 quiz banks from the last 5 master modules are **sub-par and must be rewritten**:

| lesson_id | File | Status |
|---|---|---|
| `PPL_PA_III_A_01` | `PPL_PA_III_A_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_III_A_02` | `PPL_PA_III_A_02_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_III_B_01` | `PPL_PA_III_B_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_VI_B_01` | `PPL_PA_VI_B_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_VI_B_02` | `PPL_PA_VI_B_02_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_VI_B_03` | `PPL_PA_VI_B_03_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_VII_A_01` | `PPL_PA_VII_A_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_VII_D_01` | `PPL_PA_VII_D_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_IX_B_01` | `PPL_PA_IX_B_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_IX_C_01` | `PPL_PA_IX_C_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_XI_A_01` | `PPL_PA_XI_A_01_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_XI_A_02` | `PPL_PA_XI_A_02_quiz.json` | ❌ Rewrite needed |
| `PPL_PA_XI_A_03` | `PPL_PA_XI_A_03_quiz.json` | ❌ Rewrite needed |

**These were never pushed to Firebase** — so no live data needs to be rolled back.
After rewriting, they go through Daniel's CFI review, then get pushed via `upload_quiz_banks.py`.

---

## 14. Firebase Deployment

### Quiz Banks → Firestore

**Script:** [upload_quiz_banks.py](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/src/gcp/upload_quiz_banks.py)

```bash
cd src/gcp
python upload_quiz_banks.py
```

| Detail | Value |
|---|---|
| Firestore database | `aviationchat-database` |
| Collection | `quiz_banks` |
| Document ID | `{lesson_id}` (e.g., `PPL_PA_I_A_01`) |
| Write mode | `set()` — creates or overwrites |
| Auth | `auth_keys/librarian-service-account.json` |
| Source | `specialist_curriculum/quiz_banks/*_quiz.json` |

### RKP Manifests → Firestore

**Script:** [upload_manifests.py](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Ingestion_pipeline_AvCh/src/gcp/upload_manifests.py)

```bash
cd src/gcp
python upload_manifests.py
```

| Detail | Value |
|---|---|
| Collection | `rkp_manifests` |
| Document ID | `{lesson_id}` |
| Everything else | Same as quiz banks |

### Pre-Push Checklist
- [ ] Quiz JSON passes the pre-ship self-check (§10)
- [ ] Daniel has explicitly approved the quiz bank
- [ ] `lesson_id` field is present and matches the filename
- [ ] The corresponding RKP manifest is also pushed (or was previously)
- [ ] `auth_keys/librarian-service-account.json` exists and is valid
- [ ] Script path in `upload_quiz_banks.py` line 10 matches the workspace
