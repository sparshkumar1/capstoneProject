"""
E1 -- mechanical application of the pre-declared extended-budget decision
rule (recorded in research/paper_strengthening/results/e1_training/
run_manifest.json BEFORE the primary-budget training run started).

Rule (verbatim from the manifest): pool each arm's 5 seeds'
training_curves.csv mean_reward_rolling series (aligned by logged timestep).
Fit the rise over the final quartile of logged points (timestep > 18432) and
compare it to the rise over the full curve. If the final-quartile rise
exceeds 10% of the full-curve rise for EITHER arm, the curve is judged
still-rising and the extended-budget diagnostic is triggered for BOTH arms.

This script only reads training_curves.csv files this run produced; it does
not touch development or confirmatory MAE.
"""
import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np

REPO = Path(__file__).resolve().parents[3]
TRAIN_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_training"
CONFIG_PATH = REPO / "research" / "paper_strengthening" / "scripts" / "e1_config.json"

with open(CONFIG_PATH, encoding="utf-8") as f:
    cfg = json.load(f)
SEEDS = cfg["training_seeds"]
ARMS = cfg["arms"]
PRIMARY_BUDGET = cfg["timesteps_primary"]
QUARTILE_CUTOFF = 0.75 * PRIMARY_BUDGET


def load_curve(arm, seed):
    path = TRAIN_ROOT / arm / f"seed_{seed}" / "training_curves.csv"
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((int(r["timestep"]), float(r["mean_reward_rolling"])))
    rows.sort(key=lambda x: x[0])
    return rows


def pooled_curve(arm):
    """Averages mean_reward_rolling across the 5 seeds at each matching logged timestep."""
    by_ts = defaultdict(list)
    for seed in SEEDS:
        for ts, val in load_curve(arm, seed):
            by_ts[ts].append(val)
    ts_sorted = sorted(by_ts)
    pooled = [(ts, float(np.mean(by_ts[ts]))) for ts in ts_sorted]
    return pooled


def quartile_check(pooled):
    full_rise = pooled[-1][1] - pooled[0][1]
    quartile_pts = [(ts, v) for ts, v in pooled if ts > QUARTILE_CUTOFF]
    if len(quartile_pts) < 2:
        quartile_rise = 0.0
    else:
        quartile_rise = quartile_pts[-1][1] - quartile_pts[0][1]
    denom = abs(full_rise) if abs(full_rise) > 1e-9 else 1e-9
    ratio = quartile_rise / denom
    return {
        "full_curve_first_point": pooled[0], "full_curve_last_point": pooled[-1],
        "full_rise": full_rise, "quartile_first_point": quartile_pts[0] if quartile_pts else None,
        "quartile_last_point": quartile_pts[-1] if quartile_pts else None,
        "quartile_rise": quartile_rise, "quartile_rise_over_full_rise_ratio": ratio,
        "still_rising": bool(ratio > 0.10),
    }


def main():
    result = {}
    triggered = False
    for arm in ARMS:
        pooled = pooled_curve(arm)
        check = quartile_check(pooled)
        result[arm] = check
        if check["still_rising"]:
            triggered = True

    result["extended_budget_triggered"] = triggered
    result["rule_applied"] = (
        "quartile_rise / full_rise > 0.10 for EITHER arm triggers extended budget for BOTH arms"
    )

    out_path = TRAIN_ROOT / "e1_convergence_check.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

    print(json.dumps(result, indent=2, default=str))
    print(f"\nExtended-budget diagnostic triggered: {triggered}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
