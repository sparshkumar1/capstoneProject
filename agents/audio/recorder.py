import os
import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
RECORDINGS_DIR = "recordings"

def _apply_noise_gate(audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
    return np.where(np.abs(audio) < threshold, 0.0, audio)

def _normalize_loudness(audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
    rms = np.sqrt(np.mean(audio ** 2))
    if rms == 0:
        return audio
    target_rms = 10 ** (target_db / 20)
    return audio * (target_rms / rms)

def record_audio(duration: int = 10, filename: str = "processed_audio.wav") -> str:
    os.makedirs(RECORDINGS_DIR, exist_ok=True)

    raw_path       = os.path.join(RECORDINGS_DIR, "raw_audio.wav")
    processed_path = os.path.join(RECORDINGS_DIR, filename)

    print(f"[Recorder] Recording {duration}s at {SAMPLE_RATE}Hz...")
    audio = sd.rec(int(duration * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=1,
                   dtype="float32")
    sd.wait()
    audio = audio.flatten()

    sf.write(raw_path, audio, SAMPLE_RATE)
    print(f"[Recorder] Raw audio saved to {raw_path}")

    cleaned = _apply_noise_gate(audio)
    cleaned = _normalize_loudness(cleaned)

    sf.write(processed_path, cleaned, SAMPLE_RATE)
    print(f"[Recorder] Processed audio saved to {processed_path}")
    return processed_path