# Architecture inventory — what is actually multi-agent in PREPAIred

Snapshot: `cb888f28ee57a4d14c966307020ed039d8dbfd9b` (all line numbers refer to that commit unless "(branch)" is stated).
Evidence labels: **code** = read in source; **traced** = observed on the 8 replay sessions (`results/trace_state_writes.json`,
186 turns); **test** = covered by a named test; **E1/E2/E3** = experiments of protocol ADCOM-E1..E3 v1.
V10 and the earlier papers were not used to describe the system; the code is the authority.

## 1. One-paragraph verdict
PREPAIred is a **centrally orchestrated, role-separated pipeline**, not a decentralised multi-agent system. One
session-scoped object (`InterviewOrchestrator`, `agents/orchestrator/interview_orchestrator.py:119`) owns all session state,
serialises every mutation with one `asyncio.Lock`, and calls the other roles synchronously (in-process calls, or HTTP to the Qwen
service). No role calls another role, no role holds private state that survives a turn (the PPO policy and the follow-up
policy are functions of state passed in), and there is no negotiation, voting, delegation tree or planning loop. Measured with
Wooldridge and Jennings' weak notion of agency (autonomy, social ability, reactivity, pro-activeness), only the difficulty
policy is a learned, reactive decision-maker; the follow-up and feedback roles are LLM-assisted functions with deterministic
fallbacks; the rest are deterministic modules. What *is* distinctive and testable is an **authority partition**: which
component may write which part of the session record (section 5).

## 2. Roles (component, authority, kind)
| Role | Code | Inputs → outputs | Decision kind | Independent decision-maker? | LLM / RL / rule |
|---|---|---|---|---|---|
| Hub / session controller | `interview_orchestrator.py:119` (`handle_voice_answer` :369, `handle_next_question` :1085, `handle_retry` :1039) | candidate answer, evaluator payload → committed score, state, next question | deterministic state machine | it is the coordinator, not a peer | rules |
| Evaluator (authoritative scorer) | `services/evaluator/app.py:451` `evaluate`; called in-process through `apps/backend/main.py:108` `_run_integrated_evaluator` and `Orchestrator._evaluate_verbal` :1408 | question, transcript, rubric → score, correct/missing/incorrect concepts, confidence | learned scorer (SBERT + FAISS + fine-tuned cross-encoder), no generation | no (pure function) | learned, not an LLM |
| Score validator | `agents/validation/score_validator.py:55` | raw score + evidence → clamped score + trace | deterministic caps (mandatory cap 0.65, penalty ≤ 0.25) | no | rules |
| Feedback agent | `agents/orchestrator/feedback_agent.py:77` `generate` :86 | evaluator payload (+audio) → feedback text | Qwen call with deterministic template fallback | no (function) | LLM (optional) + rules |
| Follow-up agent | `Orchestrator._decide_and_inject_followup` :1822, `_inject_followup_question` :1861; generator `services/qwen/app.py` `/followup` :884, fallback `_synthesize_structured_followup` :598 | evaluator evidence → new question inserted in queue | policy (gap/score thresholds, cap 2) + Qwen text, fallback template | partially (a policy, but invoked by the hub) | rules + LLM (optional) |
| Difficulty policy | `agents/strategy/hybrid_orchestrator.py:165` `suggest` :188; guardrails `Orchestrator._apply_guardrails` :1631 | 6-D observation → easier/same/harder | PPO (frozen checkpoint, `deterministic=True`) then rule overrides G4,G1,G2,G3,G6 | yes, the only learned decision-maker | RL + rules |
| Timer | `agents/timing/timer.py:31` | start/stop → timing modifier | deterministic | no | rules |
| Question selector | `apps/backend/main.py:493` `select_questions` (production); `agents/question_selector/` is a commented baseline artifact | topics, difficulty → question list | deterministic | no | rules |
| Code sandbox | `agents/coding_executor/coding_executor.py:35` | code → compile/run result in Docker | deterministic, isolated | no | rules |
| Hint / report generator | `Orchestrator._get_hint` :1590, `services/qwen/app.py` `/hint`, `/report` | context → text | Qwen call, explicit `llm_unavailable` state on failure | no | LLM |
| STT / prosody | `agents/audio/` | audio → transcript, confidence, hesitation | deterministic pipeline | no | learned STT, signal processing |

Only one language model is used (Qwen2.5-1.5B Q4_K_M behind `services/qwen/app.py`, see `docs`/`research` for provenance);
it serves three roles (follow-up text, feedback text, hint/report). In this environment the model weights are not present,
so no LLM output was generated in any experiment (section 8).

## 3. Communication and coordination
- **Mechanism (code):** method calls inside one process; `httpx.AsyncClient` POSTs to `http://localhost:8001` (Qwen) with
  `timeout=6.0`, two attempts, two endpoints (`interview_orchestrator.py:1895-1912`, `feedback_agent.py:580-600`); WebSocket/REST
  between browser and backend (outside this paper). No message bus, no agent-to-agent protocol.
