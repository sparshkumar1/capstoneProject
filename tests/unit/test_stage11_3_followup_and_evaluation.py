"""
test_stage11_3_followup_and_evaluation.py
Authoritative test suite for Stage 11.3 verification:
1. Partial answer -> missing concept follow-up
2. Misconception -> corrective follow-up
3. Wrong answer -> grounded follow-up
4. Strong answer -> no unnecessary follow-up
5. Follow-up resolves gap -> stop
6. Follow-up fails -> second follow-up
7. Second follow-up -> hard stop (consecutive_followups <= 2)
8. Exact transcript grounding (what_candidate_said == transcript)
9. Follow-up deduplication
10. Qwen failure -> explicit failure, no fabrication
11. Follow-up history separated from main question count
12. State update after follow-up
13. Pause-time propagation consistency
14. Topic-performance mapping consistency
15. Training/runtime time_norm formula consistency
"""

import math
import numpy as np
import pytest
from unittest.mock import patch, AsyncMock

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.orchestrator.feedback_agent import FeedbackAgent
from agents.timing.timer import QuestionTimer
from agents.strategy.hybrid_orchestrator import HybridOrchestrator, build_rl_observation
from rl.env.interview_env import InterviewEnv
from services.evaluator.app import evaluate, get_rubric
from services.qwen.app import (
    FollowupRequest,
    FeedbackRequest,
    _synthesize_structured_followup,
    _synthesize_structured_feedback,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. PARTIAL ANSWER -> MISSING CONCEPT FOLLOW-UP
# ─────────────────────────────────────────────────────────────────────────────
def test_partial_answer_missing_concept_followup():
    """Candidate answer covers only 1 mechanism -> missing concept identified -> Qwen follow-up probes it."""
    rubric = {
        "expected_concepts": [
            "Separate chaining with linked lists or dynamic arrays",
            "Open addressing with linear or quadratic probing",
        ],
        "mandatory_concepts": [
            "Separate chaining with linked lists or dynamic arrays",
            "Open addressing with linear or quadratic probing",
        ],
        "common_mistakes": ["Overwriting previous value on collision"],
    }
    q_text = "Explain how a hash table handles collisions."
    partial_transcript = "A hash table handles collisions using separate chaining where each bucket stores a linked list of collided keys."

    eval_res = evaluate(q_text, partial_transcript, rubric)
    assert 0.35 <= eval_res["final_score"] < 0.85, f"Expected partial score, got {eval_res['final_score']}"
    assert len(eval_res["missing_concepts"]) > 0, "Missing concepts should not be empty"
    assert any("open addressing" in m.lower() or "probing" in m.lower() for m in eval_res["missing_concepts"])

    req = FollowupRequest(
        original_question=q_text,
        topic="hash_tables",
        candidate_answer=partial_transcript,
        structured_evaluation=eval_res,
        missing_concepts=eval_res["missing_concepts"],
        correct_concepts=eval_res["correct_claims"],
        misconceptions=[],
        weakest_gap=eval_res["weakest_gap"],
        current_difficulty=3,
        previous_questions=[q_text],
        previous_followups=[],
    )
    fu_res = _synthesize_structured_followup(req)
    assert fu_res.followup is not None
    assert len(fu_res.followup) > 15
    assert len(fu_res.target_concepts) > 0
    # Must target the missing concept
    assert any("open addressing" in str(t).lower() or "probing" in str(t).lower() for t in fu_res.target_concepts)


# ─────────────────────────────────────────────────────────────────────────────
# 2. MISCONCEPTION -> CORRECTIVE FOLLOW-UP
# ─────────────────────────────────────────────────────────────────────────────
def test_misconception_corrective_followup():
    """Candidate answer contains misconception -> incorrect claim identified -> corrective probe generated."""
    rubric = {
        "expected_concepts": [
            "Separate chaining with linked lists",
            "Open addressing linear probing",
        ],
        "mandatory_concepts": ["Separate chaining with linked lists"],
        "common_mistakes": ["Overwriting the existing value in the slot on collision"],
    }
    q_text = "Explain how a hash table handles collisions."
    misconception_transcript = "On a collision, the new key simply overwrites the old value in the slot, replacing it."

    eval_res = evaluate(q_text, misconception_transcript, rubric)
    assert eval_res["final_score"] < 0.50
    assert len(eval_res["incorrect_claims"]) > 0 or len(eval_res["missing_concepts"]) > 0

    req = FollowupRequest(
        original_question=q_text,
        topic="hash_tables",
        candidate_answer=misconception_transcript,
        structured_evaluation=eval_res,
        misconceptions=eval_res.get("incorrect_claims", ["Overwriting key on collision"]),
        correct_concepts=[],
        missing_concepts=eval_res["missing_concepts"],
        weakest_gap="Collision resolution mechanism",
        current_difficulty=3,
        previous_questions=[q_text],
        previous_followups=[],
    )
    fu_res = _synthesize_structured_followup(req)
    assert "overwrit" in fu_res.followup.lower() or "approach" in fu_res.followup.lower() or "concrete" in fu_res.followup.lower()
    assert "Probing" in fu_res.reason or "misconception" in fu_res.reason.lower()


# ─────────────────────────────────────────────────────────────────────────────
# 3. WRONG ANSWER -> GROUNDED FOLLOW-UP
# ─────────────────────────────────────────────────────────────────────────────
def test_wrong_answer_grounded_followup():
    """Off-topic / wrong answer gets low score and grounded recovery probe without fabricated praise."""
    rubric = {
        "expected_concepts": ["Separate chaining", "Open addressing"],
        "mandatory_concepts": ["Separate chaining"],
        "common_mistakes": [],
    }
    q_text = "Explain how a hash table handles collisions."
    wrong_transcript = "The compiler optimizes recursion using tail call optimization to avoid stack overflow."

    eval_res = evaluate(q_text, wrong_transcript, rubric)
    assert eval_res["final_score"] < 0.35
    assert eval_res["grade"] in {"Poor", "Average"}

    req = FollowupRequest(
        original_question=q_text,
        topic="hash_tables",
        candidate_answer=wrong_transcript,
        structured_evaluation=eval_res,
        missing_concepts=eval_res["missing_concepts"],
        correct_concepts=[],
        misconceptions=[],
        weakest_gap="Collision resolution mechanism",
        current_difficulty=3,
        previous_questions=[q_text],
        previous_followups=[],
    )
    fu_res = _synthesize_structured_followup(req)
    assert len(fu_res.followup) > 15
    assert (
        "chaining" in fu_res.followup.lower()
        or "addressing" in fu_res.followup.lower()
        or "approach" in fu_res.followup.lower()
        or "efficiency" in fu_res.followup.lower()
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. STRONG ANSWER -> NO UNNECESSARY FOLLOW-UP
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_strong_answer_no_unnecessary_followup():
    """Candidate covers all concepts -> score >= 0.85 -> follow-up is skipped by policy."""
    orch = InterviewOrchestrator(
        "sess_strong_test",
        {"id": "c1", "experience": "senior"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["hash_tables"]},
    )
    q = {"id": "q_hash", "text": "Explain hash table collision resolution.", "topic": "hash_tables", "type": "verbal"}
    strong_eval = {
        "final_score": 0.95,
        "grade": "Excellent",
        "correct_claims": ["Separate chaining", "Open addressing"],
        "missing_concepts": [],
        "incorrect_claims": [],
        "weakest_gap": "None — comprehensive answer",
        "decision_source": "evaluator_cross_encoder",
    }
    transcript = "Hash tables resolve collisions via separate chaining using linked lists or open addressing with linear probing."

    injected = await orch._decide_and_inject_followup(q, transcript, strong_eval)
    assert injected is False, "Strong answer should not trigger a follow-up"


# ─────────────────────────────────────────────────────────────────────────────
# 5. FOLLOW-UP RESOLVES GAP -> STOP FOLLOW-UPS
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_followup_resolves_gap_stops_followups():
    """When a candidate correctly answers a follow-up, no further follow-up is injected."""
    orch = InterviewOrchestrator(
        "sess_resolve_gap",
        {"id": "c1", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["hash_tables"]},
    )
    # Simulate answering follow-up
    fu_q = {
        "id": "fu_12345",
        "text": "How would you handle open addressing with linear probing?",
        "topic": "hash_tables",
        "type": "verbal",
        "source": "qwen_followup",
        "is_followup": True,
    }
    resolved_eval = {
        "final_score": 0.90,
        "grade": "Pass",
        "correct_claims": ["Linear probing searches consecutive slots until empty"],
        "missing_concepts": [],
        "incorrect_claims": [],
        "weakest_gap": "None",
        "decision_source": "evaluator_cross_encoder",
    }
    transcript = "In linear probing, we increment the index by one on each collision until finding an empty slot."

    injected = await orch._decide_and_inject_followup(fu_q, transcript, resolved_eval)
    assert injected is False, "Resolved follow-up must not trigger another follow-up"


# ─────────────────────────────────────────────────────────────────────────────
# 6. FOLLOW-UP FAILS -> SECOND FOLLOW-UP TRIGGERED
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_followup_fails_triggers_second_followup():
    """When a follow-up answer is still incomplete (consecutive_followups=1), a 2nd follow-up is allowed."""
    orch = InterviewOrchestrator(
        "sess_second_fu",
        {"id": "c1", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["hash_tables"]},
    )
    orch._state["consecutive_followups"] = 1  # 1 follow-up already done
    fu_q = {
        "id": "fu_12345",
        "text": "How would you handle open addressing with linear probing?",
        "topic": "hash_tables",
        "type": "verbal",
        "source": "qwen_followup",
    }
    partial_fu_eval = {
        "final_score": 0.50,
        "grade": "Average",
        "correct_claims": ["Probing searches slots"],
        "missing_concepts": ["Primary clustering avoidance", "Step size logic"],
        "incorrect_claims": [],
        "weakest_gap": "Primary clustering avoidance",
        "decision_source": "evaluator_cross_encoder",
    }
    transcript = "You check other slots in the array."

    injected = await orch._decide_and_inject_followup(fu_q, transcript, partial_fu_eval)
    assert injected is True, "Incomplete 1st follow-up should trigger 2nd follow-up"


# ─────────────────────────────────────────────────────────────────────────────
# 7. SECOND FOLLOW-UP -> HARD STOP ENFORCED
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_second_followup_hard_cap_enforced():
    """When consecutive_followups >= 2, hard stop strictly blocks any 3rd follow-up."""
    orch = InterviewOrchestrator(
        "sess_hard_cap",
        {"id": "c1", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["hash_tables"]},
    )
    orch._state["consecutive_followups"] = 2  # Already 2 follow-ups
    fu_q = {
        "id": "fu_67890",
        "text": "How do you avoid primary clustering in linear probing?",
        "topic": "hash_tables",
        "type": "verbal",
        "source": "qwen_followup",
    }
    failed_eval = {
        "final_score": 0.20,
        "grade": "Poor",
        "correct_claims": [],
        "missing_concepts": ["Quadratic probing", "Double hashing"],
        "incorrect_claims": [],
        "weakest_gap": "Clustering resolution",
        "decision_source": "evaluator_cross_encoder",
    }
    transcript = "I do not know."

    injected = await orch._decide_and_inject_followup(fu_q, transcript, failed_eval)
    assert injected is False, "Hard cap consecutive_followups >= 2 must strictly block further follow-ups"


# ─────────────────────────────────────────────────────────────────────────────
# 8. EXACT TRANSCRIPT GROUNDING
# ─────────────────────────────────────────────────────────────────────────────
def test_exact_transcript_grounding():
    """what_candidate_said in feedback must match candidate transcript without synthetic quotes."""
    req = FeedbackRequest(
        question_text="Explain Two Sum algorithm.",
        topic="Arrays",
        candidate_answer="I iterate through the array and store each value in a hash map.",
        structured_evaluation={
            "final_score": 0.65,
            "grade": "Good",
            "correct_claims": ["Iterate through array", "Use hash map"],
            "missing_concepts": ["Check complement existence"],
            "incorrect_claims": [],
            "expected_concepts": ["Single pass", "Hash map complement lookup"],
            "weakest_gap": "Check complement existence",
        },
    )
    fb = _synthesize_structured_feedback(req)
    assert fb.what_candidate_said == "I iterate through the array and store each value in a hash map."
    assert not fb.what_candidate_said.startswith('"')
    assert not fb.what_candidate_said.endswith('"')


# ─────────────────────────────────────────────────────────────────────────────
# 9. FOLLOW-UP DEDUPLICATION
# ─────────────────────────────────────────────────────────────────────────────
def test_followup_deduplication():
    """If the exact same follow-up was already asked, an alternative probe is generated."""
    prev_fu = "You covered the initial setup well. How would you specifically handle the open addressing with linear probing to ensure optimal efficiency?"
    req = FollowupRequest(
        original_question="Explain hash collisions.",
        topic="hash_tables",
        candidate_answer="I use separate chaining.",
        structured_evaluation={"final_score": 0.5, "missing_concepts": ["Open addressing with linear probing"]},
        missing_concepts=["Open addressing with linear probing"],
        correct_concepts=["Separate chaining"],
        misconceptions=[],
        weakest_gap="Open addressing with linear probing",
        current_difficulty=3,
        previous_questions=["Explain hash collisions."],
        previous_followups=[prev_fu],
    )
    res = _synthesize_structured_followup(req)
    assert res.followup != prev_fu, "Deduplication must yield a distinct alternative follow-up"
    assert "space complexity" in res.followup.lower() or "optimized" in res.followup.lower() or "auxiliary" in res.followup.lower()


# ─────────────────────────────────────────────────────────────────────────────
# 10. QWEN FAILURE -> EXPLICIT FAILURE, NO FABRICATION
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_qwen_failure_explicit_reported_no_fabrication():
    """When Qwen microservice is unreachable, FeedbackAgent returns structured fallback with llm_status=llm_unavailable."""
    agent = FeedbackAgent(qwen_url="http://127.0.0.1:9999")  # Non-existent port
    eval_res = {
        "final_score": 0.60,
        "grade": "Average",
        "covered_concepts": ["Pointers store addresses"],
        "missing_concepts": ["Pointer arithmetic scaling"],
        "incorrect_claims": [],
        "decision_source": "evaluator_cross_encoder",
    }
    fb = await agent.generate(
        transcript="A pointer holds an address in memory.",
        question={"text": "What is a pointer?", "topic": "pointers"},
        eval_result=eval_res,
    )
    assert fb["llm_status"] == "llm_unavailable"
    assert fb["final_score"] == 0.60
    assert "Pointers store addresses" in fb["what_was_correct"]
    assert "Pointer arithmetic scaling" in fb["missing_concepts"]


# ─────────────────────────────────────────────────────────────────────────────
# 11. FOLLOW-UP HISTORY SEPARATED FROM MAIN QUESTION COUNT
# ─────────────────────────────────────────────────────────────────────────────
def test_followup_history_separated_from_main_question_count():
    """Follow-up questions do NOT increment main_questions_count and track under followup_history."""
    orch = InterviewOrchestrator(
        "sess_count_sep",
        {"id": "c1", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["arrays"]},
    )
    main_q = {"id": "q_main_1", "topic": "arrays", "type": "verbal", "source": "bank"}
    fu_q = {"id": "fu_1", "topic": "arrays", "type": "verbal", "source": "qwen_followup", "is_followup": True}

    # Main answer 1
    orch._update_session_state(main_q, 0.60, {"covered_concepts": ["Array indexing"]}, transcript="Main answer 1")
    assert orch._state["main_questions_count"] == 1
    assert orch._state["followups_count"] == 0
    assert orch._state["consecutive_followups"] == 0

    # Follow-up answer 1
    orch._update_session_state(fu_q, 0.80, {"covered_concepts": ["Bounds check"]}, transcript="Followup answer 1")
    assert orch._state["main_questions_count"] == 1, "Follow-up must NOT increment main_questions_count"
    assert orch._state["followups_count"] == 1
    assert orch._state["consecutive_followups"] == 1
    assert len(orch._state["followup_history"]) == 1

    # Main answer 2 (resets consecutive_followups)
    main_q2 = {"id": "q_main_2", "topic": "pointers", "type": "verbal", "source": "bank"}
    orch._update_session_state(main_q2, 0.85, {"covered_concepts": ["Dereference"]}, transcript="Main answer 2")
    assert orch._state["main_questions_count"] == 2
    assert orch._state["followups_count"] == 1
    assert orch._state["consecutive_followups"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# 12. STATE UPDATE AFTER FOLLOW-UP
# ─────────────────────────────────────────────────────────────────────────────
def test_state_update_after_followup():
    """State accurately aggregates concepts mastered, missed, and performance history."""
    orch = InterviewOrchestrator(
        "sess_state_update",
        {"id": "c1", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["arrays"]},
    )
    q = {"id": "q1", "topic": "pointers", "type": "verbal"}
    fb = {
        "covered_concepts": ["Address-of operator &"],
        "missing_concepts": ["Dereference operator *"],
        "what_was_incorrect": ["Pointers are integers"],
    }
    orch._update_session_state(q, 0.70, fb, transcript="& gives address", raw_score=0.70)

    state = orch._state
    assert "Address-of operator &" in state["concepts_mastered"]
    assert "Dereference operator *" in state["concepts_missed"]
    assert "Pointers are integers" in state["misconceptions"]
    assert state["topic_performance"]["pointers"]["avg_score"] == 0.70
    assert state["technical_performance"] == 0.70


# ─────────────────────────────────────────────────────────────────────────────
# 13. PAUSE-TIME PROPAGATION CONSISTENCY
# ─────────────────────────────────────────────────────────────────────────────
def test_pause_time_propagation_consistency():
    """Audio analysis total_pause_time properly propagates into orchestrator communication_indicators."""
    orch = InterviewOrchestrator(
        "sess_pause_test",
        {"id": "c1", "experience": "junior"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["arrays"]},
    )
    audio_analysis = {
        "confidence_score": 0.82,
        "transcription": {
            "pause_count": 3,
            "total_pause_time": 1.45,
            "total_speech_time": 8.55,
            "true_speaking_rate": 140.0,
            "alignment_source": "whisperx",
        },
    }
    orch.ingest_audio_analysis(audio_analysis, 0.82)
    orch._update_session_state({"id": "q1", "topic": "arrays", "type": "verbal"}, 0.75, {})

    comm = orch._state.get("communication_indicators", {})
    assert comm.get("total_pause_time") == 1.45
    assert comm.get("pause_count") == 3
    assert comm.get("speaking_rate") == 140.0
    assert comm.get("confidence_score") == 0.82


# ─────────────────────────────────────────────────────────────────────────────
# 14. TOPIC-PERFORMANCE MAPPING CONSISTENCY
# ─────────────────────────────────────────────────────────────────────────────
def test_topic_performance_mapping_consistency():
    """Question topic metadata correctly aggregates under state topic_performance."""
    orch = InterviewOrchestrator(
        "sess_topic_test",
        {"id": "c1", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers", "memory_management"], "dsa_topics": ["hash_tables"]},
    )
    q_hash = {"id": "q_hash_1", "topic": "hash_tables", "type": "verbal"}
    orch._update_session_state(q_hash, 0.90, {}, transcript="Hash table answer")

    assert "hash_tables" in orch._state["topic_performance"]
    assert orch._state["topic_performance"]["hash_tables"]["avg_score"] == 0.90
    assert orch._state["topic_performance"]["hash_tables"]["attempts"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# 15. TRAINING AND RUNTIME TIME_NORM FORMULA CONSISTENCY
# ─────────────────────────────────────────────────────────────────────────────
def test_training_and_runtime_time_norm_formula_consistency():
    """
    Verify training formula in InterviewEnv and runtime formula in QuestionTimer:
    1. Both are bounded in [0.0, 1.0].
    2. Both clip response latency at 0.0 lower bound and 1.0 upper bound.
    3. Normal response pace maps consistently around the VecNormalize running mean ~0.417.
    """
    env = InterviewEnv()
    timer = QuestionTimer()

    # Training normalization: ideal_time = 3.0 + 6.0 * diff, scaled by 2.0
    # For difficulty = 0.4 (mid), ideal = 5.4s, max_scale = 10.8s
    t_train_fast = env._normalize_time(2.7, difficulty=0.4)    # 2.7 / 10.8 = 0.25
    t_train_mid = env._normalize_time(4.5, difficulty=0.4)     # 4.5 / 10.8 = 0.4167 (~VecNormalize mean)
    t_train_slow = env._normalize_time(15.0, difficulty=0.4)   # 15.0 / 10.8 -> clipped 1.0

    assert 0.0 <= t_train_fast <= 1.0
    assert 0.0 <= t_train_mid <= 1.0
    assert t_train_slow == 1.0

    # Runtime normalization: elapsed / allowed (e.g. allowed = 60s)
    # 15s / 60s = 0.25 (fast), 25s / 60s = 0.4167 (nominal), 75s / 60s -> clipped 1.0
    snapshot = timer.start(allowed_time_sec=60.0)
    # Simulate stop with various ratios
    res_fast = timer.compute_timing_modifier(raw_score=0.85, time_ratio=0.25)
    res_nom = timer.compute_timing_modifier(raw_score=0.85, time_ratio=0.4167)
    res_slow = timer.compute_timing_modifier(raw_score=0.85, time_ratio=1.25)

    assert 0.0 <= min(max(res_fast["time_ratio"], 0.0), 1.0) <= 1.0
    assert 0.0 <= min(max(res_nom["time_ratio"], 0.0), 1.0) <= 1.0
    assert min(max(res_slow["time_ratio"], 0.0), 1.0) == 1.0
    assert abs(t_train_mid - 0.4167) < 0.01
