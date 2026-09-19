# PREPAIred — Canonical Scientific Truth and Verified System Facts

**Audited Commit:** `9cfd34f`  
**Standard:** This document represents the **authoritative Level 3 scientific ground truth** for the PREPAIred framework. All future papers, reports, and AI reasoning must source facts directly from this document. Any conflicting assertion in historical documents is superseded.

---

## A. Current Project Architecture
- **Architecture Type:** Asynchronous hub-and-spoke multimodal assessment framework.
- **Orchestrator:** `InterviewOrchestrator` (`agents/orchestrator/interview_orchestrator.py`) managing session state, question queue, attempt tracking, Socratic follow-up state machine, and service dispatch.
- **Microservices & Isolation:**
  - Evaluator: Sub-process / Python service running SBERT, FAISS, and CrossEncoder.
  - Coding Executor: Non-root Docker container running GCC in isolated cgroups.
  - Persistence: Local SQLite database in WAL mode with thread serialization.
  - Feedback Generator: Local Qwen LLM microservice grounded in structured evaluator output.

---

## B. Current Evaluator Formula & Configuration
- **Source File:** `services/evaluator/app.py:350-405`
- **Scoring Equation:**
  $$\text{BaseScore} = 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$$
  $$\text{FinalScore} = \min(\text{BaseScore} + \text{Bonus} - \text{Penalty}, \text{MandatoryCap})$$
- **Signal Breakdown:**
  - $S_1$ (Semantic Similarity): Cosine similarity between candidate embedding and rubric context using `all-MiniLM-L6-v2`.
  - $S_2$ (Concept Coverage): Ratio of rubric concept groups detected via FAISS inner-product vector search (`logic_vectors.faiss`) at cosine threshold $\theta = 0.30$.
  - $R$ (Reasoning Entailment): Fine-tuned CrossEncoder (`models/tuned_model2/`, base `cross-encoder/ms-marco-MiniLM-L6-v2`).
- **Anti-Gaming Dampener:**
  $$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ S_2 \times 0.60 & \text{if } R \le 0.30 \end{cases}$$
- **Grade Thresholds:** Excellent $\ge 0.75$, Good $\ge 0.60$, Average $\ge 0.40$, Poor $< 0.40$.

---

## C. Current Evaluator Benchmark Status
- **Question Bank:** 100 questions across 13 DSA/systems topics (`data/questions/qns.json`).
- **Rubric Assets:** 100 structured rubrics (`data/rubrics/rubrics_final_clean.json`), 1,518 indexed vectors in FAISS (`logic_vectors.faiss`).
- **Curated Benchmark Cases:** 40 multi-category evaluation cases across 4 core DSA topics (`research/data/evaluator_benchmark/benchmark_cases.json`).

---

## D. Current Verified Human Evaluation Result
- **Verified Human Metric:** **Spearman $\rho = 0.6975$ ($p = 6.29 \times 10^{-4}$)**, **Pearson $r = 0.7290$ ($p = 3.03 \times 10^{-4}$)**, **MAE = $0.2245$**, **RMSE = $0.3039$**.
- **Sample Size:** $N = 20$ technical answer explanations across 4 standard DSA topics.
- **Rater Ground Truth:** 1 authentic blinded Computer Science educator / faculty evaluator (`ablation/results/ratings_rater1.csv`).
- **95% Bootstrap Confidence Intervals ($B=2000$):**
  - $\rho \in [0.4401, 0.8371]$
  - $r \in [0.5018, 0.8654]$
- **Clarification on Superseded / Historical Numbers:**
  - $\rho = 0.7400$ is an **EXPLICITLY SUPERSEDED STATIC CSV ARTIFACT** (produced by reading an older uncalibrated `system_score` column and applying `.fillna(0.0)`, forensic provenance detailed in `research/audit/rho_provenance.md`).
  - $\rho = 0.9152$ is **SYNTHETIC PROXY DATA** (`ratings_proxy.csv`).
  - $\rho = 0.8358$ is an **AVERAGED COMPOSITE** of 1 human + 3 synthetic proxy raters.

