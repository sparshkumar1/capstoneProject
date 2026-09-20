# Decisions on the X1-A defects FLT-03 and FLT-06 (2026-09-20)

Build A = `release/app-repair/v1` (`980747ff…`). Build B = the repair commit tagged `sut/X1/build-B` (hash in `X1_OLD_VS_NEW_SUMMARY.md`). Original X1-A/X1-C results are retained unchanged.

## FLT-03 — evaluator outage recorded as a candidate score of 0.0 → **FIX**
**What happens (build A, read from the code and reproduced by X1-A).** `_evaluate_verbal` already returns an explicit failure state (`status`/`decision_source = evaluator_unavailable`, `final_score 0.0`). `handle_voice_answer` then (1) passes it to the feedback agent, which produced ordinary-looking feedback and dropped the flag; (2) computed a timing-modified score from the 0.0; (3) **persisted an attempt with `raw_score = validated_score = 0.0`** when a candidate id exists; (4) appended 0.0 to `scores`/`raw_scores`; (5) ran difficulty adaptation on it; (6) consumed one of the candidate's attempts.
**Can it alter a retained claim?** Yes:
- *Candidate grading / session scoring / report:* the outage lowers the session's technical score and per-topic averages.
- *Authoritative best answer:* a 0.0 attempt is stored in the attempt history and enters the comparison against the previous best.
- *RL state and difficulty:* the difficulty controller's performance input becomes 0, so the next difficulty can drop because a service was down.
- *User-visible feedback:* the candidate sees feedback generated from a fabricated failing score.
- *Research measurements:* any application-level measurement made during an outage would silently contain false zeros.
It contradicts Paper 1's own dependability framing ("failure-aware", "no fabricated score") and the design text elsewhere in the repository ("free retry, turn not counted against candidate"). Papers 2 and 3 do not run through this path (offline benchmark; simulator).
**Repair (build B).** On an evaluator outage `handle_voice_answer` now returns immediately with `status = decision_source = evaluator_unavailable`, `infrastructure_failure = true`, `final_score = null`, grade `Unscored`, and `next_action = "retry_answer"`. It appends nothing to `scores`/`raw_scores`/`answers`, does not adapt difficulty, does not persist an attempt, restores the attempt count and the previous timing values, restarts the timer, and records an `infrastructure_errors` entry and a log line. `_evaluate_verbal` is unchanged. The candidate can answer the same question again.
**Deliberately not changed.** (a) NaN/Inf/out-of-range evaluator output is still clamped (NaN/Inf/−3 → 0.0): a faulty evaluator that returns a number is a different failure from an outage and changing it would alter the frozen FLT-04 criteria; it is reported as a residual limitation. (b) Empty or failed-STT transcripts keep their existing explicit, flagged `Ungraded` 0.0 turn (`stt_unavailable`); that is an intentional, tested behaviour about the candidate's audio, not a service outage.
**Old test contract changed on purpose:** `tests/integration/test_multiagent_responsibility_and_failures.py` asserted `final_score == 0.0` for an evaluator failure; it now asserts the fail-closed state.

## FLT-06 — compile timeout leaves the container running → **FIX**
**What happens (build A).** `subprocess.run(..., timeout=10)` kills the local `docker` client on `TimeoutExpired`; the container it started is not stopped and has no lifetime of its own (`--rm` fires only when the container exits). X1-A observed a live container 3 s after return in 5/5 runs.
**Repair (build B).** Compile and run containers get a unique `--name`; on `TimeoutExpired` the executor runs `docker rm -f <name>` (best effort, 15 s cap). The same pattern existed in the run phase's own `TimeoutExpired` branch and was fixed the same way (it is not exercised by X1-A; it is covered by a unit test for the compile path only). No other executor behaviour changed (flags, limits, statuses, policy pre-flight).
**Why a rerun is required.** `agents/coding_executor` is the SUT of X1-C and the executor path of X1-A. The added `--name` changes every `docker run` command line, so the old X1-C result belongs to build A. Both X1-A and X1-C are rerun in full on build B under new registration tags; results are kept beside, not over, the build-A results.

## Other application defects examined for X1-B (Qwen path)
| Item | Decision | Reason |
|---|---|---|
| `feedback_agent` hard-coded `llm_status = "available"` even when the service returned its deterministic template (`non_llm_structured_recovery`, `llm_unavailable`) | **FIX** (one line: pass the service's `llm_status` through; default `available` when absent) | Truthfulness of a status field the paper's claims and the UI rely on; the service itself already reported the truth. |
| Feedback generation capped at 256 new tokens; the nine-field JSON is often truncated → silent template | **FIX** (cap 512, env `QWEN_FEEDBACK_MAX_NEW_TOKENS`) | Reproduced offline in the X1-B v1 diagnosis; a truncated JSON turns every LLM call into the template. Roughly doubles worst-case generation time. |
| Client timeout 6.0 s vs 13–21 s real generation on this CPU | **NOT CHANGED — documented limitation** | The UI abandons an evaluation after 20 s (`InterviewRoom.jsx`), so raising the client wait without a product decision on the latency budget would create a different inconsistency. On CPU-only hardware the shipped configuration therefore serves the deterministic feedback; that is a latency finding for the paper, not a correctness defect. The X1-B campaign continues to raise the wait to 600 s as a registered deviation. |
| Follow-up channel (Qwen text becomes the question and expected concepts) | **NOT CHANGED — documented dependency** | Design property, not a defect; B1 does not cover it. |
