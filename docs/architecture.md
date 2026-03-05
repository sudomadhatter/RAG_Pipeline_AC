---
stepsCompleted: ['step-01-init', 'step-02-context', 'step-03-starter', 'step-04-decisions', 'step-05-patterns', 'step-06-structure', 'step-07-validation', 'step-08-complete']
lastStep: 'step-08-complete'
status: 'complete'
completedAt: '2026-02-16'
inputDocuments: ['c:/AGY-Projects/aviationChat-AGY/_bmad-output/planning-artifacts/prd.md', 'c:/AGY-Projects/aviationChat-AGY/_bmad-output/planning-artifacts/product-brief-aviationChat-AGY-2026-02-10.md', 'c:/AGY-Projects/aviationChat-AGY/_bmad-output/planning-artifacts/ux-design-specification.md']
workflowType: 'architecture'
project_name: 'aviationChat-AGY'
user_name: 'Daniel'
date: '2026-02-16'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (39 FRs across 7 categories):**

| Category                      | FRs                             | Architectural Significance                                                                |
| ----------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------- |
| **Expert Witness (Text/RAG)** | FR1–FR5, FR5-A, FR1-A, FR1-B    | Multi-agent orchestration, dual-database RAG, SSE streaming, continuous verification      |
| **Voice Interaction**         | FR6–FR10, FR6-A, FR10-A, FR10-B | Real-time audio pipeline, dynamic VAD, barge-in feedback, STT/TTS integration             |
| **Pedagogical Engine**        | FR11–FR15, FR15-A, FR15-B       | ACS state machine, mastery gates, decay logic, quiz generation                            |
| **Compliance & Identity**     | FR16–FR20                       | Session logging, FAA-format exports, Firebase Auth, concurrent session prevention         |
| **Data Model**                | FR21–FR23, FR21-A, FR21-B       | Mastery schema, atomic transitions, session context caching, Learning Context Cache       |
| **Agent Output Delivery**     | FR24, FR24-A, FR24-B            | Auto-opening Drawer, dual in-chat thinking bubbles, tier unlock toasts, SSE event routing |
| **Admin Agent & Grading**     | FR25, FR26                      | Voice transcript grading, mastery authority, untracked DPE practice mode                  |

**Non-Functional Requirements:**

- **Verification Latency:** <10s for full Expert Witness loop; fallback "Fast Answer" if exceeded
- **Voice Response:** <2s time-to-first-byte for audio; <800ms target with dynamic VAD
- **Citation Accuracy:** 99% verified accuracy; 0% hallucination on cited regulations
- **Concurrency:** 50+ concurrent sessions (Beta scale)
- **Security:** AES-256 at rest, TLS 1.3 in transit; FERPA out of scope for V1
- **Availability:** Best-effort SLA for initial beta

### Scale & Complexity

- **Primary domain:** Full-stack SaaS/PWA (Aviation EdTech)
- **Complexity level:** High
- **Estimated architectural components:** ~15 (Frontend, 5 routers, 8+ agents, 3 data stores, voice pipeline)
- **Project context:** Brownfield — existing codebase with working agents being refactored

### Technical Constraints & Dependencies

| Constraint                      | Decision                            | Rationale                                                 |
| ------------------------------- | ----------------------------------- | --------------------------------------------------------- |
| **Online-only**                 | No offline sync                     | Verification Swarm requires real-time web access          |
| **Backend-driven state**        | Frontend cannot write mastery state | Prevents students from hacking progress                   |
| **SSE for Expert Witness**      | Already implemented, keeping for V1 | Browser-native, firewall-friendly for institutional Wi-Fi |
| **Firebase Auth**               | Phone/Email auth                    | Already integrated, supports Student role                 |
| **Firestore**                   | Primary data store                  | Already in stack, TA Agent hub pattern established        |
| **GCP Cloud Run**               | Deployment target                   | Existing infrastructure                                   |
| **ADK (Agent Development Kit)** | Agent orchestration framework       | Already in use, supports sub-agent pattern                |

### Cross-Cutting Concerns Identified

