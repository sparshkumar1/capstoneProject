"""
E1 -- development-phase training runner (approved run, step 4 of the E1 V4
development-phase approval message).

Calls e1_train_condition_b.train_condition_b_seed() for both arms (B0, B2)
across all 5 registered training seeds at the primary budget
(TIMESTEPS_PRIMARY=24576, from e1_config.json). No hyperparameter is
hard-coded here; everything comes from e1_config.json via
train_condition_b_seed(). Writes per-run metadata and prints a summary; any
exception for one (arm, seed) run is caught and recorded rather than
aborting the remaining runs, and is reported as a failure in the run
manifest, not silently retried.
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from e1_train_condition_b import train_condition_b_seed, load_config  # noqa: E402

cfg = load_config()
SEEDS = cfg["training_seeds"]
ARMS = cfg["arms"]

OUTPUT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_training"


def main():
    summary = []
    for arm in ARMS:
        for seed in SEEDS:
            t0 = time.time()
            entry = {"arm": arm, "training_seed": seed, "extended_budget": False}
            try:
                meta = train_condition_b_seed(arm, seed, output_root=OUTPUT_ROOT, extended_budget=False)
                elapsed = time.time() - t0
                entry.update({"status": "completed", "elapsed_sec": round(elapsed, 2), "meta": meta})
                print(f"[{arm} seed={seed}] completed in {elapsed:.1f}s -> {meta['model_path']}")
            except Exception as exc:  # noqa: BLE001  -- deliberately broad: record, never silently retry
                elapsed = time.time() - t0
                entry.update({"status": "failed", "elapsed_sec": round(elapsed, 2), "error": repr(exc)})
                print(f"[{arm} seed={seed}] FAILED after {elapsed:.1f}s: {exc!r}")
            summary.append(entry)

    summary_path = OUTPUT_ROOT / "training_run_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {summary_path}")

    n_failed = sum(1 for e in summary if e["status"] == "failed")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
