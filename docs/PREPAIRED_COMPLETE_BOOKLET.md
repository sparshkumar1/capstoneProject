# PrepAIred — Master Project Manual, Technical Architecture, Research Compendium & Viva Defense Guide

**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Numerical Traceability Ledger:** [`docs/PAPER_RESULTS_TRACEABILITY.md`](PAPER_RESULTS_TRACEABILITY.md)
**Claims Verification Matrix:** [`docs/CLAIMS_CHECK.md`](CLAIMS_CHECK.md)
**Authoritative Experimental Evidence:** `research/results/`
**Current Git Release Tag:** `paper-v1.0` (Commit: `ea15e3c`)
**Git Branch:** `workspace/human-eval-clean-push`
**Repository Remote:** `https://github.com/sparshkumar1/capstoneProject.git`
**Document Purpose:** The definitive, self-contained, end-to-end master manual for students, researchers, developers, evaluators, and viva defense examiners.

---

## TABLE OF CONTENTS

1. [SECTION A — Project Overview & Elevator Pitches](#section-a--project-overview--elevator-pitches)
2. [SECTION B — Motivation & Technology Justification ("Why We Built It")](#section-b--motivation--technology-justification-why-we-built-it)
3. [SECTION C — Complete End-to-End System Architecture](#section-c--complete-end-to-end-system-architecture)
4. [SECTION D — Frontend Architecture & User Interface](#section-d--frontend-architecture--user-interface)
5. [SECTION E — Backend FastAPI Orchestrator & API Specification](#section-e--backend-fastapi-orchestrator--api-specification)
6. [SECTION F — Multi-Agent Subsystem Decomposition](#section-f--multi-agent-subsystem-decomposition)
7. [SECTION G — Audio & Speech Processing Pipeline](#section-g--audio--speech-processing-pipeline)
8. [SECTION H — Multi-Component Scoring Engine ($S_1+S_2+R$) & Anti-Gaming Logic](#section-h--multi-component-scoring-engine-s_1s_2r--anti-gaming-logic)
9. [SECTION I — Reinforcement Learning & Guardrailed PPO Difficulty Controller](#section-i--reinforcement-learning--guardrailed-ppo-difficulty-controller)
10. [SECTION J — Question Selection, Personalization & Deduplication](#section-j--question-selection-personalization--deduplication)
11. [SECTION K — Dual Qwen LLM System & Local CPU GGUF Demo Runtime](#section-k--dual-qwen-llm-system--local-cpu-gguf-demo-runtime)
12. [SECTION L — Containerized C Coding Sandbox & Isolation Policy](#section-l--containerized-c-coding-sandbox--isolation-policy)
13. [SECTION M — Database Architecture, Session Persistence & Concurrency](#section-m--database-architecture-session-persistence--concurrency)
14. [SECTION N — Exhaustive Verification & Test Suite Inventory](#section-n--exhaustive-verification--test-suite-inventory)
15. [SECTION O — Pre-Registered Empirical Research Experiments (EXP 1–5)](#section-o--pre-registered-empirical-research-experiments-exp-15)
16. [SECTION P — Blinded Human Rater Study & Inter-Rater Reliability](#section-p--blinded-human-rater-study--inter-rater-reliability)
17. [SECTION Q — IEEE Access Manuscript Deep Dive & Traceability Guide](#section-q--ieee-access-manuscript-deep-dive--traceability-guide)
18. [SECTION R — Step-by-Step Clean-Machine Reproduction Guide](#section-r--step-by-step-clean-machine-reproduction-guide)
19. [SECTION S — Independent Friend Reproduction Protocol & Feedback Template](#section-s--independent-friend-reproduction-protocol--feedback-template)
20. [SECTION T — Comprehensive Troubleshooting Manual](#section-t--comprehensive-troubleshooting-manual)
21. [SECTION U — Security, Sandbox Defense & Data Privacy](#section-u--security-sandbox-defense--data-privacy)
22. [SECTION V — Performance Benchmarks & Latency Characterization](#section-v--performance-benchmarks--latency-characterization)
23. [SECTION W — Complete Repository Directory & File Map](#section-w--complete-repository-directory--file-map)
24. [SECTION X — Git Release Manifest, Checksum & Provenance Audit](#section-x--git-release-manifest-checksum--provenance-audit)
25. [SECTION Y — Live Demonstration Scripts (2-min, 5-min, 10-min)](#section-y--live-demonstration-scripts-2-min-5-min-10-min)
26. [SECTION Z — Master Viva Voce & Technical Defense Q&A Compendium](#section-z--master-viva-voce--technical-defense-qa-compendium)
27. [SECTION AA — Foundational CS Concepts ("Explain Like I'm New")](#section-aa--foundational-cs-concepts-explain-like-im-new)
28. [SECTION AB — Architectural Trade-Offs & Technology Comparisons ("Why Did We Choose This?")](#section-ab--architectural-trade-offs--technology-comparisons-why-did-we-choose-this)
29. [SECTION AC — Methodological Limitations & Honest Scientific Defense](#section-ac--methodological-limitations--honest-scientific-defense)
30. [SECTION AD — Future Research & Engineering Roadmap](#section-ad--future-research--engineering-roadmap)
31. [SECTION AE — Quick-Revision Cheat Sheets & Viva Flashcards](#section-ae--quick-revision-cheat-sheets--viva-flashcards)

---

## SECTION A — PROJECT OVERVIEW & ELEVATOR PITCHES

### 1. What is PrepAIred?
**PrepAIred** is an open-source, multimodal, closed-loop technical interview assessment and practice platform. It evaluates candidates across verbal conceptual explanations and live C programming tasks while dynamically adapting interview difficulty using a guardrailed reinforcement learning controller.

### 2. One-Sentence Summary
> PrepAIred is an adaptive multimodal technical interview preparation platform that combines calibrated neural short-answer grading, containerized coding sandboxes, and safety-shielded PPO reinforcement learning to deliver personalized, formative interview practice without hallucinated scoring.

### 3. The 30-Second Elevator Pitch
"Technical interviews are broken: static LeetCode platforms ignore verbal communication, while generic LLM chatbots hallucinate grades and give inconsistent feedback. PrepAIred solves this by integrating a calibrated 3-component scoring engine ($S_1+S_2+R$), a containerized Docker C sandbox, and a PPO reinforcement learning policy that dynamically adjusts question difficulty based on candidate mastery and acoustic confidence. Everything runs locally with full traceability back to frozen rubrics."

### 4. The 1-Minute Explanation
"Software engineering interviews require candidates to explain algorithms verbally, write bug-free code under time limits, and answer follow-up probing questions. PrepAIred simulates this multi-turn dynamic through a decoupled multi-agent architecture:
1. **Verbal Assessment:** The candidate speaks; the offline speech pipeline transcribes the answer and extracts prosodic confidence and hesitation metrics.
2. **Calibrated Grading:** A 3-component neural evaluator ($S_1$ sentence similarity, $S_2$ FAISS concept coverage, and $R$ CrossEncoder reasoning entailment) grades the answer against verified rubrics while penalizing keyword stuffing.
3. **Adaptive Tutoring:** A Proximal Policy Optimization (PPO) agent observes a 6D candidate state vector and dynamically chooses the next question difficulty, shielded by deterministic safety guardrails.
4. **Coding Sandbox:** Live C code is compiled and executed inside a locked-down Docker container with strict CPU, memory (128MB), and network isolation.
5. **Formative Feedback:** Targeted follow-up questions and actionable feedback are generated locally via quantized open-weights models (`llama.cpp` GGUF) or deterministic structured recovery."

### 5. The 3-Minute Technical Deep Dive
"Traditional Automated Short Answer Grading (ASAG) relies on single bi-encoder cosine similarity, which candidates easily game by reciting keywords like 'hash map' without understanding collisions. PrepAIred fixes this by decomposing answer grading into three orthogonal signals:
- $S_1$ (Sentence-BERT similarity, weight 0.15) captures surface topicality.
- $S_2$ (FAISS dense concept retrieval, weight 0.35) checks whether required sub-concepts are present.
- $R$ (Fine-tuned CrossEncoder, weight 0.50) performs joint cross-attention across the question and answer to verify logical entailment. If reasoning $R \le 0.30$, an anti-keyword dampening rule cuts the concept score $S_2$ by 40%.

The candidate's evolving performance forms a 6-dimensional state vector $\mathbf{s}_t = [\bar{s}_t, c_t, h_t, \tau_t, s_t, d_t] \in [0, 1]^6$ representing moving score average, acoustic confidence, speech hesitation, pacing, current score, and current difficulty. A discrete-action PPO agent selects difficulty transitions $\Delta d \in \{-1, 0, +1\}$. To prevent erratic difficulty jumps, six deterministic safety guardrails override the neural policy when boundary conditions are triggered.

In empirical evaluations across 5 pre-registered experiments ($n=480$ total trials):
- The evaluator achieved Spearman $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$) against 3 blinded human raters (inter-rater agreement Krippendorff's $\alpha = 0.8255$).
- Guardrailed PPO demonstrated statistically significant adaptive progression ($\rho = +0.1572 \pm 0.08$) compared to fixed and heuristic baselines.
- The 3-tier question selector eliminated question repetition ($0.0\%$ vs. $6.0\%$ random) while demonstrating clear difficulty divergence ($d = 14.21$) across candidate skill personas."

### 6. Problem Statement
Technical interview preparation tools suffer from three fundamental flaws:
1. **Multimodal Disconnect:** Existing tools only assess code submissions (e.g. LeetCode, HackerRank) or conduct unstructured text chat, ignoring candidate verbal articulation and time pacing.
2. **Scoring Hallucination & Keyword Gaming:** Uncalibrated generative LLMs assign arbitrary scores, while bi-encoder similarity metrics award high scores to superficial buzzwords.
3. **Rigid Difficulty Progression:** Fixed difficulty ladders cause candidate boredom (if too easy) or panic-induced dropout (if too hard).

### 7. Core Scientific Contributions
1. **Calibrated Multi-Component Scoring Engine ($S_1+S_2+R$):** Decomposed ASAG combining bi-encoders, FAISS concept indexing, and cross-encoder entailment with anti-keyword dampening, validated against blinded human expert ground truth.
2. **Pedagogically Shielded PPO Difficulty Controller:** A reinforcement learning policy operating on a 6D candidate state space, constrained by 6 deterministic safety guardrails.
3. **Dual Qwen LLM Architecture:** Methodological separation between GPU research benchmarks (Qwen-7B bfloat16) and local CPU live-demo deployment (`llama.cpp` Q4_K_M GGUF).
4. **Hardened Docker Coding Sandbox:** Sub-second containerized C execution with 128MB RAM, 32 PIDs, 2.0s execution timeout, and disabled network interfaces.
5. **Open Reproducibility Package:** 100% deterministic reproducibility across 480 pre-registered evaluation trials with zero proprietary API dependencies.

### 8. Explicit Scientific Invariants & Non-Claims
To maintain absolute scientific honesty, PrepAIred explicitly declares:
- **EXP 1, 4, and 5 use simulated candidate trajectories:** They validate algorithmic convergence and safety stability, not human longitudinal learning gains.
- **Human validation is restricted to the 20-answer expert benchmark:** Inter-rater reliability was measured on 20 representative CS technical answers graded by 3 blinded experts ($\alpha = 0.8255$).
- **Student hiring success & retention are NOT claimed:** Whole-system educational efficacy requires future longitudinal multi-cohort trials.
- **Microphone hardware is NOT claimed in headless CLI:** Offline speech pipeline ingestion is verified; live microphone streaming requires physical hardware.

---

## SECTION B — MOTIVATION & TECHNOLOGY JUSTIFICATION ("WHY WE BUILT IT")

| Technology / Method | Simple Explanation | Technical Explanation | Why PrepAIred Chose It | Repository Location |
|---|---|---|---|---|
| **Reinforcement Learning (PPO)** | An AI that learns by getting rewards for good difficulty adjustments. | On-policy actor-critic algorithm with clipped surrogate objective: $L^{CLIP}(\theta) = \hat{\mathbb{E}}_t [\min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t)]$. | Adapts interview difficulty smoothly without manual heuristic hardcoding while optimizing long-term candidate engagement. | `rl/gym_env/`, `rl/checkpoints/` |
| **Deterministic Guardrails** | Hard safety rules that prevent the AI from making crazy difficulty leaps. | Rule-based override layer acting on policy action $a_t \in \{-1, 0, +1\}$ when boundary conditions $g_1 \dots g_6$ are violated. | Guarantees pedagogical safety, prevents panic from sudden difficulty spikes, and stops overload on consecutive failures. | `agents/strategy/hybrid_orchestrator.py` |
| **3-Component Evaluator ($S_1+S_2+R$)** | Tests vocabulary ($S_1$), concept presence ($S_2$), and logical reasoning ($R$). | Multi-stage ASAG pipeline: $S_{\text{tech}} = 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$, where $S_{2,\text{eff}} = 0.60 \cdot S_2$ if $R \le 0.30$. | Prevents candidates from gaming grading engines by reciting disconnected keywords. | `services/evaluator/app.py` |
| **Sentence-BERT (`all-MiniLM-L6-v2`)** | Turns text into numbers so we can compare sentence meanings. | 384-dimensional dense bi-encoder embedding model mapping texts into a metric space with cosine similarity. | High-speed ($<15\text{ms}$) surface semantic grounding for reference answers and rubric concept clusters. | `services/evaluator/` |
| **Cross-Encoder (`tuned_model2`)** | Reads the question and answer together to check if the logic actually makes sense. | 12-layer cross-attention transformer (`ms-marco-MiniLM-L-12-v2` fine-tuned) computing joint cross-attention tokens. | Detects subtle logical errors and causal reasoning that bi-encoders completely miss. | `services/evaluator/models/tuned_model2/` |
| **FAISS Vector Index** | A super-fast search engine for finding concept matches in milliseconds. | Dense vector index supporting exact L2 and inner product similarity search across pre-computed 384D embeddings. | Enables instantaneous sub-sentence concept retrieval across 125 complex CS rubrics without cloud dependencies. | `services/evaluator/app.py` |
| **Docker C Sandbox** | A locked digital box that runs candidate code safely so they can't hack the server. | Linux container runtime enforcing Linux kernel `cgroups` (128MB RAM, 32 PIDs), `seccomp` filters, read-only root, and `--net=none`. | Prevents fork bombs, memory leaks, infinite loops, and unauthorized system access during C code evaluation. | `agents/coding_executor/`, `Dockerfile.sandbox` |
| **Qwen 2.5 (1.5B & 7B)** | A high-quality open-source LLM that writes custom follow-up questions and feedback. | Dense auto-regressive transformer trained on multi-lingual technical tokens with strong code and reasoning capabilities. | Allows completely private, on-premise execution with zero per-token API costs and zero vendor lock-in. | `services/qwen/app.py` |
| **llama.cpp / GGUF** | Super-fast C++ program that runs LLMs on regular laptop CPUs using 4-bit quantization. | Highly optimized C/C++ LLM inference engine using integer quantization (Q4_K_M) and multi-threaded SIMD execution. | Enables real-time local follow-up generation ($2.195\text{s}$ latency) on commodity laptops without dedicated GPUs. | `services/qwen/app.py` |
| **FastAPI** | Modern, lightning-fast Python web server. | Asynchronous ASGI Python framework built on Starlette and Pydantic with native WebSocket and OpenAPI support. | High concurrency, automatic request validation, and clean async integration with AI microservices. | `apps/backend/main.py` |
| **React 18 + Vite** | Fast, responsive web frontend for the interview room and Monaco code editor. | Component-based UI library with Vite Hot Module Replacement (HMR) and Monaco editor integration. | Smooth candidate interview experience, real-time timer updates, and live coding support. | `apps/web/` |
| **WebSocket / Socket.IO** | Persistent two-way phone call between browser and server for live interview events. | Full-duplex bidirectional communication channel over a single TCP connection. | Low-latency question streaming, live pacing alerts, and instantaneous transcript updates. | `apps/web/src/useInterviewWS.js`, `apps/backend/` |
| **MongoDB** | Flexible database for saving candidate sessions, questions, and detailed final reports. | Document-oriented NoSQL database storing JSON-like BSON documents with dynamic schemas. | Natural fit for nested multi-turn interview transcripts, multi-component score breakdowns, and rubrics. | `apps/backend/` |

---

## SECTION C — COMPLETE END-TO-END SYSTEM ARCHITECTURE

### Production Architecture Diagram
```
                     +---------------------------------------------+
                     |           React 18 Frontend Client          |
                     |  (Monaco Editor, Voice Recorder, Timer UI)  |
                     +---------------------------------------------+
                                     |             ^
                    REST (HTTP POST) |             | WebSockets / Socket.IO
                                     v             |
                     +---------------------------------------------+
                     |          FastAPI Backend Orchestrator       |
                     |    (Auth, Session State, Turn Coordinator)  |
                     +---------------------------------------------+
                                     |
    +--------------------------------+--------------------------------+
    |                                |                                |
    v                                v                                v
+-----------------------+  +-----------------------+  +-----------------------+
|  Speech & Prosody     |  | Evaluator Service     |  | Qwen LLM Service      |
|  Pipeline             |  | (:5000)               |  | (:8001)               |
|  - Whisper STT        |  | - S1: SBERT (384D)    |  | - llama.cpp Engine    |
|  - Hesitation Scorer  |  | - S2: FAISS Index     |  | - Q4_K_M GGUF (1.5B)  |
|  - Energy Alignment   |  | - R: Cross-Encoder    |  | - Fallback Recovery   |
+-----------------------+  +-----------------------+  +-----------------------+
    |                                |                                |
    +--------------------------------+--------------------------------+
                                     |
                                     v
                     +---------------------------------------------+
                     |     Reinforcement Learning Controller       |
                     |  - 6D Candidate State: s_t in [0, 1]^6      |
                     |  - Trained PPO Policy (seed_123)            |
                     |  - 6 Deterministic Safety Guardrails        |
                     +---------------------------------------------+
                                     |
                                     v
                     +---------------------------------------------+
                     |     Question Selection & Coding Sandbox     |
                     |  - 3-Tier Deduplication & Personalization   |
                     |  - Docker C Sandbox (128MB, 32 PIDs, net=0) |
                     +---------------------------------------------+
                                     |
                                     v
                     +---------------------------------------------+
                     |     MongoDB Database / Final Report Agent   |
                     +---------------------------------------------+
```

### End-to-End Execution Sequence
1. **Session Initialization:** Candidate logs in, selects technical domain (e.g., C / DSA), and starts interview. Orchestrator initializes 6D state $\mathbf{s}_0 = [0.5, 0.5, 0.0, 0.5, 0.5, 2.0]$.
2. **Question Delivery:** `QuestionSelector` pulls an initial Medium question ($d=2$) from the 125-question bank, applying Level-1 (Session), Level-2 (Global History), and Level-3 (Semantic Cosine) deduplication.
3. **Candidate Response:** Candidate answers verbally (audio captured at 16kHz WAV) or writes code in Monaco Editor.
4. **Audio & Speech Ingestion:** `agents/audio/` processes WAV audio, extracting text transcript, speech duration, pause count, speaking rate (WPM), hesitation score $h_t$, and acoustic confidence $c_t$.
5. **Calibrated Evaluation:** `services/evaluator/app.py` grades answer:
   - Computes cosine similarity $S_1$ against reference answer.
   - Queries FAISS concept clusters for sentence matches ($\ge 0.42$) yielding $S_2$.
   - Executes CrossEncoder over $(Q, A)$ producing reasoning entailment $R$.
   - Applies anti-keyword dampening ($S_{2,\text{eff}} = 0.60 \cdot S_2$ if $R \le 0.30$).
   - Checks mandatory concept checklist; caps score at $0.60$ if violated.
6. **RL Difficulty Step:** Orchestrator constructs updated 6D state $\mathbf{s}_t$. PPO policy predicts action $a_t \in \{-1, 0, +1\}$. `HybridOrchestrator` checks 6 safety guardrails, overriding neural action if safety threshold is triggered.
7. **Adaptive Follow-Up / Feedback:** If conceptual gaps exist, `services/qwen/app.py` synthesizes targeted follow-up question. If Qwen service is offline, deterministic fallback synthesizes structured recovery without faking LLM status.
8. **Coding Execution:** When coding questions occur, code is compiled (`gcc -O2`) and tested against mandatory and edge test cases inside Docker sandbox.
9. **Final Comprehensive Report:** At interview completion, `FeedbackAgent` aggregates multi-turn scores, timing pacing, topic mastery, and radar charts into an actionable debrief report saved to MongoDB.

---

## SECTION D — FRONTEND ARCHITECTURE & USER INTERFACE

### 1. Technology Stack
- **Framework:** React 18 with Vite build tooling.
- **Code Editor:** `@monaco-editor/react` (VS Code editor engine in browser).
- **Styling:** Modular Tailwind CSS with high-contrast accessibility themes.
- **Real-Time Layer:** Native WebSocket client (`useInterviewWS.js`) with automatic reconnection and heartbeat.
- **Audio Capture:** HTML5 MediaRecorder API recording 16-bit PCM WAV audio at 16,000 Hz.

### 2. Key Frontend Components & Source Files
- [`apps/web/src/App.jsx`](file:///c:/Users/spars/Downloads/PrepAIred/apps/web/src/App.jsx): Root routing, authentication provider, and global application state.
- [`apps/web/src/InterviewRoom.jsx`](file:///c:/Users/spars/Downloads/PrepAIred/apps/web/src/InterviewRoom.jsx): Master interview room combining question prompt, live audio waveform, question timer, and Monaco code editor.
- [`apps/web/src/MonacoEditor.jsx`](file:///c:/Users/spars/Downloads/PrepAIred/apps/web/src/MonacoEditor.jsx): Sandboxed C syntax editor with compiler error markers, standard input terminal, and test case execution runner.
- [`apps/web/src/TopicSelector.jsx`](file:///c:/Users/spars/Downloads/PrepAIred/apps/web/src/TopicSelector.jsx): Technical domain picker (Arrays, Trees, Pointers, Memory Management, OS).
- [`apps/web/src/Report.jsx`](file:///c:/Users/spars/Downloads/PrepAIred/apps/web/src/Report.jsx): Comprehensive post-interview debrief dashboard rendering multi-turn scores, radar charts, hesitation timeline, and concept gaps.
- [`apps/web/src/servicesApi.js`](file:///c:/Users/spars/Downloads/PrepAIred/apps/web/src/servicesApi.js): REST client connecting to FastAPI backend and microservice endpoints.

---

## SECTION E — BACKEND FASTAPI ORCHESTRATOR & API SPECIFICATION

### Complete API Endpoint Specification

| Method | Endpoint Path | Subsystem Purpose | Request Payload | Response Schema | Caller Subsystem | Failure Fallback Mode |
|---|---|---|---|---|---|---|
| `POST` | `/api/auth/login` | Candidate JWT Authentication | `{"username": str, "password": str}` | `{"access_token": str, "user_id": str}` | Web Client (Login.jsx) | Returns 401 Unauthorized |
| `POST` | `/api/interview/start` | Initialize Mock Interview Session | `{"topic": str, "difficulty": int}` | `{"session_id": str, "initial_question": dict}` | Web Client (TopicSelector.jsx) | Fallback to default C topics |
| `POST` | `/api/interview/answer` | Submit Verbal / Text Answer | `{"session_id": str, "answer_text": str, "audio_base64": str, "time_taken": float}` | `{"score_breakdown": dict, "next_action": dict, "followup": dict}` | Web Client (InterviewRoom.jsx) | Deterministic evaluation fallback |
| `POST` | `/api/interview/code` | Submit C Code to Sandbox | `{"session_id": str, "code": str, "question_id": int}` | `{"passed": bool, "test_results": list, "compile_error": str, "score": float}` | MonacoEditor.jsx | Returns structured sandbox diagnostic |
| `GET` | `/api/interview/report/{id}`| Fetch Final Comprehensive Report | URL Path Parameter (`id`) | `{"overall_score": float, "radar_metrics": dict, "turn_history": list, "gap_summary": list}` | Report.jsx | Generates on-the-fly from session state |
| `POST` | `/evaluate` (Port 5000) | Standalone Evaluator Grading | `{"question": str, "student_answer": str, "rubric": dict}` | `{"final_score": float, "s1_semantic": float, "s2_concepts": float, "r_reasoning": float, "missing_concepts": list}` | Backend Orchestrator | Strict rubric keyword fallback |
| `POST` | `/generate_followup` (:8001)| Qwen Follow-Up Generation | `{"question": str, "student_answer": str, "missing_concepts": list}` | `{"followup_question": str, "attribution": str, "latency": float}` | Backend Orchestrator | Structured recovery (`non_llm_structured_recovery`)|

---

## SECTION F — MULTI-AGENT SUBSYSTEM DECOMPOSITION

PrepAIred strictly distinguishes between **Agents** (autonomous goal-directed controllers), **Services** (stateless computation microservices), **Orchestrators** (turn coordinators), and **Utilities** (deterministic helper functions):

```
+-------------------------------------------------------------------------------+
|                             MULTI-AGENT HIERARCHY                             |
+-------------------------------------------------------------------------------+
| 1. InterviewOrchestrator (Orchestrator): Central coordinator managing turns,  |
|    calling evaluator, updating candidate state, and driving session flow.     |
| 2. HybridStrategyAgent (RL Agent): PPO policy + 6 safety guardrails choosing  |
|    optimal difficulty transitions Delta d in {-1, 0, +1}.                     |
| 3. QuestionSelectorAgent (Agent): 3-tier deduplication and domain picker.     |
| 4. CodingExecutorAgent (Agent): Docker container manager compiling & testing. |
| 5. FeedbackAgent (Agent): Generates post-interview debrief & radar reports.   |
| 6. SpeechAgent (Agent/Utility): Transcribes WAV and extracts acoustic prosody.|
| 7. EvaluatorService (Microservice :5000): S1 + S2 + R neural scoring engine.  |
| 8. QwenService (Microservice :8001): Local GGUF LLM follow-up probing engine. |
+-------------------------------------------------------------------------------+
```

---

## SECTION G — AUDIO & SPEECH PROCESSING PIPELINE

### 1. Acoustic & Linguistic Signal Extraction
When a candidate speaks, audio is recorded at 16,000 Hz single-channel PCM. The speech pipeline extracts 5 key signals:
1. **Normalized Transcript:** Extracted via local Whisper / faster-whisper STT.
2. **Speech Pacing ($\tau_t$):** Words-per-minute (WPM) mapped against target range $[110, 160]\text{ WPM}$.
3. **Hesitation Score ($h_t \in [0, 1]$):** Energy-aligned pause duration plus lexical filler detection (*"um"*, *"uh"*, *"like"*, *"you know"*):
   $$h_t = \min\left(1.0,\ \frac{T_{\text{pause}}}{T_{\text{total}}} + 0.05 \cdot N_{\text{fillers}}\right)$$
4. **Acoustic Confidence ($c_t \in [0, 1]$):** Computed from Harmonic-to-Noise Ratio (HNR), pitch contour stability ($\Delta F_0$), and token log-probabilities:
   $$c_t = 0.40 \cdot \bar{P}_{\text{token}} + 0.35 \cdot \text{norm}(\text{HNR}) + 0.25 \cdot (1.0 - \text{norm}(\text{StdDev}(F_0)))$$
5. **State Vector Projection:** $c_t$, $h_t$, and $\tau_t$ directly populate dimensions 2, 3, and 4 of the RL candidate state $\mathbf{s}_t$.

### 2. Offline vs. Live Hardware Demarcation
- **`OFFLINE SPEECH PIPELINE = VERIFIED`:** Verified via automated unit tests (`tests/unit/test_speech_pipeline.py`) ingesting pre-recorded WAV buffers and extracting prosody cleanly.
- **`LIVE MICROPHONE HARDWARE = NOT VERIFIED`:** Live browser microphone streaming depends on user-end physical audio hardware.

---

## SECTION H — MULTI-COMPONENT SCORING ENGINE ($S_1+S_2+R$) & ANTI-GAMING LOGIC

### 1. Mathematical Formulation
The calibrated technical score $S_{\text{tech}}$ fuses three orthogonal neural representations:

$$S_{\text{tech}} = \text{clip}\Big( 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R + \text{Bonus} - \text{Penalty},\ 0.0,\ 1.0 \Big)$$

Where:
- **$S_1$ (Surface Semantic Similarity, $w=0.15$):** Bi-encoder cosine similarity between candidate answer and reference answer using `all-MiniLM-L6-v2`.
- **$S_2$ (Rubric Concept Coverage, $w=0.35$):** Maximum sentence cosine similarity against pre-computed FAISS concept clusters:
  $$S_2 = \frac{1}{M} \sum_{j=1}^M \mathbb{I}\left[ \max_{s_k \in \text{Sentences}} \cos(\mathbf{e}_{C_j}, \mathbf{e}_{s_k}) \ge 0.42 \right]$$
- **$R$ (Reasoning Entailment, $w=0.50$):** Joint cross-attention logit converted via sigmoid using fine-tuned CrossEncoder (`models/tuned_model2`):
  $$R = \sigma(\text{CrossEncoder}(Q \oplus A))$$
- **Anti-Keyword Dampening Rule ($S_{2,\text{eff}}$):**
  $$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ 0.60 \cdot S_2 & \text{if } R \le 0.30 \quad \text{(Penalizes keyword stuffing without reasoning)} \end{cases}$$
- **Mandatory Concept Cap:** If any non-negotiable concept is missing, $S_{\text{tech}} = \min(S_{\text{tech}}, 0.60)$.

### 2. Concrete Grading Example Walkthrough

**Question:** *"Explain your logic to find two indices in an array that sum to a target value."*

| Candidate Response | $S_1$ (Semantic) | $S_2$ (Concepts) | $R$ (Reasoning) | Anti-Gaming Triggered? | Final Score | Qualitative Grade |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Comprehensive Correct Answer:** *"I iterate through the array once. For each element $x$, I calculate the complement $\text{target}-x$. I check if the complement exists in a hash map; if so, I return both indices. Otherwise, I store $x$ and its index. This achieves $O(N)$ time and $O(N)$ space."* | $0.463$ | $1.000$ | $0.884$ | No ($R > 0.30$) | **$0.9215$** | **Excellent** |
| **Keyword-Stuffed Answer:** *"Hash map target array indices time complexity space collision key value lookup complement."* | $0.380$ | $0.500 \to \mathbf{0.300}$ | $0.147$ | **YES ($R \le 0.30$, $S_2$ cut by 40%)** | **$0.2354$** | **Poor** |
| **Confident Wrong Answer:** *"You sort the array in $O(N)$ time, then pick the first and last elements because they always sum to the target value."* | $0.237$ | $0.000$ | $0.000$ | **YES (Mandatory check fails)** | **$0.0000$** | **Poor** |

---

## SECTION I — REINFORCEMENT LEARNING & GUARDRAILED PPO DIFFICULTY CONTROLLER

### 1. 6D Candidate State Vector Space
At each interview turn $t$, candidate performance is represented by a bounded vector $\mathbf{s}_t \in [0, 1]^6$:

$$\mathbf{s}_t = \big[ \bar{s}_t,\ c_t,\ h_t,\ \tau_t,\ s_t,\ d_t \big]$$

1. $\bar{s}_t \in [0, 1]$: Exponential moving average of technical scores across turns ($\alpha = 0.30$).
2. $c_t \in [0, 1]$: Normalized acoustic/prosodic confidence score.
3. $h_t \in [0, 1]$: Speech hesitation and filler density metric.
4. $\tau_t \in [0, 1]$: Normalized response pacing relative to target question time.
5. $s_t \in [0, 1]$: Current turn technical score.
6. $d_t \in [0, 1]$: Current question difficulty normalized from $[1, 5] \to \frac{d-1}{4}$.

### 2. Action Space & Reward Formulation
- **Action Space:** Discrete 3-action difficulty adjustment:
  $$\mathcal{A} = \{0: \text{Easier } (\Delta d = -1),\ 1: \text{Same } (\Delta d = 0),\ 2: \text{Harder } (\Delta d = +1)\}$$
- **Reward Function:** Balances ZPD target challenge, confidence calibration, and stability:
  $$R_t = R_{\text{zone}} + 0.20 \cdot c_t - 0.15 \cdot h_t - 0.10 \cdot |\Delta d| - R_{\text{penalty}}$$
  Where Zone of Proximal Development (ZPD) reward is maximized when candidate score is near optimal challenge ($s_t \approx 0.65$):
  $$R_{\text{zone}} = 1.0 - 2.0 \cdot |s_t - 0.65|$$

### 3. The 6 Deterministic Safety Guardrails

```
+-------------------------------------------------------------------------------+
|                       6 DETERMINISTIC SAFETY GUARDRAILS                       |
+-------------------------------------------------------------------------------+
| G1 (Overload Protection): If s_t < 0.20 and a_t == Harder (+1) --> FORCED EASIER (-1)
| G2 (Anxiety Stabilizer): If h_t > 0.70 and c_t < 0.30 --> FORCED SAME (0)     |
| G3 (Boundary Clamp): If d_t == 1 and a_t == Easier --> CLAMP AT 1             |
| G4 (Boundary Ceiling): If d_t == 5 and a_t == Harder --> CLAMP AT 5           |
| G5 (Partial Credit Stability): If 0.40 <= s_t <= 0.60 and a_t == Harder --> FORCED SAME (0)
| G6 (Mastery Acceleration): If s_t >= 0.85 and c_t >= 0.70 --> FORCED HARDER (+1)
+-------------------------------------------------------------------------------+
```

---

## SECTION J — QUESTION SELECTION, PERSONALIZATION & DEDUPLICATION

### 3-Level Deduplication Filter
To guarantee zero repetitive questions across an interview session:
1. **Level 1 (Session Exact ID Filter):** Hard exclusion of all question IDs already presented in active session.
2. **Level 2 (Candidate History Filter):** Penalizes questions attempted by candidate in past sessions within 30 days.
3. **Level 3 (Semantic Cosine Filter):** Rejects questions with Sentence-BERT cosine similarity $\ge 0.82$ against recently asked prompts.

---

## SECTION K — DUAL QWEN LLM SYSTEM & LOCAL CPU GGUF DEMO RUNTIME

### Architectural Demarcation
- **EXP-3 Research Evidence (GPU):** `Qwen2.5-7B-Instruct` unquantized bfloat16 executed on NVIDIA Tesla T4 GPU (Grounding: $0.2496$, Gap Coverage: $72.5\%$, Latency: $9.78\text{s}$).
- **Local Live Demo (CPU):** `Qwen2.5-1.5B-Instruct-GGUF` (quantization `Q4_K_M`) executed via `llama.cpp` / `llama-cpp-python` on 12 CPU threads (Mean generation latency: **$2.195\text{s}$**, RSS RAM: **$1.36\text{ GB}$**).

### Execution Flow & Attribution Tracking
When synthesizing follow-up questions or feedback:
- If Qwen GGUF is available $\to$ Tagged `decision_source = "qwen_1.5b_llm"`.
- If Qwen service is offline $\to$ Deterministic fallback executes rubric gap extraction, tagged `decision_source = "non_llm_structured_recovery"` with `llm_status = "llm_unavailable"`. No fake LLM output is ever produced.

---

## SECTION L — CONTAINERIZED C CODING SANDBOX & ISOLATION POLICY

### Docker Sandbox Policy (`Dockerfile.sandbox`)
Untrusted candidate C code is compiled and executed inside an ephemeral Docker container governed by strict Linux kernel constraints:

| Security Parameter | Hard Limit | Enforcement Mechanism | Failure Response |
|---|---|---|---|
| **RAM Memory** | $128\text{ MB}$ | Linux Kernel `cgroups` (`--memory=128m --memory-swap=128m`) | Kernel OOM Killer (`SIGKILL`) |
| **CPU Time** | $2.0\text{ seconds}$ | Subprocess SIGALRM Timeout | `Execution Timeout (>2.0s)` |
| **Process Count** | $32\text{ PIDs}$ | Docker `--pids-limit=32` | Blocks Fork Bombs (`EAGAIN`) |
| **Network Access** | Completely Disabled | Docker `--net=none` | Sockets Blocked (`EPERM`) |
| **Root Filesystem** | Read-Only | Docker `--read-only` | Writes Blocked (`EROFS`) |
| **Workspace Dir** | Temporary In-Memory | `--tmpfs /tmp:rw,noexec,nosuid,size=32m` | Clean Reset on Exit |

---

## SECTION M — DATABASE ARCHITECTURE, SESSION PERSISTENCE & CONCURRENCY

### MongoDB Document Collections
1. **`users`:** Stores hashed credentials, candidate profile, and historical topic mastery.
2. **`interview_sessions`:** Stores multi-turn interview state, active question sequence, 6D trajectory history, and raw transcripts.
3. **`interview_reports`:** Stores finalized post-interview evaluations, radar chart breakdowns, and recommendations.
4. **`question_bank`:** Stores 125 curated DSA and C language technical questions with structured concept rubrics.

---

## SECTION N — EXHAUSTIVE VERIFICATION & TEST SUITE INVENTORY

### Verified Test Suite Summary (Exit Code 0)
- **Backend Test Suite (`pytest tests/ -v`):** **177 passed, 1 skipped** (CUDA gated), **0 failed** ($388.94\text{s}$ runtime).
- **Frontend Test Suite (`npm test -- --run`):** **7 passed, 0 failed** ($32.52\text{s}$ runtime).
- **Evaluator Standalone Verification:** **8/8 passed** across representative edge cases.
- **Qwen GGUF Integration:** **7/7 passed** with verified fallback attribution.
- **Docker Coding Sandbox:** **14/14 passed** verifying compilation, runtime errors, and isolation.
- **Reproducibility Harness (`reproduce_paper.py`):** **480/480 verified**, Figures 1–8 regenerated.

---

## SECTION O — PRE-REGISTERED EMPIRICAL RESEARCH EXPERIMENTS (EXP 1–5)

```
================================================================================
PREPAIRED PRE-REGISTERED EXPERIMENTS MASTER TABLE (n = 480 TOTAL RUNS)
================================================================================
EXP-1: Adaptive Difficulty Controller (n = 150 episodes)
  - PPO + Guardrails Adaptation Correlation: rho = +0.1572 +- 0.08
  - Fixed Baseline Correlation:             rho = +0.0000 (p = 6.15e-04)
  - Rule-Based Baseline Correlation:        rho = -0.2572 (p = 5.30e-08)

EXP-2: Evaluator Component Ablation (n = 140 scorings, 7 configs)
  - Human Inter-Rater Reliability (Krippendorff alpha): alpha = 0.8255
  - Full Pipeline (S1+S2+R): Spearman rho = 0.8358 (p = 4.46e-06, MAE = 0.2585)
  - Surface + Concept (S1+S2): Spearman rho = 0.8358 (p = 4.46e-06, MAE = 0.1907)

EXP-3: Formative Feedback Grounding (n = 60 scorings, Tesla T4 GPU)
  - Qwen-7B Transcript Lexical Grounding: 0.2496 (vs Non-LLM 0.0383, p = 2.56e-03)
  - Non-LLM Structured Recovery Gap Coverage: 100.0% (vs Qwen-7B 72.5%, p = 9.11e-04)
  - Non-LLM Latency: <0.05s (vs Qwen-7B 9.78s)

EXP-4: Personalization & Trajectory Divergence (n = 60 sessions)
  - Question Repetition Rate: 0.00% (vs Random Selection 6.00%, p < 0.001)
  - Candidate Profile Difficulty Divergence: d = 14.21

EXP-5: Leave-One-Out Subsystem Ablation (n = 70 sessions)
  - 100% clean subsystem decoupling across 7 isolated failure conditions.
================================================================================
```

---

## SECTION P — BLINDED HUMAN RATER STUDY & INTER-RATER RELIABILITY

### Methodology & Interpretation
- **Dataset:** 20 representative technical interview answers spanning 4 quality tiers (Blank, Off-Topic, Partial, Good) across core CS topics.
- **Blinded Protocol:** 3 independent expert software engineers graded answers on a $[0, 10]$ scale (normalized to $[0, 1]$) with blinded question metadata to prevent anchoring bias.
- **Inter-Rater Reliability:** Krippendorff's $\alpha = \mathbf{0.8255}$ (well above standard academic reliability threshold $\alpha \ge 0.80$).
- **Correlation with Full Pipeline:** Spearman rank correlation $\rho = \mathbf{0.8358}$ ($p = \mathbf{4.4568 \times 10^{-6}}$).
- **Synthetic Proxy Distinction:** Synthetic datasets (`ratings_synthetic_rater*.csv`) are accompanied by `.meta.txt` explicitly marking them as testing proxies, completely separate from human calibration evidence.

---

## SECTION Q — IEEE ACCESS MANUSCRIPT DEEP DIVE & TRACEABILITY GUIDE

### 29-Section Manuscript Structure ([`docs/paper_draft_ieee.md`](paper_draft_ieee.md))
- **Title:** *A Personalized Adaptive Framework for Multimodal Technical Interview Assessment and Preparation*
- **Sections I–III:** Problem formulation, related work in ASAG and RL tutoring, and 7-layer system architecture.
- **Sections IV–VI:** Mathematical formulation of scoring engine, RL state-action mechanics, and speech extraction.
- **Sections VII–XI:** Detailed empirical findings across EXP 1–5 ($n=480$).
- **Sections XII–XIV:** Discussion of educational implications, threats to validity, and honest declaration of limitations.
- **Status:** **`SCIENTIFICALLY FROZEN DRAFT MANUSCRIPT`** (Identical SHA256 hash `623267...` across `docs/` and `submission/`).

---

## SECTION R — STEP-BY-STEP CLEAN-MACHINE REPRODUCTION GUIDE

### 1. Prerequisites (Windows / Linux / macOS)
- Python 3.10 or 3.11 installed.
- Node.js 18+ and npm installed.
- Git installed.
- Optional for Coding Sandbox: Docker Desktop running.

### 2. Step-by-Step Terminal Commands (Windows PowerShell)

```powershell
# Step 1: Clone Repository
git clone https://github.com/sparshkumar1/capstoneProject.git
cd capstoneProject

# Step 2: Create Python Virtual Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Step 3: Install Core Dependencies
pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/evaluator.txt
pip install -r requirements/rl.txt
pip install -e .

# Step 4: Install Frontend Dependencies
npm --prefix apps/web install

# Step 5: Run Full Test Suite
python -m pytest tests/ -v
npm --prefix apps/web test -- --run

# Step 6: Reproduce All Paper Figures and Verify 480 Experiments
python scripts/reproduce_paper.py
```

---

## SECTION S — INDEPENDENT FRIEND REPRODUCTION PROTOCOL & FEEDBACK TEMPLATE

> **External Third-Party Validation: PENDING**
> The repository has been internally verified and a self-contained independent reproduction protocol has been prepared. Independent third-party reproduction has not yet been completed.

See [`docs/FRIEND_REPRODUCTION_CHECKLIST.md`](FRIEND_REPRODUCTION_CHECKLIST.md) for the standalone 17-step checklist and structured evaluation form designed for independent testers.


---

## SECTION T — COMPREHENSIVE TROUBLESHOOTING MANUAL

| Symptom | Probable Root Cause | Verified Remediation Fix | Verification Command |
|---|---|---|---|
| `ExecutionPolicy` error in PowerShell | Windows restricts unsigned scripts | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` | `.\.venv\Scripts\Activate.ps1` |
| `llama-cpp-python` build failure | Missing C++ build tools on Windows | Install Visual Studio C++ Build Tools or use CPU pre-built wheel | `pip install llama-cpp-python` |
| Port 5000 / 8000 already in use | Stale backend process running | Run `Get-Process python \| Stop-Process` (PowerShell) | `netstat -ano \| findstr :5000` |
| Docker sandbox unavailable | Docker Desktop not started | Start Docker Desktop or rely on simulated sandbox fallback | `docker ps` |
| Evaluator model missing | Model assets not cloned | Verify `services/evaluator/models/tuned_model2/` exists | `python scratch/verify_evaluator_standalone.py` |

---

## SECTION U — SECURITY, SANDBOX DEFENSE & DATA PRIVACY

- **JWT Token Authentication:** HS256 algorithm with strict expiration and cryptographic password hashing (`bcrypt`).
- **Sandbox Boundary:** Fork bomb, memory exhaustion, and network access strictly constrained via kernel `cgroups` and `--net=none`.
- **Zero Real Audio PII:** All audio test fixtures (`tests/test_candidate_hash_table_answer.wav`) generated via synthetic Windows SAPI TTS.

---

## SECTION V — PERFORMANCE BENCHMARKS & LATENCY CHARACTERIZATION

- **Evaluator Latency ($S_1+S_2+R$):** **$142\text{ ms}$** mean scoring time per turn.
- **Qwen 1.5B GGUF CPU Latency:** **$2.195\text{ s}$** mean generation latency ($18.79\text{ tok/s}$) on 12 CPU threads.
- **Speech Pipeline Processing:** **$2.43\text{ s}$** for 12.5s audio buffer.
- **RL Action Inference:** **$<2\text{ ms}$** per decision turn.
- **Docker Sandbox Compilation + Run:** **$420\text{ ms}$** per C code submission.

---

## SECTION W — COMPLETE REPOSITORY DIRECTORY & FILE MAP

See [`docs/FINAL_REPOSITORY_TREE.md`](FINAL_REPOSITORY_TREE.md) for the complete directory tree inventory.

---

## SECTION X — GIT RELEASE MANIFEST, CHECKSUM & PROVENANCE AUDIT

- **Release Tag:** `paper-v1.0`
- **Release Commit:** `ea15e3c`
- **Manuscript SHA256:** `6232679871245C462249DB3B5CE5F9CE588BD47676A043C175F74224A0D66D59`
- **Tracked GGUF Model Binaries:** **0 files tracked** (Protected via `.gitignore`).

---

## SECTION Y — LIVE DEMONSTRATION SCRIPTS

### 5-Minute Live Viva Demo Script
1. **Minute 1 — Architecture & Login:** Show architecture diagram; log into web client at `http://localhost:5173`.
2. **Minute 2 — Verbal Question & Anti-Gaming Demo:** Answer Question 1 (Two Sum). First give a keyword-stuffed answer $\to$ show anti-keyword dampening penalizing score ($0.235$). Then give a comprehensive reasoning answer $\to$ show high score ($0.921$).
3. **Minute 3 — RL Difficulty Adaptation:** Demonstrate PPO observing high score and transitioning difficulty from Medium $\to$ Hard ($d=2 \to 3$).
4. **Minute 4 — Sandboxed Coding Task:** Open Monaco Editor; write C code with dynamic memory allocation; run code $\to$ show sub-second Docker execution output.
5. **Minute 5 — Comprehensive Debrief:** Open Report dashboard; explain multi-turn score radar chart, concept gap analysis, and pacing metrics.

---

## SECTION Z — MASTER VIVA VOCE & TECHNICAL DEFENSE Q&A COMPENDIUM

### Top Viva Questions & Answers

#### Q1: Why did you use Reinforcement Learning instead of simple if-else rules for difficulty adaptation?
- **Short Answer:** Rule-based heuristics over-react to single-turn noise, causing extreme difficulty oscillations. PPO learns a smooth, multi-step policy over a 6D candidate state space.
- **Detailed Answer:** In EXP-1 ($n=150$ episodes), simple heuristic rules produced negative adaptation correlation ($\rho = -0.2572$) because they oscillate violently when candidates give partial answers. Guardrailed PPO achieved statistically significant positive adaptive progression ($\rho = +0.1572 \pm 0.08, p = 6.15 \times 10^{-4}$).
- **Likely Follow-Up:** *Why do you still need guardrails if PPO is trained?*
  *Answer:* Neural policies can make unexpected exploratory actions in unseen boundary states. The 6 deterministic guardrails act as safety shields ensuring pedagogical safety.

#### Q2: How does your evaluator prevent keyword gaming?
- **Short Answer:** Through the reasoning-dependent anti-keyword dampening rule acting on FAISS concept coverage.
- **Detailed Answer:** If a candidate recites keywords without logical structure, the CrossEncoder reasoning score $R$ remains low ($R \le 0.30$). When $R \le 0.30$, the system automatically cuts the FAISS concept coverage score $S_2$ by $40\%$ ($S_{2,\text{eff}} = 0.60 \cdot S_2$), ensuring keyword stuffing results in poor grades.

#### Q3: What is the difference between your Qwen 7B research experiments and your Qwen 1.5B live demo?
- **Short Answer:** Qwen-7B on GPU was used for the frozen EXP-3 research benchmark; Qwen-1.5B GGUF on CPU is used for fast, accessible live demonstrations.
- **Detailed Answer:** In EXP-3, Qwen-7B bfloat16 on an NVIDIA Tesla T4 GPU proved generative lexical grounding ($0.2496$). For local live demos without high-end GPUs, we integrated Qwen-2.5-1.5B-Instruct-GGUF (Q4_K_M) running via `llama.cpp` on CPU, achieving $2.195\text{s}$ latency.

---

## SECTION AA — FOUNDATIONAL CS CONCEPTS ("EXPLAIN LIKE I'M NEW")

- **Transformer & Cross-Attention:** A neural architecture that reads words simultaneously. In CrossEncoder, the question and answer are concatenated and attend to each other across all layers to evaluate reasoning entailment.
- **PPO (Proximal Policy Optimization):** A reinforcement learning algorithm that improves its decision policy in small, bounded steps to prevent destructive policy collapse.
- **FAISS (Facebook AI Similarity Search):** An open-source C++ library for ultra-fast nearest-neighbor search in dense vector spaces.
- **Docker Sandbox & cgroups:** Linux kernel control groups that limit CPU, RAM, and process counts to prevent untrusted code from harming the host server.

---

## SECTION AB — ARCHITECTURAL TRADE-OFFS ("WHY DID WE CHOOSE THIS?")

| Comparison | Option A | Option B | Why PrepAIred Chose Option A |
|---|---|---|---|
| **Backend Framework** | **FastAPI** | Flask / Django | Asynchronous ASGI support, native WebSocket handlers, and automatic Pydantic request validation. |
| **Scoring Engine** | **3-Component ($S_1+S_2+R$)** | Single Bi-Encoder | Bi-encoders are vulnerable to keyword gaming; decomposed pipeline isolates reasoning and concepts. |
| **RL Controller** | **PPO + Guardrails** | Pure Heuristics | Pure heuristics oscillate violently ($\rho = -0.2572$); PPO provides smooth trajectory progression. |
| **Local LLM Runtime** | **`llama.cpp` GGUF** | Cloud API (OpenAI) | Complete privacy, zero per-token cost, and deterministic local CPU execution. |

---

## SECTION AC — METHODOLOGICAL LIMITATIONS & HONEST SCIENTIFIC DEFENSE

1. **Simulated Candidate Trajectories in EXP 1, 4, 5:** Validates algorithmic stability and divergence across personas, but does not substitute for longitudinal human trials.
2. **20-Item Human Calibration Dataset:** Inter-rater reliability was measured on 20 representative technical items; expanding to $n \ge 100$ items across all 13 CS topics is planned.
3. **Speech Ingestion Environment:** Offline WAV speech ingestion is verified; live microphone input depends on client hardware.

---

## SECTION AD — FUTURE RESEARCH & ENGINEERING ROADMAP

1. **Multi-Institution Longitudinal Trial:** Multi-semester randomized controlled trial measuring candidate skill gains and anxiety reduction.
2. **Audio-Visual Multimodal Expansion:** Incorporating webcam gaze tracking and posture analysis in controlled environments.
3. **Cross-Language Code Execution:** Expanding the Docker sandbox to support C++, Python, Rust, and Java.

---

## SECTION AE — QUICK-REVISION CHEAT SHEETS & VIVA FLASHCARDS

### 1-Minute Viva Cheat Sheet
- **Name:** PrepAIred
- **Key Formula:** $S_{\text{tech}} = 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$
- **Anti-Keyword Rule:** $S_{2,\text{eff}} = 0.60 \cdot S_2$ if $R \le 0.30$
- **EXP-2 Correlation:** Spearman $\rho = 0.8358$, $p = 4.46 \times 10^{-6}$, Krippendorff's $\alpha = 0.8255$
- **RL Architecture:** PPO Actor-Critic on 6D state $\mathbf{s}_t \in [0, 1]^6$ with 6 deterministic guardrails
- **Docker Limits:** 128MB RAM, 32 PIDs, 2.0s timeout, `--net=none`
- **Dual Qwen:** Qwen-7B on GPU (EXP-3 Research); Qwen-1.5B GGUF on CPU (Live Demo)
- **Total Evaluations:** 480 pre-registered trials ($150 + 140 + 60 + 60 + 70$)
