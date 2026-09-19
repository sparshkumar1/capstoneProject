# X3-A analysis report (PIPELINE-TEST FIXTURE - not a result)

Primary contrast: PPO | G minus Constant-Same | G; unit = persona (5 in stratum 'frozen'); training seed second random factor (5 seeds); two-way cluster bootstrap B=10000, seed 42; 95 % percentile CI.

| Quantity | Value |
|---|---|
| Mean paired difference (MAE units) | 0.00527 |
| 95 % CI | [-0.00727, 0.02655] |
| SD of persona-level differences | 0.01733 |
| Cohen d_z (persona level) | 0.304 |
| Equivalence margin delta / superiority margin m | 0.12 / 0.2 |
| **Classification** | **Equivalent** |
| X3-B trigger fires | False |

Interpretation rule: no detectable PPO contribution beyond the shield in these checkpoints (equivalence within +/-0.12 MAE).
Secondary metrics, contrasts, rule ablations and strata are DESCRIPTIVE (no multiplicity control); see `x3a_primary_and_secondary_metrics.csv`, `x3a_secondary_contrasts.csv`, `x3a_condition_summary.csv`, `x3a_strata_descriptive.csv`.
