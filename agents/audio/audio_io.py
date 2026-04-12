from __future__ import annotations

import io
import subprocess
import wave
from pathlib import Path

import numpy as np

try:
    from imageio_ffmpeg import get_ffmpeg_exe

    _FFMPEG_EXE = get_ffmpeg_exe()
except Exception:
    _FFMPEG_EXE = None


def _pcm_to_float(buffer: bytes, sample_width: int) -> np.ndarray:
    if not buffer:
        return np.zeros(0, dtype=np.float32)

    if sample_width == 1:
        data = np.frombuffer(buffer, dtype=np.uint8).astype(np.float32)
        return (data - 128.0) / 128.0
    if sample_width == 2:
        data = np.frombuffer(buffer, dtype="<i2").astype(np.float32)
        return data / 32768.0
    if sample_width == 4:
        data = np.frombuffer(buffer, dtype="<i4").astype(np.float32)
        return data / 2147483648.0

    return np.zeros(0, dtype=np.float32)


def _read_wav_bytes(wav_bytes: bytes) -> tuple[np.ndarray, int]:
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_count = wav_file.getnframes()
        buffer = wav_file.readframes(frame_count)

    samples = _pcm_to_float(buffer, sample_width)
    if samples.size == 0:
        return np.zeros(0, dtype=np.float32), sample_rate

    if channels > 1:
        usable = (samples.size // channels) * channels
        if usable == 0:
            return np.zeros(0, dtype=np.float32), sample_rate
        samples = samples[:usable].reshape(-1, channels).mean(axis=1)

    return samples.astype(np.float32, copy=False), sample_rate


def decode_audio(audio_path: str | Path, target_sr: int = 16000) -> tuple[np.ndarray, int, str]:
    path = Path(audio_path)
    if not path.exists():
        return np.zeros(0, dtype=np.float32), target_sr, "missing"

    if _FFMPEG_EXE:
        try:
            command = [
                _FFMPEG_EXE,
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(path),
                "-ac",
                "1",
                "-ar",
                str(target_sr),
                "-f",
                "wav",
                "pipe:1",
            ]
            completed = subprocess.run(command, capture_output=True, check=True)
            samples, sample_rate = _read_wav_bytes(completed.stdout)
            if samples.size > 0:
                return samples, sample_rate, "ffmpeg"
        except Exception:
            pass

    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                buffer = wav_file.readframes(wav_file.getnframes())
            samples = _pcm_to_float(buffer, sample_width)
            if channels > 1 and samples.size > 0:
                usable = (samples.size // channels) * channels
                samples = samples[:usable].reshape(-1, channels).mean(axis=1)
            return samples.astype(np.float32, copy=False), sample_rate, "wav"
        except Exception:
            pass

    return np.zeros(0, dtype=np.float32), target_sr, "unavailable"


def frame_rms(samples: np.ndarray, frame_length: int = 1024, hop_length: int = 256) -> np.ndarray:
    data = np.asarray(samples, dtype=np.float32)
    if data.size == 0:
        return np.zeros(0, dtype=np.float32)

    frame_length = max(int(frame_length), 1)
    hop_length = max(int(hop_length), 1)
    if data.size < frame_length:
        return np.array([float(np.sqrt(np.mean(data ** 2)))], dtype=np.float32)

    values = []
    for start in range(0, data.size - frame_length + 1, hop_length):
        frame = data[start:start + frame_length]
        values.append(float(np.sqrt(np.mean(frame ** 2))))

    return np.asarray(values, dtype=np.float32)