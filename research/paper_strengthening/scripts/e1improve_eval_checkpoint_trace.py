"""
E1-Improve V1, Intervention A evaluation: evaluates every periodic B2
checkpoint saved by e1improve_train_b2_checkpointed.py (8192-step
intervals, 5 seeds) on EVAL_SEEDS_DEV, on the identical 24-cell grid used
throughout E1. Reports the full per-checkpoint trace -- pooled MAE and the
lucky_guesser-cell MAE specifically -- with no snapshot selection.
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

cfg = load_config()
TRAINING_SEEDS = cfg["training_seeds"]
DEV_EVAL_SEEDS = cfg["development_eval_seeds"]
EVAL_GRID = ARM_GRIDS["B2"]
LUCKY_GUESSER_CELL = (0.80, 0.60)
CHECKPOINT_INTERVAL = 8192
TOTAL = cfg["timesteps_extended_budget"]
CHECKPOINT_STEPS = list(range(CHECKPOINT_INTERVAL, TOTAL + 1, CHECKPOINT_INTERVAL))

TRACE_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1improve_checkpoint_trace"
OUT_DIR = TRACE_ROOT
DUMMY_ENV_LOG = OUT_DIR / "_trace_eval_env_dummy_log.csv"


def load_ppo_at_step(seed: int, step: int):
    seed_dir = TRACE_ROOT / "B2" / f"seed_{seed}"
    model_path = seed_dir / f"b2_seed{seed}_{step}_steps.zip"
    vn_path = seed_dir / f"b2_seed{seed}_vecnormalize_{step}_steps.pkl"
    if not model_path.exists() or not vn_path.exists():
        return None
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from rl.env.interview_env import InterviewEnv
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
                         "mae": res["mae_x"], "final_actions": res["final_actions"]})
    return rows


def main():
    trace = []
    for step in CHECKPOINT_STEPS:
        for seed in TRAINING_SEEDS:
            policy = load_ppo_at_step(seed, step)
            if policy is None:
                print(f"MISSING checkpoint: seed={seed} step={step}")
                continue
            rows = run_condition(policy.act)
            pooled_mae = float(np.mean([r["mae"] for r in rows]))
            lucky_rows = [r for r in rows if (r["skill"], r["k"]) == LUCKY_GUESSER_CELL]
            lucky_mae = float(np.mean([r["mae"] for r in lucky_rows]))
            trace.append({"step": step, "seed": seed, "pooled_mae": pooled_mae, "lucky_guesser_mae": lucky_mae})
            print(f"step={step:6d} seed={seed}: pooled_mae={pooled_mae:.4f} lucky_mae={lucky_mae:.4f}")

    if DUMMY_ENV_LOG.exists():
        DUMMY_ENV_LOG.unlink()

    with open(OUT_DIR / "checkpoint_trace_raw.json", "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2)

    by_step = defaultdict(list)
    for r in trace:
        by_step[r["step"]].append(r)
    pooled_by_step = []
    for step in sorted(by_step):
        items = by_step[step]
        pooled_by_step.append({
            "step": step,
            "pooled_mae_mean": float(np.mean([i["pooled_mae"] for i in items])),
            "pooled_mae_sd": float(np.std([i["pooled_mae"] for i in items])),
            "lucky_guesser_mae_mean": float(np.mean([i["lucky_guesser_mae"] for i in items])),
            "lucky_guesser_mae_sd": float(np.std([i["lucky_guesser_mae"] for i in items])),
            "n_seeds": len(items),
        })
    with open(OUT_DIR / "checkpoint_trace_summary.json", "w", encoding="utf-8") as f:
        json.dump(pooled_by_step, f, indent=2)

    print("\nPer-step summary (averaged across seeds):")
    for r in pooled_by_step:
        print(f"  step={r['step']:6d}: pooled_mae={r['pooled_mae_mean']:.4f}±{r['pooled_mae_sd']:.4f}  "
              f"lucky_mae={r['lucky_guesser_mae_mean']:.4f}±{r['lucky_guesser_mae_sd']:.4f}")


if __name__ == "__main__":
    main()
