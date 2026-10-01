"""
PPO V2 -- periodic-checkpointing training + predeclared checkpoint selection.

Motivation: PPO_V2_MECHANISM_DIAGNOSIS.md (same directory's parent) found the
B2 primary-vs-extended-budget regression is concentrated almost entirely
(99.4% of the pooled-cell regression) in the skill=0.80 persona, where the
raw "Harder" action rate falls from ~8-10% (primary budget, 24,576 steps) to
0-6% (extended budget, 98,304 steps) -- a narrow, persona-specific behavior
that is learned early and lost with continued training, not a general
undertraining effect. skill=0.90 is largely stable over the same interval.

Hypothesis (predeclared before this script is run): the behavior peaks
somewhere near the previously-tested primary budget and degrades roughly
monotonically afterward for the affected persona; a checkpoint-selection
strategy -- save the model periodically during one continuous training run,
evaluate EACH checkpoint on the development grid only (never confirmatory
data), and select a SINGLE cross-seed-common training-step interval (not a
per-seed cherry-pick) that minimizes cross-seed-averaged pooled dev-grid MAE
-- will recover performance at least as good as the fixed 24,576-step
primary budget, without needing to have guessed the right budget in advance.

Decision rule (predeclared): the intervention is judged SUPPORTED only if
the single selected checkpoint interval, applied uniformly across all 5
training seeds, achieves cross-seed pooled dev-grid MAE no worse than the
original fixed-primary-budget MAE (0.2735) by more than 0.01, AND is
selected using only the development grid (seeds 1001-5005), never the
locked confirmatory seeds or held-out profiles. This is compared against
two fixed-budget baselines (always-primary, always-extended) that are NOT
told the answer in advance (i.e., they are just the fixed 24576/98304
endpoints, not re-selected).

Reward, state, action space, and every PPO hyperparameter (learning_rate,
n_steps, batch_size, n_epochs, gamma, gae_lambda, clip_range) are UNCHANGED
from e1_train_condition_b.py / e1_config.json. The only change is HOW OFTEN
the model is saved during one continuous 98,304-step run and, subsequently,
which of those saved checkpoints is used at evaluation/deployment time. No
frozen driver (e1_train_condition_b.py), no frozen checkpoint, and no
confirmatory/held-out data is read for writing or written to by this file.
"""
import argparse
import json
import sys
import time
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

from e1_train_condition_b import load_config, build_env_class  # noqa: E402  (frozen, imported unmodified)

CHECKPOINT_INTERVAL = 8192  # steps; 98304 / 8192 = 12 checkpoints per seed
OUTPUT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "ppo_v2_checkpoint_selection"
LOG_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_training_logs"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def train_b2_with_periodic_checkpoints(training_seed: int) -> dict:
    import execute_paper3_study as eps  # noqa: local import, frozen module
    from stable_baselines3 import PPO
    from stable_baselines3.common.callbacks import BaseCallback, CallbackList
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

    cfg = load_config()
    seed_dir = OUTPUT_ROOT / "B2_periodic" / f"seed_{training_seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"B2v2ckpt_seed{training_seed}.csv"

    EnvClass = build_env_class()

    def make_env():
        return EnvClass(arm="B2", training_seed=training_seed,
                         dim4_mode=cfg["dim4_mode"], log_file=str(log_path))

    train_vec_env = VecNormalize(DummyVecEnv([make_env]), norm_obs=True, norm_reward=True, clip_obs=10.0)
    convergence_cb = eps.TrainingConvergenceCallback(log_path=seed_dir, seed=training_seed, log_freq=256)

    saved_checkpoints = []

    class PeriodicCheckpointCallback(BaseCallback):
        def _on_step(self) -> bool:
            if self.num_timesteps % CHECKPOINT_INTERVAL == 0:
                ckpt_dir = seed_dir / f"step_{self.num_timesteps}"
                ckpt_dir.mkdir(parents=True, exist_ok=True)
                self.model.save(str(ckpt_dir / "ppo_final"))
                self.training_env.save(str(ckpt_dir / "vecnormalize.pkl"))
                saved_checkpoints.append(self.num_timesteps)
            return True

    hp = cfg["ppo_hyperparameters"]
    model = PPO(
        hp["policy"], train_vec_env,
        learning_rate=hp["learning_rate"], n_steps=hp["n_steps"], batch_size=hp["batch_size"],
        n_epochs=hp["n_epochs"], gamma=hp["gamma"], gae_lambda=hp["gae_lambda"], clip_range=hp["clip_range"],
        verbose=0, seed=training_seed,
    )
    t0 = time.time()
    model.learn(total_timesteps=cfg["timesteps_extended_budget"],
                callback=CallbackList([convergence_cb, PeriodicCheckpointCallback()]))
    elapsed = time.time() - t0

    meta = {
        "training_seed": training_seed, "elapsed_sec": round(elapsed, 2),
        "checkpoint_interval": CHECKPOINT_INTERVAL, "checkpoints_saved": saved_checkpoints,
        "per_step_log": str(log_path),
    }
    with open(seed_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta


EXPECTED_CHECKPOINTS_PER_SEED = 98304 // CHECKPOINT_INTERVAL  # 12, derived not hard-coded twice


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    args = parser.parse_args()

    cfg = load_config()
    seeds = args.seeds or cfg["training_seeds"]
    assert len(seeds) == len(set(seeds)), f"Duplicate seed values in --seeds: {seeds}"

    summary = []
    for seed in seeds:
        try:
            meta = train_b2_with_periodic_checkpoints(seed)
            n_ckpts = len(meta["checkpoints_saved"])
            if n_ckpts != EXPECTED_CHECKPOINTS_PER_SEED:
                # A run that didn't raise but produced a truncated checkpoint
                # set (e.g. an interrupted process) must not be silently
                # recorded as "completed" -- that would let a partial run
                # into downstream selection/evaluation undetected.
                raise RuntimeError(
                    f"seed={seed}: expected {EXPECTED_CHECKPOINTS_PER_SEED} checkpoints, "
                    f"got {n_ckpts} ({meta['checkpoints_saved']})"
                )
            print(f"[seed={seed}] completed in {meta['elapsed_sec']:.1f}s, "
                  f"{n_ckpts} checkpoints saved")
            summary.append({"status": "completed", **meta})
        except Exception as exc:  # noqa: BLE001
            print(f"[seed={seed}] FAILED: {exc!r}")
            summary.append({"status": "failed", "training_seed": seed, "error": repr(exc)})

    summary_path = OUTPUT_ROOT / "training_run_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to {summary_path}")
    n_failed = sum(1 for s in summary if s["status"] != "completed")
    if n_failed:
        print(f"WARNING: {n_failed}/{len(summary)} seed(s) failed or produced a partial run -- see summary for detail.")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
