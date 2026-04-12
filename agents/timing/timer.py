import time
from dataclasses import dataclass


@dataclass
class TimerSnapshot:
    allowed_time_sec: float
    started_at: float


class QuestionTimer:
    """Tracks per-question timing and normalized time for RL state."""

    def start(self, allowed_time_sec: float) -> TimerSnapshot:
        allowed = max(float(allowed_time_sec or 60.0), 1.0)
        return TimerSnapshot(allowed_time_sec=allowed, started_at=time.monotonic())

    def stop(self, snapshot: TimerSnapshot, attempts: int = 1, retries: int = 0) -> dict:
        elapsed = max(time.monotonic() - snapshot.started_at, 0.0)
        allowed = snapshot.allowed_time_sec
        overrun = max(elapsed - allowed, 0.0)
        return {
            "time_taken_sec": round(elapsed, 3),
            "allowed_time_sec": round(allowed, 3),
            "time_overrun_sec": round(overrun, 3),
            "is_overrun": overrun > 0.0,
            "time_norm": round(min(elapsed / allowed, 1.0), 4),
            "attempts": int(attempts),
            "retries": int(retries),
        }
