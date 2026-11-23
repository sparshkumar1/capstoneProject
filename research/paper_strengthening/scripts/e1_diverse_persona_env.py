"""
E1 -- PPO persona-diversity development experiment (protocol V4).

Defines the confidence/hesitation decoupling wrapper candidate, the B0/B2
training grids, the episode-seed formula, and the held-out confirmatory
profiles, exactly as specified in
research/paper_strengthening/E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V4.md
(sections 1.1, 1.2, 2.4).

This module imports rl/training/simulated_candidate.py's SimulatedCandidate
UNMODIFIED and composes a new wrapper around it. It does not subclass or
alter SimulatedCandidate, InterviewEnv, or any other frozen file.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from rl.training.simulated_candidate import SimulatedCandidate  # noqa: E402  (frozen; imported only)


class DiverseCandidate:
    """
    Compositional wrapper (holds, does not subclass, a SimulatedCandidate)
    that applies a disclosed, bounded, single-parameter confidence/hesitation
    decoupling offset to the values SimulatedCandidate.answer_question()
    returns:

        confidence' = clip(confidence - k, 0, 1)
        hesitation' = clip(hesitation + k, 0, 1)

    performance_score and response_time are passed through unchanged -- the
    offset never touches the candidate's underlying performance level, only
    the confidence/hesitation channel, per protocol V4 section 1.1/2.2.

    At k=0.0 this is an exact identity transform: the inner dict is returned
    unmodified (same object), not merely numerically equal, so B0 (k always
    0) behaves exactly as an unwrapped, unmodified SimulatedCandidate would.
    """

    def __init__(self, skill: float, seed: int, k: float = 0.0):
        if not (0.0 <= k <= 1.0):
            raise ValueError(f"k must be in [0.0, 1.0], got {k!r}")
        self.skill = float(skill)
        self.seed = int(seed)
        self.k = float(k)
        self.persona = "normal"
        self._inner = SimulatedCandidate(skill=skill, seed=seed, persona="normal")

    def answer_question(self, difficulty: float, hint_applied: bool = False):
        out = self._inner.answer_question(difficulty, hint_applied=hint_applied)
        if self.k == 0.0:
            return out
        conf = out["confidence_score"]
        hes = out["hesitation"]
        conf_p = min(1.0, max(0.0, conf - self.k))
        hes_p = min(1.0, max(0.0, hes + self.k))
        return {
            "performance_score": out["performance_score"],
            "confidence_score": float(conf_p),
            "hesitation": float(hes_p),
            "response_time": out["response_time"],
        }


# ---------------------------------------------------------------------------
# Grid definitions -- protocol V4 section 1.1
# ---------------------------------------------------------------------------

SKILL_GRID = (0.20, 0.35, 0.50, 0.65, 0.80, 0.90)
K_GRID = (0.0, 0.30, 0.45, 0.60)

# Both arms cycle through the identical 24-cell (skill, "slot") structure;
# B0 pins k=0 for every slot, B2 uses the real k grid. This guarantees
# identical skill-value exposure counts and identical grid-visitation order
# between the two arms -- the only difference is the k value at each cell.
ARM_GRIDS = {
    "B0": tuple((s, 0.0) for s in SKILL_GRID for _ in K_GRID),
    "B2": tuple((s, k) for s in SKILL_GRID for k in K_GRID),
}
assert len(ARM_GRIDS["B0"]) == len(ARM_GRIDS["B2"]) == 24
assert [c[0] for c in ARM_GRIDS["B0"]] == [c[0] for c in ARM_GRIDS["B2"]], (
    "B0 and B2 must visit the identical skill-value sequence, differing only in k"
)


def grid_cell_for_episode(arm: str, episode_index: int):
    """Deterministic cycling rule: grid[episode_index % 24]. Identical cycling
    rule and order for both arms (protocol V4 section 1.1)."""
    if arm not in ARM_GRIDS:
        raise ValueError(f"Unknown arm {arm!r}; expected one of {sorted(ARM_GRIDS)}")
    grid = ARM_GRIDS[arm]
    return grid[episode_index % len(grid)]


def episode_seed(training_seed: int, episode_index: int) -> int:
    """Protocol V4 section 1.2's exact formula. Deliberately independent of
    arm and of grid cell, so corresponding B0/B2 episodes at the same
    (training_seed, episode_index) share the same underlying SimulatedCandidate
    noise draw before the k-transform is applied -- a true paired design."""
    return int(training_seed) * 100_000 + int(episode_index)


def make_candidate(arm: str, training_seed: int, episode_index: int) -> DiverseCandidate:
    """Builds the DiverseCandidate for one training episode, per protocol V4."""
    skill, k = grid_cell_for_episode(arm, episode_index)
    seed = episode_seed(training_seed, episode_index)
    return DiverseCandidate(skill=skill, seed=seed, k=k)


# ---------------------------------------------------------------------------
# Held-out confirmatory profiles -- protocol V4 section 2.4
# ---------------------------------------------------------------------------

def x3a_target_difficulty(skill: float) -> float:
    """Verbatim formula from research/confirmatory/X3-A/x3a_lib.py::persona_grid()
    ("target = round(10*skill)/2", read directly from that frozen file).
    Reproduced here, not imported, because x3a_lib.py's own target computation
    is inlined in a list comprehension rather than exposed as a standalone
    function; the formula is copied verbatim and is not an independent
    approximation (see the docstring of persona_grid() for the source)."""
    return round(10 * skill) / 2.0


HOLDOUT_PROFILES = (
    {"profile_id": "HOLDOUT-1", "skill": 0.27, "k": 0.20, "target": x3a_target_difficulty(0.27)},
    {"profile_id": "HOLDOUT-2", "skill": 0.58, "k": 0.38, "target": x3a_target_difficulty(0.58)},
    {"profile_id": "HOLDOUT-3", "skill": 0.83, "k": 0.52, "target": x3a_target_difficulty(0.83)},
)

_EXISTING_SKILLS = {
    0.20, 0.30, 0.60, 0.80, 0.88,                      # PERSONA_TARGETS (execute_paper3_study.py)
    0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90,    # X3-A's 8-point grid (x3a_lib.py SKILLS)
    0.20, 0.35, 0.50, 0.65, 0.80, 0.90,                # B0/B2's own grid (SKILL_GRID above)
}
for _p in HOLDOUT_PROFILES:
    if any(abs(_p["skill"] - e) < 1e-9 for e in _EXISTING_SKILLS):
        raise AssertionError(f"{_p['profile_id']} skill {_p['skill']} collides with an existing grid skill")
