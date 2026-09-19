# P0-2 — Paper 3: How much of the reported behaviour is PPO?

Forensic pass, 2026-09-19. **No training, no tuning, no edit to frozen results.**
Method: the frozen `run_session_trajectory()` from `research/scripts/execute_paper3_study.py`, unchanged, was replayed from the five frozen checkpoints (evaluation only) and
with **control policies substituted for the PPO model** (constant actions and random actions passed through the *same* simulator and the *same* canonical guardrails).
All outputs stayed in the session scratchpad. The replay reproduces every frozen Paper 3 number it touches (per-seed MAE, volatility, oscillation, interventions).
Control-policy numbers are **audit diagnostics, not frozen evidence**.

## 0. Bottom line

**The current evidence supports a claim about the guardrail-controlled policy. It does not support a claim that PPO (as trained) is what produces the reported gain, stability, or safety.**

- A policy that ignores the state and always proposes "Same", wrapped in the identical guardrails, gets **MAE 0.673**. Guarded PPO gets **0.673–0.687** (5-seed mean 0.677).
- Against the constant-Same+guardrails control, PPO+guardrails differs in only **5 of 125 sessions**, with a pooled MAE difference of **+0.0044** (95 % session-bootstrap CI [+0.0007, +0.0087]) — PPO is, if anything, *marginally worse*.
- The 0.006 across-seed SD ("stability") is the SD of five copies of the same guardrail rules, not evidence of policy convergence.
- Raw PPO (no guardrails) does carry a small, real, seed-dependent signal. It beats the fixed baseline in all five seeds (MAE 0.804–1.138, mean 0.958 vs 1.200) but only for the two low-skill personas.
- The simple threshold heuristic is better than every PPO variant (0.473).

## 1. Evidence tables

### 1.1 MAE by condition (25 sessions per row: 5 personas × 5 evaluation seeds; frozen simulator; lower is better)

| Condition | MAE | Vol. | Source |
|---|---|---|---|
| Fixed (Same, no guardrails) | **1.200** | 0.000 | frozen |
| Heuristic threshold rule | **0.473** | 0.160 | frozen |
| Raw PPO, seeds 42 / 123 / 456 / 789 / 999 | 1.127 / 0.804 / 1.138 / 0.855 / 0.866 (mean **0.958**, SD 0.161) | 0.078 mean | frozen ablation row = replay |
| PPO + guardrails, same five seeds | 0.687 / 0.673 / 0.676 / 0.673 / 0.676 (mean **0.677**, SD **0.006**) | 0.186 mean | frozen = replay |
| **Constant "Same" + guardrails** (control) | **0.673** | 0.080 | audit diagnostic |
| Constant "Easier" + guardrails (control) | 1.364 | 0.160 | audit diagnostic |
| Constant "Harder" + guardrails (control) | 0.502 | 0.380 | audit diagnostic |
| Random actions + guardrails (20 draws; control) | mean 0.795 (range 0.618–0.946) | 0.416 | audit diagnostic |
| Random actions, no guardrails (20 draws; control) | mean 1.514 (range 1.233–1.764) | 0.585 | audit diagnostic |

Two further points from the controls:
- Guardrails move *every* base policy toward the target (random 1.514 → 0.795; constant-Harder 2.036 → 0.502; constant-Easier 1.709 → 1.364; constant-Same 1.200 → 0.673). The guardrails are a rule-based curriculum policy in their own right, not a thin safety filter.
- Constant "Harder" + guardrails (MAE 0.502) is closer to the heuristic than PPO is. This is a property of this simulator (see §3), not a recommendation.

### 1.2 Per-persona MAE (mean over the five evaluation seeds)

| Persona (target difficulty) | Fixed | Heuristic | Const-Same+G | PPO raw s123 | PPO+G s42 | PPO+G s123 | PPO+G s456 | PPO+G s789 | PPO+G s999 |
|---|---|---|---|---|---|---|---|---|---|
| normal (3.0) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nervous_expert (4.5) | 1.500 | 0.591 | **1.500** | 1.500 | 1.500 | 1.500 | 1.500 | 1.500 | 1.500 |
| lucky_guesser (4.0) | 1.000 | 0.909 | **1.000** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| overconfident_fail (1.5) | 1.500 | 0.591 | 0.591 | 0.591 | 0.591 | 0.591 | 0.591 | 0.591 | 0.591 |
| struggling_junior (1.0) | 2.000 | 0.273 | 0.273 | 0.927 | 0.346 | 0.273 | 0.291 | 0.273 | 0.291 |

