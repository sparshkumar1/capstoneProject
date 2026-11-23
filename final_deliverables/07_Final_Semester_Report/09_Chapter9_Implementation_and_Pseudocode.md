# Chapter 9: Implementation and Pseudocode

## 9.1 Orchestrator Implementation Decisions

This phase's inspection verified the implementation patterns in `agents/orchestrator/interview_orchestrator.py` detailed in Chapter 6, Section 6.1; they are summarised here as the basis for the pseudocode below:

- **Concurrency safety via `asyncio.Lock`**: one orchestrator instance exists per WebSocket session, and every public mutating method grabs an instance-scoped lock at entry. Duplicate or out-of-order events within a single session get serialised this way, with no performance cost to other sessions.
- **Dependency injection for testability**: the orchestrator's two most complex dependencies, the evaluator function and the question-selection function, come in as constructor arguments instead of being imported directly. That lets the 25-file automated test suite (Chapter 10) inject deterministic mocks and exercise every logical branch without ever starting an external service.
- **Single source of truth for state**: all mutable session state lives in one dictionary. REST-facing code only ever receives a shallow copy of it. That keeps the serialisable state clean while internal bookkeeping (the question queue, attempt counts) stays private.
- **Idempotent termination**: the session-termination method caches its generated report the first time it runs, so every call after that returns the cached result instead of regenerating the report from scratch.

## 9.2 Pseudocode: Adaptive Difficulty Pipeline

**Which guardrail call this represents (corrected in this correction pass).** The pseudocode below shows the pipeline's overall shape, which both implementations share. The `apply_guardrails(...)` step is **not** a literal call to `rl.guardrails.apply_canonical_guardrails()` on the live production path. The live orchestrator (`interview_orchestrator.py::_apply_guardrails`) is a separate, hand-duplicated implementation with three confirmed divergences from the canonical module (Chapter 6, Section 6.3; Chapter 10, Section 10.3). The canonical function is the one `rl/env/interview_env.py` calls during RL training and simulation. It's also the one this phase's own boundary tests (Chapter 10, Section 10.3) exercise directly. Presenting a single unified pseudocode block for both is a deliberate simplification for readability. The two implementations' actual rule conditions differ, as documented in Chapter 6, Section 6.3.

```
function adapt_difficulty(session, latest_score):
    if session.current_question_index < BASELINE_LENGTH:
        apply deterministic baseline schedule
        return  # RL not consulted

    obs = build_rl_observation(latest_score, session.difficulty, session)
    norm_obs = (obs - vecnormalize.mean) / sqrt(vecnormalize.var + eps)
    norm_obs = clip(norm_obs, -10, 10)

    if ppo_model.ready and ppo_model.compatible:
        action_idx = ppo_model.predict(norm_obs, deterministic=True)
        action = ACTION_MAP[action_idx]
    else:
        action = heuristic_fallback(latest_score)   # score-threshold rule

    # Live path: interview_orchestrator.py's own _apply_guardrails (hand-duplicated).
    # Canonical path (RL training/simulation only): rl.guardrails.apply_canonical_guardrails().
    # The two differ -- see Chapter 6, Section 6.3.
    final_action, overridden, guardrail_id = apply_guardrails(
        perf=obs.perf, avg_perf=obs.avg_perf, conf=obs.conf, hes=obs.hes,
        progress=obs.progress, difficulty=session.difficulty,
        proposed_action=action
    )

    session.difficulty = clamp(apply(final_action, session.difficulty), 1, 5)
    log(action, overridden, guardrail_id)   # for turns.jsonl and this report's evidence
```

## 9.3 Pseudocode: FeedbackAgent Assembly

```
function assemble_feedback(turn_result, session):
    feedback = {}
    feedback.final_score, feedback.grade = turn_result.score, turn_result.grade
    feedback.score_breakdown = {S1: ..., S2: ..., R: ...}
    feedback.strong_points = turn_result.covered_concepts
    feedback.missing_concepts = turn_result.missing_concepts   # mandatory concepts first
    feedback.incorrect_or_incomplete = detect_misconceptions(transcript, rubric)
    feedback.trend = compute_trend(turn_result.score, session.rl_perf_history[-3:])

    if confidence_score and hesitation_score available:
        feedback.communication_tips = derive_from_audio_signals(...)
    else:
        feedback.communication_tips = []   # empty list, never a fabricated placeholder

    if turn_result.score <= 0.65:
        feedback.detailed = call_qwen_microservice(turn_result, session)  # selective LLM call
    else:
        feedback.detailed = template_feedback(turn_result)

    return feedback   # all 15 schema fields always populated, never omitted
```

## 9.4 Backend Dispatch: WebSocket Event Routing

This phase's verification confirms the backend dispatcher (`apps/backend/main.py`) contains no domain logic at all: it is a thin router that forwards each JSON-encoded WebSocket event to the matching orchestrator method:

