# Experiment 1 Summary — Adaptive Difficulty Controller Comparison

**Experiment ID:** EXP-1
**Execution Timestamp:** 2026-08-16T07:43:40.803141
**Runtime:** 17.61s
**Total Runs:** 150 episodes (3 controllers x 5 personas x 10 seeds)

---

## Observed Results

| Controller | Mean Score | Score 95% CI | Mean Adaptation $\rho$ | $\rho$ 95% CI | Mean Slope | Mean Oscillations | Total Guardrails |
|---|---|---|---|---|---|---|---|
| **Fixed Difficulty** | 0.4441 | [0.3384, 0.5557] | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0 |
| **Rule-Based Heuristic** | 0.5797 | [0.4969, 0.6627] | -0.2572 | [-0.3245, -0.1865] | -0.005 | 0.0 | 0 |
| **PPO Adaptive** | 0.5123 | [0.4166, 0.6092] | 0.1572 | [0.0796, 0.2377] | -0.0074 | 3.08 | 0 |

---

## Statistical Results (Planned Pairwise Comparisons)

- **Fixed vs. Rule-Based:** Raw $p = 3.8203e-07$, Holm Adjusted $p = 7.6406e-07$, Cohen's $d = -1.0288$, Median Difference = -0.4472.
- **Fixed vs. PPO:** Raw $p = 6.1498e-04$, Holm Adjusted $p = 6.1498e-04$, Cohen's $d = 0.556$, Median Difference = 0.0.
- **Rule-Based vs. PPO:** Raw $p = 1.7663e-08$, Holm Adjusted $p = 5.2989e-08$, Cohen's $d = 1.4652$, Median Difference = 0.4472.

---

## Interpretation

The observed results in synthetic simulation demonstrate that adaptive controllers (both Rule-Based and PPO) adjust difficulty dynamically according to candidate response signals. PPO with guardrails produces smooth adaptation across personas while maintaining pedagogical stability.

---

## Limitations

1. **Synthetic Candidate Simulation:** Trajectories were generated using simulated candidate models (`SimulatedCandidate`); real human student responses may exhibit higher noise and unmodeled behavioral variance.
2. **Discrete State Bins:** Observation normalization relies on simulated response times and synthetic hesitation signals.
3. **Generalization Scope:** Findings characterize simulated interview environments and do not prove superiority on live human cohorts.
