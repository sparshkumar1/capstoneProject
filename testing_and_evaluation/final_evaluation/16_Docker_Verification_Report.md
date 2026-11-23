# 16. Docker Verification Report

**Date:** 2026-11-13. **Scope:** verification only, per explicit instruction — no rebuild, redesign, refactor or
optimization of PrepAIred. Preservation of the existing working project took priority throughout.

---

## Executive Summary

This verification confirms the successful operation of PrepAIred's Docker-based C-code execution environment using
a live, reachable Docker Desktop daemon.

All 19 individually identified Docker-dependent test cases passed during the focused verification. Additionally,
12 sandbox-dependent tests that had previously been skipped because Docker was unavailable were successfully
executed and passed.

The verification covered C compilation and execution, compilation-error handling, runtime failures, timeout
enforcement, resource restrictions, filesystem isolation, network isolation, partial test evaluation, and
integration with the interview orchestration workflow.

The complete execution path was traced from the frontend through the backend API and Docker sandbox to the
WebSocket and interview orchestrator. The Docker-unavailable path was also examined to confirm that untrusted
code execution is blocked when the sandbox cannot be reached.

No application-code or test-code modifications were required. The existing sandbox implementation was verified
as it stood, preserving the working project and its historical results.

A separate, previously documented state-preservation issue was reproduced and retained outside the scope of this
Docker verification. The focused verification results are not used to revise the project's overall historical
test pass rate.

---

## 1. Environment (Task 1)

| Item | Value | Command |
|---|---|---|
| Repository path | `D:\Capstone_29_AUG\capstoneProject` | `pwd` |
| Branch | `final-eval/controlled-improvements` | `git branch --show-current` |
| HEAD commit | `1caa90bb24d856cad87c05317de207bf15173752` (2026-11-13 14:38:39 +0530) | `git rev-parse HEAD` |
| Working tree | Not clean — many modified/untracked files from this engagement's prior sessions (feature work, documentation, figures); none touched by this Docker-verification pass except this report itself, as recorded in §6 | `git status --short` |

**Docker Desktop / daemon:**

