# Paper 3 — RL Adaptive Difficulty Reproduction Guide

### Execution Command
```bash
python research/scripts/run_paper3_study.py
```

### Hyperparameters
- Algorithm: Stable-Baselines3 PPO (`MlpPolicy` [64, 64])
- Total timesteps per seed: 24,576 (12 rollout iterations)
- Training seeds: `[42, 123, 456, 789, 999]`
- Evaluation seeds: `[1001, 2002, 3003, 4004, 5005]`
- Learning rate: 3e-4, Batch size: 64, Gamma: 0.99, Clip: 0.2
- Output CSV: `research/results/rl_results.csv`
