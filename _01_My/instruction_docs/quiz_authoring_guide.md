---
title: "Quiz & RKP Authoring Guide — How to Write Hard, High-Signal Questions"
type: reference
date: 2026-06-15
audience: "The agent (and team) that authors RKP manifests + quiz banks"
companion: "rkp_creation_guide.md (the schema/mechanics). This guide is the QUALITY bar — how to make the questions actually hard and worth taking."
gold_standard: "The Area I bank (PPL_PA_I_*). The 13 new-lesson questions (III/VI/VII/IX/XI) are being rewritten and are NOT a reference."
---

# Quiz & RKP Authoring Guide — Writing Questions That Are Actually Hard

> **Why this exists.** The original design-session notes for our quiz system were lost, so this guide
> **reconstructs the standard from the gold-standard bank itself** — the Area I questions
> (`PPL_PA_I_*`). It tells the authoring agent how to write questions that *separate a pilot who
> understands from one who memorized*. **Do not model new questions on the 13 new-lesson questions —
> those are sub-par and being rewritten. The reference is Area I.**

> ### Note (2026-06-16): canonical bank location + citation verification
> Quiz banks are authored and maintained in **this pipeline repo** (`curriculum_components/quiz_banks/`),
> which is the **canonical** source the app repo syncs *from* (pipeline → app). When the app serves nothing
> for a lesson, check the drift: as of 2026-06-16 the pipeline copies already carry a `far_reference` on
> **every** question (zero nulls), while the app copies had `null`s — so the near-term task is **verifying**
> the existing pipeline citations are in-scope and syncing, not authoring new ones. Scope still matters: a
> precise-but-wrong reg (e.g. `14 CFR 23.2150`, a Part 23 *aircraft-certification* standard, on an
> *operating* question) is exactly the §5.4 trap — flag it for the CFI rather than shipping it.

---

## 0. Author from the RKP first (do this before you write a single question)

A quiz question is only fair if the fact needed to pick the correct answer is **actually taught in
the RKP it points to**. A student studies the RKPs, then takes the quiz — if you test something the
lesson never taught, you've blindsided them, and the 80% gate punishes them for *your* gap, not
theirs. So author **from** the RKP, never from your own training.

**The procedure (every bank starts here):**
1. **Read every RKP `knowledge` field in the lesson** — not the `lesson_overview`, the `knowledge`
   field. That is the source of truth the student learns from.
2. **Build a fact inventory** — list the testable claims actually present (the limits, the numbers,
   the named concepts, the consequences, the misconceptions).
3. **Write each question against a fact in that inventory.** In the question's `explanation`, you
   should be able to point to the RKP sentence that makes the correct answer learnable.
4. **If a hard question you want has no supporting fact → flag the RKP for enrichment, don't invent
   the test.** The fix for a thin RKP is a deeper RKP, never a question the lesson can't support.
   (This is the reverse-contract in `rkp_creation_guide.md` — testable facts must live in `knowledge`.)

> **Two-way contract.** Question → RKP: every correct answer traces to a sentence in its
> `tested_rkp_id` RKP. RKP → Question: if you want a second-order question (a cognitive mechanism, a
> consequence-of-the-consequence), the RKP `knowledge` must teach that second-order concept first.
> **Worked example (`PPL_PA_III_A_01`):** the safety question on *expectation bias* works because
> RKP_02's `knowledge` teaches "expectation bias" by name with the exact Runway-27 example — the
> question didn't reach beyond the lesson, it tested it. Contrast: a question whose answer lives only
> in the `lesson_overview` (not in any `knowledge` field) is reaching beyond what the student studied.

### The SJT exception (don't let strict tracing kill a good SJT)
Risk_management **SJTs test judgment** — the hazardous-attitudes / IMSAFE / ADM framework — which is
taught in the **Area I risk-management foundations**, not re-taught in every lesson. So an SJT's
`tested_rkp_id` anchors the **scenario domain** (e.g. lost-comm → the lost-comm RKP), while the
**judgment framework is assumed cross-lesson**. That's correct design. Trace an SJT's *scenario* to
the lesson's RKP; do **not** require the ADM vocabulary (get-there-itis, IMSAFE) to live in that
lesson's own RKPs.

---

## 1. The structural contract (non-negotiable)

