# State Dimension-4 Impact & Domain Transfer Analysis (EXP-RL-2)

Comparison of training definition (normalized response time) vs runtime definition (session progress ratio):

- **Action Agreement Rate**: 80.50% (fraction of identical discrete actions)
- **Mean Final Difficulty Discrepancy**: 0.020 difficulty units

| Dimension 4 Definition | Mean Difficulty | Final Difficulty | Smoothness $\downarrow$ | Oscillation Rate $\downarrow$ | Mean Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **runtime_progress** | 2.63 | 2.94 | 0.338 | 0.224 | 0.559 |
| **response_time** | 2.87 | 2.96 | 0.184 | 0.083 | 0.533 |
| **zero** | 2.82 | 3.03 | 0.421 | 0.266 | 0.529 |

> [!NOTE]
> High action agreement demonstrates that the PPO policy treats dimension 4 primarily as a monotonic progression index, remaining robust under the runtime substitution.
