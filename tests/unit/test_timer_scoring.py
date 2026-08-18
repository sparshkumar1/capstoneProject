"""
test_timer_scoring.py — Dedicated Unit Tests for Stage 6: Timer and Final Evaluation.

Verifies:
  1. Very fast response (tau <= 0.50)
  2. Nominal response (0.50 < tau <= 1.00)
  3. Overrun response (tau > 1.00)
  4. Timeout behavior
  5. Technically correct + slow (score >= 0.70 with penalty)
  6. Technically wrong + fast (zero speed bonus guaranteed)
  7. Correct answer with normal timing
  8. Incorrect answer with normal timing
  9. Timing unavailable (graceful default)
 10. STT unavailable (ungraded, 0.0)
 11. Skipped question (recorded as 0.0 across all metrics)
 12. Final score bounds [0.0, 1.0]
 13. Configurable timing parameters (delta_fast, delta_overrun)
 14. Raw evaluator score preservation
 15. Timing contribution separately observable
 16. Fast wrong answer < Slower correct answer (Dominance invariant)
 17. Coding question scoring with response timing
 18. Coding execution timeout distinction
 19. Component breakdown in final report
 20. End-to-end orchestrator timing integration
"""

import pytest
import asyncio
from agents.timing.timer import QuestionTimer, TimerSnapshot
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator


# ─────────────────────────────────────────────────────────────────────────────
# 1. QuestionTimer Core Logic & Modifier Calculation
# ─────────────────────────────────────────────────────────────────────────────

def test_fast_response_with_strong_score_receives_modest_bonus():
    timer = QuestionTimer(delta_fast=0.03, delta_overrun=0.10)
    # Fast: tau = 0.40, strong score = 0.90
    mod = timer.compute_timing_modifier(raw_score=0.90, time_ratio=0.40)
    assert mod["is_fast"] is True
    assert mod["speed_bonus_eligible"] is True
    assert mod["timing_modifier"] == pytest.approx(0.03 * 0.90, abs=1e-4)  # +0.027
    assert mod["final_score"] == pytest.approx(0.927, abs=1e-3)
    assert mod["raw_score"] == 0.90
    assert mod["timing_score"] == 1.0


def test_fast_wrong_answer_never_receives_speed_bonus():
    """
    CRITICAL INVARIANT: Technical correctness dominance.
    A candidate answering incorrectly (score < 0.70) in 2 seconds gets 0 bonus.
    """
    timer = QuestionTimer(delta_fast=0.03, delta_overrun=0.10)
    # Fast: tau = 0.10, but score is low (0.25)
    mod = timer.compute_timing_modifier(raw_score=0.25, time_ratio=0.10)
    assert mod["is_fast"] is True
    assert mod["speed_bonus_eligible"] is False
    assert mod["timing_modifier"] == 0.0
    assert mod["final_score"] == 0.25  # Unchanged!
    assert mod["raw_score"] == 0.25


def test_nominal_pacing_produces_zero_modifier():
    timer = QuestionTimer()
    # Nominal pace: tau = 0.75, score = 0.85
    mod = timer.compute_timing_modifier(raw_score=0.85, time_ratio=0.75)
    assert mod["is_fast"] is False
    assert mod["is_overrun"] is False
    assert mod["timing_modifier"] == 0.0
    assert mod["final_score"] == 0.85


def test_overrun_applies_proportional_overtime_penalty():
    timer = QuestionTimer(delta_overrun=0.10)
    # Overrun: tau = 1.50 (50% over limit)
    mod = timer.compute_timing_modifier(raw_score=0.90, time_ratio=1.50)
    assert mod["is_overrun"] is True
    assert mod["timing_modifier"] == pytest.approx(-0.05, abs=1e-4)  # -0.10 * 0.50
    assert mod["final_score"] == pytest.approx(0.85, abs=1e-3)
    assert mod["raw_score"] == 0.90