---

## E. Current RL Configuration
- **Algorithm:** Proximal Policy Optimization (PPO) via Stable-Baselines3 (`MlpPolicy`).
- **Observation Space:** 6-dimensional continuous box $\mathcal{S} \subset [0, 1]^6$.
- **Action Space:** Discrete(3) corresponding to difficulty adjustments: $\{-1 \text{ (Easier)}, 0 \text{ (Same)}, +1 \text{ (Harder)}\}$.
- **Reward Function:** Hybrid stability reward:
  $$R_{\text{total}} = 0.60 \cdot R_{\text{dec}} + 0.30 \cdot R_{\text{out}} + 0.10 \cdot R_{\text{shp}}$$
- **Pedagogical Guardrails (G1–G4):**
  - G1: Low score ($\le 0.40$) blocks difficulty increase (`Harder` $\to$ `Same`).
  - G2: High acoustic hesitation ($> 0.70$) blocks difficulty increase (`Harder` $\to$ `Same`) to protect anxious candidates.
  - G3: Oscillation dampener blocks consecutive reversal cycles ($+1 \to -1 \to +1$).
  - G4: High score ($\ge 0.85$) with low hesitation prevents difficulty demotion (`Easier` $\to$ `Same`).

---

## F. Current RL Training Steps
- **Authoritative Training Budget:** **300,000 steps** (`rl/training/retrain_quick.py:32`).
- **Historical Claim (204,800 steps):** An early checkpoint artifact ($100 \times 2048$ rollouts) from initial prototyping, superseded by 300,000 steps for value function stability.

---

## G. Current State Representation & Dimension 4 Alignment
- **Observation Vector:** $\mathbf{s} = [perf, avg\_perf, conf, hes, dim4, diff]^T$.
- **Dimension 4 Formulation:**
  - Training Simulator: Normalized response time $\Delta t / (2 \cdot (3 + 6d))$.
  - Production Runtime: Turn progress ratio $t / T$.
- **Empirical Domain Transfer Verification (`EXP-RL-2`):**
  - Action agreement rate across policies: **80.50%**.
  - Final difficulty discrepancy: **0.020 difficulty units**.
  - Confirms PPO policy uses dimension 4 primarily as a monotonic pacing indicator.

---

## H. Current Docker Sandbox Configuration
- **Containment Primitives:**
  - Non-root user: UID `1001:1001`
  - Capabilities: `--cap-drop=ALL` (drops all Linux capabilities)
  - Network: `--net=none` (completely disables network stack)
  - Filesystem: `--read-only` root filesystem with 64MB tmpfs at `/workspace` (`noexec, nosuid`)
  - Resource Caps: 128MB RAM ceiling, `--pids-limit=32`
  - Timeout: 2.0 seconds wall-clock hard SIGKILL
- **Empirical Negative Testing (`EXP-SYS-1`):** Traps ptrace tampering (`SEC-01`), GCC compilation errors (`SEC-03`), null dereference SIGSEGV (`SEC-04`), infinite loops (`SEC-05`), memory bombs (`SEC-06`), outbound network connections (`SEC-07`), fork bombs (`SEC-08`), and rootfs overwrite (`SEC-09`).

---

## I. Current Qwen Role & Containment
- **Model:** Local Qwen2.5-1.5B-Instruct running on CPU (`services/qwen/`).
- **Role:** Strictly qualitative explanation generation, learning gap suggestions, and candidate encouragement.
- **Scoring Exclusion Invariant:** **The LLM is completely excluded from technical scoring.** Technical scoring is 100% deterministic (SBERT + FAISS + CrossEncoder + GCC).
- **Validation & Fallback:** `FeedbackAgent` validates output against boilerplate, length, and contradiction. If invalid or offline, it falls back instantly to deterministic evaluator synthesis (`EXP-LLM-1`).

