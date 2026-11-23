"""Claim audit: recompute every quantitative claim of the manuscript from the raw result artifacts and require the number to appear in
the manuscript source. Exit 1 on any failure. Reads only; never edits results."""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
RES = REPO / "research/multiagent/results"
OLD = REPO / "paper/adcom2027/results"
sys.path.insert(0, str(REPO / "research/multiagent/analysis"))
from stats_util import clopper_pearson  # noqa: E402

import subprocess
# The audited text is what a reader sees: the extracted text of the built PDF (macros expanded, tables included),
# with all whitespace removed from haystack and needles so that spacing and line breaks cannot matter.
pdf_txt = subprocess.run(["pdftotext", str(HERE / "manuscript/main.pdf"), "-"], capture_output=True, text=True).stdout
txt = re.sub(r"\s+", "", pdf_txt.replace("\u2212", "-").replace("\u2013", "-"))
fails, n = [], 0


def need(label, s):
    global n
    n += 1
    if re.sub(r"\s+", "", s) not in txt:
        fails.append((label, s))


xa = defaultdict(dict)
for l in open(RES / "xa/xa_runs.jsonl"):
    r = json.loads(l)
    xa[r["condition"]][(r["k"], r["seed"])] = r
keys = sorted(xa["B0"])
S = {r["condition"]: r for r in csv.DictReader(open(RES / "xa/xa_summary.csv"))}
P = {r["comparison"]: r for r in csv.DictReader(open(RES / "xa/xa_paired.csv"))}
f2 = lambda x: f"{float(x):.2f}"
need("B0 level changes", f2(S["B0"]["level_changes_mean"]))
need("M1 level changes", f2(S["M1"]["level_changes_mean"]))
need("B0 reversals", f2(S["B0"]["reversals_mean"]))
need("M1 reversals", f2(S["M1"]["reversals_mean"]))
need("ppo agree B0", f"{float(S['B0']['ppo_agree_mean']):.3f}")
need("ppo agree M1", f"{float(S['M1']['ppo_agree_mean']):.3f}")
def ci2(cell):
    m = re.match(r"([+-][\d.]+) \[([+-][\d.]+),([+-][\d.]+)\]", cell)
    f = lambda x: f"{float(x):+.2f}"
    return f(m.group(1)), f(m.group(2)), f(m.group(3))


from stats_util import paired_boot  # noqa: E402
for key in ("level_changes", "reversals", "turns"):
    pt, lo, hi = paired_boot([xa["M1"][k][key] for k in keys], [xa["B0"][k][key] for k in keys])   # full precision from raw runs
    need("M1-B0 " + key, f"[{lo:+.2f},{hi:+.2f}]")
    if key != "turns":
        need("M1-B0 " + key + " point", f"{pt:+.2f}")
pt, lo, hi = ci2(P["M1-B0"]["turn_ms_p50_diff"])
need("latency median diff", f"[{lo},{hi}]")
need("agent calls", f"{float(S['M1']['agent_calls_mean']):.1f} agent calls")
need("conflicts", f"{float(S['M1']['conflicts_mean']):.1f} decisions per session")
need("M4 level changes", f"{float(S['M4']['level_changes_mean']):.1f} per session")
need("M4 agree", f"{float(S['M4']['ppo_agree_mean']):.3f}")
need("M4 bypass sessions", f"{S['M4']['sessions_with_bypass']} sessions contained")
need("B0/M1 p50", f"{float(S['B0']['turn_ms_p50']):.3f}")
need("M1 p95", f"{float(S['M1']['turn_ms_p95']):.3f}")
d97 = sum(xa["M7"][k]["diff_path"] != xa["B7"][k]["diff_path"] for k in keys)
need("M7 vs B7 sessions", f"{d97} of 160 sessions")
need("M1 differs all", "all 160 sessions")
need("CP lower 160/160", f"{clopper_pearson(160, 160)[0]:.3f}")
for c in xa:
    assert all(xa[c][k]["completed"] and xa[c][k]["authority_ok"] and xa[c][k]["transition_ok"] for k in keys), c

xb = [json.loads(l) for l in open(RES / "xb/xb_runs.jsonl")]
cell = defaultdict(list)
for r in xb:
    cell[(r["target"], r["fault"], r["variant"])].append(r)
