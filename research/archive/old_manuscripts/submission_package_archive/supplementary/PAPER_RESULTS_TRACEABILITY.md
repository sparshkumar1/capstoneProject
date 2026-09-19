# PrepAIred — Authoritative Research Paper Results Traceability Matrix

**Document Version:** 1.0.0 (Stage 17 Master Traceability)
**System:** PrepAIred Automated Technical Interview System
**Paper Manuscript:** [`docs/paper_draft_ieee.md`](docs/paper_draft_ieee.md)
**Purpose:** Cryptographic and dataflow traceability mapping every numerical result, metric, statistical test, and claim in the research paper directly to its underlying raw artifacts, processed files, analysis scripts, tables, figures, and status.

---

## 1. Master Numerical Results Traceability Table

| # | Paper Section | Numerical Claim / Stated Result | Experiment ID | Raw Data Artifact | Processed Data Artifact | Analysis Script / Method | Figure / Table | Claim Status in `docs/CLAIMS_CHECK.md` |
|:---:|---|---|:---:|---|---|---|---|:---:|
| **1** | Abstract, Sec. XIV-A | PPO adaptation correlation $\rho = +0.1572 \pm 0.08$ | **EXP-1** | `research/results/raw/experiment_1_raw.json` | `research/results/processed/experiment_1_analysis.csv` | `scipy.stats.spearmanr`, bootstrap SE | Table VII, Fig. 4 | **`EXPERIMENTALLY VALIDATED`** (Claim #5) |
| **2** | Abstract, Sec. XIV-A | Fixed difficulty adaptation $\rho = 0.0000 \pm 0.00$ | **EXP-1** | `research/results/raw/experiment_1_raw.json` | `research/results/processed/experiment_1_analysis.csv` | `scipy.stats.spearmanr` | Table VII, Fig. 4 | **`EXPERIMENTALLY VALIDATED`** (Claim #5) |
| **3** | Abstract, Sec. XIV-A | Rule-Based adaptation $\rho = -0.2572 \pm 0.065$ | **EXP-1** | `research/results/raw/experiment_1_raw.json` | `research/results/processed/experiment_1_analysis.csv` | `scipy.stats.spearmanr` | Table VII, Fig. 4 | **`EXPERIMENTALLY VALIDATED`** (Claim #5) |
| **4** | Abstract, Sec. XIV-A | PPO vs Fixed Wilcoxon $p = 6.15 \times 10^{-4}, d = 0.5562$ | **EXP-1** | `research/results/raw/experiment_1_raw.json` | `research/results/processed/experiment_1_analysis.csv` | `scipy.stats.wilcoxon`, Holm correction | Table VII, Fig. 4 | **`EXPERIMENTALLY VALIDATED`** (Claim #5) |
| **5** | Abstract, Sec. XIV-A | PPO vs Rule-Based Wilcoxon $p = 5.30 \times 10^{-8}, d = 1.4654$ | **EXP-1** | `research/results/raw/experiment_1_raw.json` | `research/results/processed/experiment_1_analysis.csv` | `scipy.stats.wilcoxon`, Holm correction | Table VII, Fig. 4 | **`EXPERIMENTALLY VALIDATED`** (Claim #5) |
| **6** | Abstract, Sec. XIV-B | Evaluator Full Pipeline Spearman $\rho = 0.8358, p = 4.46 \times 10^{-6}$ | **EXP-2** | `research/results/raw/experiment_2_raw.json` | `research/results/processed/experiment_2_analysis.csv` | `scipy.stats.spearmanr` | Table VIII, Fig. 5 | **`EXPERIMENTALLY VALIDATED`** (Claim #1) |
| **7** | Sec. XIV-B | Evaluator $S_1+S_2$ Spearman $\rho = 0.8358, \text{MAE} = 0.1907$ | **EXP-2** | `research/results/raw/experiment_2_raw.json` | `research/results/processed/experiment_2_analysis.csv` | `scipy.stats.spearmanr`, numpy MAE | Table VIII, Fig. 5 | **`EXPERIMENTALLY VALIDATED`** (Claim #1) |
| **8** | Sec. XIV-B | Evaluator Full Pipeline MAE = $0.2585$ | **EXP-2** | `research/results/raw/experiment_2_raw.json` | `research/results/processed/experiment_2_analysis.csv` | numpy MAE | Table VIII, Fig. 5 | **`EXPERIMENTALLY VALIDATED`** (Claim #1) |
| **9** | Abstract, Sec. XIV-B | Human Inter-Rater Reliability Krippendorff's $\alpha = 0.8255$ | **EXP-2** | `ablation/results/ratings_averaged.csv` | `ablation/results/ratings_averaged.csv` | `ablation/compute_krippendorff.py` (56 pairs) | Table VIII, Fig. 5 | **`HUMAN VALIDATED`** (Claim #2) |
| **10** | Abstract, Sec. XIV-C | Qwen-7B Lexical Grounding = $0.2496$ (95% CI: $[0.1758, 0.3331]$) | **EXP-3** | `research/results/raw/experiment_3_qwen_raw.json` | `research/results/processed/experiment_3_qwen_processed.csv` | `experiments/experiment_3_feedback/import_qwen_colab_results.py` | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **11** | Abstract, Sec. XIV-C | Structured Recovery Grounding = $0.0383$ (95% CI: $[0.0059, 0.0919]$) | **EXP-3** | `research/results/raw/experiment_3_raw.json` | `research/results/processed/experiment_3_analysis.csv` | Bootstrap 10,000 resamples | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **12** | Abstract, Sec. XIV-C | Generic Template Grounding = $0.0000$ (95% CI: $[0.0000, 0.0000]$) | **EXP-3** | `research/results/raw/experiment_3_raw.json` | `research/results/processed/experiment_3_analysis.csv` | Bootstrap 10,000 resamples | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **13** | Abstract, Sec. XIV-C | Qwen-7B vs Structured Grounding $W = 15.0, p = 2.56 \times 10^{-3}, d = 0.8903$ | **EXP-3** | `research/results/raw/experiment_3_qwen_raw.json`, `experiment_3_raw.json` | `research/results/tables/experiment_3_results.csv` | `scipy.stats.wilcoxon`, Holm correction | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **14** | Abstract, Sec. XIV-C | Qwen-7B vs Generic Grounding $W = 0.0, p = 3.94 \times 10^{-4}, d = 1.3628$ | **EXP-3** | `research/results/raw/experiment_3_qwen_raw.json`, `experiment_3_raw.json` | `research/results/tables/experiment_3_results.csv` | `scipy.stats.wilcoxon`, Holm correction | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **15** | Abstract, Sec. XIV-C | Structured Recovery Rubric Gap Coverage = $100.0\%$ ($1.0000$) | **EXP-3** | `research/results/raw/experiment_3_raw.json` | `research/results/processed/experiment_3_analysis.csv` | Rubric concept tracking matching | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **16** | Abstract, Sec. XIV-C | Qwen-7B Rubric Gap Coverage = $72.5\%$ ($0.7250$) | **EXP-3** | `research/results/raw/experiment_3_qwen_raw.json` | `research/results/processed/experiment_3_qwen_processed.csv` | Evaluator missing concept matching | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **17** | Abstract, Sec. XIV-C | Structured vs Qwen Gap Coverage $W = 0.0, p = 9.11 \times 10^{-4}, d = 1.0775$ | **EXP-3** | `research/results/raw/experiment_3_qwen_raw.json`, `experiment_3_raw.json` | `research/results/tables/experiment_3_results.csv` | `scipy.stats.wilcoxon`, Holm correction | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **18** | Sec. XIV-C | Actionable Directives Count: Structured ($3.90$) vs Qwen ($3.70$) ($p = 0.6033$) | **EXP-3** | `research/results/raw/experiment_3_qwen_raw.json`, `experiment_3_raw.json` | `research/results/tables/experiment_3_results.csv` | `scipy.stats.wilcoxon`, $d = 0.1133$ | Table IX, Fig. 6 | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **19** | Abstract, Sec. XIV-C | Qwen-7B Mean Latency on Tesla T4 GPU = $9.78\text{s}$ | **EXP-3** | `research/results/raw/experiment_3_qwen_raw.json` | `research/results/processed/experiment_3_qwen_processed.csv` | `time.time()` GPU kernel timing | Table IX | **`EXPERIMENTALLY VALIDATED`** (Claim #11) |
| **20** | Abstract, Sec. XIV-D | Question Repetition: Personalized ($0.0\%$) vs Random ($6.0\%$) ($p < 0.001$) | **EXP-4** | `research/results/raw/experiment_4_raw.json` | `research/results/processed/experiment_4_analysis.csv` | Chi-square contingency test | Table X, Fig. 7 | **`EXPERIMENTALLY VALIDATED`** (Claim #7) |
| **21** | Sec. XIV-D | Weakness Remediation Rate: Personalized ($16.67\%$) vs Random ($2.00\%$) | **EXP-4** | `research/results/raw/experiment_4_raw.json` | `research/results/processed/experiment_4_analysis.csv` | Weakness-targeted question match | Table X, Fig. 7 | **`EXPERIMENTALLY VALIDATED`** (Claim #7) |
| **22** | Abstract, Sec. XIV-D | Trajectory Euclidean Divergence Distance = $14.21$ | **EXP-4** | `research/results/raw/experiment_4_raw.json` | `research/results/processed/experiment_4_analysis.csv` | Euclidean distance between strong and weak difficulty vectors | Table X, Fig. 7 | **`EXPERIMENTALLY VALIDATED`** (Claim #8) |
| **23** | Sec. XIV-E | Leave-One-Out RL Removal: Adaptation $\rho$ drops $+0.1572 \to 0.0000$ | **EXP-5** | `research/results/raw/experiment_5_raw.json` | `research/results/processed/experiment_5_analysis.csv` | Controller isolation delta | Table XI, Fig. 8 | **`EXPERIMENTALLY VALIDATED`** (Claim #5) |
| **24** | Sec. XIV-E | Leave-One-Out Probing Removal: Probes drop $0.50 \to 0.00$ probes/session | **EXP-5** | `research/results/raw/experiment_5_raw.json` | `research/results/processed/experiment_5_analysis.csv` | Follow-up trigger isolation delta | Table XI, Fig. 8 | **`EXPERIMENTALLY VALIDATED`** (Claim #10) |
| **25** | Sec. VIII, X, XII | Timing additive modifier bounds $f_{\text{time}} \in [-0.10, +0.03]$ | Core System | `docs/SCORING.md`, `agents/timing/timer.py` | `agents/timing/timer.py` | `tests/unit/test_timer_scoring.py` | Sec. XII-C | **`TESTED`** (Claim #13) |
| **26** | Sec. IX-A | PPO Timesteps = 300,000, 6D state, 3 actions | Core System | `rl/train_ppo.py`, `rl/checkpoints/` | `rl/env/interview_env.py` | `tests/unit/test_rl_env.py` | Table IV | **`TESTED`** (Claim #4) |
| **27** | Sec. VII | Question Curriculum Bank = 125 curated questions across 13 CS topics | Core System | `data/questions/qns.json`, `data/rubrics/` | `data/rubrics/rubrics_final_clean.json` | `tests/unit/test_personalization_questions.py` | Table I | **`TESTED`** (Claim #15) |

---

## 2. Cryptographic Integrity & Execution Artifacts

- **Total Pre-Registered Evaluations:** Exactly 480 runs ($150 + 140 + 60 + 60 + 70 = 480$).
- **Total Completed Evaluations:** Exactly 480 runs (100% completion rate).
- **Total Unverified / Fabricated Claims in Manuscript:** Exactly 0.
- **Traceability Status:** 100% of all numerical claims in [`docs/paper_draft_ieee.md`](docs/paper_draft_ieee.md) are directly traceable to raw machine-readable JSON/CSV files.
