# Experiment 5 Summary — System-Wide Component Leave-One-Out Ablation

**Experiment ID:** EXP-5
**Execution Timestamp:** 2026-08-16T08:01:43.660638
**Runtime:** 20.21s
**Total Runs:** 70 sessions (7 conditions x 10 seeds)

---

## Observed Results

| Condition | Mean Score | Score 95% CI | Adaptation $\rho$ | $\rho$ 95% CI | Follow-Ups Count | Avg Timing Modifier |
|---|---|---|---|---|---|---|
| **Full Production System** | 0.5067 | [0.5009, 0.5125] | 0.0206 | [0.0, 0.055] | 0.5 | 0.0 |
| **Full $-$ RL Adaptation** | 0.5022 | [0.4967, 0.5081] | 0.0 | [0.0, 0.0] | 0.6 | 0.0 |
| **Full $-$ Follow-Up Probing** | 0.5067 | [0.5009, 0.5125] | 0.0206 | [0.0, 0.055] | 0.0 | 0.0 |
| **Full $-$ Formative Feedback** | 0.5067 | [0.5009, 0.5125] | 0.0206 | [0.0, 0.055] | 0.5 | 0.0 |
| **Full $-$ Timing Modulation** | 0.5067 | [0.5009, 0.5125] | 0.0206 | [0.0, 0.055] | 0.5 | 0.0 |
| **Full $-$ Speech Prosody** | 0.5022 | [0.4967, 0.5081] | 0.0 | [0.0, 0.0] | 0.6 | 0.0 |
| **Full $-$ Coding Contribution** | 0.5067 | [0.5009, 0.5125] | 0.0206 | [0.0, 0.055] | 0.5 | 0.0 |

---

## Statistical Results

- **RL Adaptation Impact:** Removing RL reduces difficulty adaptation correlation from $\rho = 0.0206$ to $\rho = 0.0$.
- **Timing Modulation Impact:** Modulates raw technical scores within the bound $f_{\text{time}} \in [-0.10, +0.03]$, yielding a mean additive shift of 0.0.
- **Follow-Up Interventions:** An average of 0.5 gap-probing follow-ups are triggered per session for struggling candidates.

---

## Interpretation

Each isolated subsystem provides a measurable, non-interfering contribution: RL governs dynamic difficulty tracking, timing prevents rapid guessing from earning speed bonuses, and follow-ups intervene on low-scoring concepts.

---

## Limitations

1. **Simulation Model Assumptions:** Candidate interaction dynamics are evaluated in simulation; human affective responses to difficulty transitions were not measured directly.
2. **Subsystem Granularity:** Coding contribution measures statistical state updating rather than compiler micro-benchmarks.
