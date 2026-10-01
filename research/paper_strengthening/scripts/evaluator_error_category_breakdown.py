"""
Seventh research-strengthening pass. Development-only error-category breakdown
of the CURRENT evaluator (post sixth-pass negation-filter fix) against the
frozen 64-case human-gold benchmark, grouped by the benchmark's own existing,
already-labeled `expected_quality_category` taxonomy (never before analyzed
per-category in any prior pass's reports, which only reported the overall
Spearman correlation).

This is a read-only regression/diagnostic analysis of already-frozen,
already-repeatedly-used-as-a-regression-check data (the same 64-case set every
evaluator change since the second pass has been checked against). No evaluator
parameter is chosen or adjusted by looking at this script's output; it runs
against the evaluator as it already stands after the sixth pass's fix, which
was justified independently (a substring-matching defect), not by this
analysis.

Reads (read-only):
  - research/data/evaluator_benchmark/benchmark_dataset.csv
  - research/data/evaluator_benchmark/final_human_gold.csv
  - services/evaluator/assets/rubrics.json (via services.evaluator.app)

Writes:
  - research/paper_strengthening/results/seventh_pass/evaluator_error_category_breakdown.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import os
os.environ.setdefault("EVALUATOR_MOCK_MODE", "0")

from services.evaluator.app import evaluate, get_rubric  # noqa: E402

OUT = ROOT / "research/paper_strengthening/results/seventh_pass/evaluator_error_category_breakdown.json"

bench = pd.read_csv(ROOT / "research/data/evaluator_benchmark/benchmark_dataset.csv")
gold = pd.read_csv(ROOT / "research/data/evaluator_benchmark/final_human_gold.csv")
df = bench.merge(gold, on="case_id", how="inner")
assert len(df) == 64, f"expected 64 merged cases, got {len(df)}"

rows = []
for _, row in df.iterrows():
    qid = int(row["qid"])
    rubric = get_rubric(qid)
    if rubric is None:
        raise RuntimeError(f"no rubric for qid={qid} (case {row['case_id']})")
    result = evaluate(row["question"], row["candidate_answer"], rubric)
    eval_score = result["final_score"]
    gold_score = float(row["final_gold_score"])
    rows.append({
        "case_id": row["case_id"],
        "qid": qid,
        "category": row["expected_quality_category"],
        "eval_score": eval_score,
        "gold_score": gold_score,
        "signed_diff": round(eval_score - gold_score, 4),
        "abs_diff": round(abs(eval_score - gold_score), 4),
    })

per_case = pd.DataFrame(rows)

rng = np.random.default_rng(20270101)  # fresh, disclosed seed for this pass's own bootstrap

by_cat = {}
for cat, g in per_case.groupby("category"):
    n = len(g)
    mean_signed = float(g["signed_diff"].mean())
    mean_abs = float(g["abs_diff"].mean())
    # Case-resampling bootstrap CI on mean_abs, B=5000; only reported for n>=6
    # groups -- smaller groups (contradictory n=4, paraphrase n=4,
    # suboptimal_correct n=2) get point estimates only, explicitly flagged,
    # since a bootstrap CI on n<6 cases is not informative and would be
    # misleading to present as if it were.
    ci = None
    if n >= 6:
        vals = g["abs_diff"].to_numpy()
        boot = [float(np.mean(rng.choice(vals, size=n, replace=True))) for _ in range(5000)]
        boot.sort()
        ci = [round(boot[int(0.025 * 5000)], 4), round(boot[int(0.975 * 5000) - 1], 4)]
    by_cat[cat] = {
        "n": n,
        "mean_signed_diff_eval_minus_gold": round(mean_signed, 4),
        "mean_abs_diff": round(mean_abs, 4),
        "abs_diff_95pct_bootstrap_ci": ci,
        "ci_note": None if ci is not None else f"n={n} too small for an informative bootstrap CI; point estimate only",
        "case_ids": g["case_id"].tolist(),
    }

overall_mean_abs = float(per_case["abs_diff"].mean())
overall_spearman = float(per_case[["eval_score", "gold_score"]].corr(method="spearman").iloc[0, 1])

out = {
    "n_cases": len(per_case),
    "overall_mean_abs_diff": round(overall_mean_abs, 4),
    "overall_spearman_rho": round(overall_spearman, 4),
    "by_category": by_cat,
    "per_case": rows,
    "bootstrap_seed": 20270101,
    "bootstrap_reps": 5000,
    "note": (
        "Evaluated with the evaluator as it stands after the sixth pass's "
        "negation-filter fix (justified independently of this analysis). "
        "This is a diagnostic breakdown of an already-existing regression "
        "check, not a new tuning target; no evaluator parameter was chosen "
        "by looking at this output."
    ),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2))
print(f"overall: mean_abs_diff={overall_mean_abs:.4f}  spearman_rho={overall_spearman:.4f}")
for cat, d in sorted(by_cat.items(), key=lambda kv: -kv[1]["mean_abs_diff"]):
    ci_str = f"CI={d['abs_diff_95pct_bootstrap_ci']}" if d["abs_diff_95pct_bootstrap_ci"] else d["ci_note"]
    print(f"  {cat:22s} n={d['n']:2d}  mean_abs_diff={d['mean_abs_diff']:.4f}  signed={d['mean_signed_diff_eval_minus_gold']:+.4f}  {ci_str}")
print(f"Written: {OUT}")
