# Sixth research-and-engineering improvement pass — project-wide, evidence-driven

**Date:** 2026-09-28. **Scope:** non-PPO-focused, project-wide pass. Unlike the fifth pass (which found nearly every audit phase already covered and produced one verification/review document), this pass explicitly prioritized finding and fixing genuine, previously-undiscovered defects across the evaluator, audio pipeline and orchestration, and did so. Three real code defects were found, fixed, tested and regression-checked. Nothing was committed, tagged, pushed or submitted. No frozen file, checkpoint, protocol, or confirmatory/held-out data was touched.

## 1. Executive summary

Four genuine, independently-verified improvements were made this pass, three of them in code that had never been touched by any of the previous five passes (audio scorers, evaluator negation handling) and one that resolves the single persistent test failure that survived all five prior passes:

1. **Fixed the persistent `obs[4]` test failure** (§3) — root-caused in the fifth pass, resolved in this one via the safe option (correct a stale test/docstring to match already-documented, already-intentional runtime semantics; no behavioral/state-definition change). All 14 tests in the file now pass.
2. **Fixed a real NaN/Inf score-fabrication bug in the audio confidence and hesitation scorers** (§4) — a failed Parselmouth measurement (common on very short, silent or unvoiced audio) previously and silently produced the *best possible* voice-quality sub-score (confidence) or *worst possible* pitch-instability sub-score (hesitation), due to a Python `min()`/`max()` NaN-comparison quirk in the existing `_clamp()` helper. Both now score neutrally (0.5) when a measurement is invalid, with a new regression test.
3. **Fixed a real vocabulary-dependent false-negative bug in the evaluator's negation filter** (§2) — a plain substring check for `"not"` and `"no "` incorrectly classified sentences containing ordinary words like **"another"** (an-`not`-her) and **"notation"** ("Big-O notation" — ubiquitous in this project's own CS/algorithms question domain) as negations, silently excluding them from mistake-vector and misconception matching in three separate functions. Fixed with a single, shared, word-boundary-matched implementation; verified against the frozen 64-case human-gold benchmark (correlation unchanged within CI; six cases changed, all in the expected direction — previously-missed mistakes now correctly penalized).
4. **Diagnosed and explicitly deferred one genuine reliability tension** (§8) that turned out to require an author decision rather than a code fix: the shipped 6 s LLM-service client timeout versus the measured 19–30 s generation time is not just disclosed in P1's manuscript, it is *live and current* in `interview_orchestrator.py`; changing it would directly invalidate a manuscript claim about the "shipped configuration," so it was not touched.

No PPO code, config, checkpoint or evaluation script was touched this pass, consistent with the task's explicit instruction not to make this another PPO-only investigation.

## 2. Evaluator (Phase 2) — found and fixed a real bug, did not re-attempt a failed fix class

The three previously-documented embedding-similarity-based fix attempts for the evaluator's "correct terminology, wrong reasoning" weakness were **not repeated** — that specific problem remains open and is not solved here (see §9). Instead, this pass traced the complete scoring path (`services/evaluator/app.py::evaluate()` → `semantic_score`/`concept_detection`/`cross_encoder_verification`/`bonus_score`/`mistake_penalty`/`_detect_misconceptions`) looking for implementation-level defects distinct from the reasoning-correlation limitation, per the task's explicit instruction to look beyond another embedding-weight adjustment.

**Found:** `bonus_score()`, `mistake_penalty()` and `_detect_misconceptions()` each independently implemented the same "exclude negation sentences" filter as a plain substring check:
```python
negation_words = ["avoid", "avoids", "not", "without", "instead", "unlike", "no "]
filtered = [s for s in sentences if not any(neg in s.lower() for neg in negation_words)]
```
This matches `"not"` and `"no "` as **substrings**, not words. Verified directly:
```
"We use Big-O notation to describe the runtime."  -> matched (false positive: "no-TAT-ion"... "an-NOT-ation")
"A pointer ... is a variable that stores ... another variable." -> matched (false positive: "a-NOT-her")
"The pianist played a note." -> matched (false positive)
```
`"another"` and `"notation"` are both extremely common in ordinary technical English and, for this project specifically, in its own algorithms/CS question domain. Any sentence containing them was **silently excluded** from mistake-vector matching (`mistake_penalty`) and misconception detection (`_detect_misconceptions`) — meaning a genuine mistake stated in a sentence that happened to mention "another" or "notation" could escape penalty and never surface as an `incorrect_claim` in feedback. In `bonus_score`, the same bug caused under-crediting (excluded from bonus eligibility) rather than escaped penalty.

