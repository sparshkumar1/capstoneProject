from __future__ import annotations

import numpy as np

try:
    import parselmouth
    from parselmouth.praat import call

    _PARSELMOUTH_AVAILABLE = True
except ImportError:
    parselmouth = None
    call = None
    _PARSELMOUTH_AVAILABLE = False

try:
    from .audio_io import decode_audio, frame_rms
except ImportError:
    from audio_io import decode_audio, frame_rms


def _safe_float(value, default=0.0):
    """Coerce a value to float, falling back on None/NaN/conversion errors.

    Args:
        value: Value to convert.
        default (float): Value to return if `value` is None, NaN, or not
            convertible (default 0.0).

    Returns:
        float: The converted value, or `default`.
    """
    try:
        if value is None:
            return default
        if isinstance(value, float) and np.isnan(value):
            return default
        return float(value)
    except Exception:
        return default


def _robust_mean(values, default=0.0):
    """Compute a mean that trims non-finite values and (for n>=8) outlier tails.

    Args:
        values: Array-like of numeric values.
        default (float): Value to return if no finite values remain
            (default 0.0).

    Returns:
        float: Mean of the finite, (optionally trimmed to the 10th-90th
            percentile) values, or `default` if none remain.
    """
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return float(default)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float(default)
    if arr.size >= 8:
        low, high = np.quantile(arr, [0.1, 0.9])
        trimmed = arr[(arr >= low) & (arr <= high)]
        if trimmed.size > 0:
            arr = trimmed
    return float(np.mean(arr))


def _robust_std(values, default=0.0):
    """Compute a standard deviation that trims non-finite values and (for n>=8) outlier tails.

    Args:
        values: Array-like of numeric values.
        default (float): Value to return if no finite values remain
            (default 0.0).

    Returns:
        float: Standard deviation of the finite, (optionally trimmed)
            values, or `default` if none remain.
    """
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return float(default)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float(default)
    if arr.size >= 8:
        low, high = np.quantile(arr, [0.1, 0.9])
        trimmed = arr[(arr >= low) & (arr <= high)]
        if trimmed.size > 0:
            arr = trimmed
    return float(np.std(arr))


def _spectral_flatness(samples: np.ndarray) -> float:
    """Compute the Wiener spectral flatness (geometric/arithmetic mean of the power spectrum).

    Used as a fallback proxy for voice quality (harmonics-to-noise ratio)
    when parselmouth/Praat isn't available: a tonal (harmonic) voice has low
    flatness, while a noisy signal has flatness closer to 1.

    Args:
        samples (np.ndarray): Mono audio samples for one frame/clip.

    Returns:
        float: Spectral flatness in (0, 1], or 1.0 for empty/silent input.
    """
    data = np.asarray(samples, dtype=np.float32)
    if data.size == 0:
        return 1.0
    window = np.hanning(data.size) if data.size > 1 else np.ones(1, dtype=np.float32)
    spectrum = np.abs(np.fft.rfft(data * window)) ** 2
    spectrum = spectrum[spectrum > 0]
    if spectrum.size == 0:
        return 1.0
    return float(np.exp(np.mean(np.log(spectrum))) / np.mean(spectrum))


def _estimate_pitch_track(samples: np.ndarray, sr: int) -> np.ndarray:
    """Estimate a frame-by-frame pitch (F0) track via autocorrelation.

    Fallback pitch estimator used when parselmouth/Praat isn't available.
    Skips low-energy (silent) frames and frames whose best autocorrelation
    peak isn't clearly periodic.

    Args:
        samples (np.ndarray): Mono audio samples.
        sr (int): Sample rate in Hz.

    Returns:
        np.ndarray: Estimated pitch in Hz for each voiced frame detected
            (searched over roughly 75-500 Hz); empty if `samples`/`sr` are
            invalid or no voiced frames are found.
    """
    data = np.asarray(samples, dtype=np.float32)
    if data.size == 0 or sr <= 0:
        return np.zeros(0, dtype=np.float32)

    frame_length = max(int(sr * 0.04), 256)
    hop_length = max(int(sr * 0.01), 64)
    min_lag = max(1, int(sr / 500.0))
    max_lag = max(min_lag + 1, int(sr / 75.0))
    pitches = []

    for start in range(0, max(1, data.size - frame_length + 1), hop_length):
        frame = data[start:start + frame_length]
        if frame.size < frame_length:
            break
        frame = frame - float(np.mean(frame))
        energy = float(np.sqrt(np.mean(frame ** 2)))
        if energy < 1e-3:
            continue

        windowed = frame * np.hanning(frame.size)
        autocorr = np.correlate(windowed, windowed, mode="full")[frame.size - 1:]
        if autocorr.size <= max_lag:
            continue
        region = autocorr[min_lag:max_lag]
        if region.size == 0:
            continue
        peak_index = int(np.argmax(region)) + min_lag
        peak_value = float(autocorr[peak_index])
        if peak_value <= 0 or autocorr[0] <= 0:
            continue
        if peak_value / float(autocorr[0]) < 0.2:
            continue
        pitches.append(float(sr / peak_index))

    return np.asarray(pitches, dtype=np.float32)


