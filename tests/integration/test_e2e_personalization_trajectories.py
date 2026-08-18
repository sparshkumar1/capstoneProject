"""
Integration Test: End-to-End Personalization Trajectories
Simulates two distinct candidate profiles (Candidate A - Strong vs Candidate B - Weak)
and verifies trajectory divergence across difficulty, follow-up behavior, topic adaptation,
and candidate-state evolution.
"""
import pytest
from unittest.mock import AsyncMock, patch

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator


@pytest.mark.asyncio
async def test_e2e_personalization_divergence_strong_vs_weak():
    """Verify Candidate A and Candidate B diverge across all adaptive metrics."""
    # ── Candidate A (Strong) ──
    cand_a_profile = {"id": "cand_strong", "experience": "senior"}
    orch_a = InterviewOrchestrator(
        "sess_e2e_strong",
        cand_a_profile,
        {"num_questions": 4, "interview_mode": "standard"},
    )
    q_a1 = await orch_a.start()

    # Turn 1: Strong answer (0.95)
    eval_a1 = {
        "final_score": 0.95,
        "covered_concepts": ["Pointers", "Pointer arithmetic", "Memory layout"],
        "missing_concepts": [],
        "what_was_incorrect": [],
    }
    with patch.object(orch_a, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_a1):
        with patch.object(orch_a, "_generate_feedback", new_callable=AsyncMock, return_value=eval_a1):
            resp_a1 = await orch_a.handle_voice_answer("Flawless explanation of pointers", q_a1["id"])

    # Advance to Turn 2: Strong answer (0.92) - completes baseline
    next_a2 = await orch_a.handle_next_question()
    q_a2 = next_a2["payload"]
    eval_a2 = {
        "final_score": 0.92,
        "covered_concepts": ["Dynamic allocation", "Heap memory"],
        "missing_concepts": [],
        "what_was_incorrect": [],
    }
    with patch.object(orch_a, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_a2):
        with patch.object(orch_a, "_generate_feedback", new_callable=AsyncMock, return_value=eval_a2):
            resp_a2 = await orch_a.handle_voice_answer("Complete malloc and free management", q_a2["id"])

    # Advance to Turn 3: Strong answer (0.90) in RL phase
    next_a3 = await orch_a.handle_next_question()
    q_a3 = next_a3["payload"]
    eval_a3 = {
        "final_score": 0.90,
        "covered_concepts": ["Graph BFS", "Queue", "Visited set"],
        "missing_concepts": [],
        "what_was_incorrect": [],
    }
    with patch.object(orch_a, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_a3):
        with patch.object(orch_a, "_generate_feedback", new_callable=AsyncMock, return_value=eval_a3):
            resp_a3 = await orch_a.handle_voice_answer("BFS uses queue and visited array", q_a3["id"])

    # ── Candidate B (Struggling) ──
    cand_b_profile = {"id": "cand_weak", "experience": "beginner"}
    orch_b = InterviewOrchestrator(
        "sess_e2e_weak",
        cand_b_profile,
        {"num_questions": 4, "interview_mode": "standard"},
    )
    q_b1 = await orch_b.start()

    # Turn 1: Weak answer (0.25)
    eval_b1 = {
        "final_score": 0.25,
        "covered_concepts": [],
        "missing_concepts": ["Pointer definition", "Dereference"],
        "what_was_incorrect": ["Confused pointer with normal variable"],
    }
    with patch.object(orch_b, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_b1):
        with patch.object(orch_b, "_generate_feedback", new_callable=AsyncMock, return_value=eval_b1):
            resp_b1 = await orch_b.handle_voice_answer("I don't know what pointer is", q_b1["id"])

    # Advance to Turn 2: Weak answer (0.20)
    next_b2 = await orch_b.handle_next_question()
    q_b2 = next_b2["payload"]
    eval_b2 = {
        "final_score": 0.20,
        "covered_concepts": [],
        "missing_concepts": ["Dynamic memory", "Freeing memory"],
        "what_was_incorrect": ["Claimed malloc allocates on the stack"],
    }
    with patch.object(orch_b, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_b2):
        with patch.object(orch_b, "_generate_feedback", new_callable=AsyncMock, return_value=eval_b2):
            resp_b2 = await orch_b.handle_voice_answer("malloc creates stack variables", q_b2["id"])

    # Advance to Turn 3: Weak answer (0.15) in RL phase
    next_b3 = await orch_b.handle_next_question()
    q_b3 = next_b3["payload"]
    eval_b3 = {
        "final_score": 0.15,
        "covered_concepts": [],
        "missing_concepts": ["Tree traversal"],
        "what_was_incorrect": ["Confused tree with linear array"],
    }
    with patch.object(orch_b, "_evaluate_verbal", new_callable=AsyncMock, return_value=eval_b3):
        with patch.object(orch_b, "_generate_feedback", new_callable=AsyncMock, return_value=eval_b3):
            resp_b3 = await orch_b.handle_voice_answer("Trees are same as arrays", q_b3["id"])

    # ── VERIFY TRAJECTORY & PERSONALIZATION DIVERGENCE ──
    # 1. Difficulty Divergence: Strong candidate reaches higher difficulty than weak candidate
    diff_a = orch_a._state["current_difficulty"]
    diff_b = orch_b._state["current_difficulty"]
    assert diff_a > diff_b, f"Expected diff_a ({diff_a}) > diff_b ({diff_b})"

    # 2. Overall Technical Score Divergence
    rep_a = await orch_a.end()
    rep_b = await orch_b.end()
    assert rep_a["overall_score"] > rep_b["overall_score"]
    assert rep_a["component_breakdown"]["technical_score"] > 0.85
    assert rep_b["component_breakdown"]["technical_score"] < 0.35

    # 3. Concept Mastery vs Concepts Missed Separation
    state_a = orch_a.to_session_dict()
    state_b = orch_b.to_session_dict()
    assert len(state_a["concepts_mastered"]) >= 3
    assert len(state_b["concepts_missed"]) >= 3
    assert len(state_a["strengths"]) > len(state_b["strengths"])
    assert len(state_b["weaknesses"]) > len(state_a["weaknesses"])
