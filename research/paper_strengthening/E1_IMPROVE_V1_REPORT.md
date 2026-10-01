# E1-Improve V1 — Bounded Improvement Iteration: Findings and Results

**Protocol:** `E1_IMPROVE_V1_PROTOCOL.md` (SHA-256 `0fb518e2c838af5bed44b90a46bf4a152c6c4c8edad29d952b692c8b0af7fe4b`), local tag `explore/E1-improve/v1` on commit `00ddcf1` (**not pushed**). Builds on the completed `E1_DEVELOPMENT_RUN_REPORT.md`. Uses `EVAL_SEEDS_DEV = [1001,2002,3003,4004,5005]` only; confirmatory seeds (21021-40040) and the 3 held-out profiles were never touched — verified directly on every new raw-output file (only `SKILL_GRID` values `{0.20,...,0.90}` appear).

## 1. Verified metric definition, and whether a 70/100 target is meaningful

**What is measured.** `target_tracking_error` / `mae_x` (`x3a_lib.simulate()`, `e1_simulate_adapter.simulate_diverse()`, both read directly, unmodified) = mean absolute difference between the controller's **question-difficulty level** (a scalar on `[1,5]` at evaluation) and a **fixed per-scenario target difficulty** (`target = round(10·skill)/2`), averaged over the 11 difficulty values in a trajectory (initial value + 10 steps). **This is a controller/policy-tracking metric — how well the difficulty-adjustment policy converges to and holds the "right" difficulty level for a given simulated candidate's skill. It is not the evaluator's answer-scoring composite** (`services/evaluator/app.py`'s `0.15·S1+0.35·S2_eff+0.50·R`, a completely different subsystem measuring answer quality, not difficulty control) **and not any measure of "correctness" of individual controller decisions** (a related but distinct quantity, "oracle_agreement", is reported separately throughout and never merged into MAE, per the project's own standing rule). Verified directly against `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2 (`Fixed (d=3.0): Tracking MAE = 1.200` — independently reproduced by hand: with targets `{1.0,1.5,3.0,4.0,4.5}` for the five named personas and a fixed difficulty of `3.0`, `mean(|3-1|,|3-1.5|,|3-3|,|3-4|,|3-4.5|) = 1.200` exactly).

**Comparability.** `0.2674` (Heuristic+G), `0.2735` (B2 primary), `0.3942` (B2 extended) are all computed by the identical formula, on the same `[1,5]` difficulty scale, the same target formula, the same shield — **directly comparable in units and definition.** They are **not** a strict apples-to-apples "same test set" comparison to the original frozen P3 numbers (`0.473`, `0.677`, `1.200`), which evaluate 5 fixed named personas rather than E1's 24-cell `(skill,k)` grid — same metric, different scenario distribution, magnitudes are meaningfully comparable but not a literal re-test.

**Is `100·(1-MAE)` a legitimate closeness index? No — not justified by this metric.** MAE is **not bounded to `[0,1]`**: it is a raw difference on a `[1,5]` difficulty scale (range 4), and values above `1.0` are already observed in stored, frozen data — the canonical-truth `Fixed` baseline itself is `1.200`, and this iteration's own extended-budget B0 reaches `1.0964` at one grid cell (`research/paper_strengthening/results/e1_dev_eval_extended/e1_dev_eval_raw.json`). Applying `100·(1-1.200) = -20` or `100·(1-1.0964) = -9.64` produces a negative "score out of 100," which has no coherent interpretation. There is also no principled reason `1` full difficulty-level of error corresponds to "0% closeness" — it is an arbitrary linear anchor, not a probability or percentage-correct. **If a bounded `[0,1]` closeness measure is wanted, the defensible normalization is `MAE / 4` (dividing by the actual difficulty-scale range `[1,5]`)**, which would put Heuristic+G at `1 - 0.2674/4 = 93.3` and the `Fixed` baseline at `1 - 1.200/4 = 70.0` — a different number from the requested formula and not something this report treats as validated either, since it has never been used or interpreted elsewhere in this project. **No 70/100 target is reported as met or unmet using the requested `100·(1-MAE)` transform, because that transform is not a valid interpretation of this metric.** Reported instead: raw MAE throughout, plus the `MAE/4` normalization where a bounded number is useful for intuition, always labeled as such.

**No implementation/aggregation/target-construction bug was found.** `target_tracking_error` and `mae_x` are computed identically in `x3a_lib.simulate()` and (verified by the parity check, `E1_DEVELOPMENT_RUN_REPORT.md` §3, 0 mismatches across 36 combinations) in `e1_simulate_adapter.simulate_diverse()`. The clipping (`difficulty ∈ [1,5]`), target formula, and aggregation (`err.mean()` over 11 points) were each re-read from source and re-derived by hand against the `Fixed=1.200` reference value with an exact match.

## 2. Root-cause findings (facts vs. hypotheses clearly separated)

**Fact, code-verified, newly confirmed by this iteration:** training and evaluation use **different difficulty dynamics**, both frozen, both reused unmodified by E1:
- **Episode horizon:** training (`rl/env/interview_env.py:63`, default `max_steps=15`, unchanged by `AlignedInterviewEnv`/`e1_train_condition_b.py`) vs. evaluation (`x3a_lib.simulate`/`simulate_diverse`, `max_steps=10`). Already documented for the original P3 study in `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.1; confirmed to apply identically to E1.
- **Difficulty step size (new finding, direct code read, `interview_env.py:401-405`):** training moves `self.difficulty` by **±0.1** within `[0.1,1.0]`; evaluation moves `cur` by **±1.0** within `[1,5]`, i.e. **±0.2 once normalized** (`cur/5.0`) — evaluation moves normalized difficulty **2× faster per action** than the policy was trained to expect.
- **Initial difficulty distribution (new finding, `interview_env.py:306`):** training starts at `Uniform(0.3,0.7)`; evaluation always starts at the fixed `0.6` (`cur=3.0/5.0`).

**Fact, established by this iteration's own controlled data:** B2's primary-budget (24,576-step) advantage over B0 is **robust across all 5 training seeds** (`lucky_guesser`-cell MAE identically `0.1636` at every seed) but **not robust to training duration** — it degrades gradually starting around step 40,960 and is fully gone by step ~90,112–98,304 (full checkpoint-interval trace, §3 below). Direct trajectory inspection shows the effect is driven by a single correctly-timed `Harder` proposal at one step that the model produces at short-to-moderate training and stops producing after extended training.

**Fact, established in this session's prior phase (`RL_GUARDRAIL_COVERAGE_DECOMPOSITION_REPORT.md`) and reused as motivation, not re-derived here:** PPO has zero training exposure to the state quadrant `perf≥0.90, conf<0.40, hes>0.60` (guardrail G6's own "nervous" exclusion condition, verified against live `x3a_lib.shield()` source in this iteration's regression tests) because the only training candidate configuration ever used (`persona="normal"`, static-code finding N1, prior session phase) does not naturally produce that perf/conf/hes combination.

**Hypothesis, not established:** that the step-size/horizon mismatch is *the* mechanism behind the extended-budget collapse (plausible, consistent with "more training pushes further toward the training-time-optimal behavior, which is tuned for a different per-step dynamic than evaluation uses," and directly motivated Intervention A) — not proven by a controlled ablation in this iteration, since doing so would require retraining with a modified environment, which is outside this iteration's explicit "do not change reward/state/action definitions" boundary.

**Heuristic deployability, verified:** `x3a_lib.make_policy("heuristic")` (`if perf>hi and current<5: Harder; if perf<lo and current>1: Easier; else Same`) reads only `perf` (candidate's own current-turn score) and `current` (the controller's own tracked difficulty) — both already inside the same 6-D observation PPO receives. **No oracle information, no hidden state, no leakage.** It is a legitimate, deployable baseline, not dismissed on that basis, per instruction.

## 3. Implemented improvements

### Intervention A — B2 checkpoint-interval trace (new training, exploratory; `e1improve_train_b2_checkpointed.py`)

5 training seeds, periodic checkpoints every 8,192 steps to 98,304 (12 snapshots/seed, 60 total), same hyperparameters/environment/candidate construction as E1 (`e1_train_condition_b.py` reused unmodified for the environment class). W&B used (project `prepaired-e1improve`, 5 runs, IDs recorded in `training_summary.json`; `wandb.init()` called before any callback, per instruction). **0 training failures**, 405–440s/seed.

**Full per-checkpoint dev-eval trace** (`e1improve_eval_checkpoint_trace.py`, pooled across the same 24-cell grid × 5 dev eval seeds, averaged over the 5 training seeds):

| step | pooled MAE | lucky_guesser-cell MAE |
|---|---|---|
| 8,192 | 0.2776 ± 0.0143 | 0.1891 ± 0.0509 |
| 16,384 | **0.2697 ± 0.0034** | 0.1636 ± 0.0000 |
| 24,576 (E1's original primary) | 0.2735 ± 0.0094 | 0.1636 ± 0.0000 |
| 32,768 | 0.2785 ± 0.0111 | 0.2945 ± 0.2618 |
| 40,960 | 0.3036 ± 0.0224 | 0.3345 ± 0.3328 |
| 49,152 | 0.3376 ± 0.0268 | 0.4691 ± 0.3641 |
| 57,344 | 0.3820 ± 0.0290 | 0.7636 ± 0.3232 |
| 65,536 | 0.4115 ± 0.0244 | 0.9273 ± 0.1455 |
| 73,728 | 0.4150 ± 0.0171 | 0.9273 ± 0.1455 |
| 81,920 | 0.4033 ± 0.0166 | 0.9636 ± 0.0727 |
| 90,112 | 0.3962 ± 0.0243 | **1.0000 ± 0.0000** |
| 98,304 (E1's original extended) | 0.3994 ± 0.0301 | 1.0000 ± 0.0000 |

**Finding: this is not a narrow spike.** The good behavior forms a genuine, stable **plateau across 4 consecutive checkpoints (8,192–32,768)**, then **degrades gradually and monotonically** from 40,960 onward, essentially fully collapsed by 90,112. E1's original 24,576-step choice sits inside this real plateau, not on a lucky isolated point. `16,384` has the **lowest cross-seed variance of any checkpoint** (pooled SD `0.0034` vs. `24,576`'s `0.0094`) and identical, perfectly-consistent `lucky_guesser`-cell performance (`0.1636 ± 0.0000`, all 5 seeds).

**Per-cell regression check, `16,384` vs. `24,576`:** pooled improvement is small and mostly a variance reduction, **not a strict dominance** — one cell (`skill=0.65, k=0.0`) regresses by `+0.0509`, just over the same `0.05` threshold used throughout this study; all other cells are flat or improved. **Reported honestly, not smoothed over: `16,384` is a defensible, better-characterized stopping point given its much tighter cross-seed variance and the newly-established plateau shape, but it is not an unambiguous per-cell improvement over `24,576`.**

### Intervention B — deterministic PPO+Heuristic gated hybrid (no training; `e1improve_hybrid_gate.py`, `e1improve_eval_hybrid.py`)

Gate: when the pre-shield state satisfies `perf≥0.90 and conf<0.40 and hes>0.60` (reused verbatim from `x3a_lib.shield()`'s own G6 "nervous" clause — not a new threshold), use the Heuristic's raw proposal instead of the wrapped policy's; otherwise unchanged. The same, unmodified `x3a_lib.shield()` is still applied afterward, exactly as for every other condition in this study. 9 new regression tests (`test_e1improve_hybrid_gate.py`) verify the exact boundary logic and cross-check the reused thresholds against a live read of `x3a_lib.shield()`'s source — **all 9 pass** (one test-authoring bug of my own, a wrong expected value at an exact-equality boundary case, was caught and fixed before reporting).

| Condition | pooled MAE (ungated) | pooled MAE (gated) | Δ | max per-cell regression |
|---|---|---|---|---|
| Condition A (existing, frozen, deployed checkpoint) | 0.4571 | **0.4192** | −0.0379 | 0 cells ≥0.05 |
| B0 primary | 0.4389 | **0.4011** | −0.0379 | 0 cells ≥0.05 |
| B2 primary | 0.2735 | 0.2735 | 0.0000 (no-op) | — |

**Mechanistically clear, not just observed:** the gain is concentrated at `skill=0.90` cells (`k=0.45`: −0.20; `k=0.60`: −0.71), where the candidate's actual performance at the evaluation-time initial difficulty (`0.6`) genuinely crosses the reused `0.90` threshold. **Honest limitation, checked directly:** at the `(skill=0.80,k=0.60)` "lucky_guesser proxy" cell specifically, the candidate's actual performance at difficulty `0.6` is only `~0.76–0.87` (directly computed via `DiverseCandidate.answer_question(0.6)` for all 5 dev eval seeds) — **below** the `0.90` gate threshold, so the gate does **not** fire there and does not fix that specific cell for Condition A or B0. The gate is a genuine, zero-cost, zero-regression improvement to the specific high-skill/high-decoupling region it actually covers, not a fix for the `lucky_guesser` cell narrative used to motivate it.

## 4. Verification that the improvements are real

- **Tests:** original E1 suite still 52/52 passing (unaffected by new, additive files); 9/9 new hybrid-gate regression tests passing after fixing one authoring bug of my own.
- **Recomputation:** every MAE figure above is recomputed directly from saved checkpoints/raw JSON by the scripts cited, not carried over from memory or estimated.
- **Per-profile/per-cell regressions:** checked explicitly for both interventions (§3); Intervention B has zero ≥0.05 regressions for the two conditions it changes; Intervention A's `16,384` candidate has exactly one, disclosed above.
- **Seed dependence:** both interventions' key numbers are reported per-seed, not only pooled (checkpoint trace: per-seed SD shown at every step; hybrid gate: identical regression outcome for all 5 seeds of Condition A/B0, confirmed via the `per_seed_by_condition` field in `e1improve_hybrid_summary.json`).
- **Exploratory, not confirmatory:** both interventions ran once, on already-used development seeds, with decision criteria fixed in the protocol before execution; nothing was retried or threshold-adjusted after seeing results. This is exploratory, reused-development-seed evidence, explicitly not a claim of generalization to the locked confirmatory seeds or to real users.

**70/100 target:** not evaluated as requested — the transform is not valid for this metric (§1). **Reported instead in the metric's own units throughout.**

**Does the learned controller reliably beat the strongest valid deployable baseline (Heuristic+G, MAE `0.2674`)?** **No, not established by this iteration.** Every PPO-based condition tested — B2 primary (`0.2735`), B2 at the best-characterized stopping point `16,384` (`0.2697`), the gated hybrids (`0.4011`–`0.4192`, still far from Heuristic's level) — remains at or slightly above Heuristic+G's pooled MAE; the closest (`16,384`, gap `0.0023`) is within the checkpoint's own cross-seed SD (`0.0034`) and therefore not a reliable win. **This is consistent with, not contrary to, the project's own existing frozen finding** (`CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2, P0-2: "the heuristic (0.473) is better than every PPO variant... PPO's contribution under guardrails is not identified by the frozen study") — extended here to the harder, persona-diverse setting, with the same qualitative outcome.

