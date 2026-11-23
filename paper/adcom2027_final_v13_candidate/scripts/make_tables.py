"""Generate every results table and number macro of the paper from machine-readable outputs. Nothing is typed by hand."""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
RES = HERE.parents[1] / "research/multiagent/results"
T = HERE / "tables"
T.mkdir(exist_ok=True)


def esc(s):
    return str(s).replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("_", "\\_").replace("%", "\\%").replace("#", "\\#")


def rd(p):
    return list(csv.DictReader(open(p)))


def write(name, text):
    (T / name).write_text(text)


macros = {}
# ----------------------------------------------------------------- XA
xs = {r["condition"]: r for r in rd(RES / "xa/xa_summary.csv")}
order = ["B0", "B7", "B0c", "M1", "M2", "M3", "M4", "M5", "M6", "M8", "M7", "M1c"]
rows = []
for c in order:
    r = xs[c]
    rows.append(" & ".join([c, r["completed"].split("/")[0], r["authority_ok"].split("/")[0], r["transition_ok"].split("/")[0], r["level_changes_mean"], r["reversals_mean"],
                            (r["ppo_agree_mean"] or "--"), r["guardrail_fires_mean"], r["strategy_source_mean"], str(r["sessions_with_bypass"]),
                            r["turn_ms_p50"], r["turn_ms_p95"], r.get("agent_calls_mean", "--") or "--"]) + " \\\\")
