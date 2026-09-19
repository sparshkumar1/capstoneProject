# PREPAIred — Frozen Human Rating & Adjudication Protocol

**Date:** September 2026  
**Status:** Pre-specified and frozen before human annotation  
**Applicability:** 64-Case Evaluator Benchmark Study (Paper 2)  
**Raters:** 3 Independent Computer Science Educators / Technical Interviewers (`RATER_1`, `RATER_2`, `RATER_3`)

---

## 1. Scale Specification

- **Scale Type:** Bounded Continuous Interval $[0.00, 1.00]$.
- **Anchor Bands (as defined in `SCORING_RUBRIC.md`):**
  - $[0.85, 1.00]$: Optimal / Complete
  - $[0.65, 0.84]$: Correct / Suboptimal or Minor Gaps
  - $[0.40, 0.64]$: Partial / Incomplete
  - $[0.15, 0.39]$: Superficial / Misconception
  - $[0.00, 0.14]$: Unacceptable / Off-Topic
- **Precision:** Continuous floating-point decimals (standard increments of $0.05$ or $0.10$ encouraged; exact decimals permitted).

---

## 2. Frozen Inter-Rater Agreement Metrics

Because human ratings are collected on a continuous interval scale $[0.00, 1.00]$, discrete agreement statistics (such as Cohen's $\kappa$ or Fleiss' $\kappa$) are mathematically inappropriate without artificial quantization.

The following continuous inter-rater reliability (IRR) statistics are pre-specified and frozen before human annotation:

### 2.1 Primary Reliability Metric: Two-Way Random Intraclass Correlation Coefficient
Following McGraw & Wong (1996) and Shrout & Fleiss (1979):
1. **$\text{ICC}(2, 1)$ — Single-Rater Absolute Agreement:**
   $$\text{ICC}(2, 1) = \frac{\text{MS}_R - \text{MS}_E}{\text{MS}_R + (k-1)\text{MS}_E + \frac{k}{n}(\text{MS}_C - \text{MS}_E)}$$
   Measures the reliability of ratings from any single individual rater.
2. **$\text{ICC}(2, k)$ — Average-Measures Absolute Agreement:**
   $$\text{ICC}(2, k) = \frac{\text{MS}_R - \text{MS}_E}{\text{MS}_R + \frac{\text{MS}_C - \text{MS}_E}{n}}$$
   Measures the reliability of the pooled mean score across all $k = 3$ raters (the final ground-truth target).
- **Target Thresholds:**
  - $\text{ICC} \ge 0.75$: Excellent agreement.
  - $0.60 \le \text{ICC} < 0.75$: Good agreement.
  - $0.40 \le \text{ICC} < 0.60$: Moderate agreement.

### 2.2 Secondary Reliability Metric: Krippendorff's Alpha (Interval Metric)
- **$\alpha_{\text{interval}}$**: Computed using the squared difference metric $d_{ck}^2 = (c - k)^2$ over the continuous values.
- Validates agreement against chance across the 64 benchmark cases.

### 2.3 Pairwise Correlational & Error Metrics
For all rater pairs $(R_1, R_2)$, $(R_1, R_3)$, and $(R_2, R_3)$:
- **Pairwise Spearman's Rank Correlation ($\rho$)**
- **Pairwise Pearson's Correlation ($r$)**
- **Mean Absolute Difference ($\text{MAD}$):**
  $$\text{MAD}(j, k) = \frac{1}{64} \sum_{i=1}^{64} |s_{ij} - s_{ik}|$$

---

## 3. Disagreement Threshold

For each benchmark item $i \in \{1, \dots, 64\}$:
$$\Delta_{\max}(i) = \max_{j, k \in \{1, 2, 3\}} |s_{ij} - s_{ik}|$$

- **Consensus Condition ($\Delta_{\max}(i) \le 0.20$):**
  The scores from all three raters are within $0.20$ of one another (i.e., within one rubric anchor band).
- **Disagreement Condition ($\Delta_{\max}(i) > 0.20$):**
  The spread between the lowest and highest score exceeds $0.20$ (spanning more than an entire qualitative rubric tier, e.g. one rater marking "Optimal" ($0.85$) while another marks "Partial" ($0.60$)).  
  **The item is automatically flagged with `HUMAN_ADJUDICATION_REQUIRED = true`.**

---

## 4. Frozen Adjudication Rule

The adjudication rule is strictly frozen as follows:

```
If max pairwise difference <= 0.20:
    final gold = arithmetic mean of the 3 ratings:
    y_i = (s_{i,1} + s_{i,2} + s_{i,3}) / 3

If max pairwise difference > 0.20:
    mark HUMAN_ADJUDICATION_REQUIRED = true
    do NOT automatically choose mean/median
```

### Invariants:
1. **Preserve All Original Ratings:** All 3 original ratings ($s_{i, 1}, s_{i, 2}, s_{i, 3}$) and their associated `rater_comments` are permanently retained in the dataset.
2. **No Automated Resolution for Divergent Items:** The automated pipeline will **NOT** automatically default to either the mean or median for items where $\Delta_{\max} > 0.20$.
3. **Human Adjudication Protocol (HUMAN GATE 3):** Any item flagged with `HUMAN_ADJUDICATION_REQUIRED = true` is held for formal human adjudication by the expert educator committee during **HUMAN GATE 3**.

---

## 5. Freezing & Tamper-Proof Safeguards

- This protocol is pre-specified and frozen before human annotation.
- **Under no circumstances may the adjudication rule, agreement formula, or $\Delta_{\max} > 0.20$ threshold be altered post-hoc after ratings are inspected.**
