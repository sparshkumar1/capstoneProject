"""
Correctness tests for the E1 persona-diversity implementation
(E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V4.md). All tests here are deterministic
unit/static checks: no PPO training, no PPO checkpoint loading, no
confirmatory-scale replay. They exercise only:
  - the DiverseCandidate wrapper (pure function of its inputs, given a seed),
  - the B0/B2 grid and episode-seed helpers,
  - the new DiversePersonaAlignedEnv's reset()/step() via a handful of manual
    calls (no PPO involved -- actions are supplied directly),
  - the e1_simulate_adapter parity against x3a_lib.simulate() using only
    x3a_lib's non-PPO deterministic policies (const_same, heuristic, oracle,
    random) -- never a PPO checkpoint.

Run with: .venv/Scripts/python.exe -m pytest research/paper_strengthening/scripts/tests/test_e1_diverse_persona.py -v
"""
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = REPO / "research" / "paper_strengthening" / "scripts"
X3A_DIR = REPO / "research" / "confirmatory" / "X3-A"
for p in (REPO, SCRIPTS_DIR, X3A_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from rl.training.simulated_candidate import SimulatedCandidate  # noqa: E402
from e1_diverse_persona_env import (  # noqa: E402
    DiverseCandidate, SKILL_GRID, K_GRID, ARM_GRIDS,
    grid_cell_for_episode, episode_seed, make_candidate,
    HOLDOUT_PROFILES, x3a_target_difficulty,
)
from e1_simulate_adapter import (  # noqa: E402
    simulate_diverse, ordinary_candidate_factory, diverse_candidate_factory,
)
import x3a_lib  # noqa: E402  (frozen library, imported only)


# ---------------------------------------------------------------------------
# 1. Exact identity of the wrapper at k=0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill,seed,diff", [(0.2, 1, 0.3), (0.6, 42, 0.5), (0.9, 999, 0.8)])
def test_wrapper_k0_is_exact_identity(skill, seed, diff):
    wrapped = DiverseCandidate(skill=skill, seed=seed, k=0.0)
    plain = SimulatedCandidate(skill=skill, seed=seed, persona="normal")
    out_w = wrapped.answer_question(diff)
    out_p = plain.answer_question(diff)
    assert out_w == out_p, "k=0 must reproduce the unwrapped SimulatedCandidate output exactly"


def test_wrapper_k0_returns_inner_dict_unmodified_object():
    # k=0 short-circuits to `return out` (the inner dict itself), not a rebuilt copy.
    wrapped = DiverseCandidate(skill=0.5, seed=7, k=0.0)
    out = wrapped.answer_question(0.4)
    assert set(out.keys()) == {"performance_score", "confidence_score", "hesitation", "response_time"}


# ---------------------------------------------------------------------------
# 2. Correct, bounded confidence/hesitation transform for k > 0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("k", [0.0, 0.30, 0.45, 0.60, 1.0])
@pytest.mark.parametrize("skill", [0.2, 0.5, 0.9])
def test_transform_matches_formula_and_stays_bounded(skill, k):
    seed = 123
    wrapped = DiverseCandidate(skill=skill, seed=seed, k=k)
    plain = SimulatedCandidate(skill=skill, seed=seed, persona="normal")
    for diff in (0.2, 0.5, 0.8):
        out_w = wrapped.answer_question(diff)
        out_p = plain.answer_question(diff)
        expected_conf = min(1.0, max(0.0, out_p["confidence_score"] - k))
        expected_hes = min(1.0, max(0.0, out_p["hesitation"] + k))
        assert out_w["confidence_score"] == pytest.approx(expected_conf, abs=1e-12)
        assert out_w["hesitation"] == pytest.approx(expected_hes, abs=1e-12)
        assert 0.0 <= out_w["confidence_score"] <= 1.0
        assert 0.0 <= out_w["hesitation"] <= 1.0


def test_k_out_of_range_rejected():
    with pytest.raises(ValueError):
        DiverseCandidate(skill=0.5, seed=1, k=1.5)
    with pytest.raises(ValueError):
        DiverseCandidate(skill=0.5, seed=1, k=-0.1)


# ---------------------------------------------------------------------------
# 3. Performance and response_time unchanged by the transform
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("k", [0.0, 0.30, 0.60])
def test_perf_and_response_time_unchanged(k):
    seed, skill, diff = 55, 0.7, 0.4
    wrapped = DiverseCandidate(skill=skill, seed=seed, k=k)
    plain = SimulatedCandidate(skill=skill, seed=seed, persona="normal")
    out_w = wrapped.answer_question(diff)
    out_p = plain.answer_question(diff)
    assert out_w["performance_score"] == out_p["performance_score"]
    assert out_w["response_time"] == out_p["response_time"]


# ---------------------------------------------------------------------------
# 4. Deterministic episode-seed formula and grid cycling
# ---------------------------------------------------------------------------

def test_episode_seed_formula_exact():
    assert episode_seed(42, 0) == 42 * 100_000 + 0
    assert episode_seed(999, 1637) == 999 * 100_000 + 1637
    assert episode_seed(42, 0) == episode_seed(42, 0)  # deterministic, no hidden state


def test_grid_cycling_deterministic_and_wraps():
    for arm in ("B0", "B2"):
        seq1 = [grid_cell_for_episode(arm, i) for i in range(48)]
        seq2 = [grid_cell_for_episode(arm, i) for i in range(48)]
        assert seq1 == seq2, "grid cycling must be a pure function, no hidden mutation"
        assert seq1[0] == seq1[24], "grid must wrap exactly every 24 episodes"
        assert seq1[5] == seq1[29]


def test_grid_cycling_unknown_arm_raises():
    with pytest.raises(ValueError):
        grid_cell_for_episode("B1", 0)


# ---------------------------------------------------------------------------
# 5. B0 vs B2: matching base candidate seeds and skill exposure
# ---------------------------------------------------------------------------

def test_b0_b2_identical_skill_sequence_and_seed_at_every_episode():
    for t in (42, 123, 999):
        for i in range(48):  # two full cycles
            c0 = make_candidate("B0", t, i)
            c2 = make_candidate("B2", t, i)
            assert c0.seed == c2.seed, f"seed mismatch at t={t}, i={i}"
            assert c0.skill == c2.skill, f"skill mismatch at t={t}, i={i}"
            assert c0.k == 0.0
            # B2's k varies; only assert it's from the declared grid
            assert c2.k in K_GRID


def test_b0_skill_exposure_matches_b2_exactly():
    for t in (42,):
        skills_b0 = [make_candidate("B0", t, i).skill for i in range(24)]
        skills_b2 = [make_candidate("B2", t, i).skill for i in range(24)]
        assert skills_b0 == skills_b2
        # each of the 6 skill values appears exactly 4 times in one full cycle
        for s in SKILL_GRID:
            assert skills_b0.count(s) == 4
            assert skills_b2.count(s) == 4


def test_b0_k_always_zero_across_full_cycle():
    ks = [make_candidate("B0", 42, i).k for i in range(24)]
    assert ks == [0.0] * 24


def test_b2_k_grid_exposure_matches_declared_grid():
    ks = [make_candidate("B2", 42, i).k for i in range(24)]
    for k in K_GRID:
        assert ks.count(k) == 6  # 6 skill values x this k value


# ---------------------------------------------------------------------------
# 6. Environment reset/termination -- no PPO, manual actions only
# ---------------------------------------------------------------------------

def test_env_reset_assigns_correct_candidate_and_terminates(tmp_path):
    # IMPORTANT: InterviewEnv defaults log_file to rl/env/training_logs/interview_data.csv
    # (an existing, untracked, gitignored log documented in PPO_TRAINING_EXPERIENCE_AUDIT.md).
    # Every env instantiated in these tests must pass an isolated tmp_path log_file so
    # test runs never append to, and thereby alter, that existing file.
    from e1_train_condition_b import build_env_class
    EnvClass = build_env_class()
    env = EnvClass(arm="B2", training_seed=42, dim4_mode="aligned_progress",
                    log_file=str(tmp_path / "test_env_log.csv"))

    obs0, _ = env.reset()
    assert env._episode_index == 1
    expected_skill, expected_k = grid_cell_for_episode("B2", 0)
    assert env.sim_candidate.skill == expected_skill
    assert env.sim_candidate.k == expected_k
    assert env.sim_candidate.seed == episode_seed(42, 0)

    terminated = False
    steps = 0
    while not terminated and steps < 100:
        obs, reward, terminated, truncated, info = env.step(1)  # always "Same"
        steps += 1
    assert terminated, "episode must terminate within max_steps"
    assert steps == env.max_steps

    obs1, _ = env.reset()
    assert env._episode_index == 2
    expected_skill2, expected_k2 = grid_cell_for_episode("B2", 1)
    assert env.sim_candidate.skill == expected_skill2
    assert env.sim_candidate.k == expected_k2
    assert env.sim_candidate.seed == episode_seed(42, 1)


def test_env_b0_never_exposes_nonzero_k(tmp_path):
    from e1_train_condition_b import build_env_class
    EnvClass = build_env_class()
    env = EnvClass(arm="B0", training_seed=999, dim4_mode="aligned_progress",
                    log_file=str(tmp_path / "test_env_log_b0.csv"))
    for _ in range(5):
        env.reset()
        assert env.sim_candidate.k == 0.0
        for _ in range(env.max_steps):
            _, _, terminated, _, _ = env.step(1)
            if terminated:
                break


# ---------------------------------------------------------------------------
# 7/8. Metric calculations and action handling: parity with x3a_lib.simulate()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("policy_kind", ["const_same", "heuristic", "oracle", "random"])
@pytest.mark.parametrize("ptype,skill,eval_seed,target,shield_on", [
    ("normal", 0.60, 1001, 3.0, True),
    ("normal", 0.60, 2002, 3.0, False),
    ("struggling_junior", 0.20, 1001, 1.0, True),
    ("lucky_guesser", 0.80, 3003, 4.0, True),
])
def test_adapter_parity_with_x3a_lib_simulate_ordinary_candidates(policy_kind, ptype, skill, eval_seed, target, shield_on):
    policy_fn = x3a_lib.make_policy(policy_kind, persona_index=0, eval_seed=eval_seed)
    ref = x3a_lib.simulate(policy_fn, ptype, skill, target, eval_seed, shield_on)

    # re-create an identically-seeded policy_fn for the adapter call, since
    # "random"'s policy_fn is stateful (an RNG) and must not be reused across
    # two independent simulate() calls sharing the same eval_seed.
    policy_fn2 = x3a_lib.make_policy(policy_kind, persona_index=0, eval_seed=eval_seed)
    cand_factory = ordinary_candidate_factory(ptype, skill)
    got = simulate_diverse(policy_fn2, cand_factory, target, eval_seed, shield_on)

    for key in ("final_difficulty", "target_tracking_error", "volatility", "oscillation_rate",
                "guardrail_interventions", "constraint_violations", "raw_actions", "final_actions",
                "guardrail_ids", "overrides", "oracle_agreement"):
        assert got[key] == ref[key], f"mismatch in {key}: adapter={got[key]!r} vs x3a_lib.simulate={ref[key]!r}"
    for step in ref["obs_log"]:
        assert np.array_equal(got["obs_log"][step], ref["obs_log"][step]), f"obs mismatch at step {step}"


def test_adapter_diverse_candidate_k0_matches_ordinary_candidate():
    """A DiverseCandidate with k=0 run through the adapter must match
    x3a_lib.simulate() on an ordinary (unwrapped) 'normal' candidate exactly,
    since persona='normal' + k=0 is by construction an identity transform."""
    ptype, skill, eval_seed, target = "normal", 0.60, 4004, 3.0
    policy_fn = x3a_lib.make_policy("heuristic", eval_seed=eval_seed)
    ref = x3a_lib.simulate(policy_fn, ptype, skill, target, eval_seed, True)

    policy_fn2 = x3a_lib.make_policy("heuristic", eval_seed=eval_seed)
    got = simulate_diverse(policy_fn2, diverse_candidate_factory(skill=skill, k=0.0), target, eval_seed, True)

    assert got["target_tracking_error"] == ref["target_tracking_error"]
    assert got["final_actions"] == ref["final_actions"]
    assert got["oracle_agreement"] == ref["oracle_agreement"]


def test_adapter_diverse_candidate_k_positive_changes_something_or_stays_valid():
    """Sanity check only (not a parity check, k>0 is expected to differ from
    the unwrapped candidate): the adapter must still return a well-formed,
    internally consistent result for k>0 (bounded MAE, valid action names)."""
    got = simulate_diverse(
        x3a_lib.make_policy("heuristic", eval_seed=5005),
        diverse_candidate_factory(skill=0.80, k=0.60),
        target=4.0, eval_seed=5005, shield_on=True,
    )
    assert 0.0 <= got["target_tracking_error"] <= 4.0
    assert all(a in ("Easier", "Same", "Harder") for a in got["final_actions"])
    assert 0.0 <= got["oracle_agreement"] <= 1.0


# ---------------------------------------------------------------------------
# 9. Held-out profiles: formula agreement and no grid collisions
# ---------------------------------------------------------------------------

def test_holdout_profile_targets_match_x3a_formula():
    for p in HOLDOUT_PROFILES:
        assert p["target"] == x3a_target_difficulty(p["skill"])
    assert HOLDOUT_PROFILES[0]["target"] == 1.5
    assert HOLDOUT_PROFILES[1]["target"] == 3.0
    assert HOLDOUT_PROFILES[2]["target"] == 4.0


def test_holdout_profile_skills_do_not_collide_with_any_existing_grid():
    persona_targets_skills = {0.20, 0.30, 0.60, 0.80, 0.88}
    x3a_grid_skills = set(x3a_lib.SKILLS)
    b0_b2_skills = set(SKILL_GRID)
    all_existing = persona_targets_skills | x3a_grid_skills | b0_b2_skills
    for p in HOLDOUT_PROFILES:
        assert all(abs(p["skill"] - e) > 1e-9 for e in all_existing), (
            f"{p['profile_id']} skill {p['skill']} collides with an existing grid skill"
        )
