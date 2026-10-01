# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V14 (final, registration-ready)

**Status: complete protocol, NOT executed, NOT registered.** V1–V13 preserved unmodified. Sample, question split, hypotheses, answer construction, evaluator, estimator, bootstrap procedure, and numerical thresholds are **unchanged from V13** (unchanged since V7 for the core design). This version makes one substantive addition — approved by the user as the final reporting direction — and no other change: D1 is finalized as a **prespecified descriptive benchmark**, with the topic-equal-weighted estimates as the primary result and every bootstrap-based analysis (intervals, tail-fraction p-values, and the P1/P2/M1 decision rules built on them) reported as **secondary and explicitly qualified**, rather than as verified confirmatory statistical significance. This is a reporting-convention finalization, not a redesign: nothing about what is computed changes, only the explicit, unambiguous statement of what each computed quantity is entitled to claim.

## 1. Estimand and primary result — unchanged, restated as the finalized primary

**Primary result (unconditional, assumption-free):** the topic-equal-weighted mean of the relevant per-question quantity (e.g., `final_score(C1) - final_score(C4)` for P1-i; the interaction contrast for P1-ii; the coverage difference for P2), computed by taking each of the 31 confirmatory topics' own mean first and then averaging those 31 topic-means with equal weight (V7 §2 estimator, unchanged). This is a finite-set descriptive statistic over exactly the 67 confirmatory questions / 31 confirmatory topics actually used. It requires no statistical model, no exchangeability assumption, and no claim about topics or questions outside this set. **This — not any p-value or interval — is the benchmark's primary reported result**, per the approved direction.

**Scope, restated for clarity:** results describe the 67 confirmatory questions across 31 confirmatory topics only. The 26 development questions (6 topics) were used solely for piloting the construction rules and are not part of any reported estimate. The 29 cap-excluded questions play no role at all (V6–V9). No claim extends to the full 122-question/37-topic eligible bank, nor to CS/programming topics outside the rubric bank, per V9 §1's correction (unchanged).

## 2. Secondary analyses — the bootstrap layer, explicitly demoted and scoped

All bootstrap-based quantities (the percentile-bootstrap confidence intervals; the tail-fraction p-values for P1-i, P1-ii, P2's two components, and M1; and anything derived from Holm's step-down) are, per the approved direction, **secondary analyses**, reported alongside but never in place of §1's primary estimate, and never described as establishing verified statistical significance. This is not a new computation or a new procedure — B=5000 resamples, the same percentiles, the same 0.025/0.05 Holm comparison values (V6 §2.3) are unchanged — it is a finalized statement of evidentiary status:

- **What secondary status means in practice for the manuscript:** a bootstrap CI or p-value is reported with its exact value and its exact, disclosed limitations (below) in the same breath — never as a bare number, and never headlined ahead of the primary estimate.
- **Why secondary, not primary:** §3 below lists the specific, unresolved calibration questions (carried forward from V11–V13) that stop these quantities from being reported as fully validated inference. None of them is disqualifying — a disclosed, secondary, exploratory bootstrap analysis is legitimate and informative — but none of them currently supports a confirmatory-grade significance claim either.

## 3. Mechanical decision-rule outcomes vs. statistically validated significance — the distinction finalized

**The prespecified P1, P2, and M1 criteria (V6 §2, unchanged) remain exactly as designed:** P1 rejects its union null when `max(p_{P1-i}, p_{P1-ii})` clears the relevant Holm threshold; P2 rejects when `max(p_upper, p_lower)` clears its threshold; M1 is checked and reported unconditionally as a validity gate (diagnosed, not suppressed, per V6 §7). These are **mechanical decision rules**: fixed before any confirmatory data existed, applied identically and automatically regardless of which outcome looks more favorable. That pre-registration property is real, valuable, and unconditional — it protects against post-hoc cherry-picking of which claim to foreground, independent of anything else in this document.

**What firing (or not firing) that decision rule does *not*, by itself, establish:** that the observed result reflects a statistically validated effect at the nominal error rate the threshold names. Per V12–V13's audits: (a) the ~6–7% Type-I rate found by simulation describes a single component test, at the 0.05 threshold only, under one joint-null configuration, not the compound P1/P2 tests generally, and not the 0.025 threshold Holm also uses (V13 §0); (b) the compound (IUT) bound is mathematically valid at that one simulated configuration but its extension across the full union null — including the case where one component is null and the other strongly alternative — rests on an unverified stability assumption (V13 §1); (c) the Holm procedure's actual family-wise error rate is not quantified (V13 §3); (d) whether real D1 topics satisfy the exchangeability assumption the whole inferential layer rests on is itself disclosed and unverified (V11 §2, unchanged).

**Finalized reporting convention:** the manuscript states, for each of P1/P2/M1, (i) the primary descriptive estimate (§1); (ii) whether the prespecified decision rule fired, explicitly labeled *"prespecified decision-rule outcome"*, not *"statistically significant result"*; and (iii) the underlying secondary bootstrap CI/p-value with the exact caveats of §2–3 attached. A decision rule firing is reported as exactly what it is — a fixed, disclosed, non-cherry-picked rule crossing its threshold — and is not, by itself, elevated to a claim of verified significance beyond that.

## 4. Calibration evidence — retained exactly, with its conditions and limitations, no extension

The Monte Carlo calibration results (`d1_bootstrap_calibration_check.py`/`.txt`, unchanged) are retained as reported in V13 §0–2, with no addition or extension:

