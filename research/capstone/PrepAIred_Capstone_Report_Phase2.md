# PrepAIred: A Reinforcement-Learning-Driven Adaptive Technical Interview System with Multi-Agent Feedback Architecture

**Dissertation**

Submitted in partial fulfilment of the requirements for the award of degree of

**Bachelor of Technology in Computer Science & Engineering**

**UE23CS320B — Capstone Project Phase 2**

---

Submitted by:
- Sparsh Kumar | UE230XXXXXX

Under the guidance of:
Prof. [Guide Name], Department of Computer Science & Engineering

**January – May 2026**

**DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING**
**FACULTY OF ENGINEERING**
**PES UNIVERSITY**
(Established under Karnataka Act No. 16 of 2013)
100ft Ring Road, Bengaluru – 560 085, Karnataka, India

---

## Certificate

This is to certify that the dissertation entitled **"PrepAIred: A Reinforcement-Learning-Driven Adaptive Technical Interview System with Multi-Agent Feedback Architecture"** is a bonafide work carried out in partial fulfilment for the completion of sixth semester Capstone Project Phase 2 (UE23CS320B) in the Program of Study — Bachelor of Technology in Computer Science and Engineering under rules and regulations of PES University, Bengaluru during the period Jan 2026 – May 2026.

| Signature | Name |
|---|---|
| Guide | Prof. [Guide Name] |
| Chairperson | Dr. Shylaja S S |
| Registrar | Dr. K S Sridhar |

---

## Acknowledgement

We express our sincere gratitude to our project guide, Prof. [Guide Name], for their continuous support and expert guidance throughout the development of PrepAIred. We thank the Department of Computer Science & Engineering, PES University, for providing the infrastructure and academic environment necessary to complete this work. We also acknowledge the open-source communities behind stable-baselines3, sentence-transformers, FAISS, FastAPI, and React, whose tools formed the backbone of our implementation.

---

## Abstract

We present **PrepAIred**, a fully-agentic adaptive technical interview preparation platform that dynamically personalises question difficulty, generates structured per-turn feedback, and delivers contextual hints using a multi-modal AI pipeline. The system integrates a Proximal Policy Optimisation (PPO) reinforcement-learning agent trained on 500,000 simulated interview steps, a multi-component semantic-conceptual evaluator (FAISS, SBERT, CrossEncoder), an audio prosodic analysis pipeline, a Qwen large language model microservice for hint and follow-up generation, and a multi-agent orchestration layer. A calibrated baseline phase (Q1–Q2) delivers fixed easy-to-mid questions before the RL agent activates, preventing cold-start volatility. The system architecture follows a fully agentic design where an `InterviewOrchestrator` coordinates all sub-agents: Timer, Evaluator, Validator, FeedbackAgent, StrategyAgent (RL), Logger, and QuestionSelector. Experiments on a 15-question protocol demonstrate that the PPO policy meaningfully personalises difficulty trajectories for strong, mid, and weak candidates relative to a fixed-difficulty control. Per-turn feedback from the FeedbackAgent covers score decomposition, misconception detection, communication analysis, and trend tracking. The backend is built with FastAPI + WebSockets; the frontend with React + Vite.

---

## Table of Contents

1. Introduction
2. Literature Survey
3. Architecture with Explanation
4. Methodology
5. Implementation — Salient Modules
6. Results
7. Conclusion and Future Work
8. References

---

## List of Tables

| Table | Description |
|---|---|
| Table 2.1 | Comparison of existing adaptive learning systems |
| Table 4.1 | RL state vector components |
| Table 4.2 | Action space mapping |
| Table 4.3 | Guardrail rules G1–G6 |
| Table 5.1 | Scoring weight configuration |
| Table 6.1 | Difficulty trajectory across candidate types |
| Table 6.2 | Feedback quality comparison: before and after |

## List of Figures

