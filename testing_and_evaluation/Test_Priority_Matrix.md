# Test Priority Matrix

Concrete, executable test items derived from `Test_Strategy.md`'s ESSENTIAL/RECOMMENDED rows. "Existing" = maps to a test file already in the repo (run as-is). "New — proposed" = a gap identified in Phase 2 with no current coverage; a small new script is proposed, to be placed under `testing_and_evaluation/` (never inside `tests/`, so the existing suite is never touched) and approved before being written in Phase 3/4.

Acceptance criteria below are **engineering targets I am setting now, before execution**, not externally-mandated requirements (none were supplied) — labeled as such per the master prompt's instruction not to present invented thresholds as approved requirements.

## Group 1 — Existing automated suite (run as-is, no new code)

| Test ID | Category | Component | File | Objective | Importance | Expected result |
|---|---|---|---|---|---|---|
| T-U01 | Unit | Evaluator formula | `tests/unit/test_evaluator.py` | Verify `0.15·S1+0.35·S2_eff+0.50·R`, mandatory cap, mistake penalty, keyword-stuffing defense, 10 adversarial score-ordering invariants | ESSENTIAL | All assertions pass |
| T-U02 | Unit | Evaluator fault handling | `tests/unit/test_evaluator_outage_and_sandbox_cleanup.py` | Evaluator unavailable → graceful fallback, sandbox cleanup on failure | ESSENTIAL | No unhandled exception; session continues |
| T-U03 | Unit | Orchestrator | `tests/unit/test_orchestrator.py` | Session state transitions, lock behavior | ESSENTIAL | All assertions pass |
| T-U04 | Unit | Persistence | `tests/unit/test_persistence_and_history.py` | Turn/session records written and retrievable correctly | ESSENTIAL | All assertions pass |
| T-U05 | Unit | Best-answer tracking | `tests/unit/test_best_answer_authority.py` | Correct best-answer selection logic | RECOMMENDED | All assertions pass |
| T-U06 | Unit | Coding executor | `tests/unit/test_coding_executor.py` | Sandbox exec, pass/fail/timeout handling | ESSENTIAL | All assertions pass |
| T-U07 | Unit | RL environment | `tests/unit/test_rl_env.py` | Gym env observation/action contracts | ESSENTIAL | All assertions pass |
| T-U08 | Unit | PPO/guardrail interaction (frozen Paper-3 artifacts) | `tests/unit/test_paper3_blockers.py` | Regression-guards the frozen Paper-3 findings | ESSENTIAL | All assertions pass; any failure = possible silent drift in frozen behavior, investigate before anything else |
| T-U09 | Unit | Score validator | `tests/unit/test_score_validator.py` | `mandatory_cap`/`mistake_penalty`/`coding_failure_multiplier` rules | ESSENTIAL | All assertions pass |
| T-U10 | Unit | Timer | `tests/unit/test_timer_scoring.py` | `time_norm` computation | RECOMMENDED | All assertions pass |
| T-U11 | Unit | Speech pipeline | `tests/unit/test_speech_pipeline.py` | STT + prosody pipeline runs end-to-end | ESSENTIAL (functional only, not WER accuracy) | No crash; produces transcript + confidence/hesitation scalars |
| T-U12 | Unit | Qwen feedback | `tests/unit/test_qwen_followup_feedback.py`, `test_qwen_specific_feedback.py`, `test_real_qwen_inference.py` | Qwen-generated hint/follow-up/feedback correctness paths | RECOMMENDED | All assertions pass |
| T-U13 | Unit | Personalization | `tests/unit/test_personalization_questions.py`, `test_primary_question_budget.py` | Question selection respects persona/budget rules | RECOMMENDED | All assertions pass |
| T-U14 | Unit | Audio warmup | `tests/unit/test_backend_audio_warmup.py` | Backend audio model warmup doesn't block startup | RECOMMENDED | All assertions pass |
| T-U15 | Unit | Stage-11 progression suite | `test_stage11_3_followup_and_evaluation.py`, `test_stage11_4_coding_verification.py`, `test_stage11_5_coding_adaptation.py`, `test_stage11_6_full_interview_e2e.py` | Layered functional→integration→e2e progression | ESSENTIAL | All pass **except the one documented known failure** (`test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`, obs[4] 0.0 vs expected 0.22 — unresolved per `CLAUDE.md`, not to be "fixed" without a decision) |
| T-I01 | Integration | 15-question demo + contextual follow-up | `tests/integration/test_15q_demo_and_contextual_followup.py` | Full 15-question session with follow-up injection | ESSENTIAL | Session completes, follow-up logic fires correctly |
| T-I02 | Integration | Personalization trajectories | `tests/integration/test_e2e_personalization_trajectories.py` | Different candidate profiles produce different trajectories | ESSENTIAL | Trajectories differ meaningfully by profile |
| T-I03 | Integration | Full lifecycle | `tests/integration/test_full_interview_lifecycle.py` | Start→finish session lifecycle | ESSENTIAL | Session completes with valid report |
| T-I04 | Integration | Multi-agent responsibility/failures | `tests/integration/test_multiagent_responsibility_and_failures.py` | Each agent fails independently without cascading | ESSENTIAL | Directly supports the "graceful degradation" architecture claim |
| T-F01 | Frontend | UI tests | `apps/web/src/__tests__/*.test.jsx` (4 files) | Layout, question progress, best-answer authority, UI fixes | RECOMMENDED | All assertions pass (Vitest) |

