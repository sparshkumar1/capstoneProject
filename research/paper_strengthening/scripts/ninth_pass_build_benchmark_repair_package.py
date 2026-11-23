"""
Ninth research-strengthening pass. Builds the machine-readable evaluator
benchmark repair package: affected-case list, qid mapping, and a
reproducible evaluation script/output for the valid matched subset only.

Read-only against research/data/evaluator_benchmark/{benchmark_dataset.csv,
final_human_gold.csv} and services/evaluator/assets/{qns.json,rubrics.json}.
Does not modify any frozen file. Writes only under
research/paper_strengthening/results/ninth_pass/evaluator_benchmark_repair_package/.
"""
import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from services.evaluator.app import evaluate, get_rubric, questions  # noqa: E402

OUT_DIR = ROOT / "research/paper_strengthening/results/ninth_pass/evaluator_benchmark_repair_package"
OUT_DIR.mkdir(parents=True, exist_ok=True)

bench = pd.read_csv(ROOT / "research/data/evaluator_benchmark/benchmark_dataset.csv")
gold = pd.read_csv(ROOT / "research/data/evaluator_benchmark/final_human_gold.csv")
df = bench.merge(gold, on="case_id", how="inner")
assert len(df) == 64

live_q_by_qid = {int(q["qid"]): q.get("question_text", "") for q in questions}

MISMATCHED_QIDS = [7, 15, 22, 50]
MATCHED_QIDS = [1, 3, 10, 41]

# ---- 1. qid mapping table ----
qid_mapping = []
for qid in sorted(bench["qid"].unique()):
    bench_q = bench[bench["qid"] == qid]["question"].iloc[0]
    live_q = live_q_by_qid.get(int(qid), None)
    case_ids = bench[bench["qid"] == qid]["case_id"].tolist()
    qid_mapping.append({
        "qid": int(qid),
        "status": "mismatched" if qid in MISMATCHED_QIDS else "matched",
        "benchmark_question_text": bench_q,
        "current_live_question_text_for_this_qid": live_q,
        "exact_text_match": bench_q == live_q,
        "case_ids": case_ids,
        "n_cases": len(case_ids),
    })

(OUT_DIR / "qid_mapping.json").write_text(json.dumps(qid_mapping, indent=2))

# ---- 2. affected-case list (machine readable) ----
affected_cases = []
for qid in MISMATCHED_QIDS:
    rows = df[df["qid"] == qid]
    for _, row in rows.iterrows():
        affected_cases.append({
            "case_id": row["case_id"],
            "qid": int(qid),
            "reason": "benchmark question text does not match the current live rubrics.json/qns.json entry for this qid",
            "benchmark_question": row["question"],
            "current_live_rubric_question": live_q_by_qid.get(int(qid)),
            "gold_score_still_valid": True,
            "gold_score_note": "human rating was made against the benchmark's own stored question/answer text, not against get_rubric(qid); unaffected by this bug",
            "production_rescoring_via_get_rubric_qid_is_invalid_for_this_case": True,
        })

(OUT_DIR / "affected_cases.json").write_text(json.dumps(affected_cases, indent=2))

# ---- 3. proposed corrected benchmark schema (documented, not applied) ----
schema = {
    "schema_version": "evaluator_benchmark_v2-proposed",
    "status": "PROPOSAL ONLY -- not applied to any frozen file",
    "changes_from_v1_benchmark_dataset_csv": [
        "Add a `qid_status` column: 'matched' | 'mismatched' | 'retired' per case, "
        "computed from qid_mapping.json rather than assumed.",
        "Add a `rubric_source` column: 'production_rubrics_json' (for matched cases) "
        "| 'benchmark_self_contained_reference_answer' (for mismatched cases, until "
        "re-indexed) -- makes explicit, per case, which scoring path is valid, so a "
        "future evaluate() caller cannot silently use get_rubric(qid) on a "
        "known-mismatched case without an explicit override.",
        "For any case whose qid is later reused for re-indexed rubric content, add a "
        "`benchmark_qid` column distinct from the production `qid`, so the benchmark's "
        "own identity does not silently follow a future production renumbering again.",
    ],
    "fields_requiring_human_authorship_or_approval_before_a_full_repair": [
        {"field": "mandatory_concepts", "why": "not present anywhere in benchmark_dataset.csv for the 4 mismatched questions; inventing them would not reflect what the original human raters saw or scored against"},
        {"field": "common_mistakes_addressed / bonus indicator text", "why": "same reason; no source content exists in the benchmark file"},
        {"field": "new held-out human ratings (if cases are replaced rather than re-indexed)", "why": "requires new rater recruitment and a documented independence/blinding protocol, not something this pass can produce"},
    ],
}
(OUT_DIR / "proposed_corrected_schema.json").write_text(json.dumps(schema, indent=2))

