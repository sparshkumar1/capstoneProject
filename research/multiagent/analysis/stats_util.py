"""Shared statistics helpers (protocol MA-XA-XB v1): Clopper-Pearson, paired bootstrap, cluster bootstrap of pooled medians."""
import numpy as np
from scipy.stats import beta


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def paired_boot(a, b, B=10000, seed=20270101):
    """Mean of (a - b) over units with percentile bootstrap CI; a, b aligned per unit."""
    d = np.asarray(a, float) - np.asarray(b, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(B, len(d)))
    means = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def pooled_quantile_diff(turns_a, turns_b, q=0.5, B=2000, seed=20270101):
    """Difference of pooled-turn quantiles (a - b); sessions are the resampling clusters (aligned lists of arrays)."""
    rng = np.random.default_rng(seed)
    n = len(turns_a)
    A = [np.asarray(t, float) for t in turns_a]
    Bb = [np.asarray(t, float) for t in turns_b]
    point = float(np.quantile(np.concatenate(A), q) - np.quantile(np.concatenate(Bb), q))
    ds = np.empty(B)
    for i in range(B):
        ix = rng.integers(0, n, size=n)
        ds[i] = np.quantile(np.concatenate([A[j] for j in ix]), q) - np.quantile(np.concatenate([Bb[j] for j in ix]), q)
    return point, float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def quantile(xs, q):
    return float(np.quantile(np.asarray(xs, float), q))
