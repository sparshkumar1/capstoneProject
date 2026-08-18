import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from services.qwen.app import _build_followup_prompt, FollowupRequest


@pytest.mark.asyncio
async def test_exact_15_question_interview_lifecycle():
    """Verify that a demo_rl interview runs for exactly 15 candidate-facing turns."""
    session_id = "sess_15q_test_001"
    candidate = {"id": "cand_15q", "experience": "intermediate"}
    config = {
        "duration_minutes": 30,
        "num_questions": 15,
        "interview_mode": "demo_rl",
        "c_topics": ["pointers", "memory_management", "arrays_strings"],
        "dsa_topics": ["linked_list", "trees", "graphs"],
    }

    orch = InterviewOrchestrator(session_id, candidate, config)
    assert orch._state["num_questions"] == 15

    # 1. Start session -> Q1
    q1 = await orch.start()
    assert q1 is not None
    assert q1.get("turn_index") == 1
    assert q1.get("total_questions") == 15

    turns_completed = 0
    current_q = q1

    # Simulate 15 turns with a follow-up injected at turn 2
    for turn in range(1, 16):
        qid = current_q["id"]
        eval_mock = {
            "final_score": 0.70 if turn == 2 else 0.85,
            "covered_concepts": ["concept_a"],
            "missing_concepts": ["concept_b"] if turn == 2 else [],
            "incorrect_claims": [],
            "justification": f"Turn {turn} evaluation",
            "decision_source": "evaluator_cross_encoder",
        }

        with patch.object(orch, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_mock):
            with patch.object(orch, "_generate_feedback", new_callable=AsyncMock, return_value=eval_mock):
                resp = await orch.handle_voice_answer(
                    transcript=f"Candidate answer for turn {turn}",
                    question_id=qid,
                )

        turns_completed += 1
        assert "feedback" in resp
        assert "hint" not in resp or resp.get("hint") is None, "Hint must be absent from response envelope!"

        if turn < 15:
            assert resp["next_action"] == "wait_for_next", f"Expected wait_for_next at turn {turn}"
            next_resp = await orch.handle_next_question()
            assert next_resp["type"] == "question", f"Expected question at turn {turn + 1}"
            current_q = next_resp["payload"]
            assert current_q["turn_index"] == turn + 1, f"Expected turn_index {turn + 1}, got {current_q.get('turn_index')}"
            assert current_q["total_questions"] == 15
        else:
            assert resp["next_action"] == "session_end", "Expected session_end on turn 15!"
            next_resp = await orch.handle_next_question()
            assert next_resp["type"] == "session_end", "Expected session_end payload after turn 15!"

    assert turns_completed == 15
    assert len(orch._state["scores"]) == 15

    # Verify final report contains all 15 turns
    report = await orch.end()
    assert report is not None
    assert len(report.get("question_results", [])) == 15
    assert report.get("session_id") == session_id


def test_qwen_followup_prompt_contextual_grounding():
    """Verify that Qwen follow-up prompt builder enforces missing concept probing and no repetition."""
    req = FollowupRequest(
        original_question="How does a hash table resolve collisions in C?",
        topic="hashing",
        candidate_answer="A hash table stores key-value pairs using a hash index. I am not sure about collisions.",
        correct_concepts=["key-value pairs", "hash index"],
        missing_concepts=["chaining", "open addressing"],
        misconceptions=[],
        current_difficulty=3,
    )
    prompt = _build_followup_prompt(req)

    assert "chaining, open addressing" in prompt
    assert "Do NOT repeat or re-phrase the original question" in prompt
    assert "Directly probe the missing concepts" in prompt
    assert "hashing" in prompt


@pytest.mark.asyncio
async def test_followup_injection_caps_queue_at_15():
    """Verify that injecting follow-up questions caps the total questions at exactly 15."""
    session_id = "sess_fu_cap_002"
    candidate = {"id": "cand_fu", "experience": "intermediate"}
    config = {
        "duration_minutes": 30,
        "num_questions": 15,
        "interview_mode": "demo_rl",
        "c_topics": ["pointers"],
        "dsa_topics": ["linked_list"],
    }
    orch = InterviewOrchestrator(session_id, candidate, config)
    assert len(orch._question_queue) == 15

    # Inject follow-up
    current_q = orch._question_queue[0]
    eval_result = {
        "final_score": 0.50,
        "missing_concepts": ["double pointers"],
        "correct_claims": ["pointers"],
    }
    injected = await orch._inject_followup_question(current_q, context_text="some code", eval_result=eval_result)
    assert injected is True

    # Assert queue length remains strictly 15
    assert len(orch._question_queue) == 15
    assert orch._question_queue[1]["source"] == "qwen_followup"
    assert orch._question_queue[1]["parent_question_id"] == current_q["id"]


def test_evaluator_concept_extraction_uses_human_readable_names():
    """Verify that rubric concept extraction returns human-readable concepts and NEVER Concept N."""
    from services.evaluator.app import _extract_concept_texts

    rubric_sample = {
        "qid": "1",
        "topic": "Arrays",
        "logic_markers": {
            "concept_groups": [
                ["single pass iteration", "one loop traversal"],
                ["store value-to-index mapping", "check complement existence"],
            ],
            "mandatory": ["hash map for storing values"],
        },
        "semantic_targets": ["Two-sum uses complement lookup"],
    }

    concepts = _extract_concept_texts(rubric_sample)
    assert len(concepts) >= 2
    assert "single pass iteration" in concepts
    assert "store value-to-index mapping" in concepts
    assert not any(str(c).startswith("Concept ") for c in concepts)


@pytest.mark.asyncio
async def test_absence_of_hint_workflow_in_orchestrator():
    """Verify that the orchestrator turn loop contains no hint generation or hint state."""
    session_id = "sess_no_hint_003"
    candidate = {"id": "cand_nohint", "experience": "intermediate"}
    config = {
        "duration_minutes": 30,
        "num_questions": 15,
        "interview_mode": "demo_rl",
        "c_topics": ["pointers"],
        "dsa_topics": ["linked_list"],
    }
    orch = InterviewOrchestrator(session_id, candidate, config)
    q1 = await orch.start()

    eval_mock = {
        "final_score": 0.80,
        "covered_concepts": ["pointer mechanics"],
        "missing_concepts": [],
        "incorrect_claims": [],
        "justification": "Clear answer",
        "decision_source": "evaluator_cross_encoder",
    }

    with patch.object(orch, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_mock):
        with patch.object(orch, "_generate_feedback", new_callable=AsyncMock, return_value=eval_mock):
            resp = await orch.handle_voice_answer(transcript="Pointers hold memory addresses", question_id=q1["id"])

    assert "hint" not in resp or resp.get("hint") is None
    assert "hint_given" not in orch._state.get("answers", [{}])[0] or not orch._state["answers"][0].get("hint_given")