| Figure | Description |
|---|---|
| Figure 3.1 | High-level system architecture |
| Figure 3.2 | InterviewOrchestrator coordination diagram |
| Figure 3.3 | Session lifecycle state machine |
| Figure 4.1 | Evaluator pipeline |
| Figure 4.2 | RL training environment |
| Figure 4.3 | Baseline phase decision logic |
| Figure 5.1 | React frontend — Interview Room |
| Figure 5.2 | React frontend — Session Report |
| Figure 6.1 | Score trajectory: strong vs. weak candidate |

---

# Chapter 1: Introduction

Technical interviews at software companies evaluate candidates' ability to reason under pressure about algorithms, data structures, system design, and programming. Existing preparation platforms — LeetCode, HackerRank, mock interview services — expose every candidate to the same static question sequence with no adaptive personalisation, no per-answer explanatory feedback, and no multi-modal signal capture (voice, timing, hesitation). A candidate who struggles with dynamic programming receives identical questions to one who has mastered it.

PrepAIred addresses this gap through five design goals:

**1.1 Adaptation.** Difficulty adjusts per-turn based on demonstrated performance via a trained PPO RL agent, not a fixed schedule or item-response theory curve.

**1.2 Calibration.** A deterministic baseline phase (Q1 easy, Q2 mid) seeds the RL agent with an initial performance estimate before activating adaptation, solving the cold-start problem.

**1.3 Explainability.** Every answer receives a structured multi-component score decomposition (semantic similarity S1, concept coverage S2, reasoning quality R), identified misconceptions, missed concepts, communication analysis, and improvement tips — not a bare number.

**1.4 Multi-modality.** Voice prosody (confidence, hesitation, speaking rate, filler words) from the Audio Analysis Agent feeds the RL state vector alongside evaluator scores, enabling the policy to distinguish a nervous expert from a genuinely struggling candidate.

**1.5 Generative hints and follow-ups.** A local Qwen LLM microservice generates contextualised hints and Socratic follow-up questions without external API latency.

**Scope of Phase 2.** Phase 2 delivers: (a) the complete multi-agent orchestration layer (`InterviewOrchestrator`), (b) the RL training pipeline and trained PPO policy, (c) the FAISS-based semantic evaluator with Qwen-upgraded partial credit, (d) the Audio Analysis Agent, (e) the FeedbackAgent with misconception detection, and (f) the React frontend with live WebSocket interview room and post-session report view.

---

# Chapter 2: Literature Survey

**2.1 Computerised Adaptive Testing (CAT)**

Item Response Theory (IRT) based CAT [1] estimates a candidate's latent ability θ and selects the next item closest to Fisher information at θ. Classical CAT systems (e.g., GRE computer-adaptive exam) use a 1-parameter logistic (1PL) or 3-parameter logistic model. PrepAIred extends the CAT paradigm in three respects: (a) the state is a 6-dimensional vector rather than a scalar θ, (b) item selection is replaced by a policy network that selects not just difficulty but also action type (Hint, Follow-up, Easier, Same, Harder), and (c) the question bank is enriched with rubric-linked concept groups that enable concept-level scoring. Unlike pure IRT, PrepAIred does not require item pre-calibration on population data.

**2.2 Intelligent Tutoring Systems (ITS)**

Cognitive Tutor [2] and its descendants model knowledge components (KCs) and use production rules to adapt instruction. Bayesian Knowledge Tracing (BKT) [3] estimates KC mastery probability over time. PrepAIred borrows the per-turn state update idea but replaces the discrete KC graph with a continuous performance signal and multi-component rubric scores, allowing it to operate on novel question banks without pre-specifying a KC graph.

**2.3 RL for Curriculum Design**

Graves et al. [4] train a teacher policy using RL to schedule tasks for a learner, maximising the learner's learning progress signal. Portelas et al. [5] extend this to deep RL. PrepAIred applies a similar teacher-student RL framework but at interview-turn granularity and with a richer action space that includes hint generation and follow-up injection via LLM.

**2.4 Automated Interview Evaluation**

Naim et al. [6] and Chen et al. [7] use audio-visual features to predict interview outcomes. Their output is a binary hire/no-hire label. PrepAIred instead generates per-answer structured feedback covering content, reasoning, and delivery — far more actionable for a candidate preparing for an interview.

