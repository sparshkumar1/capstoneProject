"""Toy-mode runner for PrepAIred reproducibility appendix.
Runs evaluation pipeline in a lightweight mode using synthetic or proxy data so reviewers can reproduce key analysis without large models.

Usage:
    python tools/toy_mode.py
"""
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
ablation = root / 'ablation'
results = ablation / 'results'

# This script will:
# 1. Use existing synthetic ratings in ablation/results/ratings_proxy.csv or ratings_synthetic_rater*.csv
# 2. Run the averaging script (if present) and significance scripts to regenerate summaries

# Helper to run command and stream output
def run(cmd, cwd=None):
    print('> ' + ' '.join(cmd))
    proc = subprocess.Popen(cmd, cwd=cwd or root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line, end='')
    proc.wait()
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

# Step 1: look for synthetic ratings
synthetic = list(results.glob('ratings_synthetic_*.csv'))
proxy = results / 'ratings_proxy.csv'
if not synthetic and not proxy.exists():
    print('No synthetic ratings found. The toy mode requires at least one synthetic ratings CSV in ablation/results/.')
    print('You can generate a minimal proxy by copying ratings_rater1.csv to ratings_proxy.csv and adjusting values.')
    sys.exit(1)

# If averaging script exists, run it
avg_script = ablation / 'average_ratings.py'
sig_script = ablation / 'significance_statistics.py'
comp_script = ablation / 'comparison_and_coverage_figures.py'

if avg_script.exists():
    # If proxy exists, skip averaging
    if proxy.exists():
        print('Using existing ratings_proxy.csv')
    else:
        cmd = [sys.executable, str(avg_script), '--ratings'] + [str(p) for p in synthetic] + ['--out', str(results / 'ratings_averaged.csv')]
        run(cmd, cwd=ablation)

# Run significance statistics if available
if sig_script.exists():
    run([sys.executable, str(sig_script)], cwd=ablation)
else:
    print('significance_statistics.py not found. toy-mode will end after averaging.')

# Run comparison figures if available
if comp_script.exists():
    run([sys.executable, str(comp_script)], cwd=ablation)

print('\nToy-mode run complete. Check ablation/results/ for regenerated summaries and figures.')