1. **Auth/Identity:** Firebase Auth flows into every router; concurrent session prevention spans all endpoints
2. **ACS State Machine:** Drives dashboard, quiz generation, agent selection (Sully unlock), cache invalidation, decay warnings, and compliance exports — the most coupled component in the system
3. **Learning Context Cache:** Read by 6+ agents (Specialist, Socratic Teacher, Quiz Generator, Sully, Igor, Admin); written by 2 (Specialist, Socratic Teacher); clears on mastery achievement
4. **Session Context Object:** Static profile data cached at login to reduce TA Agent load
5. **Admin Agent (Grading Authority):** Receives full voice transcripts from Sully and Igor, grades performance, and is the sole authority for APPLICATION and MASTERED mastery transitions. Teaching agents never grade.
6. **Verification Pipeline:** Must remain active during ALL teaching interactions (initial query + Socratic corrections + quiz remediation)
6. **Voice Infrastructure:** VAD → STT → Agent → TTS pipeline with 4 serial hops; latency budget must account for dynamic VAD threshold

### System Topology (Graph of Thoughts Analysis)

**Hidden architectural patterns identified through deep analysis:**

| Pattern                        | Discovery                                            | Architectural Implication                                                                           |
| ------------------------------ | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **TA Agent bottleneck**        | All agents funnel through TA for user data           | Must be pure function layer (not LLM), sub-100ms target. Session Context Object mitigates hot reads |
| **Cache read/write asymmetry** | Learning Context Cache: 5 readers, 2 writers         | Write-few/read-many — ideal for Firestore. Cache schema must be stable                              |
| **Voice serial hops**          | 4-hop pipeline: VAD → STT → Agent → TTS              | Stream TTS output, pre-warm from cache. Total budget ~2-4s                                          |
| **SSE message typing**         | Single SSE stream carries Fast Answer + Verification | Need typed event protocol with message discriminator                                                |
| **ACS state coupling**         | 6 subsystems depend on mastery transitions           | Atomic transactions required (FR21-A); most likely source of cascading bugs                         |
| **Firestore multi-pattern**    | Serves hot reads, append-only writes, and temp cache | Monitor access patterns; split if needed post-V1                                                    |

### PRD Enhancements Applied During Analysis

During context analysis, 8 PRD enhancements were identified and applied:

1. **Socratic Teacher sub-agent** — Dedicated sub-agent in Specialist stack with re-verification pipeline
2. **FR5-A (Continuous Verification)** — Verification Swarm active during all teaching loops
3. **FR6-A (Dynamic VAD)** — Adaptive silence threshold (1.5s–3.0s) to solve 3.8s effective latency
4. **FR10-B (Barge-in Feedback)** — Immediate visual acknowledgment on voice interrupt
5. **FR17 (Compliance Format)** — Aligned with 14 CFR Part 141, Appendix B
6. **FR23 (Learning Context Cache)** — Per-task cache with mastery-level invalidation and all-agent access
7. **FR21-A (Atomic Mastery Transitions)** — Single atomic operation for all state changes
8. **FR21-B (Session Context Object)** — Login-time static profile caching to reduce TA load

## Starter Template Evaluation

### Primary Technology Domain

Full-stack SaaS/PWA — **Brownfield project** with established codebase. No starter template needed.

### Existing Technology Stack (Locked Decisions)

| Layer                  | Technology                   | Version/Status                   |
| ---------------------- | ---------------------------- | -------------------------------- |
| **Frontend Framework** | Next.js (React)              | In production                    |
| **Styling**            | Tailwind CSS + Shadcn/UI     | In production                    |
| **Animation**          | Framer Motion                | Specified in UX Spec             |
| **Backend Framework**  | FastAPI (Python)             | Refactored (Foundation Sprint)   |
| **Agent Framework**    | Google ADK (Python)          | In production                    |
| **LLM**                | Gemini 3.0 (Pro/Flash)       | In production                    |
| **Database**           | Firestore                    | In production                    |
| **Auth**               | Firebase Auth (Phone/Email)  | In production                    |
| **RAG**                | Vertex AI Search (DB1 + DB2) | In production                    |
| **Streaming**          | SSE (Server-Sent Events)     | In production                    |
| **STT**                | Deepgram Nova-3              | Specified in PRD                 |
| **TTS**                | Deepgram Aura-2              | Sub-200ms TTFB, unified pipeline |
| **VAD**                | Silero VAD                   | Specified in PRD                 |
| **Deployment**         | GCP Cloud Run                | Target                           |
| **CI/CD**              | GitHub Actions               | Existing GitHub integration      |
| **Typography**         | Inter + JetBrains Mono       | Specified in UX                  |

