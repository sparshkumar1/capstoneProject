"""Independent re-computation of XA/XB headline results from raw run files (fresh code; does not import analyze_xa/xb).
Also reports a POST HOC supplementary analysis: cluster bootstrap over the 8 recorded-answer sessions (k), because the 160 sessions per
condition are 8 recorded answer sets x 20 question orders and are therefore dependent. Labelled post hoc; not part of protocol MA-XA-XB v1.
Usage: python independent_check.py RESULTS_DIR"""
import json, sys, collections
from pathlib import Path
import numpy as np

R = Path(sys.argv[1])
xa = [json.loads(l) for l in open(R / "xa/xa_runs.jsonl")]
xb = [json.loads(l) for l in open(R / "xb/xb_runs.jsonl")]
ok = True
def chk(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name, detail)

# ---- design counts
conds = collections.Counter(r["condition"] for r in xa)
chk("XA: 12 conditions x 160 sessions = 1920", len(conds) == 12 and set(conds.values()) == {160} and len(xa) == 1920, dict(conds))
chk("XA: sessions = 8 k x 20 seeds per condition", all(len({(r['k'], r['seed']) for r in xa if r['condition'] == c}) == 160 for c in conds))
cells = collections.Counter((r["target"], r["fault"], r["variant"]) for r in xb)
chk("XB: 11 faults x 4 variants x 40 = 1760", len(cells) == 44 and set(cells.values()) == {40} and len(xb) == 1760)
chk("XB: sessions = 8 k x 5 seeds", all(len({(r['k'], r['seed']) for r in xb if (r['target'], r['fault'], r['variant']) == c}) == 40 for c in list(cells)[:44]))

A = {c: {(r["k"], r["seed"]): r for r in xa if r["condition"] == c} for c in conds}
keys = sorted(A["B0"])
same = lambda a, b: all(A[a][k]["diff_path"] == A[b][k]["diff_path"] and A[a][k]["score_path"] == A[b][k]["score_path"] and A[a][k]["q_path"] == A[b][k]["q_path"] for k in keys)
frac = lambda a, b: np.mean([A[a][k]["diff_path"] != A[b][k]["diff_path"] for k in keys])
chk("A1-A3 completion/authority/transition 1920/1920", all(r["completed"] and r["authority_ok"] and r["transition_ok"] for r in xa))
chk("A4 M2==B0 paths", same("M2", "B0"))
chk("A5 M3,M5,M6,M8 == M1", all(same(m, "M1") for m in ("M3", "M5", "M6", "M8")))
chk("A6 bypass M4>0 sessions, M1 none", sum(A["M4"][k]["guardrail_bypass"] > 0 for k in keys) > 0 and not any(A["M1"][k]["guardrail_bypass"] for k in keys),
    sum(A["M4"][k]["guardrail_bypass"] > 0 for k in keys))
chk("A7 M1 differs from B0 in all sessions", frac("M1", "B0") == 1.0)
allturn = lambda c: np.concatenate([A[c][k]["turn_ms"] for k in keys])
d = np.median(allturn("M1")) - np.median(allturn("B0"))
chk("A8 median turn latency diff < 50 ms", d < 50, f"{d:+.3f} ms")
print("A9 M7 vs B7 differ frac", frac("M7", "B7"), "(registered: >=0.5 -> contradicted if below)")
print("A10 B0c vs B0 sessions differing", int(sum(A["B0c"][k]["diff_path"] != A["B0"][k]["diff_path"] for k in keys)))

# ---- XB
def cell(t, f, v): return [r for r in xb if (r["target"], r["fault"], r["variant"]) == (t, f, v)]
full = [r for r in xb if r["variant"] == "full"]
chk("B1 full: all contained, no bypass, no leak", all(r["completed"] and r["authority_ok"] and r["transition_ok"] and not r["guardrail_bypass"] and not r["ungrounded_leak"] for r in full))
fk = lambda v, key: sum(r["ma"]["reasons"].get(f"strategy:{key}", 0) for r in cell("strategy", "forbidden_key", v))
chk("B2 authority vs schema classification", fk("full", "authority_violation") > 0 and fk("full", "schema_violation") == 0 and fk("no_authority", "authority_violation") == 0 and fk("no_authority", "schema_violation") > 0,
    (fk("full", "authority_violation"), fk("no_authority", "schema_violation")))
byp = lambda v: sum(r["guardrail_bypass"] > 0 for r in cell("strategy", "adversarial_valid", v))
chk("B3 adversarial bypass: no_arbitration>0, full==0", byp("no_arbitration") > 0 and byp("full") == 0, (byp("no_arbitration"), byp("full")))
lk = lambda v: sum(r["ungrounded_leak"] > 0 for r in cell("coaching", "ungrounded", v))
chk("B4 ungrounded leak: no_grounding>0, full==0", lk("no_grounding") > 0 and lk("full") == 0, (lk("no_grounding"), lk("full")))
print("ungrounded leak sessions by variant:", {v: lk(v) for v in ("full", "no_authority", "no_arbitration", "no_grounding")})
print("adversarial bypass sessions by variant:", {v: byp(v) for v in ("full", "no_authority", "no_arbitration", "no_grounding")})

# ---- XB B6: how identical are the per-cell breaker-open rates, and why (shared fault schedule per (k,seed))
def opened(r):
    return any("breaker" in k or k.endswith("circuit_open") for k in r["ma"]["reasons"])
for key in ("strategy:crash", "strategy:malformed", "coaching:crash"):
    t, f = key.split(":")
    print("breaker-open fraction", key, np.mean([opened(r) for r in cell(t, f, "full")]))

# ---- POST HOC: cluster bootstrap over k (8 clusters)
rng = np.random.default_rng(20270101)
def cluster_ci(a, b, metric, B=10000):
    per_k = []
    for k in range(8):
        ks = [kk for kk in keys if kk[0] == k]
        per_k.append(np.mean([(A[a][x][metric] if A[a][x][metric] is not None else np.nan) - (A[b][x][metric] if A[b][x][metric] is not None else np.nan) for x in ks]))
    per_k = np.array(per_k)
    boots = per_k[rng.integers(0, 8, size=(B, 8))].mean(axis=1)
    return per_k.mean(), np.nanpercentile(boots, 2.5), np.nanpercentile(boots, 97.5), (per_k < 0).sum() if per_k.mean() < 0 else (per_k > 0).sum()
print("\nPOST HOC cluster bootstrap over 8 recorded-answer sessions (mean diff [95% CI], clusters sharing the sign of the mean):")
out = {}
for a, b in (("M1", "B0"),):
    for m in ("level_changes", "reversals", "followups", "ppo_agree"):
        mean, lo, hi, nsame = cluster_ci(a, b, m)
        out[f"{a}-{b}:{m}"] = {"mean": mean, "lo": lo, "hi": hi, "clusters_same_sign": int(nsame), "clusters": 8, "B": 10000, "seed": 20270101}
        print(f"  {a}-{b} {m}: {mean:+.3f} [{lo:+.3f},{hi:+.3f}]  ({nsame}/8 clusters same sign)")
if len(sys.argv) > 2:
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=2, sort_keys=True))
print("\nOVERALL", "PASS" if ok else "FAIL")
