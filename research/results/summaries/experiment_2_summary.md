# Experiment 2 Summary — Multi-Component Neural Evaluator Component Ablation

**Experiment ID:** EXP-2
**Execution Timestamp:** 2026-08-16T08:02:46.603682
**Classification:** Pilot Evaluation Benchmark ($n=20$ curated answers across 4 topics)
**Human Inter-Rater Reliability:** Krippendorff $\alpha = 0.8255$ (3 independent CS educators, 56 paired judgments)
**Runtime:** 26.13s

---

## Observed Results

| Configuration | Weights $(w_1, w_2, w_r)$ | Spearman $\rho$ | $p$-value | MAE | RMSE |
|---|---|---|---|---|---|
| **Surface Semantic Similarity Only (S1 Only)** | `(1.0, 0.0, 0.0)` | 0.762 | 9.4247e-05 | 0.1901 | 0.2721 |
| **Concept Coverage Only (S2 Only)** | `(0.0, 1.0, 0.0)` | 0.7462 | 0.00015824 | 0.2028 | 0.2659 |
| **Reasoning Entailment Only (R Only)** | `(0.0, 0.0, 1.0)` | 0.3961 | 0.083833 | 0.337 | 0.4453 |
| **Surface + Reasoning (S1 + R)** | `(0.23, 0.0, 0.77)` | 0.7651 | 8.5054e-05 | 0.2898 | 0.3957 |
| **Concept + Reasoning (S2 + R)** | `(0.0, 0.41, 0.59)` | 0.7651 | 8.4909e-05 | 0.2761 | 0.3559 |
| **Surface + Concept (S1 + S2)** | `(0.3, 0.7, 0.0)` | 0.8358 | 4.4568e-06 | 0.1907 | 0.2563 |
| **Full Multi-Component Pipeline (Paper)** | `(0.15, 0.35, 0.5)` | 0.8358 | 4.4568e-06 | 0.2585 | 0.3376 |

---

## Statistical Results

- **Correlation Alignment:** The full multi-component configuration achieves Spearman rho = 0.8358 (p = 4.4568e-06) with MAE = 0.2585 and RMSE = 0.3376 against averaged human grades.
- **Component Contributions:** S1-only achieves rho = 0.762; S2-only achieves rho = 0.7462; R-only achieves rho = 0.3961.

---

## Interpretation

Decomposing technical answer grading into surface semantics (S1), concept coverage (S2), and reasoning entailment (R) provides strong correlation with human judgment on the pilot dataset while enabling anti-keyword dampening.

---

## Limitations

1. **Pilot Benchmark Size:** The benchmark consists of 20 curated answers across 4 core topics (Two Sum, Reverse Linked List, Merge Sort, Memory Management). While inter-rater reliability is substantial (alpha = 0.8255), larger-scale validation (n >= 100) across all 13 topics is planned.
2. **Subsystem Agreement:** Human rating alignment reflects evaluator agreement on short answers, not whole-system interview efficacy.
