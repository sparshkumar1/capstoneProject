# Paper 2 Evaluator Study: Official Execution Completion Report

**Date:** September 2026  
**Status:** **EXECUTION COMPLETE & AUDIT PASSED**  
**Target Milestone:** Paper 2 (*Evidence-Grounded Technical Interview Answer Evaluation with Entailment Dampening*)  
**Execution Script:** [`research/scripts/execute_paper2_study.py`](file:///c:/Users/spars/Downloads/PrepAIred/research/scripts/execute_paper2_study.py)  
**Primary Report:** [`research/results/paper2/PAPER2_FINAL_REPORT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/PAPER2_FINAL_REPORT.md)  

---

## 1. Execution Checksums & Environment Attestation

| Parameter / Artifact | Exact Value / Checksum | Verification Status |
| :--- | :--- | :---: |
| **Git Baseline Checkpoint** | Commit `375f4f869c47907d7c222d27df3b4f9e09dc8941` (Tag: `pre-paper2-execution`) | **MATCH** |
| **Human Gold Dataset** | `research/data/evaluator_benchmark/final_human_gold.csv`  <br>SHA-256: `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2` | **MATCH (IMMUTABLE)** |
| **Model Weights Checkpoint** | `services/evaluator/models/tuned_model2/model.safetensors`  <br>SHA-256: `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450` | **MATCH (IMMUTABLE)** |
| **Frozen Configuration** | `research/experiments/paper2/frozen_config.yaml`  <br>SHA-256: `f057baf1b2b9608eb0eb34d9aef3a4a3571db868f9ee728dda180364cc4e90f1` | **MATCH (IMMUTABLE)** |
| **Number of Evaluated Cases** | Exactly **$N = 64$** items (`BM-001` through `BM-064`, 0 missing, 0 excluded) | **COMPLETE** |
| **Runtime Environment** | Python 3.12.7 (Windows AMD64, PyTorch 2.2.2+cpu, Transformers 4.57.6, FAISS 1.13.2) | **VERIFIED** |

---

## 2. Primary Alignment Metric

- **Primary Metric:** Spearman rank correlation $\rho(\text{model\_score}, \text{human\_gold\_score})$ on $N=64$ paired benchmark cases.
- **Spearman $\rho$:** **$0.3812$**
- **Two-tailed $p$-value:** **$1.8863 \times 10^{-3}$** (statistically significant, $p < 0.01$)
- **95% Bootstrap Percentile Confidence Interval:** **$[0.1575, 0.5774]$**
- **Bootstrap Protocol:** Paired case-level resampling of $(y_{\text{gold}, i}, y_{\text{pred}, i})$ tuples ($B = 2,000$ iterations, random seed $42$).

---

## 3. Secondary Evaluation Metrics

| Metric | Point Estimate | 95% Bootstrap Percentile CI | $p$-value / Resampling Method |
| :--- | :---: | :---: | :--- |
| **Pearson $r$** | **0.4042** | $[0.1846, 0.5960]$ | $p = 9.2455 \times 10^{-4}$ (Paired case-level bootstrap, $B=2000$) |
| **Kendall $\tau$** | **0.2715** | $[0.1168, 0.4295]$ | $p = 1.7272 \times 10^{-3}$ (Paired case-level bootstrap, $B=2000$) |
| **Mean Absolute Error (MAE)** | **0.2920** | $[0.2431, 0.3457]$ | Case-level bootstrap ($B=2,000$, seed=42) |
| **Root Mean Squared Error (RMSE)** | **0.3601** | $[0.3008, 0.4184]$ | Case-level bootstrap ($B=2,000$, seed=42) |

---

## 4. 7-Way Component Ablation Matrix Summary

All seven pre-registered configurations were evaluated across the identical $N=64$ human gold benchmark cases without post-hoc tuning:

| Configuration | Formula | Spearman $\rho$ | 95% Bootstrap CI | Pearson $r$ | Kendall $\tau$ | MAE | RMSE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_1$ only (Semantic)** | `1.00 * S1` | 0.2070 | $[-0.0317, 0.4125]$ | 0.2430 | 0.1406 | 0.3171 | 0.3985 |
| **$S_2$ only (FAISS)** | `1.00 * S2` | 0.3021 | $[0.0492, 0.5337]$ | 0.3324 | 0.2562 | 0.3251 | 0.4421 |
| **$R$ only (CrossEncoder)** | `1.00 * R` | 0.4832 | $[0.2501, 0.6762]$ | 0.5080 | 0.3492 | 0.2763 | 0.3125 |
| **$S_1 + S_2$** | `0.30*S1 + 0.70*S2` | 0.2894 | $[0.0470, 0.4956]$ | 0.3240 | 0.2111 | 0.3042 | 0.4159 |
| **$S_1 + R$** | `0.23*S1 + 0.77*R` | 0.4884 | $[0.2624, 0.6751]$ | 0.5137 | 0.3460 | 0.2790 | 0.3198 |
| **$S_2 + R$** | `0.41*S2 + 0.59*R` | 0.4171 | $[0.1978, 0.6124]$ | 0.4540 | 0.3140 | 0.2674 | 0.3337 |
| **Full Composite** | `0.15*S1 + 0.35*S2_eff + 0.50*R` | **0.3812** | $[0.1575, 0.5774]$ | **0.4042** | **0.2715** | **0.2920** | **0.3601** |

---

## 5. Robustness & Containment Verification

- **Metamorphic Robustness (7 Relations, 21 Test Executions):**  
  **19/21 (90.5%) PASS**. Handled paraphrase invariance, irrelevant text addition, monotonic concept deletion, negation collapse, sentence reordering, and sentence duplication. (Two edge failures on pure keyword lists for multi-concept items where partial keyword hits remained bounded at $0.578$ and $0.664$).
- **Adversarial Containment (13 Attack Vectors):**  
  **11/13 (84.6%) CONTAINED**. Successfully contained instruction injection ($0.00$), score manipulation ($0.009$), keyword stuffing ($0.425$), buzzwords ($0.00$), fake authority ($0.00$), JSON formatting manipulation ($0.00$), and prompt repetitions. (Two partial breaches on complex sentence-level negation and contradiction clauses where the CrossEncoder awarded partial passage entailment of $0.43 - 0.46$).

---

## 6. Case-Level Error Analysis Summary

- **Distribution:** $N=64$ cases evaluated.
- **Top Overestimations:** Primarily in `verbose_wrong` ($+0.2193$) and subtle `contradictory` explanations ($+0.1279$) where high surface text density slightly inflated FAISS concept coverage.
- **Top Underestimations:** Concentrated in `concise_correct` ($-0.5154$) and `paraphrase` ($-0.4835$) where students provided terse, syntactically non-standard explanations that omitted secondary rubric keywords, triggering lower $S_2$ coverage.
- **Full Case Breakdown:** Preserved in [`research/results/paper2/paper2_error_analysis.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_error_analysis.csv).

---

## 7. Artifact Manifest & Verification

All 9 required Paper 2 artifacts exist and are fully populated in [`research/results/paper2/`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/):

1. [`paper2_case_level_results.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_case_level_results.csv) (64 rows, 15,059 bytes)
2. [`paper2_summary_results.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_summary_results.csv) (5 metric records, 406 bytes)
3. [`paper2_ablation_results.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_ablation_results.csv) (7 configurations, 1,511 bytes)
4. [`paper2_bootstrap_results.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_bootstrap_results.csv) (5 bootstrap distributions, 355 bytes)
5. [`paper2_metamorphic_results.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_metamorphic_results.csv) (21 metamorphic tests, 2,402 bytes)
6. [`paper2_adversarial_results.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_adversarial_results.csv) (13 attack vectors, 1,951 bytes)
7. [`paper2_error_analysis.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_error_analysis.csv) (64 error diagnoses, 16,398 bytes)
8. [`paper2_evaluator_raw.json`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/paper2_evaluator_raw.json) (full raw output dictionaries, 279,007 bytes)
9. [`PAPER2_FINAL_REPORT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper2/PAPER2_FINAL_REPORT.md) (comprehensive scientific report, 16,623 bytes)

---

## 8. Final Gate & Integrity Status

- **Integrity Status:** **PASSED / CLEAN**
- **Test Suite Status:** **213 PASSED**, 1 skipped, 0 failed.
- **Source Invariant:** Zero modifications to `final_human_gold.csv`, raw ratings, model weights, or production evaluator thresholds.
- **Conclusion:** Paper 2 empirical evaluation is 100% complete and frozen.

> ### 🛑 FINAL STOP CONDITION REACHED
> Paper 2 execution is finished. Per protocol, execution halts here.
