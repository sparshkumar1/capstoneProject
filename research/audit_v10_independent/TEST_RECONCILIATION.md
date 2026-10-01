# Test Suite Reconciliation & Execution Audit (V10)

**Date**: 2026-09-30  
**Auditor**: Independent Software Verification Engineer  
**Scope**: Reconciliation of Test Counts (16 vs. 41 vs. 53 vs. 87 vs. 314), Execution Verification, and Coverage Gap Analysis  

---

## 1. EXECUTIVE SUMMARY: THE "16 VERSUS 41" TEST RECONCILIATION

The prompt highlighted an apparent discrepancy between the **41 relevant targeted tests** reported in earlier audit passes and the **16 passing tests** cited in the V10 validation report.

### Root Cause & Definitive Finding:
**There is no discrepancy, deletion, or contradiction.** The two numbers represent two distinct, legitimate, and intentionally scoped test selections designed for different verification objectives:

1. **The 16 Tests** represents the **narrow, targeted regression suite** written specifically for the **ScoreValidator reliability hardening** and evaluator infrastructure outage propagation. These 16 tests reside in exactly two files:
   - `tests/unit/test_score_validator.py` (11 tests)
   - `tests/unit/test_evaluator_infrastructure_failure_flag.py` (5 tests)
   - **Sum**: $11 + 5 = \mathbf{16\text{ tests}}$.
   - These 16 tests were executed fresh against the active V10 code snapshot: **16 passed in 14.95s**.

2. **The 41 Tests** represents the **core technical evaluator behavior suite** evaluated during earlier audit passes prior to the isolated ScoreValidator split:
   - `tests/unit/test_evaluator.py`: 11 basic evaluator tests (correct answer, partial credit, wrong answer, keyword stuffing, missing concept, etc.)
   - `tests/unit/test_score_validator.py`: 11 score validation tests (type parsing, NaN/Inf, mandatory caps, mistake penalties, coding multipliers)
   - `tests/unit/test_evaluator_outage_and_sandbox_cleanup.py`: 9 fail-closed outage tests (evaluator down, timeout, retryable attempt preservation, Docker container cleanup)
   - `tests/unit/test_evaluator_v4_adversarial_development_suite.py`: 10 adversarial behavior tests (misconceptions, repetition dedup, alternative phrasing)
   - **Sum**: $11 + 11 + 9 + 10 = \mathbf{41\text{ tests}}$.

### Status of Tests:
- **Were any tests deleted?** **NO.** Every single test from the 41-test suite remains present and functional in the repository.
- **Were any tests skipped?** **NO.** 0 tests skipped in both suites.
- **Is 16 a subset of 41?** **Partial overlap**: 11 of the 16 tests (`test_score_validator.py`) are directly part of the 41-test core suite; the remaining 5 tests (`test_evaluator_infrastructure_failure_flag.py`) were created to test end-to-end propagation through `InterviewOrchestrator._evaluate_verbal` to verify that invalid scores are not converted into legitimate zero candidate attempts.

---

## 2. COMPREHENSIVE TEST SUITE TAXONOMY

To prevent future confusion among reviewers and auditors, the following table summarizes all five test selections documented across PrepAIred revisions:

| Test Selection Label | Count | Exact Command / Specification | Scope & Purpose |
|---|:---:|---|---|
| **V10 Targeted Regression Suite** | **16** | `pytest -q tests/unit/test_score_validator.py tests/unit/test_evaluator_infrastructure_failure_flag.py` | Specifically verifies `ScoreValidator` handling of NaN, Inf, None, malformed strings, contradictory `"success"` status, and orchestrator propagation. |
| **Core Evaluator Behavior Suite** | **41** | `pytest -q tests/unit/test_evaluator.py tests/unit/test_score_validator.py tests/unit/test_evaluator_outage_and_sandbox_cleanup.py tests/unit/test_evaluator_v4_adversarial_development_suite.py` | Verifies verbal scoring mechanics, rubrics, fail-closed outages, and adversarial robustness. |
| **Five-File Component Selection** | **53** | `pytest -q tests/unit/test_evaluator.py tests/unit/test_evaluator_infrastructure_failure_flag.py tests/unit/test_evaluator_outage_and_sandbox_cleanup.py tests/unit/test_orchestrator.py tests/unit/test_score_validator.py` | Component-level verification of all 5 primary evaluator and orchestrator test files. |
| **Keyword Filter Selection** | **87** | `EVALUATOR_MOCK_MODE=1 pytest -q tests/unit/ -k "validat or orchestrator or evaluat"` | Keyword-matched subset across all 16 test files (53 core tests + 34 auxiliary tests with matching substrings in test names). |
| **Full Backend Suite** | **314** | `pytest tests/unit/` (unfiltered) | Complete unit test coverage across all subsystems (speech, RL, orchestrator, scoring, database, executors). 314 passed, 1 skipped, 1 pre-existing failure (`test_stage11_5_coding_adaptation.py`). |

