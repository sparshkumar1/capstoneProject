# Experiment 3 Summary — Formative Feedback Grounding & Actionability Comparison

**Experiment ID:** EXP-3
**Classification:** Formative Feedback Grounding Benchmark ($n=20$ paired evaluation turns)
**Execution Ledger:** **60 / 60 Completed Evaluations** ($100\%$ complete across all 3 preregistered conditions)
- `generic_template`: **20 / 20 COMPLETED**
- `structured_evaluator_recovery`: **20 / 20 COMPLETED**
- `qwen_7b_grounded_feedback`: **20 / 20 COMPLETED** (Executed on NVIDIA Tesla T4 GPU on Google Colab)

---

## 1. Observed Results

| Feedback Condition | Underlying Method / Model | Execution Status | Completed Turns | Mean Lexical Grounding | Grounding 95% Bootstrap CI | Mean Gap Coverage | Mean Actionable Directives | Mean Turn Latency |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Generic Template Baseline** | Score-Tier Boilerplate | **COMPLETED** | 20 | **0.0000** | [0.0000, 0.0000] | **0.0000 (0.0%)** | **1.00** | < 0.01s |
| **Structured Evaluator Recovery** | Non-LLM Rubric Structured Evaluator | **COMPLETED** | 20 | **0.0383** | [0.0059, 0.0919] | **1.0000 (100.0%)** | **3.90** | < 0.05s |
| **Qwen-7B Grounded Feedback** | Qwen2.5-7B-Instruct (bfloat16) | **COMPLETED** | 20 | **0.2496** | [0.1758, 0.3331] | **0.7250 (72.5%)** | **3.70** | 9.78s |

---

## 2. Statistical Analysis (Pairwise Wilcoxon Signed-Rank Tests with Holm-Bonferroni Correction)

### A. Lexical Transcript Grounding Ratio:
1. **Generic vs. Structured Recovery:** $W = 0.0, p_{\text{raw}} = 0.0431, p_{\text{holm}} = 0.0431, d = 0.3419$ (**Significant**).
2. **Generic vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{raw}} = 1.3121 \times 10^{-4}, p_{\text{holm}} = 3.9364 \times 10^{-4}, d = 1.3628$ (**Significant**).
3. **Structured Recovery vs. Qwen-7B Grounded:** $W = 15.0, p_{\text{raw}} = 1.2803 \times 10^{-3}, p_{\text{holm}} = 2.5607 \times 10^{-3}, d = 0.8903$ (**Significant**).

### B. Rubric Concept Gap Coverage:
1. **Generic vs. Structured Recovery:** $W = 0.0, p_{\text{raw}} = 1.9073 \times 10^{-6}, p_{\text{holm}} = 5.7220 \times 10^{-6}$ (**Significant**).
2. **Generic vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{raw}} = 1.9073 \times 10^{-6}, p_{\text{holm}} = 3.8147 \times 10^{-6}, d = 2.8408$ (**Significant**).
3. **Structured Recovery vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{raw}} = 9.1112 \times 10^{-4}, p_{\text{holm}} = 9.1112 \times 10^{-4}, d = 1.0775$ (**Significant**; Non-LLM Structured Recovery strictly exceeds Qwen-7B in gap coverage).

### C. Actionable Directives Count:
1. **Generic vs. Structured Recovery:** $W = 0.0, p_{\text{holm}} = 5.7220 \times 10^{-6}, d = 2.5911$ (**Significant**).
2. **Generic vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{holm}} = 3.8147 \times 10^{-6}, d = 2.2162$ (**Significant**).
3. **Structured Recovery vs. Qwen-7B Grounded:** $W = 51.0, p_{\text{raw}} = 0.6033, p_{\text{holm}} = 0.6033, d = 0.1133$ (**No significant difference**).

---

## 3. Infrastructure & Execution Provenance

- **Local Workstation CPU Benchmark:**
  - CPU: 12 cores, 15.68 GB RAM (0.00 GB VRAM).
  - Unquantized 7.61B parameter autoregressive generation in CPU bfloat16 emulation resulted in >22 minutes per turn due to memory swap thrashing.
  - Historical failure record preserved in [`research/results/raw/experiment_3_qwen_failed_infrastructure_log.json`](research/results/raw/experiment_3_qwen_failed_infrastructure_log.json).
- **Google Colab GPU Execution:**
  - GPU: NVIDIA Tesla T4 (14.56 GB Total VRAM, 14.19 GB Allocated).
  - Driver & CUDA: CUDA 12.8, PyTorch 2.11.0+cu128, Transformers 5.13.1, Python 3.12.13.
  - Mean generation latency on Tesla T4: **9.78s per turn** (~3.2 minutes total for 20 evaluations).
  - Provenance files: [`research/results/raw/experiment_3_qwen_raw.json`](research/results/raw/experiment_3_qwen_raw.json) and [`research/results/processed/experiment_3_qwen_processed.csv`](research/results/processed/experiment_3_qwen_processed.csv).

---

## 4. Interpretation

1. **Trade-Off Between Transcript Fluency and Concept Completeness:**
   - Qwen-7B achieves significantly higher verbatim transcript lexical grounding ($0.2496$ vs $0.0383$, $p=2.56 \times 10^{-3}$), reflecting natural synthesis and explicit quotation of candidate statements.
   - Non-LLM Structured Recovery achieves strictly higher rubric concept gap coverage ($100.0\%$ vs $72.5\%$, $p=9.11 \times 10^{-4}$), because deterministic concept tracking ($S_2 < 0.42$) surfaces all missing rubric markers without generative omission or stylistic abbreviation.
2. **Actionability Parity:**
   - Both Structured Recovery ($3.90$) and Qwen-7B ($3.70$) provide significantly more actionable remediation directives than static boilerplate templates ($1.00$), with no statistically significant difference between Structured Recovery and Qwen-7B ($p=0.6033$).
3. **Deployment Recommendation:**
   - Edge and low-resource deployments should utilize non-LLM Structured Evaluator Recovery for zero latency (<0.05s) and 100% gap coverage.
   - GPU-enabled deployments can incorporate Qwen-7B for enriched transcript quotation and natural language synthesis.

---

## 5. Limitations

1. **Automated Lexical Proxies:** Grounding metrics measure word-level transcript overlap and rubric concept strings; human educator ratings of feedback clarity and pedagogical utility were not collected in this run.
2. **No Longitudinal Retention Measurement:** Feedback utility is measured structurally on individual turns; candidate learning gains over repeated sessions remain unvalidated.
