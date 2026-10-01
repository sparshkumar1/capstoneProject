# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V12 (final)

**Status: complete protocol, NOT executed, NOT registered.** V1–V11 preserved unmodified, sample and design untouched. This version fixes one concrete reproducibility defect (§0 — the saved script did not actually reproduce V11's quoted numbers) and one real scope overreach (§1 — V11 implicitly extended a single-test calibration finding to the compound and family-wise procedures without ever checking those). Both are corrections to what was actually verified, not to the design.

## 0. A provenance defect, found and fixed: the saved script did not reproduce V11's numbers

**Checked directly, as instructed.** V11 quoted calibration rates (0.0628, 0.0587, 0.0604, 0.0675) that were computed in an ad hoc, unsaved command with `N_OUTER=12000`. The script actually saved to the repository, `d1_bootstrap_calibration_check.py`, still had `N_OUTER=3000` hardcoded — the underpowered configuration whose *first* run had returned a misleadingly reassuring 0.0507. Running the saved script as it existed would **not** have reproduced V11's numbers. This is exactly the kind of "cited number doesn't match the stored artifact" defect this project has been strict about catching everywhere else, and it had crept into this project's own output. **Fixed:** the script now hardcodes `N_OUTER=12000` and the seeds actually used (`2026, 2036, 2046, 31415`), with the discrepancy documented in-line rather than silently corrected away, and the output file (`results/d1_bootstrap_calibration_check.txt`) was regenerated and now matches exactly:

```
tau=0.0  normal noise : Type-I rate=0.0628  95% MC CI=[0.0584, 0.0671]
tau=0.3  normal noise : Type-I rate=0.0587  95% MC CI=[0.0545, 0.0630]
tau=0.6  normal noise : Type-I rate=0.0604  95% MC CI=[0.0562, 0.0647]
tau=0.3 heavy-tailed(t,df=3): Type-I rate=0.0675  95% MC CI=[0.0630, 0.0720]
```

These are now verified, reproducible from the saved script exactly as committed to this workspace.

## 1. What the simulation actually establishes — corrected scope

**Checked precisely, per the instruction's (a)/(b)/(c) breakdown.** The simulation's `one_sim` function computes a single set of simulated per-question values, forms topic means, bootstraps, and checks **one** one-sided rejection rule (`p ≤ 0.05` for a single null boundary at zero). It does not simulate P1-ii at all, does not compute a max-p compound for P1, does not simulate P2's two one-sided components jointly, and does not run the Holm step-down across {P1, P2}. **The simulation establishes calibration for (a) an individual one-sided test only** — the shared mechanics underlying each of P1-i, P1-ii, and each of P2's two TOST components taken alone. **It says nothing directly about (b) the compound P1/P2 tests or (c) the full Holm-corrected family**, and V11's statement that "Holm's actual family-wise rate is correspondingly somewhat above its nominal target too" was not earned by this evidence — it extrapolated an individual-test finding onto the compound and family-wise procedures without checking either. That sentence is withdrawn here, not softened.

**What can be said about the compound tests without further simulation, and is mathematically certain, not approximate:** for any two events A and B, `P(A ∩ B) ≤ min(P(A), P(B))`, regardless of how A and B are correlated. Since P1's compound rejection requires *both* `p_{P1-i} ≤ threshold` **and** `p_{P1-ii} ≤ threshold` (an intersection, by the max-p construction in V6 §2.1), the compound P1's actual Type-I error rate is bounded above by the smaller of its two components' individual rates — i.e., **at most approximately 6–7%, and in general strictly lower**, since equality only holds in the degenerate case of perfect positive correlation between the two components. The same logic bounds P2's compound (TOST) rate above by its own components' individual rates. **This is a valid, rigorous statement obtainable from probability theory alone; it does not require, and this document does not claim, a simulated exact value for the compound rate.**

**What cannot yet be said, and is left explicitly open:** the exact family-wise error rate for the Holm procedure applied to `{p_P1, p_P2}` depends on the joint behavior of two compound p-values that have not been directly simulated. Holm's own guarantee (FWER ≤ α) requires each input p-value to be individually valid; §0's finding that the underlying single-test mechanic runs somewhat liberal means the compound p-values feeding Holm are themselves not guaranteed exactly valid, but by the bound above they are *at least as good as, and generally better than*, the individual-component finding suggests. **The precise family-wise rate is not quantified here and should not be quoted as a number** — only bounded, qualitatively, by the reasoning above.

## 2. Does the simulated data-generating process represent the assumed exchangeable-topic model — or just test the procedure under an idealized best case?

**Checked directly, as instructed.** The simulation's topic effects were drawn i.i.d. from `N(0, τ)` — this is not an approximation of exchangeability, it is exchangeability **imposed by construction**: the simulated topics are, by design, exactly the kind of exchangeable draws §2 of V10/V11 discusses as an assumption for real D1 topics. This means the simulation is a **best-case check**: it asks "even when the exchangeability assumption holds exactly, does the bootstrap procedure itself introduce miscalibration purely from the small, size-imbalanced cluster count (31 topics, 19 singletons)?" The answer (§0's rates) is yes, modestly.