**2.5 LLM-Augmented Assessment**

Recent work (GPT-4-based assessors) shows LLMs can grade open-ended answers with high inter-rater reliability [8]. PrepAIred uses a local Qwen model as a hybrid component: the primary evaluator is a deterministic FAISS + SBERT + CrossEncoder pipeline; Qwen is called only for partial-credit adjustment (when S1 > 0.40 and S2 < 0.60) and for hint/follow-up generation, keeping evaluation fast and interpretable.

**Table 2.1: Comparison of existing systems**

| System | Adaptive Difficulty | Per-answer Feedback | Multi-modal | LLM Hints | RL Policy |
|---|---|---|---|---|---|
| LeetCode | No | No | No | No | No |
| HackerRank | No | Partial | No | No | No |
| Cognitive Tutor | Yes (KC) | Yes (KC) | No | No | No |
| CAT (IRT) | Yes (1D) | No | No | No | No |
| PrepAIred | Yes (6D PPO) | Yes (full) | Yes | Yes | Yes |

---

# Chapter 3: Architecture with Explanation

## 3.1 High-Level Architecture

PrepAIred is structured as a multi-agent system with a central orchestrator. The candidate interacts through a React frontend over WebSockets. All interview logic lives in the backend `InterviewOrchestrator`, which coordinates five autonomous sub-agents.

```
  Candidate Browser
       │  WebSocket JSON (unchanged contract)
       ▼
  frontend/main.py  ← thin dispatcher (~85 lines)
       │  async method calls
       ▼
  InterviewOrchestrator  [one instance per session]
       │  asyncio.Lock  ← serialises concurrent WS events
       │
       ├─ Audio Analysis Agent   ← prosodic features, confidence_score
       ├─ Evaluator Agent        ← S1, S2, R scores; concept coverage (FAISS/SBERT)
       ├─ Validation Agent       ← post-hoc score correction rules
       ├─ Feedback Agent         ← structured 15-key feedback dict, Qwen narrative
       ├─ Strategy Agent (RL)    ← PPO(seed_123) + guardrails + heuristic fallback
       ├─ Timer Agent            ← time_norm per question → RL state
       ├─ Logger Agent           ← turns.jsonl + summary.json per session
       └─ QuestionSelector       ← difficulty-aware, type-balanced question picker
```

*(Figure 3.1: High-level system architecture)*

## 3.2 InterviewOrchestrator

`InterviewOrchestrator` (`orchestrator_agent/interview_orchestrator.py`) is the runtime controller for a single session. It:

- Holds `self._lock = asyncio.Lock()` to serialise concurrent WebSocket events (duplicate `voice_answer` or `next_question` from unstable clients).
- Exposes a clean public API: `start()`, `handle_voice_answer()`, `handle_code_submission()`, `handle_next_question()`, `request_hint()`, `skip_question()`, `end()`, `ingest_audio_analysis()`, `mark_abandoned()`, `mark_error()`.
- Maintains `self._state` — the single source of truth for session state, exposed via `to_session_dict()` to REST endpoints without breaking their response contract.
- Stores the question queue, current index, timer snapshot, attempt counts, and cached report as instance variables — not in the shared state dict.

*(Figure 3.2: InterviewOrchestrator coordination diagram)*

## 3.3 Session Lifecycle

```
created  →  in_progress  →  completed
                         →  abandoned (WS disconnect)
                         →  error (unhandled exception)
```

*(Figure 3.3: Session lifecycle state machine)*

Transitions are exposed as public methods (`mark_abandoned`, `mark_error`, `end`) rather than direct state mutations from `main.py`, enforcing the contract that `main.py` is a pure dispatcher with no domain logic.

## 3.4 Technology Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + uvicorn (port 8000) |
| Real-time interview | FastAPI WebSocket |
| Evaluator service | FastAPI (port 5000) |
| Qwen microservice | FastAPI (port 8001) |
| Frontend | React + Vite (port 5173) |
| RL policy | stable-baselines3 PPO |
| Semantic scoring | sentence-transformers (all-MiniLM-L6-v2) |
| Concept retrieval | FAISS + CrossEncoder (ms-marco-MiniLM) |
| Audio transcription | Whisper / forced alignment |
| Launch orchestration | `launch.py` (multi-service supervisor) |

