"""
E1-Improve V3 -- development evaluation of the B2ent (persona-diverse +
ent_coef=0.01) checkpoints, on the same 24-cell dev grid x 5 development
eval seeds (1001-5005) as e1_dev_eval.py, so B2ent is directly comparable to
the already-reported B0/B2/ConditionA/ConstantSame/Heuristic numbers in
E1_DEVELOPMENT_RUN_REPORT.md.

Reuses e1_dev_eval.py's own condition-runner/aggregation functions
unmodified (imported, not copied) so the evaluation methodology is
byte-identical to the one already used for B0/B2 -- the only difference is
which checkpoints are evaluated and where they are read from.

No confirmatory eval seed, no held-out profile, and no existing B0/B2/
Condition A checkpoint or result file is read for writing or modified.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import e1_dev_eval as dev_eval  # noqa: E402  (imported unmodified; its main() is never called)

BUDGET_LABEL = sys.argv[1] if len(sys.argv) > 1 else "primary"
B2ENT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_improve_v3_entropy" / "B2ent" / BUDGET_LABEL
OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_improve_v3_entropy" / f"eval_{BUDGET_LABEL}"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    all_rows = []
    print(f"Evaluating B2ent ({BUDGET_LABEL} budget) checkpoints...")
    for seed in dev_eval.TRAINING_SEEDS:
        ckpt_dir = B2ENT_ROOT / f"seed_{seed}"
        policy = dev_eval.load_ppo_condition(ckpt_dir)
        all_rows += dev_eval.run_condition(policy.act, "B2ent", seed)

    if dev_eval.DUMMY_ENV_LOG.exists():
        dev_eval.DUMMY_ENV_LOG.unlink()

    raw_path = OUT_DIR / "raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    pooled = dev_eval.aggregate(all_rows, ["condition"])
    per_seed = dev_eval.aggregate(all_rows, ["condition", "training_seed"])
    per_cell = dev_eval.aggregate(all_rows, ["condition", "skill", "k"])
    lucky_rows = [r for r in all_rows if (r["skill"], r["k"]) == dev_eval.LUCKY_GUESSER_CELL]
    lucky_by = dev_eval.aggregate(lucky_rows, ["condition"])

    summary = {
        "budget": BUDGET_LABEL,
        "ent_coef": 0.01,
        "n_rows_total": len(all_rows),
        "pooled": pooled,
        "per_seed": per_seed,
        "per_cell": per_cell,
        "lucky_guesser_cell": lucky_by,
    }
    summary_path = OUT_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Raw: {raw_path}\nSummary: {summary_path}")
    for r in pooled:
        print(f"  {r['condition']}: mae_mean={r['mae_mean']:.4f} sd={r['mae_sd']:.4f} n={r['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
