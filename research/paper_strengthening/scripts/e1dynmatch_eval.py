"""
E1 Dynamics Match V1 -- evaluation of all 8 arms x 5 seeds x 3 checkpoint
steps (8192, 16384, 24576) on EVAL_SEEDS_DEV only, on the existing 24-cell
grid. Intermediate checkpoints (8192/16384) are explicitly labeled as
snapshots of the single 24576-step schedule, never as independently-
budgeted models (protocol section 3).
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
X3A_DIR = REPO / "research" / "confirmatory" / "X3-A"
if str(X3A_DIR) not in sys.path:
    sys.path.insert(0, str(X3A_DIR))
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import x3a_lib  # noqa: E402
from e1_simulate_adapter import simulate_diverse, diverse_candidate_factory  # noqa: E402
from e1_diverse_persona_env import ARM_GRIDS, x3a_target_difficulty  # noqa: E402
from e1_train_condition_b import load_config  # noqa: E402
from e1dynmatch_env_variant import ALL_8_ARMS, arm_label_for  # noqa: E402

cfg = load_config()
TRAINING_SEEDS = cfg["training_seeds"]
DEV_EVAL_SEEDS = cfg["development_eval_seeds"]
EVAL_GRID = ARM_GRIDS["B2"]
CHECKPOINT_STEPS = [8192, 16384, 24576]

RUN_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1dynmatch_v1"
OUT_DIR = RUN_ROOT
DUMMY_ENV_LOG = OUT_DIR / "_eval_env_dummy_log.csv"


def load_checkpoint(label: str, seed: int, step: int):
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from rl.env.interview_env import InterviewEnv
    seed_dir = RUN_ROOT / label / f"seed_{seed}"
    if step == 24576:
        model_path = seed_dir / f"{label}_seed{seed}_final_24576.zip"
        vn_path = seed_dir / f"{label}_seed{seed}_vecnormalize_final_24576.pkl"
    else:
        model_path = seed_dir / f"{label}_seed{seed}_{step}_steps.zip"
        vn_path = seed_dir / f"{label}_seed{seed}_vecnormalize_{step}_steps.pkl"
    if not model_path.exists() or not vn_path.exists():
        return None
    model = PPO.load(str(model_path))
    vn = VecNormalize.load(str(vn_path), DummyVecEnv([lambda: InterviewEnv(log_file=str(DUMMY_ENV_LOG))]))
    vn.training = False
    vn.norm_reward = False
    return x3a_lib.PPOPolicy(model, vn)


def run_condition(policy_fn):
    rows = []
    for skill, k in EVAL_GRID:
        target = x3a_target_difficulty(skill)
        for eval_seed in DEV_EVAL_SEEDS:
            res = simulate_diverse(policy_fn, diverse_candidate_factory(skill, k), target, eval_seed, shield_on=True)
            rows.append({"skill": skill, "k": k, "eval_seed": eval_seed, "target": target,
                         "mae": res["mae_x"], "oracle_agreement": res["oracle_agreement"],
                         "final_actions": res["final_actions"]})
    return rows


def main():
    all_rows = []
    missing = []
    for factor_a, factor_b, factor_c in ALL_8_ARMS:
        label = arm_label_for(factor_a, factor_b, factor_c)
        for seed in TRAINING_SEEDS:
            for step in CHECKPOINT_STEPS:
                policy = load_checkpoint(label, seed, step)
                if policy is None:
                    missing.append((label, seed, step))
                    print(f"MISSING: {label} seed={seed} step={step}")
                    continue
                rows = run_condition(policy.act)
                for r in rows:
                    r.update({"arm": label, "factor_a": factor_a, "factor_b": factor_b, "factor_c": factor_c,
                               "training_seed": seed, "checkpoint_step": step})
                all_rows += rows
                print(f"Evaluated {label} seed={seed} step={step}: pooled_mae={np.mean([r['mae'] for r in rows]):.4f}")

    if DUMMY_ENV_LOG.exists():
        DUMMY_ENV_LOG.unlink()

    raw_path = OUT_DIR / "e1dynmatch_eval_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    def aggregate(rows, keys):
        buckets = defaultdict(list)
        for r in rows:
            buckets[tuple(r[k] for k in keys)].append(r)
        out = []
        for key, items in buckets.items():
            entry = dict(zip(keys, key))
            entry["n"] = len(items)
            entry["mae_mean"] = float(np.mean([i["mae"] for i in items]))
            entry["mae_sd"] = float(np.std([i["mae"] for i in items]))
            entry["oracle_agreement_mean"] = float(np.mean([i["oracle_agreement"] for i in items]))
            out.append(entry)
        return out

    pooled = aggregate(all_rows, ["arm", "checkpoint_step"])
    per_seed = aggregate(all_rows, ["arm", "checkpoint_step", "training_seed"])
    per_cell = aggregate(all_rows, ["arm", "checkpoint_step", "skill", "k"])

    summary = {
        "missing_checkpoints": missing,
        "pooled_by_arm_step": pooled,
        "per_seed_by_arm_step": per_seed,
        "per_cell_by_arm_step": per_cell,
    }
    summary_path = OUT_DIR / "e1dynmatch_eval_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nRaw: {raw_path}\nSummary: {summary_path}\n")
    print("Pooled MAE at 24576 steps, by arm:")
    for r in sorted(pooled, key=lambda x: x["arm"]):
        if r["checkpoint_step"] == 24576:
            print(f"  {r['arm']}: mae_mean={r['mae_mean']:.4f} sd={r['mae_sd']:.4f} n={r['n']}")
    if missing:
        print(f"\n{len(missing)} MISSING checkpoints -- see summary.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