def extract_prosodic_features(audio_path):
    """Extract prosodic/voice-quality features from an audio recording.

    Uses parselmouth (Praat) for jitter, shimmer, HNR, and pitch when it's
    installed; otherwise falls back to the numpy/ffmpeg-based estimators in
    this module (`_estimate_pitch_track`, `_spectral_flatness`, etc.). All
    outputs are clamped to plausible physical ranges.

    Args:
        audio_path (str | Path): Path to the audio recording.

    Returns:
        dict: `jitter`, `shimmer`, `hnr`, `pitch_mean`, `pitch_stddev`,
            `signal_rms` (all floats), and `voice_quality_source`
            ("parselmouth", "ffmpeg_numpy_fallback", or the decode-failure
            reason from `decode_audio` if the file couldn't be read).
    """
    if _PARSELMOUTH_AVAILABLE:
        snd = parselmouth.Sound(audio_path)

        point_process = call(snd, "To PointProcess (periodic, cc)", 75, 500)
        jitter = _safe_float(call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3))
        shimmer = _safe_float(call([snd, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6))

        harmonicity = call(snd, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
        hnr = _safe_float(call(harmonicity, "Get mean", 0, 0))

        pitch = call(snd, "To Pitch", 0, 75, 500)
        pitch_mean = _safe_float(call(pitch, "Get mean", 0, 0, "Hertz"))
        pitch_stddev = _safe_float(call(pitch, "Get standard deviation", 0, 0, "Hertz"))
        signal_rms = _safe_float(np.sqrt(np.mean(np.asarray(snd.values) ** 2)), default=0.0)
    else:
        y, sr, decode_source = decode_audio(audio_path)
        if y.size == 0:
            return {
                "jitter": 0.02,
                "shimmer": 0.05,
                "hnr": 0.0,
                "pitch_mean": 0.0,
                "pitch_stddev": 0.0,
                "signal_rms": 0.0,
                "voice_quality_source": decode_source,
            }

        rms = frame_rms(y, frame_length=max(int(sr * 0.04), 256), hop_length=max(int(sr * 0.01), 64))
        if rms.size == 0:
            rms = np.array([float(np.sqrt(np.mean(y ** 2)))], dtype=np.float32)

        threshold = max(float(np.percentile(rms, 30) * 1.15), 1e-6)
        voiced_mask = rms > threshold
        voiced_rms = rms[voiced_mask] if np.any(voiced_mask) else rms

        pitch_track = _estimate_pitch_track(y, sr)
        pitch_mean = _safe_float(_robust_mean(pitch_track, default=0.0))
        pitch_stddev = _safe_float(_robust_std(pitch_track, default=0.0))

        if pitch_track.size > 2:
            periods = 1.0 / (pitch_track + 1e-9)
            local_jitter = np.abs(np.diff(periods)) / (np.abs(periods[:-1]) + 1e-9)
            jitter = _safe_float(_robust_mean(local_jitter, default=0.02))
        else:
            jitter = 0.02

        if voiced_rms.size > 2:
            local_shimmer = np.abs(np.diff(voiced_rms)) / (np.abs(voiced_rms[:-1]) + 1e-9)
            shimmer = _safe_float(_robust_mean(local_shimmer, default=0.05))
        else:
            shimmer = 0.05

        flatness = _spectral_flatness(y)
        hnr = _safe_float(max(0.0, min(30.0, 28.0 - flatness * 95.0)))
        signal_rms = _safe_float(_robust_mean(rms, default=0.0))

    jitter = float(np.clip(jitter, 0.0, 0.2))
    shimmer = float(np.clip(shimmer, 0.0, 0.4))
    hnr = float(np.clip(hnr, 0.0, 40.0))
    pitch_mean = float(np.clip(pitch_mean, 0.0, 600.0))
    pitch_stddev = float(np.clip(pitch_stddev, 0.0, 300.0))

    return {
        "jitter": round(jitter, 6),
        "shimmer": round(shimmer, 6),
        "hnr": round(hnr, 4),
        "pitch_mean": round(pitch_mean, 2),
        "pitch_stddev": round(pitch_stddev, 2),
        "signal_rms": round(signal_rms, 6),
        "voice_quality_source": "parselmouth" if _PARSELMOUTH_AVAILABLE else "ffmpeg_numpy_fallback",
    }


def extract_audio_features(audio_path):
    """Alias for `extract_prosodic_features`.

    Args:
        audio_path (str | Path): Path to the audio recording.

    Returns:
        dict: Same as `extract_prosodic_features`.
    """
    return extract_prosodic_features(audio_path)