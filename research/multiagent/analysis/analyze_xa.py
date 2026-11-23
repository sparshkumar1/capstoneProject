"""Analysis of XA (protocol MA-XA-XB v1). Reads xa_runs.jsonl; writes xa_summary.csv, xa_paired.csv, xa_predictions.csv.
Registered predictions A1-A10 are evaluated with the criteria stated in the protocol; nothing is added after seeing results."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from stats_util import clopper_pearson, paired_boot, pooled_quantile_diff, quantile  # noqa: E402


def load(d):
    rows = [json.loads(l) for l in open(Path(d) / "xa_runs.jsonl")]
    by = defaultdict(dict)
    for r in rows:
        by[r["condition"]][(r["k"], r["seed"])] = r
    return by


def main(d):
    by = load(d)
    keys = sorted(next(iter(by.values())))
    conds = list(by)
    out = Path(d)
    # ---------------- summary
    summ = []
    for c in conds:
        R = [by[c][k] for k in keys]
        n = len(R)
        ma = [r["ma"] for r in R if r["ma"]]
        tm = [t for r in R for t in r["turn_ms"]]
        row = {"condition": c, "n_sessions": n}
        for f in ("completed", "authority_ok", "transition_ok"):
            k_ = sum(bool(r[f]) for r in R)
            lo, hi = clopper_pearson(k_, n)
            row[f] = f"{k_}/{n}"
            row[f + "_ci95"] = f"[{lo:.3f},{hi:.3f}]"
        for f in ("turns", "followups", "level_changes", "reversals", "rl_decisions", "guardrail_fires", "strategy_source",
                  "guardrail_bypass", "ungrounded_leak", "qwen_attempts"):
            row[f + "_mean"] = round(float(np.mean([r[f] for r in R])), 3)
        ag = [r["ppo_agree"] for r in R if r["ppo_agree"] is not None]
        row["ppo_agree_mean"] = round(float(np.mean(ag)), 3) if ag else ""
        row["sessions_with_bypass"] = sum(r["guardrail_bypass"] > 0 for r in R)
        row["turn_ms_p50"] = round(quantile(tm, 0.5), 3)
        row["turn_ms_p95"] = round(quantile(tm, 0.95), 3)
        row["session_ms_median"] = round(quantile([r["total_ms"] for r in R], 0.5), 2)
        if ma:
            calls = sum(m["agent_call_records"] for m in ma)
            row["agent_calls_mean"] = round(np.mean([m["strategy_calls"] + m["coaching_calls"] for m in ma]), 2)
            row["agent_valid_rate"] = round(sum(m["agent_valid"] for m in ma) / calls, 4) if calls else ""
            row["conflicts_mean"] = round(float(np.mean([m["conflicts"] for m in ma])), 3)
            row["probes_by_strategy_mean"] = round(float(np.mean([m["probe_strategy"] for m in ma])), 3)
            row["version_equals_commits"] = sum(m["version"] == m["commits"] for m in ma)
        summ.append(row)
    cols = sorted({k for r in summ for k in r}, key=lambda k: (k != "condition", k != "n_sessions", k))
    with open(out / "xa_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(summ)

    # ---------------- paired comparisons
    pairs = [("M1", "B0"), ("M2", "B0"), ("M3", "M1"), ("M4", "M1"), ("M5", "M1"), ("M6", "M1"), ("M8", "M1"),
             ("M7", "B7"), ("B0c", "B0"), ("M1c", "M1c" if False else "M1")]
    metrics = ["level_changes", "reversals", "followups", "turns", "ppo_agree", "total_ms", "guardrail_fires"]
    pr = []
    for a, b in pairs:
        if a not in by or b not in by:
            continue
        diffpath = np.mean([by[a][k]["diff_path"] != by[b][k]["diff_path"] for k in keys])
        scorepath = np.mean([by[a][k]["score_path"] != by[b][k]["score_path"] for k in keys])
        row = {"comparison": f"{a}-{b}", "frac_sessions_diff_difficulty_path": round(float(diffpath), 4),
               "frac_sessions_diff_score_path": round(float(scorepath), 4)}
        for m in metrics:
            xs = [(by[a][k][m], by[b][k][m]) for k in keys if by[a][k][m] is not None and by[b][k][m] is not None]
            if not xs:
                continue
            mean, lo, hi = paired_boot([x[0] for x in xs], [x[1] for x in xs])
            row[m] = f"{mean:+.3f} [{lo:+.3f},{hi:+.3f}]"
        pt, lo, hi = pooled_quantile_diff([by[a][k]["turn_ms"] for k in keys], [by[b][k]["turn_ms"] for k in keys], 0.5)
        row["turn_ms_p50_diff"] = f"{pt:+.3f} [{lo:+.3f},{hi:+.3f}]"
        pt, lo, hi = pooled_quantile_diff([by[a][k]["turn_ms"] for k in keys], [by[b][k]["turn_ms"] for k in keys], 0.95)
        row["turn_ms_p95_diff"] = f"{pt:+.3f} [{lo:+.3f},{hi:+.3f}]"
        pr.append(row)
    cols = sorted({k for r in pr for k in r}, key=lambda k: (k != "comparison", k))
    with open(out / "xa_paired.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(pr)

    # ---------------- registered predictions
    def allk(c, f):
        return all(by[c][k][f] for k in keys)

    def same_path(a, b):
        return all(by[a][k]["diff_path"] == by[b][k]["diff_path"] and by[a][k]["score_path"] == by[b][k]["score_path"]
                   and by[a][k]["q_path"] == by[b][k]["q_path"] for k in keys)
    preds = []

    def add(pid, claim, observed, ok):
        preds.append({"id": pid, "prediction": claim, "observed": observed, "verdict": "SUPPORTED" if ok else "CONTRADICTED"})
    add("A1", "completion 100% in every condition", {c: sum(by[c][k]["completed"] for k in keys) for c in conds}, all(allk(c, "completed") for c in conds))
    add("A2", "committed scores equal the recorded evaluator output in every session of every condition",
        {c: sum(by[c][k]["authority_ok"] for k in keys) for c in conds}, all(allk(c, "authority_ok") for c in conds))
    add("A3", "difficulty levels stay within [1,5], and every RL-phase decision moves by at most one level, in every session of every condition",
        {c: sum(by[c][k]["transition_ok"] for k in keys) for c in conds}, all(allk(c, "transition_ok") for c in conds))
    if "M2" in by:
        add("A4", "M2 (no Strategy Agent) reproduces B0 (difficulty, score and question paths) in every session",
            sum(same_path("M2", "B0") for _ in [0]), same_path("M2", "B0"))
    ab = {m: same_path(m, "M1") for m in ("M3", "M5", "M6", "M8") if m in by}
    add("A5", "M3, M5, M6, M8 reproduce M1's difficulty/score/question paths in every session (fault-free)", ab, all(ab.values()))
    if "M4" in by:
        add("A6", "M4 (no arbitration) has guardrail_bypass>0 in >=1 session; M1 has 0 in all",
            {"M4_sessions": sum(by["M4"][k]["guardrail_bypass"] > 0 for k in keys), "M1_sessions": sum(by["M1"][k]["guardrail_bypass"] > 0 for k in keys)},
            any(by["M4"][k]["guardrail_bypass"] > 0 for k in keys) and not any(by["M1"][k]["guardrail_bypass"] > 0 for k in keys))
    frac = float(np.mean([by["M1"][k]["diff_path"] != by["B0"][k]["diff_path"] for k in keys]))
    add("A7", "M1 differs from B0 in difficulty path in >=50% of sessions", round(frac, 4), frac >= 0.5)
    pt, lo, hi = pooled_quantile_diff([by["M1"][k]["turn_ms"] for k in keys], [by["B0"][k]["turn_ms"] for k in keys], 0.5)
    add("A8", "median per-turn latency M1 - B0 < 50 ms (pooled turns)", f"{pt:+.3f} ms [{lo:+.3f},{hi:+.3f}]", pt < 50.0)
    if "M7" in by and "B7" in by:
        fr7 = float(np.mean([by["M7"][k]["diff_path"] != by["B7"][k]["diff_path"] for k in keys]))
        add("A9", "with PPO unavailable, M7 differs from B7 in difficulty path in >=50% of sessions", round(fr7, 4), fr7 >= 0.5)
    if "B0c" in by:
        n_diff = sum(by["B0c"][k]["diff_path"] != by["B0"][k]["diff_path"] for k in keys)
        add("A10", "canonical guardrails change the difficulty path in >=1 session vs legacy (B0c vs B0)", f"{n_diff}/{len(keys)}", n_diff >= 1)
    with open(out / "xa_predictions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "prediction", "observed", "verdict"])
        w.writeheader()
        for p in preds:
            p["observed"] = json.dumps(p["observed"], sort_keys=True)
            w.writerow(p)
    for p in preds:
        print(p["id"], p["verdict"], p["observed"][:140])


if __name__ == "__main__":
    main(sys.argv[1])