| Rule | Value |
|---|---|
| Questions per lesson | **8** |
| Distribution | **2 legal · 2 safety · 2 application · 2 risk_management** |
| `risk_management` type | **SJT** (Situational Judgment Test) preferred; `mcq` only if SJT doesn't fit |
| Other three perspectives | `mcq` |
| Options | 4 (A–D) — one correct, three plausible |
| Pass threshold | **80%** (a student must nearly ace it — so every distractor must *earn* its place) |
| Every question links to an RKP | `tested_rkp_id` (the assessment→mastery loop depends on it) |

The 80% pass bar is the whole reason difficulty matters: if a question is guessable or trivial, it
inflates the score and the student "passes" without understanding. **Every distractor must be a
mistake a real student would actually make.**

---

## 2. The four perspectives — what each one is *for*

Each perspective tests a **different layer of knowing**. Authoring all four for one RKP forces the
student to know the rule, its consequence, its application, AND the judgment around it.

### Legal — "What does the rule actually say?"
Tests the precise regulatory fact. Frame it in a **scenario** (a ramp check, a logbook question), not
"According to 14 CFR 61.3…". Distractors are real aviation items that *sound* plausible.
> **Gold example (`PPL_PA_I_A_01`):** ramp-checked, you show your certificate + medical — what's the
> third required item? (Answer: government photo ID. Distractors: registration, logbook, flight-review
> endorsement — all real documents, none of which must be *on your person*.)

### Safety — "Beyond the rule, why does it matter?" (second-order consequence)
This is the perspective most authors get wrong by making it another legal question. **Safety asks for
the downstream real-world consequence** the reg exists to prevent.
> **Gold example (`PPL_PA_I_A_01`):** a pilot takes full payment for a sightseeing flight — *beyond*
> the 61.113 violation, what compounding safety risk? (Answer: it can **void the insurance**, leaving
> everyone financially exposed in a crash.) The stem literally says "Beyond the regulatory violation…".

### Application — "Apply the rule to *this* concrete situation"
Usually a **calculation or a specific fact pattern**. The student can't recall a sentence; they must
*use* the rule.
> **Gold example (`PPL_PA_I_A_01`):** 3 people, $300 total cost, friend offers to pay all of it — what's
> the max you can legally accept? (Answer: $200 = the two passengers' pro-rata share; you must pay your
> own $100. Distractors: $300, $150, $0 — each a specific misunderstanding of pro-rata sharing.)

### Risk Management — the SJT (its own section below)
"All options are legal — which is the **safest** decision?" Tests judgment / human factors, not rules.

---

## 3. The SJT — "no wrong answers, only a best answer" (the crown jewel)

**Every option is legal and possible; the student must choose the safest / most defensible aeronautical
decision.** It tests Aeronautical Decision Making (ADM) and the **five hazardous attitudes** — the thing
that actually kills pilots.

