"""
PrepAIred — Unit Tests for Speech & Audio Analysis Pipeline (Stage 3)
====================================================================
Tests the authoritative speech-to-text pipeline, transcript normalization,
technical terminology fidelity, pause/timing extraction, and evaluation passing.
"""

import io
import math
import wave
import pytest
import numpy as np
from fastapi.testclient import TestClient

from agents.audio.transcriber import (
    normalize_transcript_text,
    transcribe_and_align,
    _fallback_energy_timing,
)
from agents.audio.audio_io import _read_wav_bytes, _pcm_to_float, frame_rms
from agents.audio.hesitation_scorer import score_hesitation
from agents.audio.confidence_scorer import score as audio_confidence_score
from agents.audio.nlp_analyzer import analyze_linguistic_confidence
from apps.backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _generate_synthetic_wav(duration_sec=2.0, sample_rate=16000, frequency=440.0, silence_gap=0.3) -> bytes:
    """Generate a valid WAV audio byte stream with a tone burst and silence gap."""
    total_samples = int(duration_sec * sample_rate)
    gap_samples = int(silence_gap * sample_rate)
    burst_samples = (total_samples - gap_samples) // 2

    # Segment 1: Tone
    t1 = np.linspace(0, burst_samples / sample_rate, burst_samples, endpoint=False)
    sig1 = 0.5 * np.sin(2 * np.pi * frequency * t1)

    # Segment 2: Silence
    sig_silence = np.zeros(gap_samples, dtype=np.float32)

    # Segment 3: Tone
    t2 = np.linspace(0, burst_samples / sample_rate, burst_samples, endpoint=False)
    sig2 = 0.5 * np.sin(2 * np.pi * frequency * t2)

    full_sig = np.concatenate([sig1, sig_silence, sig2]).astype(np.float32)
    pcm_data = (full_sig * 32767.0).astype(np.int16).tobytes()

    wav_buf = io.BytesIO()
    with wave.open(wav_buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    return wav_buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Normal Speech Transcript Normalization
# ─────────────────────────────────────────────────────────────────────────────
def test_normal_speech_normalization():
    """Whitespace and formatting must be standardized without altering words."""
    raw = "  In   a hash   table, keys    are mapped to indices.   "
    normalized = normalize_transcript_text(raw)
    assert normalized == "In a hash table, keys are mapped to indices."


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Technical Terminology & Case Preservation
# ─────────────────────────────────────────────────────────────────────────────
def test_technical_terminology_fidelity():
    """Technical terms, symbols, and C programming tokens must never be auto-corrected or rewritten."""
    raw = "malloc, free, struct Node*, O(n log n) time complexity, and pthread_mutex_lock"
    normalized = normalize_transcript_text(raw)
    assert "malloc" in normalized
    assert "struct Node*" in normalized
    assert "O(n log n)" in normalized
    assert "pthread_mutex_lock" in normalized


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Misconception Fidelity (No Auto-Correcting Candidate Errors)
# ─────────────────────────────────────────────────────────────────────────────
def test_misconception_text_preservation():
    """Candidate errors must NOT be rewritten into correct terms (e.g., 'stack' must not become 'heap')."""
    raw_error = "malloc allocates dynamic memory directly on the stack frame."
    normalized = normalize_transcript_text(raw_error)
    assert "stack frame" in normalized
    assert "heap" not in normalized


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Repeated Words and Stutter Preservation
# ─────────────────────────────────────────────────────────────────────────────
def test_repeated_words_preservation():
    """Repeated words and speech disfluencies must be preserved for hesitation analysis."""
    raw_repeated = "I I think we we should use a a linked list."
    normalized = normalize_transcript_text(raw_repeated)
    assert normalized == "I I think we we should use a a linked list."


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Filler Words Detection in Hesitation Scorer
# ─────────────────────────────────────────────────────────────────────────────
def test_filler_words_hesitation_scoring():
    """Hesitation scorer must detect filler density (um, uh, like, basically)."""
    transcription_fluent = {
        "transcript": "A binary search tree maintains sorted order where the left subtree is smaller.",
        "words": [{"word": w} for w in "A binary search tree maintains sorted order".split()],
        "pause_count": 0,
        "total_pause_time": 0.0,
        "total_speech_time": 3.0,
        "true_speaking_rate": 3.0,
    }
    transcription_hesitant = {
        "transcript": "Um like basically uh I guess you know sort of maybe",
        "words": [{"word": w} for w in "Um like basically uh I guess you know sort of maybe".split()],
        "pause_count": 4,
        "total_pause_time": 2.5,
        "total_speech_time": 2.0,
        "audio_duration": 4.5,
        "true_speaking_rate": 2.0,
        "pauses": [{"duration": 0.8}, {"duration": 1.7}],
    }
    hes_fluent = score_hesitation({}, transcription_fluent)
    hes_hesitant = score_hesitation({"jitter": 0.04}, transcription_hesitant)

    assert hes_hesitant["filler_density"] > hes_fluent["filler_density"]
    assert hes_hesitant["hesitation_score"] > hes_fluent["hesitation_score"]


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Acoustic Pause and Timing Extraction
# ─────────────────────────────────────────────────────────────────────────────
def test_acoustic_timing_and_pause_extraction(tmp_path):
    """Energy fallback timing must correctly detect duration and silence gaps in raw WAV."""
    wav_bytes = _generate_synthetic_wav(duration_sec=2.0, sample_rate=16000, silence_gap=0.4)
    audio_file = tmp_path / "test_timing.wav"
    audio_file.write_bytes(wav_bytes)

    timing = _fallback_energy_timing(str(audio_file))
    assert timing["audio_duration"] >= 1.8
    assert timing["pause_count"] >= 1
    assert timing["total_pause_time"] >= 0.2
    assert timing["total_speech_time"] > 0.5


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Authoritative API Endpoint (/api/transcribe) Raw Audio Processing
# ─────────────────────────────────────────────────────────────────────────────
def test_api_transcribe_authoritative_audio_flow(client):
    """POST /api/transcribe must process uploaded audio and return structured timing and transcript."""
    wav_bytes = _generate_synthetic_wav(duration_sec=1.5, sample_rate=16000, silence_gap=0.3)
    files = {"audio": ("candidate_speech.wav", io.BytesIO(wav_bytes), "audio/wav")}
    data = {
        "session_id": "test_audio_session_1",
        "transcript": "I will use a hash map for two sum.",
    }

    resp = client.post("/api/transcribe", files=files, data=data)
    assert resp.status_code == 200
    res = resp.json()

    assert "transcript" in res
    assert "browser_preview_transcript" in res
    assert res["browser_preview_transcript"] == "I will use a hash map for two sum."
    assert "audio_analysis" in res
    assert "total_speech_time" in res
    assert "total_pause_time" in res


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Audio Confidence Scoring Components
# ─────────────────────────────────────────────────────────────────────────────
def test_audio_confidence_scoring():
    """Confidence scoring combines prosody, fluency, speaking rate, and linguistic markers."""
    prosodic = {"jitter": 0.015, "shimmer": 0.05, "hnr": 20.0, "pitch_stddev": 35.0}
    transcription = {
        "transcript": "We will use a hash map because it gives O(1) average lookup time.",
        "words": [{"word": w} for w in "We will use a hash map because it gives O(1) average lookup time.".split()],
        "total_speech_time": 4.0,
        "total_pause_time": 0.4,
        "true_speaking_rate": 3.25,
        "transcription_confidence": 0.95,
        "pause_count": 1,
    }
    linguistic = analyze_linguistic_confidence(transcription["transcript"])
    conf_score = audio_confidence_score(prosodic, transcription, linguistic)

    assert 0.0 <= conf_score <= 1.0
    assert conf_score >= 0.65  # Clear assertive statement with fluent acoustics


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Evaluator Receives Exact Authoritative Transcript
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_orchestrator_receives_authoritative_transcript():
    """InterviewOrchestrator evaluate_verbal must process the exact server transcript passed to it."""
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    def _q(qid="q0", topic="arrays", diff=3, qtype="verbal"):
        return {
            "id": qid,
            "text": "Explain how Two Sum works.",
            "topic": topic,
            "difficulty": diff,
            "type": qtype,
            "expected_concepts": ["Hash map lookup", "Complement target - current"],
        }

    received_transcripts = []

    def mock_evaluator(transcript, question):
        received_transcripts.append(transcript)
        return {
            "final_score": 0.85,
            "grade": "Excellent",
            "correct_claims": ["Hash map lookup"],
            "missing_concepts": [],
            "incorrect_claims": [],
            "decision_source": "mock_test",
        }

    orch = InterviewOrchestrator(
        "test_eval_transcript_flow",
        {"id": "c1", "experience": "intermediate"},
        {"num_questions": 3, "interview_mode": "standard"},
        evaluator_fn=mock_evaluator,
    )
    orch._question_queue = [_q("q0")]
    orch._state["questions"] = list(orch._question_queue)
    await orch.start()

    authoritative_text = "I iterate through the array and store complement in a hash table."
    res = await orch.handle_voice_answer(authoritative_text, "q0")

    assert len(received_transcripts) == 1
    assert received_transcripts[0] == authoritative_text
    assert orch._state["answers"][0]["transcript"] == authoritative_text


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Browser Preview Never Promoted to Authoritative Transcript
# ─────────────────────────────────────────────────────────────────────────────
def test_browser_preview_never_promoted_to_authoritative_transcript(client):
    """When server STT cannot transcribe audio, browser preview must NOT become authoritative transcript."""
    # Send empty/silent audio buffer
    silent_wav = _generate_synthetic_wav(duration_sec=0.5, silence_gap=0.5)
    files = {"audio": ("silent.wav", io.BytesIO(silent_wav), "audio/wav")}
    data = {
        "session_id": "test_no_promote_session",
        "transcript": "Browser transcribed this text.",
    }

    resp = client.post("/api/transcribe", files=files, data=data)
    assert resp.status_code == 200
    res = resp.json()

    # Browser preview is stored strictly for UI preview
    assert res["browser_preview_transcript"] == "Browser transcribed this text."
    # Authoritative transcript remains strictly server-generated or explicit failure
    assert res["transcript_source"] != "browser_fallback"
    if not res["transcript"]:
        assert res["stt_status"] == "stt_unavailable"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 11: Structured STT Failure State in Orchestrator
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_stt_failure_produces_structured_failure_state():
    """When STT fails or produces empty transcript, orchestrator must NOT fabricate an evaluation score."""
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    def _make_q(qid="q0"):
        return {
            "id": qid,
            "text": "Explain hash table collisions.",
            "topic": "hash_tables",
            "difficulty": 3,
            "type": "verbal",
            "expected_concepts": ["Chaining", "Open addressing"],
        }

    orch = InterviewOrchestrator(
        "test_stt_failure",
        {"id": "c1", "experience": "intermediate"},
        {"num_questions": 3, "interview_mode": "standard"},
    )
    orch._question_queue = [_make_q("q0")]
    orch._state["questions"] = list(orch._question_queue)
    await orch.start()


    # Submit failed / empty STT transcript
    res = await orch.handle_voice_answer("[STT error: decoding failed]", "q0")
    fb = res["feedback"]

    assert fb.get("stt_status") == "stt_unavailable"
    assert fb.get("final_score") == 0.0
    assert fb.get("grade") == "Ungraded"
    assert "No authoritative server transcript" in fb.get("justification", "")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 12: WhisperX Dependency-Gated Execution
# ─────────────────────────────────────────────────────────────────────────────
def test_whisperx_dependency_gated_execution():
    """Gated test that verifies WhisperX runtime when installed."""
    whisperx = pytest.importorskip("whisperx")
    assert whisperx is not None
