# X1 Protocol Draft — Paper 1 systems evaluation (2026-09-19)

**Status: DRAFT. Not registered, not hashed, not tagged, not executed.** Fields marked **[FIX IN PHASE 2]** must be completed and reviewed before the protocol is hashed and tagged (`PREREGISTRATION_SPEC.md`). No X1 run may start without that tag. This draft changes no code and implements nothing (in particular, **no `FeedbackValidator`**).

Locked decisions (`PHASE0_DECISION_LOCK.md`): "secure" removed from title/framing (failure-aware / sandboxed); X1-A/B/C/D prepared; **positive/mutation controls mandatory**; "fault-tolerant" conditional on X1-A; defect policy §2.

## 0. Central question
Which failure-handling, isolation and containment properties of the multi-agent interview-assessment system hold under injected faults and adversarial programs, measured with oracles that are demonstrated to be able to fail?

## 1. System under test (SUT) and freezing
- SUT = a specific git commit/tag of the project (the "build"). Tag name **[FIX IN PHASE 2]**, e.g., `sut/X1/build-A`. No change to `apps/backend`, `services/`, `agents/`, `rl/` between protocol tag and campaign completion, except under §2.
- Harness = new code in a new directory (never in the frozen `research/scripts/`). The frozen `execute_paper1_study.py` is **not** re-run: it would reprint the literal PASS strings (registry `P1-C004/C005`).
- Environment: locked (`ENVIRONMENT_LOCK_SPEC.md`), manifest per run (`RUN_MANIFEST_SPEC.md`).
- **PASS/FAIL is computed by the harness from asserted observable fields and stored logs; it is never a typed or hard-coded string** (the defect of the frozen script). A result row without the logged observables that produced it is invalid. (Added in the Phase-0 closeout audit as a mechanical restatement of the approved "computed PASS/FAIL" requirement; see `PHASE0_CLOSEOUT_AUDIT.md`.)

## 2. Defect policy (approved)
1. Every defect (a scenario or attack that fails its pre-specified criterion, or a harness/SUT crash) is **reported as found**, with logs.
2. Fixes are made **only under a new tag** (`sut/X1/build-B`), never on build A.
3. The **complete relevant campaign** (all scenarios of the affected experiment, not just the failed scenario) is rerun on build B.
4. **Both builds and both result sets are retained and reported.** Criteria, observables and harness may not be edited between A and B (a harness bug is itself a defect handled under this policy, with a version bump and full rerun).
5. Whether a defect is fixed at all is decided with the user; a fix that changes scoring, difficulty or guardrail semantics needs separate approval (`CLAUDE.md`).

## 3. Mandatory positive (mutation) controls
For every oracle there is a paired control that **must** be detected as FAIL:
- **Fault scenarios:** a mutant build/config in which the relevant handler is disabled or bypassed (e.g., fallback removed, timeout removed, infrastructure-failure flag ignored). The harness must report FAIL on the mutant; if it reports PASS, the oracle is invalid and the scenario is not usable.
- **Security attacks:** a deliberately permissive container configuration (e.g., network enabled to a **local** canary listener, writable canary directory outside the container mount, raised limits) under which the same oracle must observe the breach/exhaustion.
- **Qwen isolation:** a mutant in which an LLM-output field is (artificially) wired into the score/difficulty path in a test harness copy; the bit-identity test must fail.
- Controls run only in an isolated local environment with local canaries; never against real networks/hosts.

## 4. X1-A — Fault-injection core
**Question.** Does the SUT handle each enumerated dependency failure without losing state, fabricating a score, or hanging?
**Hypothesis (per scenario).** The pre-specified observable criteria are met; the mutant fails the same criteria.
**Scenario derivation [FIX IN PHASE 2].** Enumerate every external dependency of the request path from the architecture (Qwen service, evaluator service, Docker daemon/compiler, SQLite, WebSocket transport, speech/feature extraction, filesystem) × failure mode {unavailable, slow beyond timeout, malformed/invalid output}. The enumeration table (with the code reference for each dependency) is part of the frozen protocol, so the scenario list is derived, not chosen after seeing behaviour. Candidate scenarios carried from the earlier plan (final list comes from the enumeration):

| Candidate | Injection | Observable | Pass criterion (draft) |
|---|---|---|---|
| FLT-01 Qwen down | block/stop Qwen | response status, feedback source flag, latency | returns within SLA; evaluator score and concepts identical to no-fault run; source flag = unavailable |
| FLT-02 Qwen slow | stub sleeping past timeout | latency, flag | returns by timeout + margin on the fallback path; score unchanged |
| FLT-03 Evaluator 503 | stub returns 503 | infrastructure-failure flag, score field | flag true; **no 0.0 recorded as candidate failure**; retry offered |
| FLT-04 Invalid score | stub returns NaN / Inf / out-of-range | stored value | never stored raw; handled per `ScoreValidator` |
| FLT-05 Docker daemon down | unreachable Docker host | executor status | structured error; no hang; no false "accepted" |
| FLT-06 Compiler hang | toolchain outlives timeout | status, wall time | terminated at timeout; no orphan process/container |
| FLT-07 DB write-lock contention | second connection holds write lock (shorter/longer than busy timeout) | operation outcome, row counts | short: succeeds; long: fails cleanly and visibly; acknowledged writes == stored rows |
| FLT-08 WebSocket reset | close socket mid-evaluation | server log, DB state | no crash; attempt fully recorded or absent, never partial |
| FLT-09 Feature-extractor crash | force exception | response | neutral fallback **flagged as fallback**; technical score unaffected |
| FLT-10 Empty input | empty transcript / code | status | structured "no input" outcome; no exception |

