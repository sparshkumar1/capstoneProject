"""Paper 1, Fig. 1: per-run containment outcomes for X1-C on the repaired SUT (v2).

Sources (read-only):
  research/confirmatory/X1/results/x1c_v2/runs.jsonl   (per-run criteria_met, one record per run)
  research/confirmatory/X1/results/x1c_v2/results.csv  (per-run executor status)
Calculation: none beyond reading. A blue dot is a shipped-configuration run that met all prespecified
criteria; a vermillion cross is a permissive-control run whose criteria failed (breach detected).
'Executor status shipped vs. permissive' is 'identical' when the set of executor status strings in the
shipped runs equals the set in the permissive runs. Benign row: 5 shipped + 5 permissive-all runs, all accepted.
The baseline SUT (x1c/) gave identical counts.
"""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _style import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RES = os.path.join(ROOT, "research", "confirmatory", "X1", "results", "x1c_v2")
OUT = os.path.dirname(__file__)

runs = pd.read_csv(os.path.join(RES, "results.csv"))
perrun = {}
for line in open(os.path.join(RES, "runs.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    perrun.setdefault((r["attack"], r["config"]), []).append(bool(r["criteria_met"]))

SHORT = {"SEC-01": "ptrace", "SEC-02": "socket + connect", "SEC-03": "syntax error", "SEC-04": "SIGSEGV",
         "SEC-05": "CPU loop", "SEC-06": "memory", "SEC-07": "exfiltration", "SEC-08": "fork attempts",
         "SEC-09": "filesystem write", "BEN": "benign program"}
keys = [f"SEC-0{i}" for i in range(1, 10)] + ["BEN"]
rows = []
for a in keys:
    sh = set(runs[(runs.attack == a) & (runs.config == "shipped")].status)
    pe = set(runs[(runs.attack == a) & (runs.config == "permissive")].status)
    same = "n/a" if not pe else ("same" if sh == pe else "differs")
    rows.append((a, sorted(sh)[0], sorted(pe)[0] if pe else "", same))

setup()
fig, ax = plt.subplots(figsize=(DBL_W, 2.9))
n = len(rows)
ax.set_xlim(0, 100); ax.set_ylim(n + 0.9, -1.4); ax.axis("off")
X_SH, X_PE, X_EQ, X_ST = 25, 43, 59, 66
hdr = dict(fontsize=6.4, fontweight="bold", va="center")
ax.text(1, -0.9, "Attack program", **hdr)
ax.text(X_SH + 3.2, -0.9, "Shipped\n(criteria met)", ha="center", **hdr)
ax.text(X_PE + 3.2, -0.9, "Permissive control\n(breach detected)", ha="center", **hdr)
ax.text(X_EQ, -0.9, "Executor status\nsame in both?", ha="left", **hdr)
ax.text(X_ST + 9, -0.9, "Status string(s)", ha="left", **hdr)
ax.plot([0, 100], [-0.3, -0.3], color=MUTED, lw=0.6)
for i, (a, s_sh, s_pe, same) in enumerate(rows):
    y = i + 0.35
    if i % 2 == 0:
        ax.axhspan(y - 0.5, y + 0.5, color="#f3f3f1", lw=0)
    ax.text(1, y, f"{a}  {SHORT[a]}", va="center", fontsize=6.6)
    sh = perrun.get((a, "shipped"), []) + (perrun.get((a, "permissive-all"), []) if a == "BEN" else [])
    for k, ok in enumerate(sh):
        ax.plot(X_SH + k * 1.6, y, "o", ms=4.0, mfc=BLUE if ok else "white", mec=BLUE, mew=0.9)
    pe = perrun.get((a, "permissive"), [])
    if pe:
        for k, met in enumerate(pe):
            breach = not met
            ax.plot(X_PE + k * 1.6, y, "X" if breach else "o", ms=4.6 if breach else 4.0,
                    mfc=VERM if breach else "white", mec=VERM, mew=0.6 if breach else 0.9)
    else:
        ax.text(X_PE + 4, y, "no control" if a != "BEN" else "(in shipped cell)", fontsize=6.0,
                color=MUTED, ha="center", va="center", style="italic")
    if same == "same":
        ax.text(X_EQ, y, "identical", fontsize=6.4, color=VERM, fontweight="bold", va="center")
    elif same == "differs":
        ax.text(X_EQ, y, "differs", fontsize=6.4, color=MUTED, va="center")
    else:
        ax.text(X_EQ, y, "-", fontsize=6.4, color=MUTED, va="center")
    label = f"{s_sh}  |  {s_pe}" if s_pe else s_sh
    ax.text(X_ST + 9, y, label, fontsize=6.1, va="center")
y0 = n + 0.25
ax.plot(2, y0, "o", ms=4.0, mfc=BLUE, mec=BLUE)
ax.text(3.4, y0, "shipped run met all criteria", fontsize=6.0, va="center", color=MUTED)
ax.plot(29, y0, "X", ms=4.6, mfc=VERM, mec=VERM, mew=0.6)
ax.text(30.4, y0, "permissive run breached", fontsize=6.0, va="center", color=MUTED)
ax.text(62, y0, "Repaired SUT, 5 runs per cell; baseline SUT identical.",
        fontsize=6.0, va="center", color=MUTED)
save(fig, "fig_p1_containment_matrix", OUT)
print(pd.DataFrame(rows, columns=["attack", "shipped_status", "permissive_status", "status_same"]).to_string())
