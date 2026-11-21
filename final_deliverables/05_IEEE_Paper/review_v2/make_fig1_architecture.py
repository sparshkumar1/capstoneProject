"""Regenerate the PrepAIred architecture figure with a true hub-and-spoke
layout: the orchestrator sits in the centre cell of a 3x3 grid, the eight
other components occupy the eight surrounding cells, and every arrow is a
short, straight spoke from the centre box's edge to one neighbour's edge.
This guarantees no arrow crosses through a third box -- the defect in the
original hand-drawn figure (arrows misaligned, not straight, passing through
blocks).

No connection is drawn between two non-orchestrator boxes, matching the
verified finding (17_Architecture_Audit_Report.md / 24_..._v2.md) that no
component calls another as a peer -- all coordination is orchestrator-
mediated. This is a content-accurate simplification, not just a cosmetic one.

Output: a NEW file (fig1_architecture_v2.png) in this review_v2 folder.
The original final_deliverables/05_IEEE_Paper/IEEE_Figures/fig1_architecture.png
is read, never modified -- it still backs the preserved original paper.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = "fig1_architecture_v2.png"

# category -> colour (kept close to the original legend's palette)
COLORS = {
    "orchestration": "#F4B183",   # orange
    "rl":            "#FFD966",   # yellow
    "feedback_llm":  "#F4A7B9",   # pink
    "io":            "#9DC3E6",   # light blue
    "evaluation":    "#A9D18E",   # green
    "infra":         "#D9D9D9",   # grey
}

# grid cell -> (label, category)   -- row 0 = top, col 0 = left; centre = (1,1)
GRID = {
    (0, 0): ("Frontend UI\n(React / WebSocket)", "io"),
    (0, 1): ("Evaluator\n(S1 + S2 + R)", "evaluation"),
    (0, 2): ("Speech Pipeline\n(STT + prosody)", "evaluation"),
    (1, 0): ("Strategy\n(PPO + guardrails)", "rl"),
    (1, 1): ("Orchestrator\n(session state owner)", "orchestration"),
    (1, 2): ("Feedback LLM\n(Qwen2.5-1.5B, local)", "feedback_llm"),
    (2, 0): ("Code Sandbox\n(isolated container)", "infra"),
    (2, 1): ("Persistence\n(relational store)", "infra"),
    (2, 2): ("Question Bank\n(curated items)", "infra"),
}

BOX_W, BOX_H = 2.15, 0.95
GAP_X, GAP_Y = 1.15, 0.85  # extra space between cell edges, keeps spokes short and clear

def cell_center(row, col):
    x = col * (BOX_W + GAP_X)
    y = -row * (BOX_H + GAP_Y)
    return x, y

fig, ax = plt.subplots(figsize=(7.2, 7.0))
ax.set_aspect("equal")
ax.axis("off")

box_edges = {}  # (row,col) -> (cx, cy, half_w, half_h)
for (row, col), (label, cat) in GRID.items():
    cx, cy = cell_center(row, col)
    box_edges[(row, col)] = (cx, cy, BOX_W / 2, BOX_H / 2)
    box = FancyBboxPatch(
        (cx - BOX_W / 2, cy - BOX_H / 2), BOX_W, BOX_H,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.1, edgecolor="#404040", facecolor=COLORS[cat], zorder=2,
    )
    ax.add_patch(box)
    ax.text(cx, cy, label, ha="center", va="center", fontsize=9.0,
             color="#1a1a1a", zorder=3, linespacing=1.3)

# -- spokes: centre (1,1) <-> every other cell, edge-to-edge, straight, no overlap --
ccx, ccy, chw, chh = box_edges[(1, 1)]
for (row, col), (lx, ly, lhw, lhh) in box_edges.items():
    if (row, col) == (1, 1):
        continue
    dx, dy = lx - ccx, ly - ccy
    # start point: edge of the centre box in the direction of the target
    if dx == 0:
        sx, sy = ccx, ccy + chh * (1 if dy > 0 else -1)
    elif dy == 0:
        sx, sy = ccx + chw * (1 if dx > 0 else -1), ccy
    else:
        sx, sy = ccx + chw * (1 if dx > 0 else -1), ccy + chh * (1 if dy > 0 else -1)
    # end point: edge of the target box in the direction of the centre
    if dx == 0:
        ex, ey = lx, ly - lhh * (1 if dy > 0 else -1)
    elif dy == 0:
        ex, ey = lx - lhw * (1 if dx > 0 else -1), ly
    else:
        ex, ey = lx - lhw * (1 if dx > 0 else -1), ly - lhh * (1 if dy > 0 else -1)

    arrow = FancyArrowPatch(
        (sx, sy), (ex, ey),
        arrowstyle="<|-|>", mutation_scale=11,
        linewidth=1.1, color="#444444", zorder=1,
        shrinkA=2, shrinkB=2,
    )
    ax.add_patch(arrow)

# -- legend --
legend_items = [
    ("Orchestration", COLORS["orchestration"]),
    ("RL policy + guardrails", COLORS["rl"]),
    ("Feedback LLM", COLORS["feedback_llm"]),
    ("IO interface", COLORS["io"]),
    ("Evaluation", COLORS["evaluation"]),
    ("Infrastructure", COLORS["infra"]),
]
handles = [Line2D([0], [0], marker="s", linestyle="", markersize=10,
                   markerfacecolor=c, markeredgecolor="#404040", label=l)
           for l, c in legend_items]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02),
          ncol=3, frameon=False, fontsize=8.0, handletextpad=0.5, columnspacing=1.1)

xs = [c[0] for c in box_edges.values()]
ys = [c[1] for c in box_edges.values()]
ax.set_xlim(min(xs) - BOX_W, max(xs) + BOX_W)
ax.set_ylim(min(ys) - BOX_H * 1.6, max(ys) + BOX_H)

plt.tight_layout()
plt.savefig(OUT, dpi=300, bbox_inches="tight")
print(f"wrote {OUT}")
