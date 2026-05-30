PR summary: human-eval pipeline, analysis artifacts, and filled draft
===============================================================

Branch: workspace/human-eval-updates

Summary of what was added in this branch (pushed May 30, 2026):

- Ablation / human-eval artifacts (folder `ablation/results/`):
  - `ratings_averaged_real.csv` — averaged ratings from available rater(s)
  - `comparison_and_coverage.png` / `.svg` — evaluator comparison heatmaps
  - `significance_statistics.json` / `.md` — RL + evaluator significance results
  - `rl_ablation_summary.json` — pilot RL ablation summaries
  - additional figures: `rl_convergence.*`, `adaptive_trajectory.*`, `difficulty_smoothness.*`

- Analysis helpers:
  - `ablation/compute_krippendorff.py` — simple script to compute Krippendorff α

- Paper draft (filled placeholders):
  - `docs/paper_draft_ieee_filled.md` — draft where available stats were inserted (note: provenance marked in-text)

Key numbers (from current analysis using rater1 + synthetic proxies):

- Evaluator Full (paper) Spearman ρ = 0.9612
- Krippendorff α (interval) = 0.918 (computed from rater1 + synthetic proxies)
- RL pilot: PPO+Guardrails adaptation ρ = 0.871, adj slope = 0.0475, PPO rate = 62%
- Guardrail intervention rate ≈ 31%

Notes about provenance and recommended next steps:

1. The current filled draft uses a mix of real rater data (rater1) and synthetic proxy raters. Replace these provisional numbers after collecting at least two additional independent human raters (3+ total) for robust statistics.

2. To re-run analysis after adding new rater CSVs to `ablation/results/`:

```bash
python ablation/average_ratings.py --ratings ablation/results/ratings_rater1.csv ablation/results/ratings_rater2.csv ablation/results/ratings_rater3.csv --out ablation/results/ratings_averaged.csv
python ablation/significance_statistics.py
python ablation/comparison_and_coverage_figures.py
```

3. After re-running, update `docs/paper_draft_ieee_filled.md` with final numbers and replace the provisional filled draft in the PR body.

4. CI is configured to run the test suite in mock mode; please review CI logs after pushing new data or code changes.

Suggested immediate action (ideal next step): collect two more independent human rater CSVs using `ablation/human_eval_harness.py` (each rater runs a separate instance) and then ask me to re-run averaging + analysis and update the draft; I can also update the PR description or post a PR comment summarising these results.

If you'd like, I can now (pick one):
- update the PR description with this summary, or
- post the summary as a comment on the PR, or
- wait and re-run analysis after additional raters are added.

-- PrepAIred assistant
