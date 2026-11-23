"""Analysis of XC (protocol MA-XC v1). Reads xc_runs.jsonl and the XA results (for M1/M4 reference); writes xc_summary.csv, xc_predictions.csv.
Primary intervals: cluster bootstrap over the 8 recorded-answer sessions (B=10000, seed 20270101)."""
import csv, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

xc_dir, xa_dir = Path(sys.argv[1]), Path(sys.argv[2])
rows = [json.loads(l) for l in open(xc_dir / "xc_runs.jsonl")]
xa = [json.loads(l) for l in open(xa_dir / "xa_runs.jsonl")]
by = defaultdict(dict)
for r in rows:
    by[r["condition"]][(r["k"], r["seed"])] = r
m1 = {(r["k"], r["seed"]): r for r in xa if r["condition"] == "M1"}
m4 = [r for r in xa if r["condition"] == "M4"]
keys = sorted(m1)
conds = ["TAU0", "TAU5", "TAU6", "TAU7", "TAU8", "TAU9"]
rng = np.random.default_rng(20270101)


def cluster(vals_by_key, B=10000):
    per_k = np.array([np.mean([vals_by_key[x] for x in keys if x[0] == k]) for k in range(8)])
    boots = per_k[rng.integers(0, 8, size=(B, 8))].mean(axis=1)
    return per_k.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5)


def metric(c, f):
    return {x: (by[c][x][f] if by[c][x][f] is not None else np.nan) for x in keys}


summ = []
for c in conds:
    row = {"condition": c, "tau": json.load(open(Path(__file__).parents[1] / "configs/ma_xc_v1.json"))["taus"][c], "n_sessions": len(by[c])}
    for f in ("level_changes", "reversals", "followups", "ppo_agree", "strategy_source", "guardrail_fires"):
        m, lo, hi = cluster(metric(c, f))
        row[f] = f"{m:.3f} [{lo:.3f},{hi:.3f}]"
    row["sessions_with_bypass"] = sum(by[c][x]["guardrail_bypass"] > 0 for x in keys)
    for f in ("completed", "authority_ok", "transition_ok"):
        row[f] = sum(bool(by[c][x][f]) for x in keys)
    summ.append(row)
with open(xc_dir / "xc_summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summ[0]))
    w.writeheader(); w.writerows(summ)

same = lambda a, b: all(a[x]["diff_path"] == b[x]["diff_path"] and a[x]["score_path"] == b[x]["score_path"] and a[x]["q_path"] == b[x]["q_path"] for x in keys)
mean = lambda c, f: float(np.mean([by[c][x][f] for x in keys if by[c][x][f] is not None]))
preds = []
def add(i, claim, obs, ok): preds.append({"id": i, "prediction": claim, "observed": json.dumps(obs, sort_keys=True), "verdict": "SUPPORTED" if ok else "CONTRADICTED"})
c1 = {"ppo_agree": round(mean("TAU0", "ppo_agree"), 3), "level_changes": round(mean("TAU0", "level_changes"), 3),
      "bypass_sessions": sum(by["TAU0"][x]["guardrail_bypass"] > 0 for x in keys)}
add("C1", "TAU0: PPO agreement<0.10, level changes<5.0, no guardrail bypass", c1, c1["ppo_agree"] < 0.10 and c1["level_changes"] < 5.0 and c1["bypass_sessions"] == 0)
add("C2", "TAU6 reproduces XA M1 paths in every session", same(by["TAU6"], m1), same(by["TAU6"], m1))
add("C3", "TAU5 equals TAU6 in every session", same(by["TAU5"], by["TAU6"]), same(by["TAU5"], by["TAU6"]))
ss = [mean(c, "strategy_source") for c in ("TAU6", "TAU7", "TAU8", "TAU9")]
add("C4", "strategy-sourced decisions non-increasing over tau 0.6,0.7,0.8,0.9", [round(s, 3) for s in ss], all(a >= b for a, b in zip(ss, ss[1:])))
add("C5", "tau=0.9 strategy-sourced decisions < half of tau=0.6", {"tau0.9": round(ss[3], 3), "tau0.6": round(ss[0], 3)}, ss[3] < 0.5 * ss[0])
ok = all(by[c][x][f] for c in conds for x in keys for f in ("completed", "authority_ok", "transition_ok"))
add("V", "completion/authority/transition valid in every session of every condition", ok, ok)
with open(xc_dir / "xc_predictions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "prediction", "observed", "verdict"]); w.writeheader(); w.writerows(preds)
for p in preds: print(p["id"], p["verdict"], p["observed"])
print("reference XA M4: ppo_agree %.3f level_changes %.3f" % (np.mean([r["ppo_agree"] for r in m4 if r["ppo_agree"] is not None]), np.mean([r["level_changes"] for r in m4])))
