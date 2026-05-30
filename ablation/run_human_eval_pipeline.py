"""Run the human-eval pipeline end-to-end for testing.

By default this uses the synthetic proxy generator to create synthetic rater CSVs,
averages them, and runs the analysis and figure generation steps.

Usage:
  python ablation/run_human_eval_pipeline.py --use-synthetic
  python ablation/run_human_eval_pipeline.py --no-synthetic --ratings ablation/results/ratings_rater1.csv ablation/results/ratings_rater2.csv
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd: list[str]):
    print("\n$ " + " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser(description="Run human-eval pipeline")
    parser.add_argument("--use-synthetic", action="store_true", help="Generate synthetic rater CSVs for testing")
    parser.add_argument("--ratings", nargs="*", help="Paths to existing rater CSVs (if not using synthetic)")
    args = parser.parse_args()

    if args.use_synthetic:
        run([sys.executable, str(ROOT / "generate_synthetic_proxies.py"), "--source", str(ROOT / "results" / "ratings_proxy.csv"), "--out-dir", str(ROOT / "results"), "--n", "3", "--seed", "123"])
        ratings = [str(ROOT / "results" / f"ratings_synthetic_rater{i}.csv") for i in (1, 2, 3)]
    else:
        if not args.ratings:
            print("Provide --ratings or use --use-synthetic")
            return
        ratings = args.ratings

    # Average
    run([sys.executable, str(ROOT / "average_ratings.py"), "--ratings"] + ratings + ["--out", str(ROOT / "results" / "ratings_averaged.csv")])

    # Run significance and figures
    run([sys.executable, str(ROOT / "significance_statistics.py")])
    run([sys.executable, str(ROOT / "comparison_and_coverage_figures.py")])
    print("\nPipeline complete. Artifacts in: ablation/results/")


if __name__ == "__main__":
    main()
