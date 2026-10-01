# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V8 (final)

**Status: complete protocol, NOT executed, NOT registered.** V1–V7 preserved unmodified, sample and design untouched. This version makes exactly one correction: the *interpretation* of the estimand and its bootstrap interval, which V4's "population mean" wording (carried forward by reference through V5–V7 without being re-examined) stated more strongly than the design actually supports. No sample change, no new hypothesis, no re-splitting — this is a precision-of-claim fix, requested explicitly as the final check before registration.

## 1. The estimand, restated without overclaiming

Every hypothesis in V7 (P1-i, P1-ii, P2's two components, the S2 descriptive report, M1) is now described as:

**the equal-weighted mean over the 31 confirmatory topics** of the relevant per-topic contrast (each topic's own mean of its per-question values, per V7 §2), **not** "the population mean over confirmatory topics" as V4 stated. This is not a change to what is computed — V7's estimator (§2) already computes exactly this quantity. It is a correction to what that quantity is *called* and, more importantly, what it licenses claiming.

## 2. Why "population mean" was the wrong description, and what the bootstrap CI actually characterizes

The 31 confirmatory topics are not a random or representative sample from any larger universe of technical-interview topics. They are a **fixed, disclosed, complete subset** of this project's own 37-topic eligible rubric bank — specifically, every eligible topic *except* the 6 assigned to development. Nothing was subsampled from a larger pool of eligible-but-unused topics; the 31 confirmatory topics are all of the non-development topics available, a full census of that subset, not a draw from it.

Given that, the topic-resampling bootstrap (V7 §2) is correctly understood as characterizing **topic-to-topic heterogeneity within this fixed, already-enumerated set of 31 topics** — a sensitivity measure for how much the equal-weighted average depends on which of these 31 topics' own behavior happens to be more or less typical, given that some topics contribute more questions than others. It is **not** a formal frequentist confidence interval for a population parameter defined over topics that could exist beyond this specific rubric bank, because the sampling step that would justify that reading — drawing topics at random from such a broader population — never happened. Reporting the interval is still useful and still statistically legitimate for the narrower claim; it is not evidence for the broader one.

## 3. Explicit scope boundary (the distinction requested)

- **Supported:** conclusions about the evaluator's behavior, averaged with equal weight, across **these 31 held-out confirmatory topics**, and — since those 31 are a complete, non-cherry-picked subset of the full eligible bank minus development — by direct extension, conclusions about **this project's own 122-question, 37-topic eligible rubric bank** as a whole.
- **Not supported:** any claim that these findings **generalize to technical topics outside this specific rubric bank** — other subject areas, other question authors, other institutions' interview-question sets, or "technical topics" as an open-ended category. The 37 topics were authored by this project's own team for its own question bank; they were never intended or sampled as a representative cross-section of technical-interview topics in general, and no part of this design supports treating them as one.

This boundary must be stated in the eventual manuscript's scope/limitations section in exactly these terms — as a stated boundary, not folded into softer language like "may not generalize" that would understate how specific the claim actually is.

## 4. Confirmation this does not affect registration readiness

Nothing about the sample (122 eligible / 26 development / 67 confirmatory / 29 excluded), the hypotheses (P1-i, P1-ii, P2, M1), the estimator or bootstrap mechanics (V7 §2), the construction rules, or the stopping rules changes. This document only fixes how the result will be *described* once it exists — which is exactly the kind of thing that must be settled before, not after, seeing confirmatory data, to prevent the write-up from claiming more than the design supports once real numbers are in hand.

## 5. Registration package (final)

- **Protocol file (frozen):** `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V8.md`
- **SHA-256:** see chat response — necessarily different from V7's, since this is a new, distinct file; V7's hash is not reused because V7 is superseded, not identical.
- **Proposed Git tag:** `prereg/D1-eval-synth/v1` (unchanged).
- **Run-manifest fields, exact commands, compute estimate, pre-execution integrity checks:** unchanged from V7 §6, with one addition — confirm the eventual results write-up states the scope boundary in §3 above verbatim or equivalently, before any claim about "generalization" appears in the manuscript.

Not executed: no item generated, no model called, no tag created, nothing committed or pushed.
