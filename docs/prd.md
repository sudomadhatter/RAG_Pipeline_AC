---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish']
classification:
  projectType: 'Web App (SaaS/PWA)'
  domain: 'Aviation EdTech'
  complexity: 'High'
  projectContext: 'Brownfield'
inputDocuments: ['c:/AGY-Projects/aviationChat-AGY/_01_My/Docs/aviationchat_mission_statement',
'c:/AGY-Projects/aviationChat-AGY/frontend/README.md',
'c:/AGY-Projects/aviationChat-AGY/_bmad-output/planning-artifacts/product-brief-aviationChat-AGY-2026-02-10.md']
documentCounts:
  briefCount: 1
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 2
workflowType: 'prd'
---

# Product Requirements Document - aviationChat-AGY

**Author:** Daniel
**Date:** 2026-02-10

## Success Criteria

### User Success

*   **The "Confidence" Metric:** Users report feeling "ahead of the airplane" during their oral exam, specifically citing the ability to reason through regulations rather than just memorizing answers.
*   **The "North Star":** **Completion Rate.** A user is successful when they log **100% ACS Application-Mastery** across the 11 study areas and unlock the DPE Voice Agent (Igor).
*   **Emotional "Aha!" Moment:** The moment a user sees the Specialist answer from memory and then successfully verifies it against a specific FAR/AIM citation in real-time, building trust that differs from a standard search engine.
*   **Study Consistency:** Users engage in daily active study sessions averaging **45 minutes**, validating the "1 hour a day to stay ready" value proposition.
*   **Retention Rate:** >85% accuracy on "Review" items (expired topics), validating the spacing effect.

### Business Success

*   **Launch Timeline:** Transform the "Lean Full App" into a production-ready deployable via Replit/GCP within **2 months**.
*   **Beta Validation:** Acquire **50+ active beta users** from the Flight Club partner community with activity spanning > 2 weeks.
*   **Commercial Validation:** Convert the initial interested **Flight School** from a "demo viewer" to a "paid institutional customer" based on the beta results.
*   **Beta Feedback Score:** Achieve a **4.5/5 star rating** average from Flight Club testers.

### Technical Success

*   **Regulatory Accuracy (CRITICAL):** **99% accuracy rate** on regulatory questions. Given the safety implications of aviation training, hallucination on FARs is a critical failure mode. The dual-store "Expert Witness" architecture is the primary control for this metric.
*   **Voice Latency:** End-to-end voice response latency **< 800ms** to maintain conversational flow with the AI instructors (Sully/Igor).
*   **System Stability:** The verification swarm must operate reliably, handling parallel research agent execution without hanging or timing out the user session.
*   **Hallucination Rate:** 0% on cited regulations. Every regulation cited must have a valid "Bridge Key" link to an actual FAA document.

### Measurable Outcomes

1.  **Safety:** 99% verified accuracy on all regulatory citations displayed to students.
2.  **Retention:** 80% of active users reach the 60% ACS completion milestone (DPE Unlock).
3.  **Engagement:** Daily active users spend an average of 45+ minutes in the session.

## Product Scope

### Lean Full App (V1.0 Launch Scope)

This is **not an MVP**; it is a production-quality "Lean Full App" designed to deliver complete value for the core PPL use case.

**1. The "Expert Witness" Text Tutor (Talker-Thinker Pattern)**
*   **"Talker" (Fast Answer — Lane 1):** The Specialist Agent quickly retrieves from Curriculum DB1 and streams an initial answer, like a real CFI answering from memory.
*   **"Thinker" (Deep Verification — Lane 2):** In parallel, the Verification Swarm searches all official FAA documents (DB2), then either confirms the Talker's answer with a ✓ checkmark, corrects any inaccuracies by editing the original text, or expands on the quick answer with additional regulatory context. This mirrors how a real CFI teaches: answer from memory first, then look up the reg to verify and expand.
*   **Socratic Teacher (Sub-Agent):** Reads the full RAG pull from the Thinker's cache, gives a quick explanation of the topic, then immediately jumps into targeted Socratic questions to help the student learn the material. Routes any new regulatory claims through the Verification Swarm before display. All agents in the stack share a common **Learning Context Cache** (see FR23).
*   **"Living Text" UI:** Real-time transition from initial Talker answer to Thinker-verified citation.

