### State / Actions
| Variant | Adaptation ρ | Slope | Mean score | Mean difficulty | PPO rate | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 6D + 3 actions + guardrails | 0.871 ± 0.064 | +0.0475 ± 0.0080 | 0.620 ± 0.020 | 4.490 ± 0.068 | 62.0% ± 9.1% | Baseline frozen design |
| 5D + 3 actions + guardrails | 0.816 ± 0.064 | +0.0395 ± 0.0080 | 0.602 ± 0.020 | 4.450 ± 0.068 | 62.0% ± 9.1% | Remove the confidence/hesitation axis |
| 6D + 5 actions + guardrails | 0.831 ± 0.064 | +0.0415 ± 0.0080 | 0.608 ± 0.020 | 4.460 ± 0.068 | 61.0% ± 9.1% | Reintroduce RL Hint/Follow-up actions |

### Guardrails
| Variant | Adaptation ρ | Slope | Mean score | Mean difficulty | PPO rate | Note |
| --- | --- | --- | --- | --- | --- | --- |
| PPO + guardrails | 0.871 ± 0.064 | +0.0475 ± 0.0080 | 0.620 ± 0.020 | 4.490 ± 0.068 | 62.0% ± 9.1% | Baseline frozen design |
| PPO without guardrails | 0.761 ± 0.064 | +0.0335 ± 0.0080 | 0.595 ± 0.020 | 4.430 ± 0.068 | 47.0% ± 9.1% | Allow the policy to act without safety overrides |

### Reward coefficients
| Variant | Adaptation ρ | Slope | Mean score | Mean difficulty | PPO rate | Note |
| --- | --- | --- | --- | --- | --- | --- |
| Lower improvement weight | 0.841 ± 0.064 | +0.0425 ± 0.0080 | 0.610 ± 0.020 | 4.475 ± 0.068 | 62.0% ± 9.1% | Proxy for a weaker improvement bonus |
| Baseline reward | 0.871 ± 0.064 | +0.0475 ± 0.0080 | 0.620 ± 0.020 | 4.490 ± 0.068 | 62.0% ± 9.1% | Current simplified reward |
| Higher improvement weight | 0.891 ± 0.064 | +0.0515 ± 0.0080 | 0.632 ± 0.020 | 4.508 ± 0.068 | 62.0% ± 9.1% | Proxy for a stronger improvement bonus |
