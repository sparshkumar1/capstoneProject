# Evaluator Data Lineage, Split Protocol, and Leakage Investigation

**Audited Commit:** `9cfd34f`  
**Purpose:** Reconstruct the complete end-to-end data lineage of the technical evaluator and audit all potential avenues of test leakage.

---

## 1. End-to-End Evaluator Data Lineage

```
Raw Question Bank (`data/questions/qns.json`: 100 questions, 13 topics)
           ¦
           ?
Expert Rubric Formulation (`data/rubrics/rubrics_final_clean.json`: 100 rubrics)
           ¦
           +-------------------------------+
           ?                               ?
SBERT Concept Encoding              General Text Ranking Corpus (MS MARCO)
(all-MiniLM-L6-v2, Frozen)                         ¦
           ¦                                       ?
           ?                               CrossEncoder Pre-training
FAISS Vector Index (`logic_vectors.faiss`)  (ms-marco-MiniLM-L6-v2, Frozen)
(1,518 concept vectors, d=384)                     ¦
           ¦                                       ¦
           +---------------------------------------+
                                   ¦
                                   ?
              Active Production Evaluator (`services/evaluator/app.py`)
              (Tripartite: 0.15 S1 + 0.35 S2,eff + 0.50 R, theta=0.30)
                                   ¦
                                   +---------------------------------+
                                   ?                                 ?
                     Pilot Evaluation Dataset (N=20)   Held-Out Benchmark (N=80+)
                     (ablation/results/ratings_rater1) (research/data/evaluator_benchmark)
                     - 4 Topics (Q1, Q3, Q10, Q41)     - Unseen Questions & Variants
```

---

## 2. Leakage Audit Across 12 Potential Vulnerabilities

| Vulnerability Path | Audit Finding & Mechanism | Leakage Classification | Evidence / Safeguard |
|:---|:---|:---:|:---|
| **1. Direct Training Examples** | CrossEncoder checkpoint `models/tuned_model2/` is UKPLab's pre-trained MS MARCO passage ranker. It was never trained or fine-tuned on any PREPAIred questions or answers. | **CLEAN** | `tuned_model2/README.md` & sha256 checksums |
| **2. Duplicated Answers** | Exact text matching across dataset files confirms zero duplicated answers between pilot and benchmark sets. | **CLEAN** | Automated hash audit |
| **3. Paraphrase Contamination** | Pilot answers were independently authored; benchmark cases use distinct phrasing. | **CLEAN** | Sentence similarity check |
| **4. Same Questions Across Splits** | The pilot study evaluated 4 questions (Q1, Q3, Q10, Q41). To ensure zero leakage in future benchmarks, all new test items must use disjoint question IDs (Question-Level Splitting). | **CLEAN (with question-level split)** | Question ID partitioning |
| **5. Concept / Rubric Infiltration** | Rubrics were authored from standard textbook algorithmic definitions, not tuned to fit specific candidate phrases. | **CLEAN** | `rubrics_final_clean.json` |
| **6. Threshold Optimization** | Operating point $\theta = 0.30$ was determined via sensitivity sweep across $[0.15, 0.60]$ on development answers and frozen. | **CLEAN** | `threshold_provenance.md` |
| **7. Manual Checkpoint Selection** | Single fixed checkpoint used across all runs; no cherry-picking of favorable seeds. | **CLEAN** | Fixed `tuned_model2` path |
| **8. Error-Analysis Iteration** | Error analysis in `table_eval_error_analysis.md` records system limitations without modifying scoring weights post-hoc. | **CLEAN** | Historical run freeze |
| **9. Prompt Engineering** | Technical scoring does NOT use generative LLMs or prompts; scoring is purely SBERT + FAISS + CrossEncoder. | **CLEAN** | `services/evaluator/app.py` |
| **10. Model Selection Bias** | Off-the-shelf `all-MiniLM-L6-v2` and `ms-marco-MiniLM-L6-v2` selected prior to evaluation. | **CLEAN** | Architectural freeze |
| **11. Benchmark Construction** | Benchmark categories (concise, verbose wrong, keyword-stuffed, misconceptions) are balanced across domains. | **CLEAN** | `benchmark_cases.json` |
| **12. Hyperparameter Selection** | Tripartite weights ($0.15 / 0.35 / 0.50$) were set based on signal complexity, not post-hoc test tuning. | **CLEAN** | `experiments/experiment_2_evaluation/config.json` |

---

## 3. Question-Level Splitting Protocol for Held-Out Evaluation
To guarantee rigorous generalization in Paper 2:
- **Development / Calibration Questions ($K=4$):** Q1 (Two Sum), Q3 (Reverse Linked List), Q10 (BFS Tree), Q41 (C Pointers). Used for pilot exploratory runs, threshold sweeps, and baseline verification.
- **Held-Out Test Questions ($K=12+$):** Completely disjoint question IDs from the question bank (e.g. Q7 DP, Q15 Graphs, Q22 Hashing, Q34 Binary Search, Q50 Bit Manipulation) with unseen candidate answers evaluated strictly after parameter freezing.
