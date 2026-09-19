# Reproducible Engineering Test Manifest

**Timestamp:** 2026-09-17T22:27:03+05:30  
**Git Head Commit:** `9cfd34f278de8cc6b2810a4855b571b6b7264495` (`9cfd34f`)  
**Git Branch:** `workspace/human-eval-clean-push`  
**Execution Environment:** Windows 11 / `.venv` (Python 3.12.7, PyTorch 2.11.0+cpu, Stable-Baselines3 2.7.1, FAISS 1.13.2)  
**Exact Shell Command (Backend):** `.\.venv\Scripts\python.exe -m pytest tests/ -q`  
**Exact Shell Command (Frontend):** `npm --prefix apps/web run test:ci`  
**Exact Shell Command (Build):** `npm --prefix apps/web run build`  

---

## 1. Test Execution Verification

### 1.1 Backend Test Suite (`pytest tests/ -q`)
| Category | Metric | Result |
|---|---|:---:|
| **Discovery** | Total Discovered Tests | **205** |
| **Execution** | Total Executed Tests | **205** |
| **Outcome** | Passed Tests | **205 (100% PASS)** |
| **Failures** | Failed Tests | **0** |
| **Skips** | Skipped Tests | **0** |
| **Warnings** | Deprecation / Model Config Warnings | 309 |
| **Execution Time** | Total Wall-Clock Runtime | 440.19 seconds (7m 20s) |

### 1.2 Frontend Test Suite (`vitest run`)
| Category | Metric | Result |
|---|---|:---:|
| **Test Files** | Total Executed Test Files | **2** (`layout.test.jsx`, `ui_fixes.test.jsx`) |
| **Execution** | Total Executed Tests | **20** |
| **Outcome** | Passed Tests | **20 (100% PASS)** |
| **Failures** | Failed Tests | **0** |
| **Skips** | Skipped Tests | **0** |
| **Execution Time** | Total Wall-Clock Runtime | 2.07 seconds |

### 1.3 Production Frontend Distribution Build (`vite build`)
| Category | Metric | Result |
|---|---|:---:|
| **Status** | Compilation & Chunking | **SUCCESS (0 errors, 0 warnings)** |
| **Transformed Modules** | Total Modules Transformed | **57** |
| **Build Duration** | Wall-Clock Runtime | **864 ms** |
| **Artifacts** | Output Assets | `dist/index.html` (1.82 kB)<br>`dist/assets/index-cw2DIPLZ.css` (47.86 kB)<br>`dist/assets/index-DDy7VFzy.js` (107.24 kB)<br>`dist/assets/react-jVyfcstf.js` (140.78 kB) |

---

## 2. Test Inventory Breakdown by Subsystem

### Unit Test Suites (193 Tests)
1. `tests/unit/test_persistence_and_history.py` (**14 tests**): SQLite schema migrations, candidate resolution, attempt numbering, retry rollbacks, compound tie-breaking.
2. `tests/unit/test_rl_env.py` (**19 tests**): 6D observation space bounds, 3-action transitions, reward formulation, episode termination conditions.
3. `tests/unit/test_evaluator.py` (**11 tests**): S1 semantic, S2 concept, R reasoning, keyword-stuffing dampening, mandatory concept caps.
4. `tests/unit/test_coding_executor.py` (**22 tests**): Docker compilation, runtime error segregation (SIGSEGV, timeout, OOM), capabilities, read-only root, tmpfs.
5. `tests/unit/test_orchestrator.py` (**20 tests**): FSM states, baseline warm-up phase, guardrail triggers, concurrency serialization via `asyncio.Lock()`.
6. `tests/unit/test_personalization_questions.py` (**14 tests**): 100+ question bank validity, rubric bank integrity, lexical overlap prevention.
7. `tests/unit/test_qwen_followup_feedback.py` (**14 tests**): JSON schema validation, targeted misconception follow-ups, attribution logging.
8. `tests/unit/test_qwen_specific_feedback.py` (**8 tests**): Request/response schema contracts, attempt-aware feedback prompting, anti-fluff validation, contradiction detection, score leakage protection, evaluator result preservation.
9. `tests/unit/test_real_qwen_inference.py` (**1 test**): Live local inference test using `Qwen2.5-1.5B-Instruct`.
10. `tests/unit/test_speech_pipeline.py` (**12 tests**): Audio normalization, pause duration, prosodic feature extraction, hesitation scoring.
11. `tests/unit/test_stage11_3_followup_and_evaluation.py` (**15 tests**): Socratic follow-up decision policy, cap of 2, pause propagation.
12. `tests/unit/test_stage11_4_coding_verification.py` (**14 tests**): Isolated C compilation, security flags, resource bounds.
13. `tests/unit/test_stage11_5_coding_adaptation.py` (**14 tests**): Candidate state tracking, RL 6D vector isolation from coding execution times.
14. `tests/unit/test_stage11_6_full_interview_e2e.py` (**6 tests**): Production evaluator scoring, PPO inference, research artifact verification.
15. `tests/unit/test_timer_scoring.py` (**13 tests**): Pacing modifiers, overtime penalty, component breakdown transparency.

### Integration Test Suites (12 Tests)
1. `tests/integration/test_15q_demo_and_contextual_followup.py` (**5 tests**): Complete 15-question interview lifecycle, queue capping, hint omission.
2. `tests/integration/test_e2e_personalization_trajectories.py` (**1 test**): Trajectory divergence between strong and weak candidates.
3. `tests/integration/test_full_interview_lifecycle.py` (**1 test**): End-to-end multi-turn interview simulation.
4. `tests/integration/test_multiagent_responsibility_and_failures.py` (**5 tests**): Fault injection and graceful degradation across evaluator, Qwen, Docker, and RL.

---

## 3. Discrepancy & Exclusion Explanation

1. **Initial Shell Inconsistency**: When `python -m pytest` was executed via the global Anaconda base interpreter (`C:\Users\spars\anaconda3\python.exe`), an unhandled Windows C-runtime DLL error (`0xc0000139` entry point not found) occurred during collection when `torchaudio` loaded system libraries.
2. **Resolution**: All project dependencies and frozen binaries reside in the local virtual environment (`c:\Users\spars\Downloads\PrepAIred\.venv`).
3. **Verification**: When invoked via `.\.venv\Scripts\python.exe -m pytest tests/`, all 205 tests execute natively without any collection crashes, exclusions, or skipped fixtures.
4. **Baseline Evolution**: The baseline increased from 202 to 205 tests due to the addition of 3 feedback validation guardrail tests in `tests/unit/test_qwen_specific_feedback.py` (contradiction rejection, score leakage rejection, and evaluator score preservation).
