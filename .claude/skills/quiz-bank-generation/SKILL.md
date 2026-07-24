---
name: quiz-bank-generation
description: >
  Skill for creating 8-question quiz banks grounded in RKP manifests. Covers the
  4-perspective structure (Legal/Safety/Application/Risk Management), SJT authoring
  rules, difficulty levers, explanation standards, and Firebase deployment.
  Activates when an RKP manifest is ready and Daniel requests quiz generation.
  Area I (PPL_PA_I_*) is the style reference; all 48 banks are verified to standard (2026-06-19).
---

# Quiz Bank Generation Skill

> **Owner:** Woz (Agent) — generates quiz banks from completed RKP manifests.
> **Trigger:** An RKP manifest exists and Daniel requests quiz creation.
> **Output:** `{lesson_id}_quiz.json` in `curriculum_components/quiz_banks/` + pushed to Firebase.
> **Gold Standard (style reference):** Area I quiz banks (`PPL_PA_I_*`). All 48 banks verified to standard (2026-06-19).

---

## 1. The Structural Contract (Non-Negotiable)

| Rule | Value |
|---|---|
| Questions per lesson | **8** |
| Distribution | **2 legal · 2 safety · 2 application · 2 risk_management** |
| `risk_management` type | **SJT** preferred; `mcq` only if SJT doesn't fit |
| Options | 4 (A–D) — one correct, three plausible |
| Answer key balance | Per bank exactly **{A,A,B,B,C,C,D,D}** — no positional meaning (SOP §6; enforced by `src/tests/test_answer_distribution.py`) |
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

Four options = **three hazardous-attitude paths + one correct active middle path**. The correct
option's LETTER comes from the bank's balanced key (§1) — **attitude never maps to a letter
position**. (The old "A=get-there-itis … D=correct" grid is retired, 2026-07-23; it produced a
positional skew students could exploit. `hazardous_attitude` tags travel with the option text,
wherever it sits.)

- The three wrong paths each embody a **different** hazardous attitude — `get_there_itis` (chase
  the destination/schedule), `macho` (overconfidence), `resignation` (give up when a middle path
  exists) — tagged via `hazardous_attitude`; the correct option carries `hazardous_attitude: null`.
- **Critical Rule: the correct path is NEVER "cancel the flight."** Cancelling = resignation.
  Correct = the **active professional middle path**: self-assessment/test + risk mitigation plan.

### SJT Quality Gate
- [ ] All four options legal/possible?
- [ ] Correct option requires active judgment (test + mitigation)?
- [ ] The three wrong options each embody a different hazardous attitude?
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

**Feedback prose (`explanation` + `sjt_rationale`) is LETTER-FREE** — never "Option A", "choice
B", "(C)"; name the option's *content* or the *behavior* it represents ("The 'gift' defense is
explicitly rejected…", "Delegating a PIC responsibility is a Macho pattern…"). Proper aviation
names ("Class B airspace", "A&P", "W&B") are fine. Why: letter-free prose survives any re-letter;
letter-anchored prose lies to students the moment options move. (SOP §6; lint in
`src/tests/test_answer_distribution.py`.)

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

0. **Run the `faa-grounding-gate` skill — MANDATORY.** Every stem, option, explanation, and
   `far_reference` must trace to an ACS/FAA source document on disk; NTSB/accident figures must be
   real. Never author a regulatory claim from memory — unverifiable ⇒ flag for Daniel.
0b. **Read references** — before authoring, read `docs/instruction_docs/quiz_authoring_guide.md` §0
   ("Author from the RKP first") and the target lesson's RKP `knowledge` fields in
   `curriculum_components/rkp_manifests/{lesson_id}_rkp.json`. Every question must trace to a fact taught
   in an RKP; if it can't, flag the RKP for enrichment instead of inventing the test.
