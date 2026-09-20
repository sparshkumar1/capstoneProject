# Paper 3 - result tables (exact frozen numbers)
**Table 1. Primary and sensitivity estimates** (delta = PPO+G minus Constant-Same+G tracking MAE; margins +/-0.12 equivalence, -0.20 superiority)
| Analysis | delta | 95% CI | Class |
|---|---|---|---|
| Registered (X3-A, two-way cluster bootstrap, B=10,000, seed 42) | -0.0350 | [-0.0818, +0.0021] | Equivalent |
| O7-R0 reproduction | -0.0350 (difference 0.0) | - | reproduced |
| O7-A persona-only bootstrap | -0.0350 | [-0.0673, -0.0052] | Equivalent |
| O7-B seed-level t (df 4) | -0.0350 | [-0.0758, +0.0057] | Equivalent |
| O7-C leave-one-seed-out (5) | -0.0463 ... -0.0234 (points) | see x3a_o7_results.json | Equivalent x5 |
Sources: research/confirmatory/X3-A/results/x3a_decision.json (dfa9c0f7...); research/analysis/x3a_o7/results/x3a_o7_results.json. Persona-level SD 0.1015; seed 123 +0.0100, seed 42 -0.0816 (O7_INTERPRETATION.md).
**Table 2. Secondary contrasts (40 personas x 5 seeds)**: volatility +0.14877 [0.0666, 0.25445]; oscillation +0.25061 [0.13027, 0.38584]; zeroed observation +0.36982 [0.09077, 0.64148]; partner observation +0.25382 [0.10948, 0.41417]; PPO+G minus heuristic+G -0.46414 [-0.7134, -0.22601]; minus proportional+G -0.30084 [-0.51982, -0.09469]; minus oracle-rule+G -0.10698 [-0.21823, 0.00841]; shield on/off for Constant-Same 1.104 vs 1.000 (0.10386 [-0.18375, 0.38796]); removing G1: PPO+G -0.08725 [-0.23925, 0.03782], Constant-Same+G -0.146 [-0.34944, 0.03637].
**Table 3. Five-persona frozen study**: MAE Fixed(3.0) 1.200; Heuristic 0.473 (volatility 0.160); PPO+G 0.677 (per seed 0.687/0.673/0.676/0.673/0.676); PPO+G volatility 0.186 (0.268/0.088/0.208/0.240/0.128; sample SD 0.076); Constant-Same+G MAE 0.673, volatility 0.080; activations 563/1250 (45.0%); overrides 99/1250 (7.9%); attempted out-of-range 232 (18.6%); raw PPO boundary attempts 136 (10.9%).