**2. The Pedagogical Architecture ("The Mastery Pipeline")**
*   **Phase 1: SEEN (Exposure):** Initial Specialist answer + Socratic Teacher interaction. Teacher does NOT grade — just teaches. SEEN is the only progress unlocked at this stage.
*   **Phase 2: ROTE (Factual Retention):** Text-based rote quiz (multiple choice). Passing score of **80%** unlocks ROTE level. Expires in **14 Days**. Upon quiz completion, the **TA Agent** compiles all context (Specialist interaction, Socratic chat, quiz results) into a teaching script for the Voice Instructor.
*   **Phase 3: APPLICATION (Scenario Mastery):** Voice-based Socratic session via Sully (CFI Voice Agent). Sully follows the TA-generated teaching script. The full voice transcript is sent to the **Admin Agent** for grading — Sully does NOT grade, only teaches. Admin Agent updates mastery to APPLICATION upon satisfactory performance. Expires in **21 Days**.
*   **Phase 4: MASTERED (Checkride):** Igor (DPE Voice Agent) conducts an adversarial mock oral exam. Full transcript sent to **Admin Agent** for final grading. Passing = MASTERED.
*   **Decay Logic Engine:** Strict expiration timers force automatic review before checkride (50/50 split: review expired + new discovery).

**3. Voice Agents (The "Swarm" Personality Layer)**
*   **"Sully" (CFI Voice Agent):** Application-level coaching voice mode. Patient, encouraging. Follows TA-generated teaching scripts. Does NOT grade — the Admin Agent grades from the full transcript.
*   **"Igor" (DPE Voice Agent):** Mock checkride examiner voice mode. Unlocks when the student reaches **60% overall ACS completion** (calculated as: ROTE = 50% per topic, APPLICATION = 100% per topic). Adversarial, stress-inducing — borderline mean. Follows pre-made question scripts, but interactions/responses are entirely his own. Challenges correct answers with "are you sure?" Also available in **untracked practice mode** (no mastery updates) so students can experience how unprepared they are.
*   **Admin Agent:** Receives full voice transcripts from Sully and Igor sessions. Grades performance, updates mastery levels (APPLICATION and MASTERED respectively). The single authority for voice-based mastery transitions.
*   **STT/TTS Pipeline:** Real-time voice interaction with aviation-specific vocabulary tuning.

**4. Curriculum & Progress System**
*   **ACS State Machine:** Full PPL ACS coverage (11 Areas).
*   **Dashboard:** Visual progress tracking (Area % Completion).
*   **Resource Hub:** Curated FAA links + embedded YouTube videos.

**5. User System**
*   **Onboarding:** Chat-based profile creation (Mrs. Coleman).
*   **Auth/Data:** Secure login, persistent history, cross-device sync.

### Growth Features (Post-Launch V1.1+)

*   **Instructor Dashboards:** Administrative view for Flight Schools to track student progress rosters.
*   **Advanced Psychometrics:** VAD-based confidence scoring to identify student hesitation.
*   **Content Expansion:** Support for Instrument Rating (IR) and Commercial Pilot (CPL) curriculums.
*   **Creator Economy:** Revenue-sharing marketplace for CFI content creators.

### Vision (Future)

*   **Full Pilot Career Companion:** A complete AI training ecosystem that supports a pilot from their first discovery flight through their ATP certification.
*   **Institutional Scale:** Backend integration with major Part 141 Flight Schools via API access and roster management.

## User Journeys

### Journey 1: The "Panic Study" Session (Primary User - Alex)

**Persona:** Alex (32), Part 61 Student, Checkride in 60 days.
**Goal:** Verify a confusing regulatory concept he just argued with his CFI about.

1.  **The Prompt:** He types: *"Can I legally change the tire on my Cessna 172 as a private pilot? My CFI said maybe not."*
2.  **The Specialist Response (Lane 1):** Instantly, the Specialist responds: *"Yes, you can. Preventive maintenance is defined in FAR Part 43, Appendix A, Graph C. Item 1 covers tires."*
3.  **The Verification (Lane 2):** As he reads, a "Verifying..." badge pulses. A second later, it turns green: *Verified against 14 CFR Part 43 App A (c)(1)*. The actual text of the regulation appears in a collapsable citation block.
4.  **The Socratic Pivot:** Alex feels relieved. But then the system pivots: *"Since you're looking at preventive maintenance, Alex, what specific entry must you make in the logbook after you change that tire?"*
5.  **The Struggle:** Alex pauses. *"Uh, just the date and what I did?"*
6.  **The Coaching:** The system gently corrects: *"Almost. You also need your signature and certificate number. Why is the signature critical for airworthiness responsibility?"*
7.  **Resolution:** Alex realizes he would have missed that on the checkride. The system prompts: *"Ready to lock this in?"* Alex accepts the **Mastery Quiz**, scores 100%, and the system signs off the **"Airworthiness Requirements" [Task PA.I.B]** on his dashboard. He closes the laptop feeling genuinely "checkride ready" for that topic.

