# PREPAIred — Master Research Repository & Scientific Evidence Package

**Audited Commit:** `9cfd34f`  
**System Verification:** **205/205 backend tests passed (100%)** | **20/20 frontend vitest passed (100%)** | **Vite build passed**  
**Role:** Canonical starting point for researchers, reviewers, and AI assistants (Claude).

---

## 1. Project Description
**PREPAIred** is an evidence-grounded adaptive multimodal technical assessment and tutoring framework. It dynamically evaluates free-form natural language answers to Data Structures and Algorithms (DSA) questions and C programming code. The system adaptively adjusts interview difficulty using reinforcement learning while maintaining an asynchronous hub-and-spoke architecture that insulates technical grading from free-form LLM hallucinations.

---

## 2. Current System Architecture
- **Orchestrator (`agents/orchestrator/`):** Asynchronous hub-and-spoke session controller with a Socratic follow-up finite state machine.
- **Technical Evaluator (`services/evaluator/`):** Tripartite NLP scoring engine ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$) combining SBERT embeddings, FAISS concept indexing, and CrossEncoder reasoning entailment.
- **Coding Sandbox (`agents/coding_executor/`):** Ephemeral Docker container enforcing `--cap-drop=ALL`, `--net=none`, non-root UID 1001, tmpfs `/workspace`, 128MB RAM, 32 PIDs, and 2.0s timeout.
- **PPO Controller (`rl/` & `agents/strategy/`):** 6D candidate state ($[perf, avg\_perf, conf, hes, dim4, diff]^T$) with post-hoc pedagogical guardrails (G1–G4).
- **Grounded Feedback Generator (`services/qwen/`):** Local Qwen2.5-1.5B-Instruct running on CPU, strictly grounded in evaluator claims with deterministic fallback.
- **Multi-Attempt Persistence (`services/storage/`):** SQLite in Write-Ahead Logging (`WAL`) mode tracking attempts, best attempts, and learning gaps.

---

## 3. Current Verified Scientific Truth & Metrics

