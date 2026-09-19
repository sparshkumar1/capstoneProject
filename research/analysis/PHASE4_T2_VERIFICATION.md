# Phase 4 T2 verification (independent recomputation)

| Check | Recomputed | Stored/claimed | Tolerance | Result |
|---|---|---|---|---|
| X3-A primary mean difference (PPO+G - ConstSame+G) | -0.03505 | -0.03505 | 1e-09 | PASS |
| X3-A persona count | 40.00000 | 40.00000 | 0 | PASS |
| X3-A sessions per grid condition (Constant-Same | G) | 800.00000 | 800.00000 | 0 | PASS |
| X3-A frozen stratum Constant-Same|G MAE (compare X3-0c 0.6728) | 0.67273 | 0.67273 | 0.0005 | PASS |
| X2-B Spearman derived_ce vs human gold | 0.48246 | 0.48250 | 5e-05 | PASS |
| X2-B Spearman upstream_ce vs human gold | 0.14543 | 0.14540 | 5e-05 | PASS |
| X2-B Spearman length_only vs human gold | 0.48973 | 0.48970 | 5e-05 | PASS |
| X2-B derived_ce vs stored R (rank-equal, Spearman = 1 up to clipping ties) | 0.99998 | 1.00000 | 0.002 | PASS |
| X1-D warm evaluator n | 100.00000 | 100.00000 | 0 | PASS |
| X1-D warm evaluator median | 236.12855 | 236.12900 | 0.0005 | PASS |
| X1-D SQLite write median | 12.69710 | 12.69700 | 0.0005 | PASS |
| X1-D junit tests | 226.00000 | 226.00000 | 0 | PASS |
| X1-D junit failures | 1.00000 | 1.00000 | 0 | PASS |

RESULT: PASS (0 failures)