- **On nervous_expert and lucky_guesser, guarded PPO is identical to the fixed baseline in every seed** (1.500 and 1.000). PPO never learned to raise difficulty.
- The entire improvement over fixed comes from overconfident_fail (1.500 → 0.591) and struggling_junior (2.000 → ≈0.27–0.35). Guardrails G1/G4 produce that improvement; constant-Same+G reproduces it to three decimals.
- Raw PPO's own improvement is confined to those same two personas and is seed-dependent (raw overconfident_fail: 0.591 in seed 123 only; 1.136 in seed 42; 1.500 in seeds 456/789/999; raw struggling_junior: 0.273 in seed 789, 0.328 in 999, 0.927 in 123, 1.691 in 456, 2.000 in 42).

### 1.3 Paired session-level comparisons (percentile bootstrap, B = 2000, over the 25 or 125 sessions)

| Contrast | Mean MAE difference | 95 % CI | Sessions that differ |
|---|---|---|---|
| PPO+G minus Const-Same+G, seed 42 | +0.015 | [0.000, +0.033] | 3 / 25 |
| … seed 123 | 0.000 | [0.000, 0.000] | 0 / 25 |
| … seed 456 | +0.004 | [0.000, +0.011] | 1 / 25 |
| … seed 789 | 0.000 | [0.000, 0.000] | 0 / 25 |
| … seed 999 | +0.004 | [0.000, +0.011] | 1 / 25 |
| … pooled 125 sessions (pseudo-replicated by seed) | +0.0044 | [+0.0007, +0.0087] | 5 / 125 |
| Const-Same+G minus Fixed | −0.527 | [−0.807, −0.251] | — |
| PPO+G (5-seed mean 0.677) minus Fixed | −0.523 | (frozen) | — |
| Const-Same+G minus Heuristic | +0.200 | [+0.084, +0.345] | — |
| PPO+G seed 123 minus Heuristic | +0.200 | [+0.069, +0.345] | — |
| Raw PPO minus Fixed, seeds 42 / 123 / 456 / 789 / 999 | −0.073 / −0.396 / −0.062 / −0.345 / −0.334 | each CI excludes 0 | — |

### 1.3b Turn-level agreement

Final actions of PPO+guardrails equal those of constant-Same+guardrails on **200 of 250 turns (80.0 %) in every one of the five seeds**; 15 of 25 sessions are action-for-action identical per seed. In the guarded runs the rules determine the action on 101–122 of 250 turns per seed (40–49 %). On the remaining turns PPO's proposals are mostly "Same" (seed 42: 100 Same / 24 Harder / 4 Easier; 123: 100 / 1 / 48; 456: 100 / 16 / 19; 789: 100 / 20 / 10; 999: 100 / 6 / 39 — counts are of PPO's proposals on that run's own non-rule turns; the resulting MAE differs from constant-Same+guardrails by at most 0.015).

## 2. Attribution

| Component | What the frozen + replayed evidence attributes to it |
|---|---|
| **A. PPO (learned policy, no guardrails)** | A modest, seed-dependent reduction vs fixed (mean −0.24 MAE; −0.06 to −0.40 by seed), only for low-skill personas; no ability to raise difficulty for high-skill personas; raw MAE seed SD 0.161. |
| **B. Canonical guardrails (rules G1, G2, G4, G5; G6 never fires)** | Essentially the entire headline improvement (−0.527 MAE with a state-blind base policy); the entire cross-seed "stability" (SD 0.006); a large increase in volatility over raw PPO (0.078 → 0.186, `volatility_reduction_pct = −140.21` is stored in the frozen `paper3_raw_results.json`). |
| **C. Constant-Same behaviour** | Explains PPO's behaviour on about 80 % of guarded turns and reproduces the guarded MAE to three decimals (0.673). PPO's raw action histogram is 67–96 % "Same" depending on seed (raw runs: Same 210/168/239/200/200 of 250). |
| **D. Heuristic** | Better than every PPO condition (0.473 vs 0.677; paired +0.200, CI [+0.07, +0.35]); tracks the two high-skill personas that PPO never adapts to. |

