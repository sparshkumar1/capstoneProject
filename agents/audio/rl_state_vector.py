"""
Builds S = [Performance, Confidence, Hesitation, Time, Difficulty]
for the PrepAIred PPO agent from audio analysis outputs.
"""

from __future__ import annotations
import time

_sessions: dict[str, dict] = {}

def _clamp(v, lo=0.0, hi=1.0):
    """Clamp a numeric value to the inclusive range [lo, hi].

    Args:
        v (float): Value to clamp (coerced to float).
        lo (float): Lower bound (default 0.0).
        hi (float): Upper bound (default 1.0).

    Returns:
        float: `v` restricted to [lo, hi].
    """
    return max(lo, min(hi, float(v)))

def build_state_vector(
    confidence_score: float,
    hesitation: dict,
    transcription: dict,
    linguistic: dict,
    session_id: str = "default",
    current_difficulty: float = 0.5,
    question_index: int = 0,
    max_questions: int = 10,
) -> dict:
    """Build the 5-D audio-pipeline state vector S = [Performance, Confidence,
    Hesitation, Time, Difficulty], and a rule-based action recommendation.

    Updates in-memory per-session timing/history state as a side effect, so
    repeated calls with the same `session_id` accumulate a turn history used
    for the (currently unused) average-performance calculation.

    Args:
        confidence_score (float): Blended confidence score in [0, 1] from
            `confidence_scorer.score`.
        hesitation (dict): Output of `score_hesitation`; its
            `hesitation_score` field is used.
        transcription (dict): Transcription output; `transcription_confidence`
            and `audio_duration` are used.
        linguistic (dict): Linguistic-confidence output; `linguistic_score`
            is used.
        session_id (str): Session identifier for timing/history tracking
            (default "default").
        current_difficulty (float): Current question difficulty, normalized
            in [0, 1] (default 0.5).
        question_index (int): Zero-based index of the current question
            (default 0).
        max_questions (int): Total questions in the session, used to budget
            the `Time` component (default 10).

    Returns:
        dict: `state_vector` (the 5 rounded floats S), `labels` (their
            names), `recommended_action` ("harder"/"easier"/"hint"/"same"),
            `session_id`, `question_index`, and `components` (the same five
            values as a named dict).
    """
    # Track session timing
    sess = _sessions.setdefault(session_id, {"start": time.time(), "q_times": []})
    elapsed = time.time() - sess["start"]
    audio_dur = transcription.get("audio_duration", 10.0)
    sess["q_times"].append(audio_dur)

    # Performance: blend ASR confidence + linguistic score
    asr_conf  = _clamp(transcription.get("transcription_confidence", 0.5))
    ling_score = _clamp(linguistic.get("linguistic_score", 0.5))
    performance = _clamp(0.55 * ling_score + 0.45 * asr_conf)

    # Confidence: direct from scorer
    conf = _clamp(confidence_score)

    # Hesitation
    hes = _clamp(hesitation.get("hesitation_score", 0.5))

    # Time: fraction of session budget used (assume ~2 min per question)
    budget = max_questions * 120.0
    time_norm = _clamp(elapsed / budget)

    # Difficulty passthrough
    diff = _clamp(current_difficulty)

    S = [
        round(performance, 4),
        round(conf, 4),
        round(hes, 4),
        round(time_norm, 4),
        round(diff, 4),
    ]

    # PPO action recommendation (rule-based until real RL model trained)
    avg_perf = sum(s["performance"] for s in _sessions[session_id].get("history", [{"performance": performance}])) / max(1, len(_sessions[session_id].get("history", [])))

    if conf > 0.70 and hes < 0.30:
        action = "harder"
    elif conf < 0.40 or hes > 0.65:
        action = "easier"
    elif hes > 0.45:
        action = "hint"
    else:
        action = "same"

    record = {
        "performance": performance,
        "confidence": conf,
        "hesitation": hes,
        "action": action,
    }
    sess.setdefault("history", []).append(record)

    return {
        "state_vector":  S,
        "labels":        ["Performance", "Confidence", "Hesitation", "Time", "Difficulty"],
        "recommended_action": action,
        "session_id":    session_id,
        "question_index": question_index,
        "components": {
            "performance":  round(performance, 4),
            "confidence":   round(conf, 4),
            "hesitation":   round(hes, 4),
            "time_norm":    round(time_norm, 4),
            "difficulty":   round(diff, 4),
        },
    }


def reset_session(session_id: str = "default"):
    """Discard the in-memory timing/history state for a session.

    Args:
        session_id (str): Session identifier to clear (default "default").

    Returns:
        None: Removes the session's entry from the module-level `_sessions`
            cache if present; no error if it doesn't exist.
    """
    _sessions.pop(session_id, None)