```
tau=0.0  normal noise : Type-I rate=0.0628  95% MC CI=[0.0584, 0.0671]
tau=0.3  normal noise : Type-I rate=0.0587  95% MC CI=[0.0545, 0.0630]
tau=0.6  normal noise : Type-I rate=0.0604  95% MC CI=[0.0562, 0.0647]
tau=0.3 heavy-tailed(t,df=3): Type-I rate=0.0675  95% MC CI=[0.0630, 0.0720]
```

These describe a single component test, at the 0.05 threshold, under an idealized exchangeability-imposed simulation matching D1's exact cluster structure — nothing more. No claim is made, in either direction, about how real D1 calibration compares to these figures (V13 §2, "floor" language removed and not reinstated). Calibration at the 0.025 threshold remains unchecked (V13 §0). No new simulation was run for this version; none was needed, since nothing here changes what was computed, only how the results are classified in the write-up.

## 5. IUT bounds and Holm — no remaining overclaim found

**Re-checked against V13 §1 and §3, specifically for any residual overclaim, per the instruction.** None found requiring further correction: V13 already (a) states the `P(A∩B) ≤ min(P(A),P(B))` bound is verified only at the single simulated joint-null configuration, not across the full union null; (b) withdraws the "generally strictly lower" language and replaces it with "approached, not beaten, in the ordinary partial-null case"; (c) leaves Holm's numerical family-wise rate fully unquantified rather than qualitatively bounded. This version adds no new mathematical claim about either the IUT bound or Holm — it only reclassifies these already-correctly-scoped quantities as secondary analyses (§2) and separates their mechanical decision-rule role from any significance claim (§3).

## 6. Confirmation: no change to sample, hypotheses, construction rules, or computational mechanics

Checked explicitly. The 122/26/67/29 sample, the P1-i/P1-ii/P2/M1 hypotheses, the nine construction categories, and the computational procedure (B=5000, the percentile bootstrap, the 0.025/0.05 Holm comparison values, the topic-mean-of-means estimator) are unchanged from V7 through V13 and remain unchanged here. No new hypothesis, test, or procedure is introduced. The only change in this version is the explicit, finalized reporting convention in §1–3: primary descriptive estimate first, secondary bootstrap analyses second, and mechanical decision-rule outcomes kept distinct from statistically validated significance claims. Because this is a reporting/classification finalization rather than a change to sample, hypotheses, construction, or procedure, it does not trigger the instruction's stop-for-approval condition — no genuine methodological change was found necessary, and none is made.

## 7. Final determination

- **V13 was not itself defective** — its mathematical corrections (the IUT bound's scope, the withdrawn "floor" claim, the 0.025 gap) stand and are carried forward unchanged. **V14 is required, not for a defect, but because the user's approved final direction — descriptive-primary, bootstrap-secondary, decision-rule-outcomes distinguished from validated significance — was not yet stated explicitly and unambiguously anywhere in V13.** That is a substantive addition to what the protocol commits to reporting, not a cosmetic wording pass, so a new version is warranted per the standing "only version for substantive corrections" rule.
- **V14 is ready for registration.** The estimand, primary/secondary reporting split, decision-rule-vs-significance distinction, scope, and limitations are now stated unambiguously in one place, consistent with every prior version's verified mathematical content.
- **No further revision is recommended.** Every substantive methodological and reporting question raised across this entire review sequence — leakage, circularity, margin justification, estimator weighting, inferential scope, calibration evidence and its limits, IUT/Holm bound precision, and now primary/secondary reporting status — has been checked against actual computation or explicit statement, not assumed. Further iteration at this point would be wording only.

## 8. Consistency check — protocol references, commands, manifest fields, calibration artifacts

Verified directly against the files on disk:
- **Calibration script and output:** `research/paper_strengthening/scripts/d1_bootstrap_calibration_check.py` and `results/d1_bootstrap_calibration_check.txt` — both unchanged since V12/V13, both still match the numbers quoted in §4 above (re-verified, not re-run).
- **Run-manifest fields, exact commands, compute estimate:** unchanged from V7 §6; nothing in this version's reporting-convention addition touches execution mechanics, so no manifest field needed updating.
- **Cross-references:** V11's exchangeability disclosure, V13's §0/§1/§2/§3 mathematical corrections, and this version's §1–3 reporting convention are mutually consistent — no contradiction found between any of them on re-reading all four documents together.

## 9. Registration package (final)

- **Protocol file (frozen):** `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V14.md`
- **SHA-256:** see chat response.
- **Proposed Git tag:** `prereg/D1-eval-synth/v1` (unchanged).
- **Calibration evidence:** `research/paper_strengthening/scripts/d1_bootstrap_calibration_check.py` and `results/d1_bootstrap_calibration_check.txt`, unchanged, reverified consistent with §4.
- **Run-manifest fields, exact commands, compute estimate:** unchanged from V7 §6.
- **Pre-execution integrity checks:** V7's checks, plus confirmation that the eventual results write-up follows this document's §1–3 reporting order exactly: primary descriptive estimate first, decision-rule outcomes labeled as such (not as significance claims), secondary bootstrap analyses last with their full caveats, no 0.025 calibration claim, no calibration "floor" claim, and the IUT bound stated as approached-not-beaten.

Not executed: no item generated, no model called, no tag created, nothing committed or pushed.
