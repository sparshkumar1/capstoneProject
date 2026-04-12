from __future__ import annotations

import numpy as np

try:
    import whisperx

    _WHISPERX_AVAILABLE = True
except ImportError:
    whisperx = None
    _WHISPERX_AVAILABLE = False

try:
    from .audio_io import decode_audio, frame_rms
except ImportError:
    from audio_io import decode_audio, frame_rms


_MODEL = None
_ALIGN_MODEL = None
_METADATA = None


def _empty_transcription(alignment_source: str = "unavailable") -> dict:
    return {
        "transcript": "",
        "words": [],
        "pauses": [],
        "pause_count": 0,
        "total_pause_time": 0.0,
        "total_speech_time": 0.0,
        "true_speaking_rate": 0.0,
        "transcription_confidence": 0.0,
        "audio_duration": 0.0,
        "alignment_source": alignment_source,
    }


def _fallback_energy_timing(audio_path: str) -> dict:
    try:
        y, sr, decode_source = decode_audio(audio_path)
        if y.size == 0:
            return _empty_transcription(alignment_source=decode_source)

        frame_length = max(int(sr * 0.04), 256)
        hop_length = max(int(sr * 0.01), 64)
        rms = frame_rms(y, frame_length=frame_length, hop_length=hop_length)
        if rms.size == 0:
            return _empty_transcription(alignment_source=f"{decode_source}_empty")

        threshold = max(float(np.percentile(rms, 25) * 1.6), 1e-6)
        voiced_mask = rms > threshold
        frame_sec = hop_length / float(sr)

        pause_count = 0
        total_pause = 0.0
        run = 0
        for flag in voiced_mask:
            if flag:
                if run * frame_sec >= 0.2:
                    pause_count += 1
                    total_pause += run * frame_sec
                run = 0
            else:
                run += 1
        if run * frame_sec >= 0.2:
            pause_count += 1
            total_pause += run * frame_sec

        total_duration = len(y) / float(sr)
        total_speech = max(0.0, total_duration - total_pause)

        return {
            "transcript": "",
            "words": [],
            "pauses": [],
            "pause_count": int(pause_count),
            "total_pause_time": round(float(total_pause), 3),
            "total_speech_time": round(float(total_speech), 3),
            "true_speaking_rate": 0.0,
            "transcription_confidence": 0.35,
            "audio_duration": round(float(total_duration), 3),
            "alignment_source": f"{decode_source}_energy_fallback",
        }
    except Exception:
        return _empty_transcription(alignment_source="fallback_error")


def _get_models(device="cpu"):
    global _MODEL, _ALIGN_MODEL, _METADATA
    if _MODEL is None:
        if not _WHISPERX_AVAILABLE:
            raise ImportError("whisperx is not installed")

        compute_type = "int8" if device == "cpu" else "float16"
        _MODEL = whisperx.load_model("base", device, compute_type=compute_type)
        _ALIGN_MODEL, _METADATA = whisperx.load_align_model(language_code="en", device=device)
    return _MODEL, _ALIGN_MODEL, _METADATA


def transcribe_and_align(audio_path: str) -> dict:
    if not _WHISPERX_AVAILABLE:
        return _fallback_energy_timing(audio_path)

    model, align_model, metadata = _get_models()

    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=16)
    aligned = whisperx.align(result["segments"], align_model, metadata, audio, device="cpu")

    words = []
    for word in aligned.get("word_segments", []):
        token = (word.get("word") or "").strip()
        if token:
            words.append(
                {
                    "word": token,
                    "start": word.get("start"),
                    "end": word.get("end"),
                    "score": word.get("score"),
                }
            )

    pauses = []
    for i in range(1, len(words)):
        previous_end = words[i - 1].get("end")
        current_start = words[i].get("start")
        if previous_end is None or current_start is None:
            continue
        gap = current_start - previous_end
        if gap > 0.2:
            pauses.append({"after_word": words[i - 1]["word"], "duration": round(gap, 3)})

    transcript = " ".join(word["word"] for word in words).strip()
    total_speech = sum(
        (word.get("end", 0.0) - word.get("start", 0.0))
        for word in words
        if word.get("start") is not None and word.get("end") is not None
    )
    total_pause = sum(pause["duration"] for pause in pauses)
    segments = result.get("segments", [])
    confidence = float(np.clip(1.0 + np.mean([segment.get("avg_logprob", -1.0) for segment in segments]) if segments else 0.0, 0.0, 1.0))
    audio_duration = float(audio.shape[0] / 16000.0) if hasattr(audio, "shape") else 0.0

    # Prefer words/minute style normalization to avoid extreme values on short clips.
    effective_speech = max(total_speech, 0.8)
    true_rate = len(words) / effective_speech

    return {
        "transcript": transcript,
        "words": words,
        "pauses": pauses,
        "pause_count": len(pauses),
        "total_pause_time": round(total_pause, 3),
        "total_speech_time": round(total_speech, 3),
        "true_speaking_rate": round(true_rate, 2),
        "transcription_confidence": round(confidence, 4),
        "audio_duration": round(audio_duration, 3),
        "alignment_source": "whisperx",
    }


def transcribe_audio(audio_path: str) -> tuple[str, float]:
    transcription = transcribe_and_align(audio_path)
    return transcription.get("transcript", ""), transcription.get("transcription_confidence", 0.0)