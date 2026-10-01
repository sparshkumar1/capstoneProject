"""
Unit and regression tests for codebase audit bug fixes (BUG-01 through BUG-09):
- BUG-01: /api/run_code retrieves test cases from active session orchestrator via _get_current_question()
- BUG-02: _select_best_attempt handles None, NaN, and non-numeric scores safely
- BUG-03: ScoreValidator and Orchestrator turn handlers handle None raw scores without crashing
- BUG-04: Multimodal acoustic hesitation score persists in orchestrator state and feeds RL observation
- BUG-05: Qwen follow-up and feedback prompt builders and synthesizers handle None/NaN final_score safely
- BUG-06: FeedbackAgent.generate handles None and non-numeric scores safely
- BUG-07: database.compare_with_previous_best handles None and NaN scores safely
- BUG-08: database.get_candidate_history attaches authoritative best attempts
- BUG-09: /api/reports/{session_id} recovers session from snapshot if evicted from memory
"""

import math
import sqlite3
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from agents.orchestrator.feedback_agent import FeedbackAgent
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.validation.score_validator import ScoreValidator
from apps.backend import main as backend_main
from services.qwen.app import (
    FeedbackRequest,
    FollowupRequest,
    _build_feedback_prompt,
    _build_followup_prompt,
    _synthesize_structured_feedback,
    _synthesize_structured_followup,
)
from services.storage.database import (
    compare_with_previous_best,
    get_candidate_history,
    get_or_create_candidate,
    init_db,
    save_attempt,
)


@pytest.fixture
def temp_db(tmp_path: Path):
    db_file = tmp_path / "test_regressions.db"
    init_db(db_file)
    return db_file