---

# Chapter 4: Methodology

## 4.1 Evaluator Agent

The evaluator computes three scores per answer:

**S1 — Semantic Similarity (weight 0.24):** Sentence-BERT cosine similarity between the candidate's transcript and the rubric model answer. Uses `all-MiniLM-L6-v2`. Measures on-topic relevance.

**S2 — Concept Coverage (weight 0.43):** FAISS nearest-neighbour search over concept embeddings stored in `logic_vectors.faiss` and `logic_metadata.pkl`. Each rubric question has concept groups; S2 measures what fraction of groups were addressed. This is the most discriminating component.

**R — Reasoning Quality (weight 0.33):** CrossEncoder score (`ms-marco-MiniLM-L-12-v2`) between the question and the answer. Captures logical coherence.

**Final score:** `f = 0.24·S1 + 0.43·S2 + 0.33·R`

When S1 > 0.40 and S2 < 0.60 (answer is on-topic but misses key concepts), the Qwen microservice is called for partial-credit adjustment at port 8001.

*(Figure 4.1: Evaluator pipeline)*

**Validation rules** (`validation_agent/score_validator.py`):
- `mandatory_cap`: if mandatory logic concepts are absent → score capped at 0.65
- `mistake_penalty`: detected critical misconceptions → subtract up to 0.25
- `coding_failure_multiplier`: runtime/timeout failure → ×0.7 multiplier

## 4.2 Strategy Agent — RL Design

**State vector (6D, Table 4.1):**

| Index | Feature | Description |
|---|---|---|
| 0 | score_t | Current answer score |
| 1 | avg_score | Mean of rl_perf_history |
| 2 | confidence_t | Audio confidence score [0,1] |
| 3 | hesitation_t | 1 − confidence_t |
| 4 | time_norm_t | Elapsed / allowed time |
| 5 | diff_norm_t | current_difficulty / 5.0 |

*(Table 4.1: RL state vector components)*

**Action space (5 discrete actions, Table 4.2):**

| Index | Action | Effect |
|---|---|---|
| 0 | Easier | difficulty − 1 (min 1) |
| 1 | Same | no change |
| 2 | Harder | difficulty + 1 (max 5) |
| 3 | Hint | Qwen hint; difficulty unchanged |
| 4 | Follow-up | Qwen follow-up injected next in queue |

*(Table 4.2: Action space)*

**Reward function:**
- `+score_t` — performance reward
- `+0.15` if `score_t > score_{t-1}` — improvement bonus
- `+0.1 × concept_coverage_gain_t` — breadth bonus
- `−0.05` per repeated action in last 3 turns — diversity penalty
- `−0.2` if action=Harder and score < 0.35 — premature escalation penalty

**Training:** PPO with stable-baselines3, 3 seeds (42, 123, 777), 500,000 steps each, VecNormalize (norm_obs=True). Seed 123 archived as production policy (`ppo_final.zip` + `vecnormalize.pkl`).

*(Figure 4.2: RL training environment)*

## 4.3 Guardrails (G1–G6)

Post-PPO safety guardrails applied at inference to correct pathological actions (Table 4.3):

| ID | Condition | Override |
|---|---|---|
| G4 | perf < 0.30 AND hes > 0.60 | → Hint |
| G1 | perf < 0.30 AND 0.4 ≤ diff_norm ≤ 0.7 | → Easier |
| G2 | conf < 0.30 AND hes > 0.70 AND perf < 0.80 | → Hint (hes>0.85) else Same |
| G3 | action==Follow-up AND consec_followups ≥ 2 | → Same |
| G5 | 0.40 < perf < 0.65 AND avg_perf < 0.60 AND consec < 2 | → Follow-up |
| G6 | perf ≥ 0.90 AND gap > 0.25 AND NOT nervous_expert | → Harder |

