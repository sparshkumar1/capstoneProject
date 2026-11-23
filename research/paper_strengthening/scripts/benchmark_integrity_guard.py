"""
Reusable guard against the qid-mismatch class of bug discovered in the
seventh research-strengthening pass: a benchmark case's `qid` column can
silently drift out of sync with the live `services/evaluator/assets/
{qns,rubrics}.json` question bank, causing `get_rubric(qid)` to return a
rubric for a DIFFERENT question than the one the benchmark's own stored
`question` text (and any human rating attached to it) actually concerns.

Any future script that scores `research/data/evaluator_benchmark/
benchmark_dataset.csv` (or a similarly-shaped benchmark file with a `qid`
and a `question` column) against the live evaluator should call
`load_and_verify_benchmark()` from this module instead of loading the CSV
and calling get_rubric(qid) directly -- it will not let a case with a
known-mismatched qid pass through unlabeled.

This module makes no network or file-write calls; it only reads the
already-existing frozen/source files and raises or annotates in memory.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class QidIntegrityResult(NamedTuple):
    qid: int
    benchmark_question: str
    live_question: str | None
    matched: bool


def check_qid_integrity(bench_df, questions=None) -> list[QidIntegrityResult]:
    """
    bench_df: a pandas DataFrame with at least `qid` and `question` columns
    (one row per case; only the first row per distinct qid is checked, since
    a benchmark's rows for the same qid are expected to share one question).
    questions: the live question-bank list (services.evaluator.app.questions);
    imported lazily if not passed, so this module has no hard import-time
    dependency on the evaluator package.

    Returns one QidIntegrityResult per distinct qid in bench_df.
    """
    if questions is None:
        from services.evaluator.app import questions as _questions
        questions = _questions

    live_q_by_qid = {}
    for q in questions:
        qid = q.get("qid")
        if qid is None:
            continue
        live_q_by_qid.setdefault(int(qid), q.get("question_text"))

    results = []
    for qid in sorted(bench_df["qid"].unique()):
        bench_q = bench_df[bench_df["qid"] == qid]["question"].iloc[0]
        live_q = live_q_by_qid.get(int(qid))
        results.append(QidIntegrityResult(
            qid=int(qid),
            benchmark_question=bench_q,
            live_question=live_q,
            matched=(live_q == bench_q),
        ))
    return results


class BenchmarkQidMismatchError(RuntimeError):
    """Raised when a benchmark case's qid does not match the live question
    bank, to stop a caller from silently scoring it against the wrong
    rubric via get_rubric(qid)."""


def load_and_verify_benchmark(
    bench_path: Path | str | None = None,
    questions=None,
    on_mismatch: str = "raise",
):
    """
    Loads the evaluator human-gold benchmark CSV and verifies every qid
    against the live question bank before returning it.

    on_mismatch:
      "raise"  (default) -- raises BenchmarkQidMismatchError listing every
               mismatched qid and its affected case_ids; the caller cannot
               proceed to score anything without explicitly catching this
               and making a deliberate choice.
      "annotate" -- returns (df, results) where df has an added
               `_qid_verified` boolean column and results is the full list
               of QidIntegrityResult; the caller is responsible for
               checking `_qid_verified` before calling get_rubric(qid) on
               any row where it is False.

    This function does not modify the source CSV in any way.
    """
    import pandas as pd

    if bench_path is None:
        bench_path = ROOT / "research/data/evaluator_benchmark/benchmark_dataset.csv"
    df = pd.read_csv(bench_path)

    results = check_qid_integrity(df, questions=questions)
    mismatched = [r for r in results if not r.matched]

    if mismatched and on_mismatch == "raise":
        lines = []
        for r in mismatched:
            case_ids = df[df["qid"] == r.qid]["case_id"].tolist()
            lines.append(
                f"  qid={r.qid}: benchmark question {r.benchmark_question!r} "
                f"!= live rubric question {r.live_question!r} "
                f"(affects case_ids: {case_ids})"
            )
        raise BenchmarkQidMismatchError(
            f"{len(mismatched)} of {len(results)} benchmark question IDs do not match "
            f"the live question bank -- get_rubric(qid) would score these cases against "
            f"the wrong question. Pass on_mismatch='annotate' to proceed deliberately, "
            f"or exclude these cases (see research/paper_strengthening/results/"
            f"ninth_pass/evaluator_benchmark_repair_package/):\n" + "\n".join(lines)
        )

    mismatched_qids = {r.qid for r in mismatched}
    df = df.copy()
    df["_qid_verified"] = ~df["qid"].isin(mismatched_qids)
    return df, results


if __name__ == "__main__":
    # Self-test / demonstration: running this file directly shows the guard
    # correctly refuses to proceed on the known-affected benchmark.
    try:
        load_and_verify_benchmark()
        print("UNEXPECTED: no mismatch detected (has the benchmark or live bank changed?)")
    except BenchmarkQidMismatchError as exc:
        print("Guard correctly raised on the known-mismatched benchmark:")
        print(exc)
    print()
    df, results = load_and_verify_benchmark(on_mismatch="annotate")
    n_verified = int(df["_qid_verified"].sum())
    print(f"Annotate mode: {n_verified}/{len(df)} cases have a verified qid; "
          f"{len(df) - n_verified} are flagged for exclusion or special handling.")
