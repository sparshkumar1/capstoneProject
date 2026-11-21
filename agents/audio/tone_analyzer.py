try:
    from .audio_features import extract_prosodic_features
except ImportError:
    from audio_features import extract_prosodic_features


def analyze_tone(audio_path: str) -> dict:
    """Analyze the vocal tone of a recorded answer.

    Args:
        audio_path (str): Filesystem path to the candidate's audio recording.

    Returns:
        dict: Prosodic feature dictionary produced by
            `extract_prosodic_features` (pitch, energy, jitter/shimmer, HNR,
            etc.) — this function is a thin pass-through wrapper around it.
    """
    return extract_prosodic_features(audio_path)