# ─────────────────────────────────────────────────────────────────────────────
# BUG-01: /api/run_code retrieves test cases via _get_current_question()
# ─────────────────────────────────────────────────────────────────────────────
def test_run_code_uses_orchestrator_get_current_question(temp_db: Path, monkeypatch):
    monkeypatch.setattr("services.storage.database.DEFAULT_DB_PATH", temp_db)
    client = TestClient(backend_main.app)

    session_id = f"sess_runcode_{uuid.uuid4().hex[:8]}"
    mock_orch = MagicMock()
    mock_test_cases = [
        {"input": "2\n3\n", "expected": "5\n"},
        {"input": "10\n20\n", "expected": "30\n"},
    ]
    mock_orch._get_current_question.return_value = {
        "id": "q_custom",
        "title": "Custom Question",
        "test_cases": mock_test_cases,
    }
    backend_main.SESSIONS[session_id] = mock_orch

    with patch("agents.coding_executor.coding_executor.evaluate_c_submission") as mock_eval:
        mock_eval.return_value = {
            "status": "accepted",
            "passed": True,
            "coding_score": 1.0,
            "tests_total": 2,
            "tests_passed": 2,
        }
        try:
            resp = client.post(
                "/api/run_code",
                json={
                    "code": "#include <stdio.h>\nint main(){ return 0; }",
                    "session_id": session_id,
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["tests_total"] == 2
            assert data["tests_passed"] == 2
            mock_orch._get_current_question.assert_called_once()
            mock_eval.assert_called_once_with(
                "#include <stdio.h>\nint main(){ return 0; }",
                test_cases=mock_test_cases,
            )
        finally:
            backend_main.SESSIONS.pop(session_id, None)


def test_run_code_fallback_when_session_absent():
    client = TestClient(backend_main.app)
    with patch("agents.coding_executor.coding_executor.evaluate_c_submission") as mock_eval:
        mock_eval.return_value = {
            "status": "accepted",
            "passed": True,
            "coding_score": 1.0,
            "tests_total": 0,
            "tests_passed": 0,
        }
        resp = client.post(
            "/api/run_code",
            json={
                "code": "#include <stdio.h>\nint main(){ return 0; }",
                "session_id": "nonexistent_session",
            },
        )
        assert resp.status_code == 200
        mock_eval.assert_called_once_with(
            "#include <stdio.h>\nint main(){ return 0; }",
            test_cases=[],
        )


# ─────────────────────────────────────────────────────────────────────────────
# BUG-02: _select_best_attempt handles None, NaN, and non-numeric scores
# ─────────────────────────────────────────────────────────────────────────────
def test_select_best_attempt_with_none_and_nan_scores():
    orch = InterviewOrchestrator(
        session_id="test_sess_bug02",
        candidate={"id": "c1", "name": "Cand"},
        config={"num_questions": 1, "duration_minutes": 10},
    )
    attempts = [
        {"attempt_id": "att1", "raw_score": None, "timestamp": 100},
        {"attempt_id": "att2", "raw_score": float("nan"), "timestamp": 101},
        {"attempt_id": "att3", "raw_score": "not_a_number", "timestamp": 102},
        {"attempt_id": "att4", "raw_score": 0.82, "timestamp": 103},
        {"attempt_id": "att5", "raw_score": 0.45, "timestamp": 104},
    ]
    best = orch._select_best_attempt(attempts)
    assert best is not None
    assert best["attempt_id"] == "att4"
    assert best["raw_score"] == 0.82


def test_select_best_attempt_all_invalid():
    orch = InterviewOrchestrator(
        session_id="test_sess_bug02_inv",
        candidate={"id": "c1", "name": "Cand"},
        config={"num_questions": 1, "duration_minutes": 10},
    )
    attempts = [
        {"attempt_id": "att1", "raw_score": None, "timestamp": 100},
        {"attempt_id": "att2", "raw_score": float("nan"), "timestamp": 101},
    ]
    best = orch._select_best_attempt(attempts)
    assert best is not None  # Returns an attempt without crashing


# ─────────────────────────────────────────────────────────────────────────────
# BUG-03: ScoreValidator and Orchestrator turn handlers handle None raw scores
# ─────────────────────────────────────────────────────────────────────────────
def test_score_validator_handles_none():
    validator = ScoreValidator()
    result = validator.validate(None, evidence={}, is_coding=False)
    assert result["validated_score"] == 0.0
    assert any(t["rule"] == "missing_score" for t in result["validation_trace"])


@pytest.mark.asyncio
async def test_orchestrator_handles_none_evaluation_score(temp_db: Path, monkeypatch):
    monkeypatch.setattr("services.storage.database.DEFAULT_DB_PATH", temp_db)
    # Mock evaluator returning None final_score
    mock_eval = MagicMock(return_value={
        "final_score": None,
        "grade": "Poor",
        "missing_concepts": ["concept_a"],
        "correct_claims": [],
        "incorrect_claims": [],
        "feedback": "Needs work.",
    })
    orch = InterviewOrchestrator(
        session_id="sess_eval_none",
        candidate={"id": "c1", "name": "Cand"},
        config={"num_questions": 1, "duration_minutes": 10},
        evaluator_fn=mock_eval,
    )
    orch._question_queue = [{"id": "q1", "text": "Explain virtual memory.", "difficulty": 2, "type": "verbal"}]
    orch._state["questions"] = list(orch._question_queue)
    await orch.start()

    # handle_voice_answer must not raise TypeError when final_score is None
    turn_res = await orch.handle_voice_answer("I don't know.", "q1")
    assert "feedback" in turn_res
    assert turn_res["feedback"]["final_score"] == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# BUG-04: Multimodal acoustic hesitation score persists and feeds RL
# ─────────────────────────────────────────────────────────────────────────────
def test_ingest_audio_analysis_persists_hesitation_score():
    orch = InterviewOrchestrator(
        session_id="sess_audio_04",
        candidate={"id": "c1", "name": "Cand"},
        config={"num_questions": 1, "duration_minutes": 10},
    )
    audio_analysis = {
        "confidence": {"score": 0.85, "grade": "High"},
        "hesitation": {"score": 0.72, "hesitation_detected": True},
        "speaking_rate": {"wpm": 130},
    }
    orch.ingest_audio_analysis(audio_analysis)
    assert orch._state["last_confidence_score"] == 0.85
    assert orch._state["last_hesitation_score"] == 0.72

    # Now verify build_rl_observation incorporates s3 = 0.72
    from agents.strategy.hybrid_orchestrator import build_rl_observation
    obs = build_rl_observation(score=0.8, current_difficulty=3, session=orch._state)
    # Dimension 3 of the 6D observation corresponds to hesitation
    assert len(obs) == 6
    assert pytest.approx(obs[3], 0.01) == 0.72


# ─────────────────────────────────────────────────────────────────────────────
# BUG-05: Qwen follow-up and feedback handling None/NaN final_score
# ─────────────────────────────────────────────────────────────────────────────
def test_qwen_followup_and_feedback_handle_none_score():
    req_fu = FollowupRequest(
        original_question="What is a hash table?",
        candidate_answer="It maps keys to values.",
        topic="DSA",
        structured_evaluation={"final_score": None, "grade": "Average"},
    )
    # Prompt builder must not raise TypeError
    prompt_fu = _build_followup_prompt(req_fu)
    assert "Score: 0.00" in prompt_fu

    # Synthesizer fallback must not raise TypeError in >= 0.75 comparison
    synth_fu = _synthesize_structured_followup(req_fu)
    assert synth_fu.followup != ""

    req_fb = FeedbackRequest(
        question_text="What is a hash table?",
        candidate_answer="It maps keys to values.",
        topic="DSA",
        structured_evaluation={"final_score": None, "grade": "Average"},
    )
    prompt_fb = _build_feedback_prompt(req_fb)
    assert "Final Score: 0.00" in prompt_fb

    synth_fb = _synthesize_structured_feedback(req_fb)
    assert synth_fb.final_score == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# BUG-06: FeedbackAgent.generate handles None scores
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_feedback_agent_handles_none_scores():
    agent = FeedbackAgent()
    eval_result = {
        "final_score": None,
        "raw": {"S1_semantic": None, "S2_structural": None, "R_reasoning": None},
        "grade": "Average",
        "missing_concepts": ["concept_x"],
        "correct_claims": ["claim_y"],
    }
    feedback = await agent.generate(
        transcript="Caching speeds up data access.",
        question={"text": "Explain caching."},
        eval_result=eval_result,
        attempt_number=1,
    )
    assert isinstance(feedback, dict)
    assert feedback["final_score"] == 0.0
    assert "how_to_improve" in feedback


# ─────────────────────────────────────────────────────────────────────────────
# BUG-07: database.compare_with_previous_best handles None and NaN scores
# ─────────────────────────────────────────────────────────────────────────────
def test_compare_with_previous_best_none_scores(temp_db: Path):
    c = get_or_create_candidate("comp_cand@test.com", "Comp Cand", db_path=temp_db)
    cid = c["id"]
    qid = "q_comp"
    save_attempt(
        {
            "candidate_id": cid,
            "session_id": "sess_comp",
            "question_id": qid,
            "transcript": "Previous attempt",
            "raw_score": 0.5,
            "validated_score": 0.5,
            "covered_concepts": ["a"],
            "missing_concepts": ["b"],
            "feedback_json": {"grade": "Average"},
        },
        db_path=temp_db,
    )
    current_eval = {"validated_score": None, "final_score": None, "missing_concepts": []}
    comp = compare_with_previous_best(candidate_id=cid, question_id=qid, current_eval=current_eval, db_path=temp_db)
    assert comp["score_delta"] == -0.5
    assert comp["has_previous_best"] is True
    assert comp["has_improvement"] is False


# ─────────────────────────────────────────────────────────────────────────────
# BUG-08: database.get_candidate_history attaches authoritative best attempts
# ─────────────────────────────────────────────────────────────────────────────
def test_get_candidate_history_attaches_best_attempt(temp_db: Path):
    c = get_or_create_candidate("hist_cand@test.com", "History Cand", db_path=temp_db)
    cid = c["id"]
    sid = "sess_hist_1"
    
    # Save attempt 1 (score 0.45)
    save_attempt(
        {
            "candidate_id": cid,
            "session_id": sid,
            "question_id": "q_hist",
            "transcript": "Attempt 1 text",
            "raw_score": 0.45,
            "validated_score": 0.45,
            "covered_concepts": ["a"],
            "missing_concepts": ["b"],
            "feedback_json": {"grade": "Average"},
        },
        db_path=temp_db,
    )
    # Save attempt 2 (score 0.85)
    save_attempt(
        {
            "candidate_id": cid,
            "session_id": sid,
            "question_id": "q_hist",
            "transcript": "Attempt 2 text",
            "raw_score": 0.85,
            "validated_score": 0.85,
            "covered_concepts": ["a", "b"],
            "missing_concepts": [],
            "feedback_json": {"grade": "Good"},
        },
        db_path=temp_db,
    )

    history = get_candidate_history(cid, db_path=temp_db)
    q_entries = {h["question_id"]: h for h in history}
    assert "q_hist" in q_entries
    q_entry = q_entries["q_hist"]
    assert q_entry["has_authoritative_best"] is True
    assert q_entry["best_attempt"] is not None
    assert q_entry["best_attempt"]["validated_score"] == 0.85
    assert q_entry["best_attempt"]["transcript"] == "Attempt 2 text"


# ─────────────────────────────────────────────────────────────────────────────
# BUG-09: /api/reports/{session_id} recovers session from snapshot
# ─────────────────────────────────────────────────────────────────────────────
def test_get_report_recovers_session_from_snapshot(temp_db: Path, monkeypatch):
    monkeypatch.setattr("services.storage.database.DEFAULT_DB_PATH", temp_db)
    client = TestClient(backend_main.app)

    session_id = f"sess_rpt_{uuid.uuid4().hex[:8]}"
    cand_id = f"cand_rpt_{uuid.uuid4().hex[:8]}"
    backend_main.CANDIDATES[cand_id] = {"id": cand_id, "name": "Report Candidate"}

    orch = InterviewOrchestrator(
        session_id=session_id,
        candidate={"id": cand_id, "name": "Report Candidate"},
        config={"num_questions": 1, "duration_minutes": 10},
    )
    orch._state["scores"] = [0.88]
    orch._state["current_difficulty"] = 3
    orch._question_queue = [{"id": "q1", "text": "Explain indexing.", "difficulty": 3, "type": "verbal"}]
    orch._state["questions"] = list(orch._question_queue)
    orch._current_q_index = 1

    # Save snapshot
    backend_main._snapshot_session(orch)

    # Evict from in-memory SESSIONS
    backend_main.SESSIONS.pop(session_id, None)
    assert session_id not in backend_main.SESSIONS

    # Request report
    resp = client.get(f"/api/reports/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == session_id
    assert "overall_score" in data or "behaviour" in data


# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 REGRESSION: Database persistence boundary score sanitization & best-answer preservation
# ─────────────────────────────────────────────────────────────────────────────
def test_save_attempt_db_boundary_score_sanitization(temp_db: Path):
    """save_attempt safely converts None, NaN, +/-inf, and non-numeric values to 0.0,
    clamps out-of-range finite floats to [0.0, 1.0], and preserves valid scores."""
    cand = get_or_create_candidate(f"boundary_{uuid.uuid4().hex[:6]}@test.com", "Boundary Candidate", db_path=temp_db)
    cid = cand["id"]
    sid = f"sess_boundary_{uuid.uuid4().hex[:8]}"

    test_cases = [
        (None, 0.0),
        (math.nan, 0.0),
        (float("inf"), 0.0),
        (-float("inf"), 0.0),
        ("not-a-number", 0.0),
        (0.0, 0.0),
        (0.5, 0.5),
        (1.5, 1.0),
        (-0.3, 0.0),
    ]

    for raw_input, expected_val in test_cases:
        qid = f"q_boundary_{uuid.uuid4().hex[:6]}"
        res = save_attempt(
            {
                "candidate_id": cid,
                "session_id": sid,
                "question_id": qid,
                "transcript": f"Testing input {raw_input}",
                "raw_score": raw_input,
                "covered_concepts": ["core logic"],
                "missing_concepts": [],
            },
            db_path=temp_db,
        )
        assert res["attempt_id"] is not None
        conn = sqlite3.connect(temp_db)
        row = conn.execute(
            "SELECT raw_score, validated_score, evaluation_confidence FROM question_attempts WHERE id = ?;",
            (res["attempt_id"],),
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == expected_val
        assert row[1] == expected_val
        expected_conf = 0.85 if expected_val > 0.0 else 0.0
        assert row[2] == expected_conf


def test_save_attempt_invalid_score_does_not_displace_existing_best(temp_db: Path):
    """An invalid attempt (e.g. crashed evaluator, NaN/inf/None score) must never
    displace or corrupt an existing valid best answer."""
    cand = get_or_create_candidate(f"freeze_{uuid.uuid4().hex[:6]}@test.com", "Freeze Candidate", db_path=temp_db)
    cid = cand["id"]
    sid = f"sess_displace_{uuid.uuid4().hex[:8]}"
    qid = "q_authoritative_freeze_test"

    # Attempt 1: Valid high score
    att1 = save_attempt(
        {
            "candidate_id": cid,
            "session_id": sid,
            "question_id": qid,
            "transcript": "First high quality response",
            "raw_score": 0.85,
            "validated_score": 0.85,
            "covered_concepts": ["concept_a", "concept_b"],
            "missing_concepts": [],
        },
        db_path=temp_db,
    )
    assert att1["is_best"] is True
    assert att1["current_best"]["validated_score"] == 0.85
    assert att1["current_best"]["id"] == att1["attempt_id"]

    # Attempt 2: Invalid/corrupt attempt with NaN score and missing evaluation
    att2 = save_attempt(
        {
            "candidate_id": cid,
            "session_id": sid,
            "question_id": qid,
            "transcript": "Corrupted non-numeric attempt",
            "raw_score": math.nan,
            "validated_score": float("inf"),
            "covered_concepts": [],
            "missing_concepts": ["concept_a", "concept_b"],
        },
        db_path=temp_db,
    )
    # Attempt 2 must NOT be marked best
    assert att2["is_best"] is False
    # Attempt 1 must remain authoritative best
    assert att2["current_best"] is not None
    assert att2["current_best"]["id"] == att1["attempt_id"]
    assert att2["current_best"]["validated_score"] == 0.85


# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 REGRESSION: Missing evaluation scores fail closed to 0.0 vs genuine 0.50
# ─────────────────────────────────────────────────────────────────────────────
def test_qwen_feedback_fallback_fails_closed_to_zero_and_poor_grade():
    """Qwen feedback synthesized fallback must fail closed to 0.0 and 'Poor' grade
    when final_score is missing/None/non-finite, while preserving genuine 0.50 as 'Average'."""
    # Case A: Missing final_score -> 0.0 and Poor
    req_missing = FeedbackRequest(
        question_text="Explain Two Sum logic",
        topic="Arrays",
        candidate_answer="I tried to think about it but got stuck.",
        structured_evaluation={"final_score": None, "missing_concepts": ["hash map lookup"]},
    )
    res_missing = _synthesize_structured_feedback(req_missing)
    assert res_missing.final_score == 0.0
    assert res_missing.grade == "Poor"
    assert res_missing.final_score < 0.40  # Below verbal eligibility threshold

    # Case B: NaN final_score -> 0.0 and Poor
    req_nan = FeedbackRequest(
        question_text="Explain Two Sum logic",
        topic="Arrays",
        candidate_answer="I tried to think about it but got stuck.",
        structured_evaluation={"final_score": math.nan, "missing_concepts": ["hash map lookup"]},
    )
    res_nan = _synthesize_structured_feedback(req_nan)
    assert res_nan.final_score == 0.0
    assert res_nan.grade == "Poor"

    # Case C: Genuine 0.50 score -> 0.50 and Average
    req_partial = FeedbackRequest(
        question_text="Explain Two Sum logic",
        topic="Arrays",
        candidate_answer="I used a brute force O(N^2) double loop.",
        structured_evaluation={"final_score": 0.50, "missing_concepts": ["O(N) hash map"]},
    )
    res_partial = _synthesize_structured_feedback(req_partial)
    assert res_partial.final_score == 0.50
    assert res_partial.grade == "Average"
    assert res_partial.final_score >= 0.40  # Eligible for partial credit


@pytest.mark.asyncio
async def test_feedback_agent_missing_score_fails_closed():
    """FeedbackAgent must output final_score 0.0 and grade F when evaluation has no score,
    distinguishing it from a genuine partial 0.50 score."""
    agent = FeedbackAgent()

    # Missing evaluation score
    fb_missing = await agent.generate(
        transcript="Vague answer with no evaluation",
        question={"id": "q1", "text": "Explain quicksort", "topic": "sorting"},
        eval_result={"final_score": None},
    )
    assert fb_missing["final_score"] == 0.0
    assert fb_missing["grade"] == "F"
    assert fb_missing["score_breakdown"]["overall"] == 0.0

    # Genuine 0.50 partial evaluation score
    fb_genuine = await agent.generate(
        transcript="Quicksort partitions the array around a pivot",
        question={"id": "q1", "text": "Explain quicksort", "topic": "sorting"},
        eval_result={"final_score": 0.50},
    )
    assert fb_genuine["final_score"] == 0.50
    assert fb_genuine["grade"] == "D"
    assert fb_genuine["score_breakdown"]["overall"] == 0.50


@pytest.mark.asyncio
async def test_orchestrator_code_submission_missing_score_fails_closed():
    """InterviewOrchestrator handle_code_submission must fail closed to 0.0 when
    the code evaluator returns None or missing final_score."""
    session_id = f"sess_code_fail_{uuid.uuid4().hex[:8]}"
    orch = InterviewOrchestrator(
        session_id=session_id,
        candidate={"id": "cand_code_test", "name": "Code Test Candidate"},
        config={"num_questions": 1, "duration_minutes": 10},
    )
    orch._question_queue = [{
        "id": "q_code_1",
        "text": "def two_sum(nums, target): pass",
        "difficulty": 2,
        "type": "coding",
        "test_cases": [{"input": "1", "expected": "1"}],
    }]
    orch._state["questions"] = list(orch._question_queue)
    orch._current_q_index = 0

    # Mock evaluate_code returning None for final_score
    with patch.object(orch, "_evaluate_code", return_value={"final_score": None, "feedback": "Evaluation failed"}):
        res = await orch.handle_code_submission(
            code="def two_sum(): pass",
            question_id="q_code_1",
            passed=False,
            tests_passed=0,
            tests_total=1,
            stdout="",
            stderr="Error",
        )
        assert res["feedback"]["final_score"] == 0.0
        assert orch._state["raw_scores"][-1] == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT DEFECT REGRESSIONS: Evaluation Confidence & Status Forwarding
# ─────────────────────────────────────────────────────────────────────────────
def test_save_attempt_preserves_explicit_confidence(temp_db: Path):
    """save_attempt preserves explicit evaluation_confidence, clamps to [0.0, 1.0],
    and does not default to 0.85 when 0.0 is explicitly passed."""
    cand = get_or_create_candidate(f"conf_{uuid.uuid4().hex[:6]}@test.com", "Confidence Candidate", db_path=temp_db)
    cid = cand["id"]
    sid = f"sess_conf_{uuid.uuid4().hex[:8]}"

    # Explicit 0.92 confidence
    res1 = save_attempt(
        {
            "candidate_id": cid,
            "session_id": sid,
            "question_id": "q_conf_1",
            "transcript": "Good response",
            "raw_score": 0.80,
            "evaluation_confidence": 0.92,
        },
        db_path=temp_db,
    )
    conn = sqlite3.connect(temp_db)
    row1 = conn.execute("SELECT evaluation_confidence FROM question_attempts WHERE id = ?;", (res1["attempt_id"],)).fetchone()
    assert row1[0] == 0.92

    # Explicit 0.0 confidence (e.g. failed evaluation)
    res2 = save_attempt(
        {
            "candidate_id": cid,
            "session_id": sid,
            "question_id": "q_conf_2",
            "transcript": "Failed evaluation attempt",
            "raw_score": 0.0,
            "evaluation_confidence": 0.0,
        },
        db_path=temp_db,
    )
    row2 = conn.execute("SELECT evaluation_confidence FROM question_attempts WHERE id = ?;", (res2["attempt_id"],)).fetchone()
    conn.close()
    assert row2[0] == 0.0


@pytest.mark.asyncio
async def test_orchestrator_forwards_evaluation_confidence():
    """InterviewOrchestrator handle_voice_answer forwards eval_result evaluation_confidence
    to attempt_payload and storage, preventing unjustified 0.85 on missing evaluations."""
    session_id = f"sess_orch_conf_{uuid.uuid4().hex[:8]}"
    orch = InterviewOrchestrator(
        session_id=session_id,
        candidate={"id": "cand_orch_conf", "name": "Conf Candidate"},
        config={"num_questions": 1, "duration_minutes": 10},
    )
    orch._question_queue = [{
        "id": "q_conf_voice",
        "text": "Explain indexing.",
        "difficulty": 2,
        "type": "verbal",
    }]
    orch._state["questions"] = list(orch._question_queue)
    orch._current_q_index = 0

    saved_payloads = []
    def fake_save_attempt(payload, db_path=None):
        saved_payloads.append(payload)
        return {"attempt_id": "fake_aid", "is_best": False, "current_best": None}

    # Case 1: Evaluator returns explicit 0.95 confidence
    with patch("services.storage.database.save_attempt", side_effect=fake_save_attempt):
        with patch.object(orch, "_evaluate_verbal", return_value={"final_score": 0.85, "evaluation_confidence": 0.95, "correct_claims": ["Index"], "missing_concepts": []}):
            await orch.handle_voice_answer("Index speeds up lookups.", "q_conf_voice")
            assert len(saved_payloads) == 1
            assert saved_payloads[0]["evaluation_confidence"] == 0.95

    # Case 2: STT failure / empty transcript -> evaluation_confidence must be 0.0
    saved_payloads.clear()
    with patch("services.storage.database.save_attempt", side_effect=fake_save_attempt):
        await orch.handle_voice_answer("", "q_conf_voice")
        assert len(saved_payloads) == 1
        assert saved_payloads[0]["evaluation_confidence"] == 0.0


def test_report_generation_includes_evaluation_status():
    """InterviewOrchestrator._generate_report exposes question evaluation status
    to allow the frontend to accurately distinguish evaluated vs unavailable questions."""
    orch = InterviewOrchestrator(
        session_id="sess_report_status",
        candidate={"id": "cand_rpt", "name": "Report Cand"},
        config={"num_questions": 2, "duration_minutes": 10},
    )
    orch._question_queue = [
        {"id": "q1", "text": "Q1 text", "difficulty": 2, "type": "verbal"},
        {"id": "q2", "text": "Q2 text", "difficulty": 3, "type": "verbal"},
    ]
    orch._state["questions"] = list(orch._question_queue)

    # Question 1: evaluated normally
    orch._state["answers"] = [
        {
            "question_id": "q1",
            "score": 0.8,
            "raw_score": 0.8,
            "feedback": {"status": "success", "grade": "Good", "justification": "Good explanation."},
        },
        {
            "question_id": "q2",
            "score": 0.0,
            "raw_score": 0.0,
            "feedback": {"status": "stt_unavailable", "grade": "Ungraded", "justification": "STT unavailable."},
        },
    ]

    report = orch._generate_report()
    results = report["question_results"]
    assert len(results) == 2
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "stt_unavailable"

