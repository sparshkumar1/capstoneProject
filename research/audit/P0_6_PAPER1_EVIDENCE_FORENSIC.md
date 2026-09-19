# P0-6 — Paper 1 fault-injection / Qwen / test-count evidence

Forensic pass, 2026-09-19. **Nothing was rerun**: no Docker container, no pytest, no benchmark. All findings come from reading the frozen script, stored results, source code, test files and Git history. Existing tests are identified by reading them; I did not execute them, so "a test exists" is not "the test passes today" (CLAUDE.md records one known failing test in the current tree).

Evidence classes used (as requested):
- **A** — genuinely executed in the recorded Paper 1 run *and* independently evidenced.
- **B** — partially executed / partially evidenced (real behaviour exists in tests or code, but the Paper 1 record does not show it, or the observation does not discriminate).
- **C** — represented only by a hard-coded PASS in the Paper 1 script/output.
- **D** — unverifiable from anything in the repository.

## 0. Bottom line

The audit's suspicion is **confirmed for the fault-injection and Qwen tables**, and the security table is **real but weakly judged**.

| Claim in the Paper 1 report | Verdict |
|---|---|
| "10/10 fault scenarios recovered" | **Not measured.** All ten rows are static dictionaries with a literal `"status": "PASS"` (`execute_paper1_study.py:279-426`, PASS at :423). Only four `ScoreValidator` asserts run (:399, :402, :406, :409). Classes: **A ×1, B ×5, C ×4.** |
| "5/5 Qwen boundaries verified" | **Not measured.** Five static dicts with literal `"PASS"` (`:659-713`); no Qwen output is generated or inspected. One "containment" mechanism (`FeedbackValidator`) **does not exist in the code base.** Classes: **B ×3, C ×2.** |
| "9/9 attack vectors contained" | **Real execution, weak oracle.** All nine programs were actually run (1 blocked by the static filter, 8 in Docker); 4 outcomes directly match the intended mechanism, 5 do not discriminate. Classes: **A ×4, B ×5.** |
| "213 tests passed, 0 failed" | **D** — no stored pytest output; the only recorded run is `204 passed, 1 skipped` (STEP0). |
| Concurrency 0 lock errors / 0 isolation violations, latency tables | **A (real measurement), scope-limited**; latency mean is contaminated by a cold-start sample. |
| `paper1_systems_results.csv` PASS column | **C** — every "PASS" is a literal string (`:950-960`); no criterion is defined. |

## 1. What the script actually executes

| Section | Executes real work? | Notes |
|---|---|---|
| 1 Security suite (`:81-272`) | Yes — `validate_source_safety()` + `DockerCSandbox.compile_and_execute()` | pass = observed status ∈ {timeout, runtime_error, compilation_error, sandbox_error, wrong_answer, accepted}; `expected_outcome` is recorded but **never compared**; `"host_safe": True` is hard-coded |
| 2 Fault injection (`:279-428`) | **No** — 4 `assert`s on `ScoreValidator`, then PASS for every row | rows are pre-written text |
| 3 Concurrency (`:435-566`) | Yes — real threads, real SQLite | synthetic writes only (no evaluator, no LLM); max 25 sessions |
| 4 Latency (`:573-652`) | Yes — real timings | evaluator N=20 |
| 5 Qwen isolation (`:659-713`) | **No** | five static dicts, PASS literal |
| 6 Multimodal (`:720-742`) | Narrow — `inspect.signature(evaluate)` asserts no `audio/pitch/prosody` parameter | proves only the function signature |
| 7 Threat model (`:745-`) | No — static mapping table | documentation, not a test |

The same pattern already existed in the earlier script `research/scripts/run_paper1_systems_study.py:573-584` (two asserts, then `"Graceful fallback verified; zero data loss"`, `"100%"`, `PASS` for all ten rows), whose stored output is `research/results/fault_injection.csv`. Both files share the same hard-coded pattern; neither is fault-injection evidence.
The raw JSON (`paper1_systems_raw.json`) records `docker_available: true` (Docker via WSL2 Ubuntu-22.04), the evaluator/model/gold hashes, and a hard-coded `git_commit 375f4f8…` string. The script and results were committed together in `b7cad49`, and no console log of the run is stored.

