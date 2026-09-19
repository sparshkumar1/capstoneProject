# Current Implementation Map & Subsystem Architecture

**Audited Git Head Commit:** `9cfd34f278de8cc6b2810a4855b571b6b7264495`  
**System Architecture:** Hub-and-Spoke Asynchronous Multimodal Architecture  
**Primary Language:** Python 3.12, C11 (`gcc -O2`), TypeScript / React  

---

## 1. Subsystem Implementation Registry

### 1.1 Central Interview Orchestration
* **File:** `agents/orchestrator/interview_orchestrator.py`
* **Class/Functions:** `InterviewOrchestrator` (`start_interview`, `handle_verbal_answer`, `handle_code_submission`, `retry_current_question`, `_decide_and_inject_followup`, `_adapt_difficulty`)
* **Inputs:** Candidate audio transcripts, C code submissions, candidate metadata, question queues.
* **Outputs:** Evaluated turn payloads, Socratic follow-up decisions, difficulty adjustments, final session report.
* **Model/Checkpoint:** None (orchestrates calls to evaluator, PPO, Qwen, Docker).
* **Persistent State:** Session ID, Candidate ID, turn number, active attempt records in SQLite WAL mode. Volatile per-session mutexes (`asyncio.Lock()`).
* **Failure Behavior:** If evaluator or Qwen microservice is unreachable, falls back to deterministic heuristic evaluation or non-LLM structured templates; records fault in logs without dropping session state.
* **Tests:** `tests/unit/test_orchestrator.py` (20 tests), `tests/integration/test_full_interview_lifecycle.py` (1 test).
* **Research Role:** Central coordinator for Paper 1 (Systems/Security) and Paper 3 (RL Difficulty Controller).

### 1.2 Multi-Signal Technical Answer Evaluator
* **File:** `services/evaluator/app.py`
* **Class/Functions:** `evaluate()`, `semantic_score()`, `_cosine_similarity()`, `cross_encoder_verification()`, `mandatory_check()`, `mistake_penalty()`
* **Inputs:** Candidate answer string, question text, rubric dictionary (reference answers, expected concepts, mandatory invariants, misconceptions).
* **Outputs:** Dictionary containing `S1_semantic`, `S2_structural`, `reasoning_score`, `final_score`, `grade`, `weakest_gap`, `correct_claims`, `missing_concepts`.
* **Model/Checkpoint:**
  - SBERT: `all-MiniLM-L6-v2` (384-dimensional dense vectors)
  - FAISS Index: `faiss.IndexFlatIP(384)` over 1,518 rubric concept vectors
  - CrossEncoder: `ms-marco-MiniLM-L6-v2` fine-tuned checkpoint (`models/tuned_model2`)
* **Persistent State:** Pre-indexed FAISS binary and static question rubrics in `services/evaluator/data/`.
* **Failure Behavior:** If FAISS or CrossEncoder raises an exception, falls back to SBERT cosine similarity $S_1$ with safe default score $0.50$.
* **Tests:** `tests/unit/test_evaluator.py` (11 tests), `tests/unit/test_stage11_3_followup_and_evaluation.py` (15 tests).
* **Research Role:** Primary subject of Paper 2 (Evaluator / ICTCS 2026).

### 1.3 Score Validator & Rule Guardrails
* **File:** `agents/validation/score_validator.py`
* **Class/Functions:** `ScoreValidator.validate_verbal()`, `ScoreValidator.validate_coding()`
* **Inputs:** Raw evaluator score dict, mandatory pass boolean, execution status dict.
* **Outputs:** Bound validated score $\in [0.0, 1.0]$, applied penalty log, cap flags.
* **Model/Checkpoint:** None (deterministic rules).
* **Persistent State:** None (stateless validation pipeline).
* **Failure Behavior:** Clamps all scores strictly to $[0.0, 1.0]$; sets default score $0.0$ if input is corrupted.
* **Tests:** `tests/unit/test_evaluator.py`, `tests/unit/test_coding_executor.py`.
* **Research Role:** Guardrail layer between NLP scores and adaptive curriculum decisions (Paper 1 & Paper 2).

