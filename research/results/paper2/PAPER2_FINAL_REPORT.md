# PREPAIred — Paper 2 Final Scientific Evaluation Report

**Title:** Grounded Multi-Component Technical Interview Answer Evaluation with Entailment Dampening  
**Evaluation Date:** September 2026  
**Benchmark Dataset:** `research/data/evaluator_benchmark/final_human_gold.csv` (SHA-256: `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2`)  
**Evaluator Config:** `research/experiments/paper2/frozen_config.yaml` (SHA-256: `f057baf1b2b9608eb0eb34d9aef3a4a3571db868f9ee728dda180364cc4e90f1`)  
**Model Checkpoint:** `services/evaluator/models/tuned_model2/model.safetensors` (SHA-256: `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`)  
**Sample Size:** $N = 64$ authentic technical interview explanations across 10 balanced categories  

---

## 1. Executive Summary & Core Scientific Findings

This report presents the frozen empirical findings of the Paper 2 Technical Evaluator study evaluated against the 64-case human consensus gold benchmark. The benchmark was established by three independent computer science educators with rigorous inter-rater agreement ($\text{ICC}(2,1) = 0.9528$, $\text{ICC}(2,k) = 0.9838$, Krippendorff $\alpha = 0.9523$) and expert blind adjudication of all 10 borderline disagreement cases ($\Delta_{\max} > 0.20$).

### Key Empirical Outcomes:
1. **Primary Human Alignment:** The frozen production evaluator achieves a Spearman rank correlation of **$\rho = 0.3812$** ($p = 1.8863e-03$, 95% bootstrap CI $[0.1575, 0.5774]$) against the 64-case human gold benchmark.
2. **Linear and Error Metrics:** Pearson $r = 0.4042$ ($p = 9.2455e-04$), Kendall $\tau = 0.2715$ ($p = 1.7272e-03$), $\text{MAE} = 0.2920$, $\text{RMSE} = 0.3601$.
3. **Component Ablation Findings:** Cross-Encoder Reasoning Entailment ($R$) is the strongest individual component ($\rho = 0.4832$), substantially exceeding Semantic Similarity ($S_1$ only: $\rho = 0.2070$) and FAISS Concept Coverage ($S_2$ only: $\rho = 0.3021$). The Full Composite pipeline ($\rho = 0.3812$) integrates dampening and rubric constraints to protect against keyword stuffing and prompt manipulation.
4. **Metamorphic Robustness:** **19/21 (90.5%)** metamorphic transformation tests passed across all 7 relations (paraphrase invariance, irrelevant text addition, monotonic concept deletion, negation collapse, keyword injection resistance, sentence reordering, and sentence duplication).
5. **Adversarial Containment:** **11/13 (84.6%)** prompt injection and manipulation attack vectors were successfully contained below engineering safety ceilings.

---

## 2. Model & Checkpoint Provenance Certification

