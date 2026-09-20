import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from services.qwen.app import _build_followup_prompt, FollowupRequest


@pytest.mark.asyncio
async def test_exact_15_question_interview_lifecycle():
    """A demo_rl interview asks exactly 15 PRIMARY questions; a follow-up is an extra turn, not a primary slot."""
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
    assert q1.get("primary_question_index") == 1 and q1.get("is_followup") is False

    turns_completed = 0
    primary_answered = 0
    current_q = q1

    # Simulate a session in which the second PRIMARY question triggers one follow-up
    for _ in range(40):
        qid = current_q["id"]
        weak = (not current_q["is_followup"]) and current_q["primary_question_index"] == 2
        eval_mock = {
            "final_score": 0.70 if weak else 0.85,
            "covered_concepts": ["concept_a"],
            "missing_concepts": ["concept_b"] if weak else [],
            "incorrect_claims": [],
            "justification": f"Turn {turns_completed + 1} evaluation",
            "decision_source": "evaluator_cross_encoder",
        }

        with patch.object(orch, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_mock):
            with patch.object(orch, "_generate_feedback", new_callable=AsyncMock, return_value=dict(eval_mock)):
                resp = await orch.handle_voice_answer(
                    transcript=f"Candidate answer for turn {turns_completed + 1}",
                    question_id=qid,
                )

        turns_completed += 1
        primary_answered += 0 if current_q["is_followup"] else 1
        assert "feedback" in resp
        assert "hint" not in resp or resp.get("hint") is None, "Hint must be absent from response envelope!"

        if resp["next_action"] == "session_end":
            next_resp = await orch.handle_next_question()
            assert next_resp["type"] == "session_end", "Expected session_end payload after the final turn!"
            break
        next_resp = await orch.handle_next_question()
        assert next_resp["type"] == "question", f"Expected a question after turn {turns_completed}"
        current_q = next_resp["payload"]
        assert current_q["turn_index"] == turns_completed + 1
        assert current_q["total_questions"] == 15
    else:
        raise AssertionError("session did not terminate")

    # 15 primary questions + 1 follow-up = 16 candidate-facing turns; the follow-up did not take a primary slot
    assert primary_answered == 15
    assert turns_completed == 16
    assert len(orch._state["scores"]) == 16
    assert orch._state["main_questions_count"] == 15 and orch._state["followups_count"] == 1

    # Verify final report contains every turn
    report = await orch.end()
    assert report is not None
    assert len(report.get("question_results", [])) == 16
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
async def test_followup_injection_does_not_evict_primary_questions():
    """Injecting a follow-up must not evict any of the 15 primary questions."""
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

    # The follow-up is queued in addition to the 15 primary questions; none is evicted
    assert len(orch._question_queue) == 16
    assert len([q for q in orch._question_queue if q.get("source") != "qwen_followup"]) == 15
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
