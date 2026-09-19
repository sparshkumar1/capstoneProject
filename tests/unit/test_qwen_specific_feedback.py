"""
Unit tests for Question-Specific, Concept-Grounded, and Attempt-Aware Qwen Feedback.

Run with:
    pytest tests/unit/test_qwen_specific_feedback.py -v
"""

from __future__ import annotations

import pytest

from agents.orchestrator.feedback_agent import FeedbackAgent
from services.qwen.app import (
    FeedbackRequest,
    FeedbackResponse,
    _build_feedback_prompt,
    _synthesize_structured_feedback,
    _validate_feedback_output,
)


# ── 1. Schema Validation ──────────────────────────────────────────────────────

def test_feedback_request_response_schemas():
    """Verify schemas serialize multi-attempt and comparison fields accurately."""
    req = FeedbackRequest(
        question_text="What is a memory leak in C?",
        topic="memory_management",
        candidate_answer="Allocating memory without freeing it.",
        structured_evaluation={
            "final_score": 0.85,
            "grade": "A",
            "correct_claims": ["allocated memory not freed"],
            "missing_concepts": ["valgrind", "pointer reassignment"],
        },
        attempt_number=2,
        previous_best_answer="Memory leak is when memory stays.",
        previous_best_score=0.50,
        resolved_concepts=["allocated memory not freed"],
        remaining_concepts=["valgrind"],
        score_delta=0.35,
    )

    assert req.attempt_number == 2
    assert req.previous_best_score == 0.50
    assert req.score_delta == 0.35
    assert req.resolved_concepts == ["allocated memory not freed"]

    resp = _synthesize_structured_feedback(req)
    assert isinstance(resp, FeedbackResponse)
    assert resp.attempt_number == 2
    assert resp.comparison is not None
    assert resp.comparison["score_delta"] == 0.35
    assert "allocated memory not freed" in resp.comparison["resolved_concepts"]


# ── 2. Re-Attempt Feedback Differentiation & Grounding ────────────────────────

def test_synthesize_feedback_attempt_awareness():
    """
    Attempt 1 vs Attempt 2 must produce differentiated feedback:
    Attempt 2 must explicitly recognize the retry, praise resolved gaps, and identify remaining targets.
    """
    # Attempt 1
    req1 = FeedbackRequest(
        question_text="Explain segmentation faults.",
        topic="pointers",
        candidate_answer="It happens when accessing memory.",
        structured_evaluation={
            "final_score": 0.40,
            "grade": "C",
            "correct_claims": ["invalid memory access"],
            "missing_concepts": ["NULL pointer dereference", "buffer overflow"],
        },
        attempt_number=1,
    )
    resp1 = _synthesize_structured_feedback(req1)
    assert resp1.attempt_number == 1
    assert "Re-attempt" not in resp1.narrative_feedback
    assert any("NULL pointer dereference" in item for item in resp1.actionable_improvements)

    # Attempt 2: Resolved NULL pointer dereference
    req2 = FeedbackRequest(
        question_text="Explain segmentation faults.",
        topic="pointers",
        candidate_answer="It occurs when dereferencing a NULL pointer or accessing out-of-bounds memory.",
        structured_evaluation={
            "final_score": 0.80,
            "grade": "B+",
            "correct_claims": ["NULL pointer dereference", "out-of-bounds memory"],
            "missing_concepts": ["OS signal SIGSEGV"],
        },
        attempt_number=2,
        previous_best_answer=req1.candidate_answer,
        previous_best_score=0.40,
        resolved_concepts=["NULL pointer dereference"],
        remaining_concepts=["OS signal SIGSEGV"],
        score_delta=0.40,
    )
    resp2 = _synthesize_structured_feedback(req2)
    assert resp2.attempt_number == 2
    assert "[Attempt #2]" in resp2.narrative_feedback
    assert "Successfully addressed previous gaps: NULL pointer dereference" in resp2.narrative_feedback
    assert resp2.comparison["score_delta"] == 0.40


# ── 3. Prompt Construction Includes Context ───────────────────────────────────

def test_prompt_builder_includes_attempt_context():
    """Verify prompt builder instructs the LLM with candidate history and delta."""
    req = FeedbackRequest(
        question_text="How does binary search work?",
        topic="algorithms",
        candidate_answer="Divide the array in half each time.",
        structured_evaluation={
            "final_score": 0.70,
            "grade": "B",
            "correct_claims": ["halving search space"],
            "missing_concepts": ["sorted array prerequisite", "log N complexity"],
        },
        attempt_number=2,
        previous_best_answer="Check middle element.",
        previous_best_score=0.45,
        resolved_concepts=["halving search space"],
        remaining_concepts=["sorted array prerequisite"],
        score_delta=0.25,
    )

    prompt = _build_feedback_prompt(req)
    assert "RE-ATTEMPT CONTEXT:" in prompt
    assert "Attempt Number: 2" in prompt
    assert "Previous Best Score: 0.45" in prompt
    assert "Score Delta: +0.25" in prompt
    assert "Resolved Concepts in this attempt: halving search space" in prompt
    assert "Still Remaining Gaps: sorted array prerequisite" in prompt


# ── 4. Output Validation Guardrails ───────────────────────────────────────────

