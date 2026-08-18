# Stage 16.7 — EXP-3 Qwen-7B GPU Execution, Import, & Independent Verification Report

**Document ID:** `STAGE-16.7-REPORT`
**System:** PrepAIred Automated Technical Interview & Assessment Platform
**Experiment ID:** EXP-3 — Formative Feedback Grounding & Actionability Comparison
**Execution Hardware:** NVIDIA Tesla T4 GPU (Google Colab CUDA Environment)
**Final Status:** **`EXP-3 COMPLETE — 60/60 EVALUATIONS`**

---

## 1. Experiment Overview & Metadata
- **Experiment Identifier:** `EXP-3`
- **Model Identifier:** `Qwen/Qwen2.5-7B-Instruct`
- **Exact Model Revision:** `a09a35458c702b33eeacc393d103063234e8bc28`
- **Execution GPU:** NVIDIA Tesla T4 (14.56 GB Total VRAM, 14.19 GB Allocated)
- **CUDA Runtime Status:** `CUDA Available: True`, CUDA Version `12.8`
- **Environment Stack:** Python `3.12.13`, PyTorch `2.11.0+cu128`, Transformers `5.13.1`, Accelerate `0.30`
- **Total Evaluations Targeted:** 20 benchmark items
- **Total Evaluations Completed:** 20 benchmark items (100% completed on GPU)

---

## 2. Raw JSON & Processed CSV Verification
1. **Raw JSON Artifact:** [`research/results/raw/experiment_3_qwen_raw.json`](research/results/raw/experiment_3_qwen_raw.json)
   - Contains exactly 20 unique benchmark evaluation records.
   - All 20 items correspond to the pre-registered candidate answer transcripts and rubric definitions.
   - Every generated output is non-empty and directly attributable to `Qwen/Qwen2.5-7B-Instruct` operating in unquantized `bfloat16`.
   - Zero mock, placeholder, synthetic, or proxy outputs exist.
2. **Processed CSV Artifact:** [`research/results/processed/experiment_3_qwen_processed.csv`](research/results/processed/experiment_3_qwen_processed.csv)
   - Contains exactly 20 rows matching the raw JSON items.
   - Fully derived from raw JSON records with 100% field parity.
3. **Historical Failure Preservation:**
   - [`research/results/raw/experiment_3_qwen_failed_infrastructure_log.json`](research/results/raw/experiment_3_qwen_failed_infrastructure_log.json) remains strictly preserved as the historical record of the CPU-only swap thrashing bottleneck.

---

## 3. Independent Metric Recalculation Audit

Using the standalone independent verification script ([`experiments/experiment_3_feedback/import_qwen_colab_results.py`](experiments/experiment_3_feedback/import_qwen_colab_results.py)), all metrics were independently computed directly from the raw transcript tokens and generated feedback text:

| Metric | Colab-Reported Value | Independently Recalculated | Discrepancy / Delta | Audit Verification |
|---|:---:|:---:|:---:|:---:|
| **Mean Transcript Lexical Grounding** | `0.2496` | **0.2496** | `0.0000` | **MATCH (VERIFIED)** |
| **Grounding 95% Bootstrap CI** | `[0.1758, 0.3331]` | **[0.1758, 0.3331]** | `[0.0000, 0.0000]` | **MATCH (VERIFIED)** |
| **Mean Rubric Concept Gap Coverage** | `0.7250 (72.5%)` | **0.7250 (72.5%)** | `0.0000` | **MATCH (VERIFIED)** |
| **Mean Actionable Directives Count** | `3.70` | **3.70** | `0.00` | **MATCH (VERIFIED)** |
| **Mean Generation Latency (GPU)** | `9.78s` | **9.78s** | `0.00s` | **MATCH (VERIFIED)** |

---

## 4. Master EXP-3 Tri-Condition Ledger

| Feedback Condition | Underlying Architecture | Sample Scope | Mean Lexical Grounding | 95% Bootstrap CI | Mean Gap Coverage | Mean Actionable Directives | Mean Latency |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`generic_template`** | Score-Tier Static Boilerplate | 20 | **0.0000** | [0.0000, 0.0000] | **0.0%** (0.0000) | **1.00** | < 0.01s |
| **`structured_evaluator_recovery`** | Non-LLM Rubric Evaluator | 20 | **0.0383** | [0.0059, 0.0919] | **100.0%** (1.0000) | **3.90** | < 0.05s |
| **`qwen_7b_grounded_feedback`** | Qwen2.5-7B-Instruct (Tesla T4) | 20 | **0.2496** | [0.1758, 0.3331] | **72.5%** (0.7250) | **3.70** | 9.78s |
| **Total EXP-3 Scope** | **All 3 Pre-Registered Conditions** | **60** | — | — | — | — | — |

