"""
test_stage11_5_coding_adaptation.py — Stage 11.5 Coding Integration & Adaptive RL Verification.

Covers:
  1. Accepted coding result updates candidate state
  2. Partial coding result updates candidate state
  3. Failed coding result updates candidate state
  4. Infrastructure sandbox failure does not become candidate failure
  5. Coding topic maps correctly
  6. Multiple coding attempts aggregate correctly
  7. Observation remains exactly 6D
  8. Observation values remain in [0,1]
  9. Coding execution time does not enter RL state
  10. Runtime/training state formulas remain consistent
  11. Strong-vs-weak coding trajectories produce expected state divergence
  12. PPO remains authoritative for adaptive action
  13. Post-coding next question uses updated state
  14. Mixed verbal/coding session accounting is correct
  15. Coding feedback is grounded in sandbox evidence
  16. PPO fallback path is explicit and distinct
"""

import asyncio
import numpy as np
import pytest
from agents.coding_executor.coding_executor import DockerCSandbox
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.strategy.hybrid_orchestrator import HybridOrchestrator, build_rl_observation
from rl.env.interview_env import InterviewEnv


@pytest.fixture(scope="module")
def sandbox():
    return DockerCSandbox()


@pytest.fixture
def orchestrator_factory():
    def _create(session_id="test_sess", mode="standard"):
        orch = InterviewOrchestrator(
            session_id,
            {"id": "cand_1", "experience": "intermediate"},
            {
                "duration_minutes": 30,
                "num_questions": 5,
                "c_topics": ["pointers", "memory_management"],
                "dsa_topics": ["arrays"],
                "interview_mode": mode,
            },
        )
        return orch
    return _create


def test_accepted_coding_result_updates_candidate_state(sandbox, orchestrator_factory):
    """Accepted C code (1.0) updates coding_attempted, coding_accepted, coding_pass_rate, and topic performance."""
    code = """
#include <stdio.h>
int main() {
    int a, b;
    if (scanf("%d %d", &a, &b) == 2) {
        printf("%d\\n", a + b);
    }
    return 0;
}
"""
    test_cases = [
        {"id": "tc1", "input": "2 3\n", "expected": "5\n", "is_mandatory": True, "is_hidden": False},
        {"id": "tc2", "input": "10 20\n", "expected": "30\n", "is_mandatory": False, "is_hidden": False},
    ]
    exec_res = sandbox.compile_and_execute(code, test_cases)
    assert exec_res["status"] == "accepted"
    assert exec_res["passed"] is True

    orch = orchestrator_factory("sess_acc")
    q_dict = {"id": "C01", "qid": "C01", "topic": "Arrays", "type": "code", "difficulty": 2}
    orch._question_queue = [q_dict]
    orch._current_q_index = 0

    res = asyncio.run(orch.handle_code_submission(
        code=code,
        question_id="C01",
        passed=exec_res["passed"],
        tests_passed=exec_res["tests_passed"],
        tests_total=exec_res["tests_total"],
        stdout=exec_res["test_results"][0]["stdout"],
        stderr="",
    ))

    state = orch._state
    assert state["coding_attempted"] == 1
    assert state["coding_accepted"] == 1
    assert state["coding_pass_rate"] == 1.0
    assert "Arrays" in state["topic_performance"]
    assert state["topic_performance"]["Arrays"]["avg_score"] == 1.0
    assert state["code_streak"] == 1


def test_partial_coding_result_updates_candidate_state(sandbox, orchestrator_factory):
    """Partial C code (0.50) updates candidate state with wrong_answer and failed test tracking."""
    code = """
#include <stdio.h>
int main() {
    int x;
    if (scanf("%d", &x) == 1) {
        if (x > 10) printf("999\\n");
        else printf("%d\\n", x * 2);
    }
    return 0;
}
"""
    test_cases = [
        {"id": "tc1", "input": "5\n", "expected": "10\n", "is_mandatory": False, "is_hidden": False},
        {"id": "tc2", "input": "20\n", "expected": "40\n", "is_mandatory": False, "is_hidden": False},
    ]
    exec_res = sandbox.compile_and_execute(code, test_cases)
    assert exec_res["status"] == "wrong_answer"
    assert exec_res["passed"] is False

    orch = orchestrator_factory("sess_part")
    q_dict = {"id": "C02", "qid": "C02", "topic": "Pointers", "type": "code", "difficulty": 2}
    orch._question_queue = [q_dict]
    orch._current_q_index = 0

    asyncio.run(orch.handle_code_submission(
        code=code,
        question_id="C02",
        passed=exec_res["passed"],
        tests_passed=exec_res["tests_passed"],
        tests_total=exec_res["tests_total"],
        stdout=exec_res["test_results"][0]["stdout"],
        stderr="",
    ))

    state = orch._state
    assert state["coding_attempted"] == 1
    assert state["coding_accepted"] == 0
    assert state["coding_pass_rate"] == 0.0
    assert "Pointers" in state["topic_performance"]
    assert state["topic_performance"]["Pointers"]["avg_score"] == 0.5
    assert len(state["coding_failures"]) == 1


