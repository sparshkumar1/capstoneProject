# PrepAIred — Research Methodology & Scientific Roadmap

**Document Version:** 2.1.0 (Authoritative Stage 14 Consistency Correction)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Research Contributions & Vision

PrepAIred addresses the challenge of automated, formative technical interview assessment for software engineering. The core scientific contributions under investigation are:

1. **Three-Component Evaluator ($S_1 + S_2 + R$):** An answer evaluation pipeline fusing surface semantics ($S_1$), knowledge concept coverage ($S_2$), and deep reasoning entailment ($R$) into a calibrated scoring model.
2. **Pedagogically Shielded PPO Adaptation:** A discrete-action reinforcement learning policy operating on a 6D observation space with safety guardrails to personalise interview difficulty.
3. **Evidence-Grounded Formative Feedback & Gap Probing:** A feedback generation mechanism anchored on verbatim candidate transcripts and rubric concept coverage.
4. **Open Inter-Rater Reliability Harness:** Open benchmark suite supporting Krippendorff's $\alpha$ calculation and ablation reproducibility.

---

## 2. Evaluator Ablation Study & Empirical Results

We conducted an ablation study across seven weight configurations against a curated dataset of 20 technical interview answers spanning four quality levels (Blank, Off-Topic, Partial, Good) across core CS topics (Two Sum, Reverse Linked List, Merge Sort, Memory Management).

Ratings were collected from three independent human raters using a 0–10 scale (normalized to $[0, 1]$). Human scores were hidden from raters during grading to prevent anchoring bias.

### Evaluator Ablation Results Table

| Configuration ID | Weight $S_1$ (Semantic) | Weight $S_2$ (Concept) | Weight $R$ (Reasoning) | Spearman $\rho$ | $p$-value |
|---|---|---|---|---|---|
| **S1 Only** | $1.00$ | $0.00$ | $0.00$ | $0.7620$ | $7.13 \times 10^{-5}$ |
| **S2 Only** | $0.00$ | $1.00$ | $0.00$ | $0.7462$ | $1.26 \times 10^{-4}$ |
| **R Only** | $0.00$ | $0.00$ | $1.00$ | $0.3961$ | $0.0838$ |
| **S1 + R** | $0.23$ | $0.00$ | $0.77$ | $0.7818$ | $3.58 \times 10^{-5}$ |
| **S2 + R** | $0.00$ | $0.41$ | $0.59$ | $0.8179$ | $9.32 \times 10^{-6}$ |
| **S1 + S2** | $0.30$ | $0.70$ | $0.00$ | $0.8358$ | $4.46 \times 10^{-6}$ |
| **Full Pipeline (Paper)** | **$0.15$** | **$0.35$** | **$0.50$** | **$0.8358$** | **$4.46 \times 10^{-6}$** |

- **Empirical Scope:** The evaluator showed strong correlation with blinded human ground-truth ratings on the 20-sample benchmark dataset (Spearman $\rho=0.8358, p=4.46 \times 10^{-6}$), while inter-rater reliability among the three human raters was Krippendorff $\alpha=0.8255$ ($n=20$ paired items, 56 total judgments).
- **Finding:** The multi-component configuration ($0.15 \cdot S_1 + 0.35 \cdot S_2 + 0.50 \cdot R$) achieves high correlation while preventing keyword stuffing via reasoning dampening.


---

## 3. RL Difficulty Adaptation Experiments (Simulation Pilot)

| Adaptation Condition | Mean Adaptation $\rho$ | Difficulty Slope | Mean Final Score | PPO Contribution Rate |
|---|---|---|---|---|
| **PPO + Guardrails** | $0.871 \pm 0.064$ | $+0.0475 \pm 0.0080$ | $0.620 \pm 0.020$ | $62.0\%$ |
| **PPO Only (No Guardrails)**| $0.467 \pm 0.201$ | $+0.0287 \pm 0.0096$ | $0.568 \pm 0.041$ | $100.0\%$ |
| **Heuristic Only** | $-0.040 \pm 0.248$ | $+0.0065 \pm 0.0158$ | $0.540 \pm 0.061$ | $0.0\%$ |

*Note on Empirical Scope:* RL ablation results reflect simulated candidate trajectories in `InterviewEnv`; full comparative validation on real human cohorts will be executed in subsequent research phases.

---

## 4. Planned Research Experiments (Stages 15 & 16)

The research protocol establishes five planned comparative experiments (no results are claimed prior to execution):

- **Experiment 1 (RL Comparative Baseline):** PPO + Guardrails vs. Heuristic vs. Fixed Difficulty on candidate evaluation cohorts.
- **Experiment 2 (Evaluator Cross-Domain Scaling):** Evaluator ablation scaling across $n \ge 100$ items across all 13 CS topics.
- **Experiment 3 (Feedback Remediation Utility):** Comparative ablation of Formative vs. Simple Score feedback.
- **Experiment 4 (Personalization Efficacy):** Adaptive vs. Random vs. Linear question sequencing trajectories.
- **Experiment 5 (Component Ablation):** Evaluate the individual contributions of:
  1. Reinforcement learning difficulty adaptation
  2. Follow-up probing agent
  3. Personalized formative feedback
  4. Response timing modulation
  5. Speech communication features
  6. Sandboxed coding performance
  *(No results or outcomes are claimed prior to execution).*

---

## 5. Scientific Limitations & Future Work

1. **Evaluator Sample Size:** $n=20$ serves as a validated pilot study; expanding to $n \ge 100$ answers across all 13 topics will be conducted.
2. **Simulation-to-Real RL Transfer:** PPO was trained on `SimulatedCandidate`; online fine-tuning on real interview sessions is planned.
3. **Longitudinal Learning Outcomes:** Controlled double-blind pre/post assessment trials are required before claiming candidate interview efficacy improvements.
