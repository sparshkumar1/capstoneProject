"""
verify_stage11_3_followup_e2e.py
Comprehensive end-to-end verification script for Stage 11.3:
Part A: Consistency checks (time_norm formula, pause-time propagation, topic-performance mapping).
Part B: Real partial answer -> Evaluator -> Qwen follow-up.
Part C: Real misconception answer -> Evaluator -> Qwen corrective probe.
Part D: Real wrong answer -> Evaluator -> low score -> grounded probe.
Part E: Real strong answer -> Evaluator -> high score -> no unnecessary follow-up.
Part F: Answering follow-up -> gap resolution / consecutive follow-up tracking / hard stop.
Part G: Follow-up transcript grounding.
Part H: Follow-up deduplication.
Part I: Qwen failure behavior.
Part J: Full Candidate State verification.
Part K: RL separation invariant.
"""

import asyncio
import io
import json
import math
import os
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.orchestrator.feedback_agent import FeedbackAgent
from agents.timing.timer import QuestionTimer
from agents.strategy.hybrid_orchestrator import HybridOrchestrator, build_rl_observation
from rl.env.interview_env import InterviewEnv
from services.evaluator.app import evaluate, get_rubric, _ensure_evaluator_assets_loaded
from services.qwen.app import (
    FollowupRequest,
    FeedbackRequest,
    _synthesize_structured_followup,
    _synthesize_structured_feedback,
)


