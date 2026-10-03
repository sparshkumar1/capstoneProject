"""Analysis of E1 (protocol v1 section 8). Counts, Clopper-Pearson intervals, prediction check, exploratory reversals."""
import csv, json, sys
from collections import defaultdict
from pathlib import Path
from scipy.stats import beta

R = Path(__file__).parents[1] / "results"
rows = [json.loads(l) for l in open(R / "e1_runs.jsonl")]


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi


cells = defaultdict(list)
for r in rows:
    cells[(r["fault"], r["variant"])].append(r)

INV = {"I1": lambda r: r["I1_committed_without_valid_eval"] > 0,
       "I2": lambda r: r["I2_invalid_stored_numbers"] > 0,
       "I3": lambda r: (r["I3_mandatory_violations"] or 0) > 0,
       "I4": lambda r: not r["I4_terminated"],
       "I5": lambda r: r["I5_max_followup_run"] > 2,
       "I6": lambda r: r["I6_state_inconsistent"],
       "I7": lambda r: r["I7_up_after_low"] > 0}
APPLIES = {"F0": ["I1", "I2", "I4", "I5", "I6", "I7"], "F1": ["I1", "I4"], "F2": ["I1", "I4"], "F3": ["I1", "I2"],
           "F4": ["I3"], "F5": ["I6"]}
out = []
for (f, v), rs in sorted(cells.items()):
    n = len(rs)
    for inv in APPLIES[f]:
        k = sum(INV[inv](r) for r in rs)
        lo, hi = cp(k, n)
        tot = sum({"I1": r["I1_committed_without_valid_eval"], "I2": r["I2_invalid_stored_numbers"],
                   "I3": r["I3_mandatory_violations"] or 0, "I4": 0, "I5": 0, "I6": 0,
                   "I7": r["I7_up_after_low"]}[inv] for r in rs)
        out.append({"fault": f, "variant": v, "invariant": inv, "sessions": n, "sessions_violating": k,
                    "ci_lo": round(lo, 3), "ci_hi": round(hi, 3), "total_violation_count": tot,
                    "mean_turns": round(sum(r["n_turns"] for r in rs) / n, 2),
                    "mean_followups": round(sum(r["n_followups"] for r in rs) / n, 2)})
with open(R / "e1_cells.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)

# prediction check against protocol section 5 (predictions copied verbatim as booleans: violation expected in ablated variant)
PRED = [("F1", "V6", "I1", True, "known"), ("F2", "V6", "I1", True, "known"), ("F3", "V0", "I1", True, "known (full system)"),
        ("F3", "V1", "I2", True, "unsure"), ("F4", "V1", "I3", True, "known"), ("F0", "V5", "I5", True, "known"),
        ("F0", "V5", "I4", True, "known"), ("F5", "V7", "I6", True, "unsure"), ("F0", "V2", "I7", True, "unsure"),
        ("F0", "V4", "I5", False, "trivial"), ("F1", "V0", "I1", False, "known"), ("F2", "V0", "I1", False, "known"),
        ("F4", "V0", "I3", False, "known"), ("F5", "V0", "I6", False, "known")]
look = {(o["fault"], o["variant"], o["invariant"]): o for o in out}
with open(R / "e1_predictions.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["fault", "variant", "invariant", "predicted_violation", "basis", "observed_sessions_violating", "sessions", "match"])
    for f, v, inv, p, b in PRED:
        o = look[(f, v, inv)]
        obs = o["sessions_violating"] > 0
        w.writerow([f, v, inv, p, b, o["sessions_violating"], o["sessions"], "yes" if obs == p else "NO"])

# exploratory: reversals of difficulty direction in RL phase (non-registered, amendment A1)
def reversals(path, flags_dec):
    deltas = []
    prev = 2
    for d, src in zip(path, flags_dec):
        if src != "baseline_warmup":
            if d != prev: deltas.append(1 if d > prev else -1)
        prev = d
    return sum(1 for a, b in zip(deltas, deltas[1:]) if a != b), len(deltas)
rev = []
for v in ["V0", "V2", "V3"]:
    rs = cells[("F0", v)]
    rr = [reversals(r["difficulty_path"], r["decision_path"]) for r in rs]
    rev.append({"variant": v, "sessions": len(rs), "mean_reversals": round(sum(a for a, _ in rr) / len(rr), 2),
                "mean_changes": round(sum(b for _, b in rr) / len(rr), 2)})
with open(R / "e1_reversals_exploratory.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rev[0])); w.writeheader(); w.writerows(rev)
# decision-source composition in RL phase (descriptive)
comp = defaultdict(lambda: defaultdict(int))
for v in ["V0", "V2", "V3"]:
    for r in cells[("F0", v)]:
        for s, n in r["decision_sources_rl_phase"].items():
            comp[v][s] += n
json.dump({v: dict(c) for v, c in comp.items()}, open(R / "e1_decision_sources.json", "w"), indent=1, sort_keys=True)

print("cell table:")
for o in out:
    print(o["fault"], o["variant"], o["invariant"], f'{o["sessions_violating"]}/{o["sessions"]}', (o["ci_lo"], o["ci_hi"]), "count", o["total_violation_count"], "turns", o["mean_turns"], "fu", o["mean_followups"])
print("\npredictions:")
for l in open(R / "e1_predictions.csv"): print(l.strip())
print("\nreversals:", rev); print("sources:", {v: dict(c) for v, c in comp.items()})
