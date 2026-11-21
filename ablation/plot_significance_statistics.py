"""Render a forest plot of significance_statistics.json's evaluator-component
ablation (delta Spearman rho vs. the full composite evaluator, with its
bootstrap 95% CI and significance test) and save it as a .png alongside the
source JSON.

Run: .venv/Scripts/python.exe ablation/plot_significance_statistics.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SRC = RESULTS / "significance_statistics.json"
OUT_PNG = RESULTS / "significance_statistics.png"
OUT_SVG = RESULTS / "significance_statistics.svg"

POSITIVE = "#2a78d6"
NEGATIVE = "#e34948"
NOT_SIG = "#898781"
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
    vs_full = data["evaluator"]["vs_full"]

    # Keep JSON order, plot top-to-bottom in reading order.
    configs = list(vs_full.keys())
    rows = []
    for cfg in configs:
        d = vs_full[cfg]
        rows.append(
            {
                "label": cfg,
                "delta": d["delta_rho"],
                "lo": d["ci95_low"],
                "hi": d["ci95_high"],
                "p": d["p_value"],
            }
        )
    rows.reverse()

    def color_for(r: dict) -> str:
        if r["lo"] > 0:
            return POSITIVE
        if r["hi"] < 0:
            return NEGATIVE
        return NOT_SIG

    def sig_stars(p: float) -> str:
        if p < 0.001:
            return "***"
        if p < 0.01:
            return "**"
        if p < 0.05:
            return "*"
        return "n.s."

    fig_height = 0.62 * len(rows) + 1.8
    fig, ax = plt.subplots(figsize=(9.5, fig_height), constrained_layout=True)

    y_positions = range(len(rows))
    for y, r in zip(y_positions, rows):
        color = color_for(r)
        ax.plot([r["lo"], r["hi"]], [y, y], color=color, linewidth=2.0, zorder=3)
        ax.plot([r["lo"], r["lo"]], [y - 0.12, y + 0.12], color=color, linewidth=2.0, zorder=3)
        ax.plot([r["hi"], r["hi"]], [y - 0.12, y + 0.12], color=color, linewidth=2.0, zorder=3)
        ax.scatter([r["delta"]], [y], color=color, s=70, zorder=4, edgecolor="white", linewidth=0.8)
        label = f"Δρ = {r['delta']:+.3f}  (p = {r['p']:.3g}, {sig_stars(r['p'])})"
        ax.text(r["hi"] + 0.02, y, label, va="center", fontsize=8.5, color="#0b0b0b")

    ax.axvline(0, color="#52514e", linewidth=1.0, zorder=2)
    ax.set_yticks(list(y_positions), labels=[r["label"] for r in rows])
    ax.set_xlabel("Δ Spearman ρ vs. the full composite evaluator (95% CI)")
    ax.set_title("Evaluator component ablation — significance of each configuration's shortfall")
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    all_hi = max(r["hi"] for r in rows)
    all_lo = min(r["lo"] for r in rows)
    span = all_hi - all_lo
    ax.set_xlim(all_lo - 0.05 * span, all_hi + 0.55 * span)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    handles = [
        plt.Line2D([0], [0], marker="o", color=POSITIVE, linestyle="", markersize=8, label="Significant, higher than full"),
        plt.Line2D([0], [0], marker="o", color=NEGATIVE, linestyle="", markersize=8, label="Significant, lower than full"),
        plt.Line2D([0], [0], marker="o", color=NOT_SIG, linestyle="", markersize=8, label="Not significant (CI crosses 0)"),
    ]
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=3,
        frameon=False,
        fontsize=8.5,
    )

    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_SVG, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved -> {OUT_PNG}")
    print(f"Saved -> {OUT_SVG}")


if __name__ == "__main__":
    main()
