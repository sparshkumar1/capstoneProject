# PrepAIred — All Tests, End-to-End: Complete Test and Evaluation Register

**Purpose of this document.** A single, consolidated register of every distinct test, evaluation, or verification activity performed on the PrepAIred project across its entire evidence-generation history available to this engagement — both the original Phase 2/3 comprehensive testing programme and the later Final Evaluation Phase (Task 6, "controlled improvements"). It supersedes no prior document; every row below traces to a specific stored log, script, or result file. Git branch: `final-eval/controlled-improvements`, base commit `9d5c528b3596d0d80c6bb8d606547f64c036b081`.

## 1. How to read this register

- **Result** states the literal outcome as measured, not an interpretation.
- **Evidence** points to the exact file/script this result traces to.
- Rows are grouped by category, not by when they ran, so a reader can find "everything about the database" or "everything about PPO" in one place.
- Frozen research results (human-correlation study, PPO baseline comparison, confirmatory equivalence test) are included for completeness but are **not** re-executed by this engagement; they are cited from their existing, unmodified source files.

## 2. Automated regression suites

| # | Test | Run | Result | Evidence |
|---|---|---|---|---|
| 1 | Backend `pytest`, full suite | Phase 2/3 baseline (pre any Task-6 code change) | 264 passed, 19 failed, 15 skipped (283 executable, 93.3%) | `testing_and_evaluation/logs/full_suite_after_guardrail_fix.log` |
| 2 | Backend `pytest`, full suite | Final Evaluation Phase, pre-fix re-confirmation | 264/19/15, identical | `testing_output/logs/full_pytest_prefix.log` |
| 3 | Backend `pytest`, full suite | Final Evaluation Phase, **post** all 3 code changes | **264/19/15, identical — zero regressions** (953.32s) | `testing_output/logs/full_pytest_postfix.log` |
| 4 | Frontend `Vitest` | Both before and after this phase's changes | 28/28 passed, both times | `apps/web` test run logs |

**All 19 persistent failures, same in every run:** 18 trace to the Docker daemon being unreachable in this environment (sandboxed code-execution tests); 1 is the single pre-existing, already-documented known issue (`test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`), deliberately left unresolved pending a decision, per `CLAUDE.md`.

## 3. Targeted scripts — Phase 2/3 (10 scripts, all with real executed output)

| ID | Category | Result | Evidence |
|---|---|---|---|
| T-N01 | Smoke test | Services started OK; **launcher Unicode crash found & fixed** | `testing_and_evaluation/baseline_results/T-N01_smoke_test_finding.md` |
| T-N02 | RL policy inference sanity | **10/10** constructed scenarios produced valid actions, real checkpoint confirmed loaded | `testing_and_evaluation/rl_evaluation/T-N02_*` |
| T-N03 | Guardrail boundary verification | **13/13** pass after the G5 fix (originally 11, +2 new boundary cases) | `testing_and_evaluation/rl_evaluation/T-N03_*` |
| T-N04 | Evaluator API contract | **7/7** pass (health, validation, 200/400/404 paths) | `testing_and_evaluation/api_tests/T-N04_*` |
| T-N06 | Evaluator adversarial/edge-case input | **10/10** handled, no crash, all scores in [0,1] | `testing_and_evaluation/security_privacy/T-N06_*` |
| T-N09 | Latency spot-check | Median 896.1ms, p95 986.3ms (n=30, warm, this host) | `testing_and_evaluation/performance_tests/T-N09_*` |
| T-N10 | Question selection correctness | **15/15** distinct, perfect topic rotation; corrected the "FAISS retrieval" claim (rule-based) | `testing_and_evaluation/` |
| T-N11 | Database CRUD/consistency | **0/52, 0/26** orphaned foreign keys; roundtrip verified | `testing_and_evaluation/database_tests/T-N11_*` |
| T-N12 | Sandbox security config review | All claimed Docker isolation flags confirmed present (static review) | `testing_and_evaluation/security_privacy/T-N12_*` |
| T-N13 | Compatibility/deployment | Python 3.11.9 local vs 3.12 Docker target documented; build untestable (daemon down) | `testing_and_evaluation/compatibility/T-N13_*` |
| T-N14 | Structured UI inspection | Deliberate error/loading-state handling confirmed, both primary views | `testing_and_evaluation/ui_tests/T-N14_*` |

