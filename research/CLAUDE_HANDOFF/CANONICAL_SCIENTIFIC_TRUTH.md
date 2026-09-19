# PREPAIred — Canonical Scientific Truth and Master System Facts

**Audited Commit:** `b7cad49b6b7a54460f4eeb4ecb0292bfcb78e12f` (Tag: `v1.0-paper3-complete`)  
**Standard:** Level 3 Certified Scientific Ground Truth for the PREPAIred Research Package.  
**Audience:** Claude (Manuscript Drafting Agent) and Human Auditors.

---

## A. Master System Architecture
- **Architecture Paradigm:** Asynchronous hub-and-spoke multimodal technical assessment framework.
- **Orchestrator:** `InterviewOrchestrator` (`agents/orchestrator/interview_orchestrator.py`) managing session state, question queue, attempt tracking, Socratic follow-up state machine, and service dispatch.
- **Subsystem Isolation:**
  - **Evaluator:** In-memory Python microservice running SBERT (`all-MiniLM-L6-v2`), FAISS (`logic_vectors.faiss`), and off-the-shelf CrossEncoder (`cross-encoder/ms-marco-MiniLM-L6-v2`).
  - **Code Execution Sandbox:** Non-root Docker container running GCC 13.2.1 in isolated Linux cgroups (`--net=none`, `--cap-drop=ALL`, `--read-only`, 32MB tmpfs at `/workspace`, 128MB RAM, 2.0s wall-clock SIGKILL).
  - **Persistence:** Local SQLite database in WAL mode with `threading.Lock()` serialization.
  - **Feedback Generation:** Local Qwen2.5-1.5B-Instruct LLM microservice strictly grounded in structured evaluator output, possessing **zero authority over scoring or difficulty**.

---

## B. Evaluator Formula & Operating Parameters
- **Primary Scoring Equation:**
  $$\text{BaseScore} = 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$$
  $$\text{FinalScore} = \min(\text{BaseScore} + \text{Bonus} - \text{Penalty}, \text{MandatoryCap})$$
- **Component Breakdown:**
  - $S_1$ (Semantic Similarity): Cosine similarity between candidate answer and rubric context using frozen `sentence-transformers/all-MiniLM-L6-v2`.
  - $S_2$ (Concept Coverage): Ratio of rubric concept groups detected via FAISS inner-product vector search (`logic_vectors.faiss`) at cosine operating threshold $\theta = 0.30$.
  - $R$ (Reasoning Entailment): Zero-shot CrossEncoder (`cross-encoder/ms-marco-MiniLM-L6-v2`), pre-trained on MS MARCO by UKPLab, with **no PREPAIred-specific fine-tuning or domain adaptation**.
- **Reasoning Dampening Shield:**
  $$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ S_2 \times 0.60 & \text{if } R \le 0.30 \end{cases}$$
- **Score Sanitization:** Handled by `ScoreValidator` (`0.004 ms` latency), enforcing bounds in $[0.0, 1.0]$ and converting infrastructure errors to non-penalizing retry flags.

---

## C. Paper 1: Systems, Security & Resilience Outcomes
- **Security Negative Testing (EXP-SYS-1):** **9/9 (100.0%)** negative C attack vectors contained (`SEC-01` through `SEC-09`).
- **Fault Injection Recovery (FLT-01..10):** **10/10 (100.0%)** tested failure scenarios recovered gracefully using deterministic fallbacks without state corruption.
- **Concurrency & ACID Isolation:** Benchmarked across 1, 5, 10, and 25 concurrent sessions under SQLite WAL mode: **0 lock errors**, **0 isolation leaks**. Write latency scales from 16.3ms (1 session) to 21.0ms P95 (25 sessions).
- **Subsystem Latency SLA:**
  - Warm Evaluator: **1960.8 ms** mean (median: 404.6 ms, P95: 2098.6 ms).
  - SQLite WAL write + index: **17.2 ms** (P95: 21.0 ms).
  - SQLite WAL read: **5.0 ms** (P95: 8.5 ms).
  - ScoreValidator: **0.004 ms**.
- **Model Role Isolation:** 5/5 boundary tests passed (`QWN-01` through `QWN-05`). Qwen LLM has zero authority over scores, difficulty, or attempt ranking.
- **Multimodal Separation:** Acoustic prosody is **100% insulated from technical scoring**.

---

## D. Paper 2: NLP Evaluator Scientific Alignment ($N=64$)
- **Benchmark Benchmark Definition:** `research/data/evaluator_benchmark/final_human_gold.csv` (SHA-256: `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2`).
- **Human Consensus Quality ($N=64$):** 3 independent blind CS educators; 54 consensus (`mean_of_three`) + 10 expert blind adjudication (`expert_adjudication`).
  - Single-Rater Reliability: $\text{ICC}(2, 1) = \mathbf{0.9528}$ (95% CI $[0.9290, 0.9689]$)
  - Average-Rater Reliability: $\text{ICC}(2, k) = \mathbf{0.9838}$ (95% CI $[0.9751, 0.9894]$)
  - Krippendorff's Alpha: $\alpha = \mathbf{0.9523}$ (95% CI $[0.9281, 0.9685]$)
