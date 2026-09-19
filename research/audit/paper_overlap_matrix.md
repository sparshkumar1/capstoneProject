# Three-Paper Division and Overlap Audit Matrix

**Objective:** Ensure distinct research questions, contributions, figures, and tables across the three papers to prevent duplicate publication or self-plagiarism.

---

| Dimension | Paper 1 (Systems / Framework) | Paper 2 (Technical Evaluator) | Paper 3 (Adaptive RL) |
|---|---|---|---|
| **Working Title** | *PREPAIred: An Evidence-Grounded Adaptive Multimodal Framework for Technical Interview Assessment and Feedback* | *Evidence-Grounded Technical Answer Evaluation Using Semantic, Concept, and Reasoning Signals* | *Guardrailed Multimodal Reinforcement Learning for Adaptive Technical Interview Difficulty* |
| **Target Venue** | **ATIS 2026** (Bengaluru, Nov 7 deadline) / **HCII 2027** | **ICTCS 2026** (Ahmedabad) / **ICMETE 2026** (Oct 20) | **SmartCom 2027** (Goa, Jan 2027) / **ICMLSC 2027** |
| **Core RQ** | Can an asynchronous hub-and-spoke architecture isolate failure modes and remove LLMs from the technical scoring path while maintaining sub-second latency? | How do semantic similarity, concept coverage, and reasoning entailment combine to correlate with human grading while defeating keyword stuffing? | How effectively does a guardrailed PPO controller adapt interview difficulty across diverse candidate personas compared to fixed and heuristic baselines? |
| **Primary Contribution** | Systems architecture, Docker C sandbox isolation, persistent multi-attempt state, fault tolerance. | Multi-signal NLP scoring pipeline, $S_2$ reasoning dampening, rubric FAISS vector search, ScoreValidator. | 6D state formulation, PPO curriculum adaptation, stability reward shaping, post-hoc pedagogical guardrails. |
| **Unique Figures** | Figure 1: System Architecture Data & Control Flow<br>Figure 2: Component Latency & Resource Utilization | Figure 1: Multi-Signal Evaluator Flow<br>Figure 2: Concept Threshold Sensitivity Curve<br>Figure 3: Adversarial Keyword-Stuffing Scores | Figure 1: Candidate State-RL Adaptation Loop<br>Figure 2: Multi-Persona Difficulty Trajectories<br>Figure 3: Guardrail Activation & Smoothness |
| **Unique Tables** | Table 1: Subsystem Latency Benchmark (Median, P95)<br>Table 2: Docker Security Negative Test Matrix<br>Table 3: System-Level Component Removal Study | Table 1: 7-Way Evaluator Ablation Benchmark<br>Table 2: Qualitative Error & Misconception Analysis<br>Table 3: Concept Threshold Recall/Precision | Table 1: PPO vs Baselines Across 5 Seeds<br>Table 2: Guardrail & Reward Component Ablation<br>Table 3: 6D State Ablation & Speech Robustness |
| **Shared Assets** | High-level system overview; question bank statistics. | Evaluator scoring formula only. | 6D state definition only. |
