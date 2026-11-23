"""
E1 Dynamics Match V1 -- factorial contrast analysis and CSV export
(protocol section 3's secondary, exploratory, descriptive-only analyses).
No significance testing; purely descriptive main-effect/interaction
contrasts using the standard 2x2x2 factorial sign-table formula.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from e1dynmatch_env_variant import ALL_8_ARMS, arm_label_for  # noqa: E402

RUN_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1dynmatch_v1"

SIGN = {"original": -1, "matched": +1}


def load_summary():
    with open(RUN_ROOT / "e1dynmatch_eval_summary.json", encoding="utf-8") as f:
        return json.load(f)


def factorial_contrasts(arm_means: dict, step: int):
    """arm_means: {arm_label: pooled_mae_mean at this step}. Returns main
    effects and all interaction contrasts using the standard 2x2x2
    sign-table formula: contrast_X = (1/4) * sum_arms( sign_X(arm) * mean(arm) ),
    i.e. the average difference attributable to flipping that factor/
    interaction combination, holding the marginal structure fixed. This is
    a descriptive decomposition only -- no inference, no significance."""
    results = {}
    for combo_name, factors in [
        ("A", ("a",)), ("B", ("b",)), ("C", ("c",)),
        ("AB", ("a", "b")), ("AC", ("a", "c")), ("BC", ("b", "c")),
        ("ABC", ("a", "b", "c")),
    ]:
        total = 0.0
        for factor_a, factor_b, factor_c in ALL_8_ARMS:
            label = arm_label_for(factor_a, factor_b, factor_c)
            levels = {"a": factor_a, "b": factor_b, "c": factor_c}
            sign_product = 1
            for f in factors:
                sign_product *= SIGN[levels[f]]
            total += sign_product * arm_means[label]
        results[combo_name] = total / 4.0
    return results


def main():
    summary = load_summary()
    pooled = summary["pooled_by_arm_step"]
    per_seed = summary["per_seed_by_arm_step"]
    per_cell = summary["per_cell_by_arm_step"]

    # --- Per-seed / per-cell CSV export ---
    with open(RUN_ROOT / "e1dynmatch_per_seed_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["arm", "checkpoint_step", "training_seed", "n", "mae_mean", "mae_sd", "oracle_agreement_mean"])
        w.writeheader()
        for r in sorted(per_seed, key=lambda x: (x["arm"], x["checkpoint_step"], x["training_seed"])):
            w.writerow(r)

    with open(RUN_ROOT / "e1dynmatch_per_cell_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["arm", "checkpoint_step", "skill", "k", "n", "mae_mean", "mae_sd", "oracle_agreement_mean"])
        w.writeheader()
        for r in sorted(per_cell, key=lambda x: (x["arm"], x["checkpoint_step"], x["skill"], x["k"])):
            w.writerow(r)

    # --- Paired within-seed MMM vs OOO ---
    ooo_seed = {r["training_seed"]: r["mae_mean"] for r in per_seed if r["arm"] == "OOO" and r["checkpoint_step"] == 24576}
    mmm_seed = {r["training_seed"]: r["mae_mean"] for r in per_seed if r["arm"] == "MMM" and r["checkpoint_step"] == 24576}
    paired = []
    for seed in sorted(ooo_seed):
        paired.append({
            "training_seed": seed, "OOO_mae": ooo_seed[seed], "MMM_mae": mmm_seed.get(seed),
            "MMM_minus_OOO": (mmm_seed[seed] - ooo_seed[seed]) if seed in mmm_seed else None,
        })

    # --- Per-cell regression check, MMM vs OOO at 24576 ---
    ooo_cell = {(r["skill"], r["k"]): r["mae_mean"] for r in per_cell if r["arm"] == "OOO" and r["checkpoint_step"] == 24576}
    mmm_cell = {(r["skill"], r["k"]): r["mae_mean"] for r in per_cell if r["arm"] == "MMM" and r["checkpoint_step"] == 24576}
    cell_diffs = []
    for key in sorted(ooo_cell):
        diff = mmm_cell[key] - ooo_cell[key]
        cell_diffs.append({"skill": key[0], "k": key[1], "OOO_mae": ooo_cell[key], "MMM_mae": mmm_cell[key],
                            "MMM_minus_OOO": diff, "regressed_ge_0.05": diff >= 0.05})

    # --- Factorial contrasts at each checkpoint step ---
    contrasts_by_step = {}
    for step in (8192, 16384, 24576):
        arm_means = {r["arm"]: r["mae_mean"] for r in pooled if r["checkpoint_step"] == step}
        if len(arm_means) == 8:
            contrasts_by_step[step] = factorial_contrasts(arm_means, step)

    with open(RUN_ROOT / "e1dynmatch_factorial_contrasts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["checkpoint_step", "contrast", "value_mae_units", "interpretation"])
        interp = {
            "A": "main effect of step-size/floor factor (matched - original, averaged)",
            "B": "main effect of horizon factor", "C": "main effect of initial-difficulty factor",
            "AB": "A x B interaction", "AC": "A x C interaction", "BC": "B x C interaction",
            "ABC": "three-way interaction",
        }
        for step, contrasts in contrasts_by_step.items():
            for name, val in contrasts.items():
                w.writerow([step, name, round(val, 5), interp[name]])

    # --- Extended-budget trigger check ---
    ooo_24576 = next(r for r in pooled if r["arm"] == "OOO" and r["checkpoint_step"] == 24576)
    mmm_24576 = next(r for r in pooled if r["arm"] == "MMM" and r["checkpoint_step"] == 24576)
    mae_gap = ooo_24576["mae_mean"] - mmm_24576["mae_mean"]  # positive = MMM better
    max_regression = max((c["MMM_minus_OOO"] for c in cell_diffs), default=0.0)
    trigger_met = (mae_gap >= 0.02) and (max_regression < 0.05)

    HEURISTIC_MAE = 0.2674
    final_summary = {
        "primary_comparison_24576": {
            "OOO_pooled_mae": ooo_24576["mae_mean"], "OOO_sd": ooo_24576["mae_sd"],
            "MMM_pooled_mae": mmm_24576["mae_mean"], "MMM_sd": mmm_24576["mae_sd"],
            "MMM_minus_OOO": mmm_24576["mae_mean"] - ooo_24576["mae_mean"],
            "gap_to_heuristic_G_0.2674": {
                "OOO": ooo_24576["mae_mean"] - HEURISTIC_MAE,
                "MMM": mmm_24576["mae_mean"] - HEURISTIC_MAE,
            },
        },
        "paired_within_seed_mmm_vs_ooo": paired,
        "per_cell_mmm_vs_ooo_regressions": cell_diffs,
        "n_cells_regressed_ge_0.05": sum(1 for c in cell_diffs if c["regressed_ge_0.05"]),
        "extended_budget_trigger": {
            "mae_gap_ooo_minus_mmm": mae_gap, "required_gap": 0.02,
            "max_percell_regression": max_regression, "required_max_regression": "< 0.05",
            "triggered": trigger_met,
        },
        "practical_improvement_criterion_met_for_MMM_vs_OOO": (
            mmm_24576["mae_mean"] < ooo_24576["mae_mean"] and max_regression < 0.05
        ),
    }
    with open(RUN_ROOT / "e1dynmatch_decision_summary.json", "w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=2)

    print(json.dumps(final_summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
