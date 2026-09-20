"""
Regression tests: an incorrect answer must never become the authoritative best answer.

Eligibility comes from the existing authoritative evaluation (services/storage/best_answer.py):
correct or partially correct attempts only. Ranking among eligible attempts is the pre-existing deterministic
selector (validated_score, fewest missing concepts, most recent). Backend-authoritative: SQLite selection,
orchestrator feedback payload and the /api/history response all use the same rule.

Run with:
    EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest tests/unit/test_best_answer_authority.py -q
"""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.storage.best_answer import CORRECT, INCORRECT, PARTIAL, classify_attempt, select_best
from services.storage.database import (
    get_best_attempt,
    get_connection,
    get_or_create_candidate,
    get_question_attempts,
    init_db,
    save_attempt,
)

# validated scores placed inside the evaluator's grade bands (Good/Excellent >= .60, Average >= .40, Poor < .40)
SCORE = {"C": 0.90, "P": 0.50, "I": 0.10}
LABEL = {"C": CORRECT, "P": PARTIAL, "I": INCORRECT}


@pytest.fixture
def temp_db(tmp_path: Path):
    db_file = tmp_path / "best_answer.db"
    init_db(db_file)
    return db_file


@pytest.fixture
def cq(temp_db):
    cand = get_or_create_candidate(f"{uuid.uuid4().hex}@t.dev", "T", db_path=temp_db)
    return cand["id"], "q_best"


def _attempt(cid, qid, kind, **extra):
    a = {
        "candidate_id": cid, "session_id": "s1", "question_id": qid, "attempt_type": "primary",
        "answer_type": "verbal", "transcript": f"answer-{kind}", "raw_score": SCORE[kind],
        "validated_score": SCORE[kind], "missing_concepts": [],
    }
    a.update(extra)
    return a


def _best_number(cid, qid, db):
    best = get_best_attempt(cid, qid, db_path=db)
    return best["attempt_number"] if best else None


def _flag_count(cid, qid, db):
    return sum(1 for a in get_question_attempts(cid, qid, db_path=db) if a["is_best"] == 1)


# ── classification uses the existing evaluator semantics ─────────────────────

def test_classification_bands_follow_evaluator_grades():
    assert classify_attempt({"validated_score": 0.75}) == CORRECT      # Excellent
    assert classify_attempt({"validated_score": 0.60}) == CORRECT      # Good
    assert classify_attempt({"validated_score": 0.59}) == PARTIAL      # Average
    assert classify_attempt({"validated_score": 0.40}) == PARTIAL
    assert classify_attempt({"validated_score": 0.39}) == INCORRECT    # Poor
    assert classify_attempt({"validated_score": 0.0}) == INCORRECT     # evaluator/STT unavailable
    assert classify_attempt({"validated_score": float("nan")}) == INCORRECT
    assert classify_attempt({}) == INCORRECT


def test_qwen_or_feedback_grade_cannot_promote_an_incorrect_attempt():
    a = {"validated_score": 0.10, "feedback_json": {"grade": "Excellent", "status": "accepted",
                                                    "justification": "great language, confident"}}
    assert classify_attempt(a) == INCORRECT           # verbal: status/grade text is ignored, score decides


def test_code_verdict_classification():
    code = lambda **fb: {"answer_type": "code", "validated_score": 0.95, "feedback_json": fb}
    assert classify_attempt(code(status="accepted", passed=True)) == CORRECT
    assert classify_attempt(code(status="wrong_answer", passed=False, tests_passed=2, tests_total=5)) == PARTIAL
    assert classify_attempt(code(status="wrong_answer", passed=False, tests_passed=0, tests_total=5)) == INCORRECT
    assert classify_attempt(code(status="compilation_error", passed=False, tests_passed=0)) == INCORRECT
    assert classify_attempt(code(status="sandbox_error", passed=False, tests_passed=0)) == INCORRECT


# ── required behaviour, cases A-J (SQLite selector, backend authority) ───────

