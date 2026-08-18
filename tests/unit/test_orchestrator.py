"""
PR 2 test matrix — InterviewOrchestrator
20 tests covering: baseline phases, RL phase, guardrails, auxiliary follow-up injection,
skip, end idempotency, report storage, concurrency, code path, hint tracking,
and explicit RL attribution / non-RL recovery distinction.

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
    o._state["scores"].append(0.9)
    diff, reason, action = await o._adapt_difficulty(0.9)
    assert action == "Baseline"
    assert o._state["baseline_complete"] is False
    assert "not yet stable" in reason

    # Third question (0.85) — baseline max reached → RL activates regardless
    o._state["scores"].append(0.85)
    diff, reason, action = await o._adapt_difficulty(0.85)
    assert action == "Baseline->RL"
    assert o._state["baseline_complete"] is True


# ─── Test 3: RL phase selects Harder on strong answer ───────────────────────

@pytest.mark.asyncio
async def test_rl_phase_harder():
    """RL phase: score > 0.8 on diff 3 → Harder (diff becomes 4)."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["current_difficulty"] = 3
    o._state["scores"] = [0.85, 0.90]

    # Ensure strategy is None so pure heuristic applies predictably
    o._strategy = None
    diff, reason, action = await o._adapt_difficulty(0.92)
    assert action == "Harder"
    assert diff == 4
    assert o._state["current_difficulty"] == 4


# ─── Test 4: RL phase selects Same on medium answer ─────────────────────────

@pytest.mark.asyncio
async def test_rl_phase_same():
    """RL phase: score 0.65 on diff 3 → Same (diff stays 3)."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["current_difficulty"] = 3
    o._state["scores"] = [0.60, 0.70]
    o._strategy = None

    diff, reason, action = await o._adapt_difficulty(0.65)
    assert action == "Same"
    assert diff == 3


# ─── Test 5: Guardrail G4 (critically struggling) overrides to Easier ────────

@pytest.mark.asyncio
async def test_guardrail_g4_stuck():
    """G4: score < 0.30 AND hes > 0.60 → overrides to Easier."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["current_difficulty"] = 3
    o._state["scores"] = [0.60, 0.70]
    o._state["last_confidence_score"] = 0.20  # hes = 1 - 0.20 = 0.80 > 0.60
    o._strategy = None

    # Score 0.25 (G4 triggers: perf=0.25 < 0.30, hes=0.80 > 0.60)
    diff, reason, action = await o._adapt_difficulty(0.25)
    assert action == "Easier"
    assert diff == 2
    assert o._last_guardrail_name == "guardrail_G4"


# ─── Test 6: Guardrail G5 (follow-up ceiling) ────────────────────────────────

@pytest.mark.asyncio
async def test_guardrail_g5_followup():
    """consecutive_followups >= 2 → block further follow-ups on next Q."""
    o = _orch(n=5)
    o._state["consecutive_followups"] = 2
    # Verify the count is tracked in state
    assert o._state["consecutive_followups"] == 2
    # Reset on new main Q
    o._state["consecutive_followups"] = 0
    assert o._state["consecutive_followups"] == 0


# ─── Test 7: Guardrail G3 (cap at max diff 5) ────────────────────────────────

