# X1-D Protocol v1 - Test-suite report and latency for SUT build A (2026-09-19)

**Status: FINAL for tagging (`prereg/X1-D/v1`); SUT tag `sut/X1/build-A`.** Scope: **only X1-D**. X1-A (fault injection), X1-B (Qwen authority isolation) and X1-C (security oracle campaign) are **not** covered, not tagged and not run (see `research/audit/SPRINT_DECISIONS_AND_BLOCKERS.md`, section X1). Normative parameters: `research/confirmatory/X1-D/x1d_config.json`. Independent methodology review (ChatGPT) has not been performed.

## 1. Question
What is the state of the SUT's automated test suite at a fixed commit, and what are the warm-evaluator and single-writer SQLite latencies, with the cold-start cost reported separately? This replaces the withdrawn Paper 1 statements "213 tests passed, 0 failed", "warm evaluator 1960.8 ms mean" and the unsupported latency texts.

## 2. SUT and environment
SUT = the git commit pointed to by tag `sut/X1/build-A` (this protocol's commit; no file of `apps/`, `services/`, `agents/`, `rl/` or `tests/` differs from the previous commit). The environment is the SUT's own project `.venv` (unlocked; numpy 2.5.2 / torch 2.11.0 pin conflicts recorded; versions written to the run manifest); no lock is claimed. Outputs go only to `research/confirmatory/X1-D/results/`.

## 3. Design
**Test report.** One run of `python -m pytest -q -p no:cacheprovider --junitxml=... --tb=short` with `EVALUATOR_MOCK_MODE=1`, **without** `-x`, on the whole suite. The known failing test (`tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`) is disclosed in advance; failures are findings and are **not fixed** (defect policy: a fix would need a new build tag and a complete rerun). The JUnit XML, the console output and a summary (counts, failed test IDs) are stored. Running the suite may create runtime files (databases, logs) in untracked locations; a frozen-artifact hash check is run afterwards and reported.
**Latency.** In-process, real (non-mock) evaluator: asset load timed once; first request timed once (cold); then 100 warm requests, request i using stored benchmark triple i mod 64 (latency only; scores unused). SQLite: 100 sequential `save_attempt` writes on a fresh temporary database, uncontended (the concurrency workload is not re-measured here). Raw per-request values are stored; median, P95, P99 with iid bootstrap 95 % percentile intervals (B = 10 000, seed 42). With N = 100 the P99 is set by the two largest samples and is reported with that caveat. No SLA is defined and no result is labelled pass/fail.

## 4. Hypotheses / endpoints
None confirmatory. Descriptive endpoints: counts of passed/failed/errored/skipped tests and the failed IDs; the latency statistics above.

## 5. Stopping, reruns, interpretation
Single run; the runner refuses to start if `results/` exists; an interruption or crash is logged in a deviations file and the attempt retained. Only the stored, dated report and raw latency lists may be cited. Latency scope: one machine, one process, stored benchmark answers, uncontended DB writes; it is not a concurrency or deployment claim. The frozen study's numbers (mean 1960.8 ms; P95 21.0 ms SQLite write) are not re-derived here.

## 6. Disclosures
The authors built the SUT and the harness. The suite includes tests that mock failures; a passing suite is not fault-injection evidence (X1-A). The test result is specific to the tagged commit and the recorded, unlocked environment.
