Human evaluation protocol and scripts
===================================

This document explains how to collect human ratings for the PrepAIred evaluator, how to run the analysis pipeline, and how to reproduce the figures in `ablation/results/`.

1) Interactive human rating (recommended)

- Activate the virtualenv then run the interactive harness. Each rater runs this separately and produces a CSV:

```powershell
.\.venv\Scripts\Activate.ps1
python ablation/human_eval_harness.py --answers ablation/data/ablation_answers.json --out ablation/results/ratings_rater1.csv
```

- Repeat for each rater (e.g., `ratings_rater2.csv`, `ratings_rater3.csv`). Do not show the `system_score` column to raters during collection (the harness hides it by default).

2) Averaging rater CSVs

After collecting ratings from N raters, average them:

```powershell
python ablation/average_ratings.py --ratings \
  ablation/results/ratings_rater1.csv \
  ablation/results/ratings_rater2.csv \
  ablation/results/ratings_rater3.csv \
  --out ablation/results/ratings_averaged.csv
```

3) Analysis and figures

Once `ablation/results/ratings_averaged.csv` exists, run the full analysis (significance, convergence, coverage figures):

```powershell
python ablation/significance_statistics.py
python ablation/comparison_and_coverage_figures.py
python ablation/plot_rl_convergence.py
python ablation/difficulty_smoothness.py
python ablation/adaptive_trajectory_figure.py
```

4) Synthetic proxy data (for testing only)

If you don't have real human raters yet, use the synthetic generator to create clearly-labeled synthetic rater CSVs for internal testing:

```powershell
python ablation/generate_synthetic_proxies.py --source ablation/results/ratings_proxy.csv --out-dir ablation/results --n 3 --seed 123
python ablation/average_ratings.py --ratings ablation/results/ratings_synthetic_rater1.csv ablation/results/ratings_synthetic_rater2.csv ablation/results/ratings_synthetic_rater3.csv --out ablation/results/ratings_averaged.csv
python ablation/significance_statistics.py
```

Important: Synthetic files are marked with `.meta.txt` files and must not be presented as real human data in publications.

5) Reproducibility and ethics

- Keep each rater's CSV intact and include a short manifest describing rater recruitment and instructions when preparing materials for review.
- Use `krippendorff.alpha` (already wired in `human_eval_harness.py`) to report inter-rater reliability.
- Do not fabricate or mislabel data. The repository includes the synthetic generator purely for offline testing and pipeline checks.

Contact
-------
If you want me to prepare a PR with these artifacts and a short changelog, tell me and I'll open it.
