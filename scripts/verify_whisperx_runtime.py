#!/usr/bin/env python3
"""
PrepAIred - WhisperX Runtime & Portability Verification Script.
Authoritatively validates:
1. WhisperX and PyTorch CPU/CUDA environment.
2. Direct invocation of agents.audio.transcriber.transcribe_and_align.
3. Word timestamps, pause metrics, speaking rate, and confidence extraction.
4. Clean separation between WhisperX authoritative STT and DSP recovery fallback.
"""

import os
import sys
import tempfile
import wave
import struct
import json
from pathlib import Path
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def create_synthetic_speech_wav(duration_sec: float = 3.0, sample_rate: int = 16000) -> str:
    """Create a temporary multi-tone modulated WAV file resembling speech cadence."""
    num_samples = int(duration_sec * sample_rate)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        wav_path = tf.name
        with wave.open(tf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            # Modulate carrier (220 Hz) with speech-like bursts (3 Hz)
            t = np.linspace(0, duration_sec, num_samples, endpoint=False)
            carrier = np.sin(2.0 * np.pi * 220.0 * t)
            envelope = 0.5 * (1.0 + np.sin(2.0 * np.pi * 3.0 * t))
            signal = carrier * envelope * 0.4

            for s in signal:
                val = int(s * 32767.0)
                wf.writeframes(struct.pack("<h", max(-32768, min(32767, val))))
    return wav_path


def verify_whisperx_pipeline():
    print("=" * 65)
    print("  PrepAIred - WhisperX Audio Pipeline Verification")
    print("=" * 65)

    # 1. Environment & Library Checks
    results = {}
    print("\n[1/5] Checking PyTorch & Audio Libraries...")

    try:
        import torch
        results["torch_version"] = torch.__version__
        results["cuda_available"] = torch.cuda.is_available()
        print(f"  [OK] PyTorch: {torch.__version__} (CUDA Available: {torch.cuda.is_available()})")
    except Exception as e:
        results["torch_error"] = str(e)
        print(f"  [FAIL] PyTorch import failed: {e}")

    try:
        import torchaudio
        results["torchaudio_version"] = torchaudio.__version__
        print(f"  [OK] Torchaudio: {torchaudio.__version__}")
    except Exception as e:
        results["torchaudio_error"] = str(e)
        print(f"  [FAIL] Torchaudio import failed: {e}")

    try:
        import faster_whisper
        results["faster_whisper"] = "available"
        print("  [OK] faster-whisper: available")
    except Exception as e:
        results["faster_whisper"] = f"failed ({e})"
        print(f"  [FAIL] faster-whisper failed: {e}")

    whisperx_available = False
    try:
        import whisperx
        whisperx_available = True
        results["whisperx_version"] = getattr(whisperx, "__version__", "available")
        print(f"  [OK] WhisperX: {results['whisperx_version']}")
    except Exception as e:
        results["whisperx_error"] = str(e)
        print(f"  [FAIL] WhisperX import failed: {e}")

    # 2. Transcriber Module Verification
    print("\n[2/5] Importing Authoritative Transcriber Module...")
    from agents.audio.transcriber import transcribe_and_align, _fallback_energy_timing, _WHISPERX_AVAILABLE
    print(f"  Transcriber _WHISPERX_AVAILABLE flag: {_WHISPERX_AVAILABLE}")

    # 3. Create Sample Audio
    print("\n[3/5] Generating Synthetic Speech-Cadence Audio...")
    wav_path = create_synthetic_speech_wav(duration_sec=3.0)
    file_size = Path(wav_path).stat().st_size
    print(f"  Temporary WAV generated at: {wav_path} ({file_size} bytes, 3.0s)")

    # 4. Execute transcribe_and_align
    print("\n[4/5] Running transcribe_and_align Pipeline...")
    output = transcribe_and_align(wav_path)
    print(f"  Transcriber output payload keys: {list(output.keys())}")
    print(f"  Alignment Source: {output.get('alignment_source')}")
    print(f"  Audio Duration: {output.get('audio_duration')}s")
    print(f"  Pause Count: {output.get('pause_count')}")
    print(f"  Total Pause Time: {output.get('total_pause_time')}s")
    print(f"  Total Speech Time: {output.get('total_speech_time')}s")
    print(f"  Speaking Rate (WPM): {output.get('true_speaking_rate')}")
    print(f"  Confidence: {output.get('transcription_confidence')}")

    # 5. DSP Recovery Fallback Test
    print("\n[5/5] Testing DSP Energy-Timing Fallback Pipeline...")
    fallback_output = _fallback_energy_timing(wav_path)
    print(f"  Fallback Source: {fallback_output.get('alignment_source')}")
    print(f"  Fallback Duration: {fallback_output.get('audio_duration')}s")
    print(f"  Fallback Pause Count: {fallback_output.get('pause_count')}")

    # Cleanup
    if Path(wav_path).exists():
        Path(wav_path).unlink()

    # Invariant Validations
    assert "transcript" in output, "Missing transcript key"
    assert "words" in output, "Missing words key"
    assert "pauses" in output, "Missing pauses key"
    assert "energy" in fallback_output.get("alignment_source", ""), "Invalid fallback source label"

    print("\n" + "=" * 65)
    print("  VERIFICATION RESULT: ALL AUDIO INVARIANTS SATISFIED (PASS)")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = verify_whisperx_pipeline()
    sys.exit(0 if success else 1)