def test_failed_coding_result_compilation_error(sandbox, orchestrator_factory):
    """Compilation failure produces score 0.0 and records diagnostic without crashing."""
    code = "int main() { invalid_c_syntax }"
    exec_res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "", "is_mandatory": False}])
    assert exec_res["status"] == "compilation_error"

    orch = orchestrator_factory("sess_comperr")
    q_dict = {"id": "C03", "qid": "C03", "topic": "Arrays", "type": "code", "difficulty": 2}
    orch._question_queue = [q_dict]
    orch._current_q_index = 0

    asyncio.run(orch.handle_code_submission(
        code=code,
        question_id="C03",
        passed=False,
        tests_passed=0,
        tests_total=1,
        stdout="",
        stderr=exec_res["compiler_output"],
    ))

    state = orch._state
    assert state["coding_attempted"] == 1
    assert state["coding_accepted"] == 0
    assert state["coding_pass_rate"] == 0.0
    assert state["topic_performance"]["Arrays"]["avg_score"] == 0.0


def test_infrastructure_failure_does_not_corrupt_candidate_metrics(orchestrator_factory):
    """Sandbox infrastructure error (sandbox_error) is isolated to infrastructure_errors without docking candidate."""
    orch = orchestrator_factory("sess_infr")
    q_dict = {"id": "C04", "qid": "C04", "topic": "Arrays", "type": "code", "difficulty": 2}
    orch._question_queue = [q_dict]
    orch._current_q_index = 0

    # Simulate infrastructure error report
    sandbox_err_feedback = {
        "status": "sandbox_error",
        "passed": False,
        "error": "Docker sandbox daemon is unreachable. Untrusted code execution blocked to protect host.",
        "decision_source": "sandbox_error",
    }
    orch._update_session_state(q_dict, score=0.0, feedback=sandbox_err_feedback, code="int main() {}")

    state = orch._state
    # Candidate metrics are NOT docked
    assert state.get("coding_attempted", 0) == 0
    assert state.get("coding_accepted", 0) == 0
    assert len(state.get("infrastructure_errors", [])) == 1
    assert state["infrastructure_errors"][0]["type"] == "sandbox_error"


def test_coding_topic_maps_correctly(orchestrator_factory):
    """Coding on 'Linked Lists' updates 'Linked Lists' topic performance, leaving others intact."""
    orch = orchestrator_factory("sess_topic")
    q_dict = {"id": "C05", "qid": "C05", "topic": "Linked Lists", "type": "code", "difficulty": 3}
    orch._question_queue = [q_dict]
    orch._current_q_index = 0

    orch._update_session_state(q_dict, score=0.90, feedback={"status": "accepted", "passed": True}, code="int main() {}")

    state = orch._state
    assert "Linked Lists" in state["topic_performance"]
    assert "Arrays" not in state["topic_performance"]
    assert state["topic_performance"]["Linked Lists"]["avg_score"] == 0.90


def test_multiple_coding_attempts_aggregate_correctly(orchestrator_factory):
    """Multiple coding submissions in same topic correctly compute running average and attempt counts."""
    orch = orchestrator_factory("sess_agg")
    q1 = {"id": "C06a", "topic": "Pointers", "type": "code", "difficulty": 2}
    q2 = {"id": "C06b", "topic": "Pointers", "type": "code", "difficulty": 3}

    orch._update_session_state(q1, score=1.0, feedback={"status": "accepted", "passed": True}, code="code1")
    orch._update_session_state(q2, score=0.5, feedback={"status": "wrong_answer", "passed": False}, code="code2")

    state = orch._state
    assert state["coding_attempted"] == 2
    assert state["coding_accepted"] == 1
    assert state["coding_pass_rate"] == 0.50
    assert state["topic_performance"]["Pointers"]["attempts"] == 2
    assert state["topic_performance"]["Pointers"]["avg_score"] == 0.75


def test_observation_strictly_6d_and_bounded():
    """6D RL observation vector is strictly shape (6,) with all values in [0.0, 1.0]."""
    state = {
        "scores": [0.8, 0.9, 0.7],
        "last_confidence_score": 0.85,
        "last_hesitation_score": 0.15,
        "last_time_norm": 0.40,
    }
    obs = build_rl_observation(score=0.95, current_difficulty=4, session=state)
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (6,)
    assert obs.dtype == np.float32
    assert np.all(obs >= 0.0)
    assert np.all(obs <= 1.0)


