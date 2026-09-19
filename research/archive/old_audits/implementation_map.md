# ARCHIVED / SUPERSEDED — NOT A SOURCE OF CURRENT FACTS
> **Superseded by:** Current audits in 
esearch/audit/ and 
esearch/CANONICAL_SCIENTIFIC_TRUTH.md  
> **Date Archived:** 2026-09-17  
> **Reason:** Early exploratory audit report superseded by consolidated forensic audits. Preserved for historical record.  

---

# PrepAIred — Complete Current Implementation Map

**Audited Git Commit:** `9cfd34f`  
**System Architecture:** Hub-and-Spoke Asynchronous Multimodal Architecture  
**Primary Language:** Python 3.12, C11 (`gcc -O2`), TypeScript / React  

---

## 1. Subsystem Implementation Registry

### 1.1 Central Interview Orchestration
- **Module Path:** `agents/orchestrator/interview_orchestrator.py`
- **Primary Class:** `InterviewOrchestrator`
- **Role:** Central asynchronous hub and state machine managing interview turns, concurrency locks, timer pacing, question queues, and sub-agent dispatch.
- **State Properties:**
  - `_state`: Volatile active session dictionary (`current_difficulty`, `scores`, `consecutive_followups`, `active_attempts`).
  - `_session_locks`: Per-session `asyncio.Lock()` preventing race conditions on concurrent WebSocket payloads.
- **Key Methods:**
  - `start_interview()`: Initializes session, pulls question queue, logs session creation.
  - `handle_verbal_answer()`: Triggers audio prosody extraction and multi-component evaluator.
  - `handle_code_submission()`: Triggers Docker C sandbox execution and `ScoreValidator`.
  - `retry_current_question()`: Rolls back tentative in-memory turn scores, leaves question index unadvanced, records attempt in SQLite.
  - `_decide_and_inject_followup()`: Evaluates deterministic rule threshold (`score < 0.80` or gaps); caps consecutive follow-ups at 2.
  - `_adapt_difficulty()`: Manages baseline warm-up phase (Turns 1-2) and invokes `HybridOrchestrator` PPO policy with post-hoc guardrails G1–G6.

### 1.2 Multi-Component Answer Evaluator
- **Module Path:** `services/evaluator/app.py`
- **Dependencies:** `sentence-transformers`, `faiss-cpu`, PyTorch, `tuned_model2`
- **Role:** Pure technical scoring authority. Evaluates technical depth across three orthogonal NLP signals.
- **Scoring Formula:**
  $$\text{Base Score} = 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$$
  $$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ 0.60 \cdot S_2 & \text{if } R \le 0.30 \text{ (anti-keyword stuffing dampening)} \end{cases}$$
- **Components:**
  - $S_1$ (Surface Similarity): Cosine similarity using `all-MiniLM-L6-v2` against rubric reference answer.
  - $S_2$ (Concept Coverage): `faiss.IndexFlatIP` search over 1,518 rubric concept embeddings with match threshold $\theta = 0.42$.
  - $R$ (Reasoning Entailment): Fine-tuned CrossEncoder (`ms-marco-MiniLM-L6-v2` base) evaluating question-answer pair cross-attention entailment.

### 1.3 Score Validator & Guardrails
- **Module Path:** `agents/validation/score_validator.py`
- **Class:** `ScoreValidator`
- **Role:** Deterministic guardrail layer between raw NLP scores and candidate state.
- **Rules:**
  - Mandatory Concept Check: If `mandatory_pass == False`, score is capped at `0.65`.
  - Mistake Pattern Penalties: Pattern-detected misconception penalty subtracted directly (capped at `0.25`).
  - Coding Execution Failure: Multiplier of `0.70` applied if execution status is `policy_blocked`, `runtime_error`, `timeout`, or `failed`.
  - Bounding: Final score strictly clamped to $[0.0, 1.0]$.

### 1.4 Docker C Execution Sandbox
- **Module Path:** `agents/coding_executor/coding_executor.py`
- **Class:** `DockerCSandbox`
- **Container Target:** `prepaired-c-sandbox:latest`
- **Compiler:** `gcc -O2 -Wall -Wextra -std=c11 /workspace/solution.c -o /workspace/solution -lm`
- **Isolation Primitives:**
  - Network: `--net=none`
  - Capabilities: `--cap-drop=ALL`
  - Privileges: `--security-opt=no-new-privileges`
  - User: `--user 1001:1001`
  - Memory: `--memory=128m --memory-swap=128m`
  - Process limits: `--pids-limit=32`
  - Root Filesystem: `--read-only`
  - Workspace: In-memory tmpfs mounted at `/workspace:rw,exec,size=32m,uid=1001,gid=1001,mode=1777`
  - Host mount: Read-only input mount `-v {host_tmp}:/input:ro`
- **Diagnostics:** Exit code 124 (Timeout), 137 (OOM / SIGKILL), 139 (SIGSEGV), 134 (SIGABRT), 136 (SIGFPE).

### 1.5 Persistent Storage & Deterministic Best-Answer Selection
- **Module Path:** `services/storage/database.py`
- **Database File:** `data/prepaired.db` (SQLite 3.50 in WAL mode)
- **Tables:** `candidates`, `sessions`, `question_attempts`
- **Deterministic Best-Answer Selection (`save_attempt`):**
  Filters primary attempts (`attempt_type = 'primary'`) for candidate and question.
  Sort Key: `(float(validated_score), -len(missing_concepts), int(attempt_number))` in descending order.
  Enforces exactly one row with `is_best = 1`. Follow-ups are excluded.

### 1.6 Reinforcement Learning Difficulty Controller
- **Module Paths:** `rl/env/interview_env.py`, `agents/strategy/hybrid_orchestrator.py`
- **Environment:** Gymnasium `InterviewEnv`
- **Observation Space:** 6D Continuous `Box(0.0, 1.0, shape=(6,))`
  $s = [\text{perf}, \text{avg\_perf}, \text{conf}, \text{hes}, \text{progress}, \text{diff}]$
- **Action Space:** Discrete 3 `{0: Easier, 1: Same, 2: Harder}`
- **Checkpoint:** `rl/checkpoints/seed_123/ppo_final.zip` (SB3 `MlpPolicy`, 2x64 tanh)
- **Normalizer:** Running mean and variance in `rl/checkpoints/seed_123/vecnormalize.pkl`
- **Post-Hoc Guardrails:** G4 (Stuck candidate $\to$ Easier), G1 (Overload at mid-diff $\to$ Easier), G2 (High anxiety $\to$ Same), G5 (Partial understanding $\to$ Same), G6 (Strong performer push $\to$ Harder).

### 1.7 Grounded Feedback Generation & Validation
- **Module Path:** `services/qwen/app.py`
- **Model:** Local weights `Qwen2.5-1.5B-Instruct`
- **Role:** Generates conversational narrative feedback and Socratic hints conditioned strictly on evaluator claims.
- **Feedback Validator (`_validate_feedback_output`):**
  - Length checks: `len(narrative) >= 20`, `len(how_to) >= 15`.
  - Rejection of generic fluff: `"good answer"`, `"good job"`, `"be more detailed"`, `"keep practicing"`, `"nice try"`.
  - Deterministic Fallback: `_synthesize_structured_feedback` constructs structured bullet points directly from evaluator lists if Qwen fails or times out (>6.0s).
