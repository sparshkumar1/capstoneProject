# E1 — Development-Phase Run Report

**Run ID:** `E1-dev-2026-09-28-001`. **Protocol:** `research/preregistration/E1/PROTOCOL.md` (SHA-256 `22ee4b744f4d3d4212b8c02d0ed551c0cc9da0186b41e67a0185245577ef0d6b`), tag `prereg/E1-ppo-persona-diversity/v4` on commit `461e06b` (**local tag, not pushed**). Run manifest: `research/paper_strengthening/results/e1_training/run_manifest.json`, `status: completed`. **This is a development-phase report. No confirmatory evaluation (`EVAL_SEEDS_CONFIRMATORY` 21021–40040, or the three held-out profiles) was run or inspected — verified below.**

## 1. Pre-run integrity (step 1)

- `E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V4.md` SHA-256 recomputed and matched exactly against the hash quoted in the approval message: `22ee4b744f4d3d4212b8c02d0ed551c0cc9da0186b41e67a0185245577ef0d6b`. No discrepancy.
- All 5 implementation-file hashes recomputed and matched exactly against `E1_IMPLEMENTATION_REPORT.md`'s own table (`e1_config.json`, `e1_diverse_persona_env.py`, `e1_simulate_adapter.py`, `e1_train_condition_b.py`, `test_e1_diverse_persona.py`). No discrepancy.
- Frozen directories (`rl/checkpoints`, `rl/env/interview_env.py`, `rl/training/simulated_candidate.py`, `rl/guardrails.py`, `research/experiments/paper3/checkpoints`, `research/experiments/paper3/frozen_config.yaml`, `research/confirmatory/`, `research/scripts/execute_paper3_study.py`) confirmed unmodified via `git status --porcelain` (empty) before and after every step below.

## 2. Registration and freeze (step 2)

- `research/preregistration/E1/PROTOCOL.md` created as a byte-identical copy of the frozen V4 file (`diff` confirmed identical, same SHA-256).
- `research/preregistration/E1/protocol_manifest.json` created, hashing the protocol, all 5 implementation files, and every frozen dependency (`execute_paper3_study.py`, `x3a_lib.py`, `interview_env.py`, `simulated_candidate.py`, `guardrails.py`, `frozen_config.yaml`, and all 10 checkpoint files for training seeds 42/123/456/789/999). **All 10 checkpoint hashes verified byte-identical to X3-A's own registered `protocol_manifest.json`** — zero drift since that study froze them.
- Commit `461e06b` created containing **only** the 12 E1-specific files (4 protocol versions, implementation report, 5 implementation files, 2 new preregistration files) — verified via `git status --porcelain` immediately before commit that no other untracked file (D1 protocols, `SYSTEM_IMPROVEMENT_PLAN.md`, Item D/PPO-audit files, `.serena/`) was staged.
- Annotated tag `prereg/E1-ppo-persona-diversity/v4` created on commit `461e06b`, message containing both the protocol and manifest SHA-256. **Not pushed** — branch remains 1 commit ahead of `origin/workspace/human-eval-clean-push`, exactly as before this run except for this one local commit.

## 3. Runtime PPO adapter parity check (step 3)

New script `research/paper_strengthening/scripts/e1_ppo_parity_check.py`. Loaded the existing, frozen `research/experiments/paper3/checkpoints/seed_42/` checkpoint via `x3a_lib.load_ppo()` (unmodified), built `x3a_lib.PPOPolicy` (unmodified), and ran **36 combinations** (5 frozen personas × 3 eval seeds × shield on/off, plus a `k=0` `DiverseCandidate`-wrapper check for the `normal` persona) comparing `x3a_lib.simulate()` directly against `e1_simulate_adapter.simulate_diverse()` on the identical PPO policy object.

