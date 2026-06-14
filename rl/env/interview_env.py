"""
interview_env.py — Merged environment
6D state + 3 actions (Easier / Same / Harder) + oracle-guided hybrid reward.

State (6D):
  [0] performance      - last answer score 0..1
  [1] avg_performance  - rolling mean of last 5 scores
  [2] confidence       - from SimulatedCandidate
  [3] hesitation       - from SimulatedCandidate
  [4] time_norm        - normalised response time
  [5] difficulty       - current difficulty 0.0..1.0

Actions (3):
  0 = Easier
  1 = Same
  2 = Harder

Reward modes:
  oracle  : purely oracle-match signal
  outcome : purely performance-delta signal
  hybrid  : weighted combination (default, recommended)
"""

import csv
import os
import warnings
from pathlib import Path

import gymnasium as gym
from gymnasium import spaces
import numpy as np

try:
    from simulated_candidate import SimulatedCandidate
except ImportError:  # fallback when imported from the repo root
    from rl.training.simulated_candidate import SimulatedCandidate


BASE_DIR = Path(__file__).resolve().parent


class InterviewEnv(gym.Env):

    metadata = {"render_modes": ["human"]}

    ACTION_NAMES = {
        0: "Easier",
        1: "Same",
        2: "Harder",
    }

    def __init__(
        self,
        simulated_candidate=None,
        max_steps=15,
        strict_logging=False,
        initial_difficulty=None,
        reward_mode="hybrid",
        log_file=str(BASE_DIR / "training_logs" / "interview_data.csv"),
        # oracle-mode scale
        oracle_scale=0.7,
        # hybrid weights (auto-normalised)
        hybrid_decision_weight=0.60,
        hybrid_outcome_weight=0.30,
        hybrid_shaping_weight=0.10,
        # critical-state bonuses
        critical_mismatch_penalty=-1.0,
        critical_match_bonus=0.2,
        # outcome-component params
        outcome_delta_clip=0.2,
        outcome_tanh_gain=5.0,
        # shaping params
        repeat_easier_penalty=-0.1,
        conf_weight_low_perf=0.4,
        conf_weight_high_perf=0.4,
        conf_perf_threshold=0.4,
        hesitation_weight=0.3,
        time_weight=0.2,
        delta_transform_gain=0.0,
        # persona bias corrections
        persona_bonus_nervous=0.0,
        persona_bonus_lucky=0.0,
        persona_bonus_overconfident=0.0,
        persona_bonus_junior=0.0,
        # guardrails
        guardrails_enabled=True,
        medium_difficulty_min=0.4,
        medium_difficulty_max=0.7,
        oscillation_penalty=-0.10,
        followup_overuse_limit=2,
    ):
        super().__init__()

        self.max_steps = max_steps
        self.current_step = 0
        self.strict_logging = strict_logging
        self.reward_mode = str(reward_mode).lower().strip()
        self._eval_initial_difficulty = initial_difficulty

        valid_reward_modes = {"oracle", "outcome", "hybrid"}
        if self.reward_mode not in valid_reward_modes:
            raise ValueError(
                f"Invalid reward_mode '{self.reward_mode}'. "
                f"Expected one of {sorted(valid_reward_modes)}"
            )

        self.oracle_scale = float(oracle_scale)
        self.hybrid_decision_weight = float(hybrid_decision_weight)
        self.hybrid_outcome_weight = float(hybrid_outcome_weight)
        self.hybrid_shaping_weight = float(hybrid_shaping_weight)
        self.critical_mismatch_penalty = float(critical_mismatch_penalty)
        self.critical_match_bonus = float(critical_match_bonus)
        self.outcome_delta_clip = float(outcome_delta_clip)
        self.outcome_tanh_gain = float(outcome_tanh_gain)
        self.repeat_easier_penalty = float(repeat_easier_penalty)
        self.conf_weight_low_perf = float(conf_weight_low_perf)
        self.conf_weight_high_perf = float(conf_weight_high_perf)
        self.conf_perf_threshold = float(conf_perf_threshold)
        self.hesitation_weight = float(hesitation_weight)
        self.time_weight = float(time_weight)
        self.delta_transform_gain = float(delta_transform_gain)
        self.persona_bonus_nervous = float(persona_bonus_nervous)
        self.persona_bonus_lucky = float(persona_bonus_lucky)
        self.persona_bonus_overconfident = float(persona_bonus_overconfident)
        self.persona_bonus_junior = float(persona_bonus_junior)
        self.guardrails_enabled = bool(guardrails_enabled)
        self.medium_difficulty_min = float(medium_difficulty_min)
        self.medium_difficulty_max = float(medium_difficulty_max)
        self.oscillation_penalty = float(oscillation_penalty)
        self.followup_overuse_limit = int(followup_overuse_limit)

        # Validation
        if self.outcome_delta_clip <= 0.0:
            raise ValueError("outcome_delta_clip must be > 0")
        if self.outcome_tanh_gain <= 0.0:
            raise ValueError("outcome_tanh_gain must be > 0")
        if not (0.0 <= self.medium_difficulty_min <= self.medium_difficulty_max <= 1.0):
            raise ValueError("medium_difficulty bounds invalid")

        # Normalise hybrid weights
        hw = (self.hybrid_decision_weight
              + self.hybrid_outcome_weight
              + self.hybrid_shaping_weight)
        if hw <= 0.0:
            raise ValueError("Hybrid weights must sum to a positive value")
        self.hybrid_decision_weight /= hw
        self.hybrid_outcome_weight  /= hw
        self.hybrid_shaping_weight  /= hw

        # 6D observation space
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(6,), dtype=np.float32
        )
        # 3 actions: Easier / Same / Harder
        self.action_space = spaces.Discrete(3)

        self.sim_candidate = simulated_candidate or SimulatedCandidate()
        self.difficulty = 0.5
        self.scores = []
        self.last_obs = None
        self.prev_action = None

        # CSV logging setup
        self.log_file = str(log_file)
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                csv.writer(f).writerow([
                    "step", "skill", "persona", "difficulty",
                    "performance", "avg_perf", "confidence", "hesitation",
                    "time_norm", "pre_action", "action", "oracle_action",
                    "oracle_match", "forced_action", "guardrail_id",
                    "decision_component", "outcome_component",
                    "shaping_component", "stability_penalty",
                    "critical_consistency", "persona_bias", "reward",
                ])

    # ─────────────────────────────────────────────────────────────────
    # Oracle
    # ─────────────────────────────────────────────────────────────────

    @staticmethod
    def oracle_action_from_obs(obs):
        """
        Expert oracle — 6D state, 3 actions.

        obs: [perf, avg_perf, conf, hes, time_norm, difficulty]

        Rule priority (earlier rules take precedence):
          R1: perf < 0.30 and hes > 0.60              -> Easier      (stuck)
          R2: perf < 0.35                              -> Easier      (weak)
          R3: 0.80 < perf < 0.95 and hes > 0.65       -> Same        (nervous expert)
          R4: perf >= 0.95 and gap > 0.20              -> Harder      (rock star)
          R5: 0.40 < perf < 0.65 and avg_perf < 0.60  -> Same        (partial understanding)
          R6: gap > 0.25                               -> Harder      (strong gap)
          R7: else                                     -> Same        (default)
        """
        perf, avg_perf, conf, hes, time_norm, difficulty = [float(x) for x in obs]
        gap = perf - difficulty

        if perf < 0.30 and hes > 0.60:            # R1
            return 0  # Easier
        if perf < 0.35:                             # R2
            return 0  # Easier
        if 0.80 < perf < 0.95 and hes > 0.65:     # R3
            return 1  # Same (nervous expert)
        if perf >= 0.95 and gap > 0.20:            # R4
            return 2  # Harder (rock star)
        if 0.40 < perf < 0.65 and avg_perf < 0.60: # R5
            return 1  # Same (partial understanding)
        if gap > 0.25:                              # R6
            return 2  # Harder
        return 1                                    # R7 Same

    # ─────────────────────────────────────────────────────────────────
    # Guardrails
    # ─────────────────────────────────────────────────────────────────

    def _apply_guardrails(self, pre_obs, proposed_action):
        if not self.guardrails_enabled:
            return int(proposed_action), False, "none"

        perf, avg_perf, conf, hes, time_norm, difficulty = [float(x) for x in pre_obs]
        action = int(proposed_action)

        # G4: Stuck candidate — HIGHEST PRIORITY (before G1)
        # perf<0.30 AND hes>0.60: needs Easier, not a harder follow-up.
        # Must come before G1 which would fire first on the same low-perf state.
        if perf < 0.30 and hes > 0.60:
            return 0, True, "g4_stuck_easier"

        # G1: overload — weak candidate at medium difficulty (not stuck)
        if (perf < 0.30
                and self.medium_difficulty_min <= difficulty <= self.medium_difficulty_max):
            return 0, True, "g1_overload_protection"

        # G2: anxiety stabiliser — low confidence + high hesitation + NOT high performer
        # High performers (perf >= 0.80) with anxiety still need Harder, not stabilisation.
        # Lucky Guesser persona has high perf but low conf — should get Harder.
        if conf < 0.30 and hes > 0.70 and perf < 0.80:
            return 1, True, "g2_anxiety_stabilizer_same"

        # G5: Partial understanding — stay at Same
        # The partial-understanding zone (0.40<perf<0.65, avg<0.60) sits adjacent to Easier,
        # causing PPO to produce unstable boundaries across seeds.
        # Guardrail keeps the policy stable while remaining in the 3-action space.
        if (0.40 < perf < 0.65
                and avg_perf < 0.60
                ):
            return 1, True, "g5_partial_same"

        # G6: Strong candidate with big gap -> always Harder
        # Handles Rock Star and Lucky Guesser personas.
        # Excludes nervous expert state (0.80<perf<0.95 AND hes>0.65)
        # because nervous experts need stabilisation, not more difficulty.
        gap = perf - difficulty
        nervous_expert_state = 0.80 < perf < 0.95 and hes > 0.65
        if perf >= 0.90 and gap > 0.25 and not nervous_expert_state:
            return 2, True, "g6_strong_harder"

        return action, False, "none"

    @staticmethod
    def _is_zigzag_transition(prev_action, current_action):
        return bool(
            (prev_action == 0 and current_action == 2)
            or (prev_action == 2 and current_action == 0)
        )

    def _persona_bias_correction(self):
        persona = getattr(self.sim_candidate, "persona", "normal")
        if persona == "nervous_expert":     return self.persona_bonus_nervous
        if persona == "lucky_guesser":      return self.persona_bonus_lucky
        if persona == "overconfident_fail": return self.persona_bonus_overconfident
        if persona == "struggling_junior":  return self.persona_bonus_junior
        return 0.0

    def _normalize_time(self, response_time, difficulty):
        ideal_time = 3.0 + 6.0 * difficulty
        return float(np.clip(response_time / (ideal_time * 2.0), 0.0, 1.0))

    # ─────────────────────────────────────────────────────────────────
    # Gym interface
    # ─────────────────────────────────────────────────────────────────

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.scores = []
        self.prev_action = None

        if self._eval_initial_difficulty is not None:
            self.difficulty = float(self._eval_initial_difficulty)
        else:
            self.difficulty = float(self.np_random.uniform(0.3, 0.7))

        # [perf, avg_perf, conf, hes, time_norm, difficulty]
        obs = np.array([0.0, 0.0, 0.5, 0.2, 0.0, self.difficulty], dtype=np.float32)
        self.last_obs = obs.copy()
        return obs, {}

    def step(self, action):
        self.current_step += 1
        pre_action = int(action)
        prev_obs = self.last_obs.copy()

        # Oracle uses pre-action state
        oracle_action = self.oracle_action_from_obs(prev_obs)

        # Guardrails may redirect action
        action, forced_action, guardrail_id = self._apply_guardrails(prev_obs, pre_action)
        hint_applied = False
        current_difficulty = self.difficulty

        # Candidate answers
        out = self.sim_candidate.answer_question(
            current_difficulty, hint_applied=hint_applied
        )
        perf   = float(out["performance_score"])
        conf   = float(out["confidence_score"])
        hes    = float(out["hesitation"])
        t_norm = self._normalize_time(out["response_time"], current_difficulty)

        # Rolling average
        self.scores.append(perf)
        avg_perf = float(np.mean(self.scores[-5:]))
        gap = perf - current_difficulty

        # ── Reward components ─────────────────────────────────────
        decision_component = 1.0 if action == oracle_action else -1.0

        prev_perf = float(prev_obs[0])
        raw_delta_p = perf - prev_perf
        if self.delta_transform_gain > 0.0:
            delta_source = float(np.tanh(self.delta_transform_gain * raw_delta_p))
        else:
            delta_source = float(raw_delta_p)
        delta_p = float(np.clip(delta_source,
                                -self.outcome_delta_clip,
                                self.outcome_delta_clip))
        outcome_component = float(np.tanh(self.outcome_tanh_gain * delta_p))

        conf_weight = (self.conf_weight_low_perf
                       if perf < self.conf_perf_threshold
                       else self.conf_weight_high_perf)
        shaping_component = (
            conf_weight * conf
            - self.hesitation_weight * hes
            - self.time_weight * t_norm
        )

        repeat_easier = (self.repeat_easier_penalty
                         if (self.prev_action == 0 and action == 0) else 0.0)
        zigzag = (self.oscillation_penalty
                  if self._is_zigzag_transition(self.prev_action, action) else 0.0)
        stability_penalty = repeat_easier + zigzag

        persona_bias = self._persona_bias_correction()

        # Critical states — covers the 3 canonical difficulty shifts
        critical_state = (
            (perf < 0.30 and hes > 0.60)                    # stuck -> Easier
            or (perf < 0.35)                                  # weak -> Easier
            or (0.80 < perf < 0.95 and hes > 0.65)           # nervous expert -> Same
            or (perf >= 0.95 and gap > 0.20)                  # rock star -> Harder
            or (0.40 < perf < 0.65 and avg_perf < 0.60)      # partial -> Same
        )
        if critical_state and action != oracle_action:
            critical_consistency = self.critical_mismatch_penalty
        elif critical_state and action == oracle_action:
            critical_consistency = self.critical_match_bonus
        else:
            critical_consistency = 0.0

        if self.reward_mode == "oracle":
            reward = self.oracle_scale * decision_component
        elif self.reward_mode == "outcome":
            reward = outcome_component
        else:  # hybrid
            reward = (
                self.hybrid_decision_weight * decision_component
                + self.hybrid_outcome_weight * outcome_component
                + self.hybrid_shaping_weight * shaping_component
                + stability_penalty
                + critical_consistency
                + persona_bias
            )

        # ── Apply difficulty change AFTER reward ──────────────────
        if action == 0:   # Easier
            self.difficulty = max(0.1, self.difficulty - 0.1)
        elif action == 2: # Harder
            self.difficulty = min(1.0, self.difficulty + 0.1)
        # Same does not change difficulty

        obs = np.array(
            [perf, avg_perf, conf, hes, t_norm, self.difficulty],
            dtype=np.float32,
        )
        self.prev_action = action
        self.last_obs = obs.copy()

        # ── CSV logging ───────────────────────────────────────────
        try:
            with open(self.log_file, "a", newline="") as f:
                csv.writer(f).writerow([
                    self.current_step,
                    getattr(self.sim_candidate, "skill", None),
                    getattr(self.sim_candidate, "persona", "normal"),
                    current_difficulty, perf, avg_perf, conf, hes, t_norm,
                    pre_action, action, oracle_action,
                    int(action == oracle_action),
                    int(forced_action), guardrail_id,
                    decision_component, outcome_component,
                    shaping_component, stability_penalty,
                    critical_consistency, persona_bias, reward,
                ])
        except Exception as exc:
            msg = f"Failed to write log row: {exc}"
            if self.strict_logging:
                raise RuntimeError(msg) from exc
            warnings.warn(msg)

        terminated = self.current_step >= self.max_steps

        info = {
            "difficulty":           self.difficulty,
            "avg_perf":             avg_perf,
            "persona":              getattr(self.sim_candidate, "persona", "normal"),
            "pre_action":           int(pre_action),
            "final_action":         int(action),
            "final_action_name":    self.ACTION_NAMES.get(action, str(action)),
            "forced_action":        bool(forced_action),
            "guardrail_id":         guardrail_id,
            "oracle_action":        oracle_action,
            "oracle_action_name":   self.ACTION_NAMES[oracle_action],
            "oracle_match":         bool(action == oracle_action),
            "decision_component":   float(decision_component),
            "outcome_component":    float(outcome_component),
            "critical_consistency": float(critical_consistency),
            "reward_mode":          self.reward_mode,
        }

        return obs, float(reward), terminated, False, info
