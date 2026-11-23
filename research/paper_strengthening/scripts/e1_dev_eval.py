"""
E1 -- development-phase evaluation (approved run, step 5 of the E1 V4
development-phase approval message).

Evaluates B0 and B2's newly trained checkpoints (5 training seeds each) on
the DEVELOPMENT evaluation seeds only (1001-5005, from e1_config.json). Does
NOT touch EVAL_SEEDS_CONFIRMATORY (21021-40040) or the 3 held-out profiles --
those remain locked per protocol V4 section 2.4 / section 4.1.

Evaluation grid: the same 24-cell (skill, k) grid used to train B2
(ARM_GRIDS["B2"] in e1_diverse_persona_env.py), used identically for every
condition below so all comparisons are on "identical scenarios" (the
explicit instruction in the approval message, step 5):
  - B0  (5 seeds, this run's new checkpoints)
  - B2  (5 seeds, this run's new checkpoints)
  - Condition A (the existing, frozen, unmodified PPO+G checkpoints,
    research/experiments/paper3/checkpoints/seed_<s>/, same 5 seeds)
  - Constant-Same+G (x3a_lib.make_policy("const_same"), no training seed)
  - Heuristic+G (x3a_lib.make_policy("heuristic"), no training seed)

All conditions use shield_on=True (the "+G" convention used throughout
X3-A/P3), the unmodified x3a_lib.shield(), and the frozen
target_difficulty = round(10*skill)/2.0 formula (independent of k).

The "lucky_guesser mechanism check" cell referenced in protocol V4 section
4.3 is (skill=0.80, k=0.60) -- the grid cell verified in protocol V3 section
1.2 to reach the high-perf/low-conf/high-hes (guardrail G6 nervous-expert
exclusion) state ~94-95% of the time, with target_difficulty=4.0 matching
PERSONA_TARGETS' lucky_guesser target exactly -- and is reported separately
from pooled/other-cell numbers, never merged into them.

No confirmatory data (EVAL_SEEDS_CONFIRMATORY, held-out profiles) is
inspected by this script. No frozen file is modified. No checkpoint is
retrained.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
X3A_DIR = REPO / "research" / "confirmatory" / "X3-A"
if str(X3A_DIR) not in sys.path:
    sys.path.insert(0, str(X3A_DIR))
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import x3a_lib  # noqa: E402  (frozen; imported only)
from e1_simulate_adapter import simulate_diverse, diverse_candidate_factory  # noqa: E402
from e1_diverse_persona_env import ARM_GRIDS, x3a_target_difficulty  # noqa: E402
from e1_train_condition_b import load_config  # noqa: E402

cfg = load_config()
TRAINING_SEEDS = cfg["training_seeds"]
DEV_EVAL_SEEDS = cfg["development_eval_seeds"]
EVAL_GRID = ARM_GRIDS["B2"]  # 24 cells: skill in {0.20,...,0.90} x k in {0.0,0.30,0.45,0.60}
LUCKY_GUESSER_CELL = (0.80, 0.60)

BUDGET_LABEL = sys.argv[1] if len(sys.argv) > 1 else "primary"
if BUDGET_LABEL == "extended":
    E1_TRAINING_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_training_extended"
    OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_dev_eval_extended"
else:
    E1_TRAINING_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_training"
    OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_dev_eval"
CONDITION_A_ROOT = REPO / "research" / "experiments" / "paper3" / "checkpoints"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DUMMY_ENV_LOG = OUT_DIR / "_dev_eval_env_dummy_log.csv"


def load_ppo_condition(ckpt_dir: Path):
    model, vn = x3a_lib.load_ppo(str(ckpt_dir), str(DUMMY_ENV_LOG))
    return x3a_lib.PPOPolicy(model, vn)


def run_condition(policy_fn, label: str, training_seed):
    """Runs one condition across the full EVAL_GRID x DEV_EVAL_SEEDS matrix."""
    rows = []
    for skill, k in EVAL_GRID:
        target = x3a_target_difficulty(skill)
        for eval_seed in DEV_EVAL_SEEDS:
            res = simulate_diverse(
                policy_fn, diverse_candidate_factory(skill, k), target, eval_seed, shield_on=True
            )
            rows.append({
                "condition": label, "training_seed": training_seed, "skill": skill, "k": k,
                "eval_seed": eval_seed, "target": target,
                "mae": res["mae_x"], "volatility": res["vol_x"], "oscillation": res["osc_x"],
                "guardrail_interventions": res["guardrail_interventions"],
                "overrides": res["overrides"], "oracle_agreement": res["oracle_agreement"],
                "final_actions": res["final_actions"],
            })
    return rows


def aggregate(rows, group_keys):
    buckets = defaultdict(list)
    for r in rows:
        key = tuple(r[k] for k in group_keys)
        buckets[key].append(r)
    out = []
    for key, items in buckets.items():
        entry = dict(zip(group_keys, key))
        entry["n"] = len(items)
        entry["mae_mean"] = float(np.mean([i["mae"] for i in items]))
        entry["mae_sd"] = float(np.std([i["mae"] for i in items]))
        entry["oracle_agreement_mean"] = float(np.mean([i["oracle_agreement"] for i in items]))
        entry["volatility_mean"] = float(np.mean([i["volatility"] for i in items]))
        out.append(entry)
    return out


def main():
    all_rows = []

    print("Evaluating B0 checkpoints...")
    for seed in TRAINING_SEEDS:
        ckpt_dir = E1_TRAINING_ROOT / "B0" / f"seed_{seed}"
        policy = load_ppo_condition(ckpt_dir)
        all_rows += run_condition(policy.act, "B0", seed)

    print("Evaluating B2 checkpoints...")
    for seed in TRAINING_SEEDS:
        ckpt_dir = E1_TRAINING_ROOT / "B2" / f"seed_{seed}"
        policy = load_ppo_condition(ckpt_dir)
        all_rows += run_condition(policy.act, "B2", seed)

    print("Evaluating Condition A (existing frozen PPO+G checkpoints)...")
    for seed in TRAINING_SEEDS:
        ckpt_dir = CONDITION_A_ROOT / f"seed_{seed}"
        policy = load_ppo_condition(ckpt_dir)
        all_rows += run_condition(policy.act, "ConditionA", seed)

    print("Evaluating Constant-Same+G and Heuristic+G baselines...")
    const_same = x3a_lib.make_policy("const_same")
    heuristic = x3a_lib.make_policy("heuristic")
    all_rows += run_condition(const_same, "ConstantSame", None)
    all_rows += run_condition(heuristic, "Heuristic", None)

    if DUMMY_ENV_LOG.exists():
        DUMMY_ENV_LOG.unlink()

    raw_path = OUT_DIR / "e1_dev_eval_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    pooled = aggregate(all_rows, ["condition"])
    per_seed = aggregate(all_rows, ["condition", "training_seed"])
    per_cell = aggregate(all_rows, ["condition", "skill", "k"])
    lucky_cell_rows = [r for r in all_rows if (r["skill"], r["k"]) == LUCKY_GUESSER_CELL]
    lucky_by_condition = aggregate(lucky_cell_rows, ["condition"])
    lucky_by_condition_seed = aggregate(lucky_cell_rows, ["condition", "training_seed"])

    per_persona_regression = []
    b0_cell = {(r["condition"], r["skill"], r["k"]): r for r in per_cell if r["condition"] == "B0"}
    for r in per_cell:
        if r["condition"] == "B2":
            key = ("B0", r["skill"], r["k"])
            if key in b0_cell:
                diff = r["mae_mean"] - b0_cell[key]["mae_mean"]
                per_persona_regression.append({
                    "skill": r["skill"], "k": r["k"],
                    "B2_mae": r["mae_mean"], "B0_mae": b0_cell[key]["mae_mean"],
                    "B2_minus_B0": diff, "regressed_ge_0.05": diff >= 0.05,
                })

    summary = {
        "eval_grid_cells": len(EVAL_GRID),
        "development_eval_seeds": DEV_EVAL_SEEDS,
        "n_rows_total": len(all_rows),
        "pooled_by_condition": pooled,
        "per_seed_by_condition": per_seed,
        "per_cell_by_condition": per_cell,
        "lucky_guesser_cell_skill_k": LUCKY_GUESSER_CELL,
        "lucky_guesser_cell_by_condition": lucky_by_condition,
        "lucky_guesser_cell_by_condition_and_seed": lucky_by_condition_seed,
        "B2_vs_B0_per_cell_regression_check": per_persona_regression,
    }
    summary_path = OUT_DIR / "e1_dev_eval_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nRaw rows: {raw_path}")
    print(f"Summary: {summary_path}")
    print("\nPooled MAE by condition:")
    for r in sorted(pooled, key=lambda x: x["condition"]):
        print(f"  {r['condition']:>15s}: mae_mean={r['mae_mean']:.4f} sd={r['mae_sd']:.4f} n={r['n']}")
    print("\nlucky_guesser cell (skill=0.80, k=0.60) MAE by condition:")
    for r in sorted(lucky_by_condition, key=lambda x: x["condition"]):
        print(f"  {r['condition']:>15s}: mae_mean={r['mae_mean']:.4f} oracle_agree={r['oracle_agreement_mean']:.4f} n={r['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