**Result: 0 mismatches across all 36 combinations, on every field including the raw observation arrays.** This is the parity check `E1_IMPLEMENTATION_REPORT.md` explicitly deferred ("would require loading a checkpoint"); it is now confirmed with a real loaded policy, not only the deterministic stand-in policies used in the unit-test suite. The checkpoint was loaded read-only; `git status` on `rl/checkpoints`, `research/experiments/paper3/checkpoints`, and the isolated dummy env-log path (deleted after use) confirmed no side effects. Full output: `research/paper_strengthening/results/e1_parity/e1_ppo_parity_check.json`.

## 4. Development training (step 4)

10 runs (`B0`/`B2` × seeds `[42,123,456,789,999]`) at the primary budget (`TIMESTEPS_PRIMARY=24576`), using `e1_train_condition_b.train_condition_b_seed()` unmodified, reading all hyperparameters from `e1_config.json`. **0 failures.** Total training time: 831.2s (~13.9 min). Per-seed times 69.7–91.2s, closely matching Condition A's own historical ~84s/seed.

**Pre-declared extended-budget rule** (fixed in the run manifest *before* this training started, quoted in full there): pool each arm's 5-seed `mean_reward_rolling` curves; if the final-quartile rise exceeds 10% of the full-curve rise for either arm, run the 98,304-step extended-budget diagnostic for **both** arms together.

Applied mechanically (`e1_check_convergence.py`, full output in `research/paper_strengthening/results/e1_training/e1_convergence_check.json`):

| Arm | full-curve rise | final-quartile rise | ratio | still rising? |
|---|---|---|---|---|
| B0 | 0.1508 | 0.0087 | 5.77% | No |
| B2 | 0.1019 | 0.0118 | 11.62% | **Yes** |

**B2's ratio exceeds 10% → the rule triggers.** Per protocol V4 §1.2 ("the extended budget is never used for one arm alone"), the 98,304-step diagnostic was run for **both** B0 and B2, all 5 seeds each (10 more runs, separate output root `e1_training_extended/` so the primary checkpoints/curves are untouched; the 10 primary per-step env logs were backed up to `e1_training_logs/primary_budget/` first since that log path is not parametrized by output root — disclosed in the run manifest's `deviations`). **0 failures.** Total: 4271.6s (~71.2 min). The MAE decision below is **not** selected using this extended-budget data (no arm/checkpoint is ever selected by its own confirmatory-or-diagnostic MAE, per §4.3) — it is reported as the stability diagnostic it is, and it turns out to be the single most important finding of this run (§6).

## 5. Development evaluation (step 5)

Both the primary-budget and the extended-budget checkpoints were evaluated on `development_eval_seeds = [1001,2002,3003,4004,5005]` only, on the identical 24-cell `(skill,k)` grid used to train B2 (`ARM_GRIDS["B2"]`), for 5 conditions: B0, B2, Condition A (existing frozen PPO+G, same 5 seeds), Constant-Same+G, Heuristic+G. Shield on (`+G`) throughout, `x3a_lib.shield()` unmodified, `target = round(10·skill)/2.0`. **`EVAL_SEEDS_CONFIRMATORY` and the 3 held-out profiles were never touched** — verified by direct inspection of the raw output: only the 6 registered `SKILL_GRID` values (`{0.20,0.35,0.50,0.65,0.80,0.90}`) appear anywhere in either evaluation's raw JSON.

### 5a. Primary-budget checkpoints (the governing dataset for the development gate)

Pooled MAE (24 cells × 5 seeds × 5 eval seeds = 600 rows for seed-dependent conditions; 120 for the two baselines):

| Condition | MAE mean | MAE SD | n |
|---|---|---|---|
| B0 | 0.4389 | 0.3945 | 600 |
| **B2** | **0.2735** | 0.2269 | 600 |
| Condition A | 0.4571 | 0.3980 | 600 |
| Constant-Same+G | 0.4621 | 0.4026 | 120 |
| Heuristic+G | 0.2674 | 0.2165 | 120 |

