from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
RL_ENV_DIR = ROOT / "rl" / "env"
if str(RL_ENV_DIR) not in sys.path:
    sys.path.insert(0, str(RL_ENV_DIR))

from interview_env import InterviewEnv


def test_interview_env_uses_three_actions_only():
    env = InterviewEnv(max_steps=1, guardrails_enabled=False, initial_difficulty=0.5)
    assert env.action_space.n == 3
    assert env.ACTION_NAMES == {0: "Easier", 1: "Same", 2: "Harder"}


def test_oracle_maps_to_three_actions_only():
    obs_easy = [0.2, 0.2, 0.3, 0.8, 0.2, 0.5]
    obs_same = [0.55, 0.45, 0.7, 0.2, 0.3, 0.5]
    obs_harder = [0.98, 0.7, 0.9, 0.1, 0.2, 0.6]

    assert InterviewEnv.oracle_action_from_obs(obs_easy) == 0
    assert InterviewEnv.oracle_action_from_obs(obs_same) == 1
    assert InterviewEnv.oracle_action_from_obs(obs_harder) == 2
