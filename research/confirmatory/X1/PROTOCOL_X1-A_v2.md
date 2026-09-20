# X1-A v2 protocol — fault-injection campaign rerun on build B (Paper 1)

Registered by commit + annotated tag `prereg/X1-A/v2` BEFORE the v2 run. Harness `x1a_harness_v2.py`.
**This is a rerun after repairs, not a blind replication.** The v1 results (`prereg/X1-A/v1`, `freeze/X1-A/v1`, build A) showed defects in FLT-03 and FLT-06 and one timing-bound miss in FLT-07b; they are retained unchanged.

## 1. Build B and what was repaired
Commit tagged `sut/X1/build-B` (see `DEFECT_DECISIONS_FLT03_FLT06.md`): (a) evaluator outage fails closed in `handle_voice_answer` (FLT-03); (b) executor removes the timed-out container (FLT-06); (c) `feedback_agent` reports the service's real `llm_status`; (d) Qwen feedback token cap 256 → 512. (c) and (d) matter for X1-B, and (c) is exercised by FLT-01/02 (the local stub returns no `llm_status`, so the default `available` is unchanged there).

## 2. Design, criteria, controls, interpretation rules
**Identical to `PROTOCOL_X1-A.md` (v1)**: same scenarios, criteria, SLAs (`SLA_QWEN_DOWN_S = 5.0`, `SLA_QWEN_SLOW_S = 15.0`, `SLA_DOCKER_DOWN_S = 2.0`, `COMPILE_TIMEOUT_S = 10.0`, `DB_BUSY_TIMEOUT_S = 30.0`), perturbation controls and `REPS = 5`. **The FLT-07b upper bound (33.0 s) and the 5.0 s Qwen-down SLA are deliberately not changed** even though v1 showed them tight; changing them after seeing results would break the like-for-like comparison, so FLT-07b may fail again for the same timing reason and would then be reported as such. The v2 harness differs from v1 **only** in protocol tag, SUT tag (`sut/X1/build-B`), output directory (`results/x1a_v2`), the two checked file names and docstring text (`diff x1a_harness.py x1a_harness_v2.py`).
Not repaired, carried as limitations (`X1_METHOD_AUDIT.md`): FLT-05 injects "CLI not found", not an unresponsive daemon; FLT-04's oracle accepts NaN/Inf/−3 → 0.0; FLT-03's oracle checks in-memory state only (persistence is covered by a unit test, not by this campaign); FLT-08/09 not executed.

## 3. Outcome reporting
`X1-A-old-vs-new.md`: per scenario v1 result, v2 result, changed outcomes, whether any claim changed. Wording rule for "fault-tolerant" is unchanged from v1 §5 and remains unavailable while any executed scenario fails or FLT-08/09 are unexecuted (protocol scopes the term to the executed classes; the paper should still prefer "failure-aware").
