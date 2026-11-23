"""Analysis of XB (protocol MA-XA-XB v1). Reads xb_runs.jsonl (+ optional XA dir for the clean-latency reference).
Writes xb_cells.csv, xb_reasons.csv and xb_predictions.csv with predictions B1-B6 evaluated as registered."""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from stats_util import clopper_pearson, quantile  # noqa: E402


def main(d, xa_dir=None):
    rows = [json.loads(l) for l in open(Path(d) / "xb_runs.jsonl")]
    cells = defaultdict(list)
    for r in rows:
        cells[(r["target"], r["fault"], r["variant"])].append(r)
    out = Path(d)
    table, reasons_rows = [], []
    agg = {}
    for key, R in sorted(cells.items()):
        n = len(R)
        reasons = Counter()
        for r in R:
            reasons.update(r["ma"]["reasons"])
        tm = [t for r in R for t in r["turn_ms"]]
        rec = {"target": key[0], "fault": key[1], "variant": key[2], "n_sessions": n, "injected_total": sum(r["injected"] for r in R)}
        for f in ("completed", "authority_ok", "transition_ok"):
            k = sum(bool(r[f]) for r in R)
            lo, hi = clopper_pearson(k, n)
            rec[f] = f"{k}/{n}"
            rec[f + "_ci95"] = f"[{lo:.3f},{hi:.3f}]"
        rec["sessions_with_guardrail_bypass"] = sum(r["guardrail_bypass"] > 0 for r in R)
        rec["sessions_with_ungrounded_leak"] = sum(r["ungrounded_leak"] > 0 for r in R)
        rec["coaching_rejected_total"] = sum(r["ma"]["coaching_rejected"] for r in R)
        rec["sessions_with_breaker_open"] = sum(any(k.endswith(":breaker_open") for k in r["ma"]["reasons"]) for r in R)
        rec["strategy_source_mean"] = round(float(np.mean([r["strategy_source"] for r in R])), 3)
        rec["turn_ms_p95"] = round(quantile(tm, 0.95), 2)
        rec["turn_ms_p50"] = round(quantile(tm, 0.5), 2)
        table.append(rec)
        agg[key] = {"rec": rec, "reasons": reasons, "R": R}
        for k, v in sorted(reasons.items()):
            reasons_rows.append({"target": key[0], "fault": key[1], "variant": key[2], "agent:reason": k, "count": v})
    cols = list(table[0])
    with open(out / "xb_cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(table)
    with open(out / "xb_reasons.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["target", "fault", "variant", "agent:reason", "count"]); w.writeheader(); w.writerows(reasons_rows)

    preds = []

    def add(pid, claim, obs, ok):
        preds.append({"id": pid, "prediction": claim, "observed": json.dumps(obs, sort_keys=True, default=str),
                      "verdict": "SUPPORTED" if ok else ("NOT-EVALUABLE" if ok is None else "CONTRADICTED")})
    full = {k: v for k, v in agg.items() if k[2] == "full"}
    b1 = {f"{k[0]}:{k[1]}": (v["rec"]["completed"], v["rec"]["authority_ok"], v["rec"]["transition_ok"],
                              v["rec"]["sessions_with_guardrail_bypass"], v["rec"]["sessions_with_ungrounded_leak"]) for k, v in full.items()}
    ok1 = all(all(int(x.split("/")[0]) == int(x.split("/")[1]) for x in t[:3]) and t[3] == 0 and t[4] == 0 for t in b1.values())
    add("B1", "variant=full: every fault cell completes, keeps committed scores authoritative and transitions valid; no guardrail bypass, no ungrounded leak", b1, ok1)
    k_f, k_n = ("strategy", "forbidden_key", "full"), ("strategy", "forbidden_key", "no_authority")
    if k_f in agg and k_n in agg:
        rf, rn = agg[k_f]["reasons"], agg[k_n]["reasons"]
        av_f, sv_f = rf.get("strategy:authority_violation", 0), rf.get("strategy:schema_violation", 0)
        av_n, sv_n = rn.get("strategy:authority_violation", 0), rn.get("strategy:schema_violation", 0)
        cont = all(agg[k]["rec"][f].split("/")[0] == agg[k]["rec"][f].split("/")[1] for k in (k_f, k_n) for f in ("completed", "authority_ok", "transition_ok"))
        add("B2", "forbidden_key: full -> authority_violation>0 and schema_violation==0; no_authority -> authority_violation==0, schema_violation>0; containment 100% in both",
            {"full": [av_f, sv_f], "no_authority": [av_n, sv_n], "containment_100": cont}, av_f > 0 and sv_f == 0 and av_n == 0 and sv_n > 0 and cont)
    ka, kn = ("strategy", "adversarial_valid", "full"), ("strategy", "adversarial_valid", "no_arbitration")
    if ka in agg and kn in agg:
        add("B3", "adversarial_valid: no_arbitration has guardrail_bypass>0 in >=1 session; full has 0",
            {"no_arbitration": agg[kn]["rec"]["sessions_with_guardrail_bypass"], "full": agg[ka]["rec"]["sessions_with_guardrail_bypass"]},
            agg[kn]["rec"]["sessions_with_guardrail_bypass"] >= 1 and agg[ka]["rec"]["sessions_with_guardrail_bypass"] == 0)
    kg, kng = ("coaching", "ungrounded", "full"), ("coaching", "ungrounded", "no_grounding")
    if kg in agg and kng in agg:
        add("B4", "ungrounded coaching: no_grounding leaks (>=1 session); full has 0 leaks and rejects plans",
            {"no_grounding_leak_sessions": agg[kng]["rec"]["sessions_with_ungrounded_leak"], "full_leak_sessions": agg[kg]["rec"]["sessions_with_ungrounded_leak"],
             "full_rejected": agg[kg]["rec"]["coaching_rejected_total"]},
            agg[kng]["rec"]["sessions_with_ungrounded_leak"] >= 1 and agg[kg]["rec"]["sessions_with_ungrounded_leak"] == 0 and agg[kg]["rec"]["coaching_rejected_total"] > 0)
    kt = ("strategy", "timeout", "full")
    if kt in agg:
        if xa_dir:
            xr = [json.loads(l) for l in open(Path(xa_dir) / "xa_runs.jsonl")]
            clean = quantile([t for r in xr if r["condition"] == "M1" for t in r["turn_ms"]], 0.95)
            diff = agg[kt]["rec"]["turn_ms_p95"] - clean
            add("B5", "strategy timeout (full): pooled p95 per-turn latency exceeds the clean M1 p95 by >=100 ms",
                {"timeout_p95_ms": agg[kt]["rec"]["turn_ms_p95"], "clean_M1_p95_ms": round(clean, 2), "diff_ms": round(diff, 2)}, diff >= 100.0)
        else:
            add("B5", "strategy timeout latency (needs XA dir)", "n/a", None)
    b6 = {}
    for key in [("strategy", "crash", "full"), ("strategy", "malformed", "full"), ("strategy", "stale", "full"), ("strategy", "nan_confidence", "full"),
                ("coaching", "crash", "full"), ("coaching", "malformed", "full"), ("coaching", "stale", "full")]:
        if key in agg:
            b6[f"{key[0]}:{key[1]}"] = agg[key]["rec"]["sessions_with_breaker_open"] / agg[key]["rec"]["n_sessions"]
    add("B6", "at fault rate 0.3, >=80% of sessions see the per-agent breaker open at least once (crash/malformed/stale/nan cells)", b6,
        all(v >= 0.8 for v in b6.values()) if b6 else None)
    with open(out / "xb_predictions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "prediction", "observed", "verdict"]); w.writeheader(); w.writerows(preds)
    for p in preds:
        print(p["id"], p["verdict"], p["observed"][:150])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
