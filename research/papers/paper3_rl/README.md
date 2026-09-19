# Paper 3: Adaptive Reinforcement Learning & Pedagogical Guardrails

- **Working Title:** *Guardrailed Multimodal Reinforcement Learning for Adaptive Technical Interview Difficulty*
- **Target Venues:** **SmartCom 2027** (Goa, Jan 2027) / **ICMLSC 2027**
- **Domain:** Reinforcement Learning, Intelligent Tutoring Systems, Human-Centered AI

---

## 1. Abstract
Fixed-difficulty technical interviews cause disengagement among struggling candidates and fail to differentiate top performers. While naive heuristic adjustment rules scale difficulty with instant scores, they induce severe difficulty volatility and jarring oscillation. We propose a guardrailed reinforcement learning controller that dynamically adjusts technical interview difficulty using Proximal Policy Optimization (PPO) over a 6D candidate state space capturing technical accuracy, running performance, speech confidence, acoustic hesitation, session progress, and current difficulty. To prevent harmful pedagogical transitions, the policy is bounded by post-hoc pedagogical guardrails that eliminate premature escalation under acoustic anxiety and prevent consecutive difficulty reversals. In simulation across five candidate personas (Strong, Fragile Genius, Anxious Competent, Inconsistent, Weak) over 20 random seeds, the guardrailed PPO controller reduces trajectory volatility by 21% compared to heuristic baselines ($0.451$ vs $0.573$, $p < 0.01$), eliminates difficulty whiplash, and maintains stable pacing under acoustic perturbation. Furthermore, a formal counterfactual transfer experiment confirms 80.5% policy action agreement between training and runtime state definitions.

---

## 2. Core Contributions
1. **6D Multimodal State Formulation:** Combines objective technical performance with acoustic prosody signals and session progression to inform pedagogical pacing without biasing grading.
2. **Hybrid Stability Reward Shaping:** Balances pacing challenge ($R_{\text{dec}}$), trajectory smoothness ($R_{\text{shp}}$), and outcome achievement ($R_{\text{out}}$) to penalize rapid oscillation.
3. **Pedagogical Guardrail Safeguards (G1–G4):** Post-hoc decision bounds protecting anxious candidates from premature difficulty jumps and enforcing difficulty stability.
4. **Empirical Policy Comparison Across Personas:** Rigorous statistical evaluation against Fixed and Heuristic baselines across 100 sessions per policy with Welch's $t$-tests and Cohen's $d$ effect sizes.

---

## 3. Associated Empirical Assets
- **Table 1:** Adaptive Policy vs Baselines Evaluation (`research/tables/table_rl_policy_comparison.md`)
- **Table 2:** State Dimension-4 Impact & Domain Transfer (`research/tables/table_rl_dim4_analysis.md`)
- **Table 3:** Speech Perturbation Stability (`research/tables/table_rl_speech_perturbation.md`)
- **Figure 1:** Multi-Persona Difficulty Trajectories (`research/figures/rl_trajectory_comparison.png`)
- **Figure 2:** Speech Acoustic Perturbation Robustness (`research/figures/rl_speech_perturbation_stability.png`)
