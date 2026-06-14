# AviationChat — Admin Agent & Self-Improving Evolution Engine
## Technical Data Audit & Opportunity Assessment
### Prepared for External Consultant Review — May 2026

---

## 1. Executive Summary

AviationChat is an AI-powered private pilot ground school. Students learn through three pedagogical surfaces:

1. **Specialist (Text Chat)** — Expert Q&A with a 4-lane "Expert Witness" verification pipeline
2. **Socratic Teacher (Text)** — Guided discovery using 8 rotating pedagogical tools ("Strategy Roulette")
3. **Sully (Voice)** — Live voice CFI sessions via Gemini Live API with real-time evaluation

The **Admin Agent** is the async, fire-and-forget meta-grader. It runs after every session to evaluate student performance, update the student's cognitive profile, and advance mastery state. It is the **only component with write access** to the evaluation/grading layer — teaching agents are forbidden from grading.

**The goal of this research:** Identify what data we currently collect, what we could collect, and what will provide the highest ROI for making the Admin Agent a **self-improving evolution engine** — one that learns which teaching strategies work best and automatically optimizes pedagogy across the platform.

---

## 2. Current Architecture: The Three Data Silos

### 2.1 Firestore Collection Map

| Collection Path | What It Stores | Written By | Read By |
|---|---|---|---|
| `users/{uid}/sar_interactions/{auto_id}` | Per-turn Socratic telemetry (tool deployed, **tool-restructured tutor_question wording**, eval tag, confusion score, mercy data) | Specialist orchestrator | Admin Agent (future) |
| `users/{uid}/sully_sessions/{session_id}` | Full voice session telemetry + transcript with per-turn technique/hesitation/filler data | Sully WebSocket handler | Admin Agent |
| `users/{uid}/quiz_results/{quiz_id}` | Permanent quiz result with per-question detail (selected index, correct index, ACS key) | QuizService | Admin Agent, Study Context |
| `users/{uid}/quiz_tutor_results/{session_id}` | Quiz Tutor remediation session outcomes (per-question eval, **tool-restructured tutor_question used to unblock**, attempts to resolve, mercy triggers) | Quiz Tutor orchestrator | Admin Agent |
| `users/{uid}/specialist_chats/{session_id}` | Full Q&A conversation (max 50 messages per session) with verification stats, sources, ACS context | ChatHistoryService | Frontend (reload), Admin Agent (future) |
| `users/{uid}/learning_context/{lesson_id}` | Per-lesson accumulator: interactions, weak points, quiz history, citations | Multiple agents | All agents |
| `users/{uid}/acs_knowledge_ledger/{acs_code}` | Per-ACS mastery node: tool_affinity_weights, misconception_log, mastery_status | Admin Agent, Strategy Roulette | DossierContextBuilder |
| `users/{uid}/global_profile/singleton` | Learner identity: frustration tolerance, vocabulary level, affective state | Admin Agent, Onboarding | All agents |
| `users/{uid}/session_logs/{session_id}` | Session metadata: type, duration, ACS codes covered, mastery transitions | SessionLogger | Compliance export |
| `lessons/{lesson_id}` | Institutional memory: `top_3_global_traps` per lesson | Nightly Overseer (future) | Lesson Planner (Agent 1) |
| `dashboard_metadata/golden_candidates/{id}` | **NEW:** RKP Teaching Ledger nominations — `(acs_element_key, deployed_tool, tutor_question)` triples that met the breakthrough threshold and are pending CFI review | Nightly Overseer | Admin Dashboard, Golden RAG |

---

## 3. Detailed Audit: What We Collect Today

### 3.1 Socratic Text Sessions — SAR Telemetry

