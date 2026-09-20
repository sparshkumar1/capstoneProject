"""
Regression tests: num_questions is the PRIMARY-question budget.

Follow-ups are continuations of a primary question. They are queued in addition to the primary questions, never
evict one, never consume budget, and the session ends only after the primary budget is spent AND any follow-up
queued for the last answered question has been delivered and answered (a follow-up to the final primary question
is delivered under the same consecutive-follow-up cap as everywhere else).

Run with:
    EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest tests/unit/test_primary_question_budget.py -q
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

N = 15

WEAK = {"final_score": 0.50, "covered_concepts": [], "missing_concepts": ["gap"], "incorrect_claims": [],
        "weakest_gap": "gap", "decision_source": "evaluator_cross_encoder"}
STRONG = {"final_score": 0.90, "covered_concepts": ["a"], "missing_concepts": [], "incorrect_claims": [],
          "weakest_gap": "None - comprehensive answer", "decision_source": "evaluator_cross_encoder"}


def _orch(n=N):
    o = InterviewOrchestrator("sid", {"experience": "intermediate"},
                              {"c_topics": ["pointers"], "dsa_topics": ["graphs"], "duration_minutes": 30,
                               "num_questions": n, "interview_mode": "demo_rl" if n >= N else "standard"})
    o._select_questions_fn = None          # keep the synthetic queue (no re-selection); no persistence (no id)
    o._question_queue = [{"id": f"q{i}", "text": f"Explain topic {i}.", "topic": "pointers", "difficulty": 3,
                          "type": "verbal"} for i in range(n)]
    o._state["questions"] = list(o._question_queue)
    return o


def _followup_http():
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"followup": "Can you elaborate on how that behaves for edge cases?",
                              "reason": "missing_concepts", "target_concepts": ["gap"]}
    return patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=resp)


async def _answer(o, q, weak):
    ev = WEAK if weak else STRONG
    with patch.object(o, "_evaluate_verbal", new_callable=AsyncMock, return_value=dict(ev)), \
            patch.object(o, "_generate_feedback", new_callable=AsyncMock, side_effect=lambda *a, **k: dict(ev)):
        return await o.handle_voice_answer("An answer to the question.", q["id"])


async def _run(o, weak_at):
    """Drive a whole session. `weak_at(q)` -> True makes that answer weak (triggers the follow-up policy).
    Returns the list of delivered question payloads (primary + follow-ups) in order."""
    delivered = []
    q = await o.start()
    with _followup_http():
        for _ in range(60):
            delivered.append(q)
            resp = await _answer(o, q, weak_at(q))
            nxt = await o.handle_next_question()
            if resp["next_action"] == "session_end":
                assert nxt["type"] == "session_end"
                return delivered
            if nxt["type"] == "session_end":
                return delivered
            q = nxt["payload"]
    raise AssertionError("session did not terminate")


primaries = lambda d: [q for q in d if not q["is_followup"]]
followups = lambda d: [q for q in d if q["is_followup"]]


# ── A. 15-primary-question budget ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_A1_no_followups_gives_15_primary_questions():
    o = _orch()
    d = await _run(o, lambda q: False)
    assert len(d) == 15 and len(followups(d)) == 0
    assert [q["id"] for q in primaries(d)] == [f"q{i}" for i in range(N)]
    assert o._state["main_questions_count"] == 15


@pytest.mark.asyncio
async def test_A2_followup_after_q1_still_reaches_q15():
    o = _orch()
    d = await _run(o, lambda q: (not q["is_followup"]) and q["primary_question_index"] == 1)
    assert len(followups(d)) == 1 and len(primaries(d)) == 15
    assert [q["id"] for q in primaries(d)] == [f"q{i}" for i in range(N)]     # q14 (Question 15) delivered
    assert d[1]["is_followup"] is True and d[1]["parent_question_index"] == 1
    assert d[-1]["id"] == "q14" and d[-1]["primary_question_index"] == 15


@pytest.mark.asyncio
async def test_A3_multiple_followups_still_reach_q15_and_do_not_consume_budget():
    o = _orch()
    weak_primaries = {1, 4, 7, 10}
    d = await _run(o, lambda q: (not q["is_followup"]) and q["primary_question_index"] in weak_primaries)
    assert len(followups(d)) == 4 and len(primaries(d)) == 15
    assert len(d) == 19                                                        # turns > 15 is intended
    assert [q["id"] for q in primaries(d)] == [f"q{i}" for i in range(N)]
    assert o._state["main_questions_count"] == 15 and o._state["followups_count"] == 4


# ── B. Question 15 ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_B_followup_to_q15_is_delivered_then_session_ends():
    o = _orch()
    d = await _run(o, lambda q: (not q["is_followup"]) and q["primary_question_index"] == 15)
    assert len(primaries(d)) == 15 and d[-2]["id"] == "q14"                    # Q15 delivered
    last = d[-1]
    assert last["is_followup"] is True and last["primary_question_index"] == 15 and last["parent_question_index"] == 15
    assert last["source"] == "qwen_followup"                                    # delivered, not popped/evicted
    assert o._state["main_questions_count"] == 15 and o._state["followups_count"] == 1
    assert o._cached_report is not None                                         # ended only after it was answered


@pytest.mark.asyncio
async def test_B_q15_followup_chain_respects_consecutive_cap_of_two():
    o = _orch()
    d = await _run(o, lambda q: q["primary_question_index"] == 15)              # Q15 and its follow-ups stay weak
    assert len(primaries(d)) == 15 and len(followups(d)) == 2                   # cap: never a third in a row
    assert o._cached_report is not None


@pytest.mark.asyncio
async def test_B_q15_without_followup_ends_after_q15():
    o = _orch()
    resp = None
    q = await o.start()
    for i in range(N):
        resp = await _answer(o, q, False)
        if i < N - 1:
            q = (await o.handle_next_question())["payload"]
    assert q["id"] == "q14" and resp["next_action"] == "session_end"


# ── C. Queue ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_C_injected_followup_does_not_evict_a_primary_question():
    o = _orch()
    before = [q["id"] for q in o._question_queue]
    with _followup_http():
        assert await o._inject_followup_question(o._question_queue[0], "ctx", dict(WEAK)) is True
    assert len(o._question_queue) == N + 1
    assert [q["id"] for q in o._question_queue if not q["id"].startswith("fu_")] == before
    assert o._question_queue[1]["id"].startswith("fu_")
    assert not hasattr(o, "_evicted_by_followup")                               # eviction bookkeeping is gone


@pytest.mark.asyncio
async def test_C_retry_removes_unserved_followup_without_touching_primaries():
    o = _orch()
    q = await o.start()
    with _followup_http():
        await _answer(o, q, True)                                               # attempt 1 injects a follow-up
        assert o._question_queue[1]["id"].startswith("fu_")
        await o.handle_retry(q["id"])
    assert [x["id"] for x in o._question_queue] == [f"q{i}" for i in range(N)]
    assert o._state["main_questions_count"] == 0                                # the retried attempt was rolled back


@pytest.mark.asyncio
async def test_C_retries_do_not_consume_primary_slots():
    o = _orch()
    q = await o.start()
    for _ in range(3):                                                          # three attempts at Q1
        await _answer(o, q, False)
        await o.handle_retry(q["id"])
    await _answer(o, q, False)
    assert o._state["main_questions_count"] == 1
    nxt = await o.handle_next_question()
    assert nxt["payload"]["primary_question_index"] == 2 and o._state["main_questions_count"] == 1


@pytest.mark.asyncio
async def test_C_skipped_primary_counts_toward_budget():
    o = _orch()
    await o.start()
    res = None
    for i in range(N):
        assert o._cached_report is None
        res = await o.skip_question("")
    assert res["type"] == "session_end" and o._state["main_questions_count"] == N


# ── D. Termination ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_D_session_does_not_terminate_early_at_turn_15():
    o = _orch()
    q = await o.start()
    with _followup_http():
        for turn in range(1, 16):                                               # 15 turns, first one has a follow-up
            resp = await _answer(o, q, weak=(turn == 1))
            assert resp["next_action"] == "wait_for_next", turn
            q = (await o.handle_next_question())["payload"]
    assert len(o._state["scores"]) == 15                                        # len(scores) == 15 is NOT the end
    assert o._cached_report is None and o._state["main_questions_count"] == 14
    assert q["id"] == "q14"                                                     # Question 15 still to come


@pytest.mark.asyncio
async def test_D_duplicate_next_after_session_end_is_idempotent():
    o = _orch(n=2)
    d = await _run(o, lambda q: False)
    assert len(d) == 2
    again = await o.handle_next_question()
    assert again["type"] == "session_end"


# ── numbering payload ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_payload_numbering_distinguishes_followups_from_primaries():
    o = _orch()
    d = await _run(o, lambda q: (not q["is_followup"]) and q["primary_question_index"] in (1, 2))
    seq = [(q["primary_question_index"], q["is_followup"]) for q in d[:6]]
    assert seq == [(1, False), (1, True), (2, False), (2, True), (3, False), (4, False)]
    assert all(q["total_questions"] == N for q in d)
    assert [q["turn_index"] for q in d] == list(range(1, len(d) + 1))          # legacy field: delivered-turn position
    assert all(q["parent_question_index"] is None for q in primaries(d))
