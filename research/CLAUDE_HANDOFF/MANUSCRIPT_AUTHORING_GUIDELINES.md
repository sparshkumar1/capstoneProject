# Manuscript Authoring Guidelines for Claude

**Date:** September 19, 2026  
**Audience:** Claude (Manuscript Authoring Agent)  
**Authority:** Level 3 Certified Scientific Record

---

## 1. Approved Terminology & Phrasing Standards

To maintain scientific integrity during peer review, strictly observe the following phrasing standards:

| Topic | ❌ FORBIDDEN Phrasing | ✅ REQUIRED / APPROVED Phrasing | Rationale |
|:---|:---|:---|:---|
| **Protocol Status** | *"Pre-registered in an open registry..."* | *"Pre-specified experimental protocol frozen prior to human annotation"* | No external registry (OSF/AsPredicted) was used; all conditions were pre-specified and versioned internally. |
| **Model Provenance** | *"Fine-tuned CrossEncoder for PREPAIred"* | *"Off-the-shelf pre-trained cross-encoder (`cross-encoder/ms-marco-MiniLM-L6-v2`) in zero-shot inference"* | No domain fine-tuning was performed; local folder `tuned_model2` is internal scaffolding. |
| **Security Boundary** | *"Inviolable security boundary"* / *"Mathematically proven sandbox"* | *"Defense-in-depth Linux kernel process containment"* | Docker containers share the host Linux kernel; microVMs provide stronger hypervisor isolation. |
| **Fault Resilience** | *"Universally fault-tolerant architecture"* | *"All 10 evaluated failure modes recovered without state corruption"* | Guarantees cannot extend to unforeseen distributed partition events. |
| **RL Pacing Objective** | *"Zone of Proximal Development (ZPD) stabilization"* | *"Score-band stabilization ($0.40 \le p \le 0.70$)"* | Avoids anthropomorphic psychometric claims; reflects empirical scoring bounds. |
| **RL Convergence** | *"Provable asymptotic global convergence"* | *"Empirical action-distribution stabilization and rolling-reward plateauing across all five independent seeds within 20,000 steps"* | Accurately describes empirical training curve behavior. |
| **RL Superiority** | *"PPO is universally superior to heuristic adaptation"* | *"PPO delivers smoother curriculum pacing and lower volatility ($0.088$ vs $0.160$) at the cost of higher tracking error than the deterministic heuristic ($0.677$ vs $0.473$)"* | Accurately describes the multi-objective trade-off. |
| **Acoustic Features** | *"Speech prosody determines technical competency"* | *"Acoustic prosody is insulated from technical scoring; it modulates pacing and hesitation guardrails only"* | Insulates technical assessment from subjective vocal/accent characteristics. |
| **Educational Scope** | *"Improves human student hiring rates by 28%"* | *"Evaluated in simulation across calibrated synthetic candidate personas"* | No human classroom or longitudinal hiring study has been conducted. |

---

## 2. Statistical Reporting Invariants

### 2.1 Paper 1 (Systems & Security)
- Concurrency write latencies: P95 latencies are **17.9ms** (1 session), **126.5ms** (5 sessions), **263.8ms** (10 sessions), and **719.1ms** (25 sessions).
- Zero lock errors and zero isolation violations across all 287 total transaction operations.
- Warm evaluator mean latency: **1960.8 ms** (median: 404.6 ms, P95: 2098.6 ms).
- SQLite commit indexing: **17.2 ms**; ScoreValidator: **0.004 ms**.
- Regression tests at freeze: **213 passed, 1 skipped, 0 failed**.

