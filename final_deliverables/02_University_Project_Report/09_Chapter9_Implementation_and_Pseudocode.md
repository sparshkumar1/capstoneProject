# Chapter 9: Implementation and Pseudocode

## 9.1 Implementation Decisions (orchestrator)

The following implementation patterns in `agents/orchestrator/interview_orchestrator.py` were verified in Phase 1/2 of this project's inspection and are reused here as accurate (not independently re-derived, but cross-checked against the architectural facts established in Chapters 5–7):

- **Concurrency safety via `asyncio.Lock`**: the orchestrator is instantiated once per WebSocket session; every public mutating method acquires an instance-scoped lock at entry, so duplicate or out-of-order events within one session are serialised without any cross-session performance penalty (separate sessions use separate lock instances).
- **Dependency injection for testability**: the orchestrator's two most complex dependencies — the evaluator function and the question-selection function — are accepted as constructor arguments rather than imported directly, allowing the 25-file automated test suite (Chapter 10) to inject deterministic mocks and test every logical branch (baseline transitions, guardrail activations, follow-up injection, session termination) without starting any external service.
- **Single source of truth for state**: all mutable session state lives in one dictionary (`self._state`); REST-facing code receives only a shallow copy, keeping the serialisable state clean while internal bookkeeping (question queue, attempt counts) stays private.
- **Idempotent termination**: `end()` caches its generated report on first call; every subsequent call (which can arrive from a near-simultaneous WebSocket disconnect and explicit end-session event, especially on mobile connections) returns the cached result rather than re-executing report generation, eliminating a race condition that would otherwise be possible.

## 9.2 Pseudocode — Adaptive Difficulty Pipeline

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

    final_action, overridden, guardrail_id = apply_canonical_guardrails(
        perf=obs.perf, avg_perf=obs.avg_perf, conf=obs.conf, hes=obs.hes,
        progress=obs.progress, difficulty=session.difficulty,
        proposed_action=action
    )

    session.difficulty = clamp(apply(final_action, session.difficulty), 1, 5)
    log(action, overridden, guardrail_id)   # for turns.jsonl and this report's evidence
```

## 9.3 Pseudocode — FeedbackAgent Assembly

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

## 9.4 Pseudocode — This Phase's Test Scripts (representative example)

The following is the actual pattern used by the 10 new, independently executed test scripts written in this phase (full scripts under `testing_and_evaluation/`), shown here as implementation documentation for how this report's evidence was produced:

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

This directly-against-production-code verification pattern (no mocking of the function under test, real inputs, assertable boundaries) is why the guardrail coverage gap documented in Chapter 10 §10.3 could be found empirically rather than only by manual code reading.
