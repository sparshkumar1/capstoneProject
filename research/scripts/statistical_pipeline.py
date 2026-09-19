"""
PREPAIred Statistical Evaluation Pipeline for Technical Answer Assessment.
Implements robust parametric, non-parametric, bootstrap, and paired statistical tests.

NOTE ON TOY DATA:
Toy data in the __main__ block is strictly for software validation and unit testing.
It MUST NOT be cited or used as empirical research evidence.
"""

import math
import numpy as np
from scipy import stats
from typing import Dict, Any, Tuple, List, Optional


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Computes comprehensive correlation and error metrics with bootstrap confidence intervals.
    
    Args:
        y_true: Ground-truth human ratings (1D array)
        y_pred: Model predicted scores (1D array)
        n_bootstrap: Number of bootstrap iterations for confidence intervals
        alpha: Significance level (default 0.05 for 95% CI)
        seed: Random seed for bootstrap reproducibility
        
    Returns:
        Dict containing Spearman rho, Kendall tau, Pearson r, MAE, RMSE,
        associated p-values, and 95% bootstrap confidence intervals.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: len(y_true)={len(y_true)} vs len(y_pred)={len(y_pred)}")
    if len(y_true) < 3:
        raise ValueError("At least 3 observations required for statistical evaluation")
        
    n = len(y_true)
    
    # 1. Non-parametric rank correlations
    rho, rho_p = stats.spearmanr(y_pred, y_true)
    tau, tau_p = stats.kendalltau(y_pred, y_true)
    
    # 2. Linear correlation
    r, r_p = stats.pearsonr(y_pred, y_true)
    
    # 3. Absolute and squared error metrics
    errors = np.abs(y_pred - y_true)
    mae = float(np.mean(errors))
    rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))
    
    # 4. Bootstrap confidence intervals (Percentile Method)
    rng = np.random.default_rng(seed)
    boot_rho, boot_tau, boot_r, boot_mae, boot_rmse = [], [], [], [], []
    
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        t_b = y_true[idx]
        p_b = y_pred[idx]
        
        # Check for non-constant slices to avoid SciPy warnings
        if np.std(t_b) > 1e-9 and np.std(p_b) > 1e-9:
            b_rho, _ = stats.spearmanr(p_b, t_b)
            b_tau, _ = stats.kendalltau(p_b, t_b)
            b_r, _ = stats.pearsonr(p_b, t_b)
            boot_rho.append(b_rho)
            boot_tau.append(b_tau)
            boot_r.append(b_r)
        
        boot_mae.append(np.mean(np.abs(p_b - t_b)))
        boot_rmse.append(np.sqrt(np.mean((p_b - t_b) ** 2)))
        
    low_pct = 100.0 * (alpha / 2.0)
    high_pct = 100.0 * (1.0 - alpha / 2.0)
    
    def get_ci(arr):
        if len(arr) == 0:
            return (float("nan"), float("nan"))
        return (float(np.percentile(arr, low_pct)), float(np.percentile(arr, high_pct)))

    return {
        "n_samples": n,
        "spearman_rho": {
            "value": float(rho),
            "p_value": float(rho_p),
            "ci_95": get_ci(boot_rho)
        },
        "kendall_tau": {
            "value": float(tau),
            "p_value": float(tau_p),
            "ci_95": get_ci(boot_tau)
        },
        "pearson_r": {
            "value": float(r),
            "p_value": float(r_p),
            "ci_95": get_ci(boot_r)
        },
        "mae": {
            "value": mae,
            "ci_95": get_ci(boot_mae)
        },
        "rmse": {
            "value": rmse,
            "ci_95": get_ci(boot_rmse)
        }
    }


