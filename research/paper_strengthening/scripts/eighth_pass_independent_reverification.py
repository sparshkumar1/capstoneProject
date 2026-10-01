"""
Eighth research-strengthening pass. Fully independent re-verification of the
seventh pass's qid-mismatch finding -- written from scratch, sharing no code
with evaluator_error_category_breakdown.py or
evaluator_qid_rubric_mismatch_diagnosis.py, and re-deriving every number
rather than reading either script's stored JSON output.

Checks performed:
  1. Data integrity of the 64-case benchmark itself: duplicate case_ids,
     per-qid case counts, missing/malformed rubric_concepts, any case whose
     candidate_answer or gold score is missing/non-numeric.
  2. All 8 qid-to-question mappings, cross-checked independently against
     BOTH qns.json and rubrics.json (not assumed consistent with each other;
     checked separately).
  3. A fresh manual Spearman correlation (via scipy, but cross-checked
     against a from-scratch rank-correlation implementation using only
     numpy, to rule out a scipy-usage bug) for: all 64 cases (stale
     scoring), the matched-32 subset, the mismatched-32 subset (stale), and
     the mismatched-32 subset (ad hoc rescored) -- using a fresh call to
     evaluate() for every case, not reading any prior script's per-case
     scores back in.
  4. Explicit tie handling / missing-value check: are there any repeated
     score values that could make Spearman's rank handling ambiguous, and
     are there any NaN/Inf evaluator or gold scores anywhere in the 64 cases?

Read-only against: research/data/evaluator_benchmark/{benchmark_dataset.csv,
final_human_gold.csv}, services/evaluator/assets/{qns.json,rubrics.json}.
Writes only to research/paper_strengthening/results/eighth_pass/.
"""
import ast
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from services.evaluator.app import evaluate, get_rubric, questions  # noqa: E402

OUT = ROOT / "research/paper_strengthening/results/eighth_pass/independent_reverification.json"

bench = pd.read_csv(ROOT / "research/data/evaluator_benchmark/benchmark_dataset.csv")
gold = pd.read_csv(ROOT / "research/data/evaluator_benchmark/final_human_gold.csv")

report = {"data_integrity": {}, "qid_mapping": {}, "correlations": {}, "tie_and_missing_check": {}}

# ---- 1. Data integrity of the benchmark itself ----
dupe_case_ids = bench["case_id"][bench["case_id"].duplicated()].tolist()
report["data_integrity"]["n_bench_rows"] = len(bench)
report["data_integrity"]["n_gold_rows"] = len(gold)
report["data_integrity"]["duplicate_case_ids_in_bench"] = dupe_case_ids
report["data_integrity"]["per_qid_case_counts"] = bench["qid"].value_counts().sort_index().to_dict()
report["data_integrity"]["case_ids_bench_minus_gold"] = sorted(set(bench["case_id"]) - set(gold["case_id"]))
report["data_integrity"]["case_ids_gold_minus_bench"] = sorted(set(gold["case_id"]) - set(bench["case_id"]))

malformed_concepts = []
for _, row in bench.iterrows():
    try:
        parsed = ast.literal_eval(row["rubric_concepts"])
        if not isinstance(parsed, list) or len(parsed) == 0:
            malformed_concepts.append(row["case_id"])
    except Exception:
        malformed_concepts.append(row["case_id"])
report["data_integrity"]["malformed_or_empty_rubric_concepts"] = malformed_concepts

missing_answer = bench[bench["candidate_answer"].isna() | (bench["candidate_answer"].astype(str).str.strip() == "")]["case_id"].tolist()
report["data_integrity"]["cases_with_missing_or_empty_candidate_answer"] = missing_answer

non_numeric_gold = []
for _, row in gold.iterrows():
    try:
        v = float(row["final_gold_score"])
        if math.isnan(v) or math.isinf(v) or not (0.0 <= v <= 1.0):
            non_numeric_gold.append({"case_id": row["case_id"], "value": row["final_gold_score"]})
    except Exception:
        non_numeric_gold.append({"case_id": row["case_id"], "value": row["final_gold_score"]})