@pytest.mark.parametrize("seq, expected_best_after_each", [
    ("I",   [None]),                 # A  incorrect only            -> no best
    ("P",   [1]),                    # B  partial only              -> partial best
    ("C",   [1]),                    # C  correct only              -> correct best
    ("CI",  [1, 1]),                 # D  correct -> incorrect      -> correct remains
    ("PI",  [1, 1]),                 # E  partial -> incorrect      -> partial remains
    ("IP",  [None, 2]),              # F  incorrect -> partial      -> partial becomes best
    ("PC",  [1, 2]),                 # G  partial -> correct        -> correct becomes best
    ("II",  [None, None]),           # H  incorrect -> incorrect    -> no best
    ("CP",  [1, 1]),                 # I  correct -> partial        -> existing ranking (score) decides
    ("ICI", [None, 2, 2]),           #    incorrect, correct, later incorrect
    ("IIP", [None, None, 3]),
])
def test_best_answer_sequences(temp_db, cq, seq, expected_best_after_each):
    cid, qid = cq
    for i, kind in enumerate(seq):
        res = save_attempt(_attempt(cid, qid, kind), db_path=temp_db)
        expected = expected_best_after_each[i]
        assert _best_number(cid, qid, temp_db) == expected, (seq, i)
        assert res["is_best"] is (expected == i + 1), (seq, i)          # "new best" only if it actually became best
        assert (res["current_best"] or {}).get("attempt_number") == expected
        assert _flag_count(cid, qid, temp_db) == (0 if expected is None else 1)


def test_J_later_incorrect_with_higher_raw_score_does_not_displace_earlier_correct(temp_db, cq):
    cid, qid = cq
    save_attempt(_attempt(cid, qid, "C", answer_type="code", transcript="", code_submitted="good();",
                          feedback_json={"status": "accepted", "passed": True, "tests_passed": 3, "tests_total": 3},
                          validated_score=0.85, raw_score=0.85), db_path=temp_db)
    later = save_attempt(_attempt(cid, qid, "I", answer_type="code", transcript="", code_submitted="bad();",
                                  feedback_json={"status": "wrong_answer", "passed": False, "tests_passed": 0,
                                                 "tests_total": 3},
                                  validated_score=0.97, raw_score=0.97,       # higher auxiliary/raw score
                                  missing_concepts=[]), db_path=temp_db)
    assert later["is_best"] is False
    best = get_best_attempt(cid, qid, db_path=temp_db)
    assert best["attempt_number"] == 1 and best["code_submitted"] == "good();"


def test_latest_and_retry_order_cannot_make_incorrect_best(temp_db, cq):
    cid, qid = cq
    for kind in "PIII":
        save_attempt(_attempt(cid, qid, kind), db_path=temp_db)
    assert _best_number(cid, qid, temp_db) == 1


def test_partial_code_attempt_can_be_best_but_zero_test_attempt_cannot(temp_db, cq):
    cid, qid = cq
    r0 = save_attempt(_attempt(cid, qid, "I", answer_type="code", transcript="", code_submitted="x",
                               feedback_json={"status": "wrong_answer", "passed": False, "tests_passed": 0}),
                      db_path=temp_db)
    assert r0["is_best"] is False and get_best_attempt(cid, qid, db_path=temp_db) is None
    r1 = save_attempt(_attempt(cid, qid, "I", answer_type="code", transcript="", code_submitted="y",
                               validated_score=0.35, raw_score=0.35,
                               feedback_json={"status": "wrong_answer", "passed": False, "tests_passed": 1,
                                              "tests_total": 3}), db_path=temp_db)
    assert r1["is_best"] is True and _best_number(cid, qid, temp_db) == 2


def test_legacy_incorrect_best_flag_is_not_trusted(temp_db, cq):
    """Rows written by the old selector (incorrect attempt flagged is_best=1) are not returned as best."""
    cid, qid = cq
    save_attempt(_attempt(cid, qid, "I"), db_path=temp_db)
    conn = get_connection(temp_db)
    try:
        with conn:
            conn.execute("UPDATE question_attempts SET is_best = 1 WHERE candidate_id = ?;", (cid,))
    finally:
        conn.close()
    assert get_best_attempt(cid, qid, db_path=temp_db) is None
    res = save_attempt(_attempt(cid, qid, "I"), db_path=temp_db)
    assert res["previous_best"] is None and res["is_best"] is False
    assert _flag_count(cid, qid, temp_db) == 0                          # stale flag cleared
    res = save_attempt(_attempt(cid, qid, "P"), db_path=temp_db)
    assert res["is_best"] is True and _best_number(cid, qid, temp_db) == 3