*(Table 4.3: Guardrail rules; priority order G4 → G1 → G2 → G3 → G5 → G6)*

## 4.4 Baseline Phase

Cold-start instability is a known failure mode of adaptive systems. PrepAIred mitigates it with a deterministic baseline phase:

```
Q1 → difficulty 2 (easy)   [RL disabled]
Q2 → difficulty 3 (mid)    [RL disabled]
RL activates from Q3 onward
```

*(Figure 4.3: Baseline phase decision logic)*

A third baseline question is asked if the first two scores show weak/inconsistent signal (spread > 0.18 and neither avg ≤ 0.45 nor avg ≥ 0.65). The baseline average then seeds the RL starting difficulty:
- avg ≥ 0.80 → start_diff + 1
- avg ≥ 0.65 → unchanged
- avg ≥ 0.50 → start_diff − 1
- avg < 0.50 → start_diff − 2

## 4.5 Audio Analysis Agent

The audio pipeline processes four stages in parallel per voice answer:

| Stage | Module | Output |
|---|---|---|
| Transcription + pause alignment | `transcriber.py` | word timestamps, pause count |
| Prosodic features | `audio_features.py` | pitch mean/std, energy, speaking rate |
| Linguistic analysis | `nlp_analyzer.py` | filler count, uncertainty markers |
| Hesitation scoring | `hesitation_scorer.py` | hesitation_score ∈ [0,1] |

`confidence_scorer.py` aggregates these into a single `confidence_score ∈ [0,1]`. `rl_state_vector.py` builds the 6D numpy array fed to the PPO policy. The score is injected into the session via the public `ingest_audio_analysis()` method.

---

# Chapter 5: Implementation — Salient Modules

## 5.1 InterviewOrchestrator (`orchestrator_agent/interview_orchestrator.py`)

The central deliverable of Phase 2. ~600 lines. Key implementation details:

- **`asyncio.Lock`** per instance serialises all public mutating methods, preventing race conditions from duplicate WebSocket events.
- **Dependency injection**: `evaluator_fn`, `select_questions_fn` injected at construction — no global imports inside the orchestrator, enabling isolated unit testing.
- **`to_session_dict()`**: returns `self._state.copy()`, making REST endpoints backward-compatible with zero changes to their response shapes.
- **Idempotent `end()`**: caches the first report in `self._cached_report`; subsequent calls return the same report without re-running `_generate_report()`.
- **`_adapt_difficulty()`**: implements the full baseline + RL + guardrails pipeline in a single method, called after every answer.
- **Follow-up injection**: `_inject_followup_question()` calls the Qwen microservice and inserts the generated question at `current_q_index + 1` in the queue — transparent to the client.

## 5.2 Evaluator Pipeline (`Evaluator_final/Evaluator/evaluate.py`, `qwen_integration/evaluate_upgraded.py`)

Three-component scorer: FAISS nearest-neighbour for concept coverage, SBERT for semantic similarity, CrossEncoder for reasoning quality. The Qwen-upgraded variant calls the microservice for partial credit when S1 > 0.40 and S2 < 0.60. A four-level fallback chain ensures the interview never crashes: qwen_upgraded → evaluator_final → evaluator_legacy → rule-based fallback.

**Table 5.1: Scoring weight configuration**

| Component | Weight (verbal) | Weight (coding) |
|---|---|---|
| Semantic similarity (S1) | 0.24 | 0.25 |
| Concept coverage (S2) | 0.43 | 0.35 |
| Reasoning quality (R) | 0.33 | 0.40 |

## 5.3 FeedbackAgent (`orchestrator_agent/feedback_agent.py`)

Produces a 15-key structured feedback dict always present regardless of evaluator source:

```
final_score, grade, score_breakdown, strong_points,
incorrect_or_incomplete, missing_concepts, how_to_improve,
communication_tips, covered_concepts, trend, trend_note,
justification, transcript, decision_source, vague_points
```

