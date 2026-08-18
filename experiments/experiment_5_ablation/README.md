# Experiment 5 — System-Wide Component Leave-One-Out Ablation

**Experiment ID:** EXP-5
**Target Submission:** IEEE ICALT 2026 / IEEE EDUCON 2026 (Section VI & VII)
**Priority:** **HIGH PRIORITY**

---

## 1. Research Question & Pre-Registered Hypothesis

- **Research Question:** Which implemented subsystems contribute measurable changes to the system's runtime behavior, candidate assessment accuracy, and pacing?
- **Pre-Registered Hypothesis:** Each separable subsystem provides a distinct, non-redundant contribution to candidate assessment, difficulty adaptation, or pacing control.

---

## 2. Seven Scientifically Isolated Ablation Conditions

1. **Full Production System:** Complete orchestrator with PPO strategy, Evaluator, Follow-Up Agent, FeedbackAgent, QuestionTimer, and Docker C Sandbox.
2. **Ablation 1 ($-\text{RL Adaptation}$):** Difficulty strategy disabled; difficulty locked at Level 3.
3. **Ablation 2 ($-\text{Follow-Up Probing}$):** Gap probing disabled; session proceeds strictly linearly through main questions.
4. **Ablation 3 ($-\text{Formative Feedback}$):** Formative feedback disabled; score-only baseline returned.
5. **Ablation 4 ($-\text{Timing Modulation}$):** Timing modifier $f_{\text{time}} = 0.000$ unconditionally; speed modulation inactive.
6. **Ablation 5 ($-\text{Speech Prosody}$):** Acoustic confidence and hesitation fixed at neutral $0.50$.
7. **Ablation 6 ($-\text{Coding Contribution}$):** Real Docker container executes candidate C code, but coding performance is excluded from downstream candidate-state updating and difficulty adaptation.

---

## 3. Mathematical Count Verification

$$\text{Total Sessions} = 7\text{ Conditions} \times 10\text{ Matched Seeds} = \mathbf{70\text{ sessions}}$$

- **Matched Seeds:** 10 evaluation seeds ($3001 \le S \le 3010$).
- **Session Length:** 15 turns per session ($1,050$ total question/coding turns evaluated).

---

## 4. Dependent Variables & Metrics

1. **Session Score Mean & Variance ($\sigma_{\text{score}}^2$):** Sensitivity to scoring modulations.
2. **Difficulty Adaptation $\rho$:** Measure of difficulty alignment with candidate ability.
3. **Total Follow-Up Interventions:** Number of gap-probing turns triggered.
4. **Average Timing Modifier ($\bar{f}_{\text{time}}$):** Impact of pacing modulation on final scores.
5. **Diagnostic Granularity Index:** Number of distinct diagnostic features produced per turn.

---

## 5. Execution Command (Stage 16)

```bash
python experiments/experiment_5_ablation/runner.py --config experiments/experiment_5_ablation/config.json
```

*Results Status in Stage 15:* **RESULTS NOT YET GENERATED (Design & Pre-Registration Frozen)**
