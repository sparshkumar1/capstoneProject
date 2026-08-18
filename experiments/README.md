# PrepAIred — Master Research Experiment Protocols (Pre-Registered)

**Document Version:** 2.0.0 (Stage 15 Pre-Registration & Design Freeze — Verified)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Purpose:** Pre-registered experimental protocols, configurations, runner scripts, and schemas for scientific evaluation in Stage 16.

> [!IMPORTANT]
> **Stage 15 Design Freeze Invariant:** This directory contains experimental designs, parameter configurations, runner scripts, and output schemas. **No experimental results, fake data, or synthetic p-values are generated in Stage 15.** Actual experimental execution and data collection occur in Stage 16.

---

## Master Experiment Registry & Exact Counts

| Experiment ID | Directory | Research Question | Independent Variable | Primary Metrics | Exact Mathematical Sample Count | Status in Stage 15 | Priority |
|---|---|---|---|---|---|---|:---:|
| **EXP-1** | [`experiment_1_adaptive_difficulty/`](experiment_1_adaptive_difficulty/) | Does adaptive difficulty produce different and potentially more appropriate interview trajectories than fixed difficulty, and does PPO provide measurable benefit beyond a deterministic rule-based controller? | Controller $\in \{\text{Fixed}, \text{Rule-Based}, \text{PPO}\}$ | Adaptation $\rho$, slope, score variance, oscillation count | $3\text{ controllers} \times 5\text{ personas} \times 10\text{ seeds} = \mathbf{150\text{ episodes}}$ | **PRE-REGISTERED (RUNNER READY)** | **HIGH** |
| **EXP-2** | [`experiment_2_evaluation/`](experiment_2_evaluation/) | Which components of the structured evaluator contribute to agreement with human ratings, and does the full multi-component evaluator provide measurable benefit over its individual components? | Evaluator Config $\in \{\text{S1}, \text{S2}, \text{R}, \text{S1+R}, \text{S2+R}, \text{S1+S2}, \text{Full}\}$ | Spearman $\rho$, $p$-value, MAE, RMSE vs. human ratings | $7\text{ configs} \times 20\text{ pilot items} = \mathbf{140\text{ item evaluations}}$ | **PRE-REGISTERED (RUNNER READY)** | **HIGH** |
| **EXP-3** | [`experiment_3_feedback/`](experiment_3_feedback/) | Does candidate-specific structured feedback differ measurably from generic feedback in transcript grounding, misconception diagnosis, and actionable remediation? | Feedback Mode $\in \{\text{Generic Template}, \text{Evaluator-Structured}, \text{Qwen-7B}\}$ | Lexical grounding ratio, gap coverage, actionability count | $3\text{ conditions} \times 20\text{ items} = \mathbf{60\text{ feedback evaluations}}$ | **PRE-REGISTERED (RUNNER READY)** | **MEDIUM** |
| **EXP-4** | [`experiment_4_personalization/`](experiment_4_personalization/) | Does candidate-state-driven personalization produce measurably different and more targeted interview trajectories than non-adaptive questioning? | Selector $\in \{\text{Uniform Random}, \text{Topic Baseline}, \text{Candidate State}\}$ | Trajectory divergence, Jaccard repetition rate, remediation targeting | $3\text{ selectors} \times 2\text{ profiles} \times 10\text{ seeds} = \mathbf{60\text{ runs}}$ | **PRE-REGISTERED (RUNNER READY)** | **HIGH** |
| **EXP-5** | [`experiment_5_ablation/`](experiment_5_ablation/) | Which implemented subsystems contribute measurable changes to the system's runtime behavior, candidate assessment accuracy, and pacing? | Ablated Subsystem $\in \{\text{Full}, -\text{RL}, -\text{FollowUp}, -\text{Feedback}, -\text{Timing}, -\text{Speech}, -\text{Coding}\}$ | Score variance, adaptation $\rho$, follow-up count, pacing modifier | $7\text{ conditions} \times 10\text{ matched seeds} = \mathbf{70\text{ sessions}}$ | **PRE-REGISTERED (RUNNER READY)** | **HIGH** |

---

## Global Scientific & Methodological Standards

1. **Pre-Registration:** All hypotheses, metrics, candidate seeds, and statistical tests are frozen prior to execution.
2. **Planned Pairwise Statistics (EXP-1):** Primary statistical testing uses the paired Wilcoxon signed-rank test with Holm-Bonferroni multiplicity correction over the 3 planned pairwise comparisons (`Fixed vs Rule-Based`, `Fixed vs PPO`, `Rule-Based vs PPO`). Paired Cohen's $d$ and 95% bootstrap BCa confidence intervals are reported.
3. **Evaluator Scope & Sample Size (EXP-2):** EXP-2 is explicitly classified as a **pilot evaluation study on $n=20$ curated answers** evaluated by 3 blinded human raters ($\alpha=0.8255$). An optional target protocol for $\ge 100$ items across 13 topics is pre-registered without fabricating uncollected ratings.
4. **Clean Component Isolation (EXP-5):** Every ablation condition isolates a single separable subsystem without altering container execution semantics (e.g. coding turn scores are excluded from downstream state updates while real Docker execution is preserved).
5. **Neutral Scientific Language:** All documentation uses neutral phrasing (*"evaluates comparative performance against"*, *"evaluates differences relative to"*) with zero unearned claims of improvement or superiority.