**Source:** [agent.py `_write_sar_telemetry()`](file:///c:/AGY-Projects/aviationChat-AGY/backend/agents/specialist/agent.py#L2621-L2678)

Every Socratic turn writes a document to `sar_interactions/` with:

| Field | Type | Description |
|---|---|---|
| `deployed_tool` | string | Which of the 8 Strategy Roulette tools was used (e.g., `tool_6_broken_machine`) |
| `tutor_question` | string | **NEW (Story 8.2):** The exact **tool-restructured** Socratic question — the reformulation Agent 2 generates when the Strategy Roulette deploys a teaching tool after `EVAL_INCORRECT`. This is NOT the initial lesson-plan question (Q1/Q2 from Agent 1). Captures the dynamic intervention *wording* that may have caused the breakthrough, not just the tool category. |
| `tutor_question_mode` | string | **NEW (Story 8.2):** `text` or `voice` — isolates text pipeline questions from Sully voice questions (different register and length constraints) |
| `acs_element_key` | string | **Story 8.1:** The specific ACS RKP being taught (e.g., `PA.I.A.K1`) — the atomic key linking this record to the RKP Teaching Ledger |
| `evaluation` | string | `EVAL_CORRECT`, `EVAL_PARTIAL`, `EVAL_INCORRECT`, `EVAL_RESOLVED`, `EVAL_MERCY`, `EVAL_CLOSE` |
| `confusion_score` | float | 0.0–1.0 per-turn confusion from Agent 2 |
| `cognitive_zone` | int | 1 (flow), 2 (productive struggle), 3 (frustration) |
| `response_length` | int | Character count of student's response |
| `mercy_deployed` | bool | Whether the mercy rule fired |
| `mercy_type` | string | `surrender`, `dynamic_tf`, `fallback_reveal`, `surrender_tf`, `quiz_tutor_tf` |
| `mercy_mcq_correct` | bool | Whether student got the mercy T/F question right |
| `surrender` | bool | Student explicitly gave up |
| `reward_status` | string | `"pending"` → `"scored"` once BipartiteRewardService processes |
| `reward_score` | float | Bipartite reward score (Story 8.1 — now actively scored via `BipartiteRewardService`) |

> [!IMPORTANT]
> **Story 8.1 Status Update:** The `reward_status` and `reward_score` fields are now **actively scored** by `BipartiteRewardService` (fire-and-forget after quiz completion). The `acs_element_key` field is also now populated (Story 8.1). The `tutor_question` and `tutor_question_mode` fields are the next enrichment targets (Story 8.2).

### 3.2 Sully Voice Sessions — Full Telemetry

**Source:** [sully_spike_websocket.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/routers/sully_spike_websocket.py#L1113-L1222)

At session close, a `SullySessionTelemetry` document is written with:

| Field | Type | Description |
|---|---|---|
| `technique_usage` | Dict[str, int] | **A/B testing data** — maps technique name → deployment count |
| `transcript` | List[SullyTranscriptEntry] | Full turn-by-turn transcript with per-turn metadata |
| Per student turn: `hesitation_ms` | int | Response latency in milliseconds |
| Per student turn: `pause_category` | string | From PauseTelemetryManager |
| Per student turn: `filler_word_count` | int | Linguistic fragility marker |
| Per Sully turn: `deployed_technique` | string | Which of the 12 voice techniques was used |
| Per Sully turn: `evaluation` | string | EVAL tag from `log_evaluation` tool call |
| `consequence_chains` | int | Number of consequence engine activations |
| `max_consequence_depth` | int | Deepest consequence chain reached |
| `override_count` | int | Native barge-in interruptions |

**Admin Agent grading output** ([SullyGradingResult](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/sully_grading.py#L95-L130)):

| Field | Type | Description |
|---|---|---|
| `technique_effectiveness` | Dict[str, str] | **Maps technique → "effective" / "partially_effective" / "ineffective"** |
| `fragile_knowledge_detected` | bool | Text-correct but voice-uncertain |
| `voice_confidence_score` | float | 0.0–1.0 overall oral delivery confidence |
| `weak_rkps` | List[str] | RKP titles where student showed weakness |
| `recommended_action` | enum | `advance_to_application` / `repeat_sully_session` / `review_lesson` |

> [!TIP]
> **Opportunity:** The `technique_effectiveness` field already captures per-technique A/B data from Sully. The Admin Agent grades each technique as effective/partially/ineffective. **This data is being written but never read back to influence future technique selection.** Closing this loop is a high-ROI opportunity.

### 3.3 Specialist Q&A Conversations

**Source:** [chat_history_service.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/services/chat_history_service.py)

Each Specialist session stores up to **50 messages** in `specialist_chats/{session_id}` with:

| Field | Type | Description |
|---|---|---|
| `content` | string | Full text of user question and assistant answer |
| `status` | string | `verified` — Expert Witness pipeline result |
| `intentMode` | string | Detected intent classification |
| `sources` | list | RAG citations from the Librarian (6-search dual-database) |
| `verificationStats` | dict | Reasoner verification metrics |
| `acsContext` | dict | Which ACS elements the response covers |
| `lessonCard` | dict | Associated lesson metadata |

> [!NOTE]
> **Finding:** These conversations are stored but **never analyzed by the Admin Agent**. The Admin Agent currently only grades Socratic and Sully sessions. Specialist Q&A is a large untapped data source — students often reveal misconceptions in their free-text questions that the Socratic path never surfaces.

### 3.4 Quiz Results & Quiz Tutor Remediation

**Source:** [quiz_service.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/services/quiz_service.py), [quiz_tutor_result.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/quiz_tutor_result.py)

| Collection | Key Fields | Purpose |
|---|---|---|
| `quiz_results/{quiz_id}` | `score`, `passed`, `attempt_number`, `reset_triggered`, per-question `selected_index`/`correct_index`/`acs_element_key` | Permanent quiz attempt record |
| `quiz_tutor_results/{session_id}` | `questions_reviewed`, `questions_mastered`, `aggregate_confusion_score`, per-question `eval_outcome`/`attempts_to_resolve`/`mercy_rule_triggered` | Remediation effectiveness |

### 3.5 ACS Knowledge Ledger — The Existing A/B Framework

**Source:** [cognitive_dossier.py `ACSKnowledgeNode`](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/cognitive_dossier.py#L156-L273)

This is the **existing but dormant A/B testing infrastructure** for Strategy Roulette:

```python
tool_affinity_weights: Dict[str, float] = {
    "tool_1_analogical": 0.125,      # Equal starting weights
    "tool_2_first_principles": 0.125,
    "tool_3_boundary": 0.125,
    "tool_4_contrasting_cases": 0.125,
    "tool_5_reverse_chaining": 0.125,
    "tool_6_broken_machine": 0.125,
    "tool_7_missing_link": 0.125,
    "tool_8_triage": 0.125,
}
```

These weights are described as **"Epsilon-greedy exploration weights for Strategy Roulette"** — but `StrategyRoulette.roll()` currently uses `random.choice()` and **completely ignores these weights**. The weights exist in the schema, are validated (must sum to 1.0), but are never read during tool selection.

> [!CAUTION]
> **Critical Gap:** The Strategy Roulette currently selects tools **uniformly at random** ([strategy_roulette.py L42](file:///c:/AGY-Projects/aviationChat-AGY/backend/services/strategy_roulette.py#L42)). The per-student, per-ACS `tool_affinity_weights` exist in the schema but are never consulted. This is the core mechanism the Evolution Engine needs to close.

---

## 4. What We Do NOT Collect (Gaps)

| Gap | Description | Value |
|---|---|---|
| **tutor_question Capture** | SAR records log WHICH tool was used but not WHAT the agent said. The exact tool-restructured question wording — the dynamic Socratic reformulation the agent generated when deploying a teaching tool (not the initial Q1/Q2) — is not stored. | **Critical** — without this, we know the strategy but not the execution. The RKP Teaching Ledger cannot be built. |
| **Specialist Q&A Analysis** | Admin Agent never reads `specialist_chats/` — free-text misconceptions are invisible | **High** — students reveal knowledge gaps in questions the Socratic path never tests |
| **Time-to-Resolution** | We store turn counts but not wall-clock seconds per Socratic node | **Medium** — would distinguish "fast correct" from "slow grind to correct" |
| **Tool Decay Curves** | No tracking of whether a tool's effectiveness changes as students advance through the curriculum | **High** — Analogical Bridging may work for early lessons but fail for IFR |
| **Cross-Surface Correlation** | No linking of Sully voice `technique_effectiveness` back to text `tool_affinity_weights` | **High** — 6 techniques overlap between text and voice |
| **Abandonment / Session Drop** | No tracking of when students close the app mid-session | **Medium** — predictive churn model |
| **Quiz Tutor → Quiz Retry Correlation** | `quiz_tutor_results` exist but are never correlated with the subsequent quiz retry result | **High** — "did the tutor actually help?" |
| **Golden RAG Injection** | Even once Golden Candidates are nominated, there is no mechanism to retrieve and inject proven questions into future Socratic sessions | **High** — the feedback loop is not closed until reuse is implemented |

---

## 5. The Self-Improving Loop: How It Should Work

The vision is a **three-phase epsilon-greedy optimization cycle**:

### Phase 1: Observe (Already Implemented)
- Socratic Teacher deploys a random tool → SAR telemetry records the tool + eval tag
- Sully deploys a technique → session telemetry records technique + per-turn eval
- Quiz service records pass/fail + per-question detail

### Phase 2: Correlate (NOT Implemented — The Critical Gap)
The Admin Agent needs to:
1. Read the SAR telemetry for a completed Socratic session
2. Wait for the subsequent quiz result on the same lesson
3. Compute the **bipartite reward**: Did Tool X lead to a quiz pass?
4. Write `reward_score` back to the SAR document (closing the `"pending"` loop)
5. Update `tool_affinity_weights` on the student's `ACSKnowledgeNode`

### Phase 3: Exploit + Explore (NOT Implemented)
Strategy Roulette needs to:
1. Read the student's `tool_affinity_weights` for the active ACS code
2. Use **epsilon-greedy selection**: 80% of the time, pick the highest-weighted tool; 20% of the time, explore a random alternative
3. Over time, the weights converge on the best tool *for this student* on *this concept*

### The "Macro" Loop (Institutional Learning)
Aggregate `tool_affinity_weights` across ALL students for a given ACS code:
- If 70% of students learn `PA.I.A.K1` best with `tool_6_broken_machine`, that becomes the **global default starting weight** for new students
- This is the Nightly Overseer's job — it reads aggregated data and writes to `lessons/{lesson_id}.top_3_global_traps`

---

## 6. Proposed A/B Testing Strategy

### 6.1 Text (Strategy Roulette) — 8 Tools

**Current state:** Random selection, no feedback loop.
**Proposed state:** Epsilon-greedy with bipartite reward.

```
Champion (80%): Use highest-weighted tool from tool_affinity_weights
Challenger A (10%): Random alternative tool
Challenger B (10%): Random alternative tool

After quiz result:
  → Pass: Increase deployed tool's weight by +Δ
  → Fail: Decrease deployed tool's weight by -Δ
  → Renormalize weights to sum to 1.0
```

### 6.2 Voice (Sully) — 12 Techniques

**Current state:** Gemini Live selects techniques autonomously, Admin Agent grades effectiveness post-session.
**Proposed state:** Feed `technique_effectiveness` results back into the system prompt for subsequent sessions.

The `SullyGradingResult.technique_effectiveness` already classifies each technique as `effective`/`partially_effective`/`ineffective`. This data could be:
1. Aggregated per-student per-ACS into a `voice_technique_affinity` map
2. Injected into Sully's system prompt as a directive: *"For this student, prefer consequence_engine (effective 3/3 sessions) over devils_advocate (ineffective 2/2 sessions)"*

### 6.3 Quiz Tutor — Remediation Effectiveness

**Current state:** Quiz Tutor reviews missed questions using Socratic method, results stored in `quiz_tutor_results/`.
**Proposed state:** Correlate `quiz_tutor_results` with subsequent quiz retry scores.

| Signal | Measurement |
|---|---|
| Tutor helped | Student passes quiz on next attempt after tutor session |
| Tutor failed | Student fails quiz again after tutor session |
| Tutor partially helped | Student improves score but still fails |

---

## 7. Data We Should Start Collecting

### 7.1 Immediate (Low Engineering Cost)
1. **Specialist Q&A misconception extraction** — Run Admin Agent grading on `specialist_chats/` conversations (same pattern as Socratic grading, different prompt)
2. **Wall-clock time per Socratic node** — Add `started_at` timestamp to SAR telemetry
3. **Session abandonment events** — Log when a student disconnects mid-Socratic or mid-Sully without completing

### 7.2 Medium-Term (Requires Schema Changes)
4. **Bipartite reward scoring** — Admin Agent reads SAR + quiz_results and writes `reward_score` back
5. **Tool affinity weight updates** — After bipartite scoring, update `acs_knowledge_ledger/{acs_code}.tool_affinity_weights`
6. **Voice technique affinity map** — New field on `ACSKnowledgeNode` for Sully technique preferences
7. **Quiz Tutor → Quiz Retry correlation** — Link `quiz_tutor_results` to subsequent `quiz_results` by `lesson_id` + `attempt_number`

### 7.3 Long-Term (Requires New Infrastructure)
8. **Golden Transcript collection** — Save high-scoring Socratic sessions as exemplars for vector-based recall
9. **Semantic error clustering** — Vector-embed wrong answers to auto-discover new curriculum traps
10. **Nightly Overseer batch job** — Aggregate per-student weights into global defaults + `top_3_global_traps`

---

## 8. Priority Ranking for Consultant Review

| Priority | Item | Why | Effort |
|---|---|---|---|
| **P0** | ~~Close the bipartite reward loop (SAR → Quiz → reward_score)~~ **✅ Done — Story 8.1** | BipartiteRewardService implemented. | Done |
| **P0** | Add `tutor_question` + `tutor_question_mode` to SAR telemetry | Without the exact tool-restructured question wording (the Strategy Roulette intervention, not the initial Q1/Q2), we know which strategy worked but not how to replicate it. This is the missing field for the RKP Teaching Ledger. | Low |
| **P0** | Make Strategy Roulette read `tool_affinity_weights` (epsilon-greedy) | The weights exist in the schema but are ignored. Flip the switch. | Low |
| **P1** | Nightly Overseer — Golden RAG Discovery Pipeline | Scans SARs, groups by `(acs_element_key, deployed_tool, tutor_question)`, nominates breakthrough fingerprints. Builds the RKP Teaching Ledger. | Medium |
| **P1** | CFI Review Gate for Golden Candidates | Human-in-the-loop before any proven question is injected into future sessions. Admin Dashboard integration. | Low |
| **P1** | Feed Sully `technique_effectiveness` back into system prompt | Data is already being written. Just read it and inject it. | Low |
| **P1** | Correlate Quiz Tutor results with quiz retry outcomes | "Did the remediation actually work?" — critical for proving tutor value. | Medium |
| **P1** | Prerequisite DAG & Pre-Bunking service (Story 4.20) | DAG data exists in curriculum_key.json but the service was never built. Proactive misconception clearing. | Medium |
| **P2** | Analyze Specialist Q&A conversations | Large untapped data source. Students reveal misconceptions in free-text. | Medium |
| **P2** | Nightly Overseer — `top_3_global_traps` aggregation job | Institutional learning across all students. Makes the platform smarter globally. | High |
| **P3** | Golden RAG Injection into Strategy Roulette | After Golden Candidates are approved, inject proven question phrasings as Socratic bias for future students on same RKP. | High |
| **P3** | Graph RAG for auto-discovered prerequisite edges | Let failure data reveal prerequisite relationships humans missed. | High |
| **P3** | Semantic error clustering | Vector-embed wrong answers to auto-discover new curriculum traps. | High |

---

## 9. Prerequisite DAG & Pre-Bunking (Exploration)

### 9.1 What Exists Today

The **Prerequisite DAG** is already partially built into the curriculum. Every lesson in [curriculum_key.json](file:///c:/AGY-Projects/aviationChat-AGY/backend/data/curriculum_key.json) has a `prerequisite_acs_nodes` array:

```json
{
  "lesson_id": "PPL_PA_I_C_01",
  "lesson_name": "Airspace Cloud Clearances",
  "prerequisite_acs_nodes": ["PA.I.B.K2"]
}
```

This data was hand-curated — 34 lessons each have manually-mapped prerequisite ACS codes. The idea: before teaching Cloud Clearances, the system should check if the student has a misconception about AGL/MSL altitude (PA.I.B.K2). If they do, the tutor clears it first.

**Story 4.20** ([story-4.20-prerequisite-dag-prebunking.md](file:///c:/AGY-Projects/aviationChat-AGY/_bmad/bmm/stories/story-4.20-prerequisite-dag-prebunking.md)) is fully specified but **has never been implemented**. Status: "Ready for Dev."

### 9.2 How Pre-Bunking Would Work

1. Student clicks "Teach Me" on Lesson X
2. Backend reads `curriculum_key.json[lesson_x].prerequisite_acs_nodes`
3. Queries the student's `ACSKnowledgeLedger` (Tier 2) for active misconceptions on those prerequisite codes
4. If misconceptions exist → Agent 1 receives a `[PRE-BUNK DIRECTIVE]` and inserts a **clearing node** BEFORE the 4 standard Socratic nodes
5. Student experiences it as the tutor "naturally remembering" — no clinical UI alert

> [!TIP]
> **The UX is critical:** Pre-bunking must feel like a natural conversational callback ("Before we get into Cloud Clearances, let me make sure we're on the same page about altitudes..."), NOT a diagnostic warning screen.

### 9.3 The Graph RAG Opportunity — Auto-Discovering Prerequisites

The V1 DAG is hand-curated (34 edges). But the Evolution Engine data could **auto-discover** prerequisite relationships that human CFIs missed:

**Signal:** If students who have a misconception on ACS code `A` consistently fail on ACS code `B`, that implies `A → B` is a prerequisite edge, even if no human wrote it down.

**How this could work:**
1. Admin Agent already writes `misconception_log` entries to `acs_knowledge_ledger/{acs_code}`
2. Quiz results capture per-question `acs_element_key` failures
3. A batch job correlates: "Students with active misconceptions on code X fail quizzes on code Y at a rate 3x higher than students without that misconception"
4. Statistically significant correlations become **auto-discovered prerequisite edges**
5. These edges feed back into the Pre-Bunking service — the DAG grows itself

**Graph RAG consideration:** This is where a graph database (Neo4j, or even Firestore with a graph-like collection) would be valuable. The prerequisite DAG is inherently a directed graph. Currently it's stored as a flat JSON array per lesson. As the DAG grows from 34 hand-curated edges to potentially hundreds of auto-discovered edges, querying "all transitive prerequisites for Lesson X" becomes a graph traversal problem.

| Approach | Pro | Con |
|---|---|---|
| **Keep it flat (JSON arrays)** | No new infra, already works | Can't express transitive dependencies, no cycle detection |
| **Firestore graph collection** | Stays in existing stack | Graph queries in Firestore are awkward (fan-out reads) |
| **Neo4j / Graph DB** | Native graph traversal, pattern matching | New infrastructure, new deployment, new cost |
| **Vertex AI Graph RAG** | Google-native, integrates with existing Vertex AI Search | Newer product, may be immature |

### 9.4 Pre-Bunking A/B Testing

Once Pre-Bunking is live, we should A/B test:

| Hypothesis | Measurement |
|---|---|
| Pre-bunking reduces quiz failure rate | Compare quiz pass rates: lessons WITH pre-bunk intervention vs. lessons WITHOUT |
| Pre-bunking is most effective for specific ACS codes | Track which prerequisite clearings lead to the highest quiz score lift |
| Pre-bunking order matters | When a student has misconceptions on 2+ prerequisites, does clearing the most-recent vs. most-confused-about misconception first lead to better outcomes? |
| Auto-discovered edges outperform hand-curated edges | Do statistically-discovered prerequisites predict failure better than CFI-curated ones? |

---

## 10. Key Questions for Consultant

1. **Reward Signal Design:** Should the bipartite reward be binary (pass/fail) or continuous (quiz score 0.0–1.0)? Should it decay over time (a tool that helped 6 months ago matters less than one that helped yesterday)?

2. **Epsilon-Greedy vs. Thompson Sampling:** Is epsilon-greedy (80/20 exploit/explore) the right bandit algorithm, or would Thompson Sampling (Bayesian posterior) converge faster given our relatively small per-student sample sizes?

3. **Cold Start Problem:** New students have uniform weights. How many interactions do we need before the weights become meaningful? Should we seed new students with the global aggregate weights?

4. **Cross-Surface Transfer:** If `tool_6_broken_machine` works well in text, does that predict `broken_machine` will work well in voice? Or are these independent signals?

5. **Confounding Variables:** A student who passes the quiz might have passed regardless of which tool was deployed. How do we isolate the tool's contribution from natural learning progression?

6. **Institutional vs. Individual:** When do we trust the per-student signal vs. the aggregate? If 90% of students learn best with Tool X but this student learns best with Tool Y, which wins?

7. **Data Volume:** With ~113 lessons and 8 tools, we need significant interaction volume to get statistically meaningful weight distributions. What's the minimum viable sample size per ACS code?

8. **Prerequisite DAG — Graph Infrastructure:** We currently have 34 hand-curated prerequisite edges stored as flat JSON arrays. If we want auto-discovered edges (potentially hundreds), should we invest in a graph database (Neo4j), use Vertex AI Graph RAG, or can we scale with Firestore + application-level graph traversal?

9. **Pre-Bunking — Causal vs. Correlational:** If students with misconception A fail on topic B, is that causal (A causes B failure) or correlational (both A and B are hard topics)? How do we design the experiment to establish causality before auto-injecting pre-bunk nodes?

10. **DAG Cycle Prevention:** Auto-discovered edges could create cycles (A→B→C→A). What guardrails should we build to prevent the system from creating circular prerequisite chains that trap students in infinite pre-bunk loops?

---

## 11. Appendix: File References

| Component | File |
|---|---|
| Admin Agent (grading logic) | [agent.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/agents/admin/agent.py) |
| Admin Agent (prompts) | [prompts.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/agents/admin/prompts.py) |
| Strategy Roulette (tool selection) | [strategy_roulette.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/services/strategy_roulette.py) |
| SAR Telemetry (schema) | [telemetry.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/telemetry.py) |
| Cognitive Dossier (ACS weights) | [cognitive_dossier.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/cognitive_dossier.py) |
| Sully Grading (voice eval) | [sully_grading.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/sully_grading.py) |
| Sully WebSocket (telemetry write) | [sully_spike_websocket.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/routers/sully_spike_websocket.py) |
| Quiz Service (scoring + persistence) | [quiz_service.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/services/quiz_service.py) |
| Quiz Result (permanent record) | [quiz_result_record.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/quiz_result_record.py) |
| Quiz Tutor Result (remediation) | [quiz_tutor_result.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/quiz_tutor_result.py) |
| Chat History (Specialist Q&A) | [chat_history_service.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/services/chat_history_service.py) |
| Learning Context Cache (LCC) | [learning_context.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/learning_context.py) |
| Session Logs (compliance) | [session_log.py](file:///c:/AGY-Projects/aviationChat-AGY/backend/schemas/session_log.py) |
| Curriculum Key (DAG data) | [curriculum_key.json](file:///c:/AGY-Projects/aviationChat-AGY/backend/data/curriculum_key.json) |
| Story 4.20 (Pre-Bunking spec) | [story-4.20](file:///c:/AGY-Projects/aviationChat-AGY/_bmad/bmm/stories/story-4.20-prerequisite-dag-prebunking.md) |