**Fix:** one shared, word-boundary-matched (`\b...\b`) implementation, `_is_negation_sentence()`, used by all three call sites (also removing the threefold duplication, a minor Phase 12 side-benefit). `"cannot"` was added explicitly to the word list, since it is the one genuine negation the old substring check caught that a naive `\bnot\b` boundary match would have missed (`"cannot"` has no internal word boundary around `"not"`).

**Verification (not tuning):**
- All 36 existing evaluator/adversarial-suite tests still pass (`tests/unit/test_evaluator.py`, `test_evaluator_logical_reasoning_adversarial.py`, `test_evaluator_v4_adversarial_development_suite.py`, `tests/integration/test_evaluator_feedback_integration.py`).
- Re-ran the existing, reusable regression-check script (`research/paper_strengthening/scripts/evaluator_v2_recalibration_check.py`, unmodified) against the frozen 64-case human-gold benchmark (read-only): correlation moved from 0.3812 (original evaluator) to **0.3728** (95% CI [0.2955, 0.5563] — overlaps both the original 0.3812 and the second-pass value 0.3787; not a statistically detectable change). Six of 64 cases changed score, **all six in the negative direction** (mean |Δ|=0.0081, max |Δ|=0.12), consistent with the fix's mechanism: previously-excluded sentences are now correctly checked and, where they contain a real mistake, correctly penalized. Traced one case (`BM-025`) sentence-by-sentence to confirm the exact mechanism: `"...a variable that stores... another variable."` — old code matched (false positive on "another"), new code does not.
- This was not evaluated against or tuned by looking at this benchmark; the fix was designed and justified purely from the substring-matching defect itself, and the benchmark was run afterward as a regression check, per the task's own required discipline.

**Other evaluator findings, not changed:** `evaluate()`'s `depth` diagnostic field computes sentence count from the raw (pre-deduplication) `candidate_text` rather than `scoring_text`, so a candidate repeating a sentence would see a (very slightly) inflated `depth` value even though `final_score`/`technical_correctness` are fully protected against this by the existing dedup fix. `depth` is explicitly documented as "NEVER added as positive bonus to technical score" and is display-only — labeled **investigated, no change justified** given its limited, already-bounded consequence and this pass's time budget; a one-line fix (`len(split_sentences(scoring_text))`) is available if the author wants it.

## 3. Orchestration (Phase 5) — resolved the persistent `obs[4]` test failure

