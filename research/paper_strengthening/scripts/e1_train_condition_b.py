"""
E1 -- Condition B (B0/B2) training driver, per
E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V4.md sections 1.2, 5, and 7.

NOT EXECUTED by this implementation pass. This file defines everything needed
to run a single (arm, training_seed) training job, reading its configuration
from e1_config.json (no hard-coded hyperparameters), but performs no training
when merely imported -- exactly like research/scripts/execute_paper3_study.py,
which this file imports unmodified and whose main() is never called.

Reward, state definition (6-D), action space (3 discrete actions), and every
PPO hyperparameter are unchanged from the frozen training routine
(research/scripts/execute_paper3_study.py::train_ppo_seed). The ONLY change
relative to that routine is which candidate InterviewEnv.reset() constructs
at the start of each episode -- everything else (step(), reward computation,
guardrail application inside training, PPO's own hyperparameters) is
inherited unmodified from AlignedInterviewEnv / InterviewEnv.

Output paths are new and separate from every frozen/historical directory:
  research/paper_strengthening/results/e1_training/<arm>/seed_<seed>/
  research/paper_strengthening/results/e1_training_logs/<arm>_seed<seed>.csv
Nothing under research/experiments/paper3/, research/confirmatory/X3-A/, or
rl/checkpoints/ is read for writing, or written to, by this file.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
SCRIPTS_DIR = REPO / "research" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

CONFIG_PATH = THIS_DIR / "e1_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_env_class():
    """
    Returns the real DiversePersonaAlignedEnv class, subclassing the frozen
    AlignedInterviewEnv (research/scripts/execute_paper3_study.py) with ONLY
    reset()'s candidate construction overridden, per protocol V4 section 1.2.
    Imports execute_paper3_study unmodified; its main() is never called
    (identical precedent to research/analysis/phase1/x3_0/x3_0c_replay.py).
    """
    import execute_paper3_study as eps  # noqa: local import, frozen module, main() never called
    from e1_diverse_persona_env import make_candidate

    class _DiversePersonaAlignedEnv(eps.AlignedInterviewEnv):
        def __init__(self, arm: str, training_seed: int, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if arm not in ("B0", "B2"):
                raise ValueError(f"Unknown arm {arm!r}; expected 'B0' or 'B2'")
            self.arm = arm
            self.training_seed = int(training_seed)
            self._episode_index = 0

        def reset(self, *, seed=None, options=None):
            self.sim_candidate = make_candidate(self.arm, self.training_seed, self._episode_index)
            self._episode_index += 1
            return super().reset(seed=seed, options=options)

    return _DiversePersonaAlignedEnv


def train_condition_b_seed(arm: str, training_seed: int, output_root: Path = None,
                            extended_budget: bool = False) -> dict:
    """
    Trains one (arm, training_seed) PPO policy. NOT CALLED anywhere in this
    implementation pass -- see the accompanying implementation report for why
    (training execution is explicitly out of scope for this turn; this
    function exists, complete and importable, for the later, approved
    development run).
    """
    import execute_paper3_study as eps  # noqa: local import, frozen module
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

    cfg = load_config()
    if output_root is None:
        output_root = REPO / "research" / "paper_strengthening" / "results" / "e1_training"
    output_root = Path(output_root)
    seed_dir = output_root / arm / f"seed_{training_seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)

    log_dir = REPO / "research" / "paper_strengthening" / "results" / "e1_training_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{arm}_seed{training_seed}.csv"

    EnvClass = build_env_class()

    def make_env():
        return EnvClass(arm=arm, training_seed=training_seed,
                         dim4_mode=cfg["dim4_mode"], log_file=str(log_path))

    train_vec_env = VecNormalize(DummyVecEnv([make_env]), norm_obs=True, norm_reward=True, clip_obs=10.0)

    callback = eps.TrainingConvergenceCallback(log_path=seed_dir, seed=training_seed, log_freq=256)

    hp = cfg["ppo_hyperparameters"]
    model = PPO(
        hp["policy"],
        train_vec_env,
        learning_rate=hp["learning_rate"],
        n_steps=hp["n_steps"],
        batch_size=hp["batch_size"],
        n_epochs=hp["n_epochs"],
        gamma=hp["gamma"],
        gae_lambda=hp["gae_lambda"],
        clip_range=hp["clip_range"],
        verbose=0,
        seed=training_seed,
    )
    timesteps = cfg["timesteps_extended_budget"] if extended_budget else cfg["timesteps_primary"]
    model.learn(total_timesteps=timesteps, callback=callback)

    model_path = seed_dir / "ppo_final"
    norm_path = seed_dir / "vecnormalize.pkl"
    model.save(str(model_path))
    train_vec_env.save(str(norm_path))

    meta = {
        "arm": arm, "training_seed": training_seed, "timesteps": timesteps,
        "extended_budget": extended_budget, "config": str(CONFIG_PATH),
        "per_step_log": str(log_path), "model_path": str(model_path) + ".zip",
        "norm_path": str(norm_path),
    }
    with open(seed_dir / "e1_training_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="E1 Condition B training driver (V4). NOT invoked by this pass.")
    parser.add_argument("--arm", required=True, choices=["B0", "B2"])
    parser.add_argument("--training_seed", required=True, type=int)
    parser.add_argument("--extended_budget", action="store_true")
    args = parser.parse_args()
    print(train_condition_b_seed(args.arm, args.training_seed, extended_budget=args.extended_budget))