### 1.4 Isolated C Execution Sandbox
* **File:** `agents/coding_executor/coding_executor.py`
* **Class/Functions:** `DockerCSandbox.execute()`, `validate_source_safety()`, `evaluate_c_submission()`
* **Inputs:** C source code string, input/output test case suites, timeout limit (3.0s), memory limit (128MB).
* **Outputs:** Compilation status, stdout, stderr, execution time, test case pass counts, exit signal (OOM, SIGSEGV, Timeout).
* **Model/Checkpoint:** Docker image `prepaired-c-sandbox:latest` running GCC 12 (C11 standard).
* **Persistent State:** In-memory `/workspace` tmpfs mounted per execution; zero host filesystem persistence.
* **Failure Behavior:** Rejects prohibited system calls via static filter; catches container timeouts (124) or runtime signals (137, 139) and formats them into candidate-facing errors without host crash.
* **Tests:** `tests/unit/test_coding_executor.py` (22 tests), `tests/unit/test_stage11_4_coding_verification.py` (14 tests).
* **Research Role:** Primary containment boundary for Paper 1 (Systems/Security / ATIS 2026).

### 1.5 Durable Storage & Deterministic Best Selection
* **File:** `services/storage/database.py`
* **Class/Functions:** `init_db()`, `save_attempt()`, `get_best_attempt()`, `get_candidate_history()`, `resolve_or_create_candidate()`
* **Inputs:** Turn attempt records, validated scores, concept breakdown, execution metrics.
* **Outputs:** SQLite attempt records with durable `is_best` flags, candidate trajectory summaries.
* **Model/Checkpoint:** SQLite 3.50 engine in WAL mode with compound indices.
* **Persistent State:** `data/prepaired.db` containing `candidates`, `sessions`, `question_attempts`.
* **Failure Behavior:** Database transaction rollbacks; WAL checkpointing prevents database locking under concurrent reading.
* **Tests:** `tests/unit/test_persistence_and_history.py` (14 tests).
* **Research Role:** Data integrity and learning gap persistence for Paper 1.

### 1.6 Reinforcement Learning Difficulty Controller
* **File:** `agents/strategy/hybrid_orchestrator.py`, `rl/env/interview_env.py`
* **Class/Functions:** `HybridOrchestrator.get_next_action()`, `build_rl_observation()`, post-hoc guardrails G1–G6.
* **Inputs:** 6D candidate observation vector $[\text{perf}, \overline{\text{perf}}, \text{conf}, \text{hes}, \text{progress}, \text{diff}]$.
* **Outputs:** Action index $\{0: \text{Easier}, 1: \text{Same}, 2: \text{Harder}\}$, mapped to difficulty level $d \in [1, 5]$.
* **Model/Checkpoint:** `rl/checkpoints/seed_123/ppo_final.zip` (SB3 PPO `MlpPolicy`, $2 \times 64$ tanh), `vecnormalize.pkl`.
* **Persistent State:** Checkpoint weights and running observation normalizer statistics.
* **Failure Behavior:** If PPO model file is missing or invalid, falls back immediately to deterministic heuristic difficulty ladder.
* **Tests:** `tests/unit/test_rl_env.py` (19 tests), `tests/unit/test_stage11_5_coding_adaptation.py` (14 tests).
* **Research Role:** Primary subject of Paper 3 (RL Difficulty Controller / SmartCom 2027).

### 1.7 Grounded Feedback Microservice & Validation
* **File:** `services/qwen/app.py`
* **Class/Functions:** `generate_feedback()`, `_validate_feedback_output()`, `_synthesize_structured_feedback()`, `generate_hint()`
* **Inputs:** Question text, candidate answer/transcript, structured evaluation dictionary, retry comparison context.
* **Outputs:** Qualitative narrative feedback, actionable improvements, how-to-answer guide, Socratic hints.
* **Model/Checkpoint:** Local weights `Qwen2.5-1.5B-Instruct` (GGUF CPU engine via `llama-cpp-python` or PyTorch Transformers).
* **Persistent State:** In-memory loaded model registry.
* **Failure Behavior:** If Qwen output fails schema checks, is generic, contradicts evaluator evidence, or times out (>6.0s), `_synthesize_structured_feedback` activates deterministic fallback directly from rubric facts.
* **Tests:** `tests/unit/test_qwen_specific_feedback.py` (8 tests), `tests/unit/test_qwen_followup_feedback.py` (14 tests).
* **Research Role:** Feedback grounding and fallback resilience for Paper 1.
