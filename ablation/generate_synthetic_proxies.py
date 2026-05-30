"""Create clearly-labelled synthetic rater CSVs from the existing proxy ratings.

This is for internal testing only and is explicitly marked as synthetic.
Usage:
  python ablation/generate_synthetic_proxies.py --source ablation/results/ratings_proxy.csv --out-dir ablation/results --n 3 --seed 42
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def load_proxy(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def jitter_score(score_str: str, rng: random.Random, scale: float = 0.03) -> str:
    if not score_str:
        return ""
    try:
        v = float(score_str)
    except Exception:
        return score_str
    # add small Gaussian noise in [−scale, +scale], clip to [0,1]
    nv = max(0.0, min(1.0, v + rng.gauss(0, scale)))
    return f"{nv:.4f}"


def write_rater(rows: list[dict], out_path: Path, label: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "question", "answer", "system_score", "human_score"])
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "qid": r.get("qid", ""),
                "question": r.get("question", ""),
                "answer": r.get("answer", ""),
                "system_score": r.get("system_score", ""),
                "human_score": r.get("human_score", ""),
            })


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic rater CSVs (marked as synthetic)")
    parser.add_argument("--source", required=True)
    parser.add_argument("--out-dir", default="ablation/results")
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    src = Path(args.source)
    out_dir = Path(args.out_dir)
    rng = random.Random(args.seed)

    rows = load_proxy(src)
    if not rows:
        print(f"No rows found in {src}")
        return

    for i in range(1, args.n + 1):
        new_rows = []
        for r in rows:
            new_r = r.copy()
            # jitter human_score slightly to simulate rater disagreement
            new_r["human_score"] = jitter_score(r.get("human_score", ""), rng, scale=0.04)
            new_rows.append(new_r)

        out_path = out_dir / f"ratings_synthetic_rater{i}.csv"
        # add a header note by writing to a .meta file alongside the CSV
        (out_dir / f"ratings_synthetic_rater{i}.meta.txt").write_text(
            "THIS FILE IS SYNTHETIC PROXY DATA FOR TESTING. NOT REAL HUMAN RATINGS.\n",
            encoding="utf-8",
        )
        write_rater(new_rows, out_path, f"synthetic_rater_{i}")
        print(f"Wrote synthetic rater → {out_path}")


if __name__ == "__main__":
    main()
