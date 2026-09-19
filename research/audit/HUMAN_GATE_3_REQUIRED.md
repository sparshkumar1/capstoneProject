# HUMAN GATE 3 REQUIRED: Benchmark Adjudication Disagreement Log

**Status:** **HUMAN GATE 3 REQUIRED (10 Cases Exceed Disagreement Threshold $\Delta_{\max} > 0.20$)**  
**Audit Date:** September 2026  
**Protocol Reference:** `research/annotation/HUMAN_RATING_PROTOCOL.md`  
**Agreement Results Dataset:** `research/results/human_agreement_results.csv`  
**Total Benchmark Cases:** $N = 64$  
**Cases Requiring Adjudication:** 10  
**Consensus Cases ($\Delta_{\max} \le 0.20$):** 54

---

## 1. Adjudication Cases Log

In accordance with the frozen protocol, cases where the maximum pairwise difference between any two human raters exceeds $0.20$ are held for formal human adjudication.

Under the scientific blinding invariant, **no automated system scores or model predictions are included or utilized**.

| Case ID | Rater 1 Score | Rater 2 Score | Rater 3 Score | Max Pairwise Difference ($\Delta_{\max}$) | Adjudication Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **BM-006** | 0.25 | 0.10 | 0.34 | 0.2400 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-014** | 0.30 | 0.10 | 0.38 | 0.2800 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-019** | 0.45 | 0.50 | 0.78 | 0.3300 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-022** | 0.30 | 0.10 | 0.36 | 0.2600 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-030** | 0.30 | 0.10 | 0.35 | 0.2500 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-038** | 0.35 | 0.10 | 0.39 | 0.2900 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-046** | 0.35 | 0.10 | 0.39 | 0.2900 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-051** | 0.40 | 0.45 | 0.71 | 0.3100 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-054** | 0.35 | 0.10 | 0.39 | 0.2900 | `HUMAN_ADJUDICATION_REQUIRED` |
| **BM-062** | 0.35 | 0.10 | 0.40 | 0.3000 | `HUMAN_ADJUDICATION_REQUIRED` |

---

## 2. Next Step: Human Gate 3 Resolution

> **STOPPING AT HUMAN GATE 3:**  
> In accordance with research protocol:
> 1. No automated mean or median is assigned to these 10 divergent cases.
> 2. The three human educators / expert committee must review the qualitative comments and reconcile these 10 items.
> 3. Automated model-vs-human evaluation for Paper 2 **MUST NOT RUN** until Human Gate 3 is resolved by human adjudicators.
