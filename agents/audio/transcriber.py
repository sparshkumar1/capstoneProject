from __future__ import annotations

import numpy as np

try:
    import torchaudio
    if not hasattr(torchaudio, "AudioMetaData"):
        from dataclasses import dataclass

        @dataclass
        class AudioMetaData:
            sample_rate: int = 16000
            num_frames: int = 0
            num_channels: int = 1
            bits_per_sample: int = 16
            encoding: str = "PCM_S"

        torchaudio.AudioMetaData = AudioMetaData
    if not hasattr(torchaudio, "list_audio_backends"):
        torchaudio.list_audio_backends = lambda: ["soundfile"]
    if not hasattr(torchaudio, "set_audio_backend"):
        torchaudio.set_audio_backend = lambda backend: None
except Exception:
    pass

try:
    import torch
    import omegaconf
    if hasattr(torch.serialization, "add_safe_globals"):
        torch.serialization.add_safe_globals([
            omegaconf.listconfig.ListConfig,
            omegaconf.dictconfig.DictConfig,
            omegaconf.nodes.IntegerNode,
            omegaconf.nodes.StringNode,
            omegaconf.nodes.BooleanNode,
            omegaconf.nodes.FloatNode,
            omegaconf.nodes.AnyNode,
            omegaconf.basecontainer.BaseContainer,
            omegaconf.base.Container,
            omegaconf.base.Node,
        ])
except Exception:
    pass

try:
    import whisperx
    from whisperx.vads.pyannote import VoiceActivitySegmentation
    from pyannote.audio.pipelines.voice_activity_detection import VoiceActivityDetection

    def _vas_init_shim(self, segmentation="pyannote/segmentation", fscore=False, token=None, **inference_kwargs):
        VoiceActivityDetection.__init__(self, segmentation=segmentation, fscore=fscore, **inference_kwargs)

    VoiceActivitySegmentation.__init__ = _vas_init_shim
    _WHISPERX_AVAILABLE = True
except (ImportError, Exception):
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

        min_rms = float(np.min(rms))
        max_rms = float(np.max(rms))
        threshold = max(min_rms + 0.15 * (max_rms - min_rms), 0.005)
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
        import torch

        _orig_torch_load = torch.load

        def _compat_torch_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return _orig_torch_load(*args, **kwargs)

        try:
            torch.load = _compat_torch_load
            _MODEL = whisperx.load_model("base", device, compute_type=compute_type)
            _ALIGN_MODEL, _METADATA = whisperx.load_align_model(language_code="en", device=device)
        finally:
            torch.load = _orig_torch_load
    return _MODEL, _ALIGN_MODEL, _METADATA


def normalize_transcript_text(text: str) -> str:
    """
    Standardize whitespace and clean transcription artifacts without altering technical terms,
    misconceptions, or candidate vocabulary. Never semantically rewrites or corrects candidate errors.
    """
    if not text:
        return ""
    # Collapse multiple whitespace characters while preserving verbatim words and casing
    return " ".join(text.strip().split())


def transcribe_and_align(audio_path: str) -> dict:
    if not _WHISPERX_AVAILABLE:
        return _fallback_energy_timing(audio_path)

    try:
        model, align_model, metadata = _get_models()

        try:
            audio = whisperx.load_audio(audio_path)
        except Exception:
            audio = decode_audio(audio_path, target_sr=16000)[0]
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
            if gap >= 0.2:
                pauses.append(
                    {
                        "start": round(float(previous_end), 3),
                        "end": round(float(current_start), 3),
                        "duration": round(float(gap), 3),
                    }
                )

        total_pause = sum(p["duration"] for p in pauses)
        total_duration = float(len(audio)) / 16000.0 if len(audio) > 0 else 0.0
        total_speech = max(0.0, total_duration - total_pause)

        transcript = normalize_transcript_text(" ".join(seg.get("text", "") for seg in result.get("segments", [])))
        word_count = len(words)
        speaking_rate = (word_count / (total_speech / 60.0)) if total_speech > 0 else 0.0

        scores = [w["score"] for w in words if w.get("score") is not None]
        confidence = float(np.mean(scores)) if scores else 0.0

        return {
            "transcript": transcript,
            "words": words,
            "pauses": pauses,
            "pause_count": len(pauses),
            "total_pause_time": round(float(total_pause), 3),
            "total_speech_time": round(float(total_speech), 3),
            "true_speaking_rate": round(float(speaking_rate), 2),
            "transcription_confidence": round(float(confidence), 3),
            "audio_duration": round(float(total_duration), 3),
            "alignment_source": "whisperx",
        }
    except Exception:
        return _fallback_energy_timing(audio_path)


def transcribe_audio(audio_path: str) -> tuple[str, float]:
    transcription = transcribe_and_align(audio_path)
    return transcription.get("transcript", ""), transcription.get("transcription_confidence", 0.0)