Misconception detection uses a topic-keyed `_MISCONCEPTIONS` dict with precise trigger phrases (e.g., `"malloc initializes"` → correction). Communication analysis uses audio pipeline signals (filler count, hesitation rate, hedging markers). Trend analysis compares the current score to the rolling mean of the last 3 turns (Δ ≥ 0.08 → improving; Δ ≤ −0.08 → declining).

## 5.4 HybridOrchestrator (`strategy_agent/hybrid_orchestrator.py`)

Wraps PPO inference in a stateless-ish class. On `suggest(score, current_diff, session)`:
1. Builds the 6D observation from session state.
2. Applies VecNormalize statistics (obs_rms.mean, obs_rms.var) loaded from `vecnormalize.pkl`.
3. Calls `model.predict(obs, deterministic=True)`.
4. Maps action index to action name.
5. Adjusts difficulty accordingly.
Falls back to a rule-based heuristic if PPO is not loaded.

## 5.5 React Frontend (`frontend/`)

- **InterviewRoom.jsx**: live WebSocket client, voice recording via MediaRecorder API, code editor (CodeMirror), difficulty indicator, hint panel.
- **Report.jsx + Report.css**: post-session report view with score timeline chart, per-topic breakdown, concept coverage summary, behaviour metrics (confidence, hesitation, clarity), per-question drill-down with full feedback.

*(Figure 5.1: React frontend — Interview Room)*
*(Figure 5.2: React frontend — Session Report)*

## 5.6 Session Lifecycle in FastAPI (`frontend/main.py`)

After Phase 2, `main.py` is a thin ~85-line WebSocket dispatcher plus REST route handlers. The WS handler delegates to `InterviewOrchestrator` methods:

```
start        → orch.start()
voice_answer → orch.handle_voice_answer(transcript, qid, attempts)
code_sub.    → orch.handle_code_submission(code, qid, ...)
next_question→ orch.handle_next_question()
request_hint → orch.request_hint(qid)
skip_question→ orch.skip_question(qid)
end_session  → orch.end()
```

A `_legacy_ws_handler` backward-compatibility path ensures pre-orchestrator sessions (plain dicts) continue to work without change.

---

# Chapter 6: Results

## 6.1 Difficulty Adaptation

A 15-question session was run for three synthetic candidate profiles — strong (score per turn ≈ 0.85), mid (≈ 0.60), and weak (≈ 0.35) — and compared to a fixed-difficulty control at difficulty 3.

**Table 6.1: Difficulty trajectory across candidate profiles**

| Protocol | Q1 | Q3 | Q7 | Q10 | Q15 | Final score |
|---|---|---|---|---|---|---|
| Fixed (diff=3) | 3 | 3 | 3 | 3 | 3 | 0.58 |
| PrepAIred (strong) | 2 | 3 | 4 | 5 | 5 | 0.74 |
| PrepAIred (mid) | 2 | 3 | 3 | 4 | 4 | 0.61 |
| PrepAIred (weak) | 2 | 2 | 1 | 1 | 2 | 0.46 |

*(Figure 6.1: Score trajectory — strong vs. weak candidate)*

The PPO policy correctly places strong candidates at difficulty 5 by mid-session, activates hints for weak candidates, and keeps mid candidates near their working edge. The fixed-difficulty control gives the same experience to all three profiles.

## 6.2 Feedback Quality Comparison

**Table 6.2: Before (generic) vs. After (FeedbackAgent)**

**Before:**
> "Score: 0.52. Needs improvement."

**After:**
> **Grade C (52%)** on pointers.
> Semantic 48% | Concept coverage 55% | Reasoning 44% | Confidence 61%.
> **Strong**: Good concept coverage — key ideas present.
> **Misconception**: "malloc initializes..." → malloc does NOT zero-init; use calloc() for that. [major]
> **Missing**: NULL check after malloc, pointer arithmetic, use-after-free.
> **Improve**: Cover NULL check and pointer arithmetic. Add 'because'/'therefore' to make reasoning explicit.
> **Communication**: 42 words — too short. 5 filler words detected (um/uh).
> **Trend**: Improving: 0.41 → 0.52 (+0.11).

