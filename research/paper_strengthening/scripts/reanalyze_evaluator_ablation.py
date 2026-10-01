"""
Re-analysis of frozen Paper-2 evaluator ablation data.

Reads only already-stored, frozen columns from
research/results/paper2/paper2_case_level_results.csv (S1, S2, S2_eff, R,
final_score, human_gold_score, qid). Generates NO new model scores, calls
no model, and modifies no frozen file. Recombines already-computed
component scores under already-published weightings, and adds a
question-clustered bootstrap (resampling the 8 distinct qids, not the 64
items) to respect the true number of independent units, per instruction.

Output: research/paper_strengthening/results/evaluator_reanalysis.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
CASE_CSV = ROOT / "research/results/paper2/paper2_case_level_results.csv"
OUT = Path(__file__).resolve().parents[1] / "results" / "evaluator_reanalysis.json"

RNG = np.random.default_rng(20260921)  # fixed seed, disclosed
B = 2000

df = pd.read_csv(CASE_CSV)
assert len(df) == 64, f"expected 64 cases, got {len(df)}"
qids = df["qid"].unique()
assert len(qids) == 8, f"expected 8 distinct questions, got {len(qids)}"

CONFIGS = {
    "S1 only": lambda d: d["S1"],
    "S2 only": lambda d: d["S2"],
    "R only": lambda d: d["R"],
    "S1+S2 (0.30/0.70)": lambda d: 0.30 * d["S1"] + 0.70 * d["S2"],
    "S1+R (0.23/0.77)": lambda d: 0.23 * d["S1"] + 0.77 * d["R"],
    "S2+R (0.41/0.59)": lambda d: 0.41 * d["S2"] + 0.59 * d["R"],
    "Full composite (stored final_score, incl. bonus/penalty/cap)": lambda d: d["final_score"],
}

human = df["human_gold_score"].to_numpy()


def item_level_rho(scores: np.ndarray) -> float:
    rho, _ = spearmanr(scores, human)
    return float(rho)


def cluster_bootstrap_rho(score_col: str, n_boot: int = B):
    """Resample by qid (8 clusters), not by item (64 items)."""
    rhos = []
    for _ in range(n_boot):
        sampled_qids = RNG.choice(qids, size=len(qids), replace=True)
        idx = np.concatenate([df.index[df["qid"] == q].to_numpy() for q in sampled_qids])
        sub = df.loc[idx]
        if sub["human_gold_score"].nunique() < 2:
            continue
        rho, _ = spearmanr(sub[score_col_cache[score_col]], sub["human_gold_score"])
        if not np.isnan(rho):
            rhos.append(rho)
    arr = np.array(rhos)
    return {
        "n_valid_boot": int(len(arr)),
        "mean": float(np.mean(arr)),
        "ci95_low": float(np.percentile(arr, 2.5)),
        "ci95_high": float(np.percentile(arr, 97.5)),
    }


results = {}
score_col_cache = {}
for name, fn in CONFIGS.items():
    df[f"__score__{name}"] = fn(df)
    score_col_cache[name] = f"__score__{name}"
    item_rho = item_level_rho(df[f"__score__{name}"].to_numpy())
    cluster = cluster_bootstrap_rho(name)
    results[name] = {
        "item_level_spearman_rho": round(item_rho, 4),
        "question_clustered_bootstrap": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in cluster.items()},
    }

# Paired comparison: Full composite vs R-only, question-clustered bootstrap of mean(|err_full| - |err_R|)
err_full = np.abs(df[f"__score__Full composite (stored final_score, incl. bonus/penalty/cap)"] - human)
err_r = np.abs(df["__score__R only"] - human)
df["__err_full"] = err_full
df["__err_r"] = err_r

diffs = []
for _ in range(B):
    sampled_qids = RNG.choice(qids, size=len(qids), replace=True)
    idx = np.concatenate([df.index[df["qid"] == q].to_numpy() for q in sampled_qids])
    sub = df.loc[idx]
    diffs.append(float(sub["__err_full"].mean() - sub["__err_r"].mean()))
diffs = np.array(diffs)

paired = {
    "mean_abs_error_full": round(float(err_full.mean()), 4),
    "mean_abs_error_R_only": round(float(err_r.mean()), 4),
    "question_clustered_bootstrap_of_mean_diff_full_minus_R": {
        "mean": round(float(diffs.mean()), 4),
        "ci95_low": round(float(np.percentile(diffs, 2.5)), 4),
        "ci95_high": round(float(np.percentile(diffs, 97.5)), 4),
    },
    "interpretation": (
        "CI excludes 0 => full composite's error is significantly different from R-only's, "
        "at the question-clustered level. CI includes 0 => no significant difference "
        "detectable given only 8 independent questions."
    ),
}

# Per-question homogeneity check (does the correlation depend heavily on which question?)
per_question = (
    df.groupby("qid")
    .apply(lambda g: pd.Series({
        "n_items": len(g),
        "mean_human": round(float(g["human_gold_score"].mean()), 3),
        "mean_final_score": round(float(g["final_score"].mean()), 3),
        "mean_R": round(float(g["R"].mean()), 3),
    }))
    .reset_index()
    .to_dict(orient="records")
)

out = {
    "n_cases": 64,
    "n_questions": 8,
    "seed": 20260921,
    "n_bootstrap": B,
    "note": "Item-level rho values are cross-checks against the frozen ablation CSV, not new results. "
            "Question-clustered bootstrap CIs are the honest interval given 8 independent questions, "
            "not 64 independent items.",
    "configurations": results,
    "paired_full_vs_R_only": paired,
    "per_question_breakdown": per_question,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
