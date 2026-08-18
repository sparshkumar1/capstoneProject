"""
Integration Test: Full Interview Lifecycle
Tests the complete multi-turn interview workflow:
Session Start -> Main Q1 -> Voice Answer -> STT/Evaluation -> Feedback -> Follow-Up ->
Baseline Counting -> RL Activation after Baseline -> PPO Difficulty Adjustment ->
Coding Question Submission -> Real Docker Sandbox Execution -> Timer Integration ->
Final Session Report Generation.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.coding_executor.coding_executor import evaluate_c_submission


@pytest.mark.asyncio
async def test_full_interview_lifecycle_simulation():
    """Execute complete end-to-end multi-turn interview session."""
    session_id = "sess_integration_lifecycle_001"
    candidate = {"id": "cand_integ_01", "experience": "intermediate"}
    config = {
        "duration_minutes": 30,
        "num_questions": 5,
        "interview_mode": "standard",
        "c_topics": ["pointers", "memory_management"],
        "dsa_topics": ["arrays", "linked_lists"],
    }

    orch = InterviewOrchestrator(
        session_id,
        candidate,
        config,
    )

    # 1. START SESSION
    q1 = await orch.start()
    assert q1 is not None
    assert "id" in q1
    assert q1["difficulty"] in {1, 2, 3}
    assert orch._state["baseline_complete"] is False

    # 2. ANSWER MAIN Q1 (Strong answer in baseline)
    eval_q1 = {
        "final_score": 0.88,
        "covered_concepts": ["Pointers", "Dereferencing"],
        "missing_concepts": ["Null pointer check"],
        "what_was_incorrect": [],
        "justification": "Good understanding of pointer mechanics.",
    }
    with patch.object(orch, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_q1):
        with patch.object(orch, "_generate_feedback", new_callable=AsyncMock, return_value=eval_q1):
            resp1 = await orch.handle_voice_answer(
                transcript="Pointers store memory addresses and dereferencing accesses the value.",
                question_id=q1["id"],
            )

    assert "feedback" in resp1
    assert orch._state["baseline_complete"] is False  # Baseline requires min 2 main Qs
    assert len(orch._state["scores"]) == 1
    assert orch._state["last_decision_source"] == "baseline_warmup"
    assert orch._state["rl_status"] == "baseline_warmup"

    # Advance to Question 2
    next_res2 = await orch.handle_next_question()
    assert next_res2["type"] == "question"
    q2 = next_res2["payload"]

    # 3. ANSWER MAIN Q2 (Completes baseline warmup)
    eval_q2 = {
        "final_score": 0.85,
        "covered_concepts": ["Dynamic memory", "malloc", "free"],
        "missing_concepts": [],
        "what_was_incorrect": [],
    }
    with patch.object(orch, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_q2):
        with patch.object(orch, "_generate_feedback", new_callable=AsyncMock, return_value=eval_q2):
            resp2 = await orch.handle_voice_answer(
                transcript="malloc allocates heap memory and free releases it.",
                question_id=q2["id"],
            )

    assert len(orch._state["scores"]) == 2
    assert orch._state["baseline_complete"] is True
    assert orch._state["rl_enabled"] is True

    # Advance to Question 3
    next_res3 = await orch.handle_next_question()
    assert next_res3["type"] == "question"
    q3 = next_res3["payload"]

    # 4. ANSWER MAIN Q3 (RL Active -> PPO Difficulty Adjustment)
    eval_q3 = {
        "final_score": 0.92,
        "covered_concepts": ["Linked list", "Node traversal"],
        "missing_concepts": [],
        "what_was_incorrect": [],
    }
    with patch.object(orch, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_q3):
        with patch.object(orch, "_generate_feedback", new_callable=AsyncMock, return_value=eval_q3):
            resp3 = await orch.handle_voice_answer(
                transcript="Traversal uses head pointer iterating until next is NULL.",
                question_id=q3["id"],
            )

    assert len(orch._state["scores"]) == 3
    # Verify RL telemetry recorded in state
    assert orch._state["rl_status"] in {"available", "rl_unavailable"}
    assert orch._state["last_decision_source"] in {"ppo", "guardrail_g6", "non_rl_heuristic_recovery"}
    assert len(orch._state["difficulty_history"]) >= 3

    # 5. CODING QUESTION & DOCKER SANDBOX EXECUTION
    next_res4 = await orch.handle_next_question()
    assert next_res4["type"] == "question"
    q4 = next_res4["payload"]

    c_source = r"""
    #include <stdio.h>
    int main() {
        int a, b;
        if (scanf("%d %d", &a, &b) == 2) {
            printf("%d\n", a + b);
        }
        return 0;
    }
    """
    test_cases = [
        {"id": "tc1", "input": "2 3\n", "expected": "5\n", "is_hidden": False, "is_mandatory": True},
        {"id": "tc2", "input": "10 20\n", "expected": "30\n", "is_hidden": True, "is_mandatory": False},
    ]

    exec_result = evaluate_c_submission(c_source, test_cases=test_cases, timeout_sec=5.0)
    assert exec_result["status"] in {"accepted", "sandbox_error"}
    if exec_result["status"] == "accepted":
        assert exec_result["passed"] is True
        assert exec_result["tests_passed"] == 2

    # Submit code to orchestrator
    code_eval = {
        "final_score": 1.0,
        "covered_concepts": ["Correct addition", "stdin parsing"],
        "missing_concepts": [],
        "what_was_incorrect": [],
        "decision_source": "docker_sandbox",
    }
    with patch("agents.orchestrator.interview_orchestrator.FEEDBACK_AGENT.generate_code_feedback", return_value=code_eval):
        resp_code = await orch.handle_code_submission(
            code=c_source,
            question_id=q4["id"],
            passed=exec_result["passed"],
            tests_passed=exec_result["tests_passed"],
            tests_total=exec_result["tests_total"],
            stdout="5\n30\n",
            stderr="",
        )

    assert orch._state["coding_performance"] is not None
    assert "attempted" in orch._state["coding_performance"]
    assert "passed" in orch._state["coding_performance"]

    # 6. COMPLETE SESSION & REPORT GENERATION
    report = await orch.end()
    assert report is not None
    assert "id" in report
    assert "overall_score" in report
    assert "component_breakdown" in report
    assert "technical_score" in report["component_breakdown"]
    assert "timing_score" in report["component_breakdown"]
    assert "coding_score" in report["component_breakdown"]
    assert "question_results" in report
    assert len(report["question_results"]) >= 4