**Precondition for all Group 1 items:** `pytest`/`pytest-asyncio` installed in `.venv` (currently blocked — see `Test_Strategy.md` "Known blocker"). Command: `EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest -q` (full suite, ~6 min per `CLAUDE.md`) or targeted: `EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest tests/unit/test_evaluator.py -q`.

## Group 2 — New, proposed (gaps with no existing coverage; not yet written, pending this matrix's approval)

| Test ID | Category | Component | Objective | Importance | Procedure | Acceptance criterion (engineering target, not a formal requirement) | Evidence to record |
|---|---|---|---|---|---|---|---|
| T-N01 | Smoke | Full stack startup | Confirm `launch.py` brings up backend, evaluator, Qwen, frontend, DB connects | **ESSENTIAL** | Run `python launch.py`, then `--no-qwen`, `--no-frontend`, `--backend-only` variants; observe startup logs | All 4 flag combinations start without unhandled exception within a reasonable startup window | Captured stdout/stderr logs in `testing_and_evaluation/logs/` |
| T-N02 | RL inference sanity | Frozen PPO checkpoint | Load `rl/checkpoints/seed_123/ppo_final.zip` + `vecnormalize.pkl`, run `.predict()` on ~10 constructed 6-D states spanning strong/weak/boundary candidates | **ESSENTIAL** | New read-only script under `testing_and_evaluation/rl_evaluation/`; no training, no modification of checkpoint | Output is always one of {0,1,2} (Discrete(3)); VecNormalize applied (confirm via comparing normalized vs raw obs); no exception | Script output log |
| T-N03 | Guardrail unit verification | `rl/guardrails.py` | Directly unit-test each G-rule's trigger condition against constructed states (not currently covered by a dedicated test file; only exercised indirectly via `test_paper3_blockers.py`) | **ESSENTIAL** | New read-only test script, constructed states per documented G-rule conditions | Each rule fires exactly on its documented boundary, confirmed against the rule definitions in code (not the capstone report's possibly-inaccurate description) | Script output log |
| T-N04 | API contract | Evaluator REST endpoint | Confirm request/response schema, status codes, timeout handling for `services/evaluator/app.py`'s HTTP interface | RECOMMENDED | Start evaluator service, send valid/invalid/malformed requests | Valid requests return expected schema; invalid requests return a clear error status, not a crash | Request/response log |
| T-N05 | API contract | Qwen REST endpoint | Same, for `services/qwen/app.py` | RECOMMENDED | Same pattern | Same | Request/response log |
| T-N06 | Negative | Evaluator with edge-case inputs | Empty transcript, extremely long transcript, non-English/garbled text | RECOMMENDED | Call `evaluate()` directly with constructed inputs | No crash; score stays in [0,1]; reasonable (not necessarily "correct") behavior | Script output log |
| T-N07 | Compatibility | Python version | `.venv` is 3.11.9; `CLAUDE.md` states project targets 3.12 | RECOMMENDED | Confirm via `python --version`; check whether any 3.12-only syntax/feature is used | Record as a fact, do not silently "fix" | Already captured in Phase-2 baseline record |
| T-N08 | Deployment | Docker build | `docker build` dry-run for each of the 5 Dockerfiles | OPTIONAL | `docker build -f Dockerfile.X .` for each | Builds succeed or documented failure reason | Build logs |
| T-N09 | Performance | Evaluator latency (new spot-check) | Re-measure evaluator call latency on a small new sample, report median/p90/p95, compare against Paper 1's frozen figures (median 404.6ms) as context, not a re-run of Paper 1 | RECOMMENDED | Timing harness around `evaluate()` calls | Report median/p90/p95 with n and hardware; do not claim equivalence to Paper 1's figures without controlling for hardware | Timing log + CSV |
| T-N10 | Retrieval spot-check | FAISS question selection | For a handful of (topic, target-difficulty) queries, confirm the returned question is topically and difficulty-appropriate | RECOMMENDED | Call `question_selector` directly with constructed queries | Qualitative pass/fail per query, documented | Script output log |

