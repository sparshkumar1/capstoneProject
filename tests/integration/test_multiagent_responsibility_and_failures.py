"""
Integration Test: Multi-Agent Responsibility & Failure Semantics
Verifies:
1. Clear separation of agent responsibilities (Evaluator, Follow-Up Agent, Feedback Agent,
   RL Difficulty Agent, Docker Sandbox, Timer, Orchestrator).
2. Explicit structured failure reporting when any service is unreachable (evaluator_unavailable,
   llm_unavailable, stt_unavailable, sandbox_error, non_rl_heuristic_recovery).
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.orchestrator.feedback_agent import FeedbackAgent
from agents.coding_executor.coding_executor import DockerCSandbox, evaluate_c_submission


@pytest.mark.asyncio
async def test_evaluator_failure_produces_structured_failure_without_fabrication():
    """Evaluator failure returns explicit evaluator_unavailable state with score 0.0."""
    orch = InterviewOrchestrator(
        "sess_eval_fail_test",
        {"id": "cand_fail_01"},
        {"num_questions": 3, "interview_mode": "standard"},
    )
    q = await orch.start()

    with patch("httpx.AsyncClient.post", side_effect=Exception("Evaluator microservice down")):
        resp = await orch.handle_voice_answer("Some candidate answer", q["id"])

    # Must NOT fabricate a score or canned feedback
    feedback = resp["feedback"]
    assert feedback["final_score"] == 0.0
    assert "unavailable" in feedback["justification"].lower() or feedback["decision_source"] in {"evaluator_unavailable", "evaluator_structured"}


@pytest.mark.asyncio
async def test_qwen_failure_preserves_evaluator_evidence():
    """Qwen LLM failure returns structured feedback preserving evaluator scores."""
    agent = FeedbackAgent(qwen_url="http://127.0.0.1:99999")  # Unreachable port

    eval_result = {
        "final_score": 0.78,
        "covered_concepts": ["Dynamic programming"],
        "missing_concepts": ["Space optimization"],
        "what_was_incorrect": [],
        "justification": "Good DP concept",
        "score_breakdown": {"semantic_similarity": 0.78},
    }

    fb = await agent.generate(
        transcript="I used a memoization table",
        question={"id": "q_knapsack", "text": "How to solve knapsack?", "topic": "dynamic_programming"},
        eval_result=eval_result,
    )

    assert fb["llm_status"] == "llm_unavailable"
    assert fb["final_score"] == 0.78
    assert "Dynamic programming" in fb["covered_concepts"]
    assert "Space optimization" in fb["missing_concepts"]
    assert fb["decision_source"] == "evaluator_structured"


@pytest.mark.asyncio
async def test_docker_unavailability_produces_structured_sandbox_error():
    """When Docker daemon is unreachable, coding executor reports sandbox_error without fake execution."""
    sandbox = DockerCSandbox()

    with patch.object(sandbox, "_resolve_docker_prefix", return_value=None):
        res = sandbox.compile_and_execute("int main(){return 0;}", test_cases=[{"input": "2 3\n", "expected": "5\n", "is_hidden": False}])

    assert res["status"] == "sandbox_error"
    assert res["passed"] is False
    assert "not available" in res["error"].lower() or "unreachable" in res["error"].lower() or "sandbox" in res["error"].lower() or "docker" in res["error"].lower()


@pytest.mark.asyncio
async def test_rl_unavailability_produces_non_rl_heuristic_recovery():
    """When RL strategy is unavailable, orchestrator logs non_rl_heuristic_recovery without claiming PPO."""
    orch = InterviewOrchestrator(
        "sess_rl_fail_test",
        {"id": "cand_rl_fail"},
        {"num_questions": 3, "interview_mode": "standard"},
    )
    orch._state["baseline_complete"] = True
    orch._state["rl_enabled"] = True
    orch._strategy = None  # RL unavailable

    diff, reason, action = await orch._adapt_difficulty(0.85)
    assert orch._state["last_decision_source"] == "non_rl_heuristic_recovery"
    assert orch._state["rl_status"] == "rl_unavailable"
    assert orch._state["raw_rl_action"] is None
    assert orch._state["rl_last_action"] is None
    assert orch._state["last_decision_source"] != "ppo"


@pytest.mark.asyncio
async def test_followup_agent_cannot_alter_authoritative_evaluator_score():
    """Follow-up agent probing decisions cannot modify authoritative evaluator technical score."""
    eval_result = {"final_score": 0.65, "missing_concepts": ["Recursion base case"]}
    orch = InterviewOrchestrator("sess_fu_score_lock", {"id": "c1"}, {"num_questions": 3})

    # Record score into state
    orch._state["scores"].append(eval_result["final_score"])
    assert orch._state["scores"][-1] == 0.65

    # Trigger follow-up injection
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "followup": "What happens when base case is missing?",
        "reason": "missing_concepts",
        "target_concepts": ["Recursion base case"],
    }
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        injected = await orch._inject_followup_question(
            {"id": "q1", "text": "Explain recursion", "topic": "recursion"},
            "I write recursive calls without stop",
            eval_result,
        )

    assert injected is True
    # Technical score remains locked and unchanged by follow-up generation
    assert orch._state["scores"][-1] == 0.65