### MCP Tools Available to Dev Agents

AI coding agents (dev, SM, QA) have direct MCP server access during implementation and testing. **Use these instead of guessing at data structure or making blind Firestore writes.**

| MCP Server              | Tools | Primary Use During Dev                                                                                                                                                                          |
| ----------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **firebase-mcp-server** | 17    | 🔥 **PRIMARY TESTING TOOL** — Inspect live Firestore documents, verify session state writes, check field schemas. Use `firebase_read_resources` to read `chat_sessions/{session_id}` directly after any write. |
| **cloudrun-mcp-server** | 8     | Deploy to Cloud Run, tail service logs, verify live endpoint health after backend changes.                                                                                                      |
| **github-mcp-server**   | —     | Create branches, push commits, open PRs — standard Git workflow tooling.                                                                                                                        |

> **Dev Agent Rule:** When implementing any Firestore read/write, use `firebase-mcp-server` to verify the document structure in the live `greeting-agent` database **before and after** your changes. This prevents schema mismatches without print-debugging.


### Architectural Decisions Established by Codebase

| Decision          | Choice                                   | Rationale                        |
| ----------------- | ---------------------------------------- | -------------------------------- |
| Frontend Language | TypeScript                               | Next.js standard                 |
| Backend Language  | Python 3.11+                             | ADK requirement                  |
| Backend Routing   | FastAPI routers (5 routers)              | Foundation Sprint                |
| Frontend Routing  | Next.js App Router                       | Existing config                  |
| State Management  | Backend-driven (Firestore)               | PRD: prevent client-side hacking |
| Component Library | Shadcn/UI + Apple standard glassmorphism | UX Spec                          |
| Build Tooling     | Next.js built-in (Turbopack)             | Existing config                  |
| API Protocol      | REST + SSE (text), TBD (voice)           | Existing implementation          |

### Starter Template Decision

**No starter template required.** The Foundation Sprint established the backend architecture (`main.py` → 5 routers → schemas → patches). The frontend was already structured via Next.js conventions. Project initialization is not a story — we iterate on the existing codebase.

## Core Architectural Decisions

### Data Architecture

| Decision                            | Choice                                                             | Rationale                                                                                                           |
| ----------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **Learning Context Cache storage**  | Firestore subcollection: `users/{uid}/learning_context/{acs_task}` | Aligns with existing `completed_items` pattern; clean per-user scoping; auto-cleanup via Cloud Functions TTL        |
| **Session Context Object delivery** | ADK session state injection at login                               | TA Agent fetches static profile once, injects into session; all sub-agents inherit; zero extra DB calls per request |

### Authentication & Security

| Decision                          | Choice                                                      | Rationale                                                                                                                              |
| --------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Request authorization**         | Firebase ID token verification middleware on FastAPI routes | Standard `verify_token` dependency injected into routes; ~50ms per request; proven pattern                                             |
| **Database Security Rules**       | Explicit `firestore.rules` file in project root             | Enforces that frontend clients can only read/write their own profile data, while blocking raw question bank writes.                    |
| **Agent-to-agent trust**          | ADK in-process sub-agents (no network boundary)             | All agents run in same Cloud Run instance; sub-agents are Python function calls; no auth overhead                                      |
| **Concurrent session prevention** | Firestore session token in user doc                         | On login, write `active_session_id`; existing sessions with old tokens get soft-rejected with "logged in elsewhere" message            |
| **Bot Guard (Rate Limiting)**     | `slowapi` token bucket middleware                           | Strict IPs limits (5/min) on unauthenticated routes; moderate limits (10/min) on authenticated routes to prevent script abuse.         |
| **Billing Protection (Quotas)**   | Firestore tracking: `users/{uid}/usage/{YYYY-MM-DD}`        | Middleware uses Firestore `Increment(1)` to track cost limits. Fails open on DB errors to prevent blocking legit users during outages. |

### API & Communication Patterns