| Metric / Dimension | Verified Value | Empirical Nature & Sample | Authoritative Evidence File |
|:---|:---:|:---|:---|
| **Evaluator Human Correlation** | **$\rho = 0.6975$** ($p = 6.29 \times 10^{-4}$) | 1 Real CS Educator ($N=20$) | [`research/results/paper2_final_results.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2_final_results.md) |
| **Evaluator Pearson Correlation** | **$r = 0.7290$** ($p = 3.03 \times 10^{-4}$) | 1 Real CS Educator ($N=20$) | [`research/results/paper2_final_results.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2_final_results.md) |
| **Evaluator Mean Absolute Error** | **$\text{MAE} = 0.2245$** | 1 Real CS Educator ($N=20$) | [`research/tables/table_eval_threshold.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_eval_threshold.md) |
| **PPO Volatility vs Heuristic** | **$0.451$ vs $0.573$ (-21.3%)** | 100 sessions, 20 seeds ($p=0.0028$) | [`research/tables/table_rl_policy_comparison.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_rl_policy_comparison.md) |
| **Dimension 4 Action Agreement** | **80.50%** | Progress vs Response Time | [`research/tables/table_rl_dim4_analysis.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_rl_dim4_analysis.md) |
| **PPO Training Duration** | **300,000 steps** | SB3 MlpPolicy checkpoint | [`rl/training/retrain_quick.py`](file:///c:/Users/spars/Downloads/PrepAIred/rl/training/retrain_quick.py) |
| **Sandbox Negative Security** | **9 / 9 vectors contained** | Pre-flight + Kernel containment | [`research/tables/table_sys_security_boundary.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_sys_security_boundary.md) |
| **Evaluator Median Latency** | **167.59 ms** | 50 iterations | [`research/tables/table_sys_latency_benchmark.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_sys_latency_benchmark.md) |
| **PPO Median Inference Latency**| **0.64 ms** | 50 iterations | [`research/tables/table_sys_latency_benchmark.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_sys_latency_benchmark.md) |
| **Turn Operational Resilience** | **100% (0 crashes)** | 6 component ablation modes | [`research/tables/table_sys_architectural_ablation.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_sys_architectural_ablation.md) |

---

## 4. Known Scientific Limitations
1. **Pilot Human Ground Truth ($N=20$):** Single-educator ground truth provides initial validation ($\rho=0.6975, \text{CI: } [0.440, 0.837]$, note: $\rho=0.7400$ was superseded as an uncalibrated static CSV artifact); multi-rater expansion is prepared in `research/annotation/`.
2. **Dimension 4 Covariate Shift:** Simulator trained with response time while runtime uses turn progress ($80.5\%$ action agreement, $0.020$ difficulty discrepancy).
3. **CrossEncoder Collocations:** Ungrammatical keyword bags with dense multi-word phrases can achieve partial entailment ($R \approx 0.46 - 0.52$), bounded by ScoreValidator caps.
4. **Cold-Start Docker Overhead:** Container startup adds ~1.5s latency per compilation turn.

---

## 5. Three-Paper Publication Strategy

```
                          +------------------------+
                          ¦   PREPAIred Codebase   ¦
                          ¦   (Source of Truth)    ¦
                          +------------------------+
         +----------------------------+----------------------------+
         ?                            ?                            ?
+------------------+         +------------------+         +------------------+
¦     Paper 1      ¦         ¦     Paper 2      ¦         ¦     Paper 3      ¦
¦ Systems/Security ¦         ¦   NLP Evaluator  ¦         ¦   Adaptive RL    ¦
+------------------¦         +------------------¦         +------------------¦
¦ ATIS 2026        ¦         ¦ ICTCS 2026       ¦         ¦ SmartCom 2027    ¦
¦ (Nov 7 deadline) ¦         ¦ (Ahmedabad)      ¦         ¦ (Goa, Jan 2027)  ¦
¦ / IEEE Access    ¦         ¦ / IEEE ToE       ¦         ¦ / ICMLSC 2027    ¦
+------------------+         +------------------+         +------------------+
```

- **Paper 1 (Systems, Security & Fault Tolerance):** [`research/papers/paper1_systems/`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/paper1_systems/)  
  *Venue:* **ATIS 2026** (Bengaluru, Nov 7 deadline) / *IEEE Access*.  
  *Core Evidence:* Architecture, Docker sandbox containment (`SEC-01` to `SEC-09`), subsystem latencies, single-component removal reliability.
- **Paper 2 (Grounded Technical Evaluator):** [`research/papers/paper2_evaluator/`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/paper2_evaluator/)  
  *Venue:* **ICTCS 2026** (Ahmedabad) / *IEEE Transactions on Education (ToE)*.  
  *Core Evidence:* Multi-signal scoring ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$), FAISS index, concept dampening, 7-way ablation, metamorphic suite (`MG-1` to `MG-5`).
- **Paper 3 (Guardrailed Reinforcement Learning):** [`research/papers/paper3_rl/`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/paper3_rl/)  
  *Venue:* **SmartCom 2027** (Goa, Jan 2027) / *ICMLSC 2027*.  
  *Core Evidence:* 6D state representation, PPO controller, 21% volatility reduction vs heuristic baselines, speech noise stability, dimension 4 domain transfer.

---

## 6. Directory Map & Artifact Locations

| Artifact Type | Directory / Path | Description |
|:---|:---|:---|
| **Authoritative Scientific Truth** | [`research/CANONICAL_SCIENTIFIC_TRUTH.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/CANONICAL_SCIENTIFIC_TRUTH.md) | Verified metrics, formulas, and constraints |
| **Claude Navigation Index** | [`research/CLAUDE_RESEARCH_INDEX.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/CLAUDE_RESEARCH_INDEX.md) | Priority reading guide and routing matrix for AI |
| **Forensic Audits** | [`research/audit/`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/) | Claims, test manifests, data leakage, threat model, equations |
| **Benchmark & Datasets** | [`research/data/evaluator_benchmark/`](file:///c:/Users/spars/Downloads/PrepAIred/research/data/evaluator_benchmark/) | Curated evaluation test cases and questions |
| **Annotation Package** | [`research/annotation/`](file:///c:/Users/spars/Downloads/PrepAIred/research/annotation/) | Blinded template, rater guidelines, agreement script |
| **Experiment Scripts** | [`research/scripts/`](file:///c:/Users/spars/Downloads/PrepAIred/research/scripts/) | Evaluator, metamorphic, RL, and systems experiment runners |
| **Raw JSON Outputs** | [`research/raw/`](file:///c:/Users/spars/Downloads/PrepAIred/research/raw/) | Machine-readable experiment outputs |
| **Result Tables** | [`research/tables/`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/) | Publication markdown tables with statistics and CIs |
| **Result Figures** | [`research/figures/`](file:///c:/Users/spars/Downloads/PrepAIred/research/figures/) | High-resolution publication plots |
| **Reproducibility Guides** | [`research/reproducibility/`](file:///c:/Users/spars/Downloads/PrepAIred/research/reproducibility/) | Environment manifests and reproduction commands |
| **Superseded Docs Register** | [`research/audit/SUPERSEDED_DOCUMENTS.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/SUPERSEDED_DOCUMENTS.md) | Historical files marked "DO NOT USE AS CURRENT TRUTH" |
| **Archived Manuscripts & Reports**| [`research/papers/archived/`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/archived/) & [`research/archive/`](file:///c:/Users/spars/Downloads/PrepAIred/research/archive/) | Deprecated monolithic drafts and legacy stage audits |

---

## 7. How to Reproduce All Experiments

```powershell
# 1. Activate Environment
.venv\Scripts\Activate.ps1

# 2. Run Baseline Engineering Tests (205 tests)
pytest tests/ -q

# 3. Paper 2: Technical Evaluator Experiments & Metamorphic Suite
python research/scripts/run_evaluator_experiments.py
python research/scripts/run_metamorphic_tests.py
python research/scripts/analyze_human_ratings.py

# 4. Paper 3: RL Adaptive Difficulty & Baseline Experiments
python research/scripts/run_rl_experiments.py

# 5. Paper 1: Systems Security Negative Tests & Latency Profiling
python research/scripts/run_systems_experiments.py
```

---

## 8. Authoritative vs Non-Authoritative Files

### Authoritative Files (Use as Ground Truth)
- All files in [`research/CANONICAL_SCIENTIFIC_TRUTH.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/CANONICAL_SCIENTIFIC_TRUTH.md)
- All files in [`research/audit/`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/)
- All markdown tables in [`research/tables/`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/)
- Active paper packages in [`research/papers/paper{1,2,3}_*/`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/)

### Non-Authoritative / Superseded Files (DO NOT CITE AS CURRENT TRUTH)
- Any file in [`research/papers/archived/`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/archived/) or [`research/archive/`](file:///c:/Users/spars/Downloads/PrepAIred/research/archive/)
- Any file listed in [`research/audit/SUPERSEDED_DOCUMENTS.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/SUPERSEDED_DOCUMENTS.md)
- Any claims of $\rho = 0.9152$ or $\rho = 0.8358$ as "human correlation"
- Any claims of 204,800 PPO training steps

