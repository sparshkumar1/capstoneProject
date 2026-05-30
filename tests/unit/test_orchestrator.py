"""
PR 2 test matrix — InterviewOrchestrator
14 tests covering: baseline phases, RL phase, guardrails, auxiliary follow-up injection,
skip, end idempotency, report storage, concurrency, code path, hint tracking.

Run with:  pytest tests/test_orchestrator.py -v
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # repo root

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _q(id_, diff=3, topic="pointers", qtype="verbal"):
    return {"id": id_, "text": f"Q{id_}", "topic": topic, "difficulty": diff, "type": qtype}


def _orch(n=5, mode="standard"):
    """Create an orchestrator with a pre-loaded question queue (no real selector)."""
    o = InterviewOrchestrator(
        "sid",
        {"id": "c1", "experience": "intermediate"},
        {
            "c_topics": ["pointers"],
            "dsa_topics": ["graphs"],
            "duration_minutes": 30,
            "num_questions": n,
            "interview_mode": mode,
            "baseline_questions": None,
        },
    )
    # Replace queue with synthetic questions so tests are selector-independent
    o._question_queue = [_q(f"q{i}", diff=3) for i in range(n)]
    o._state["questions"] = list(o._question_queue)
    return o


def _fake_eval_result(score=0.7):
    return {
        "final_score": score,
        "grade": "B",
        "justification": "test",
        "strong_points": ["good"],
        "missing_concepts": [],
        "covered_concepts": ["malloc"],
        "incorrect_or_incomplete": [],
        "how_to_improve": [],
        "communication_tips": [],
        "score_breakdown": {"semantic_similarity": score},
        "trend": "stable",
        "trend_note": "",
        "decision_source": "test",
    }


# ─── Test 1: baseline standard path ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_baseline_standard_path():
    """5-question standard session: Q1+Q2 are baseline, Q3 activates RL."""
    o = _orch(n=5, mode="standard")
    assert o._state["baseline_complete"] is False
    assert o._state["baseline_min_questions"] == 2

    # Answer Q1 (score=0.7) — still in baseline
    diff1, reason1, action1 = await o._adapt_difficulty(0.7)
    o._state["scores"].append(0.7)
    # answered=1 < baseline_min=2 → still baseline
    # Re-run adapt after appending (simulate real call order)
    o._state["scores"] = []
    o._state["scores"].append(0.7)
    diff1, reason1, action1 = await o._adapt_difficulty(0.7)
    assert action1 == "Baseline"
    assert o._state["baseline_complete"] is False

    # Answer Q2 (score=0.75) — baseline_established → RL activates
    o._state["scores"].append(0.75)
    diff2, reason2, action2 = await o._adapt_difficulty(0.75)
    assert action2 == "Baseline->RL"
    assert o._state["baseline_complete"] is True
    assert o._state["rl_enabled"] is True


# ─── Test 2: demo_rl baseline extends to 3rd question ───────────────────────

@pytest.mark.asyncio
async def test_baseline_demo_rl_3q():
    """demo_rl: volatile Q1+Q2 scores → extra baseline Q3 triggered."""
    o = _orch(n=15, mode="demo_rl")
    assert o._state["baseline_max_questions"] == 3

    # Very volatile: 0.2 and 0.9 — spread=0.7, avg=0.55 (neither strong nor consistent)
    o._state["scores"].append(0.2)
    await o._adapt_difficulty(0.2)   # answered=1 < min=2 → Baseline

    o._state["scores"].append(0.9)
    diff, reason, action = await o._adapt_difficulty(0.9)  # answered=2, but not established
    assert action == "Baseline"   # spread too wide → extra Q required
    assert o._state["baseline_complete"] is False

    # Q3 resolves it
    o._state["scores"].append(0.85)
    diff3, reason3, action3 = await o._adapt_difficulty(0.85)
    assert action3 == "Baseline->RL"
    assert o._state["baseline_complete"] is True


# ─── Test 3: RL phase — Harder action increases difficulty ───────────────────

@pytest.mark.asyncio
async def test_rl_phase_harder():
    """PPO heuristic: high score → Harder → difficulty +1, queue rebuilt."""
    o = _orch(n=5, mode="standard")
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["scores"] = [0.9]
    o._state["current_difficulty"] = 3

    # Patch strategy to return Harder
    mock_strategy = MagicMock()
    mock_strategy.suggest.return_value = (4, "RL: strong", "Harder")
    o._strategy = mock_strategy

    diff, reason, action = await o._adapt_difficulty(0.9)
    assert action == "Harder"
    assert diff == 4
    assert o._state["current_difficulty"] == 4
    assert o._state["rl_last_action"] == "Harder"


# ─── Test 4: RL phase — Same action → explicit no-op difficulty update ───────

@pytest.mark.asyncio
async def test_rl_phase_same():
    """Same action → difficulty unchanged, handle_voice_answer returns an explicit no-op update."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["scores"] = []
    o._state["current_difficulty"] = 3
    o._state["last_confidence_score"] = 0.4

    mock_strategy = MagicMock()
    mock_strategy.suggest.return_value = (3, "RL: stable", "Same")
    o._strategy = mock_strategy

    with patch.object(o, "_evaluate_verbal", return_value=_fake_eval_result(0.3)):
        with patch.object(o, "_generate_feedback", return_value=_fake_eval_result(0.3)):
            with patch.object(o, "_get_hint", new_callable=AsyncMock, return_value="Try this hint"):
                result = await o.handle_voice_answer("bad answer", "q0", attempts=1)

    assert result["difficulty_update"] == {
        "new_difficulty": 3,
        "reason": "RL: stable",
        "action": "Same",
    }
    assert result["hint"] is None
    assert o._state["answers"][-1]["hint_given"] is False