| Decision                | Choice                                                      | Rationale                                                                                                                                                                                                                                                                                                                          |
| ----------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SSE event protocol**  | Typed JSON events with `type` discriminator                 | Event types: `specialist_chunk`, `verification_result`, `citation`, `thinking_status` (→ dual in-chat bubbles with `lane` field: `talker` or `thinker`), `drawer_content` (→ auto-open Drawer with quiz/table/report payload). Extensible; frontend routes events to different handlers. Supports Talker-Thinker pattern (FR24-A). |
| **Error handling**      | Structured error envelope + user-facing toast notifications | Backend returns `{error, code, message, retryable}`; frontend translates to cockpit-styled Sonner toasts (Amber/Red/Green); user never sees error codes                                                                                                                                                                            |
| **Rate/Quota Errors**   | Specific HTTP 429 and 403 intercepts in `api.ts`            | Frontend global fetch wrapper intercepts `RATE_LIMIT` and `QUOTA_EXCEEDED` structured errors to display unified toast warnings without crashing components.                                                                                                                                                                        |
| **Voice communication** | WebSocket for bidirectional audio                           | Full duplex supports barge-in (FR10); pairs with Deepgram streaming STT natively; simpler than WebRTC for V1                                                                                                                                                                                                                       |

### Frontend Architecture

| Decision                      | Choice                                    | Rationale                                                                                                                                                                                                 |
| ----------------------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Toast/notification system** | Shadcn/UI Sonner with cockpit HUD styling | Sonner for behavior, custom Amber/Red/Green HUD theming for cockpit aesthetic                                                                                                                             |
| **Global state management**   | Zustand                                   | Lightweight (~1KB), selective re-renders, no boilerplate; chat state, voice toggle, citation panel, and progress data shared across ChatPanel, CitationSnap, SullyDrawer, Dashboard without prop drilling |

### Infrastructure & Deployment

| Decision                      | Choice                                                   | Rationale                                                                                  |
| ----------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Logging & monitoring**      | Google Cloud Logging (native to Cloud Run)               | Zero setup, structured JSON logs, free tier sufficient for beta                            |
| **Environment configuration** | `.env` files + GCP Secret Manager for production secrets | Existing `.env` pattern; Secret Manager secures API keys in Cloud Run without code changes |

### Decision Impact Analysis

**Implementation Sequence:**
1. Zustand store setup (enables all frontend state sharing)
2. Firebase token middleware (gates all authenticated routes)
3. SSE typed event protocol (enables Expert Witness UI)
4. Learning Context Cache schema (enables agent data sharing)
5. WebSocket voice endpoint (enables Sully/Igor)
6. Concurrent session prevention (enables license control)

**Cross-Component Dependencies:**
- Zustand store ↔ SSE event handler ↔ CitationPanel ↔ SullyDrawer
- Firebase middleware ↔ ADK session state ↔ Session Context Object
- Learning Context Cache ↔ Specialist ↔ Socratic Teacher ↔ Voice agents
- WebSocket voice ↔ VAD ↔ STT ↔ TTS pipeline

## Implementation Patterns & Consistency Rules

### Naming Conventions

| Area                   | Convention                  | Example                                               |
| ---------------------- | --------------------------- | ----------------------------------------------------- |
| Firestore collections  | `snake_case`, plural        | `users`, `completed_items`, `learning_context`        |
| Firestore fields       | `snake_case`                | `mastery_level`, `last_seen`, `decay_due_date`        |
| Python functions       | `snake_case`                | `get_user_profile()`, `verify_citation()`             |
| Python files           | `snake_case`                | `specialist_router.py`, `ta_agent.py`                 |
| FastAPI endpoints      | `/kebab-case`, plural nouns | `/api/v1/specialist/ask`, `/api/v1/history/sessions`  |
| TypeScript functions   | `camelCase`                 | `getUserProfile()`, `handleSseEvent()`                |
| React components       | `PascalCase`                | `ChatPanel`, `CitationSnap`, `SullyDrawer`            |
| TS files (components)  | `PascalCase.tsx`            | `ChatPanel.tsx`, `SullyDrawer.tsx`                    |
| TS files (hooks/utils) | `camelCase.ts`              | `useAppStore.ts`, `sseClient.ts`                      |
| Zustand slices         | `camelCase`                 | `chatSlice`, `voiceSlice`, `progressSlice`            |
| SSE event types        | `snake_case`                | `specialist_chunk`, `verification_result`, `citation` |

