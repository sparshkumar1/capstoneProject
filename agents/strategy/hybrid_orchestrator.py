"""
HybridOrchestrator — Strategy layer for adaptive RL interview difficulty adjustment.

Wraps the PPO policy (seed_123) trained on InterviewEnv (6D observation, 3 discrete actions)
with explicit validation, canonical state extraction, and graceful heuristic fallback.

Discrete Action Space (3):
  0 = Easier (decrease difficulty by 1)
  1 = Same   (maintain current difficulty)
  2 = Harder (increase difficulty by 1)

Canonical Observation Space (6D):
  [0] performance      (float in [0, 1]): Latest answer score
  [1] avg_performance  (float in [0, 1]): Rolling mean of last 5 scores
  [2] confidence       (float in [0, 1]): Measured or estimated candidate confidence
  [3] hesitation       (float in [0, 1]): Measured or estimated candidate hesitation
  [4] time_norm        (float in [0, 1]): Normalized response latency
  [5] difficulty       (float in [0, 1]): Current difficulty normalized (diff / 5.0)
"""

from __future__ import annotations
import math
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path

_np = None
_PPO = None
_RL_READY = False


def _try_load_rl() -> bool:
    global _np, _PPO, _RL_READY
    if _RL_READY:
        return True
    try:
        import numpy as np_mod
        from stable_baselines3 import PPO as PPO_mod
        _np = np_mod
        _PPO = PPO_mod
        _RL_READY = True
        return True
    except Exception:
        return False


ACTION_MAP: Dict[int, str] = {0: "Easier", 1: "Same", 2: "Harder"}
ACTION_NAME_TO_IDX: Dict[str, int] = {"Easier": 0, "Same": 1, "Harder": 2}

BASELINE_DIFFICULTY_SCHEDULE: Dict[int, int] = {
    0: 2,   # Q1 → easy (diff 2)
    1: 3,   # Q2 → mid  (diff 3)
}


def build_rl_observation(
    score: float,
    current_difficulty: int,
    session: dict,
) -> Any:
    """
    Construct canonical 6D observation vector from InterviewOrchestrator canonical state.

    Guarantees:
      - Shape: (6,)
      - Dtype: float32
      - Range: [0.0, 1.0] for all raw components
      - No NaN or Inf
      - Deterministic ordering

    Dimension Index & Semantics:
      [0] perf: Latest evaluated question score (float in [0.0, 1.0])
      [1] avg_perf: Rolling mean of recent 5 answers (float in [0.0, 1.0])
      [2] conf: Candidate confidence signal from audio analysis or state (float in [0.0, 1.0])
      [3] hes: Candidate hesitation signal from acoustic/filler analysis (float in [0.0, 1.0])
      [4] time_norm: Normalized question latency from QuestionTimer (float in [0.0, 1.0])
      [5] diff_norm: Current difficulty mapped linearly to [0.0, 1.0] (diff / 5.0)
    """
    import numpy as np

    # 1. Performance (safe finite float in [0, 1])
    try:
        raw_perf = float(score)
        if math.isnan(raw_perf) or math.isinf(raw_perf):
            raw_perf = 0.5
    except (TypeError, ValueError):
        raw_perf = 0.5
    perf = float(np.clip(raw_perf, 0.0, 1.0))

    # 2. Rolling Average Performance (last 5 scores)
    history = session.get("rl_perf_history", [])
    if history:
        valid_history = [float(h) for h in history if not (math.isnan(h) or math.isinf(h))]
        avg_perf = float(np.mean(valid_history[-5:])) if valid_history else perf
    else:
        scores = session.get("scores", [])
        valid_scores = [float(s) for s in scores if not (math.isnan(s) or math.isinf(s))]
        avg_perf = float(np.mean(valid_scores[-5:])) if valid_scores else perf
    avg_perf = float(np.clip(avg_perf, 0.0, 1.0))

    # 3. Confidence Signal
    raw_conf = session.get("last_confidence_score")
    if raw_conf is None:
        raw_conf = session.get("last_confidence")
    if raw_conf is None or math.isnan(float(raw_conf)) or math.isinf(float(raw_conf)):
        raw_conf = perf
    conf = float(np.clip(float(raw_conf), 0.0, 1.0))

    # 4. Hesitation Signal
    raw_hes = session.get("last_hesitation_score")
    if raw_hes is None:
        raw_hes = session.get("last_hesitation")
    if raw_hes is None or math.isnan(float(raw_hes)) or math.isinf(float(raw_hes)):
        raw_hes = 1.0 - conf
    hes = float(np.clip(float(raw_hes), 0.0, 1.0))

    # 5. Response Latency (normalized time from QuestionTimer)
    raw_time = session.get("last_time_norm")
    if raw_time is None or math.isnan(float(raw_time)) or math.isinf(float(raw_time)):
        raw_time = 0.0
    time_norm = float(np.clip(float(raw_time), 0.0, 1.0))

    # 6. Normalized Difficulty Level
    try:
        raw_diff = float(current_difficulty) / 5.0
        if math.isnan(raw_diff) or math.isinf(raw_diff):
            raw_diff = 0.6
    except (TypeError, ValueError):
        raw_diff = 0.6
    diff_norm = float(np.clip(raw_diff, 0.0, 1.0))

    return np.array([perf, avg_perf, conf, hes, time_norm, diff_norm], dtype=np.float32)