def test_validate_feedback_output_rejects_empty_and_boilerplate():
    """Validator must reject empty responses, degenerate strings, and pure boilerplate."""
    req = FeedbackRequest(
        question_text="Test question",
        candidate_answer="Test answer",
    )

    # Empty / None
    assert _validate_feedback_output(None, req) is False
    assert _validate_feedback_output({}, req) is False

    # Degenerate / Short
    assert _validate_feedback_output({"narrative_feedback": "Short"}, req) is False

    # Pure generic boilerplate
    assert _validate_feedback_output({"narrative_feedback": "Good job", "how_to_answer": "valid how to answer here"}, req) is False
    assert _validate_feedback_output({"narrative_feedback": "nice try", "how_to_answer": "valid how to answer here"}, req) is False

    # Valid comprehensive response
    valid_data = {
        "narrative_feedback": "Candidate clearly explained pointer dereferencing with correct syntax, but missed checking for NULL before accessing memory.",
        "how_to_answer": "Explain the concept, provide syntax, and mention edge cases such as NULL checks.",
    }
    assert _validate_feedback_output(valid_data, req) is True


# ── 5. FeedbackAgent Multi-Attempt Integration ────────────────────────────────

@pytest.mark.asyncio
async def test_feedback_agent_passes_attempt_and_comparison():
    """FeedbackAgent must accept and return attempt_number and comparison payload."""
    agent = FeedbackAgent()

    eval_result = {
        "final_score": 0.75,
        "grade": "B",
        "correct_claims": ["malloc allocation"],
        "missing_concepts": ["free", "memory leak"],
        "covered_concepts": ["malloc allocation"],
    }
    question = {
        "id": "c_mem_1",
        "text": "Explain malloc in C.",
        "topic": "memory",
    }
    comparison = {
        "has_previous_best": True,
        "previous_best_score": 0.50,
        "score_delta": 0.25,
        "resolved_concepts": ["malloc allocation"],
        "remaining_concepts": ["free"],
    }

    # Verbal feedback
    res = await agent.generate(
        transcript="malloc allocates memory on the heap.",
        question=question,
        eval_result=eval_result,
        attempt_number=2,
        comparison=comparison,
    )
    assert res["attempt_number"] == 2
    assert res["comparison"] == comparison
    assert res["final_score"] == 0.75

    # Code feedback
    code_res = agent.generate_code_feedback(
        code="int *p = malloc(sizeof(int));",
        passed=True,
        tests_passed=3,
        tests_total=3,
        stdout="OK",
        stderr="",
        question=question,
        attempt_number=2,
        comparison=comparison,
    )
    assert code_res["attempt_number"] == 2
    assert code_res["comparison"] == comparison


# ── 6. Contradiction & Score-Leakage Guardrail Tests ──────────────────────────

def test_validate_feedback_output_rejects_contradictions():
    """Validator must reject feedback claiming a concept was correctly covered when evaluator marked it missing."""
    req = FeedbackRequest(
        question_text="Explain Two Sum logic.",
        topic="arrays",
        candidate_answer="I loop through the array.",
        structured_evaluation={
            "final_score": 0.40,
            "grade": "C",
            "correct_claims": ["array iteration"],
            "missing_concepts": ["hash map lookup", "complement calculation"],
        },
    )

    # 1. Contradiction in what_was_correct list
    contradictory_list = {
        "what_was_correct": ["hash map lookup"],
        "narrative_feedback": "Candidate attempted iteration but needs more depth in the implementation.",
        "how_to_answer": "Use a hash map to look up the complement in O(1) time.",
    }
    assert _validate_feedback_output(contradictory_list, req) is False

    # 2. Contradiction in narrative prose
    contradictory_prose = {
        "what_was_correct": ["array iteration"],
        "narrative_feedback": "You correctly explained hash map lookup and solved the problem.",
        "how_to_answer": "Use a hash map to look up the complement in O(1) time.",
    }
    assert _validate_feedback_output(contradictory_prose, req) is False


def test_validate_feedback_output_rejects_score_leakage():
    """Validator must reject LLM output that attempts to inject raw evaluator scores or percentages."""
    req = FeedbackRequest(
        question_text="Explain malloc in C.",
        candidate_answer="Allocates heap memory.",
        structured_evaluation={"final_score": 0.85, "grade": "A"},
    )

    score_leak = {
        "narrative_feedback": "Score: 0.85 achieved with clear explanation of heap allocation mechanics.",
        "how_to_answer": "Explain malloc returns a void pointer to allocated heap memory.",
    }
    assert _validate_feedback_output(score_leak, req) is False

    semantic_leak = {
        "narrative_feedback": "Semantic 90% reached on pointer allocation mechanics with clear explanation.",
        "how_to_answer": "Explain malloc returns a void pointer to allocated heap memory.",
    }
    assert _validate_feedback_output(semantic_leak, req) is False


def test_feedback_cannot_alter_authoritative_evaluator_score():
    """Adversarial or malformed feedback must never alter the authoritative score or grade."""
    eval_result = {
        "final_score": 0.7250,
        "grade": "B+",
        "correct_claims": ["allocated heap memory"],
        "missing_concepts": ["free", "null check"],
    }
    req = FeedbackRequest(
        question_text="Explain malloc.",
        candidate_answer="Allocates memory.",
        structured_evaluation=eval_result,
        attempt_number=1,
    )

    resp = _synthesize_structured_feedback(req)
    # Technical score and grade must remain strictly identical to evaluator
    assert resp.final_score == 0.7250
    assert resp.grade == "B+"
    assert resp.what_was_correct == ["allocated heap memory"]
    assert "free" in resp.missing_concepts