## 2. Security suite (SEC-01 … SEC-09)

All nine were genuinely run. The stored `observed_status` values and my reading:

| ID | Observed status | Does the observation show the intended containment? | Class |
|---|---|---|---|
| SEC-01 ptrace | `policy_blocked` (static filter, 0.0 s) | Yes for the static pre-flight filter (not a runtime container property) | **A** |
| SEC-02 socket creation | `wrong_answer` (exit 0, stdout ≠ "test") | **No.** In a `--net=none` namespace `socket()` still succeeds; the program exits 0 either way | B |
| SEC-03 syntax error | `compilation_error` | Yes; also covered by `tests/unit/test_coding_executor.py::test_docker_detects_c_compilation_error` | **A** |
| SEC-04 null deref | `runtime_error` | Yes (crash contained, host unaffected) | **A** |
| SEC-05 infinite loop | `timeout` | Yes; also `test_docker_terminates_infinite_loop_timeout`, `test_timeout_infinite_loop` | **A** |
| SEC-06 256 MB malloc, 128 MB cap | `wrong_answer` (exit 0) | **No.** No OOM kill (137 → `memory_limit`) was observed, so the memory cap was not shown to be exercised. The unused-allocation loop is compiled with `-O2` and may have been optimised away (hypothesis, untested) | B |
| SEC-07 exfil to 8.8.8.8 | `wrong_answer` (exit 0) | **No.** Program ignores `connect()`'s return value and prints nothing; blocked vs. succeeded is indistinguishable | B |
| SEC-08 fork bomb | `timeout` (3.5 s) | Partially: the host survived and the run returned; the `--pids-limit` is not isolated as the cause | B |
| SEC-09 write to `/etc` | `wrong_answer` (exit 0) | Weakly consistent (a successful `fopen` would return exit 1, i.e. `runtime_error`), **but the script's pass test is vacuous**: it checks `"tamper" not in eval_out.get("stdout","")` and `eval_out.get("exit_code",0)==0`, and the sandbox result has **no top-level `stdout` or `exit_code`** (`coding_executor.py:414-431`), so the test is always true | B |

Design evidence (code, not a run): the sandbox command line sets `--user 1001:1001 --net=none --cap-drop=ALL --security-opt=no-new-privileges --memory --memory-swap --pids-limit --read-only` (`agents/coding_executor/coding_executor.py:195-203, 302-310`). This documents configuration, not effectiveness.

**Supportable:** "Nine adversarial C programs were run through the static policy filter and a Docker sandbox on WSL2; four (SEC-01, 03, 04, 05) produced outcomes matching the intended control; five ran with outcomes that did not discriminate containment from non-containment (SEC-02, 06, 07, 08, 09)."
**Not supportable:** "9/9 (100 %) contained."

## 3. Fault-injection scenarios (FLT-01 … FLT-10)

"Paper 1 record" is what the study itself shows (all `C` except where an assert ran). "Independent evidence" lists tests I found by reading `tests/` (not run here). Note that every test below simulates the failure with `patch`/an unreachable port; none injects a real outage, and none was recorded in the Paper 1 run.

