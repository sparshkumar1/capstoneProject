"""
E1-Improve V1, Intervention B evaluation. Evaluates the gated hybrid
(e1improve_hybrid_gate.make_gated_policy) wrapped around each of
Condition A, B0 (primary budget), and B2 (primary budget)'s existing,
already-frozen/already-trained checkpoints, on EVAL_SEEDS_DEV only, on the
identical 24-cell grid used throughout E1 -- the same evaluation harness as
e1_dev_eval.py, so results are directly comparable to
E1_DEVELOPMENT_RUN_REPORT.md's numbers.

No checkpoint is retrained. No confirmatory seed or held-out profile is
touched.
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

import x3a_lib  # noqa: E402
from e1_simulate_adapter import simulate_diverse, diverse_candidate_factory  # noqa: E402
from e1_diverse_persona_env import ARM_GRIDS, x3a_target_difficulty  # noqa: E402
from e1_train_condition_b import load_config  # noqa: E402
from e1improve_hybrid_gate import make_gated_policy  # noqa: E402

cfg = load_config()
TRAINING_SEEDS = cfg["training_seeds"]
DEV_EVAL_SEEDS = cfg["development_eval_seeds"]
EVAL_GRID = ARM_GRIDS["B2"]
LUCKY_GUESSER_CELL = (0.80, 0.60)

E1_TRAINING_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_training"
CONDITION_A_ROOT = REPO / "research" / "experiments" / "paper3" / "checkpoints"
OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1improve_hybrid_eval"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DUMMY_ENV_LOG = OUT_DIR / "_hybrid_eval_env_dummy_log.csv"


def load_ppo_condition(ckpt_dir: Path):
    model, vn = x3a_lib.load_ppo(str(ckpt_dir), str(DUMMY_ENV_LOG))
    return x3a_lib.PPOPolicy(model, vn)


def run_condition(policy_fn, label: str, training_seed):
    rows = []
    for skill, k in EVAL_GRID:
        target = x3a_target_difficulty(skill)
        for eval_seed in DEV_EVAL_SEEDS:
            res = simulate_diverse(policy_fn, diverse_candidate_factory(skill, k), target, eval_seed, shield_on=True)
            rows.append({
                "condition": label, "training_seed": training_seed, "skill": skill, "k": k,
                "eval_seed": eval_seed, "target": target, "mae": res["mae_x"],
                "oracle_agreement": res["oracle_agreement"], "final_actions": res["final_actions"],
            })
    return rows


def aggregate(rows, group_keys):
    buckets = defaultdict(list)
    for r in rows:
        buckets[tuple(r[k] for k in group_keys)].append(r)
    out = []
    for key, items in buckets.items():
        entry = dict(zip(group_keys, key))
        entry["n"] = len(items)
        entry["mae_mean"] = float(np.mean([i["mae"] for i in items]))
        entry["mae_sd"] = float(np.std([i["mae"] for i in items]))
        entry["oracle_agreement_mean"] = float(np.mean([i["oracle_agreement"] for i in items]))
        out.append(entry)
    return out


def main():
    all_rows = []
    conditions = [
        ("ConditionA_gated", CONDITION_A_ROOT, TRAINING_SEEDS),
        ("B0_primary_gated", E1_TRAINING_ROOT / "B0", TRAINING_SEEDS),
        ("B2_primary_gated", E1_TRAINING_ROOT / "B2", TRAINING_SEEDS),
    ]
    for label, root, seeds in conditions:
        print(f"Evaluating {label}...")
        for seed in seeds:
            ckpt_dir = root / f"seed_{seed}"
            base_policy = load_ppo_condition(ckpt_dir)
            gated = make_gated_policy(base_policy)
            all_rows += run_condition(gated, label, seed)

    if DUMMY_ENV_LOG.exists():
        DUMMY_ENV_LOG.unlink()

    raw_path = OUT_DIR / "e1improve_hybrid_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    pooled = aggregate(all_rows, ["condition"])
    per_seed = aggregate(all_rows, ["condition", "training_seed"])
    per_cell = aggregate(all_rows, ["condition", "skill", "k"])
    lucky_rows = [r for r in all_rows if (r["skill"], r["k"]) == LUCKY_GUESSER_CELL]
    lucky_by_condition_seed = aggregate(lucky_rows, ["condition", "training_seed"])

    # Regression check vs each condition's own ungated base (read from the existing E1 dev-eval summary)
    with open(REPO / "research" / "paper_strengthening" / "results" / "e1_dev_eval" / "e1_dev_eval_summary.json", encoding="utf-8") as f:
        base_summary = json.load(f)
    base_per_cell = {(r["condition"], r["skill"], r["k"]): r for r in base_summary["per_cell_by_condition"]}
    base_label_map = {"ConditionA_gated": "ConditionA", "B0_primary_gated": "B0", "B2_primary_gated": "B2"}

    regression_report = {}
    for gated_label, base_label in base_label_map.items():
        cells = [r for r in per_cell if r["condition"] == gated_label]
        regs = []
        for r in cells:
            key = (base_label, r["skill"], r["k"])
            if key in base_per_cell:
                diff = r["mae_mean"] - base_per_cell[key]["mae_mean"]
                regs.append({"skill": r["skill"], "k": r["k"], "gated_mae": r["mae_mean"],
                             "base_mae": base_per_cell[key]["mae_mean"], "gated_minus_base": diff,
                             "regressed_ge_0.05": diff >= 0.05})
        regression_report[gated_label] = {
            "n_regressed": sum(1 for r in regs if r["regressed_ge_0.05"]),
            "mean_diff": float(np.mean([r["gated_minus_base"] for r in regs])) if regs else None,
            "cells": regs,
        }

    summary = {
        "gate_condition": "perf>=0.90 and conf<0.40 and hes>0.60 (verbatim x3a_lib.shield() G6 nervous clause)",
        "pooled_by_condition": pooled,
        "per_seed_by_condition": per_seed,
        "lucky_guesser_cell_by_condition_and_seed": lucky_by_condition_seed,
        "regression_vs_own_ungated_base": regression_report,
        "reference_baselines_from_E1_DEVELOPMENT_RUN_REPORT": {
            r["condition"]: {"mae_mean": r["mae_mean"], "n": r["n"]}
            for r in base_summary["pooled_by_condition"]
        },
    }
    summary_path = OUT_DIR / "e1improve_hybrid_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nRaw: {raw_path}\nSummary: {summary_path}\n")
    print("Pooled MAE, gated vs reference baselines:")
    for r in sorted(pooled, key=lambda x: x["condition"]):
        print(f"  {r['condition']:>20s}: mae_mean={r['mae_mean']:.4f} n={r['n']}")
    for label, stats in summary["reference_baselines_from_E1_DEVELOPMENT_RUN_REPORT"].items():
        print(f"  {label + ' (ungated ref)':>20s}: mae_mean={stats['mae_mean']:.4f} n={stats['n']}")
    print("\nRegression vs own ungated base:")
    for label, rep in regression_report.items():
        print(f"  {label}: n_regressed>=0.05={rep['n_regressed']} mean_diff={rep['mean_diff']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