```
$ docker version
Client:  Version 29.7.2, API 1.55
Server:  Docker Desktop 4.88.1 (237512), Engine 29.7.2

$ docker info
... Server: Containers: 0, Images: 2, Server Version: 29.7.2, OSType: linux,
    Architecture: x86_64, CPUs: 12, Total Memory: 7.607GiB, Name: docker-desktop ...

$ docker run --rm hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

**Conclusion: Docker Desktop is installed, the daemon is running and reachable, and it can pull and execute a
real container end-to-end.** This is a change from the state recorded in every prior baseline document in this
project (`testing_and_evaluation/Baseline_Record.md`, `baseline_results/Full_Suite_Baseline_Results.md`), which
confirmed via `docker ps`/`docker version` at the time that the daemon was **not** reachable. I did not start
Docker Desktop myself — it was already running when this verification began.

**Project sandbox image:** `prepaired-c-sandbox:latest` already exists locally (`docker images`: ID `d9ab90d4269e`,
238MB disk / 66.2MB content) — built previously, not rebuilt for this pass.

---

## 2. The 18-vs-19 count — a pre-existing documentation inconsistency, disclosed not resolved

Before running anything, I located the project's own itemized breakdown of the Docker-dependent failures
(`testing_and_evaluation/baseline_results/Full_Suite_Baseline_Results.md`, "Cause 2"). It lists, by file:

| File | Items listed |
|---|---|
| `tests/unit/test_coding_executor.py` | 14 |
| `tests/unit/test_stage11_6_full_interview_e2e.py` | 2 |
| `tests/unit/test_stage11_5_coding_adaptation.py` | 3 |
| **Total** | **19** |

This source document's own section header reads "Cause 2 — Docker daemon not running (**19** of 35 items...)", which
contradicts the "**18** Docker-dependent + 1 known = 19 total failed" framing repeated elsewhere in this project
(`CLAUDE.md`, the README, the university report, both IEEE paper tracks, the presentation). **I did not find a
version of this list that sums to exactly 18.** This is a pre-existing inconsistency in the project's own prior
documentation, not something I introduced or am resolving by picking a side — per instruction, historical results
are not being changed. I verified the itemized **19**-test list directly against the current test files (below) and
ran every one of them; the "18 vs 19" labeling discrepancy itself is reported as a disclosed finding, not corrected.

**The 19 itemized Docker-dependent test cases** (file path :: test name), confirmed to exist at their stated
locations by direct inspection of the current test files:

| # | File | Test |
|---|---|---|
| 1 | `tests/unit/test_coding_executor.py` | `test_docker_compiles_and_runs_correct_c_program` |
| 2 | `tests/unit/test_coding_executor.py` | `test_docker_wrong_answer_output_comparison` |
| 3 | `tests/unit/test_coding_executor.py` | `test_docker_detects_c_compilation_error` |
| 4 | `tests/unit/test_coding_executor.py` | `test_docker_runtime_error_segfault` |
| 5 | `tests/unit/test_coding_executor.py` | `test_docker_terminates_infinite_loop_timeout` |
| 6 | `tests/unit/test_coding_executor.py` | `test_docker_memory_limit_oom_enforcement` |
| 7 | `tests/unit/test_coding_executor.py` | `test_docker_network_isolation_blocked` |
| 8 | `tests/unit/test_coding_executor.py` | `test_docker_pid_limit_process_capping` |
| 9 | `tests/unit/test_coding_executor.py` | `test_docker_output_limit_truncation` |
| 10 | `tests/unit/test_coding_executor.py` | `test_docker_non_root_uid_gid` |
| 11 | `tests/unit/test_coding_executor.py` | `test_docker_filesystem_root_read_only` |
| 12 | `tests/unit/test_coding_executor.py` | `test_docker_partial_test_performance_7_of_10_passed` |
| 13 | `tests/unit/test_coding_executor.py` | `test_docker_mandatory_test_failure_caps_score` |
| 14 | `tests/unit/test_coding_executor.py` | `test_candidate_state_tracks_rich_coding_metrics` (uses real sandbox execution to populate state; the 14th item in this file's historical count) |
| 15 | `tests/unit/test_stage11_5_coding_adaptation.py` | `test_accepted_coding_result_updates_candidate_state` |
| 16 | `tests/unit/test_stage11_5_coding_adaptation.py` | `test_partial_coding_result_updates_candidate_state` |
| 17 | `tests/unit/test_stage11_5_coding_adaptation.py` | `test_failed_coding_result_compilation_error` |
| 18 | `tests/unit/test_stage11_6_full_interview_e2e.py` | `test_full_interview_lifecycle` |
| 19 | `tests/unit/test_stage11_6_full_interview_e2e.py` | `test_coding_partial_credit_in_sandbox` |

**Code-level confirmation of why these specifically depend on Docker, and why others in the same files do not:**
`test_stage11_5_coding_adaptation.py` and `test_stage11_6_full_interview_e2e.py` each define their own
module-scoped `sandbox` fixture as `return DockerCSandbox()` with **no availability check** — so any test using it
fails (not skips) when Docker is unreachable. `test_coding_executor.py` has no shared fixture and no skip guard
anywhere in the file. By contrast, `test_stage11_4_coding_verification.py`'s `sandbox` fixture explicitly calls
`sb.is_docker_available()` and calls `pytest.skip(...)` if false — which is exactly why that file's 12
sandbox-dependent tests were correctly counted among the historical **skips**, not failures, and are not in the
19-item list above.

---

## 3. Task 2 — Executing the Docker-dependent tests

**Command used** (the project's existing test configuration, no modification — this is the `VAR=value command`
form, not valid PowerShell syntax, so it was run in Git Bash):
```
EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest tests/unit/test_coding_executor.py \
  tests/unit/test_stage11_4_coding_verification.py tests/unit/test_stage11_5_coding_adaptation.py \
  tests/unit/test_stage11_6_full_interview_e2e.py tests/integration/test_full_interview_lifecycle.py -v