- **Message contract:** Python dicts. Typed only at the Qwen service boundary (`FollowupRequest/Response`, `FeedbackRequest/Response`,
  `services/qwen/app.py:327-410`); the evaluator→hub payload is an untyped dict.
- **Shared vs private state (traced):** one dict `Orchestrator._state` plus the question queue; all writes to `scores`, `answers`,
  `raw_scores`, `timing_*`, `topic_*`, `question_history`, `followup_history` come from the hub's commit step
  (`_update_session_state` :1963). The difficulty policy writes only difficulty/RL fields (`current_difficulty`,
  `difficulty_history`, `rl_*`, `guardrail_applied`, `next_question_type`, `progress`). The follow-up agent changes only the
  question queue. Evaluator+validator and feedback agent change **no** state key in 186 traced turns.
- **Concurrency:** all public mutating methods run under one `asyncio.Lock` (:134). No peer concurrency.

## 4. Delegation, monitoring, retry, termination, conflict handling (code unless stated)
- **Delegation:** the hub calls roles in a fixed order per turn: evaluate → (validate) → feedback → commit → difficulty →
  follow-up → log (`handle_voice_answer` :379-616).
- **Timeouts/retry:** evaluator call `wait_for(180 s)`; failure → `evaluator_unavailable` → `_fail_closed_evaluator_unavailable`
  :620 (nothing scored, attempt not counted, timer restarted, error recorded). Qwen: 2 attempts × 6 s per call, 0.1 s back-off,
  then deterministic fallback. `FeedbackAgent._qwen_ok` is set but never read, so there is **no circuit breaker** (E2 measures
  the consequence).
- **Termination:** primary-question budget (`_primary_budget_exhausted` :926), queue exhaustion, follow-up cap
  `consecutive_followups >= 2` (:1836). Test: `tests/unit/test_primary_question_budget.py`.
- **Conflicting or unsupported outputs:** (a) Qwen feedback is accepted only if `_validate_feedback_output` passes
  (`services/qwen/app.py:686`); the check is lexical (exact/substring match, regex for score leakage); otherwise the
  deterministic template is used. (b) The evaluator's own evidence can contradict itself (the same string in `correct_claims`
  and `missing_concepts` in 17 of the 64 stored payloads, E3 exploratory count); no component reconciles it. (c) A malformed
  evaluator score is not detected at the hub in the shipped code (None/NaN/non-numeric become 0.0 and are committed; E1 F3);
  addressed in the branch change tested in E4.
- **Hallucination handling:** none on the LLM text beyond (a); the LLM never writes a score (section 5).

## 5. Authority partition (the architecture's real contribution to analyse)
Established by the traced write-set (186 turns) and by the code:
1. Only the hub commits candidate scores; its input is the evaluator payload (after the validator).
2. LLM-facing roles (feedback, follow-up text) cannot change `scores`, `raw_scores`, `answers` or difficulty. Test:
   `tests/integration/test_multiagent_responsibility_and_failures.py::test_followup_agent_cannot_alter_authoritative_evaluator_score`.
3. LLM text can still influence scoring indirectly: follow-up question text becomes the `question_text` given to the
   evaluator for the follow-up answer, and follow-up scores are appended to `scores` and are seen by the difficulty policy
   (`_update_session_state` :1963; `_adapt_difficulty` runs after every committed turn including follow-ups). This indirect
   path is a coupling between roles, documented here from code; its size was not measured (replay cannot measure it).
4. The difficulty policy and the guardrails are two decision components acting on the same variable. In replay this produces
   oscillation (exploratory metric, E1): see results.

## 6. What is centralised, what is decentralised
Everything is centralised in the hub. Decentralised aspects: process separation (Qwen service, sandbox container), and role
specific failure semantics (explicit `*_unavailable` states). There is no decentralised decision-making.

## 7. Tests that support architectural claims
`tests/integration/test_multiagent_responsibility_and_failures.py` (5 tests: evaluator outage fails closed; Qwen failure preserves
evaluator evidence; sandbox unavailability; RL unavailability falls back to a labelled heuristic; follow-up cannot alter
the score), `tests/unit/test_primary_question_budget.py`, `tests/unit/test_orchestrator.py`, `tests/unit/test_score_validator.py`,
`tests/unit/test_qwen_followup_feedback.py`, `tests/unit/test_best_answer_authority.py`, `tests/unit/test_timer_scoring.py`
(145 passed in this environment; first run showed 2 failures that did not reproduce, see `logs/`).

## 8. What was not verified here
No live Qwen, no live evaluator (models not available offline), no Docker sandbox run, no WebSocket path, no real
candidates. The architecture claims above are from code and replay; none is a statement about live behaviour.
