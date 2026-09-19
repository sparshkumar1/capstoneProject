# Reproducible Engineering Test Manifest

**Timestamp:** 2026-09-17T14:43:44+05:30  
**Git Head Commit:** `9cfd34f9a0c710d540209677334ae112658a086b` (`9cfd34f`)  
**Git Branch:** `workspace/human-eval-clean-push`  
**Execution Environment:** Windows 11 / `.venv` (Python 3.12.7, PyTorch 2.11.0+cpu, Stable-Baselines3 2.7.1, FAISS 1.13.2)  
**Exact Shell Command:** `.\.venv\Scripts\python.exe -m pytest tests/ -q`  

---

## 1. Test Execution Verification

| Category | Metric | Result |
|---|---|:---:|
| **Discovery** | Total Discovered Tests | **202** |
| **Execution** | Total Executed Tests | **202** |
| **Outcome** | Passed Tests | **202 (100% PASS)** |
| **Failures** | Failed Tests | **0** |
| **Skips** | Skipped Tests | **0** |
| **Warnings** | Deprecation / Mark Warnings | 309 |
| **Execution Time** | Total Wall-Clock Runtime | 640.03 seconds (10m 40s) |

---

## 2. Test Inventory Breakdown by Subsystem

### Unit Test Suites (190 Tests)
- `tests/unit/test_persistence_and_history.py` (14 tests): SQLite schema, candidate identity resolution, attempt numbering, retry rollbacks, compound tie-breaking.
- `tests/unit/test_rl_env.py` (19 tests): 6D observation space bounds, 3-action transitions, reward formulations, episode termination.
- `tests/unit/test_evaluator.py` (11 tests): Correct/partial/wrong answer scoring, keyword-stuffing dampening, mandatory concept caps.
- `tests/unit/test_coding_executor.py` (22 tests): Docker compilation, runtime error segregation (SIGSEGV, timeout, OOM), capabilities, read-only root, tmpfs.
- `tests/unit/test_orchestrator.py` (20 tests): FSM states, baseline warm-up phase, guardrail triggers, concurrency serialisation via `asyncio.Lock()`.
- `tests/unit/test_personalization_questions.py` (14 tests): 100+ question bank validity, rubric bank integrity, lexical overlap prevention.
- `tests/unit/test_qwen_followup_feedback.py` (14 tests): JSON schema validation, targeted misconception follow-ups, attribution logging.
- `tests/unit/test_qwen_specific_feedback.py` (5 tests): Request/response schema contracts, attempt-aware feedback prompting, anti-fluff validation.
- `tests/unit/test_real_qwen_inference.py` (1 test): Live local inference test using `Qwen2.5-1.5B-Instruct`.
- `tests/unit/test_speech_pipeline.py` (12 tests): Audio normalisation, pause duration, prosodic feature extraction, hesitation scoring.
- `tests/unit/test_stage11_3_followup_and_evaluation.py` (15 tests): Socratic follow-up decision policy, cap of 2, pause propagation.
- `tests/unit/test_stage11_4_coding_verification.py` (14 tests): Isolated C compilation, security flags, resource bounds.
- `tests/unit/test_stage11_5_coding_adaptation.py` (14 tests): Candidate state tracking, RL 6D vector isolation from coding execution times.
- `tests/unit/test_stage11_6_full_interview_e2e.py` (6 tests): Production evaluator scoring, PPO inference, research artifact verification.
- `tests/unit/test_timer_scoring.py` (13 tests): Pacing modifiers, overtime penalty, component breakdown transparency.

### Integration Test Suites (12 Tests)
- `tests/integration/test_15q_demo_and_contextual_followup.py` (5 tests): Complete 15-question interview lifecycle, queue capping, hint omission.
- `tests/integration/test_e2e_personalization_trajectories.py` (1 test): Trajectory divergence between strong and weak candidates.
- `tests/integration/test_full_interview_lifecycle.py` (1 test): End-to-end multi-turn interview simulation.
- `tests/integration/test_multiagent_responsibility_and_failures.py` (5 tests): Fault injection and graceful degradation across evaluator, Qwen, Docker, and RL.

---

## 3. Discrepancy & Earlier Exclusion Explanation

1. **Initial Shell Inconsistency**: When `python -m pytest` was initially executed via the global Anaconda base interpreter (`C:\Users\spars\anaconda3\python.exe`), an unhandled Windows C-runtime DLL error (`0xc0000139` entry point not found) occurred during collection when `torchaudio` loaded system libraries.
2. **Resolution**: All project dependencies and frozen binaries reside in the local virtual environment (`c:\Users\spars\Downloads\PrepAIred\.venv`).
3. **Verification**: When invoked via `.\.venv\Scripts\python.exe -m pytest tests/`, all 202 tests execute natively without any collection crashes, exclusions, or skipped fixtures.