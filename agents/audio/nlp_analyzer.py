try:
    from transformers import pipeline
except ImportError:
    pipeline = None


_CLASSIFIER = None

_CONFIDENT_TERMS = {
    "definitely", "clearly", "certainly", "sure", "confident", "strong", "always",
    "exactly", "absolutely", "prove", "because", "therefore", "hence", "conclude",
}
_HESITANT_TERMS = {
    "maybe", "perhaps", "might", "guess", "probably", "not sure", "unsure", "i think",
    "um", "uh", "like", "sort of", "kind of", "possibly", "idk",
}


def _get_classifier():
    global _CLASSIFIER
    if _CLASSIFIER is None:
        if pipeline is None:
            raise ImportError("transformers is not installed")
        _CLASSIFIER = pipeline(
            "zero-shot-classification",
            model="cross-encoder/nli-MiniLM2-L6-H768",
            device=-1,
        )
    return _CLASSIFIER


def _safe_text_score(transcript: str) -> dict:
    text = (transcript or "").strip().lower()
    if not text:
        return {
            "linguistic_score": 0.5,
            "label": "neutral",
            "label_scores": {"neutral": 1.0},
            "analysis_source": "heuristic_empty",
        }

    tokens = text.split()
    token_count = max(len(tokens), 1)
    confident_hits = sum(1 for term in _CONFIDENT_TERMS if term in text)
    hesitant_hits = sum(1 for term in _HESITANT_TERMS if term in text)

    hedge_density = min(1.0, hesitant_hits / max(1, token_count / 20))
    assertive_density = min(1.0, confident_hits / max(1, token_count / 25))

    raw = 0.5 + 0.28 * assertive_density - 0.28 * hedge_density
    linguistic_score = max(0.0, min(1.0, raw))

    if linguistic_score >= 0.62:
        label = "confident and assertive"
    elif linguistic_score <= 0.38:
        label = "uncertain and hesitant"
    else:
        label = "neutral"

    return {
        "linguistic_score": round(linguistic_score, 4),
        "label": label,
        "label_scores": {
            "confident and assertive": round(max(0.0, linguistic_score - 0.2), 4),
            "neutral": round(1.0 - min(1.0, abs(linguistic_score - 0.5) * 2), 4),
            "uncertain and hesitant": round(max(0.0, 0.8 - linguistic_score), 4),
        },
        "analysis_source": "heuristic",
    }


def analyze_linguistic_confidence(transcript: str) -> dict:
    if not transcript or not transcript.strip():
        return _safe_text_score(transcript)

    if pipeline is None:
        return _safe_text_score(transcript)

    try:
        clf = _get_classifier()
        result = clf(
            transcript,
            candidate_labels=[
                "confident and assertive",
                "uncertain and hesitant",
                "neutral",
            ],
        )
    except Exception:
        return _safe_text_score(transcript)

    label_scores = dict(zip(result["labels"], result["scores"]))
    confident_score = label_scores.get("confident and assertive", 0.0)
    uncertain_score = label_scores.get("uncertain and hesitant", 0.0)
    linguistic_score = (confident_score - uncertain_score + 1) / 2

    return {
        "linguistic_score": round(linguistic_score, 4),
        "label": result["labels"][0],
        "label_scores": {key: round(value, 4) for key, value in label_scores.items()},
        "analysis_source": "transformers",
    }


def analyze_text(transcript: str) -> dict:
    return analyze_linguistic_confidence(transcript)