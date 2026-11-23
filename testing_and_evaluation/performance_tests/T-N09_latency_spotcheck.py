"""
T-N09 — Performance spot-check: evaluator call latency.

Read-only, in-process timing (no network, no running FastAPI server) around
repeated calls to the real evaluate() function, after a warm-up call to
exclude one-time model-loading cost from the measured distribution (same
distinction research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md's Paper-1 finding
already made: "the mean is dominated by a cold-start-scale outlier").

Reports median/p90/p95/mean over n calls, with warm-up excluded and reported
separately. This is a new spot-check, NOT a re-run of Paper 1's frozen
latency study -- it exists to sanity-check current-codebase latency order of
magnitude, not to reproduce or supersede Paper 1's numbers.

Run: .venv/Scripts/python.exe testing_and_evaluation/performance_tests/T-N09_latency_spotcheck.py
"""
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.evaluator.app import evaluate, get_rubric  # noqa: E402

QID = "1"
QN = "Explain your logic to find the two indices in an array that sum up to a target value."
ANSWER = ("I would use a hash map. Iterate through the array, and for each element, check if "
          "target minus the current element exists in the map. If it does, return the pair of "
          "indices. Otherwise, insert the current element and its index into the map. This runs "
          "in O(n) time with O(n) space, compared to the O(n^2) brute-force approach.")

N_CALLS = 30


def pctl(sorted_vals, p):
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def main() -> int:
    rubric = get_rubric(QID)
    if rubric is None:
        print("FATAL: rubric not found")
        return 2

    # Warm-up call: triggers model loading (SBERT/FAISS/CrossEncoder), excluded from stats.
    t0 = time.perf_counter()
    evaluate(QN, ANSWER, rubric)
    warmup_ms = (time.perf_counter() - t0) * 1000
    print(f"Warm-up call (includes model load): {warmup_ms:.1f} ms")

    latencies_ms = []
    for i in range(N_CALLS):
        t0 = time.perf_counter()
        evaluate(QN, ANSWER, rubric)
        latencies_ms.append((time.perf_counter() - t0) * 1000)

    latencies_ms.sort()
    median = statistics.median(latencies_ms)
    mean = statistics.mean(latencies_ms)
    p90 = pctl(latencies_ms, 0.90)
    p95 = pctl(latencies_ms, 0.95)
    p99 = pctl(latencies_ms, 0.99)

    print(f"\nn={N_CALLS} warm calls (model already loaded, same rubric/answer repeated)")
    print(f"mean={mean:.2f}ms  median={median:.2f}ms  p90={p90:.2f}ms  p95={p95:.2f}ms  p99={p99:.2f}ms")
    print(f"min={min(latencies_ms):.2f}ms  max={max(latencies_ms):.2f}ms")
    print()
    print("Context (NOT a direct comparison -- different hardware/environment/sample size):")
    print("Paper 1 frozen result (CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md §E): evaluator n=20, "
          "mean 1960.8ms, median 404.6ms, P95 2098.6ms, P99 26369.4ms (mean dominated by a "
          "cold-start outlier).")
    print(f"This spot-check: n={N_CALLS}, in-process direct function calls (no HTTP/network layer), "
          "same host that ran the Phase-2 baseline pytest suite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
