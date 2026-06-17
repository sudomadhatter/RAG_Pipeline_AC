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
> **Gold Standard:** Area I quiz banks (`PPL_PA_I_*`) ONLY.

---

## 1. The Structural Contract (Non-Negotiable)

| Rule | Value |
|---|---|
| Questions per lesson | **8** |
| Distribution | **2 legal · 2 safety · 2 application · 2 risk_management** |
| `risk_management` type | **SJT** preferred; `mcq` only if SJT doesn't fit |
| Options | 4 (A–D) — one correct, three plausible |
| Pass threshold | **80%** |
| Every question links to an RKP | `tested_rkp_id` mandatory |
| Every RKP must be tested | At least one question per RKP |

---

## 2. The Four Perspectives

### Legal — "What does the rule actually say?"
- Precise regulatory fact in a scenario (not "According to 14 CFR...").
- Distractors: real aviation items that sound plausible.

### Safety — "Beyond the rule, why does it matter?"
- **Second-order consequence.** NOT another legal question.
- Ask what the reg exists to prevent. "Beyond the regulatory violation..."

### Application — "Apply the rule to this concrete situation"
- Calculation or specific fact pattern. Student must *use* the rule, not recall it.

### Risk Management — the SJT
- "All options are legal — which is the safest decision?"
- Tests judgment / human factors. See §3.

---

## 3. The SJT Rules

```
OPTION A → "get_there_itis"   (chase the destination/schedule)
OPTION B → "macho"            (overconfidence)
OPTION C → "resignation"      (give up / cancel when middle path exists)
OPTION D → ✅ CORRECT         (active test + mitigation)
```

**Critical Rule: D is NEVER "cancel the flight."** Cancelling = resignation (C).
D is the **active professional middle path**: self-assessment/test + risk mitigation plan.

### SJT Quality Gate
- [ ] All four options legal/possible?
- [ ] D requires active judgment (test + mitigation)?
- [ ] A/B/C each embody a different hazardous attitude?
- [ ] A rote student could still pick wrong?

---

## 4. Difficulty Levers

1. **Plausible distractors only** — every wrong option = real student mistake
2. **No rote-recall-only** — test understanding, not trivia
3. **Second-order reasoning** — consequence of the consequence
4. **Scenario specificity** — real numbers, airports, timelines
5. **"Two right-looking answers" trap** — correct in another context, wrong here
6. **Rote necessary but not sufficient** — need fact AND judgment

---

## 5. Explanation Standard

Every `explanation` must: (1) teach the principle, (2) cite the authority (FAR + handbook),
(3) ground in real accident/enforcement data (real NTSB numbers, never invented).

`far_reference` = FAA regulations ONLY. Legal interpretations/NTSB → `explanation` prose.

---

## 6. JSON Schemas

### Quiz File Wrapper
```json
{
  "lesson_id": "PPL_PA_I_A_01",
  "title": "Privileges & Limitations",
  "questions": [ ... 8 question objects ... ]
}
```

### MCQ Fields
`id`, `perspective`, `question_type`, `tested_rkp_id`, `text`, `options` (4x label+text),
`correct_answer`, `explanation`, `far_reference`, `acs_element`

### SJT Additional Fields
`hazardous_attitude` on options A/B/C, `sjt_rationale`

---

## 7. Execution Pipeline

1. **Load RKP Manifest** — read `{lesson_id}_rkp.json`
2. **Plan Coverage** — map 8 questions to RKPs, ensure every RKP tested
3. **Author Questions** — scenario stem → correct answer → 3 distractors → explanation
4. **Pre-Ship Self-Check** (§9)
5. **Daniel CFI Review** — no question enters without explicit approval
6. **Write Quiz JSON** — save to `specialist_curriculum/quiz_banks/`
7. **Push to Firebase** — run `src/gcp/upload_quiz_banks.py`
8. **Push RKP Manifests** (if needed) — run `src/gcp/upload_manifests.py`

> [!IMPORTANT]
> **Claude-specific tooling note:** If `write_to_file` stalls on JSON, use Bash:
> ```bash
> cat > specialist_curriculum/quiz_banks/PPL_PA_II_A_01_quiz.json << 'EOF'
> { ... your JSON ... }
> EOF
> ```

---

## 8. Firebase Deployment

### Quiz Banks → Firestore
```bash
cd src/gcp && python upload_quiz_banks.py
```
- Database: `aviationchat-database`
- Collection: `quiz_banks`
- Doc ID: `{lesson_id}`
- Auth: `auth_keys/librarian-service-account.json`

### RKP Manifests → Firestore
```bash
cd src/gcp && python upload_manifests.py
```
- Collection: `rkp_manifests`

### Pre-Push Checklist
- [ ] Quiz passes pre-ship self-check
- [ ] Daniel has explicitly approved
- [ ] `lesson_id` present and matches filename
- [ ] Corresponding RKP manifest also pushed
- [ ] Service account key exists and is valid

---

## 9. Pre-Ship Self-Check

- [ ] Exactly 8 questions: 2L / 2S / 2A / 2RM
- [ ] RM questions are real SJTs (all-legal, A/B/C attitudes, D = active middle path)
- [ ] No obviously eliminable distractors
- [ ] Safety questions ask second-order consequences
- [ ] Every explanation: teaches why + cites FAR/handbook + real accident data
- [ ] Every `tested_rkp_id` points to a valid RKP
- [ ] Every RKP appears in at least one `tested_rkp_id`
- [ ] All options within 10% character length
- [ ] A rote student could still miss the SJTs and safety questions

---

## 10. Quiz Banks Needing Rewrite

Area I (`PPL_PA_I_*`) = gold standard, do NOT touch.

These 13 are sub-par and must be rewritten (never pushed to Firebase):

`PPL_PA_III_A_01`, `PPL_PA_III_A_02`, `PPL_PA_III_B_01`,
`PPL_PA_VI_B_01`, `PPL_PA_VI_B_02`, `PPL_PA_VI_B_03`,
`PPL_PA_VII_A_01`, `PPL_PA_VII_D_01`,
`PPL_PA_IX_B_01`, `PPL_PA_IX_C_01`,
`PPL_PA_XI_A_01`, `PPL_PA_XI_A_02`, `PPL_PA_XI_A_03`

---

## 11. Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|---|---|
| Obviously absurd distractors | Every distractor = real student mistake |
| Pure trivia recall | Scenario + "why/when/so what" |
| Safety = another legal question | Second-order consequence |
| SJT with illegal option | All four legal |
| SJT D = "cancel" | D = test + mitigation |
| Invented NTSB numbers | Real citations only |
| Correct answer much longer | All options within 10% length |

---

## 12. Gold Standards

- `specialist_curriculum/quiz_banks/PPL_PA_I_A_01_quiz.json` — original gold
- `specialist_curriculum/quiz_schema.md` — locked JSON schema
- `_01_My/instruction_docs/quiz_authoring_guide.md` — Daniel's quality bar
- `_01_My/project_context_prps/quiz_generator_prompt.md` — system prompt + 12 Lessons Learned
