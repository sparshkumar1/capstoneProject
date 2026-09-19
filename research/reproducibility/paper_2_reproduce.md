# Reproduction Guide: Paper 2 (Technical Evaluator & Scoring)

**Target Venue:** *ICTCS 2026* / *IEEE Transactions on Education (ToE)*  
**Paper Title:** *Evidence-Grounded Technical Answer Evaluation Using Semantic, Concept, and Reasoning Signals*

---

## 1. Prerequisites
- Python virtual environment activated:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- Evaluator assets present in `services/evaluator/assets/` (`logic_vectors.faiss`, `logic_metadata.pkl`).
- Fine-tuned CrossEncoder checkpoint present in `services/evaluator/models/tuned_model2/`.

---

## 2. Execute Evaluator Experiments

### A. Component Ablation & Threshold Sweep
```powershell
python research/scripts/run_evaluator_experiments.py
```
This command automatically executes:
1. **EXP-EVAL-1: 7-Way Component Ablation**
   - Evaluates $S_1$, $S_2$, $R$, $S_1+R$, $S_1+S_2$, $S_2+R$, and Full Composite ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$) across:
     - Pilot Real Human Rater 1 ($N=20$)
     - Synthetic Proxy ($N=20$)
     - Averaged Set ($N=20$)
   - Calculates Spearman $\rho$, Pearson $r$, MAE, RMSE, bootstrap 95% CIs ($B=1000$), and $p$-values.
   - Outputs: `research/raw/eval_ablation_raw.json`, `research/tables/table_eval_ablation.md`, `research/figures/eval_ablation_comparison.png`.

2. **EXP-EVAL-2: Adversarial Keyword-Stuffing Resistance**
   - Tests reasoning-conditioned concept dampening ($S_{2,\text{eff}} = S_2 \times 0.60$ when $R \le 0.30$) across authentic technical, keyword-stuffed, and superficial responses.
   - Outputs: `research/raw/eval_adversarial_raw.json`, `research/tables/table_eval_adversarial.md`.

3. **EXP-EVAL-3: Concept Threshold Sensitivity Sweep**
   - Sweeps FAISS inner-product cosine threshold $\theta \in [0.20, 0.70]$ in increments of $0.02$.
   - Outputs: `research/raw/eval_threshold_raw.json`, `research/tables/table_eval_threshold.md`, `research/figures/eval_threshold_sensitivity.png`.

4. **EXP-EVAL-4: Error Analysis & Misconception Diagnostics**
   - Evaluates confusion matrices, false positives, false negatives, and misconception detection across score grade boundaries.
   - Outputs: `research/raw/eval_error_analysis_raw.json`, `research/tables/table_eval_error_analysis.md`.

### B. Metamorphic Testing Suite
```powershell
python research/scripts/run_metamorphic_tests.py
```
- Tests 5 metamorphic relations (Paraphrase Invariance, Irrelevant Text Addition, Keyword Stuffing, Concept Deletion, Negation Inversion).
- Outputs: `research/results/metamorphic_tests.csv`, `research/raw/metamorphic_raw.json`, `research/tables/metamorphic_results.md`.

### C. Human Benchmark Agreement Analysis
```powershell
python research/scripts/analyze_human_ratings.py --input ablation/results/ratings_rater1.csv
```
- Computes Krippendorff alpha, Cohen/Spearman correlations, and bootstrap 95% CIs.
- Outputs: `research/results/rater_analysis.json`.

---

## 3. Verify Engineering Test Suite
```powershell
pytest tests/unit/test_evaluator.py tests/unit/test_score_validator.py -v
```
All tests must report `PASSED`.
