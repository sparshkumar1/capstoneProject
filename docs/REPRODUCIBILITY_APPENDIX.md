Reproducibility appendix

This appendix explains how to reproduce the key analysis and figures without downloading large model artifacts. It provides a "toy mode" that runs the evaluation and analysis using synthetic/proxy ratings included in the repository.

Quick start (toy mode)

```powershell
# Activate venv
. .venv\Scripts\Activate.ps1
# Run toy mode (uses synthetic ratings in ablation/results/)
python tools/toy_mode.py
```

What toy mode does
- Uses existing synthetic ratings in `ablation/results/ratings_synthetic_*.csv` or `ablation/results/ratings_proxy.csv`.
- Runs `ablation/average_ratings.py` (if present) to create `ratings_averaged.csv`.
- Runs `ablation/significance_statistics.py` to regenerate `significance_statistics.json` and Markdown summaries.
- Runs `ablation/comparison_and_coverage_figures.py` to regenerate `comparison_and_coverage.png` and SVG.

If you want to reproduce with real models
- Install model artifacts separately (not included in repo).
- See `docs/GIT_LFS_MIGRATION.md` for guidance on hosting large models externally and not committing them to the repo.

Contact
If anything fails, open an issue or ask me to run the toy-mode and diagnose failing steps.