---

## J. Current Persistence & Best-Answer Semantics
- **Database:** SQLite in Write-Ahead Logging (`WAL`) mode with `threading.Lock()` connection serialization (`services/storage/database.py`).
- **Retry Semantics:** Voluntary candidate retries pause turn progression; follow-up attempts are isolated.
- **Best Attempt Determination:** Deterministic compound sorting key:
  $$\text{AttemptRank} = (\text{validated\_score}, -\text{len}(\text{missing\_concepts}), \text{attempt\_number})$$
  The top-ranked record dynamically receives `is_best = 1`.

---

## K. Current Feedback Validator Behavior
- Candidate UI receives qualitative feedback without exposing raw floating-point numbers.
- Explanations explicitly list covered concepts, missing concepts, and concrete steps to improve.
- Fluff rejection rejects responses containing generic filler phrases without technical terms.

---

## L. Current Engineering Test Count
- **Backend Unit & Integration Tests:** **205 / 205 PASSED (100%)** in 440.19s (Commit `9cfd34f`).
- **Frontend Vitest Suite:** **20 / 20 PASSED (100%)** in 2.07s.
- **Frontend Production Build:** Vite build successful in 864ms with 0 warnings.

---

## M. Current Known Limitations
1. **Pilot Human Sample Size:** Human rater ground truth is currently based on $N=20$ expert educator evaluations across 4 core DSA topics. Larger multi-faculty cohorts should be added during camera-ready expansion using `research/annotation/`.
2. **Dimension 4 Covariate Shift:** Simulator trained on response time while runtime uses turn progress ratio (quantified at 80.5% action agreement).
3. **Container Cold-Start Overhead:** Docker container execution requires ~1.5s per compile turn, suitable for asynchronous turn submission but requiring warm containers for ultra-high throughput.
4. **Keyword Collocations in CrossEncoder:** Dense keyword phrases can achieve partial entailment ($R \approx 0.46 - 0.52$) in metamorphic testing (`MG-3`), requiring ScoreValidator guardrail caps.

---

## N. Current Three-Paper Split & O scope
1. **Paper 1 (Systems & Security):** Architecture, Docker sandboxing, negative security testing, failure recovery, subsystem latencies, persistent multi-attempt state.
2. **Paper 2 (Technical Evaluator):** Multi-signal scoring ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$), FAISS concept index, reasoning dampening, human pilot correlation ($\rho = 0.6975$), threshold sensitivity, metamorphic testing.
3. **Paper 3 (Adaptive RL):** 6D state formulation, PPO pacing policy, 21% volatility reduction vs heuristic baselines, speech perturbation robustness, dimension 4 domain transfer.

---

## O. Current Publication Venue Plan
- **Paper 1 (Primary Target):** **ATIS 2026** (Bengaluru, Submission Deadline: Nov 7, 2026) / Alternative: *IEEE Access*.
- **Paper 2 (Primary Target):** **ICTCS 2026** (Ahmedabad) / Alternative: *IEEE Transactions on Education (ToE)*.
- **Paper 3 (Primary Target):** **SmartCom 2027** (Goa, Jan 2027) / Alternative: *ICMLSC 2027*.

---

## P. Current Reproducibility Location
- **System Specs & Checksums:** `research/reproducibility/environment_manifest.json`
- **Paper 1 Reproduction:** `research/reproducibility/paper_1_reproduce.md`
- **Paper 2 Reproduction:** `research/reproducibility/paper_2_reproduce.md`
- **Paper 3 Reproduction:** `research/reproducibility/paper_3_reproduce.md`
- **Experiment Scripts:** `research/scripts/`
- **Raw Outputs:** `research/raw/`
- **Formatted Tables:** `research/tables/`
- **Figures:** `research/figures/`