## 5. Paper implications

- **Can be reported:** the metric definition and its exact units/formula (§1); the train/eval dynamics-mismatch facts (§2, code-verified, citable); the checkpoint-interval plateau-then-collapse trace (§3A) as a genuine, if exploratory, training-stability characterization; the gated hybrid's concentrated, zero-regression improvement to two existing/no-retraining-needed checkpoints (§3B), with its honest scope limitation stated alongside it.
- **Must be narrowed:** any claim that PPO (in any variant tested here, gated or not) beats the heuristic baseline — it does not, on this evidence, and the manuscript should state this plainly rather than omit the comparison, exactly as the existing canonical-truth document already does for the original P3 study. Any claim that `24,576` steps was specifically "tuned" or "selected" for its result — it was not tuned; it happens to sit inside a real, now-characterized plateau, which is a more defensible, different claim.
- **Remains unproven:** that the step-size/horizon train/eval mismatch is *the* causal mechanism for the extended-budget collapse (plausible, not tested by ablation); that a `100·(1-MAE)` or `MAE/4` closeness framing has any established meaning for a reader outside this project (neither has been used or validated elsewhere in the paper family); any claim about real candidates, real interviews, or human learning (simulation-only throughout, as always).

## 6. Targets met?

| Target | Result |
|---|---|
| 70/100 closeness index at both budgets | **Not evaluated — the requested `100·(1-MAE)` transform is not a valid interpretation of this metric (§1).** |
| Learned controller reliably beats the strongest deployable baseline (Heuristic+G) | **No.** Closest approach (B2 @ 16,384 steps, MAE 0.2697) is within noise of Heuristic+G's 0.2674, not a reliable win. |
| A real, verified, bounded improvement was found and implemented | **Yes**, twice: (1) the gated hybrid genuinely improves Condition A and B0 (−0.038 pooled MAE, zero regressions, no retraining) within its actual coverage region; (2) the checkpoint trace establishes `16,384` steps as a better-characterized, lower-variance stopping point than either training-duration extreme, with one disclosed near-threshold per-cell tradeoff. |

