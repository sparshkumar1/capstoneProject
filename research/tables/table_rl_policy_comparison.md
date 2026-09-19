# Adaptive Policy vs Baselines Evaluation (EXP-RL-1)

Evaluation across 5 candidate personas ($N=100$ interview sessions per policy, 10 steps each):

| Policy | Mean Score | Mean Difficulty | Final Difficulty | Smoothness $\downarrow$ | Volatility $\downarrow$ | Oscillation Rate $\downarrow$ | Alignment ($r$) $\uparrow$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **PPO** | 0.560 $\pm$ 0.33 | 2.62 $\pm$ 0.53 | 2.92 | 0.342 $\pm$ 0.33 | 0.451 | 0.230 | 0.303 ($p=2.2e-03$) |
| **Heuristic** | 0.569 $\pm$ 0.29 | 2.87 $\pm$ 1.66 | 3.00 | 0.180 $\pm$ 0.10 | 0.573 | 0.000 | 0.962 ($p=2.6e-57$) |
| **Fixed** | 0.513 $\pm$ 0.38 | 3.00 $\pm$ 0.00 | 3.00 | 0.100 $\pm$ 0.00 | 0.287 | 0.000 | 0.000 ($p=1.0e+00$) |

## Statistical Significance (Welch's $t$-test & Cohen's $d$)

| Comparison | Metric | $\Delta$ (PPO - Baseline) | $t$-statistic | $p$-value | Cohen's $d$ | Significance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| PPO_vs_Heuristic | mean_score | -0.009 | -0.20 | 8.4106e-01 | -0.03 | n.s. |
| PPO_vs_Heuristic | mean_difficulty | -0.255 | -1.46 | 1.4690e-01 | -0.21 | n.s. |
| PPO_vs_Heuristic | smoothness | +0.162 | 4.70 | 7.3234e-06 | 0.66 | **p < 0.01** |
| PPO_vs_Heuristic | volatility | -0.122 | -3.03 | 2.8500e-03 | -0.43 | **p < 0.01** |
| PPO_vs_Heuristic | oscillation_rate | +0.230 | 6.88 | 5.5128e-10 | 0.97 | **p < 0.01** |
| PPO_vs_Fixed | mean_score | +0.047 | 0.93 | 3.5317e-01 | 0.13 | n.s. |
| PPO_vs_Fixed | mean_difficulty | -0.381 | -7.18 | 1.3049e-10 | -1.02 | **p < 0.01** |
| PPO_vs_Fixed | smoothness | +0.242 | 7.32 | 6.6894e-11 | 1.04 | **p < 0.01** |
| PPO_vs_Fixed | volatility | +0.164 | 7.70 | 1.0329e-11 | 1.09 | **p < 0.01** |
| PPO_vs_Fixed | oscillation_rate | +0.230 | 6.88 | 5.5128e-10 | 0.97 | **p < 0.01** |
