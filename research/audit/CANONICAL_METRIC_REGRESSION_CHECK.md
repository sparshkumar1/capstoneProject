# Canonical Metric Regression Check & Provenance Audit

**Audit Date:** September 19, 2026  
**Auditor:** Senior Research Engineer & Scientific Integrity Auditor  
**Purpose:** Formally establish the single canonical active scientific metric for human evaluator agreement and document the exact status and provenance of all historical, proxy, and artifact numbers.

---

## 1. Metric Traceability Matrix

| Metric | Active Canonical Value | Historical / Superseded Values | Exact Source & File | Scientific Status |
|:---|:---:|:---:|:---|:---|
| **Evaluator Spearman $\rho$** | **$\rho = 0.6975$**<br>($p = 6.29 \times 10^{-4}$, 95% CI: $[0.440, 0.837]$) | - **$0.7400$**<br>- **$0.8358$**<br>- **$0.9152$** | - Active: `services.evaluator.app.evaluate()` executed on 20 items of `ablation/results/ratings_rater1.csv` (`paper2_final_results.md`).<br>- $0.7400$: Static uncalibrated CSV column `system_score` in `ratings_rater1.csv` with post-hoc `.fillna(0.0)`.<br>- $0.8358$: `ratings_averaged.csv` (1 human + 3 synthetic proxy raters).<br>- $0.9152$: `ratings_proxy.csv` (pure synthetic proxy heuristic scores). | **ACTIVE CANONICAL VALUE**<br>($0.7400$ is superseded static CSV artifact; $0.8358$ & $0.9152$ are historical synthetic/hybrid data). |
| **Evaluator Pearson $r$** | **$r = 0.7290$**<br>($p = 3.03 \times 10^{-4}$, 95% CI: $[0.502, 0.865]$) | - **$0.6690$**<br>- **$0.84 - 0.88$** | - Active: Live `evaluate()` on 20 items of `ratings_rater1.csv`.<br>- $0.6690$: Static CSV column `.fillna(0.0)` artifact.<br>- $0.84-0.88$: Mixed synthetic proxies in early draft text. | **ACTIVE CANONICAL VALUE**<br>($0.6690$ is superseded static CSV artifact). |
| **Evaluator MAE** | **$\text{MAE} = 0.2245$** | - **$0.2092$**<br>- **$0.2585$** | - Active: Live `evaluate()` vs `ratings_rater1.csv`.<br>- $0.2092$: Static CSV column `.fillna(0.0)` artifact.<br>- $0.2585$: `ratings_averaged.csv` composite. | **ACTIVE CANONICAL VALUE** |
| **Evaluator RMSE** | **$\text{RMSE} = 0.3039$** | - **$0.2728$** | - Active: Live `evaluate()` vs `ratings_rater1.csv`.<br>- $0.2728$: Static CSV column `.fillna(0.0)` artifact. | **ACTIVE CANONICAL VALUE** |
| **Human Inter-Rater Reliability** | **Not Applicable**<br>(Single authentic human educator in pilot baseline) | - **$\alpha = 0.8255$**<br>- **$\alpha = 0.9177$** | - $\alpha = 0.8255$: Computed across `ratings_synthetic_rater*.csv` proxy files.<br>- $\alpha = 0.9177$: Computed in `rater_analysis.json` across 1 human + 3 synthetic proxies. | **RETRACTED / NOT APPLICABLE**<br>(No human-to-human $\alpha$ exists. A 3-rater human annotation package is designed and pending human execution at Gate 1). |
| **PPO Training Timesteps** | **300,000 steps** | - **204,800 steps**<br>- **500,000 steps** | - Active: `rl/training/retrain_quick.py:32` & checkpoint `rl/checkpoints/seed_123/ppo_final.zip`.<br>- 204,800: Early checkpoint rollout artifact ($100 \times 2048$).<br>- 500,000: Uncalibrated capstone slide claim. | **ACTIVE CANONICAL VALUE** |
| **RL Action Space** | **3 Actions**<br>`{0: Easier, 1: Same, 2: Harder}` | - **5 Actions**<br>`{Easier, Same, Harder, Hint, Followup}` | - Active: `rl/env/interview_env.py` and `agents/strategy/hybrid_orchestrator.py`.<br>- 5 Actions: Legacy prototype MDP before pedagogical decoupling. | **ACTIVE CANONICAL VALUE** |

---

## 2. Definitive Provenance of $\rho = 0.6975$ vs $\rho = 0.7400$

As established in [`research/audit/rho_provenance.md`](file:///C:/Users/spars/Downloads/PrepAIred/research/audit/rho_provenance.md):
1. **Live Code Truth ($\rho = 0.6975$):** Calling the live production evaluation pipeline (`services.evaluator.app.evaluate`) across the 20 technical answers in `ablation/results/ratings_rater1.csv` produces:
   - Spearman $\rho = 0.697528$ ($p = 0.000629$)
   - Pearson $r = 0.729014$ ($p = 0.000303$)
   - $\text{MAE} = 0.2245$
   - $\text{RMSE} = 0.3039$
2. **Static CSV Artifact ($\rho = 0.7400$):** In `ablation/results/ratings_rater1.csv`, a pre-existing column named `system_score` contained values from a June 2026 uncalibrated run with 3 blank/NaN entries (rows 0, 10, 16). When an offline analysis script called `.fillna(0.0)` on this stale column, it produced $\rho = 0.740038$.
3. **Mandatory Canonical Invariant:**
   - **The sole authoritative live human pilot baseline is $\rho = 0.6975$.**
   - $\rho = 0.7400$ is permanently classified as a superseded static CSV artifact and must not be cited as the live evaluator's performance.
   - All active canonical files (`README.md`, `research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/README.md`, `research/CLAUDE_RESEARCH_INDEX.md`, `research/papers/paper2_evaluator/`) have been synchronized to $\rho = 0.6975$.