## 3. Why the design cannot separate PPO from the guardrails

1. **The training environment is not the evaluation environment.** Training: 15-step episodes, continuous difficulty in [0.1, 1.0], oracle-imitation reward (`rl/env/interview_env.py`). Evaluation: 10-step sessions, integer difficulty 1–5, ±1 transitions. (Separate P1 finding; it weakens any claim that the evaluation measures what PPO was trained to do.)
2. **Guardrails re-decide 40–49 % of turns and, on the remaining turns, PPO mostly emits "Same".** With a start difficulty of 3 and a "normal" persona target of 3, "Same" is already optimal for that persona; for the two high-skill personas (targets 4.0 and 4.5) the heuristic raises difficulty and reduces MAE, whereas PPO never does.
3. **The evaluation set is 5 personas.** Four of the five persona MAE values are identical across all guarded conditions; the 25-session N is five distinct persona behaviours × five evaluation seeds. Distinguishing PPO from a constant needs personas on which the constant is wrong *and* guardrails are silent (e.g., high-skill personas), which is exactly where PPO does nothing.
4. **No PPO-free guardrail control was in the study design.** The frozen ablation compares raw PPO vs PPO+guardrails only; that comparison cannot identify the PPO contribution.

## 4. What can and cannot be claimed

**Supportable now (frozen numbers + this diagnostic):**
- "In the simulator, the deterministic guardrail rules alone reduce mean difficulty-tracking error from 1.200 (fixed) to about 0.67; PPO+guardrails reaches the same value (0.677, seed SD 0.006)."
- "Raw PPO improves modestly over a fixed baseline (0.958 vs 1.200) with large seed variance (0.804–1.138) and only for low-skill personas."
- "A threshold heuristic tracks the target better than PPO+guardrails (0.473 vs 0.677)."
- "The evaluation cannot distinguish PPO+guardrails from a constant-action policy with the same guardrails (5 of 125 sessions differ; pooled ΔMAE +0.004)."

**Not supportable:**
- "PPO learns adaptive difficulty" / "PPO improves target tracking" *when guardrails are on* — i.e. any headline that attributes 1.200 → 0.677 to PPO.
- "Multi-seed stability of PPO" from the 0.006 SD.
- "PPO outperforms a baseline" other than the fixed-difficulty baseline, and even then only for raw PPO with heterogeneous seeds.
- Any claim about real learners (simulation-only; already in CLAUDE.md).

## 5. Recommended path (recommendations only — USER DECISION REQUIRED)

1. **Reframe Paper 3 (documentation/analysis, no new experiment).** Present the finding as "a guardrail-controlled adaptive policy and a study of what a learned policy adds," reporting raw PPO, guardrails-only (constant-Same+G as a labelled control) and heuristic side by side; state the negative result on PPO's marginal contribution.
2. **If a claim about PPO is wanted, a new experiment is needed** (rerun required; not authorised): evaluate PPO on personas/states where guardrails are silent, add the guardrail-only and random+guardrail controls to the *pre-specified* design, use more personas than five (e.g., a persona grid), compare on the training-consistent environment, and treat persona (not session × seed) as the unit.
3. Do not edit the frozen files; supersede via a new errata/addendum file.

## 6. Classification

`CONFIRMED` (PPO's contribution is not identified) + `ANALYSIS_ERROR` (attributing the guarded MAE and seed stability to PPO).

## 7. Limits

- The controls (constant and random policies) are diagnostics run through the frozen code; they are not part of the frozen study.
- I did not test alternative simulator settings or personas; the conclusions apply to this frozen simulator and persona set.
- Per-turn perf/conf/hes values are not stored in frozen outputs, so counterfactual rule-firing along the raw-PPO path was not computed.
