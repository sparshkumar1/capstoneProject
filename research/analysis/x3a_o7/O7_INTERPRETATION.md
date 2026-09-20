# X3-A / O7 — official result and registered interpretation (2026-09-20)

Status: **official O7 run completed; R0 PASS.** This file interprets the stored outputs strictly under the rules registered in
`research/audit/X3A_O7_SENSITIVITY_SPEC.md` (Revision 3) and `O7_REGISTRATION.json`. No parameter, margin, seed, comparator or rule was changed;
no output was inspected before the single run. O7 is **secondary sensitivity/robustness evidence** and does not replace the primary X3-A result.

## Provenance
- Command: `envs/LOCK-X3-2026-09-19/Scripts/python.exe research/analysis/x3a_o7/x3a_o7.py --registered-commit 5217542e13f8c556a3e3b884e47299a6380b2128`
- Executed at HEAD == tag commit `5217542e13f8c556a3e3b884e47299a6380b2128` (`prereg/X3-A-O7/v1`, tag object `157598a2…`), one execution, exit 0, about 8 s. No retry.
- Environment: Python 3.12.7 (Anaconda), numpy 2.5.2, scipy 1.17.1, Windows 64-bit; lock and requirements hashes verified by the script.
- Output namespace: `research/analysis/x3a_o7/results/` (exactly three files; SHA-256 in `run_record/O7_RUN_RECORD.json`). No X3-A primary file was touched.
- The script writes no run manifest and `run_manifest_v2` was not usable for this registration (see `run_record/O7_RUN_RECORD.json`); provenance is `r0_record.json` plus that record.

## R0 (independent reproduction gate): PASS
Independent recomputation reproduced the registered result exactly: |Δpoint| = |Δci_low| = |Δci_high| = 0.0 (criterion ≤ 1e-12).
Key sets verified: 63,000 rows; PPO|G 4,000 keys (5 seeds × 40 personas × 20 evaluation seeds); Constant-Same|G 800 keys.

## Results (Δ = PPO+G − Constant-Same+G tracking MAE; negative favours PPO numerically)
| Analysis | Estimand | Point | 95% CI | Registered-rule class |
|---|---|---|---|---|
| REG (registered, unchanged) | personas × training population | −0.0350 | [−0.0818, +0.0021] | Equivalent |
| A persona-only (five checkpoints fixed) | conditional | −0.0350 | [−0.0673, −0.0052] | Equivalent |
| B seed-level t interval (5 aggregates, df = 4) | conditional | −0.0350 | [−0.0758, +0.0057] | Equivalent |
| C leave-one-seed-out (removed seed 42 / 123 / 456 / 789 / 999) | stability, not inferential | −0.0234 / −0.0463 / −0.0335 / −0.0372 / −0.0348 | [−0.0614, +0.0092] / [−0.0948, −0.0043] / [−0.0874, +0.0070] / [−0.0873, −0.0005] / [−0.0898, +0.0078] | Equivalent ×5 |

## Registered interpretation
1. **Equivalence:** every one of the 8 intervals lies entirely inside ±0.12 (registered rule: lower > −0.12 and upper < +0.12) → class "Equivalent" in all analyses; the registered classification is unchanged under three labelled robustness checks. Under the spec's wording this is *not* "robust" in a general sense, only "registered result unchanged under A, B and C".
2. **Superiority:** not met anywhere. Meaningful PPO superiority would need an upper limit < −0.20; the largest-magnitude limits observed are the lower ends (e.g. −0.0948), and every upper limit is above −0.20 (the most negative upper limit is −0.0052, analysis A).
3. **Not "no effect":** equivalence within ±0.12 is not evidence of zero difference. Analysis A's interval and two leave-one-out intervals (removed seed 123 and 789) exclude zero on the PPO-favourable side: the persona-only interval, which excludes checkpoint-to-checkpoint variability by design (spec §3), is narrower than REG and does not license a claim that PPO tracks better. The registered REG and B intervals include zero.
4. **Seed stability:** seed-level differences Δs = −0.0816 (42), +0.0100 (123), −0.0411 (456), −0.0266 (789), −0.0359 (999). Four of five are negative; seed 123 is slightly positive. SD = 0.0328, min −0.0816, max +0.0100. The seed-level jackknife SE is 0.0147. Removing any single seed shifts the point by at most 0.0116 (seed 42, the most favourable seed; point moves to −0.0234).
5. **Persona uncertainty:** the persona-level SD of D̄ is 0.1015, much larger than the mean difference, so persona heterogeneity dominates the point estimate.
6. **Boundary effects:** the closest any interval comes to the lower equivalence margin is −0.0948 (seed 123 removed), 0.0252 inside −0.12; the closest to the upper margin is +0.0092, far inside +0.12. No interval crosses a margin.
7. **Sensitivity departures / unexpected failures:** none. All 8 classes agree; no analysis was rerun.

## Limits (unchanged from the specification)
Five checkpoints from a non-reproducible recipe; the seed factor is a hypothetical population; B is a conditional interval on five aggregates with normality unassessable; the 40 personas are a factorial grid, not a random sample; simulated candidates only; no real-user claim. The ±0.12 margin is a registered decision; whether that margin is practically small is not evaluated here.

## Permissible wording
"The registered X3-A classification (Equivalent, margin ±0.12) was unchanged under three pre-specified secondary sensitivity analyses (persona-only bootstrap, conditional seed-level t interval, leave-one-seed-out), on the five frozen checkpoints in simulation." Not permitted: PPO superiority, PPO "robustly equivalent to Constant-Same", "no effect", or any real-user claim.
