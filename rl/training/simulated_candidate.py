# rl/simulated_candidate.py
import numpy as np


class SimulatedCandidate:
    """
    Simple synthetic candidate model.
    - skill: float in [0,1]
    - persona: behavior mode controlling signal skew
    - answer_question(difficulty, hint_applied) -> dict with:
      performance_score, confidence_score, hesitation, response_time
    """

    VALID_PERSONAS = {
        "normal",
        "nervous_expert",
        "lucky_guesser",
        "overconfident_fail",
        "struggling_junior",
    }

    def __init__(self, skill: float = 0.6, seed: int = None, persona: str = "normal"):
        self.skill = float(np.clip(skill, 0.0, 1.0))
        self.rng = np.random.RandomState(seed)
        if persona not in self.VALID_PERSONAS:
            raise ValueError(f"Invalid persona '{persona}'. Expected one of {sorted(self.VALID_PERSONAS)}")
        self.persona = persona

    def _sigmoid_perf(self, skill, difficulty, slope=8.0, noise=0.05):
        x = (skill - difficulty) * slope
        p = 1.0 / (1.0 + np.exp(-x))
        p = np.clip(p + self.rng.normal(0, noise), 0.0, 1.0)
        return p

    def answer_question(self, difficulty: float, hint_applied: bool = False):
        """
        Returns a realistic tuple of signals.
        - performance_score: main objective (0..1)
        - confidence_score: correlated with perf but noisy
        - hesitation: inverse of confidence + noise
        - response_time: seconds (will be normalized by env)
        """
        # base performance (sigmoid)
        perf = self._sigmoid_perf(self.skill, difficulty, slope=8.0, noise=0.03)

        # hints help a bit
        if hint_applied:
            perf = np.clip(perf + 0.08, 0.0, 1.0)

        # confidence correlates with perf but skewed: experts may be hesitant sometimes
        conf = np.clip(perf - 0.15 + self.rng.normal(0.0, 0.07), 0.0, 1.0)

        # hesitation roughly inverse of confidence, but noisy and skill-dependent
        hes = np.clip(1.0 - conf + self.rng.normal(0.0, 0.08), 0.0, 1.0)

        # response_time increases with difficulty and hesitation
        base_time = 2.0 + 6.0 * difficulty
        response_time = max(0.2, base_time * (0.6 + 0.8 * hes) * (1.0 + self.rng.normal(0.0, 0.05)))

        # Persona adjustments are bounded and soft to keep trajectories realistic.
        if self.persona == "nervous_expert":
            # Clamp to oracle's Same-safeguard band [0.82, 0.94].
            # Without the upper cap, perf can exceed 0.95 → oracle picks Harder
            # (rock-star rule) → agent over-learns Harder for this persona.
            perf = np.clip(max(perf, 0.82) + self.rng.normal(0.0, 0.02), 0.82, 0.94)
            conf = np.clip(conf - 0.20 + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            hes = np.clip(max(hes, 0.75) + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            response_time *= 1.20

        elif self.persona == "lucky_guesser":
            perf = np.clip(max(perf, 0.95) + self.rng.normal(0.0, 0.015), 0.0, 1.0)
            conf = np.clip(min(conf, 0.30) + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            hes = np.clip(max(hes, 0.80) + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            response_time *= 1.15

        elif self.persona == "overconfident_fail":
            perf = np.clip(min(perf, 0.20) + self.rng.normal(0.0, 0.02), 0.0, 1.0)
            conf = np.clip(max(conf, 0.85) + self.rng.normal(0.0, 0.02), 0.0, 1.0)
            hes = np.clip(min(hes, 0.25) + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            response_time *= 0.90

        elif self.persona == "struggling_junior":
            perf = np.clip(min(perf, 0.30) + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            conf = np.clip(min(conf, 0.30) + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            # Randomize hesitation floor in [0.30, 0.90] so both stuck
            # (hes > 0.60 → oracle=Hint) and weak-but-not-stuck
            # (hes ≤ 0.60 → oracle=Easier) states appear during training.
            hes_floor = self.rng.uniform(0.30, 0.90)
            hes = np.clip(max(hes, hes_floor) + self.rng.normal(0.0, 0.03), 0.0, 1.0)
            response_time *= 1.25

        response_time = max(0.2, float(response_time))

        return {
            "performance_score": float(perf),
            "confidence_score": float(conf),
            "hesitation": float(hes),
            "response_time": float(response_time)
        }