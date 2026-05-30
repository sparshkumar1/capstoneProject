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
| S1 only | 0.9724 | ±0.0358 | 0.9642 |
| S2 only | 0.9534 | ±0.0863 | 0.9456 |
| R only | 0.9690 | ±0.0798 | 0.9651 |
| S1 + R | 0.9561 | ±0.0755 | 0.9479 |
| S1 + S2 | 0.9476 | ±0.0829 | 0.9381 |
| S2 + R | 0.9612 | ±0.0793 | 0.9542 |
| Full (paper) | 0.9612 | ±0.0793 | 0.9542 |

### Delta vs Full (paper)

| Config | Δρ | 95% CI | p-value |
| --- | --- | --- | --- |
| S1 only | +0.0112 | [-0.0312, +0.0830] | 0.7733 |
| S2 only | -0.0078 | [-0.0618, +0.0326] | 0.9953 |
| R only | +0.0078 | [+0.0003, +0.0432] | 0.04667 |
| S1 + R | -0.0051 | [-0.0364, +0.0051] | 0.5273 |
| S1 + S2 | -0.0136 | [-0.0680, +0.0304] | 0.352 |
| S2 + R | +0.0000 | [+0.0000, +0.0000] | 2 |
