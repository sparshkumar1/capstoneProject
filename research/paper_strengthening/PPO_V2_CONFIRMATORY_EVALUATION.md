# PPO V2 — Confirmatory Evaluation: Protocol, Ablation, and Status

## 1. Independent reproduction of the reported development result

Re-derived directly from `research/paper_strengthening/results/ppo_v2_checkpoint_selection/eval/by_step_summary.json` and `raw.json` (7,200 rows: 5 seeds × 12 checkpoints × 24 cells × 5 eval seeds), not re-run from scratch (the saved artifacts are the frozen record of that run; re-training would not "verify" the prior report, it would produce a new, different run).

- Cross-seed-averaged pooled MAE at step 16,384: **0.2697** (recomputed as `mean(seed42..999 pooled-MAE at step 16384)` = mean(0.2667, 0.2742, 0.2720, 0.2705, 0.2652) = 0.26972) — **matches the third-pass report exactly.**
- Fixed primary-budget (24,576) reference: **0.2735**, fixed extended-budget (98,304) reference: **0.3994** (recomputed pooled cross-seed mean; the third-pass report cited 0.3942, sourced from the *original* unmodified-B2 run, a *different* training run than this periodic-checkpoint run's own step-98304 checkpoint, 0.3994 — both numbers are real and correctly attributed to their own runs, not a discrepancy, but worth flagging: **the two "extended budget" numbers differ by 0.0052 across the two separately-trained runs at the identical nominal step count**, itself a small piece of evidence for the run-to-run variance discussed in §3 below).
- **Reproduced successfully, discrepancy noted and explained, not silently accepted.**

## 2. Freezing the selection procedure (item 2.1)

Read directly from `research/paper_strengthening/scripts/ppo_v2_checkpoint_selection_experiment.py` and `ppo_v2_checkpoint_selection_eval.py` (both written in the prior pass; re-read fresh for this audit rather than trusted from memory):

- **Selection metric:** cross-seed-averaged pooled MAE (mean over 5 training seeds of each seed's own pooled-over-24-cells-×-5-eval-seeds MAE) at a given checkpoint step.
- **Eligible checkpoints:** 12 per seed, every 8,192 steps from 8,192 to 98,304 (one continuous training run per seed; checkpoints are not separate training replications).
- **Tie-breaking rule:** **none was predeclared.** Not exercised in practice (16,384's MAE, 0.2697, is a clear unique minimum — the next-closest values are 0.2735 at 24,576 and 0.2776 at 8,192, both >0.003 away), but this is a genuine gap in the original protocol, disclosed here rather than silently patched after the fact.
- **Seed aggregation:** simple unweighted mean across the 5 fixed training seeds (42, 123, 456, 789, 999 — the same 5 used throughout every E1-family experiment).
- **Confirmatory-data usage: verified absent.** `dev_eval.DEV_EVAL_SEEDS` (imported unmodified from `e1_dev_eval.py`) is `[1001, 2002, 3003, 4004, 5005]` — the development eval seeds. Neither script imports or references `EVAL_SEEDS_CONFIRMATORY` (21021-40040) or the 3 held-out profiles anywhere; confirmed by direct read of both files' full source, not by trusting their docstrings alone.
- **Frozen as of this pass:** the selection procedure, selected checkpoint (16,384 steps), and all 5 seeds' checkpoint files under `research/paper_strengthening/results/ppo_v2_checkpoint_selection/B2_periodic/seed_<s>/step_16384/` are treated as fixed from this point forward in this pass. No parameter of the selection rule was adjusted after seeing this section's own analysis.

## 3. Checkpoint-selection ablation (item 2.4) — the improvement is real but not uniform across seeds

Per-seed comparison, selected checkpoint (16,384) vs. the fixed primary-budget checkpoint (24,576), both from the *same* periodic-checkpoint training run (so this is a clean within-run comparison, not confounded by two separately-trained runs):

| seed | step 16,384 MAE | step 24,576 MAE | Δ (16384 − 24576) |
|---|---|---|---|
| 42 | 0.2667 | 0.2652 | **+0.0015** (worse) |
| 123 | 0.2742 | 0.2803 | −0.0061 (better) |
| 456 | 0.2720 | 0.2674 | **+0.0046** (worse) |
| 789 | 0.2705 | 0.2659 | **+0.0046** (worse) |
| 999 | 0.2652 | 0.2886 | −0.0234 (better) |

**The selected checkpoint is worse than the fixed-24,576 checkpoint on 3 of 5 seeds**, and the cross-seed-average win is driven disproportionately by seed 999's large improvement (−0.0234, more than 3× the magnitude of any other seed's delta in either direction). Examining *why* (per-cell, skill=0.80-specific MAE, the persona driving the overall regression per §1's diagnosis): seed 999's skill=0.80 MAE is 0.264 at step 24,576 but only 0.132 at step 16,384 — while seeds 42, 456, and 789 are already at their (good) floor value of 0.127 at *both* steps. **This is better characterized as "step 24,576 happened to be a locally mediocre point for seed 999 specifically" than as "step 16,384 is uniquely and robustly better"** — both checkpoints sit inside the same broad, low-MAE, pre-collapse plateau (steps 8,192-32,768, see §4), and the seed-999 delta looks like within-plateau training noise for that one seed rather than a large, robust, generalizable effect.

**Compared against the final checkpoint (98,304):** the selected checkpoint is dramatically and uniformly better on all 5 seeds (0.2652-0.2742 vs. 0.3500-0.4432) — this part of the result is robust and not seed-dependent.

**No prespecified alternative checkpoint-selection rule exists from a prior pass** (none was registered before this one), so no such comparison was run, per this pass's own instruction not to introduce an extensive new search.

## 4. Skill=0.80 mechanism, reproduced at full resolution (item 2.5)

Full per-step, per-skill pooled MAE (all 6 skill values, all 5 seeds, all 5 eval seeds), computed directly from `raw.json`:

| step | skill=0.20 | skill=0.35 | skill=0.50 | skill=0.65 | **skill=0.80** | skill=0.90 |
|---|---|---|---|---|---|---|
| 8,192 | 0.2727 | 0.1073 | 0.5000 | 0.0200 | 0.1700 | 0.5955 |
| 16,384 | 0.2727 | 0.0982 | 0.5000 | 0.0182 | **0.1373** | 0.5918 |
| 24,576 | 0.2727 | 0.0955 | 0.5000 | 0.0055 | 0.1727 | 0.5945 |
| 32,768 | 0.2727 | 0.0973 | 0.5000 | 0.0027 | 0.2045 | 0.5936 |
| 40,960 | 0.2727 | 0.0964 | 0.5000 | 0.0000 | 0.3364 | 0.6164 |
| 49,152 | 0.2727 | 0.0964 | 0.5000 | 0.0000 | 0.5255 | 0.6309 |
| 57,344 | 0.2727 | 0.0973 | 0.5000 | 0.0000 | 0.7618 | 0.6600 |
| 65,536 | 0.2727 | 0.0991 | 0.5000 | 0.0000 | 0.8618 | 0.7355 |
| 73,728 | 0.2727 | 0.0964 | 0.5000 | 0.0000 | **0.8691** (peak) | 0.7518 |
| 81,920 | 0.2727 | 0.0945 | 0.5000 | 0.0000 | 0.8436 | 0.7091 |
| 90,112 | 0.2727 | 0.0964 | 0.5000 | 0.0000 | 0.8091 | 0.6991 |
| 98,304 | 0.2727 | 0.0964 | 0.5000 | 0.0000 | 0.8227 | 0.7045 |

This resolves the mechanism cleanly, with a resolution the prior pass's 2-point (primary/extended) comparison could not provide:

- **Skills 0.20, 0.35, 0.50, 0.65 are essentially perfectly flat across the entire 8,192-98,304 range** — completely unaffected by training duration. (Skill=0.65 even *improves* slightly, 0.0200→0.0000, and then holds exactly at the floor from step 40,960 onward.)
- **Skill=0.90 rises moderately and gradually** (0.5955→0.7518 peak at step 73,728, partial recovery to ~0.70-0.70 by 98,304) — a real but much smaller effect than skill=0.80's.
- **Skill=0.80 is flat-to-good through step 32,768, then collapses sharply and almost monotonically** from step 32,768/40,960 through its peak at step 73,728 (0.17 → 0.87, a >5× increase), with only partial recovery afterward (down to ~0.82 by 98,304, still >6× worse than its early-training value).
- **Skill=0.80's own minimum across all 12 checkpoints is at step 16,384** (0.1373) — this is the direct, causal reason the cross-seed checkpoint-selection procedure landed on 16,384: it is not a coincidence, it is the checkpoint where the specific persona driving the entire regression happens to be at its best.
- **The collapse is not specific to one seed** — per-seed skill=0.80 trajectories (all 5 seeds) show the same rise pattern starting in the 32,768-49,152 range and escalating through 57,344-90,112, ending badly degraded (0.627-0.955) at step 98,304 for every seed. This is a systematic property of this training setup, not seed-specific noise.
- **Evaluation-noise check:** skill=0.80's own step-to-step variation *within* the stable early region (8,192-32,768: 0.1700, 0.1373, 0.1727, 0.2045) has a range of ~0.07 — this is the natural floor of measurement noise for this cell at this eval-seed count (5), and is the same order of magnitude as the seed-999 checkpoint-selection delta discussed in §3, supporting that characterization.

**This does not, by itself, explain *why* skill=0.80 specifically (not 0.65 or 0.90) is the fragile one** — that would require inspecting the persona/target-difficulty structure in more depth than existing artifacts support without new instrumentation, and is not pursued further in this pass per the instruction not to repeat broad tuning without a new, specific, testable hypothesis.

## 5. Confirmatory evaluation: NOT executed in this pass — explicit, reasoned decision

**Per this pass's own instructions** ("If any of these conditions cannot be verified, stop and report the limitation rather than presenting the experiment as confirmatory" and "complete all safe preparatory work and document the exact blocker" when blocked), and consistent with every prior E1-family pass's stopping discipline in this project (`E1_DEVELOPMENT_RUN_REPORT.md` §6/§7, `E1_IMPROVE_V2_REPORT.md`, `PPO_FORMULATION_INVESTIGATION_V1_REPORT.md` §6), **this pass does not spend the locked confirmatory evaluation seeds (21021-40040) or the 3 held-out profiles on the selected checkpoint.**

This is a reasoned decision, not a technical inability — nothing in §§1-4 above found broken tooling or unverifiable claims; the selection procedure, seeds, and data boundaries are all confirmed clean. The decision rests on §3's finding specifically:

1. **The checkpoint-selection "improvement" is not a uniform, robust win** — it is worse than the naive fixed-budget checkpoint on 3 of 5 seeds, and the aggregate win is driven by one seed's delta that is plausibly within-plateau noise rather than a large true effect (§3, §4's noise-floor check).
2. **CLAUDE.md's own standing rule** requires a hashed, git-tagged, *approved* protocol and run manifest before any new confirmatory experiment starts, and explicit human approval for major experiment decisions — an autonomous pass has no mechanism to obtain that sign-off mid-task, and spending the confirmatory dataset is **irreversible**: per this pass's own instruction 2.3, "If the existing confirmatory dataset has already been used to tune or select models, do not reuse it as untouched confirmatory evidence" — meaning a confirmatory run on a result this marginal, once spent, cannot be "tried again" if the result doesn't hold up, or reserved for a more robust future candidate.
3. Given (1), spending an irreplaceable resource now is a poor use of it even setting aside (2): a candidate that isn't robustly better than the naive baseline on the development grid itself is a weak candidate for confirmatory promotion regardless of authorization.

**What this pass did instead, as the safe preparatory work for when this evaluation is authorized:**

- A complete, ready-to-run protocol is specified below (§6), so that if/when a human authorizes spending the confirmatory data — either on this checkpoint or a more robust future candidate — the protocol exists and is separately reviewable *before* being run (true preregistration, not retroactive).
- §§3-4 constitute the exploratory/ablation analysis item 2.3/2.4 call for, entirely on development data.

## 6. Ready-to-run confirmatory protocol (registered here, not yet executed)

If authorized: evaluate the frozen step-16,384 checkpoint (all 5 training seeds, files already saved and untouched since training) against the locked confirmatory eval seeds (21021-40040, 20 seeds) and the 3 held-out profiles, using the exact same `x3a_lib.simulate()`/`shield()` methodology as X3-A and every other E1-family confirmatory-eligible evaluation. Comparisons: selected checkpoint vs. fixed-primary-budget (24,576) checkpoint (same training run, paired by seed and eval scenario), vs. Constant-Same+G, vs. Heuristic+G (both parameter-free, already-available baselines). Statistics: paired differences with two-way cluster bootstrap (by persona and by training seed, matching X3-A's own methodology), 95% CI, the same ±0.12 equivalence margin used in X3-A's primary contrast, superiority threshold −0.20 (matching X3-A). Report per-seed and aggregate results, explicit accounting of any excluded/invalid observations, and — given §3's finding — an explicit per-seed non-uniformity check as a required part of the write-up, not an optional afterthought. This protocol is newly proposed for PPO V2 specifically (X3-A's own registration covers only the original frozen PPO+G checkpoint) and is labeled as such, not retroactively described as preregistered before this document.

## Status: development result independently reproduced and reconciled; selection procedure frozen and verified confirmatory-data-clean; ablation reveals the win is real but not uniform across seeds; confirmatory evaluation NOT executed, protocol prepared and pending explicit human authorization.
