"""
tests/unit/test_paper3_blockers.py
==================================
Unit and regression tests verifying all 5 blocker repairs for Paper 3:
1. Dimension 4 state semantic parity (t / T progress ratio).
2. Fixed-difficulty baseline calibration (non-zero tracking error, MAE ≈ 1.200).
3. Canonical guardrails hierarchy and override behavior (G1-G6).
4. Strict checkpoint directory isolation for historical mismatch ablation.
5. Training convergence callback logging (step-level metrics, CSV/JSON export).
"""

import math
import numpy as np
import pytest
from pathlib import Path
import sys
import tempfile
import json
import csv

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
from rl.guardrails import apply_canonical_guardrails
from agents.strategy.hybrid_orchestrator import build_rl_observation
from research.scripts.run_paper3_study import (
    AlignedInterviewEnv,
    PERSONA_TARGETS,
    run_session_trajectory,
    TrainingConvergenceCallback,
    train_ppo_seed,
)


# ==============================================================================
# Blocker 1: Dimension 4 State Semantic Parity (t / T)
# ==============================================================================

def test_dim4_progress_ratio_in_interview_env():
    """InterviewEnv must compute dimension 4 as current_step / max_steps."""
    env = InterviewEnv(max_steps=10)
    obs, _ = env.reset(seed=42)
    assert obs[4] == 0.0

    # Step 1: progress = 1/10 = 0.1
    obs, _, _, _, info = env.step(1)
    assert obs[4] == pytest.approx(0.1, abs=1e-4)
    assert info["progress"] == pytest.approx(0.1, abs=1e-4)
    assert "time_norm" in info  # Latency info still available for auxiliary telemetry

    # Step 5: progress = 5/10 = 0.5
    for _ in range(4):
        obs, _, _, _, info = env.step(1)
    assert obs[4] == pytest.approx(0.5, abs=1e-4)
    assert info["progress"] == pytest.approx(0.5, abs=1e-4)


def test_dim4_progress_ratio_in_hybrid_orchestrator():
    """HybridOrchestrator.build_rl_observation must populate dimension 4 with session progress."""
    # Direct progress key
    session_with_progress = {"progress": 0.40, "scores": [0.8]}
    obs = build_rl_observation(0.8, 3, session_with_progress)
    assert obs[4] == pytest.approx(0.40, abs=1e-4)

    # Derived progress from turn_idx / total_turns
    session_with_turns = {"turn_idx": 7, "total_turns": 10, "scores": [0.7]}
    obs2 = build_rl_observation(0.7, 3, session_with_turns)
    assert obs2[4] == pytest.approx(0.70, abs=1e-4)


def test_aligned_interview_env_modes():
    """AlignedInterviewEnv respects dim4_mode configurations."""
    # aligned_progress mode
    env_prog = AlignedInterviewEnv(max_steps=10, dim4_mode="aligned_progress")
    env_prog.reset(seed=42)
    obs_prog, _, _, _, _ = env_prog.step(1)
    assert obs_prog[4] == pytest.approx(0.10, abs=1e-4)

    # zero mode
    env_zero = AlignedInterviewEnv(max_steps=10, dim4_mode="zero")
    env_zero.reset(seed=42)
    obs_zero, _, _, _, _ = env_zero.step(1)
    assert obs_zero[4] == 0.0


# ==============================================================================
# Blocker 2: Fixed-Difficulty Baseline Calibration
# ==============================================================================

def test_fixed_difficulty_baseline_non_zero_tracking_error():
    """
    Fixed-difficulty baseline must evaluate candidates at their actual persona skills,
    producing non-zero tracking error (target MAE = 1.200 across the 5 canonical personas).
    """
    tracking_errors = []
    for persona_name, cfg in PERSONA_TARGETS.items():
        res = run_session_trajectory(
            policy_mode="Fixed",
            persona_name=persona_name,
            dim4_mode="aligned_progress",
            eval_seed=1001,
            guardrails_enabled=False,
            max_steps=10,
        )
        assert res["final_difficulty"] == 3.0
        expected_te = abs(3.0 - cfg["target_difficulty"])
        assert res["target_tracking_error"] == pytest.approx(expected_te, abs=1e-3)
        tracking_errors.append(res["target_tracking_error"])

    mean_te = float(np.mean(tracking_errors))
    # Targets: [1.0, 1.5, 3.0, 4.0, 4.5] -> errors: [2.0, 1.5, 0.0, 1.0, 1.5] -> mean = 1.200
    assert mean_te == pytest.approx(1.200, abs=1e-3)
    assert mean_te > 0.0  # Confirms artifact of 0.000 is resolved


# ==============================================================================
# Blocker 3: Canonical Guardrails Hierarchy & Deterministic Overrides
# ==============================================================================

