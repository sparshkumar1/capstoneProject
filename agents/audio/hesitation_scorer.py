"""
Extracts a dedicated hesitation score for the RL state vector.
Combines acoustic pauses + filler density + pitch-drop markers.
"""
from __future__ import annotations
import math
import numpy as np

_FILLERS = {
    "um","uh","like","you know","basically","actually","literally",
    "right","so","hmm","ah","er","well","kind of","sort of","i mean",
}

def _clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def score_hesitation(prosodic: dict, transcription: dict) -> dict:
    """
    Returns hesitation_score in [0,1] plus sub-components.
    High score = high hesitation (bad for confidence).
    """
    words = transcription.get("words", [])
    transcript = transcription.get("transcript", "").lower()
    pause_count = transcription.get("pause_count", 0)
    total_pause = transcription.get("total_pause_time", 0.0)
    speech_time = max(transcription.get("total_speech_time", 1.0), 0.5)
    audio_dur   = max(transcription.get("audio_duration", speech_time), 0.5)

    # 1. Pause ratio (>0.3 is high hesitation)
    pause_ratio = _clamp(total_pause / audio_dur)
    pause_score = _clamp(pause_ratio / 0.45)

    # 2. Pause frequency (pauses per 10s)
    pause_freq = pause_count / (audio_dur / 10.0)
    freq_score = _clamp(pause_freq / 8.0)

    # 3. Long pauses (>1.5s each)
    pauses = transcription.get("pauses", [])
    long_pauses = sum(1 for p in pauses if p.get("duration", 0) > 1.5)
    long_score  = _clamp(long_pauses / 4.0)

    # 4. Filler density with strict word-boundary matching
    import re
    token_count = max(len(transcript.split()), 1)
    filler_hits = sum(1 for f in _FILLERS if re.search(r"\b" + re.escape(f) + r"\b", transcript))
    filler_density = _clamp(filler_hits / max(token_count / 15, 1))

    # 5. Pitch instability during speech (jitter proxy). A missing, non-numeric,
    # NaN or infinite jitter reading (e.g. Parselmouth failing on very
    # short/silent/unvoiced audio) must not silently become a fabricated
    # instability reading -- score this component neutrally (0.5) instead of
    # letting a NaN propagate through _clamp (which would otherwise clamp NaN
    # to 1.0, the worst-case hesitation contribution, for a signal that was
    # never actually measured).
    _jitter_raw = prosodic.get("jitter", 0.02)
    try:
        jitter = float(_jitter_raw)
        if math.isnan(jitter) or math.isinf(jitter):
            raise ValueError
        pitch_instability = _clamp(jitter / 0.05)
    except (TypeError, ValueError):
        pitch_instability = 0.5

    # 6. Speaking rate deviation (optimal 2.1-4.3 words/sec). true_speaking_rate
    # is produced by transcriber.py in words per minute; convert to words per
    # second here, at the point of use (see confidence_scorer.py's matching
    # comment). A missing or non-numeric value keeps the prior "assume
    # optimal" default (3.2, already words/sec) rather than being treated as
    # a real rate of zero.
    _rate_raw = transcription.get("true_speaking_rate")
    try:
        rate = 3.2 if _rate_raw is None else float(_rate_raw) / 60.0
    except (TypeError, ValueError):
        rate = 3.2
    if 2.1 <= rate <= 4.3:
        rate_dev = 0.0
    else:
        rate_dev = _clamp(abs(rate - 3.2) / 3.2)

    hesitation_score = (
        0.30 * pause_score +
        0.20 * freq_score +
        0.15 * long_score +
        0.20 * filler_density +
        0.10 * pitch_instability +
        0.05 * rate_dev
    )

    return {
        "hesitation_score":    round(_clamp(hesitation_score), 4),
        "pause_ratio":         round(pause_ratio, 4),
        "pause_frequency":     round(pause_freq, 2),
        "long_pause_count":    long_pauses,
        "filler_density":      round(filler_density, 4),
        "pitch_instability":   round(pitch_instability, 4),
        "rate_deviation":      round(rate_dev, 4),
    }
