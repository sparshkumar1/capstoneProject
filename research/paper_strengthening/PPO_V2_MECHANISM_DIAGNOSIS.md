# PPO V2 — Mechanism Diagnosis (diagnostic-only, no new training)

Predeclared before any of the analysis below: this diagnosis uses only already-stored, frozen-for-their-own-reports evaluation data (`e1_dev_eval/e1_dev_eval_raw.json`, `e1_dev_eval_extended/e1_dev_eval_raw.json`) and the already-stored per-step training logs. No new training, no new random draws, no confirmatory data.

## Question 2.1.5 — Which persona groups account for the regression?

Per-cell MAE regression (extended-budget minus primary-budget, condition B2, pooled over 5 training seeds × 5 dev eval seeds = 25 episodes/cell):

| skill | k | primary MAE | extended MAE | Δ |
|---|---|---|---|---|
| 0.80 | 0.60 | 0.1636 | 1.0000 | **+0.8364** |
| 0.80 | 0.45 | 0.1636 | 0.9345 | **+0.7709** |
| 0.80 | 0.30 | 0.0909 | 0.7382 | **+0.6473** |
| 0.80 | 0.00 | 0.2727 | 0.5527 | **+0.2800** |
| 0.90 | 0.60 | 0.5909 | 0.8600 | +0.2691 |
| 0.90 | 0.45 | 0.5909 | 0.6673 | +0.0764 |
| 0.90 | 0.30 | 0.5909 | 0.5909 | 0.0000 |
| 0.90 | 0.00 | 0.6055 | 0.6055 | 0.0000 |
| all other 16 cells (skill ≤ 0.65) | — | — | — | ≤ 0.02 each |

**The top 6 cells (all at skill ∈ {0.80, 0.90}) account for 99.4% of the total pooled-cell regression.** Every cell at skill ≤ 0.65 is stable or trivially different (≤0.02) between budgets. This is not a diffuse, system-wide degradation — it is concentrated almost entirely in the two highest-skill personas, and within that, overwhelmingly in skill=0.80 specifically (skill=0.90 is largely stable at k∈{0.0,0.3}, exactly unchanged).

## Question 2.1.1/2.1.4/2.1.6 — Does the policy learn, then lose, a specific action on this persona group?

Raw (pre-shield is not available in this stored data; post-shield `final_actions` is) action-distribution counts, pooled 5 seeds × 5 eval seeds × 10 turns = 250 actions/cell:

| skill | k | primary Harder-rate | extended Harder-rate |
|---|---|---|---|
| 0.80 | 0.00 | 20/250 (8.0%) | 14/250 (5.6%) |
| 0.80 | 0.30 | 25/250 (10.0%) | 8/250 (3.2%) |
| 0.80 | 0.45 | 25/250 (10.0%) | 2/250 (0.8%) |
| 0.80 | 0.60 | 25/250 (10.0%) | **0/250 (0.0%)** |
| 0.90 | 0.00 | 25/250 (10.0%) | 25/250 (10.0%) — **unchanged** |
| 0.90 | 0.30 | 25/250 (10.0%) | 25/250 (10.0%) — **unchanged** |
| 0.90 | 0.45 | 25/250 (10.0%) | 25/250 (10.0%) — unchanged (count) |
| 0.90 | 0.60 | 25/250 (10.0%) | 21/250 (8.4%) |

**Yes: the primary-budget checkpoint proposes "Harder" for skill=0.80 at a stable ~8-10% rate across all four k-values; the extended-budget checkpoint has nearly or fully abandoned "Harder" for exactly this persona (down to 0-6%), while skill=0.90's Harder-rate is materially preserved at 3 of 4 k-values.** This directly answers 2.1.1 (yes, a useful action on a specific persona is learned and then lost) and 2.1.6 (the primary-budget advantage is not a diffuse skill but a narrow, persona-specific behavior — consistent with, and a generalization of, `E1_DEVELOPMENT_RUN_REPORT.md`'s "single correctly-timed Harder action" finding, which is now shown to be one instance of a broader skill=0.80-specific pattern, not an isolated fluke at one (skill,k) cell).

## Question 2.1.7 — Does oracle-agreement (proxy for "did the policy still track the oracle locally") also collapse, or is this something subtler?

| skill=0.80, k | primary oracle_agreement | extended oracle_agreement |
|---|---|---|
| 0.00 | 0.916 | 0.848 |
| 0.30 | 0.920 | 0.776 |
| 0.45 | 0.824 | **0.940** |
| 0.60 | 0.828 | **0.980** |

For k=0.45/0.60, oracle-agreement *rises* even as MAE collapses to ~1.0. This is not a contradiction: `oracle_agreement` measures whether the *local, per-step* action matches what the oracle rule would prescribe given the *current* (possibly already off-target) state, while `mae` measures the whole-episode gap between achieved difficulty and the fixed persona target. A policy that stops proposing "Harder" gets stuck below the target difficulty; once stuck, both the policy and the oracle rule can locally agree "Same" is the locally-sensible action from that (wrong) position, so local agreement can rise even as the episode-level tracking error stays high. This is consistent with, not contrary to, the action-collapse finding above — it is the mechanism by which the collapse becomes self-reinforcing (once "Harder" stops being proposed, the state never reaches a region where the oracle would prescribe "Harder" either, so there is no local signal pushing the policy back toward it).

## Question 2.1.2/2.1.3 — Is this a reward/objective misalignment?

Consistent with, not newly proven by, this diagnostic: the frozen reward's decision-alignment term (weight 0.60) rewards matching the *oracle's local action*, not the episode-level difficulty-tracking error that `mae` (the evaluation metric) actually measures. §XI.2's existing finding already establishes this reward/metric gap exists in general (PPO+G is statistically indistinguishable from Constant-Same+G under the confirmatory MAE metric despite a nontrivial decision-alignment reward term). The mechanism identified above shows a *specific* way this gap can bite: once training drifts a policy toward a "Same"-heavy region for a specific persona, the reward signal (rewarding local oracle-agreement) provides no strong corrective pressure to climb back out, because local oracle-agreement can *improve* even as episode-level tracking error worsens. This is a plausible, disclosed account, not independently proven by a causal intervention in this diagnostic pass.

## Conclusion and chosen intervention

The primary-budget checkpoint is not "less trained" than the extended-budget one in a way that would predict it performing worse — it is a **narrower, persona-specific behavior (skill=0.80 Harder-differentiation) that is present at 24,576 steps and lost, specifically for that persona, by 98,304 steps**, while performance elsewhere is stable or (skill=0.90) largely preserved. This is exactly the situation "checkpoint selection based on a prespecified development criterion" (task item 2.2) is suited to, and is lower-risk than a reward redesign (which would touch frozen reward code and require a new, separately-justified predeclared reward term with its own validation burden, for a mechanism only partially understood). The chosen intervention, executed next: **periodic checkpointing during a single training run per seed, with a single, cross-seed-predeclared stopping interval selected on the development grid only** (never on confirmatory data) — testing whether this recovers the primary-budget advantage without needing to guess the right budget in advance, and specifically whether it prevents the skill=0.80 collapse identified above. See `PPO_V2_CHECKPOINT_SELECTION_REPORT.md` for the experiment and result.
