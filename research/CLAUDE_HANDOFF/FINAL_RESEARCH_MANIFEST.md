# PREPAIred — Final Authoritative Research Manifest

**Generated:** September 19, 2026  
**Status:** **PERMANENTLY FROZEN & AUDITED**  
**Repository:** `https://github.com/sparshkumar1/capstoneProject`  
**Standard:** Level 3 Certified Scientific Record (Ground Truth for Manuscript Drafting)

---

## 1. Frozen Repository Snapshots & Artifact Locations

| Milestone | Target Venue | Frozen Git Checkpoint | Result Directory | Primary Report | Status |
|:---|:---|:---|:---|:---|:---:|
| **Paper 1: Systems & Security** | ATIS 2026 / IEEE Access | Commit `375f4f869c47907d7c222d27df3b4f9e09dc8941` | `research/results/paper1/` | [`PAPER1_FINAL_REPORT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper1/PAPER1_FINAL_REPORT.md) | **FROZEN** |
| **Paper 2: Evaluator Alignment** | ICTCS 2026 / IEEE TLT | Commit `375f4f869c47907d7c222d27df3b4f9e09dc8941` | `research/results/paper2/` | [`PAPER2_FINAL_REPORT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/PAPER2_FINAL_REPORT.md) | **FROZEN** |
| **Paper 3: Adaptive RL** | SmartCom 2027 / ICMLSC 2027 | Commit `b7cad49b6b7a54460f4eeb4ecb0292bfcb78e12f` (Tag `v1.0-paper3-complete`) | `research/results/paper3/` | [`PAPER3_FINAL_REPORT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper3/PAPER3_FINAL_REPORT.md) | **FROZEN** |

---

## 2. Cryptographic Checksum Registry

### 2.1 Benchmark Datasets
- **Paper 2 Human Gold Benchmark:** `research/data/evaluator_benchmark/final_human_gold.csv`  
  `SHA-256: 363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2` (IMMUTABLE, $N=64$)
- **Rater 1 Completed:** `research/annotation/FROZEN_HUMAN_RATINGS/RATER_1_COMPLETED.csv`  
  `SHA-256: 5c8086c6434a81100b5106c06a33dea23c30f8272b5cd4336ac3bade52ecc1ef`
- **Rater 2 Completed:** `research/annotation/FROZEN_HUMAN_RATINGS/RATER_2_COMPLETED.csv`  
  `SHA-256: b0d15a693dd68a15b0c694ee2a1815bece562c4f84813ed343b17fd1f984ebd0`
- **Rater 3 Completed:** `research/annotation/FROZEN_HUMAN_RATINGS/RATER_3_COMPLETED.csv`  
  `SHA-256: ce995d0e159053cb3ff46676b7844da2aab6335ecd47148eedb4c477737a9614`

### 2.2 Model Safetensors & Policy Checkpoints
- **CrossEncoder Checkpoint:** `services/evaluator/models/tuned_model2/model.safetensors`  
  `SHA-256: 6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`  
  *Provenance Note:* Off-the-shelf `cross-encoder/ms-marco-MiniLM-L6-v2` (UKPLab), zero PREPAIred fine-tuning.
- **Paper 3 PPO Seed 42 Checkpoint:** `research/experiments/paper3/checkpoints/seed_42/ppo_final.zip`  
  `SHA-256: 8395b6da753f5d272c46bfad018f7a7ae6e5508be58bcd732094771911b3d465`
- **Paper 3 PPO Seed 123 Checkpoint:** `research/experiments/paper3/checkpoints/seed_123/ppo_final.zip`  
  `SHA-256: 299437ea0dcdd7a5eed51326e80854bd3bb55341194420b619c5da3d675e24e0`
- **Paper 3 PPO Seed 456 Checkpoint:** `research/experiments/paper3/checkpoints/seed_456/ppo_final.zip`  
  `SHA-256: f9799143aac6a2a67664caadbfa2ce55a113704632bbbe9cfbd1990724a40c55`
- **Paper 3 PPO Seed 789 Checkpoint:** `research/experiments/paper3/checkpoints/seed_789/ppo_final.zip`  
  `SHA-256: 0ebb8800f71d453a48f4e307bea4e6cf18dbeb128a38707ac2029b38e757bbcb`
- **Paper 3 PPO Seed 999 Checkpoint:** `research/experiments/paper3/checkpoints/seed_999/ppo_final.zip`  
  `SHA-256: 16494e754125443275f83b6868a964e1688f065976396e88f400de5f60776adf`

### 2.3 Frozen Experiment Configurations
- **Paper 2 Frozen Config:** `research/experiments/paper2/frozen_config.yaml`  
  `SHA-256: f057baf1b2b9608eb0eb34d9aef3a4a3571db868f9ee728dda180364cc4e90f1`
- **Paper 3 Frozen Config:** `research/experiments/paper3/frozen_config.yaml`  
  `SHA-256: d3da218479ef15f61d9f760e40b2398ee571b4672d1370954ead23ecb3104d9e`

---

## 3. Authoritative Scientific Metrics & Empirical Outcomes

### 3.1 Paper 1: Systems Architecture, Security & Reliability
- **Security Containment:** **9/9 (100.0%)** negative C test vectors contained (`SEC-01` to `SEC-09`).
- **Fault Recovery:** **10/10 (100.0%)** tested fault scenarios recovered without state corruption (`FLT-01` to `FLT-10`).
- **Concurrency (1, 5, 10, 25 sessions):** **0 lock contention errors**, **0 isolation leaks**. Write latency: 16.3ms (1 session) to 21.0ms P95 (25 sessions).
- **Latency Profile:** Warm evaluator 1960.8ms mean (P95 2098.6ms); SQLite write 17.2ms; ScoreValidator 0.004ms.
- **Model Role Isolation:** Qwen LLM strictly insulated to qualitative feedback with **zero authority over technical scoring, question difficulty, RL actions, or best-attempt flags** (5/5 boundary invariants verified).
- **Multimodal Separation:** Acoustic prosody is **100% insulated from technical scoring**; it influences pacing only.
- **Backend Test Suite at Freeze:** 213 passed, 1 skipped, 0 failed.

### 3.2 Paper 2: Evaluator Alignment & Entailment Dampening ($N=64$)
- **Human Committee Inter-Rater Reliability ($N=64$, 3 Raters):**
  - $\text{ICC}(2, 1) = 0.9528$ (95% CI $[0.9290, 0.9689]$)
  - $\text{ICC}(2, k) = 0.9838$ (95% CI $[0.9751, 0.9894]$)
  - Krippendorff's $\alpha = 0.9523$ (95% CI $[0.9281, 0.9685]$)
- **Model-vs-Human Alignment (Full Composite):**
  - Spearman $\rho = \mathbf{0.3812}$ ($p = 1.8863 \times 10^{-3}$, 95% bootstrap CI $[0.1575, 0.5774]$)
  - Pearson $r = 0.4042$ ($p = 9.2455 \times 10^{-4}$, 95% bootstrap CI $[0.1846, 0.5960]$)
  - Kendall $\tau = 0.2715$ ($p = 1.7272 \times 10^{-3}$, 95% bootstrap CI $[0.1168, 0.4295]$)
  - $\text{MAE} = 0.2920$ (95% CI $[0.2431, 0.3457]$), $\text{RMSE} = 0.3601$ (95% CI $[0.3008, 0.4184]$)
- **7-Way Component Ablation:**
  - S1 only (Semantic): $\rho = 0.2070$, $\text{MAE} = 0.3171$
  - S2 only (FAISS): $\rho = 0.3021$, $\text{MAE} = 0.3251$
  - **R only (CrossEncoder):** $\mathbf{\rho = 0.4832}$, $\text{MAE} = 0.2763$
  - S1 + S2: $\rho = 0.2894$, $\text{MAE} = 0.3042$
  - **S1 + R:** $\mathbf{\rho = 0.4884}$, $\text{MAE} = 0.2790$
  - S2 + R: $\rho = 0.4171$, $\text{MAE} = 0.2674$
  - **Full Composite (0.15/0.35/0.50):** $\mathbf{\rho = 0.3812}$, $\text{MAE} = 0.2920$
  - *Finding:* Full composite sacrifices raw correlation to enforce rubric concept coverage and prevent keyword exploitation.
- **Robustness:** 19/21 (90.5%) metamorphic transformation tests passed; 11/13 (84.6%) adversarial attacks contained.

### 3.3 Paper 3: Adaptive RL Curriculum & Guardrails
- **Evaluation Unit:** $N = 25$ sessions per condition (5 candidate personas $\times$ 5 evaluation seeds).
- **Training Stability Unit:** $S = 5$ independent training seeds (`42, 123, 456, 789, 999`).
- **PPO vs. Baselines:**
  - Fixed Baseline ($d = 3.0$): $\text{MAE} = \mathbf{1.200}$ (95% CI $[0.920, 1.440]$)
  - Heuristic Baseline: $\text{MAE} = \mathbf{0.473}$ (95% CI $[0.349, 0.598]$)
  - PPO + Guardrails: $\text{MAE} = \mathbf{0.677 \pm 0.006}$ (across-seed SD $= 0.006$; session SD $= 0.531$)
- **Effect Size:** True session-level effect size vs. fixed baseline is **Cohen's $d \approx \mathbf{0.87}$** ($p < 0.001$).
  *(Historical artifact $t = -195.46, d = 87.41$ is archived strictly as an audit record of seed-mean variance collapse).*
- **Trade-Off Finding:** Heuristic tracks faster ($\text{MAE} = 0.473$), while PPO delivers significantly lower trajectory volatility ($0.088$ vs $0.160$) and multimodal adaptation. Universal PPO superiority is **not** claimed.
- **Safety Shield:** **0 actual out-of-bounds difficulty transitions** under guardrails; 563 total guardrail interventions across 5 seeds.
- **Ablation Mechanistic Insight:** Dimension 4 formulations (`aligned_progress`, `aligned_response_time`, `zero_progress`) yield identical aggregate $\text{MAE} = 0.673$ because $s_4$ has low policy sensitivity in neutral coordinates and guardrails override divergent proposals.
- **Convergence:** Policy action distributions stabilize and rolling rewards plateau across all 5 seeds within 20,000 steps.
- **Pacing Standard:** Described strictly as *"score-band stabilization ($0.40 \le p \le 0.70$)"* rather than "Zone of Proximal Development".

---

## 4. Methodological Claim Boundaries & Restrictions

1. **Terminology Standard:** All experimental configurations and benchmarks were **"pre-specified and frozen before human annotation"**, not "pre-registered".
2. **Model Provenance Standard:** CrossEncoder is **off-the-shelf `cross-encoder/ms-marco-MiniLM-L6-v2`** operating zero-shot. No PREPAIred-specific fine-tuning was performed.
3. **LLM Boundary Standard:** Qwen2.5-1.5B is strictly a qualitative language synthesis microservice with **zero authority over technical score, difficulty, or best-attempt ranking**.
4. **Security Boundary Standard:** Docker containerization provides OS-level process containment sharing the host kernel; it is **defense-in-depth, not an inviolable security boundary**.
5. **Educational Boundary Standard:** All RL evaluations were conducted on simulated synthetic personas. **No claims of human classroom learning gains or interview hiring pass rates are made.**
6. **Acoustic Standard:** Speech features modulate pacing and hesitation guardrails; they are **insulated from scoring** and reported as observational coordinate sweeps, not causal proofs.

---

## 5. Reproduction Suite Commands

```bash
# Paper 1 Systems Study Reproduction:
python research/scripts/execute_paper1_study.py

# Paper 2 Evaluator Study Reproduction:
python research/scripts/execute_paper2_study.py

# Paper 3 RL Study Reproduction:
python research/scripts/execute_paper3_study.py
```