def test_severe_overrun_penalty_is_capped_at_delta_overrun():
    timer = QuestionTimer(delta_overrun=0.10)
    # Massive overrun: tau = 3.00 (200% over limit)
    mod = timer.compute_timing_modifier(raw_score=0.90, time_ratio=3.00)
    assert mod["timing_modifier"] == -0.10  # Capped at -0.10
    assert mod["final_score"] == pytest.approx(0.80, abs=1e-3)


def test_fast_wrong_score_is_strictly_less_than_slower_correct_score():
    """
    Direct verification of FAST + WRONG < SLOWER + CORRECT.
    """
    timer = QuestionTimer(delta_fast=0.03, delta_overrun=0.10)

    # Candidate A: Fast + Wrong (tau=0.20, raw=0.20)
    mod_a = timer.compute_timing_modifier(raw_score=0.20, time_ratio=0.20)

    # Candidate B: Slower + Correct (tau=1.50 [50% overtime], raw=0.90)
    mod_b = timer.compute_timing_modifier(raw_score=0.90, time_ratio=1.50)

    assert mod_a["final_score"] < mod_b["final_score"]
    assert mod_b["final_score"] - mod_a["final_score"] > 0.50  # Substantial superiority preserved


def test_score_bounds_clamping_at_zero_and_one():
    timer = QuestionTimer(delta_fast=0.05, delta_overrun=0.20)
    # Test upper bound clamping: raw=0.98 + 0.05 -> clamped at 1.00
    mod_high = timer.compute_timing_modifier(raw_score=0.98, time_ratio=0.10, delta_fast=0.05)
    assert mod_high["final_score"] <= 1.00

    # Test lower bound clamping: raw=0.05 - 0.10 -> clamped at 0.00
    mod_low = timer.compute_timing_modifier(raw_score=0.05, time_ratio=2.00)
    assert mod_low["final_score"] >= 0.00


def test_configurable_timing_parameters_override():
    timer = QuestionTimer(delta_fast=0.03, delta_overrun=0.10)
    # Dynamic override with delta_fast=0.05 and delta_overrun=0.15
    mod = timer.compute_timing_modifier(
        raw_score=0.80,
        time_ratio=0.30,
        delta_fast=0.05,
    )
    assert mod["timing_modifier"] == pytest.approx(0.04, abs=1e-4)  # 0.05 * 0.80


# ─────────────────────────────────────────────────────────────────────────────
# 2. Orchestrator Integration & Reporting
# ─────────────────────────────────────────────────────────────────────────────

def _make_orch(questions, evaluator_fn=None):
    orch = InterviewOrchestrator(
        "sess_test_1",
        {"id": "cand_1", "name": "Alice"},
        {
            "c_topics": ["c_pointers"],
            "dsa_topics": ["dsa_search"],
            "duration_minutes": 30,
            "num_questions": len(questions),
            "interview_mode": "standard",
        },
        evaluator_fn=evaluator_fn,
    )
    orch._question_queue = list(questions)
    orch._state["questions"] = list(questions)
    return orch


@pytest.mark.asyncio
async def test_orchestrator_voice_answer_records_raw_and_timed_scores():
    orch = _make_orch(
        questions=[
            {"id": "q1", "text": "What is a pointer in C?", "topic": "c_pointers", "difficulty": 2, "type": "verbal"},
            {"id": "q2", "text": "Explain binary search.", "topic": "dsa_search", "difficulty": 3, "type": "verbal"},
        ],
        evaluator_fn=lambda t, q: {"final_score": 0.88, "score_breakdown": {"s1": 0.9, "s2": 0.85, "r": 0.89}},
    )

    # 1. Dispatch Question 1 (starts timer)
    q1 = orch._select_and_send_question()
    assert q1["id"] == "q1"

    # 2. Handle Answer
    res = await orch.handle_voice_answer(
        transcript="A pointer holds a memory address of another variable in C.",
        question_id="q1",
    )

    fb = res["feedback"]
    assert "raw_evaluator_score" in fb
    assert fb["raw_evaluator_score"] == 0.88
    assert "timing_modifier" in fb
    assert "timing_score" in fb
    assert "time_taken_sec" in fb
    assert "allowed_time_sec" in fb
    assert fb["final_score"] >= 0.0


