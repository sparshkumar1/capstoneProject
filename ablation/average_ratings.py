"""Average one or more human rater CSV files into a single CSV.

This script keeps the original item ordering from the first rater file and
computes the mean of any numeric `human_score` / `system_score` values found
for each item key.

Usage:
  python ablation/average_ratings.py --ratings rater1.csv rater2.csv rater3.csv --out ablation/results/ratings_averaged.csv
"""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _item_key(row: dict) -> tuple[str, str, str]:
    return (
        str(row.get("qid", "")).strip(),
        str(row.get("question", "")).strip(),
        str(row.get("answer", "")).strip(),
    )


def load_rows(paths: list[str]) -> list[dict]:
    ordered: OrderedDict[tuple[str, str, str], dict] = OrderedDict()

    for path in paths:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = _item_key(row)
                bucket = ordered.setdefault(
                    key,
                    {
                        "qid": row.get("qid", ""),
                        "question": row.get("question", ""),
                        "answer": row.get("answer", ""),
                        "system_scores": [],
                        "human_scores": [],
                    },
                )
                system_score = _parse_float(row.get("system_score"))
                human_score = _parse_float(row.get("human_score"))
                if system_score is not None:
                    bucket["system_scores"].append(system_score)
                if human_score is not None:
                    bucket["human_scores"].append(human_score)

    rows = []
    for bucket in ordered.values():
        system_scores = bucket.pop("system_scores")
        human_scores = bucket.pop("human_scores")
        averaged = dict(bucket)
        averaged["system_score"] = f"{sum(system_scores) / len(system_scores):.4f}" if system_scores else ""
        averaged["human_score"] = f"{sum(human_scores) / len(human_scores):.4f}" if human_scores else ""
        rows.append(averaged)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Average human rater CSV files")
    parser.add_argument("--ratings", nargs="+", required=True, help="Input rater CSV files")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(args.ratings)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "question", "answer", "system_score", "human_score"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} averaged rows to {out_path}")


if __name__ == "__main__":
    main()
