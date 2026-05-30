# Significance statistics

## RL ablation

| Comparison | Metric | Δ | t | p-value | Cohen's d |
| --- | --- | --- | --- | --- | --- |
| vs_PPO_only | mean_score | +0.052 | 2.235 | 0.04348 | 0.999 |
| vs_PPO_only | mean_difficulty | +1.130 | 11.098 | 1.953e-07 | 4.963 |
| vs_PPO_only | adaptation_rho | +0.404 | 3.749 | 0.005143 | 1.950 |
| vs_PPO_only | adjusted_slope | +0.019 | 2.953 | 0.008716 | 1.321 |
| vs_PPO_only | ppo_rate | -0.380 | -8.143 | 1.921e-05 | -3.642 |
| vs_Heuristic_only | mean_score | +0.080 | 2.440 | 0.03299 | 1.091 |
| vs_Heuristic_only | mean_difficulty | +2.200 | 14.014 | 7.254e-08 | 6.267 |
| vs_Heuristic_only | adaptation_rho | +0.911 | 6.964 | 0.0001218 | 3.654 |
| vs_Heuristic_only | adjusted_slope | +0.041 | 4.539 | 0.0005216 | 2.030 |
| vs_Heuristic_only | ppo_rate | +0.620 | 13.286 | 3.221e-07 | 5.942 |
| vs_Fixed_difficulty | mean_score | +0.120 | 4.645 | 0.0005353 | 2.077 |
| vs_Fixed_difficulty | mean_difficulty | +1.490 | 42.815 | 1.032e-11 | 19.147 |
| vs_Fixed_difficulty | adaptation_rho | N/A | nan | nan | nan |
| vs_Fixed_difficulty | adjusted_slope | +0.079 | 10.947 | 8.202e-09 | 4.895 |
| vs_Fixed_difficulty | ppo_rate | +0.620 | 13.286 | 3.221e-07 | 5.942 |

## Evaluator ablation

Paired items used: 20

| Config | Spearman ρ | 95% CI half-width | Bootstrap mean |
| --- | --- | --- | --- |
| S1 only | 0.8233 | ±0.2536 | 0.8082 |
| S2 only | 0.8888 | ±0.1545 | 0.8783 |
| R only | 0.5866 | ±0.3261 | 0.5784 |
| S1 + R | 0.6747 | ±0.2911 | 0.6581 |
| S1 + S2 | 0.9165 | ±0.1332 | 0.9049 |
| S2 + R | 0.8922 | ±0.1865 | 0.8778 |
| Full (paper) | 0.9152 | ±0.1241 | 0.9021 |

### Delta vs Full (paper)

| Config | Δρ | 95% CI | p-value |
| --- | --- | --- | --- |
| S1 only | -0.0918 | [-0.2927, +0.0273] | 0.15 |
| S2 only | -0.0263 | [-0.1193, +0.0636] | 0.5313 |
| R only | -0.3285 | [-0.6282, -0.0839] | 0.006667 |
| S1 + R | -0.2404 | [-0.4882, -0.0622] | 0.001333 |
| S1 + S2 | +0.0014 | [-0.0628, +0.0647] | 0.8727 |
| S2 + R | -0.0229 | [-0.1538, +0.0895] | 0.7253 |