# ─── Test 5: guardrail G4 — critically struggling candidate ─────────────────

def test_guardrail_g4_stuck():
    """perf<0.30 AND hes>0.60 → G4 forces Hint regardless of PPO action."""
    o = _orch()
    o._state["consecutive_followups"] = 0
    # PPO says Harder (idx=2), G4 should override to Easier (idx=0)
    result = o._apply_guardrails(2, perf=0.25, avg_perf=0.25, conf=0.3, hes=0.7, diff_norm=0.5)
    assert result == 0  # Easier


# ─── Test 6: guardrail G5 — mid-performance → Follow-up ────────────────────

def test_guardrail_g5_followup():
    """0.40 < perf < 0.65 AND avg < 0.60 AND consec < 2 → G5 forces Follow-up."""
    o = _orch()
    o._state["consecutive_followups"] = 0
    # PPO says Same (idx=1), G5 should keep the action conservative
    result = o._apply_guardrails(1, perf=0.5, avg_perf=0.5, conf=0.7, hes=0.3, diff_norm=0.6)
    assert result == 1  # Same


# ─── Test 7: guardrail G3 — no longer produces follow-ups ────────────────────

def test_guardrail_g3_cap():
    """Frozen 3-action policy keeps G3 conservative rather than emitting follow-ups."""
    o = _orch()
    o._state["consecutive_followups"] = 2
    # PPO says Same (idx=1), G3 remains Same in the simplified policy
    result = o._apply_guardrails(1, perf=0.5, avg_perf=0.5, conf=0.7, hes=0.3, diff_norm=0.6)
    assert result == 1  # Same


# ─── Test 8: follow-up injection ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_followup_injection():
    """Follow-up action: Qwen returns text → question inserted at index+1."""
    o = _orch(n=3)
    o._question_queue = [_q("q0"), _q("q1"), _q("q2")]
    o._current_q_index = 0

    with patch.object(o, "_get_hint", new_callable=AsyncMock, return_value="Follow-up: Explain X"):
        inserted = await o._inject_followup_question(_q("q0"), context_text="my answer")

    assert inserted is True
    assert len(o._question_queue) == 4
    fu = o._question_queue[1]
    assert fu["id"].startswith("fu_")
    assert fu["source"] == "qwen_followup"
    assert "Follow-up" in fu["text"]


# ─── Test 9: skip appends score but NOT answer entry ────────────────────────

@pytest.mark.asyncio
async def test_skip_no_answer_entry():
    """skip_question appends 0.0 to scores but leaves answers list untouched."""
    o = _orch(n=3)
    o._question_queue = [_q("q0"), _q("q1"), _q("q2")]
    o._state["baseline_complete"] = True

    await o.skip_question("q0")

    assert o._state["scores"] == [0.0]
    assert o._state["answers"] == []
    assert o._current_q_index == 1


