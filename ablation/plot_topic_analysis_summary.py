"""Render a grouped bar chart of topic_analysis_summary.json (human vs.
system average score, per topic) and save it as a .png alongside the source
JSON.

Run: .venv/Scripts/python.exe ablation/plot_topic_analysis_summary.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SRC = RESULTS / "topic_analysis_summary.json"
OUT_PNG = RESULTS / "topic_analysis_summary.png"
OUT_SVG = RESULTS / "topic_analysis_summary.svg"

# Categorical slots 1 and 2 from the project's validated chart palette.
HUMAN = "#2a78d6"
SYSTEM = "#eb6834"
GRID = "#e1e0d9"

plt.rcParams.update(
    {
        "figure.dpi": 160,
        "savefig.dpi": 300,
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
)


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    topics = data["topics"]

    labels = [t["topic"] for t in topics]
    human = [t["avg_human_score"] for t in topics]
    system = [t["avg_system_score"] for t in topics]
    n_ratings = [t["ratings"] for t in topics]

    x = np.arange(len(labels))
    width = 0.34

    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)

    bars_h = ax.bar(x - width / 2, human, width, color=HUMAN, label="Human rater score", zorder=3)
    bars_s = ax.bar(x + width / 2, system, width, color=SYSTEM, label="System (evaluator) score", zorder=3)

    for bars in (bars_h, bars_s):
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.015,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=8.5,
                color="#0b0b0b",
            )

    xtick_labels = [f"{label}\n(n={n})" for label, n in zip(labels, n_ratings)]
    ax.set_xticks(x, labels=xtick_labels)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Average score (0–1)")
    ax.set_title("Evaluator vs. human score by topic")
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", frameon=False, fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_SVG, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved -> {OUT_PNG}")
    print(f"Saved -> {OUT_SVG}")


if __name__ == "__main__":
    main()
