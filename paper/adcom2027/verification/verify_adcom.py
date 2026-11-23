"""Independent verification of the manuscript numbers.  Recomputes from the raw result files with fresh code (not the analysis
scripts) and compares with the macros in manuscript/numbers.tex; checks citations, labels, macros, and blind-review hygiene."""
import json, math, re, subprocess, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parents[1]
R, M = ROOT / "results", ROOT / "manuscript"
macros = dict(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*?)\}", (M / "numbers.tex").read_text()))
W = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
nm = lambda s: "".join(W[int(c)] if c.isdigit() else c for c in s)
res = []

def check(label, got, want):
    ok = str(got) == str(want)
    res.append((ok, label, got, want))

# --- trace
tr = json.load(open(R / "trace_state_writes.json"))
check("trace turns", tr["turns"], macros["nTurns"]); check("trace followups", tr["followup_turns"], macros["nFU"])
roles = {}
for k, c in tr["writes"].items():
    for r in c: roles.setdefault(r, set()).add(k)
check("evaluator/validator keys", len(roles.get("Evaluator+Validator", ())), 0); check("feedback keys", len(roles.get("FeedbackAgent", ())), 0)
check("followup keys", len(roles.get("FollowUpAgent", ())), 1); check("difficulty keys", len(roles["DifficultyPolicy(PPO+guardrails)"]), 14)
check("hub commit keys", len(roles["Hub:state-commit"]), 22)
check("hub other keys", len(roles["Hub:other"] | roles["Hub:report"] | roles["Hub:question-dispatch"]), 8)
# --- E1 raw recount
rows = [json.loads(l) for l in open(R / "e1_runs.jsonl")]
check("E1 sessions", len(rows), macros["eOneSessions"])
def sel(f, v): return [r for r in rows if r["fault"] == f and r["variant"] == v]
def viol(rs, fn): return f"{sum(fn(r) for r in rs)}/{len(rs)}"
check("F3 V0 I1", viol(sel("F3", "V0"), lambda r: r["I1_committed_without_valid_eval"] > 0), macros["fIIIVzeroSess"])
check("F3 V0 I1 count", sum(r["I1_committed_without_valid_eval"] for r in sel("F3", "V0")), macros["fIIIVzeroCount"])
check("F3 V1 I2", viol(sel("F3", "V1"), lambda r: r["I2_invalid_stored_numbers"] > 0), macros["fIIIVoneIIsess"])
check("F4 V1 I3", viol(sel("F4", "V1"), lambda r: (r["I3_mandatory_violations"] or 0) > 0), macros["fIVVoneSess"])
check("F4 V0 I3 zero", viol(sel("F4", "V0"), lambda r: (r["I3_mandatory_violations"] or 0) > 0), "0/8")
check("F1 V6 I1", viol(sel("F1", "V6"), lambda r: r["I1_committed_without_valid_eval"] > 0), macros["fIVsix"])
check("F2 V6 I1", viol(sel("F2", "V6"), lambda r: r["I1_committed_without_valid_eval"] > 0), macros["fIIVsix"])
check("F2 V0 I4", viol(sel("F2", "V0"), lambda r: not r["I4_terminated"]), macros["fIIVzeroIV"])
check("F0 V5 I4", viol(sel("F0", "V5"), lambda r: not r["I4_terminated"]), macros["fOVfiveIV"])
check("F5 V7 I6", viol(sel("F5", "V7"), lambda r: r["I6_state_inconsistent"]), macros["fVVseven"])
for v in ["V0", "V2", "V3"]:
    check(f"I7 {v}", viol(sel("F0", v), lambda r: r["I7_up_after_low"] > 0), macros[nm(f"sevenSess{v}")])
def reversals(r):
    deltas, prev = [], 2
    for d, s in zip(r["difficulty_path"], r["decision_path"]):
        if s != "baseline_warmup" and d != prev: deltas.append(1 if d > prev else -1)
        prev = d
    return sum(1 for a, b in zip(deltas, deltas[1:]) if a != b)
for v in ["V0", "V2", "V3"]:
    rs = sel("F0", v); check(f"reversals {v}", round(sum(map(reversals, rs)) / len(rs), 2), macros[nm(f"rev{v}")])