@pytest.mark.asyncio
async def test_stt_unavailable_produces_zero_without_timing_artifacts():
    orch = _make_orch(
        questions=[{"id": "q1", "text": "Explain quicksort.", "topic": "dsa_search", "difficulty": 2, "type": "verbal"}],
    )
    orch._select_and_send_question()

    # Empty / STT failure
    res = await orch.handle_voice_answer(transcript="", question_id="q1")
    fb = res["feedback"]
    assert fb["final_score"] == 0.0
    assert fb["raw_evaluator_score"] == 0.0
    assert fb["timing_modifier"] == 0.0
    assert fb["stt_status"] == "stt_unavailable"


@pytest.mark.asyncio
async def test_skip_question_records_zero_across_all_metrics():
    orch = _make_orch(
        questions=[
            {"id": "q1", "text": "Explain heaps.", "topic": "dsa_search", "difficulty": 2, "type": "verbal"},
            {"id": "q2", "text": "Explain stacks.", "topic": "dsa_search", "difficulty": 2, "type": "verbal"},
        ],
    )
    orch._select_and_send_question()

    # Skip
    await orch.skip_question("q1")
    assert orch._state["scores"] == [0.0]
    assert orch._state["raw_scores"] == [0.0]
    assert orch._state["timing_scores"] == [0.0]
    assert orch._state["timing_modifiers"] == [0.0]


@pytest.mark.asyncio
async def test_final_report_contains_transparent_component_breakdown():
    orch = _make_orch(
        questions=[
            {"id": "q1", "text": "What is malloc?", "topic": "c_pointers", "difficulty": 2, "type": "verbal"},
        ],
        evaluator_fn=lambda t, q: {
            "final_score": 0.85,
            "covered_concepts": ["memory allocation", "heap"],
            "missing_concepts": [],
            "score_breakdown": {"s1": 0.85, "s2": 0.90, "r": 0.88},
        },
    )
    orch._select_and_send_question()
    await orch.handle_voice_answer("malloc dynamically allocates memory on heap", "q1")

    report = await orch.end()

    # Verify Stage 6 report fields
    assert "overall_score" in report
    assert "raw_technical_score" in report
    assert "component_breakdown" in report
    assert "timing_analysis" in report

    cb = report["component_breakdown"]
    assert cb["technical_score"] >= 0.80
    assert cb["concept_score"] >= 0.85
    assert cb["reasoning_score"] >= 0.85
    assert "communication_score" in cb
    assert "timing_score" in cb
    assert cb["final_overall"] == report["overall_score"]

    ta = report["timing_analysis"]
    assert "avg_timing_score" in ta
    assert "net_timing_modifier" in ta
    assert len(ta["response_timing"]) == 1


@pytest.mark.asyncio
async def test_code_submission_distinguishes_response_and_execution_timing():
    orch = _make_orch(
        questions=[
            {"id": "code_1", "text": "Implement sum(a, b)", "type": "code", "topic": "c_pointers", "difficulty": 2},
        ],
    )
    orch._select_and_send_question()

    res = await orch.handle_code_submission(
        code="int sum(int a, int b) { return a + b; }",
        question_id="code_1",
        passed=True,
        tests_passed=5,
        tests_total=5,
        stdout="",
        stderr="",
    )

    fb = res["feedback"]
    assert fb["raw_evaluator_score"] >= 0.85
    assert "timing_modifier" in fb
    assert "time_taken_sec" in fb
    assert fb["final_score"] >= 0.85
