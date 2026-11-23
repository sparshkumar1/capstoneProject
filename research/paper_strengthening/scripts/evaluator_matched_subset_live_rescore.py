"""
Sixth system-paper pass -- live, current-code re-score of the matched-qid subset,
replacing reanalyze_evaluator_ablation_matched_subset.py's frozen-CSV attempt.

That first attempt (reanalyze_evaluator_ablation_matched_subset.py) restricted the
existing frozen research/results/paper2/paper2_case_level_results.csv to the 32
qid-clean cases and recombined its stored S1/S2/R/final_score columns. Its own
built-in consistency check against the ninth pass's already-independently-verified
matched-subset full-composite number (evaluator_benchmark_repair_package/
matched_subset_evaluation.json, rho=0.655) FAILED (this script's frozen-CSV
recomputation gave rho=0.7092). Direct per-case comparison found 6 of the 32 cases'
final_score differs between the frozen CSV and the ninth pass's live re-score,
while all 32 gold scores are identical -- meaning services/evaluator/app.py's
working tree (`git status` shows it as locally modified, uncommitted, from this
engagement's own earlier NaN-handling and negation-filter fixes) now produces
different scores than whatever evaluator version paper2_case_level_results.csv
was frozen from (2026-09-19). So the frozen CSV is not just qid-contaminated for
half the benchmark -- for the matched-and-supposedly-clean half, it is ALSO stale
relative to the CURRENT evaluator code.

This script fixes that by re-deriving every component (S1_semantic, S2_structural,
reasoning_score, final_score) live, via the current, real (non-mock) evaluate()
function, exactly as the ninth pass's matched_subset_evaluation.json did for
final_score alone -- extended here to capture the components Table X's other six
configurations need. It reads only the frozen, read-only benchmark source files
(benchmark_dataset.csv, final_human_gold.csv) and calls the live evaluate()/
get_rubric() functions; it writes no frozen file.

Run with EVALUATOR_MOCK_MODE unset/0 (real SBERT + CrossEncoder + FAISS), matching
"real production scoring, no shortcuts" per the ninth pass's own convention.

Output: research/paper_strengthening/results/evaluator_matched_subset_live_rescore.json
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("EVALUATOR_MOCK_MODE", "0")

from services.evaluator.app import evaluate, get_rubric  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results" / "evaluator_matched_subset_live_rescore.json"

MATCHED_QIDS = [1, 3, 10, 41]
RNG = np.random.default_rng(20270901)  # matches the ninth pass's matched-subset convention
B = 5000

bench = pd.read_csv(ROOT / "research/data/evaluator_benchmark/benchmark_dataset.csv")
gold = pd.read_csv(ROOT / "research/data/evaluator_benchmark/final_human_gold.csv")
df = bench.merge(gold, on="case_id", how="inner")
assert len(df) == 64
df = df[df["qid"].isin(MATCHED_QIDS)].reset_index(drop=True)
assert len(df) == 32, f"expected 32 matched-qid cases, got {len(df)}"

rows = []
for _, row in df.iterrows():
    qid = int(row["qid"])
    rubric = get_rubric(qid)
    result = evaluate(row["question"], row["candidate_answer"], rubric)
    rows.append({
        "case_id": row["case_id"],
        "qid": qid,
        "S1": result["S1_semantic"],
        "S2": result["S2_structural"],
        "R": result["reasoning_score"],
        "final_score": result["final_score"],
        "human_gold_score": float(row["final_gold_score"]),
    })

rdf = pd.DataFrame(rows)

# Sanity check: full-composite item-level rho should now match the ninth pass's
# matched_subset_evaluation.json (rho=0.655) exactly, since both call the same
# live evaluate() function against the same 32 cases.
_rho_check, _ = spearmanr(rdf["final_score"], rdf["human_gold_score"])
_consistency_check = {
    "expected_from_ninth_pass_matched_subset_evaluation_json": 0.655,
    "computed_this_script": round(float(_rho_check), 4),
    "matches_within_rounding": abs(float(_rho_check) - 0.655) < 0.001,
}

qids = rdf["qid"].unique()
human = rdf["human_gold_score"].to_numpy()

CONFIGS = {
    "S1 only": lambda d: d["S1"],
    "S2 only": lambda d: d["S2"],
    "R only": lambda d: d["R"],
    "S1+S2 (0.30/0.70)": lambda d: 0.30 * d["S1"] + 0.70 * d["S2"],
    "S1+R (0.23/0.77)": lambda d: 0.23 * d["S1"] + 0.77 * d["R"],
    "S2+R (0.41/0.59)": lambda d: 0.41 * d["S2"] + 0.59 * d["R"],
    "Full composite (live final_score, incl. bonus/penalty/cap)": lambda d: d["final_score"],
}


def item_level_rho(scores: np.ndarray) -> float:
    rho, _ = spearmanr(scores, human)
    return float(rho)


def cluster_bootstrap_rho(score_col: str, n_boot: int = B):
    rhos = []
    for _ in range(n_boot):
        sampled_qids = RNG.choice(qids, size=len(qids), replace=True)
        idx = np.concatenate([rdf.index[rdf["qid"] == q].to_numpy() for q in sampled_qids])
        sub = rdf.loc[idx]
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
    rdf[f"__score__{name}"] = fn(rdf)
    score_col_cache[name] = f"__score__{name}"
    item_rho = item_level_rho(rdf[f"__score__{name}"].to_numpy())
    cluster = cluster_bootstrap_rho(name)
    results[name] = {
        "item_level_spearman_rho": round(item_rho, 4),
        "question_clustered_bootstrap": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in cluster.items()},
    }

full_key = "Full composite (live final_score, incl. bonus/penalty/cap)"
err_full = np.abs(rdf[f"__score__{full_key}"] - human)
err_r = np.abs(rdf["__score__R only"] - human)
rdf["__err_full"] = err_full
rdf["__err_r"] = err_r

diffs = []
for _ in range(B):
    sampled_qids = RNG.choice(qids, size=len(qids), replace=True)
    idx = np.concatenate([rdf.index[rdf["qid"] == q].to_numpy() for q in sampled_qids])
    sub = rdf.loc[idx]
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
}

out = {
    "n_cases": 32,
    "n_questions": 4,
    "matched_qids": MATCHED_QIDS,
    "seed": 20270901,
    "n_bootstrap": B,
    "method": "Live, current-code re-score via services.evaluator.app.evaluate() against "
              "benchmark_dataset.csv's self-contained question/candidate_answer, restricted to "
              "the 4 qid-clean questions. Not read from the frozen paper2_case_level_results.csv "
              "(confirmed stale for 6/32 of these cases relative to current evaluator code).",
    "consistency_check_against_ninth_pass_final_score_only": _consistency_check,
    "provenance_note": (
        "This supersedes reanalyze_evaluator_ablation_matched_subset.py's frozen-CSV-based attempt "
        "for the matched subset specifically. The ORIGINAL Table X (full 64-case, in "
        "FINAL_MANUSCRIPT_EVIDENCE_V2.md Section XI.1) still uses the frozen CSV and is not "
        "recomputed here; it carries both the qid-mismatch contamination (32/64 cases) AND this "
        "same staleness caveat, disclosed but not corrected for the full 64-case table in this pass."
    ),
    "selection_limitation": (
        "Reduced, non-random subset of the original 8-question design (4 of 8 questions), not a "
        "fresh sample matched to its intended power. Question-clustered bootstrap CIs resample "
        "only 4 clusters and are correspondingly wide."
    ),
    "configurations": results,
    "paired_full_vs_R_only": paired,
    "per_case": rows,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2))
print(json.dumps(_consistency_check, indent=2))
print(json.dumps({k: v["question_clustered_bootstrap"] for k, v in results.items()}, indent=2))
print(f"Written: {OUT}")
