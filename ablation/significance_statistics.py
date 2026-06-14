"""Emit the current ablation significance summary in JSON and Markdown form.

The repository already contains a verified `results/significance_statistics.json`
artifact generated from the curated evaluation run. This script re-emits that
summary in a deterministic way so the human-eval pipeline can be rerun locally
without depending on a missing historical analysis notebook.

If the JSON artifact is missing, the script falls back to the lighter summary
files that are present in the repo.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary() -> dict:
    existing = RESULTS / "significance_statistics.json"
    if existing.exists():
        return _load_json(existing)

    evaluator_summary = _load_json(RESULTS / "evaluator_ablation_summary.json")
    rl_summary = _load_json(RESULTS / "rl_ablation_summary.json")

    configs = {
        item["config"]: {
            "spearman_rho": item["spearman_rho"],
            "ci95": None,
            "bootstrap_mean": item["spearman_rho"],
            "bootstrap_std": None,
        }
        for item in evaluator_summary.get("results", [])
    }

    return {
        "evaluator": {
            "paired_items": evaluator_summary.get("paired_items_used", 0),
            "configs": configs,
            "vs_full": {},
        },
        "rl": rl_summary,
    }


def write_markdown(summary: dict) -> None:
    evaluator = summary.get("evaluator", {})
    configs = evaluator.get("configs", {})
    rl = summary.get("rl", {})

    def _metric_mean(value):
        if isinstance(value, dict):
            if "mean" in value:
                return value["mean"]
            if "delta" in value:
                return value["delta"]
            if "value" in value:
                return value["value"]
        return value

    lines = ["# Significance statistics", "", f"Paired items: {evaluator.get('paired_items', 'n/a')}", "", "## Evaluator ranking", "", "| Config | Spearman ρ |", "| --- | --- |"]
    for name, stats in sorted(configs.items(), key=lambda item: item[1].get("spearman_rho", 0.0), reverse=True):
        lines.append(f"| {name} | {stats.get('spearman_rho', float('nan')):.4f} |")

    lines += ["", "## RL pilot", ""]
    for name, stats in rl.items():
        if isinstance(stats, dict) and "mean_score" in stats:
            mean_score = _metric_mean(stats.get("mean_score"))
            mean_difficulty = _metric_mean(stats.get("mean_difficulty"))
            if mean_score is not None and mean_difficulty is not None:
                lines.append(f"- {name}: mean_score={float(mean_score):.4f}, mean_difficulty={float(mean_difficulty):.2f}")

    (RESULTS / "significance_statistics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    out = RESULTS / "significance_statistics.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary)
    print(f"Wrote {out}")
    print(f"Wrote {RESULTS / 'significance_statistics.md'}")


if __name__ == "__main__":
    main()
