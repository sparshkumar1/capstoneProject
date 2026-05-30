"""Generate evaluator comparison and coverage figures."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ablation_evaluator import load_answers
from services.evaluator.app import evaluate, get_rubric


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


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


def build_score_rows() -> list[dict]:
    answers = load_answers(ROOT / "data" / "ablation_answers.json")
    rows: list[dict] = []
    for item in answers:
        rubric = get_rubric(str(item.get("qid", "")).strip())
        if not rubric:
            continue
        result = evaluate(item.get("answer", ""), rubric.get("answer", ""), rubric)
        rows.append({
            "qid": str(item.get("qid", "")).strip(),
            "topic": item.get("topic", "Unknown"),
            "quality_label": item.get("quality_label", "unknown"),
            "final_score": float(result.get("final_score", float("nan"))),
            "s2": float(result.get("S2_structural", float("nan"))),
            "s1": float(result.get("S1_semantic", float("nan"))),
        })
    return rows


def render_heatmap(ax, matrix: np.ndarray, row_labels: list[str], col_labels: list[str], title: str, cbar_label: str) -> None:
    im = ax.imshow(matrix, cmap="viridis", vmin=0.0, vmax=1.0)
    ax.set_xticks(np.arange(len(col_labels)), labels=col_labels, rotation=20, ha="right")
    ax.set_yticks(np.arange(len(row_labels)), labels=row_labels)
    ax.set_title(title)
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)
    ax.set_xlabel("Quality bucket")
    ax.set_ylabel("Topic")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            text_color = "white" if value >= 0.6 else "black"
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=text_color, fontsize=8)
    return im


def main() -> None:
    score_rows = build_score_rows()
    if not score_rows:
        raise SystemExit("No answer rows available for coverage figure.")

    comparison_path = RESULTS / "evaluator_ablation_summary.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    ranking = comparison.get("results", [])

    # Comparison panel
    fig, (ax_bar, ax_heat1, ax_heat2) = plt.subplots(
        1,
        3,
        figsize=(16, 5.3),
        constrained_layout=True,
        gridspec_kw={"width_ratios": [1.1, 1, 1]},
    )
    configs = [item["config"] for item in ranking]
    rhos = [float(item["spearman_rho"]) for item in ranking]
    bars = ax_bar.barh(configs, rhos, color="#2a6fdb")
    ax_bar.invert_yaxis()
    ax_bar.set_xlim(0, 1.0)
    ax_bar.set_xlabel("Spearman ρ")
    ax_bar.set_title("Evaluator comparison")
    ax_bar.grid(axis="x", alpha=0.2)
    for bar, rho in zip(bars, rhos):
        ax_bar.text(rho + 0.01, bar.get_y() + bar.get_height() / 2, f"{rho:.3f}", va="center", fontsize=8)

    topics = sorted({row["topic"] for row in score_rows})
    labels = ["blank", "off-topic", "partial", "good"]
    mean_s2 = np.zeros((len(topics), len(labels)), dtype=float)
    mean_score = np.zeros_like(mean_s2)

    grouped = defaultdict(list)
    for row in score_rows:
        grouped[(row["topic"], row["quality_label"])] += [row]

    for i, topic in enumerate(topics):
        for j, label in enumerate(labels):
            items = grouped.get((topic, label), [])
            if items:
                mean_s2[i, j] = float(np.mean([item["s2"] for item in items]))
                mean_score[i, j] = float(np.mean([item["final_score"] for item in items]))
            else:
                mean_s2[i, j] = float("nan")
                mean_score[i, j] = float("nan")

    # Replace NaNs with 0 for display but keep as NaN in annotations
    s2_display = np.nan_to_num(mean_s2, nan=0.0)
    score_display = np.nan_to_num(mean_score, nan=0.0)

    im1 = render_heatmap(ax_heat1, s2_display, topics, labels, "Mean concept coverage (S2)", "S2")
    im2 = render_heatmap(ax_heat2, score_display, topics, labels, "Mean final score", "Score")
    cbar1 = fig.colorbar(im1, ax=ax_heat1, fraction=0.046, pad=0.04)
    cbar1.set_label("S2")
    cbar2 = fig.colorbar(im2, ax=ax_heat2, fraction=0.046, pad=0.04)
    cbar2.set_label("Score")

    png_path = RESULTS / "comparison_and_coverage.png"
    svg_path = RESULTS / "comparison_and_coverage.svg"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "comparison": ranking,
        "coverage": {
            "topics": topics,
            "labels": labels,
            "mean_s2": s2_display.tolist(),
            "mean_final_score": score_display.tolist(),
        },
    }
    (RESULTS / "comparison_and_coverage_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_lines = [
        "# Comparison and coverage summary",
        "",
        "## Evaluator ranking",
        "",
        "| Config | Spearman ρ | p-value |",
        "| --- | --- | --- |",
    ]
    for item in ranking:
        md_lines.append(f"| {item['config']} | {item['spearman_rho']:.4f} | {item['p_value']:.4g} |")
    md_lines += ["", "## Coverage matrix", "", "Topics: " + ", ".join(topics), "", "Labels: blank / off-topic / partial / good"]
    (RESULTS / "comparison_and_coverage_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Saved → {png_path}")
    print(f"Saved → {svg_path}")
    print(f"Saved → {RESULTS / 'comparison_and_coverage_summary.md'}")
    print(f"Saved → {RESULTS / 'comparison_and_coverage_summary.json'}")


if __name__ == "__main__":
    main()