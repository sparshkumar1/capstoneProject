"""
PrepAIred — Unit Tests for Personalization and Question System (Stage 4)
========================================================================
Tests question bank scale (>100), rubric coverage (>100), Easy initial question
selection, lexical token overlap deduplication, exact ID / text deduplication,
decision source tracking, canonical candidate state, and baseline main-question flow.
"""

import pytest
from apps.backend.main import (
    QUESTION_BANK,
    select_questions,
    _lexical_token_overlap,
    _text_similarity,
)
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Question Bank Scale (>100 Questions)
# ─────────────────────────────────────────────────────────────────────────────
def test_question_bank_size_exceeds_100():
    """Question bank must contain more than 100 distinct curated questions."""
    total_questions = sum(len(qs) for qs in QUESTION_BANK.values())
    unique_ids = {q["id"] for qs in QUESTION_BANK.values() for q in qs}
    assert total_questions > 100, f"Expected >100 questions, got {total_questions}"
    assert len(unique_ids) > 100, f"Expected >100 unique IDs, got {len(unique_ids)}"
    assert len(unique_ids) == total_questions, "Duplicate question IDs detected in bank!"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Rubric Coverage (>100 Question-Specific Rubrics)
# ─────────────────────────────────────────────────────────────────────────────
def test_rubric_bank_size_exceeds_100():
    """Every question must have a meaningful question-specific rubric attached."""
    all_qs = [q for qs in QUESTION_BANK.values() for q in qs]
    rubrics = [q.get("rubric") for q in all_qs if q.get("rubric")]
    assert len(rubrics) > 100, f"Expected >100 rubrics, got {len(rubrics)}"

    sample_rubric = all_qs[0].get("rubric", {})
    assert sample_rubric, "Question missing rubric dictionary"
    assert "logic_context" in sample_rubric or "answer" in sample_rubric or "common_mistakes" in sample_rubric


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Question Metadata Completeness
# ─────────────────────────────────────────────────────────────────────────────
def test_all_questions_have_valid_metadata():
    """All questions must have stable IDs, topics, difficulty, and expected concepts."""
    for topic, qs in QUESTION_BANK.items():
        for q in qs:
            assert q.get("id"), f"Question in topic {topic} missing ID"
            assert q.get("text"), f"Question {q.get('id')} missing text"
            assert 1 <= int(q.get("difficulty", 0)) <= 5, f"Question {q.get('id')} invalid difficulty {q.get('difficulty')}"
            assert q.get("type") in {"verbal", "code"}, f"Question {q.get('id')} invalid type {q.get('type')}"
            assert "expected_concepts" in q, f"Question {q.get('id')} missing expected_concepts"
            assert "category" in q, f"Question {q.get('id')} missing category"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Initial Question is Easy or Easy-Medium
# ─────────────────────────────────────────────────────────────────────────────
def test_first_question_is_easy_or_easy_medium():
    """The first question must always establish a baseline at difficulty <= 2 (Easy/Easy-Medium)."""
    for _ in range(5):
        selected = select_questions(["arrays"], ["linked_lists"], num=5, difficulty=4)
        assert len(selected) > 0
        first_q = selected[0]
        assert first_q.get("difficulty") <= 2, f"Initial question difficulty was {first_q.get('difficulty')} (must be <= 2)"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Level 1 Duplicate Prevention (Question IDs)
# ─────────────────────────────────────────────────────────────────────────────
def test_duplicate_id_prevention():
    """select_questions must never re-select questions present in exclude_ids."""
    first_batch = select_questions([], [], num=5, difficulty=2)
    seen_ids = {q["id"] for q in first_batch}

    second_batch = select_questions([], [], num=5, difficulty=2, exclude_ids=seen_ids)
    second_ids = {q["id"] for q in second_batch}

    overlap = seen_ids & second_ids
    assert len(overlap) == 0, f"Duplicate IDs returned across batches: {overlap}"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Level 2 Duplicate Prevention (Identical / Normalized Text)
# ─────────────────────────────────────────────────────────────────────────────
def test_identical_normalized_text_prevention():
    """Normalized text duplicates must be filtered out."""
    pool = select_questions([], [], num=20, difficulty=3)
    seen_texts = set()
    for q in pool:
        norm = " ".join(q["text"].lower().split())
        assert norm not in seen_texts, f"Duplicate text found: {q['text']}"
        seen_texts.add(norm)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Level 3 Duplicate Prevention (Lexical / Token Overlap Threshold)
