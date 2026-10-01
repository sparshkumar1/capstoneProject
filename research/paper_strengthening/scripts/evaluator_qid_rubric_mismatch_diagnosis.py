"""
Seventh research-strengthening pass -- follow-up to
evaluator_error_category_breakdown.py, which surfaced a severe, previously
undocumented systematic under-scoring bias concentrated in specific
questions. This script diagnoses the root cause: benchmark_dataset.csv's
`qid` column is STALE relative to the live services/evaluator/assets/{qns,
rubrics}.json question bank. The two banks were internally consistent with
each other when the 64-case benchmark was built, but the live bank has since
been revised (question content reassigned to the same qid numbers) without
benchmark_dataset.csv being updated to match, so 4 of the benchmark's 8
questions (qid 7, 15, 22, 50 -- half the benchmark, 32 of 64 cases) are
currently scored, via get_rubric(qid), against a rubric for a COMPLETELY
DIFFERENT question:
  qid=7  bench: "climb n stairs" (DP)        live rubric: matrix rotation
  qid=15 bench: "DFS cycle in digraph"       live rubric: Dutch National Flag partition
  qid=22 bench: "binary search"              live rubric: BFS cycle detection (undirected graph)
  qid=50 bench: "race condition"             live rubric: segmentation fault
(qid=1 two-sum, qid=3 reverse linked list, qid=10 BFS traversal, qid=41
pointer-in-C remain correctly matched.)

This is a DATA/CONFIGURATION bug discovery, not a claim that the evaluator's
underlying architecture is well-calibrated in general; it is reported as
such. Nothing frozen is modified: final_human_gold.csv and
benchmark_dataset.csv are read-only inputs, rubrics.json/qns.json are
read-only inputs. The ad hoc rubric built here for the 4 mismatched
questions, from benchmark_dataset.csv's own already-existing
`reference_answer`/`rubric_concepts` columns (present precisely so each
benchmark case is self-contained), is a DIAGNOSTIC RE-SCORE, not a change to
the evaluator, the benchmark file, or the rubric bank -- it exists only in
this script's memory and is never written back anywhere.

Limitation of the ad hoc rescore: it embeds `rubric_concepts` on the fly via
the same code path evaluate() already supports for a rubric with no indexed
FAISS vectors (concept_detection/semantic_score's `rubric.get(
"expected_concepts")` fallback), but it cannot exercise the mandatory-concept
cap, the bonus-vector path or the semantic-mistake-vector path (none of
those have matching indexed vectors for these ad hoc rubrics), so it is a
necessarily incomplete stand-in for a properly re-indexed rubric -- reported
as a lower bound on what correct scoring would achieve, not a claim of full
production-equivalent scoring.

Reads (read-only): research/data/evaluator_benchmark/{benchmark_dataset.csv,
final_human_gold.csv}; services/evaluator/assets/{qns.json,rubrics.json} via
services.evaluator.app.

Writes: research/paper_strengthening/results/seventh_pass/
        evaluator_qid_rubric_mismatch_diagnosis.json
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

OUT = ROOT / "research/paper_strengthening/results/seventh_pass/evaluator_qid_rubric_mismatch_diagnosis.json"

MISMATCHED_QIDS = {7, 15, 22, 50}
MATCHED_QIDS = {1, 3, 10, 41}

bench = pd.read_csv(ROOT / "research/data/evaluator_benchmark/benchmark_dataset.csv")
gold = pd.read_csv(ROOT / "research/data/evaluator_benchmark/final_human_gold.csv")
df = bench.merge(gold, on="case_id", how="inner")
assert len(df) == 64

# --- Confirm the mismatch directly from the live question bank (not asserted, derived) ---
live_q_by_qid = {int(q["qid"]): q.get("question_text", "") for q in questions}
mismatch_confirmation = {}
for qid in sorted(MISMATCHED_QIDS | MATCHED_QIDS):
    bench_q = df[df["qid"] == qid]["question"].iloc[0]
    live_q = live_q_by_qid.get(qid, "<qid not found in live bank>")
    mismatch_confirmation[qid] = {"benchmark_question": bench_q, "live_rubric_question": live_q}

rows = []
for _, row in df.iterrows():
    qid = int(row["qid"])
    stale_rubric = get_rubric(qid)
    stale_result = evaluate(row["question"], row["candidate_answer"], stale_rubric)
    stale_score = stale_result["final_score"]

    rescored_score = None
    if qid in MISMATCHED_QIDS:
        concepts = ast.literal_eval(row["rubric_concepts"])
        adhoc_rubric = {
            "qid": f"adhoc-{qid}",
            "topic": row["topic"],
            "answer": row["reference_answer"],
            "expected_concepts": concepts,
        }
        rescored_result = evaluate(row["question"], row["candidate_answer"], adhoc_rubric)
        rescored_score = rescored_result["final_score"]

    gold_score = float(row["final_gold_score"])
    rows.append({
        "case_id": row["case_id"],
        "qid": qid,
        "group": "mismatched" if qid in MISMATCHED_QIDS else "matched",
        "stale_score": stale_score,
        "rescored_score": rescored_score,
        "gold_score": gold_score,
        "stale_signed_diff": round(stale_score - gold_score, 4),
        "rescored_signed_diff": round(rescored_score - gold_score, 4) if rescored_score is not None else None,
    })

per_case = pd.DataFrame(rows)


def summarize(scores, gold_scores):
    diffs = np.array(scores) - np.array(gold_scores)
    rho, _ = spearmanr(scores, gold_scores)
    return {
        "n": len(scores),
        "mean_signed_diff": round(float(diffs.mean()), 4),
        "mean_abs_diff": round(float(np.abs(diffs).mean()), 4),
        "spearman_rho": round(float(rho), 4) if not np.isnan(rho) else None,
    }


matched = per_case[per_case["group"] == "matched"]
mismatched = per_case[per_case["group"] == "mismatched"]

summary = {
    "mismatch_confirmation_from_live_question_bank": mismatch_confirmation,
    "full_64_case_set_stale_scoring": summarize(per_case["stale_score"], per_case["gold_score"]),
    "matched_32_case_subset_stale_scoring": summarize(matched["stale_score"], matched["gold_score"]),
    "mismatched_32_case_subset_stale_scoring": summarize(mismatched["stale_score"], mismatched["gold_score"]),
    "mismatched_32_case_subset_adhoc_rescoring": summarize(mismatched["rescored_score"], mismatched["gold_score"]),
    "full_64_case_set_with_mismatched_cases_adhoc_rescored": summarize(
        list(matched["stale_score"]) + list(mismatched["rescored_score"]),
        list(matched["gold_score"]) + list(mismatched["gold_score"]),
    ),
    "per_case": rows,
    "note": (
        "stale scoring = current production get_rubric(qid) lookup (what every "
        "prior pass's human-gold correlation number, including the sixth pass's "
        "0.3728, actually measured). adhoc rescoring = diagnostic-only re-score "
        "of the 32 mismatched cases against a rubric built from the benchmark's "
        "own reference_answer/rubric_concepts columns, with the limitations "
        "documented in this script's module docstring (no mandatory-cap/bonus/"
        "mistake-vector path for these ad hoc rubrics)."
    ),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(summary, indent=2))

print("=== Mismatch confirmation (live bank) ===")
for qid in sorted(MISMATCHED_QIDS):
    c = mismatch_confirmation[qid]
    print(f"  qid={qid}: benchmark={c['benchmark_question'][:55]!r}")
    print(f"           live_rubric={c['live_rubric_question'][:55]!r}")
print()
print("=== Stale (current production) scoring ===")
for label, key in [("full 64", "full_64_case_set_stale_scoring"),
                    ("matched 32 (qid 1,3,10,41)", "matched_32_case_subset_stale_scoring"),
                    ("mismatched 32 (qid 7,15,22,50)", "mismatched_32_case_subset_stale_scoring")]:
    s = summary[key]
    print(f"  {label:32s} n={s['n']:2d}  mean_signed={s['mean_signed_diff']:+.4f}  mean_abs={s['mean_abs_diff']:.4f}  rho={s['spearman_rho']}")
print()
print("=== Ad hoc rescoring of the 32 mismatched cases (diagnostic only) ===")
s = summary["mismatched_32_case_subset_adhoc_rescoring"]
print(f"  {'rescored mismatched 32':32s} n={s['n']:2d}  mean_signed={s['mean_signed_diff']:+.4f}  mean_abs={s['mean_abs_diff']:.4f}  rho={s['spearman_rho']}")
print()
print("=== Full 64 if mismatched cases were correctly (ad hoc) scored ===")
s = summary["full_64_case_set_with_mismatched_cases_adhoc_rescored"]
print(f"  {'matched (stale) + mismatched (rescored)':32s} n={s['n']:2d}  mean_signed={s['mean_signed_diff']:+.4f}  mean_abs={s['mean_abs_diff']:.4f}  rho={s['spearman_rho']}")
print(f"\nWritten: {OUT}")
