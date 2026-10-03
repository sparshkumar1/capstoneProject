"""Figure 1: hub-and-spoke architecture with the authority partition (drawn from the traced write-set, results/trace_state_writes.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W = json.loads((Path(__file__).parents[1] / "results" / "trace_state_writes.json").read_text())
fig, ax = plt.subplots(figsize=(6.4, 3.9), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis("off")
GREY, LIGHT, DARK = "#dddddd", "#f2f2f2", "#222222"


def box(x, y, w, h, text, fc=LIGHT, ls="-", lw=0.9, fs=6.6, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8", fc=fc, ec=DARK, lw=lw, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=DARK, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(p, q, text="", dashed=False, fs=5.6, off=(0, 0.9)):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=7, lw=0.8, color=DARK, ls="--" if dashed else "-"))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="bottom", fontsize=fs, color=DARK)

box(36, 22, 28, 18, "Hub\n(InterviewOrchestrator)\none session lock,\nsole writer of scores,\nanswers, history", fc=GREY, bold=True, fs=6.8)
box(2, 46, 24, 12, "Evaluator\n(SBERT+FAISS+\ncross-encoder)\nno generation")
box(2, 26, 24, 10, "Score validator\n(rules: cap 0.65,\npenalty \u2264 0.25)")
box(72, 46, 22, 12, "Follow-up role\npolicy (cap 2) +\nLLM text or template")
box(72, 26, 22, 10, "Feedback role\nLLM text or template\n(grounding check)")
box(38, 2, 24, 12, "Difficulty policy\nPPO (frozen) then\nguardrails G1\u2013G6")
box(2, 4, 24, 9, "Timer, question\nselector, C sandbox", fs=6.2)
box(72, 4, 22, 9, "Qwen service\n(LLM, optional)\nHTTP, 6 s timeout", ls="--", fs=6.2)
arrow((14, 46), (14, 36), "payload", off=(5, -1))
arrow((26, 31), (36, 31), "score", off=(0, 0.7))
arrow((72, 52), (60, 40), "queue insert", off=(2, 1.2))
arrow((72, 31), (64, 31), "text only", off=(0, 0.7))
arrow((50, 14), (50, 22), "difficulty", off=(4.5, -1))
arrow((26, 10), (38, 28), "", off=(0, 0))
arrow((83, 13), (83, 26), "", dashed=True)
ax.plot([94, 97], [8.5, 8.5], color=DARK, lw=0.8, ls="--")
ax.plot([97, 97], [8.5, 52], color=DARK, lw=0.8, ls="--")
arrow((97, 52), (94.2, 52), "", dashed=True)
fig.savefig(Path(__file__).parent / "fig1_architecture.pdf", bbox_inches="tight")
fig.savefig(Path(__file__).parent / "fig1_architecture.png", bbox_inches="tight")
print("ok")
