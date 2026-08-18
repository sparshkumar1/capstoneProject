# Experiment 4 — Candidate-State Personalization & Trajectory Divergence

**Experiment ID:** EXP-4
**Target Submission:** IEEE ICALT 2026 / IEEE EDUCON 2026 (Section III & V)
**Priority:** **HIGH PRIORITY**

---

## 1. Research Question & Pre-Registered Hypothesis

- **Research Question:** Does candidate-state-driven personalization produce measurably different and more targeted interview trajectories than non-adaptive questioning?
- **Pre-Registered Hypothesis:** Candidate-state personalization produces statistically significant trajectory divergence between strong and struggling candidate profiles, ensures topic remediation on identified weak concepts, and eliminates question repetition via 3-level deduplication.

---

## 2. Selection Conditions (Independent Variable)

1. **Condition A — Uniform Random Non-Adaptive:** Selects random questions from the 125-item question bank without conditioning on prior performance or difficulty targets.
2. **Condition B — Topic-Count Heuristic Baseline:** Selects questions to balance topic frequencies and match nearest difficulty without weakness tracking (`agents/question_selector/question_selector.py`).
3. **Condition C — Production Personalized Selector:** Conditioned on live `candidate_state` (weakness remediation, strength advancement, 3-level deduplication, Easy-start guarantee $\le 2$).

---

## 3. Dependent Variables & Metrics

1. **Trajectory Euclidean Divergence:** Distance between difficulty profiles of Strong ($S=0.85$) vs Weak ($S=0.25$) candidates:
   $$\text{Divergence} = \|\mathbf{d}_{\text{strong}} - \mathbf{d}_{\text{weak}}\|_2$$
2. **Question Repetition Rate:** Proportion of sessions containing duplicate IDs or questions with Jaccard lexical overlap $\ge 0.75$.
3. **Weakness Remediation Rate:** Proportion of questions probing topics where prior turn score $S_{\text{tech}} < 0.50$.
4. **Topic Coverage Entropy ($H$):** Shannon entropy over topic selections:
   $$H = -\sum_{i=1}^K p_i \log_2 p_i$$
5. **First Question Difficulty Constraint:** Verification that $d_1 \le 2$ (Easy / Easy-Medium).

---

## 4. Execution Command (Stage 16)

```bash
python experiments/experiment_4_personalization/runner.py --config experiments/experiment_4_personalization/config.json
```

*Results Status in Stage 15:* **RESULTS NOT YET GENERATED (Design & Pre-Registration Frozen)**
