"""Generate manuscript/numbers.tex from the stored result files. Every number in the manuscript text is a macro defined here."""
import csv, json
from pathlib import Path
R = Path(__file__).parents[1] / "results"
out = {}

W = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]


def put(name, val):
    name = "".join(W[int(c)] if c.isdigit() else c for c in name)
    out[name] = val

tr = json.load(open(R / "trace_state_writes.json"))
put("nTurns", tr["turns"]); put("nFU", tr["followup_turns"]); put("nSess", tr["sessions"]); put("nPrimary", tr["turns"] - tr["followup_turns"])
# E1
rows = [json.loads(l) for l in open(R / "e1_runs.jsonl")]
put("eOneSessions", len(rows))
cells = list(csv.DictReader(open(R / "e1_cells.csv")))
def cell(f, v, inv):
    for c in cells:
        if (c["fault"], c["variant"], c["invariant"]) == (f, v, inv): return c
    raise KeyError((f, v, inv))
def frac(c): return f'{c["sessions_violating"]}/{c["sessions"]}'
put("fIIIVzeroSess", frac(cell("F3", "V0", "I1"))); put("fIIIVzeroCount", cell("F3", "V0", "I1")["total_violation_count"])
put("fIIIVoneIIsess", frac(cell("F3", "V1", "I2"))); put("fIIIVoneIICount", cell("F3", "V1", "I2")["total_violation_count"])
put("fIVVoneSess", frac(cell("F4", "V1", "I3"))); put("fIVVoneCount", cell("F4", "V1", "I3")["total_violation_count"])
put("fVVseven", frac(cell("F5", "V7", "I6")))
put("fOVfiveIV", frac(cell("F0", "V5", "I4"))); put("fOVfiveV", frac(cell("F0", "V5", "I5")))
put("fIVsix", frac(cell("F1", "V6", "I1"))); put("fIVsixCount", cell("F1", "V6", "I1")["total_violation_count"])
put("fIIVsix", frac(cell("F2", "V6", "I1"))); put("fIIVsixCount", cell("F2", "V6", "I1")["total_violation_count"])
put("fIIVzeroIV", frac(cell("F2", "V0", "I4")))
put("fIVzeroIV", frac(cell("F1", "V0", "I4")))
for v in ["V0", "V1", "V2", "V3", "V4", "V6", "V7"]:
    c = cell("F0", v, "I7"); put(f"sevenSess{v}", frac(c)); put(f"sevenCount{v}", c["total_violation_count"])
preds = list(csv.DictReader(open(R / "e1_predictions.csv")))
put("predTotal", len(preds)); put("predMatch", sum(p["match"] == "yes" for p in preds))
rev = {r["variant"]: r for r in csv.DictReader(open(R / "e1_reversals_exploratory.csv"))}
for v in rev: put(f"rev{v}", rev[v]["mean_reversals"]); put(f"chg{v}", rev[v]["mean_changes"])
src = json.load(open(R / "e1_decision_sources.json"))
put("srcVzeroG", src["V0"].get("guardrail_g1", 0) + src["V0"].get("guardrail_g3", 0)); put("srcVzeroPPO", src["V0"]["ppo"])
put("srcVzeroN", sum(src["V0"].values())); put("srcVzeroGone", src["V0"].get("guardrail_g1", 0))
# E3
e3 = json.load(open(R / "e3_grounding.json"))
for k, v in e3.items():
    key = k.split("_")[0]
    put(f"eThree{key}acc", v["accepted"]); put(f"eThree{key}n", v["applicable"]); put(f"eThree{key}rej", v["rejected"])
ov = json.load(open(R / "e3_evidence_overlap.json"))
put("overlapN", ov["payloads_with_any_overlap"])
# E4
c4 = list(csv.DictReader(open(R / "e4_cells.csv")))
def c4g(cell_, var): 
    for c in c4:
        if c["cell"] == cell_ and c["variant"].startswith(var): return c
