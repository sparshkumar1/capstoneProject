"""POST HOC sensitivity analysis (NOT part of any registered protocol; added after the cluster-level heterogeneity was noticed).
Leave-one-cluster-out (LOCO) over the 8 recorded answer sets k, for M1 - B0 on XA. Fresh code reading results/xa/xa_runs.jsonl only.
For each metric: per-cluster mean difference (20 question orders per cluster), the LOCO mean, and an exact percentile interval over all
7^7 resamples of the remaining 7 clusters. Usage: python leave_one_cluster_out.py RESULTS_DIR [OUT_JSON]"""
import json, sys, itertools
from pathlib import Path
import numpy as np

R = Path(sys.argv[1])
xa = [json.loads(l) for l in open(R / "xa/xa_runs.jsonl")]
A = {c: {(r["k"], r["seed"]): r for r in xa if r["condition"] == c} for c in ("M1", "B0")}
keys = sorted(A["B0"])
assert len(keys) == 160 and sorted({k for k, _ in keys}) == list(range(8))

def per_cluster(metric):
    out = []
    for k in range(8):
        d = [A["M1"][x][metric] - A["B0"][x][metric] for x in keys if x[0] == k]
        out.append(float(np.mean(d)))
    return np.array(out)

def exact_ci(v):
    n = len(v)
    idx = np.array(list(itertools.product(range(n), repeat=n)), dtype=np.int8)
    m = np.sort(v[idx].mean(axis=1))
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))

out = {}
for metric in ("level_changes", "reversals", "followups", "ppo_agree"):
    pk = per_cluster(metric)
    res = {"per_cluster": pk.tolist(), "all8_mean": float(pk.mean()), "loco": {}}
    for drop in range(8):
        rest = np.delete(pk, drop)
        lo, hi = exact_ci(rest)
        res["loco"][str(drop)] = {"mean": float(rest.mean()), "lo": lo, "hi": hi, "excludes_zero": bool(lo > 0 or hi < 0)}
    out[f"M1-B0:{metric}"] = res
    print(metric, "per-cluster", np.round(pk, 3).tolist(), f"all8 {pk.mean():+.3f}")
    for d, v in res["loco"].items():
        print(f"   drop k={d}: {v['mean']:+.3f} [{v['lo']:+.3f},{v['hi']:+.3f}] excludes0={v['excludes_zero']}")
if len(sys.argv) > 2:
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=2, sort_keys=True))
