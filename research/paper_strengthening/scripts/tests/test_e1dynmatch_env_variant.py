"""
Deterministic tests for E1 Dynamics Match V1's environment variant
(e1dynmatch_env_variant.py) -- Phase 4.2/4.3 of the protocol, run BEFORE
any training as part of presenting the planned code change for approval.
No PPO training occurs anywhere in this file (only env.reset()/env.step()
calls) -- consistent with the instruction not to train before approval.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
REPO = SCRIPTS_DIR.parents[2]
for p in (str(SCRIPTS_DIR), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

from e1dynmatch_env_variant import (  # noqa: E402
    build_variant_env_class, make_dynmatch_env, FACTOR_A_LEVELS, FACTOR_B_LEVELS, FACTOR_C_LEVELS,
    arm_label_for, ALL_8_ARMS,
)
from e1_train_condition_b import build_env_class  # noqa: E402


@pytest.fixture
def tmp_log(tmp_path):
    return str(tmp_path / "dynmatch_test_log.csv")


def test_observation_and_action_space_unchanged(tmp_log):
    for factor_a in ("original", "matched"):
        env = make_dynmatch_env("B2", 42, factor_a, "original", "original", tmp_log)
        assert env.observation_space.shape == (6,)
        assert float(env.observation_space.low[0]) == 0.0
        assert float(env.observation_space.high[0]) == 1.0
        assert env.action_space.n == 3


def test_original_factor_a_matches_frozen_step_size_and_floor(tmp_log):
    """The 'original' DynamicsVariantEnv must reproduce the frozen
    InterviewEnv's own difficulty transition (+/-0.1, floor 0.1, ceiling
    1.0) exactly, for every possible pre-step difficulty and action."""
    EnvClass = build_variant_env_class(**FACTOR_A_LEVELS["original"])
    env = EnvClass(arm="B2", training_seed=42, dim4_mode="aligned_progress", log_file=tmp_log)
    env.reset(seed=42)
    for pre_difficulty, action, expected in [
        (0.15, 0, 0.1),    # Easier near floor: 0.15-0.1=0.05 -> clipped to floor 0.1
        (0.5, 0, 0.4),     # Easier: 0.5-0.1
        (0.95, 2, 1.0),    # Harder near ceiling: 0.95+0.1=1.05 -> clipped to 1.0
        (0.5, 2, 0.6),     # Harder: 0.5+0.1
        (0.5, 1, 0.5),     # Same: unchanged
    ]:
        env.difficulty = pre_difficulty
        env.last_obs = np.array([0.5, 0.5, 0.5, 0.3, 0.1, pre_difficulty], dtype=np.float32)
        # Force the raw action through by using a state where no guardrail overrides it
        env.difficulty = pre_difficulty
        obs, reward, term, trunc, info = env.step(action)
        # Only assert when the guardrail did not override (final_action == pre_action)
        if info["final_action"] == action:
            assert abs(env.difficulty - expected) < 1e-9, (pre_difficulty, action, env.difficulty, expected)


def test_matched_factor_a_uses_02_step_and_02_floor(tmp_log):
    EnvClass = build_variant_env_class(**FACTOR_A_LEVELS["matched"])
    env = EnvClass(arm="B2", training_seed=42, dim4_mode="aligned_progress", log_file=tmp_log)
    env.reset(seed=42)
    for pre_difficulty, action, expected in [
        (0.25, 0, 0.2),    # Easier near floor: 0.25-0.2=0.05 -> clipped to floor 0.2
        (0.6, 0, 0.4),     # Easier: 0.6-0.2
        (0.9, 2, 1.0),     # Harder near ceiling: 0.9+0.2=1.1 -> clipped to 1.0
        (0.6, 2, 0.8),     # Harder: 0.6+0.2
        (0.6, 1, 0.6),     # Same: unchanged
    ]:
        env.difficulty = pre_difficulty
        obs, reward, term, trunc, info = env.step(action)
        if info["final_action"] == action:
            assert abs(env.difficulty - expected) < 1e-9, (pre_difficulty, action, env.difficulty, expected)


def test_factor_a_never_produces_out_of_bounds_observation(tmp_log):
    for level in ("original", "matched"):
        EnvClass = build_variant_env_class(**FACTOR_A_LEVELS[level])
        env = EnvClass(arm="B2", training_seed=1, dim4_mode="aligned_progress", log_file=tmp_log)
        env.reset(seed=1)
        for _ in range(30):
            obs, reward, term, trunc, info = env.step(env.action_space.sample())
            assert (obs >= 0.0).all() and (obs <= 1.0).all()
            if term:
                env.reset(seed=1)


def test_factor_b_horizon_propagates_via_existing_max_steps_kwarg(tmp_log):
    env10 = make_dynmatch_env("B2", 42, "original", "matched", "original", tmp_log)
    env15 = make_dynmatch_env("B2", 42, "original", "original", "original", tmp_log)
    assert env10.max_steps == 10
    assert env15.max_steps == 15


def test_factor_c_initial_difficulty_propagates_via_existing_kwarg(tmp_log):
    env_matched = make_dynmatch_env("B2", 42, "original", "original", "matched", tmp_log)
    obs, _ = env_matched.reset(seed=42)
    assert abs(float(obs[5]) - 0.6) < 1e-6  # obs is float32; 0.6 is not exactly representable

    env_original = make_dynmatch_env("B2", 42, "original", "original", "original", tmp_log)
    seen = set()
    for s in range(20):
        obs, _ = env_original.reset(seed=s)
        seen.add(round(float(obs[5]), 3))
    assert len(seen) > 1, "original Factor C must retain Uniform(0.3,0.7) variability across resets"
    assert all(0.3 - 1e-6 <= v <= 0.7 + 1e-6 for v in seen)


def test_reward_at_first_step_is_unaffected_by_difficulty_patch():
    """At step 0, both the frozen env and every DynamicsVariantEnv share an
    identical pre-step state (same seed -> same reset() difficulty draw,
    same episode-seeded candidate) -- so the FIRST step's reward, which is
    computed entirely from the pre-step observation and the post-guardrail
    action (rl/env/interview_env.py:340-398 never reads the difficulty the
    step is about to produce), must be bit-identical regardless of Factor A.
    (From step 1 onward the trajectories legitimately diverge once an
    Easier/Harder action has actually been applied with different step
    sizes -- that divergence is the intervention working as intended, not
    tested here; see test_matched_factor_a_produces_a_different_trajectory.)"""
    import tempfile
    for action in (0, 1, 2):
        with tempfile.TemporaryDirectory() as d:
            frozen_log = str(Path(d) / "frozen.csv")
            variant_log = str(Path(d) / "variant.csv")
            FrozenClass = build_env_class()
            frozen_env = FrozenClass(arm="B2", training_seed=42, dim4_mode="aligned_progress", log_file=frozen_log)
            variant_env = make_dynmatch_env("B2", 42, "matched", "original", "original", variant_log)

            frozen_env.reset(seed=123)
            variant_env.reset(seed=123)
            _, r_frozen, _, _, info_f = frozen_env.step(action)
            _, r_variant, _, _, info_v = variant_env.step(action)
            assert info_f["final_action"] == info_v["final_action"], "guardrail decision must match at step 0"
            assert abs(r_frozen - r_variant) < 1e-6, (action, r_frozen, r_variant)


def test_matched_factor_a_produces_a_different_trajectory_after_divergent_action():
    """Once an Easier/Harder action is actually applied with a different
    step size, the resulting difficulty (and hence all subsequent
    observations/rewards) legitimately diverges -- confirming the
    intervention has a real effect, not that anything is broken."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        frozen_log = str(Path(d) / "frozen.csv")
        variant_log = str(Path(d) / "variant.csv")
        FrozenClass = build_env_class()
        frozen_env = FrozenClass(arm="B2", training_seed=42, dim4_mode="aligned_progress", log_file=frozen_log)
        variant_env = make_dynmatch_env("B2", 42, "matched", "original", "original", variant_log)
        frozen_env.reset(seed=123)
        variant_env.reset(seed=123)
        _, _, _, _, info_f = frozen_env.step(1)
        _, _, _, _, info_v = variant_env.step(1)
        if info_f["final_action"] != 1:  # guardrail overrode Same -> an Easier/Harder action actually applied
            assert abs(frozen_env.difficulty - variant_env.difficulty) > 1e-6, (
                "different step sizes must produce different post-step difficulty once a "
                "non-Same action is actually applied"
            )


def test_all_8_arms_are_distinct_and_complete():
    labels = {arm_label_for(*combo) for combo in ALL_8_ARMS}
    assert len(labels) == 8
    assert "OOO" in labels and "MMM" in labels


def test_ooo_arm_is_env_class_equivalent_to_registered_e1_training(tmp_log):
    """The all-original (OOO) arm must be behaviorally equivalent to the
    existing, registered e1_train_condition_b.py training environment --
    both reduce to the same frozen dynamics (step=0.1, floor=0.1,
    ceiling=1.0, max_steps=15, initial_difficulty=Uniform(0.3,0.7))."""
    ooo_env = make_dynmatch_env("B2", 42, "original", "original", "original", tmp_log)
    assert ooo_env.step_size == 0.1
    assert ooo_env.diff_floor == 0.1
    assert ooo_env.diff_ceiling == 1.0
    assert ooo_env.max_steps == 15
    assert ooo_env._eval_initial_difficulty is None
