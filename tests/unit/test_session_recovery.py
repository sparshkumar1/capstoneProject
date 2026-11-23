"""
Unit tests for session-snapshot persistence and recovery:
  - services/storage/database.py: save_session_snapshot / load_session_snapshot
  - agents/orchestrator/interview_orchestrator.py: InterviewOrchestrator.snapshot_state /
    restore_from_snapshot
  - apps/backend/main.py: _snapshot_session / _try_restore_session (the glue that lets a
    WebSocket reconnect after SESSIONS (the in-memory session dict) has lost a session,
    e.g. after a backend process restart)

Prior to this, sessions existed only in the in-memory SESSIONS dict; a restart lost all
in-progress interview state with no recovery path and no test coverage of that gap.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from services.storage.database import (
    init_db,
    load_session_snapshot,
    save_session_snapshot,
)


@pytest.fixture
def temp_db(tmp_path: Path):
    db_file = tmp_path / "test_prepaired.db"
    init_db(db_file)
    return db_file


# ─────────────────────────────────────────────────────────────────────────────
# Database-level round trip
# ─────────────────────────────────────────────────────────────────────────────
def test_save_and_load_session_snapshot_round_trip(temp_db: Path):
    state = {
        "id": "sess-1", "candidate_id": "cand-1", "scores": [0.7, 0.5],
        "question_ids": ["q1", "q2", "q3"], "current_difficulty": 3,
    }
    queue = [{"id": "q1"}, {"id": "q2"}, {"id": "fu_q2_0"}, {"id": "q3"}]

    save_session_snapshot("sess-1", state, queue, current_q_index=1, db_path=temp_db)
    loaded = load_session_snapshot("sess-1", db_path=temp_db)

    assert loaded is not None
    assert loaded["state"] == state
    assert loaded["question_queue"] == queue
    assert loaded["current_q_index"] == 1
    assert "updated_at" in loaded


def test_save_session_snapshot_overwrites_previous_snapshot(temp_db: Path):
    save_session_snapshot("sess-1", {"scores": [0.1]}, [{"id": "q1"}], 0, db_path=temp_db)
    save_session_snapshot("sess-1", {"scores": [0.1, 0.9]}, [{"id": "q1"}, {"id": "q2"}], 1, db_path=temp_db)

    loaded = load_session_snapshot("sess-1", db_path=temp_db)
    assert loaded["state"]["scores"] == [0.1, 0.9]
    assert loaded["current_q_index"] == 1


def test_load_session_snapshot_returns_none_when_missing(temp_db: Path):
    assert load_session_snapshot("nonexistent-session", db_path=temp_db) is None


def test_save_session_snapshot_ignores_empty_session_id(temp_db: Path):
    save_session_snapshot("", {"scores": []}, [], 0, db_path=temp_db)
    assert load_session_snapshot("", db_path=temp_db) is None


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator-level snapshot/restore fidelity
# ─────────────────────────────────────────────────────────────────────────────
def _make_orchestrator(session_id="sess-orch-1"):
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    def fake_select_questions(c_topics, dsa_topics, num, start_diff):
        return [
            {"id": "q1", "text": "Q1", "topic": "Arrays", "difficulty": start_diff, "type": "verbal"},
            {"id": "q2", "text": "Q2", "topic": "Arrays", "difficulty": start_diff, "type": "verbal"},
            {"id": "q3", "text": "Q3", "topic": "Arrays", "difficulty": start_diff, "type": "verbal"},
        ]

    return InterviewOrchestrator(
        session_id=session_id,
        candidate={"id": "cand-1", "name": "Test Candidate", "experience": "intermediate"},
        config={"c_topics": ["Arrays"], "dsa_topics": [], "duration_minutes": 30,
                "num_questions": 3, "interview_mode": "standard", "defer_rl": True},
        evaluator_fn=None,
        select_questions_fn=fake_select_questions,
    )


def test_snapshot_state_captures_state_queue_and_index():
    orch = _make_orchestrator()
    orch._state["scores"] = [0.6, 0.8]
    orch._state["current_difficulty"] = 4
    orch._question_queue.insert(1, {"id": "fu_q1_0", "text": "Follow-up", "type": "verbal"})
    orch._current_q_index = 2

    snap = orch.snapshot_state()

    assert snap["state"]["scores"] == [0.6, 0.8]
    assert snap["state"]["current_difficulty"] == 4
    assert snap["question_queue"][1]["id"] == "fu_q1_0"
    assert snap["current_q_index"] == 2


def test_restore_from_snapshot_reconstructs_equivalent_orchestrator():
    """The core recovery guarantee: a freshly-constructed orchestrator restored
    from a snapshot must have the same resumable state as the original at the
    moment of the snapshot -- including a follow-up question injected into the
    live queue, which is NOT present in self._state["questions"]."""
    original = _make_orchestrator(session_id="sess-restore-1")
    original._state["scores"] = [0.7]
    original._state["answers"] = ["I would use a hash map."]
    original._state["current_difficulty"] = 3
    original._question_queue.insert(1, {"id": "fu_q1_0", "text": "Follow-up on hash maps", "type": "verbal"})
    original._current_q_index = 1

    snapshot = original.snapshot_state()

    restored = _make_orchestrator(session_id="sess-restore-1")
    restored.restore_from_snapshot(snapshot)

    assert restored._state["scores"] == [0.7]
    assert restored._state["answers"] == ["I would use a hash map."]
    assert restored._state["current_difficulty"] == 3
    assert restored._question_queue[1]["id"] == "fu_q1_0"
    assert restored._current_q_index == 1
    # The restored queue must be an independent copy, not aliased to the original
    restored._question_queue.append({"id": "extra"})
    assert len(restored._question_queue) != len(original._question_queue)


def test_restore_from_snapshot_rejects_malformed_snapshot():
    orch = _make_orchestrator()
    with pytest.raises(ValueError):
        orch.restore_from_snapshot({"state": {}, "question_queue": "not-a-list", "current_q_index": 0})
    with pytest.raises(ValueError):
        orch.restore_from_snapshot("not-a-dict")


# ─────────────────────────────────────────────────────────────────────────────
# Backend glue: _snapshot_session / _try_restore_session
# ─────────────────────────────────────────────────────────────────────────────
def test_backend_snapshot_and_restore_round_trip(temp_db: Path, monkeypatch):
    """Simulates the actual failure mode this feature targets: the backend's
    in-memory SESSIONS dict loses a session (e.g. a process restart), and a
    reconnecting client's session_id must be recoverable from the last saved
    snapshot via the same helpers the WebSocket handler calls."""
    import services.storage.database as db_module
    monkeypatch.setattr(db_module, "DEFAULT_DB_PATH", temp_db)

    from apps.backend import main as backend_main

    orch = _make_orchestrator(session_id="sess-backend-1")
    orch._state["scores"] = [0.65]
    orch._state["current_difficulty"] = 3
    orch._current_q_index = 1
    backend_main.CANDIDATES["cand-1"] = {"id": "cand-1", "name": "Test Candidate"}

    backend_main._snapshot_session(orch)

    # Simulate a restart: the original orchestrator instance is gone, SESSIONS is empty.
    restored = backend_main._try_restore_session("sess-backend-1")

    assert restored is not None
    assert restored._state["scores"] == [0.65]
    assert restored._state["current_difficulty"] == 3
    assert restored._current_q_index == 1


def test_backend_restore_returns_none_when_no_snapshot_exists(temp_db: Path, monkeypatch):
    import services.storage.database as db_module
    monkeypatch.setattr(db_module, "DEFAULT_DB_PATH", temp_db)

    from apps.backend import main as backend_main

    assert backend_main._try_restore_session("never-existed-session") is None