def test_guardrail_infrastructure_failure():
    """G0: Infrastructure failure must maintain difficulty (Same = 1)."""
    action, overridden, gid = apply_canonical_guardrails(
        perf=0.9, avg_perf=0.9, conf=0.9, hes=0.1, progress=0.5, difficulty=0.6,
        proposed_action=2, is_infrastructure_failure=True
    )
    assert action == 1
    assert overridden is True
    assert gid == "guardrail_infra_failure_same"


def test_guardrail_g4_stuck_candidate():
    """G4: Severe underperformance with high hesitation forces Easier (0)."""
    action, overridden, gid = apply_canonical_guardrails(
        perf=0.20, avg_perf=0.25, conf=0.2, hes=0.75, progress=0.5, difficulty=0.6,
        proposed_action=1
    )
    assert action == 0
    assert overridden is True
    assert gid == "g4_stuck_easier"


def test_guardrail_g1_overload_protection():
    """G1: Low performance on medium/high difficulty forces Easier (0)."""
    action, overridden, gid = apply_canonical_guardrails(
        perf=0.25, avg_perf=0.35, conf=0.4, hes=0.4, progress=0.5, difficulty=0.6,
        proposed_action=1
    )
    assert action == 0
    assert overridden is True
    assert gid == "g1_overload_protection"


def test_guardrail_g2_anxiety_stabilizer():
    """G2: Anxious candidate (low conf, high hes, passing perf) forces Same (1)."""
    action, overridden, gid = apply_canonical_guardrails(
        perf=0.70, avg_perf=0.70, conf=0.25, hes=0.75, progress=0.5, difficulty=0.6,
        proposed_action=2
    )
    assert action == 1
    assert overridden is True
    assert gid == "g2_anxiety_stabilizer_same"


def test_guardrail_g5_partial_understanding():
    """G5: Borderline performance with low average forces Same (1)."""
    action, overridden, gid = apply_canonical_guardrails(
        perf=0.50, avg_perf=0.55, conf=0.5, hes=0.3, progress=0.5, difficulty=0.6,
        proposed_action=2
    )
    assert action == 1
    assert overridden is True
    assert gid == "g5_partial_same"


def test_guardrail_g6_strong_performer():
    """G6: Dominant score exceeding difficulty gap forces Harder (2), except nervous_expert."""
    # Standard candidate (high confidence, low hesitation)
    action, overridden, gid = apply_canonical_guardrails(
        perf=0.95, avg_perf=0.90, conf=0.9, hes=0.1, progress=0.5, difficulty=0.4,
        proposed_action=1
    )
    assert action == 2
    assert overridden is True
    assert gid == "g6_strong_harder"

    # Nervous expert exemption (high performance, but low conf & high hes)
    action_ne, overridden_ne, gid_ne = apply_canonical_guardrails(
        perf=0.92, avg_perf=0.90, conf=0.35, hes=0.75, progress=0.5, difficulty=0.4,
        proposed_action=1
    )
    assert action_ne == 1
    assert overridden_ne is False
    assert gid_ne == "none"


# ==============================================================================
# Blocker 4: Checkpoint Isolation Assertion
# ==============================================================================

def test_checkpoint_isolation_assertions():
    """train_ppo_seed must enforce strict directory isolation between canonical and mismatch runs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        canonical_dir = Path(tmpdir) / "checkpoints"
        mismatch_dir = Path(tmpdir) / "checkpoints" / "historical_mismatch"

        # Attempting to save non-canonical mode into canonical directory must raise AssertionError
        with pytest.raises(AssertionError, match="Safety violation: Non-canonical mode"):
            train_ppo_seed(seed=99, dim4_mode="aligned_response_time", output_dir=canonical_dir)

        # Attempting to save canonical mode into mismatch directory must raise AssertionError
        with pytest.raises(AssertionError, match="Safety violation: Canonical mode"):
            train_ppo_seed(seed=99, dim4_mode="aligned_progress", output_dir=mismatch_dir)


# ==============================================================================
# Blocker 5: Training Convergence Instrumentation
# ==============================================================================

def test_training_convergence_callback():
    """TrainingConvergenceCallback must record step-level metrics and export valid CSV and JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir)
        cb = TrainingConvergenceCallback(log_path=log_path, log_freq=2)
        cb.num_timesteps = 2
        cb.locals = {
            "actions": np.array([0, 1]),
            "rewards": np.array([0.5, 0.8]),
            "dones": np.array([False, True]),
        }
        cb._on_step()
        cb._on_training_end()

        csv_file = log_path / "training_curves.csv"
        json_file = log_path / "training_curves.json"
        assert csv_file.exists() and csv_file.stat().st_size > 0
        assert json_file.exists() and json_file.stat().st_size > 0

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert "timestep" in rows[0]
            assert "mean_reward_rolling" in rows[0]
            assert "action_easier_pct" in rows[0]

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["timestep"] == 2
            assert data[0]["episode"] == 1