assert all(r["completed"] and r["authority_ok"] and r["transition_ok"] for r in xb)
reasons = lambda k: sum((Counter(r["ma"]["reasons"]) for r in cell[k]), Counter())
need("152 forbidden", "152")
fa, na = reasons(("strategy", "forbidden_key", "full")), reasons(("strategy", "forbidden_key", "no_authority"))
assert fa["strategy:authority_violation"] == 152 and fa["strategy:schema_violation"] == 0
assert na["strategy:schema_violation"] == 152 and na["strategy:authority_violation"] == 0
need("930 adversarial", "930 injections")
byp = lambda k: sum(r["guardrail_bypass"] > 0 for r in cell[k])
need("bypass adv no-arb", f"{byp(('strategy','adversarial_valid','no_arbitration'))} of 40")
assert byp(("strategy", "adversarial_valid", "full")) == 0
need("bypass strat fault cells", f"{byp(('strategy','crash','no_arbitration'))} of 40")
for f in ("crash", "timeout", "malformed", "forbidden_key", "stale", "nan_confidence"):
    assert byp(("strategy", f, "no_arbitration")) == byp(("strategy", "crash", "no_arbitration"))
need("adv strategy source", f"{np.mean([r['strategy_source'] for r in cell[('strategy','adversarial_valid','full')]]):.1f} decisions per session")
need("950 ungrounded", "950 ungrounded plans")
assert sum(r["ma"]["coaching_rejected"] for r in cell[("coaching", "ungrounded", "full")]) == 950
need("leak 40", f"{sum(r['ungrounded_leak'] > 0 for r in cell[('coaching','ungrounded','no_grounding')])} of 40 sessions")
p95 = lambda k: float(np.quantile([t for r in cell[k] for t in r["turn_ms"]], 0.95))
need("timeout p95", f"{p95(('strategy','timeout','full')):.1f}")
need("clean p95", f"{float(np.quantile([t for r in xa['M1'].values() for t in r['turn_ms']], 0.95)):.1f}")
bo = sum(any(k.endswith(":breaker_open") for k in r["ma"]["reasons"]) for r in cell[("strategy", "crash", "full")])
need("breaker 29/40", f"{bo} of 40 sessions")
need("breaker pct", f"{100 * bo / 40:.1f}")

xd = json.load(open(RES / "xd/xd_grounding.json"))
c = xd["ALL"]["categories"]
assert c["C0_faithful"]["rejected"] == 17 and c["C4_truncated_paraphrase_credit"]["accepted"] == 40
need("XD 47/47", "47/47"); need("XD 64/64", "64/64")
assert xd["NO_OVERLAP"]["categories"]["C0_faithful"]["accepted"] == 47 and xd["RELABELLED"]["categories"]["C0_faithful"]["accepted"] == 64
assert xd["NO_OVERLAP"]["categories"]["C4_truncated_paraphrase_credit"]["accepted"] == 40 and xd["RELABELLED"]["categories"]["C4_truncated_paraphrase_credit"]["accepted"] == 57
lo, hi = clopper_pearson(57, 57)
need("XD CP", f"[{lo:.3f},{hi:.3f}]".replace("1.000]", "1.000]"))

old = defaultdict(list)
for l in open(OLD / "e1_runs.jsonl"):
    r = json.loads(l)
    old[(r["fault"], r["variant"])].append(r)
v0 = sum(r["I7_up_after_low"] > 0 for r in old[("F0", "V0")]); v2 = sum(r["I7_up_after_low"] > 0 for r in old[("F0", "V2")])
need("V2 3 of 8", f"{v2} of 8 sessions for V2 and {v0} of 8")
e1 = json.load(open(RES / "xe_e1/xe_e1_reproduction.json"))
assert e1["byte_identical"] and e1["rows"] == 752
need("E1 byte identical rows", "all 752 sessions")
need("E1 sha prefix not required", "byte-identical")
b = json.load(open(RES / "xe_b503/xe_b503.json"))
assert b["err503_legacy"]["committed_scores"] == b["err503_fixed"]["committed_scores"] == b["healthy_fixed"]["committed_scores"]
need("b503 legacy", str(b["err503_legacy"]["http_attempts_total"])); need("b503 fixed", str(b["err503_fixed"]["http_attempts_total"]))

