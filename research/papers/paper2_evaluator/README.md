# Paper 2: Grounded Technical Evaluator & Multi-Signal Scoring

- **Working Title:** *Evidence-Grounded Technical Answer Evaluation Using Semantic, Concept, and Reasoning Signals*
- **Target Venues:** **ICTCS 2026** (Ahmedabad) / **IEEE Transactions on Education (ToE)**
- **Domain:** Natural Language Processing, Educational Assessment, Information Retrieval

---

## 1. Abstract
Automated grading of free-form technical explanations in computer science typically relies on lexical keyword matching (vulnerable to cheating) or generative LLM prompting (vulnerable to hallucination and inconsistency). We present a grounded, multi-signal evaluation framework that synergizes semantic sentence embeddings ($S_1$, SBERT), fast rubric concept indexing ($S_2$, FAISS inner-product search), and deep cross-encoder reasoning entailment ($R$, MiniLM). To counter adversarial exploitation, we introduce reasoning-conditioned concept dampening, which discounts concept coverage by 40% when reasoning entailment falls below a calibrated threshold ($R \le 0.30$). Evaluated against expert human educator ratings across standard Data Structures and Algorithms questions, the multi-signal model achieves Spearman correlation $\rho = 0.6975$ ($p = 6.29 \times 10^{-4}$) and Pearson $r = 0.7290$, substantially outperforming single-signal baselines. Extensive sensitivity sweeps analyze concept detection boundaries, and metamorphic testing across five relation classes proves strong semantic invariance, monotonicity, and resistance to adversarial keyword stuffing.

---

## 2. Core Contributions
1. **Multi-Signal Tripartite Technical Scoring Model:** Synergizes $S_1$ (semantic relevance), $S_2$ (concept coverage), and $R$ (reasoning entailment) into an evidence-grounded scoring metric ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$).
2. **Reasoning-Conditioned Concept Dampening:** Penalizes ungrounded keyword stuffing by dynamically scaling concept coverage when logical coherence is absent.
3. **FAISS Vector Rubric Indexing:** Enables sub-second retrieval of structured rubric concept groups, mandatory constraints, and common misconceptions.
4. **Empirical Validation & Metamorphic Suite:** Evaluated across human educator benchmarks, threshold sensitivity curves, adversarial keyword injections, and 5-relation metamorphic tests.

---

## 3. Associated Empirical Assets
- **Table 1:** 7-Way Evaluator Component Ablation (`research/tables/table_eval_ablation.md`)
- **Table 2:** Adversarial Keyword-Stuffing Resistance (`research/tables/table_eval_adversarial.md`)
- **Table 3:** Concept Threshold Sensitivity Sweep (`research/tables/table_eval_threshold.md`)
- **Table 4:** Metamorphic Robustness Testing Suite (`research/tables/metamorphic_results.md`)
- **Table 5:** Qualitative Error Analysis & Confusion Matrix (`research/tables/table_eval_error_analysis.md`)
- **Figure 1:** Component Ablation Comparison (`research/figures/eval_ablation_comparison.png`)
- **Figure 2:** Threshold Sensitivity Precision-Recall Curve (`research/figures/eval_threshold_sensitivity.png`)
