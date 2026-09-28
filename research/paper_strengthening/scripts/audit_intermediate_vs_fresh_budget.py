"""
E1-Dynamics-Match V1, Phase 1.6 audit: is an intermediate checkpoint saved
during a 98304-step run (via CheckpointCallback) equivalent to a model
independently trained with that checkpoint's step count as its total
training budget? Diagnostic only -- not part of the registered factorial
protocol. One seed (42), one budget (16384), same env/config/hyperparameters
as e1_train_condition_b.py / e1improve_train_b2_checkpointed.py (imported
unmodified where possible). Output goes to an isolated path; does not touch
any existing checkpoint or the shared training_logs file.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))
SCRIPTS_DIR = REPO / "research" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from e1_train_condition_b import load_config, build_env_class
import execute_paper3_study as eps  # noqa: frozen, imported only

OUT = REPO / "research" / "paper_strengthening" / "results" / "_audit_intermediate_vs_fresh"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 42
BUDGET = 16384

cfg = load_config()
EnvClass = build_env_class()
log_path = OUT / f"B2_seed{SEED}_fresh{BUDGET}_env_log.csv"


def make_env():
    return EnvClass(arm="B2", training_seed=SEED, dim4_mode=cfg["dim4_mode"], log_file=str(log_path))


train_vec_env = VecNormalize(DummyVecEnv([make_env]), norm_obs=True, norm_reward=True, clip_obs=10.0)
hp = cfg["ppo_hyperparameters"]
model = PPO(
    hp["policy"], train_vec_env,
    learning_rate=hp["learning_rate"], n_steps=hp["n_steps"], batch_size=hp["batch_size"],
    n_epochs=hp["n_epochs"], gamma=hp["gamma"], gae_lambda=hp["gae_lambda"], clip_range=hp["clip_range"],
    verbose=0, seed=SEED,
)
callback = eps.TrainingConvergenceCallback(log_path=OUT, seed=SEED, log_freq=256)
model.learn(total_timesteps=BUDGET, callback=callback)

model_path = OUT / f"b2_seed{SEED}_fresh{BUDGET}.zip"
norm_path = OUT / f"b2_seed{SEED}_fresh{BUDGET}_vecnormalize.pkl"
model.save(str(model_path))
train_vec_env.save(str(norm_path))
print("Saved:", model_path, norm_path)
