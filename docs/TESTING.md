# PrepAIred — Automated Testing Suite & Verification Guide

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Test Suite Architecture

PrepAIred maintains comprehensive automated test suites covering unit components, multi-agent integration, dockerized sandbox execution, and web frontend UI contracts:

- **Backend Pytest Suite:** 178 collected tests (177 fast automated unit/integration tests + 1 live GPU test).
- **Frontend Vitest Suite:** 7 automated UI component and layout tests.
- **Coverage Areas:** Multi-component evaluator, PPO policy loading, 6D observation bounds, 3-level question deduplication, Docker C security/runtime isolation, follow-up hard caps, timing equations, and UI error boundaries.

---

## 2. Test Suite Directory Breakdown

```
tests/
├── unit/
│   ├── test_evaluator.py                           # 13 tests: Evaluator S1, S2, R, dampening, caps
│   ├── test_rl_env.py                              # 15 tests: Gym InterviewEnv, observation, actions
│   ├── test_coding_executor.py                     # 20 tests: Docker C compilation, segfaults, OOM, timeout
│   ├── test_timer_scoring.py                       # 18 tests: Timing bounds, f_time, fast wrong invariance
│   ├── test_qwen_followup_feedback.py              # 14 tests: Grounded follow-ups, feedback schema, attribution
│   ├── test_personalization_questions.py           # 13 tests: 3-level deduplication, Easy start, Q125 bank
│   ├── test_speech_pipeline.py                     # 15 tests: WhisperX, WPM, pause rate, hesitation derivation
│   ├── test_orchestrator.py                        # 20 tests: Session lifecycle, baseline warmup, guardrails
│   ├── test_stage11_3_followup_and_evaluation.py   # 14 tests: Feedback contract, 2-turn FU hard cap
│   ├── test_stage11_4_coding_verification.py       # 14 tests: Coding turn state updates, isolation
│   ├── test_stage11_5_coding_adaptation.py         # 14 tests: 6D observation invariant after coding
│   ├── test_stage11_6_full_interview_e2e.py        #  6 tests: End-to-end full 15-question session
│   └── test_real_qwen_inference.py                 #  1 test:  (Marked for live GPU / Ollama)
└── integration/
    ├── test_multiagent_responsibility_and_failures.py # 5 tests: Subservice failure isolation
    ├── test_full_interview_lifecycle.py            # 1 test:  Complete WebSocket session lifecycle
    └── test_e2e_personalization_trajectories.py    # 1 test:  Strong vs weak candidate trajectory divergence
```

---

## 3. Running Test Suites

### 3.1 Running the Complete Backend Suite

```bash
# Run all unit and integration tests (excluding live GPU test)
pytest tests/unit/ tests/integration/ -v -m "not live_gpu"

# Run with full output and timing
pytest tests/unit/ tests/integration/ -v --durations=10
```

### 3.2 Running Subsystem Test Suites

```bash
# Evaluator & Scoring Tests
pytest tests/unit/test_evaluator.py tests/unit/test_timer_scoring.py -v

# Reinforcement Learning & Observation State Tests
pytest tests/unit/test_rl_env.py tests/unit/test_stage11_5_coding_adaptation.py -v

# Docker C Sandbox & Coding Executor Tests
pytest tests/unit/test_coding_executor.py tests/unit/test_stage11_4_coding_verification.py -v

# Follow-Up & Feedback System Tests
pytest tests/unit/test_qwen_followup_feedback.py tests/unit/test_stage11_3_followup_and_evaluation.py -v

# Personalization & Deduplication Tests
pytest tests/unit/test_personalization_questions.py -v
```

### 3.3 Running Frontend UI Tests

```bash
# Run Vitest suite in CI mode
npm run --prefix apps/web test:ci
```

---

## 4. Test Invariants Enforced by CI

1. **6D RL State Invariant:** No test or code path may expand the RL observation vector beyond 6 dimensions.
2. **Technical Dominance Invariant:** Fast incorrect answers ($S_{\text{tech}} < 0.70$) must strictly receive $f_{\text{time}} = 0.0$.
3. **Attribution Invariant:** Offline non-LLM structured recovery must never report `decision_source = "qwen_*_llm"`.
4. **Sandbox Security Invariant:** Any submission attempting dangerous system calls or forbidden headers must be blocked or isolated within the unprivileged container.
5. **No Mock Fallback Invariant:** Frontend report components must never fall back to fake candidate data on network error.