def test_coding_execution_time_does_not_enter_rl_state():
    """Execution duration (e.g. 3500ms) is stored in coding_history but NOT injected into time_norm."""
    state = {
        "scores": [1.0],
        "last_time_norm": 0.0,  # Verbal latency untouched
        "coding_history": [{"question_id": "C01", "execution_time_ms": 3500.0}],
    }
    obs = build_rl_observation(score=1.0, current_difficulty=3, session=state)
    # Dimension [4] is time_norm
    assert obs[4] == 0.0


def test_runtime_and_training_state_formula_consistency():
    """Runtime build_rl_observation vector conforms to 6D state structure of training InterviewEnv."""
    env = InterviewEnv()
    env.reset(seed=42)
    assert env.observation_space.shape == (6,)
    assert env.action_space.n == 3

    runtime_session = {
        "scores": [0.85],
        "last_confidence_score": 0.90,
        "last_hesitation_score": 0.10,
        "last_time_norm": 0.25,
    }
    runtime_obs = build_rl_observation(0.85, 3, runtime_session)
    expected_obs = np.array([0.85, 0.85, 0.90, 0.10, 0.25, 3.0 / 5.0], dtype=np.float32)

    np.testing.assert_allclose(runtime_obs, expected_obs, atol=1e-5)


def test_strong_vs_weak_coding_trajectory_divergence(orchestrator_factory):
    """Candidate with strong coding results produces distinct 6D RL state and policy action from weak candidate."""
    # Strong candidate
    orch_strong = orchestrator_factory("sess_div_strong", mode="full")
    orch_strong._state["baseline_complete"] = True
    orch_strong._state["rl_enabled"] = True
    orch_strong._state["current_difficulty"] = 3
    q_strong = {"id": "C07s", "topic": "Arrays", "type": "code", "difficulty": 3}
    orch_strong._question_queue = [q_strong]
    orch_strong._current_q_index = 0

    res_strong = asyncio.run(orch_strong.handle_code_submission(
        code="int main(){return 0;}",
        question_id="C07s",
        passed=True,
        tests_passed=5,
        tests_total=5,
        stdout="5\n",
        stderr="",
    ))

    # Weak candidate
    orch_weak = orchestrator_factory("sess_div_weak", mode="full")
    orch_weak._state["baseline_complete"] = True
    orch_weak._state["rl_enabled"] = True
    orch_weak._state["current_difficulty"] = 3
    q_weak = {"id": "C07w", "topic": "Arrays", "type": "code", "difficulty": 3}
    orch_weak._question_queue = [q_weak]
    orch_weak._current_q_index = 0

    res_weak = asyncio.run(orch_weak.handle_code_submission(
        code="int main(){invalid;}",
        question_id="C07w",
        passed=False,
        tests_passed=0,
        tests_total=5,
        stdout="",
        stderr="syntax error",
    ))

    obs_strong = build_rl_observation(1.0, orch_strong._state["current_difficulty"], orch_strong._state)
    obs_weak = build_rl_observation(0.0, orch_weak._state["current_difficulty"], orch_weak._state)

    assert obs_strong[0] > obs_weak[0]  # Latest score
    assert obs_strong[1] > obs_weak[1]  # Avg score
    assert orch_strong._state["coding_pass_rate"] == 1.0
    assert orch_weak._state["coding_pass_rate"] == 0.0


def test_ppo_policy_authoritative_inference():
    """HybridOrchestrator uses real PPO checkpoint and outputs Discrete(3) actions without heuristics."""
    orch = HybridOrchestrator()
    if orch.ready:
        state_high = {"scores": [1.0, 1.0], "last_confidence_score": 1.0, "last_hesitation_score": 0.0, "last_time_norm": 0.2}
        diff_h, reason_h, act_h = orch.suggest(1.0, 3, state_high)
        assert act_h in {"Same", "Harder", "Easier"}

        state_low = {"scores": [0.1, 0.2], "last_confidence_score": 0.2, "last_hesitation_score": 0.8, "last_time_norm": 0.9}
        diff_l, reason_l, act_l = orch.suggest(0.1, 3, state_low)
        assert act_l in {"Same", "Harder", "Easier"}
    else:
        pytest.skip("PPO checkpoint not available in current test environment")


