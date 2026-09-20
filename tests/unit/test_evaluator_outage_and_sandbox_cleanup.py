"""Regression tests for the two defects found by the X1-A campaign (build A -> build B).

FLT-03: an evaluator outage must fail closed (no candidate score recorded, no difficulty adaptation, no persisted attempt,
        attempt not consumed) instead of being stored as a 0.0 answer.
FLT-06: a compile/run timeout must remove the sandbox container, not only kill the docker client.
"""
import asyncio
import subprocess
from unittest.mock import MagicMock, patch

import pytest

import agents.coding_executor.coding_executor as ce
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator

Q = {"id": "q1", "text": "Explain a pointer.", "topic": "pointers", "difficulty": 3, "type": "verbal",
     "expected_concepts": ["pointer dereference"], "reference_answer": "An address."}
OK = {"final_score": 0.8, "raw_evaluator_score": 0.8, "grade": "Good", "covered_concepts": ["pointer dereference"],
      "missing_concepts": [], "decision_source": "evaluator_cross_encoder", "mandatory_pass": True}


def _orch(evaluator):
    o = InterviewOrchestrator("s", {"experience": "intermediate"}, {"c_topics": ["pointers"], "dsa_topics": [], "duration_minutes": 30,
                                                                     "num_questions": 4, "interview_mode": "standard"})
    o._select_questions_fn = None
    o._question_queue = [dict(Q), dict(Q, id="q2"), dict(Q, id="q3"), dict(Q, id="q4")]
    o._state["questions"] = list(o._question_queue)
    asyncio.run(o.start())
    o._evaluator_fn = evaluator
    return o


def _raise(t, q):
    raise ConnectionError("evaluator 503")


def test_evaluator_outage_records_no_score_and_is_retryable():
    o = _orch(_raise)
    before = (list(o._state["scores"]), o._state.get("current_difficulty"), dict(o._attempt_counts), list(o._state["answers"]))
    resp = asyncio.run(o.handle_voice_answer("A pointer stores an address.", "q1"))
    fb = resp["feedback"]
    assert fb["status"] == "evaluator_unavailable" and fb["infrastructure_failure"] is True and fb["final_score"] is None
    assert resp["difficulty_update"] is None and resp["next_action"] == "retry_answer"
    assert (list(o._state["scores"]), o._state.get("current_difficulty"), dict(o._attempt_counts), list(o._state["answers"])) == before
    assert o._state["infrastructure_errors"] == [{"question_id": "q1", "type": "evaluator_unavailable", "error": o._state["infrastructure_errors"][0]["error"]}]
    assert not o._state.get("pending_next", False)
    # the same question can be answered once the evaluator is back, and is then scored normally
    o._evaluator_fn = lambda t, q: dict(OK)
    resp2 = asyncio.run(o.handle_voice_answer("A pointer stores an address.", "q1"))
    assert resp2["feedback"].get("status") != "evaluator_unavailable" and len(o._state["scores"]) == 1 and o._state["scores"][0] > 0.0


def test_evaluator_returning_nothing_is_also_an_outage():
    o = _orch(lambda t, q: None)
    resp = asyncio.run(o.handle_voice_answer("answer", "q1"))
    assert resp["feedback"]["status"] == "evaluator_unavailable" and o._state["scores"] == []


def test_normal_evaluation_unchanged():
    o = _orch(lambda t, q: dict(OK))
    resp = asyncio.run(o.handle_voice_answer("A pointer stores an address.", "q1"))
    assert resp["feedback"].get("status") != "evaluator_unavailable" and len(o._state["scores"]) == 1
    assert resp["next_action"] in ("wait_for_next", "session_end")


def test_empty_transcript_semantics_unchanged():
    o = _orch(lambda t, q: dict(OK))
    resp = asyncio.run(o.handle_voice_answer("", "q1"))
    assert resp["feedback"]["stt_status"] == "stt_unavailable" and resp["feedback"]["grade"] == "Ungraded"


class _Recorder:
    """Stands in for the subprocess module inside the executor; the compile step times out."""
    TimeoutExpired = subprocess.TimeoutExpired
    PIPE = subprocess.PIPE

    def __init__(self):
        self.calls = []

    def run(self, cmd, *a, **kw):
        self.calls.append(list(cmd))
        if len(cmd) > 1 and cmd[1] == "run":
            raise subprocess.TimeoutExpired(cmd, kw.get("timeout", 0))
        return MagicMock(returncode=0, stdout="", stderr="")


def test_compile_timeout_removes_the_named_container():
    rec = _Recorder()
    sb = ce.DockerCSandbox()
    sb._cmd_prefix = ["docker"]
    with patch.object(ce, "subprocess", rec):
        res = sb.compile_and_execute("int main(void){return 0;}\n", [{"id": "t", "input": "", "expected": ""}])
    assert res["status"] == "compilation_error" and "timed out" in res["compiler_output"].lower()
    run_cmd = next(c for c in rec.calls if c[1] == "run")
    name = run_cmd[run_cmd.index("--name") + 1]
    assert ["docker", "rm", "-f", name] in rec.calls


def test_container_names_are_unique():
    assert ce.DockerCSandbox._new_container_name() != ce.DockerCSandbox._new_container_name()


# ---- Qwen feedback: llm_status must be truthful (build A hard-coded "available" even for the service's template) ----
from agents.orchestrator.feedback_agent import FeedbackAgent


def _fb(qwen_res):
    agent = FeedbackAgent()

    async def fake(*a, **k):
        return qwen_res

    agent._query_qwen_feedback = fake
    ev = {"final_score": 0.7, "covered_concepts": ["a"], "missing_concepts": [], "decision_source": "evaluator_cross_encoder"}
    return asyncio.run(agent.generate(transcript="t", question={"id": "q", "text": "x", "topic": "pointers"}, eval_result=ev))


def test_llm_status_reports_the_services_template_as_unavailable():
    fb = _fb({"what_candidate_said": "t", "narrative_feedback": "n", "llm_status": "llm_unavailable", "decision_source": "non_llm_structured_recovery"})
    assert fb["llm_status"] == "llm_unavailable" and fb["decision_source"] == "non_llm_structured_recovery"


def test_llm_status_available_when_the_service_says_so_or_is_silent():
    assert _fb({"what_candidate_said": "t", "llm_status": "available", "decision_source": "qwen_1.5b_llm"})["llm_status"] == "available"
    assert _fb({"what_candidate_said": "t"})["llm_status"] == "available"


def test_evaluator_outage_persists_no_attempt():
    """Build A wrote an attempt with raw_score 0.0 to the database when a candidate id existed; build B must not touch storage."""
    o = _orch(_raise)
    o._state["candidate_id"] = "cand_x1a_probe"
    with patch("services.storage.database.save_attempt", side_effect=AssertionError("attempt must not be persisted")) as sa, \
            patch("services.storage.database.get_question_attempts", side_effect=AssertionError("no history lookup on outage")):
        resp = asyncio.run(o.handle_voice_answer("A pointer stores an address.", "q1"))
    assert resp["feedback"]["status"] == "evaluator_unavailable" and not sa.called