```
async function websocket_handler(websocket, session_id):
    orch = session_registry[session_id]
    for message in websocket.iter_json():
        event = message["type"]
        if event == "start": await orch.start()
        elif event == "voice_answer": await orch.handle_voice_answer(
            message["transcript"], message["qid"], message["attempts"])
        elif event == "code_submission": await orch.handle_code_submission(
            message["code"], message["qid"], ...)
        elif event == "next_question": await orch.handle_next_question()
        elif event == "request_hint": await orch.request_hint(message["qid"])
        elif event == "skip_question": await orch.skip_question(message["qid"])
        elif event == "end_session":
            report = await orch.end()
            await websocket.send_json({"type": "session_report", "data": report})
```

Look closely and every one of those branches is nothing more than a method call handed off to the orchestrator — no conditional logic sits here, no state gets inspected, no score gets computed. That's intentional: it's what lets the dispatcher layer get tested, or swapped out entirely, without anyone having to touch interview domain logic.

## 9.5 React Frontend Implementation

Under the hood this is a fairly ordinary React-on-Vite app, split across two main views — the Interview Room and the Session Report — that both stay connected to the backend over the same single persistent WebSocket opened when the session starts.

**Interview Room (`InterviewRoom.jsx`).** Voice capture goes through the browser's own `MediaRecorder` API. Once submitted, the audio blob gets base64-encoded and shipped to the backend inside the `voice_answer` WebSocket message, riding alongside whatever transcript the browser's `SpeechRecognition` API already produced on its own — that transcript is there purely as a fallback, in case server-side Whisper transcription ends up slower than expected. Code questions get a CodeMirror editor instead, which only shows up when the question's own metadata says it's a coding question. Between questions, a difficulty indicator (1–5) ticks to whatever value the orchestrator sent in its next-question message. And if a hint ever gets requested — by the candidate, or unprompted by the guardrail/feedback layer — the orchestrator's Qwen-generated hint text renders inline, visually set apart so it reads as supplementary guidance rather than part of the question itself.

**Session Report (`Report.jsx`).** Once the orchestrator acknowledges that the session has ended, this view renders five things at once: a score-timeline chart tracking the candidate across every question, a per-topic bar chart calling out where they were weakest, a concept-coverage summary colour-coded by status (fully covered, partially covered, missed), a behaviour-metrics panel with average confidence, hesitation, and a clarity rating built from filler-word rate and response length, and a per-question drill-down that opens into the full fifteen-field feedback dictionary for that turn. Of everything the candidate sees, that drill-down is the most detailed — it's meant to be the thing they actually use to revise afterward.

## 9.6 Logger Implementation: Session Persistence

Running quietly alongside everything else, the Logger writes turn-level and session-level data to disk without ever blocking the evaluation or feedback pipeline it's shadowing. It's built to be strictly passive — it watches and records, but never feeds anything back into session state or any downstream decision. One consequence of that design: a logging failure can't touch the candidate's actual experience, and the logger itself can be switched off entirely in test environments with zero effect on how the rest of the system behaves.

**Turn-level logging.** After every evaluated turn, a structured log record holding that turn's complete state is appended as a single JSON object to a session-specific `turns.jsonl` file (one line per turn). JSONL was chosen over a single JSON array specifically because it supports incremental writes. Each turn flushes to disk immediately after evaluation. So a session that terminates unexpectedly, whether from a crash or a disconnect, leaves behind a recoverable partial log, not a corrupt or empty file. Each turn record carries the question ID and metadata, the candidate's full transcript or submitted code, all fifteen FeedbackAgent output fields, the raw and weighted component scores, the action the strategy layer selected, the resulting difficulty, and the audio-analysis features where available.

**Session-level summary.** When the session ends, a session-level aggregate file (`summary.json`) is generated once from the complete `turns.jsonl` record. It captures total questions attempted, per-topic average scores, the overall session mean score, the complete difficulty trajectory, the action-frequency distribution, average confidence and hesitation, and a final performance classification.

**Graceful degradation.** If the Logger fails to write to disk, say a filesystem permission error or disk-space exhaustion, the failure is caught, a structured warning goes to the application log, and the session simply continues. The session report still gets generated from in-memory session state and returned to the candidate. Only the persistent disk record is lost.

## 9.7 Pseudocode: This Phase's Test Scripts (representative example)

What follows is the actual pattern used by the new, independently executed test scripts this phase wrote (full scripts under `testing_and_evaluation/`), included here as implementation documentation for how this report's evidence was produced:

```
function verify_guardrail_boundary(cases):
    for (label, perf, avg_perf, conf, hes, diff, proposed, expected) in cases:
        final_action, overridden, guardrail_id = apply_canonical_guardrails(
            perf, avg_perf, conf, hes, progress=0.5, difficulty=diff,
            proposed_action=proposed
        )
        assert guardrail_id == expected, f"{label}: MISMATCH"
        record_result(label, final_action, guardrail_id)
    report(total_cases, mismatches)
```

It is exactly this pattern that mattered: no mocking of the function under test, real inputs, boundaries you can assert against. That discipline is what let the guardrail coverage gap documented in Chapter 10, Section 10.3 be found empirically, not only by reading the code by hand.