### API Format Patterns

**Success response:**
```json
{ "success": true, "data": { } }
```

**Error response (backend → frontend):**
```json
{ "success": false, "error": { "code": "VERIFICATION_TIMEOUT", "message": "...", "retryable": true } }
```

**SSE event (typed):**
```json
{ "type": "specialist_chunk", "data": { "content": "...", "session_id": "..." } }
```

**Date format:** ISO 8601 strings (`2026-02-16T14:30:00Z`)
**JSON field naming:** `snake_case` (match Firestore schema)

### Project Structure Patterns

```
backend/
├── main.py              # App factory + middleware
├── routers/             # FastAPI routers (1 per domain)
│   ├── greeting.py
│   ├── specialist.py    # SSE streaming endpoint
│   └── voice.py         # WebSocket endpoint
├── agents/              # ADK agent definitions
│   ├── specialist/
│   │   ├── agent.py
│   │   ├── socratic_teacher.py
│   │   └── tools/
│   └── voice/
├── schemas/             # Pydantic models (request/response)
├── services/            # Business logic layer
└── middleware/           # Auth, error handling

frontend/
├── app/                 # Next.js App Router pages
├── components/          # Organized by feature
│   ├── chat/            # ChatPanel, MessageBubble, LivingText
│   ├── citation/        # CitationSnap, PinnedNotebook
│   ├── voice/           # SullyDrawer, VoiceIndicator
│   └── ui/              # Shadcn/UI components
├── stores/              # Zustand stores
│   └── useAppStore.ts
├── hooks/               # Custom React hooks
├── lib/                 # Utilities (sseClient, wsClient)
└── styles/              # Global CSS, design tokens
```

### Process Patterns

| Pattern            | Rule                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| Loading states     | `idle \| loading \| success \| error` enum in Zustand                                                  |
| Error boundaries   | React ErrorBoundary per feature area (chat, voice, dashboard)                                          |
| Toast messages     | User-facing only: `"Looking up citations..."` not `"VERIFICATION_IN_PROGRESS"`                         |
| Retry logic        | Exponential backoff (1s, 2s, 4s) for retryable errors; max 3 attempts                                  |
| Auth flow          | Check token on mount → redirect to login if expired → refresh silently                                 |
| Tests (Python)     | Co-located in `tests/` mirror of `backend/`                                                            |
| Tests (TypeScript) | Co-located: `ChatPanel.test.tsx` next to `ChatPanel.tsx`                                               |
| Logging (Python)   | Structured JSON: `{"level": "info", "agent": "specialist", "action": "rag_query", "duration_ms": 450}` |

### AI Agent Enforcement Rules

All AI agents implementing features MUST:
1. Follow naming conventions above — no exceptions
2. Use the structured error envelope for all API responses
3. Emit typed SSE events with `type` discriminator
4. Read static profile from ADK session state, not Firestore
5. Route all Firestore writes through TA Agent service layer
6. Use Zustand (not useState) for cross-component state
7. Keep toast messages human-friendly — no error codes shown to user

## Project Structure & Boundaries

### Complete Project Directory Structure