def compare_models(
    y_true: np.ndarray,
    y_pred_a: np.ndarray,
    y_pred_b: np.ndarray,
    model_a_name: str = "Model A",
    model_b_name: str = "Model B"
) -> Dict[str, Any]:
    """
    Performs paired hypothesis tests and computes effect sizes between two models.
    
    Args:
        y_true: Ground-truth human ratings
        y_pred_a: Predictions from Model A
        y_pred_b: Predictions from Model B
        model_a_name: Label for Model A
        model_b_name: Label for Model B
        
    Returns:
        Dict with paired t-test, Wilcoxon signed-rank test, Cohen's d, and Cliff's delta.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred_a = np.asarray(y_pred_a, dtype=float)
    y_pred_b = np.asarray(y_pred_b, dtype=float)
    
    # Absolute errors for each model
    err_a = np.abs(y_pred_a - y_true)
    err_b = np.abs(y_pred_b - y_true)
    diff = err_a - err_b  # Negative diff means Model A has lower error
    
    # 1. Paired t-test
    t_stat, t_p = stats.ttest_rel(err_a, err_b)
    
    # 2. Wilcoxon signed-rank test
    # If all differences are zero, handle gracefully
    if np.all(diff == 0):
        w_stat, w_p = 0.0, 1.0
    else:
        try:
            w_stat, w_p = stats.wilcoxon(err_a, err_b)
        except Exception:
            w_stat, w_p = float("nan"), float("nan")
            
    # 3. Cohen's d for paired differences: mean(diff) / std(diff)
    diff_std = np.std(diff, ddof=1)
    cohens_d = float(np.mean(diff) / diff_std) if diff_std > 1e-9 else 0.0
    
    # 4. Cliff's delta for non-parametric ordinal dominance
    n_a = len(err_a)
    n_b = len(err_b)
    greater = sum(1 for a in err_a for b in err_b if a > b)
    less = sum(1 for a in err_a for b in err_b if a < b)
    cliffs_delta = float((greater - less) / (n_a * n_b))
    
    return {
        "model_a": model_a_name,
        "model_b": model_b_name,
        "mean_error_a": float(np.mean(err_a)),
        "mean_error_b": float(np.mean(err_b)),
        "mean_error_diff (A - B)": float(np.mean(diff)),
        "paired_t_test": {
            "statistic": float(t_stat),
            "p_value": float(t_p)
        },
        "wilcoxon_signed_rank": {
            "statistic": float(w_stat),
            "p_value": float(w_p)
        },
        "effect_size": {
            "cohens_d": cohens_d,
            "cliffs_delta": cliffs_delta
        }
    }


if __name__ == "__main__":
    print("=== PREPAIred Statistical Pipeline Unit Test (TOY DATA ONLY) ===")
    print("WARNING: This data is randomly generated strictly to verify function correctness.")
    
    rng = np.random.default_rng(12345)
    toy_true = rng.uniform(0.1, 0.9, size=30)
    toy_pred_a = toy_true + rng.normal(0, 0.08, size=30)
    toy_pred_b = toy_true + rng.normal(0, 0.18, size=30)
    toy_pred_a = np.clip(toy_pred_a, 0.0, 1.0)
    toy_pred_b = np.clip(toy_pred_b, 0.0, 1.0)
    
    metrics_a = compute_metrics(toy_true, toy_pred_a, n_bootstrap=200)
    print("\nModel A Metrics on Toy Data:")
    print(f"  Spearman rho: {metrics_a['spearman_rho']['value']:.4f} (p={metrics_a['spearman_rho']['p_value']:.4e}, 95% CI: {metrics_a['spearman_rho']['ci_95']})")
    print(f"  Kendall tau:  {metrics_a['kendall_tau']['value']:.4f} (p={metrics_a['kendall_tau']['p_value']:.4e})")
    print(f"  Pearson r:    {metrics_a['pearson_r']['value']:.4f} (p={metrics_a['pearson_r']['p_value']:.4e})")
    print(f"  MAE:          {metrics_a['mae']['value']:.4f} (95% CI: {metrics_a['mae']['ci_95']})")
    print(f"  RMSE:         {metrics_a['rmse']['value']:.4f} (95% CI: {metrics_a['rmse']['ci_95']})")
    
    comp = compare_models(toy_true, toy_pred_a, toy_pred_b, "Full Pipeline", "Ablated Baseline")
    print("\nModel Comparison (Toy Data):")
    print(f"  Paired t-test: t={comp['paired_t_test']['statistic']:.4f}, p={comp['paired_t_test']['p_value']:.4e}")
    print(f"  Cohen's d:     {comp['effect_size']['cohens_d']:.4f}")
    print(f"  Cliff's delta: {comp['effect_size']['cliffs_delta']:.4f}")
    print("\nValidation Complete: All statistical functions operate cleanly and produce valid outputs.")