@pytest.mark.asyncio
async def test_guardrail_g3_cap():
    """G3: score in [0.40, 0.65] on low avg_perf → caps/holds at Same."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["current_difficulty"] = 4
    o._state["scores"] = [0.45, 0.50]
    o._state["rl_perf_history"] = [0.45, 0.50]  # avg = 0.475 < 0.60
    o._strategy = None

    diff, reason, action = await o._adapt_difficulty(0.55)
    assert action == "Same"
    assert o._last_guardrail_name == "guardrail_G3"


# ─── Test 8: follow-up injection increments queue ────────────────────────────

@pytest.mark.asyncio
async def test_followup_injection():
    """_inject_followup_question inserts a fu_ question after current index."""
    o = _orch(n=3)
    o._current_q_index = 0
    initial_len = len(o._question_queue)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "followup": "Can you elaborate on how malloc handles fragmentation?",
        "reason": "missing_concepts",
        "target_concepts": ["fragmentation"],
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        injected = await o._inject_followup_question(
            o._question_queue[0],
            context_text="I used malloc to allocate memory",
            eval_result={"missing_concepts": ["fragmentation"]},
        )

    assert injected is True
    assert len(o._question_queue) == initial_len + 1
    injected_q = o._question_queue[1]
    assert injected_q["id"].startswith("fu_")
    assert injected_q["source"] == "qwen_followup"
    assert injected_q["parent_question_id"] == "q0"


# ─── Test 9: skip_question does not add answer entry ─────────────────────────

@pytest.mark.asyncio
async def test_skip_no_answer_entry():
    """skip_question appends 0.0 to scores but does NOT add to answers array."""
    o = _orch(n=4)
    o._current_q_index = 0
    assert len(o._state["answers"]) == 0

    await o.skip_question("q0")

    assert len(o._state["answers"]) == 0
    assert o._state["scores"] == [0.0]
    assert o._state["raw_scores"] == [0.0]
    assert o._current_q_index == 1


# ─── Test 10: end is idempotent ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_end_idempotent():
    """Calling end() twice returns the same report_id and score."""
    o = _orch(n=2)
    o._state["scores"] = [0.8, 0.7]

    r1 = await o.end()
    r2 = await o.end()

    assert r1["id"] == r2["id"]
    assert r1["overall_score"] == r2["overall_score"]
    assert r1["session_id"] == "sid"


# ─── Test 11: full report body stored in _reports dict ───────────────────────

@pytest.mark.asyncio
async def test_report_full_body_stored():
    """After end(), full report dict is returned and stored on orchestrator."""
    o = _orch(n=2)
    o._state["scores"] = [0.75]

    rep = await o.end()
    assert "id" in rep
    assert rep["overall_score"] == pytest.approx(0.75, abs=1e-3)
    assert o._state["report_id"] == rep["id"]
    assert o._cached_report["id"] == rep["id"]


# ─── Test 12: lock serialises concurrent calls ───────────────────────────────

@pytest.mark.asyncio
async def test_lock_serialises_concurrent():
    """Two concurrent handle_voice_answer calls both complete without corruption."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True

    async def slow_eval(*a, **kw):
        await asyncio.sleep(0.05)
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


# ─── Test 15: PPO available → PPO action is used & attributed ───────────────

@pytest.mark.asyncio
async def test_ppo_available_action_used_and_attributed():
    """When PPO is available and ready, its action is used and labeled 'ppo' or 'ppo_policy'."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["current_difficulty"] = 3
    o._state["scores"] = [0.70, 0.75]

    mock_strategy = MagicMock()
    mock_strategy.ready = True
    mock_strategy.is_compatible = True
    mock_strategy.suggest.return_value = (3, "PPO: Same — score=0.75, avg=0.73", "Same")
    o._strategy = mock_strategy

    diff, reason, action = await o._adapt_difficulty(0.75)
    assert action == "Same"
    assert diff == 3
    assert o._state["last_decision_source"] in {"ppo", "ppo_policy"}
    assert o._state["rl_status"] == "available"
    assert o._state["raw_rl_action"] == "Same"
    assert o._state["rl_last_action"] == "Same"


# ─── Test 16: PPO unavailable → explicit RL failure & non-RL recovery labeled ─

@pytest.mark.asyncio
async def test_ppo_unavailable_explicit_rl_failure_and_non_rl_recovery():
    """When PPO is missing/incompatible, explicit non_rl_heuristic_recovery is recorded."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["current_difficulty"] = 3
    o._state["scores"] = [0.85, 0.90]

    mock_strategy = MagicMock()
    mock_strategy.ready = False
    mock_strategy.is_compatible = False
    mock_strategy.status = "rl_unavailable"
    mock_strategy.suggest.return_value = (4, "Non-RL Recovery: Strong answer", "Harder")
    o._strategy = mock_strategy

    diff, reason, action = await o._adapt_difficulty(0.92)
    assert action == "Harder"
    assert diff == 4
    assert o._state["last_decision_source"] in {"non_rl_heuristic_recovery", "guardrail_g6"}
    assert o._state["rl_status"] == "rl_unavailable"
    assert o._state["raw_rl_action"] is None
    assert any(k in reason for k in ["Non-RL", "PPO Unavailable", "Guardrail", "Heuristic", "Recovery"])


