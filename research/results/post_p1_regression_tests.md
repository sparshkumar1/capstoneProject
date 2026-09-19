# Post-P1 Full Regression Test Report

**Execution Timestamp:** September 19, 2026  
**Auditor:** Senior Research Engineer & Systems Verification Lead  
**Git Commit / Checkpoint:** Post-P1 Hardening (`workspace/human-eval-clean-push`)  
**Status:** **100% PASS ACROSS ALL SUITES**

---

## 1. Executive Summary

Following P1 non-human preparation and `ScoreValidator` defensive hardening, the complete test suite across all application tiers (Python FastAPI backend, React/Vite frontend, and Vite production bundle pipeline) was executed to verify zero regression.

| Test Suite | Total Collected | Passed | Failed | Skipped | Execution Time | Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Backend Full Suite (`pytest`)** | 213 | **213** | 0 | 0 | 426.48s (07:06) | **PASS** |
| **Frontend Full Suite (`vitest`)** | 20 | **20** | 0 | 0 | 6.29s | **PASS** |
| **Frontend Production Build (`vite build`)** | 57 modules | **57** | 0 | 0 | 3.30s | **PASS** |

---

## 2. Backend Suite Details (`pytest`)

- **Command Executed:** `.venv\Scripts\python -m pytest`
- **Configuration:** `pyproject.toml`
- **Environment:** Python 3.12.7, Pytest 9.0.3, Pluggy 1.6.0, AnyIO 4.13.0, AsyncIO 1.3.0
- **Breakdown by Component:**
  - `tests/integration/test_15q_demo_and_contextual_followup.py`: 5 passed
  - `tests/integration/test_e2e_personalization_trajectories.py`: 1 passed
  - `tests/integration/test_full_interview_lifecycle.py`: 1 passed
  - `tests/integration/test_multiagent_responsibility_and_failures.py`: 5 passed
  - `tests/unit/test_coding_executor.py`: 20 passed
  - `tests/unit/test_evaluator.py`: 11 passed
  - `tests/unit/test_orchestrator.py`: 20 passed
  - `tests/unit/test_persistence_and_history.py`: 14 passed
  - `tests/unit/test_personalization_questions.py`: 13 passed
  - `tests/unit/test_qwen_followup_feedback.py`: 14 passed
  - `tests/unit/test_qwen_specific_feedback.py`: 8 passed
  - `tests/unit/test_real_qwen_inference.py`: 1 passed
  - `tests/unit/test_rl_env.py`: 18 passed
  - `tests/unit/test_score_validator.py`: **8 passed** *(New defensive guardrail suite)*
  - `tests/unit/test_speech_pipeline.py`: 9 passed
  - `tests/unit/test_system_resilience.py`: 16 passed
  - `tests/unit/test_timer.py`: 7 passed
  - `tests/unit/test_whisper_integration.py`: 42 passed
- **Total:** **213 passed, 309 warnings in 426.48s**

---

## 3. Frontend Suite Details (`vitest`)

- **Command Executed:** `npm run test:ci` (`vitest run` in `apps/web/`)
- **Environment:** Node.js, Vitest 2.1.9, JSDOM 26.0.0, React 18.3.1
- **Test Files:**
  - `src/__tests__/layout.test.jsx`: 3 passed (391ms)
  - `src/__tests__/ui_fixes.test.jsx`: 17 passed (1725ms)
- **Total:** **20 passed (2 test files) in 6.29s**

---

## 4. Production Build Details (`vite build`)

- **Command Executed:** `npm run build` (`vite build` in `apps/web/`)
- **Environment:** Vite 5.4.21
- **Bundle Output:**
  - `dist/index.html`: 1.82 kB (gzip: 0.92 kB)
  - `dist/assets/index-cw2DIPLZ.css`: 47.86 kB (gzip: 10.03 kB)
  - `dist/assets/index-DDy7VFzy.js`: 107.24 kB (gzip: 28.68 kB)
  - `dist/assets/react-jVyfcstf.js`: 140.78 kB (gzip: 45.24 kB)
- **Transformation:** 57 modules transformed in 3.30s with zero errors and zero build warnings.
