# Historical Results & Claims Reconciliation Report

**Audited Git Head Commit:** `9cfd34f278de8cc6b2810a4855b571b6b7264495`  
**Status:** Mandatory Methodological Reconciliation  
**Source of Truth:** Current reproducible codebase, raw evaluation files (`research/raw/`, `ablation/results/`), and verified test execution.

---

## 1. Executive Reconciliation Summary

Past project drafts, capstone presentations, and exploratory markdown reports in `docs/` and `docs/archive/` contained several contradictory statistical claims and architectural statements. This document reconciles every discrepancy between historical claims and the verified implementation reality.

> [!CAUTION]
> **Authoritative Binding Rule (Rule 0.3):**
> Under no circumstances may historical claims of $\rho = 0.8358$, $\alpha = 0.8255$, or "3 blinded human raters" be cited in new conference submissions as proven empirical facts. All reporting must strictly reflect the verified, reproducible dataset: $N=20$, **1 real human CS educator rater** ($\rho = 0.6975$, $r = 0.7290$, $\text{MAE} = 0.2245$).

---

## 2. Metric & Claim Reconciliation Matrix

| Domain | Historical Claim (Drafts / Archive) | Actual Verified Implementation (`9cfd34f`) | Root Cause of Discrepancy | Reconciled Status / Correct Scientific Wording |
|---|---|---|---|---|
| **Human Rater Count** | "3 independent blinded expert human raters evaluated all answers" | **1 real human CS educator rater** + 3 synthetic proxy models | Earlier prototype used 3 synthetic LLM proxy personas as stand-ins for raters, erroneously documented as 3 human raters. | **RETRACTED**. Must report: *"Evaluated on a pilot benchmark of $N=20$ technical answers scored by 1 human computer science educator, analyzed separately from synthetic proxy ratings."* |
| **Evaluator Spearman $\rho$** | $\rho = 0.8358$, $\rho = 0.9152$, $\rho = 0.7400$ | **$\rho = 0.6975$** [95% CI: 0.440, 0.837] on Human Rater 1 ($N=20$) | $\rho = 0.9152$ was synthetic proxy data. $\rho = 0.8358$ was a hybrid human-synthetic proxy composite. $\rho = 0.7400$ was an artifact of reading a stale uncalibrated CSV column with `.fillna(0.0)` (`rho_provenance.md`). | **RECONCILED**. The sole authentic, reproducible live evaluator human agreement is **$\rho = 0.6975$** ($p = 6.29 \times 10^{-4}$). $\rho = 0.7400$ is superseded/artifact-only. Synthetic/hybrid values ($\rho=0.9152, 0.8358$) are strictly historical. |
| **Evaluator Pearson $r$** | $r = 0.84$ – $0.88$, $r = 0.6690$ | **$r = 0.7290$** [95% CI: 0.502, 0.865] on Human Rater 1 ($N=20$) | $r = 0.84-0.88$ was calculated on mixed synthetic data. $r = 0.6690$ was an artifact of the stale static CSV column. | **RECONCILED**. Real human linear correlation of the live evaluator is **$r = 0.7290$** ($p = 3.03 \times 10^{-4}$, $\text{MAE} = 0.2245$). |
| **Inter-Rater Reliability** | Krippendorff's $\alpha = 0.8255$ | **Not Applicable (Single Human Rater)** | $\alpha$ was calculated across the single human rater and two synthetic LLM proxy outputs. Measuring inter-rater reliability between a human and an LLM and labeling it human inter-rater agreement is scientifically invalid. | **RETRACTED**. No human-to-human $\alpha$ exists in the current data. A 3-rater human annotation package is designed and pending human execution. |
| **PPO Training Timesteps** | "204,800 timesteps" (or 500k in capstone slides) | **300,000 timesteps** (`rl/training/retrain_quick.py`) | Checkpoint `rl/checkpoints/seed_123/ppo_final.zip` was trained for 300,000 steps with 10-step horizon episodes across 5 synthetic candidate personas. | **UPDATED**. Report 300,000 training timesteps. Provide exact SB3 hyperparameter manifest. |
| **RL Action Space** | 5 actions: `{Easier, Same, Harder, Hint, Followup}` | **3 actions:** `{0: Easier, 1: Same, 2: Harder}` | Hints and Socratic follow-ups were moved out of the RL MDP into deterministic orchestrator rules (`_decide_and_inject_followup`). Decoupling pedagogy from curriculum difficulty stabilized the RL policy. | **RESOLVED**. RL controls global question difficulty only; orchestrator rules handle in-turn remediation. |
| **RL State Dimension 4** | "Response-time normalized signal" | **Training = response time; Runtime = progress fraction** | Mismatch: simulator trains with normalized response time ($\Delta t / \Delta t_{\max}$), whereas production orchestrator passes turn progress fraction ($t / T$). | **IDENTIFIED LIMITATION**. Must be reported as an aligned domain-shift limitation or retrained with unified semantics. |
| **LLM Microservice** | "Qwen-7B via remote Ollama instance" | **Local `Qwen2.5-1.5B-Instruct`** GGUF / Transformers | Remote 7B model had latency >8s and required external GPU hosting. 1.5B GGUF runs locally on CPU in <2.5s with zero external cloud dependencies. | **RECONCILED**. Current system uses local `Qwen2.5-1.5B-Instruct` with deterministic non-LLM structured fallback. |
| **Security Guarantees** | "Mathematical container isolation prevents host compromise" | **Defense-in-depth Linux kernel containment** | Static AST/regex source filtering + Docker container flags (`--cap-drop=ALL`, `--net=none`, `--read-only`, tmpfs `/workspace`, non-root UID 1001). | **WEAKENED TO DEFENSE-IN-DEPTH**. Docker is an OS containment boundary, not hardware virtualization or a formal mathematical proof. |
| **Educational Efficacy** | "Improves student technical interview performance by 28%" | **No longitudinal learning study has been conducted** | Early slide decks conflated synthetic candidate persona skill progression with real human learning outcomes. | **RETRACTED**. PREPAIred evaluates technical assessment infrastructure and simulation dynamics. No student learning efficacy claim may be made. |

