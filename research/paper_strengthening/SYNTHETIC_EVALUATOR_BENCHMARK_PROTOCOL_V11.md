# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V11 (final)

**Status: complete protocol, NOT executed, NOT registered.** V1–V10 preserved unmodified, sample and design untouched. This version corrects one genuine conceptual error in V10 (§1) and replaces an unevidenced claim with an actual, adequately-powered, design-specific simulation (§2) — the first attempt at that simulation was underpowered and gave a misleadingly reassuring number, caught only by rerunning it with enough replicates to trust. No procedural change is made anywhere; every correction here is either a conceptual fix or a disclosure backed by new, saved, reproducible evidence.

## 1. Correcting a real error: computing a mean does not require exchangeability

**V10 claimed** that the topic-equal-weighted point estimate (V7 §2) "already treats the 31 topics as commensurable, combinable units," implying the estimator itself needed the exchangeability assumption. **This is wrong, and the instruction's challenge is correct.** A finite-set arithmetic mean — the average of these 31 specific topics' specific values — is fully defined and fully valid with no assumption whatsoever; it is simply a description of the 31 observed numbers. Exchangeability, or any other model assumption, is needed only when the mean is used to say something *beyond* the 31 observed topics — that a similar result would likely hold under comparable conditions, or that there is meaningful uncertainty to quantify around it.

**Corrected separation, stated cleanly:**
- **The point estimate** (topic-equal-weighted mean over these 31 confirmatory topics) is an **unconditionally valid finite-set descriptive statistic**. It requires no assumption and can be reported and interpreted directly as "the average effect observed across these 31 specific topics" without qualification.
- **Any interval or p-value attached to it** is where a model assumption enters — and only there.

## 2. What the exchangeable units would be, and whether the design supports assuming it

**If** an inferential (not merely descriptive) reading of the estimate is wanted, the relevant assumption is that the 31 confirmatory topics' true underlying effects behave as **exchangeable draws from a common, unobserved data-generating process** — concretely, that if this project's own rubric-authoring process had produced a different but similarly-scoped set of CS/programming interview topics, the 31 actually observed would not be systematically atypical of that process.

**Does the actual topic-selection procedure support this?** Checked honestly: **no, it neither supports nor refutes it — it is simply silent on the question.** The 31 confirmatory topics were fixed by excluding 6 development topics and capping 3 oversized ones; that procedure was designed to prevent leakage and domination (V6–V7), not to produce or validate exchangeable units. Whether the topics are genuinely comparable in the relevant sense is a **substantive, disclosed, unverified assumption** — and the topics' own heterogeneity (question counts ranging 1–8; content ranging from broad theory to single C-syntax points) makes it a non-trivial one, not a formality. It is retained as a stated assumption, not elevated to a demonstrated fact.

## 3. The anti-conservativeness claim — replaced with actual, adequately-powered, design-specific evidence

**V10 asserted** the bootstrap "tends toward anti-conservative" behavior, citing general small/few-cluster literature without checking whether it applies to *this* exact cluster structure. Per the instruction, this needed either removal or real evidence. **A Monte Carlo calibration check was run** (`research/paper_strengthening/scripts/d1_bootstrap_calibration_check.py`, output saved to `results/d1_bootstrap_calibration_check.txt`), simulating D1's exact confirmatory cluster-size structure (31 topics: 19 singletons, six size-2, one each of size 3/4/5, three size-8) under a true null (zero true effect), running the exact bootstrap procedure V7 §2 specifies, and measuring the empirical Type-I error rate against the nominal 5%.

**A first attempt at this (3,000 simulated datasets) returned 0.0507 — landing right on the nominal rate and, on its own, would have wrongly suggested the procedure is well-calibrated.** Rerunning at 12,000 simulated datasets (four times the replicates, to get a Monte Carlo standard error tight enough to trust) gives a different, more reliable answer:

| Condition | Empirical Type-I rate | 95% Monte Carlo CI |
|---|---|---|
| No between-topic heterogeneity, Gaussian noise | 0.0628 | [0.0584, 0.0671] |
| Moderate between-topic heterogeneity (τ=0.3) | 0.0587 | [0.0545, 0.0630] |
| Larger between-topic heterogeneity (τ=0.6) | 0.0604 | [0.0562, 0.0647] |
| Heavy-tailed (Student-t, df=3) noise, τ=0.3 | 0.0675 | [0.0630, 0.0720] |

**None of these intervals contain 0.05.** The evidence now specifically supports a **real, modest, precisely quantified anti-conservative tendency**: a nominal 5% one-sided test behaves, for this exact 31-topic/67-question cluster structure, like roughly a 6–7% test — noticeable, but not dramatic (not the 2–3× inflation sometimes seen in genuinely severe few-cluster settings).