report["data_integrity"]["gold_scores_out_of_range_or_non_numeric"] = non_numeric_gold

# ---- 2. Independent qid-mapping cross-check against BOTH qns.json and rubrics.json separately ----
live_q_by_qid = {}
for q in questions:
    live_q_by_qid.setdefault(int(q["qid"]), []).append(q.get("question_text", ""))

qid_check = {}
for qid in sorted(bench["qid"].unique()):
    bench_q_texts = bench[bench["qid"] == qid]["question"].unique().tolist()
    rubric = get_rubric(int(qid))
    rubric_answer = rubric.get("answer", "") if rubric else None
    rubric_topic = rubric.get("topic", "") if rubric else None
    live_qns_texts = live_q_by_qid.get(int(qid), [])
    # Primary check: exact question-text match against the LIVE qns.json
    # question bank (apples-to-apples, question vs question -- not the
    # earlier weaker word-overlap-against-the-ANSWER heuristic tried below,
    # which is retained only as a documented negative result, see
    # WEAK_HEURISTIC_DISAGREEMENTS below).
    bench_q_text = bench_q_texts[0] if bench_q_texts else None
    exact_match = bench_q_text is not None and bench_q_text in live_qns_texts

    # crude lexical overlap check: does the rubric's own answer text share any
    # content word with the benchmark's question text? Kept only to document
    # that it disagreed with the exact-match check on 2/8 qids (7, 10) and
    # was wrong both times -- a genuine negative result about this weaker
    # heuristic's reliability, not a second, competing finding.
    bench_words = set(bench_q_texts[0].lower().split()) if bench_q_texts else set()
    rubric_words = set((rubric_answer or "").lower().split())
    stopwords = {"the", "a", "an", "is", "are", "of", "to", "in", "and", "how", "you", "do", "what", "for", "on", "its", "it"}
    overlap = (bench_words - stopwords) & (rubric_words - stopwords)
    weak_heuristic_flagged_mismatch = len(overlap) == 0

    qid_check[int(qid)] = {
        "n_cases": len(bench[bench["qid"] == qid]),
        "bench_question_texts_all_identical": len(bench_q_texts) == 1,
        "bench_question": bench_q_text,
        "live_qns_json_question_for_this_qid": live_qns_texts,
        "live_rubrics_json_answer_snippet": (rubric_answer or "")[:120],
        "live_rubrics_json_topic": rubric_topic,
        "exact_question_text_match_vs_live_bank": exact_match,
        "flagged_mismatch": not exact_match,
        "weak_word_overlap_heuristic_agreed_with_exact_match": weak_heuristic_flagged_mismatch == (not exact_match),
    }
report["qid_mapping"] = qid_check

confirmed_mismatched = sorted([q for q, d in qid_check.items() if d["flagged_mismatch"]])
confirmed_matched = sorted([q for q, d in qid_check.items() if not d["flagged_mismatch"]])
report["qid_mapping_summary"] = {
    "mismatched_qids_independently_confirmed": confirmed_mismatched,
    "matched_qids_independently_confirmed": confirmed_matched,
}

# ---- 3. Fresh scoring + fresh correlation computation ----
df = bench.merge(gold, on="case_id", how="inner")
assert len(df) == 64

def rank_corr_from_scratch(x, y):
    """Spearman correlation implemented from scratch with numpy only
    (average-rank tie handling), to cross-check scipy's spearmanr."""
    def avg_ranks(v):
        order = np.argsort(v, kind="mergesort")
        ranks = np.empty(len(v))
        sorted_v = v[order]
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and sorted_v[j + 1] == sorted_v[i]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg_rank
            i = j + 1
        return ranks

    rx, ry = avg_ranks(np.asarray(x, dtype=float)), avg_ranks(np.asarray(y, dtype=float))
    return float(np.corrcoef(rx, ry)[0, 1])