---

## 5. Statistical Comparison (Paired Wilcoxon Signed-Rank Tests with Holm-Bonferroni Correction)

### A. Transcript Lexical Grounding Ratio:
- **Generic Template vs. Structured Recovery:** $W = 0.0, p_{\text{raw}} = 0.0431, p_{\text{holm}} = 0.0431, d = 0.3419$ (**Significant**).
- **Generic Template vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{raw}} = 1.3121 \times 10^{-4}, p_{\text{holm}} = 3.9364 \times 10^{-4}, d = 1.3628$ (**Significant**).
- **Structured Recovery vs. Qwen-7B Grounded:** $W = 15.0, p_{\text{raw}} = 1.2803 \times 10^{-3}, p_{\text{holm}} = 2.5607 \times 10^{-3}, d = 0.8903$ (**Significant**).
- *Finding:* Qwen-7B achieves significantly higher transcript lexical grounding than both non-LLM structured recovery and generic boilerplate templates.

### B. Rubric Concept Gap Coverage:
- **Generic Template vs. Structured Recovery:** $W = 0.0, p_{\text{raw}} = 1.9073 \times 10^{-6}, p_{\text{holm}} = 5.7220 \times 10^{-6}$ (**Significant**).
- **Generic Template vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{raw}} = 1.9073 \times 10^{-6}, p_{\text{holm}} = 3.8147 \times 10^{-6}, d = 2.8408$ (**Significant**).
- **Structured Recovery vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{raw}} = 9.1112 \times 10^{-4}, p_{\text{holm}} = 9.1112 \times 10^{-4}, d = 1.0775$ (**Significant**).
- *Critical Scientific Finding (Unfavorable Finding Preserved):* Non-LLM Structured Recovery achieves **strictly higher rubric concept gap coverage ($100.0\%$) than Qwen-7B ($72.5\%$)**, because deterministic concept tracking ($S_2 < 0.42$) surfaces all missing rubric markers without generative omission or stylistic abbreviation.

### C. Actionable Directives Count:
- **Generic Template vs. Structured Recovery:** $W = 0.0, p_{\text{holm}} = 5.7220 \times 10^{-6}, d = 2.5911$ (**Significant**).
- **Generic Template vs. Qwen-7B Grounded:** $W = 0.0, p_{\text{holm}} = 3.8147 \times 10^{-6}, d = 2.2162$ (**Significant**).
- **Structured Recovery vs. Qwen-7B Grounded:** $W = 51.0, p_{\text{raw}} = 0.6033, p_{\text{holm}} = 0.6033, d = 0.1133$ (**No statistically significant difference**).

---

## 6. Scientific Interpretation & Architectural Trade-Offs

1. **Transcript Grounding vs. Concept Completeness Trade-Off:**
   - **Qwen-7B Advantage:** Generative LLM feedback excels at contextual phrasing, verbatim quoting of candidate expressions, and fluent instructional scaffolding ($0.2496$ grounding ratio).
   - **Non-LLM Structured Recovery Advantage:** Deterministic rubric concept extraction achieves 100% gap coverage at near-zero latency (<0.05s) without requiring GPU accelerators or incurring generative omission risks.
2. **Actionability Parity:**
   - Both Structured Recovery ($3.90$) and Qwen-7B ($3.70$) provide significantly more actionable remediation directives than static boilerplate templates ($1.00$).
3. **Deployment Guidance:**
   - In resource-constrained environments (client-side or edge CPUs), Non-LLM Structured Evaluator Recovery is the superior operational choice.
   - In cloud GPU deployments, Qwen-7B provides natural conversational feedback that is statistically grounded in candidate transcripts.

---

## 7. Limitations
1. **Automated Lexical Proxies:** Grounding metrics evaluate token overlap and rubric string matching rather than human pedagogical perception.
2. **Cross-Session Retention:** EXP-3 evaluates single-turn formative guidance; candidate skill improvement across repeated interviews requires future longitudinal user studies.

---

## 8. Complete 5-Experiment Repository Audit

