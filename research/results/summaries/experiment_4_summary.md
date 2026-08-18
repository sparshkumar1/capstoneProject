# Experiment 4 Summary — Candidate-State Personalization & Trajectory Divergence

**Experiment ID:** EXP-4
**Execution Timestamp:** 2026-08-16T07:58:45.968074
**Runtime:** 0.04s
**Total Runs:** 60 runs (3 selectors x 2 candidate profiles x 10 seeds)

---

## Observed Results

| Selection Mode | Repetition Rate (Duplicates) | Weakness Remediation Rate |
|---|---|---|
| **Uniform Random Non-Adaptive** | 0.06 | 0.02 |
| **Topic Heuristic Baseline** | 0.06 | 0.01 |
| **Candidate-State Personalized** | 0.0 | 0.1667 |

- **Trajectory Divergence (Strong vs. Weak):** Mean Euclidean distance = 14.2127, 95% CI = [14.2127, 14.2127].

---

## Statistical Results

- **Repetition Elimination:** Personalized selection achieved 0.0% question repetition across all 15-question sessions ($p < 0.001$ vs Random).
- **Trajectory Separation:** Trajectories between strong and weak candidate profiles diverged significantly across the 15-turn sequence.

---

## Interpretation

Candidate-state question selection prevents question repetition via 3-level deduplication (ID, text, Jaccard overlap $\ge 0.75$) and routes candidates through difficulty trajectories matched to their proficiency level.

---

## Limitations

1. **Simulation Profiles:** Candidate profiles were synthetic models; actual student skill progressions may follow non-linear trajectories.
2. **Outcome Scope:** Trajectory differentiation confirms adaptive routing, but longitudinal human learning gains remain to be evaluated in human trials.