---

## 3. Discrepancy Traceability & Audit Trail

### 3.1 The "3 Blinded Raters" Discrepancy
In `docs/archive/` and early draft LaTeX files, the methodology text described:
> *"Three domain-expert raters independently graded 20 candidate responses on a scale of 0 to 1, achieving high inter-rater reliability (Krippendorff's $\alpha = 0.8255$)."*

Inspection of `ablation/results/` revealed the actual data files:
- `ratings_rater1.csv`: 20 responses scored by an actual human CS educator.
- `ratings_synthetic_rater1.csv`, `ratings_synthetic_rater2.csv`, `ratings_synthetic_rater3.csv`: Three runs of an LLM prompt acting as proxy raters.
- `ratings_proxy.csv`: Composite synthetic scores.
- `ratings_averaged.csv`: Average across human and synthetic ratings.

**Audit Finding:** The correlation $\rho = 0.8358$ was obtained by running the evaluator against `ratings_averaged.csv`. When evaluated against `ratings_rater1.csv` alone, the evaluator achieves $\rho = 0.6975$ ($p = 0.0006$).

### 3.2 Protocol for Paper Submissions
1. **Paper 2 (Evaluator / ICTCS 2026):**
   - Must report the real human baseline: $\rho = 0.6975$, $r = 0.7290$, $\text{MAE} = 0.2245$ on $N=20$.
   - Must report the synthetic baseline separately: $\rho = 0.9152$, $r = 0.9328$, $\text{MAE} = 0.0984$.
   - Must describe the designed 3-rater human annotation benchmark protocol as an ongoing expansion, not completed work.
2. **Paper 3 (RL / SmartCom 2027):**
   - Must report simulated candidate trajectories across 5 calibrated synthetic personas.
   - Must not claim human learning gains.
3. **Paper 1 (Systems / ATIS 2026):**
   - Must report measured Docker negative security tests (SEC-01 through SEC-09).
   - Must report measured subsystem latencies and failure-injection recovery.