def test_pure_selector_excludes_followups_and_ineligible():
    pool = [
        {"attempt_type": "followup", "validated_score": 0.99, "attempt_number": 3},
        {"attempt_type": "primary", "validated_score": 0.30, "attempt_number": 2},
    ]
    assert select_best(pool) is None
    pool.append({"attempt_type": "primary", "validated_score": 0.45, "attempt_number": 1})
    assert select_best(pool)["attempt_number"] == 1


# ── API: backend history endpoint reports no best answer for incorrect-only history ──

def test_history_api_has_no_best_attempt_for_incorrect_only(temp_db, cq):
    from apps.backend.main import get_history_for_question
    cid, qid = cq
    save_attempt(_attempt(cid, qid, "I", transcript="I don't know, something about the weather."), db_path=temp_db)
    with patch("services.storage.database.DEFAULT_DB_PATH", temp_db):
        out = asyncio.run(get_history_for_question(cid, qid))
        assert out["total_attempts"] == 1 and out["best_attempt"] is None
        save_attempt(_attempt(cid, qid, "P", transcript="Pointers hold addresses."), db_path=temp_db)
        out = asyncio.run(get_history_for_question(cid, qid))
        assert out["best_attempt"]["transcript"] == "Pointers hold addresses."


# ── orchestrator feedback payload (screenshot-like regression) ───────────────

def _eval(score, grade, covered, missing):
    return {"final_score": score, "grade": grade, "justification": "x", "covered_concepts": covered,
            "missing_concepts": missing, "incorrect_claims": [], "strong_points": [], "communication_tips": []}


NON_RESPONSIVE = "Um, I think it is blue. I had lunch earlier and the weather is nice."


@pytest.mark.asyncio
async def test_orchestrator_non_responsive_answer_is_never_reported_as_best(temp_db):
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
    c = get_or_create_candidate("nonresp@t.dev", "NR", db_path=temp_db)
    ev = MagicMock(return_value=_eval(0.12, "Poor", [], ["dereference", "null_check"]))
    with patch("services.storage.database.DEFAULT_DB_PATH", temp_db):
        orch = InterviewOrchestrator(
            session_id=str(uuid.uuid4()),
            candidate={"id": c["id"], "email": "nonresp@t.dev", "name": "NR", "experience": "intermediate"},
            config={"num_questions": 3, "duration_minutes": 15}, evaluator_fn=ev)
        orch._question_queue = [{"id": "q_nr", "text": "Explain pointer dereferencing in C.", "difficulty": 2,
                                 "type": "verbal"},
                                {"id": "q_nr2", "text": "Explain malloc.", "difficulty": 2, "type": "verbal"}]
        orch._state["questions"] = list(orch._question_queue)
        await orch.start()

        r1 = (await orch.handle_voice_answer(NON_RESPONSIVE, "q_nr"))["feedback"]
        assert r1["is_best"] is False and r1["authoritative_best_answer"] is False and r1["best_answer"] is None
        await orch.handle_retry("q_nr")
        r2 = (await orch.handle_voice_answer(NON_RESPONSIVE + " Also I like cats.", "q_nr"))["feedback"]
        # previously: a later/higher-scoring incorrect answer became "New Best Answer"
        assert r2["is_best"] is False and r2["authoritative_best_answer"] is False and r2["best_answer"] is None
        assert (r2.get("comparison") or {}).get("has_previous_best") is False
        assert get_best_attempt(c["id"], "q_nr", db_path=temp_db) is None

        # a partially correct retry becomes the best; a later non-responsive answer does not displace it
        await orch.handle_retry("q_nr")
        ev.return_value = _eval(0.50, "Average", ["pointer_intro"], ["null_check"])
        r3 = (await orch.handle_voice_answer("Pointers store memory addresses.", "q_nr"))["feedback"]
        assert r3["is_best"] is True and r3["authoritative_best_answer"] is True
        assert r3["best_answer"]["answer"] == "Pointers store memory addresses."
        await orch.handle_retry("q_nr")
        ev.return_value = _eval(0.12, "Poor", [], ["dereference", "null_check"])
        r4 = (await orch.handle_voice_answer(NON_RESPONSIVE, "q_nr"))["feedback"]
        assert r4["is_best"] is False and r4["authoritative_best_answer"] is True
        assert r4["best_answer"]["answer"] == "Pointers store memory addresses."      # previous valid best remains
        assert r4["comparison"]["has_previous_best"] is True