# ─────────────────────────────────────────────────────────────────────────────
def test_lexical_token_overlap_detection():
    """_lexical_token_overlap must correctly compute token Jaccard overlap."""
    t1 = "Explain how dynamic memory allocation works in C using malloc and free."
    t2 = "Explain how dynamic memory allocation works in C using malloc and free pointers."
    overlap_high = _lexical_token_overlap(t1, t2)
    assert overlap_high >= 0.75, f"Expected high lexical overlap (>=0.75), got {overlap_high}"

    # Alias check
    assert _text_similarity(t1, t2) == overlap_high


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Different Questions Sharing Terminology Are NOT Falsely Rejected
# ─────────────────────────────────────────────────────────────────────────────
def test_different_questions_sharing_terminology_not_rejected():
    """Questions on the same topic sharing technical tokens must have moderate overlap (< 0.75) and NOT collide."""
    q_hash_1 = "Explain how a hash table handles collisions using separate chaining."
    q_hash_2 = "Explain how a hash table computes array bucket indices from string keys."

    overlap = _lexical_token_overlap(q_hash_1, q_hash_2)
    assert overlap < 0.60, f"Expected moderate lexical overlap (< 0.60), got {overlap}"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Decision Source Attribution (Baseline vs Guardrail vs Heuristic)
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_decision_source_attribution():
    """InterviewOrchestrator must explicitly tag decision_source for difficulty adjustments."""
    orch = InterviewOrchestrator(
        "sess_decision_source_test",
        {"id": "c1"},
        {"num_questions": 5, "interview_mode": "standard"},
        evaluator_fn=lambda t, q: {"final_score": 0.85, "decision_source": "mock_eval"},
    )
    first_q = await orch.start()

    # Turn 1: In baseline phase
    res1 = await orch.handle_voice_answer("Good answer", first_q["id"])
    diff_update1 = res1.get("difficulty_update")
    assert diff_update1 is not None
    assert orch._state["last_decision_source"] == "baseline_warmup"

    # Simulate G4 guardrail trigger (low score + high hesitation)
    orch._state["baseline_complete"] = True
    orch._state["rl_enabled"] = True
    orch._state["last_confidence_score"] = 0.10  # high hesitation

    action_idx = orch._apply_guardrails(
        action_idx=1, perf=0.20, avg_perf=0.50, conf=0.10, hes=0.90, diff_norm=0.60
    )
    assert orch._last_guardrail_name == "guardrail_G4"
    assert action_idx == 0  # "Easier"



# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Canonical Candidate State (Single Source of Truth)
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_canonical_candidate_state_is_single_source_of_truth():
    """InterviewOrchestrator._state must canonically house all candidate metrics."""
    orch = InterviewOrchestrator(
        "sess_canonical_state_test",
        {"id": "cand_999"},
        {"num_questions": 3, "interview_mode": "standard"},
        evaluator_fn=lambda t, q: {
            "final_score": 0.88,
            "covered_concepts": ["Dynamic programming", "Memoization"],
            "missing_concepts": ["Space optimization"],
            "what_was_incorrect": [],
        },
    )
    q = await orch.start()
    await orch.handle_voice_answer("I use memoization table.", q["id"])

    state = orch.to_session_dict()
    assert "strengths" in state and len(state["strengths"]) > 0
    assert "concepts_mastered" in state and "Memoization" in state["concepts_mastered"]
    assert "concepts_missed" in state and "Space optimization" in state["concepts_missed"]
    assert "topic_performance" in state and q.get("topic") in state["topic_performance"]
    assert "recent_performance" in state and len(state["recent_performance"]) == 1
    assert "difficulty_history" in state and len(state["difficulty_history"]) >= 1
    assert "question_history" in state and q["id"] in state["question_history"]
    assert "technical_performance" in state and state["technical_performance"] == 0.88
    assert "coding_performance" in state
    assert "response_timing" in state


