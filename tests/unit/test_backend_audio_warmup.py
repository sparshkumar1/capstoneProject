"""
Regression tests for backend start-up / audio-stack initialisation (apps/backend/main.py).

Covers: explicit init state machine, single initialisation under concurrency, failure and timeout
handling, session creation independence from audio init, and the event loop staying responsive
while a request waits for audio. Mock-based tests prove control flow only; the final test runs the
real STT/prosody pipeline on a fixture recording and is skipped when whisperx is not installed.
"""
from __future__ import annotations

import asyncio
import importlib.util
import io
import sys
import threading
import time
import wave
from pathlib import Path

import httpx
import pytest

import apps.backend.main as m

FIXTURE_WAV = Path(__file__).resolve().parent.parent / "test_candidate_hash_table_answer.wav"

_AUDIO_GLOBALS = [
    "extract_prosodic_features", "audio_confidence_score", "audio_score_breakdown",
    "analyze_linguistic_confidence", "transcribe_and_align", "score_hesitation",
    "build_state_vector", "reset_audio_session",
]


@pytest.fixture
def audio_state(monkeypatch):
    """Reset the audio state machine to 'pending' and restore every global afterwards."""
    for name in _AUDIO_GLOBALS:
        monkeypatch.setattr(m, name, getattr(m, name))
    monkeypatch.setattr(m, "AUDIO_ANALYSIS_READY", False)
    monkeypatch.setattr(m, "_AUDIO_STATE", "pending")
    monkeypatch.setattr(m, "_AUDIO_ERROR", None)
    monkeypatch.setattr(m, "_AUDIO_DONE", threading.Event())
    monkeypatch.setattr(m, "AUDIO_WAIT_TIMEOUT_S", 5.0)
    monkeypatch.setattr(m, "LOGGING_READY", False)  # no legacy STT fallback in these tests
    return m


def _fake_import(monkeypatch, calls, *, delay=0.3, fail=False):
    def fake():
        calls.append(time.perf_counter())
        time.sleep(delay)
        if fail:
            monkeypatch.setattr(m, "_AUDIO_STATE", "failed")
            monkeypatch.setattr(m, "_AUDIO_ERROR", "ImportError: boom")
        else:
            monkeypatch.setattr(m, "AUDIO_ANALYSIS_READY", True)
            monkeypatch.setattr(m, "_AUDIO_STATE", "ready")
        m._AUDIO_DONE.set()
        return not fail
    monkeypatch.setattr(m, "_import_audio_analysis", fake)


def _wav_bytes(seconds=0.5, rate=16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x00" * int(seconds * rate))
    return buf.getvalue()


def _client():
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=m.app), base_url="http://test", timeout=60)


# ── state machine ─────────────────────────────────────────────────────

def test_concurrent_requests_initialise_audio_once(audio_state, monkeypatch):
    calls: list = []
    _fake_import(monkeypatch, calls)
    results: list = []
    threads = [threading.Thread(target=lambda: results.append(m._ensure_audio_analysis_imports())) for _ in range(8)]
    [t.start() for t in threads]
    [t.join(10) for t in threads]
    assert len(calls) == 1, "audio stack initialised more than once"
    assert results == [True] * 8
    assert m.audio_status()["state"] == "ready"


def test_failed_init_releases_waiters_and_is_not_ready(audio_state, monkeypatch):
    calls: list = []
    _fake_import(monkeypatch, calls, fail=True)
    results: list = []
    threads = [threading.Thread(target=lambda: results.append(m._ensure_audio_analysis_imports())) for _ in range(4)]
    started = time.perf_counter()
    [t.start() for t in threads]
    [t.join(10) for t in threads]
    assert results == [False] * 4
    assert time.perf_counter() - started < 3
    assert len(calls) == 1
    assert m.audio_status()["state"] == "failed" and m.audio_status()["ready"] is False
    assert m._ensure_audio_analysis_imports() is False and len(calls) == 1  # failure is sticky, no re-import storm