src = Counter()
for r in sel("F0", "V0"): src.update(r["decision_sources_rl_phase"])
check("V0 decisions", sum(src.values()), macros["srcVzeroN"]); check("V0 ppo", src["ppo"], macros["srcVzeroPPO"])
check("V0 guardrail", src["guardrail_g1"] + src["guardrail_g3"], macros["srcVzeroG"])
# predictions recount from raw: each (fault,variant,inv,predicted)
P = [("F1","V6","I1",1),("F2","V6","I1",1),("F3","V0","I1",1),("F3","V1","I2",1),("F4","V1","I3",1),("F0","V5","I5",1),("F0","V5","I4",1),
     ("F5","V7","I6",1),("F0","V2","I7",1),("F0","V4","I5",0),("F1","V0","I1",0),("F2","V0","I1",0),("F4","V0","I3",0),("F5","V0","I6",0)]
fn = {"I1": lambda r: r["I1_committed_without_valid_eval"] > 0, "I2": lambda r: r["I2_invalid_stored_numbers"] > 0,
      "I3": lambda r: (r["I3_mandatory_violations"] or 0) > 0, "I4": lambda r: not r["I4_terminated"],
      "I5": lambda r: r["I5_max_followup_run"] > 2, "I6": lambda r: r["I6_state_inconsistent"], "I7": lambda r: r["I7_up_after_low"] > 0}
match = sum((any(fn[i](r) for r in sel(f, v))) == bool(p) for f, v, i, p in P)
check("predictions matched", match, macros["predMatch"]); check("predictions total", len(P), macros["predTotal"])
# --- E3 recompute from the stored scorer payloads + validator
sys.path.insert(0, str(ROOT / "experiments"))
import harness as H
from services.qwen.app import FeedbackRequest, _validate_feedback_output
e3 = json.load(open(R / "e3_grounding.json"))
for cat, v in e3.items():
    check(f"E3 {cat} accepted", v["accepted"], macros[nm(f"eThree{cat.split('_')[0]}acc")])
payloads = [c["raw_eval"] for vv in H.load_cases().values() for c in vv]
faith = 0
for ev in payloads:
    data = {"what_was_correct": [str(c) for c in ev.get("correct_claims", [])], "how_to_answer": "State the mechanism first, then the complexity, then an edge case.",
            "narrative_feedback": "You covered part of the expected reasoning; the gaps listed above should be addressed next."}
    faith += bool(_validate_feedback_output(data, FeedbackRequest(question_text="q", structured_evaluation=ev)))
check("E3 faithful accepted (recomputed)", faith, macros["eThreeCZeroacc"])
ov = sum(1 for ev in payloads if {str(x).lower().strip() for x in ev.get("correct_claims", []) if x} & {str(x).lower().strip() for x in ev.get("missing_concepts", []) if x})
check("evidence self-overlap", ov, macros["overlapN"])
# --- E4 recount
r4 = [json.loads(l) for l in open(R / "e4_runs.jsonl")]
def c4(cell, strict): return [r for r in r4 if r["cell"] == cell and r["strict"] == strict]
check("E4 F6 B sessions", sum(r["I1_committed_without_valid_eval"] > 0 for r in c4("F6", False)), macros["fSixBsess"])
check("E4 F6 B commits", sum(r["I1_committed_without_valid_eval"] for r in c4("F6", False)), macros["fSixBcount"])
check("E4 F6 S sessions", sum(r["I1_committed_without_valid_eval"] > 0 for r in c4("F6", True)), macros["fSixSsess"])
check("E4 F6 S finished", sum(r["I4_terminated"] for r in c4("F6", True)), macros["fSixSdone"])
f0b, f0s = c4("F0", False), c4("F0", True)
same = all(a["committed_scores"] == b["committed_scores"] and a["difficulty_path"] == b["difficulty_path"] and a["followup_flags"] == b["followup_flags"] and a["decision_path"] == b["decision_path"] for a, b in zip(f0b, f0s))
check("E4 F0 identical", "identical" if same else "NOT identical", macros["fOidentical"])
for t, n_ in [("None","None"),("NaN","NaN"),("high","High"),("1.7","Hi"),("-0.3","Lo")]:
    check(f"E4 {t} B commits", sum(r["I1_committed_without_valid_eval"] for r in c4(f"F3each:{t}", False)), macros[f"eFourB{n_}"])
    check(f"E4 {t} S commits", sum(r["I1_committed_without_valid_eval"] for r in c4(f"F3each:{t}", True)), macros[f"eFourS{n_}"])
