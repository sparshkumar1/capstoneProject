import json
import os
from collections import Counter
from datetime import datetime


class SessionLogger:
    """Appends per-turn JSON records to disk and produces a session summary."""

    def __init__(self, base_dir: str = "orchestrator_logs"):
        """Create a new, timestamp-named log directory for this session.

        Args:
            base_dir (str): Parent directory under which a fresh
                `session_<timestamp>/` directory is created (default
                "orchestrator_logs").

        Returns:
            None.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        self.session_dir = os.path.join(base_dir, self.session_id)
        os.makedirs(self.session_dir, exist_ok=True)

        self.turns_path = os.path.join(self.session_dir, "turns.jsonl")
        self.summary_path = os.path.join(self.session_dir, "summary.json")
        self.turns = []

    def log_turn(self, payload: dict) -> None:
        """Record one turn, in memory and appended to `turns.jsonl`.

        Args:
            payload (dict): Turn record to log (question metadata, scores,
                action, timing, etc.) — written as-is as one JSON line.

        Returns:
            None.
        """
        self.turns.append(payload)
        with open(self.turns_path, "a", encoding="utf-8") as fp:
            fp.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def finalize(self, extra: dict | None = None) -> dict:
        """Compute and persist the session-level summary to `summary.json`.

        Args:
            extra (dict | None): Additional fields to merge into the
                summary (e.g. candidate/session metadata); overrides
                computed fields of the same name.

        Returns:
            dict: The summary written to disk — always `session_id` and
                `total_turns`; if any turns were logged, also
                `average_validated_score`, `average_time_taken_sec`, and
                `action_distribution`.
        """
        extra = extra or {}

        total_turns = len(self.turns)
        if total_turns == 0:
            summary = {
                "session_id": self.session_id,
                "total_turns": 0,
                **extra,
            }
        else:
            avg_final = sum(t.get("final_validated_score", 0.0) for t in self.turns) / total_turns
            avg_time = sum(t.get("timing", {}).get("time_taken_sec", 0.0) for t in self.turns) / total_turns
            action_dist = Counter(t.get("action", "Unknown") for t in self.turns)

            summary = {
                "session_id": self.session_id,
                "total_turns": total_turns,
                "average_validated_score": round(float(avg_final), 4),
                "average_time_taken_sec": round(float(avg_time), 4),
                "action_distribution": dict(action_dist),
                **extra,
            }

        with open(self.summary_path, "w", encoding="utf-8") as fp:
            json.dump(summary, fp, indent=2)

        return summary
