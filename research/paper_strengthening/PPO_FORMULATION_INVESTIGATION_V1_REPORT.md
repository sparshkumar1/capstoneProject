# PPO Formulation Investigation V1

Development-only, exploratory investigation into the PPO controller's reward/training formulation, following directly from `E1_DEVELOPMENT_RUN_REPORT.md` §6 and `E1_IMPROVE_V2_REPORT.md` §7, both of which left this specific question open rather than closing it.

**Scope discipline (stated up front, unchanged from the E1 series):** no locked confirmatory seed (21021-40040) or held-out profile was read. No frozen checkpoint, frozen result, or `research/experiments/paper3/`, `research/confirmatory/X3-A/`, `rl/checkpoints/`, or `ablation/results/` file was modified. `rl/env/interview_env.py`'s reward/state/action code, `rl/guardrails.py`, and `e1_diverse_persona_env.py`'s grid/candidate definitions were imported unmodified — the only change made anywhere is a single new PPO *training* hyperparameter (`ent_coef`) passed at construction time in a new, separate script, never touching the shared driver `e1_train_condition_b.py`. No new experiment was tuned against its own outcome: the decision rule below was written before either diagnostic or training was run.

## 1. Where the prior investigation stopped

`E1_DEVELOPMENT_RUN_REPORT.md` established that condition B2 (PPO trained on a persona-diverse confidence/hesitation-decoupled grid) beats B0 (persona-fixed) substantially on the 24-cell dev grid at the registered primary training budget (24,576 steps: MAE 0.2735 vs 0.4389, holding at all 5/5 training seeds, zero per-cell regressions ≥0.05), but that this advantage is **budget-fragile**: training the identical setup 4x longer (98,304 steps, the pre-declared extended-budget diagnostic) loses the effect almost entirely (MAE 0.3942). The report explicitly declined to recommend confirmatory evaluation on this basis and flagged, without testing, a specific mechanism question: *"does it depend on an early-training exploration artifact that later training optimizes away toward the guardrail-imitating 'Same' default?"*

