"""
E1-Improve V3, Task 1 (diagnostic-only): does PPO's raw action distribution
collapse toward "Same" over extended training, explaining why B2's
primary-budget (24,576-step) advantage over B0 vanishes at the extended
(98,304-step) checkpoint (E1_DEVELOPMENT_RUN_REPORT.md Section 6)?

This performs NO training and NO new random draws. It re-reads the existing,
already-frozen-for-this-report per-step training logs at
research/paper_strengthening/results/e1_training_logs/{B0,B2}_seed{S}.csv
(the un-suffixed files are the full 122,880-row logs spanning primary +
extended budget concatenated; primary_budget/*.csv is the first 24,576-row
prefix of the same file, confirmed by exact row-count match: 24576+98304=122880).

It uses the PRE-shield `action` field... actually the logged `action` column
is the FINAL (post-guardrail) action per interview_env.py's CSV writer
(`action` after `apply_canonical_guardrails` in step()). To see the raw
PPO proposal (pre-shield), use `pre_action`, which is written before the
guardrail call. This script reports both, since the collapse hypothesis is
about the POLICY's raw behavior, not the shielded output.

Hypothesis (predeclared before running): if the raw PPO policy is collapsing
toward a degenerate "Same"-heavy strategy over training, then the proportion
of pre_action==1 (Same) among steps in the LATE part of the extended run
(the 98,304-step tail, i.e. steps 24,577-122,880) should be measurably higher
than in the primary-budget window (steps 1-24,576), for B2 specifically
(the arm whose advantage regresses), with B0 (whose MAE is already poor at
both budgets - not "regressing", just uniformly worse) as a control that is
not expected to show the same late-training shift pattern (since it isn't
the arm exhibiting recovery-then-collapse).

Decision rule (predeclared): a >=5 percentage-point rise in pre_action==1
proportion (Same) from the primary window to the extended-tail window, for
B2, consistent across a majority (>=3/5) of seeds, is treated as directional
support for the mode-collapse hypothesis. Anything smaller, or a pattern
also present in B0's control, is treated as non-support -- in which case the
"single correctly-timed Harder action" explanation in E1_DEVELOPMENT_RUN_REPORT
(a much narrower, sparser effect than a broad distributional collapse) remains
the operative one and this diagnostic does not, by itself, motivate a new
training intervention.
"""
import csv
import json
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LOG_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_training_logs"
OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_action_collapse_diagnostic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEEDS = [42, 123, 456, 789, 999]
CONDITIONS = ["B0", "B2"]
PRIMARY_STEPS = 24576
ACTION_NAMES = {0: "Easier", 1: "Same", 2: "Harder"}


def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def action_props(rows, col):
    n = len(rows)
    if n == 0:
        return {0: None, 1: None, 2: None}
    counts = {0: 0, 1: 0, 2: 0}
    for r in rows:
        counts[int(r[col])] += 1
    return {k: v / n for k, v in counts.items()}


def main():
    results = {}
    for cond in CONDITIONS:
        results[cond] = {}
        for col in ["pre_action", "action"]:
            per_seed = []
            for seed in SEEDS:
                path = LOG_DIR / f"{cond}_seed{seed}.csv"
                rows = load_rows(path)
                total = len(rows)
                expected_total = 122880
                if total != expected_total:
                    raise RuntimeError(
                        f"{path} has {total} rows, expected {expected_total}; "
                        "log layout assumption (primary+extended concatenated) is violated."
                    )
                primary_rows = rows[:PRIMARY_STEPS]
                extended_tail_rows = rows[PRIMARY_STEPS:]
                p_primary = action_props(primary_rows, col)
                p_tail = action_props(extended_tail_rows, col)
                same_delta_pp = (p_tail[1] - p_primary[1]) * 100.0
                per_seed.append({
                    "seed": seed,
                    "primary_props": p_primary,
                    "extended_tail_props": p_tail,
                    "same_delta_pp": round(same_delta_pp, 2),
                })
            same_deltas = [s["same_delta_pp"] for s in per_seed]
            n_seeds_rising_ge5pp = sum(1 for d in same_deltas if d >= 5.0)
            results[cond][col] = {
                "per_seed": per_seed,
                "same_delta_pp_mean": round(statistics.mean(same_deltas), 2),
                "same_delta_pp_sd": round(statistics.pstdev(same_deltas), 2),
                "n_seeds_rising_ge5pp_of_5": n_seeds_rising_ge5pp,
            }

    b2_pre = results["B2"]["pre_action"]
    b2_post = results["B2"]["action"]
    b0_pre = results["B0"]["pre_action"]

    verdict = {
        "hypothesis": "B2 raw policy (pre_action) shifts toward Same in the extended-budget tail",
        "decision_rule": ">=5pp mean rise AND >=3/5 seeds individually >=5pp, for B2 pre_action, "
                          "not similarly present in B0 pre_action control",
        "b2_pre_action_supports_collapse": bool(
            b2_pre["same_delta_pp_mean"] >= 5.0 and b2_pre["n_seeds_rising_ge5pp_of_5"] >= 3
        ),
        "b0_control_also_shows_pattern": bool(
            b0_pre["same_delta_pp_mean"] >= 5.0 and b0_pre["n_seeds_rising_ge5pp_of_5"] >= 3
        ),
    }
    verdict["net_verdict"] = (
        "SUPPORTS mode-collapse hypothesis (B2-specific)"
        if verdict["b2_pre_action_supports_collapse"] and not verdict["b0_control_also_shows_pattern"]
        else "DOES NOT SUPPORT a B2-specific mode-collapse hypothesis under the predeclared rule"
    )

    out = {
        "primary_steps": PRIMARY_STEPS,
        "extended_tail_steps": 122880 - PRIMARY_STEPS,
        "action_names": ACTION_NAMES,
        "results": results,
        "verdict": verdict,
    }
    out_path = OUT_DIR / "action_collapse_diagnostic.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"B2 pre_action Same-share delta (primary -> extended tail): "
          f"mean={b2_pre['same_delta_pp_mean']}pp, seeds>=5pp: {b2_pre['n_seeds_rising_ge5pp_of_5']}/5")
    print(f"B2 post-shield action Same-share delta: mean={b2_post['same_delta_pp_mean']}pp, "
          f"seeds>=5pp: {b2_post['n_seeds_rising_ge5pp_of_5']}/5")
    print(f"B0 control pre_action Same-share delta: mean={b0_pre['same_delta_pp_mean']}pp, "
          f"seeds>=5pp: {b0_pre['n_seeds_rising_ge5pp_of_5']}/5")
    print(f"VERDICT: {verdict['net_verdict']}")
    print(f"Full output: {out_path}")


if __name__ == "__main__":
    main()
