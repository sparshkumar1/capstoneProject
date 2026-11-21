# -*- coding: utf-8 -*-
"""Generate the three poster graphics: system-flow diagram, evaluator
pipeline diagram, and the RL/guardrail ablation bar chart. High-DPI PNGs
with transparent background, sized for clean embedding in an A1 poster."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.font_manager as fm

OUT = r"D:\SystemTemp\claude\D--Capstone-29-AUG-capstoneProject\cbcdaf0a-067f-417a-bca2-5a13c946087b\scratchpad"

NAVY = "#1D2863"
CYAN = "#5FC1DB"
GREEN = "#7CBB00"
PURPLE = "#B098D4"
GREY = "#5A5A5A"
LIGHTGREY = "#E8E8E8"
TEXT_DARK = "#1A1A1A"

plt.rcParams["font.family"] = "DejaVu Sans"


def box(ax, xy, w, h, text, color, fontsize=20.2, textcolor="white", fontweight="bold", sub=None, subsize=15.5):
    x, y = xy
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
                            linewidth=0, facecolor=color, zorder=2)
    ax.add_patch(patch)
    if sub:
        ax.text(x + w / 2, y + h * 0.62, text, ha="center", va="center", fontsize=fontsize,
                 color=textcolor, fontweight=fontweight, zorder=3, wrap=True)
        ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center", fontsize=subsize,
                 color=textcolor, fontweight="normal", zorder=3, wrap=True, style="italic")
    else:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
                 color=textcolor, fontweight=fontweight, zorder=3, wrap=True)


def varrow(ax, x, y1, y2, color=GREY):
    ax.add_patch(FancyArrowPatch((x, y1), (x, y2), arrowstyle="-|>", mutation_scale=22,
                                  linewidth=2.6, color=color, zorder=1, shrinkA=0, shrinkB=0))


def harrow(ax, x1, x2, y, color=GREY):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>", mutation_scale=22,
                                  linewidth=2.6, color=color, zorder=1, shrinkA=0, shrinkB=0))


# =====================================================================
# DIAGRAM 1: System / interview-turn flow
# =====================================================================
fig, ax = plt.subplots(figsize=(9.0, 15.0), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 34)
ax.axis("off")

BW, BH, CX = 8.6, 2.55, 5.0
GAP = 0.55

steps = [
    ("Candidate", None, GREY, "white"),
    ("Topic Selection & Session Init", "React + Vite \u2192 FastAPI Backend", CYAN, "white"),
    ("Adaptive Question Selection", "nearest-difficulty match + topic rotation", CYAN, "white"),
    ("Candidate Answer", "spoken / typed verbal answer  or  C code submission", GREY, "white"),
    ("Whisper Speech Transcription", "+ prosodic confidence / hesitation signals", PURPLE, "white"),
    ("Multi-Component Evaluator", "S1 Sentence-BERT + S2 FAISS + R CrossEncoder", PURPLE, "white"),
    ("FeedbackAgent", "15-field structured feedback\nQwen 2.5 (narrative text only)", PURPLE, "white"),
    ("PPO Policy + 6 Guardrails", "difficulty decision: Easier / Same / Harder", GREEN, "white"),
    ("Performance Report", None, GREY, "white"),
]

y = 33.0 - BH
centers = []
for i, (title, sub, color, tc) in enumerate(steps):
    box(ax, (CX - BW / 2, y), BW, BH, title, color, fontsize=22.3, textcolor=tc, sub=sub, subsize=16.5)
    centers.append(y + BH / 2)
    if i < len(steps) - 1:
        varrow(ax, CX, y, y - GAP)
    y -= (BH + GAP)

# Loop-back arrow: PPO+Guardrails -> Adaptive Question Selection (next question)
loop_x = CX + BW / 2 + 0.55
y_ppo = centers[7]
y_q = centers[2]
ax.add_patch(FancyArrowPatch((CX + BW / 2, y_ppo), (loop_x, y_ppo), arrowstyle="-", linewidth=2.3, color=GREEN))
ax.add_patch(FancyArrowPatch((loop_x, y_ppo), (loop_x, y_q), arrowstyle="-", linewidth=2.3, color=GREEN))
ax.add_patch(FancyArrowPatch((loop_x, y_q), (CX + BW / 2 + 0.05, y_q), arrowstyle="-|>", mutation_scale=20,
                              linewidth=2.3, color=GREEN))
ax.text(loop_x + 0.35, (y_ppo + y_q) / 2, "Next question /\nadaptive follow-up",
        ha="left", va="center", fontsize=15.5, color=GREEN, fontweight="bold", rotation=90)


plt.tight_layout(pad=0.2)
plt.savefig(f"{OUT}/diagram_architecture.png", transparent=True, bbox_inches="tight", pad_inches=0.15)
plt.close()
print("Saved diagram_architecture.png")


# =====================================================================
# DIAGRAM 2: Evaluator pipeline (compact)
# =====================================================================
fig, ax = plt.subplots(figsize=(14.8, 7.0), dpi=300)
ax.set_xlim(0, 14.8)
ax.set_ylim(0, 7)
ax.axis("off")

box(ax, (0.3, 2.6), 2.2, 1.8, "Candidate\nTranscript", GREY, fontsize=18.9)

comp_x = 3.1
comp_w, comp_h = 2.5, 1.55
comps_y = [5.0, 3.075, 1.15]
comps = [
    ("S1 — SBERT", "semantic similarity\nweight 0.15"),
    ("S2 — FAISS", "concept coverage\nweight 0.35"),
    ("R — CrossEncoder", "reasoning quality\nweight 0.50"),
]
for (title, sub), cy in zip(comps, comps_y):
    # fontsize trimmed from 17.6: "R - CrossEncoder" (the longest of the
    # three titles) was crowding the box edges at the original size.
    box(ax, (comp_x, cy), comp_w, comp_h, title, PURPLE, fontsize=16.2, sub=sub, subsize=13.8)
    harrow(ax, 2.5, comp_x, cy + comp_h / 2)

# Defense box spans the full height of the three stacked components so each
# arrow enters cleanly at its own source height instead of converging on a
# single off-center point.
defense_x = comp_x + comp_w + 0.55
defense_bottom, defense_top = comps_y[2], comps_y[0] + comp_h
box(ax, (defense_x, defense_bottom), 2.5, defense_top - defense_bottom,
    "Keyword-Stuffing\nDefense", NAVY, fontsize=16.9, sub="S2 × 0.6 if R ≤ 0.30", subsize=13.8)
for cy in comps_y:
    harrow(ax, comp_x + comp_w, defense_x, cy + comp_h / 2)

final_x = defense_x + 2.5 + 0.55
final_mid = (defense_bottom + defense_top) / 2
box(ax, (final_x, final_mid - 0.9), 3.05, 1.8, "Weighted Sum +\nScore Validator", GREEN, fontsize=16.9,
    sub="0.15·S1 + 0.35·S2,eff\n+ 0.50·R", subsize=13.5)
harrow(ax, defense_x + 2.5, final_x, final_mid)

score_x = final_x + 3.05 + 0.55
box(ax, (score_x, final_mid - 0.9), 1.9, 1.8, "Final\nScore", NAVY, fontsize=19.6)
harrow(ax, final_x + 3.05, score_x, final_mid)

plt.tight_layout(pad=0.2)
plt.savefig(f"{OUT}/diagram_evaluator.png", transparent=True, bbox_inches="tight", pad_inches=0.15)
plt.close()
print("Saved diagram_evaluator.png")


# =====================================================================
# CHART: RL / guardrail ablation (difficulty-tracking MAE, lower = better)
# =====================================================================
fig, ax = plt.subplots(figsize=(7.6, 5.6), dpi=300)
labels = ["Fixed\ndifficulty", "Rule-based\nheuristic", "PPO\n(raw policy)", "PPO +\nguardrails"]
values = [1.200, 0.473, 0.804, 0.677]
colors = [LIGHTGREY, CYAN, "#C9A6E8", GREEN]
bars = ax.bar(labels, values, color=colors, edgecolor=NAVY, linewidth=1.3, width=0.62, zorder=3)
for b, v in zip(bars, values):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.035, f"{v:.3f}", ha="center", va="bottom",
            fontsize=20.2, fontweight="bold", color=TEXT_DARK)
ax.set_ylabel("Difficulty-tracking MAE (lower is better)", fontsize=16.9, color=TEXT_DARK)
ax.set_ylim(0, 1.38)
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color(GREY)
ax.tick_params(axis="x", labelsize=13.5, colors=TEXT_DARK)
ax.tick_params(axis="y", labelsize=11.5, colors=TEXT_DARK)
ax.yaxis.grid(True, linewidth=0.6, color=LIGHTGREY, zorder=0)
ax.set_axisbelow(True)
plt.tight_layout(pad=0.3)
plt.savefig(f"{OUT}/chart_ablation.png", transparent=True, bbox_inches="tight", pad_inches=0.12)
plt.close()
print("Saved chart_ablation.png")
