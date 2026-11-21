def _clamp(value, minimum=0.0, maximum=1.0):
    """Clamp a numeric value to the inclusive range [minimum, maximum].

    Args:
        value (float): Value to clamp.
        minimum (float): Lower bound (default 0.0).
        maximum (float): Upper bound (default 1.0).

    Returns:
        float: `value` restricted to [minimum, maximum].
    """
    return max(minimum, min(maximum, value))


def _get(dct, key, default=0.0):
    """Safely read a numeric field from a dict, coercing to float.

    Args:
        dct (dict): Dict to read from.
        key (str): Key to look up.
        default (float): Value to use if the key is missing or the stored
            value can't be converted to float (default 0.0).

    Returns:
        float: The field's value as a float, or `default`.
    """
    try:
        value = dct.get(key, default)
        return float(value)
    except Exception:
        return float(default)


def _compute_components(prosodic, transcription, linguistic):
    """Derive the individual sub-scores that feed the final confidence score.

    Args:
        prosodic (dict): Prosodic features (`jitter`, `shimmer`, `hnr`,
            `pitch_stddev`).
        transcription (dict): Transcription/timing features
            (`total_speech_time`, `total_pause_time`, `true_speaking_rate`,
            `pause_count`, `transcription_confidence`).
        linguistic (dict): Linguistic-confidence output (`linguistic_score`).

    Returns:
        dict: `voice_quality`, `fluency_score`, `rate_score`,
            `rhythm_score`, `ling_score`, `asr_confidence`, the voice-quality
            sub-scores (`jitter_score`, `shimmer_score`, `hnr_score`,
            `pitch_var_score`), and the raw `pause_ratio` — all floats, most
            in [0, 1].
    """
    jitter = _get(prosodic, "jitter")
    shimmer = _get(prosodic, "shimmer")
    hnr = _get(prosodic, "hnr")
    pitch_std = _get(prosodic, "pitch_stddev")

    jitter_score = _clamp(1 - jitter / 0.03)
    shimmer_score = _clamp(1 - shimmer / 0.12)
    hnr_score = _clamp(hnr / 28.0)

    # Very flat or very unstable pitch can both reduce perceived confidence.
    if pitch_std <= 0:
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

    rate = _get(transcription, "true_speaking_rate", 0.0)
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
    """Compute the final blended speech-confidence score.

    Weighted blend of voice quality (28%), linguistic confidence (27%),
    fluency (22%), speaking rate (13%), and rhythm (10%); the weight on
    transcript-derived factors is reduced when ASR confidence is low.

    Args:
        prosodic (dict): Prosodic features, see `_compute_components`.
        transcription (dict): Transcription/timing features, see
            `_compute_components`.
        linguistic (dict): Linguistic-confidence output, see
            `_compute_components`.

    Returns:
        float: Final confidence score in [0, 1], rounded to 4 decimals.
    """
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
    """Compute the final confidence score together with every sub-component.

    Args:
        prosodic (dict): Prosodic features, see `_compute_components`.
        transcription (dict): Transcription/timing features, see
            `_compute_components`.
        linguistic (dict): Linguistic-confidence output, see
            `_compute_components`.

    Returns:
        dict: `final_score` (as from `score`) plus the rounded sub-scores
            `voice_quality`, `fluency_score`, `rate_score`, `rhythm_score`,
            `ling_score`, `asr_confidence`, `pause_ratio`, `jitter_score`,
            `shimmer_score`, `hnr_score`, and `pitch_var_score`.
    """
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