write("xa_summary.tex", "\\begin{tabular}{lcccrrrrrrrrr}\n\\toprule\nCond. & compl. & auth. & trans. & chg. & rev. & agr. & gfire & strat. & byp. & p50 & p95 & calls\\\\\n\\midrule\n"
      + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
pr = rd(RES / "xa/xa_paired.csv")
rows = []
for r in pr:
    z = lambda v: "0" if v.startswith("+0.000 [+0.000,+0.000]") else v.replace("-", "$-$")
    rows.append(" & ".join([r["comparison"].replace("-", "$-$"), r["frac_sessions_diff_difficulty_path"], z(r["level_changes"]), z(r["reversals"]), z(r["ppo_agree"]), z(r["turn_ms_p50_diff"])]) + " \\\\")
write("xa_paired.tex", "\\begin{tabular}{lrcccc}\n\\toprule\nA$-$B & path$\\ne$ & $\\Delta$ level chg. & $\\Delta$ reversals & $\\Delta$ PPO agree & $\\Delta$ p50 ms\\\\\n\\midrule\n"
      + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def preds(csvp, short):
    rows = []
    for r in rd(csvp):
        rows.append(f"{r['id']} & {esc(short.get(r['id'], r['prediction']))} & {esc(r['verdict'].capitalize())} \\\\")
    return "\\begin{tabular}{lp{7.6cm}l}\n\\toprule\nID & Prediction & Outcome\\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n"


write("xa_pred.tex", preds(RES / "xa/xa_predictions.csv", {}))
for r in rd(RES / "xa/xa_predictions.csv"):
    macros["pred" + r["id"]] = r["verdict"].lower()
macros["xaN"] = xs["B0"]["n_sessions"]
macros["xaMoneMed"] = xs["M1"]["turn_ms_p50"]
macros["xaBzeroMed"] = xs["B0"]["turn_ms_p50"]
macros["xaMoneHigh"] = xs["M1"]["turn_ms_p95"]
macros["xaBzeroHigh"] = xs["B0"]["turn_ms_p95"]
# ----------------------------------------------------------------- XB
if (RES / "xb/xb_cells.csv").exists():
    cells = rd(RES / "xb/xb_cells.csv")
    rows = []
    for r in cells:
        rows.append(" & ".join([esc(r["target"][:5] + ":" + r["fault"]), esc(r["variant"]), r["completed"], r["authority_ok"], r["transition_ok"],
                                r["sessions_with_guardrail_bypass"], r["sessions_with_ungrounded_leak"], r["sessions_with_breaker_open"], r["turn_ms_p95"]]) + " \\\\")
    write("xb_cells.tex", "\\begin{tabular}{llcccrrrr}\n\\toprule\nFault & Variant & compl. & auth. & trans. & byp. & leak & brk. & p95 ms\\\\\n\\midrule\n"
          + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    comp = {}
    for r in cells:
        comp.setdefault((r["target"], r["fault"]), {})[r["variant"]] = r
    rows = []
    for (tg, fl), v in comp.items():
        tot = sum(int(v[x]["completed"].split("/")[0]) for x in v)
        auth = sum(int(v[x]["authority_ok"].split("/")[0]) for x in v)
        trans = sum(int(v[x]["transition_ok"].split("/")[0]) for x in v)
        n = sum(int(v[x]["completed"].split("/")[1]) for x in v)
        rows.append(" & ".join([esc(tg[:5] + ":" + fl), v["full"]["injected_total"], f"{tot}/{n}", f"{auth}/{n}", f"{trans}/{n}",
                                f"{v['full']['sessions_with_guardrail_bypass']} / {v['no_arbitration']['sessions_with_guardrail_bypass']}",
                                f"{v['full']['sessions_with_ungrounded_leak']} / {v['no_grounding']['sessions_with_ungrounded_leak']}",
                                v["full"]["sessions_with_breaker_open"], v["full"]["turn_ms_p95"]]) + " \\\\")
    write("xb_compact.tex", "\\begin{tabular}{lrcccccrr}\n\\toprule\nFault & inj. & compl. & auth. & trans. & bypass & leak & brk. & p95\\\\\n"
          " & (full) & \\multicolumn{3}{c}{all 4 variants} & full/no-arb. & full/no-gr. & full & ms\\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    write("xb_pred.tex", preds(RES / "xb/xb_predictions.csv", {}))
    for r in rd(RES / "xb/xb_predictions.csv"):
        macros["pred" + r["id"]] = r["verdict"].lower()
# ----------------------------------------------------------------- XD
if (RES / "xd/xd_grounding.json").exists():
    d = json.load(open(RES / "xd/xd_grounding.json"))
    rows = []
    for cat, _ in d["ALL"]["categories"].items():
        parts = [esc(cat.replace("_", " ")[:34])]
        for sub in ("ALL", "NO_OVERLAP", "RELABELLED"):
            c = d[sub]["categories"][cat]
            parts.append(f"{c['disagree_with_intended_label']}/{c['applicable']}")
        rows.append(" & ".join(parts) + " \\\\")
    write("xd.tex", "\\begin{tabular}{lccc}\n\\toprule\nCategory & ALL (64) & NO\\_OVERLAP (%d) & RELABELLED (64)\\\\\n\\midrule\n" % d["NO_OVERLAP"]["n_payloads"]
          + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    macros["xdOverlap"] = d["_checks"]["payloads_with_overlap"]
    macros["xdPlaceholder"] = d["_checks"]["payloads_with_placeholder"]
# ----------------------------------------------------------------- XE
if (RES / "xe_e1/xe_e1_reproduction.json").exists():
    e = json.load(open(RES / "xe_e1/xe_e1_reproduction.json"))
    macros["xeEoneIdentical"] = "yes" if e["byte_identical"] else "no"
    macros["xeEoneRows"] = e["rows"]
    macros["xeEoneDiff"] = e["rows_differing"]
if (RES / "xe_b503/xe_b503.json").exists():
    b = json.load(open(RES / "xe_b503/xe_b503.json"))
    for k in ("healthy_fixed", "err503_legacy", "err503_fixed"):
        macros["b503" + k.replace("_", "")] = b[k]["http_attempts_total"]
        macros["b503med" + k.replace("_", "")] = f"{b[k]['turn_s_median']:.3f}"
if (RES / "xe_e5/e5_circuit_breaker.json").exists():
    n5 = json.load(open(RES / "xe_e5/e5_circuit_breaker.json"))
    o5 = json.load(open(HERE.parent / "adcom2027/results/e5_circuit_breaker.json"))
    for sc in ("hang_B", "hang_S_P30", "hang_S_P60", "hang_S_P120", "ok_S_P60", "refuse_S_P60", "recover_S_P60"):
        t = sc.replace("_", "")
        macros["efive" + t + "new"] = f"{n5[sc]['turn_s_median']:.2f}"
        macros["efive" + t + "old"] = f"{o5[sc]['turn_s_median']:.2f}"
        macros["efive" + t + "newtot"] = f"{n5[sc]['turn_s_total']:.1f}"
        macros["efive" + t + "oldtot"] = f"{o5[sc]['turn_s_total']:.1f}"
        macros["efive" + t + "newhttp"] = n5[sc]["http_attempts_total"]
        macros["efive" + t + "oldhttp"] = o5[sc]["http_attempts_total"]
# ----------------------------------------------------------------- XC and post hoc cluster bootstrap
if (RES / "xc/xc_summary.csv").exists():
    import csv as _csv
    xc = list(_csv.DictReader(open(RES / "xc/xc_summary.csv")))
    xp = {r["id"]: r for r in _csv.DictReader(open(RES / "xc/xc_predictions.csv"))}
    lines = []
    for r in xc:
        lines.append(" & ".join([r["tau"], r["level_changes"].split(" ")[0], r["reversals"].split(" ")[0], r["ppo_agree"].split(" ")[0],
                                 r["strategy_source"].split(" ")[0], r["guardrail_fires"].split(" ")[0], r["sessions_with_bypass"]]) + " \\\\")
    write("xc.tex", "\\begin{tabular}{rcccccc}\\toprule\n$\\tau$ & chg. & rev. & agr. & strat. & gfire & byp.\\\\\n\\midrule\n" + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
    for r in xc:
        macros["xc" + r["condition"].lower() + "chg"] = r["level_changes"].split(" ")[0]
        macros["xc" + r["condition"].lower() + "agr"] = r["ppo_agree"].split(" ")[0]
    macros["xcsupported"] = sum(1 for k in ("C1", "C2", "C3", "C4", "C5") if xp[k]["verdict"] == "SUPPORTED")
if (RES / "post_hoc/cluster_bootstrap.json").exists():
    ph = json.load(open(RES / "post_hoc/cluster_bootstrap.json"))
    for m, nm in (("level_changes", "chg"), ("reversals", "rev"), ("followups", "fu"), ("ppo_agree", "agr")):
        d = ph["M1-B0:" + m]
        macros["ph" + nm + "mean"] = (f"{d['mean']:+.2f}" if m != "ppo_agree" else f"{d['mean']:+.3f}").replace("-", "$-$")
        macros["ph" + nm + "ci"] = (f"[{d['lo']:+.2f},{d['hi']:+.2f}]" if m != "ppo_agree" else f"[{d['lo']:+.3f},{d['hi']:+.3f}]").replace("-", "$-$")
        macros["ph" + nm + "same"] = d["clusters_same_sign"]
if (RES / "post_hoc/strategy_confidence_distribution.json").exists():
    sc = json.load(open(RES / "post_hoc/strategy_confidence_distribution.json"))["mode|confidence"]
    macros["scTotal"] = f"{sum(sc.values()):,}".replace(",", "{,}")
    fm = lambda n: f"{n:,}".replace(",", "{,}")
    macros["scRecSeven"] = fm(sc["recover|0.70"]); macros["scRecEight"] = fm(sc["recover|0.80"])
    macros["scRemEight"] = fm(sc["remediate|0.80"]); macros["scSteady"] = fm(sc["steady|0.45"])
    macros["scStretch"] = sum(v for k, v in sc.items() if k.startswith("stretch"))
DIG = dict(zip("0123456789", ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]))


def mname(k):
    """LaTeX control-sequence names may contain letters only: spell out digits."""
    return "".join(DIG.get(ch, ch) for ch in k)


(HERE / "manuscript/numbers.tex").write_text("".join("\\newcommand{\\%s}{%s}\n" % (mname(k), str(v).replace("_", "\\_")) for k, v in sorted(macros.items())))
print("tables and", len(macros), "macros written")
