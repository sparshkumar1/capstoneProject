"""
Unit tests for Persistent Candidate Learning History, Multi-Attempts,
Deterministic Best Answer Selection, and Evaluator-Grounded Comparison.

Run with:
    pytest tests/unit/test_persistence_and_history.py -v
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.storage.database import (
    compare_with_previous_best,
    get_best_attempt,
    get_candidate_by_id,
    get_connection,
    get_or_create_candidate,
    get_question_attempts,
    init_db,
    save_attempt,
    save_session,
)


@pytest.fixture
def temp_db(tmp_path: Path):
    """Fixture providing an isolated SQLite database path for testing."""
    db_file = tmp_path / "test_prepaired.db"
    init_db(db_file)
    return db_file


# ── 1. Schema & Initialization ───────────────────────────────────────────────

def test_init_db_creates_tables_and_indices(temp_db: Path):
    """Verify SQLite initialization idempotently creates all required tables and indices."""
    conn = get_connection(temp_db)
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ).fetchall()
        ]
        assert "candidates" in tables
        assert "sessions" in tables
        assert "question_attempts" in tables

        indices = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index';"
            ).fetchall()
        ]
        assert "idx_candidates_email" in indices
        assert "idx_attempts_candidate_question" in indices
        assert "idx_attempts_candidate_question_best" in indices
    finally:
        conn.close()


# ── 2. Candidate Persistent Identity ─────────────────────────────────────────

def test_candidate_identity_persistent_across_logins(temp_db: Path):
    """Same normalized email must return the identical UUID across repeated logins."""
    c1 = get_or_create_candidate("john.doe@university.edu", "John Doe", college="MIT", db_path=temp_db)
    assert c1["id"]
    assert c1["email"] == "john.doe@university.edu"

    # Second login with mixed case and whitespace
    c2 = get_or_create_candidate("  JOHN.DOE@university.edu ", "John Updated", college="MIT", db_path=temp_db)
    assert c2["id"] == c1["id"]
    assert c2["name"] == "John Updated"

    # Distinct email gets distinct ID
    c3 = get_or_create_candidate("jane@university.edu", "Jane", db_path=temp_db)
    assert c3["id"] != c1["id"]

    # Lookup by ID
    found = get_candidate_by_id(c1["id"], db_path=temp_db)
    assert found is not None
    assert found["id"] == c1["id"]
    assert found["email"] == "john.doe@university.edu"


# ── 3. Multi-attempt Numbering & Deterministic Best-Answer ───────────────────

def test_multi_attempt_numbering_and_best_selection(temp_db: Path):
    """
    Candidate answering the same question multiple times:
    - Attempt numbers increment (1, 2, 3).
    - Higher validated_score wins is_best.
    - Subsequent lower scores do not degrade previous best.
    """
    c = get_or_create_candidate("student1@test.com", "Student One", db_path=temp_db)
    cid = c["id"]
    sid = "sess_001"
    qid = "c_pointers_01"

    # Attempt 1: score 0.50
    res1 = save_attempt({
        "candidate_id": cid,
        "session_id": sid,
        "question_id": qid,
        "attempt_type": "primary",
        "raw_score": 0.50,
        "validated_score": 0.50,
        "covered_concepts": ["pointer_declaration"],
        "missing_concepts": ["dereferencing", "null_check"],
        "transcript": "A pointer holds an address.",
    }, db_path=temp_db)

    assert res1["attempt_number"] == 1
    assert res1["session_attempt_number"] == 1
    assert res1["is_best"] is True

    best1 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best1 is not None
    assert best1["attempt_number"] == 1
    assert best1["validated_score"] == 0.50
    assert best1["is_best"] == 1

    # Attempt 2: Improved answer with score 0.85
    res2 = save_attempt({
        "candidate_id": cid,
        "session_id": sid,
        "question_id": qid,
        "attempt_type": "primary",
        "raw_score": 0.85,
        "validated_score": 0.85,
        "covered_concepts": ["pointer_declaration", "dereferencing", "null_check"],
        "missing_concepts": [],
        "transcript": "A pointer holds memory address, dereferenced with asterisk, checked for NULL.",
    }, db_path=temp_db)

    assert res2["attempt_number"] == 2
    assert res2["session_attempt_number"] == 2
    assert res2["is_best"] is True

    best2 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best2["attempt_number"] == 2
    assert best2["validated_score"] == 0.85

    # Attempt 3: Inferior answer with score 0.65 in a future session
    sid2 = "sess_002"
    res3 = save_attempt({
        "candidate_id": cid,
        "session_id": sid2,
        "question_id": qid,
        "attempt_type": "primary",
        "raw_score": 0.65,
        "validated_score": 0.65,
        "covered_concepts": ["pointer_declaration"],
        "missing_concepts": ["dereferencing"],
        "transcript": "Pointers point to memory.",
    }, db_path=temp_db)

    assert res3["attempt_number"] == 3
    assert res3["session_attempt_number"] == 1  # First attempt in session 2!
    assert res3["is_best"] is False

    # Invariant: Attempt 2 remains the best answer
    best3 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best3["attempt_number"] == 2
    assert best3["validated_score"] == 0.85
    assert best3["is_best"] == 1

    # Invariant: Exactly one attempt has is_best == 1
    attempts = get_question_attempts(cid, qid, db_path=temp_db)
    assert len(attempts) == 3
    bests = [a for a in attempts if a["is_best"] == 1]
    assert len(bests) == 1
    assert bests[0]["attempt_number"] == 2


# ── 4. Strict Tie-Breaking Invariants ─────────────────────────────────────────

def test_tie_breaking_fewest_missing_concepts_wins(temp_db: Path):
    """
    Tie-breaker 1: Equal score -> attempt with FEWEST missing concepts wins.
    """
    c = get_or_create_candidate("tie1@test.com", "Tie One", db_path=temp_db)
    cid = c["id"]
    qid = "c_mem_01"

    # Attempt 1: score 0.75, 2 missing concepts
    save_attempt({
        "candidate_id": cid,
        "session_id": "s1",
        "question_id": qid,
        "attempt_type": "primary",
        "raw_score": 0.75,
        "validated_score": 0.75,
        "missing_concepts": ["free", "valgrind"],
        "covered_concepts": ["malloc"],
    }, db_path=temp_db)

    # Attempt 2: score 0.75, only 1 missing concept
    save_attempt({
        "candidate_id": cid,
        "session_id": "s1",
        "question_id": qid,
        "attempt_type": "primary",
        "raw_score": 0.75,
        "validated_score": 0.75,
        "missing_concepts": ["valgrind"],
        "covered_concepts": ["malloc", "free"],
    }, db_path=temp_db)

    best = get_best_attempt(cid, qid, db_path=temp_db)
    assert best["attempt_number"] == 2
    assert len(best["missing_concepts"]) == 1


def test_tie_breaking_most_recent_wins_on_equal_missing(temp_db: Path):
    """
    Tie-breaker 2: Equal score and equal missing concepts -> most recent attempt (attempt_number DESC) wins.
    """
    c = get_or_create_candidate("tie2@test.com", "Tie Two", db_path=temp_db)
    cid = c["id"]
    qid = "c_struct_01"

    # Attempt 1: score 0.80, 1 missing concept
    save_attempt({
        "candidate_id": cid,
        "session_id": "s1",
        "question_id": qid,
        "attempt_type": "primary",
        "raw_score": 0.80,
        "validated_score": 0.80,
        "missing_concepts": ["padding"],
        "covered_concepts": ["struct", "sizeof"],
    }, db_path=temp_db)

    # Attempt 2: score 0.80, 1 missing concept
    save_attempt({
        "candidate_id": cid,
        "session_id": "s1",
        "question_id": qid,
        "attempt_type": "primary",
        "raw_score": 0.80,
        "validated_score": 0.80,
        "missing_concepts": ["alignment"],
        "covered_concepts": ["struct", "sizeof"],
    }, db_path=temp_db)

    best = get_best_attempt(cid, qid, db_path=temp_db)
    assert best["attempt_number"] == 2


# ── 5. Candidate and Question Isolation ──────────────────────────────────────

def test_data_isolation_between_candidates_and_questions(temp_db: Path):
    """Ensure candidate A cannot see candidate B data, and Q1 data does not bleed into Q2."""
    c_a = get_or_create_candidate("alice@test.com", "Alice", db_path=temp_db)
    c_b = get_or_create_candidate("bob@test.com", "Bob", db_path=temp_db)

    # Alice answers Q1
    save_attempt({
        "candidate_id": c_a["id"],
        "session_id": "s_a",
        "question_id": "q1",
        "attempt_type": "primary",
        "validated_score": 0.90,
        "transcript": "Alice's answer to Q1",
    }, db_path=temp_db)

    # Bob checks Q1
    assert get_best_attempt(c_b["id"], "q1", db_path=temp_db) is None
    assert get_question_attempts(c_b["id"], "q1", db_path=temp_db) == []

    # Alice checks Q2
    assert get_best_attempt(c_a["id"], "q2", db_path=temp_db) is None
    assert get_question_attempts(c_a["id"], "q2", db_path=temp_db) == []


# ── 6. Follow-up vs Retry Decoupling ─────────────────────────────────────────

def test_followup_attempt_does_not_overwrite_primary_best(temp_db: Path):
    """
    Auxiliary follow-ups target gaps and must be recorded with attempt_type='followup',
    but they must NEVER alter or overwrite the primary question's is_best answer.
    """
    c = get_or_create_candidate("cand_fu@test.com", "Followup Candidate", db_path=temp_db)
    cid = c["id"]
    qid = "c_trees_01"

    # Primary attempt: score 0.70
    primary_res = save_attempt({
        "candidate_id": cid,
        "session_id": "s1",
        "question_id": qid,
        "attempt_type": "primary",
        "validated_score": 0.70,
        "transcript": "Binary search tree has left child smaller and right child larger.",
    }, db_path=temp_db)
    assert primary_res["is_best"] is True

    # Auxiliary follow-up probe: score 0.99
    fu_res = save_attempt({
        "candidate_id": cid,
        "session_id": "s1",
        "question_id": "fu_trees_balance",
        "parent_question_id": qid,
        "attempt_type": "followup",
        "validated_score": 0.99,
        "transcript": "AVL tree maintains balance factor between -1 and 1 via rotations.",
    }, db_path=temp_db)
    assert fu_res["is_best"] is False

    # Primary best remains the primary attempt with score 0.70
    primary_best = get_best_attempt(cid, qid, db_path=temp_db)
    assert primary_best["attempt_number"] == 1
    assert primary_best["validated_score"] == 0.70
    assert primary_best["attempt_type"] == "primary"


# ── 7. Evaluator-Grounded Comparison Facts ───────────────────────────────────

def test_compare_with_previous_best_concept_tracking(temp_db: Path):
    """
    compare_with_previous_best derives objective comparison facts:
    - resolved concepts (previously missing, now covered)
    - remaining concepts (still missing)
    - newly missed concepts (previously covered, now missing)
    - score delta
    """
    c = get_or_create_candidate("compare@test.com", "Compare Cand", db_path=temp_db)
    cid = c["id"]
    qid = "c_fork_01"

    # First attempt (saved as best)
    save_attempt({
        "candidate_id": cid,
        "session_id": "s1",
        "question_id": qid,
        "attempt_type": "primary",
        "validated_score": 0.50,
        "covered_concepts": ["process_id", "pid_zero"],
        "missing_concepts": ["copy_on_write", "waitpid"],
        "incorrect_claims": ["fork creates thread"],
        "transcript": "fork clones the process. child gets pid 0.",
    }, db_path=temp_db)

    # Current second attempt evaluation
    curr_eval = {
        "final_score": 0.80,
        "validated_score": 0.80,
        "covered_concepts": ["process_id", "copy_on_write"],  # Resolved copy_on_write!
        "correct_claims": ["process_id", "copy_on_write"],
        "missing_concepts": ["waitpid"],                      # Remaining waitpid
        "incorrect_claims": [],                               # Dropped error!
    }

    comp = compare_with_previous_best(cid, qid, curr_eval, db_path=temp_db)

    assert comp["has_previous_best"] is True
    assert comp["previous_best_score"] == 0.50
    assert comp["score_delta"] == 0.30
    assert "copy_on_write" in comp["resolved_concepts"]
    assert "waitpid" in comp["remaining_concepts"]
    assert comp["has_improvement"] is True


# ── 8. Orchestrator Same-Session Retry Integration ───────────────────────────

@pytest.mark.asyncio
async def test_orchestrator_same_session_retry_flow(temp_db: Path):
    """
    Verify InterviewOrchestrator same-session retry behavior:
    - Attempt 1 submitted.
    - handle_retry resets timer and pending_next, but does NOT advance turn_index.
    - Attempt 2 submitted.
    - Finalizing with handle_next_question commits the best attempt and advances turn.
    """
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    c = get_or_create_candidate("orch_retry@test.com", "Orch Tester", db_path=temp_db)
    cid = c["id"]

    mock_eval = MagicMock()
    mock_eval.return_value = {
        "final_score": 0.50,
        "grade": "C",
        "justification": "Partial understanding",
        "covered_concepts": ["pointer_intro"],
        "missing_concepts": ["dereference", "null_check"],
        "incorrect_claims": [],
        "strong_points": ["Basic idea"],
        "communication_tips": [],
        "score_breakdown": {"similarity": 0.50},
    }

    with patch("services.storage.database.DEFAULT_DB_PATH", temp_db):
        orch = InterviewOrchestrator(
            session_id=str(uuid.uuid4()),
            candidate={"id": cid, "email": "orch_retry@test.com", "name": "Orch Tester", "experience": "intermediate"},
            config={"num_questions": 3, "duration_minutes": 15},
            evaluator_fn=mock_eval,
        )
        # Seed question queue
        orch._question_queue = [
            {"id": "q_p1", "text": "Explain pointer dereferencing in C.", "difficulty": 2, "type": "verbal"},
            {"id": "q_p2", "text": "Explain malloc and free in C.", "difficulty": 2, "type": "verbal"},
        ]
        orch._state["questions"] = list(orch._question_queue)

        start_res = await orch.start()
        assert start_res["id"] == "q_p1"
        assert start_res["type"] == "verbal"
        assert orch._current_q_index == 0

        # Attempt 1: Score 0.50
        ans1_res = await orch.handle_voice_answer("Pointers store memory addresses.", "q_p1")
        assert "feedback" in ans1_res
        assert orch._current_q_index == 0  # Question turn has NOT advanced
        assert orch._state["pending_next"] is True
        assert ans1_res["feedback"]["attempt_number"] == 1
        assert ans1_res["feedback"]["is_best"] is True

        # Candidate clicks "Try Again (Retry)"
        retry_res = await orch.handle_retry("q_p1")
        assert retry_res["type"] == "retry_ready"
        assert retry_res["payload"]["id"] == "q_p1"
        assert retry_res["payload"]["turn_index"] == 1  # Turn index unchanged!
        assert retry_res["payload"]["current_attempt_count"] == 1
        assert orch._state["pending_next"] is False
        assert orch._current_q_index == 0

        # Attempt 2: Improved answer, score 0.85
        mock_eval.return_value = {
            "final_score": 0.85,
            "grade": "A",
            "justification": "Comprehensive answer",
            "covered_concepts": ["pointer_intro", "dereference", "null_check"],
            "missing_concepts": [],
            "incorrect_claims": [],
            "strong_points": ["Solid coverage"],
            "communication_tips": [],
            "score_breakdown": {"similarity": 0.85},
        }

        ans2_res = await orch.handle_voice_answer(
            "Pointers store addresses and are dereferenced using asterisk. Always check for NULL.",
            "q_p1",
        )
        assert ans2_res["feedback"]["attempt_number"] == 2
        assert ans2_res["feedback"]["is_best"] is True
        # Comparison facts populated
        comp = ans2_res["feedback"].get("comparison")
        assert comp is not None
        assert comp["has_previous_best"] is True
        assert comp["score_delta"] == 0.35

        # Candidate is satisfied and advances to next question
        next_res = await orch.handle_next_question()
        assert next_res["type"] == "question"
        assert orch._current_q_index == 1
        assert next_res["payload"]["id"]
        assert next_res["payload"]["turn_index"] == 2

        # End interview and check session storage
        report = await orch.end()
        assert orch._state["status"] == "completed"
        assert "id" in report
        assert "overall_score" in report
        # The finalized score for Q1 should reflect the best attempt (0.85)
        q1_score_records = [s for s in orch._state.get("scores", [])]
        assert len(q1_score_records) == 1
        assert q1_score_records[0] == pytest.approx(0.85, abs=0.05)


@pytest.mark.asyncio
async def test_exact_best_score_consistency_uncontaminated_by_timer(temp_db: Path):
    """
    Critical Audit Fix:
    Verify that the authoritative criterion for BEST selection is strictly
    the validated technical evaluator final_score (e.g. 0.85) with ZERO
    timing/composite score contamination (e.g. 0.88) in SQLite, question_attempts,
    active_question_attempts, report, and comparisons.
    """
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    cand = get_or_create_candidate(email="consistent_score@test.com", name="Score Consistency", db_path=temp_db)
    cid = cand["id"]
    sid = str(uuid.uuid4())

    mock_eval = MagicMock()
    mock_eval.return_value = {
        "final_score": 0.85,
        "grade": "A",
        "justification": "Optimal technical answer",
        "covered_concepts": ["concept_a", "concept_b"],
        "missing_concepts": [],
        "incorrect_claims": [],
        "strong_points": ["Strong technical accuracy"],
    }

    with patch("services.storage.database.DEFAULT_DB_PATH", temp_db):
        orch = InterviewOrchestrator(
            session_id=sid,
            candidate={"id": cid, "email": "consistent_score@test.com"},
            config={"num_questions": 1, "duration_minutes": 10},
            evaluator_fn=mock_eval,
        )
        orch._question_queue = [
            {"id": "q_strict_score", "text": "Explain synchronization in C.", "difficulty": 3, "type": "verbal"}
        ]
        orch._state["questions"] = list(orch._question_queue)

        await orch.start()
        ans_res = await orch.handle_voice_answer("Mutex locks enforce mutual exclusion.", "q_strict_score")
        fb = ans_res["feedback"]

        # Evaluator raw score must be strictly 0.85
        assert fb["raw_evaluator_score"] == pytest.approx(0.85, abs=1e-4)

        # In SQLite, validated_score and raw_score MUST both be strictly 0.85, NOT contaminated by timing score
        best_db = get_best_attempt(cid, "q_strict_score", db_path=temp_db)
        assert best_db is not None
        assert best_db["raw_score"] == pytest.approx(0.85, abs=1e-4)
        assert best_db["validated_score"] == pytest.approx(0.85, abs=1e-4)

        # In-memory active_question_attempts must also store validated_score = 0.85
        attempts = orch._active_question_attempts["q_strict_score"]
        assert len(attempts) == 1
        assert attempts[0]["validated_score"] == pytest.approx(0.85, abs=1e-4)
        assert attempts[0]["raw_score"] == pytest.approx(0.85, abs=1e-4)

        # Session raw_scores must record 0.85
        assert orch._state["raw_scores"][0] == pytest.approx(0.85, abs=1e-4)

        # Report question_results must report validated_score = 0.85
        rep = await orch.end()
        q_res = rep["question_results"][0]
        assert q_res["raw_score"] == pytest.approx(0.85, abs=1e-4)
        assert q_res["validated_score"] == pytest.approx(0.85, abs=1e-4)
        assert q_res["best_score"] == pytest.approx(0.85, abs=1e-4)


@pytest.mark.asyncio
async def test_explicit_rl_retry_isolation_call_counts(temp_db: Path):
    """
    Critical Audit Fix:
    Intermediate retry submissions of the same question must NOT trigger RL difficulty
    adaptation (Q1 Attempt 1 -> 0, Attempt 2 -> 0, Attempt 3 -> 0).
    RL difficulty adaptation occurs exactly once when the candidate finalizes the turn.
    """
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    cand = get_or_create_candidate(email="rl_isolation@test.com", name="RL Isolation", db_path=temp_db)
    cid = cand["id"]
    sid = str(uuid.uuid4())

    mock_eval = MagicMock()
    mock_eval.return_value = {
        "final_score": 0.40,
        "grade": "C",
        "justification": "Partial explanation",
        "covered_concepts": ["concept_1"],
        "missing_concepts": ["concept_2"],
        "incorrect_claims": [],
    }

    with patch("services.storage.database.DEFAULT_DB_PATH", temp_db):
        orch = InterviewOrchestrator(
            session_id=sid,
            candidate={"id": cid, "email": "rl_isolation@test.com"},
            config={"num_questions": 2, "duration_minutes": 15, "defer_rl": True},
            evaluator_fn=mock_eval,
        )
        orch._decide_and_inject_followup = AsyncMock(return_value=False)
        orch._question_queue = [
            {"id": "q1_rl", "text": "Q1 text", "difficulty": 3, "type": "verbal"},
            {"id": "q2_rl", "text": "Q2 text", "difficulty": 3, "type": "verbal"},
        ]
        orch._state["questions"] = list(orch._question_queue)

        # Spy on _adapt_difficulty
        adapt_call_count = 0
        orig_adapt = orch._adapt_difficulty

        async def spy_adapt(score):
            nonlocal adapt_call_count
            adapt_call_count += 1
            return await orig_adapt(score)

        orch._adapt_difficulty = spy_adapt

        await orch.start()

        # Attempt 1: Submitting intermediate answer
        await orch.handle_voice_answer("First attempt partial answer", "q1_rl")
        assert adapt_call_count == 0, f"Attempt 1 triggered RL adaptation prematurely ({adapt_call_count} calls)"

        # Candidate retries: Attempt 2
        await orch.handle_retry("q1_rl")
        mock_eval.return_value["final_score"] = 0.65
        await orch.handle_voice_answer("Second attempt improved answer", "q1_rl")
        assert adapt_call_count == 0, f"Attempt 2 triggered RL adaptation prematurely ({adapt_call_count} calls)"

        # Candidate retries: Attempt 3
        await orch.handle_retry("q1_rl")
        mock_eval.return_value["final_score"] = 0.85
        await orch.handle_voice_answer("Third attempt strong answer", "q1_rl")
        assert adapt_call_count == 0, f"Attempt 3 triggered RL adaptation prematurely ({adapt_call_count} calls)"

        # Finalize turn by advancing to next question -> Exactly ONE adaptation call!
        await orch.handle_next_question()
        assert adapt_call_count == 1, f"Expected exactly 1 RL adaptation call on turn finalization, got {adapt_call_count}"
        assert orch._current_q_index == 1


@pytest.mark.asyncio
async def test_mandatory_followup_cannot_be_skipped_or_displaced(temp_db: Path):
    """
    Critical Audit Fix:
    Bounded follow-up probes (fu_...) injected after an incomplete/gap answer
    must be presented before advancing to Q2. Re-ordering / rebuilding must NEVER
    displace or wipe out injected follow-ups.
    """
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    cand = get_or_create_candidate(email="followup_guard@test.com", name="Followup Guard", db_path=temp_db)
    cid = cand["id"]
    sid = str(uuid.uuid4())

    mock_eval = MagicMock()
    mock_eval.return_value = {
        "final_score": 0.45,
        "grade": "C",
        "justification": "Candidate missed boundary conditions",
        "covered_concepts": ["initial_loop"],
        "missing_concepts": ["boundary_handling"],
        "incorrect_claims": [],
    }

    mock_select = MagicMock()
    mock_select.return_value = [
        {"id": "q_fresh_replacement", "text": "Replacement Question", "difficulty": 2, "topic": "c_pointers", "type": "verbal"}
    ]

    with patch("services.storage.database.DEFAULT_DB_PATH", temp_db):
        orch = InterviewOrchestrator(
            session_id=sid,
            candidate={"id": cid, "email": "followup_guard@test.com"},
            config={"num_questions": 3, "duration_minutes": 15},
            evaluator_fn=mock_eval,
            select_questions_fn=mock_select,
        )
        orch._question_queue = [
            {"id": "q1_main", "text": "Main Question 1", "difficulty": 2, "topic": "c_pointers", "type": "verbal"},
            {"id": "q2_main", "text": "Main Question 2", "difficulty": 3, "topic": "dsa_trees", "type": "verbal"},
        ]
        orch._state["questions"] = list(orch._question_queue)

        await orch.start()

        # Mock follow-up injection directly
        fu_q = {
            "id": "fu_probe_boundary",
            "text": "How do you handle the NULL pointer boundary?",
            "topic": "c_pointers",  # Note: same topic as Q1 (could trigger repeat penalty without fix)
            "difficulty": 2,
            "type": "verbal",
            "source": "qwen_followup",
            "parent_question_id": "q1_main",
        }
        # Simulate Follow-Up Agent inserting follow-up at index 1
        orch._question_queue.insert(orch._current_q_index + 1, fu_q)

        # Trigger a queue rebuild (which previously wiped out index + 1!)
        orch._rebuild_remaining_questions(new_diff=2)

        # Verify the follow-up was NOT wiped out by _rebuild_remaining_questions
        assert orch._question_queue[1]["id"] == "fu_probe_boundary"

        # Candidate clicks Continue / handle_next_question()
        orch._state["pending_next"] = True
        next_q_envelope = await orch.handle_next_question()

        # The question presented MUST be the injected follow-up, NOT Q2
        served_q = next_q_envelope["payload"]
        assert served_q["id"] == "fu_probe_boundary", f"Expected follow-up, but received: {served_q['id']}"
        assert served_q["parent_question_id"] == "q1_main"


@pytest.mark.asyncio
async def test_rollback_tentative_attempt_preserves_sqlite_history(temp_db: Path):
    """
    Critical Audit Fix:
    Verify that in-memory turn rollback during retries does NOT delete
    or prune historical attempts from SQLite.
    """
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    cand = get_or_create_candidate(email="rollback_safety@test.com", name="Rollback Tester", db_path=temp_db)
    cid = cand["id"]
    sid = str(uuid.uuid4())

    mock_eval = MagicMock()
    mock_eval.return_value = {
        "final_score": 0.50,
        "grade": "C",
        "justification": "Initial attempt",
        "covered_concepts": ["concept_x"],
        "missing_concepts": ["concept_y"],
        "incorrect_claims": [],
    }

    with patch("services.storage.database.DEFAULT_DB_PATH", temp_db):
        orch = InterviewOrchestrator(
            session_id=sid,
            candidate={"id": cid, "email": "rollback_safety@test.com"},
            config={"num_questions": 2, "duration_minutes": 10},
            evaluator_fn=mock_eval,
        )
        orch._question_queue = [
            {"id": "q_rollback_test", "text": "Question for rollback", "difficulty": 2, "type": "verbal"}
        ]
        orch._state["questions"] = list(orch._question_queue)

        await orch.start()
        await orch.handle_voice_answer("Attempt 1 text", "q_rollback_test")

        # Prior to retry, SQLite has 1 attempt
        assert len(get_question_attempts(cid, "q_rollback_test", db_path=temp_db)) == 1

        # Candidate retries -> triggers _rollback_tentative_attempt
        await orch.handle_retry("q_rollback_test")

        # In-memory scores rolled back
        assert len(orch._state["scores"]) == 0

        # SQLite database MUST still retain Attempt 1
        db_attempts = get_question_attempts(cid, "q_rollback_test", db_path=temp_db)
        assert len(db_attempts) == 1, "Rollback erroneously deleted historical attempt from SQLite!"
        assert db_attempts[0]["attempt_number"] == 1


def test_deterministic_best_flag_integrity_five_attempt_sequence_and_ties(temp_db: Path):
    """
    Critical Audit Fix:
    Exact 5-attempt sequence verification:
    A1=0.40, A2=0.70, A3=0.60 -> BEST=A2
    A4=0.85 -> BEST=A4
    A5=0.50 -> BEST=A4
    Also verifies tie-breakers:
    1. Fewer missing concepts wins on score tie
    2. Most recent attempt wins on score and missing concepts tie
    3. Exactly ONE attempt has is_best=1 at every step.
    """
    cand = get_or_create_candidate(email="best_flag@test.com", name="Best Flag Tester", db_path=temp_db)
    cid = cand["id"]
    sid = str(uuid.uuid4())
    qid = "q_five_attempt_seq"

    # Attempt 1: Score 0.40
    r1 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid,
        "attempt_type": "primary", "raw_score": 0.40, "validated_score": 0.40,
        "missing_concepts": ["m1", "m2", "m3"],
    }, db_path=temp_db)
    assert r1["is_best"] is True
    best1 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best1["attempt_number"] == 1

    # Attempt 2: Score 0.70
    r2 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid,
        "attempt_type": "primary", "raw_score": 0.70, "validated_score": 0.70,
        "missing_concepts": ["m1"],
    }, db_path=temp_db)
    assert r2["is_best"] is True
    best2 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best2["attempt_number"] == 2

    # Attempt 3: Score 0.60 (lower) -> BEST remains Attempt 2
    r3 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid,
        "attempt_type": "primary", "raw_score": 0.60, "validated_score": 0.60,
        "missing_concepts": ["m1", "m2"],
    }, db_path=temp_db)
    assert r3["is_best"] is False
    best3 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best3["attempt_number"] == 2

    # Attempt 4: Score 0.85 (higher) -> BEST becomes Attempt 4
    r4 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid,
        "attempt_type": "primary", "raw_score": 0.85, "validated_score": 0.85,
        "missing_concepts": [],
    }, db_path=temp_db)
    assert r4["is_best"] is True
    best4 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best4["attempt_number"] == 4

    # Attempt 5: Score 0.50 (lower) -> BEST remains Attempt 4
    r5 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid,
        "attempt_type": "primary", "raw_score": 0.50, "validated_score": 0.50,
        "missing_concepts": ["m1", "m2"],
    }, db_path=temp_db)
    assert r5["is_best"] is False
    best5 = get_best_attempt(cid, qid, db_path=temp_db)
    assert best5["attempt_number"] == 4

    # Verify exactly ONE attempt has is_best=1
    all_atts = get_question_attempts(cid, qid, db_path=temp_db)
    assert len(all_atts) == 5
    bests = [a for a in all_atts if a["is_best"] == 1]
    assert len(bests) == 1
    assert bests[0]["attempt_number"] == 4

    # ── Test Tie-Breakers on a new question ─────────────────────────────────
    qid_tie = "q_tie_breaker_test"

    # Attempt 1: 0.70 with 2 missing concepts
    t1 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid_tie,
        "attempt_type": "primary", "raw_score": 0.70, "validated_score": 0.70,
        "missing_concepts": ["m1", "m2"],
    }, db_path=temp_db)
    assert t1["is_best"] is True

    # Attempt 2: 0.70 with 1 missing concept -> Wins tie on fewer missing concepts!
    t2 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid_tie,
        "attempt_type": "primary", "raw_score": 0.70, "validated_score": 0.70,
        "missing_concepts": ["m1"],
    }, db_path=temp_db)
    assert t2["is_best"] is True
    best_tie = get_best_attempt(cid, qid_tie, db_path=temp_db)
    assert best_tie["attempt_number"] == 2

    # Attempt 3: 0.70 with 1 missing concept -> Same score and same missing concepts -> Most recent (Attempt 3) wins!
    t3 = save_attempt({
        "candidate_id": cid, "session_id": sid, "question_id": qid_tie,
        "attempt_type": "primary", "raw_score": 0.70, "validated_score": 0.70,
        "missing_concepts": ["m1"],
    }, db_path=temp_db)
    assert t3["is_best"] is True
    best_tie2 = get_best_attempt(cid, qid_tie, db_path=temp_db)
    assert best_tie2["attempt_number"] == 3

    tie_atts = get_question_attempts(cid, qid_tie, db_path=temp_db)
    assert len([a for a in tie_atts if a["is_best"] == 1]) == 1
