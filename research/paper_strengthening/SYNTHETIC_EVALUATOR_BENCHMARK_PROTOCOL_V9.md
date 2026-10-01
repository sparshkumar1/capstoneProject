# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V9 (final)

**Status: complete protocol, NOT executed, NOT registered.** V1–V8 preserved unmodified, sample and design untouched. Both corrections in this version are interpretive/documentation fixes, not procedural changes — confirmed explicitly in §3 below, per the instruction that a redesign is warranted only if a genuine statistical inconsistency makes it unavoidable, and neither correction here rises to that.

## 1. §3 corrected — the extension claim to the full eligible bank is removed

V8 §3 said confirmatory findings extend "by direct extension" to "this project's own 122-question, 37-topic eligible rubric bank as a whole." That is an overclaim, for a precise reason: the eligible bank splits into three groups with entirely different roles, and only one of them is actually measured.

- **Confirmatory set — 67 questions, 31 topics.** This is what is scored under the frozen construction rules and what every statistic (P1-i, P1-ii, P2, M1, the S2 descriptive report) is computed over. This is the only set any conclusion is drawn from.
- **Development set — 26 questions, 6 topics.** Used only to pilot and correct category-construction templates before anything was frozen (V4 §5 / V6 §1). These questions are never scored under the final confirmatory procedure and are never part of any reported estimate. If any descriptive read of development items occurs during piloting, it stays a piloting record, not a result, and is never merged into or averaged with confirmatory numbers.
- **Excluded set — 29 questions.** Given no role at all — not scored, not piloted on, not read during template construction (V6 §1's fix). They exist in the record solely as a disclosed audit trail of what was set aside from the three oversized topics and why.

**Corrected scope statement (replaces V8 §3's extension claim):** conclusions from this benchmark apply to the **67 confirmatory questions across the 31 confirmatory topics, specifically and only** — not to the development questions (never scored), not to the excluded questions (never used), and not, by extension or otherwise, to "the entire eligible bank" as an undifferentiated whole. The eligible bank is the *sampling frame* this design drew from; it is not itself the object the results describe.

## 2. Bootstrap CIs and hypothesis-test p-values — extending V8's caveat to the whole testing apparatus, not just the CI

V8 §2 correctly reinterpreted the bootstrap **confidence interval** as a topic-to-topic heterogeneity/sensitivity measure within the fixed 31-topic set, not a formal interval over a broader population of topics — because the 31 topics are a complete, disclosed census of a defined subset, not a random draw from anything larger. That reasoning was not fully carried through to the **hypothesis tests themselves** (P1-i, P1-ii, P2, M1: their null/alternative hypotheses, the α=0.05 rejection rule, the Holm procedure, V6 §2). Standard null-hypothesis significance testing — p-values as long-run frequencies, Type-I error rates held at a nominal level — is defined relative to a repeated-sampling process from a population. A fixed, complete census of 31 topics does not supply that process, so the same distinction applies to the p-values and "reject H0" decisions as applies to the CI:

- **What the testing procedure legitimately provides:** a **pre-specified, disclosed decision rule** — fixed before any confirmatory score existed, applied mechanically and identically to every hypothesis, immune to post-hoc cherry-picking of which comparisons to highlight. The percentile-bootstrap "p-value" is a resampling-based **sensitivity criterion**: it tells you whether an observed effect looks consistent across resamples of these 31 topics' own heterogeneity, or whether it is fragile — driven by one or two topics that happen to dominate whenever they're drawn. That is a genuinely useful, honest thing to report.
- **What it does not provide:** a formal guarantee that, over hypothetical repeated draws of a different set of technical topics from some broader population, a true null effect would be incorrectly rejected no more than 5% of the time. That guarantee requires the topics to have been randomly sampled from such a population, which they were not.

**Reporting convention adopted (no procedural change):** the exact same numbers are computed and reported exactly as V6/V7 specify — same percentiles, same α=0.05 threshold, same Holm step-down comparisons (0.025 then 0.05). Only the language describing what a "rejection" means changes: results are described as *"the pre-specified decision rule was met/not met, indicating the effect is/is not robust to topic-level resampling within this confirmatory set,"* not as *"the null hypothesis is rejected at the 5% significance level"* in the population-inference sense that phrase ordinarily carries. This is a labeling and description correction, not a change to any computed value or comparison threshold.

## 3. Confirmation that no procedural redesign was required

Checked explicitly, as instructed: neither correction above changes the sample (122 eligible / 26 dev / 67 confirmatory / 29 excluded, unchanged), the hypotheses (P1-i, P1-ii, P2, M1, unchanged), the answer construction rules (C1–C7/C5a/C5b, unchanged), the estimator (V7 §2's topic-equal-weighted mean-of-means, unchanged), or the computational procedure (B=5000, the same percentiles, the same Holm comparison values, unchanged). Both corrections are descriptions of what the already-computed numbers mean, not changes to how they are computed. No genuine statistical inconsistency requiring a stop-and-redesign was found.

## 4. Manuscript scope check (performed in this pass)

`FINAL_MANUSCRIPT_EVIDENCE_V2.md` — the current manuscript draft — was checked for any language about D1, the eligible bank, or confirmatory/development topic counts. **None found; the manuscript predates D1's design entirely and makes no claims that could conflict with §1–2 above.** This is noted so the obligation is not lost: when D1's results are eventually written into the manuscript, the Results and Methodology sections must state the scope exactly as §1 defines it (67 questions / 31 topics, not "the eligible bank") and describe significance findings using §2's decision-rule framing, not population-inference language.

## 5. Registration package (final)

- **Protocol file (frozen):** `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V9.md`
- **SHA-256:** see chat response — a new value, since this is a new file superseding V8.
- **Proposed Git tag:** `prereg/D1-eval-synth/v1` (unchanged).
- **Run-manifest fields, exact commands, compute estimate, pre-execution integrity checks:** unchanged from V7 §6 / V8 §5, with one addition — confirm the eventual results write-up uses §1's exact three-way scope distinction and §2's decision-rule (not population-significance) framing before any claim about the benchmark's findings appears in the manuscript.

Not executed: no item generated, no model called, no tag created, nothing committed or pushed.
