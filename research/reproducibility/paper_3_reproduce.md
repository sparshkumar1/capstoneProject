# Reproduction Guide: Paper 3 (Adaptive RL Difficulty & Guardrails)

**Target Venue:** *SmartCom 2027* / *ICMLSC 2027*  
**Paper Title:** *Guardrailed Multimodal Reinforcement Learning for Adaptive Technical Interview Difficulty*

---

## 1. Prerequisites
- Python virtual environment activated:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- SB3 checkpoint present at `rl/checkpoints/seed_123/ppo_final.zip`.
- Vector normalization stats present at `rl/checkpoints/seed_123/vecnormalize.pkl`.

---

## 2. Execute RL Experiments

Run the automated RL validation suite:
```powershell
python research/scripts/run_rl_experiments.py
```

This single command automatically executes:
1. **EXP-RL-1: Policy vs Baselines Evaluation Across 5 Personas & 20 Seeds**
   - Tests PPO vs Heuristic vs Fixed Difficulty policies across 5 candidate personas:
     - `Strong Candidate`: High skill, confident speech.
     - `Fragile Genius`: High technical skill, high acoustic hesitation.
     - `Anxious Competent`: Medium skill, high hesitation, sensitive to pacing.
     - `Inconsistent Candidate`: High variance in performance.
     - `Weak / Struggling`: Low skill, slow response times.
   - Evaluates: Mean Score, Mean Difficulty, Final Difficulty, Trajectory Smoothness, Trajectory Volatility, Oscillation Rate, and Alignment ($r$).
   - Computes Welch’s $t$-tests, $p$-values, and Cohen’s $d$ effect sizes.
   - Outputs: `research/raw/rl_policy_comparison_raw.json`, `research/tables/table_rl_policy_comparison.md`, `research/figures/rl_trajectory_comparison.png`.

2. **EXP-RL-2: Dimension 4 Impact & Domain Transfer Analysis**
   - Compares training definition (`normalized response time`) vs runtime definition (`session progress ratio`) vs uninformative `zero`.
   - Computes Action Agreement Rate and final difficulty discrepancies.
   - Outputs: `research/raw/rl_dim4_impact_raw.json`, `research/tables/table_rl_dim4_analysis.md`.

3. **EXP-RL-3: 6D State Ablation & Speech Perturbation Sensitivity Analysis**
   - Evaluates policy performance under 3 state ablation regimes (`full`, `text_only`, `performance_only`).
   - Injects Gaussian acoustic noise ($\sigma \in [0.0, 0.5]$) into confidence and hesitation signals to measure policy stability.
   - Outputs: `research/raw/rl_state_ablation_raw.json`, `research/tables/table_rl_speech_perturbation.md`, `research/figures/rl_speech_perturbation_stability.png`.

---

## 3. Verify Engineering Test Suite
```powershell
pytest tests/unit/test_orchestrator.py -v -k "rl or hybrid"
```
All tests must report `PASSED`.