class HybridOrchestrator:
    """
    RL difficulty orchestrator for adaptive technical interviews.
    Implements PPO policy inference with canonical 6D observation vector,
    strict checkpoint validation, and deterministic heuristic fallback.
    """

    def __init__(
        self,
        model_path: str = "rl/checkpoints/seed_123/ppo_final.zip",
        vec_path: str = "rl/checkpoints/seed_123/vecnormalize.pkl",
    ):
        self.model_path = model_path
        self.vec_path = vec_path
        self.model = None
        self.obs_mean = None
        self.obs_var = None
        self.obs_dim = 6
        self.ready = False
        self._attempted = False
        self.is_compatible = False
        self._try_load()

    def suggest(
        self,
        score: float,
        current_difficulty: int,
        session: dict,
    ) -> Tuple[int, str, str]:
        """
        Produce next difficulty proposal.
        Returns: (new_difficulty: int, reason: str, action_name: str)
        """
        # Baseline check
        if not session.get("baseline_complete", True):
            answered = len(session.get("scores", []))
            target = BASELINE_DIFFICULTY_SCHEDULE.get(answered, 3)
            session.setdefault("rl_perf_history", []).append(float(score))
            reason = (
                f"Baseline Q{answered + 1} — RL inactive, "
                f"difficulty fixed to {'easy' if target <= 2 else 'mid'} ({target})"
            )
            return target, reason, "Baseline"

        # Ensure model is loaded
        if not self.ready:
            self._try_load()

        session.setdefault("rl_perf_history", []).append(float(score))
        raw_obs = build_rl_observation(score, current_difficulty, session)
        session["last_rl_observation"] = raw_obs.tolist()

        if self.ready and self.is_compatible and _np is not None and self.model is not None:
            try:
                norm_obs = _np.clip(
                    (raw_obs - self.obs_mean) / _np.sqrt(self.obs_var + 1e-8),
                    -10.0, 10.0,
                ).reshape(1, -1)
                action_pred, _ = self.model.predict(norm_obs, deterministic=True)
                action_idx = int(_np.asarray(action_pred).reshape(-1)[0])
                action_name = ACTION_MAP.get(action_idx, "Same")
                src = "ppo"
                session["rl_status"] = "available"
                session["rl_source"] = "ppo"
                session["rl_last_action"] = action_name
                reason = f"PPO: {action_name} — score={score:.2f}, avg={raw_obs[1]:.2f}"
            except Exception as exc:
                action_name = self._heuristic_action(score, current_difficulty)
                src = "non_rl_heuristic_recovery"
                session["rl_status"] = "rl_unavailable"
                session["rl_source"] = "non_rl_heuristic_recovery"
                session["rl_last_action"] = None
                reason = f"Non-RL Recovery [PPO error: {exc}]: {action_name} — score={score:.2f}, avg={raw_obs[1]:.2f}"
        else:
            action_name = self._heuristic_action(score, current_difficulty)
            src = "non_rl_heuristic_recovery"
            session["rl_status"] = "rl_unavailable"
            session["rl_source"] = "non_rl_heuristic_recovery"
            session["rl_last_action"] = None
            reason = f"Non-RL Recovery [heuristic]: {action_name} — score={score:.2f}, avg={raw_obs[1]:.2f}"

        new_diff = int(current_difficulty)
        if action_name == "Easier":
            new_diff = max(1, new_diff - 1)
        elif action_name == "Harder":
            new_diff = min(5, new_diff + 1)

        return new_diff, reason, action_name


    def _heuristic_action(self, score: float, current_difficulty: int) -> str:
        """Deterministic heuristic fallback when RL model is not available or incompatible."""
        if score > 0.80 and current_difficulty < 5:
            return "Harder"
        elif score < 0.40 and current_difficulty > 1:
            return "Easier"
        return "Same"

    def _try_load(self) -> None:
        """Load and validate PPO model and VecNormalize state."""
        if self._attempted:
            return
        self._attempted = True
        if not _try_load_rl():
            return

        import pickle
        root = Path(__file__).resolve().parent.parent.parent
        mp = root / self.model_path
        vp = root / self.vec_path

        if not mp.exists() or not vp.exists():
            return

        try:
            loaded_model = _PPO.load(str(mp))

            # Validate Action Space (must be Discrete(3))
            act_space = getattr(loaded_model, "action_space", None)
            if act_space is None or getattr(act_space, "n", None) != 3:
                print(f"[HybridOrchestrator] Warning: Incompatible action space {act_space} in {mp}. Expected Discrete(3). Rejecting checkpoint.")
                self.is_compatible = False
                self.ready = False
                return

            # Validate Observation Space (must be Box(6,))
            obs_space = getattr(loaded_model, "observation_space", None)
            if obs_space is None or getattr(obs_space, "shape", None) != (6,):
                print(f"[HybridOrchestrator] Warning: Incompatible observation space {obs_space} in {mp}. Expected Box(6,). Rejecting checkpoint.")
                self.is_compatible = False
                self.ready = False
                return

            with open(vp, "rb") as f:
                vec = pickle.load(f)

            obs_rms = getattr(vec, "obs_rms", None)
            if obs_rms is None or not hasattr(obs_rms, "mean") or not hasattr(obs_rms, "var"):
                print(f"[HybridOrchestrator] Warning: Invalid vecnormalize pickle in {vp}.")
                self.is_compatible = False
                self.ready = False
                return

            self.obs_mean = _np.asarray(obs_rms.mean, dtype=_np.float32)
            self.obs_var = _np.asarray(obs_rms.var, dtype=_np.float32)
            self.obs_dim = int(self.obs_mean.shape[0])

            if self.obs_dim != 6:
                print(f"[HybridOrchestrator] Warning: Observation normalization dimension {self.obs_dim} != 6.")
                self.is_compatible = False
                self.ready = False
                return

            self.model = loaded_model
            self.is_compatible = True
            self.ready = True
            print(f"[HybridOrchestrator] PPO loaded successfully (dim={self.obs_dim}, actions=3)")
        except Exception as e:
            print(f"[HybridOrchestrator] PPO load failed: {e}")
            self.ready = False
            self.is_compatible = False
