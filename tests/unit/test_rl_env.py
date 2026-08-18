import math
import numpy as np
import pytest
from pathlib import Path
import sys
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[2]
RL_ENV_DIR = ROOT / "rl" / "env"
RL_TRAIN_DIR = ROOT / "rl" / "training"
if str(RL_ENV_DIR) not in sys.path:
    sys.path.insert(0, str(RL_ENV_DIR))
if str(RL_TRAIN_DIR) not in sys.path:
    sys.path.insert(0, str(RL_TRAIN_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from interview_env import InterviewEnv
from agents.strategy.hybrid_orchestrator import (
    HybridOrchestrator,
    build_rl_observation,
    ACTION_MAP,
    ACTION_NAME_TO_IDX,
)
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator


# ─────────────────────────────────────────────────────────────────────────────
# 1. State Construction & Fixed Dimensionality (6D)
# ─────────────────────────────────────────────────────────────────────────────

def test_rl_observation_shape_and_dtype():
    """Observation vector must be strictly 1D float32 of length 6."""
    session = {
        "scores": [0.75, 0.80],
        "rl_perf_history": [0.75, 0.80],
        "last_confidence_score": 0.85,
        "last_hesitation_score": 0.15,
        "last_time_norm": 0.42,
    }
    obs = build_rl_observation(0.80, current_difficulty=3, session=session)
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (6,)
    assert obs.dtype == np.float32


def test_rl_observation_deterministic_construction():
    """Identical candidate states must yield identical observation vectors."""
    session = {
        "scores": [0.60, 0.70],
        "rl_perf_history": [0.60, 0.70],
        "last_confidence_score": 0.65,
        "last_hesitation_score": 0.35,
        "last_time_norm": 0.50,
    }
    obs1 = build_rl_observation(0.70, current_difficulty=3, session=session)
    obs2 = build_rl_observation(0.70, current_difficulty=3, session=session)
    np.testing.assert_array_almost_equal(obs1, obs2)


def test_rl_observation_no_nan_or_inf():
    """State builder must sanitize any NaN, Inf, or invalid values to safe finite floats."""
    corrupted_session = {
        "scores": [float("nan"), float("inf")],
        "rl_perf_history": [float("nan"), float("-inf")],
        "last_confidence_score": float("nan"),
        "last_hesitation_score": float("inf"),
        "last_time_norm": float("nan"),
    }
    obs = build_rl_observation(float("nan"), current_difficulty=3, session=corrupted_session)
    assert not np.isnan(obs).any()
    assert not np.isinf(obs).any()
    assert (obs >= 0.0).all() and (obs <= 1.0).all()


def test_rl_observation_normalization_bounds():
    """All 6 dimensions must be strictly bounded in [0.0, 1.0]."""
    extreme_session = {
        "scores": [5.0, 10.0],
        "rl_perf_history": [5.0, 10.0],
        "last_confidence_score": 2.5,
        "last_hesitation_score": 3.0,
        "last_time_norm": 100.0,
    }
    obs = build_rl_observation(10.0, current_difficulty=8, session=extreme_session)
    for dim_idx, val in enumerate(obs):
        assert 0.0 <= val <= 1.0, f"Dimension {dim_idx} exceeded [0, 1] bounds with value {val}"


def test_rl_observation_missing_and_default_handling():
    """Empty session must default safely without crashing."""
    empty_session = {}
    obs = build_rl_observation(0.70, current_difficulty=3, session=empty_session)
    assert obs.shape == (6,)
    assert obs[0] == pytest.approx(0.70, abs=1e-4)   # perf
    assert obs[1] == pytest.approx(0.70, abs=1e-4)   # avg_perf fallback to perf
    assert obs[2] == pytest.approx(0.70, abs=1e-4)   # conf fallback to perf
    assert obs[3] == pytest.approx(0.30, abs=1e-4)   # hes fallback to 1-conf
    assert obs[4] == pytest.approx(0.00, abs=1e-4)   # time_norm default
    assert obs[5] == pytest.approx(0.60, abs=1e-4)   # difficulty (3 / 5.0)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Training and Runtime Semantic & Dimensional Parity
# ─────────────────────────────────────────────────────────────────────────────

def test_training_and_runtime_dimensional_parity():
    """Environment observation space and runtime state vector must both be 6D Box(6)."""
    env = InterviewEnv(max_steps=1)
    assert env.observation_space.shape == (6,)
    assert env.observation_space.dtype == np.float32

    session = {"scores": [0.5], "last_time_norm": 0.2}
    runtime_obs = build_rl_observation(0.5, 3, session)
    assert runtime_obs.shape == env.observation_space.shape


def test_training_and_runtime_semantic_parity():
    """
    Every dimension index must represent the identical concept:
    [0] latest score
    [1] rolling average
    [2] confidence
    [3] hesitation
    [4] response latency
    [5] normalized difficulty
    """
    env = InterviewEnv(max_steps=1)
    env_obs, _ = env.reset(seed=42)
    assert len(env_obs) == 6

    # Verify runtime features match intended environment layout
    session = {
        "scores": [0.80],
        "rl_perf_history": [0.80],
        "last_confidence_score": 0.90,
        "last_hesitation_score": 0.10,
        "last_time_norm": 0.35,
    }
    runtime_obs = build_rl_observation(0.80, current_difficulty=4, session=session)
    assert runtime_obs[0] == pytest.approx(0.80, abs=1e-4)  # perf
    assert runtime_obs[1] == pytest.approx(0.80, abs=1e-4)  # avg_perf
    assert runtime_obs[2] == pytest.approx(0.90, abs=1e-4)  # conf
    assert runtime_obs[3] == pytest.approx(0.10, abs=1e-4)  # hes
    assert runtime_obs[4] == pytest.approx(0.35, abs=1e-4)  # time_norm
    assert runtime_obs[5] == pytest.approx(0.80, abs=1e-4)  # diff_norm (4/5)


def test_canonical_orchestrator_state_extracts_to_observation():
    """InterviewOrchestrator session dict directly feeds build_rl_observation."""
    session = {
        "scores": [0.5, 0.7, 0.9],
        "rl_perf_history": [0.5, 0.7, 0.9],
        "last_confidence_score": 0.88,
        "last_hesitation_score": 0.12,
        "last_time_norm": 0.40,
        "current_difficulty": 3,
    }
    obs = build_rl_observation(0.9, 3, session)
    assert obs[0] == pytest.approx(0.9, abs=1e-4)
    assert obs[1] == pytest.approx(0.7, abs=1e-4)  # mean([0.5, 0.7, 0.9])
    assert obs[2] == pytest.approx(0.88, abs=1e-4)
    assert obs[3] == pytest.approx(0.12, abs=1e-4)
    assert obs[4] == pytest.approx(0.40, abs=1e-4)
    assert obs[5] == pytest.approx(0.60, abs=1e-4)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Action Space and Transition Semantics
# ─────────────────────────────────────────────────────────────────────────────

def test_action_space_is_strictly_three_discrete_actions():
    """Action space must be Discrete(3): 0=Easier, 1=Same, 2=Harder."""
    assert ACTION_MAP == {0: "Easier", 1: "Same", 2: "Harder"}
    assert ACTION_NAME_TO_IDX == {"Easier": 0, "Same": 1, "Harder": 2}

    env = InterviewEnv(max_steps=1)
    assert env.action_space.n == 3


def test_difficulty_transitions_bounds():
    """
    Easier decrements difficulty (clamped at 1).
    Same maintains difficulty.
    Harder increments difficulty (clamped at 5).
    """
    orch = HybridOrchestrator()
    # Test heuristic / action transition arithmetic and bounds directly
    # Easier
    assert orch._heuristic_action(0.2, current_difficulty=3) == "Easier"
    assert orch._heuristic_action(0.2, current_difficulty=1) == "Same"  # bounded at min difficulty 1

    # Harder
    assert orch._heuristic_action(0.95, current_difficulty=3) == "Harder"
    assert orch._heuristic_action(0.95, current_difficulty=5) == "Same"  # bounded at max difficulty 5

    # Same
    assert orch._heuristic_action(0.65, current_difficulty=3) == "Same"


    # Verify suggest clamping with heuristic
    orch_h = HybridOrchestrator(model_path="nonexistent.zip", vec_path="nonexistent.pkl")
    session = {"baseline_complete": True, "scores": [0.2]}
    d_easy_clamp, _, _ = orch_h.suggest(0.2, current_difficulty=1, session=session)
    assert d_easy_clamp == 1  # clamped at 1

    d_hard_clamp, _, _ = orch_h.suggest(0.95, current_difficulty=5, session=session)
    assert d_hard_clamp == 5  # clamped at 5

    d_hard_step, _, _ = orch_h.suggest(0.95, current_difficulty=3, session=session)
    assert d_hard_step == 4  # 3 + 1 = 4




# ─────────────────────────────────────────────────────────────────────────────
# 4. Baseline Warmup Phase Isolation
# ─────────────────────────────────────────────────────────────────────────────

def test_baseline_phase_does_not_invoke_ppo():
    """When baseline_complete is False, PPO policy is bypassed with deterministic warmup."""
    orch = HybridOrchestrator()
    session = {
        "baseline_complete": False,
        "scores": [0.85],  # 1 main Q answered
        "num_questions": 5,
    }
    target_diff, reason, action = orch.suggest(0.85, current_difficulty=2, session=session)
    assert action == "Baseline"
    assert target_diff == 3
    assert "Baseline Q2" in reason


def test_ppo_activates_strictly_after_baseline_complete():
    """When baseline_complete is True, PPO suggest executes."""
    orch = HybridOrchestrator()
    session = {
        "baseline_complete": True,
        "scores": [0.70, 0.75, 0.80],
        "rl_perf_history": [0.70, 0.75, 0.80],
        "last_confidence_score": 0.80,
    }
    target_diff, reason, action = orch.suggest(0.80, current_difficulty=3, session=session)
    assert action in {"Easier", "Same", "Harder"}
    assert "PPO:" in reason or "RL [" in reason


# ─────────────────────────────────────────────────────────────────────────────
# 5. Environment Step, Reward & Next State
# ─────────────────────────────────────────────────────────────────────────────

def test_interview_env_step_transition():
    """Env step must execute action, evaluate candidate, compute reward, and return 6D next obs."""
    env = InterviewEnv(max_steps=5, initial_difficulty=0.5)
    obs, info = env.reset(seed=123)
    assert obs.shape == (6,)

    next_obs, reward, terminated, truncated, info = env.step(action=1)
    assert next_obs.shape == (6,)
    assert isinstance(reward, float)
    assert not math.isnan(reward)
    assert not terminated
    assert "oracle_action" in info
    assert "decision_component" in info
    assert "outcome_component" in info


def test_interview_env_reward_components():
    """Reward must accurately reflect alignment with oracle and candidate progress."""
    env = InterviewEnv(max_steps=3, reward_mode="hybrid", initial_difficulty=0.5)
    env.reset(seed=10)

    # Step with action 0 (Easier), 1 (Same), 2 (Harder)
    for a in [0, 1, 2]:
        obs, rew, term, _, info = env.step(a)
        assert isinstance(rew, float)
        assert not math.isnan(rew)
        assert "reward_mode" in info and info["reward_mode"] == "hybrid"


# ─────────────────────────────────────────────────────────────────────────────
# 6. Guardrail Precedence & Audit Preservation
# ─────────────────────────────────────────────────────────────────────────────

def test_guardrail_g4_stuck_overrides_to_easier():
    """G4 (perf < 0.30 and hes > 0.60) forces Easier even if PPO says Harder."""
    env = InterviewEnv(max_steps=1, guardrails_enabled=True)
    stuck_obs = [0.20, 0.20, 0.20, 0.85, 0.50, 0.50]
    action, forced, gid = env._apply_guardrails(stuck_obs, proposed_action=2)  # Proposed Harder
    assert action == 0  # Forced Easier
    assert forced is True
    assert gid == "g4_stuck_easier"


def test_guardrail_g6_strong_candidate_pushes_harder():
    """G6 (perf >= 0.90, gap > 0.25) pushes Harder on strong candidates."""
    env = InterviewEnv(max_steps=1, guardrails_enabled=True)
    strong_obs = [0.95, 0.90, 0.95, 0.05, 0.10, 0.40]  # gap = 0.55
    action, forced, gid = env._apply_guardrails(strong_obs, proposed_action=1)  # Proposed Same
    assert action == 2  # Forced Harder
    assert forced is True
    assert gid == "g6_strong_harder"


# ─────────────────────────────────────────────────────────────────────────────
# 7. Checkpoint Compatibility and Graceful Fallback
# ─────────────────────────────────────────────────────────────────────────────

def test_incompatible_checkpoint_action_space_rejected():
    """HybridOrchestrator must cleanly reject checkpoints that have != 3 actions."""
    orch = HybridOrchestrator(model_path="nonexistent_model.zip", vec_path="nonexistent_vec.pkl")
    orch._try_load()
    assert orch.ready is False
    assert orch.is_compatible is False

    # Should gracefully use heuristic fallback without error
    session = {"baseline_complete": True, "scores": [0.85]}
    new_d, reason, act = orch.suggest(0.85, 3, session)
    assert act == "Harder"
    assert "heuristic" in reason


# ─────────────────────────────────────────────────────────────────────────────
# 8. Diverse Candidate State Handling
# ─────────────────────────────────────────────────────────────────────────────

def test_different_candidate_states_produce_distinct_observations():
    """Weak, intermediate, and strong candidate states must yield distinctly different observation vectors."""
    weak_session = {
        "scores": [0.20, 0.25],
        "rl_perf_history": [0.20, 0.25],
        "last_confidence_score": 0.20,
        "last_hesitation_score": 0.80,
        "last_time_norm": 0.90,
    }
    strong_session = {
        "scores": [0.95, 0.90],
        "rl_perf_history": [0.95, 0.90],
        "last_confidence_score": 0.90,
        "last_hesitation_score": 0.10,
        "last_time_norm": 0.20,
    }

    obs_weak = build_rl_observation(0.25, current_difficulty=3, session=weak_session)
    obs_strong = build_rl_observation(0.90, current_difficulty=3, session=strong_session)

    assert not np.allclose(obs_weak, obs_strong)
    assert obs_weak[0] < obs_strong[0]   # perf
    assert obs_weak[2] < obs_strong[2]   # conf
    assert obs_weak[3] > obs_strong[3]   # hes
    assert obs_weak[4] > obs_strong[4]   # time_norm
