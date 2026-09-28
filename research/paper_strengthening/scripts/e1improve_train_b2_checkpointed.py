"""
E1-Improve V1, Intervention A: B2 checkpoint-interval trace.

Retrains B2 only (5 seeds, same config as E1 V4's e1_train_condition_b.py,
same hyperparameters, same episode-seed formula, same grid) to the extended
budget (98304 steps), adding ONLY a periodic-checkpoint callback (SB3's
CheckpointCallback, saving every 8192 steps) and a W&B run (per
E1_IMPROVE_V1_PROTOCOL.md section 4 / user instruction to use W&B where it
is already configured). No reward, state, action, or hyperparameter is
changed; the environment class (_DiversePersonaAlignedEnv) and candidate
construction (make_candidate) are imported unmodified from
e1_train_condition_b.py / e1_diverse_persona_env.py.

Output: research/paper_strengthening/results/e1improve_checkpoint_trace/
  B2/seed_<seed>/b2_seed<seed>_<n>_steps.zip
  B2/seed_<seed>/b2_seed<seed>_vecnormalize_<n>_steps.pkl
  B2/seed_<seed>/training_curves.csv (from the existing, reused
    TrainingConvergenceCallback -- same mechanism E1 already used)
"""
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))
SCRIPTS_DIR = REPO / "research" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import wandb  # noqa: E402
from wandb.integration.sb3 import WandbCallback  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402

from e1_train_condition_b import load_config, build_env_class  # noqa: E402
import execute_paper3_study as eps  # noqa: E402  (frozen module; imported only, main() never called)

cfg = load_config()
SEEDS = cfg["training_seeds"]
CHECKPOINT_INTERVAL = 8192
TOTAL_TIMESTEPS = cfg["timesteps_extended_budget"]  # 98304, same extended budget as E1's own diagnostic

OUT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1improve_checkpoint_trace"


def train_one_seed(seed: int):
    seed_dir = OUT_ROOT / "B2" / f"seed_{seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    log_path = seed_dir / f"B2_seed{seed}_env_log.csv"

    run = wandb.init(
        project="prepaired-e1improve",
        name=f"e1improve_b2_checkpointed_seed{seed}",
        config={
            "experiment": "E1-Improve-V1", "intervention": "A_checkpoint_trace",
            "arm": "B2", "training_seed": seed,
            "total_timesteps": TOTAL_TIMESTEPS, "checkpoint_interval": CHECKPOINT_INTERVAL,
            **cfg["ppo_hyperparameters"],
            "protocol": "E1_IMPROVE_V1_PROTOCOL.md",
        },
        reinit=True,
        sync_tensorboard=False,
    )

    EnvClass = build_env_class()

    def make_env():
        return EnvClass(arm="B2", training_seed=seed, dim4_mode=cfg["dim4_mode"], log_file=str(log_path))

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
        name_prefix=f"b2_seed{seed}", save_vecnormalize=True, verbose=0,
    )
    wandb_cb = WandbCallback(verbose=0)

    t0 = time.time()
    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=CallbackList([convergence_cb, checkpoint_cb, wandb_cb]))
    elapsed = time.time() - t0

    final_path = seed_dir / "ppo_final_98304.zip"
    norm_path = seed_dir / "vecnormalize_final_98304.pkl"
    model.save(str(final_path))
    train_vec_env.save(str(norm_path))

    wandb.log({"elapsed_sec": elapsed})
    run.finish()
    print(f"[B2 seed={seed}] completed in {elapsed:.1f}s, wandb run: {run.url if hasattr(run, 'url') else run.id}")
    return {"seed": seed, "elapsed_sec": elapsed, "wandb_run_id": run.id}


def main():
    summary = []
    for seed in SEEDS:
        try:
            summary.append(train_one_seed(seed))
        except Exception as exc:  # noqa: BLE001
            print(f"[B2 seed={seed}] FAILED: {exc!r}")
            summary.append({"seed": seed, "status": "failed", "error": repr(exc)})
    import json
    with open(OUT_ROOT / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("Done.", summary)


if __name__ == "__main__":
    main()