1. **Load RKP Manifest** — read `{lesson_id}_rkp.json`
2. **Plan Coverage** — map 8 questions to RKPs, ensure every RKP tested
3. **Author Questions** — scenario stem → correct answer → 3 distractors → explanation
4. **Pre-Ship Self-Check** (§9)
5. **Daniel CFI Review** — no question enters without explicit approval
6. **Write Quiz JSON** — save to `curriculum_components/quiz_banks/`
7. **Push to Firebase** — `python src/gcp/ingest_quiz_banks.py` (dry run), then `--execute`. Writes the
   `quiz_banks/{lesson_id}/questions/{q}` subcollection the app reads (never the old `upload_quiz_banks.py`).
8. **Push RKP Manifests** (if needed) — `python src/gcp/upload_manifests.py --execute`

> [!IMPORTANT]
> **Claude-specific tooling note:** If `write_to_file` stalls on JSON, use Bash:
> ```bash
> cat > curriculum_components/quiz_banks/PPL_PA_II_A_01_quiz.json << 'EOF'
> { ... your JSON ... }
> EOF
> ```

---

## 8. Firebase Deployment

### Quiz Banks → Firestore
```bash
python src/gcp/ingest_quiz_banks.py            # dry run (validates, mutates nothing)
python src/gcp/ingest_quiz_banks.py --execute  # writes to Firestore
```
- Database: `aviationchat-database`
- Target: `quiz_banks/{lesson_id}/questions/{q}` **subcollection** (8 docs/lesson — the path the app reads)
- Write: validate → merge-upsert by question id + `seen_by`/`last_seen_at`; gated behind `--execute`
- Auth: `auth_keys/service-account.json` (resolved via `config.py`)

### RKP Manifests → Firestore
```bash
python src/gcp/upload_manifests.py --execute
```
- Collection: `rkp_manifests` (flat docs, one per lesson)

### Pre-Push Checklist
- [ ] Quiz passes pre-ship self-check
- [ ] Daniel has explicitly approved
- [ ] `lesson_id` present and matches filename
- [ ] Corresponding RKP manifest also pushed
- [ ] Service account key exists and is valid

---

## 9. Pre-Ship Self-Check

- [ ] Exactly 8 questions: 2L / 2S / 2A / 2RM
- [ ] Correct answers land exactly on {A,A,B,B,C,C,D,D} — no positional pattern
- [ ] No option-letter references in `explanation`/`sjt_rationale` (letter-free prose)
- [ ] RM questions are real SJTs (all-legal; three distinct hazardous attitudes; correct = active middle path, letter per the balanced key)
- [ ] No obviously eliminable distractors
- [ ] Safety questions ask second-order consequences
- [ ] Every explanation: teaches why + cites FAR/handbook + real accident data
- [ ] Every `tested_rkp_id` points to a valid RKP
- [ ] Every RKP appears in at least one `tested_rkp_id`
- [ ] All options within 10% character length
- [ ] A rote student could still miss the SJTs and safety questions

---

## 10. Bank Status

All **48** quiz banks (Area I plus Areas III/VI/VII/IX/XI) are **verified to standard** (2026-06-19) and
deployed. 2026-07-23 (story 6-3): answer keys re-lettered to the balanced {A,A,B,B,C,C,D,D} key and all
feedback prose re-anchored letter-free. Use the Area I banks (`PPL_PA_I_*`) as the **style reference** for new lessons.

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
| Any regulatory claim written from memory | Read the source PDF first (`faa-grounding-gate`) |
| Correct answer much longer | All options within 10% length |
| SJT correct answer always at D (or any positional pattern) | Letter follows the bank's balanced {A,A,B,B,C,C,D,D} key |
| "Option A is wrong because…" in feedback prose | Letter-free: name the content/behavior (SOP §6) |

---

## 12. Gold Standards

- `curriculum_components/quiz_banks/PPL_PA_I_A_01_quiz.json` — original gold
- `curriculum_components/quiz_schema.md` — locked JSON schema
- `docs/instruction_docs/quiz_authoring_guide.md` — Daniel's quality bar
- `docs/project_context_prps/quiz_generator_prompt.md` — system prompt + 12 Lessons Learned
