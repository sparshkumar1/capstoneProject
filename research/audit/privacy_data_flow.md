# Candidate Privacy, Acoustic Data Flow, and Lifecycle Audit

**Audited Git Commit:** `9cfd34f`  
**Compliance Context:** FERPA, GDPR, and AI Ethics Standards for Educational Assessment

---

## 1. Data Classification & Sensitivity

| Data Artifact | Classification | Storage Location | Retention / Lifecycle | Exposure Risk |
|:---|:---|:---|:---|:---|
| **Microphone Raw Audio (.wav)** | Highly Sensitive Biometric | Ephemeral In-Memory Buffer | Discarded immediately after STT and prosody feature extraction (0 disk persistence) | Low (Zero at-rest footprint) |
| **Acoustic Prosody Features** | Sensitive Metadata | SQLite `sessions` table | Retained per session (`hesitation`, `confidence`) for RL pacing | Low (Abstract floating-point vectors) |
| **Verbal Transcripts & Text Answers** | Educational Record | SQLite `candidate_attempts` | Persisted with candidate ID for longitudinal learning gap analysis | Moderate (Restricted access via WAL) |
| **Submitted C Source Code** | Educational Record | SQLite `candidate_attempts` | Persisted with compile/runtime verdicts | Low |
| **Rubrics & System Evaluator Signals** | Proprietary Intellectual Property | Evaluator assets (`logic_vectors.faiss`) | Static server-side assets (read-only) | Nil (Never transmitted to client) |

---

## 2. Acoustic Processing Data Flow

```
[Candidate Microphone]
         ¦
         ?
[Browser Web Audio API] -- (Captures audio stream; WebM/PCM chunks)
         ¦ (POST /api/interview/answer)
         ?
[Orchestrator Memory] --- (Temporary buffer in RAM; max 60s window)
         +--? [Whisper / STT Engine] --------? [Text Transcript]
         +--? [Acoustic Feature Extractor] --? [Hesitation, Pitch, Signal RMS]
                   ¦
                   ? (Raw audio destroyed from RAM)
            [6D State RL Input] 
```

---

## 3. Privacy Safeguards & Invariants

1. **Ephemeral Audio Lifespan:** Raw audio waveforms are never written to permanent disk storage, object stores, or persistent databases. Audio arrays exist only in heap memory during the inference turn and are garbage-collected immediately.
2. **Local Processing Independence:** STT transcription and prosody feature extraction are executed locally without transmitting candidate voice streams to third-party commercial APIs (e.g. OpenAI Whisper API or Google Speech).
3. **Strict Decoupling of Voice from Technical Score:** Acoustic features are strictly segregated from the scoring engine. A candidate with severe acoustic hesitation, stuttering, or an unfamiliar accent receives the exact same technical score as a fluent speaker giving identical text explanations.
4. **Candidate-Facing Score Masking:** Numerical sub-scores ($S_1, S_2, R$) are masked from candidate UI to avoid inducing evaluation anxiety; candidates receive constructive qualitative guidance with missing concept milestones.
