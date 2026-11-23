"""
E1-Improve V3 -- entropy-regularization test (new, exploratory, development-only).

Motivation (established this pass, not previously in any report):
  1. `e1_action_collapse_diagnostic.py` (same directory) re-read the existing,
     already-frozen-for-E1_DEVELOPMENT_RUN_REPORT per-step training logs and
     found that the raw PPO policy's "Same" action share rises by a mean of
     +10.9pp (B2) / +11.1pp (B0 control) from the primary-budget window
     (steps 1-24,576) to the extended-budget tail (steps 24,577-122,880),
     consistent (>=5pp) across all 5/5 training seeds for BOTH arms. This is
     a general training-duration effect, not B2-specific mode collapse.
  2. Reading `e1_train_condition_b.py::train_condition_b_seed` (frozen driver)
     confirms its `PPO(...)` constructor call passes no `ent_coef`, so every
     E1 training run to date (B0, B2, and the original paper3
     `execute_paper3_study.py::train_ppo_seed`, which this driver's
     hyperparameters mirror) uses Stable-Baselines3's PPO default,
     `ent_coef=0.0` -- i.e. zero entropy bonus, no structural pressure against
     the policy's output distribution collapsing toward a locally-safe
     dominant action as training proceeds. This is a plausible, disclosed
     mechanism for finding (1), not a proven one.

Hypothesis (predeclared before running): adding a small, standard, non-zero
entropy coefficient (ent_coef=0.01 -- Stable-Baselines3's own PPO docstring
example value, not tuned on this problem) to the SAME B2 persona-diverse
training setup (same env, same reward, same state/action space, same grid,
same 5 training seeds, same primary/extended budgets) will reduce the
"Same"-share rise over the extended-budget tail relative to unmodified B2,
and will reduce or eliminate the primary-vs-extended MAE regression that
E1_DEVELOPMENT_RUN_REPORT.md Section 6 found for unmodified B2 (0.2735 at
primary budget vs 0.3942 at extended budget -- see that report's Sections
5a/5b).

This changes exactly ONE PPO training hyperparameter (ent_coef). It does not
touch interview_env.py's reward/state/action code, does not touch
rl/guardrails.py, does not touch e1_diverse_persona_env.py's grid/candidate
definitions (imported unmodified), and does not touch or overwrite any B0/B2
frozen result -- all outputs go to a new directory/new log-file prefix
("B2ent") never used by any prior E1 run.

Decision rule (predeclared): the mechanism is treated as SUPPORTED only if
BOTH (a) B2ent's mean Same-share rise (primary window -> extended tail) is
at least 5 percentage points lower than unmodified B2's own 10.91pp, AND
(b) B2ent's extended-budget pooled dev-grid MAE is no worse than its own
primary-budget MAE by more than 0.02 (i.e. the primary-to-extended
regression is materially reduced, not just numerically different in some
direction). Anything short of both conditions is reported as NOT supported,
regardless of whether B2ent's absolute MAE happens to look better or worse
than B2's on either budget alone -- absolute MAE comparison is reported for
completeness but is not the decision criterion, since ent_coef could change
absolute performance for reasons unrelated to the collapse mechanism.

No locked confirmatory seed, no held-out profile, and no frozen/committed
E1 V4 artifact is read for writing or written to by this file.
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

ENT_COEF = 0.01  # SB3 PPO docstring example value; not tuned on this problem

OUTPUT_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_improve_v3_entropy"
LOG_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_training_logs"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def train_b2ent_seed(training_seed: int, extended_budget: bool) -> dict:
    import execute_paper3_study as eps  # noqa: local import, frozen module
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

    cfg = load_config()
    budget_tag = "ext" if extended_budget else "primary"
    seed_dir = OUTPUT_ROOT / "B2ent" / budget_tag / f"seed_{training_seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"B2ent_{budget_tag}_seed{training_seed}.csv"

    EnvClass = build_env_class()

    def make_env():
        return EnvClass(arm="B2", training_seed=training_seed,
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
        ent_coef=ENT_COEF,
        verbose=0,
        seed=training_seed,
    )
    timesteps = cfg["timesteps_extended_budget"] if extended_budget else cfg["timesteps_primary"]
    t0 = time.time()
    model.learn(total_timesteps=timesteps, callback=callback)
    elapsed = time.time() - t0

    model_path = seed_dir / "ppo_final"
    norm_path = seed_dir / "vecnormalize.pkl"
    model.save(str(model_path))
    train_vec_env.save(str(norm_path))

    meta = {
        "arm": "B2ent", "training_seed": training_seed, "timesteps": timesteps,
        "extended_budget": extended_budget, "ent_coef": ENT_COEF,
        "elapsed_sec": round(elapsed, 2),
        "per_step_log": str(log_path), "model_path": str(model_path) + ".zip",
        "norm_path": str(norm_path),
    }
    with open(seed_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--budgets", nargs="+", choices=["primary", "extended"], default=["primary", "extended"])
    args = parser.parse_args()

    cfg = load_config()
    seeds = cfg["training_seeds"]
    summary = []
    for budget in args.budgets:
        extended = budget == "extended"
        for seed in seeds:
            try:
                meta = train_b2ent_seed(seed, extended_budget=extended)
                print(f"[B2ent {budget} seed={seed}] completed in {meta['elapsed_sec']:.1f}s")
                summary.append({"status": "completed", **meta})
            except Exception as exc:  # noqa: BLE001
                print(f"[B2ent {budget} seed={seed}] FAILED: {exc!r}")
                summary.append({"status": "failed", "budget": budget, "training_seed": seed, "error": repr(exc)})

    summary_path = OUTPUT_ROOT / "training_run_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to {summary_path}")
    return 0 if all(s["status"] == "completed" for s in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
