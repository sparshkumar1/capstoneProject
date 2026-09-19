# 6D State Ablation & Speech Perturbation Sensitivity (EXP-RL-3)

## Part A: State Vector Representation Ablation

| State Representation | Mean Difficulty | Final Difficulty | Smoothness $\downarrow$ | Oscillation Rate $\downarrow$ | Alignment ($r$) $\uparrow$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **full** | 2.65 | 2.97 | 0.329 | 0.211 | 0.181 |
| **text_only** | 2.46 | 2.75 | 0.343 | 0.223 | 0.558 |
| **performance_only** | 2.81 | 2.95 | 0.335 | 0.191 | 0.911 |

## Part B: Acoustic / Speech Noise Perturbation (Demographic & Anxiety Robustness)

| Noise Level ($\sigma$) | Action Stability vs Clean | Mean Difficulty | Smoothness $\downarrow$ | Oscillation Rate $\downarrow$ |
| :---: | :---: | :---: | :---: | :---: |
| 0.00 | 100.0% | 2.64 | 0.330 | 0.211 |
| 0.10 | 89.9% | 2.64 | 0.329 | 0.208 |
| 0.20 | 86.9% | 2.67 | 0.303 | 0.184 |
| 0.30 | 86.1% | 2.74 | 0.293 | 0.166 |
