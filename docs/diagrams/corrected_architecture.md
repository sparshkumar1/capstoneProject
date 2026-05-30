# PrepAIred Corrected Architecture Diagram

## System Flow (Corrected)

```mermaid
flowchart TD
    subgraph Candidate["👤 Candidate Interface"]
        UILayer["Interview UI<br/>(WebSocket)"]
        VoiceInput["🎤 Voice Input"]
        CodeInput["💻 Code Input"]
        TextInput["📝 Text Input"]
    end

    subgraph InputAnalysis["📊 Input Analysis Layer"]
        AudioPipeline["Audio Pipeline<br/>(STT, Confidence,<br/>Hesitation)"]
        CodeAnalyzer["Code Analyzer"]
        TextProcessor["Text Processor"]
    end

    subgraph Core["🎯 Core Orchestration"]
        Orchestrator["Interview Orchestrator<br/>(Session Hub)"]
    end

    subgraph Processing["⚙️ Processing Agents"]
        QuestionSelector["Question Selector<br/>(Difficulty/Topic)"]
        Timer["Session Timer"]
        Evaluator["Evaluator Agent<br/>(Semantic, Concept,<br/>Reasoning)"]
    end

    subgraph Refinement["✅ Refinement Layer"]
        Validator["Score Validator<br/>(Guardrails)"]
    end

    subgraph Output["📋 Output Layer"]
        Feedback["Feedback Agent<br/>(15-field structured)"]
    end

    subgraph Strategy["🤖 Adaptive Strategy"]
        StrategyAgent["Strategy Agent<br/>(PPO-based RL)<br/>Actions: Easier/Same/Harder<br/>Hints and follow-ups are auxiliary"]
    end

    subgraph Execution["💾 Execution"]
        CodeExecutor["Code Executor<br/>(Sandbox with<br/>Safety Checks)"]
    end

    subgraph Storage["🗄️ Storage"]
        SessionLog["Session Logger<br/>(Turn-level events)"]
        VectorStore["Vector Store<br/>(FAISS Index)"]
    end

    %% Input Flow
    VoiceInput --> AudioPipeline
    CodeInput --> CodeAnalyzer
    TextInput --> TextProcessor
    
    %% Analysis to Orchestrator
    AudioPipeline --> Orchestrator
    CodeAnalyzer --> Orchestrator
    TextProcessor --> Orchestrator
    
    %% Orchestrator coordinates agents
    Orchestrator --> QuestionSelector
    Orchestrator --> Timer
    Orchestrator --> Evaluator
    
    %% Evaluator may need code execution
    Evaluator -.->|if code| CodeExecutor
    CodeExecutor -->|results| Evaluator
    
    %% Processing back to Orchestrator
    QuestionSelector --> Orchestrator
    Timer --> Orchestrator
    Evaluator --> Orchestrator
    
    %% Validation
    Orchestrator --> Validator
    Validator -->|guardrailed score| Orchestrator
    
    %% Feedback generation
    Orchestrator --> Feedback
    Feedback -->|structured feedback| Orchestrator
    
    %% Strategy decision
    Orchestrator --> StrategyAgent
    StrategyAgent -->|next action| Orchestrator
    
    %% Logging
    Orchestrator --> SessionLog
    Evaluator --> VectorStore
    
    %% Back to UI
    Orchestrator -->|question/feedback| UILayer
    UILayer -->|user response| Candidate
    
    %% Loop back
    UILayer -.->|next turn| Candidate

    style Orchestrator fill:#90EE90
    style Candidate fill:#87CEEB
    style InputAnalysis fill:#FFB6C1
    style Processing fill:#DDA0DD
    style Refinement fill:#F0E68C
    style Output fill:#FFE4B5
    style Strategy fill:#E6E6FA
    style Execution fill:#B0E0E6
    style Storage fill:#D3D3D3
