# Speech Feature Missingness & Isolation Audit Report

**Audit Target:** Speech Prosody Acoustic Extraction, Fallback Defaults, and Scoring Isolation  
**Audited Source Files:**
- `agents/audio/confidence_scorer.py`
- `agents/audio/hesitation_scorer.py`
- `agents/audio/main.py`
- `agents/orchestrator/interview_orchestrator.py`
- `services/evaluator/app.py`  
**Audited Checkpoint Commit:** `1b11c1ab48d774a5d2db34df50834b07e0fd0810`  
**Audit Date:** September 19, 2026  
**Status:** **AUDITED & ZERO-INFLUENCE INVARIANT CONFIRMED**

---

## 1. Executive Summary & Core Research Invariant

### Core Scientific Invariant:
> **Zero Influence on Technical Correctness:** Speech features (confidence, pitch jitter, shimmer, harmonics-to-noise ratio, speaking rate, acoustic pause duration, and hesitation) are **strictly isolated from technical answer evaluation**.

- `services/evaluator/app.py:evaluate(qn, candidate, rubric)` operates exclusively on textual candidate transcripts and reference rubrics ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$).
- Speech features are ingested exclusively by:
  1. The 6D RL candidate state representation (Dimension 2: confidence $\in [0, 1]$, Dimension 3: hesitation $\in [0, 1]$).
  2. The anxiety-protective heuristic guardrail (Guardrail G2: if high technical performance is paired with high hesitation, the system prevents difficulty jumps to avoid penalizing anxious candidates).
- Therefore, **speech availability never alters technical correctness or candidate grades**.

---

## 2. Speech Failure vs. Genuine Neutrality Audit

### Current System Behavior:
When an audio extraction fails (corrupted WAV, missing microphone input, librosa/Praat Parselmouth failure, or text-only attempt):
```python
# agents/orchestrator/interview_orchestrator.py
"last_confidence_score": 0.50
"confidence_score": float(audio.get("confidence_score", 0.50))
```
- **The Ambiguity:** Currently, `confidence = 0.50` is returned both when:
  - An audio failure/timeout occurs (default neutral fallback = 0.50).
  - A candidate speaks with genuine, measured neutral confidence (acoustic score = 0.50).
- **Current Distinguishability:** The numeric vector $[0.50]$ does NOT carry a boolean availability flag. A consumer inspecting only `rl_observation[2]` cannot distinguish between missing audio and genuine neutral delivery.

---

## 3. Missingness Indicator Architectural Specification

To provide clear observability and downstream transparency without altering RL observation shapes, the following typed missingness specification is established:

### Proposed Schema:
```python
from dataclasses import dataclass

@dataclass
class AudioAnalysisResult:
    speech_available: bool
    confidence_score: float        # Imputed to 0.50 if speech_available is False
    hesitation_score: float         # Imputed to 0.00 if speech_available is False
    missing_reason: Optional[str]  # e.g., "microphone_disabled", "parselmouth_failed", "text_submission"
```

### Downstream Invariants Under Missing Audio (`speech_available = False`):
1. **Evaluator:** Evaluates textual transcript unchanged ($S_1, S_2, R$ unaffected).
2. **RL Controller:** Uses imputed neutral values $[0.50, 0.00]$ for Dimensions 2 and 3; does NOT activate anxiety penalty or bonus.
3. **Database:** Persists `answer_type = 'text'` or logs `audio_status = 'unavailable'`.
4. **Candidate Analytics:** UI reports display *"Speech Analysis: Not Available"* rather than misleadingly reporting *"Candidate Confidence: 50%"*.
