# Protocol ADCOM-E1..E3 v1 — mechanism ablation under injected faults, handoff-cost measurement, grounding probe

Status: written and hashed BEFORE any E1–E3 result was produced. Branch `adcom2027/multiagent`, base `cb888f2`.
Evidence classes in this protocol: **REPLAY** (real orchestrator code, recorded evaluator outputs, stubbed LLM), **SOCKET**
(real orchestrator + real HTTP sockets to a local fake service), **CONSTRUCTED** (inputs authored by us). None of them is a
live-model run; none measures LLM or learning quality. Nothing is changed after seeing results without a new registered
experiment (amendments are appended to the end of this file, never edited in place).

## 0. Question and scope
Primary question: **In the implemented hub-and-spoke pipeline, which orchestrator-level coordination mechanisms keep the
stored session record faithful to the authoritative evaluator evidence when components fail or misbehave, and what do they
cost?**
- RQ1 (authority). Which roles change which part of the session state? (descriptive probe, `results/trace_state_writes.json`,
  run before this protocol; reported as descriptive, not as a test.)
- RQ2 (necessity). For each implemented mechanism M, is there a registered fault F under which removing M violates a
  registered invariant I that the full system satisfies? (E1)
- RQ3 (cost). What does the failure/handoff path cost in calls and wall-clock when the LLM service is healthy, refusing or
  hanging? (E2)
- RQ4 (grounding). What does the Qwen-output grounding check accept and reject on constructed outputs, and what class of
  contradiction can it not see? (E3)
Not claimed: that the system is decentralised, that agents negotiate, that any mechanism improves feedback quality or
learning, or any rate that would hold with a live LLM.

## 1. Fixture (E1, E2)
- 8 sessions (k = 0..7). Session k asks the 8 benchmark questions (qid 1, 3, 7, 10, 15, 22, 41, 50) and answers each with the
  k-th recorded answer (ordered by case_id). The 8 sessions cover each of the 64 recorded answers once.
- Evaluator = replay of `research/results/paper2/paper2_evaluator_raw.json` (`raw_eval` payload, sha256 recorded in the run
  manifest). A follow-up question is answered with the recorded answer of its root primary question (replay has no recorded
  follow-up answers; this makes the candidate "non-improving" and is a stated limitation).
