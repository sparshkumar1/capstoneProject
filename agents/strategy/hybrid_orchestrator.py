"""
HybridOrchestrator — thin strategy layer used by the WebSocket interview handler.

Wraps the PPO policy (seed_123) + heuristic fallback in a single object so
frontend/main.py can do:

    orchestrator = HybridOrchestrator()
    new_diff, reason, action = orchestrator.suggest(score, difficulty, session)

It does NOT replace the OrchestratorAgent CLI; it exposes the same RL decision
logic through a reusable, import-safe class.
"""

from __future__ import annotations
from typing import Optional

_np  = None
_PPO = None
_RL_READY = False


def _try_load_rl():
    global _np, _PPO, _RL_READY
    if _RL_READY:
        return True
    try:
        import numpy as np_mod
        from stable_baselines3 import PPO as PPO_mod
        _np  = np_mod
        _PPO = PPO_mod
        _RL_READY = True
        return True
    except Exception:
        return False


ACTION_MAP = {0: "Easier", 1: "Same", 2: "Harder"}

BASELINE_DIFFICULTY_SCHEDULE = {
    0: 2,   # Q1 → easy (diff 2)
    1: 3,   # Q2 → mid  (diff 3)
}


class HybridOrchestrator:
    """
    Stateless-ish orchestrator: one instance per session is fine,
    but the session dict carries all mutable state so it can also
    be used as a singleton.
    """

    def __init__(
        self,
        model_path: str = "rl/checkpoints/seed_123/ppo_final.zip",
        vec_path:   str = "rl/checkpoints/seed_123/vecnormalize.pkl",
    ):
        self.model_path = model_path
        self.vec_path   = vec_path
        self.model      = None
        self.obs_mean   = None
        self.obs_var    = None
        self.obs_dim    = 6
        self.ready      = False
        self._attempted = False

    # ── Public API ────────────────────────────────────────────────────────

    def suggest(
        self,
        score: float,
        current_difficulty: int,
        session: dict,
    ) -> tuple[int, str, str]:
        """
        Returns (new_difficulty, reason_string, action_name).
        Baseline phase: returns deterministic easy→mid schedule, no RL.
        RL phase: PPO policy with heuristic fallback.
        """
        # ── Baseline guard ────────────────────────────────────────────
        if not session.get("baseline_complete", True):
            answered = len(session.get("scores", []))
            target = BASELINE_DIFFICULTY_SCHEDULE.get(answered, 3)
            session.setdefault("rl_perf_history", []).append(float(score))
            reason = (
                f"Baseline Q{answered + 1} — RL inactive, "
                f"difficulty fixed to {'easy' if target <= 2 else 'mid'} ({target})"
            )
            return target, reason, "Baseline"

        # ── RL phase ──────────────────────────────────────────────────
        if not self.ready:
            self._try_load()

        session.setdefault("rl_perf_history", []).append(float(score))
        history = session["rl_perf_history"]
        avg_perf = sum(history) / max(len(history), 1)

        conf = float(session.get("last_confidence_score", score))
        conf = max(0.0, min(1.0, conf))
        hesite = max(0.0, min(1.0, 1.0 - conf))

        answered = len(session.get("scores", []))
        total    = max(int(session.get("num_questions", 1)), 1)
        time_norm = max(0.0, min(1.0, answered / total))
        diff_norm = max(0.0, min(1.0, float(current_difficulty) / 5.0))

        if self.ready and _np is not None:
            raw = _np.array(
                [float(score), float(avg_perf), conf, hesite, time_norm, diff_norm],
                dtype=_np.float32,
            )
            raw = self._fit_dim(raw)
            obs = _np.clip(
                (raw - self.obs_mean) / _np.sqrt(self.obs_var + 1e-8),
                -10.0, 10.0,
            ).reshape(1, -1)
            action_pred, _ = self.model.predict(obs, deterministic=True)
            action_idx  = int(_np.asarray(action_pred).reshape(-1)[0])
            action_name = ACTION_MAP.get(action_idx, "Same")
        else:
            # Heuristic fallback
            if score > 0.80 and current_difficulty < 5:
                action_name = "Harder"
            elif score < 0.40 and current_difficulty > 1:
                action_name = "Easier"
            else:
                action_name = "Same"

        new_diff = int(current_difficulty)
        if action_name == "Easier":
            new_diff = max(1, new_diff - 1)
        elif action_name == "Harder":
            new_diff = min(5, new_diff + 1)

        session["rl_last_action"] = action_name
        src = "PPO(seed_123)" if self.ready else "heuristic"
        reason = f"RL [{src}]: {action_name} — score={score:.2f}, avg={avg_perf:.2f}"
        return new_diff, reason, action_name

    # ── Private helpers ───────────────────────────────────────────────────

    def _try_load(self):
        if self._attempted:
            return
        self._attempted = True
        if not _try_load_rl():
            return

        import os, pickle
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent.parent  # agents/strategy -> agents -> repo root
        mp   = root / self.model_path
        vp   = root / self.vec_path

        if not mp.exists() or not vp.exists():
            return
        try:
            self.model = _PPO.load(str(mp))
            with open(vp, "rb") as f:
                vec = pickle.load(f)
            self.obs_mean = _np.asarray(vec.obs_rms.mean, dtype=_np.float32)
            self.obs_var  = _np.asarray(vec.obs_rms.var,  dtype=_np.float32)
            self.obs_dim  = int(self.obs_mean.shape[0])
            self.ready    = True
            print(f"[HybridOrchestrator] PPO loaded (dim={self.obs_dim})")
        except Exception as e:
            print(f"[HybridOrchestrator] PPO load failed: {e}")

    def _fit_dim(self, arr):
        if arr.shape[0] == self.obs_dim:
            return arr
        if arr.shape[0] < self.obs_dim:
            pad = self.obs_dim - arr.shape[0]
            return _np.pad(arr, (0, pad), mode="edge")
        return arr[: self.obs_dim]