```
aviationChat-AGY/
├── backend/
│   ├── main.py                          # FastAPI app factory + CORS + middleware
│   ├── requirements.txt
│   ├── .env / .env.example
│   ├── middleware/
│   │   ├── auth.py                      # Firebase ID token verification
│   │   ├── error_handler.py             # Structured error envelope
│   │   └── session_guard.py             # Concurrent session prevention
│   ├── routers/
│   │   ├── greeting.py                  # Capt. Chuck
│   │   ├── auth.py                      # Login, registration, session token
│   │   ├── hr.py                        # Mrs. Coleman onboarding
│   │   ├── specialist.py               # SSE streaming — Expert Witness
│   │   ├── voice.py                     # WebSocket — Sully/Igor
│   │   └── history.py                   # Session history, progress
│   ├── agents/
│   │   ├── captain_chuck/
│   │   │   ├── agent.py
│   │   │   └── tools/
│   │   ├── mrs_coleman/
│   │   │   ├── agent.py
│   │   │   └── tools/
│   │   ├── specialist/
│   │   │   ├── agent.py                 # Specialist orchestrator (Lane 1)
│   │   │   ├── socratic_teacher.py      # Sub-agent (FR5-A)
│   │   │   ├── quiz_generator.py        # Sub-agent (FR15)
│   │   │   └── tools/
│   │   │       ├── librarian.py         # DB2 RAG retrieval
│   │   │       ├── curriculum_search.py # DB1 RAG retrieval
│   │   │       └── citation_verifier.py # Bridge Key validation
│   │   ├── verification_swarm/
│   │   │   ├── orchestrator.py          # Lane 2 parallel research
│   │   │   ├── research_agent.py
│   │   │   └── cross_checker.py
│   │   ├── voice/
│   │   │   ├── sully.py                 # CFI personality
│   │   │   └── igor.py                  # DPE personality
│   │   └── ta_agent/
│   │       ├── service.py               # Pure function layer (NOT LLM)
│   │       └── session_context.py       # Session Context Object
│   ├── schemas/
│   │   ├── specialist.py                # Pydantic: SSE events, queries
│   │   ├── voice.py                     # Pydantic: WebSocket messages
│   │   ├── user.py                      # Pydantic: profile, session
│   │   └── mastery.py                   # Pydantic: ACS state, decay
│   ├── services/
│   │   ├── mastery_service.py           # Atomic transitions (FR21-A)
│   │   ├── learning_context_service.py  # Cache CRUD (FR23)
│   │   ├── compliance_service.py        # Part 141 export (FR17)
│   │   └── telemetry_service.py         # Session logging (FR22)
│   └── tests/
│       ├── routers/
│       ├── agents/
│       └── services/
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── app/                             # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx                     # Landing / login
│   │   ├── dashboard/page.tsx           # Progress dashboard
│   │   └── chat/page.tsx                # Main chat interface
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx            # Main chat + SSE handler
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── LivingText.tsx           # Animated verification transition
│   │   │   └── ChatPanel.test.tsx
│   │   ├── citation/
│   │   │   ├── CitationSnap.tsx         # Citation slide-in panel
│   │   │   └── PinnedNotebook.tsx       # Saved Q&A pairs (FR4)
│   │   ├── voice/
│   │   │   ├── SullyDrawer.tsx          # Voice interface drawer
│   │   │   ├── VoiceIndicator.tsx       # Barge-in feedback pulse (FR10-B)
│   │   │   └── VadController.tsx        # Dynamic VAD UI (FR6-A)
│   │   ├── dashboard/
│   │   │   ├── ProgressGauge.tsx        # ACS mastery visualization
│   │   │   ├── DecayWarning.tsx         # Decay timer alerts
│   │   │   └── ComplianceExport.tsx     # Part 141 report (FR17)
│   │   └── ui/                          # Shadcn/UI base components
│   ├── stores/
│   │   └── useAppStore.ts               # Zustand — chat, voice, progress
│   ├── hooks/
│   │   ├── useSseStream.ts              # Typed SSE event handler
│   │   ├── useWebSocket.ts              # Voice WebSocket manager
│   │   └── useAuth.ts                   # Firebase auth hook
│   ├── lib/
│   │   ├── sseClient.ts                 # SSE connection factory
│   │   ├── wsClient.ts                  # WebSocket connection factory
│   │   ├── api.ts                       # REST API client + error handling
│   │   └── firebase.ts                  # Firebase config + init
│   └── styles/
│       ├── globals.css                  # Design tokens, cockpit theme
│       └── animations.css               # Living Text + micro-animations
└── _bmad-output/planning-artifacts/     # Architecture docs
```

### Architectural Boundaries

| Boundary           | Separation                    | Communication          |
| ------------------ | ----------------------------- | ---------------------- |
| Frontend ↔ Backend | HTTP (REST + SSE + WebSocket) | JSON with typed events |
| Router ↔ Agent     | Function call within FastAPI  | ADK orchestration      |
| Agent ↔ Sub-agent  | In-process (Decision 2.2)     | ADK delegation         |
| Agent ↔ Firestore  | Via TA Agent service layer    | Pure function calls    |
| Agent ↔ RAG stores | Via tool functions            | Vertex AI Search API   |
| Voice ↔ STT        | WebSocket stream              | Deepgram streaming API |

