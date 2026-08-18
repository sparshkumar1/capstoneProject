# Experiment 1 — Adaptive Difficulty Controller Comparison

**Experiment ID:** EXP-1
**Target Submission:** IEEE ICALT 2026 / IEEE EDUCON 2026 (Section V & VI-B)
**Priority:** **HIGH PRIORITY**

---

## 1. Research Question & Pre-Registered Hypothesis

- **Research Question:** Does adaptive difficulty produce different and potentially more appropriate interview trajectories than fixed difficulty, and does PPO provide measurable benefit beyond a deterministic rule-based controller?
- **Pre-Registered Hypothesis:** Adaptive controllers produce different and potentially more appropriate difficulty trajectories than fixed difficulty. PPO may or may not outperform the deterministic rule-based controller in simulation.

---

## 2. Experimental Conditions (Independent Variable)

1. **Condition A — Fixed Difficulty Baseline:** Difficulty is locked at level 3 (mid) throughout all 15 questions.
2. **Condition B — Deterministic Rule-Based Controller:** Difficulty transitions $\pm 1$ level based on hardcoded score thresholds ($>0.80 \to \text{Harder}, <0.40 \to \text{Easier}$) with G1–G6 safety guardrails.
3. **Condition C — PPO Policy + Guardrails:** Pre-trained PPO policy (seed 123) over the strict 6D state representation $\mathbf{s} \in [0, 1]^6$ with post-policy G1–G6 safety guardrails.

---

## 3. Mathematical Count Verification

$$\text{Total Episodes} = 3\text{ Controllers} \times 5\text{ Personas} \times 10\text{ Seeds} = \mathbf{150\text{ episodes}}$$

- **Candidate Personas:** 5 distinct skill profiles (`normal`, `nervous_expert`, `lucky_guesser`, `overconfident_fail`, `struggling_junior`).
- **Matched Random Seeds:** 10 held-out evaluation seeds ($1001 \le S \le 1010$) per persona $= 50$ matched runs per controller.
- **Leakage Isolation:** Evaluation seeds ($1001\text{--}1010$) are strictly held-out and disjoint from the PPO training seed ($123$).

---

## 4. Planned Pairwise Statistical Comparisons

To avoid post-hoc selective reporting, the three planned pairwise comparisons are frozen:

1. **Fixed vs. Rule-Based:** Evaluates the baseline benefit of simple rule-based adaptation over constant difficulty.
2. **Fixed vs. PPO:** Evaluates policy-driven adaptation relative to constant difficulty.
3. **Rule-Based vs. PPO:** Evaluates whether reinforcement learning provides measurable behavioral differences beyond hand-tuned heuristic thresholds.

### Statistical Procedure
- **Primary Test:** Paired Wilcoxon signed-rank test across matched candidate seeds.
- **Multiplicity Correction:** Holm-Bonferroni step-down procedure over the 3 comparisons.
- **Effect Sizes:** Paired Cohen's $d$ and 95% bootstrap BCa confidence intervals ($B = 10,000$ resamples).
- **Secondary Sensitivity Analysis:** Paired Student's t-test (reported secondarily if normality assumptions hold).

---

## 5. Execution Command (Stage 16)

```bash
python experiments/experiment_1_adaptive_difficulty/runner.py --config experiments/experiment_1_adaptive_difficulty/config.json
```

*Results Status in Stage 15:* **RESULTS NOT YET GENERATED (Design & Pre-Registration Frozen)**
