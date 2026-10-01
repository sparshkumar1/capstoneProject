"""
Read-only audit of an UNVERIFIED, non-frozen, gitignored local log file
(rl/env/training_logs/interview_data.csv) that happens to match the exact
per-step CSV schema written by rl/env/interview_env.py's InterviewEnv.step()
during PPO training (oracle_action, guardrail_id, decision/outcome/shaping
reward components).

PROVENANCE CAVEAT (see the accompanying report, section 2, for full detail):
this file is NOT tracked in git, IS explicitly gitignored (`training_logs/` in
.gitignore), carries no seed identifier column, and its row count (295,291)
is ~2.4x the combined ~122,880 timesteps the frozen training_meta.json files
record for the actual 5 checkpointed seeds (42/123/456/789/999) -- meaning it
almost certainly accumulated rows from MORE runs than just the 5 that were
kept (repeated/exploratory invocations across sessions, since the logger
appends and only writes one header the first time the file is created). It
CANNOT be attributed to the specific frozen checkpoints. It CAN be read as
evidence of how this exact reward/guardrail/oracle code (rl/env/interview_env.py,
rl/guardrails.py) behaves when actually executed with the training-time
candidate configuration -- which X3_0B_STATIC_CODE_NOTE.md's finding N1
(static code reading, no execution) already establishes as the ONLY candidate
configuration ever used for training: skill=0.6, persona="normal" -- confirmed
directly in this file (its persona and skill columns take exactly one value
each, "normal" and 0.6, across all 295,291 rows).

This script performs ONLY read-only aggregation on the existing file. It does
not modify, move, or delete it, and does not execute any simulation.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
LOG = REPO / "rl" / "env" / "training_logs" / "interview_data.csv"
OUT_DIR = REPO / "research" / "paper_strengthening" / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ACTION_NAMES = {0: "Easier", 1: "Same", 2: "Harder"}


def main():
    df = pd.read_csv(LOG)
    n = len(df)

    findings = {}
    findings["provenance"] = {
        "path": str(LOG.relative_to(REPO)),
        "git_tracked": False,
        "gitignored": True,
        "total_rows": int(n),
        "unique_personas": sorted(df["persona"].unique().tolist()),
        "unique_skills": sorted(df["skill"].unique().tolist()),
        "episodes_inferred_from_step_resets": int((df["step"] == 1).sum()),
        "combined_5_seed_frozen_training_timesteps_for_comparison": 5 * 24576,
        "note": (
            "Row count far exceeds the 5 frozen seeds' combined recorded training timesteps -- "
            "this log almost certainly spans more runs than the 5 that were kept as final "
            "checkpoints. It cannot be attributed to a specific seed. It is treated here purely "
            "as evidence of code behavior under the one training candidate configuration "
            "(skill=0.6, persona='normal') that X3_0B_STATIC_CODE_NOTE.md (finding N1, static "
            "code reading) already established as the sole training distribution."
        ),
        "header_bug_note": (
            "The CSV header names column 9 'time_norm', but InterviewEnv.step()'s writer actually "
            "puts the 'progress' variable (current_step / max_steps) there, not a "
            "response-time-normalized value. Verified: this column's observed values are exact "
            "multiples of 1/15 (0.0667, 0.1333, ..., 1.0), consistent with max_steps=15 and "
            "progress = step/15, not with any time-based quantity. This is a label/content "
            "mismatch in the frozen logger itself, harmless to training (the real progress "
            "variable is used correctly inside step()), but relevant to anyone reading this "
            "column by its header name."
        ),
    }

    findings["oracle_action_distribution"] = {
        ACTION_NAMES[k]: int(v) for k, v in df["oracle_action"].value_counts().items()
    }
    findings["oracle_action_distribution_share"] = {
        ACTION_NAMES[k]: round(float(v), 4) for k, v in df["oracle_action"].value_counts(normalize=True).items()
    }
    findings["ppo_raw_proposal_distribution"] = {
        ACTION_NAMES[k]: int(v) for k, v in df["pre_action"].value_counts().items()
    }
    findings["final_action_distribution"] = {
        ACTION_NAMES[k]: int(v) for k, v in df["action"].value_counts().items()
    }

    findings["guardrail_activation_counts"] = df["guardrail_id"].value_counts().to_dict()
    findings["guardrail_coverage_overall"] = round(float((df["guardrail_id"] != "none").mean()), 4)
    findings["forced_action_rate_overall"] = round(float(df["forced_action"].mean()), 4)

    g6 = df[df["guardrail_id"] == "g6_strong_harder"]
    findings["g6_strong_harder"] = {
        "activations": int(len(g6)),
        "share_of_all_rows": round(float(len(g6) / n), 4),
        "forced_action_rate_within_g6": round(float(g6["forced_action"].mean()), 4) if len(g6) else None,
        "note": "g6 fired 0 times in the 5-persona P3 evaluation replay (see the companion guardrail-coverage report); it fires here at a non-trivial rate under the training-matched (skill=0.6, normal) candidate.",
    }

    # Confusion: oracle_action vs pre_action (PPO's raw proposal), overall
    confusion_raw = pd.crosstab(df["oracle_action"], df["pre_action"])
    confusion_raw.index = [ACTION_NAMES[i] for i in confusion_raw.index]
    confusion_raw.columns = [ACTION_NAMES[c] for c in confusion_raw.columns]
    findings["oracle_vs_ppo_raw_confusion_ALL_ROWS"] = confusion_raw.to_dict()

    # Reward received specifically when PPO's raw/final action correctly matches oracle==Harder
    correct_harder = df[(df["oracle_action"] == 2) & (df["action"] == 2)]
    oracle_harder_all = df[df["oracle_action"] == 2]
    oracle_harder_missed = df[(df["oracle_action"] == 2) & (df["action"] != 2)]
    findings["harder_signal_quality"] = {
        "rows_where_oracle_wants_harder": int(len(oracle_harder_all)),
        "of_those_final_action_is_harder_too": int(len(correct_harder)),
        "of_those_final_action_is_NOT_harder": int(len(oracle_harder_missed)),
        "share_correctly_resolved_to_harder": round(float(len(correct_harder) / len(oracle_harder_all)), 4) if len(oracle_harder_all) else None,
        "mean_reward_when_oracle_wants_harder_and_final_is_harder": round(float(correct_harder["reward"].mean()), 4) if len(correct_harder) else None,
        "mean_decision_component_when_oracle_wants_harder_and_final_is_harder": round(float(correct_harder["decision_component"].mean()), 4) if len(correct_harder) else None,
        "mean_reward_when_oracle_wants_harder_but_final_is_NOT_harder": round(float(oracle_harder_missed["reward"].mean()), 4) if len(oracle_harder_missed) else None,
        "overall_mean_reward_all_rows": round(float(df["reward"].mean()), 4),
        "guardrail_id_breakdown_when_oracle_wants_harder_but_missed": oracle_harder_missed["guardrail_id"].value_counts().to_dict(),
    }

    # "forced_action" in this log is True whenever ANY guardrail matches (see
    # rl/env/interview_env.py::_apply_guardrails -- every branch returns
    # forced=True), NOT specifically when it changes the action. The real
    # action-changing indicator, comparable to the X3-0c evaluation replay's
    # "override" column, is pre_action != action.
    df["changed"] = df["pre_action"] != df["action"]
    findings["forced_action_column_semantics_note"] = (
        "forced_action==True whenever guardrail_id != 'none' (i.e. it means 'a guardrail rule "
        "matched', not 'the guardrail changed the action') -- confirmed: forced_action_rate_overall "
        "equals guardrail_coverage_overall exactly (0.6129 == 0.6129). The action-changing rate used "
        "below is the separately-computed pre_action != action indicator, matching the 'override' "
        "definition used in the companion guardrail-coverage-decomposition report."
    )
    findings["action_changed_rate_overall"] = round(float(df["changed"].mean()), 4)
    findings["action_changed_rate_given_any_guardrail_fired"] = round(float(df[df["guardrail_id"] != "none"]["changed"].mean()), 4)
    by_rule_change = df[df["guardrail_id"] != "none"].groupby("guardrail_id")["changed"].agg(["sum", "count", "mean"])
    findings["action_changed_rate_by_rule"] = {
        idx: {"changed": int(r["sum"]), "activations": int(r["count"]), "changed_share": round(float(r["mean"]), 4)}
        for idx, r in by_rule_change.iterrows()
    }

    g6 = df[df["guardrail_id"] == "g6_strong_harder"]
    correct_harder_proposed = df[(df["oracle_action"] == 2) & (df["pre_action"] == 2)]
    findings["g6_and_correct_harder_proposals"] = {
        "g6_total_activations": int(len(g6)),
        "g6_action_changed_count": int(g6["changed"].sum()),
        "g6_pre_action_distribution": {ACTION_NAMES[k]: int(v) for k, v in g6["pre_action"].value_counts().items()},
        "rows_where_oracle_wants_harder_and_ppo_raw_already_proposes_harder": int(len(correct_harder_proposed)),
        "of_those_any_guardrail_changed_it_away_from_harder": int((correct_harder_proposed["changed"] & (correct_harder_proposed["action"] != 2)).sum()),
        "of_those_g6_fired_redundantly_no_change_needed": int(((correct_harder_proposed["guardrail_id"] == "g6_strong_harder") & (~correct_harder_proposed["changed"])).sum()),
        "interpretation": (
            "No guardrail ever blocks or changes away from a correct Harder proposal in this log "
            "(0 of 34,535 such rows have action != pre_action). g6 fires concurrently with an "
            "already-correct Harder proposal in a large share of cases (redundant reconfirmation, "
            "the same pattern g5 showed at evaluation time: 0% override rate), and separately forces "
            "Harder in the ~37% of its activations where PPO's raw proposal was NOT already Harder "
            "(a genuine correction toward the oracle's target, not a block)."
        ),
    }

    with open(OUT_DIR / "ppo_training_log_audit.json", "w", encoding="utf-8") as f:
        import json
        json.dump(findings, f, indent=2, default=str)

    print(pd_json := __import__("json").dumps(findings, indent=2, default=str))


if __name__ == "__main__":
    main()
