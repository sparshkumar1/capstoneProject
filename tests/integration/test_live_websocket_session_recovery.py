"""
Live-WebSocket session-recovery integration test.

The prior (second) pass implemented session snapshot/restore
(agents/orchestrator/interview_orchestrator.py::snapshot_state/restore_from_snapshot,
services/storage/database.py's session_snapshots table, and
apps/backend/main.py's _snapshot_session/_try_restore_session) and tested it
at the database, orchestrator, and backend-glue layers directly
(tests/unit/test_session_recovery.py) -- but explicitly documented, as a
disclosed gap, that no test exercised the actual live WebSocket endpoint
(/ws/interview/{session_id}) end to end: connect, take a turn, lose the
connection, simulate a backend restart, reconnect, and confirm the session
resumes.

This is the highest-risk untested path this pass's own instructions ask to
close if practical: this file drives the REAL FastAPI app (apps.backend.main)
through FastAPI's TestClient WebSocket support, not a shadow copy of the
handler logic.
"""
import os

os.environ.setdefault("EVALUATOR_MOCK_MODE", "1")

import pytest
from fastapi.testclient import TestClient

from apps.backend.main import app, SESSIONS


@pytest.fixture
def client():
    return TestClient(app)


def test_session_resumes_after_simulated_backend_restart_via_live_websocket(client):
    """End-to-end: create a session, take one real turn over a live WebSocket
    connection, disconnect, simulate a backend process restart (clear the
    in-memory SESSIONS registry -- the actual mechanism a real restart would
    wipe), reconnect on a NEW WebSocket connection with the SAME session_id,
    and confirm the session is transparently restored and can continue,
    rather than returning "Session not found"."""
    create_resp = client.post(
        "/api/sessions",
        json={
            "c_topics": ["Arrays"],
            "dsa_topics": [],
            "duration_minutes": 30,
            "num_questions": 5,
            "interview_mode": "standard",
        },
    )
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]
    assert session_id in SESSIONS

    # --- First connection: start the session and answer one question ---
    with client.websocket_connect(f"/ws/interview/{session_id}") as ws:
        ws.send_json({"type": "start"})
        question_msg = ws.receive_json()
        assert question_msg["type"] == "question"
        question_id = question_msg["payload"]["id"]

        ws.send_json({
            "type": "voice_answer",
            "payload": {
                "transcript": "I would use a hash map to store elements and their indices as I iterate.",
                "question_id": question_id,
                "attempts": 1,
            },
        })
        feedback_msg = ws.receive_json()
        assert feedback_msg["type"] == "feedback"
    # WebSocket context manager exit closes the connection (simulates a client disconnect).

    scores_after_first_turn = list(SESSIONS[session_id]._state["scores"])
    assert len(scores_after_first_turn) == 1, "Expected exactly one scored turn before the simulated restart"

    # --- Simulate a backend process restart: wipe the in-memory session registry ---
    del SESSIONS[session_id]
    assert session_id not in SESSIONS

    # --- Second connection, same session_id: must transparently restore, not "Session not found" ---
    with client.websocket_connect(f"/ws/interview/{session_id}") as ws:
        assert session_id in SESSIONS, "Reconnecting must have triggered restoration into SESSIONS"
        restored_scores = SESSIONS[session_id]._state["scores"]
        assert restored_scores == scores_after_first_turn, "Restored session must preserve the pre-restart turn history"

        ws.send_json({"type": "next_question"})
        next_msg = ws.receive_json()
        assert next_msg["type"] in ("question", "session_end"), (
            f"Expected the resumed session to continue normally, got: {next_msg}"
        )


def test_reconnect_to_a_session_with_no_snapshot_still_reports_not_found(client):
    """Control: a session_id that was never created (no snapshot exists) must
    still get the original 'Session not found' behavior, not a crash."""
    with client.websocket_connect("/ws/interview/nonexistent-session-id") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "not found" in msg["payload"]["message"].lower()