### Journey 2: The "Gap Filler" (Primary User - Maria)

**Persona:** Maria (21), Part 141 Student.
**Goal:** Identify and fix weak spots before her End of Course stage check.

1.  **The Nudge:** The dashboard highlights: *"Recommended: Finish Microbursts (PA.II.C) to unlock Igor."* She sighs and clicks "Start Lesson."
2.  **The Interaction:** Instead of a video, Sully (Voice Agent) speaks: *"Maria, you're on final approach and you see a sudden increase in airspeed followed by a sharp drop. What's happening?"*
3.  **The Mistake:** Maria says, *"Wind shear?"*
4.  **The Correction:** Sully: *"Technically yes, but be more specific. That's the signature of a microburst encounter. What determines if you go around or try to ride it out?"*
5.  **The 'Aha':** Maria laughs, *"Never ride it out. Go around immediately."*
6.  **The Upsell:** Sully confirms: *"Correct. That concludes this session."* as the voice session ends, her dashboard updates. A notification badge appears: **"Weather Progress: 55%. 2 more tasks to unlock Igor."** The drawer slides open, showing exactly which tasks remain to unlock the DPE agent.
7.  **Resolution:** The gamification hooks her. She pushes through one more topic just to see the progress bar move.

### Journey 3: The "Resume State" (Primary User - Tom)

**Persona:** Tom (47), Weekend Warrior.
**Goal:** Pick up exactly where he left off 2 weeks ago.

1.  **The Welcome:** Captain Vibe greetings him: *"Welcome back, Tom! Last time we were talking about Class E airspace weather minimums. You got stuck on the 'above 10,000 feet' rule. Want to tackle that?"*
2.  **The Relief:** Tom exhales. He doesn't have to decide what to study. *"Yeah, let's do it."*
3.  **The Quick Win:** The system throws a rapid-fire quiz question. Tom gets it right.
4.  **The Progress:** *"Nice. That closes out Class E. You're 10% closer to your PPL oral than you were 5 minutes ago."*
5.  **Resolution:** Tom only spends 15 minutes, but he leaves feeling like a pilot, not a dropout.

### Journey 4: The Admin/CFI (Secondary User - Institutional)

**Persona:** Captain Miller, Chief Instructor at "Flight Club" flight school.
**Goal:** Monitor student engagement and identify at-risk students.

1.  **The Overview:** He sees a roster of his 5 active PPL students.
2.  **The Alert:** A red indicator sits next to "David." The insight text says: *"David has attempted 'Cross Country Planning' quizzes 5 times with <50% accuracy. Hesitation detected in voice responses."*
3.  **The Action:** Miller clicks into David's profile. He sees the chat logs where David consistently confuses True vs. Magnetic course.
4.  **The Intervention:** Miller texts David: *"Hey, bring your plotter today. We're going to hit magnetic variation on the ground before we fly."*
5.  **Resolution:** AviationChat acted as an early warning radar, allowing Miller to fix a knowledge gap before it wasted expensive flight time.

## Domain-Specific Requirements

### Compliance & Regulatory (Aviation EdTech)

*   **Mandatory Training Logs:** The system MUST strictly log study session duration, exact topics covered (ACS Codes), and quiz performance.
    *   *Rationale:* Part 141 Flight Schools require verified "Ground Training" hours. This log serves as the legal proof of instruction for the school's records.
*   **Operational Scope:** The system must be explicitly positioned as "Ground School / Oral Prep Only."
    *   *Constraint:* It must NOT provide "flight planning" or "operational decision support" (e.g., weather briefings for an actual flight) to avoid liability as an EFB (Electronic Flight Bag).

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. The "Expert Witness" Architecture (Compliance-Grade AI)**
*   **Dual-Loop Verification:** Most AI chat apps are single-loop. AviationChat differentiates by splitting "conversational speed" (Specialist) from "regulatory truth" (Verifier Swarm).
*   **The "Living Text" UI:** The interface morphs from a fast answer to a verified citation in real-time, building trust.
*   **Citation-First UX:** Unlike generic LLMs that "hallucinate confidently," the system prioritizes the *source* (FAR/AIM) over the *synthesis*.