---

## 3. FRESH TEST EXECUTION EVIDENCE (V10 SNAPSHOT)

### 3.1 Execution of the 16 Targeted Regression Tests
Executed fresh on Python 3.12.7 in worktree `exp032-orchestrator-concept-list-fix`:
```bash
pytest -q tests/unit/test_score_validator.py tests/unit/test_evaluator_infrastructure_failure_flag.py
```

**Output Log**:
```text
................                                                         [100%]
16 passed in 14.95s
```

**Individual Test Breakdown**:
1. `test_score_validator.py::test_validator_clamps_out_of_range_numeric` — **PASSED**
2. `test_score_validator.py::test_validator_handles_missing_and_none_score` — **PASSED**
3. `test_score_validator.py::test_validator_handles_wrong_type_and_non_numeric` — **PASSED**
4. `test_score_validator.py::test_validator_handles_nan_and_inf` — **PASSED**
5. `test_score_validator.py::test_validator_handles_malformed_and_none_evidence` — **PASSED**
6. `test_score_validator.py::test_validator_enforces_mandatory_cap_on_contradictory_evaluation` — **PASSED**
7. `test_score_validator.py::test_validator_applies_mistake_penalty` — **PASSED**
8. `test_score_validator.py::test_validator_penalizes_coding_failures` — **PASSED**
9. `test_score_validator.py::test_validator_distinguishes_infrastructure_failure_from_candidate_failure` — **PASSED**
10. `test_score_validator.py::test_validator_flags_non_finite_score_as_infrastructure_failure` — **PASSED**
11. `test_score_validator.py::test_validator_does_not_accept_invalid_score_under_success_status` — **PASSED**
12. `test_evaluator_infrastructure_failure_flag.py::test_score_validator_non_finite_score_flagged_as_infrastructure_failure` — **PASSED**
13. `test_evaluator_infrastructure_failure_flag.py::test_evaluate_verbal_propagates_non_finite_flag_and_logs_infrastructure_error` — **PASSED**
14. `test_evaluator_infrastructure_failure_flag.py::test_evaluate_verbal_genuine_zero_score_is_not_flagged_as_infrastructure_failure` — **PASSED**
15. `test_evaluator_infrastructure_failure_flag.py::test_evaluate_verbal_missing_score_is_not_reported_as_success` — **PASSED**
16. `test_evaluator_infrastructure_failure_flag.py::test_evaluate_verbal_nonnumeric_score_is_not_reported_as_success` — **PASSED**

---

## 4. DETAILED CODE PATH TRACE (SCORE-VALIDATION DEFECT)

The audit traced the complete execution path from evaluator HTTP response to session state persistence:

