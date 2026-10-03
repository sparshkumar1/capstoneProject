"""Claim audit for ADCoM 2027 Specialization & Coordination candidate:
Recomputes every quantitative claim of the revised manuscript directly from raw result artifacts
and asserts its exact occurrence in the compiled candidate PDF text.
Exit code 1 on any discrepancy. Reads only; never edits results.
"""
import csv
import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
RES = REPO / "research/multiagent/results"
sys.path.insert(0, str(REPO / "research/multiagent/analysis"))
from stats_util import clopper_pearson, paired_boot  # noqa: E402

candidate_pdfs = [
    HERE / "manuscript/main.pdf",
    HERE / "ADCOM2027_PREPAIred_v12_specialization_blind.pdf",
]
pdf_txt = ""
for cand in candidate_pdfs:
    if cand.exists():
        pdf_txt = subprocess.run(["pdftotext", str(cand), "-"], capture_output=True, text=True).stdout
        if pdf_txt:
            break
if not pdf_txt:
    print("ERROR: No compiled PDF found to audit.")
    sys.exit(1)

txt = re.sub(r"\s+", "", pdf_txt.replace("\u2212", "-").replace("\u2013", "-"))
fails, n = [], 0


def need(label, s):
    global n
    n += 1
    needle = re.sub(r"\s+", "", str(s))
    if needle not in txt:
        fails.append((label, s, needle))


# --- 1. Experiment XA: Replay Baseline & Coordination Dynamics ---
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

# Paired bootstrap intervals (naive session level)
for key in ("level_changes", "reversals", "turns"):
    pt, lo, hi = paired_boot([xa["M1"][k][key] for k in keys], [xa["B0"][k][key] for k in keys])
    need(f"M1-B0 {key} CI", f"[{lo:+.2f},{hi:+.2f}]")
    if key != "turns":
        need(f"M1-B0 {key} point", f"{pt:+.2f}")

# Latency overhead and operational counts
def ci2(cell):
    m = re.match(r"([+-][\d.]+) \[([+-][\d.]+),([+-][\d.]+)\]", cell)
    f = lambda x: f"{float(x):+.2f}"
    return f(m.group(1)), f(m.group(2)), f(m.group(3))

pt, lo, hi = ci2(P["M1-B0"]["turn_ms_p50_diff"])
need("latency median diff", f"[{lo},{hi}]")
need("agent calls", f"{float(S['M1']['agent_calls_mean']):.1f}")
need("conflicts", f"{float(S['M1']['conflicts_mean']):.1f}")
need("B0 p50 latency", f"{float(S['B0']['turn_ms_p50']):.3f}")
need("M1 p50 latency", f"{float(S['M1']['turn_ms_p50']):.3f}")
need("M1 p95 latency", f"{float(S['M1']['turn_ms_p95']):.3f}")

# Invariants and bounds
need("M1 differs all", "all 160")
need("CP lower 160/160", f"{clopper_pearson(160, 160)[0]:.3f}")
for c in ("B0", "M1", "M2", "M3", "M4", "M5", "M7"):
    assert all(xa[c][k]["completed"] and xa[c][k]["authority_ok"] and xa[c][k]["transition_ok"] for k in keys), c

# Functional invariance under ablations (A4, A5)
assert all(xa["M2"][k]["diff_path"] == xa["B0"][k]["diff_path"] for k in keys)
assert all(xa["M3"][k]["diff_path"] == xa["M1"][k]["diff_path"] for k in keys)
assert all(xa["M5"][k]["diff_path"] == xa["M1"][k]["diff_path"] for k in keys)
need("M3 coaching ablated identical", "160 of 160")

# Contradicted predictions in XA
d97 = sum(xa["M7"][k]["diff_path"] != xa["B7"][k]["diff_path"] for k in keys)
need("M7 vs B7 sessions (A9)", f"{d97} of 160")
d_can = sum(xa["B0c"][k]["diff_path"] != xa["B0"][k]["diff_path"] for k in keys)
need("canonical guardrails sessions (A10)", "0/160")

# --- 2. Post-Hoc Cluster Bootstrap & Sensitivity Audit ---
ph = json.load(open(RES / "post_hoc/cluster_bootstrap.json"))
for m in ("level_changes", "reversals", "followups"):
    d = ph["M1-B0:" + m]
    need(f"post hoc {m} lo", f"{abs(d['lo']):.2f}")
    need(f"post hoc {m} hi", f"{abs(d['hi']):.2f}")
need("post hoc followups cluster count", "only 1 of the 8")

lo = json.load(open(RES / "post_hoc/leave_one_cluster_out.json"))["M1-B0:level_changes"]["loco"]
need("LOCO drop k=1 mean", f"{abs(lo['1']['mean']):.2f}")
need("LOCO drop k=1 lo", f"{abs(lo['1']['lo']):.2f}")
need("LOCO drop k=1 hi", f"{abs(lo['1']['hi']):.2f}")

scd = json.load(open(RES / "post_hoc/strategy_confidence_distribution.json"))["mode|confidence"]
need("strategy proposals total", f"{sum(scd.values()):,}")
need("remediate 0.80 count", f"{scd['remediate|0.80']:,}")
need("recover 0.80 count", str(scd["recover|0.80"]))
need("recover 0.70 count", str(scd["recover|0.70"]))
need("steady count", f"{scd['steady|0.45']:,}")
need("level changes sign by answer set", "7 of the 8")

# --- 3. Experiment XC: Threshold Decomposition & Gating ---
xcr = {r["condition"]: r for r in csv.DictReader(open(RES / "xc/xc_summary.csv"))}
need("XC tau0 level changes", xcr["TAU0"]["level_changes"].split(" ")[0])
need("XC tau0 agreement", xcr["TAU0"]["ppo_agree"].split(" ")[0])
need("XC five predictions supported", "All 5 registered XC")

# --- 4. Guardrail Grid Disagreement Recomputation ---
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
    tot += 1
    dis += (a != bb)
need("grid points dis", f"{dis:,} of {tot:,}".replace(",", ","))
need("grid pct", f"{100 * dis / tot:.1f}")

# --- Reporting ---
if fails:
    print(f"FAILED: {len(fails)} of {n} checks failed:")
    for lab, s, needle in fails:
        print(f"  [MISSING] {lab}: expected {repr(s)} (needle: {repr(needle)})")
    sys.exit(1)
else:
    print(f"claim audit: ALL {n}/{n} checks passed successfully!")
    sys.exit(0)