| ID | Paper 1 record | Independent evidence located | Class |
|---|---|---|---|
| FLT-01 Qwen offline | literal PASS | `test_multiagent_responsibility_and_failures.py::test_qwen_failure_preserves_evaluator_evidence` (unreachable port → `llm_unavailable`, evaluator score and concepts preserved); `test_qwen_followup_feedback.py::test_qwen_attribution_available_vs_unavailable` | **B** |
| FLT-02 Qwen generation > 3000 ms | literal PASS | none found (no timeout-injection test) | **C** |
| FLT-03 Evaluator 503 | assert: `is_infrastructure_failure` true for `evaluator_unavailable`, false for a real 0.0 (:405-409) | `test_evaluator_failure_produces_structured_failure_without_fabrication` (patched exception → `final_score 0.0`, "unavailable"); `test_validator_distinguishes_infrastructure_failure_from_candidate_failure`. "Retry without penalty" and the user message are unverified | **B** |
| FLT-04 NaN / Inf / 999.0 | asserts on NaN and Inf (:399-402) | `tests/unit/test_score_validator.py` (out-of-range clamp, NaN/Inf, wrong type, None, malformed evidence) | **A** (core validator claim only) |
| FLT-05 Docker daemon down | literal PASS | `test_docker_unavailability_produces_structured_sandbox_error` (patched `_resolve_docker_prefix` → `sandbox_error`) | **B** |
| FLT-06 compiler hang > 10 s | literal PASS | none (existing tests cover syntax errors and runtime infinite loops, not a compiler hang) | **C** |
| FLT-07 DB lock contention | literal PASS | the concurrency run (§5) exercises 1–25 threads with 0 `OperationalError`, but **no lock was injected** and the 30 s busy-timeout retry path was therefore never exercised (`services/storage/database.py:31`) | **B** (load only, not fault injection) |
| FLT-08 WebSocket abrupt reset | literal PASS | none found (no disconnect test) | **C** |
| FLT-09 audio-feature crash → neutral 0.5 / 0.5 | literal PASS | only STT-failure tests (`test_stt_failure_produces_structured_failure_state`) and RL-observation fallbacks (`test_rl_env.py`); the earlier script's NaN-hesitation assert is not in the Paper 1 script; no test of a Parselmouth crash | **C** |
| FLT-10 empty payload | literal PASS | `test_timer_scoring.py::test_stt_unavailable_produces_zero_without_timing_artifacts` (empty transcript → `stt_unavailable`, score 0.0). User-facing message unverified | **B** |

Totals: **A = 1, B = 5, C = 4, D = 0.** The statement "10/10 recovered" has no measurement behind it; at most FLT-04 is fully evidenced. The claim-safety note in the report ("all tested fault scenarios recovered") is not true of anything that was *tested in the study*.

## 4. Qwen role isolation (QWN-01 … QWN-05)

Nothing in `verify_qwen_isolation()` calls Qwen or inspects its output. Independent evidence, by reading:

| ID | Claim | Evidence located | Class |
|---|---|---|---|
| QWN-01 scoring exclusion | score comes only from SBERT+FAISS+CrossEncoder | by construction: `evaluate(qn, candidate, rubric)` has no LLM input (signature check in §6 of the script); `test_followup_agent_cannot_alter_authoritative_evaluator_score` | **B** |
| QWN-02 difficulty isolation | "LLM cannot alter state" | design statement only; no test found | **C** |
| QWN-03 `is_best` isolation | deterministic SQL `is_best` | `tests/unit/test_persistence_and_history.py` (best selection, tie-breaking, five-attempt sequence). "LLM has zero DB write access" is a design claim | **B** |
| QWN-04 evaluator-truth grounding | "**FeedbackValidator** rejects empty/boilerplate outputs" | `FeedbackValidator` **does not exist** anywhere in the code (referenced only in the Paper 1 script/report strings). Related but different: `test_exact_transcript_grounding` | **C** (named mechanism absent) |
| QWN-05 offline/timeout fallback in < 50 ms | offline part | offline: `llm_unavailable` tests exist; the "< 50 ms" figure and the timeout case are not measured anywhere | **B** (offline) / **D** (< 50 ms) |

Totals: **A = 0, B = 3, C = 2.** "5/5 boundaries verified" is not supported by what was executed.

## 5. Other Paper 1 claims