- **Primary Model-vs-Human Correlation:**
  - Spearman $\rho = \mathbf{0.3812}$ ($p = 1.8863 \times 10^{-3}$, 95% bootstrap CI $[0.1575, 0.5774]$).
  - Pearson $r = \mathbf{0.4042}$ ($p = 9.2455 \times 10^{-4}$, 95% bootstrap CI $[0.1846, 0.5960]$).
  - Kendall $\tau = \mathbf{0.2715}$ ($p = 1.7272 \times 10^{-3}$, 95% bootstrap CI $[0.1168, 0.4295]$).
  - $\text{MAE} = \mathbf{0.2920}$, $\text{RMSE} = \mathbf{0.3601}$.
- **7-Way Component Ablation Findings:**
  - S1 only: $\rho = 0.2070$, $\text{MAE} = 0.3171$
  - S2 only: $\rho = 0.3021$, $\text{MAE} = 0.3251$
  - R only: $\mathbf{\rho = 0.4832}$, $\text{MAE} = 0.2763$
  - S1 + S2: $\rho = 0.2894$, $\text{MAE} = 0.3042$
  - S1 + R: $\mathbf{\rho = 0.4884}$, $\text{MAE} = 0.2790$
  - S2 + R: $\rho = 0.4171$, $\text{MAE} = 0.2674$
  - **Full Composite:** $\mathbf{\rho = 0.3812}$, $\text{MAE} = 0.2920$
  - *Scientific Fact:* The Full Composite sacrifices raw correlation to enforce rubric concept coverage and prevent keyword stuffing.
- **Robustness:** 19/21 (90.5%) metamorphic transformation relations passed; 11/13 (84.6%) adversarial attacks contained.

---

## E. Paper 3: Adaptive Reinforcement Learning Outcomes
- **MDP Formulation:**
  - State Space: 6D continuous box $\mathbf{s} = [perf, avg\_perf, conf, hes, progress, diff\_norm]^T \in [0, 1]^6$.
  - Action Space: Discrete(3) adjustments $\{-1 \text{ (Easier)}, 0 \text{ (Same)}, +1 \text{ (Harder)}\}$.
  - Safety Shield: Post-hoc deterministic guardrails G1–G6.
- **Experimental Units:**
  - Evaluation Unit: Session trajectory ($N=25$ sessions per condition across 5 personas $\times$ 5 eval seeds).
  - Training Stability Unit: $S=5$ independent training seeds (`42, 123, 456, 789, 999`).
- **Core Results:**
  - Fixed Baseline ($d=3.0$): $\text{MAE} = \mathbf{1.200}$ ($[0.920, 1.440]$).
  - Heuristic Baseline: $\text{MAE} = \mathbf{0.473}$ ($[0.349, 0.598]$).
  - PPO + Guardrails: $\text{MAE} = \mathbf{0.677 \pm 0.006}$ across 5 seeds.
  - Session-Level Effect Size: **Cohen's $d \approx \mathbf{0.87}$** ($p < 0.001$).
  - Trade-Off: Heuristic tracks faster; PPO provides lower trajectory volatility ($0.088$ vs $0.160$) and multimodal adaptation. Universal PPO superiority is **not** claimed.
  - Safety Shield: **0 actual out-of-bounds difficulty transitions** ($1.0 \le d \le 5.0$). 563 total guardrail interventions across 5 seeds.
  - Dimension 4 Ablation: `aligned_progress`, `aligned_response_time`, and `zero_progress` collapse to identical aggregate $\text{MAE} = 0.673$ due to low neutral sensitivity of $s_4$ and guardrail override convergence.
  - Training Convergence: Policy action distributions stabilize and rolling rewards plateau across all 5 seeds within 20,000 steps.

---

## F. Master Resolution of Historical Discrepancies

| Historical Value | Context / Origin | Final Authoritative Value | Resolution & Explanation |
|:---|:---|:---:|:---|
| $\rho = 0.9152$ | Synthetic LLM proxy raters (`ratings_proxy.csv`) | **$\rho = 0.3812$** | Synthetic data; not authentic human agreement. |
| $\rho = 0.8358$ | Mixed human-synthetic hybrid (`ratings_averaged.csv`) | **$\rho = 0.3812$** | Averaged composite of 1 human and 3 LLMs; methodologically invalid. |
| $\rho = 0.7400$ | Stale CSV reading with `.fillna(0.0)` | **$\rho = 0.3812$** | Code artifact reading uncalibrated column; superseded. |
| $\rho = 0.6975$ | Pilot evaluation on $N=20$ single rater | **$\rho = 0.3812$** | Pilot development dataset on 4 questions; superseded by 64-case multi-educator gold benchmark. |
| $t = -195.46, d = 87.41$ | Raw SB3 evaluation script artifact | **Cohen's $d \approx 0.87$** | Raw calculation mistakenly used the standard error of 5 seed means as denominator; true session-level Cohen's $d \approx 0.87$. |
| $\text{MAE}_{\text{Fixed}} = 0.000$ | Unpassed candidate skills in early script | **$\text{MAE} = 1.200$** | Simulator defaulted to skill=0.60; mathematically verified fixed error across true persona targets is $1.200$. |
| 204,800 PPO steps | Early prototyping rollout budget | **24,576 steps/seed** | 204.8k was an exploratory budget; final multi-seed study trained for 24,576 steps per seed with convergence confirmed by 20,000 steps. |
