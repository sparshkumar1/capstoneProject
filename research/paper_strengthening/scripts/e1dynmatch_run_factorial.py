"""
E1 Dynamics Match V1 -- primary factorial training runner (user-approved,
40 runs: 8 arms x 5 seeds x 24576 steps). Registered under tag
explore/E1-dynamics-match/v1 (commit 8e6cea8).

Uses e1dynmatch_env_variant.py's make_dynmatch_env() unmodified. Saves
checkpoints at 8192/16384/24576 steps (CheckpointCallback, single training
call per arm/seed -- the intermediate checkpoints are snapshots of this one
24576-step schedule, not independently-budgeted models). Every run gets an
isolated log_file under results/e1dynmatch_v1/<ARM>/seed_<seed>/ -- never
the shared default rl/env/training_logs/interview_data.csv.
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from e1dynmatch_env_variant import ALL_8_ARMS, arm_label_for, make_dynmatch_env
from e1_train_condition_b import load_config
import execute_paper3_study as eps  # noqa: frozen, imported only

cfg = load_config()
SEEDS = cfg["training_seeds"]
PRIMARY_BUDGET = 24576
CHECKPOINT_INTERVAL = 8192

OUT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1dynmatch_v1"


def train_one(factor_a, factor_b, factor_c, seed):
    label = arm_label_for(factor_a, factor_b, factor_c)
    seed_dir = OUT_ROOT / label / f"seed_{seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    log_path = seed_dir / f"{label}_seed{seed}_env_log.csv"

    def make_env():
        return make_dynmatch_env("B2", seed, factor_a, factor_b, factor_c, str(log_path))

    train_vec_env = VecNormalize(DummyVecEnv([make_env]), norm_obs=True, norm_reward=True, clip_obs=10.0)
    hp = cfg["ppo_hyperparameters"]
    model = PPO(
        hp["policy"], train_vec_env,
        learning_rate=hp["learning_rate"], n_steps=hp["n_steps"], batch_size=hp["batch_size"],
        n_epochs=hp["n_epochs"], gamma=hp["gamma"], gae_lambda=hp["gae_lambda"], clip_range=hp["clip_range"],
        verbose=0, seed=seed,
    )
    convergence_cb = eps.TrainingConvergenceCallback(log_path=seed_dir, seed=seed, log_freq=256)
    checkpoint_cb = CheckpointCallback(
        save_freq=CHECKPOINT_INTERVAL, save_path=str(seed_dir),
        name_prefix=f"{label}_seed{seed}", save_vecnormalize=True, verbose=0,
    )

    t0 = time.time()
    model.learn(total_timesteps=PRIMARY_BUDGET, callback=[convergence_cb, checkpoint_cb])
    elapsed = time.time() - t0

    final_path = seed_dir / f"{label}_seed{seed}_final_{PRIMARY_BUDGET}.zip"
    norm_path = seed_dir / f"{label}_seed{seed}_vecnormalize_final_{PRIMARY_BUDGET}.pkl"
    model.save(str(final_path))
    train_vec_env.save(str(norm_path))

    meta = {
        "arm": label, "factor_a": factor_a, "factor_b": factor_b, "factor_c": factor_c,
        "training_seed": seed, "elapsed_sec": round(elapsed, 2),
        "final_model_path": str(final_path), "final_vecnorm_path": str(norm_path),
    }
    with open(seed_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta


def main():
    summary = []
    for factor_a, factor_b, factor_c in ALL_8_ARMS:
        label = arm_label_for(factor_a, factor_b, factor_c)
        for seed in SEEDS:
            print(f"Training {label} seed={seed}...")
            try:
                meta = train_one(factor_a, factor_b, factor_c, seed)
                meta["status"] = "completed"
                print(f"  -> completed in {meta['elapsed_sec']:.1f}s")
            except Exception as exc:  # noqa: BLE001
                meta = {"arm": label, "factor_a": factor_a, "factor_b": factor_b, "factor_c": factor_c,
                        "training_seed": seed, "status": "failed", "error": repr(exc)}
                print(f"  -> FAILED: {exc!r}")
            summary.append(meta)

    summary_path = OUT_ROOT / "training_run_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {summary_path}")
    n_failed = sum(1 for e in summary if e.get("status") == "failed")
    print(f"Total runs: {len(summary)}, failed: {n_failed}")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
