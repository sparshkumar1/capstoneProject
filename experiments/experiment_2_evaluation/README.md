# Experiment 2 — Multi-Component Neural Evaluator Component Ablation Study

**Experiment ID:** EXP-2
**Target Submission:** IEEE ICALT 2026 / IEEE EDUCON 2026 (Section IV & VI-A)
**Priority:** **HIGH PRIORITY**

---

## 1. Research Question & Pre-Registered Hypothesis

- **Corrected Research Question:** Which components of the structured evaluator contribute to agreement with human ratings, and does the full multi-component evaluator provide measurable benefit over its individual components?
- **Pre-Registered Hypothesis:** Each component (S1 semantic similarity, S2 concept coverage, R CrossEncoder reasoning) contributes distinct, complementary assessment signals, with the full multi-component combination providing calibrated scores closely aligned with human ratings while preventing keyword gaming via reasoning dampening.

---

## 2. Seven Component Ablation Configurations

1. **Surface Semantic Similarity Only (S1 Only, $w=1.00$):** Single sentence-transformer bi-encoder (`all-MiniLM-L6-v2`) cosine similarity against rubric reference answer.
2. **Concept Coverage Only (S2 Only, $w=1.00$):** Pure FAISS concept matching against rubric logic markers ($\theta = 0.42$).
3. **Reasoning Quality Only (R Only, $w=1.00$):** Fine-tuned CrossEncoder NLI model (`tuned_model2`) on question-answer pair.
4. **Surface + Reasoning (S1 + R):** Bi-encoder similarity ($w=0.23$) + CrossEncoder reasoning ($w=0.77$).
5. **Concept + Reasoning (S2 + R):** Concept coverage ($w=0.41$) + CrossEncoder reasoning ($w=0.59$).
6. **Surface + Concept (S1 + S2):** Surface similarity ($w=0.30$) + Concept coverage ($w=0.70$).
7. **Full Multi-Component Pipeline (Paper):** $0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$ with anti-keyword dampening ($0.60 \times S_2$ when $R \le 0.30$).

---

## 3. Sample Size & Dataset Scope

- **Pilot Validation Benchmark ($n=20$):** 20 curated technical answers across 4 representative CS topics (`two_sum`, `reverse_linked_list`, `merge_sort`, `memory_management`) spanning 4 quality tiers (`blank`, `off_topic`, `partial`, `good`).
- **Human Ground Truth:** Graded by 3 independent CS educators on a 0–10 scale (blinded to model scores; inter-rater agreement: Krippendorff $\alpha = 0.8255$).
- **Sample Size Scope Statement:** The 20-sample study is explicitly classified as a **pilot evaluation benchmark**. An optional target expansion to $n \ge 100$ items across all 13 curriculum topics is pre-registered for future large-scale trials. No additional human ratings are fabricated.

---

## 4. Dependent Variables & Metrics

1. **Spearman Rank Correlation ($\rho$):** Rank-order alignment with averaged human rater scores.
2. **Two-Tailed $p$-Value:** Significance of rank correlation against null hypothesis ($\rho = 0$).
3. **Mean Absolute Error (MAE):** Average absolute deviation from human ratings on $[0, 1]$.
4. **Root Mean Squared Error (RMSE):** Quadratic penalty error metric.
5. **Monotonic Grade Separation:** Verification that $\text{Score}(\text{Good}) > \text{Score}(\text{Partial}) > \text{Score}(\text{Off-Topic}) \ge \text{Score}(\text{Blank})$.

---

## 5. Execution Command (Stage 16)

```bash
python experiments/experiment_2_evaluation/runner.py --config experiments/experiment_2_evaluation/config.json
```

*Results Status in Stage 15:* **RESULTS NOT YET GENERATED (Design & Pre-Registration Frozen)**
