try:
    from .audio_features import extract_prosodic_features
except ImportError:
    from audio_features import extract_prosodic_features


def analyze_tone(audio_path: str) -> dict:
    return extract_prosodic_features(audio_path)