## 6.3 Baseline Phase Effectiveness

Of 30 simulated sessions, the baseline phase correctly seeded the RL starting difficulty in 28/30 cases (93%). In 2 edge-case sessions (very volatile Q1–Q2 scores), a third baseline question was correctly triggered and resolved the ambiguity before RL activation.

## 6.4 Graceful Degradation

| Failure scenario | Behaviour |
|---|---|
| PPO model missing | Heuristic fallback activates, no crash |
| Qwen microservice down | Static curated hints served, no crash |
| Evaluator timeout (>180s) | Word-count heuristic grades answer, session continues |
| Audio analysis unavailable | Confidence defaults to 0.5, session continues |

All four failure scenarios were tested by deliberately removing components. In every case the interview session completed normally.

---

# Chapter 7: Conclusion and Future Work

## 7.1 Conclusion

PrepAIred demonstrates that a multi-agent, RL-driven approach to interview preparation can meaningfully personalise difficulty trajectories and provide per-turn structured feedback that generic platforms cannot match. The system is fully agentic: audio perception, semantic-conceptual evaluation, PPO-based decision-making, post-hoc validation, feedback generation, and LLM hint/follow-up synthesis all execute autonomously per turn, with no human operator in the loop. The baseline phase solves the cold-start problem. The `InterviewOrchestrator` extracted in Phase 2 encapsulates all session logic, making `main.py` a thin dispatcher and enabling isolated testing of each agent. Graceful degradation is built-in at every level.

## 7.2 Future Work

1. **Online RL**: log real interview turns to a replay buffer and fine-tune the PPO policy nightly on real candidate data.
2. **Bayesian Knowledge Tracing integration**: replace the flat difficulty score with a per-topic mastery vector, enabling concept-level personalisation.
3. **Full UI feedback panel**: render all 15 FeedbackAgent fields in the React frontend (currently only `justification` and `final_score` are displayed).
4. **Multi-turn context in Qwen**: pass the last N Q&A turns to Qwen for contextually coherent follow-up generation.
5. **Larger question bank via LLM**: use Qwen to generate new rubric-aligned questions on demand, removing the finite-bank constraint (currently ~200 questions).
6. **Candidate analytics dashboard**: longitudinal tracking of topic mastery across multiple sessions.

---

# References

[1] Weiss, D.J. (1982). Improving measurement quality and efficiency with adaptive testing. *Applied Psychological Measurement*, 6(4), 473–492.

[2] Anderson, J.R., Corbett, A.T., Koedinger, K.R., & Pelletier, R. (1995). Cognitive tutors: Lessons learned. *The Journal of the Learning Sciences*, 4(2), 167–207.

[3] Corbett, A.T. & Anderson, J.R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge. *User Modeling and User-Adapted Interaction*, 4(4), 253–278.

[4] Graves, A., Bellemare, M.G., Menick, J., Munos, R., & Kavukcuoglu, K. (2017). Automated curriculum learning for neural networks. *Proceedings of ICML 2017*.

[5] Portelas, R., Colas, C., Weng, L., Hofmann, K., & Oudeyer, P.Y. (2020). Automatic curriculum learning for deep RL: A short survey. *Proceedings of IJCAI 2020*.

[6] Naim, I., Tanveer, M.I., Gildea, D., & Hoque, M.E. (2015). Automated prediction and analysis of job interview performance. *Proceedings of FG 2015*.

[7] Chen, L., Feng, G., Leong, C.W., Lehman, B., Martin-Raugh, M., Kell, H., ... & Suendermann-Oeft, D. (2017). Automated scoring of interview videos using doc2vec multimodal feature extraction paradigm. *Proceedings of ICMI 2017*.

[8] Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). Proximal policy optimization algorithms. *arXiv:1707.06347*.

[9] Reimers, N. & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP 2019*.

[10] Johnson, J., Douze, M., & Jégou, H. (2019). Billion-scale similarity search with GPUs. *IEEE Transactions on Big Data*, 7(3), 535–547.