# --- E2 recount
e2 = json.load(open(R / "e2_handoff_cost.json"))
import statistics
check("E2 hang median", f'{statistics.median(e2["hang"]["turn_s_all"]):.1f}', macros["twoHangMed"])
check("E2 ok median", f'{statistics.median(e2["ok"]["turn_s_all"]):.2f}', macros["twoOkMed"])
check("E2 hang total", f'{sum(e2["hang"]["turn_s_all"]):.0f}', macros["twoHangTotal"])
# --- E5 recount
e5 = json.load(open(R / "e5_circuit_breaker.json"))
check("E5 B median", f'{statistics.median(e5["hang_B"]["turn_s"]):.1f}', macros["fiveMedB"])
check("E5 S60 median", f'{statistics.median(e5["hang_S_P60"]["turn_s"]):.1f}', macros["fiveMedSSixty"])
check("E5 S30 median", f'{statistics.median(e5["hang_S_P30"]["turn_s"]):.1f}', macros["fiveMedSThirty"])
check("E5 S30 total", f'{sum(e5["hang_S_P30"]["turn_s"]):.0f}', macros["fiveTotSThirty"])
check("E5 attempts S60", sum(e5["hang_S_P60"]["http_per_turn"]), macros["fiveAttSSixty"])
check("E5 ok never opens", sum(s != "closed" for s in e5["ok_S_P60"]["breaker_state_after_turn"]), macros["fiveOkOpen"])
check("E5 scores identical across all runs", all(r["committed_scores"] == e5["hang_B"]["committed_scores"] for r in e5.values()), True)
check("E5 recovery delay", next(i for i, s_ in enumerate(e5["recover_S_P60"]["breaker_state_after_turn"]) if i >= 8 and s_ == "closed") - 8, macros["fiveRecoverTurns"])
# --- text hygiene
tex = (M / "main.tex").read_text() + (M / "e5_section.tex").read_text()
bib = (M / "refs.bib").read_text()
cited = set(k for g in re.findall(r"\\cite\{([^}]*)\}", tex) for k in g.split(","))
keys = set(re.findall(r"@\w+\{([^,]+),", bib))
check("citations without bib entry", sorted(cited - keys), "[]"); check("bib entries not cited", sorted(keys - cited), "[]")
used = set(re.findall(r"\\([A-Za-z]+)", tex)); undefined = [m for m in used if m not in macros and m in {k for k in re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", "")}]
labels = set(re.findall(r"\\label\{([^}]*)\}", tex)); refs = set(re.findall(r"\\ref\{([^}]*)\}", tex))
check("refs without label", sorted(refs - labels), "[]"); check("labels never referenced", sorted(l for l in labels - refs if l.startswith(("fig", "tab"))), "[]")
undefined_macros = sorted(m for m in set(re.findall(r"\\((?:[a-z]+(?:Zero|One|Two|Three|Four|Five|Six|Seven|Eight|Nine)[A-Za-z]*|n[A-Z][A-Za-z]*|e[A-Z][A-Za-z]+|f[A-Z][A-Za-z]+|two[A-Z][A-Za-z]*|five[A-Z][A-Za-z]*|pred[A-Z][A-Za-z]*|overlapN|src[A-Z][A-Za-z]*|rev[A-Z][A-Za-z]*|seven[A-Z][A-Za-z]*))", tex)) if m not in macros)
check("undefined number macros", undefined_macros, "[]")
bad = [w for w in ["http://", "https://", "github", "university", "sparsh", "capstone"] if w.lower() in (tex + bib).lower() and w not in ("@",)]
check("identifying strings in source", bad, "[]")

fails = [r for r in res if not r[0]]
for ok, label, got, want in res: print(("PASS " if ok else "FAIL ") + f"{label}: {got}" + ("" if ok else f"  (manuscript/expected {want})"))
print(f"\n{len(res)-len(fails)} PASS, {len(fails)} FAIL")
sys.exit(1 if fails else 0)
