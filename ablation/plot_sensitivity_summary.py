"""Render a tornado chart of sensitivity_summary.json's delta-from-baseline
results (adaptation rho, the project's primary difficulty-tracking metric)
and save it as a .png alongside the source JSON.

Run: .venv/Scripts/python.exe ablation/plot_sensitivity_summary.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SRC = RESULTS / "sensitivity_summary.json"
OUT_PNG = RESULTS / "sensitivity_summary.png"
OUT_SVG = RESULTS / "sensitivity_summary.svg"

# Diverging pair from the project's validated chart palette: blue <-> red,
# used here for polarity (improves vs. degrades difficulty-tracking rho
# relative to each group's own frozen baseline).
POSITIVE = "#2a78d6"
NEGATIVE = "#e34948"
BASELINE_GRAY = "#898781"
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

    rows: list[dict] = []
    for group, variants in data.items():
        for variant in variants:
            delta = variant["delta_from_baseline"]["adaptation_rho"]
            note = variant["note"]
            rows.append(
                {
                    "group": group,
                    "label": variant["label"],
                    "is_baseline": note in ("Baseline frozen design", "Current simplified reward"),
                    "delta": delta,
                }
            )

    # Preserve JSON order (groups, then variants within each group), baseline
    # row first in each group for reference, then variants by |delta|.
    ordered: list[dict] = []
    for group in data.keys():
        group_rows = [r for r in rows if r["group"] == group]
        baseline_rows = [r for r in group_rows if r["is_baseline"]]
        variant_rows = sorted(
            (r for r in group_rows if not r["is_baseline"]),
            key=lambda r: abs(r["delta"]),
            reverse=True,
        )
        ordered.extend(baseline_rows + variant_rows)

    # Plot top-to-bottom in reading order (first group at top).
    ordered.reverse()

    fig_height = 0.52 * len(ordered) + 1.6
    fig, ax = plt.subplots(figsize=(9.5, fig_height), constrained_layout=True)

    y_positions = range(len(ordered))
    colors = [
        BASELINE_GRAY if r["is_baseline"] else (POSITIVE if r["delta"] >= 0 else NEGATIVE)
        for r in ordered
    ]
    deltas = [r["delta"] for r in ordered]

    bars = ax.barh(y_positions, deltas, color=colors, height=0.62, zorder=3)

    ax.axvline(0, color="#52514e", linewidth=1.0, zorder=2)
    ax.set_xlabel("Δ adaptation ρ vs. that group's own baseline")
    ax.set_title("Sensitivity analysis — effect on difficulty-tracking correlation (ρ)")
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    # Explicit, padded x-limits set before any text is placed, so bar-end
    # value labels (and the group-name text at the right edge) always have
    # clear space and never overlap a y-tick label or each other.
    data_min = min(deltas + [0.0])
    data_max = max(deltas + [0.0])
    span = max(data_max - data_min, 0.02)
    ax.set_xlim(data_min - 0.28 * span, data_max + 0.28 * span)

    labels = [r["label"] + ("  (baseline)" if r["is_baseline"] else "") for r in ordered]
    ax.set_yticks(list(y_positions), labels=labels)

    # Section separators + group names, one boundary per group.
    seen_ranges: dict[str, list[int]] = {}
    for i, r in enumerate(ordered):
        seen_ranges.setdefault(r["group"], []).append(i)

    xmin, xmax = ax.get_xlim()
    pad = (xmax - xmin) * 0.02
    for group, idxs in seen_ranges.items():
        top = max(idxs)
        bottom = min(idxs)
        if bottom > 0:
            ax.axhline(bottom - 0.5, color=GRID, linewidth=1.0, zorder=1)
        ax.text(
            xmax - pad,
            top + 0.5,
            group,
            ha="right",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#52514e",
        )

    # Value labels sit just inside each bar's outer end (not beyond it), so a
    # long bar's label can never overlap the y-axis tick labels in the margin.
    inset = 0.012 * span
    for bar, delta in zip(bars, deltas):
        if delta == 0.0:
            continue
        label_x = delta - inset if delta >= 0 else delta + inset
        ha = "right" if delta >= 0 else "left"
        ax.text(
            label_x,
            bar.get_y() + bar.get_height() / 2,
            f"{delta:+.3f}",
            va="center",
            ha=ha,
            fontsize=8,
            color="white",
            fontweight="bold",
        )

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
