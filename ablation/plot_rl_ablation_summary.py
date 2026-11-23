"""Render a bar chart of rl_ablation_summary.json (difficulty-tracking
correlation, mean +/- 95% CI, across the four RL/guardrail conditions) and
save it as a .png alongside the source JSON.

Run: .venv/Scripts/python.exe ablation/plot_rl_ablation_summary.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SRC = RESULTS / "rl_ablation_summary.json"
OUT_PNG = RESULTS / "rl_ablation_summary.png"
OUT_SVG = RESULTS / "rl_ablation_summary.svg"

BLUE = "#2a78d6"
MUTED = "#898781"
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

CONDITIONS = ["PPO + Guardrails", "PPO only", "Heuristic only", "Fixed difficulty"]


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))

    labels: list[str] = []
    means: list[float] = []
    cis: list[float] = []
    undefined: list[str] = []

    for cond in CONDITIONS:
        rho = data[cond]["adaptation_rho"]
        if rho["n"] == 0 or rho["mean"] != rho["mean"]:  # NaN check
            undefined.append(cond)
            continue
        labels.append(cond)
        means.append(rho["mean"])
        cis.append(rho["ci95"])

    # Largest effect at the top.
    order = sorted(range(len(labels)), key=lambda i: means[i], reverse=True)
    labels = [labels[i] for i in order]
    means = [means[i] for i in order]
    cis = [cis[i] for i in order]

    n_rows = len(labels) + len(undefined)
    fig_height = 0.75 * n_rows + 1.6
    fig, ax = plt.subplots(figsize=(8.5, fig_height), constrained_layout=True)

    y_positions = list(range(len(labels)))
    ax.barh(y_positions, means, xerr=cis, color=BLUE, height=0.55, zorder=3,
            error_kw={"ecolor": "#0b0b0b", "elinewidth": 1.2, "capsize": 4, "zorder": 4})

    for y, mean, ci in zip(y_positions, means, cis):
        ax.text(mean + ci + 0.015, y, f"{mean:.3f} ± {ci:.3f}", va="center", fontsize=8.5, color="#0b0b0b")

    # Undefined condition(s) shown as a labeled placeholder row rather than
    # silently dropped, since zero-variance Fixed difficulty has no defined
    # correlation (not the same thing as a measured zero).
    all_y = list(y_positions)
    all_labels = list(labels)
    next_y = len(labels)
    for cond in undefined:
        all_y.append(next_y)
        all_labels.append(cond)
        ax.text(0.01, next_y, "ρ undefined — no difficulty variance to correlate against",
                va="center", ha="left", fontsize=8.5, color=MUTED, style="italic")
        next_y += 1

    ax.set_yticks(all_y, labels=all_labels)
    ax.set_ylim(next_y - 0.5, -0.5)
    ax.axvline(0, color="#52514e", linewidth=1.0, zorder=2)
    ax.set_xlabel("Adaptation ρ (difficulty tracking vs. target), mean ± 95% CI")
    ax.set_title("RL/guardrail ablation — difficulty-tracking correlation by condition")
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    xmax = max(m + c for m, c in zip(means, cis)) if means else 1.0
    ax.set_xlim(0, xmax * 1.35)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_SVG, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved -> {OUT_PNG}")
    print(f"Saved -> {OUT_SVG}")


if __name__ == "__main__":
    main()