### FR-to-Directory Mapping

| FR Category            | Backend Location                                                       | Frontend Location                           |
| ---------------------- | ---------------------------------------------------------------------- | ------------------------------------------- |
| Expert Witness (FR1-5) | `routers/specialist.py` + `agents/specialist/`                         | `components/chat/` + `components/citation/` |
| Voice (FR6-10)         | `routers/voice.py` + `agents/voice/`                                   | `components/voice/`                         |
| Pedagogical (FR11-15)  | `agents/specialist/quiz_generator.py` + `services/mastery_service.py`  | `components/dashboard/`                     |
| Compliance (FR16-20)   | `services/compliance_service.py` + `middleware/session_guard.py`       | `components/dashboard/ComplianceExport.tsx` |
| Data Model (FR21-23)   | `services/mastery_service.py` + `services/learning_context_service.py` | `stores/useAppStore.ts`                     |

## Architecture Validation Results

### Coherence Validation ✅

All 11 architectural decisions validated for compatibility. No contradictions found. Technology stack is internally consistent (Python backend/ADK, TypeScript frontend/Next.js, GCP ecosystem). Naming conventions properly separated across language boundaries.

### Requirements Coverage ✅ (25/25 FRs)

| FR Range                       | Coverage | Architectural Support                                                 |
| ------------------------------ | -------- | --------------------------------------------------------------------- |
| FR1-5, FR5-A (Expert Witness)  | ✅ Full   | Specialist stack + SSE + Socratic sub-agent + continuous verification |
| FR6-10, FR6-A, FR10-B (Voice)  | ✅ Full   | WebSocket + Deepgram STT/TTS + Dynamic VAD + Barge-in feedback        |
| FR11-15 (Pedagogical)          | ✅ Full   | Mastery service + Quiz Generator + ACS state machine                  |
| FR16-20 (Compliance)           | ✅ Full   | Compliance service + Part 141 format + Session guard                  |
| FR21-23, FR21-A, FR21-B (Data) | ✅ Full   | Atomic transitions + Session Context + Learning Cache                 |
| NFRs (Performance, Security)   | ✅ Full   | Dynamic VAD + TTS streaming + Firebase + Cloud Run defaults           |

### Gap Resolutions

| Gap                | Resolution      | Rationale                                                                                                                                                      |
| ------------------ | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **TTS Engine**     | Deepgram Aura-2 | Sub-200ms TTFB; unified STT+TTS pipeline reduces integration complexity; ~$30/M chars (vs ElevenLabs $206+); sufficient clarity for technical/aviation content |
| **CI/CD Pipeline** | GitHub Actions  | Project already on GitHub; fastest setup for Node.js + Python; automates build-test-deploy to Cloud Run                                                        |

### Architecture Completeness Checklist

- [x] Project context analyzed (8 PRD enhancements from elicitation)
- [x] Scale/complexity assessed (High, 50+ concurrent sessions)
- [x] Technical constraints identified (online-only, backend-driven, GCP)
- [x] Cross-cutting concerns mapped (6 via Graph of Thoughts)
- [x] Technology stack specified (15 technologies locked)
- [x] 11 architectural decisions documented with rationale
- [x] Implementation patterns defined (naming, API, process)
- [x] AI agent enforcement rules established (7 rules)
- [x] Complete project structure with FR-to-directory mapping
- [x] Architectural boundaries defined (6 boundaries)
- [x] All gaps resolved (TTS + CI/CD)

### Architecture Readiness Assessment

**Overall Status:** ✅ READY FOR IMPLEMENTATION

**Confidence Level:** HIGH

**Key Strengths:**
- Brownfield-aware — respects existing code, builds on Foundation Sprint
- Safety-critical verification architecturally guaranteed (no bypass paths)
- Learning Context Cache eliminates redundant RAG calls across agents
- Atomic mastery transitions prevent "zombie progress" states
- Unified Deepgram pipeline (STT + TTS) minimizes voice latency

**Areas for Future Enhancement:**
- Redis for Learning Context Cache if >500 concurrent users
- WebRTC upgrade for voice if WebSocket latency proves insufficient
- FERPA compliance layer when flight school partnerships scale