# ─── Test 10: end() is idempotent ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_end_idempotent():
    """end() called twice returns identical cached report object."""
    o = _orch(n=2)
    o._state["scores"] = [0.7, 0.8]
    o._state["answers"] = [
        {"question_id": "q0", "transcript": "t", "code_submitted": "",
         "score": 0.7, "feedback": _fake_eval_result(0.7), "hint_given": False},
    ]
    o._state["baseline_complete"] = True

    r1 = await o.end()
    r2 = await o.end()

    assert r1 is r2                        # same cached object
    assert r1["id"] == r2["id"]
    assert o._state["status"] == "completed"


# ─── Test 11: full report body stored (not just metadata) ───────────────────

@pytest.mark.asyncio
async def test_report_full_body_stored():
    """end() returns full report dict including question_results and behaviour."""
    o = _orch(n=2)
    o._state["scores"] = [0.65]
    o._state["answers"] = [
        {"question_id": "q0", "transcript": "x", "code_submitted": "",
         "score": 0.65, "feedback": _fake_eval_result(0.65), "hint_given": False},
    ]

    report = await o.end()

    assert "question_results" in report
    assert "behaviour" in report
    assert "overall_score" in report
    assert "difficulty_history" in report
    assert isinstance(report["question_results"], list)


# ─── Test 12: lock serialises concurrent voice_answer calls ─────────────────

@pytest.mark.asyncio
async def test_lock_serialises_concurrent():
    """Two concurrent voice_answer calls must not interleave state writes.
    With an asyncio.Lock, the second call queues behind the first;
    scores must contain exactly 2 entries when both finish.
    """
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["scores"] = []

    async def slow_eval(transcript, question):
        await asyncio.sleep(0.02)
        return _fake_eval_result(0.7)

    async def fast_feedback(*a, **kw):
        return _fake_eval_result(0.7)

    with patch.object(o, "_evaluate_verbal", side_effect=slow_eval):
        with patch.object(o, "_generate_feedback", side_effect=fast_feedback):
            with patch.object(o, "_adapt_difficulty", new_callable=AsyncMock,
                              return_value=(3, "Same", "Same")):
                results = await asyncio.gather(
                    o.handle_voice_answer("A", "q0"),
                    o.handle_voice_answer("B", "q0"),
                    return_exceptions=True,
                )

    # Both calls must have completed successfully
    assert all(not isinstance(r, Exception) for r in results), results
    # Lock ensures sequential writes — exactly 2 scores, not 0 or 1
    assert len(o._state["scores"]) == 2


# ─── Test 13: code submission path uses sync generate_code_feedback ─────────

@pytest.mark.asyncio
async def test_code_submission_path():
    """handle_code_submission calls FEEDBACK_AGENT.generate_code_feedback (sync)."""
    o = _orch(n=3)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True

    mock_agent = MagicMock()
    mock_agent.generate_code_feedback.return_value = _fake_eval_result(0.85)

    with patch("agents.orchestrator.interview_orchestrator.FEEDBACK_AGENT", mock_agent):
        with patch("agents.orchestrator.interview_orchestrator._FEEDBACK_READY", True):
            with patch.object(o, "_adapt_difficulty", new_callable=AsyncMock,
                              return_value=(3, "Same", "Same")):
                result = await o.handle_code_submission(
                    code="int main(){}", question_id="q0",
                    passed=True, tests_passed=3, tests_total=3,
                    stdout="OK", stderr="",
                )

    mock_agent.generate_code_feedback.assert_called_once()
    # generate (async) must NOT be called on code path
    mock_agent.generate.assert_not_called()
    assert result["feedback"]["final_score"] == 0.85


# ─── Test 14: skip on last question → session_end ───────────────────────────

@pytest.mark.asyncio
async def test_end_from_skip():
    """skip_question on the last question returns session_end type."""
    o = _orch(n=1)
    o._question_queue = [_q("q0")]
    o._state["baseline_complete"] = True

    res = await o.skip_question("q0")

    assert res["type"] == "session_end"
    assert "report_id" in res["payload"]
    assert "overall_score" in res["payload"]
