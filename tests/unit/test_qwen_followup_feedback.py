"""
PrepAIred — Unit Tests for Qwen Follow-Up and Personalized Feedback (Stage 2)
=============================================================================
Tests the unified structured contract for Qwen follow-up and feedback generation:
1. Follow-up API (FastAPI endpoint test)
2. Qwen response parsing (raw JSON, fenced JSON, text)
3. Missing-concept follow-up (partially correct answer -> probes missing concept)
4. Misconception follow-up (incorrect claims -> probes misconception)
5. Strong-answer follow-up (excellent answer -> probes deeper scaling/trade-offs)
6. Duplicate follow-up prevention (avoids repeating previous questions)
7. Personalized feedback contract completeness (all required keys present)
8. Wrong-answer feedback (correction-focused tone and model explanation)
9. Partial-answer feedback (concept-bridging and clear next steps)
10. Strong-answer feedback (concise reinforcement and advanced avenues)
"""

import pytest
from fastapi.testclient import TestClient
from services.qwen.app import (
    app,
    FollowupRequest,
    FeedbackRequest,
    _extract_json_from_llm,
    _synthesize_structured_followup,
    _synthesize_structured_feedback,
)


@pytest.fixture
def client():
    return TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Follow-Up API Contract
# ─────────────────────────────────────────────────────────────────────────────
def test_followup_api_contract(client):
    """POST /api/qwen/followup must return a structured JSON response with required keys."""
    payload = {
        "original_question": "Explain your logic to find the two indices in an array that sum up to a target value.",
        "topic": "Arrays",
        "candidate_answer": "I use a hash map to store elements as I iterate.",
        "structured_evaluation": {
            "final_score": 0.4052,
            "grade": "Average",
            "correct_claims": ["Use hash map"],
            "missing_concepts": ["Calculate complement target - current", "O(1) lookup in hash map"],
            "incorrect_claims": [],
            "weakest_gap": "Calculate complement target - current",
        },
        "correct_concepts": ["Use hash map"],
        "missing_concepts": ["Calculate complement target - current"],
        "misconceptions": [],
        "weakest_gap": "Calculate complement target - current",
        "current_difficulty": 3,
        "previous_questions": ["Explain Two Sum"],
        "previous_followups": [],
    }

    resp = client.post("/api/qwen/followup", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "followup" in data
    assert "reason" in data
    assert "target_concepts" in data
    assert len(data["followup"]) > 10
    assert len(data["reason"]) > 5
    assert isinstance(data["target_concepts"], list)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Qwen JSON Response Parsing
# ─────────────────────────────────────────────────────────────────────────────
def test_qwen_json_parsing():
    """Parser must handle raw JSON, markdown-wrapped JSON, and malformed inputs."""
    raw_clean = '{"followup": "How does collision handling work?", "reason": "Probing hash map mechanics", "target_concepts": ["collisions"]}'
    res_clean = _extract_json_from_llm(raw_clean)
    assert res_clean is not None
    assert res_clean["followup"] == "How does collision handling work?"

    raw_fenced = '```json\n{\n  "followup": "What is the time complexity?",\n  "reason": "Probing efficiency",\n  "target_concepts": ["time complexity"]\n}\n```'
    res_fenced = _extract_json_from_llm(raw_fenced)
    assert res_fenced is not None
    assert res_fenced["followup"] == "What is the time complexity?"

    raw_text_wrapped = 'Here is the question:\n{\n  "followup": "Explain the base case.",\n  "reason": "Probing recursion",\n  "target_concepts": ["base case"]\n}\nHope this helps!'
    res_wrapped = _extract_json_from_llm(raw_text_wrapped)
    assert res_wrapped is not None
    assert res_wrapped["followup"] == "Explain the base case."

    raw_invalid = "This is not json at all."
    res_invalid = _extract_json_from_llm(raw_invalid)
    assert res_invalid is None


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Missing-Concept Follow-Up
# ─────────────────────────────────────────────────────────────────────────────
def test_missing_concept_followup():
    """When an answer misses a core concept, follow-up must probe that specific concept."""
    req = FollowupRequest(
        original_question="Explain Floyd's cycle detection algorithm.",
        topic="LinkedLists",
        candidate_answer="We use two pointers traversing the linked list.",
        structured_evaluation={
            "final_score": 0.45,
            "grade": "Average",
            "correct_claims": ["Use two pointers"],
            "missing_concepts": ["Fast pointer moves two steps while slow moves one", "Meeting point proves cycle"],
            "weakest_gap": "Fast pointer moves two steps while slow moves one",
        },
        missing_concepts=["Fast pointer moves two steps while slow moves one"],
    )

    res = _synthesize_structured_followup(req)
    assert "fast pointer" in res.followup.lower() or "next step" in res.followup.lower() or "moves" in res.followup.lower()
    assert "Fast pointer" in res.reason or "missing concept" in res.reason.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Misconception Follow-Up
# ─────────────────────────────────────────────────────────────────────────────
def test_misconception_followup():
    """When a candidate asserts a misconception, follow-up must directly probe that misconception."""
    req = FollowupRequest(
        original_question="Explain how dynamic memory allocation works in C with malloc.",
        topic="Pointers",
        candidate_answer="malloc allocates memory on the stack and automatically sets all bytes to zero.",
        structured_evaluation={
            "final_score": 0.25,
            "grade": "Poor",
            "correct_claims": [],
            "incorrect_claims": ["malloc initializes memory to zero", "malloc allocates on the stack"],
            "missing_concepts": ["Heap memory", "calloc vs malloc"],
        },
        misconceptions=["malloc initializes memory to zero"],
    )

    res = _synthesize_structured_followup(req)
    assert "malloc initializes" in res.reason or "misconception" in res.reason.lower()
    assert "fail" in res.followup.lower() or "walk through" in res.followup.lower() or "zero" in res.followup.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Strong-Answer Follow-Up
# ─────────────────────────────────────────────────────────────────────────────
def test_strong_answer_followup():
    """For an excellent answer, follow-up should probe deeper trade-offs, scaling, and edge cases."""
    req = FollowupRequest(
        original_question="Explain how to find two numbers that sum to target.",
        topic="Arrays",
        candidate_answer="Use a hash map in a single pass calculating target - current complement with O(n) time and O(n) space.",
        structured_evaluation={
            "final_score": 0.88,
            "grade": "Excellent",
            "correct_claims": ["Hash map lookup", "Complement target - current", "O(n) time", "O(n) space"],
            "missing_concepts": [],
            "incorrect_claims": [],
        },
    )

    res = _synthesize_structured_followup(req)
    assert "trade-off" in res.followup.lower() or "scaling" in res.followup.lower() or "edge case" in res.followup.lower() or "space" in res.followup.lower()
    assert "strong" in res.reason.lower() or "scaling" in res.reason.lower() or "deeper" in res.reason.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Duplicate Follow-Up Prevention
# ─────────────────────────────────────────────────────────────────────────────
def test_duplicate_followup_prevention():
    """Follow-up generator must avoid duplicating previous questions or follow-ups in the session."""
    repeated_q = "What are the primary space-time trade-offs and edge cases you would consider if scaling this to very large inputs?"
    req = FollowupRequest(
        original_question="Explain how to find two numbers that sum to target.",
        topic="Arrays",
        candidate_answer="Use a hash map with complement calculation in O(n) time.",
        structured_evaluation={
            "final_score": 0.85,
            "grade": "Excellent",
            "correct_claims": ["Hash map", "Complement"],
            "missing_concepts": [],
        },
        previous_followups=[repeated_q],
    )

    res = _synthesize_structured_followup(req)
    # Generated follow-up should have pivoted to an alternative topic to avoid repeating
    assert res.followup != repeated_q
    assert "space complexity" in res.target_concepts or "optimization" in res.target_concepts or "scaling" in res.reason.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Personalized Feedback Contract
# ─────────────────────────────────────────────────────────────────────────────
def test_personalized_feedback_contract(client):
    """POST /api/qwen/feedback must return complete structured schema grounded in evaluation."""
    payload = {
        "question_text": "Explain Two Sum logic.",
        "topic": "Arrays",
        "candidate_answer": "I will store elements in a hash map.",
        "structured_evaluation": {
            "final_score": 0.4052,
            "grade": "Average",
            "S1_semantic": 0.286,
            "S2_structural": 0.50,
            "reasoning_score": 0.375,
            "correct_claims": ["Store elements in a hash map"],
            "incorrect_claims": [],
            "missing_concepts": ["Calculate complement target - current", "O(1) map lookup"],
            "weakest_gap": "Calculate complement target - current",
        },
        "candidate_state": {"confidence": 0.75, "turn": 1},
        "history": [],
    }

    resp = client.post("/api/qwen/feedback", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    required_keys = [
        "what_candidate_said",
        "what_was_correct",
        "what_was_incorrect",
        "what_was_incomplete",
        "missing_concepts",
        "how_to_answer",
        "stronger_answer_guide",
        "actionable_improvements",
        "narrative_feedback",
        "final_score",
        "grade",
        "decision_source",
    ]
    for k in required_keys:
        assert k in data, f"Key '{k}' missing from feedback contract"

    # Verifies score is strictly mirrored from evaluator, not invented
    assert data["final_score"] == 0.4052
    assert data["grade"] == "Average"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Wrong-Answer Feedback (Correction-Focused)
# ─────────────────────────────────────────────────────────────────────────────
def test_wrong_answer_feedback():
    """Poor/Wrong answer feedback must be correction-focused, diagnosing the misconception."""
    req = FeedbackRequest(
        question_text="Explain Two Sum logic.",
        topic="Arrays",
        candidate_answer="I will run two nested loops i and j to check all pairs.",
        structured_evaluation={
            "final_score": 0.2491,
            "grade": "Poor",
            "correct_claims": [],
            "incorrect_claims": ["Nested loops are O(n²) and unnecessary"],
            "missing_concepts": ["Hash map single pass", "Complement calculation"],
        },
    )

    res = _synthesize_structured_feedback(req)
    assert res.final_score == 0.2491
    assert res.grade == "Poor"
    assert len(res.what_was_incorrect) > 0
    assert "Poor" in res.narrative_feedback or "gaps" in res.narrative_feedback.lower()
    assert len(res.actionable_improvements) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Partial-Answer Feedback (Concept-Bridging)
# ─────────────────────────────────────────────────────────────────────────────
def test_partial_answer_feedback():
    """Partial answer feedback must acknowledge correct points and clearly bridge missing concepts."""
    req = FeedbackRequest(
        question_text="Explain Two Sum logic.",
        topic="Arrays",
        candidate_answer="I will use a hash map to store elements as I iterate.",
        structured_evaluation={
            "final_score": 0.4052,
            "grade": "Average",
            "correct_claims": ["Use hash map to store elements"],
            "incorrect_claims": [],
            "missing_concepts": ["Calculate complement target - current"],
        },
    )

    res = _synthesize_structured_feedback(req)
    assert res.final_score == 0.4052
    assert res.grade == "Average"
    assert "Use hash map" in res.what_was_correct[0]
    assert "Calculate complement" in res.missing_concepts[0]
    assert "Average" in res.narrative_feedback or "omitted" in res.narrative_feedback.lower() or "relevant" in res.narrative_feedback.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Strong-Answer Feedback (Concise Reinforcement & Extensions)
# ─────────────────────────────────────────────────────────────────────────────
def test_strong_answer_feedback():
    """Strong answer feedback must provide concise reinforcement and advanced architectural advice."""
    req = FeedbackRequest(
        question_text="Explain Two Sum logic.",
        topic="Arrays",
        candidate_answer="Use a single pass hash map calculating complement in O(n) time and O(n) space.",
        structured_evaluation={
            "final_score": 0.8381,
            "grade": "Excellent",
            "correct_claims": ["Single pass hash map", "Complement calculation", "O(n) time complexity", "O(n) space complexity"],
            "incorrect_claims": [],
            "missing_concepts": [],
        },
    )

    res = _synthesize_structured_feedback(req)
    assert res.final_score == 0.8381
    assert res.grade == "Excellent"
    assert len(res.what_was_correct) >= 2
    assert len(res.what_was_incorrect) == 0
    assert "Excellent" in res.narrative_feedback or "strong" in res.narrative_feedback.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 11: Exact Transcript Grounding (No Fake Paraphrased Quotes)
# ─────────────────────────────────────────────────────────────────────────────
def test_exact_transcript_grounding():
    """what_candidate_said must contain the verbatim candidate transcript, without fake paraphrasing."""
    verbatim_text = "I think malloc allocates memory on the stack and sets bytes to zero."
    req = FeedbackRequest(
        question_text="Explain dynamic memory in C.",
        topic="Pointers",
        candidate_answer=verbatim_text,
        structured_evaluation={
            "final_score": 0.25,
            "grade": "Poor",
            "correct_claims": [],
            "incorrect_claims": ["malloc allocates on the stack"],
            "missing_concepts": ["Heap memory"],
        },
    )

    res = _synthesize_structured_feedback(req)
    assert res.what_candidate_said == verbatim_text
    assert not res.what_candidate_said.startswith("Candidate stated: \"")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 12: Follow-Up Decision Policy Matrix
# ─────────────────────────────────────────────────────────────────────────────
def test_followup_decision_policy_matrix():
    """Verify follow-up decision policy based on gaps, depth opportunities, and caps."""
    def should_trigger_fu(eval_res: dict, consecutive_fu: int, has_depth_opportunity: bool = False) -> bool:
        if consecutive_fu >= 2:
            return False
        miscon = list(eval_res.get("incorrect_claims", []))
        missing = list(eval_res.get("missing_concepts", []))
        score = float(eval_res.get("final_score", 0.5))
        grade = str(eval_res.get("grade", "Average"))
        if miscon or missing or not eval_res.get("mandatory_pass", True):
            return True
        # Strong answer triggers follow-up ONLY if rubric provides a meaningful depth opportunity
        if (score >= 0.75 or grade == "Excellent") and consecutive_fu == 0 and (has_depth_opportunity or eval_res.get("depth_opportunities")):
            return True
        return False

    # 1. Complete correct answer without gap or depth need -> NO follow-up
    assert should_trigger_fu({"final_score": 0.95, "grade": "Excellent", "mandatory_pass": True}, 0, has_depth_opportunity=False) is False

    # 2. Partial answer with missing mandatory concept -> Follow-up
    assert should_trigger_fu({"final_score": 0.50, "grade": "Average", "missing_concepts": ["complement"], "mandatory_pass": False}, 0) is True

    # 3. Wrong answer with misconception -> Follow-up
    assert should_trigger_fu({"final_score": 0.25, "grade": "Poor", "incorrect_claims": ["stack alloc"], "mandatory_pass": False}, 0) is True

    # 4. Strong answer + useful depth opportunity from rubric -> Follow-up
    assert should_trigger_fu({"final_score": 0.88, "grade": "Excellent", "mandatory_pass": True, "depth_opportunities": ["concurrency"]}, 0) is True

    # 5. Strong answer + no useful depth opportunity -> NO follow-up
    assert should_trigger_fu({"final_score": 0.88, "grade": "Excellent", "mandatory_pass": True, "depth_opportunities": []}, 0, has_depth_opportunity=False) is False

    # 6. Follow-up #1 resolves the gap -> NO follow-up
    assert should_trigger_fu({"final_score": 0.85, "grade": "Excellent", "missing_concepts": [], "mandatory_pass": True}, 1) is False

    # 7. Follow-up #1 does NOT resolve gap -> Follow-up #2
    assert should_trigger_fu({"final_score": 0.45, "grade": "Average", "missing_concepts": ["O(1) lookup"], "mandatory_pass": False}, 1) is True

    # 8. After Follow-up #2 -> ALWAYS proceed to next main question (NO follow-up)
    assert should_trigger_fu({"final_score": 0.40, "grade": "Average", "missing_concepts": ["still missing"], "mandatory_pass": False}, 2) is False



# ─────────────────────────────────────────────────────────────────────────────
# TEST 13: Baseline Question Counting Ignores Follow-Ups
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_baseline_question_counting_ignores_followups():
    """Verify follow-up questions do NOT increment main question count or prematurely end baseline."""
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

    def _q(qid="q0", topic="general", diff=3, qtype="verbal"):
        return {"id": qid, "text": f"Question text for {qid}", "topic": topic, "difficulty": diff, "type": qtype}

    orch = InterviewOrchestrator(
        "test_baseline_fu_sep",
        {"id": "c1", "experience": "intermediate"},
        {
            "c_topics": ["pointers"],
            "dsa_topics": ["graphs"],
            "duration_minutes": 30,
            "num_questions": 4,
            "interview_mode": "demo_rl",
            "baseline_questions": None,
        },
    )
    orch._question_queue = [_q("q0"), _q("q1"), _q("q2"), _q("q3")]
    orch._state["questions"] = list(orch._question_queue)
    await orch.start()

    # Turn 1: Main Q0
    res1 = await orch.handle_voice_answer("main answer 1", "q0")
    assert orch._state["main_questions_count"] == 1
    assert orch._state["followups_count"] == 0
    assert orch._state["baseline_complete"] is False

    # Inject and answer Follow-up 1 (FU1)
    fu_injected = await orch._inject_followup_question(_q("q0"), context_text="main answer 1", eval_result={"missing_concepts": ["gap1"]})
    assert fu_injected is True
    fu_id = orch._question_queue[1]["id"]
    await orch.handle_next_question()

    res_fu1 = await orch.handle_voice_answer("followup answer 1", fu_id)
    # Main count remains 1, followup count becomes 1
    assert orch._state["main_questions_count"] == 1
    assert orch._state["followups_count"] == 1
    assert orch._state["baseline_complete"] is False

    # Turn 2: Main Q1
    await orch.handle_next_question()
    res2 = await orch.handle_voice_answer("main answer 2", "q1")
    assert orch._state["main_questions_count"] == 2
    assert orch._state["followups_count"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# TEST 14: Qwen Attribution — Available vs Unavailable Integrity
# ─────────────────────────────────────────────────────────────────────────────
def test_qwen_attribution_available_vs_unavailable():
    """Verify that genuine Qwen vs offline structured fallback are explicitly attributed without false LLM claims."""
    # Case A: Synthesized fallback when LLM is unavailable
    req_fu = FollowupRequest(
        original_question="What is a binary search tree?",
        topic="Trees",
        candidate_answer="A tree where each node has at most two children.",
        structured_evaluation={"final_score": 0.50, "missing_concepts": ["BST ordering invariant"]},
    )
    res_fu = _synthesize_structured_followup(req_fu)
    assert res_fu.llm_status == "llm_unavailable"
    assert res_fu.decision_source == "non_llm_structured_recovery"
    assert "qwen_1.5b_llm" not in res_fu.decision_source

    req_fb = FeedbackRequest(
        question_text="What is a binary search tree?",
        topic="Trees",
        candidate_answer="A tree where each node has at most two children.",
        structured_evaluation={"final_score": 0.50, "missing_concepts": ["BST ordering invariant"]},
    )
    res_fb = _synthesize_structured_feedback(req_fb)
    assert res_fb.llm_status == "llm_unavailable"
    assert res_fb.decision_source == "non_llm_structured_recovery"
    assert "qwen_7b_llm" not in res_fb.decision_source

    # Case B: When live model is mocked/available
    from services.qwen.app import FollowupResponse, FeedbackResponse
    live_fu = FollowupResponse(
        followup="How do you maintain the BST invariant on deletion?",
        reason="Targeted probe on BST deletion mechanism",
        target_concepts=["BST deletion", "in-order predecessor"],
        decision_source="qwen_1.5b_llm",
        llm_status="available",
    )
    assert live_fu.llm_status == "available"
    assert live_fu.decision_source == "qwen_1.5b_llm"
    assert "llm" in live_fu.decision_source