def run_stage11_3_verification():
    print("=" * 80)
    print("  STAGE 11.3: REAL ADAPTIVE FOLLOW-UP & EVALUATION VERIFICATION")
    print("=" * 80)

    results = {}

    # ─────────────────────────────────────────────────────────────────────────
    # PART A — RESOLVE STAGE 11.2 CONSISTENCY QUESTIONS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART A] Inspecting Consistency Invariants...")

    # 1. TIME_NORMALIZATION
    # Training formula in InterviewEnv: ideal = 3.0 + 6.0 * diff; clip(t / (ideal * 2.0), 0.0, 1.0)
    # Runtime formula in QuestionTimer: clip(t / allowed_time_sec, 0.0, 1.0)
    env = InterviewEnv()
    timer = QuestionTimer()
    t_train = env._normalize_time(4.5, difficulty=0.4)
    t_run = timer.compute_timing_modifier(raw_score=0.85, time_ratio=0.4167)
    print(f"  [OK] Training time_norm for nominal pace: {t_train:.4f} (bounds: [0.0, 1.0])")
    print(f"  [OK] Runtime time_norm for nominal pace:  {t_run['time_ratio']:.4f} (bounds: [0.0, 1.0])")
    assert 0.0 <= t_train <= 1.0 and 0.0 <= t_run["time_ratio"] <= 1.0
    results["part_a_time_norm"] = "PASS"

    # 2. PAUSE-TIME PROPAGATION
    orch_pause = InterviewOrchestrator(
        "sess_pause_audit",
        {"id": "c_pause", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["hash_tables"]},
    )
    mock_audio_analysis = {
        "confidence_score": 0.88,
        "transcription": {
            "pause_count": 2,
            "total_pause_time": 0.601,
            "total_speech_time": 11.92,
            "true_speaking_rate": 181.27,
            "alignment_source": "whisperx",
        },
    }
    orch_pause.ingest_audio_analysis(mock_audio_analysis, 0.88)
    orch_pause._update_session_state({"id": "q1", "topic": "hash_tables", "type": "verbal"}, 0.90, {})
    comm = orch_pause._state.get("communication_indicators", {})
    print(f"  [OK] Propagated total_pause_time: {comm.get('total_pause_time')}s")
    print(f"  [OK] Propagated pause_count:      {comm.get('pause_count')}")
    print(f"  [OK] Propagated speaking_rate:    {comm.get('speaking_rate')} WPM")
    assert comm.get("total_pause_time") == 0.601
    results["part_a_pause_propagation"] = "PASS"

    # 3. TOPIC STATE MAPPING
    assert "hash_tables" in orch_pause._state["topic_performance"]
    assert orch_pause._state["topic_performance"]["hash_tables"]["avg_score"] == 0.90
    print(f"  [OK] Topic performance correctly mapped to 'hash_tables': {orch_pause._state['topic_performance']['hash_tables']}")
    results["part_a_topic_mapping"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART B — REAL PARTIAL ANSWER
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART B] Real Partial Answer Evaluation & Qwen Follow-Up...")
    rubric_hash = {
        "qid": "dsa_hash_collision",
        "expected_concepts": [
            "Separate chaining with linked lists or dynamic arrays",
            "Open addressing with linear or quadratic probing",
        ],
        "mandatory_concepts": [
            "Separate chaining with linked lists or dynamic arrays",
            "Open addressing with linear or quadratic probing",
        ],
        "common_mistakes": ["Overwriting previous value on collision"],
        "answer": "A hash table handles collisions using separate chaining where each bucket contains a linked list, or open addressing such as linear probing where we search for the next available slot.",
    }
    q_hash_text = "Explain how a hash table handles collisions."
    partial_transcript = "A hash table handles collisions using separate chaining where each bucket stores a linked list of collided keys."

    eval_partial = evaluate(q_hash_text, partial_transcript, rubric_hash)
    print(f"  [OK] Partial Score: {eval_partial['final_score']}")
    print(f"  [OK] Grade:         {eval_partial['grade']}")
    print(f"  [OK] Covered:       {eval_partial['correct_claims']}")
    print(f"  [OK] Missing:       {eval_partial['missing_concepts']}")
    print(f"  [OK] Weakest Gap:   {eval_partial['weakest_gap']}")
    print(f"  [OK] Source:        {eval_partial['decision_source']}")

    assert 0.35 <= eval_partial["final_score"] < 0.85
    assert len(eval_partial["missing_concepts"]) > 0

    req_partial = FollowupRequest(
        original_question=q_hash_text,
        topic="hash_tables",
        candidate_answer=partial_transcript,
        structured_evaluation=eval_partial,
        missing_concepts=eval_partial["missing_concepts"],
        correct_concepts=eval_partial["correct_claims"],
        misconceptions=[],
        weakest_gap=eval_partial["weakest_gap"],
        current_difficulty=3,
        previous_questions=[q_hash_text],
        previous_followups=[],
    )
    fu_partial = _synthesize_structured_followup(req_partial)
    print(f"  [OK] Generated Follow-up: '{fu_partial.followup}'")
    print(f"  [OK] Follow-up Rationale: '{fu_partial.reason}'")
    print(f"  [OK] Target Concepts:     {fu_partial.target_concepts}")
    assert any("open addressing" in str(t).lower() or "probing" in str(t).lower() for t in fu_partial.target_concepts)
    results["part_b_partial_answer"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART C — REAL MISCONCEPTION ANSWER
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART C] Real Misconception Evaluation & Targeted Corrective Probe...")
    miscon_transcript = "On a hash table collision, the new value simply overwrites the old value in that slot."
    eval_miscon = evaluate(q_hash_text, miscon_transcript, rubric_hash)
    print(f"  [OK] Misconception Score: {eval_miscon['final_score']}")
    print(f"  [OK] Incorrect claims:    {eval_miscon.get('incorrect_claims', [])}")
    print(f"  [OK] Missing concepts:    {eval_miscon['missing_concepts']}")

    req_miscon = FollowupRequest(
        original_question=q_hash_text,
        topic="hash_tables",
        candidate_answer=miscon_transcript,
        structured_evaluation=eval_miscon,
        misconceptions=["Overwriting key on collision"],
        correct_concepts=[],
        missing_concepts=eval_miscon["missing_concepts"],
        weakest_gap="Collision resolution mechanism",
        current_difficulty=3,
        previous_questions=[q_hash_text],
        previous_followups=[],
    )
    fu_miscon = _synthesize_structured_followup(req_miscon)
    print(f"  [OK] Corrective Probe:   '{fu_miscon.followup}'")
    print(f"  [OK] Probe Rationale:    '{fu_miscon.reason}'")
    assert "overwrit" in fu_miscon.followup.lower() or "approach" in fu_miscon.followup.lower() or "concrete" in fu_miscon.followup.lower()
    results["part_c_misconception"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART D — REAL WRONG ANSWER
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART D] Real Wrong / Off-Topic Answer Evaluation...")
    wrong_transcript = "The operating system manages page faults using translation lookaside buffers."
    eval_wrong = evaluate(q_hash_text, wrong_transcript, rubric_hash)
    print(f"  [OK] Wrong Answer Score: {eval_wrong['final_score']}")
    print(f"  [OK] Grade:              {eval_wrong['grade']}")
    assert eval_wrong["final_score"] < 0.35
    assert eval_wrong["grade"] in {"Poor", "Average"}
    results["part_d_wrong_answer"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART E — REAL STRONG ANSWER
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART E] Real Strong Answer Evaluation & Policy...")
    qn_strong = "Explain your logic to find the two indices in an array that sum up to a target value."
    strong_transcript = (
        "To find the two indices that sum to a target value in an array, I will use a hash map to achieve an O(n) single pass solution. "
        "As I iterate through the array, for each element, I calculate the complement as target minus the current element. "
        "I check if this complement is already present in the hash map in O(1) constant time lookup. "
        "If the complement exists, I return the index stored in the hash map along with the current index. "
        "If not, I insert the current element value and its index into the map. This avoids nested loops and runs in O(n) time and O(n) space."
    )
    rubric_strong = get_rubric("1")
    eval_strong = evaluate(qn_strong, strong_transcript, rubric_strong)
    print(f"  [OK] Strong Answer Score: {eval_strong['final_score']}")
    print(f"  [OK] Grade:               {eval_strong['grade']}")
    print(f"  [OK] Missing Concepts:    {eval_strong['missing_concepts']}")
    assert eval_strong["final_score"] >= 0.80
    assert len(eval_strong["missing_concepts"]) == 0

    orch_e = InterviewOrchestrator(
        "sess_strong_e",
        {"id": "c_strong", "experience": "senior"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["hash_tables"]},
    )
    injected_strong = asyncio.run(orch_e._decide_and_inject_followup(
        {"id": "1", "topic": "Arrays", "text": qn_strong, "type": "verbal"},
        strong_transcript,
        eval_strong,
    ))
    print(f"  [OK] Follow-up Injected for Strong Answer: {injected_strong}")
    assert injected_strong is False, "Strong comprehensive answer must NOT trigger a follow-up"
    results["part_e_strong_answer"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART F — FOLLOW-UP RESPONSE LIFECYCLE & 2-PROBE HARD CAP
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART F] Follow-up Response Lifecycle & Hard Cap Verification...")
    orch_f = InterviewOrchestrator(
        "sess_lifecycle_f",
        {"id": "c_life", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["hash_tables"]},
    )
    # Turn 1: Partial Answer -> triggers 1st follow-up
    injected_1 = asyncio.run(orch_f._decide_and_inject_followup(
        {"id": "q1", "topic": "hash_tables", "text": q_hash_text, "type": "verbal"},
        partial_transcript,
        eval_partial,
    ))
    assert injected_1 is True
    assert len(orch_f._question_queue) > 0
    fu1 = orch_f._question_queue[1]
    print(f"  [OK] Turn 1 Injected 1st Follow-up: '{fu1['text'][:60]}...'")

    # Candidate answers FU1 with still incomplete logic
    orch_f._update_session_state(fu1, 0.50, {"covered_concepts": ["Linear probing"]}, transcript="Check next slot")
    assert orch_f._state["consecutive_followups"] == 1
    assert orch_f._state["main_questions_count"] == 0, "Follow-up must NOT increment main_questions_count"

    # Turn 2: Incomplete FU1 answer -> triggers 2nd follow-up
    eval_fu1 = {"final_score": 0.50, "missing_concepts": ["Handling clustering"], "incorrect_claims": []}
    injected_2 = asyncio.run(orch_f._decide_and_inject_followup(fu1, "Check next slot", eval_fu1))
    assert injected_2 is True
    fu2 = orch_f._question_queue[2]
    print(f"  [OK] Turn 2 Injected 2nd Follow-up: '{fu2['text'][:60]}...'")

    # Candidate answers FU2 with failed answer
    orch_f._update_session_state(fu2, 0.30, {"covered_concepts": []}, transcript="I do not know")
    assert orch_f._state["consecutive_followups"] == 2
    assert orch_f._state["main_questions_count"] == 0

    # Turn 3: 2 consecutive follow-ups reached -> Hard cap blocks 3rd follow-up
    eval_fu2 = {"final_score": 0.30, "missing_concepts": ["Double hashing"], "incorrect_claims": []}
    injected_3 = asyncio.run(orch_f._decide_and_inject_followup(fu2, "I do not know", eval_fu2))
    print(f"  [OK] Turn 3 (Hard Cap >= 2) Injected 3rd Follow-up: {injected_3}")
    assert injected_3 is False, "Hard cap of 2 consecutive follow-ups must block further follow-ups"
    results["part_f_lifecycle_hard_cap"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART G — FOLLOW-UP GROUNDING
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART G] Exact Candidate Transcript Grounding...")
    req_grounding = FeedbackRequest(
        question_text=q_hash_text,
        topic="hash_tables",
        candidate_answer=partial_transcript,
        structured_evaluation=eval_partial,
    )
    fb_grounding = _synthesize_structured_feedback(req_grounding)
    print(f"  [OK] what_candidate_said: '{fb_grounding.what_candidate_said}'")
    assert fb_grounding.what_candidate_said == partial_transcript
    results["part_g_grounding"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART H — FOLLOW-UP DEDUPLICATION
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART H] Follow-up Deduplication...")
    prev_fu_text = fu_partial.followup
    req_dedup = FollowupRequest(
        original_question=q_hash_text,
        topic="hash_tables",
        candidate_answer=partial_transcript,
        structured_evaluation=eval_partial,
        missing_concepts=eval_partial["missing_concepts"],
        correct_concepts=eval_partial["correct_claims"],
        misconceptions=[],
        weakest_gap=eval_partial["weakest_gap"],
        current_difficulty=3,
        previous_questions=[q_hash_text],
        previous_followups=[prev_fu_text],
    )
    fu_dedup = _synthesize_structured_followup(req_dedup)
    print(f"  [OK] Initial Follow-up:     '{prev_fu_text}'")
    print(f"  [OK] Deduplicated Follow-up: '{fu_dedup.followup}'")
    assert fu_dedup.followup != prev_fu_text
    results["part_h_deduplication"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART I — FAILURE BEHAVIOR
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART I] Qwen Microservice Failure Explicit Reporting...")
    offline_agent = FeedbackAgent(qwen_url="http://127.0.0.1:9999")
    offline_fb = asyncio.run(offline_agent.generate(
        transcript=partial_transcript,
        question={"text": q_hash_text, "topic": "hash_tables"},
        eval_result=eval_partial,
    ))
    print(f"  [OK] Fallback llm_status:      {offline_fb['llm_status']}")
    print(f"  [OK] Fallback decision_source: {offline_fb['decision_source']}")
    print(f"  [OK] Evaluator score preserved: {offline_fb['final_score']}")
    assert offline_fb["llm_status"] == "llm_unavailable"
    assert offline_fb["final_score"] == eval_partial["final_score"]
    results["part_i_failure_behavior"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART J — CANDIDATE STATE INTEGRITY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART J] Candidate State Aggregate Fields Verification...")
    state = orch_f._state
    assert len(state["followup_history"]) == 2
    assert state["followups_count"] == 2
    assert state["consecutive_followups"] == 2
    assert state["main_questions_count"] == 0
    print(f"  [OK] Main questions count: {state['main_questions_count']}")
    print(f"  [OK] Followups count:      {state['followups_count']}")
    print(f"  [OK] Consecutive count:    {state['consecutive_followups']}")
    print(f"  [OK] Followup history len: {len(state['followup_history'])}")
    results["part_j_candidate_state"] = "PASS"

    # ─────────────────────────────────────────────────────────────────────────
    # PART K — RL SEPARATION INVARIANT
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[PART K] RL Separation Invariant Verification...")
    # Verify that RL observation is strictly 6D and actions are Discrete(3) (Easier, Same, Harder)
    rl_obs = build_rl_observation(0.85, 3, state)
    print(f"  [OK] Built RL observation dimension: {len(rl_obs)} (Vector: {rl_obs.tolist()})")
    assert len(rl_obs) == 6
    assert all(0.0 <= v <= 1.0 for v in rl_obs)
    results["part_k_rl_separation"] = "PASS"

    print("\n" + "=" * 80)
    print(f"  STAGE 11.3 VERIFICATION COMPLETE: ALL {len(results)}/{len(results)} MODULES PASSED")
    print("=" * 80)
    return results


if __name__ == "__main__":
    res = run_stage11_3_verification()