# ---- 4. reproducible evaluation of the matched subset ONLY (the safe, citable number) ----
matched_rows = []
for _, row in df[df["qid"].isin(MATCHED_QIDS)].iterrows():
    qid = int(row["qid"])
    rubric = get_rubric(qid)
    result = evaluate(row["question"], row["candidate_answer"], rubric)
    matched_rows.append({
        "case_id": row["case_id"], "qid": qid,
        "eval_score": result["final_score"],
        "gold_score": float(row["final_gold_score"]),
    })

mdf = pd.DataFrame(matched_rows)
rho, p = spearmanr(mdf["eval_score"], mdf["gold_score"])
diffs = mdf["eval_score"] - mdf["gold_score"]

rng = np.random.default_rng(20270901)
qids_arr = mdf["qid"].to_numpy()
unique_qids = np.unique(qids_arr)
boot_rhos = []
for _ in range(5000):
    sampled = rng.choice(unique_qids, size=len(unique_qids), replace=True)
    idx = np.concatenate([np.where(qids_arr == q)[0] for q in sampled])
    r, _ = spearmanr(mdf["eval_score"].to_numpy()[idx], mdf["gold_score"].to_numpy()[idx])
    if not np.isnan(r):
        boot_rhos.append(r)
boot_rhos.sort()
ci = [round(boot_rhos[int(0.025 * len(boot_rhos))], 4), round(boot_rhos[int(0.975 * len(boot_rhos)) - 1], 4)]

matched_subset_result = {
    "description": "The recommended citable evaluator/human-gold estimate until a full benchmark repair is completed: production scoring (real, fully-indexed rubrics, no shortcuts), restricted to the 4 questions (1, 3, 10, 41) whose qid still matches its originally-intended content.",
    "n_cases": len(mdf),
    "n_questions": len(unique_qids),
    "spearman_rho": round(float(rho), 4),
    "p_value": float(p),
    "question_clustered_bootstrap_95pct_ci": ci,
    "bootstrap_note": "resamples the 4 distinct qids (not the 32 case instances), B=5000, seed=20270901, matching this project's established question-clustered bootstrap convention (evaluator_v2_recalibration_check.py)",
    "mean_signed_diff": round(float(diffs.mean()), 4),
    "mean_abs_diff": round(float(diffs.abs().mean()), 4),
    "selection_limitation": (
        "This is a reduced, non-random subset (the 4 questions that happened to keep "
        "their original qid) of the originally-intended 8-question design, not a fresh "
        "sample. It should not be described as replacing the original 8-question design's "
        "intended coverage or statistical power; it is the largest subset that can "
        "currently be scored with full production fidelity."
    ),
    "per_case": matched_rows,
}
(OUT_DIR / "matched_subset_evaluation.json").write_text(json.dumps(matched_subset_result, indent=2))

print(f"Matched subset (n={len(mdf)}, {len(unique_qids)} questions): rho={rho:.4f} CI={ci} "
      f"signed={diffs.mean():+.4f} abs={diffs.abs().mean():.4f}")
print(f"\nWritten to {OUT_DIR}:")
for f in sorted(OUT_DIR.glob("*.json")):
    print(f"  {f.name}")
