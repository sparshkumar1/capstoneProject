"""
E1 Dynamics Match V1 -- configurable training-environment variant for the
three factors (E1_DYNAMICS_MATCH_V1_PROTOCOL.md section 2). NOT executed
training code; this file only defines the environment class and a factory.

DRAFT / NOT YET APPROVED FOR TRAINING. Presented for review per the task's
Phase 3 ("present the exact planned code changes... before that approval").

Design (minimises new code; two of the three factors need none at all):

  Factor B (episode horizon) and Factor C (initial difficulty) are ALREADY
  configurable, unmodified, frozen InterviewEnv constructor parameters
  (`max_steps`, `initial_difficulty`) -- no new code, just different kwargs.

  Factor A (difficulty step size / floor bound) is NOT independently
  configurable in the frozen InterviewEnv (step() hard-codes +/-0.1 and a
  0.1 floor, rl/env/interview_env.py:401-405), so this file adds a minimal
  subclass, `DynamicsVariantEnv`, that:
    1. Calls the frozen, unmodified `super().step(action)` in full --
       meaning reward is computed EXACTLY as the frozen code computes it
       (reward depends only on perf/conf/hes/gap/oracle-match using the
       PRE-step difficulty and the post-guardrail action, never on what the
       difficulty becomes afterward -- verified by reading
       rl/env/interview_env.py:340-398, none of which references the
       difficulty value the step is about to produce).
    2. Reads `info["final_action"]` -- the actual post-guardrail action the
       frozen step() applied (exposed unmodified at interview_env.py:446)
       -- and RE-derives the resulting difficulty using this variant's own
       step_size/floor/ceiling instead of the frozen 0.1/0.1/1.0 constants,
       overwriting `self.difficulty` and `obs[5]` accordingly.
  This changes only which difficulty value the NEXT step's candidate call
  and NEXT observation see; it changes nothing about the reward function,
  the guardrail/shield logic (still the frozen, unmodified
  `_apply_guardrails` called inside `super().step()`), the action space, or
  the observation space bounds (`Box(0,1,shape=(6,))`, preserved: floor/
  ceiling are always chosen inside [0,1]).

No frozen file is modified. `e1_train_condition_b.py::build_env_class()` is
imported and used completely unmodified as the base class.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from e1_train_condition_b import build_env_class, load_config  # noqa: E402

cfg = load_config()

# ---------------------------------------------------------------------------
# Factor level definitions -- section 2 of the protocol, no new thresholds
# beyond the evaluation-equivalent values already documented in
# E1_IMPROVE_V1_REPORT.md section 2 and re-verified in this iteration's
# Phase 1 audit.
# ---------------------------------------------------------------------------

FACTOR_A_LEVELS = {
    "original": {"step_size": 0.1, "diff_floor": 0.1, "diff_ceiling": 1.0},  # frozen InterviewEnv's own constants
    "matched":  {"step_size": 0.2, "diff_floor": 0.2, "diff_ceiling": 1.0},  # eval's +/-1.0 on [1,5], normalized (/5)
}
FACTOR_B_LEVELS = {
    "original": {"max_steps": 15},  # frozen InterviewEnv default
    "matched":  {"max_steps": 10},  # evaluation's max_steps
}
FACTOR_C_LEVELS = {
    "original": {"initial_difficulty": None},  # frozen: Uniform(0.3, 0.7) at reset()
    "matched":  {"initial_difficulty": 0.6},    # evaluation's fixed cur=3.0/5.0
}


def build_variant_env_class(step_size: float, diff_floor: float, diff_ceiling: float):
    """Returns a new environment class: the existing, unmodified E1 B2
    training env (DiversePersonaAlignedEnv, from e1_train_condition_b.py),
    with ONLY the post-guardrail difficulty-transition step size/bounds
    overridden. Reward, guardrails, observation/action space, and candidate
    construction are all inherited unmodified."""
    Base = build_env_class()

    class DynamicsVariantEnv(Base):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.step_size = float(step_size)
            self.diff_floor = float(diff_floor)
            self.diff_ceiling = float(diff_ceiling)
            assert 0.0 <= self.diff_floor < self.diff_ceiling <= 1.0

        def step(self, action):
            pre_difficulty = self.difficulty
            obs, reward, terminated, truncated, info = super().step(action)
            final_action = int(info["final_action"])
            if final_action == 0:      # Easier
                new_difficulty = max(self.diff_floor, pre_difficulty - self.step_size)
            elif final_action == 2:    # Harder
                new_difficulty = min(self.diff_ceiling, pre_difficulty + self.step_size)
            else:                       # Same
                new_difficulty = pre_difficulty
            self.difficulty = new_difficulty
            obs = obs.copy()
            obs[5] = new_difficulty
            self.last_obs = obs.copy()
            info = dict(info)
            info["difficulty"] = new_difficulty
            return obs, reward, terminated, truncated, info

    return DynamicsVariantEnv


def make_dynmatch_env(arm_label: str, training_seed: int, factor_a: str, factor_b: str, factor_c: str, log_file: str):
    """arm_label in {'B2'} (only B2 is used, per protocol section 4).
    factor_a/b/c in {'original','matched'}."""
    EnvClass = build_variant_env_class(**FACTOR_A_LEVELS[factor_a])
    kwargs = {}
    kwargs.update(FACTOR_B_LEVELS[factor_b])
    kwargs.update(FACTOR_C_LEVELS[factor_c])
    return EnvClass(
        arm=arm_label, training_seed=training_seed, dim4_mode=cfg["dim4_mode"],
        log_file=log_file, **kwargs,
    )


def arm_label_for(factor_a: str, factor_b: str, factor_c: str) -> str:
    """Deterministic short label, e.g. 'OOO', 'MMM', 'MOM'."""
    return "".join(f[0].upper() for f in (factor_a, factor_b, factor_c))


ALL_8_ARMS = [
    (a, b, c)
    for a in ("original", "matched")
    for b in ("original", "matched")
    for c in ("original", "matched")
]