### 2.2 Paper 2 (Technical Evaluator Alignment, $N=64$)
- Benchmark unit: $N=64$ authentic explanations across 10 DSA topics (54 `mean_of_three`, 10 `expert_adjudication`).
- Educator Inter-Rater Reliability: $\text{ICC}(2, 1) = 0.9528$, $\text{ICC}(2, k) = 0.9838$, Krippendorff's $\alpha = 0.9523$. (Strictly human-human agreement).
- Primary Evaluator Correlation: **Spearman $\rho = 0.3812$** ($p = 1.8863 \times 10^{-3}$, 95% bootstrap CI $[0.1575, 0.5774]$).
- Linear & Error Metrics: Pearson $r = 0.4042$ ($p = 9.2455 \times 10^{-4}$), Kendall $\tau = 0.2715$ ($p = 1.7272 \times 10^{-3}$), $\text{MAE} = 0.2920$, $\text{RMSE} = 0.3601$.
- 7-Way Ablation Invariant: R-only ($\rho = 0.4832$) and S1+R ($\rho = 0.4884$) achieve higher correlation than the Full Composite ($\rho = 0.3812$). The Full Composite must be framed as a safety-hardened pipeline that sacrifices unconstrained correlation to defend against keyword stuffing and enforce rubric bounds.
- Metamorphic: 19/21 (90.5%) pass; Adversarial: 11/13 (84.6%) contained.

### 2.3 Paper 3 (Adaptive RL Difficulty)
- Primary Evaluation Unit: Session trajectory ($N=25$ sessions per condition across 5 personas $\times$ 5 eval seeds).
- Multi-Seed Training Unit: $S=5$ independent training seeds (`42, 123, 456, 789, 999`).
- PPO + Guardrails Tracking Error: **$\text{MAE} = 0.677 \pm 0.006$**, where $\pm 0.006$ is strictly across-seed training stability.
- Fixed Baseline ($d=3.0$): **$\text{MAE} = 1.200$** ($[0.920, 1.440]$).
- Heuristic Baseline: **$\text{MAE} = 0.473$** ($[0.349, 0.598]$).
- Session-Level Effect Size: **Cohen's $d \approx 0.87$** ($p < 0.001$).
  *(Do NOT report $d=87.41$ or $t=-195.46$, which resulted from an erroneous division by seed-mean variance).*
- Safety Shield: **0 actual out-of-bounds transitions** ($1.0 \le d \le 5.0$). 563 total guardrail interventions across 5 seeds.
- Dimension 4 Ablation: `aligned_progress`, `aligned_response_time`, and `zero_progress` yield identical aggregate MAE ($0.673$) because $s_4$ has low marginal policy sensitivity in neutral coordinates and guardrails redirect edge cases to identical pedagogical actions.

---

## 3. Recommended Manuscript Structure & Key Citations

- **Paper 1 (ATIS 2026 / IEEE Access):**
  - Architecture: Hub-and-spoke asynchronous orchestrator with decoupled microservices.
  - Threat Model: 7-category matrix (`THR-01` to `THR-07`).
  - Empirical Containment: Negative C test vectors (`SEC-01` to `SEC-09`).
  - Concurrency: SQLite WAL serialization and multi-attempt `is_best` compound index.
  - Fault Injection: 10 scenario matrix (`FLT-01` to `FLT-10`).
- **Paper 2 (ICTCS 2026 / IEEE TLT):**
  - Architecture: Tripartite scoring ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$) with reasoning entailment dampening.
  - Ground Truth: 64-case human consensus benchmark with 3 educators and expert blind adjudication.
  - Empirical Ablation: 7-way ablation and trade-off analysis.
  - Robustness: Metamorphic testing (7 relations) and adversarial prompt injection containment.
- **Paper 3 (SmartCom 2027 / ICMLSC 2027):**
  - Architecture: 6D continuous state space MDP with discrete difficulty transitions $\{-1, 0, +1\}$.
  - Safety Shield: Deterministic post-hoc guardrails G1–G6.
  - Empirical Baselines: Corrected fixed baseline ($1.200$) and deterministic heuristic ($0.473$).
  - Multi-Seed Verification: 5 independent seeds demonstrating training stability ($\text{SD} = 0.006$) and convergence within 20,000 steps.
