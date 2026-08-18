# PrepAIred — Master Performance Analysis & Latency Characterization (Stage 23)

**Document ID:** `PERFORMANCE-ANALYSIS-STG23`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Scope:** Quantitative Latency, Computational Efficiency, Memory Profiling & Visual Result Analyses
**Execution Date:** 2026-08-17

---

## 1. Master Runtime Latency & Computational Profile

| Subsystem Component | Operational Engine | Compute Target | Mean Latency | 95th Percentile | Peak Process RAM | Output Type / Throughput |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Evaluator Pipeline ($S_1+S_2+R$)** | SBERT + FAISS + CrossEncoder | Local CPU (4 threads) | **124.5 ms** | 185.0 ms | ~450 MB | Structured Score $[0, 1]$ |
| **PPO Difficulty Controller** | Stable-Baselines3 MLP | Local CPU (1 thread) | **2.1 ms** | 4.8 ms | ~35 MB | Discrete Action $\{0, 1, 2\}$ |
| **Question Deduplication Engine** | 3-Level Jaccard & ID Filter | Local CPU (1 thread) | **<1.0 ms** | 1.5 ms | ~15 MB | Filtered Question Dict |
| **Docker C Coding Sandbox** | Docker Engine + GCC | Local Daemon | **48.2 ms** | 72.0 ms | 128 MB (cgroup) | Test Output & Diagnostics |
| **WhisperX Audio Transcriber** | Faster-Whisper + PyAnnote | CUDA GPU / CPU | **1.15 s** | 2.40 s | ~1.8 GB | Word-Aligned Transcript |
| **Non-LLM Structured Recovery** | Deterministic Rubric Mapper | Local CPU (1 thread) | **<0.05 s** | 0.08 s | ~25 MB | Remediation Directives |
| **Qwen-1.5B (Isolated Benchmark)**| `llama.cpp` (Q4_K_M) | Local CPU (12 threads) | **2.195 s** | 2.915 s | 1.36 GB | Benchmark Token Stream |
| **Qwen-1.5B (Integrated App Cases)**| `services/qwen/app.py` | Local CPU (12 threads) | **5.79 s - 7.73 s** | 8.58 s | 1.36 GB | Complete JSON Follow-Up |
| **Qwen-7B (Research EXP-3)** | Transformers bfloat16 | Tesla T4 GPU | **9.78 s** | 13.92 s | 14.53 GB | Grounded Feedback Turn |
| **Complete Closed-Loop Turn** | Integrated Production Pipeline | Local CPU + GGUF | **~2.10 s - 3.25 s** | ~4.50 s | System Nominal | Interactive Session Turn |

*Critical Operational Distinction: The isolated Qwen 1.5B benchmark evaluates raw token generation on targeted prompts (mean 2.195s @ 18.79 tok/s), whereas the integrated application flow executes full JSON schema validation and multi-field extraction (5.79s–7.73s).*

---

## 2. Visual Analysis of Publication Figures (Figures 1–8)

All 8 figures are generated at **300 DPI** using [`research/results/generate_paper_figures.py`](../research/results/generate_paper_figures.py):

### Figure 1: System Architecture Overview
- **File:** `research/results/figures/figure1_system_architecture.png`
- **Analysis:** Demonstrates strict microservice decoupling across React 18 frontend, FastAPI orchestrator, Evaluator service, PPO strategy, Docker sandbox, and Qwen inference.

### Figure 2: Candidate-State Adaptation Loop
- **File:** `research/results/figures/figure2_candidate_state_loop.png`
- **Analysis:** Illustrates the closed-loop MDP updating the 6D continuous state vector $[\mathbf{y}_t, \mathbf{\bar{y}}_t, \mathbf{c}_t, \mathbf{h}_t, \mathbf{\tau}_t, \mathbf{d}_t]$ with deterministic safety guardrails G1–G6.

### Figure 3: Experimental Methodology & Ledger
- **File:** `research/results/figures/figure3_experimental_methodology.png`
- **Analysis:** High-level schematic of all 5 pre-registered experimental tracks ($n=480$).

### Figure 4: Adaptive Difficulty Progression (EXP-1)
- **File:** `research/results/figures/figure4_adaptive_difficulty.png`
- **Analysis:** Scatter and distribution plot showing positive PPO difficulty adaptation ($\rho = +0.1572 \pm 0.08$) vs. Fixed ($\rho = 0.0$) and Rule-Based ($\rho = -0.2572$).

### Figure 5: Multi-Component Evaluator Ablation (EXP-2)
- **File:** `research/results/figures/figure5_evaluator_ablation.png`
- **Analysis:** Bar chart of Spearman correlation ($\rho = 0.8358$) and error metrics ($\text{MAE} = 0.2585$) across 7 evaluator configurations against blinded human raters ($\alpha = 0.8255$).

### Figure 6: Formative Feedback Trade-Offs (EXP-3)
- **File:** `research/results/figures/figure6_feedback_comparison.png`
- **Analysis:** Multi-panel visualization contrasting Qwen-7B's higher transcript lexical grounding ($0.2496$ vs. $0.0383$) against Structured Recovery's superior rubric gap coverage ($100.0\%$ vs. $72.5\%$) and sub-50ms latency.

### Figure 7: Question Personalization & Trajectory Divergence (EXP-4)
- **File:** `research/results/figures/figure7_personalization_divergence.png`
- **Analysis:** Trajectory divergence plot illustrating $d = 14.21$ separation between strong and weak candidate profiles and $0.0\%$ question repetition.

### Figure 8: Leave-One-Out Subsystem Decoupling (EXP-5)
- **File:** `research/results/figures/figure8_leave_one_out_ablation.png`
- **Analysis:** Radar/delta plot confirming isolated behavioral metric changes across all 7 leave-one-out conditions.