> ### ⚠️ Read this before you write a single SJT — the "always-D" trap
> An earlier version of this guide told you the correct answer is **always option D** ("D = the active
> middle path; D is never cancel"). **That is wrong, and it is the exact rule that made the old uploader
> reject 31 valid Area I banks.** It was over-fit from the *first three* Area I banks (`A_01`–`A_03`) and
> does not describe the rest of the gold standard. **Verified against the live Area I bank:** of ~68
> SJTs, only **6 have correct = D**; the correct answer is **`B` in the overwhelming majority**, with
> scattered `A` and `C`. There are **two legitimate SJT archetypes**, and the correct answer lands in
> **whatever slot is natural** — never a fixed position. What makes an SJT *valid* is **structure**, not
> the letter of the answer (§3.3).

### 3.1 Archetype A — Go/No-Go ADM SJT (correct answer = the active middle path)

Use this when the scenario is a **launch-or-continue decision** under temptation (marginal weather,
fatigue, a proficiency gap, schedule pressure). Three options each embody a hazardous attitude; the
correct option is an **active test + risk-mitigation** middle path — and in this archetype that path is
genuinely the safest, so it is the right answer regardless of which slot it sits in.

```
STEM:    A launch/continue scenario with time pressure or temptation.
         "All four actions below are legal. Which is the SAFEST aeronautical decision?"

THREE distractors → each a distinct hazardous_attitude (get_there_itis / macho / resignation / …)
ONE correct option → hazardous_attitude: null  → an ACTIVE test + a mitigation plan (NOT "just cancel")
sjt_rationale: Chain-of-Cues — name each distractor's attitude and why the active path is safest.
```

> **Gold example (`PPL_PA_I_A_01` Q007, 80 days no-fly but current):** correct = **D** — "Fly a few solo
> patterns this morning to shake off the rust, then honestly assess whether you're sharp enough." A
> *test* + an honest *self-assessment* — not "go" (get-there-itis) and not "cancel outright"
> (resignation). **`A_01`–`A_03` are the only Area I banks where the answer is D** — because they happen
> to be pure go/no-go scenarios.

In this archetype, **"cancel the flight outright" is usually the *resignation* trap, not the answer** —
the safe move is the active middle path (a self-assessment/objective test, *then* a mitigation). But that
is a fact about *this archetype's scenarios*, **not** a universal "D is always right" rule.

### 3.2 Archetype B — Legal / procedural-reasoning SJT (correct answer = the defensible synthesis)

Use this when the scenario asks **which course is legally/procedurally correct *and* safe** among four
options that are each superficially plausible. The correct option is the **defensible synthesis**; the
distractors are recognizable *rationalizations* (often `macho` "the rule doesn't really apply to me," or
`resignation` "treat a manageable situation as hopeless"). **The correct answer is whatever slot the
synthesis naturally falls in — Area I lands on `B` most of the time.**

> **Gold example (`PPL_PA_I_A_04` Q007, $600 to fly a colleague):** correct = **B** — "Accept a pro-rata
> fuel split only (not the $600), confirm a legitimate common purpose…". Here **D = "decline entirely" is
> the *resignation* trap (wrong answer)**, and A/C are `macho` rationalizations (take the $600; call it a
> "gift"). This is the proof that **"D is always the safe answer" is false** — in a legal-reasoning SJT, D
> can be the trap and B is the judgment.

### 3.3 The structural rule (what actually makes an SJT valid — both archetypes)

This is the bar the ingest schema cares about, and the bar you must hold:

- **Exactly one correct option.** The other three are each a recognizable error — a hazardous attitude
  where one fits, or a legal/procedural rationalization.
- **The correct option is NOT `hazardous_attitude`-tagged;** each of the three distractors **is** tagged
  (when the error is an attitude). `sjt_rationale` is present and walks option-by-option.
- **All four options are legal/possible** (if one is illegal, it's an MCQ in a costume).
- **Vary the correct slot across the bank.** Options are served **unshuffled** (`backend/routers/quiz.py`),
  so a bank where every SJT answers `D` is a giant answer-key tell. Match the gold standard's spread
  (mostly `B`, with `A`/`C`/`D` as the scenario dictates). **Never force a position.**

### The five hazardous attitudes (use the FAA's standard names)
`get_there_itis` (a.k.a. "get-home-itis") · `macho` · `resignation` · `impulsivity` · `invulnerability`.
Pick the three that genuinely fit the scenario's distractors — don't force the same three every time.

### SJT quality test — if any of these is false, it's not a real SJT
- [ ] Are **all four options actually legal/possible**? (If one is illegal, it's an MCQ wearing a costume.)
- [ ] Is there **exactly one correct option, and is it the only one with no `hazardous_attitude` tag**?
- [ ] Does **each distractor embody a recognizable, distinct error** (a hazardous attitude or a
      legal/procedural rationalization)?
- [ ] Is the correct answer in its **natural slot** (not forced to D), and does the bank's set of correct
      slots **vary** rather than always landing on one letter?
- [ ] Could a **rote student who memorized the reg still pick wrong**? (They should be able to — the
      trap is psychological, not factual.)

---

## 4. The difficulty levers (what separates "understands" from "memorized")

1. **Plausible distractors only.** Every wrong option must be a mistake a real student makes. If you
   can delete an option because it's obviously silly, the question is one option easier than it looks.
2. **No rote-recall-only.** "What is Vx?" is trivia. "On a hot/high day with an obstacle, why does the
   stated Vx still apply but your margin shrinks?" tests understanding.
3. **Second-order reasoning.** The safety perspective especially: ask for the *consequence of the
   consequence* (insurance voids → personal liability), not the rule.
4. **Scenario specificity.** Real numbers, real airports (KPDK→KTYS), a named passenger, a concrete
   timeline. Specificity removes hand-waving and forces a real decision.
5. **The "two right-looking answers" trap.** The best MCQs have a distractor that's *correct in a
   different context* — the student must catch the detail that makes it wrong *here*.
6. **Make rote knowledge necessary but not sufficient.** The student should need the fact AND the
   judgment to get it right.

---

## 5. The explanation standard (this is half the learning)

Every question's `explanation` must do three things — the gold bank does all three:

1. **Teach the principle**, not just "B is correct." Explain *why* the right answer is right and
   *why each tempting wrong answer fails*.
2. **Cite the authority** — the specific FAR + handbook chapter (`14 CFR 61.3(a)`, `FAA-H-8083-2A Ch 2`).
3. **Ground it in the real world** — and this is the gold bank's signature move: **cite actual accident
   / enforcement data.** Examples from the live bank: *"NTSB Safety Alert SA-019 (Reduced Proficiency)",
   "NTSB CAROL search: 'proficiency'+'currency'+'fatal' shows a repeated pattern", "FAA Order 2150.3C
   documents 61.3 as a top ramp-check enforcement citation."* This turns a quiz answer into a reason to
   care. **Use real, verifiable references — never invent an NTSB number or accident.**
4. **Cite within scope — a reg is only authority where it applies.** Citing a *real* reg for the
   *wrong* situation is as wrong as inventing one, and harder to catch. **Worked example:** VFR
   lost-comm is **NOT 14 CFR 91.185** — that section is titled *"IFR operations: Two-way radio
   communications failure"* and governs only aircraft operating **under IFR**. For a VFR flight, cite
   **91.126 / 91.127 / 91.129** (comm at non-towered / Class D-C airports) and **light-gun signals
   (AIM 4-3-13)**; squawk 7600 is AIM guidance, not a FAR. Before shipping, **verify every
   exact-number reference** (NTSB `SA-xxx`, `SAFO xxxxx`, Safety Study `SS-xx/xx`) actually resolves
   to the document you claim, and **replace any "CAROL search: 'x'+'y'" string with a named
   accident/report.** A precise-but-wrong citation is the most dangerous kind — it *looks*
   authoritative.

For SJTs, also write `sjt_rationale` — the **Chain-of-Cues**: walk option-by-option naming each
distractor's error (the hazardous attitude or rationalization) and explaining why the correct option
beats all three — wherever that correct option sits (§3.3, not forced to D).

---

## 6. RKPs feed the questions — author them to be testable

A quiz can only be as good as the RKP it tests. When writing the `knowledge` field of an RKP:
- Make it **factually complete and specific** (the numbers, the limits, the exceptions) — vague
  knowledge produces vague questions.
- Capture the **"why"** and the **common misconception** — that misconception becomes your best
  distractor.
- Note the **real-world consequence** — that becomes your safety-perspective question and your
  explanation's accident grounding.
- Keep `far_references` and document-level `bridge_keys` accurate (see `bridge_key_guide.md`) — the
  question's `far_reference` should trace to them.

> A good test while authoring an RKP: *"What are the three ways a student could get this wrong on a
> checkride?"* Each wrong way is a distractor; the right way is the answer.

---

## 7. Anti-patterns — reject any question that does these

| Anti-pattern | Why it's bad | Fix |
|---|---|---|
| Distractors that are obviously absurd | Turns a 4-option into a 2-option | Every distractor = a real student mistake |
| Pure trivia / definition recall | Tests memory, not understanding | Put it in a scenario; ask "why/when/so what" |
| "Safety" question that's just another legal question | Wastes the perspective | Ask the *second-order consequence* |
| SJT where one option is actually illegal | It's not an SJT | All four must be legal; the choice is *safest* |
| SJT correct answer forced to a fixed slot (always "D") | Answer-key tell (options served unshuffled); over-fits one archetype | Put the answer in its natural slot; vary across the bank (gold standard is mostly B) — §3.3 |
| Go/No-Go SJT where the "answer" is just "cancel / don't fly" | In a launch decision that's the *resignation* trap, not judgment | Correct = active test + mitigation middle path (Archetype A, §3.1) — but don't generalize "cancel is always wrong" to legal-reasoning SJTs |
| Invented references / fake NTSB numbers | Destroys trust + is unverifiable | Cite real FARs/handbooks/accident data only |
| Real reg cited outside its scope (e.g. 91.185 for VFR lost-comm) | Authoritative-looking but wrong; a DPE busts it | Cite the reg that governs *this* situation; verify scope |
| Answer that's only in the `lesson_overview`, not any RKP `knowledge` | Student studied the RKPs and can't answer it | Trace to a `knowledge` fact, or enrich the RKP (§0) |
| Two options both fully correct | Ambiguous; student guesses | Exactly one correct; distractors wrong *here* |

---

## 8. Fill-in templates

**MCQ (legal / safety / application):**
```json
{
  "id": "PPL_PA_<AREA>_<TASK>_<SEQ>_Q00N",
  "perspective": "safety",
  "question_type": "mcq",
  "tested_rkp_id": "RKP_0N",
  "text": "<scenario stem that forces the concept; for 'safety' ask the second-order consequence>",
  "options": [
    {"label": "A", "text": "<plausible mistake>"},
    {"label": "B", "text": "<the correct, non-obvious answer>"},
    {"label": "C", "text": "<correct-in-another-context distractor>"},
    {"label": "D", "text": "<a real misconception>"}
  ],
  "correct_answer": "B",
  "explanation": "<why B; why A/C/D fail; FAR + handbook ch; real accident/enforcement data>",
  "far_reference": "14 CFR ...",
  "acs_element": "PA.<AREA>.<TASK>.<CODE>"
}
```

**SJT (risk_management)** — the correct option carries **no** `hazardous_attitude`; the three distractors
each carry one. **Put the correct option in its natural slot and vary it across the bank — do NOT force
"D" (§3.3).** Below the correct answer is `B`, matching the gold-standard majority:
```json
{
  "id": "PPL_PA_<AREA>_<TASK>_<SEQ>_Q007",
  "perspective": "risk_management",
  "question_type": "sjt",
  "tested_rkp_id": "RKP_0N",
  "text": "<specific scenario with temptation/pressure>. All four actions below are legal. Which is the SAFEST / most defensible aeronautical decision?",
  "options": [
    {"label": "A", "text": "<a rationalization>", "hazardous_attitude": "macho"},
    {"label": "B", "text": "<the correct, defensible synthesis OR the active test + mitigation>"},
    {"label": "C", "text": "<chase the goal>", "hazardous_attitude": "get_there_itis"},
    {"label": "D", "text": "<give up / decline outright when a managed path exists>", "hazardous_attitude": "resignation"}
  ],
  "correct_answer": "B",
  "sjt_rationale": "<Chain-of-Cues: name each distractor's error; why the correct option beats all three>",
  "explanation": "<the ADM/legal principle + FAA-H-8083-2A ch (or the governing reg) + real accident pattern>",
  "far_reference": "14 CFR ...",
  "acs_element": "PA.<AREA>.<TASK>.<CODE>"
}
```
> **Archetype A (go/no-go):** the correct option is the *active test + mitigation* middle path.
> **Archetype B (legal/procedural):** the correct option is the *defensible synthesis*; "decline/cancel
> entirely" is often the resignation distractor. Either way the slot is natural, not fixed — see §3.

---

## 9. Pre-ship self-check (run on every 8-question bank)

- [ ] Exactly 8 questions: 2 legal, 2 safety, 2 application, 2 risk_management.
- [ ] The 2 risk_management are real SJTs: all four options legal; exactly one correct option and it is
      the **only** one with no `hazardous_attitude`; each distractor is a distinct, recognizable error.
- [ ] The correct SJT answer is in its **natural slot, not forced to D**, and across the bank the correct
      slots **vary** (don't all land on one letter — options are served unshuffled). §3.3
- [ ] No distractor is obviously eliminable; each is a real student mistake.
- [ ] Each "safety" question asks a second-order consequence, not a restated rule.
- [ ] Every `explanation` teaches the why + cites a real FAR/handbook + real accident/enforcement data
      (no invented references).
- [ ] Every correct answer traces to a fact in its `tested_rkp_id` RKP's `knowledge` field — **SJTs
      excepted** (their ADM judgment draws on the Area I risk foundations, not this lesson's RKPs).
- [ ] No citation is used outside its scope (e.g. 91.185 is IFR-only); every exact-number reference
      (`SA-xxx`, `SAFO`, `SS-xx/xx`) is verified, with no "CAROL search" string standing in for a citation.
- [ ] A rote student who memorized the reg could *still* miss the SJTs and the safety questions.

> If you can't honestly check the last box, the bank is too easy — a 4× retry student will pass on
> memory alone, and the 80% gate means nothing.
