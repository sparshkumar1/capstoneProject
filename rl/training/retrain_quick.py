"""
Quick PPO retrain — produces ppo_final.zip + vecnormalize.pkl compatible
with the current numpy/SB3 installation.
Trains for 300k steps (~2-3 min on CPU).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))          # so 'simulated_candidate' resolves

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import EvalCallback

from interview_env import InterviewEnv

SAVE_DIR = ROOT / "rl_runs" / "seed_123"
STEPS    = 300_000
SEED     = 123

def make_env():
    env = InterviewEnv(log_file=str(ROOT / "rl_runs" / "seed_123" / "retrain_log.csv"))
    return env

print(f"[retrain] Training PPO for {STEPS:,} steps (seed={SEED}) ...")

train_env = VecNormalize(DummyVecEnv([make_env]), norm_obs=True, norm_reward=True, clip_obs=10.0)

model = PPO(
    "MlpPolicy",
    train_env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    verbose=1,
    seed=SEED,
    tensorboard_log=None,
)

model.learn(total_timesteps=STEPS)

# Save
SAVE_DIR.mkdir(parents=True, exist_ok=True)
model.save(str(SAVE_DIR / "ppo_final"))
train_env.save(str(SAVE_DIR / "vecnormalize.pkl"))

print(f"[retrain] Saved to {SAVE_DIR}")
print(f"[retrain] numpy={np.__version__}  done.")
