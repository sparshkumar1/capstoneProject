# PrepAIred — Multi-Agent System & Agent Responsibilities

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Multi-Agent System Overview

PrepAIred decomposes the technical interview interaction into seven focused agents and controllers, each encapsulating a single functional responsibility with explicit interfaces and zero hidden couplings:

```
                          ┌───────────────────────────┐
                          │   InterviewOrchestrator   │ (Central Session Engine)
                          └─────────────┬─────────────┘
                                        │
      ┌───────────────┬─────────────────┼─────────────────┬───────────────┐
      │               │                 │                 │               │
      ▼               ▼                 ▼                 ▼               ▼
┌───────────┐   ┌───────────┐     ┌───────────┐     ┌───────────┐   ┌───────────┐
│  Hybrid   │   │ Feedback  │     │   Score   │     │ Question  │   │  Docker   │
│ Strategy  │   │   Agent   │     │ Validator │     │   Timer   │   │  Sandbox  │
│   (PPO)   │   │  (Qwen7B) │     │           │     │           │   │ (C Code)  │
└───────────┘   └───────────┘     └───────────┘     └───────────┘   └───────────┘
```

---

## 2. Agent Inventory & Detailed Responsibilities

### 2.1 `InterviewOrchestrator` (`agents/orchestrator/interview_orchestrator.py`)
- **Primary Role:** Central session lifecycle and turn sequencer.
- **Key Responsibilities:**
  - Manages session state dictionary (`answers`, `scores`, `concepts_mastered`, `concepts_missed`, `current_difficulty`).
  - Implements the 2–3 question **Baseline Warmup Phase** before RL activation.
  - Rebuilds remaining queued questions on RL difficulty updates (`_rebuild_remaining_questions`).
  - Enforces the 2-consecutive-turn hard cap on follow-up questions.
  - Generates comprehensive session summary reports (`_generate_report`).

### 2.2 `HybridOrchestrator` (`agents/strategy/hybrid_orchestrator.py`)
- **Primary Role:** Adaptive difficulty strategy and PPO policy dispatcher.
- **Key Responsibilities:**
  - Constructs the strict 6-dimensional RL observation vector $\mathbf{s} \in [0, 1]^6$.
  - Normalizes observations using pre-trained `VecNormalize` statistics.
  - Executes deterministic PPO policy inference over the discrete 3-action space (`0: Easier`, `1: Same`, `2: Harder`).
  - Applies pedagogical safety guardrails G1–G6 to prevent erratic escalations.
  - Manages deterministic heuristic fallback (`non_rl_heuristic_recovery`) when the PPO model is offline.

### 2.3 `FeedbackAgent` (`agents/orchestrator/feedback_agent.py`)
- **Primary Role:** Formative per-turn feedback generator.
- **Key Responsibilities:**
  - Formats candidate transcripts, evaluator sub-scores ($S_1, S_2, R$), and rubric gaps.
  - Queries Qwen-7B microservice (`/api/qwen/feedback`) for grounded narrative feedback.
  - Falls back to deterministic non-LLM structured recovery (`llm_status = "llm_unavailable"`) without altering evaluator scores.
  - Generates code debugging hints and error diagnostics based on sandbox execution outputs.

### 2.4 `ScoreValidator` (`agents/validation/score_validator.py`)
- **Primary Role:** Post-evaluation sanity and boundary enforcer.
- **Key Responsibilities:**
  - Validates that evaluator outputs fall strictly within $[0.0, 1.0]$.
  - Enforces mandatory concept capping when prerequisite concepts are omitted.
  - Guards against NaN/Inf floating point anomalies.

### 2.5 `QuestionTimer` (`agents/timing/timer.py`)
- **Primary Role:** Response duration stopwatch and pacing modulator.
- **Key Responsibilities:**
  - Measures candidate response duration against target question duration.
  - Computes continuous descriptive pacing score $S_{\text{time}} \in [0, 1]$.
  - Computes bounded timing modifier $f_{\text{time}} \in [-0.10, +0.03]$.
  - Enforces the invariant that fast incorrect answers ($S_{\text{tech}} < 0.70$) never receive speed bonuses.

### 2.6 `DockerCSandbox` (`agents/coding_executor/coding_executor.py`)
- **Primary Role:** Real isolated C compilation and execution engine.
- **Key Responsibilities:**
  - Pre-validates source code safety against banned headers (e.g. `<windows.h>`, raw system calls).
  - Mounts candidate source into an isolated Alpine container with GCC 13+.
  - Compiles with strict flags (`-O2 -Wall -Wextra -Werror=return-type`).
  - Executes candidate binary against multi-case test harnesses under 128MB RAM, 32 PIDs, and 2.0s timeouts.
  - Classifies execution outcomes: `accepted`, `wrong_answer`, `compilation_error`, `runtime_error` (segfault), `timeout`, `memory_limit_exceeded`.

### 2.7 `SessionLogger` (`agents/orchestrator/session_logger.py`)
- **Primary Role:** Audit and research event persistence.
- **Key Responsibilities:**
  - Logs turn-by-turn timestamps, candidate transcripts, code submissions, evaluator breakdown vectors, RL observations, actions, and decision sources to JSONL format.

---

## 3. Inter-Agent Communication Contracts

| Originating Agent | Target Agent | Request Payload | Response Schema |
|---|---|---|---|
| `InterviewOrchestrator` | `HybridOrchestrator` | `(score: float, current_diff: int, state: dict)` | `(new_diff: int, reason: str, action: str)` |
| `InterviewOrchestrator` | `FeedbackAgent` | `(transcript: str, question: dict, eval_result: dict)` | `dict` (formative feedback, breakdown, status) |
| `InterviewOrchestrator` | `QuestionTimer` | `start(allowed_sec, qid)` / `stop(snapshot)` | `dict` (elapsed, ratio, time_norm, overrun) |
| `InterviewOrchestrator` | `DockerCSandbox` | `compile_and_run(code, test_cases, limits)` | `dict` (status, pass_rate, stdout, stderr, ms) |