**Training-seed variability** (across-seed SD of each arm's own pooled MAE): B0 = 0.0159, B2 = 0.0096, Condition A = 0.0101 — all small; the B2-vs-B0 gap holds at **every one of the 5 individual seeds** (B2 range 0.265–0.289; B0 range 0.422–0.461 — no overlap).

**Per-cell regression check (B2 vs B0, all 24 cells):** mean `B2 − B0` = **−0.165** (B2 better); **0 of 24 cells regress by ≥0.05 MAE units.** Largest B2-worse-than-B0 gap across any cell: +0.022 (skill=0.65,k=0.0), far below the 0.05 threshold.

**`lucky_guesser` mechanism-check cell (skill=0.80, k=0.60 — the grid cell independently verified in protocol V3 §1.2 to reach the guardrail-G6-exclusion state ~94–95% of the time, target=4.0 matching `PERSONA_TARGETS`):**

| Condition | MAE | oracle_agreement |
|---|---|---|
| B0 | 1.0000 | 0.980 |
| **B2** | **0.1636** | 0.828 |
| Condition A | 1.0000 | 0.980 |
| Constant-Same+G | 1.0000 | 0.980 |
| Heuristic+G | 0.1636 | 0.820 |

At the primary budget, B2 escapes the same stuck-at-3.0 trajectory that B0/Condition A/Constant-Same+G all share exactly, and lands on the identical trajectory Heuristic+G finds. Direct trajectory inspection (seed 42, eval seed 1001) shows why: B0/ConditionA/ConstantSame all propose `Same` for all 10 steps; **B2 proposes exactly one `Harder` at step 3, identical to Heuristic's one `Harder` at step 3** — that single correctly-timed action, which gets through the shield, is the entire mechanism behind the MAE gap at this cell.

**Excluding this one cell**, B2 still beats B0 broadly across the other 23 cells (0.2783 vs 0.4145 pooled) — the aggregate advantage is not solely a one-cell artifact.

**Development-stage gate (protocol V4 §4.3), applied to this primary-budget data exactly as registered:** "proceed to confirmatory evaluation only if B2 shows a directional mechanism-check improvement over B0 on the development seeds, with no per-persona regression ≥0.05 MAE units relative to B0." **Both conditions are met on the primary-budget data.** See §6 for why this mechanical pass is not, by itself, a recommendation to proceed.

**Complexity-vs-heuristic check (§4.3, reported regardless of the above):** Heuristic+G's pooled MAE (0.2674) is **marginally better than B2's** (0.2735) — B2 does not beat the simplest baseline overall, even though it substantially beats both B0 and Condition A. Reported plainly, per protocol: a real, retained improvement over B0/Condition A and "PPO still doesn't justify its complexity over Heuristic+G" are both true at once.

### 5b. Extended-budget checkpoints (diagnostic only — not used for the gate decision)

| Condition | MAE mean | n |
|---|---|---|
| B0 | 0.4095 | 600 |
| B2 | 0.3942 | 600 |
| Condition A | 0.4571 | 600 |
| Constant-Same+G | 0.4621 | 120 |
| Heuristic+G | 0.2674 | 120 |

The B2-vs-B0 pooled gap **shrinks from 0.165 (primary) to 0.015 (extended)** — a 90% reduction. Excluding the `lucky_guesser` cell, the gap shrinks from 0.136 to 0.016 — this is **not** a one-cell effect; it is a broad collapse of the B2 advantage. At the `lucky_guesser` cell specifically, **B2's MAE returns to exactly 1.0000, identical to B0/Condition A/Constant-Same+G** — the single decisive `Harder` action at step 3 is gone at every one of the 5 extended-budget seeds (direct trajectory check confirms all 10 actions are `Same`, matching B0 exactly). Guardrail-coverage/oracle-agreement/action-distribution/volatility statistics for B0 and B2 also converge toward each other at the extended budget (§ full numbers in `e1_dev_eval_extended/e1_dev_eval_summary.json`).

## 6. Decision (step 6)

**Mechanically, the pre-registered development-stage gate passes on the primary-budget data**: B2 shows a directional mechanism-check improvement over B0, with zero per-cell regressions ≥0.05. Read in isolation, this would permit progressing to confirmatory evaluation.

**This mechanical pass is not treated as sufficient evidence, and confirmatory evaluation is not recommended on this evidence as it stands**, for a reason the pre-registered extended-budget diagnostic itself surfaced: the entire decisive `lucky_guesser`-cell advantage, and roughly 90% of the broader 24-cell pooled advantage, **depend on a single correctly-timed `Harder` action that the primary-budget (24,576-step) checkpoint happens to produce and that the identically-configured 98,304-step checkpoint does not**. This is exactly the training-instability failure mode the extended-budget diagnostic exists to catch (protocol V1 §5: "to check whether a null primary result is budget-limited... never used to decide retain/abandon on its own") — here it is not a null result being budget-limited, but a **positive** result that is itself budget-*fragile*: the same architecture, same reward, same seeds, same grid, trained 4× longer, loses the effect entirely. Nothing in the registered decision rules requires treating a budget-fragile primary result as disqualifying, and this report does not silently change the registered threshold — but the honest answer to the user's question ("whether additional development work is justified, and whether the intervention merits progression to the locked evaluation") is:

- **B0 and B2 do provide development-stage evidence of a difference** — B2 tracks the decoupled-persona grid substantially better than B0 or the existing Condition A checkpoints at the registered primary training budget, consistently across all 5 training seeds.
- **Additional development work is justified before spending any locked confirmatory seed on this specific checkpoint behavior.** The primary candidate for that work is understanding *why* the advantage is budget-fragile (e.g., does it depend on an early-training exploration artifact that later training optimizes away toward the guardrail-imitating "Same" default?) — not proposed here as a new experiment, since that would require a registered protocol of its own.
- **The intervention does not yet merit progression to the locked confirmatory evaluation.** Running the confirmatory 20-seed block now would risk spending an irreplaceable, non-reusable resource (per §A.5 of `PREREGISTRATION_SPEC.md`, confirmatory data cannot be re-examined and re-used after the fact) on a checkpoint behavior already shown, within this same development run, not to be robust to a routine training-duration perturbation.
- Separately and regardless of the above: **Heuristic+G still wins on pooled MAE over B2** at the primary budget, so even a robust version of this result would not by itself justify PPO's added complexity — reported per §4.3, not allowed to be obscured by the B2-vs-B0/Condition-A finding or vice versa.

No research conclusion (existing or new) was altered to favor either arm; every historical checkpoint and result is untouched (§1, §2).

## 7. Stopping conditions (step 7)

No confirmatory evaluation was run. No D1 was run. No reward, state, or action redesign was started. No retraining beyond the two registered budget runs (primary + the one pre-declared extended-budget diagnostic, applied to both arms together) was performed. The registration tag was not pushed. This report is the complete, reproducible development-evaluation output; **explicit, separate approval is required before any confirmatory evaluation is run**, and — given §6 — that approval is not recommended on the current evidence without first understanding the extended-budget instability.

## Artifacts

- `research/preregistration/E1/PROTOCOL.md`, `protocol_manifest.json` (committed, tagged)
- `research/paper_strengthening/scripts/e1_ppo_parity_check.py`, `e1_run_training.py`, `e1_check_convergence.py`, `e1_run_training_extended.py`, `e1_dev_eval.py` (new, uncommitted runner/analysis scripts — not part of the frozen E1 registration since they contain no design decisions, only mechanical invocation of the registered, already-hashed `e1_train_condition_b.py`/`e1_simulate_adapter.py` functions)
- `research/paper_strengthening/results/e1_training/` (primary checkpoints, curves, run manifest), `e1_training_extended/` (diagnostic checkpoints/curves), `e1_training_logs/` + `e1_training_logs/primary_budget/` (per-step logs, both budgets preserved), `e1_dev_eval/`, `e1_dev_eval_extended/` (evaluation raw data + summaries), `e1_parity/` (parity check output)
