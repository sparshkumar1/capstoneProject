# Evaluator V4 — Validation Report

Fourth Research Improvement Pass, items 3.1-3.4. **No scoring code was changed in this pass** (`services/evaluator/app.py` and `services/evaluator/assets/rubrics.json` are unmodified relative to the third pass's final state) — this pass's evaluator work is audit, a new adversarial development suite, and one new fix hypothesis that was tested and refuted *before* implementation, so there is nothing to revert.

## 1. Audit of previously-fixed defects (item 3.1) — all confirmed still fixed

Re-inspected `services/evaluator/app.py` directly (not assumed from the prior report):

- **Mistake-vector overflow bug** (second/third pass fix): `mistake_penalty()` now checks `_extra_mistake_texts()` beyond the FAISS-indexed count; `_detect_misconceptions()` does the same. Confirmed present at lines implementing `_extra_mistake_texts`/`_rubric_mistake_texts` and their call sites in both functions.
- **High-S2/weak-reasoning penalty tier** (second pass): confirmed present in `mistake_penalty()`, third `elif` branch (`reasoning_score < 0.50 and s2_score >= 0.60`).
- **Repeated-sentence deduplication** (second pass): confirmed `dedupe_repeated_sentences()` is called once at the top of `evaluate()` into a separate `scoring_text` variable, with `candidate_text`/`candidate_answer`/`candidate_claims` left verbatim. Re-verified it generalizes to a previously-untested question (Kadane's, qid=2) — see suite case 8 below.
- **qid=1's single kept rubric-text addition** ("returning the same index twice is invalid"): present, 4 entries where 3 existed before; safe (does not collide with any tested correct answer).
- **qid=4's two reverted entries**: confirmed absent (`rubrics.json`'s qid=4 `common_mistakes_addressed` still has exactly its original 3 entries) — the revert was not accidentally lost or reapplied.

No index mismatches, missing rubric entries, or newly-introduced false positives were found in this audit pass.

## 2. New 10-case adversarial development suite (item 3.2)

`tests/unit/test_evaluator_v4_adversarial_development_suite.py` — explicitly separate from the human-gold benchmark, the third pass's 7-case set, and all confirmatory/held-out data. Each case documents (in its own docstring, not only here): failure mode, relevant scoring component, expected behavior, and diagnostic rationale. All 10 pass, characterizing real, verified current behavior — summary:

| # | Case | Result | Finding |
|---|---|---|---|
| 1 | Correct terminology, incorrect reasoning | "Good"/"Average" | Known limitation (unchanged from 3rd pass), pinned not silently accepted |
| 2 | Correct conclusion, invalid reasoning | "Poor", S2=0.0 | Correctly caught — but via concept-coverage collapse, not explicit mechanism verification |
| 3 | Incorrect complexity analysis | penalty > 0, "Poor"/"Average" | The 2nd-pass penalty tier catches this |
| 4 | Contradictory statements | penalty > 0, "Poor" | Caught |
| 5 | Correct answer + irrelevant jargon | "Good"/"Excellent", no penalty | **No defect** — jargon neither inflates nor deflates a genuinely correct answer |
| 6 | Near-miss (high vocab overlap, wrong mechanism) | "Poor" | Correctly caught despite heavy lexical overlap |
| 7 | Correct answer, alternative vocabulary (low/high vs left/right) | penalty=0, concept_coverage ≤0.60 | **New, real finding**: a genuine vocabulary-level (not just sentence-structure-level) paraphrase sensitivity — under-credited, not penalized |
| 8 | Repetition (new question, Kadane's) | identical score once vs twice | Confirms the dedup fix generalizes beyond the two questions it was built/tested on |
| 9 | Rubric mistake-text collision (regression guard) | penalty=0.0, "Good"/"Average" | Permanent regression test for the third pass's reverted false-positive |
| 10 | Partial answer, partial credit | "Average"/"Good", 0.20 < score < 0.75 | **New, real finding**: correctly lands in the partial-credit band, but the high-S2/weak-R penalty tier (built to catch misconceptions) also fires on this merely-*incomplete* answer — a disclosed side effect, not a new defect from this pass |

## 3. New fix hypothesis: tested and refuted before implementation (item 3.3)

**Hypothesis:** the qid=4 mistake-text false-positive (third pass) could be fixed by a *relative* check — flag a mistake match only if the candidate sentence is *more* similar to the mistake description than to the rubric's own reference answer, rather than using an absolute similarity threshold alone.

**Test (no code changed to run this — a direct probe against the already-loaded SBERT model):** for the same false-positive pair used in the third pass (a correct "different speeds" answer vs. the "same speed cannot detect a cycle" mistake text), computed both similarities directly.

| | sim-to-mistake | sim-to-reference | mistake > reference? |
|---|---|---|---|
| Correct answer (different speeds) | 0.759 | 0.725 | **True** (would still be flagged) |
| Wrong answer (same speed), sentence 1 | 0.525 | 0.609 | False (would NOT be flagged) |
| Wrong answer (same speed), sentence 2 | 0.597 | 0.621 | False (would NOT be flagged) |

**Result: refuted, backwards.** By this relative rule, the CORRECT answer would still be flagged (mistake-similarity exceeds reference-similarity), while the WRONG answer would NOT be flagged (its similarity to the correct reference is, if anything, slightly higher than its similarity to the mistake description) — the opposite of the intended effect. **Not implemented.** This is the third distinct approach (after third-pass's sentence-level cross-encoder rescoring and absolute-threshold rubric-text extension) to fail for the same underlying reason: the embedding space used throughout this evaluator does not reliably separate "on-topic and correct" from "on-topic and describing the negation/inversion of correct," regardless of which existing signal (cross-encoder, absolute SBERT threshold, relative SBERT threshold) is used to try to detect it.

**Per item 3.3's own instruction ("if no safe general solution is supported, retain the limitation and document it"), no new fix was implemented this pass.**

## 4. Human-gold benchmark regression check (secondary, unchanged)

No evaluator scoring code changed in this pass, so the human-gold correlation is unchanged from the third pass's measurement: **ρ = 0.3787** (`research/paper_strengthening/results/evaluator_v2_recalibration_check.json`, point estimate, question-clustered bootstrap CI [0.307, 0.565], B=2000, seed 20260921) — re-cited here, not re-run, since nothing that would affect it changed. Original (pre-any-fix) value 0.3812 remains the historical reference; both are within each other's CI, consistent with "no meaningful correlation change" as previously and honestly reported (not re-framed as an improvement here).

## 5. Score distribution / affected-case summary

Since no scoring code changed in this pass: **zero cases changed score** relative to the third pass's final evaluator state. All "findings" in §2 are new *characterizations* of already-existing behavior (case 7, case 10), not changes caused by this pass.

## 6. Runtime / latency

Not separately re-measured this pass (no code path affecting evaluator latency changed). The 10-case adversarial suite itself runs in ~13.7s real-model wall time (10 cases, non-mock SBERT+FAISS+CrossEncoder, cold-model-already-loaded via the module-scoped fixture) — reported as a data point on the suite's own cost, not a claim about production per-request latency, which was not measured here.

## Conclusion

Evaluator V4's audit found all previously-fixed defects intact and confirmed via a new, independent test (case 8, a different question than either fix was built against). A third attempted general mitigation for the logical-reasoning weakness was tested and refuted before being implemented — a negative result recorded, not a wasted one, since it further narrows what *won't* work. Two new, real, disclosed findings emerged from the 10-case suite (vocabulary-level paraphrase sensitivity; a possible over-broad side effect of the second-pass misconception penalty on merely-incomplete answers) that were not previously characterized. No regression was introduced; the human-gold benchmark and full evaluator test suite (see final validation) are unaffected.