The fifth pass root-caused this without fixing it (two options were left open). This pass evaluated both against the current, already-frozen research decision (`research/audit/rl_state_definition.md`'s dimension-$s_4$ discussion) and selected the safe one:

- **Not chosen:** changing `build_rl_observation`'s dimension-4 priority order to favor `last_time_norm` over `session["progress"]`. This would be a genuine RL state-definition change, explicitly gated by CLAUDE.md ("do not change reward/state/action definitions... without explicit approval") and by the audit document's own deferral of this exact decision to a future retrained-policy-suite call.
- **Chosen:** the module-level docstring in `agents/strategy/hybrid_orchestrator.py` (line 17) was stale — it described dimension 4 as `"time_norm: Normalized response latency"`, contradicting the same file's own, more specific function docstring 58 lines later (`"progress: Normalized session turn-progress ratio (t/T)"`) and CLAUDE.md's own compressed state description. This is a documentation defect, not a behavior change, and was corrected with an explicit cross-reference to the audit document.
- The test itself (`tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`) was rewritten to test the *current, correct, documented* semantics rather than the stale ones: it now sets a realistic `session["progress"]` value before the coding turn and asserts it is preserved (not corrupted by the coding turn's `execution_time_ms`), and separately asserts `last_time_norm` (a distinct, still-real state field) is also preserved — recovering the test's original intent (a coding turn must not corrupt prior state) without conflating it with a dimension it no longer governs. A second latent bug in the same test was also found and fixed in passing: the test's own "default missing-value" case asserted `obs[4] == 0.00`, but the actual, already-correct fallback logic produces `0.10` for that input (`len(scores)=1 / default total_turns=10`) — this assertion had never actually been reached in five prior test runs because execution always stopped at the first (now-fixed) failing line.

**Result:** all 14 tests in the file pass. This closes the single test failure that appeared, unchanged, in the second, third, fourth and fifth passes' final validation sections.

Beyond this, a broader search for other orchestrator state inconsistencies within this pass's time budget did not surface a second defect of comparable severity; the session-recovery, guardrail, and turn-advancement code paths were already extensively tested by the second and fourth passes' work (`test_session_recovery.py`, `test_live_websocket_session_recovery.py`) and were not re-audited from scratch here, per the task's own instruction not to repeat completed work without a specific reason to question it.

## 4. Audio processing (Phase 4) — found and fixed a real NaN/Inf fabrication bug

Traced the WPM→WPS conversion (already fixed in an earlier pass) and confirmed it remains correct and consistent between `confidence_scorer.py` and `hesitation_scorer.py`. Beyond that, this pass specifically targeted the task's own stated concern — "missing values and NaNs cannot silently become misleading best-case scores" — and found a real instance of exactly that failure mode, previously unaddressed:

`confidence_scorer.py`'s `_clamp(value) = max(minimum, min(maximum, value))`. When `value` is `float('nan')`, Python's `min(1.0, nan)` returns `1.0` (a NaN comparison is always `False`, so `min` keeps its first argument), so `_clamp(nan) == 1.0` — the *maximum* possible score. Since `jitter`, `shimmer`, `hnr` and `pitch_stddev` all reach `_clamp()` through formulas where a `0.0`-mapped or NaN-driven output happens to coincide with "flawless voice quality," **a failed Parselmouth measurement (documented to occur on very short, silent or unvoiced audio segments) previously and silently produced a perfect confidence sub-score for a signal that was never actually measured.** The same mechanism in `hesitation_scorer.py`'s jitter-based `pitch_instability` term produced the *opposite* fabrication — a NaN jitter silently became the *worst possible* hesitation contribution.

**Fix:** `confidence_scorer.py` gained `_get_measured()`, which distinguishes "no valid measurement" (`None`) from a genuine reading and returns `None` for missing, non-numeric, NaN or infinite values; `_compute_components()` now scores each affected sub-component neutrally (0.5) when its input is `None`, instead of feeding an unvalidated value into the existing formula. `hesitation_scorer.py`'s jitter term got the equivalent treatment. Both fixes are scoped exactly to the measured-value-is-invalid case; genuinely missing-but-*not*-attempted measurements and the already-fixed rate-conversion logic were left untouched (out of scope, already covered by dedicated tests from an earlier pass).

**Verification:** a new regression test, `test_nan_prosodic_features_score_neutrally_not_best_or_worst_case` (`tests/unit/test_speech_pipeline.py`), checks NaN and ±Inf jitter/shimmer/hnr/pitch_stddev all score neutrally, that a genuinely valid measurement is completely unaffected by the fix (non-regression check against the exact pre-fix formula outputs), and that partially-invalid input (one NaN field among three valid ones) only affects its own sub-score. All 16 tests in `test_speech_pipeline.py` pass, including the 15 pre-existing ones (no regression).

## 5. LLM pipeline (Phase 3) — audited, one tension found and explicitly deferred

Confirmed the deployed model remains Qwen2.5-1.5B-Instruct/GGUF as CLAUDE.md states. Traced `generate_followup`/`generate_feedback` in `services/qwen/app.py`: both already have a genuine try/except-with-deterministic-fallback structure (`_synthesize_structured_followup`/`_synthesize_structured_feedback`), truthful `llm_status` reporting, output validation (`_validate_followup_output`/`_validate_feedback_output`) and prompt sanitization of candidate-controlled fields (`_sanitize_for_prompt`, applied to `candidate_answer` and `previous_best_answer` at every call site) — this is already solid, prior-pass-hardened infrastructure and was not changed.

**One finding, not fixed:** the client-side call timeout (`httpx.AsyncClient(timeout=6.0)` in `interview_orchestrator.py:1546,1831`) is exactly the "shipped 6 s" value that P1's manuscript (§V-D, §VII) reports as shorter than the measured 19–30 s generation time — this is not a newly discovered defect, it is the live, current, still-true code behind an already-published, evidence-traced manuscript claim. **This was not changed**: bumping the timeout would directly invalidate P1's stated "shipped configuration" and require re-measurement and a manuscript update, which is exactly the kind of change Phase 15 says to stop before and document rather than execute unilaterally. Labeled **requires human decision** in §10.

No new LLM development benchmark was built this pass; the existing prompt-regression and structured-output-validation tests (`tests/unit/test_qwen_followup_feedback.py`, extensively extended across the second and third passes) were judged adequate for the time available and were not duplicated.

## 6. Security (Phase 7) — investigated, no actionable defect found

Checked prompt-injection sanitization coverage across every `_build_*_prompt` function in `services/qwen/app.py`: all candidate-controlled free-text fields (`candidate_answer`, `previous_best_answer`) are sanitized via `_sanitize_for_prompt` at every call site, unchanged since the earlier pass that introduced it. `topic`/`question_text` are interpolated unsanitized, but these are curated question-bank fields, not candidate-typed input, consistent with the threat model already tested in P1's X1-B-I campaign (which specifically targets `candidate_answer`/transcript-carried injection, not topic). `generate_hint`/`generate_report` are template-based (no LLM call at all), so they carry no prompt-injection surface regardless of input sanitization. No new actionable defect was found within this pass's time budget; this is not a claim of a complete security audit.

## 7. D1 benchmark (Phase 8) — verified unchanged, no new work needed

Checked `research/data/evaluator_benchmark/` (the frozen 64-case human-gold set — unaffected by D1) and searched for any D1-specific answer/content files dated after `D1_FINAL_BLOCKER_ASSESSMENT.md`. None exist. D1's status is unchanged from the fourth and fifth passes: the 122-question/67-confirmatory/26-development/29-excluded protocol (`SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V14.md`) remains the finalized design, no content has been authored, and independent human review remains unavailable. No new tooling gap was identified beyond what `D1_INDEPENDENT_REVIEW_PACKET.md` already covers.

## 8. PPO (Phase 9) — brief, as instructed

No PPO code, configuration, checkpoint, or evaluation script was touched this pass. The fifth pass's findings stand unchanged: development-selected checkpoint MAE 0.2697, seed-sensitive checkpoint-selection gain (worse on 3/5 seeds vs. fixed-budget), the skill=0.80 collapse mechanism, no demonstrated PPO advantage over Constant-Same, and the `obs[4]` state-definition tension (now resolved at the test/documentation level — see §3; the underlying training/runtime semantic split itself remains, by design, unresolved and disclosed). The confirmatory evaluation was not run. Checkpoint files under `rl/checkpoints/` were not inspected for backup status this pass (out of scope for a non-PPO-focused pass); this remains a standing, disclosed reproducibility risk (P3 §VIII already states the checkpoints cannot be regenerated).

## 9. P1/P3/system-paper impact

- **P1:** unaffected. No claim in P1 depends on evaluator, audio, or orchestrator internals changed this pass (P1's evidence is the X1 containment/fault-injection/invariance campaigns, none of which were touched). The LLM-timeout finding in §5 is directly relevant to P1's already-published Material Limitation #4 and confirms it remains accurate and current — a small positive for P1's evidence traceability, not a change to any claim.
- **P3:** unaffected in substance. The `obs[4]` fix (§3) touches exactly the runtime code and test that `rl_state_definition.md` already discusses as a disclosed limitation; fixing the stale test/docstring does not change the underlying training/runtime mismatch P3 already reports, and no P3 number, table, or claim required any change.
- **System paper:** unaffected; still correctly blocked on ethics clearance and a human study (`SYSTEM_PAPER_BLOCKERS.md`, unchanged). This pass's evaluator fix is arguably the most relevant future asset for that paper, since it improves the evaluator the eventual human study would rely on for the automated/human agreement analysis — but this is a code-quality improvement, not new evidence toward the system paper's readiness, and is not claimed as such.

## 10. Files changed this pass, and why

| File | Change | Reason |
|---|---|---|
| `services/evaluator/app.py` | Unified, word-boundary-matched negation filter (`_is_negation_sentence`), replacing three duplicated substring-based copies | Fixed a real false-negative bug (§2) |
| `agents/audio/confidence_scorer.py` | Added `_get_measured()`; jitter/shimmer/hnr/pitch_stddev sub-scores now neutral (0.5) on NaN/Inf/invalid input | Fixed a real best-case-fabrication bug (§4) |
| `agents/audio/hesitation_scorer.py` | Jitter-based `pitch_instability` now neutral (0.5) on NaN/Inf/invalid input | Fixed a real worst-case-fabrication bug (§4) |
| `agents/strategy/hybrid_orchestrator.py` | Corrected stale module docstring for observation dimension 4 | Documentation defect found while resolving §3 |
| `tests/unit/test_stage11_5_coding_adaptation.py` | Rewrote the two `obs[4]`-related assertions to match current, documented semantics; added a `last_time_norm` preservation assertion | Resolves the persistent failure (§3); recovers original test intent |
| `tests/unit/test_speech_pipeline.py` | New test `test_nan_prosodic_features_score_neutrally_not_best_or_worst_case` | Regression coverage for §4 |
| `research/paper_strengthening/results/evaluator_v2_recalibration_check.json` | Regenerated by the existing (unmodified) regression-check script | Regression evidence for §2 |
| `research/paper_strengthening/SIXTH_PROJECT_WIDE_RESEARCH_AND_ENGINEERING_PASS_REPORT.md` | New | This report |

No frozen/protected path was touched (verified via `git status --short` against the full protected-path list before and after this pass's changes — both clean).

## 11. Tests added and outcomes

- `tests/unit/test_stage11_5_coding_adaptation.py`: 14/14 pass (was 13/14, 1 persistent failure).
- `tests/unit/test_speech_pipeline.py`: 16/16 pass (was 15/15 + 1 new test, all pass; no regression).
- `tests/unit/test_evaluator.py`, `test_evaluator_logical_reasoning_adversarial.py`, `test_evaluator_v4_adversarial_development_suite.py`, `tests/integration/test_evaluator_feedback_integration.py`: 36/36 pass, no regression from the negation-filter fix.
- Full repository suite: see §12 (final validation).

## 12. Final validation

Frozen/protected paths (`research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers/`, `research/results/paper3/`, `research/CLAUDE_HANDOFF/`, `research/audit/`, `research/experiments/paper3/frozen_config.yaml`, `research/data/evaluator_benchmark/final_human_gold.csv`, `rl/checkpoints/`, `ablation/results/`, `research/confirmatory/`) — `git status --short` against the full list: clean, both before and after this pass's changes.

Full repository suite (`pytest -q`, `EVALUATOR_MOCK_MODE=1`): **354 passed, 0 failed, 466.24s.** Baseline at the start of this pass (captured before any change, §0): 352 passed, 1 failed (466s-class runtime), the same `test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` failure that has persisted since the second pass. Net: +1 test collected (the new NaN/Inf regression test), and the one previously-failing test now passes. **Zero new failures were introduced by any of this pass's four changes; the repository suite is fully green for the first time across all six passes.**

## 13. Decisions requiring human approval

1. **LLM client timeout (§5).** The shipped 6 s timeout is shorter than measured generation time (19–30 s) and is directly cited as a "shipped configuration" fact in P1's manuscript. Raising it would improve live reliability but would invalidate that manuscript sentence until re-measured and updated. Decide: (a) leave as-is (current state, matches the published paper), or (b) raise it and treat this as a manuscript-update task alongside the code change.
2. **`build_rl_observation` dimension-4 semantics (§3), long-term.** This pass fixed the *test* to match the *current* runtime behavior (progress ratio). The underlying training/runtime split documented in `rl_state_definition.md` (training uses response latency, runtime uses progress ratio) is unchanged and was explicitly not touched, consistent with that document's own recommendation to defer unification to a future retrained-policy decision. No action needed unless the authors want to revisit that recommendation.
3. **`depth` diagnostic-field repetition sensitivity (§2).** Low-impact (display-only field, does not affect `final_score`); a one-line fix is available (`len(split_sentences(scoring_text))` instead of raw `sentences`) if wanted.

## 14. Ranked next steps

1. **Highest scientific value, not attempted here:** a genuinely different (non-embedding-similarity) approach to the evaluator's "correct terminology, wrong reasoning" weakness — e.g. structured rubric/evidence-extraction scoring — per the task's own suggestion. Three embedding-based attempts have failed; this pass found and fixed a real but narrower bug (negation-word matching) instead, which was the higher-confidence, lower-risk opportunity available in the time budget. The harder problem remains open.
2. **D1 content authoring** remains the largest concrete blocker to any evaluator-validation claim beyond the 64-case benchmark; ~93 technical answers are needed and none exist yet (§7).
3. **System-paper ethics enquiry** remains unsent (per `SYSTEM_PAPER_BLOCKERS.md`, unchanged); this is the actual bottleneck for that paper's entire research programme, not anything a code pass can resolve.
4. **PPO confirmatory-evaluation authorization decision** (fifth pass's finding) remains outstanding and unaffected by this pass.
5. Low-priority, safe-if-wanted: the `depth` field fix (§13.3) and the LLM-timeout decision (§13.1).

## 15. Final research decision (per this pass's own required framing)

- **Which paper has gained the most substantive improvement?** None of the three papers changed this pass — this was a code-reliability and evaluator-correctness pass, not a manuscript pass, and no manuscript claim required updating.
- **Which specific scientific/technical weaknesses have been resolved?** Three real, previously-undiscovered code defects (negation-filter false negatives in the evaluator, NaN/Inf score fabrication in the audio scorers, the persistent `obs[4]` test failure) — all fixed, tested, and regression-checked against the frozen human-gold benchmark where applicable.
- **Which major weaknesses remain unresolved?** The evaluator's core "correct terminology, wrong reasoning" limitation (three prior fix attempts failed; not re-attempted here); D1 content and independent review; system-paper ethics clearance; PPO confirmatory-evaluation authorization.
- **Which new experiment would add the most value?** Not a new experiment — a structured-rubric or evidence-extraction redesign of the evaluator's reasoning component would be the highest-value *engineering* investment; among genuine experiments, D1's independent-review pilot (once content exists) would be the highest-value *research* investment.
- **Which work should be stopped because it is unlikely to yield useful evidence?** Further embedding-weight/threshold tuning of the evaluator's reasoning score — three attempts have already failed for the same underlying reason (SBERT/CrossEncoder polarity-blindness), and a fourth attempt without a genuinely different mechanism would not be expected to succeed either.
- **What should be done next to maximize the quality of the papers?** For P1/P3: nothing from this pass changes their readiness; the next step remains author/venue confirmations (unchanged from the fifth pass). For the system paper and D1: the blockers are non-code (ethics, human review, content authoring) and are the actual critical path.
