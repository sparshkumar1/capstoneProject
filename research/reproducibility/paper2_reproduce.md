# Paper 2 — Evaluator Reproducibility Guide

**Target Venue:** *ICTCS 2026* / *IEEE Transactions on Education (ToE)*  
**Paper Title:** *Evidence-Grounded Technical Answer Evaluation Using Semantic, Concept, and Reasoning Signals*

---

## 1. Frozen Evaluation Execution
To execute the complete Paper 2 study (7-way ablation on human ground truth, 64-case category evaluation, 7-relation metamorphic tests, and prompt injection defense) under the frozen configuration:

```bash
python research/scripts/run_paper2_study.py
```

### Frozen Configuration
Defined in `research/experiments/paper2/frozen_config.yaml`:
- **Formula:** $\text{Final Score} = 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$
- **Semantic Encoder ($S_1$):** `sentence-transformers/all-MiniLM-L6-v2` ($d=384$)
- **Concept Matcher ($S_2$):** FAISS `IndexFlatIP` ($N=1,518$ concept vectors) with threshold $\theta = 0.30$
- **Reasoning Verifier ($R$):** `cross-encoder/ms-marco-MiniLM-L6-v2`
- **Reasoning Dampening:** When $R \le 0.30$, effective concept score $S_{2,\text{eff}} = 0.60 \cdot S_2$
- **Post-Hoc ScoreValidator:** Clamping to $[0.0, 1.0]$, mandatory concept gating ($0.65$ cap), syntax failure penalization ($0.70\times$).

---

## 2. Verified Results
- **Human Ground Truth Correlation ($N=20$, Rater 1):** $\rho = 0.6975$ ($p = 0.00063$), $r = 0.7290$, $\text{MAE} = 0.2245$
- **7-Relation Metamorphic Tests:** 6/7 Pass (monotonicity, concept deletion penalty $-0.450$, negation penalty $-0.338$, keyword injection bounded $\le 0.50$)
- **Prompt Injection Containment:** 4/4 Contained ($0.0000$ score on direct instructions)
- **Output Artifacts:**
  - `research/results/paper2_final_results.csv`
  - `research/results/paper2_final_results.md`
  - `research/results/paper2_error_analysis.md`
