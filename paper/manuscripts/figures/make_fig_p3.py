"""Paper 3 figures (descriptive re-plots of frozen files; no new inference, no evaluation-time Same share).

Fig. 1 (fig_p3_equivalence): registered primary interval and the seven sensitivity estimates.
  Sources: research/confirmatory/X3-A/results/x3a_decision.json (primary: two-way cluster bootstrap over
  personas x training seeds, B=10,000, seed 42); research/analysis/x3a_o7/results/x3a_o7_results.json
  (A persona-only bootstrap; B seed-level t interval, df=4; C leave-one-seed-out x5).
  Margins: equivalence +/-0.12; superiority threshold -0.20 (registered in the X3-A protocol).
Fig. 2 (fig_p3_guardrail): accounting of the 1250 PPO+guardrail turns of the five-persona replay.
  Source: research/analysis/phase1/x3_0/x3_0c_replay_turn_log.csv (condition == 'PPO+G'; columns
  activation, override, raw_action, final_action). Counts only.
Fig. 3 (fig_p3_divergence_volatility): (A) stored divergence counts out of 125 PPO+G sessions;
  (B) stored volatility values, five-persona replay.
  Sources: research/analysis/phase1/x3_0/x3_0c_followup.json; x3_0c_replay_summary.csv.
"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _style import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
R = os.path.join(ROOT, "research")
OUT = os.path.dirname(__file__)
setup()

# ---------- Fig 1: equivalence forest
dec = json.load(open(os.path.join(R, "confirmatory", "X3-A", "results", "x3a_decision.json")))
o7 = json.load(open(os.path.join(R, "analysis", "x3a_o7", "results", "x3a_o7_results.json")))
rows = [("Registered primary", dec["point"], dec["ci_low"], dec["ci_high"], "reg"),
        ("Persona-only bootstrap", o7["A"]["point"], o7["A"]["ci_low"], o7["A"]["ci_high"], "sens"),
        ("Seed-level t (df = 4)", o7["B"]["point"], o7["B"]["ci_low"], o7["B"]["ci_high"], "sens")]
for r in o7["C"]["rows"]:
    rows.append((f"Leave out seed {r['removed_seed']}", r["point"], r["ci_low"], r["ci_high"], "sens"))
fig, ax = plt.subplots(figsize=(COL_W, 2.9))
yy = np.arange(len(rows))[::-1]
ax.axvspan(-0.12, 0.12, color="#eef3f8", lw=0, zorder=0)
for x, ls, lab, ha, dx in ((-0.12, "--", "-0.12", "right", -0.004), (0.12, "--", "+0.12", "left", 0.004), (-0.20, ":", "-0.20", "right", -0.004)):
    ax.axvline(x, color=MUTED, lw=0.7, ls=ls, zorder=1)
    ax.text(x + dx, len(rows) - 0.3, lab, fontsize=6, ha=ha, va="bottom", color=MUTED)   # label beside the line, not on it
ax.axvline(0, color=INK, lw=0.5, zorder=1)
for yi, (lab, p, lo, hi, kind) in zip(yy, rows):
    col, mk = (BLUE, "D") if kind == "reg" else (GREEN, "o")
    ax.plot([lo, hi], [yi, yi], color=col, lw=1.3, zorder=2)
    ax.scatter(p, yi, s=22, c=col, marker=mk, zorder=3)
ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows])
ax.set_xlim(-0.25, 0.16); ax.set_ylim(-0.6, len(rows) + 0.2)
ax.set_xlabel("Tracking-MAE difference\n(PPO+guardrail minus Constant-Same+guardrail)", fontsize=6.4)
ax.grid(True, axis="x", lw=0.4)
ax.text(0.0, -0.5, "shaded: equivalence margin", fontsize=5.8, ha="center", color=MUTED)
save(fig, "fig_p3_equivalence", OUT)
print(pd.DataFrame(rows, columns=["analysis", "point", "lo", "hi", "kind"]).round(4).to_string())

# ---------- Fig 2: guardrail accounting
t = pd.read_csv(os.path.join(R, "analysis", "phase1", "x3_0", "x3_0c_replay_turn_log.csv"))
p = t[t.condition == "PPO+G"]
N = len(p); act = int(p.activation.sum()); ovr = int(p.override.sum()); noop = act - ovr
dirs = p[p.override == True].groupby(["raw_action", "final_action"]).size()
seg1 = [("No rule matched", N - act, "#d9d9d9", INK), ("Matched,\nno change", noop, "#9ecae1", INK), ("Overridden", ovr, VERM, "white")]
seg2 = [("Easier>Same\n(blocked\ndecrease)", int(dirs[("Easier", "Same")]), "#f0b48c"),
        ("Same>Easier", int(dirs[("Same", "Easier")]), "#e08a4f"),
        ("Harder>Easier", int(dirs[("Harder", "Easier")]), VERM),
        ("Harder>\nSame", int(dirs[("Harder", "Same")]), "#8f3d00")]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(COL_W, 2.2), gridspec_kw={"height_ratios": [1, 1], "hspace": 0.95})
left = 0
for lab, v, c, tc in seg1:
    a1.barh(0, v, left=left, color=c, edgecolor="white", linewidth=1.2, height=0.55)
    a1.text(left + v / 2, 0, f"{v}", ha="center", va="center", fontsize=6.6, color=tc, fontweight="bold")
    if lab == "Overridden":
        a1.text(N, 0.55, lab, ha="right", va="bottom", fontsize=5.8, color=MUTED)
    else:
        a1.text(left + v / 2, 0.55, lab, ha="center", va="bottom", fontsize=5.8, color=MUTED)
    left += v
a1.set_xlim(0, N); a1.set_ylim(-0.5, 1.05); a1.set_yticks([]); a1.spines["left"].set_visible(False)
a1.set_xlabel(f"Turns (n = {N}); activations {act} = {100*act/N:.1f}%; overrides {ovr} = {100*ovr/N:.1f}%", fontsize=6.0)
left = 0
for lab, v, c in seg2:
    a2.barh(0, v, left=left, color=c, edgecolor="white", linewidth=1.2, height=0.55)
    a2.text(left + v / 2, 0, f"{v}", ha="center", va="center", fontsize=6.6, color="white" if c in (VERM, "#8f3d00", "#e08a4f") else INK, fontweight="bold")
    a2.text(left + v / 2, 0.55, lab, ha="center", va="bottom", fontsize=5.4, color=MUTED)
    left += v
a2.set_xlim(0, ovr); a2.set_ylim(-0.5, 1.4); a2.set_yticks([]); a2.spines["left"].set_visible(False)
a2.set_xlabel(f"The {ovr} overrides, by proposed > final action", fontsize=6.0)
save(fig, "fig_p3_guardrail", OUT)
print(N, act, ovr, noop, dirs.to_dict())

# ---------- Fig 3: divergence + volatility
fu = json.load(open(os.path.join(R, "analysis", "phase1", "x3_0", "x3_0c_followup.json")))
per = fu["per_training_seed[seq,path,mae]"]
sm = pd.read_csv(os.path.join(R, "analysis", "phase1", "x3_0", "x3_0c_replay_summary.csv"))
fig, (a, b) = plt.subplots(1, 2, figsize=(DBL_W, 2.1), gridspec_kw={"width_ratios": [1, 1.15], "wspace": 0.55})
labs = ["Final-action sequence\ndiffers", "Executed difficulty path\n(after clipping) differs", "Session MAE\ndiffers"]
tot = [fu["final_action_sequence_differs"], fu["executed_difficulty_path_differs"], fu["session_mae_differs"]]
yv = np.arange(3)[::-1]
a.barh(yv, tot, color=[BLUE, "#56a0d3", "#a9cce8"], height=0.5)
for yi, v in zip(yv, tot):
    a.text(v + 1, yi, f"{v} / {fu['n_sessions']}", va="center", fontsize=6.6, fontweight="bold")
a.set_yticks(yv); a.set_yticklabels(labs); a.set_xlim(0, 70)
a.set_xlabel("PPO+G sessions differing from Constant-Same+G\n(five-persona replay, 125 sessions)", fontsize=6.4)
a.grid(True, axis="x", lw=0.4)
# B: volatility per training seed
seeds = ["42", "123", "456", "789", "999"]
pg = sm[(sm.condition == "PPO+G") & sm.training_seed.isin(seeds)].set_index("training_seed").volatility
pr = sm[(sm.condition == "PPO raw") & sm.training_seed.isin(seeds)].set_index("training_seed").volatility
pool = {"PPO+G": sm[(sm.condition == "PPO+G") & (sm.training_seed == "pooled 5 seeds")].volatility.iloc[0],
        "PPO raw": sm[(sm.condition == "PPO raw") & (sm.training_seed == "pooled 5 seeds")].volatility.iloc[0]}
cs = sm[sm.condition == "Constant-Same+G"].volatility.iloc[0]
b.axvline(cs, color=MUTED, lw=0.8, ls="--", zorder=0)
b.text(cs + 0.004, 1.55, f"Constant-Same+G\n{cs:.3f}", fontsize=5.8, color=MUTED, va="top")
for yi, (name, ser, col, mk) in zip([1, 0], [("PPO+G", pg, VERM, "o"), ("PPO raw", pr, BLUE, "s")]):
    b.scatter(ser.values, [yi] * 5, s=14, c=col, marker=mk, alpha=0.75, zorder=2, label=None)
    b.scatter([pool[name]], [yi], s=46, facecolor="white", edgecolor=col, marker="D", linewidth=1.1, zorder=3)
    b.text(pool[name], yi + 0.22, f"pooled {pool[name]:.4f}", fontsize=6, ha="center", color=INK, zorder=4,
           bbox=dict(facecolor="white", edgecolor="none", pad=1.2))   # keeps the dashed reference line from striking through the label
b.set_yticks([1, 0]); b.set_yticklabels(["PPO with\nguardrails", "PPO without\nguardrails"]); b.set_ylim(-0.5, 1.6)
b.set_xlim(0, 0.32); b.set_xlabel("Volatility: mean absolute difficulty change per turn\n(small marks = training seeds; diamond = pooled)", fontsize=6.4)
b.grid(True, axis="x", lw=0.4)
save(fig, "fig_p3_divergence_volatility", OUT)
print(pg.to_dict(), pr.to_dict(), pool, cs)