def test_real_import_failure_is_recorded_and_logged(audio_state, monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "agents.audio.audio_features", None)  # makes the import raise
    with caplog.at_level("ERROR", logger="prepaired.audio"):
        assert m._ensure_audio_analysis_imports() is False
    status = m.audio_status()
    assert status["state"] == "failed" and "audio_features" in (status["error"] or "")
    assert m.AUDIO_ANALYSIS_READY is False
    assert any("failed to initialise" in r.message for r in caplog.records)
    assert m._AUDIO_DONE.is_set()


def test_wait_for_audio_is_bounded(audio_state, monkeypatch):
    monkeypatch.setattr(m, "_AUDIO_STATE", "loading")  # someone else is loading and never finishes
    started = time.perf_counter()
    assert m._ensure_audio_analysis_imports(timeout=0.2) is False
    assert time.perf_counter() - started < 2


@pytest.mark.parametrize("state,active,expected", [
    ("loading", True, "starting"), ("pending", True, "starting"), ("pending", False, "ok"),
    ("ready", True, "ok"), ("failed", True, "degraded")])
def test_health_distinguishes_progress_success_and_failure(audio_state, monkeypatch, state, active, expected):
    monkeypatch.setattr(m, "_AUDIO_STATE", state)
    monkeypatch.setattr(m, "_WARMUP_ACTIVE", active)
    monkeypatch.setattr(m, "AUDIO_ANALYSIS_READY", state == "ready")

    async def go():
        async with _client() as c:
            return await c.get("/health")

    r = asyncio.run(go())
    body = r.json()
    assert r.status_code == 200 and body["status"] == expected
    assert {"pipeline_ready", "timestamp", "audio"} <= set(body) and body["audio"]["state"] == state


# ── session creation independence ─────────────────────────────────────

def test_session_creation_never_initialises_audio(audio_state, monkeypatch, tmp_path):
    import services.storage.database as db
    monkeypatch.setattr(db, "DEFAULT_DB_PATH", tmp_path / "isolated.db")
    monkeypatch.setattr(m, "_AUDIO_STATE", "loading")  # warm-up "in progress", never completes
    monkeypatch.setattr(m, "_import_audio_analysis", lambda: pytest.fail("session creation triggered audio init"))
    monkeypatch.setattr(m, "SESSIONS", {})

    async def go():
        async with _client() as c:
            t = time.perf_counter()
            r = await c.post("/api/sessions", json={
                "candidate_id": "test_guest_warmup", "dsa_topics": ["arrays_algo"], "c_topics": [],
                "duration_minutes": 15, "num_questions": 3, "interview_mode": "standard"})
            return r, time.perf_counter() - t

    resp, elapsed = asyncio.run(go())
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] in m.SESSIONS
    assert m._AUDIO_STATE == "loading"
    print(f"session creation (audio not ready, no warm-up): {elapsed:.1f}s")  # timing is reported, not asserted


# ── event loop responsiveness / failure reporting ─────────────────────

def test_waiting_for_audio_does_not_block_other_requests(audio_state, monkeypatch):
    monkeypatch.setattr(m, "_AUDIO_STATE", "loading")
    monkeypatch.setattr(m, "AUDIO_WAIT_TIMEOUT_S", 2.0)

    async def go():
        async with _client() as c:
            pending = asyncio.create_task(c.post(
                "/api/transcribe", files={"audio": ("a.wav", _wav_bytes(), "audio/wav")}, data={"session_id": ""}))
            await asyncio.sleep(0.3)  # the transcribe request is now waiting on audio init
            t = time.perf_counter()
            health = await c.get("/health")
            health_latency = time.perf_counter() - t
            return health, health_latency, await pending

    health, health_latency, transcribe = asyncio.run(go())
    assert health.status_code == 200 and health.json()["audio"]["state"] == "loading"
    assert health_latency < 1.0, f"event loop blocked while waiting for audio ({health_latency:.2f}s)"
    body = transcribe.json()
    assert body["stt_status"] == "stt_unavailable"
    assert body["audio_init_status"] == "loading" and body["stt_error"]