@pytest.mark.asyncio
async def test_orchestrator_without_persistence_applies_same_rule():
    """No candidate id => no SQLite; the in-memory fallback must not default is_best to True."""
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
    ev = MagicMock(return_value=_eval(0.12, "Poor", [], ["dereference"]))
    orch = InterviewOrchestrator(session_id=str(uuid.uuid4()),
                                 candidate={"id": "", "email": "", "name": "NoDB", "experience": "intermediate"},
                                 config={"num_questions": 3, "duration_minutes": 15}, evaluator_fn=ev)
    orch._question_queue = [{"id": "q_mem", "text": "Explain pointers.", "difficulty": 2, "type": "verbal"},
                            {"id": "q_mem2", "text": "Explain malloc.", "difficulty": 2, "type": "verbal"}]
    orch._state["questions"] = list(orch._question_queue)
    await orch.start()
    r1 = (await orch.handle_voice_answer(NON_RESPONSIVE, "q_mem"))["feedback"]
    assert r1["is_best"] is False and r1["authoritative_best_answer"] is False and r1["best_answer"] is None
    await orch.handle_retry("q_mem")
    ev.return_value = _eval(0.55, "Average", ["a"], ["b"])
    r2 = (await orch.handle_voice_answer("Pointers hold addresses.", "q_mem"))["feedback"]
    assert r2["is_best"] is True and r2["best_answer"]["answer"] == "Pointers hold addresses."
    await orch.handle_retry("q_mem")
    ev.return_value = _eval(0.12, "Poor", [], ["a", "b"])
    r3 = (await orch.handle_voice_answer(NON_RESPONSIVE, "q_mem"))["feedback"]
    assert r3["is_best"] is False and r3["best_answer"]["answer"] == "Pointers hold addresses."


# ── F. execution-failure statuses fail closed (independent audit hardening) ──

@pytest.mark.parametrize("status", ["timeout", "runtime_error", "memory_limit", "policy_blocked",
                                    "sandbox_error", "compilation_error", "wrong_answer", "some_future_status"])
def test_F_execution_failure_status_without_passed_flag_is_never_eligible(status):
    # no `passed` flag, no tests_passed, and a stale/auxiliary score that would otherwise look "correct"
    a = {"answer_type": "code", "validated_score": 0.97, "feedback_json": {"status": status, "grade": "A",
         "justification": "confident, well-explained, latest attempt"}}
    assert classify_attempt(a) == INCORRECT
    assert select_best([{**a, "attempt_type": "primary", "attempt_number": 9}]) is None


@pytest.mark.parametrize("status", ["timeout", "runtime_error", "memory_limit", "policy_blocked"])
def test_F_failure_status_with_passed_tests_is_partial_and_contradictory_passed_flag_cannot_promote(status):
    partial = {"answer_type": "code", "validated_score": 0.2,
               "feedback_json": {"status": status, "tests_passed": 2, "tests_total": 5}}
    assert classify_attempt(partial) == PARTIAL
    contradictory = {"answer_type": "code", "validated_score": 0.99,
                     "feedback_json": {"status": status, "passed": True, "tests_passed": 0}}
    assert classify_attempt(contradictory) == INCORRECT          # explicit failing verdict wins over a stale flag


def test_F_accepted_and_passed_flag_semantics_preserved():
    assert classify_attempt({"answer_type": "code", "validated_score": 0.1,
                             "feedback_json": {"status": "accepted"}}) == CORRECT
    assert classify_attempt({"answer_type": "code", "validated_score": 0.1,
                             "feedback_json": {"passed": True}}) == CORRECT            # no status recorded
    assert classify_attempt({"answer_type": "code", "validated_score": 0.99,
                             "feedback_json": {"passed": False, "tests_passed": 0}}) == INCORRECT


def test_F_stale_score_cannot_displace_earlier_correct_via_timeout(temp_db, cq):
    cid, qid = cq
    save_attempt(_attempt(cid, qid, "C", answer_type="code", transcript="", code_submitted="ok();",
                          feedback_json={"status": "accepted", "passed": True}, validated_score=0.8,
                          raw_score=0.8), db_path=temp_db)
    res = save_attempt(_attempt(cid, qid, "I", answer_type="code", transcript="", code_submitted="loop();",
                                feedback_json={"status": "timeout"}, validated_score=0.99, raw_score=0.99),
                       db_path=temp_db)
    assert res["is_best"] is False
    assert get_best_attempt(cid, qid, db_path=temp_db)["code_submitted"] == "ok();"