## 4. New/extended scripts — Final Evaluation Phase (Task 6)

| # | Test | Result | Evidence |
|---|---|---|---|
| 1 | Gymnasium `check_env()` on `InterviewEnv` | **PASSED**, no warnings — new category, not previously run | `testing_and_evaluation/final_evaluation/06_RL_Evaluation_Results.md` |
| 2 | PPO checkpoint SHA-256 re-verification (deployed vs. evaluated) | Both confirmed; **genuinely distinct files**, not swapped/mislabeled | `testing_and_evaluation/final_evaluation/06_RL_Evaluation_Results.md` §2 |
| 3 | T-N03 extended — 5 new boundary cases on the dormant guardrail-fallback path | **5/5 pass** after the `rl/env/interview_env.py` sync fix (0/5 before, by construction) | `testing_and_evaluation/final_evaluation/03_Test_Execution_Summary.md` §4 |
| 4 | Qwen 12-criterion narrative-quality rubric, 4 real captured samples | 1 defect found & fixed (JSON character-splitting); 1 limitation documented, not fixed (factually-confused explanation; hallucinated structured-field content) | `testing_and_evaluation/final_evaluation/07_Qwen_Feedback_Quality_Evaluation.md` |
| 5 | Admin-dashboard restart-survival check (`list_sessions()`) | **27 historical sessions** recovered (0 before the fix), cross-checked against raw SQL | `testing_and_evaluation/final_evaluation/Application_Code_Changes.md` |
| 6 | ρ-value reconciliation (0.4825 vs 0.4832; 0.4897 vs 0.4884) | **No numeric error found** — both pairs are distinct, correctly-used quantities | `testing_and_evaluation/final_evaluation/05_ML_Evaluation_Results.md` §2 |

## 5. Frozen research evidence (cited, not re-run)

| # | Study | Result | Evidence |
|---|---|---|---|
| 1 | Evaluator human-correlation study | Spearman ρ = 0.3812, 95% CI [0.158, 0.577]; 3 raters, 64 constructed answers, 8 questions | `research/results/paper2/paper2_ablation_results.csv` |
| 2 | Evaluator component ablation | R-only 0.483 [0.246,0.698]; S1+R 0.488 [0.254,0.712]; S1-only 0.207 [-0.023,0.501]; word-count baseline 0.490 [0.219,0.708] | same |
| 3 | PPO vs. baseline tracking-MAE comparison | Fixed 1.200; Heuristic 0.473; PPO raw 0.804; PPO+Guardrails 0.677 (5 personas × 5 seeds) | `research/results/paper3/paper3_baseline_results.csv` |
| 4 | Pre-registered confirmatory equivalence test (`X3A-C001`) | 95% CI for PPO+Guardrails minus Constant-Same+Guardrails crosses zero; within the pre-registered δ=0.12 MAE equivalence margin | `research/confirmatory/` + `research/audit/PHASE0_DECISION_LOCK.md` |

## 6. What this register does not include

No fabricated or estimated result is included anywhere above. Explicitly out of scope / not executed in this engagement: WER/CER speech-accuracy testing (no reference transcripts exist — a protocol is defined, not run, in `testing_and_evaluation/final_evaluation/08_Speech_Evaluation.md`); Docker-sandbox execution-level tests (daemon unreachable throughout); genuine browser-level E2E automation (no tool available); any new PPO training run (a protocol is defined, not run, in `testing_and_evaluation/final_evaluation/11_Experiment_Provenance_Register.md` §3); a length-bias probe for the evaluator.

## 7. Reproducibility

- **Commands:** `EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest tests/ -q`; `npm test -- --run` (from `apps/web`); individual scripts under `testing_and_evaluation/{rl_evaluation,ml_evaluation,api_tests,database_tests,security_privacy,compatibility,ui_tests,performance_tests,final_evaluation}/`.
- **Environment:** Windows 11 Pro, Python 3.11.9 (Phase 2/3) / `.venv` current pins (Final Evaluation Phase), Stable-Baselines3 2.8.0, pytest 9.2.0.
- **Checkpoint hashes:** deployed `2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575`; evaluated `299437ea0dcdd7a5eed51326e80854bd3bb55341194420b619c5da3d675e24e0`.
