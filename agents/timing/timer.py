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
        """Configure the fast/overrun bonus-penalty thresholds for this timer.

        Args:
            delta_fast (float): Maximum positive speed-bonus modifier
                (default 0.03).
            delta_overrun (float): Maximum negative overrun-penalty modifier
                (default 0.10).
            fast_threshold (float): Time ratio at or below which an answer
                counts as "fast" (default 0.50).
            min_score_for_fast_bonus (float): Minimum raw technical score
                required before a fast answer can earn a speed bonus
                (default 0.70).

        Returns:
            None.
        """
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
        """Start the stopwatch for a question.

        Args:
            allowed_time_sec (float): Time budget for this question in
                seconds (default 60.0; clamped to at least 1.0).
            question_id (str): Identifier of the question being timed.
            question_type (str): Question type, e.g. "verbal" or "coding"
                (default "verbal").

        Returns:
            TimerSnapshot: Immutable snapshot recording the start time and
                allotted time, to be passed to `stop()` later.
        """
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
        """Stop the stopwatch and compute timing metrics for this question.

        Args:
            snapshot (TimerSnapshot): The snapshot returned by `start()` for
                this question.
            attempts (int): Number of attempts the candidate made (default
                1).
            retries (int): Number of retries within those attempts (default
                0).

        Returns:
            dict: `time_taken_sec` (actual elapsed duration),
                `allowed_time_sec` (target budget), `time_overrun_sec`
                (seconds over budget, 0 if on-time), `time_ratio`
                (unclamped taken/allowed), `time_norm` (ratio clamped to
                [0, 1], for the RL state vector), `is_overrun` (bool),
                plus `attempts`, `retries`, `question_id`, and
                `question_type` passed through from the snapshot/args.
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
        """Calculate the Stage 6 final-score timing modifier f_time(tau, S_tech).

        Mathematical Formulation:
          f_time(tau, S) =
            + min(delta_fast, delta_fast * S)   if tau <= 0.50 and S >= 0.70
            0.0                                 if 0.50 < tau <= 1.00
            - delta_overrun * min(1.0, tau - 1) if tau > 1.00

        Guarantees:
          - S < 0.70 NEVER receives a positive modifier (Fast + Wrong -> 0 speed bonus).
          - Modifiers are strictly bounded [-delta_overrun, +delta_fast].
          - Final score is clamped in [0.0, 1.0].

        Args:
            raw_score (float): Raw technical score S_tech, coerced to a
                finite value in [0, 1] (invalid/NaN/Inf input becomes 0.0).
            time_ratio (float): Elapsed/allowed time ratio tau, coerced to a
                finite non-negative value (invalid/NaN/Inf input becomes
                1.0).
            delta_fast (float | None): Override for this call's maximum
                speed bonus; defaults to the instance's `delta_fast`.
            delta_overrun (float | None): Override for this call's maximum
                overrun penalty; defaults to the instance's
                `delta_overrun`.

        Returns:
            dict: `raw_score`, `time_ratio` (sanitized inputs),
                `timing_score` (continuous pacing-quality score in [0, 1]),
                `timing_modifier` (the signed f_time value applied),
                `final_score` (`raw_score + timing_modifier`, clamped to
                [0, 1]), `is_fast`, `is_overrun`, and
                `speed_bonus_eligible` (bools).
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