## 7. Limitations and single most defensible next step

**Limitations:** the gated hybrid's fix is narrower than its original motivating story (it covers `skill=0.90`, not the `(0.80,0.60)` "lucky_guesser" cell specifically — corrected and disclosed in §3B, not hidden); the checkpoint-trace plateau is characterized on development seeds only and has not been checked for a matching plateau shape at other grid cells individually (only pooled + the one named cell); the env-dynamics-mismatch hypothesis for the extended-budget collapse is plausible but untested by ablation; W&B logging covers Intervention A's training only (not Intervention B, which involves no training).

**Single most defensible next step:** widen the gated hybrid's coverage using the SAME already-validated approach — reuse `x3a_lib.shield()`'s other existing threshold clauses (e.g. G2's `conf<0.30 and hes>0.70 and perf<0.80`) as additional, already-precedented gate conditions, rather than inventing or tuning new numeric thresholds — and re-evaluate on the same development seeds with the same zero-regression bar, before considering any confirmatory run.

## Reproduction

```bash
cd /c/Users/spars/Downloads/PrepAIred
EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest research/paper_strengthening/scripts/tests/test_e1_diverse_persona.py research/paper_strengthening/scripts/tests/test_e1improve_hybrid_gate.py -v
.venv/Scripts/python.exe research/paper_strengthening/scripts/e1improve_train_b2_checkpointed.py   # ~35-40 min, 5 seeds, writes to results/e1improve_checkpoint_trace/, logs to W&B project prepaired-e1improve
.venv/Scripts/python.exe research/paper_strengthening/scripts/e1improve_eval_checkpoint_trace.py    # ~1-2 min
.venv/Scripts/python.exe research/paper_strengthening/scripts/e1improve_eval_hybrid.py              # ~1 min, no training
```

**Files:** protocol `research/paper_strengthening/E1_IMPROVE_V1_PROTOCOL.md`; scripts `research/paper_strengthening/scripts/e1improve_train_b2_checkpointed.py`, `e1improve_hybrid_gate.py`, `e1improve_eval_hybrid.py`, `e1improve_eval_checkpoint_trace.py`; tests `research/paper_strengthening/scripts/tests/test_e1improve_hybrid_gate.py`; registration `research/preregistration/E1/E1_IMPROVE_V1_manifest.json`, tag `explore/E1-improve/v1` on commit `00ddcf1` (local, not pushed); results `research/paper_strengthening/results/e1improve_checkpoint_trace/`, `e1improve_hybrid_eval/` (all new, uncommitted — original E1 results at `e1_training*/`, `e1_dev_eval*/` untouched). A local, untracked `wandb/` directory was created at the repo root by this run (5 sync'd runs, not gitignored by any existing pattern) — left as-is, not committed, flagged for awareness rather than unilaterally adding a `.gitignore` entry.
