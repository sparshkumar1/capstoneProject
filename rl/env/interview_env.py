"""
interview_env.py — Merged environment
6D state + 3 actions (Easier / Same / Harder) + oracle-guided hybrid reward.

State (6D):
  [0] performance      - last answer score 0..1
  [1] avg_performance  - rolling mean of last 5 scores
  [2] confidence       - from SimulatedCandidate
  [3] hesitation       - from SimulatedCandidate
  [4] progress         - normalized turn progress ratio (t / T in 0..1)
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

try:
    from rl.guardrails import apply_canonical_guardrails
except ImportError:
    try:
        from guardrails import apply_canonical_guardrails
    except ImportError:
        apply_canonical_guardrails = None


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
        """Construct the Gymnasium interview environment and its reward configuration.

        Args:
            simulated_candidate: A `SimulatedCandidate` instance to drive
                answers; a default one is created if None.
            max_steps (int): Questions per episode (default 15).
            strict_logging (bool): If True, raise on a CSV logging failure
                instead of just warning (default False).
            initial_difficulty (float | None): Fixed starting difficulty for
                evaluation runs; if None, `reset()` samples uniformly from
                [0.3, 0.7].
            reward_mode (str): One of "oracle", "outcome", "hybrid"
                (default "hybrid") — which reward formulation `step()` uses.
            log_file (str): CSV path for per-step training logs.
            oracle_scale (float): Scale factor for the oracle-only reward
                mode.
            hybrid_decision_weight, hybrid_outcome_weight,
                hybrid_shaping_weight (float): Relative weights of the
                three hybrid-reward components (auto-normalized to sum to
                1).
            critical_mismatch_penalty, critical_match_bonus (float): Reward
                adjustment when the action does/doesn't match the oracle in
                a "critical" state.
            outcome_delta_clip, outcome_tanh_gain (float): Clipping and gain
                for the outcome (score-improvement) reward component; both
                must be > 0.
            repeat_easier_penalty (float): Penalty for choosing Easier twice
                in a row.
            conf_weight_low_perf, conf_weight_high_perf,
                conf_perf_threshold (float): Confidence weighting in the
                shaping component, switched at the performance threshold.
            hesitation_weight, time_weight (float): Shaping-component
                weights for hesitation and normalized response time.
            delta_transform_gain (float): If > 0, applies a tanh transform
                to the raw score delta before clipping.
            persona_bonus_nervous, persona_bonus_lucky,
                persona_bonus_overconfident, persona_bonus_junior (float):
                Fixed reward bias per simulated-candidate persona.
            guardrails_enabled (bool): Whether `_apply_guardrails` can
                override the proposed action (default True).
            medium_difficulty_min, medium_difficulty_max (float): Bounds of
                the "medium difficulty" band used by guardrail G1; must
                satisfy 0 <= min <= max <= 1.
            oscillation_penalty (float): Penalty for an Easier<->Harder
                zigzag between consecutive steps.
            followup_overuse_limit (int): Unused by the current reward
                logic; reserved for follow-up-overuse shaping.

        Returns:
            None.

        Raises:
            ValueError: If `reward_mode` is invalid, `outcome_delta_clip`
                or `outcome_tanh_gain` isn't positive, the medium-difficulty
                bounds are invalid, or the hybrid weights sum to <= 0.
        """
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

        Args:
            obs: 6-element observation
                `[perf, avg_perf, conf, hes, time_norm, difficulty]`.

        Returns:
            int: Oracle action index (0=Easier, 1=Same, 2=Harder).
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
        """Apply the post-inference guardrail rules to a proposed action.

        Delegates to the canonical `rl.guardrails.apply_canonical_guardrails`
        when importable; otherwise falls back to a dormant inline copy of
        the same rules (kept in sync so a broken import can't silently
        reintroduce an already-fixed safety gap). A no-op if
        `self.guardrails_enabled` is False.

        Args:
            pre_obs: 6-element observation from before this step,
                `[perf, avg_perf, conf, hes, progress, difficulty]`.
            proposed_action (int): The action the policy (or oracle)
                proposed, before guardrail review.

        Returns:
            tuple[int, bool, str]: `(final_action, was_overridden,
                guardrail_id)`.
        """
        if not self.guardrails_enabled:
            return int(proposed_action), False, "none"

        perf, avg_perf, conf, hes, progress, difficulty = [float(x) for x in pre_obs]
        if apply_canonical_guardrails is not None:
            return apply_canonical_guardrails(
                perf=perf,
                avg_perf=avg_perf,
                conf=conf,
                hes=hes,
                progress=progress,
                difficulty=difficulty,
                proposed_action=proposed_action,
                medium_difficulty_min=self.medium_difficulty_min,
                medium_difficulty_max=self.medium_difficulty_max,
            )

        action = int(proposed_action)

        # G4: Stuck candidate — HIGHEST PRIORITY (before G1)
        if perf < 0.30 and hes > 0.60:
            return 0, True, "g4_stuck_easier"

        # G1: overload — weak candidate at medium difficulty (not stuck)
        if (perf < 0.30
                and self.medium_difficulty_min <= difficulty <= self.medium_difficulty_max):
            return 0, True, "g1_overload_protection"

        # G2: anxiety stabiliser — low confidence + high hesitation + NOT high performer
        if conf < 0.30 and hes > 0.70 and perf < 0.80:
            return 1, True, "g2_anxiety_stabilizer_same"

        # G5: Partial understanding — stay at Same
        # Boundary widened 2026-11-13 to perf>=0.30 to match the fix already applied in
        # rl/guardrails.py (2026-11-12, see testing_and_evaluation/Phase4_Diagnosis_and_Fixes.md):
        # perf in [0.30, 0.40) was previously unguarded by this inline fallback (it falls through
        # to `return action, False, "none"` below, i.e. no safety override), reproducing the exact
        # gap rl/guardrails.py already closed. This path only executes if the normal
        # `from rl.guardrails import apply_canonical_guardrails` import fails (see the branch
        # above) -- it is a dormant duplicate, kept in sync so a broken import cannot silently
        # reintroduce an already-fixed safety gap. Guardrail logic only; the separate, protected
        # reward-function oracle (`oracle_action_from_obs`, R5) and the reward's own
        # `critical_state` detection intentionally keep their original 0.40 boundary and are not
        # touched by this change.
        if (0.30 <= perf < 0.65 and avg_perf < 0.60):
            return 1, True, "g5_partial_same"

        # G6: Strong candidate with big gap -> always Harder
        gap = perf - difficulty
        nervous_expert_state = 0.80 < perf < 0.95 and hes > 0.65
        if perf >= 0.90 and gap > 0.25 and not nervous_expert_state:
            return 2, True, "g6_strong_harder"

        return action, False, "none"

    @staticmethod
    def _is_zigzag_transition(prev_action, current_action):
        """Check whether two consecutive actions form an Easier<->Harder zigzag.

        Args:
            prev_action (int | None): Previous step's final action index.
            current_action (int): This step's final action index.

        Returns:
            bool: True if one action was Easier (0) and the other Harder
                (2), in either order.
        """
        return bool(
            (prev_action == 0 and current_action == 2)
            or (prev_action == 2 and current_action == 0)
        )

    def _persona_bias_correction(self):
        """Look up the fixed reward bias configured for the current candidate's persona.

        Args:
            None.

        Returns:
            float: The matching `persona_bonus_*` value, or 0.0 for
                personas without a configured bias (including "normal").
        """
        persona = getattr(self.sim_candidate, "persona", "normal")
        if persona == "nervous_expert":     return self.persona_bonus_nervous
        if persona == "lucky_guesser":      return self.persona_bonus_lucky
        if persona == "overconfident_fail": return self.persona_bonus_overconfident
        if persona == "struggling_junior":  return self.persona_bonus_junior
        return 0.0

    def _normalize_time(self, response_time, difficulty):
        """Normalize a response time against a difficulty-scaled ideal time.

        Args:
            response_time (float): Raw response time in seconds.
            difficulty (float): Question difficulty in [0, 1], used to
                scale the "ideal" expected time.

        Returns:
            float: Normalized time in [0, 1] (response_time / (2x ideal
                time), clamped).
        """
        ideal_time = 3.0 + 6.0 * difficulty
        return float(np.clip(response_time / (ideal_time * 2.0), 0.0, 1.0))

    # ─────────────────────────────────────────────────────────────────
    # Gym interface
    # ─────────────────────────────────────────────────────────────────

    def reset(self, *, seed=None, options=None):
        """Start a new episode (Gymnasium API).

        Args:
            seed (int | None): Seed for this episode's RNG.
            options (dict | None): Unused; accepted for Gymnasium API
                compatibility.

        Returns:
            tuple[np.ndarray, dict]: `(obs, info)` — the initial 6D
                observation (zeroed performance/confidence history, at a
                difficulty from `initial_difficulty` or sampled uniformly
                from [0.3, 0.7]) and an empty info dict.
        """
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
        """Advance the episode by one question (Gymnasium API).

        Computes the oracle action for the pre-step state, applies
        guardrails to the proposed action, simulates the candidate's
        answer, computes the configured reward (oracle/outcome/hybrid, plus
        stability/critical-state/persona adjustments), updates difficulty,
        appends a row to the CSV training log, and builds the next
        observation.

        Args:
            action (int): Proposed action index from the policy (0=Easier,
                1=Same, 2=Harder), before guardrail review.

        Returns:
            tuple[np.ndarray, float, bool, bool, dict]: `(obs, reward,
                terminated, truncated, info)` — the next 6D observation,
                the scalar reward, whether the episode ended
                (`current_step >= max_steps`), always `truncated=False`,
                and an `info` dict with the guardrail/oracle/reward-
                component detail for this step.
        """
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

        progress = float(np.clip(self.current_step / float(self.max_steps), 0.0, 1.0))

        obs = np.array(
            [perf, avg_perf, conf, hes, progress, self.difficulty],
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
                    current_difficulty, perf, avg_perf, conf, hes, progress,
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
            "progress":             float(progress),
            "time_norm":            float(t_norm),
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
