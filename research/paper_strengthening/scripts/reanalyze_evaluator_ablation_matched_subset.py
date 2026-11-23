"""
Sixth system-paper pass -- matched-qid-subset extension of reanalyze_evaluator_ablation.py.

The seventh/eighth/ninth research-strengthening passes on this project's separate
P1/P3 track (evaluator_qid_rubric_mismatch_diagnosis.py, the ninth pass's
evaluator_benchmark_repair_package/) discovered that research/results/paper2/
paper2_case_level_results.csv -- the exact frozen source this manuscript's Table X
(Section XI.1) is built from -- has its `final_score`/S1/S2/R columns computed via
the live production get_rubric(qid) lookup, and that lookup is STALE for 4 of the
benchmark's 8 questions (qid 7, 15, 22, 50; 32 of 64 cases): benchmark_dataset.csv's
question text for those qids no longer matches what get_rubric(qid) currently
returns, so those 32 cases were scored against a rubric for a completely different
question. This means every full-64-case correlation figure ever reported for this
benchmark in this project's history -- including this manuscript's own Table X
(R-only rho=0.496, S1+R rho=0.509, full composite rho=0.414, question-clustered) --
was computed on a partially-contaminated instrument. The ninth pass built a safe
interim citable number for the FULL COMPOSITE only (matched_subset_evaluation.json,
rho=0.655, CI [0.499, 0.809], n=32/4 questions). It did not recompute the other six
configurations Table X reports (S1 only, S2 only, R only, S1+S2, S1+R, S2+R), so no
matched-subset version of Table X itself existed before this script.

This script closes that gap: identical methodology to reanalyze_evaluator_ablation.py
(same frozen CSV, same seven configurations, same question-clustered bootstrap
convention), restricted to the qid=1,3,10,41 matched subset. No new model scores are
generated, no frozen file is modified -- this recombines already-stored columns under
already-published weightings, exactly as the original script does, just over a
smaller (currently-trustworthy) case set. B and seed match the ninth pass's own
matched-subset convention (B=5000, seed=20270901), not the original script's
(B=2000, seed=20260921), specifically so this script's own full-composite row can be
checked against matched_subset_evaluation.json's already-independently-verified
rho=0.655 as a correctness check on this script itself before trusting its other six
rows.

Output: research/paper_strengthening/results/evaluator_reanalysis_matched_subset.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
CASE_CSV = ROOT / "research/results/paper2/paper2_case_level_results.csv"
OUT = Path(__file__).resolve().parents[1] / "results" / "evaluator_reanalysis_matched_subset.json"

MATCHED_QIDS = {1, 3, 10, 41}

RNG = np.random.default_rng(20270901)  # matches the ninth pass's matched-subset convention
B = 5000

full_df = pd.read_csv(CASE_CSV)
assert len(full_df) == 64, f"expected 64 cases, got {len(full_df)}"
assert set(full_df["qid"].unique()) == {1, 3, 7, 10, 15, 22, 41, 50}, "unexpected qid set -- source CSV changed?"

df = full_df[full_df["qid"].isin(MATCHED_QIDS)].reset_index(drop=True)
assert len(df) == 32, f"expected 32 matched-qid cases, got {len(df)}"
qids = df["qid"].unique()
assert len(qids) == 4, f"expected 4 matched questions, got {len(qids)}"

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
    """Resample by qid (4 clusters, matched subset only), not by item (32 items)."""
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

# Sanity check against the ninth pass's already-independently-verified full-composite number.
full_composite_key = "Full composite (stored final_score, incl. bonus/penalty/cap)"
_check_item_rho = results[full_composite_key]["item_level_spearman_rho"]
_expected = 0.655
_consistency_check = {
    "expected_item_level_rho_from_matched_subset_evaluation_json": _expected,
    "computed_item_level_rho_this_script": _check_item_rho,
    "matches_within_rounding": abs(_check_item_rho - _expected) < 0.001,
}

# Paired comparison: Full composite vs R-only, question-clustered bootstrap of mean(|err_full| - |err_R|)
err_full = np.abs(df[f"__score__{full_composite_key}"] - human)
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
        "at the question-clustered level (now only 4 independent questions -- a much weaker "
        "basis for this comparison than the original 8-question design). CI includes 0 => no "
        "significant difference detectable."
    ),
}

out = {
    "n_cases": 32,
    "n_questions": 4,
    "matched_qids": sorted(MATCHED_QIDS),
    "seed": 20270901,
    "n_bootstrap": B,
    "provenance": (
        "Restricted to the 4 of 8 benchmark questions (qid 1, 3, 10, 41) whose "
        "benchmark_dataset.csv question text still matches the live get_rubric(qid) "
        "question text, per evaluator_qid_rubric_mismatch_diagnosis.json (seventh pass) "
        "and the ninth pass's evaluator_benchmark_repair_package/qid_mapping.json. "
        "The excluded 32 cases (qid 7, 15, 22, 50) were scored, via the live production "
        "get_rubric(qid) lookup baked into paper2_case_level_results.csv, against a "
        "rubric for a different question than the one the benchmark's human raters saw."
    ),
    "consistency_check_against_ninth_pass": _consistency_check,
    "selection_limitation": (
        "This is a reduced, non-random subset of the original 8-question design, not a "
        "fresh sample matched to its intended power. All seven configurations' "
        "question-clustered bootstrap CIs now resample only 4 clusters and are "
        "correspondingly wide; do not treat this table as replacing the original "
        "8-question design's intended coverage."
    ),
    "configurations": results,
    "paired_full_vs_R_only": paired,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2))
print(json.dumps(_consistency_check, indent=2))
print(json.dumps({k: v["question_clustered_bootstrap"] for k, v in results.items()}, indent=2))
print(f"Written: {OUT}")
