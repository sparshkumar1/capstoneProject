"""
Re-scores the 64-case evaluator benchmark with the CURRENT (post-fix)
evaluate() implementation and compares Spearman correlation with the frozen
human gold scores against the ORIGINAL (pre-fix, already-published) scores
stored in research/results/paper2/paper2_case_level_results.csv.

This is a real regression check against already-collected human judgment
data for the evaluator changes made in this pass (the high-concept-coverage/
weak-reasoning penalty tier, and repeated-sentence deduplication before
scoring) -- not a re-tuning against this data: no evaluator parameter was
chosen or adjusted by looking at this script's output, which is run only
after the changes were already made and justified on other grounds (see
services/evaluator/app.py's inline comments and PPO/evaluator reports).

Reads (read-only, nothing here is modified):
  - research/data/evaluator_benchmark/benchmark_dataset.csv (question,
    candidate_answer, qid, case_id -- the actual 64 answer texts)
  - research/data/evaluator_benchmark/final_human_gold.csv (frozen, listed
    as protected in CLAUDE.md; opened for reading only)
  - research/results/paper2/paper2_case_level_results.csv (frozen; the
    ORIGINAL evaluator's stored per-case scores, for the paired comparison)

Writes: research/paper_strengthening/results/evaluator_v2_recalibration_check.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from services.evaluator.app import evaluate, get_rubric, _ensure_evaluator_assets_loaded  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "evaluator_v2_recalibration_check.json"

RNG = np.random.default_rng(20260921)  # same fixed seed as reanalyze_evaluator_ablation.py, disclosed
B = 2000


def question_clustered_bootstrap_rho(scores, human, qids):
    """Resamples the 8 distinct qids with replacement (not the 64 items),
    matching reanalyze_evaluator_ablation.py's methodology exactly, since the
    true number of independent units in this design is 8 questions, not 64
    answer instances."""
    unique_qids = np.unique(qids)
    n_q = len(unique_qids)
    point_rho, _ = spearmanr(scores, human)
    boot_rhos = []
    for _ in range(B):
        sampled_qids = RNG.choice(unique_qids, size=n_q, replace=True)
        idx = np.concatenate([np.where(qids == q)[0] for q in sampled_qids])
        r, _ = spearmanr(scores[idx], human[idx])
        if not np.isnan(r):
            boot_rhos.append(r)
    boot_rhos = np.array(boot_rhos)
    return {
        "point_rho": float(point_rho),
        "boot_n": int(len(boot_rhos)),
        "ci_lower": float(np.percentile(boot_rhos, 2.5)),
        "ci_upper": float(np.percentile(boot_rhos, 97.5)),
    }


def main():
    _ensure_evaluator_assets_loaded()

    bench = pd.read_csv(REPO / "research/data/evaluator_benchmark/benchmark_dataset.csv")
    gold = pd.read_csv(REPO / "research/data/evaluator_benchmark/final_human_gold.csv")
    old = pd.read_csv(REPO / "research/results/paper2/paper2_case_level_results.csv")

    assert len(bench) == 64 and len(gold) == 64 and len(old) == 64

    df = bench.merge(gold[["case_id", "final_gold_score"]], on="case_id", how="inner")
    df = df.merge(old[["case_id", "final_score"]].rename(columns={"final_score": "old_final_score"}),
                   on="case_id", how="inner")
    assert len(df) == 64, f"merge produced {len(df)} rows, expected 64"

    new_scores = []
    new_S1, new_S2, new_R = [], [], []
    for _, row in df.iterrows():
        rubric = get_rubric(str(row["qid"]))
        assert rubric is not None, f"no rubric for qid={row['qid']}"
        result = evaluate(row["question"], row["candidate_answer"], rubric)
        new_scores.append(result["final_score"])
        new_S1.append(result["S1_semantic"])
        new_S2.append(result["S2_structural"])
        new_R.append(result["reasoning_score"])

    df["new_final_score"] = new_scores
    human = df["final_gold_score"].to_numpy()
    qids = df["qid"].to_numpy()

    old_stats = question_clustered_bootstrap_rho(df["old_final_score"].to_numpy(), human, qids)
    new_stats = question_clustered_bootstrap_rho(df["new_final_score"].to_numpy(), human, qids)

    n_changed = int((df["new_final_score"] != df["old_final_score"]).sum())
    mean_abs_delta = float(np.mean(np.abs(df["new_final_score"] - df["old_final_score"])))
    max_abs_delta = float(np.max(np.abs(df["new_final_score"] - df["old_final_score"])))

    result = {
        "n_cases": len(df),
        "n_questions": int(len(np.unique(qids))),
        "bootstrap_reps": B,
        "seed": 20260921,
        "old_evaluator_full_composite": old_stats,
        "new_evaluator_full_composite": new_stats,
        "n_cases_with_changed_score": n_changed,
        "mean_abs_score_delta": round(mean_abs_delta, 4),
        "max_abs_score_delta": round(max_abs_delta, 4),
        "per_case_deltas": [
            {"case_id": r["case_id"], "qid": int(r["qid"]), "old": r["old_final_score"], "new": r["new_final_score"],
             "delta": round(r["new_final_score"] - r["old_final_score"], 4)}
            for _, r in df.iterrows() if r["new_final_score"] != r["old_final_score"]
        ],
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Old evaluator: rho={old_stats['point_rho']:.4f} CI=[{old_stats['ci_lower']:.4f}, {old_stats['ci_upper']:.4f}]")
    print(f"New evaluator: rho={new_stats['point_rho']:.4f} CI=[{new_stats['ci_lower']:.4f}, {new_stats['ci_upper']:.4f}]")
    print(f"Cases with changed score: {n_changed}/64, mean|delta|={mean_abs_delta:.4f}, max|delta|={max_abs_delta:.4f}")
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