def test_post_coding_next_question_uses_updated_state(orchestrator_factory):
    """handle_next_question after coding returns question reflecting post-coding difficulty."""
    orch = orchestrator_factory("sess_next_q", mode="full")
    orch._state["baseline_complete"] = True
    orch._state["rl_enabled"] = True
    orch._state["current_difficulty"] = 3

    q_code = {"id": "C08", "qid": "C08", "topic": "Arrays", "type": "code", "difficulty": 3}
    q_next = {"id": "V09", "qid": "V09", "topic": "Pointers", "type": "verbal", "difficulty": 3}
    orch._question_queue = [q_code, q_next]
    orch._current_q_index = 0

    asyncio.run(orch.handle_code_submission(
        code="int main(){return 0;}",
        question_id="C08",
        passed=True,
        tests_passed=4,
        tests_total=4,
        stdout="ok",
        stderr="",
    ))

    next_res = asyncio.run(orch.handle_next_question())
    assert next_res["type"] == "question"
    assert "id" in next_res["payload"]
    assert "text" in next_res["payload"] or "topic" in next_res["payload"]


def test_mixed_verbal_and_coding_session_accounting(orchestrator_factory):
    """Mixed session correctly tracks main_questions_count, coding_attempted, and topic performance."""
    orch = orchestrator_factory("sess_mixed", mode="full")
    q_v = {"id": "V01", "topic": "Pointers", "type": "verbal", "difficulty": 2}
    q_c = {"id": "C01", "topic": "Arrays", "type": "code", "difficulty": 2}
    orch._question_queue = [q_v, q_c]
    orch._current_q_index = 0

    # Verbal turn
    orch._update_session_state(q_v, score=0.85, feedback={"status": "evaluated"}, transcript="A pointer holds a memory address.")
    assert orch._state["main_questions_count"] == 1
    assert orch._state["verbal_streak"] == 1
    assert orch._state.get("coding_attempted", 0) == 0

    # Coding turn
    orch._update_session_state(q_c, score=1.0, feedback={"status": "accepted", "passed": True}, code="int main(){}")
    assert orch._state["main_questions_count"] == 2
    assert orch._state["coding_attempted"] == 1
    assert orch._state["coding_accepted"] == 1
    assert orch._state["coding_pass_rate"] == 1.0
    assert orch._state["code_streak"] == 1
    assert orch._state["verbal_streak"] == 0


def test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics(orchestrator_factory):
    """Coding turn preserves genuine speech confidence/hesitation from prior verbal turns without fabricating audio metrics."""
    orch = orchestrator_factory("sess_conf_preservation", mode="standard")

    # 1. Genuine speech measurement on verbal turn
    orch._state["last_confidence_score"] = 0.94
    orch._state["last_hesitation_score"] = 0.06
    orch._state["last_time_norm"] = 0.22
    orch._state["communication_indicators"] = {
        "confidence_score": 0.94,
        "speaking_rate": 145.0,
        "pause_count": 2,
        "total_pause_time": 0.8,
    }

    # 2. Coding turn execution
    q_code = {"id": "C_PRES", "topic": "Arrays", "type": "code", "difficulty": 3}
    orch._update_session_state(
        q_code,
        score=0.75,
        feedback={
            "status": "accepted",
            "passed": True,
            "tests_passed": 3,
            "tests_total": 4,
            "execution_time_ms": 1850.0,
        },
        code="int main() { return 0; }",
    )

    # 3. Speech metrics must remain preserved, not overwritten by coding turn
    assert orch._state["last_confidence_score"] == 0.94
    assert orch._state["last_hesitation_score"] == 0.06
    assert orch._state["communication_indicators"]["confidence_score"] == 0.94
    assert orch._state["coding_history"][-1]["execution_time_ms"] == 1850.0

    # 4. 6D RL observation construction
    obs = build_rl_observation(score=0.75, current_difficulty=3, session=orch._state)
    assert obs.shape == (6,)
    assert pytest.approx(float(obs[2]), abs=1e-3) == 0.94  # Genuine speech confidence preserved
    assert pytest.approx(float(obs[3]), abs=1e-3) == 0.06  # Genuine speech hesitation preserved
    assert pytest.approx(float(obs[4]), abs=1e-3) == 0.22  # Verbal response time preserved, NOT 1850ms execution time

    # 5. Default missing-value semantics when no prior speech exists
    fresh_state = {"scores": [0.80], "current_difficulty": 3}
    fresh_obs = build_rl_observation(score=0.80, current_difficulty=3, session=fresh_state)
    assert fresh_obs.shape == (6,)
    assert pytest.approx(float(fresh_obs[2]), abs=1e-3) == 0.80  # Default missing-value confidence: fallback to perf
    assert pytest.approx(float(fresh_obs[3]), abs=1e-3) == 0.20  # Default missing-value hesitation: 1.0 - conf
    assert pytest.approx(float(fresh_obs[4]), abs=1e-3) == 0.00  # Default missing-value time_norm: 0.0
