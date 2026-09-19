"""X3-0a - stored-file-only accounting for the frozen Paper 3 study (Phase 1C).

Reads only frozen CSV files. Executes no project code, loads no model, uses no RNG.
Definitions: X3_0_PRERUN_NOTE.md. Outputs: research/analysis/phase1/x3_0/ (new files only).
Run: python -B research/analysis/phase1/x3_0/x3_0a_stored.py
"""
import csv
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "tools"))
import run_manifest as rm  # noqa: E402

OUT = Path(__file__).resolve().parent
R3 = REPO / "research" / "results" / "paper3"
NOTE = OUT / "X3_0_PRERUN_NOTE.md"


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def wcsv(name, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return rm.write_new(OUT / name, buf.getvalue())


def main():
    files = ["paper3_seed_results.csv", "paper3_summary_results.csv", "paper3_baseline_results.csv",
             "paper3_ablation_results.csv", "paper3_guardrail_results.csv", "paper3_sensitivity_results.csv",
             "paper3_convergence_results.csv", "paper3_training_curves.csv"]
    m = rm.Manifest("X3-0a", OUT, __file__, note_path=NOTE, seeds={"none": "deterministic; no RNG"})
    m.add_inputs([R3 / f for f in files])
    seed = rd(R3 / "paper3_seed_results.csv")
    summ = rd(R3 / "paper3_summary_results.csv")
    base = rd(R3 / "paper3_baseline_results.csv")
    abl = rd(R3 / "paper3_ablation_results.csv")
    grd = rd(R3 / "paper3_guardrail_results.csv")
    sens = rd(R3 / "paper3_sensitivity_results.csv")
    conv = rd(R3 / "paper3_convergence_results.csv")
    facts = {}

    # ---- 1. per-seed table and totals ----
    seeds = [int(r["training_seed"]) for r in seed]
    act = [int(r["guardrail_interventions"]) for r in seed]
    bnd = [int(r["constraint_violations"]) for r in seed]
    mae = [float(r["target_tracking_error"]) for r in seed]
    vol = [float(r["volatility"]) for r in seed]
    osc = [float(r["oscillation_rate"]) for r in seed]
    assert seeds == [42, 123, 456, 789, 999]
    assert act == [122, 101, 115, 120, 105] and sum(act) == 563
    assert bnd == [26, 71, 41, 33, 61] and sum(bnd) == 232
    seed_rows = [{"training_seed": s, "rule_activations_guarded": a, "attempted_boundary_actions_guarded": b,
                  "tracking_mae": e, "volatility": v, "oscillation": o}
                  for s, a, b, e, v, o in zip(seeds, act, bnd, mae, vol, osc)]
    seed_rows.append({"training_seed": "TOTAL/MEAN", "rule_activations_guarded": sum(act),
                      "attempted_boundary_actions_guarded": sum(bnd), "tracking_mae": round(float(np.mean(mae)), 4),
                      "volatility": round(float(np.mean(vol)), 4), "oscillation": round(float(np.mean(osc)), 4)})
    facts["totals"] = {"activations": sum(act), "attempted_boundary_guarded": sum(bnd),
                       "sessions_per_seed": 25, "turns_per_seed": 250,
                       "activation_rate_per_turn_5seed": round(sum(act) / 1250, 4)}

    # ---- 2. spread conventions ----
    def sd(x, d):
        return round(float(np.std(x, ddof=d)), 4)
    spread = [
        {"metric": "tracking MAE (5 seeds)", "mean": round(float(np.mean(mae)), 4), "sd_ddof0": sd(mae, 0), "sd_ddof1": sd(mae, 1),
         "stored_string": [r for r in summ if "5-Seed" in r["condition"]][0]["mean_tracking_error"]},
        {"metric": "volatility (5 seeds)", "mean": round(float(np.mean(vol)), 4), "sd_ddof0": sd(vol, 0), "sd_ddof1": sd(vol, 1),
         "stored_string": [r for r in summ if "5-Seed" in r["condition"]][0]["volatility"]},
        {"metric": "oscillation (5 seeds)", "mean": round(float(np.mean(osc)), 4), "sd_ddof0": sd(osc, 0), "sd_ddof1": sd(osc, 1),
         "stored_string": [r for r in summ if "5-Seed" in r["condition"]][0]["oscillation_rate"]},
    ]
    assert abs(sd(mae, 1) - 0.006) < 0.0006 and abs(sd(vol, 0) - 0.068) < 0.0006 and abs(sd(vol, 1) - 0.076) < 0.0006
    facts["spread"] = {"mae_sd_ddof1": sd(mae, 1), "vol_sd_ddof0": sd(vol, 0), "vol_sd_ddof1": sd(vol, 1)}

    # ---- 3. ablation provenance (E-10, E-11) ----
    mm = [r for r in base if r["condition"] == "PPO+Guardrails (Historical Mismatch)"][0]
    mmr = [r for r in base if r["condition"] == "PPO Raw (Historical Mismatch)"][0]
    s123g = [r for r in base if r["condition"] == "PPO+Guardrails (Seed 123)"][0]
    five = {"mae": round(float(np.mean(mae)), 3), "vol": round(float(np.mean(vol)), 3), "osc": round(float(np.mean(osc)), 3),
            "act": sum(act), "bnd": sum(bnd)}
    prov = []
    for r in abl:
        if r["ablation_category"] != "Safety Shield (Guardrails)":
            continue
        for fld, key5, mmkey in (("target_tracking_error", "mae", None), ("volatility", "vol", None),
                                 ("oscillation_rate", "osc", "oscillation"), ("guardrail_interventions", "act", "total_guardrail_interventions"),
                                 ("constraint_violations", "bnd", "total_constraint_violations")):
            v = float(r[fld])
            match5 = "PPO + Guardrails" in r["configuration"] and abs(v - five[key5]) < 0.0015
            src = []
            for br in base:
                for bf in ("target_tracking_error", "volatility", "oscillation_rate", "total_guardrail_interventions", "total_constraint_violations"):
                    if abs(float(br[bf]) - v) < 1e-9 and (v != 0.0):
                        src.append(f"{br['condition']}:{bf}")
            prov.append({"ablation_row": r["configuration"], "field": fld, "stored_value": v,
                         "five_seed_value_from_seed_results": (five[key5] if "PPO + Guardrails" in r["configuration"] else "n/a (raw five-seed not stored)"),
                         "equals_five_seed_value": match5 if "PPO + Guardrails" in r["configuration"] else "n/a",
                         "equals_stored_value_of": ";".join(src) if src else "none"})
    g5 = [r for r in prov if r["ablation_row"].startswith("PPO + Guardrails")]
    assert [r["equals_five_seed_value"] for r in g5] == [True, True, False, False, False]
    d4 = [r for r in abl if r["ablation_category"].startswith("Dimension 4")]
    d4_equal = len({(r["target_tracking_error"], r["volatility"], r["oscillation_rate"], r["guardrail_interventions"],
                     r["constraint_violations"]) for r in d4 if r["configuration"] != "historical_mismatch"}) == 1
    assert d4_equal
    facts["ablation"] = {"guarded_row_fields_matching_five_seed": ["target_tracking_error", "volatility"],
                         "guarded_row_fields_not_matching": ["oscillation_rate", "guardrail_interventions", "constraint_violations"],
                         "dim4_three_rows_identical": d4_equal}

    # ---- 4. seed-123 and mismatch guardrail file: activations vs overrides ----
    G = defaultdict(list)
    for r in grd:
        G[r["condition"]].append(r)
    acc = []
    for cond, rows in G.items():
        n_act = len(rows)
        over = [r for r in rows if r["raw_action"] != r["final_action"]]
        acc.append({"condition": cond, "breakdown": "TOTAL", "key": "-", "activations": n_act, "overrides": len(over),
                    "unchanged_activations": n_act - len(over), "override_share": round(len(over) / n_act, 4)})
        for dim, keyf in (("rule", lambda r: r["guardrail_id"]), ("persona", lambda r: r["persona"]),
                          ("direction", lambda r: f"{r['raw_action']}->{r['final_action']}")):
            cnt = Counter(keyf(r) for r in rows)
            ovc = Counter(keyf(r) for r in over)
            for k in sorted(cnt):
                if dim == "direction" and ovc.get(k, 0) == 0:
                    continue
                acc.append({"condition": cond, "breakdown": dim, "key": k, "activations": cnt[k], "overrides": ovc.get(k, 0),
                            "unchanged_activations": cnt[k] - ovc.get(k, 0), "override_share": round(ovc.get(k, 0) / cnt[k], 4)})
        sess = {(r["persona"], r["eval_seed"]) for r in rows}
        acc.append({"condition": cond, "breakdown": "sessions", "key": "sessions_with_at_least_one_activation(of 25)",
                    "activations": len(sess), "overrides": len({(r["persona"], r["eval_seed"]) for r in over}),
                    "unchanged_activations": "", "override_share": ""})
    s123 = G["PPO+Guardrails (Seed 123)"]
    assert len(s123) == int(s123g["total_guardrail_interventions"]) == 101
    assert len(G["PPO+Guardrails (Historical Mismatch)"]) == int(mm["total_guardrail_interventions"]) == 112
    o123 = sum(1 for r in s123 if r["raw_action"] != r["final_action"])
    omm = sum(1 for r in G["PPO+Guardrails (Historical Mismatch)"] if r["raw_action"] != r["final_action"])
    facts["guardrail_file"] = {"seed123_activations": len(s123), "seed123_overrides": o123,
                               "mismatch_activations": 112, "mismatch_overrides": omm,
                               "raw_seed123_attempted_boundary_stored": int([r for r in base if r["condition"] == "PPO Raw (Seed 123)"][0]["total_constraint_violations"]),
                               "guarded_seed123_attempted_boundary_stored": int(s123g["total_constraint_violations"]),
                               "raw_mismatch_attempted_boundary_stored": int(mmr["total_constraint_violations"]),
                               "guarded_mismatch_attempted_boundary_stored": int(mm["total_constraint_violations"])}

    # ---- 5. stored sensitivity probes (seed-123 checkpoint; other coords at neutral point) ----
    per = defaultdict(list)
    for r in sens:
        per[r["dimension"]].append(r["action_name"])
    sens_rows = []
    for d, acts in per.items():
        c = Counter(acts)
        sens_rows.append({"dimension": d, "probes": len(acts), "Easier": c.get("Easier", 0), "Same": c.get("Same", 0),
                          "Harder": c.get("Harder", 0), "non_Same_probes": len(acts) - c.get("Same", 0)})
    tot_probe = sum(r["probes"] for r in sens_rows)
    tot_non = sum(r["non_Same_probes"] for r in sens_rows)
    facts["sensitivity"] = {"probes": tot_probe, "non_same": tot_non,
                            "dims_all_same": [r["dimension"] for r in sens_rows if r["non_Same_probes"] == 0]}
    assert tot_probe == 66 and tot_non == 8

    # ---- 6. stored training-time action shares (stochastic training policy) ----
    tr = [{"training_seed": r["training_seed"], "easier": r["final_action_easier_pct"], "same": r["final_action_same_pct"],
           "harder": r["final_action_harder_pct"], "total_timesteps": r["total_timesteps"]} for r in conv]
    facts["training_same_share_range"] = [min(float(r["same"]) for r in tr), max(float(r["same"]) for r in tr)]

    outs = [wcsv("x3_0a_seed_table.csv", seed_rows), wcsv("x3_0a_spread_conventions.csv", spread),
            wcsv("x3_0a_ablation_provenance.csv", prov), wcsv("x3_0a_guardrail_activations_vs_overrides.csv", acc),
            wcsv("x3_0a_sensitivity_probes.csv", sens_rows), wcsv("x3_0a_training_action_shares.csv", tr)]
    outs.append(rm.write_new(OUT / "x3_0a_facts.json", json.dumps(facts, indent=2)))
    f = facts
    rep = f"""# X3-0a report - stored-file-only accounting (frozen Paper 3)

Script-generated from the frozen CSV files (no replay, no RNG). Labels: STORED = value read from a frozen file; RECOMPUTED = computed from stored values here. Definitions: `X3_0_PRERUN_NOTE.md`.

1. **Totals (RECOMPUTED = STORED).** Guarded rule activations {f['totals']['activations']} (122/101/115/120/105); guarded attempted boundary actions {f['totals']['attempted_boundary_guarded']} (26/71/41/33/61). Denominator: 5 seeds x 25 sessions x 10 turns = 1 250 turns; activation rate {f['totals']['activation_rate_per_turn_5seed']:.3f} per turn.
2. **Spread convention.** The stored `0.186 +/- 0.068` is a population SD (ddof=0); the sample SD is {f['spread']['vol_sd_ddof1']}. MAE SD 0.006 is the sample SD ({f['spread']['mae_sd_ddof1']}). State the convention when quoting.
3. **Seed-123 guardrail file (STORED rows).** {f['guardrail_file']['seed123_activations']} rule activations but only {f['guardrail_file']['seed123_overrides']} actually changed the action ({100*f['guardrail_file']['seed123_overrides']/f['guardrail_file']['seed123_activations']:.1f} %); historical-mismatch run: {f['guardrail_file']['mismatch_activations']} activations, {f['guardrail_file']['mismatch_overrides']} overrides. The five-seed override count (99) is NOT recomputable from stored files (only seeds 123 and mismatch stored rows exist) and requires the replay (X3-0c).
4. **Seed-123 attempted boundary actions (STORED).** raw {f['guardrail_file']['raw_seed123_attempted_boundary_stored']}, guarded {f['guardrail_file']['guarded_seed123_attempted_boundary_stored']}: the shield did not reduce attempted boundary actions for this seed (it changes trajectories); "0 violations" refers to the post-clip range, not attempts.
5. **Ablation table provenance (E-10/E-11, RECOMPUTED).** In the "PPO + Guardrails (5 Seeds)" row, MAE and volatility equal the five-seed means, but oscillation, interventions and violations do not (0.187 / 112 / 0 vs five-seed 0.160 / 563 / 232); they trace to the historical-mismatch run (`x3_0a_ablation_provenance.csv`). The three Dimension-4 rows (aligned_progress, aligned_response_time, zero_progress) are identical to all reported digits.
6. **Stored probe sweep (seed-123 checkpoint, other coordinates at the neutral point).** {f['sensitivity']['non_same']} of {f['sensitivity']['probes']} probes choose a non-Same action; coordinates {', '.join(f['sensitivity']['dims_all_same'])} always give Same. This is a descriptive property of one checkpoint at one neutral point, not a general statement about the policy.
7. **Stored training-time action shares (stochastic policy, last logging window).** Same share {f['training_same_share_range'][0]:.3f}-{f['training_same_share_range'][1]:.3f} across the five training seeds.

Not established here: raw attempted boundary total across seeds (136), five-seed override count (99), Constant-Same + guardrails MAE (0.673): replay only (X3-0c, gated).
"""
    outs.append(rm.write_new(OUT / "X3_0A_REPORT.md", rep))
    print("manifest:", m.finish(outs), m.d["failures"], m.d["deviations"])
    print(rep)


if __name__ == "__main__":
    main()