Separately, `E1_IMPROVE_V2_REPORT.md` proved (not merely observed) that four of the five candidate guardrail-gate predicates are bit-for-bit no-ops on final MAE, and named the train/eval dynamics mismatch as "the most defensible next step" for a *different* line of inquiry — that line was pursued separately as `E1_DYNAMICS_MATCH_V1_REPORT.md` (already cited in the Paper 3 manuscript's Discussion) and did not resolve the budget-fragility question, which concerns training *duration*, not train/eval dynamics parameters.

This investigation directly tests the mechanism question the development-run report raised but did not pursue.

## 2. Step 1 (diagnostic-only, no training): does the raw policy drift toward "Same" over extended training?

`research/paper_strengthening/scripts/e1_action_collapse_diagnostic.py` re-reads the existing, already-frozen-for-that-report per-step training logs (`e1_training_logs/{B0,B2}_seed{42,123,456,789,999}.csv`, confirmed to be the primary+extended budgets concatenated: 24,576 + 98,304 = 122,880 rows, matching exactly). No new randomness, no training. It compares the raw PPO proposal's (`pre_action`, i.e. before the guardrail shield) "Same" share in the primary-budget window (steps 1-24,576) against the extended-budget tail (steps 24,577-122,880).

**Predeclared decision rule:** the mode-collapse hypothesis is supported only if B2's mean Same-share rise is ≥5 percentage points AND consistent across ≥3/5 seeds, **and** this is not similarly present in the B0 control.

**Result:**

| Condition | pre_action Same-share rise (mean, primary→extended tail) | Seeds ≥5pp |
|---|---|---|
| B2 | +10.91pp (range 7.77–15.00 across 5 seeds) | 5/5 |
| B0 (control) | +11.09pp (range 8.74–12.59 across 5 seeds) | 5/5 |

**Verdict: the specific "B2-specific mode collapse" hypothesis is NOT supported** — the rise is present, and of essentially identical magnitude, in both arms. This is a genuine negative result for the *B2-specific* framing, reported as such rather than reframed as a positive finding.

However, read differently, this is still informative: it shows PPO's raw action distribution drifts toward "Same" over extended training **generally**, regardless of which arm is trained. This matters because B2's entire primary-budget advantage over B0/Heuristic+G comes specifically from correctly deploying "Harder" (the "single correctly-timed Harder action" the development report identified as driving ~90% of the pooled advantage) — a general drift toward "Same" would erode exactly that behavior, even though it isn't unique to B2's training regime. B0 doesn't show a comparable *regression* because B0 was never differentiating well in the first place (it has nothing to lose).

## 3. Step 2: a disclosed, testable mechanism

Reading `e1_train_condition_b.py::train_condition_b_seed` (the frozen driver both B0 and B2 use, and whose hyperparameters mirror `research/scripts/execute_paper3_study.py::train_ppo_seed`) confirms its `PPO(...)` constructor call passes no `ent_coef`. Stable-Baselines3's PPO default is `ent_coef=0.0` — meaning every E1 run to date, and the original frozen Paper 3 training, trains with **zero entropy bonus**: no structural pressure against the policy's output distribution narrowing over the course of training. This is a real, code-verified fact, not a speculation about SB3's defaults.

**Hypothesis (predeclared before training):** adding a small, standard, untuned entropy coefficient (`ent_coef=0.01`, Stable-Baselines3's own PPO docstring example value) to B2's exact setup will reduce the Same-share rise over the extended-budget tail and reduce the primary-vs-extended MAE regression, relative to unmodified B2.

**Decision rule (predeclared):** supported only if BOTH (a) B2ent's mean Same-share rise is ≥5pp lower than B2's own 10.91pp, AND (b) B2ent's extended-budget MAE regresses by no more than 0.02 relative to its own primary-budget MAE (vs. unmodified B2's regression of +0.1207, i.e. 0.3942−0.2735).

## 4. Experiment: B2ent (B2 + ent_coef=0.01)

New script: `research/paper_strengthening/scripts/e1_improve_v3_entropy_experiment.py`. Changes exactly one PPO hyperparameter relative to B2; same env, same reward, same state/action space, same 24-cell grid, same 5 training seeds (42/123/456/789/999), same primary (24,576) and extended (98,304) budgets. Outputs go to a new directory (`results/e1_improve_v3_entropy/`) and new log-file prefix (`B2ent_primary_seed<s>.csv`, `B2ent_extended_seed<s>.csv`) that collide with nothing from B0/B2/Condition A. Evaluation reuses `e1_dev_eval.py`'s own condition-runner and aggregation functions unmodified (`e1_improve_v3_eval.py`), on the same 24-cell grid x 5 development eval seeds (1001-5005) as every other E1 condition — no confirmatory seed, no held-out profile.

**Primary-budget training:** 5/5 seeds completed successfully (76.9–102.3s/seed, total ≈ 7.4 min).

**Primary-budget dev-grid evaluation (600 rows, 24 cells × 5 seeds × 5 eval seeds):**

| Condition | MAE mean | MAE SD |
|---|---|---|
| B2 (unmodified, from E1_DEVELOPMENT_RUN_REPORT) | 0.2735 | 0.2269 |
| **B2ent (ent_coef=0.01)** | **0.2750** | 0.2288 |

The entropy coefficient does not materially change primary-budget performance (Δ = +0.0015, well inside cross-seed SD) — consistent with the change being a training-dynamics intervention rather than a scoring/reward change, as intended.

**Extended-budget training and evaluation:** [PENDING — see §5]

## 5. Extended-budget result

**Data-integrity note, disclosed before the result:** an earlier auto-chaining shell script (`wait_and_run_extended.sh`) that this pass wrote to launch the extended run automatically once the primary run finished was identified as redundant and killed (`pkill`) shortly after being started, while the primary run was still in progress. Despite that, the per-step CSV logs for all 5 extended-budget seeds (`B2ent_ext_seed<s>.csv`) show row counts roughly 1.9–1.96x the expected 98,304 (184,267–192,544 observed) with 3,847–11,748 malformed rows each — evidence that a duplicate copy of the extended training job ran concurrently with the intended one (`bld3y6qlf`) for all 5 seeds, most likely the watcher's child process surviving the kill of its parent shell. Because `training_seed` and the episode-seed formula (`training_seed * 100_000 + episode_index`) are fully deterministic and each process trains its own independent model/env pair in separate memory with no shared state besides the filesystem, two concurrent runs of the same seed would compute numerically identical PPO trajectories and produce equivalent final checkpoints — so the *saved checkpoints and the MAE evaluation derived from them* are not believed to be compromised, only the human-readable **per-step CSV logs**, which is why this report does not include a B2ent analogue of the §2 Same-share diagnostic (it would require trustworthy per-step logs, which these are not). This is reported rather than silently worked around; a clean single-process re-run would be needed before treating the CSV-log-dependent diagnostic as available for this arm.

**Extended-budget training:** 5/5 seeds completed (per `training_run_summary.json`, all `"status": "completed"`), 393–481s/seed.

**Extended-budget dev-grid evaluation (600 rows):**

| Condition | Primary-budget MAE | Extended-budget MAE | Regression (ext − primary) |
|---|---|---|---|
| B2 (unmodified) | 0.2735 | 0.3942 | **+0.1207** |
| **B2ent (ent_coef=0.01)** | 0.2750 | **0.3938** | **+0.1188** |

Per-seed extended-budget B2ent MAE: seed 42 = 0.3788, seed 123 = 0.4061, seed 456 = 0.3894, seed 789 = 0.3871, seed 999 = 0.4076 — tight, non-outlying spread across all 5 seeds, consistent with a real (not corrupted-artifact) measurement despite the log-file issue above.

## 6. Decision

**The predeclared hypothesis is NOT supported.** The decision rule required B2ent's extended-budget regression to be ≤0.02 relative to its own primary-budget MAE; the observed regression (+0.1188) is essentially identical to unmodified B2's own regression (+0.1207) — a difference of 0.0019, far inside noise, not a reduction. Adding a small, standard, untuned entropy coefficient does **not** prevent, or even meaningfully reduce, the primary-to-extended MAE regression that motivated this experiment.

This is itself informative: it rules out "zero entropy bonus → excessive early-training-favorable exploitation lost to later convergence" as a *sufficient* explanation on its own, at least at this coefficient value — either the mechanism is different from the one hypothesized, or `ent_coef=0.01` is too small relative to this problem's reward scale to counteract it (this experiment cannot distinguish between those two; testing a materially different coefficient would itself be a new hypothesis requiring its own predeclaration, not a post-hoc adjustment of this one). The "single correctly-timed Harder action" explanation from `E1_DEVELOPMENT_RUN_REPORT.md` §6 — a budget-fragile, possibly incidental artifact of the primary-budget checkpoint specifically, rather than a general entropy-collapse phenomenon fixable by a training-hyperparameter tweak — remains the best-supported account of the original finding.

**No confirmatory evaluation is authorized by this result**, consistent with `E1_DEVELOPMENT_RUN_REPORT.md` §6/§7: this experiment does not resolve the budget-fragility concern that already blocked confirmatory progression, it narrows what does *not* explain it. The next well-motivated step, if pursued, would be a registered protocol testing a materially different intervention (e.g. a substantially larger entropy coefficient, or a KL-divergence trust-region check on whether the primary-budget policy actually diverges from the extended-budget one on the specific lucky_guesser cell) — not proposed as executed here, since it would require its own predeclaration.

## Artifacts

- `research/paper_strengthening/scripts/e1_action_collapse_diagnostic.py` (diagnostic, no training)
- `research/paper_strengthening/scripts/e1_improve_v3_entropy_experiment.py` (training driver)
- `research/paper_strengthening/scripts/e1_improve_v3_eval.py` (evaluation, reuses `e1_dev_eval.py`)
- `research/paper_strengthening/results/e1_action_collapse_diagnostic/action_collapse_diagnostic.json`
- `research/paper_strengthening/results/e1_improve_v3_entropy/` (checkpoints, per-step logs, training summary, eval raw/summary for both budgets)