**What this does not establish:** whether real D1 confirmatory topics actually behave as exchangeable draws from a common process. That remains the disclosed, unverified, substantive assumption from V11 §2 — content-heterogeneous topics (a single C-syntax question vs. broad theory) may violate exchangeability in ways this idealized simulation cannot detect, because the simulation never modeled non-exchangeable topics to begin with. **If real topics are less exchangeable than this simulation's construction assumes, the true calibration on real D1 data could plausibly be worse than §0's numbers, not better** — those numbers are a floor on the concern, from cluster-size effects alone, not a ceiling that also accounts for possible exchangeability violations. This distinction — evidence conditional on the simulation's own assumptions vs. evidence about actual D1 data — is stated here explicitly, replacing any implication in V11 that the simulation validated real-data calibration.

## 3. Exact, supported replacement statement (replaces any "the real benchmark has ~6–7% Type-I error" reading)

**The precise, defensible claim is:** *under a Monte Carlo simulation that imposes exact topic-level exchangeability by construction and matches D1's exact confirmatory cluster-size structure (31 topics; 19 singletons; six pairs; one each of size 3, 4, 5; three size-8), a single one-sided percentile-bootstrap test of the kind used for each of P1-i, P1-ii, and each TOST component individually shows an empirical Type-I error rate of approximately 6–7% against a nominal 5%, consistently across Gaussian, topic-heterogeneous, and heavy-tailed noise conditions.* This is **not** a statement that the real D1 confirmatory run will have a 6–7% Type-I error rate — it is a statement about the simulated procedure's behavior under a best-case, exchangeability-imposed model. Both the compound-test bound (§1) and the exchangeability caveat (§2) qualify it further before any claim reaches the manuscript.

## 4. The finite-set estimate remains primary, model-based inference remains explicitly conditional — unchanged, reconfirmed

V11 §1's separation is re-verified and holds without modification: the topic-equal-weighted point estimate over the 31 confirmatory topics is an **unconditionally valid, assumption-free finite-set descriptive result**, reported as such regardless of anything in this document. Every interval or p-value attached to it is, and remains, explicitly conditional on (a) the exchangeability assumption (V11 §2, honestly unverified) and now (b) the individual-test-only, best-case-simulation scope established in §1–3 above.

## 5. Confirmation: no change to sample, hypotheses, construction, or procedure

Checked explicitly. Nothing in §0–3 touches the 122/26/67/29 sample, the P1-i/P1-ii/P2/M1 hypotheses, the construction rules, or the computational procedure (B=5000, the same percentiles, the same Holm comparison values, the same estimator). Every correction in this version is about the precision of what has actually been verified — a reproducibility fix (§0) and a scope correction (§1–3) — not a design change.

## 6. Final determination

- **V11 cannot be registered unchanged.** Its calibration numbers did not match its own cited script (§0, now fixed), and it made a compound/family-wise claim its evidence did not support (§1, now withdrawn and replaced with a rigorous bound instead of an unearned extrapolation).
- **V12 is ready for registration.** The finite-set estimate stands unconditionally. The inferential layer is now bounded and scoped exactly as far as the actual evidence reaches — individual-test calibration under a best-case exchangeability simulation, a mathematically certain (not simulated) conservative bound on the compound tests, and an explicit, un-quantified open question on the exact family-wise rate, rather than a number that was never earned.
- **No further revision is recommended beyond what is stated here.** A direct joint simulation of the compound P1/P2 tests and the full Holm procedure would be the next legitimate methodological step *if* an exact family-wise number is wanted before publication — this is named as a possible future check, not undertaken now, and not a blocker to registering the current, correctly-bounded procedure.

## 7. Registration package (final)

- **Protocol file (frozen):** `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V12.md`
- **SHA-256:** see chat response.
- **Proposed Git tag:** `prereg/D1-eval-synth/v1` (unchanged).
- **Calibration evidence:** `research/paper_strengthening/scripts/d1_bootstrap_calibration_check.py` (now `N_OUTER=12000`, seeds `2026/2036/2046/31415`) and `results/d1_bootstrap_calibration_check.txt`, verified to match exactly.
- **Run-manifest fields, exact commands, compute estimate:** unchanged from V7 §6.
- **Pre-execution integrity checks:** V7's checks, plus confirmation that the eventual results write-up uses this document's exact §3 statement (not the withdrawn family-wise claim from V11) and states the §1 compound-test bound as a bound, not a measured value.

Not executed: no item generated, no model called, no tag created, nothing committed or pushed.
