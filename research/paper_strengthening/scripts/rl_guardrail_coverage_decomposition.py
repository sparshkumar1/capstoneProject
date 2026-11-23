"""
Read-only diagnostic reanalysis of the FROZEN X3-0c replay artifacts
(research/analysis/phase1/x3_0/x3_0c_replay_turn_log.csv), which is itself a
gated (G-REPRO passed), reproducible replay of the frozen Paper-3 study code
(research/scripts/execute_paper3_study.py) on the frozen checkpoints
(research/experiments/paper3/checkpoints/*). Nothing here re-runs any
simulation, calls any model, or generates new data: it only re-aggregates and
re-derives quantities from numbers already stored in that frozen CSV, plus two
pure, deterministic functions imported unmodified from the live code
(rl/guardrails.apply_canonical_guardrails, rl/env/interview_env.py's
InterviewEnv.oracle_action_from_obs).

IMPORTANT SCHEMA FACT, verified by reading research/scripts/execute_paper3_study.py
(run_session_trajectory): the frozen EVALUATION script does NOT use the
"oracle" concept at all -- it only computes raw_action (PPO/Heuristic/Fixed's
proposal) -> apply_canonical_guardrails -> final_action. oracle_action_from_obs
exists only in rl/env/interview_env.py, the TRAINING environment, where it
shapes PPO's reward (decision_component). This script recomputes what that
training-time oracle *would have* recommended at each of the already-visited,
already-recorded states in the frozen evaluation replay -- a deterministic
function application to frozen numbers, not a new simulation -- specifically
to test whether the reward's oracle-imitation term plausibly explains the
guardrail layer's dominance, per SYSTEM_IMPROVEMENT_PLAN.md Item D.

State reconstruction, verified against execute_paper3_study.py lines 337-364:
  - avg_perf(turn t) = mean of this session's own perf values for turns
    [max(1, t-4) .. t] (rolling mean of the last <=5 perf values, INCLUDING
    the current turn -- NOT lagged).
  - progress(turn t) = t / 10 (dim4_mode="aligned_progress", used for every
    condition in the x3_0c replay).
  - normalized difficulty = difficulty_before / 5.0.
  - The guardrail/oracle decision for the row logged at "turn t" is computed
    from THIS SAME turn's own (perf, avg_perf, conf, hes, progress,
    difficulty_before) -- confirmed directly from the frozen script, which
    computes raw_obs and calls the policy/guardrails in the same loop
    iteration as the candidate's answer, with no one-turn lag.

Outputs (written under research/paper_strengthening/results/, a permitted,
non-frozen area; the source CSV and all files under research/experiments/
and research/analysis/phase1/x3_0/ are read-only in this script):
  - rl_guardrail_coverage_decomposition.json  (all numeric findings)
  - rl_guardrail_coverage_decomposition.md    (the human-readable report)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from rl.guardrails import apply_canonical_guardrails, ACTION_NAMES  # noqa: E402

# oracle_action_from_obs is a @staticmethod on InterviewEnv; importing the class
# requires gymnasium (already a project dependency) but instantiates nothing.
from rl.env.interview_env import InterviewEnv  # noqa: E402

TURN_LOG = REPO / "research" / "analysis" / "phase1" / "x3_0" / "x3_0c_replay_turn_log.csv"
SUMMARY_CSV = REPO / "research" / "analysis" / "phase1" / "x3_0" / "x3_0c_replay_summary.csv"
OUT_DIR = REPO / "research" / "paper_strengthening" / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ACTION_NAME_TO_INT = {v: k for k, v in ACTION_NAMES.items()}


def load_turns():
    df = pd.read_csv(TURN_LOG)
    assert len(df) == 3500, f"expected 3500 turn rows, got {len(df)}"
    return df


def reconstruct_state_and_oracle(df: pd.DataFrame) -> pd.DataFrame:
    """Adds avg_perf, progress, diff_norm, oracle_action, oracle_action_name,
    and a from-scratch recomputation of the guardrail decision (as a fidelity
    check against the stored final_action/guardrail_id columns)."""
    df = df.sort_values(["condition", "training_seed", "persona", "eval_seed", "turn"]).reset_index(drop=True)
    out_rows = []
    group_cols = ["condition", "training_seed", "persona", "eval_seed"]
    for _, g in df.groupby(group_cols, sort=False):
        g = g.sort_values("turn")
        perf_hist = []
        for _, row in g.iterrows():
            perf_hist.append(float(row["perf"]))
            avg_perf = float(np.mean(perf_hist[-5:]))
            progress = float(row["turn"]) / 10.0
            diff_norm = float(row["difficulty_before"]) / 5.0
            conf = float(row["conf"])
            hes = float(row["hes"])
            perf = float(row["perf"])

            obs = [perf, avg_perf, conf, hes, progress, diff_norm]
            oracle_act = InterviewEnv.oracle_action_from_obs(obs)

            raw_act_int = ACTION_NAME_TO_INT[row["raw_action"]]
            recomputed_final_act, recomputed_forced, recomputed_gid = apply_canonical_guardrails(
                perf=perf, avg_perf=avg_perf, conf=conf, hes=hes, progress=progress,
                difficulty=diff_norm, proposed_action=raw_act_int,
            )

            rec = row.to_dict()
            rec["avg_perf"] = round(avg_perf, 6)
            rec["progress"] = progress
            rec["diff_norm"] = round(diff_norm, 6)
            rec["oracle_action"] = ACTION_NAMES[oracle_act]
            rec["oracle_matches_final"] = (ACTION_NAMES[oracle_act] == row["final_action"])
            rec["oracle_matches_raw"] = (ACTION_NAMES[oracle_act] == row["raw_action"])
            rec["recomputed_final_action"] = ACTION_NAMES[recomputed_final_act]
            rec["recomputed_guardrail_id"] = recomputed_gid
            rec["recomputed_forced"] = recomputed_forced
            rec["recompute_matches_stored_final"] = (rec["recomputed_final_action"] == row["final_action"])
            rec["recompute_matches_stored_gid"] = (recomputed_gid == row["guardrail_id"])
            out_rows.append(rec)
    return pd.DataFrame(out_rows)


G_CONDITIONS = {
    # name -> function(perf, avg_perf, conf, hes, diff_norm) -> bool
    # transcribed verbatim from rl/guardrails.py's condition checks, used only
    # to count *overlap* (how many rules' PRECONDITIONS hold simultaneously,
    # even though apply_canonical_guardrails only ever fires the first match).
    "g4_stuck_easier": lambda p, ap, c, h, d: (p < 0.30 and h > 0.60),
    "g1_overload_protection": lambda p, ap, c, h, d: (p < 0.30 and 0.4 <= d <= 0.7),
    "g2_anxiety_stabilizer_same": lambda p, ap, c, h, d: (c < 0.30 and h > 0.70 and p < 0.80),
    "g5_partial_same": lambda p, ap, c, h, d: (0.40 < p < 0.65 and ap < 0.60),
    # g6 needs the proposed action's gap term (perf - diff_norm) and a
    # nervous-expert exclusion identical across raw actions; included for
    # completeness though it never fires in this persona set (see findings).
}


def count_precondition_overlap(df: pd.DataFrame) -> dict:
    counts = Counter()
    total = 0
    for _, row in df.iterrows():
        total += 1
        hits = [name for name, fn in G_CONDITIONS.items()
                if fn(row["perf"], row["avg_perf"], row["conf"], row["hes"], row["diff_norm"])]
        counts[len(hits)] += 1
        if len(hits) >= 2:
            counts[f"combo:{'+'.join(sorted(hits))}"] += 1
    return {"total_turns": total, "by_num_preconditions_true": {k: v for k, v in counts.items() if isinstance(k, int)},
            "overlap_combinations": {k: v for k, v in counts.items() if isinstance(k, str)}}


def integrity_check(df: pd.DataFrame) -> dict:
    """Reproduce the already-published aggregate numbers directly from the
    turn-level rows, independent of the stored summary CSV, as a data-integrity
    check requested in step 2."""
    ppo_g = df[df["condition"] == "PPO+G"]
    checks = {}
    per_seed_activations = ppo_g.groupby("training_seed")["activation"].sum().to_dict()
    checks["per_seed_rule_activations"] = {str(k): int(v) for k, v in per_seed_activations.items()}
    checks["total_rule_activations_5_seeds"] = int(ppo_g["activation"].sum())
    checks["total_overrides_5_seeds"] = int(ppo_g["override"].sum())
    checks["total_unchanged_activations_5_seeds"] = int(ppo_g["activation"].sum() - ppo_g["override"].sum())
    sessions_with_override = ppo_g.groupby(["training_seed", "persona", "eval_seed"])["override"].any()
    checks["sessions_with_at_least_one_override"] = int(sessions_with_override.sum())
    checks["total_sessions_ppo_plus_g"] = int(sessions_with_override.shape[0])

    against_reference = {
        "total_rule_activations_5_seeds": (checks["total_rule_activations_5_seeds"], 563),
        "total_overrides_5_seeds": (checks["total_overrides_5_seeds"], 99),
        "total_unchanged_activations_5_seeds": (checks["total_unchanged_activations_5_seeds"], 464),
        "sessions_with_at_least_one_override": (checks["sessions_with_at_least_one_override"], 41),
    }
    checks["matches_published_X3_0c_report"] = {k: (v[0] == v[1]) for k, v in against_reference.items()}
    checks["published_reference_values"] = {k: v[1] for k, v in against_reference.items()}
    return checks


def main():
    df_raw = load_turns()
    df = reconstruct_state_and_oracle(df_raw)

    findings = {}

    findings["schema_verification"] = {
        "turn_log_rows": int(len(df_raw)),
        "distinct_condition_seed_groups": int(df_raw.groupby(["condition", "training_seed"]).ngroups),
        "distinct_sessions_all_conditions": int(df_raw.groupby(["condition", "training_seed", "persona", "eval_seed"]).ngroups),
        "personas": sorted(df_raw["persona"].unique().tolist()),
        "eval_seeds": sorted(df_raw["eval_seed"].unique().tolist()),
        "training_seeds_ppo": sorted([s for s in df_raw["training_seed"].unique() if s != "-"]),
        "turns_per_session": int(df_raw.groupby(["condition", "training_seed", "persona", "eval_seed"]).size().max()),
        "note_no_stored_oracle_field": (
            "The frozen evaluation script (execute_paper3_study.run_session_trajectory) computes "
            "raw_action -> apply_canonical_guardrails -> final_action only. It does not compute or "
            "log an 'oracle' action; oracle_action_from_obs exists only in rl/env/interview_env.py, "
            "the TRAINING environment, where it shapes PPO's reward. All oracle_action values below "
            "are recomputed here (this script) from InterviewEnv.oracle_action_from_obs applied to "
            "the ALREADY-STORED per-turn state, not read from any stored oracle column."
        ),
    }

    # Guardrails were only actually invoked by execute_paper3_study.py for the
    # "PPO+G" and "Constant-Same+G" conditions (guardrails_enabled=True); for
    # "Fixed", "Heuristic", "PPO raw" and "Constant-Same raw" the original
    # generation never called apply_canonical_guardrails at all (guardrail_id
    # is stored as "none" by construction), so recomputing it on those rows
    # is not a meaningful fidelity check and is excluded here.
    guarded_conditions = df[df["condition"].isin(["PPO+G", "Constant-Same+G"])]
    fidelity_mismatches = int((~guarded_conditions["recompute_matches_stored_final"]).sum())
    fidelity_gid_mismatches = int((~guarded_conditions["recompute_matches_stored_gid"]).sum())
    findings["guardrail_recomputation_fidelity_check"] = {
        "rows_checked": int(len(guarded_conditions)),
        "scope": "PPO+G and Constant-Same+G rows only (the only conditions where the frozen script actually applied guardrails)",
        "final_action_mismatches": fidelity_mismatches,
        "guardrail_id_mismatches": fidelity_gid_mismatches,
        "interpretation": (
            "Recomputing apply_canonical_guardrails() from this script's own reconstructed avg_perf/"
            "progress/diff_norm and comparing to the stored final_action/guardrail_id in the frozen "
            "CSV, restricted to the two conditions where guardrails were actually applied during the "
            "original run. Zero mismatches means the state-reconstruction (avg_perf rolling window, "
            "progress, difficulty normalization) used throughout this analysis is verified correct "
            "against the frozen evaluation code's own recorded output, not merely assumed."
        ),
    }

    findings["integrity_check_vs_published_X3_0c_report"] = integrity_check(df)

    ppo_g = df[df["condition"] == "PPO+G"].copy()
    ppo_raw = df[df["condition"] == "PPO raw"].copy()

    findings["total_sessions_and_turns"] = {
        "PPO+G": {"sessions": int(ppo_g.groupby(["training_seed", "persona", "eval_seed"]).ngroups),
                  "turns": int(len(ppo_g))},
        "PPO_raw": {"sessions": int(ppo_raw.groupby(["training_seed", "persona", "eval_seed"]).ngroups),
                    "turns": int(len(ppo_raw))},
        "all_conditions_combined": {"sessions": int(df.groupby(["condition", "training_seed", "persona", "eval_seed"]).ngroups),
                                     "turns": int(len(df))},
    }

    cov = ppo_g["activation"].mean()
    by_rule = ppo_g[ppo_g["activation"]]["guardrail_id"].value_counts().to_dict()
    override_by_rule = ppo_g[ppo_g["activation"]].groupby("guardrail_id")["override"].agg(["sum", "count", "mean"])
    findings["guardrail_coverage_PPO_plus_G"] = {
        "turns": int(len(ppo_g)),
        "coverage_overall": round(float(cov), 4),
        "activations_by_rule": {k: int(v) for k, v in by_rule.items()},
        "override_rate_by_rule": {k: {"overrides": int(r["sum"]), "activations": int(r["count"]), "override_share": round(float(r["mean"]), 4)}
                                   for k, r in override_by_rule.iterrows()},
        "overall_override_rate_given_activation": round(float(ppo_g[ppo_g["activation"]]["override"].mean()), 4),
        "overall_override_rate_of_all_turns": round(float(ppo_g["override"].mean()), 4),
    }

    findings["precondition_overlap_PPO_plus_G"] = count_precondition_overlap(ppo_g)

    free = ppo_g[~ppo_g["activation"]].copy()
    oracle_dist_free = free["oracle_action"].value_counts(normalize=False).to_dict()
    oracle_dist_free_pct = free["oracle_action"].value_counts(normalize=True).round(4).to_dict()
    findings["guardrail_free_states_PPO_plus_G"] = {
        "turns": int(len(free)),
        "share_of_all_PPO_plus_G_turns": round(float(len(free) / len(ppo_g)), 4),
        "oracle_action_distribution_counts": {k: int(v) for k, v in oracle_dist_free.items()},
        "oracle_action_distribution_share": {k: float(v) for k, v in oracle_dist_free_pct.items()},
        "oracle_nontrivial_share": round(float((free["oracle_action"] != "Same").mean()), 4),
        "ppo_raw_action_nonSame_share_in_these_states": round(float((free["raw_action"] != "Same").mean()), 4),
        "ppo_raw_action_distribution_in_these_states": {k: int(v) for k, v in free["raw_action"].value_counts().items()},
        "oracle_matches_ppo_raw_share_in_these_states": round(float(free["oracle_matches_raw"].mean()), 4),
    }

    confusion = pd.crosstab(free["oracle_action"], free["raw_action"])
    findings["oracle_vs_ppo_raw_confusion_in_free_states"] = {
        str(idx): {str(c): int(v) for c, v in row.items()} for idx, row in confusion.iterrows()
    }
    disagreement_rows = free[free["oracle_action"] != free["raw_action"]]
    findings["actionable_disagreement_in_free_states"] = {
        "turns_where_oracle_and_ppo_raw_disagree": int(len(disagreement_rows)),
        "as_share_of_free_turns": round(float(len(disagreement_rows) / len(free)), 4),
        "as_share_of_all_PPO_plus_G_turns": round(float(len(disagreement_rows) / len(ppo_g)), 4),
        "breakdown_oracle_wants_vs_ppo_proposes": {
            f"oracle={o}_ppo={p}": int(c) for (o, p), c in disagreement_rows.groupby(["oracle_action", "raw_action"]).size().items()
        },
        "caveat": (
            "This is the count of turns where, on the ALREADY-REALIZED PPO+G trajectory, the reward's "
            "oracle target disagreed with what PPO actually proposed and no guardrail was present to "
            "mask the difference. It is the closest available proxy for 'turns where PPO's own choice, "
            "not a guardrail, drove a departure from the reward's stated target' -- it is NOT a bound on "
            "achievable MAE improvement (agreement with the oracle is not the evaluation metric, and the "
            "oracle itself is an unvalidated hand-authored heuristic, not a proven-optimal target), and it "
            "is NOT policy-invariant (a different policy would visit a different, action-dependent "
            "distribution of states, per SimulatedCandidate's difficulty-dependent performance model)."
        ),
    }

    free_raw = ppo_raw[~ppo_raw["activation"]].copy() if "activation" in ppo_raw.columns else ppo_raw.copy()
    # PPO raw rows have activation always False (guardrails disabled in that condition) -- report separately.
    findings["ppo_raw_condition_note"] = (
        "The 'PPO raw' condition runs with guardrails_enabled=False throughout, so its 'activation' "
        "column is always False by construction -- it is not a second guardrail-free sample of the "
        "same states as PPO+G, because disabling guardrails changes which difficulty each subsequent "
        "question is posed at, and therefore the candidate's subsequent performance (SimulatedCandidate's "
        "perf is a sigmoid of skill-minus-difficulty). It is reported only for its own raw-action "
        "distribution and MAE, not merged with PPO+G's guardrail-free subset."
    )
    findings["ppo_raw_own_action_distribution"] = {k: int(v) for k, v in ppo_raw["raw_action"].value_counts().items()}

    per_seed = ppo_g.groupby("training_seed").agg(
        turns=("activation", "size"), coverage=("activation", "mean"),
        override_rate=("override", "mean"),
    )
    per_seed["free_share"] = 1.0 - per_seed["coverage"]
    per_persona = ppo_g.groupby("persona").agg(
        turns=("activation", "size"), coverage=("activation", "mean"),
        override_rate=("override", "mean"),
    )
    per_persona["free_share"] = 1.0 - per_persona["coverage"]
    oracle_nontrivial_by_persona = free.groupby("persona")["oracle_action"].apply(lambda s: float((s != "Same").mean()))
    findings["variation_across_training_seeds"] = {
        str(k): {"turns": int(r["turns"]), "coverage": round(float(r["coverage"]), 4),
                  "free_share": round(float(r["free_share"]), 4), "override_rate": round(float(r["override_rate"]), 4)}
        for k, r in per_seed.iterrows()
    }
    findings["variation_across_personas"] = {
        str(k): {"turns": int(r["turns"]), "coverage": round(float(r["coverage"]), 4),
                  "free_share": round(float(r["free_share"]), 4), "override_rate": round(float(r["override_rate"]), 4),
                  "oracle_nontrivial_share_in_free_states": round(float(oracle_nontrivial_by_persona.get(k, float("nan"))), 4)
                  if k in oracle_nontrivial_by_persona.index else None}
        for k, r in per_persona.iterrows()
    }

    with open(OUT_DIR / "rl_guardrail_coverage_decomposition.json", "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, default=str)

    print(json.dumps(findings, indent=2, default=str))


if __name__ == "__main__":
    main()
