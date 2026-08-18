# PrepAIred — Speech Processing & Audio Prosody Pipeline

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Speech Pipeline Architecture

The PrepAIred speech pipeline converts candidate verbal responses into authoritative text transcripts while extracting **acoustic prosody indicators** (speaking rate, pause patterns, filler words) that feed candidate state and the RL observation vector:

```
Audio Recording (.webm / .wav)
  │
  ├──► 1. Audio Preprocessing & Format Normalization (16kHz mono WAV)
  │
  ├──► 2. WhisperX Speech-to-Text Transcription + Forced Alignment
  │      └─ Word-level timestamp extraction [t_start, t_end]
  │
  ├──► 3. Acoustic Prosody Feature Extraction
  │      ├─ Speaking Rate (Words Per Minute — WPM)
  │      ├─ Pause Detection (Silence gaps > 0.45s)
  │      └─ Filler Word Count ("umm", "uhh", "like", "you know")
  │
  └──► 4. Behavioral Score Calculation
         ├─ Confidence Score ∈ [0.0, 1.0]
         └─ Hesitation Score ∈ [0.0, 1.0]
```

---

## 2. WhisperX Model Configuration & Execution

- **Model Engine:** `faster-whisper` / `whisperx`
- **Default Model Size:** `base` (or `small` / `medium.en`)
- **Device Support:**
  - `CUDA`: Fast batched inference with FP16/INT8 compute.
  - `CPU`: Supported via `int8` quantization without GPU dependencies.
- **Forced Alignment:** Uses phoneme-level acoustic wav2vec2 models to generate precise start/end boundaries for every spoken word.

---

## 3. Acoustic Metrics Derivation

### 3.1 Speaking Rate (WPM)
$$\text{WPM} = \frac{\text{Total Spoken Words}}{\text{Active Speech Duration in Minutes}}$$
*Nominal conversational pacing in technical interviews is $130 \text{--} 160\text{ WPM}$.*

### 3.2 Pause Rate & Duration
A pause is detected when the inter-word silence gap satisfies:
$$\Delta t_{\text{gap}} = t_{\text{start}}(w_{i+1}) - t_{\text{end}}(w_i) \ge 0.45\text{ seconds}$$
$$\text{Pause Rate} = \frac{\text{Total Detected Pauses}}{\text{Total Duration (Minutes)}}$$

### 3.3 Hesitation Score ($S_{\text{hes}} \in [0.0, 1.0]$)
$$S_{\text{hes}} = \text{clip}\left(0.40 \times \frac{\text{Filler Count}}{\text{Total Words}} + 0.60 \times \frac{\text{Total Pause Time}}{\text{Total Duration}},\ 0.0,\ 1.0\right)$$

### 3.4 Acoustic Confidence Score ($S_{\text{conf}} \in [0.0, 1.0]$)
$$S_{\text{conf}} = 1.0 - S_{\text{hes}}$$

---

## 4. API Endpoints & Failure Modes

- **REST Endpoint:** `POST /api/transcribe`
  - Accepts multipart audio payload (`audio/webm` or `audio/wav`).
  - Returns `{"transcript": str, "speaking_rate": float, "pause_count": int, "total_pause_time": float, "confidence_score": float, "hesitation_score": float}`.
- **Microservice Unavailability Fallback:**
  - If the WhisperX service is unreachable, the system gracefully processes raw text inputs or browser-delivered previews with explicit status:
  - `decision_source = "speech_pipeline_text_fallback"`
  - Preserves evaluator scoring without fabricating prosody metrics.

---

## 5. Empirical Claims Status

| Speech Pipeline Claim | Status | Repository Evidence |
|---|---|---|
| WhisperX transcription with word-level timestamps | **`TESTED`** | Implemented in `agents/audio/`; verified via `test_speech_pipeline.py` |
| Accurate speaking rate (WPM) and pause extraction | **`TESTED`** | `test_speech_pipeline.py` |
| Hesitation/confidence derivation for RL observation | **`TESTED`** | `test_speech_pipeline.py`, `test_stage11_5_coding_adaptation.py` |
| Prosody metrics correlate with human psychological anxiety | **`NOT YET VALIDATED`** | Requires clinical human validation trial |
