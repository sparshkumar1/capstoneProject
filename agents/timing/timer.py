"""
timer.py — Question timing, pacing analysis, and configurable score modulation.

Tracks per-question response duration, computes normalized latency metrics for RL,
and calculates the Stage 6 final score timing modifier f_time(tau, S_tech).

Key Principles:
  1. Technical Correctness Dominance: Fast incorrect answers never receive speed bonuses.
     Speed bonus delta_fast is only unlocked when raw technical score S_tech >= 0.70.
  2. Asymmetric Pacing Modulation: Modest incentive for efficient mastery (+3% max),
     principled penalty for severe timeouts (-10% max).
  3. Strict Decoupling: Raw authoritative Stage 1 evaluator scores are preserved verbatim.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class TimerSnapshot:
    """Immutable state snapshot captured at question dispatch."""
    allowed_time_sec: float
    started_at: float
    question_id: str = ""
    question_type: str = "verbal"


class QuestionTimer:
    """
    Manages per-question timing measurements and calculates configurable
    response-time modifiers for final interview evaluations.
    """

    def __init__(
        self,
        delta_fast: float = 0.03,
        delta_overrun: float = 0.10,
        fast_threshold: float = 0.50,
        min_score_for_fast_bonus: float = 0.70,
    ):
        self.delta_fast = float(delta_fast)
        self.delta_overrun = float(delta_overrun)
        self.fast_threshold = float(fast_threshold)
        self.min_score_for_fast_bonus = float(min_score_for_fast_bonus)

    def start(
        self,
        allowed_time_sec: float = 60.0,
        question_id: str = "",
        question_type: str = "verbal",
    ) -> TimerSnapshot:
        """Start stopwatch for a question."""
        allowed = max(float(allowed_time_sec or 60.0), 1.0)
        return TimerSnapshot(
            allowed_time_sec=allowed,
            started_at=time.monotonic(),
            question_id=str(question_id or ""),
            question_type=str(question_type or "verbal"),
        )

    def stop(
        self,
        snapshot: TimerSnapshot,
        attempts: int = 1,
        retries: int = 0,
    ) -> Dict[str, Any]:
        """
        Stop stopwatch and return timing metrics.

        Returns:
          time_taken_sec: Actual elapsed duration in seconds
          allowed_time_sec: Target allocated time in seconds
          time_overrun_sec: Duration exceeding allowed time (0 if on-time)
          time_ratio: Unclamped ratio (time_taken / allowed)
          time_norm: Clamped ratio in [0.0, 1.0] for RL state vector
          is_overrun: True if candidate exceeded allowed duration
        """
        elapsed = max(time.monotonic() - snapshot.started_at, 0.0)
        allowed = snapshot.allowed_time_sec
        overrun = max(elapsed - allowed, 0.0)
        ratio = elapsed / allowed if allowed > 0 else 1.0

        return {
            "time_taken_sec": round(elapsed, 3),
            "allowed_time_sec": round(allowed, 3),
            "time_overrun_sec": round(overrun, 3),
            "time_ratio": round(ratio, 4),
            "time_norm": round(min(max(ratio, 0.0), 1.0), 4),
            "is_overrun": overrun > 0.0,
            "attempts": int(attempts),
            "retries": int(retries),
            "question_id": snapshot.question_id,
            "question_type": snapshot.question_type,
        }

    def compute_timing_modifier(
        self,
        raw_score: float,
        time_ratio: float,
        delta_fast: Optional[float] = None,
        delta_overrun: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate the Stage 6 final score timing modifier f_time(tau, S_tech).

        Mathematical Formulation:
          f_time(tau, S) =
            + min(delta_fast, delta_fast * S)   if tau <= 0.50 and S >= 0.70
            0.0                                 if 0.50 < tau <= 1.00
            - delta_overrun * min(1.0, tau - 1) if tau > 1.00

        Guarantees:
          - S < 0.70 NEVER receives a positive modifier (Fast + Wrong -> 0 speed bonus).
          - Modifiers are strictly bounded [-delta_overrun, +delta_fast].
          - Final score is clamped in [0.0, 1.0].
        """
        d_fast = float(self.delta_fast if delta_fast is None else delta_fast)
        d_over = float(self.delta_overrun if delta_overrun is None else delta_overrun)

        try:
            s_raw = float(raw_score)
            if math.isnan(s_raw) or math.isinf(s_raw):
                s_raw = 0.0
        except (TypeError, ValueError):
            s_raw = 0.0
        s_raw = max(0.0, min(1.0, s_raw))

        try:
            tau = float(time_ratio)
            if math.isnan(tau) or math.isinf(tau):
                tau = 1.0
        except (TypeError, ValueError):
            tau = 1.0
        tau = max(0.0, tau)

        # 1. Timing Quality / Pacing Score S_time in [0, 1] (Continuous everywhere)
        if tau <= 0.70:
            timing_score = 1.00
        elif tau <= 1.00:
            # Smooth descent from 1.00 to 0.85 across [0.70, 1.00]
            timing_score = 1.00 - 0.15 * ((tau - 0.70) / 0.30)
        else:
            # Smooth descent from 0.85 to 0.00 across [1.00, 2.70]
            timing_score = max(0.0, 0.85 - 0.50 * (tau - 1.00))
        timing_score = round(max(0.0, min(1.0, timing_score)), 4)


        # 2. Timing Modifier f_time
        if tau <= self.fast_threshold:
            # Fast answer: only reward if technical correctness is already established (S >= 0.70)
            if s_raw >= self.min_score_for_fast_bonus:
                modifier = round(d_fast * s_raw, 4)
            else:
                modifier = 0.0
        elif tau <= 1.00:
            # Nominal pacing: zero modifier
            modifier = 0.0
        else:
            # Overtime / overrun: progressive penalty capped at delta_overrun
            overrun_fraction = min(1.0, tau - 1.0)
            modifier = -round(d_over * overrun_fraction, 4)

        final_score = round(max(0.0, min(1.0, s_raw + modifier)), 4)

        return {
            "raw_score": s_raw,
            "time_ratio": round(tau, 4),
            "timing_score": timing_score,
            "timing_modifier": modifier,
            "final_score": final_score,
            "is_fast": tau <= self.fast_threshold,
            "is_overrun": tau > 1.00,
            "speed_bonus_eligible": s_raw >= self.min_score_for_fast_bonus and tau <= self.fast_threshold,
        }