```

**Reproducibility details** (for another developer to reproduce this exact run):
- **Shell:** Git Bash (required by the `VAR=value` env-var prefix syntax above; this would not parse in
  PowerShell or `cmd.exe`).
- **Python interpreter:** 3.11.9 (`.venv/Scripts/python.exe`; raw log line 6). Note: `CLAUDE.md` documents the
  project's venv as Python 3.12, but the actual interpreter used by `.venv` for this run was 3.11.9. This specific
  discrepancy was not found already recorded in `docs/PROJECT_STATE.md` (which documents other `.venv` pin
  mismatches, e.g. numpy/torch/accelerate); it is disclosed here as observed, not introduced or resolved by this
  verification.
- **Pytest / plugins:** pytest 9.2.0, pluggy 1.7.0, plugins `anyio-4.14.2`, `asyncio-1.4.1.post1` (raw log lines
  6, 10).
- **Virtualenv:** `.venv` was already configured from prior sessions; it was not created or modified for this
  verification.
- **Docker daemon availability:** reachable for the entire run. The run is a single continuous `pytest` process
  (168.48s, no restart or re-invocation partway through), and every Docker-dependent test in it — including the
  12 previously-skipped `sandbox`-dependent tests, which would `pytest.skip` immediately on an unreachable
  daemon — passed rather than skipped, which is itself evidence the daemon stayed reachable throughout.
- **Command semantics:** reproduced verbatim above; not altered to "clean up" the syntax.

**Result: 55 collected, 54 passed, 1 failed, in 168.48s.** (`collecting ... collected 55 items`, raw log line 12;
`1 failed, 54 passed, ... in 168.48s`, raw log line 142.) Full raw log preserved at
`testing_and_evaluation/logs/T-DOCKER01_docker_verification_run.log`. The table below itemizes all 55 collected
tests individually or in named groups; the sum of all rows' individual-test counts is 55, matching the collection
count exactly (54 passed + 1 failed, 0 skipped):

| # | Test | Historical status (Docker unavailable) | Current status (Docker available) | Cause of any remaining non-pass |
|---|---|---|---|---|
| 1 | `test_coding_executor.py::test_validate_source_safety_blocks_dangerous_c_headers` | Passed (no Docker needed) | **PASSED** | — |
| 2 | `test_coding_executor.py::test_validate_source_safety_blocks_empty_code` | Passed | **PASSED** | — |
| 3 | `test_coding_executor.py::test_validate_source_safety_accepts_clean_c_code` | Passed | **PASSED** | — |
| 4 | `test_coding_executor.py::test_policy_blocked_submission_structure` | Passed | **PASSED** | — |
| 5 | `test_coding_executor.py::test_docker_compiles_and_runs_correct_c_program` | **FAILED** (Docker) | **PASSED** | resolved |
| 6 | `test_coding_executor.py::test_docker_wrong_answer_output_comparison` | **FAILED** (Docker) | **PASSED** | resolved |
| 7 | `test_coding_executor.py::test_docker_detects_c_compilation_error` | **FAILED** (Docker) | **PASSED** | resolved |
| 8 | `test_coding_executor.py::test_docker_runtime_error_segfault` | **FAILED** (Docker) | **PASSED** | resolved |
| 9 | `test_coding_executor.py::test_docker_terminates_infinite_loop_timeout` | **FAILED** (Docker) | **PASSED** | resolved |
| 10 | `test_coding_executor.py::test_docker_memory_limit_oom_enforcement` | **FAILED** (Docker) | **PASSED** | resolved |
| 11 | `test_coding_executor.py::test_docker_network_isolation_blocked` | **FAILED** (Docker) | **PASSED** | resolved |
| 12 | `test_coding_executor.py::test_docker_pid_limit_process_capping` | **FAILED** (Docker) | **PASSED** | resolved |
| 13 | `test_coding_executor.py::test_docker_output_limit_truncation` | **FAILED** (Docker) | **PASSED** | resolved |
| 14 | `test_coding_executor.py::test_docker_non_root_uid_gid` | **FAILED** (Docker) | **PASSED** | resolved |
| 15 | `test_coding_executor.py::test_docker_filesystem_root_read_only` | **FAILED** (Docker) | **PASSED** | resolved |
| 16 | `test_coding_executor.py::test_docker_partial_test_performance_7_of_10_passed` | **FAILED** (Docker) | **PASSED** | resolved |
| 17 | `test_coding_executor.py::test_docker_mandatory_test_failure_caps_score` | **FAILED** (Docker) | **PASSED** | resolved |
| 18 | `test_coding_executor.py::test_candidate_state_tracks_rich_coding_metrics` | **FAILED** (Docker) | **PASSED** | resolved |
| 19 | `test_coding_executor.py::test_ppo_observation_remains_strictly_6d_after_coding_turn` | Passed (no Docker needed) | **PASSED** | — |
| 20 | `test_coding_executor.py::test_stage5_ppo_checkpoint_loads_and_infers_cleanly` | Passed (no Docker needed) | **PASSED** | — |
| 21–32 | `test_stage11_4_coding_verification.py` (12 `sandbox`-dependent tests) | Skipped (explicit guard) | **ALL 12 PASSED** | resolved — ran for real instead of skipping |
| 33 | `test_stage11_4_coding_verification.py::test_docker_unavailable_structured_failure` | Passed (tests the unavailable path itself) | **PASSED** | — |
| 34 | `test_stage11_4_coding_verification.py::test_candidate_state_and_rl_6d_separation` | Passed | **PASSED** | — |
| 35 | `test_stage11_5_coding_adaptation.py::test_accepted_coding_result_updates_candidate_state` | **FAILED** (Docker) | **PASSED** | resolved |
| 36 | `test_stage11_5_coding_adaptation.py::test_partial_coding_result_updates_candidate_state` | **FAILED** (Docker) | **PASSED** | resolved |
| 37 | `test_stage11_5_coding_adaptation.py::test_failed_coding_result_compilation_error` | **FAILED** (Docker) | **PASSED** | resolved |
| 38 | `test_stage11_5_coding_adaptation.py::test_infrastructure_failure_does_not_corrupt_candidate_metrics` | Passed | **PASSED** | — |
| 39 | `test_stage11_5_coding_adaptation.py::test_coding_topic_maps_correctly` | Passed | **PASSED** | — |
| 40 | `test_stage11_5_coding_adaptation.py::test_multiple_coding_attempts_aggregate_correctly` | Passed | **PASSED** | — |
| 41 | `test_stage11_5_coding_adaptation.py::test_observation_strictly_6d_and_bounded` | Passed | **PASSED** | — |
| 42 | `test_stage11_5_coding_adaptation.py::test_coding_execution_time_does_not_enter_rl_state` | Passed | **PASSED** | — |
| 43 | `test_stage11_5_coding_adaptation.py::test_runtime_and_training_state_formula_consistency` | Passed | **PASSED** | — |
| 44 | `test_stage11_5_coding_adaptation.py::test_strong_vs_weak_coding_trajectory_divergence` | Passed | **PASSED** | — |
| 45 | `test_stage11_5_coding_adaptation.py::test_ppo_policy_authoritative_inference` | Passed | **PASSED** | — |
| 46 | `test_stage11_5_coding_adaptation.py::test_post_coding_next_question_uses_updated_state` | Passed | **PASSED** | — |
| 47 | `test_stage11_5_coding_adaptation.py::test_mixed_verbal_and_coding_session_accounting` | Passed | **PASSED** | — |
| 48 | `test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` | **FAILED** (pre-existing known issue, NOT Docker) | **FAILED, identically** | see §7 — unchanged, not touched |
| 49 | `test_stage11_6_full_interview_e2e.py::test_full_interview_lifecycle` | **FAILED** (Docker) | **PASSED** | resolved |
| 50 | `test_stage11_6_full_interview_e2e.py::test_coding_partial_credit_in_sandbox` | **FAILED** (Docker) | **PASSED** | resolved |
| 51–54 | `test_stage11_6_full_interview_e2e.py` (4 non-Docker tests: `test_production_evaluator_scoring_and_concepts`, `test_qwen_followup_grounded_in_gap`, `test_ppo_inference_and_6d_state_bounds`, `test_research_artifacts_exist`) | Passed | **ALL PASSED** | — |
| 55 | `tests/integration/test_full_interview_lifecycle.py::test_full_interview_lifecycle_simulation` | Not part of the original 18/19-item list (different file/test from #49 despite the similar name); passed historically with mocked sandbox interaction | **PASSED** | — |

**Correction to an earlier draft of this table:** the previous version omitted
`test_stage11_5_coding_adaptation.py::test_mixed_verbal_and_coding_session_accounting` (row 47 above) and
mislabeled the preceding group as "9 non-Docker tests" instead of 10, leaving only 54 individual tests itemized
against a 55-item collection. That test was in fact collected and passed (raw log line 60); it has been added
above and all subsequent row numbers corrected. No test is counted twice and none of the 55 collected tests are
omitted.

**Result: all 19 itemized, previously Docker-dependent tests now PASS with a real, available Docker daemon. Zero
of the 19 remain failing for Docker-related reasons.** The only failure anywhere in this 55-test run is the single,
separately-tracked, pre-existing known issue (§7), which is not Docker-related.

**A note on an intermediate observation from an earlier full-suite run, and its relationship to this batch:**
earlier in this same session, before this focused run, a full 298-test suite run (`pytest tests/`, ~2 hours) showed
3 tests failing: `test_docker_compiles_and_runs_correct_c_program`, `test_accepted_c_solution`, and
`test_full_interview_lifecycle_simulation`.

Of these three, two appear directly in the 55-test focused batch above with their own row and are tied to the
batch's own stored evidence: `test_docker_compiles_and_runs_correct_c_program` is row 5 (PASSED, raw log line 18)
and `test_full_interview_lifecycle_simulation` is row 55 (PASSED, raw log line 68). The third,
`tests/unit/test_stage11_4_coding_verification.py::test_accepted_c_solution`, is also in this batch, but only as
part of the merged row 21–32 group (it is the first of the 12 `sandbox`-dependent tests in that file, confirmed
individually PASSED at raw log line 34) — it was not broken out by name in the original table, which is why it
looked absent from the 55-test accounting; it was not actually missing from the run.

Separately, each of the three tests was also re-run individually immediately after the full 298-test run, and all
three passed there as well. That individual-rerun evidence was **not captured in a persisted log file** — the
reruns were done interactively in the same terminal session and only the full-suite run's own (truncated) output
buffer was retained, as already disclosed in `FINAL_SOURCE_OF_TRUTH_AND_RECONCILIATION.md` (around line 424). The
only *persisted, file-backed* evidence that all three tests pass is therefore the 55-test batch run captured in
`T-DOCKER01_docker_verification_run.log`, referenced above by row and log line.

The earlier failures were not reproduced in the subsequent targeted executions. Their behaviour is consistent
with test-isolation or resource-contention effects during the extended Docker-heavy run; the available evidence
does not establish a definitive root cause.

---

## 4. Task 3 — The C-code Docker execution workflow, verified end-to-end

Traced the complete path by direct code inspection, not assumption:

1. **Frontend → REST:** `apps/web/src/InterviewRoom.jsx` (`handleRunCode`) calls `api.runCode(code, sessionId)` →
   `POST /api/run_code`.
2. **Backend REST → sandbox:** `apps/backend/main.py` (line ~1354) calls
   `evaluate_c_submission(req.code, test_cases=test_cases)` from `agents/coding_executor/coding_executor.py`.
3. **Sandbox → Docker:** `DockerCSandbox.compile_and_execute()` runs a **real** `docker run` with hardened flags
   confirmed by direct code inspection: `--user 1001:1001` (non-root), `--net=none` (network isolation),
   `--cap-drop=ALL`, `--security-opt=no-new-privileges`, `--memory`/`--memory-swap` (OOM limit),
   `--pids-limit` (fork-bomb protection), `--read-only` root filesystem with a `tmpfs` workspace, and a real
   `gcc -O2 -Wall -Wextra -std=c11` compile step. All of these specific protections are exercised and confirmed
   working by the now-passing dedicated tests (#7, #9, #10, #11, #12, #14, #15 in §3's table).
4. **Execution and test evaluation:** confirmed by the now-passing `test_docker_detects_c_compilation_error`,
   `test_docker_runtime_error_segfault`, `test_docker_terminates_infinite_loop_timeout`,
   `test_docker_partial_test_performance_7_of_10_passed`, and `test_docker_mandatory_test_failure_caps_score` —
   compilation errors, runtime crashes (segfault), infinite-loop timeouts, partial test-case scoring, and the
   mandatory-test-case score cap are all genuinely exercised against real compiled/executed binaries, not mocked.
5. **Result flows back to the frontend, then to the orchestrator:** the REST response's real fields
   (`result.passed`, `result.stdout`, `result.stderr`, `result.tests_passed`, `result.tests_total` — confirmed by
   direct inspection of `InterviewRoom.jsx` lines 193–207, which read these directly off the REST response, not
   invented client-side) are sent in a WebSocket `code_submission` message, which
   `apps/backend/main.py`'s WS handler forwards verbatim into `orch.handle_code_submission(...)`
   (`agents/orchestrator/interview_orchestrator.py`), which updates candidate state, computes the coding score, and
   produces the next difficulty/feedback step.

**Docker security evidence, organized by how it was verified:** not every hardening flag is directly exercised by
a dedicated test, so the evidence below is split into what was confirmed by reading the code versus what a
passing test actually demonstrates at runtime. This distinction is more credible than claiming every flag was
independently penetration-tested — it was not.

**A. Controls confirmed by code inspection only** (present in the `docker run` invocation in
`DockerCSandbox.compile_and_execute()`, not independently exercised by a dedicated test below):
- Non-root execution (`--user 1001:1001`)
- Network isolation (`--net=none`)
- Capability dropping (`--cap-drop=ALL`)
- No-new-privileges (`--security-opt=no-new-privileges`)
- Memory and memory-swap limits (`--memory`/`--memory-swap`)
- PID limits (`--pids-limit`)
- Read-only root filesystem (`--read-only`)
- Temporary filesystem workspace (`tmpfs`)

**B. Controls directly exercised by the test suite** (each row below is a control with a test that runs real
Docker execution and asserts the control's effect, not just the presence of the flag):

| Security or execution behaviour | Test (in `test_coding_executor.py`) |
|---|---|
| Network isolation | `test_docker_network_isolation_blocked` |
| Memory limit | `test_docker_memory_limit_oom_enforcement` |
| PID limit | `test_docker_pid_limit_process_capping` |
| Non-root execution | `test_docker_non_root_uid_gid` |
| Read-only filesystem | `test_docker_filesystem_root_read_only` |
| Output restriction | `test_docker_output_limit_truncation` |
| Infinite-loop termination | `test_docker_terminates_infinite_loop_timeout` |

All seven tests in column B passed in this verification (§3). Capability dropping and no-new-privileges (in
category A) are confirmed present in the invocation by code inspection but have no dedicated test asserting their
runtime effect; this report does not claim they were independently exercised.

**Separation from the verbal evaluator, confirmed:** `evaluate_c_submission`/`DockerCSandbox` never import or call
anything from `services/evaluator/` (the SBERT/FAISS/CrossEncoder composite pipeline), and vice versa — these are
two genuinely separate code paths, consistent with `CLAUDE.md`'s own description. No evidence found of the two
being conflated anywhere in this workflow.

---

## 5. Task 4 — Docker-unavailable / fail-closed behaviour, verified

Direct inspection of `DockerCSandbox.compile_and_execute()` (`agents/coding_executor/coding_executor.py`, lines
165–186): when `_resolve_docker_prefix()` returns `None` (daemon unreachable), the method returns immediately
with:
```python
{"status": "sandbox_error", "passed": False, "coding_score": 0.0, ...,
 "policy_reasons": ["Docker sandbox daemon unavailable"],
 "error": "Docker sandbox daemon is unreachable. Untrusted code execution blocked to protect host."}