| Claim | Evidence | Class |
|---|---|---|
| SQLite WAL concurrency: 1/5/10/25 sessions, 0 lock errors, 0 isolation violations (`paper1_concurrency_results.csv`) | Real threaded run (`:435-566`); synthetic writes/reads only; P95 write latency 17.9 / 126.5 / 263.8 / 719.1 ms | **A**, scope-limited (single machine, ≤ 25 threads, no evaluator/LLM in the loop; does not test the retry path — see FLT-07) |
| Evaluator latency, N=20 warm | Real timings: mean 1960.8 ms, median 404.6 ms, P95 2098.6 ms, **P99 26,369 ms** — one cold-start-scale outlier contaminates the mean (inferred ≈ 32 s single sample) | **A** for the measurement; the mean is not a "warm" statistic; three incompatible latency statements exist elsewhere (see the numerical-verification CSV) |
| Acoustic insulation | `inspect.signature(evaluate)` has no audio parameters | **A** for the narrow signature claim; the wider phrasing "prosody excluded 100 %" is **B** (the evaluator still sees transcript text, incl. hedging words — see the main audit) |
| Threat-model mapping (7 categories) | static table in the script | **C** (documentation) |
| `paper1_systems_results.csv` "PASS" column | literal strings | **C** |
| "213 tests passed, 0 failed" (`PAPER1_EXECUTION_COMPLETION.md:28`) | no stored log; STEP0 records `204 passed, 1 skipped` at 383.87 s; CLAUDE.md notes one known failing test in the current tree | **D** |
| Provenance `git_commit 375f4f8…` | hard-coded string; script/results first committed together in `b7cad49` | ambiguous (see stale-artifact audit) |

## 6. What can honestly be claimed now

- A systems description of the architecture and its configured isolation flags (code facts).
- Real measurements: SQLite WAL synthetic concurrency to 25 sessions (0 errors); per-operation latencies with the outlier caveat; nine adversarial C programs run with the outcome breakdown in §2.
- `ScoreValidator` clamps/handles NaN, Inf and malformed input (unit tests + four executed asserts) and distinguishes infrastructure failure from a genuine 0.0.
- Mocked-failure tests exist for evaluator failure, Qwen unreachable, Docker unavailable and empty transcript; they are unit/integration tests, not a fault-injection campaign.
- Explicitly **not** claimable: "10/10 faults recovered", "fault-tolerant", "5/5 Qwen boundaries verified", "9/9 contained", "213 tests passed".

## 7. What legitimate support would require (recommendations only — USER DECISION REQUIRED; new experiments, not run)

1. **Fault injection with a real oracle.** For each FLT, a harness that *injects* the fault (stop or firewall the Qwen process; a local stub returning 503 / hanging past the timeout; unreachable Docker host; a compile that exceeds the compile timeout; a second connection holding a write lock for less than and longer than the 30 s busy timeout; a WebSocket client that resets mid-evaluation; a truncated audio buffer; an empty payload), computes PASS from asserted fields (status code, `decision_source`, DB row present, score unchanged, latency bound), runs ≥ 30 trials per scenario, stores raw logs with the commit, and reports Wilson CIs (30/30 → 95 % lower bound 0.887; 10/10 → 0.722). Pre-specify the criteria before running.
2. **Qwen isolation with real outputs.** Feed adversarial prompts (change score / difficulty / best flag) to the real Qwen service and assert that evaluator score, difficulty state and `is_best` rows are unchanged; add a code-path test that no LLM output reaches scoring. Either implement a real feedback validator or remove the claim.
3. **Security oracles that discriminate.** Programs that print their own observation (`connect()` return value and `errno` for SEC-02/07; `errno == EROFS` for SEC-09; forks succeeded before `EAGAIN` for SEC-08; volatile/`-O0` allocation so an OOM kill (137) is expected for SEC-06), a pass rule that compares against `expected_outcome`, host-side canaries (file outside the container, a listener the container must not reach), and repeated trials.
4. **Test-suite claim:** a stored pytest report (JUnit XML) with commit and environment; resolve or disclose the known failing test.
5. **Latency:** report median/P95 with the cold-start sample separated (N ≥ 100 warm runs).

## 8. Classification

`EVIDENCE_GAP` (fault-injection, Qwen isolation, test count) + `DOCUMENTATION_ERROR` (literal PASS presented as measured results; non-existent `FeedbackValidator`; vacuous SEC-09 criterion). New experiments are needed **only if** these claims stay in the paper; otherwise the claims can be reworded to §6 without any new run.
