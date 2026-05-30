"""Compute Krippendorff alpha (interval) from multiple rating CSVs.
Usage:
  python ablation/compute_krippendorff.py ratings1.csv ratings2.csv ...
"""
import sys
import csv
import math
import numpy as np

paths = sys.argv[1:]
if not paths:
    print("Usage: python compute_krippendorff.py rater1.csv rater2.csv ...")
    sys.exit(2)

# Load scores per rater
all_scores = []  # list of lists
for p in paths:
    scores = []
    with open(p, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            h = r.get('human_score','').strip()
            s = r.get('system_score','').strip()
            val = None
            if h:
                try:
                    val = float(h)
                except:
                    val = None
            elif s:
                try:
                    val = float(s)
                except:
                    val = None
            scores.append(val if val is not None else float('nan'))
    all_scores.append(scores)

# Align lengths
max_len = max(len(s) for s in all_scores)
for s in all_scores:
    if len(s) < max_len:
        s.extend([float('nan')] * (max_len - len(s)))

# Observed disagreement Do
num_raters = len(all_scores)
Do_num = 0.0
Do_den = 0
for item_idx in range(max_len):
    vals = [all_scores[r][item_idx] for r in range(num_raters) if not math.isnan(all_scores[r][item_idx])]
    m = len(vals)
    if m < 2:
        continue
    for i in range(m):
        for j in range(i+1, m):
            Do_num += (vals[i] - vals[j])**2
            Do_den += 1

if Do_den == 0:
    print('No pairable ratings to compute alpha.')
    sys.exit(0)
Do = Do_num / Do_den

# Expected disagreement De over all observed values
all_vals = []
for r in all_scores:
    for v in r:
        if not math.isnan(v):
            all_vals.append(v)
K = len(all_vals)
if K < 2:
    print('Not enough ratings to compute expected disagreement.')
    sys.exit(0)
De_num = 0.0
De_den = 0
for i in range(K):
    for j in range(i+1, K):
        De_num += (all_vals[i] - all_vals[j])**2
        De_den += 1
De = De_num / De_den

alpha = 1.0 - (Do / De) if De != 0 else float('nan')
print(f'Krippendorff alpha (interval) = {alpha:.4f}')
print(f'Paired items used: {Do_den}, total ratings: {K}')

if __name__ == '__main__':
    pass
