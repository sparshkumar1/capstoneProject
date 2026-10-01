import math


def _clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def _get(dct, key, default=0.0):
    try:
        value = dct.get(key, default)
        return float(value)
    except Exception:
        return float(default)


def _get_measured(dct, key):
    """Returns the raw float value for key, or None if missing, non-numeric,
    NaN or infinite -- i.e. None means "no valid measurement", distinct from
    a genuine 0.0 reading. Callers must not feed None into a formula whose
    "no signal" case happens to coincide with a perfect-score input (e.g.
    jitter=0.0 scores as flawless voice quality); they must branch on it."""
    try:
        value = dct.get(key, None)
        if value is None:
            return None
        fvalue = float(value)
        if math.isnan(fvalue) or math.isinf(fvalue):
            return None
        return fvalue
    except Exception:
        return None


def _compute_components(prosodic, transcription, linguistic):
    jitter = _get_measured(prosodic, "jitter")
    shimmer = _get_measured(prosodic, "shimmer")
    hnr = _get_measured(prosodic, "hnr")
    pitch_std = _get_measured(prosodic, "pitch_stddev")

    # A missing, non-numeric, NaN or infinite voice-quality measurement (e.g.
    # Parselmouth failing on very short/silent/unvoiced audio) must not be
    # silently treated as a 0.0 reading, since 0.0 jitter/shimmer or a 0.0
    # pitch_stddev each happen to score as the *best* possible value in this
    # formula. Score the component neutrally (0.5) instead when unmeasured.
    jitter_score = 0.5 if jitter is None else _clamp(1 - jitter / 0.03)
    shimmer_score = 0.5 if shimmer is None else _clamp(1 - shimmer / 0.12)
    hnr_score = 0.5 if hnr is None else _clamp(hnr / 28.0)

    # Very flat or very unstable pitch can both reduce perceived confidence.
    if pitch_std is None:
        pitch_var_score = 0.5
    elif pitch_std <= 0:
        pitch_var_score = 0.5
    elif pitch_std < 12:
        pitch_var_score = _clamp(0.45 + (pitch_std / 12.0) * 0.35)
    elif pitch_std <= 70:
        pitch_var_score = 1.0
    else:
        pitch_var_score = _clamp(1.0 - (pitch_std - 70.0) / 130.0)

    voice_quality = (0.32 * jitter_score + 0.30 * shimmer_score + 0.28 * hnr_score + 0.10 * pitch_var_score)

    speech_time = max(_get(transcription, "total_speech_time", 1.0), 0.5)
    pause_time = max(_get(transcription, "total_pause_time", 0.0), 0.0)
    pause_ratio = pause_time / speech_time
    fluency_score = _clamp(1 - pause_ratio * 1.7)

    # true_speaking_rate is produced by transcriber.py in words per minute;
    # this scorer's threshold (2.1-4.3) is words per second. Convert here,
    # at the point of use, rather than changing the field's unit at its
    # source (agents/audio/transcriber.py, interview_orchestrator.py and
    # several verify_* scripts all consume/display it as WPM).
    rate = _get(transcription, "true_speaking_rate", 0.0) / 60.0
    if 2.1 <= rate <= 4.3:
        rate_score = 1.0
    else:
        rate_score = _clamp(1 - abs(rate - 3.2) / 3.2)

    pause_count = _get(transcription, "pause_count", 0)
    rhythm_score = _clamp(1.0 - max(0.0, pause_count - 7) / 12.0)

    ling_score = _clamp(_get(linguistic, "linguistic_score", 0.5))
    asr_conf = _clamp(_get(transcription, "transcription_confidence", 0.0))

    return {
        "voice_quality": voice_quality,
        "fluency_score": fluency_score,
        "rate_score": rate_score,
        "rhythm_score": rhythm_score,
        "ling_score": ling_score,
        "asr_confidence": asr_conf,
        "jitter_score": jitter_score,
        "shimmer_score": shimmer_score,
        "hnr_score": hnr_score,
        "pitch_var_score": pitch_var_score,
        "pause_ratio": pause_ratio,
    }


def score(prosodic, transcription, linguistic):
    c = _compute_components(prosodic, transcription, linguistic)

    final = (
        0.28 * c["voice_quality"] +
        0.27 * c["ling_score"] +
        0.22 * c["fluency_score"] +
        0.13 * c["rate_score"] +
        0.10 * c["rhythm_score"]
    )

    # Confidence in ASR quality slightly adjusts trust in transcript-driven factors.
    if c["asr_confidence"] < 0.45:
        final = 0.75 * final + 0.25 * c["voice_quality"]

    return round(_clamp(final), 4)


def score_breakdown(prosodic, transcription, linguistic):
    c = _compute_components(prosodic, transcription, linguistic)

    return {
        "final_score": score(prosodic, transcription, linguistic),
        "voice_quality": round(c["voice_quality"], 4),
        "fluency_score": round(c["fluency_score"], 4),
        "rate_score": round(c["rate_score"], 4),
        "rhythm_score": round(c["rhythm_score"], 4),
        "ling_score": round(c["ling_score"], 4),
        "asr_confidence": round(c["asr_confidence"], 4),
        "pause_ratio": round(c["pause_ratio"], 4),
        "jitter_score": round(c["jitter_score"], 4),
        "shimmer_score": round(c["shimmer_score"], 4),
        "hnr_score": round(c["hnr_score"], 4),
        "pitch_var_score": round(c["pitch_var_score"], 4),
    }