```
[Candidate Audio / Spoken Answer]
                │
                ▼
[InterviewOrchestrator.handle_voice_answer()]
                │
                ▼
[InterviewOrchestrator._evaluate_verbal()]
                │
                ▼
[HTTP Request to Evaluator Microservice (S1 + S2 + R)]
                │
                ▼
[Evaluator Response Payload: raw dict]
                │
                ├───────────────────────────────────────────────────────┐
                ▼                                                       ▼
   Case A: Genuine Candidate Answer                        Case B: Upstream Failure / Anomaly
   (e.g., final_score: 0.0 or 0.72)                        (e.g., final_score: None, "NaN", "err")
                │                                                       │
                ▼                                                       ▼
[ScoreValidator.validate(raw_score, ev)]                [ScoreValidator.validate(raw_score, ev)]
  - Structural check: valid float                         - Catches ValueError/TypeError or isnan()
  - non_finite = False                                    - non_finite_score = True / invalid_score = True
  - Mandatory cap / mistake penalty checks                - Clamps numeric score to safe 0.0
  - eval_status = "success"                               - Overrides contradictory upstream status:
  - is_infra_failure = False                                  eval_status = "non_finite_score" / "invalid_score"
                │                                             is_infra_failure = True
                ▼                                                       │
[Orchestrator Process Result]                                           ▼
  - Updates candidate history                             [Orchestrator Process Result]
  - Updates RL state vector                                 - Appends to _state["infrastructure_errors"]
  - Feeds into candidate report                             - Prevents unearned penalty to candidate
                                                            - Flags retryable turn / alert logged
```

### Verification of Behavioral Invariants:
1. **Missing Score (`final_score: None`)**:
   - `invalid_score = True`, `validated_score = 0.0`.
   - `evaluation_status = "invalid_score"`, `is_infrastructure_failure = True`.
   - **PASS**: Verified in test 2 and test 15.
2. **Non-numeric String (`final_score: "parse_error"`)**:
   - `invalid_score = True`, `validated_score = 0.0`.
   - `evaluation_status = "invalid_score"`, `is_infrastructure_failure = True`.
   - **PASS**: Verified in test 3 and test 16.
3. **Non-finite Float (`NaN`, `+Inf`, `-Inf`)**:
   - `non_finite_score = True`, `validated_score = 0.0`.
   - `evaluation_status = "non_finite_score"`, `is_infrastructure_failure = True`.
   - **PASS**: Verified in test 4, test 10, test 12, and test 13.
4. **Contradictory Upstream Status (`evaluation_status: "success"` paired with `NaN` or `None`)**:
   - Defensive override forces `eval_status = "non_finite_score"` (or `"invalid_score"`).
   - `is_infrastructure_failure = True`.
   - Upstream bug cannot fool downstream orchestrator into treating infrastructure crash as successful zero candidate score.
   - **PASS**: Verified in test 11.
5. **Legitimate Candidate Zero (`final_score: 0.0`)**:
   - `invalid_score = False`, `non_finite_score = False`, `validated_score = 0.0`.
   - `evaluation_status = "success"`, `is_infrastructure_failure = False`.
   - Zero score is NOT flagged as infrastructure failure; candidate history accurately records weak performance.
   - **PASS**: Verified in test 14.

---

## 5. TESTING COVERAGE GAPS & ENVIRONMENT BOUNDARIES

In accordance with strict verification integrity, the audit explicitly records the boundaries of automated testing in the active environment:

1. **Hardware Voice Pipeline**:
   - Audio capture via microphone, hardware soundcards, and interactive browser speech recognition are tested via unit mock audio streams and pre-recorded WAV samples. Live human spoken testing requires interactive physical setup.
2. **Live Ephemeral Docker Daemon**:
   - Hardened Docker sandbox container creation, execution, and cleanup are tested via unit mocks (`test_evaluator_outage_and_sandbox_cleanup.py`). Running live ephemeral containers against untrusted C code requires an active Docker Desktop engine daemon.
3. **Local GPU LLM Acceleration**:
   - Development tests utilize `EVALUATOR_MOCK_MODE=1` or CPU inference. True GPU-accelerated tensor generation with `Qwen2.5-1.5B-Instruct` requires a CUDA-enabled runtime environment.
4. **Known Pre-existing Suite Failure**:
   - As documented in `CLAUDE.md` and prior mission logs, `test_stage11_5_coding_adaptation.py` contains 1 pre-existing failure in full unfiltered runs (`314 passed, 1 skipped, 1 failed`). This test expects an older coding difficulty mapping that was superseded during the RL guardrail refactor and does not affect verbal evaluation or ScoreValidator.
