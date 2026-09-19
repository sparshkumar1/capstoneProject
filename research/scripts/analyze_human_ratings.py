"""Analyze Human Ratings and Inter-Rater Reliability.

Computes Spearman rho, Pearson r, MAE, RMSE, bootstrap 95% CIs,
and Krippendorff alpha for rater agreement.
"""
import argparse
import json
import os
import numpy as np
import pandas as pd
from scipy import stats


def bootstrap_ci(x, y, stat_func, n_boot=1000, ci=0.95, seed=42):
    rng = np.random.default_rng(seed)
    n = len(x)
    boot_stats = []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        stat, _ = stat_func(x[idx], y[idx])
        if not np.isnan(stat):
            boot_stats.append(stat)
    alpha = (1.0 - ci) / 2.0
    lower = float(np.percentile(boot_stats, 100 * alpha))
    upper = float(np.percentile(boot_stats, 100 * (1.0 - alpha)))
    return lower, upper


def krippendorff_alpha_interval(data_matrix):
    n_units, n_raters = data_matrix.shape
    d_o = 0.0
    n_pairs_unit = 0
    all_values = []
    
    for u in range(n_units):
        row = data_matrix[u, :]
        valid = row[~np.isnan(row)]
        m_u = len(valid)
        if m_u > 1:
            diffs = (valid[:, None] - valid[None, :]) ** 2
            d_o += np.sum(diffs) / (2.0 * (m_u - 1))
            n_pairs_unit += m_u
            all_values.extend(valid.tolist())
        elif m_u == 1:
            all_values.extend(valid.tolist())
            
    if n_pairs_unit == 0 or len(all_values) < 2:
        return 1.0

    all_vals = np.array(all_values)
    diffs_all = (all_vals[:, None] - all_vals[None, :]) ** 2
    d_e = np.sum(diffs_all) / (2.0 * (len(all_vals) - 1))
    
    if d_e == 0:
        return 1.0
    return 1.0 - (d_o / d_e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='ablation/results/ratings_rater1.csv')
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    print(f'Loaded {len(df)} records from {args.input}')

    has_system = 'system_score' in df.columns
    has_human = 'human_score' in df.columns

    results = {}
    if has_system and has_human:
        sys = df['system_score'].fillna(0.0).to_numpy()
        hum = df['human_score'].fillna(0.0).to_numpy()

        rho, p_rho = stats.spearmanr(sys, hum)
        r, p_r = stats.pearsonr(sys, hum)
        mae = float(np.mean(np.abs(sys - hum)))
        rmse = float(np.sqrt(np.mean((sys - hum) ** 2)))

        rho_low, rho_high = bootstrap_ci(sys, hum, stats.spearmanr)
        r_low, r_high = bootstrap_ci(sys, hum, stats.pearsonr)

        results['system_vs_human'] = {
            'n': int(len(sys)),
            'spearman_rho': float(rho),
            'spearman_p': float(p_rho),
            'spearman_ci95': [rho_low, rho_high],
            'pearson_r': float(r),
            'pearson_p': float(p_r),
            'pearson_ci95': [r_low, r_high],
            'mae': mae,
            'rmse': rmse
        }
        print(f'System vs Human: rho={rho:.4f} (p={p_rho:.4e}), r={r:.4f}, MAE={mae:.4f}, RMSE={rmse:.4f}')

    proxy_files = [
        'ablation/results/ratings_synthetic_rater1.csv',
        'ablation/results/ratings_synthetic_rater2.csv',
        'ablation/results/ratings_synthetic_rater3.csv'
    ]
    if all(os.path.exists(p) for p in proxy_files):
        p1 = pd.read_csv(proxy_files[0])['human_score'].to_numpy()
        p2 = pd.read_csv(proxy_files[1])['human_score'].to_numpy()
        p3 = pd.read_csv(proxy_files[2])['human_score'].to_numpy()
        r1 = df['human_score'].to_numpy()

        matrix = np.column_stack([r1, p1, p2, p3])
        alpha = krippendorff_alpha_interval(matrix)
        results['inter_rater_reliability'] = {
            'n_raters': 4,
            'krippendorff_alpha_interval': float(alpha),
            'composition': '1 Real Human + 3 Synthetic Proxies'
        }
        print(f'Inter-Rater Agreement: Krippendorff alpha = {alpha:.4f}')

    os.makedirs('research/results', exist_ok=True)
    with open('research/results/rater_analysis.json', 'w') as f_out:
        json.dump(results, f_out, indent=2)
    print('Saved analysis to research/results/rater_analysis.json')


if __name__ == '__main__':
    main()