## Execution status (updated as tests run — see `Baseline_Record.md` for full detail)

| Test ID | Status | Result |
|---|---|---|
| T-N02 | **DONE** | PASS — real PPO checkpoint, 10/10 scenarios valid; surfaced a genuine behavioral observation (score=0.35 → Harder) |
| T-N03 | **DONE** | PASS — 11/11 guardrail boundary cases match documented behavior; empirically confirmed a real guardrail coverage gap for perf ∈ (0.30, 0.40) |
| T-F01 | **DONE** | PASS — 4/4 files, 28/28 Vitest tests |
| T-U01–T-U15, T-I01–T-I04 | **DONE (final)** | Full suite, final baseline: **264 passed, 19 failed, 15 skipped, 0 collection errors (93.3%)**. All 19 failures fully explained: 18 Docker-daemon-down, 1 pre-existing known failure. Zero unexplained defects. See `baseline_results/Full_Suite_Baseline_Results.md`. |
| T-N01 | **DONE** | Services start and respond correctly (health checks pass, real evaluator + question bank load), **but `launch.py` itself crashes with `UnicodeEncodeError`** on a cp1252 Windows console (unguarded `→` character). Genuine code defect, see `baseline_results/T-N01_smoke_test_finding.md`. Orphaned services left running, not force-killed (blocked by sandbox permissions) — flagged to user. |
| T-N02 | **DONE** | PASS — see `Baseline_Record.md` |
| T-N03 | **DONE** | PASS — surfaced a real guardrail coverage gap, see `Baseline_Record.md` |
| T-N04 | **DONE** | PASS, 7/7 checks — see `api_tests/T-N04_evaluator_api_contract.py` + `logs/T-N04_output.log`. Also found evaluator service is Flask, not FastAPI as the capstone report claims. |
| T-N05 | **Not run as a separate script** | Already adequately covered by existing, already-passing suite tests (`test_qwen_followup_feedback.py::test_followup_api_contract`, `::test_personalized_feedback_contract`) — writing a duplicate was judged low-value |
| T-N06 | **DONE** | PASS, 10/10 (after fixing a console-encoding false-positive in the test script itself) — see `ml_evaluation/T-N06_evaluator_negative_and_edge_cases.py` |
| T-N07 | **DONE** | Recorded in `Baseline_Record.md` (Python 3.11.9 vs documented 3.12; all other pins within range) |
| T-N08 | Not run | Deprioritized — low marginal value given Docker daemon is down anyway |
| T-N09 | **DONE** | Evaluator latency spot-check: median 896ms, p95 986ms (warm, n=30) on this host — notably higher than Paper 1's frozen median (404.6ms); reported as a new, separate measurement, not a reproduction. See `performance_tests/T-N09_latency_spotcheck.py` |
| T-N10 | **DONE** | PASS — also corrected the capstone report's claim that question selection uses FAISS retrieval; it's actually rule-based (nearest-difficulty + topic-rotation). See `ml_evaluation/T-N10_question_selector_correctness.py` |

## Requirements covered by this matrix

See `Requirements_to_Test_Traceability_Matrix.md` for the mapping from each item above back to the capstone report's stated objectives and this session's architecture findings.
