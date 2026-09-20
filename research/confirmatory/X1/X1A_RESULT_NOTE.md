# X1-A result note — fault-injection campaign (executed 2026-09-20)

Single execution of the registered protocol (`prereg/X1-A/v1`, registration commit `80ac60447c7fe7cc1c2facd86f9819f3efbfb20b`, SUT `release/app-repair/v1`), exit 0, 60 scenario repetitions, 0 harness errors, no leftover containers after the run's own cleanup. Outputs and hashes: `run_records/x1a/RUN_RECORD.json`. No retry, no criterion or bound changed after seeing results.

## Per-scenario outcome (5 repetitions each; no pooled figure)
| Scenario | Criteria met | Oracle controls | Finding |
|---|---|---|---|
| FLT-01 Qwen unavailable | 5/5 | valid | Returned in 4.84–4.90 s (SLA 5.0 s — small margin), `llm_unavailable`, score/concepts identical to the no-fault control, next request recovered |
| FLT-02 Qwen slower than client timeout | 5/5 | valid | 12.78–12.85 s (SLA 15.0 s), same fallback behaviour, recovered |
| **FLT-03 evaluator unavailable** | **0/5** | valid | **Defect.** The failure was recorded as a candidate score of 0.0 (grade "F"), no infrastructure flag anywhere (`status`, `decision_source`, `infra*` keys, `infrastructure_errors` all empty), and the LLM stub still produced "available" feedback on it. Failed criteria: `infrastructure_failure_flagged`, `no_zero_score_recorded_as_candidate_failure` |
| FLT-04 invalid evaluator score (NaN / Inf / 999 / −3) | 5/5 each | valid | All four were clamped into [0, 1]: NaN, Inf and −3 became **0.0**, 999 became 1.0. The registered criterion (finite, in [0, 1]) is met, but a NaN or Inf is stored as an ordinary 0.0 with no flag, i.e. the same silent-zero pattern as FLT-03 |
| FLT-05 Docker daemon unreachable | 5/5 | valid | `sandbox_error` in ≈0 s, not accepted, no container created, recovery on the next call |
| **FLT-06 compiler outlives the timeout** | **0/5** | valid | **Defect.** The 10 s compile timeout fired correctly (`compilation_error`, "timed out", 10.5–11.1 s) and the next submission ran, but a container was still running 3 s after return in **5/5** runs. Cause (from the code path): on timeout the executor's `subprocess.run` kills the `docker` client process, not the container, and the container has no time limit of its own |
| FLT-07a SQLite lock held 2 s | 5/5 | valid | write waited (2.09 s), acknowledged, one row |
| **FLT-07b SQLite lock held 34 s** | **4/5** | valid | In every run the write failed visibly (`OperationalError: database is locked`), left 0 partial rows, and a retry after release succeeded. One run (33.086 s) exceeded the pre-registered upper bound of 33.0 s (30 s busy timeout + 3 s); all five took 32.58–33.09 s, i.e. about 2.6–3.1 s above the nominal 30 s. Recorded as failed exactly as registered; the bound was not moved. The behaviour itself matched the intent, the tolerance was too tight |
| FLT-10 empty input | 5/5 | valid | Empty and whitespace transcripts and empty code returned structured outcomes without exceptions. Descriptive, non-criterion observation: an empty transcript is recorded as a **0.0** score for the turn (`stt_unavailable`, grade "Ungraded") |
| FLT-08 WebSocket reset, FLT-09 audio crash | not executed | | no claim is supported |

## What this supports
"For the executed fault classes on this build, the Qwen-outage, Docker-outage, invalid-score-range, database-lock and empty-input scenarios met their pre-specified criteria (FLT-07b with one timing-tolerance miss); two scenarios exposed defects: an evaluator outage is recorded as a 0.0 candidate score without an infrastructure flag (FLT-03), and a compile timeout leaves the container running (FLT-06)." "Fault-tolerant" may **not** be claimed (protocol §5: it requires every executed scenario to pass). "Failure-aware" or "failure-characterised" is the supportable framing, with the two defects named.

## Consequences and decisions (not taken here)
- Defect policy (draft §2): both defects are reported as found and the original results are retained. **No fix was made.** A fix to FLT-03 changes scoring/difficulty semantics (an evaluator outage would stop counting as a 0.0 answer, which also feeds the difficulty controller) and needs explicit approval. A fix to FLT-06 changes `agents/coding_executor`, which is also the SUT of X1-C; it would need a new build tag and a complete rerun of X1-A and X1-C, with both builds' results retained.
- The silent 0.0 for NaN/Inf (FLT-04) and for empty input (FLT-10) is the same design question as FLT-03 and should be decided together.
- Limits: in-process injection, one machine, Qwen dependency replaced by a local stub, SLAs derived from SUT constants, oracle controls are perturbations of observations rather than mutant builds, no concurrency.
