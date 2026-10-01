# E1 Dynamics Match V1 — Factorial Experiment Report

**Protocol:** `research/paper_strengthening/E1_DYNAMICS_MATCH_V1_PROTOCOL.md`, SHA-256 `8beae2d83d43cffd5308ca6378a90dface8bd1be5753877d592b6ea8b1da75e1`. **Commit `8e6cea8`, tag `explore/E1-dynamics-match/v1`, local only, not pushed.** Run manifest: `research/paper_strengthening/results/e1dynmatch_v1/run_manifest.json`, `status: completed`. User-approved 40-run primary factorial experiment.

## 1. Verified source findings (Phase 1)

All three documented train/eval dynamics mismatches confirmed real by direct code reading, plus one further mismatch found and disclosed before expanding the design (§1 of the protocol, reproduced in brief):
- **Step size:** training ±0.1 on `[0.1,1.0]`; evaluation ±0.2-equivalent, effectively on `[0.2,1.0]` — the floor bound (0.1 vs 0.2) is a 4th mismatch, folded into Factor A's "matched" level rather than expanded into a 4th orthogonal factor.
- **Horizon:** training 15, evaluation 10.
- **Initial difficulty:** training `Uniform(0.3,0.7)`, evaluation fixed `0.6`.
- **LR schedule:** constant (verified against installed SB3 source: a plain-float `learning_rate` is wrapped in a schedule that ignores `progress_remaining`). Empirical spot-check: an intermediate checkpoint (16,384 steps, seed 42) from a longer run is **not bit-identical in weights** to an independently-budgeted 16,384-step run (max param diff ≈0.070) but **is bit-identical in dev-eval MAE** — disclosed, not glossed over, and this iteration's own intermediate checkpoints are reported as snapshots of the single 24,576-step schedule, never conflated with independent runs.
- **V2 gate-activation denominator error found and corrected:** `E1_IMPROVE_V2_REPORT.md` mis-stated `45/3000`; the correct figure is `45/6,000` (600 episodes × 10 steps).

## 2. Design (Phase 2) — as registered, unaltered

2×2×2 factorial on B2, 8 arms (`OOO` … `MMM`), 5 paired training seeds `[42,123,456,789,999]`, primary budget 24,576 steps, intermediate checkpoints at 8,192/16,384 (snapshots of the same schedule, not independent runs), evaluation on `EVAL_SEEDS_DEV=[1001,2002,3003,4004,5005]` on the existing 24-cell grid. Reward, observation/action space, guardrails, evaluator, target formula, evaluation simulator: unchanged (verified — see §5).

## 3. Execution summary

