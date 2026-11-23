# Test Execution Summary — Final Evaluation Phase

Exact, denominator-explicit counts for every suite run this phase. No aggregation across incompatible categories (unit/integration counts are kept separate from RL/ML/Qwen spot-checks).

## 1. Backend `pytest` — full suite, pre-fix baseline (this phase, before any code change)

Command: `EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest tests/ -q`
Result: **264 passed, 19 failed, 15 skipped, 0 collection errors** (283 executable tests; 93.3% pass rate).
Log: `testing_output/logs/full_pytest_prefix.log`.

## 2. Backend `pytest` — full suite, post-fix (after all 3 application code changes)

Command: `EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest tests/ -q`
Result: **264 passed, 19 failed, 15 skipped, 4 warnings, 0 collection errors** — run time 953.32s (15m53s).
Log: `testing_output/logs/full_pytest_postfix.log`.

**Identical split to §1.** The 19 failures, itemized from the actual log:

| # | Test | Cause |
|---|---|---|
| 1–13 | `tests/unit/test_coding_executor.py::test_docker_*` (13 tests: compile/run, wrong-answer, compile-error, segfault, timeout, OOM, network-isolation, PID-limit, output-truncation, non-root-uid, read-only-fs, partial-credit 7/10, mandatory-test-cap) | Docker daemon unreachable (environment gap, not code) |
| 14–16 | `tests/unit/test_stage11_5_coding_adaptation.py::test_accepted_coding_result_updates_candidate_state`, `test_partial_coding_result_updates_candidate_state`, `test_failed_coding_result_compilation_error` | Same Docker dependency (these tests drive the coding flow through the real sandbox) |
| 17 | `tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` | The pre-existing, previously-documented known failure (`obs[4]` 0.0 vs 0.22 expected) — per `CLAUDE.md`, "unresolved, not to be fixed until decided"; reproduced identically, not touched |
| 18–19 | `tests/unit/test_stage11_6_full_interview_e2e.py::test_full_interview_lifecycle`, `test_coding_partial_credit_in_sandbox` | Same Docker dependency |

18 of 19 are Docker-environment-blocked (unchanged from the pre-fix baseline and from the original `Master_Results_Table.md` §1 record); 1 of 19 is the single pre-existing known issue named in `CLAUDE.md`, left alone per instruction. **Zero new failures, zero newly-passing tests that were previously failing, zero change in skip count.** This is direct evidence that `services/qwen/app.py`, `apps/backend/main.py`, `services/storage/database.py`, and `rl/env/interview_env.py` changes did not alter any test outcome anywhere in the backend suite.

## 3. Frontend `Vitest`

Command: `npm test -- --run` (from `apps/web`)
Result: **28/28 passed**, 4 test files — run both before and after this phase's changes, identical both times.

## 4. New targeted evidence this phase (not part of the `pytest`/`Vitest` totals above)

| Check | Result |
|---|---|
| Gymnasium `check_env()` on `InterviewEnv` | **PASSED**, no warnings |
| SHA-256 recomputation, deployed PPO checkpoint | `2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575` (confirmed, matches prior record) |
| SHA-256 recomputation, evaluated PPO checkpoint | `299437ea0dcdd7a5eed51326e80854bd3bb55341194420b619c5da3d675e24e0` (confirmed, matches prior record; distinct from deployed) |
| Guardrail-fallback boundary re-test (`T-N03` extended, 5 new cases at perf=0.28/0.30/0.32/0.39/0.40) | **5/5 PASS** after the `rl/env/interview_env.py` fix (0/5 passed before, by design — the dormant path previously used the stale `0.40<perf` bound) |
| Qwen 12-criterion quality rubric, 4 real captured samples | Executed; 2 new findings (1 fixed this phase, 1 documented only) — see `07_Qwen_Feedback_Quality_Evaluation.md` |
| `list_sessions()` direct call, isolated process | 27 persisted sessions returned, cross-checked against raw `sqlite3 data/prepaired.db "SELECT COUNT(*) FROM sessions"` |

## 5. What this does and does not prove

Proves: the three code changes are regression-free against the entire existing automated test suite, and each change's own targeted before/after evidence shows the intended bug is fixed. Does **not** prove: full browser-level E2E coverage (not available in this environment), Docker-sandbox correctness under live execution (daemon unreachable throughout), or any claim about PPO's incremental value (unchanged, out of this phase's executed scope — see `06_RL_Evaluation_Results.md` and `11_Experiment_Provenance_Register.md`).