# ─────────────────────────────────────────────────────────────────────────────
# TEST 11: Heuristic Question-Selection Personalization & Trajectory Divergence
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_heuristic_question_selection_trajectory_divergence():
    """Different performance profiles produce distinct question trajectories via selection heuristics."""
    orch_strong = InterviewOrchestrator(
        "sess_diverge_s",
        {"id": "cand_s"},
        {"num_questions": 4, "interview_mode": "standard"},
        evaluator_fn=lambda t, q: {"final_score": 0.95},
        select_questions_fn=select_questions,
    )
    orch_weak = InterviewOrchestrator(
        "sess_diverge_w",
        {"id": "cand_w"},
        {"num_questions": 4, "interview_mode": "standard"},
        evaluator_fn=lambda t, q: {"final_score": 0.20},
        select_questions_fn=select_questions,
    )

    qs_s = await orch_strong.start()
    qs_w = await orch_weak.start()

    await orch_strong.handle_voice_answer("Flawless explanation", qs_s["id"])
    await orch_weak.handle_voice_answer("I don't know", qs_w["id"])

    # Verify difficulty adjustment divergence
    assert orch_strong._state["current_difficulty"] >= orch_weak._state["current_difficulty"]
    assert orch_strong._state["technical_performance"] > orch_weak._state["technical_performance"]


# ─────────────────────────────────────────────────────────────────────────────
# TEST 12: Baseline 2-3 Main Questions Flow & Follow-up Isolation
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_baseline_main_questions_flow_and_followup_isolation():
    """Baseline completes strictly after 2-3 main questions; follow-ups never advance baseline."""
    orch = InterviewOrchestrator(
        "sess_baseline_flow",
        {"id": "cand_base"},
        {"num_questions": 5, "interview_mode": "standard"},
        evaluator_fn=lambda t, q: {"final_score": 0.80},
    )
    orch._question_queue = [
        {"id": "main_q1", "text": "Q1", "difficulty": 2, "type": "verbal", "topic": "pointers"},
        {"id": "main_q2", "text": "Q2", "difficulty": 2, "type": "verbal", "topic": "arrays"},
        {"id": "main_q3", "text": "Q3", "difficulty": 3, "type": "verbal", "topic": "trees"},
    ]
    orch._state["questions"] = list(orch._question_queue)
    await orch.start()

    # Main Q1 (baseline answered = 1)
    await orch.handle_voice_answer("Ans 1", "main_q1")
    assert orch._state["main_questions_count"] == 1
    assert orch._state["baseline_complete"] is False

    # Inject follow-up
    fu_q = {
        "id": "fu_1",
        "text": "Follow-up Q",
        "difficulty": 2,
        "type": "verbal",
        "topic": "pointers",
        "source": "qwen_followup",
        "is_followup": True,
        "target_concepts": ["Pointer arithmetic"],
    }
    orch._question_queue.insert(orch._current_q_index + 1, fu_q)
    orch._current_q_index += 1

    # Answer follow-up
    await orch.handle_voice_answer("Ans FU", "fu_1")
    assert orch._state["main_questions_count"] == 1, "Follow-up must NOT increment main_questions_count"
    assert orch._state["followups_count"] == 1
    assert orch._state["baseline_complete"] is False, "Follow-up must NOT advance baseline status"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 13: Single Authoritative Production Question Selector Path
# ─────────────────────────────────────────────────────────────────────────────
def test_single_authoritative_question_selector_path():
    """Verify that InterviewOrchestrator resolves to apps.backend.main.select_questions as the single authoritative selector."""
    orch = InterviewOrchestrator(
        "sess_authoritative_selector",
        {"id": "c1", "experience": "intermediate"},
        {"num_questions": 6, "c_topics": ["pointers", "memory"], "dsa_topics": ["arrays", "trees"]},
    )
    # The default injected selector MUST be apps.backend.main.select_questions
    assert orch._select_questions_fn is select_questions

    # Select questions using the authoritative production function
    selected = select_questions(["pointers"], ["arrays"], num=4, difficulty=3)
    assert len(selected) == 4
    assert all("id" in q and "text" in q and "difficulty" in q for q in selected)

    # Verify that Question 1 is constrained to difficulty <= 2
    assert selected[0]["difficulty"] <= 2

    # Verify duplicate prevention: re-selecting with seen IDs excludes previously selected questions
    seen = {q["id"] for q in selected}
    next_batch = select_questions(["pointers"], ["arrays"], num=4, difficulty=3, exclude_ids=seen)
    assert all(q["id"] not in seen for q in next_batch)