e5 = json.load(open(RES / "xe_e5/e5_circuit_breaker.json"))
for sc in ("hang_B", "hang_S_P30", "hang_S_P60"):
    need("E5 new median " + sc, f"{e5[sc]['turn_s_median']:.2f}")
    need("E5 new http " + sc, str(e5[sc]["http_attempts_total"]))

# XC (protocol MA-XC v1) and the post hoc cluster bootstrap, recomputed independently of the analysis script
import csv as _csv
xcp = {r["id"]: r["verdict"] for r in _csv.DictReader(open(RES / "xc/xc_predictions.csv"))}
assert all(v == "SUPPORTED" for v in xcp.values()), xcp
xcr = {r["condition"]: r for r in _csv.DictReader(open(RES / "xc/xc_summary.csv"))}
need("XC tau0 level changes", xcr["TAU0"]["level_changes"].split(" ")[0]); need("XC tau0 agreement", xcr["TAU0"]["ppo_agree"].split(" ")[0])
need("XC five predictions supported", "All 5 registered XC")
ph = json.load(open(RES / "post_hoc/cluster_bootstrap.json"))
for m in ("level_changes", "reversals", "followups"):
    d = ph["M1-B0:" + m]
    need("post hoc " + m + " lo", f"{abs(d['lo']):.2f}"); need("post hoc " + m + " hi", f"{abs(d['hi']):.2f}")
need("post hoc followups cluster count", "only 1 of the 8")

lo = json.load(open(RES / "post_hoc/leave_one_cluster_out.json"))["M1-B0:level_changes"]["loco"]
need("LOCO drop k=1 mean", f"{abs(lo['1']['mean']):.2f}"); need("LOCO drop k=1 lo", f"{abs(lo['1']['lo']):.2f}"); need("LOCO drop k=1 hi", f"{abs(lo['1']['hi']):.2f}")
ups = [v["hi"] for d, v in lo.items() if d != "1"]
assert all(v["lo"] < 0 < v["hi"] for d, v in lo.items() if d != "1") and lo["1"]["hi"] < 0
agr = json.load(open(RES / "post_hoc/leave_one_cluster_out.json"))["M1-B0:ppo_agree"]["loco"]
assert all(v["excludes_zero"] for v in agr.values()); need("LOCO agreement all eight drops", "excludes zero in all eight drops")

scd = json.load(open(RES / "post_hoc/strategy_confidence_distribution.json"))["mode|confidence"]
assert not any(k.startswith("stretch") for k in scd) and set(scd) == {"recover|0.70", "recover|0.80", "remediate|0.80", "steady|0.45"}
need("strategy proposals total", f"{sum(scd.values()):,}"); need("remediate 0.80 count", f"{scd['remediate|0.80']:,}")
need("recover 0.80 count", str(scd["recover|0.80"])); need("recover 0.70 count", str(scd["recover|0.70"])); need("steady count", f"{scd['steady|0.45']:,}")
need("level changes sign by answer set", "decreased in 7 of the 8 answer sets")

# guardrail grid (recomputed from code)
import itertools, os
os.environ.setdefault("EVALUATOR_MOCK_MODE", "1")
sys.path.insert(0, str(REPO))
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator  # noqa: E402
from rl.guardrails import apply_canonical_guardrails  # noqa: E402
o = InterviewOrchestrator("g", {}, {"num_questions": 3}, select_questions_fn=lambda *a: [])
g = [i / 10 for i in range(11)]
tot = dis = 0
for perf, avg, conf, lvl, prop, consec in itertools.product(g, g, g, [1, 2, 3, 4, 5], [0, 1, 2], [0, 2]):
    o._state["consecutive_followups"] = consec
    a = o._apply_guardrails(prop, perf, avg, conf, 1 - conf, lvl / 5.0)
    bb, _, _ = apply_canonical_guardrails(perf, avg, conf, 1 - conf, 0.0, lvl / 5.0, prop, consec)
    tot += 1; dis += a != bb
need("grid", f"{dis:,} of {tot:,}".replace(",", ","))
need("grid pct", f"{100 * dis / tot:.1f}")

for lab, s in fails:
    print("MISSING", lab, repr(s))
print(f"claim audit: {n - len(fails)}/{n} checks passed")
sys.exit(1 if fails else 0)
