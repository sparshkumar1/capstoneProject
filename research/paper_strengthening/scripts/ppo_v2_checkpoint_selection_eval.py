"""
Evaluates every periodically-saved B2_periodic checkpoint (5 seeds x 12
checkpoints each, steps 8192-98304 in 8192-step increments) on the same
24-cell dev grid x 5 development eval seeds used throughout the E1 series.
No confirmatory seed, no held-out profile.

Reuses e1_dev_eval.py's own condition-runner/aggregation functions
unmodified (imported, not copied).

Writes: research/paper_strengthening/results/ppo_v2_checkpoint_selection/eval/
  - raw.json: every (seed, checkpoint_step) x cell x eval_seed row
  - by_step_summary.json: pooled MAE per checkpoint_step, per-seed and
    cross-seed-averaged, plus the single predeclared selection result
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import e1_dev_eval as dev_eval  # noqa: E402  (imported unmodified; its main() is never called)

CKPT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "ppo_v2_checkpoint_selection" / "B2_periodic"
OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "ppo_v2_checkpoint_selection" / "eval"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_BUDGET_MAE = 0.2735  # unmodified B2, from E1_DEVELOPMENT_RUN_REPORT.md, for comparison only
EXTENDED_BUDGET_MAE = 0.3942  # unmodified B2, same source


EXPECTED_CHECKPOINTS_PER_SEED = 12
EXPECTED_ROWS_PER_CHECKPOINT = 120  # 24 cells x 5 dev eval seeds, matching dev_eval.py's own grid


def main():
    # ── Reproducibility/safety guards (fourth pass, item 6) ────────────────
    # Fail loudly, before evaluating anything, rather than silently producing
    # a summary from a partial or contaminated run.
    assert list(dev_eval.DEV_EVAL_SEEDS) == [1001, 2002, 3003, 4004, 5005], (
        f"Eval seeds changed unexpectedly: {dev_eval.DEV_EVAL_SEEDS}. Refusing to run: this script must only ever "
        "evaluate against the development grid, never the locked confirmatory seeds (21021-40040)."
    )
    assert not hasattr(dev_eval, "EVAL_SEEDS_CONFIRMATORY"), (
        "e1_dev_eval.py unexpectedly exposes EVAL_SEEDS_CONFIRMATORY in a module this script imports from; "
        "refusing to run to avoid any risk of accidental confirmatory-data use."
    )

    seeds = dev_eval.TRAINING_SEEDS
    all_rows = []
    seen_seed_step_pairs = set()
    for seed in seeds:
        seed_dir = CKPT_ROOT / f"seed_{seed}"
        assert seed_dir.is_dir(), f"Missing checkpoint directory for seed={seed}: {seed_dir}"
        step_dirs = sorted(seed_dir.glob("step_*"), key=lambda p: int(p.name.split("_")[1]))
        found_steps = [int(p.name.split("_")[1]) for p in step_dirs]
        assert len(found_steps) == EXPECTED_CHECKPOINTS_PER_SEED, (
            f"seed={seed}: expected {EXPECTED_CHECKPOINTS_PER_SEED} checkpoints, found {len(found_steps)} "
            f"({found_steps}). Refusing to silently evaluate a partial/failed training run."
        )
        assert len(set(found_steps)) == len(found_steps), f"seed={seed}: duplicate checkpoint step directories found"

        for step_dir in step_dirs:
            step = int(step_dir.name.split("_")[1])
            pair = (seed, step)
            assert pair not in seen_seed_step_pairs, f"Duplicate (seed, step) pair encountered: {pair}"
            seen_seed_step_pairs.add(pair)

            policy = dev_eval.load_ppo_condition(step_dir)
            rows = dev_eval.run_condition(policy.act, f"B2ckpt_step{step}", seed)
            assert len(rows) == EXPECTED_ROWS_PER_CHECKPOINT, (
                f"seed={seed} step={step}: expected {EXPECTED_ROWS_PER_CHECKPOINT} eval rows, got {len(rows)}"
            )
            for r in rows:
                assert np.isfinite(r["mae"]), f"Non-finite MAE at seed={seed} step={step}: {r}"
                r["checkpoint_step"] = step
            all_rows.extend(rows)
            print(f"[seed={seed} step={step}] evaluated, {len(rows)} rows")

    if dev_eval.DUMMY_ENV_LOG.exists():
        dev_eval.DUMMY_ENV_LOG.unlink()

    raw_path = OUT_DIR / "raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    # Pooled MAE per (seed, step)
    by_seed_step = defaultdict(list)
    for r in all_rows:
        by_seed_step[(r["training_seed"], r["checkpoint_step"])].append(r["mae"])
    per_seed_step = {
        f"seed{seed}_step{step}": float(np.mean(maes))
        for (seed, step), maes in by_seed_step.items()
    }
    assert len(per_seed_step) == len(seeds) * EXPECTED_CHECKPOINTS_PER_SEED, (
        f"Expected {len(seeds) * EXPECTED_CHECKPOINTS_PER_SEED} (seed, step) aggregates, got {len(per_seed_step)} "
        "-- a run silently went missing between row collection and aggregation."
    )

    # Cross-seed-averaged MAE per step (the predeclared selection statistic)
    by_step = defaultdict(list)
    for (seed, step), maes in by_seed_step.items():
        by_step[step].append(float(np.mean(maes)))
    cross_seed_avg_by_step = {step: float(np.mean(vals)) for step, vals in by_step.items()}
    best_step = min(cross_seed_avg_by_step, key=cross_seed_avg_by_step.get)
    best_mae = cross_seed_avg_by_step[best_step]

    decision = {
        "predeclared_rule": "select single cross-seed-averaged-MAE-minimizing checkpoint_step, "
                             "applied uniformly to all 5 seeds; supported only if resulting MAE "
                             "is no worse than fixed-primary-budget MAE (0.2735) by more than 0.01",
        "selected_step": best_step,
        "selected_step_cross_seed_mae": round(best_mae, 4),
        "fixed_primary_budget_mae_reference": PRIMARY_BUDGET_MAE,
        "fixed_extended_budget_mae_reference": EXTENDED_BUDGET_MAE,
        "delta_vs_primary_budget": round(best_mae - PRIMARY_BUDGET_MAE, 4),
        "supported": bool(best_mae - PRIMARY_BUDGET_MAE <= 0.01),
    }

    summary = {
        "cross_seed_avg_mae_by_step": {str(k): round(v, 4) for k, v in sorted(cross_seed_avg_by_step.items())},
        "per_seed_step_mae": {k: round(v, 4) for k, v in per_seed_step.items()},
        "decision": decision,
    }
    summary_path = OUT_DIR / "by_step_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nCross-seed-averaged pooled MAE by checkpoint step:")
    for step in sorted(cross_seed_avg_by_step):
        marker = "  <-- SELECTED" if step == best_step else ""
        print(f"  step={step:>6d}: MAE={cross_seed_avg_by_step[step]:.4f}{marker}")
    print(f"\nFixed primary-budget (24576) reference MAE: {PRIMARY_BUDGET_MAE}")
    print(f"Fixed extended-budget (98304) reference MAE: {EXTENDED_BUDGET_MAE}")
    print(f"\nDECISION: {decision}")
    print(f"\nRaw: {raw_path}\nSummary: {summary_path}")


if __name__ == "__main__":
    main()
