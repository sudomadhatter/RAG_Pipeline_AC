# Talker Agent: The Four Sub-Flows

Here are clean, separated diagrams for each of the specific actions the Talker handles. This breaks down exactly how the "3 calls" (plus the Socratic correction) work independently.

## 1. The RAG Flow (Aviation Questions)
This is how the system handles a student asking a technical aviation question.

```mermaid
flowchart TD
    User(["User asks: 'What is Vg?'"]) --> Gateway["Talker Agent"]
    
    Gateway -- Recognizes Aviation Question --> ToolRAG("Tool: run_aviation_rag")
    
    ToolRAG --> Librarian["Librarian Agent"]
    Librarian -->|"Fetches Manuals / FARs"| Evidence[("Aviation Database")]
    Evidence --> Gateway
    
    Gateway --> Stream["Stream Answer to User"]
    
    classDef unified fill:#0D9488,stroke:#115E59,color:#fff
    classDef tool fill:#0369A1,stroke:#075985,color:#fff
    
    class Gateway unified
    class ToolRAG tool
```

## 2. The Next Lesson Flow
This is how the system handles starting a new study session.

```mermaid
flowchart TD
    User(["User says: 'I am ready to study'"]) --> Gateway["Talker Agent"]
    
    Gateway -- Recognizes Lesson Request --> ToolLesson("Tool: start_next_lesson")
    
    ToolLesson --> LoadContext["Fetch Next Syllabus Item"]
    LoadContext --> TriggerUI["Trigger Frontend Lesson Card UI"]
    
    classDef unified fill:#0D9488,stroke:#115E59,color:#fff
    classDef tool fill:#0369A1,stroke:#075985,color:#fff
    
    class Gateway unified
    class ToolLesson tool
```

## 3. The Platform Help Flow
This handles questions about AviationChat itself, requiring no external tools.

```mermaid
flowchart TD
    User(["User asks: 'How does this work?'"]) --> Gateway["Talker Agent"]
    
    Gateway -- Recognizes Platform Question --> Native["Internal Mission Knowledge"]
    
    Native -->|"Reads aviationchat_mission.md"| Gateway
    Gateway --> Stream["Stream Direct Reply to User"]
    
    classDef unified fill:#0D9488,stroke:#115E59,color:#fff
    
    class Gateway unified
```

## 4. The Socratic Correction Flow
This is the override that happens if the student tries to change the subject *during* an active lesson.

```mermaid
flowchart TD
    User(["User asks random question"]) --> CheckState{"Is a Lesson Active?"}
    
    CheckState -- YES --> SocraticTeacher["Socratic Teacher"]
    SocraticTeacher --> Evaluation["Evaluates Response"]
    Evaluation --> Redirect["Polite Redirect back to lesson"]
    Redirect --> User
    
    CheckState -- NO --> Gateway["Talker Agent handles normally"]
    
    classDef agent fill:#4F46E5,stroke:#3730A3,color:#fff
    
    class SocraticTeacher agent
```