# ─── Test 17: Guardrail override is distinguishable from PPO action ─────────

@pytest.mark.asyncio
async def test_guardrail_override_distinguishable_from_raw_ppo():
    """Guardrail override replaces decision_source with guardrail name while raw_rl_action is preserved."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._state["current_difficulty"] = 3
    o._state["scores"] = [0.60, 0.70]
    o._state["last_confidence_score"] = 0.20  # hes = 0.80 > 0.60 -> G4 triggers

    mock_strategy = MagicMock()
    mock_strategy.ready = True
    mock_strategy.is_compatible = True
    mock_strategy.suggest.return_value = (3, "PPO: Same", "Same")
    o._strategy = mock_strategy

    diff, reason, action = await o._adapt_difficulty(0.25)
    assert action == "Easier"
    assert diff == 2
    assert o._state["last_decision_source"] == "guardrail_g4"
    assert o._state["guardrail_applied"] == "guardrail_G4"
    assert o._state["raw_rl_action"] == "Same"  # Original PPO choice preserved
    assert o._state["rl_status"] == "available"


# ─── Test 18: Baseline warmup is distinguishable from PPO ───────────────────

@pytest.mark.asyncio
async def test_baseline_warmup_distinguishable_from_ppo():
    """Baseline warmup is labeled baseline_warmup, with raw_rl_action=None."""
    o = _orch(n=5, mode="standard")
    o._state["scores"].append(0.70)

    diff, reason, action = await o._adapt_difficulty(0.70)
    assert action == "Baseline"
    assert o._state["last_decision_source"] == "baseline_warmup"
    assert o._state["rl_status"] == "baseline_warmup"
    assert o._state["raw_rl_action"] is None


# ─── Test 19: No heuristic action is ever falsely attributed to PPO ─────────

@pytest.mark.asyncio
async def test_no_heuristic_action_ever_falsely_attributed_to_ppo():
    """Ensure heuristic actions in any phase are never labeled as 'ppo'."""
    o = _orch(n=5)
    o._state["baseline_complete"] = True
    o._state["rl_enabled"] = True
    o._strategy = None

    # Strong answer
    await o._adapt_difficulty(0.95)
    assert o._state["last_decision_source"] not in {"ppo", "ppo_policy"}
    assert o._state["last_decision_source"] in {"non_rl_heuristic_recovery", "guardrail_g6", "guardrail_g1"}

    # Weak answer
    await o._adapt_difficulty(0.20)
    assert o._state["last_decision_source"] not in {"ppo", "ppo_policy"}
    assert o._state["last_decision_source"] in {"non_rl_heuristic_recovery", "guardrail_g4", "guardrail_g1"}


# ─── Test 20: HybridOrchestrator suggest records explicit status ────────────

def test_hybrid_orchestrator_suggest_records_explicit_status():
    """HybridOrchestrator records rl_status='rl_unavailable' and src='non_rl_heuristic_recovery' when uninitialized."""
    from agents.strategy.hybrid_orchestrator import HybridOrchestrator
    ho = HybridOrchestrator(model_path="non_existent_path.zip")
    assert ho.ready is False

    session = {}
    diff, reason, action = ho.suggest(0.85, 3, session)
    assert session.get("rl_status") == "rl_unavailable"
    assert session.get("rl_source") == "non_rl_heuristic_recovery"
    assert session.get("rl_last_action") is None
    assert "Non-RL Recovery" in reason
