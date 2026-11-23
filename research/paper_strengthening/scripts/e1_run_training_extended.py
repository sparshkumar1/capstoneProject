"""
E1 -- extended-budget (98304-step) training diagnostic, triggered by the
pre-declared convergence rule (research/paper_strengthening/results/
e1_training/run_manifest.json: quartile_rise/full_rise > 0.10 for B2 at the
primary 24576-step budget). Per protocol V4 section 1.2, the extended budget
is run for BOTH B0 and B2 together, never one arm alone.

Writes to a SEPARATE output root (e1_training_extended/) so the primary
24576-step checkpoints and training_curves are not overwritten. The
per-step InterviewEnv CSV log path in e1_train_condition_b.py is not
parametrized by output_root, so this script's caller is responsible for
backing up the primary run's e1_training_logs/*.csv files first (done:
copied to e1_training_logs/primary_budget/ before this script runs); the
files this script produces at the original e1_training_logs/{arm}_seed{seed}.csv
paths are the extended-budget run's own per-step logs.
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

OUTPUT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_training_extended"


def main():
    summary = []
    for arm in ARMS:
        for seed in SEEDS:
            t0 = time.time()
            entry = {"arm": arm, "training_seed": seed, "extended_budget": True}
            try:
                meta = train_condition_b_seed(arm, seed, output_root=OUTPUT_ROOT, extended_budget=True)
                elapsed = time.time() - t0
                entry.update({"status": "completed", "elapsed_sec": round(elapsed, 2), "meta": meta})
                print(f"[EXT {arm} seed={seed}] completed in {elapsed:.1f}s -> {meta['model_path']}")
            except Exception as exc:  # noqa: BLE001
                elapsed = time.time() - t0
                entry.update({"status": "failed", "elapsed_sec": round(elapsed, 2), "error": repr(exc)})
                print(f"[EXT {arm} seed={seed}] FAILED after {elapsed:.1f}s: {exc!r}")
            summary.append(entry)

    summary_path = OUTPUT_ROOT / "training_run_summary_extended.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {summary_path}")

    n_failed = sum(1 for e in summary if e["status"] == "failed")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