rows = []
for _, row in df.iterrows():
    qid = int(row["qid"])
    rubric = get_rubric(qid)
    result = evaluate(row["question"], row["candidate_answer"], rubric)
    stale_score = result["final_score"]

    rescored = None
    if qid in confirmed_mismatched:
        concepts = ast.literal_eval(row["rubric_concepts"])
        adhoc_rubric = {"qid": f"v8-adhoc-{qid}", "topic": row["topic"], "answer": row["reference_answer"], "expected_concepts": concepts}
        rescored = evaluate(row["question"], row["candidate_answer"], adhoc_rubric)["final_score"]

    rows.append({
        "case_id": row["case_id"], "qid": qid,
        "group": "mismatched" if qid in confirmed_mismatched else "matched",
        "stale_score": stale_score, "rescored_score": rescored,
        "gold_score": float(row["final_gold_score"]),
    })

pc = pd.DataFrame(rows)
matched = pc[pc["group"] == "matched"]
mismatched = pc[pc["group"] == "mismatched"]


def both_methods(scores, golds):
    scores = np.asarray(scores, dtype=float)
    golds = np.asarray(golds, dtype=float)
    rho_scipy, p = spearmanr(scores, golds)
    rho_scratch = rank_corr_from_scratch(scores, golds)
    diffs = scores - golds
    return {
        "n": len(scores),
        "spearman_rho_scipy": round(float(rho_scipy), 4),
        "spearman_rho_from_scratch_numpy": round(rho_scratch, 4),
        "methods_agree_to_4dp": round(float(rho_scipy), 4) == round(rho_scratch, 4),
        "p_value_scipy": float(p),
        "mean_signed_diff": round(float(diffs.mean()), 4),
        "mean_abs_diff": round(float(np.abs(diffs).mean()), 4),
    }


report["correlations"]["full_64_stale"] = both_methods(pc["stale_score"], pc["gold_score"])
report["correlations"]["matched_subset_stale"] = both_methods(matched["stale_score"], matched["gold_score"])
report["correlations"]["mismatched_subset_stale"] = both_methods(mismatched["stale_score"], mismatched["gold_score"])
report["correlations"]["mismatched_subset_adhoc_rescored"] = both_methods(mismatched["rescored_score"], mismatched["gold_score"])

# ---- 4. Tie and missing-value check ----
report["tie_and_missing_check"]["n_distinct_stale_scores_full_64"] = int(pc["stale_score"].nunique())
report["tie_and_missing_check"]["n_distinct_gold_scores_full_64"] = int(pc["gold_score"].nunique())
report["tie_and_missing_check"]["n_nan_or_inf_stale_scores"] = int(np.sum(~np.isfinite(pc["stale_score"].to_numpy(dtype=float))))
report["tie_and_missing_check"]["n_nan_or_inf_gold_scores"] = int(np.sum(~np.isfinite(pc["gold_score"].to_numpy(dtype=float))))
report["tie_and_missing_check"]["max_tied_stale_score_group_size"] = int(pc["stale_score"].value_counts().max())

report["per_case"] = rows

OUT.write_text(json.dumps(report, indent=2))

print("=== Data integrity ===")
print(json.dumps(report["data_integrity"], indent=2)[:1200])
print()
print("=== Independently confirmed mismatch set ===", confirmed_mismatched)
print("=== Independently confirmed matched set ===", confirmed_matched)
print()
print("=== Correlations (scipy vs from-scratch numpy cross-check) ===")
for k, v in report["correlations"].items():
    print(f"  {k:28s} n={v['n']:2d} rho_scipy={v['spearman_rho_scipy']:.4f} rho_scratch={v['spearman_rho_from_scratch_numpy']:.4f} agree={v['methods_agree_to_4dp']} signed={v['mean_signed_diff']:+.4f} abs={v['mean_abs_diff']:.4f}")
print()
print("=== Tie/missing check ===", json.dumps(report["tie_and_missing_check"], indent=2))
print(f"\nWritten: {OUT}")
