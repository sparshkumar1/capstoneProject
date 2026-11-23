# Speaking-Rate Unit Mismatch — Full Trace and Draft Correction Protocol

**Status: diagnostic + draft protocol only.** The defect below is verified. The fix is **not implemented** and the evaluation is **not run**. Per `CLAUDE.md`, any production-code change and any new experimental run requires a hashed, git-tagged protocol and an approved run manifest, obtained before execution — this document is the draft that approval would apply to, not a record of anything already done.

## 1. Complete data path, with units at each stage

| Stage | File : line | What it computes | Unit produced / expected |
|---|---|---|---|
| Transcription | `agents/audio/transcriber.py:219-221` | `speaking_rate = word_count / (total_speech_time / 60.0)` | **Words per minute.** Realistic range ≈ 100–200 for normal speech. |
| Stored as | `agents/audio/transcriber.py:233` | `"true_speaking_rate": round(float(speaking_rate), 2)` | Same field name used everywhere downstream — no unit is recorded alongside it. |
| Confidence scoring | `agents/audio/confidence_scorer.py:40-44` | `rate = transcription["true_speaking_rate"]`; compares to `[2.1, 4.3]`, center `3.2` | **Words per second** (code comment in the sibling file confirms this reading; realistic words/sec ≈ 2–4). |
| Hesitation scoring | `agents/audio/hesitation_scorer.py:52-57` | Same field, same `[2.1, 4.3]` comparison; comment reads *"optimal 2.1–4.3 words/sec"* | Words per second. |
| Call site (confidence + hesitation) | `apps/backend/main.py:635-693` (`_analyze_audio_confidence`) | Passes the raw `transcription` dict (containing the WPM-scale field) directly into both scorers | No conversion anywhere in this path. |
| Live orchestrator state | `agents/orchestrator/interview_orchestrator.py:354-356, 1678-1679` | `conf = last_confidence_score` (set from `audio.get("confidence_score")`, i.e. the `C_final` output of the scorer above); `hes = max(0.0, 1.0 - conf)` | Both are downstream of the already-affected `C_final`. |
| PPO / guardrail input | `agents/orchestrator/interview_orchestrator.py:1685` | `self._apply_guardrails(action_idx, score, avg_perf, conf, hes, diff_norm)`, and the same `conf`/`hes` feed the 6-D observation the live policy acts on | **Affected**, for every real (non-simulated) candidate session. |
| Separate 5-D state builder | `agents/audio/rl_state_vector.py:15-54`, called from `apps/backend/main.py:663-672` and `agents/audio/main.py:56` | Uses `hesitation.get("hesitation_score", 0.5)` — the *raw* hesitation-scorer output (which independently embeds the same rate-based term via its own `rate_dev` calculation) | **Also affected**, via a different route (the hesitation scorer's own `rate_dev`, not just via confidence). **Not fully resolved in this pass:** whether this 5-D `rl_state` value is consumed by anything beyond being returned inside the `_analyze_audio_confidence` response payload (e.g., surfaced to the frontend, logged, or actually fed to a policy call) was not confirmed. Flagged as an open item, not asserted either way. |

## 2. Deterministic verification (already performed, reversible, no new data)

Real, unmodified `score_breakdown` (confidence) and `score_hesitation` functions, called directly with representative WPM inputs and otherwise-neutral prosodic inputs:

```
rate=100.0 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
rate=140.0 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
rate=160.0 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
rate=181.27 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
```

For contrast, feeding the same functions a words-per-second-scale value inside the intended range (e.g., `3.2`) produces `rate_score=1.000` — confirming the functions work correctly when given the unit they expect, and that the defect is purely a unit mismatch at the interface, not a bug in the scoring arithmetic itself.

## 3. Mathematical contribution of the affected terms

- `C_final = 0.28·VQ + 0.27·L + 0.22·F_fluency + 0.13·rate_score + 0.10·F_rhythm` (Eq. 17). With `rate_score` pinned at 0.000, `C_final` is depressed by a fixed 0.13 relative to what it would be at `rate_score = 1.0` — i.e., every real session's confidence score is missing up to 13% of its intended ceiling, regardless of how well-paced the candidate actually is.
- The hesitation scorer's six-term blend includes `rate_dev` (pinned at 1.000, its maximum) as one input to `hesitation_score`; its exact weight was not re-derived in this pass (see `agents/audio/hesitation_scorer.py` for the full weighting) and is left as a specific, small follow-up read rather than asserted from memory.
- Downstream, `hes = 1 - conf` in the live orchestrator path means the depressed `conf` mechanically inflates `hes`, compounding the effect on both the Confidence and Hesitation dimensions of the observation the live policy and guardrails act on.

## 4. What is affected vs. not affected

**Affected (confirmed by code tracing):**
- The live orchestrator's real-time Confidence and Hesitation state dimensions, for any session using real transcribed audio (`interview_orchestrator.py` path).
- The guardrail rules that consume `conf`/`hes` directly (`_apply_guardrails`).
- The candidate-facing confidence label/score wherever `C_final` is surfaced.
- Possibly the separate 5-D `rl_state` builder's Hesitation term (open item, §1).

**Not affected (confirmed by code tracing):**
- The technical evaluator (`S1`, `S2`, `R`, `S_final`) — no acoustic or rate signal enters `services/evaluator/app.py`'s `evaluate()` at all.
- The frozen P3 confirmatory RL study (`research/experiments/paper3/`) — its environment (`rl/env/interview_env.py`, `rl/training/simulated_candidate.py`) assigns confidence/hesitation values directly from synthetic personas; it never calls `transcriber.py`, `confidence_scorer.py`, or `hesitation_scorer.py`. **The PPO-vs-constant-difficulty equivalence finding is therefore independent of this defect** — it is not an artifact of the same bug, and fixing this bug would not, by itself, be expected to change that result, since the confirmatory study never exercised real audio.
- The reasoning-verification correlation figures in `EXISTING_EVIDENCE_ANALYSIS.md` — entirely text-based, no audio path involved.

## 5. Regression tests needed before any fix ships

None of the existing tests would have caught this, because `tests/unit/test_speech_pipeline.py:112-127` feeds `confidence_scorer`/`hesitation_scorer` hand-picked words/sec-scale values directly, never routing a realistic transcriber output through them. A correction should add, at minimum:
1. A test that calls `transcriber.py`'s rate computation (or a fixture matching its exact formula) and pipes the result directly into `confidence_scorer.score_breakdown` / `hesitation_scorer.score_hesitation`, asserting `rate_score` is *not* pinned to 0.0 for a realistic WPM value.
2. A regression test locking the *intended* mapping (whichever unit is chosen as canonical after the fix) so a future edit to either side of the interface cannot silently reintroduce the mismatch.
3. An assertion on the `apps/backend/main.py:_analyze_audio_confidence` → orchestrator call path with a realistic end-to-end fixture (transcript text long enough to derive a realistic rate), not just isolated unit-level calls.

## 6. Draft experimental design for evaluating a correction (NOT approved, NOT run)

- **RQ:** Does correcting the unit mismatch change (a) the distribution of `C_final`/hesitation values across a realistic range of speaking rates, and (b) the live guardrail/PPO decision distribution, relative to the current (defective) behavior?
- **Candidate fix (to be decided, not decided here):** either convert `transcriber.py`'s output to words/second before it leaves that function, or change the `[2.1, 4.3]` threshold and `3.2` center in both scorer functions to their WPM equivalents (≈ 126–258, center ≈ 192, if a direct ×60 rescaling is used — this specific choice needs its own justification, not just an algebraic rescale, since the "optimal" band may not have been chosen to survive rescaling; this is exactly the kind of decision that needs sign-off before implementation, not something to decide unilaterally here).
- **Baselines:** current (defective) behavior, kept as the disclosed starting point, not silently replaced.
- **Method:** (i) apply the fix in an isolated branch/worktree, not on the frozen production path directly; (ii) run the new regression tests from §5; (iii) re-run the full existing test suite for unrelated regressions; (iv) re-run the frozen PPO/guardrail evaluation protocol with the corrected signal substituted for synthetic-persona-derived confidence/hesitation where applicable, or, if the confirmatory study is simulation-only and does not consume real audio (per §4), instead run a new, explicitly-scoped analysis of the live orchestrator's decision distribution using recorded or newly-collected realistic speaking-rate values, clearly labeled as a new experiment.
- **Metrics:** distribution of `rate_score` and `C_final` before/after across a realistic rate sweep (80–220 WPM); count and direction of guardrail activations that change under the corrected signal, if any recorded/replayable session logs exist to test against; no claim of "improvement" — a corrected signal is not evaluated against a ground truth of "better," only against "matches its own documented design intent."
- **What this must not become:** a vehicle for silently tuning the confidence/RL system to produce more favorable-looking paper results. The fix should be justified purely by matching the code's own documented intent (the `[2.1, 4.3] words/sec` comment already states what was intended), not by which threshold produces the nicest downstream numbers.
- **Approval required before any of this executes:** yes, per `CLAUDE.md` — this touches a live scoring path (`confidence_scorer.py` and/or `hesitation_scorer.py` and/or `transcriber.py`) and constitutes a new experimental run once the fix is evaluated. A hashed protocol and git tag should be created at the point the exact fix is chosen, before implementation.

## 7. Honest scope statement

Identifying this defect does not, by itself, establish that fixing it would improve anything measurable about candidate experience or system behavior — only that the component currently does not do what its own code comment says it is supposed to do. Any claim beyond that (e.g., "fixing this improves confidence accuracy") would need the evaluation in §6, which has not been run.