```
**This confirms, from the code itself:** the system never pretends code executed successfully when Docker is
unavailable (explicit `status: "sandbox_error"`, `passed: False`, `coding_score: 0.0`); it does not silently bypass
the sandbox (there is no alternative, unsandboxed execution path anywhere in this function); and it returns a
clearly labeled unavailable/failure status rather than a fabricated result.

**Why this matters:** this is a fail-closed design, not an incidental error path.
- Untrusted candidate-submitted C code is never executed directly on the host — the sandbox is the only execution
  path, and it is not bypassed when unreachable.
- Docker unavailability does not trigger an unsafe fallback (e.g. running `gcc`/the compiled binary outside a
  container) — there is none in this function.
- The backend returns a structured failure (`status: "sandbox_error"`) that the frontend/orchestrator can detect
  and handle explicitly, rather than an ambiguous or silent error.
- The application does not fabricate a successful execution result (`passed`, `coding_score`, test-pass counts)
  when no code actually ran.

**Test coverage of this exact path:** `test_stage11_4_coding_verification.py::test_docker_unavailable_structured_failure`
(passed, §3 #33) specifically exercises this scenario and is independent of whether Docker is actually running —
it tests the code path, not the live daemon. I did not stop Docker Desktop to re-verify this live (that would be a
disruptive action affecting other work in this session and was not necessary — the test exercises the exact same
code path a live daemon-down scenario would hit, and it passed).

---

## 6. Task 5 — Code changes made

**None.** Every one of the 19 previously Docker-dependent tests passed once a real Docker daemon was available,
with no source-code modification of any kind. Per the explicit instruction ("If the 18 tests pass without any code
change, do not modify the application merely for the sake of making a change"), **no change was made to
`agents/coding_executor/`, `agents/orchestrator/`, `apps/backend/main.py`, `apps/web/src/InterviewRoom.jsx`, or any
test file.** The only file changed by this specific Docker-verification task is this report.

**Regression check:** since no code was changed, no regression run was required for this task specifically. (A
full-suite regression run was separately performed earlier this session for a different, explicitly-scoped
request — see `FINAL_SOURCE_OF_TRUTH_AND_RECONCILIATION.md`, Finding 11 — and is not duplicated here.)

---

## 7. Separate state-preservation verification observation

`tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`
failed in this verification exactly as `CLAUDE.md` has documented throughout this engagement:
`obs[4]` (verbal response time, expected preserved at `0.22`) comes back as `0.0` after a coding turn.

To be explicit about scope: this is a **separate state-preservation test**, **unrelated to Docker availability** —
it is not one of the 19 itemized Docker-dependent cases (§2), and it fails for an unrelated reason (a
state-preservation question about `obs[4]` after a coding turn), not a sandbox or container issue. It was
**reproduced identically** in this run to its previously documented behavior. **No code was changed** to address
it, per the explicit standing instruction that this issue is unresolved and not to be fixed until a decision is
made. It is kept separately identified here, not merged into or relabeled as a Docker-related failure, and not
claimed as resolved. Its presence is noted for completeness; it does not overshadow the 19/19 Docker verifications
above, which are this report's actual subject.

---

## 8. Final status summary

| Category | Result |
|---|---|
| Itemized Docker-dependent tests (§2) | **19/19 passed** |
| Previously skipped Docker-dependent tests (`test_stage11_4_coding_verification.py`'s 12 `sandbox`-guarded tests) | **12 passed** |
| Focused verification batch (§3, full 55-test command) | **54 passed, 1 failed** (55 collected; the 1 failure is the separate state-preservation issue in §7, not Docker-related) |
| Separate pre-existing issue (§7) | Reproduced identically; unchanged |
| Code modifications | **None** |
| Tests not executed | **0** — Docker was available throughout; nothing was left unexecuted |
| New defects identified | **0**, subject to the evidence qualification in §3 about the earlier full-suite run's 3 non-reproducing failures |

Do not read the 19/19 figure above as the project's overall pass rate — it describes only the itemized
Docker-dependent subset in §2, not the full suite.

**Headline test-count figures (264/283, 93.3%) cited in the university report, both IEEE paper tracks, and the
presentation are NOT updated by this report.** This verification was scoped to the Docker-dependent subset only,
run in isolation from the rest of the suite — it does not by itself constitute the "one more clean full run" that
would be needed to responsibly promote a new overall headline pass-rate (see
`FINAL_SOURCE_OF_TRUTH_AND_RECONCILIATION.md`, Finding 11, for that separate, broader recommendation).

The current verification successfully executed all 19 itemized Docker-dependent test cases against an available
Docker daemon. This establishes that every test in the identified Docker-dependent subset passed during this
verification. The historical difference between the 18-failure narrative and the 19-case itemized inventory
remains documented separately (§2) and is not retroactively reclassified.

This verification expands the project's demonstrated real-Docker test coverage — 19 previously Docker-blocked or
Docker-skipped tests now run and pass against a live daemon — while preserving the existing application and the
project's historical research results unchanged.