put("fSixBsess", c4g("F6", "B")["sessions_with_invalid_commit"]); put("fSixBn", c4g("F6", "B")["sessions"]); put("fSixBcount", c4g("F6", "B")["invalid_commits"])
put("fSixSsess", c4g("F6", "S")["sessions_with_invalid_commit"]); put("fSixSdone", c4g("F6", "S")["sessions_terminated"]); put("fSixBdone", c4g("F6", "B")["sessions_terminated"])
put("fSixBans", c4g("F6", "B")["mean_committed_answers"]); put("fSixSans", c4g("F6", "S")["mean_committed_answers"])
for t, nm in [("None", "None"), ("NaN", "NaN"), ("high", "High"), ("1.7", "Hi"), ("-0.3", "Lo")]:
    b = c4g(f"F3each:{t}", "B"); s = c4g(f"F3each:{t}", "S")
    put(f"eFourB{nm}", b["invalid_commits"]); put(f"eFourS{nm}", s["invalid_commits"]); put(f"eFourS{nm}done", s["sessions_terminated"])
put("fOidentical", "identical" if json.load(open(R / "e4_f0_identity.json"))["F0_paths_identical_B_vs_S"] else "NOT identical")
# E2
e2 = json.load(open(R / "e2_handoff_cost.json"))
put("twoOkMed", f'{e2["ok"]["turn_s_median"]:.2f}'); put("twoRefMed", f'{e2["refuse"]["turn_s_median"]:.2f}'); put("twoHangMed", f'{e2["hang"]["turn_s_median"]:.1f}')
put("twoHangTotal", f'{e2["hang"]["turn_s_total"]:.0f}'); put("twoHangMax", f'{e2["hang"]["turn_s_max"]:.1f}'); put("twoTurns", e2["hang"]["turns"])
put("twoRefTotal", f'{e2["refuse"]["turn_s_total"]:.1f}'); put("twoOkTotal", f'{e2["ok"]["turn_s_total"]:.1f}')
put("twoHangAtt", e2["hang"]["http_attempts_total"]); put("twoRefAtt", e2["refuse"]["http_attempts_total"]); put("twoOkAtt", e2["ok"]["http_attempts_total"])
# E5
e5 = json.load(open(R / "e5_circuit_breaker.json"))
names = {"hang_B": "B", "hang_S_P30": "SThirty", "hang_S_P60": "SSixty", "hang_S_P120": "SOneTwenty", "ok_S_P60": "Ok", "refuse_S_P60": "Refuse", "recover_S_P60": "Recover"}
for n, k in names.items():
    r = e5[n]
    put(f"fiveMed{k}", f'{r["turn_s_median"]:.1f}' if r["turn_s_median"] >= 1 else f'{r["turn_s_median"]:.2f}')
    put(f"fiveTot{k}", f'{r["turn_s_total"]:.0f}'); put(f"fiveAtt{k}", r["http_attempts_total"]); put(f"fiveMax{k}", f'{r["turn_s_max"]:.1f}')
base = e5["hang_B"]["committed_scores"]
put("fiveSameScores", "identical" if all(r["committed_scores"] == base for r in e5.values()) else "differ")
put("fiveOkOpen", sum(1 for st in e5["ok_S_P60"]["breaker_state_after_turn"] if st != "closed"))
rec = e5["recover_S_P60"]
put("fiveRecoverTurns", next(i for i, st in enumerate(rec["breaker_state_after_turn"]) if i >= 8 and st == "closed") - 8)
put("fiveFirstTurn", f'{e5["hang_S_P60"]["turn_s"][0]:.1f}')
put("fiveRefuseAttB", e2["refuse"]["http_attempts_total"])
with open(Path(__file__).parents[1] / "manuscript" / "numbers.tex", "w") as f:
    f.write("% generated by verification/make_numbers.py from results/*.json|csv\n")
    for k, v in out.items():
        f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
print(len(out), "macros")
