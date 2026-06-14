# 6-Search Librarian Architecture (Dual-DB Topology)

The Librarian Agent’s Search Engine has been heavily refactored. We retired the old monolithic 3-lane swarm in favor of a **Dual-DB Topology** that executes up to 6 parallel search lanes. This guarantees deterministic access to our core curriculum while dynamically retrieving edge-case knowledge from the broader FAA library.

---

## 1. High-Level Dual-DB Topology

The "brain" is split into two distinct datastores. DB1 is our curated, deterministic curriculum. DB2 is the massive Enterprise Search engine containing raw FAA documentation.

```mermaid
flowchart LR
    Librarian((Librarian Agent))
    
    subgraph DB1 ["DB1: Curriculum"]
        GCS["aviationchat-curriculum-cms"]
        TypeK["Knowledge and Skill Elements"]
        TypeR["Risk Management Elements"]
    end
    
    subgraph DB2 ["DB2: Source Library"]
        Vertex["aviation-library-v2"]
        Legal["FARs and Legal"]
        Safety["Hazards and Risks"]
        App["Practical Application"]
        Bridge["RM Bridge Hops"]
    end

    Librarian -- "Deterministic Fetch" --> DB1
    Librarian -- "Semantic Search" --> DB2
    
    GCS --- TypeK
    GCS --- TypeR
    Vertex --- Legal
    Vertex --- Safety
    Vertex --- App
    Vertex --- Bridge
```

---

## 2. The 6-Lane Parallel Execution

When the Orchestrator requests an investigation (via `perform_investigation`), the Librarian simultaneously fires off 6 async requests.

1. **DB1 Lesson (K/S Types):** Directly fetches `.md` files from GCS matching the lesson's ACS elements.
2. **DB1 RM (R Types):** Directly fetches Risk Management `.md` files from GCS.
3. **DB2 Legal:** Queries Vertex AI using RKP titles + FAR references to pull regulations.
4. **DB2 Safety:** Queries Vertex AI adding "safety hazards risks accidents" to the titles.
5. **DB2 Application:** Queries Vertex AI focusing on practical application.
6. **DB2 Bridge Hop:** Uses strict array metadata filtering (`document_tags: ANY(...)`) to find cross-disciplinary risk management bridging logic.

```mermaid
flowchart TD
    O["Orchestrator"] --> Call["perform_investigation(manifest)"]
    Call --> L["6-Search Librarian"]
    
    subgraph DB1_Fetch ["Lane 1 & 2: DB1 Fetch"]
        L --> FetchK["Fetch K/S Elements"]
        L --> FetchR["Fetch RM Elements"]
    end
    
    subgraph DB2_Search ["Lane 3-6: DB2 Search"]
        L --> SearchLegal["Search Legal (Titles + FARs)"]
        L --> SearchSafety["Search Safety (Titles + Hazards)"]
        L --> SearchApp["Search Application (Titles + Practical)"]
        L --> SearchBridge["Search Bridge Hop (STRICT document_tags filter)"]
    end
    
    FetchK --> Combine["Combine Results"]
    FetchR --> Combine
    SearchLegal --> Rerank["Re-rank DB2 results\n(Keep Top 3 per lane)"]
    SearchSafety --> Rerank
    SearchApp --> Rerank
    SearchBridge --> Rerank
    
    Rerank --> Combine
    Combine --> Return["Return unified InvestigationDossier"]
```

---

## 3. DB2 Re-ranking & Extractive Segments

Because DB2 is a massive Enterprise Search engine, we pull a wider net and then algorithmically narrow it down before feeding it to the LLM to save context window tokens.

- **Extraction:** The system attempts to parse `extractive_segments` (multi-paragraph high-relevance chunks). If not found, it falls back to `extractive_answers` or raw HTML `snippets`.
- **Re-ranking:** For the DB2 lanes, the librarian requests **5 to 10 chunks per lane**, but locally sorts them by `relevance_score` and **only keeps the Top 3**. This ensures the LLM only reads the absolute highest quality matches.

```mermaid
flowchart TD
    Search["Execute Vertex AI Query"] --> Fetch["Retrieve up to 10 chunks"]
    Fetch --> Parse{"Parse Struct Data"}
    
    Parse -- "Choice 1" --> ExtSegments["extractive_segments\n(Best quality)"]
    Parse -- "Choice 2" --> ExtAnswers["extractive_answers\n(Medium quality)"]
    Parse -- "Choice 3" --> Snippets["snippets\n(Strip HTML)"]
    
    ExtSegments & ExtAnswers & Snippets --> AssignScore["Assign relevance_score"]
    AssignScore --> Sort["Sort by score descending"]
    Sort --> Chop["Chop at index 3"]
    Chop --> Return["Return Top-3 Chunks"]
```

---

## 4. RKP-First & Off-Syllabus Fallbacks

The 6-Search Librarian has been updated to dynamically shape itself based on what the student is doing.

### Mode A: Full Curriculum (6-Lane)
- Used during the main Socratic Teacher flow.
- Requires a full `RKPManifest`.
- Executes all DB1 and DB2 lanes.

### Mode B: RKP-First Q&A (4-Lane)
- Used when answering student questions mid-lesson.
- The `include_db1=False` flag is passed.
- **Why?** The LLM already has the core curriculum loaded in its prompt (the RKP Ground Truth). Fetching the raw GCS files would be redundant token waste. It only fires the 4 DB2 lanes to grab supplementary edge-case data to answer the student's specific question.

### Mode C: Complete Off-Syllabus (6-Search)
- Used when a student asks a random aviation question not tied to any lesson.
- No manifest exists.
- The librarian executes `_query_based_investigation()`. It skips DB1 entirely, and drops the strict Bridge Hop filter. It executes a pure 6-search DB2 search (Legal, Safety, Application) using the raw user query.