Exact API field names (e.g., `is_infrastructure_failure`, `llm_unavailable`, `sandbox_error`) are those found in code/tests in the P0-6 audit and are to be confirmed against the SUT commit **[FIX IN PHASE 2]**.
**Independent variables.** scenario; injection timing (randomised for timing-sensitive scenarios); build (SUT; mutant). **Dependent variables.** status/flags, latency vs pre-specified SLA, score bytes, DB state hash and row counts, recovery on the next request. **Controls.** a no-fault run per scenario; a mutant per scenario (§3).
**Unit of analysis.** the scenario (an enumerated fault class), **not** the trial.
**Repetitions.** deterministic scenarios: 5–10 repetitions (flakiness check), reported as counts; timing-sensitive scenarios (lock contention, mid-request reset, slow-Qwen timeout): N ≈ 30 randomised injection points with a Wilson 95 % interval, which is meaningful because it samples the timing space. No pooling into a single "x/y"; no CI on deterministic repetition.
**Seeds.** order-shuffle and timing-jitter seeds logged in the manifest.
**Stopping rule.** fixed scenario list and repetition counts; harness failure is a reported outcome; no silent retry; a defect triggers §2.
**Interpretation.** *Positive:* "for the enumerated fault classes on build X, criteria were met, and the mutant controls fail". Only then may "fault-tolerant" appear in the title, scoped to enumerated classes. *Mixed/null:* failed scenarios are named; the property is dropped or narrowed; title uses "failure-aware". *Negative:* a failed scenario is a finding, not a harness error, unless the mutant control also passes (oracle invalid).
**Contamination controls.** criteria and observables hashed before running; harness dry-run on non-confirmatory fixtures only; no frozen PASS string reused; SUT tag fixed.
**Artifacts.** harness code + config, dependency-enumeration table, scenario table, manifests, per-trial logs, DB dumps with hashes, process/container listings before/after, JUnit XML, results CSV.

## 5. X1-B — Qwen authority isolation (structural + differential)
**Question.** Can LLM output alter score, difficulty or attempt ranking?
**Hypothesis.** No path exists; evaluator score bytes, orchestrator difficulty state and `is_best` rows are identical with vs without adversarial prompts.
**Design.** (i) **Static check:** an AST/grep test asserting that no code path from the LLM client writes score, difficulty or `is_best` (reported with the exact patterns). (ii) **Differential test:** ≥ 30 adversarial prompts written and hashed in advance, each paired with a benign control, run against the real Qwen service with fixed decoding settings (temperature/seed recorded). (iii) **Mutation control:** a harness-copy mutant that wires an LLM field into the score path; the test must fail.
**Explicitly excluded:** QWN-04 "validator" tests. No `FeedbackValidator` exists and none will be added; the paper states that feedback is unvalidated. (A validator, if ever wanted, is a separately approved and separately tagged change.)
**Unit.** the prompt (paired). **Test.** exact equality per pair; count of identical pairs (Wilson interval only if the LLM path is stochastic, and then labelled as such). **Stopping.** fixed prompt list. **Interpretation.** any difference is a defect (§2). A clean result supports "no LLM path to score/difficulty/ranking in the tested build", not a general isolation guarantee.
**Artifacts.** prompt file + hash, static-check output, logs, diffs.

## 6. X1-C — Security oracle campaign (five-way separation)
**Question.** For each attack program: did the payload execute, was the effect contained, and did the host remain unchanged?
**Five quantities per attack.** (1) attack execution (the program reports the syscall/library return and `errno`); (2) containment (the control blocks the effect: `connect` fails, `fopen` returns `EROFS`, `fork` fails with `EAGAIN`, allocation triggers an OOM kill); (3) status response of the executor (recorded, **not** itself a pass criterion); (4) host impact (canary file hash outside the container unchanged; host listener receives nothing; no new host processes or mounts); (5) resource impact (peak memory/CPU/PIDs versus limits).
**Attacks.** the nine existing (SEC-01…09), with programs modified so they are discriminating (design table in `P0_P1_DECISION_PLAN.md` §8.4), plus any additions listed in the frozen protocol.
**Design.** shipped configuration vs permissive-control configuration (§3) × attack; 5 repetitions each; oracles frozen before running.
**Unit.** the attack. **Test.** per-attack outcome table; no pooled percentage. **Success.** shipped configuration meets containment and host-unchanged criteria **and** the permissive control breaches on the same oracle. **Stopping.** fixed list. **Interpretation.** wording limited to "contained in this harness" for the tested attack classes; **no "secure"**.
**Artifacts.** attack programs, oracle code, canary hashes, resource counters, logs.

## 7. X1-D — Test report and latency
**Question.** What is the state of the test suite, and what is the cold vs warm latency distribution?
**Design.** run the test suite once with `--junitxml` on the SUT tag, disclose the known failing test (`tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`), store the report with commit and environment. Latency: N ≥ 100 warm requests plus cold-start samples recorded separately, raw per-request values stored; median/P95/P99 with bootstrap CIs.
**Interpretation.** only the stored, dated report is cited. **Artifacts.** JUnit XML, raw latency list, manifest.

## 8. Reporting rules for Paper 1 (fixed now)
Claims are limited to what the registered results support: scenario-level results for enumerated classes; concurrency/latency with stated scope (one machine; the concurrency test excludes the evaluator and LLM); threat-model table labelled as a design mapping; no measured claim for properties not covered by X1.

## 9. Open items **[FIX IN PHASE 2]**
Dependency-enumeration table; SLA/timeout values (taken from the design/config, not chosen from results); exact field names; SUT tag; harness location; mutant definitions; canary setup; adversarial prompt set; repetition counts per scenario; who reviews the protocol before tagging.