- **Semantic Embedding Model ($S_1$):** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense embeddings, $L_2$ normalized, cosine similarity).
- **Structural Concept Index ($S_2$):** FAISS `IndexFlatIP` exact cosine index storing 1,518 rubric concept vectors with operational threshold $\theta = 0.30$.
- **Reasoning Entailment Model ($R$):** Off-the-shelf, pre-trained cross-encoder (`cross-encoder/ms-marco-MiniLM-L6-v2`, pre-trained on MS MARCO by UKPLab), **deployed in zero-shot inference without PREPAIred-specific fine-tuning or domain adaptation**.
  - *Path:* `services/evaluator/models/tuned_model2/model.safetensors`
  - *Checksum:* SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`
  - *Note on Directory Name:* The folder name `tuned_model2` is strictly an internal local path/scaffolding artifact; no interview-domain fine-tuning was performed.

---

## 3. Primary & Secondary Statistical Evaluation (N=64)

| Metric | Point Estimate | 95% Bootstrap Percentile CI | $p$-value | Statistical Method |
| :--- | :---: | :---: | :---: | :--- |
| **Spearman $\rho$ (Primary)** | **0.3812** | **[0.1575, 0.5774]** | $1.8863e-03$ | Paired case-level bootstrap ($B=2,000$, seed=42) |
| **Pearson $r$** | 0.4042 | [0.1846, 0.5960] | $9.2455e-04$ | Paired case-level bootstrap ($B=2,000$, seed=42) |
| **Kendall $\tau$** | 0.2715 | [0.1168, 0.4295] | $1.7272e-03$ | Paired case-level bootstrap ($B=2,000$, seed=42) |
| **Mean Absolute Error (MAE)** | 0.2920 | [0.2431, 0.3457] | N/A | Case-level bootstrap ($B=2,000$, seed=42) |
| **Root Mean Squared Error (RMSE)** | 0.3601 | [0.3008, 0.4184] | N/A | Case-level bootstrap ($B=2,000$, seed=42) |

---

## 4. 7-Way Component Ablation Study

To evaluate the individual and joint contribution of each architectural component, seven pre-specified configurations were evaluated on the identical 64-case human gold benchmark.

| Configuration | Weighting Formula | Spearman $\rho$ | 95% Bootstrap CI | Pearson $r$ | Kendall $\tau$ | MAE | RMSE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| S1 only (Semantic) | `1.00 * S1` | 0.2070 | [-0.0317, 0.4125] | 0.2430 | 0.1406 | 0.3171 | 0.3985 |
| S2 only (FAISS) | `1.00 * S2` | 0.3021 | [0.0492, 0.5337] | 0.3324 | 0.2562 | 0.3251 | 0.4421 |
| R only (CrossEncoder) | `1.00 * R` | 0.4832 | [0.2501, 0.6762] | 0.5080 | 0.3492 | 0.2763 | 0.3125 |
| S1 + S2 (0.30/0.70) | `0.30 * S1 + 0.70 * S2` | 0.2894 | [0.0470, 0.4956] | 0.3240 | 0.2111 | 0.3042 | 0.4159 |
| S1 + R (0.23/0.77) | `0.23 * S1 + 0.77 * R` | 0.4884 | [0.2624, 0.6751] | 0.5137 | 0.3460 | 0.2790 | 0.3198 |
| S2 + R (0.41/0.59) | `0.41 * S2 + 0.59 * R` | 0.4171 | [0.1978, 0.6124] | 0.4540 | 0.3140 | 0.2674 | 0.3337 |
| **Full Composite (0.15/0.35/0.50)** | `0.15*S1 + 0.35*S2_eff + 0.50*R + bonus - penalty` | **0.3812** | [0.1575, 0.5774] | 0.4042 | 0.2715 | 0.2920 | 0.3601 |

### Paired Statistical Hypothesis Tests (Full Composite vs. Ablated Baselines):

| Ablated Baseline | Mean Error Diff | Paired $t$-test ($p$-val) | Wilcoxon Signed-Rank ($p$-val) | Cohen's $d$ | Cliff's $\Delta$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| S1 only (Semantic) | +0.0251 | $t=1.381$ ($p=1.7206e-01$) | $W=873.0$ ($p=2.6407e-01$) | 0.173 | +0.036 |
| S2 only (FAISS) | +0.0331 | $t=1.646$ ($p=1.0472e-01$) | $W=662.0$ ($p=1.3410e-01$) | 0.206 | -0.040 |
| R only (CrossEncoder) | -0.0157 | $t=-0.855$ ($p=3.9599e-01$) | $W=892.0$ ($p=3.2230e-01$) | -0.107 | +0.040 |
| S1 + S2 (0.30/0.70) | +0.0123 | $t=0.701$ ($p=4.8591e-01$) | $W=963.0$ ($p=6.0660e-01$) | 0.088 | -0.082 |
| S1 + R (0.23/0.77) | -0.0130 | $t=-0.898$ ($p=3.7248e-01$) | $W=912.0$ ($p=3.9200e-01$) | -0.112 | +0.042 |
| S2 + R (0.41/0.59) | -0.0246 | $t=-3.199$ ($p=2.1624e-03$) | $W=636.0$ ($p=6.8975e-03$) | -0.400 | -0.061 |

---

## 5. Metamorphic Robustness Evaluation

The evaluator was subjected to **21 metamorphic transformation tests** across 7 distinct relations.

| Case ID | Relation | Base Score | Transformed | Delta | Verdict | Expected Invariant Criterion |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| META-01 | MG-1: Paraphrase Invariance | 0.6386 | 0.6000 | -0.0386 | **PASS** | Score approximately stable (|delta| <= 0.10) |
| META-01 | MG-2: Irrelevant Addition | 0.6386 | 0.6300 | -0.0086 | **PASS** | Score does not artificially inflate (delta <= 0.05) |
| META-01 | MG-3: Concept Deletion | 0.6386 | 0.2914 | -0.3472 | **PASS** | Monotonic score drop (delta < 0) |
| META-01 | MG-4: Negation Inversion | 0.6386 | 0.4171 | -0.2215 | **PASS** | Severe penalty (delta <= -0.20) |
| META-01 | MG-5: Keyword Injection | 0.6386 | 0.4251 | -0.2135 | **PASS** | Score bounded without reasoning (score <= 0.50) |
| META-01 | MG-6: Sentence Reordering | 0.6386 | 0.6457 | +0.0071 | **PASS** | Score approximately invariant under reordering (|delta| <= 0.08) |
| META-01 | MG-7: Sentence Duplication | 0.6386 | 0.6581 | +0.0195 | **PASS** | No artificial inflation from repetition (|delta| <= 0.08) |
| META-02 | MG-1: Paraphrase Invariance | 0.7016 | 0.6510 | -0.0506 | **PASS** | Score approximately stable (|delta| <= 0.10) |
| META-02 | MG-2: Irrelevant Addition | 0.7016 | 0.6306 | -0.0710 | **PASS** | Score does not artificially inflate (delta <= 0.05) |
| META-02 | MG-3: Concept Deletion | 0.7016 | 0.5949 | -0.1067 | **PASS** | Monotonic score drop (delta < 0) |
| META-02 | MG-4: Negation Inversion | 0.7016 | 0.4416 | -0.2600 | **PASS** | Severe penalty (delta <= -0.20) |
| META-02 | MG-5: Keyword Injection | 0.7016 | 0.5781 | -0.1235 | **FAIL** | Score bounded without reasoning (score <= 0.50) |
| META-02 | MG-6: Sentence Reordering | 0.7016 | 0.7222 | +0.0206 | **PASS** | Score approximately invariant under reordering (|delta| <= 0.08) |
| META-02 | MG-7: Sentence Duplication | 0.7016 | 0.7109 | +0.0093 | **PASS** | No artificial inflation from repetition (|delta| <= 0.08) |
| META-03 | MG-1: Paraphrase Invariance | 0.7827 | 0.7396 | -0.0431 | **PASS** | Score approximately stable (|delta| <= 0.10) |
| META-03 | MG-2: Irrelevant Addition | 0.7827 | 0.7872 | +0.0045 | **PASS** | Score does not artificially inflate (delta <= 0.05) |
| META-03 | MG-3: Concept Deletion | 0.7827 | 0.4427 | -0.3400 | **PASS** | Monotonic score drop (delta < 0) |
| META-03 | MG-4: Negation Inversion | 0.7827 | 0.5014 | -0.2813 | **PASS** | Severe penalty (delta <= -0.20) |
| META-03 | MG-5: Keyword Injection | 0.7827 | 0.6644 | -0.1183 | **FAIL** | Score bounded without reasoning (score <= 0.50) |
| META-03 | MG-6: Sentence Reordering | 0.7827 | 0.7785 | -0.0042 | **PASS** | Score approximately invariant under reordering (|delta| <= 0.08) |
| META-03 | MG-7: Sentence Duplication | 0.7827 | 0.7876 | +0.0049 | **PASS** | No artificial inflation from repetition (|delta| <= 0.08) |

---

## 6. Systematic Adversarial Containment

A total of **13 adversarial attack vectors** spanning prompt injections, keyword bombs, buzzword obfuscation, and JSON overrides were evaluated against the combined pipeline (`Evaluator + ScoreValidator`).

| Vector ID | Attack Category | Raw Score | Validated Score | Safe Ceiling | Status | Attack Rationale |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `ADV-01` | instruction_override | 0.0000 | 0.0000 | $\le 0.15$ | **CONTAINED** | LLM injection string has zero technical concept or reasoning entailment against rubric. |
| `ADV-02` | score_manipulation | 0.0094 | 0.0094 | $\le 0.40$ | **CONTAINED** | Directly injects system score headers to test if keyword pattern tricks evaluator. |
| `ADV-03` | keyword_stuffing | 0.4251 | 0.4251 | $\le 0.45$ | **CONTAINED** | Pure keyword list without syntactic predicates; must be bounded. |
| `ADV-04` | buzzword_stuffing | 0.0000 | 0.0000 | $\le 0.15$ | **CONTAINED** | High syllable density buzzwords with zero relevance to two sum. |
| `ADV-05` | irrelevant_jargon | 0.0000 | 0.0000 | $\le 0.15$ | **CONTAINED** | Real technical terminology that is completely irrelevant to linked list reversal. |
| `ADV-06` | repetition | 0.0106 | 0.0106 | $\le 0.35$ | **CONTAINED** | Testing if repeated valid tokens artificially inflate FAISS concept scores. |
| `ADV-07` | correct_keywords_wrong_reasoning | 0.2052 | 0.2052 | $\le 0.40$ | **CONTAINED** | Contains valid terms but proposes an absurd, mathematically invalid execution flow. |
| `ADV-08` | correct_reasoning_irrelevant_jargon | 0.3994 | 0.3994 | $\le 0.85$ | **CONTAINED** | Correct logic should not be completely destroyed by trailing irrelevant prose, though not receive 1.0. |
| `ADV-09` | plausible_misconception | 0.2011 | 0.2011 | $\le 0.35$ | **CONTAINED** | Subtle and common student error directly violating algorithmic precondition. |
| `ADV-10` | contradiction | 0.4617 | 0.4617 | $\le 0.35$ | **BREACH** | Initial correct claim immediately contradicted by invalid mechanism. |
| `ADV-11` | negation | 0.4328 | 0.4328 | $\le 0.25$ | **BREACH** | Explicit negation of the core required action. |
| `ADV-12` | fake_authority | 0.0000 | 0.0000 | $\le 0.15$ | **CONTAINED** | Appeals to academic authority without algorithmic substance. |
| `ADV-13` | formatting_manipulation | 0.0000 | 0.0000 | $\le 0.15$ | **CONTAINED** | JSON/markdown code block payload attempting to exploit parser ambiguity. |

---

## 7. Case-Level Error Analysis & Category Breakdown

### Error Summary by Quality Category:

| Quality Category | Cases ($N$) | Mean Abs Error | Mean Signed Error | Min Error | Max Error |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `concise_correct` | 8 | 0.5154 | -0.5154 | -0.9133 | -0.1671 |
| `contradictory` | 4 | 0.1623 | +0.1279 | -0.0690 | +0.2970 |
| `incorrect` | 6 | 0.1300 | +0.0722 | -0.1167 | +0.2440 |
| `keyword_stuffed` | 8 | 0.2224 | +0.0395 | -0.3000 | +0.3234 |
| `misconception` | 8 | 0.1479 | +0.1204 | -0.1100 | +0.3332 |
| `paraphrase` | 4 | 0.4835 | -0.4835 | -0.7562 | -0.2199 |
| `partial_incomplete` | 8 | 0.3122 | -0.3122 | -0.6100 | -0.1021 |
| `suboptimal_correct` | 2 | 0.4213 | -0.4213 | -0.5299 | -0.3127 |
| `verbose_correct` | 8 | 0.3929 | -0.3929 | -0.6916 | -0.1124 |
| `verbose_wrong` | 8 | 0.2193 | +0.2193 | +0.0500 | +0.4653 |

### Top 5 Largest Absolute Error Cases:

| Case ID | Category | Topic | Human Gold | Model Score | Signed Error | Weakest Gap Identified |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `BM-057` | `concise_correct` | OS & Concurrency | 0.9133 | 0.0000 | -0.9133 | null pointer dereference: reading or writing through a null pointer accesses address 0 which is protected; buffer overflow: accessing array[n] or beyond the last valid index |
| `BM-064` | `paraphrase` | OS & Concurrency | 0.8800 | 0.1238 | -0.7562 | null pointer dereference: reading or writing through a null pointer accesses address 0 which is protected; buffer overflow: accessing array[n] or beyond the last valid index |
| `BM-033` | `concise_correct` | Dynamic Programming | 0.9233 | 0.2142 | -0.7091 | transpose iterates the upper triangle only (i < j) to avoid double-swapping; row reversal iterates each row independently |
| `BM-058` | `verbose_correct` | OS & Concurrency | 0.9833 | 0.2917 | -0.6916 | null pointer dereference: reading or writing through a null pointer accesses address 0 which is protected; buffer overflow: accessing array[n] or beyond the last valid index |
| `BM-041` | `concise_correct` | Graphs & DFS | 0.9033 | 0.2346 | -0.6687 | when array[mid]==0, swap with low and advance both; when array[mid]==2, swap with high and decrement high without advancing mid because the new element at mid is unseen |

---

## 8. Separation of Human Committee Reliability

The inter-rater agreement statistics established in Human Gate 2 describe the three real human annotators and remain permanently immutable:
- **Intraclass Correlation (Single Rater):** $\text{ICC}(2, 1) = 0.9528$ (95% CI $[0.9290, 0.9689]$)
- **Intraclass Correlation (Average of 3 Raters):** $\text{ICC}(2, k) = 0.9838$ (95% CI $[0.9751, 0.9894]$)
- **Krippendorff's Alpha (Interval Metric):** $\alpha = 0.9523$ (95% CI $[0.9281, 0.9685]$)

> **Methodological Invariant:** These values quantify human consensus reliability and are strictly isolated from model correlation metrics ($\rho = 0.3812$).

---

## 9. Scientific Claim Boundaries & Limitations

In compliance with scientific integrity standards:
1. **No Pedagogical Claims:** This study evaluates automated scoring alignment with educator judgment on written technical explanations. It does **not** evaluate student learning outcomes, interview preparation efficacy, or interview hiring pass rates.
2. **No Demographic Parity Claims:** No candidate demographic, linguistic accent, or socioeconomic features were modeled or evaluated; no fairness or bias mitigation claims are made.
3. **Scope of Domain:** The benchmark covers core algorithmic and data structures interview explanations. Generalization to conversational behavioral interviews or free-form system design whiteboard discussions remains unverified.
4. **Zero Fine-Tuning:** MiniLM-L6-v2 operates off-the-shelf; performance represents out-of-the-box transferability rather than in-domain fine-tuned capacity.

---

## 10. Reproduction Environment & Checksums

- **Git Baseline Checkpoint:** Commit `375f4f869c47907d7c222d27df3b4f9e09dc8941` (Tag: `pre-paper2-execution`)
- **Benchmark Gold SHA-256:** `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2`
- **Model Weights SHA-256:** `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`
- **Frozen Config SHA-256:** `f057baf1b2b9608eb0eb34d9aef3a4a3571db868f9ee728dda180364cc4e90f1`
- **Python Runtime:** Python 3.12.7 (x86_64, Windows)
- **Core Packages:** `torch==2.2.2+cpu`, `transformers==4.57.6`, `sentence-transformers==2.7.0`, `faiss==1.13.2`, `scipy==1.13.1`, `numpy==1.26.4`