- Timer fixed at 0.6 × allowed time (no timing modifier). Candidate has no id (no SQLite writes).
- PPO checkpoint and guardrails are the shipped ones (`agents/strategy/hybrid_orchestrator.py`), `deterministic=True`.
- Qwen service: 'down' (ConnectError, orchestrator's own non-LLM fallbacks) unless a cell says otherwise.
- Driver: `max_retries = 2` per turn after `retry_answer`; `max_turns = 40` per session.
- Seeds: stochastic faults use `numpy.random.default_rng(seed)` with seeds 0..19; deterministic faults run once.
- Unit of analysis = session. Sessions from different seeds reuse the same 64 recorded answers, so seeds are repeated draws of
  a fault schedule on fixed items, not independent samples; all intervals are descriptive.

## 2. Variants (implemented in the harness by patching an instance; repository code is not modified)
| id | variant | how |
|---|---|---|
| V0 | full system as shipped | — |
| V1 | − score validator | `orch._validator = None` |
| V2 | − guardrails | `orch._apply_guardrails = lambda a,*x: a` |
| V3 | − PPO policy (heuristic recovery path) | `orch._strategy = None` |
| V4 | − follow-up agent | `orch._decide_and_inject_followup` returns False |
| V5 | − consecutive follow-up cap | `consecutive_followups` reset to 0 before the follow-up decision |
| V6 | − fail-closed evaluator handoff | an unavailable evaluator is handed on as an ordinary answer with `final_score = 0.0` |
| V7 | − attempt rollback | `orch._rollback_tentative_attempt` is a no-op |

## 3. Faults
| id | fault | schedule |
|---|---|---|
| F0 | none | control |
| F1 | evaluator permanent outage | every call raises |
| F2 | evaluator intermittent outage | each call fails with p = 0.25, seed s |
| F3 | malformed evaluator score | call i returns `final_score` ∈ {None, NaN, "high", 1.7, −0.3}[(i + s) mod 5] |
| F4 | evaluator inconsistent with its own gate | for payloads with `mandatory_pass == False`, `final_score := 0.95` |
| F5 | duplicate submission | the candidate submits each answer twice before moving on |

## 4. Invariants (computed per session from final state and the harness log)
- **I1 no committed score from a failed or invalid evaluator call.** A committed `answers[i]` violates I1 if no evaluator call
  for that question returned a finite number in [0, 1] before the commit (F1, F2, F3). Count per session.
- **I2 valid stored numbers.** Every entry of `scores` and of `raw_scores` is finite and in [0, 1]. Count per session.
- **I3 mandatory gate.** For F4 turns, the committed score ≤ 0.65 (the `ScoreValidator.mandatory_cap`).
- **I4 termination.** The driver reaches `session_end` within `max_turns` without exhausting retries.
- **I5 follow-up bound.** The longest run of consecutive follow-up turns ≤ 2.
- **I6 state consistency.** `len(scores) == len(raw_scores) == len(answers)` and equals the number of distinct delivered
  question ids that were answered (F5).
- **I7 low-score safety.** After a committed turn with score < 0.30, `current_difficulty` did not increase (counted over turns).

## 5. Cells and pre-registered predictions
Cells: every variant × {F0} (7 non-V0 variants plus V0 → 8 cells) and the fault-specific cells below. Prediction = does the
variant violate the invariant in at least one session. "known" = from reading the code/documentation before this protocol;
"unsure" = no prior expectation.
| cell | invariant | V0 | prediction for the ablated variant |
|---|---|---|---|
| F1 × V0, V6 | I1, I4 | I1 ok, I4 not reached (retry exhausted) | V6: I1 violated (known) |
| F2 × V0, V6 | I1, I4 | I1 ok | V6: I1 violated (known) |
| F3 × V0, V1 | I1, I2 | V0: **I1 violated** for None/NaN/"high" (orchestrator and validator both map them to 0.0; known from prior inspection) | V1: I2 on `raw_scores` violated for 1.7 / −0.3 (unsure; the timer clamps `scores`) |
| F4 × V0, V1 | I3 | I3 ok | V1: I3 violated (known) |
| F0 × V5 | I4, I5 | I4, I5 ok | V5: I5 and I4 violated (known, with the non-improving replay candidate) |
| F5 × V0, V7 | I6 | I6 ok | V7: I6 violated (unsure) |
| F0 × V0, V2, V3 | I7 | unsure | V2: I7 violated more often than V0 (unsure) |
| F0 × V4 | I5 | ok | no violation (trivial) |
Result handling: every cell is reported, including those that contradict the prediction; no cell is dropped or re-run with a
modified harness. A cell where V0 itself violates an invariant is reported as a finding about the shipped system.

## 6. E2 — handoff cost (SOCKET class)
Single session k = 0, V0, F0. A local server binds `localhost:8001` (the address hard-coded in the orchestrator and the
feedback agent) in three modes: **ok** (scripted valid JSON), **refuse** (nothing listens), **hang** (accepts and never
replies). Real `httpx` and the real timeouts (6.0 s). Record per turn: wall-clock of `handle_voice_answer` and of
`handle_next_question`, number of HTTP attempts, and the roles' share of time from the tracer. Report medians and the
maximum. Analytic worst case from the code constants is reported separately and labelled analytic.

## 7. E3 — grounding probe (CONSTRUCTED class)
For each of the 64 recorded evaluator payloads build constructed Qwen feedback outputs by deterministic templates (script
`experiments/e3_grounding_probe.py`, committed before the run): C0 faithful; C1 `what_was_correct` repeats a missing
concept verbatim; C2 repeats an incorrect claim verbatim; C3 narrative "correctly explained <missing concept>"; C4 narrative
credits a truncated paraphrase of a missing concept; C5 score leak; C6 generic fluff. Calls
`services.qwen.app._validate_feedback_output`. Report accepted/total per category. C4 is an existence demonstration of the
check's lexical limit, not a rate. Categories with no applicable payload (no missing / no incorrect claim) are excluded and
the exclusion count is reported.

## 8. Reporting
Counts with Clopper–Pearson 95% intervals where a rate is given; medians/ranges for timing; no significance tests (cells are
deterministic or low-n by design). Result files are write-once under `results/` with sha256 recorded in
`results/RUN_LEDGER.md`. Environment (python/numpy/torch/sb3 versions, host CPU count) is recorded in the ledger.

## Amendments
- **A1 (before any E1–E3 result; after a harness smoke run on 1 seed to check the scripts execute).** (a) E1 records also store, per
  session, the per-turn difficulty path, score path, follow-up flags and decision-source path. (b) One **exploratory,
  non-registered** descriptive metric is added: `reversals` = number of sign changes in the sequence of non-zero difficulty
  changes in the RL phase, reported for V0, V2, V3 and labelled exploratory. It does not enter the invariant table. Reason: the
  smoke run showed the harness works end to end; the exploratory metric was suggested by looking at one smoke-run path
  (V0, session 0), which is disclosed here rather than hidden. (c) Harness speed-ups that do not change logic: the HTTP client
  class is replaced by a stand-in raising `ConnectError` in 'down' mode, `PPO.load` is memoised, and the 0.1 s retry back-off
  sleeps are skipped in E1 (E2 uses real sockets and real delays).
- **A2 (after E1 and E3 results, before E2 finished; registered as experiment E4).** E1 showed that the shipped system commits a
  malformed evaluator score (None, NaN, non-numeric) as a candidate score of 0.0 (F3 × V0, I1: 160/160 sessions) and repairs
  out-of-range numbers by clamping. Change under test (branch `adcom2027/multiagent`, `agents/orchestrator/interview_orchestrator.py`):
  with config key `strict_evaluator_contract` (default True) a payload whose `final_score` is not a finite number in [0, 1] is
  treated like an evaluator outage (fail closed). Setting the key to False reproduces the pre-change behaviour inside the same
  code (variant B); True is variant S. E4 grid (8 sessions per deterministic cell; 20 seeds for stochastic cells; same fixture,
  driver, invariants I1, I2, I4 as above): F0; F3 applied to every call with a single malformation type each
  (None, NaN, "high", 1.7, −0.3); F2 (p = 0.25); F6 = each call is malformed with p = 0.10, type drawn uniformly from the five.
  Pre-registered predictions: (i) F0: score, difficulty and follow-up paths are identical for B and S; (ii) S: I1 = 0 in every
  cell; (iii) B: I1 violated for every malformation type; (iv) S under F3-each: sessions cannot progress (I4 false), the
  integrity/availability trade-off; (v) F2: B and S identical; (vi) F6: S completes at least as many sessions as the driver
  retry budget allows (reported, no threshold). Existing regression tests and new tests (`tests/unit/test_evaluator_contract.py`)
  must pass. No change to the validator, guardrails, reward, state or action definitions.
- **A3 (after E2 and E4 results; registered as experiment E5).** E2 (SOCKET) measured median 0.14 s per turn with a healthy service,
  0.69 s with a refusing service and 24.7 s with a hanging service (24 turns, 495 s in total), matching the analytic worst case
  (2 attempts × 6 s for feedback plus 2 × 6 s for the follow-up call). The unused field `FeedbackAgent._qwen_ok` shows that no
  circuit breaker exists. Change under test: `agents/orchestrator/circuit_breaker.py` (threshold 2 consecutive failures,
  cooldown 60 s, one half-open probe) used at the three Qwen call sites. `QWEN_BREAKER.enabled = False` reproduces the previous
  behaviour inside the same code (variant B); enabled is variant S. E5 design (SOCKET class, same server as E2, session k = 0,
  V0, F0, real timeouts, real sockets): (a) hang mode, B, un-paced (repeat of E2 on the final code); (b) hang mode, S, with the
  breaker's clock advanced by a pacing P ∈ {30, 60, 120} s after every turn (candidate think time; the clock is injected, the
  HTTP timeouts stay real); (c) refuse mode, S, P = 60; (d) ok mode, S, P = 60 (must never open); (e) recovery: the server hangs for
  the first 8 turns and answers afterwards, S, P = 60, count the turns until the first LLM-path response. Measures: per-turn
  `handle_voice_answer` wall-clock (median, max, total), HTTP attempts counted at the client, breaker state transitions.
  Pre-registered predictions: (i) S/hang per-turn median ≤ 8 s at P = 60 and total time far below B's; (ii) at P = 30 the median
  is no larger than at P = 60 … reported either way; (iii) ok mode: 0 opens; (iv) recovery: LLM path restored within one cooldown
  after the server recovers (≤ 2 turns at P = 60); (v) the fallback content and committed scores are identical for B and S
  (the breaker changes waiting, not outputs; checked on the committed score path). New tests: `tests/unit/test_circuit_breaker.py`.
  Parameters were chosen before E5 from the E2 timeout constants and are not tuned afterwards. Client-side HTTP attempt counts
  are the reported counts; the server-side request counter of E2 showed 96 requests against 80 client attempts in hang mode and a
  separate 3-versus-5 check reproduced an excess of server-side hits; the cause was not investigated and server-side counts are not used.