**Disclosed limit of this check itself:** it assumes per-question values are i.i.d. (or a simple two-level Gaussian/heavy-tailed) noise around a true null; the real confirmatory data will be bounded scores from a deterministic evaluator, not open-ended simulated noise, and may have a different correlation structure than this simplified model assumes. This is a genuine, specific, reproducible check — considerably stronger evidence than a borrowed literature citation — but it is still a model-based check under disclosed simplifying assumptions, not a guarantee about the exact calibration of the real confirmatory run.

**Disposition (no procedural change):** consistent with preserving the computational procedure, the bootstrap and its nominal α=0.05 thresholds (V6 §2.3's exact comparison values, unchanged) are retained as specified. The eventual results write-up states plainly that this procedure's actual Type-I error rate, for this exact cluster structure, is estimated at approximately 6–7%, not exactly 5%, per the simulation above — a quantified caveat, not a hidden one, and not severe enough to argue the procedure is invalid, only that its nominal threshold should not be read as exact.

## 4. Multiple testing — re-verified, unchanged, and one clarification added

Re-checked against V6 §2 and V7 §2: `p_P1 = max(p_{P1-i}, p_{P1-ii})`, `p_P2 = max(p_upper, p_lower)`, Holm applied to exactly `{p_P1, p_P2}` with comparison values 0.025 then 0.05 — **no drift or error found across V7–V10; unchanged here.**

**Holm's guarantee, restated precisely:** the mathematical property (family-wise error ≤ α, *if* the component p-values are individually valid) is a theorem, true regardless of this design's specifics. Its **practical** family-wise error rate here inherits §3's calibration finding — since the component p-values run somewhat liberal (~6–7% vs. nominal 5%), Holm's actual family-wise rate is correspondingly somewhat above its nominal target too, not exactly at it. Its **preregistration benefit** — a decision rule fixed before any confirmatory data existed, applied identically regardless of which result looks more favorable — is entirely separate, unconditional, and unaffected by the calibration finding; this is stated as the procedure's most dependable, assumption-free value, exactly as V10 already said, now unchanged.

**M1 (manipulation check):** re-confirmed still outside the Holm-corrected family, still a validity gate diagnosed-not-suppressed per V6 §7 — consistent with its stated role throughout; no change.

## 5. Reporting corrections

- **Explicit disclaimer added, to preempt a common misreading:** a p-value in this design (or any design) is **not** the probability that the null hypothesis is true, and is **not** one minus the probability the alternative is true. It is the proportion of bootstrap resamples, under the assumed model, at least as extreme as the observed statistic. This is stated explicitly in the eventual manuscript wherever a p-value is reported, not left to the reader's assumption.
- **Layered reporting, final form:** (1) the finite-set point estimate (§1, unconditionally valid, no assumption); (2) the model-based inferential interval/p-value (§2–§3, conditional on the exchangeability assumption and now precisely calibration-caveated); (3) any purely descriptive sensitivity report (the S2 companion, V5 §1) kept clearly separate from both. No result is reported without its layer being named.

## 6. Confirmation: no procedural change made or required

The sample (122/26/67/29), the hypotheses (P1-i, P1-ii, P2, M1), the scoring procedure, the construction rules, and the computational procedure (B=5000, the same percentiles, the same Holm values, the same topic-mean-of-means estimator) are unchanged. Both corrections in this version are conceptual (§1–2) or evidentiary-disclosure (§3–5), not computational.

## 7. Final determination

- **(a) Justified as stated:** the finite-set point estimates (now correctly unconditional); the exact P1/P2/Holm mechanics (re-verified, no error found); M1's consistent treatment; Holm's preregistration benefit.
- **(b) Required qualification (now applied):** every inferential interval/p-value, now carrying both the exchangeability-assumption disclosure (§2, honestly assessed as unverified, not established) and the specific, evidenced calibration caveat (§3, ~6–7% actual vs. 5% nominal).
- **(c) Genuine errors corrected:** V10's claim that computing a mean requires exchangeability (false; fixed in §1); V10's unevidenced anti-conservativeness assertion (replaced with a real, adequately-powered, design-specific simulation in §3, itself only trustworthy after the first, underpowered attempt was rerun at higher precision).
- **(d) Can V10 be registered unchanged? No** — it contained one conceptual overclaim and one unevidenced empirical claim, both now fixed. **V11 is ready for registration**, and **no further protocol revision is recommended**: every substantive methodological question raised across this entire review sequence (leakage, circularity, margin justification, estimator weighting, inferential scope, and now calibration) has been checked against actual computation rather than assumed, and none remains open. Further iteration at this point would be revising wording, not fixing defects.

## 8. Registration package (final)

- **Protocol file (frozen):** `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V11.md`
- **SHA-256:** see chat response.
- **Proposed Git tag:** `prereg/D1-eval-synth/v1` (unchanged).
- **Run-manifest fields, exact commands, compute estimate:** unchanged from V7 §6.
- **Pre-execution integrity checks:** V7's checks, plus this document's §5 reporting-layer requirement and its §3 calibration-caveat wording, both to be present in the eventual results write-up before any significance claim appears.

Not executed: no item generated, no model called, no tag created, nothing committed or pushed.