| Experiment ID | Title | Planned Protocol | Completed Runs | Status Label | Key Result |
|:---:|---|:---:|:---:|:---:|---|
| **EXP-1** | Adaptive Difficulty Controller | 150 | 150 | **`EXPERIMENTALLY VALIDATED`** | PPO adaptation $\rho = +0.1572 \pm 0.08$ vs Fixed $\rho = 0.0$ and Rule $\rho = -0.2572$ ($p = 5.30 \times 10^{-8}$). |
| **EXP-2** | Evaluator Component Ablation | 140 | 140 | **`EXPERIMENTALLY VALIDATED`** | Spearman $\rho = 0.8358, p = 4.46 \times 10^{-6}$; $S_1+S_2$ MAE $0.1907$ vs Full Pipeline $0.2585$. |
| **EXP-3** | Formative Feedback Grounding | 60 | 60 | **`EXPERIMENTALLY VALIDATED`** | Qwen-7B grounding $0.2496$ ($p < 0.01$); Structured Recovery gap coverage $100\%$ ($p < 0.001$). |
| **EXP-4** | Personalization & Divergence | 60 | 60 | **`EXPERIMENTALLY VALIDATED`** | 3-level deduplication $0.0\%$ repetition vs $6.0\%$ random ($p < 0.001$); trajectory divergence $d = 14.21$. |
| **EXP-5** | Leave-One-Out Ablation | 70 | 70 | **`EXPERIMENTALLY VALIDATED`** | Component isolation verified ($\rho \to 0.0$ on RL removal; probes $\to 0.00$ on follow-up removal). |
| **Total** | **All Pre-Registered Conditions** | **480** | **480** | **100% COMPLETE** | **All 480 experimental sessions verified from raw machine-readable JSON.** |

---

## 9. Claims Matrix Update (`docs/CLAIMS_CHECK.md`)

- **Claim #11 (Formative Feedback Grounding & Actionability):** Upgraded to **`EXPERIMENTALLY VALIDATED`** for the evaluated benchmark scope ($n=20$ turns across 3 conditions).
- **Prohibited Overstatement:** Prohibits claiming whole-system hiring improvements or generalized human retention without longitudinal participant data.
- **Authoritative Taxonomy Counts:**
  - `IMPLEMENTED`: 0
  - `TESTED`: 8
  - `EXPERIMENTALLY VALIDATED`: 6
  - `HUMAN VALIDATED`: 1 (Human Inter-Rater Reliability $\alpha=0.8255$)
  - `NOT YET VALIDATED`: 1 (Whole-System Human Interview Efficacy)
  - **Total:** Exactly 16 claim rows ($0 + 8 + 6 + 1 + 1 = 16$).

---

## 10. Regression Test Verification Results

### Backend Pytest Suite:
- **EXP-3 Unit Suite:** `pytest tests/unit/test_qwen_followup_feedback.py -v` $\to$ **14 passed, 0 failed, 4 warnings** in 42.17s.
- **Backend Full Suite:** `.venv\Scripts\python.exe -m pytest tests\unit\ tests\integration\ -v` $\to$ **178 passed, 0 failed, 44 warnings** in 356.88s (100% pass).

### Frontend Vitest Suite:
- **Frontend Test Suite:** `npm run --prefix apps/web test:ci` $\to$ **7 passed, 0 failed** in 1.86s (100% pass).

---

## 11. Modified & Created Artifacts
1. [`research/results/raw/experiment_3_qwen_raw.json`](research/results/raw/experiment_3_qwen_raw.json) — Authoritative raw Qwen-7B GPU inference outputs (20/20).
2. [`research/results/processed/experiment_3_qwen_processed.csv`](research/results/processed/experiment_3_qwen_processed.csv) — Derived processed CSV.
3. [`research/results/tables/experiment_3_results.csv`](research/results/tables/experiment_3_results.csv) — 3-condition empirical comparison table.
4. [`research/results/summaries/experiment_3_summary.md`](research/results/summaries/experiment_3_summary.md) — Comprehensive EXP-3 statistical summary.
5. [`research/results/verification/verification_report.md`](research/results/verification/verification_report.md) — Master 5-experiment replication audit.
6. [`docs/CLAIMS_CHECK.md`](docs/CLAIMS_CHECK.md) — Authoritative claims matrix.
7. [`docs/stage16_7_exp3_qwen_verification.md`](docs/stage16_7_exp3_qwen_verification.md) — Stage 16.7 authoritative verification report.

---

## 12. Final Status Declaration

```
================================================================================
EXP-3 = COMPLETE
Generic Template Baseline      = 20 / 20 COMPLETED
Structured Evaluator Recovery  = 20 / 20 COMPLETED
Qwen-7B Grounded Feedback      = 20 / 20 COMPLETED (Tesla T4 GPU)
Total EXP-3 Evaluations        = 60 / 60 COMPLETED (100%)
================================================================================
```

- **All 480 pre-registered experimental runs across EXP 1–5 are 100% completed and mathematically verified.**
- **Stage 17 (Paper Writing) has NOT been started.**
- **Execution is stopped cleanly in accordance with the Stage 16.7 stop condition.**
