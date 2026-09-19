# X3-A analysis report (CONFIRMATORY)

Primary contrast: PPO | G minus Constant-Same | G; unit = persona (40 in stratum 'grid'); training seed second random factor (5 seeds); two-way cluster bootstrap B=10000, seed 42; 95 % percentile CI.

| Quantity | Value |
|---|---|
| Mean paired difference (MAE units) | -0.03505 |
| 95 % CI | [-0.08177, 0.00214] |
| SD of persona-level differences | 0.10155 |
| Cohen d_z (persona level) | -0.345 |
| Equivalence margin delta / superiority margin m | 0.12 / 0.2 |
| **Classification** | **Equivalent** |
| X3-B trigger fires | False |

Interpretation rule: no detectable PPO contribution beyond the shield in these checkpoints (equivalence within +/-0.12 MAE).
Secondary metrics, contrasts, rule ablations and strata are DESCRIPTIVE (no multiplicity control); see `x3a_primary_and_secondary_metrics.csv`, `x3a_secondary_contrasts.csv`, `x3a_condition_summary.csv`, `x3a_strata_descriptive.csv`.