def test_failed_init_is_reported_by_transcribe(audio_state, monkeypatch):
    monkeypatch.setattr(m, "_AUDIO_STATE", "failed")
    monkeypatch.setattr(m, "_AUDIO_ERROR", "ImportError: simulated")
    m._AUDIO_DONE.set()

    async def go():
        async with _client() as c:
            return await c.post("/api/transcribe", files={"audio": ("a.wav", _wav_bytes(), "audio/wav")})

    body = asyncio.run(go()).json()
    assert body["stt_status"] == "stt_unavailable"
    assert body["audio_analysis"] is None
    assert body["stt_error"] == "ImportError: simulated"
    assert body["audio_analysis_ready"] is False


# ── real pipeline (no mocks) ──────────────────────────────────────────

@pytest.mark.skipif(importlib.util.find_spec("whisperx") is None, reason="whisperx not installed in this interpreter")
@pytest.mark.skipif(not FIXTURE_WAV.exists(), reason="audio fixture missing")
def test_real_speech_pipeline_transcribes_once_per_request(audio_state):
    """Real WhisperX + prosody + hesitation on a fixture recording; first and second request."""
    import agents.audio.transcriber as tr
    try:
        tr._get_models()
    except Exception as exc:  # environment cannot load the STT model: report, never fake a pass
        pytest.skip(f"WhisperX model cannot be loaded in this environment: {type(exc).__name__}: {str(exc)[:160]}")
    audio = FIXTURE_WAV.read_bytes()
    calls = {"n": 0}

    async def go():
        async with _client() as c:
            out = []
            for _ in range(2):
                t = time.perf_counter()
                r = await c.post("/api/transcribe", files={"audio": ("fixture.wav", audio, "audio/wav")},
                                 data={"session_id": ""})
                out.append((r.json(), time.perf_counter() - t))
                if len(out) == 1:  # after the first call the stack is loaded: count STT invocations
                    real = m.transcribe_and_align

                    def counting(path, _real=real):
                        calls["n"] += 1
                        return _real(path)
                    m.transcribe_and_align = counting
            return out

    try:
        (first, t1), (second, t2) = asyncio.run(go())
    finally:
        m.transcribe_and_align = tr.transcribe_and_align
    print(f"real pipeline: first={t1:.1f}s second={t2:.1f}s transcript_chars={len(first['transcript'])}")
    for body in (first, second):
        assert body["stt_status"] == "success", body.get("stt_error")
        assert body["transcript"].strip()
        analysis = body["audio_analysis"]
        assert analysis and 0.0 <= analysis["confidence_score"] <= 1.0
        assert analysis["hesitation"] is not None and analysis["prosodic"] is not None
    assert calls["n"] == 1, "second request must transcribe exactly once (no duplicate STT inside analysis)"


@pytest.mark.skipif(not FIXTURE_WAV.exists(), reason="audio fixture missing")
def test_real_acoustic_analysis_chain_on_fixture(audio_state):
    """Real prosody + hesitation + confidence scoring + RL state vector on the fixture recording.

    Uses the pipeline's own energy-timing transcription so it does not need the STT model weights.
    """
    if not m._ensure_audio_analysis_imports():
        pytest.skip(f"audio stack unavailable: {m._AUDIO_ERROR}")
    import agents.audio.transcriber as tr
    timing = tr._fallback_energy_timing(str(FIXTURE_WAV))
    text = "I would use a hash table with chaining to resolve collisions and get constant time lookup."
    analysis = m._analyze_audio_confidence(str(FIXTURE_WAV), text, "", transcription=timing)
    assert analysis is not None
    assert 0.0 <= analysis["confidence_score"] <= 1.0
    assert analysis["label"] in {"low", "medium", "high"}
    assert analysis["hesitation"] is not None and analysis["prosodic"] is not None
    assert analysis["rl_state"] is not None