**40/40 primary runs completed, 0 failures** (~72s/run, ~48 min total). **Shared training log integrity verified: `rl/env/training_logs/interview_data.csv` SHA-256 unchanged before/after** (`9937d8a8...`, identical both times). **Frozen files/checkpoints/prior E1/E1-Improve results: unmodified** (`git status` clean on every protected path). **Confirmatory seeds (`21021`–`40040`) and held-out profiles: never referenced** (verified directly; the one grep hit across all new output files is the run manifest's own disclosure text stating they are locked, not an actual usage). **99/99 tests pass** (89 pre-existing + 10 new dynamics-variant tests).

## 4. Full baseline and factorial comparison (Phase 4/5)

### Pooled MAE by arm, all three checkpoint steps

| Arm | 8,192 | 16,384 | 24,576 | gap to Heuristic+G (0.2674) at 24,576 |
|---|---|---|---|---|
| **OOO** (all-original = standard B2 training) | 0.2776 | 0.2697 | **0.2735** | +0.0061 |
| **OOM** (only initial-difficulty matched) | 0.2824 | 0.2686 | **0.2702** | **+0.0028 (closest to Heuristic+G)** |
| OMO (only horizon matched) | 0.3115 | 0.2841 | 0.3111 | +0.0437 |
| OMM (horizon+initial-diff matched) | 0.3811 | 0.3267 | 0.3283 | +0.0609 |
| MOO (only step-size matched) | 0.3317 | 0.3167 | 0.4045 | +0.1371 |
| MOM (step-size+initial-diff matched) | 0.3182 | 0.3356 | 0.3271 | +0.0597 |
| MMO (step-size+horizon matched) | 0.3624 | 0.3050 | 0.3314 | +0.0640 |
| **MMM** (all-matched) | 0.3735 | 0.3877 | **0.3903** | **+0.1229 (worst but one)** |

**Harness-correctness check, passed:** `OOO`'s 8,192/16,384/24,576 numbers (`0.2776/0.2697/0.2735`) are **exact matches, to 4 decimal places**, of E1-Improve V1's own already-reported checkpoint-trace numbers for standard B2 training — confirming the new factorial harness reproduces the existing, registered training pipeline exactly when all factors are set to "original."

### Primary comparison: MMM vs. OOO at 24,576 steps

| | OOO | MMM | MMM − OOO |
|---|---|---|---|
| Pooled MAE | 0.2735 (SD 0.2269) | 0.3903 (SD 0.3665) | **+0.1168 (worse)** |

**Paired within-seed (every one of 5 seeds, no exception):**

| seed | OOO | MMM | MMM−OOO |
|---|---|---|---|
| 42 | 0.2652 | 0.3939 | +0.1287 |
| 123 | 0.2811 | 0.4152 | +0.1341 |
| 456 | 0.2674 | 0.3871 | +0.1197 |
| 789 | 0.2652 | 0.4038 | +0.1386 |
| 999 | 0.2886 | 0.3515 | +0.0629 |

**MMM is worse than OOO at every single training seed** — a robust, consistent effect, not driven by one outlier seed.

### Per-cell results and regressions (full table: `e1dynmatch_v1/e1dynmatch_per_cell_results.csv`; `e1dynmatch_v1/e1dynmatch_decision_summary.json`)

**5 of 24 cells regress by ≥0.05** (MMM vs. OOO), **all concentrated at the higher-`k` (decoupled-persona) cells**, exactly the region this whole line of work has tracked throughout:

| skill | k | OOO | MMM | Δ |
|---|---|---|---|---|
| 0.80 | 0.30 | 0.091 | 0.513 | **+0.422** |
| 0.80 | 0.45 | 0.164 | 0.964 | **+0.800** |
| 0.80 | 0.60 | 0.164 | **1.000** | **+0.836** (the "lucky_guesser" cell) |
| 0.90 | 0.45 | 0.591 | 0.769 | **+0.178** |
| 0.90 | 0.60 | 0.591 | 1.304 | **+0.713** |

**Not isolated to one cell — the degradation is concentrated but spread across 5 cells, all at `skill∈{0.80,0.90}, k≥0.30`**, i.e. the intervention specifically breaks exactly the region B2's original training already struggled with least (the highest-decoupling scenarios). Every other cell is flat or mildly improved.

### Factorial main effects and interactions (descriptive, exploratory, no significance claims — `e1dynmatch_v1/e1dynmatch_factorial_contrasts.csv`)

At 24,576 steps: **Factor A (step size) has by far the largest, harmful main effect: +0.0676** (matching step size raises pooled MAE by ~0.068 on average, across all 4 arm-pairs sharing that flip). Factor B (horizon): **+0.0214** (also harmful, smaller). Factor C (initial difficulty): **−0.0011** (negligible, essentially neutral — consistent with `OOM` being the single best arm). Interaction terms are all small (`|value| ≤ 0.039`) relative to Factor A's main effect. **Factor A (step size/floor matching) is the dominant, identifiable driver of the harm**, not the horizon or initial-difficulty mismatches.

### Checkpoint trajectory (8,192→16,384→24,576)

`OOO`/`OOM` are flat and stable across all three checkpoints (consistent with E1-Improve V1's already-established plateau). `MMM` **gets steadily worse with more training within the primary budget itself** (0.3735→0.3877→0.3903), the same qualitative pattern as the original (unmatched-dynamics) extended-budget degradation — matching dynamics did not prevent this within-budget degradation trend; if anything it appears earlier.

## 5. Extended-budget decision (Phase 3/5, predeclared trigger applied without modification)

**Trigger NOT met.** Required: `MMM` pooled MAE ≥0.02 lower than `OOO`'s, with no per-cell regression ≥0.05. **Actual: `MMM` is 0.1168 *higher* (worse) than `OOO`, and 5 cells regress by up to 0.836.** **The extended 98,304-step comparison was not run**, exactly per the predeclared rule — there is no basis to test whether matched dynamics prevent long-training degradation when matched dynamics already underperform at the primary budget.

## 6. Verification and tests (Phase 4/6)

- 99/99 tests pass (10 new: observation/action space preservation, exact reproduction of frozen step-size/floor, exact `0.2`/`0.2` matched values, no out-of-bounds observations, Factor B/C kwarg propagation, reward invariance at step 0, legitimate post-divergence trajectory difference, all-8-arms completeness, `OOO`-equals-frozen-constants equivalence).
- Shared log hash: unchanged, verified before and after (`9937d8a8...`).
- Frozen files/checkpoints: unmodified (`git status` clean).
- All reported numbers recomputed directly from `e1dynmatch_eval_raw.json`/`e1dynmatch_eval_summary.json` via `e1dynmatch_analyze.py`, not carried over from memory.
- No turn or grid cell is treated as an independent training-seed replicate; all cross-seed reporting uses the 5 training seeds as the unit of replication, consistent with the project's standing convention.
- No statistical significance is claimed anywhere in this report.

## Scientific conclusion (Phase 6) — exploratory, not confirmatory

1. **Which dynamics, if any, improve tracking MAE?** Only Factor C (initial-difficulty matching) shows a small, essentially neutral-to-marginal effect (`OOM` narrowly beats `OOO`, `0.2702` vs `0.2735`, well within cross-seed noise). **Factors A (step size) and B (horizon) both make things worse when matched**, individually and especially combined.
2. **Does matching all three outperform changing them individually?** **No — it is the worst full combination tested** (only `MOO`, step-size-alone, is comparably bad). Combining all three matches does not compound any benefit; it compounds harm, dominated by Factor A.
3. **Does alignment prevent or reduce the previously observed long-training degradation?** **No.** `MMM` degrades steadily across its own 8,192→24,576 trajectory, the same qualitative pattern as the original mismatched-dynamics extended-budget collapse — matching the dynamics did not fix this, and the predeclared trigger correctly blocked spending compute on the 98,304-step extension to check further, since there is no primary-budget improvement to protect.
4. **Does any PPO variant reliably outperform Heuristic+G (0.2674)?** **No.** Every one of the 8 arms has a positive (worse) gap to Heuristic+G at 24,576 steps; the closest, `OOM` at `+0.0028`, is a near-tie within noise, not a demonstrated win, and no arm here or in any prior E1/E1-Improve iteration has beaten Heuristic+G.
5. **Which configuration should be retained for further development, and why?** **`OOO` (the existing, standard B2 training) — unchanged.** None of the seven alternative dynamics configurations improves on it in any way that survives the per-cell regression check; `OOM`'s marginal pooled edge is not paired with a clean per-cell win large enough to justify adopting a new, less-tested training configuration over the one this whole project's evidence base is already built on.

**PPO does not reliably outperform the deployable Heuristic+G baseline in this iteration, exactly as in every prior E1/E1-Improve round and exactly as already documented in `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` for the original frozen P3 study.** This iteration adds a genuinely new, useful negative result — matching the dynamics is not a fix, and specifically identifies *which* mismatch (step size) is doing the damage — but does not change that conclusion. A useful adaptive-control *framework* (the guardrails, the evaluation harness, the persona-diversity grid) is well-supported by this whole body of work; a demonstrated PPO performance *advantage* over the simple heuristic controller is not.

## Limitations

Exploratory, reused development seeds throughout — not a claim of generalization to confirmatory seeds or real users. Factor A's mechanism for *why* a larger step size hurts specifically at high-`k` cells is not established causally here (a plausible story — larger per-action jumps overshoot the narrow decoupled-state region more easily — is not tested). The extended-budget arm was never run (correctly, per the trigger), so whether matched dynamics behave differently over a much longer horizon remains untested. One `n=1` weight-vs-checkpoint spot-check (§1) does not establish general checkpoint/fresh-run equivalence beyond the one case tested.

## Single most defensible next step

Given Factor A is now identified as the dominant, specific driver (not horizon, not initial difficulty), and given three consecutive iterations (deterministic gates, dynamics matching) have not beaten Heuristic+G, the most defensible next step is to **stop modifying PPO's training/environment configuration and instead treat Heuristic+G as the retained deployable baseline for the paper**, reporting the adaptive-guardrail framework and the persona-diversity evaluation harness as the genuine contributions, with PPO's specific added value over the simplest baseline reported honestly as not established across four independent, well-instrumented attempts (V1 gate, V2 gate extension, this factorial dynamics experiment, plus the original frozen P3 study).

## Deliverables

1. This report.
2. `research/paper_strengthening/results/e1dynmatch_v1/e1dynmatch_per_seed_results.csv`, `e1dynmatch_per_cell_results.csv`.
3. `research/paper_strengthening/results/e1dynmatch_v1/e1dynmatch_factorial_contrasts.csv`.
4. Test results (§6); integrity verification (§3); shared-log hash `9937d8a8e61434ac2aac4218d485b5f903ed3a1609c51b55f951a770f2138852` (unchanged).
5. Scientific conclusion (§ above), explicit about exploratory vs. confirmatory status.
6. Registered protocol commit `8e6cea8`, tag `explore/E1-dynamics-match/v1` (local, not pushed).