**2. Pedagogical State Machine**
*   **ACS Integration:** Using the FAA Airman Certification Standards (ACS) not just as a curriculum, but as a literal **state machine** that drives the AI's memory. The AI knows exactly *which* ACS task a specific chat message pertains to.
*   **Socratic "Warm Handoff":** The Verifier Agent caches its research (citations + context) and hands it off to the Socratic Teacher. When the user clicks "Teach Me," the system doesn't start from scratch; it uses the exact context of the just-verified answer to generate a targeted lesson.

**3. "Save Chat" Trigger Logic**
*   **Selective Persistence:** Users can "pin" specific verified answers to their notebook. This isn't a generic "save all history" feature; it's a specific trigger for high-value, verified regulatory explanations that the user wants to review later.

### Market Context & Competitive Landscape

*   **Generic AI (ChatGPT/Claude):** Fast but dangerous (hallucinations). No state tracking.
*   **Legacy Ground School (Sporty's/King):** Passive video consumption. No active recall or personalized coaching.
*   **AviationChat:** The only solution combining **Active Recall (AI)** with **Verified Accuracy (RAG)** and **Structured Progress (ACS)**.

### Validation Approach

*   **The "Stump the Chump" Test:** Beta users (CFIs) will be encouraged to intentionally ask tricky regulatory questions to see if the Verifier Swarm can catch the nuance (e.g., "Can I fly with a hangover?" vs "What is the specific 8-hour bottle-to-throttle rule?").
*   **Latency Testing:** Validating that the "verify + cache" loop happens fast enough (<3s) to keep the user engaged before they click "Teach Me."

## Project Type Specific Requirements (SaaS PWA)

### Project-Type Overview

AviationChat is a **B2B2C SaaS PWA** (Business-to-Business-to-Consumer). It serves individual students directly (B2C) while providing compliance value to Flight Schools (B2B). The technical architecture prioritizes **real-time streaming reliability** over offline capabilities.

### Technical Architecture Considerations

*   **Streaming Protocol:** **Server-Sent Events (SSE)**
    *   *Decision:* The "Expert Witness" topology is a read-heavy stream where the system pushes updates (Lane 1 → Lane 2 → Lane 3) to the client. SSE is natively supported by the browser `EventSource` API and is more firewall-friendly for institutional Wi-Fi than WebSockets. *Note: Current implementation uses SSE (`text/event-stream`); we will stick to this for V1 simplicity.*
*   **State Management:** **Backend-Driven State Machine**
    *   *Decision:* The "ACS State" (which tasks are distinct/passed) lives strictly in **Firestore**. The frontend is a "dumb" renderer of this state to prevent clients from hacking their own progress records.
*   **PWA Strategy:** **Passive Installability**
    *   *Decision:* We will include a Web App Manifest and Service Worker for asset caching to ensure fast loads, but we will NOT block functionality for "Add to Home Screen." The app must work flawlessly in a mobile browser tab.

### Implementation Considerations

*   **Authentication & Roles:**
    *   **Auth Provider:** Firebase Auth (Phone/Email).
    *   **Human Roles:** `Student` (Read/Write own data).
    *   **System Roles:** `Agent` (Write-only to training logs).
    *   *Note:* No "School Admin" login for V1. Schools receive data via **Compliance Exports** generated by the system.
*   **Data Isolation:**
    *   **Logical Separation:** All records keyed by `user_id`.
    *   **Institutional Mapping:** Students link to a school via a "School Code" in their profile, allowing their data to be included in that school's batch export.

### Technical Constraints

*   **Connectivity:** **Online-Only Architecture.**
    *   *Decision:* Unlike cockpit apps (ForeFlight) which require robust offline modes, this is a study tool. We will NOT build offline sync complexity for V1. The "Verified Swarm" relies on real-time web access.
*   **Data Strategy:** **"School Compliance Export"**
    *   *Decision:* Rather than building complex multi-year data retention policies for every jurisdiction, the system will generate "Compliance Reports" (PDF/CSV) that schools can download. This shifts the regulatory retention burden to the institution while giving them the data they need.

### Integration Requirements

*   **Institutional Reporting:**
    *   *Feature:* capability to aggregate student logs into a standard "Class Report" for Chief Instructors to sign off weekly ground training.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** "Lean Full App" (Production Hygiene from Day 1).
*   **Rationale:** In high-stakes aviation training, a "buggy MVP" destroys trust immediately. We are launching a complete PPL companion, not a prototype.
**Resource Requirements:** 1 Full Stack Engineer + AI Agent Swarm.

### MVP Feature Set (Phase 1 - Launch V1.0)

**Target Audience:** Student Pilots (PPL) + Beta Flight Schools.

**Must-Have Capabilities:**
1.  **Full PPL Curriculum:** 11 ACS Areas fully enabled for both text and voice.
2.  **Dual-Agent Voice:** "Sully" (Coach) and "Igor" (DPE) available for all topics.
3.  **Expert Witness:** Specialist + Verifier swarms active for regulatory queries (SSE Streaming).
4.  **Compliance Logs:** CSV/PDF export of training sessions for Part 141 credit.
5.  **PWA:** Fully functional mobile web experience (manifest + service worker).

### Post-MVP Features

**Phase 2: "The Institutional Platform" (Growth)**
*   **Target:** Flight Schools (B2B).
*   **Features:**
    *   **Instructor Dashboard:** Real-time view of student progress.
    *   **Roster Management:** Invite/Manage students by cohort.
    *   **SSO:** Integration with school identity providers.

**Phase 3: "The Career Companion" (Vision)**
*   **Target:** Advanced Pilots (IR/CPL/ATP).
*   **Features:**
    *   **Additional Curriculums:** Instrument Rating (IR) and Commercial (CPL).
    *   **Career Logbook:** Long-term tracking of proficiency.

### Risk Mitigation Strategy

**Technical Risks (Latency & Hallucination):**
*   **Mitigation:** The "Expert Witness" architecture separates speed from truth. Latency issues in verification are masked by the "Fast Specialist" response (Lane 1) while the verifier (Lane 3) catches up.

**Market Risks (Trust):**
*   **Mitigation:** The "Living Text" citation UI puts the FAA data front-and-center. We don't ask users to trust the AI; we ask them to trust the *source* the AI found.

## Functional Requirements

### 1. Expert Witness (Text/RAG)

*   **FR1:** Student can ask natural language questions about FAA regulations (FAR/AIM).
*   **FR2:** System must display a "Verifying..." indicator while the Swarm (Lane 2) is processing.
*   **FR3:** System must display specific, verified citations from the official text in a collapsible UI block.
*   **FR4:** Student can "Pin/Save" a specific verified question/answer pair to their personal Notebook.
*   **FR5:** System must provide a "Teach Me" button on confirmed answers to trigger the Socratic mode lesson.
*   **FR5-A (Continuous Verification):** The Verification Swarm MUST remain active during all interactive teaching loops (Socratic mode, Quiz remediation). Any new regulatory claim generated during a Socratic correction must be verified against DB2 (Library) before being displayed to the student. Unverified corrections are a safety hazard equivalent to hallucination.
*   **FR1-A (Specialist Role):** Specialist Agent covers "Rote" phase testing and deep retrieval from Curriculum (DB1).
*   **FR1-B (Bridge Keys):** All regulatory claims must cite DB2 (Library) via "Bridge Key" (e.g., FAR 91.103).

### 2. Voice Interaction (Audio)

*   **FR6:** Student can interact via voice with **Voice Activity Detection (VAD)** (Target: Silero VAD with dynamic pause detection).
*   **FR6-A (Dynamic VAD Threshold):** The VAD silence threshold MUST adapt based on conversation state. A static 3.0s pause + 800ms processing = 3.8s effective latency, which breaks conversational flow. The system must shorten the threshold after detecting a complete sentence (e.g., ~1.5s) and lengthen it during student thinking pauses (e.g., ~3.0s).
*   **FR7:** Student can toggle a **"Mute" button** to pause VAD input during study sessions (e.g., noisy environment).
*   **FR8:** System must differentiate personality based on user selection/context: "Sully" (Coaching) vs "Igor" (Examiner).
*   **FR9:** Voice latency must be **< 800ms** to maintain conversational flow.
*   **FR10:** System must support "Interrupt/Barge-in" to stop the AI from speaking.
*   **FR10-B (Barge-in Visual Feedback):** The system MUST provide immediate visual acknowledgment (e.g., glowing ring, "Listening" pulse) the moment the user begins speaking during barge-in. This prevents "double-talk" confusion and confirms the system has detected the interrupt.
*   **FR10-A (Telemetry):** System must log `filler_word_count` and `hesitation_duration` to detect confidence gaps.

### 3. Pedagogical Engine (ACS State)

*   **FR11:** System must track user progress against the 11 ACS Areas of Operation in the backend.
*   **FR12:** System must generate rote-level quizzes (multiple choice) for specific ACS Tasks.
*   **FR13:** System must enforce an **80% passing score** on a quiz to mark a Task as "Complete".
*   **FR14:** Student can view their progress on a "Zero-Blind-Spot" dashboard (Red/Yellow/Green).
*   **FR15:** System must persist "Stuck Points" (failed topics) and prioritize them in future sessions.
*   **FR15-A (The Vault Keeper):** System must prioritize questions in this order: Review (Expired/Failed) > New (Discovery) > Maintenance (Safe Zone).
*   **FR15-B (Decay Logic):** "Rote" items expire in 14 days; "Application" items expire in 21 days.

### 4. Compliance & Identity

*   **FR16:** System must log every study session with: Date, Duration, ACS Codes Covered, and Performance Grade.
*   **FR17:** Student can export a **"Part 141 Compliance Report"** (PDF/CSV) covering a specific date range. Export format must align with **14 CFR Part 141, Appendix B** verbiage, including fields for CFI digital signature and "Statement of Completion" to maximize institutional compliance value.
*   **FR18:** Users can sign up/login via Email or Google Auth (Firebase).
*   **FR19:** Student can link their account to a Flight School via a specific "School Code" lookup.
*   **FR20:** System must prevent concurrent active sessions for the same user ID (License sharing prevention).
*   **FR20-A (Bot Guard):** System must enforce strict IP-based rate limiting on all unauthenticated endpoints to prevent script abuse.
*   **FR20-B (Message Quotas):** System must enforce a daily message limit (e.g., 50 messages/day) on authenticated users. Reaching the limit gracefully rejects further LLM queries until the next day.

### 5. Data Model Requirements (Schema Critical Path)

*   **FR21 (The Mastery Schema):** The database MUST track the following fields for *every* ACS Task (e.g., PA.I.C.K2) per user:
    *   `last_seen` (Timestamp)
    *   `mastery_level` (Enum: SEEN, ROTE, APPLICATION, MASTERED)
    *   `decay_due_date` (Timestamp)
*   **FR21-A (Atomic Mastery Transitions):** All mastery state transitions (mastery level change, decay timer initialization, dashboard update) MUST execute as a single atomic operation. Partial state updates (e.g., quiz passes but dashboard doesn't reflect) are a critical failure mode.
*   **FR21-B (Session Context Object):** Static user profile data (`call_sign`, `target_checkride`, `name`, `school_code`) MUST be cached at the session level upon login. Agents should read static profile data from this session context rather than querying the database on every request, reducing TA Agent load to dynamic mastery updates only.
*   **FR22 (Session Telemetry):** Session logs must structure voice analytics to feed the "Confidence Gap" logic:
    *   `hesitation_duration` (Float: Seconds of silence > 3.0s)
    *   `filler_word_count` (Integer)
*   **FR23 (Learning Context Cache):** The system MUST maintain a per-task context cache containing:
    *   Verified citations and Bridge Keys from all RAG retrievals
    *   Librarian dossier (evidence package)
    *   Socratic corrections and re-verifications
    *   Student wrong answers (to avoid repeating failed explanations)
    *   **Access:** All agents in the Specialist stack AND Voice Instructor agents (Sully/Igor) MUST have read access to this cache.
    *   **Invalidation:** Cache clears ONLY when the student achieves **mastery level** (understanding/application complete) for the ACS task — NOT on simple task sign-off. Also clears on session timeout (safety).
    *   **Rationale:** Prevents expensive re-computation of RAG results across the learning loop and ensures consistent context for Voice agents coaching on previously-studied material.

### 6. Agent Output Delivery (The Talker-Reasoner UI)

*   **FR24 (Auto-Opening Drawer):** When an agent produces structured output (quiz, comparison table, report card), the system MUST automatically open the "Flight Logs" Drawer and render the appropriate view without requiring user action. The Drawer serves as the "System 2" delivery mechanism — the structured, persistent complement to the conversational chat stream.
    *   **Content Types:** Quiz (`QuizSchema`), Table (`TableSchema`), Report Card (`ReportCardSchema`).
    *   **Behavior:** Drawer auto-slides from bottom (mobile) or right (desktop). Content persists in session history.
    *   **Brownfield:** Existing `Drawer.tsx` component with 4 tabs (Status, Quizzes, Notes, Assessments) — currently using mock data.
*   **FR24-A (Dual Thinking Bubbles):** While agents process a request, the system MUST display **two parallel in-chat thinking bubbles** — one per lane of the Talker-Thinker pipeline:
    *   **Lane 1 (Talker):** Bubble shows generic text (e.g., *"Analyzing your question…"*) then morphs seamlessly into the streaming answer. Answer shows `⏳ PENDING` verification badge.
    *   **Lane 2 (Thinker):** Bubble appears below Lane 1 (e.g., *"Searching the documents…"*, *"Verifying answer…"*) and **dissolves** when verification completes, turning the badge to `✅ VERIFIED`.
    *   **Correction/Expansion:** If Lane 2 finds inaccuracies, the answer text updates in-place with a subtle highlight animation.
    *   **Rules:** Bubble text is always **generic** (no specific FAR references). Both render inline with no layout shift. Lane 2 always dissolves — final state is a single unified answer.
    *   **Integration:** Status updates stream via SSE using a `thinking_status` event type with a `lane` discriminator.
*   **FR24-B (Tier Unlock Toasts):** The system MUST display a cockpit-styled toast notification when a mastery milestone unlocks a new capability:
    *   **Sully Unlock (per-task):** Fires when a ROTE quiz is passed for a specific ACS Task. Toast names the task and confirms Sully is available.
    *   **Igor Unlock (global threshold):** Fires when the student crosses **60% overall ACS completion** (ROTE = 50%, APPLICATION = 100% per topic). No toast for intermediate progress.
    *   **Behavior:** Clicking the toast navigates to the unlocked feature. No generic "level up" text — must name specific task or milestone.

### 7. Admin Agent & Grading Authority

*   **FR25 (Admin Agent Grading):** The Admin Agent MUST receive the full transcript of every voice session (both Sully and Igor) and produce a grading assessment. Voice teaching agents (Sully, Igor) do NOT grade — they only teach/examine. The Admin Agent is the single authority for mastery transitions from voice interactions.
    *   **Sully sessions:** Admin grades → APPLICATION level transition.
    *   **Igor sessions:** Admin grades → MASTERED level transition.
    *   **Input:** Full conversation transcript + session telemetry (hesitation, filler words).
    *   **Output:** Grade (pass/fail), examiner notes, per-topic assessment.
*   **FR26 (Untracked DPE Practice Mode):** Students MUST be able to take a mock checkride with Igor without formal mastery tracking. This is a motivational tool that shows students how unprepared they are before they've completed the full preparation pipeline.
    *   **Behavior:** No mastery updates are recorded. Student receives informal feedback only.
    *   **Access:** Available at any time (no 60% gate for untracked mode).

## Non-Functional Requirements

### Performance

*   **Verification Latency:** Less than **10 seconds** for the full "Expert Witness" loop (Research + Verification).
    *   *Constraint:* If verification exceeds 10s, the system must stream the "Fast Answer" (Specialist) with a "Verification Pending" status to prevent user abandonment.
*   **Voice Response:** Less than **2 seconds** (Industry Standard) for initial audio packet (Time-to-First-Byte) to maintain conversational illusion.
*   **Tech Stack Targets:** Deepgram Nova-3 for STT (Technical Jargon), Silero VAD.

### Security & Compliance

*   **Data Protection:** Standard AES-256 encryption for all database records (At-Rest) and TLS 1.3 for all traffic (In-Transit).
*   **Infrastructure Protection:** The system employs token-bucket rate limiting (`slowapi`) and database-backed daily usage quotas to prevent API billing abuse.
*   **Compliance:** **FERPA/EdTech compliance is OUT OF SCOPE for V1.** The system is currently a standard B2C application; institutional compliance will be added in Phase 2.

### Scalability & Reliability

*   **Concurrency:** System must support **50+ concurrent active sessions** (Beta Scale) without performance degradation.
*   **Availability:** **Best Effort SLA.** Support and uptime guarantees are limited to standard business hours for the initial non-profit Partner Beta.
