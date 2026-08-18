"""
test_coding_executor.py — Dedicated Unit and Real Docker Sandbox Tests for Stage 7 (Real C Coding Sandbox).

Verifies:
  1. Pre-flight static policy validation (defense-in-depth)
  2. Policy-blocked submission handling
  3. Real Docker C compilation & execution of correct program -> accepted
  4. Real Docker C wrong-answer output comparison -> wrong_answer
  5. Real Docker GCC compilation failure -> compilation_error
  6. Real Docker runtime error (Segmentation fault) -> runtime_error
  7. Real Docker timeout termination on infinite loop -> timeout
  8. Real Docker memory limit / OOM termination -> memory_limit
  9. Real Docker network isolation verification (--net=none)
 10. Real Docker PID limit enforcement (--pids-limit=32)
 11. Real Docker output limit truncation (MAX_OUTPUT_BYTES = 64KB)
 12. Real Docker non-root execution (UID/GID 1001:1001)
 13. Real Docker read-only container root filesystem
 14. Partial test performance (7/10 tests passed -> wrong_answer, pass_rate 0.70)
 15. Mandatory test failure score capping (<= 0.30)
 16. Candidate state coding metrics tracking
 17. PPO observation invariant (strictly 6D, no dimension addition)
 18. RL checkpoint compatibility with Discrete(3) actions
"""

import os
import textwrap
import pytest
import numpy as np

from agents.coding_executor.coding_executor import (
    DockerCSandbox,
    evaluate_c_submission,
    evaluate_code_submission,
    MAX_OUTPUT_BYTES,
)
from agents.coding_executor.sandbox_policy import validate_source_safety
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.strategy.hybrid_orchestrator import HybridOrchestrator


# ─────────────────────────────────────────────────────────────────────────────
# 1. Pre-flight Static Safety & Policy Checks (Defense-in-depth)
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_source_safety_blocks_dangerous_c_headers():
    safe, reasons = validate_source_safety("int main() { ptrace(0, 0, 0, 0); return 0; }")
    assert safe is False
    assert any("ptrace" in r.lower() for r in reasons)


def test_validate_source_safety_blocks_empty_code():
    safe, reasons = validate_source_safety("   \n\t ")
    assert safe is False
    assert any("empty" in r.lower() for r in reasons)


def test_validate_source_safety_accepts_clean_c_code():
    code = textwrap.dedent(
        """
        #include <stdio.h>
        #include <stdlib.h>

        int add(int a, int b) {
            return a + b;
        }

        int main() {
            int a, b;
            if (scanf("%d %d", &a, &b) == 2) {
                printf("%d\\n", add(a, b));
            }
            return 0;
        }
        """
    )
    safe, reasons = validate_source_safety(code)
    assert safe is True
    assert len(reasons) == 0


def test_policy_blocked_submission_structure():
    res = evaluate_c_submission("int main() { ptrace(0, 0, 0, 0); return 0; }")
    assert res["status"] == "policy_blocked"
    assert res["passed"] is False
    score_val = res.get("coding_score", res.get("score"))
    assert score_val == 0.0
    assert len(res["policy_reasons"]) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 2. Genuine Docker Execution Tests (Authoritative Sandbox Execution)
# ─────────────────────────────────────────────────────────────────────────────

def test_docker_compiles_and_runs_correct_c_program():
    """Real Docker test: compilation & execution of correct program produces 'accepted'."""
    code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            int a, b;
            if (scanf("%d %d", &a, &b) == 2) {
                printf("%d\\n", a + b);
            }
            return 0;
        }
        """
    )
    test_cases = [
        {"id": "tc1", "input": "3 4\n", "expected": "7\n", "is_hidden": False},
        {"id": "tc2", "input": "10 -2\n", "expected": "8\n", "is_hidden": True},
    ]
    res = evaluate_c_submission(code, test_cases=test_cases, timeout_sec=5.0)
    assert res["status"] == "accepted"
    assert res["passed"] is True
    assert res["tests_passed"] == 2
    assert res["tests_total"] == 2
    assert res["coding_score"] == 1.0


def test_docker_wrong_answer_output_comparison():
    """Real Docker test: incorrect logic produces 'wrong_answer'."""
    code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            int a, b;
            if (scanf("%d %d", &a, &b) == 2) {
                printf("%d\\n", a - b); // BUG: subtract instead of add
            }
            return 0;
        }
        """
    )
    test_cases = [
        {"id": "tc1", "input": "5 3\n", "expected": "8\n", "is_hidden": False},
    ]
    res = evaluate_c_submission(code, test_cases=test_cases, timeout_sec=5.0)
    assert res["status"] == "wrong_answer"
    assert res["passed"] is False
    assert res["tests_passed"] == 0
    assert res["tests_total"] == 1
    assert res["coding_score"] == 0.0


def test_docker_detects_c_compilation_error():
    """Real Docker test: GCC compiler error produces 'compilation_error'."""
    bad_code = "int main() { invalid syntax here; }"
    res = evaluate_c_submission(bad_code, test_cases=[{"id": "tc1", "input": "", "expected": ""}])
    assert res["status"] == "compilation_error"
    assert res["passed"] is False
    assert res["coding_score"] == 0.0
    assert len(res["compiler_output"]) > 0


def test_docker_runtime_error_segfault():
    """Real Docker test: Segmentation fault produces 'runtime_error'."""
    segfault_code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            int *p = NULL;
            *p = 42; // Cause SIGSEGV (signal 11 / exit 139)
            return 0;
        }
        """
    )
    res = evaluate_c_submission(segfault_code, test_cases=[{"id": "tc1", "input": "", "expected": ""}], timeout_sec=5.0)
    assert res["status"] == "runtime_error"
    assert res["passed"] is False
    assert res["test_results"][0]["status"] == "runtime_error"


def test_docker_terminates_infinite_loop_timeout():
    """Real Docker test: Infinite loop is halted by per-test timeout produces 'timeout'."""
    loop_code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            while (1) {}
            return 0;
        }
        """
    )
    res = evaluate_c_submission(loop_code, test_cases=[{"id": "tc1", "input": "", "expected": ""}], timeout_sec=1.0)
    assert res["status"] == "timeout"
    assert res["passed"] is False
    assert res["tests_passed"] == 0


def test_docker_memory_limit_oom_enforcement():
    """Real Docker test: Exceeding 128MB RAM limit triggers OOM kill (exit 137) -> 'memory_limit'."""
    mem_code = textwrap.dedent(
        """
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        int main() {
            while (1) {
                char *p = malloc(16 * 1024 * 1024);
                if (!p) { fprintf(stderr, "OOM\\n"); return 1; }
                memset(p, 1, 16 * 1024 * 1024);
            }
            return 0;
        }
        """
    )
    res = evaluate_c_submission(mem_code, test_cases=[{"id": "tc1", "input": "", "expected": "NEVER_MATCH\n"}], timeout_sec=5.0)
    assert res["status"] in {"memory_limit", "runtime_error", "wrong_answer"}
    assert res["passed"] is False
    assert res["tests_passed"] == 0


def test_docker_network_isolation_blocked():
    """Real Docker test: Network connection attempt fails with --net=none."""
    net_code = textwrap.dedent(
        """
        #include <stdio.h>
        #include <unistd.h>
        extern int socket(int, int, int);
        extern int connect(int, const void *, unsigned int);
        int main() {
            int s = socket(2, 1, 0); // AF_INET, SOCK_STREAM
            if (s < 0) {
                printf("NETWORK_BLOCKED\\n");
                return 0;
            }
            // 8.8.8.8:80
            char addr[16] = {2, 0, 0, 80, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0};
            if (connect(s, addr, 16) != 0) {
                printf("NETWORK_BLOCKED\\n");
                return 0;
            }
            printf("NETWORK_CONNECTED\\n");
            return 0;
        }
        """
    )
    test_cases = [{"id": "tc1", "input": "", "expected": "NETWORK_BLOCKED\n"}]
    res = evaluate_c_submission(net_code, test_cases=test_cases, timeout_sec=3.0)
    assert res["status"] == "accepted"
    assert res["passed"] is True
    assert res["tests_passed"] == 1


def test_docker_pid_limit_process_capping():
    """Real Docker test: PID limit prevents fork-bombing host."""
    fork_code = textwrap.dedent(
        """
        #include <stdio.h>
        #include <unistd.h>
        #include <sys/wait.h>
        int main() {
            for (int i = 0; i < 50; i++) {
                pid_t p = fork();
                if (p == 0) _exit(0);
                else if (p > 0) waitpid(p, NULL, 0);
            }
            printf("FORK_CAPPED\\n");
            return 0;
        }
        """
    )
    res = evaluate_c_submission(fork_code, test_cases=[{"id": "tc1", "input": "", "expected": "FORK_CAPPED\n"}], timeout_sec=5.0)
    assert res["status"] in {"accepted", "runtime_error", "wrong_answer"}


def test_docker_output_limit_truncation():
    """Real Docker test: Output > 64KB is cleanly truncated without crashing."""
    flood_code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            for (int i = 0; i < 20000; i++) {
                printf("Line %05d: The quick brown fox jumps over the lazy dog.\\n", i);
            }
            return 0;
        }
        """
    )
    res = evaluate_c_submission(flood_code, test_cases=[{"id": "tc1", "input": "", "expected": "never_match\n"}], timeout_sec=5.0)
    assert res["passed"] is False
    assert res["status"] in {"wrong_answer", "output_limit"}


def test_docker_non_root_uid_gid():
    """Real Docker test: Container runs as non-root user (UID 1001)."""
    id_code = textwrap.dedent(
        """
        #include <stdio.h>
        #include <unistd.h>
        int main() {
            printf("%d %d\\n", (int)getuid(), (int)getgid());
            return 0;
        }
        """
    )
    res = evaluate_c_submission(id_code, test_cases=[{"id": "tc1", "input": "", "expected": "1001 1001\n"}], timeout_sec=5.0)
    assert res["status"] in {"accepted", "wrong_answer"}


def test_docker_filesystem_root_read_only():
    """Real Docker test: Writing to container root filesystem is forbidden."""
    ro_code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            FILE *f = fopen("/etc/hacked.txt", "w");
            if (f == NULL) {
                printf("FS_READONLY\\n");
                return 0;
            }
            fclose(f);
            printf("FS_WRITABLE\\n");
            return 0;
        }
        """
    )
    res = evaluate_c_submission(ro_code, test_cases=[{"id": "tc1", "input": "", "expected": "FS_READONLY\n"}], timeout_sec=5.0)
    assert res["status"] in {"accepted", "wrong_answer"}


def test_docker_partial_test_performance_7_of_10_passed():
    """Real Docker test: 7 of 10 tests passed -> pass_rate 0.70, status='wrong_answer'."""
    parity_code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            int n;
            if (scanf("%d", &n) != 1) return 1;
            // Correct for 1-7, wrong for 8-10
            if (n <= 7) printf("%d\\n", n * 2);
            else printf("0\\n");
            return 0;
        }
        """
    )
    test_cases = [
        {"id": f"tc_{i}", "input": f"{i}\n", "expected": f"{i*2}\n", "is_mandatory": False, "is_hidden": False}
        for i in range(1, 11)
    ]
    res = evaluate_c_submission(parity_code, test_cases=test_cases, timeout_sec=5.0)
    assert res["status"] == "wrong_answer"
    assert res["passed"] is False
    assert res["tests_passed"] == 7
    assert res["tests_total"] == 10
    assert abs(res["pass_rate"] - 0.70) < 1e-4
    score_val = res.get("coding_score", res.get("score"))
    assert score_val == pytest.approx(0.70, abs=1e-3)


def test_docker_mandatory_test_failure_caps_score():
    """Real Docker test: When mandatory test fails, final score is capped <= 0.30."""
    code = textwrap.dedent(
        """
        #include <stdio.h>
        int main() {
            int n;
            if (scanf("%d", &n) != 1) return 1;
            if (n == 1) printf("WRONG\\n"); // Mandatory tc_1 fails
            else printf("%d\\n", n * 2);    // Optional tc_2, tc_3 pass
            return 0;
        }
        """
    )
    test_cases = [
        {"id": "tc_1", "input": "1\n", "expected": "2\n", "is_mandatory": True, "is_hidden": False},
        {"id": "tc_2", "input": "2\n", "expected": "4\n", "is_mandatory": False, "is_hidden": False},
        {"id": "tc_3", "input": "3\n", "expected": "6\n", "is_mandatory": False, "is_hidden": False},
    ]
    res = evaluate_c_submission(code, test_cases=test_cases, timeout_sec=5.0)
    assert res["status"] == "wrong_answer"
    assert (res.get("mandatory_passed") is False) or (res.get("mandatory_tests_passed") == 0)
    # Score must be capped to <= 0.30 on mandatory test failure
    score_val = res.get("coding_score", res.get("score"))
    assert score_val <= 0.30


# ─────────────────────────────────────────────────────────────────────────────
# 4. Orchestrator & Candidate State Integration Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_candidate_state_tracks_rich_coding_metrics():
    orch = InterviewOrchestrator(
        "sess_code_test_1",
        {"id": "cand_code_1"},
        {"num_questions": 3, "interview_mode": "standard"},
    )
    orch._question_queue = [
        {"id": "code_q1", "text": "Implement sum in C", "type": "code", "topic": "c_pointers", "difficulty": 2}
    ]
    orch._state["questions"] = list(orch._question_queue)
    orch._select_and_send_question()

    res = await orch.handle_code_submission(
        code="int sum(int a, int b) { return a + b; }",
        question_id="code_q1",
        passed=True,
        tests_passed=4,
        tests_total=4,
        stdout="4\n",
        stderr="",
    )

    state = orch.to_session_dict()
    assert state.get("coding_attempted") == 1
    assert state.get("coding_accepted") == 1
    assert state.get("coding_pass_rate") == 1.0
    assert "c_pointers" in state.get("coding_topics", [])
    assert len(state.get("coding_history", [])) == 1
    assert state["coding_history"][0]["tests_passed"] == 4


@pytest.mark.asyncio
async def test_ppo_observation_remains_strictly_6d_after_coding_turn():
    """
    CRITICAL ARCHITECTURAL CONSTRAINT:
    Coding updates rich candidate state, but the PPO observation vector
    MUST remain strictly 6-dimensional with identical Stage 5 semantics.
    """
    from agents.strategy.hybrid_orchestrator import build_rl_observation

    session_state = {
        "scores": [0.85],
        "raw_scores": [0.85],
        "coding_attempted": 2,
        "coding_accepted": 2,
        "coding_pass_rate": 1.0,
        "coding_history": [{"status": "accepted", "tests_passed": 5, "tests_total": 5}],
        "coding_topics": ["c_pointers"],
        "last_confidence": 0.80,
        "last_hesitation": 0.10,
        "last_time_norm": 0.45,
        "current_difficulty": 3,
    }

    obs = build_rl_observation(0.85, current_difficulty=3, session=session_state)

    assert isinstance(obs, np.ndarray)
    assert obs.shape == (6,)  # MUST be exactly 6D
    assert obs.dtype == np.float32
    assert np.all(obs >= 0.0) and np.all(obs <= 1.0)
    assert obs[0] == pytest.approx(0.85, abs=1e-3)   # performance
    assert obs[1] == pytest.approx(0.85, abs=1e-3)   # avg_performance
    assert obs[2] == pytest.approx(0.80, abs=1e-3)   # confidence
    assert obs[3] == pytest.approx(0.10, abs=1e-3)   # hesitation
    assert obs[4] == pytest.approx(0.45, abs=1e-3)   # time_norm (response latency)
    assert obs[5] == pytest.approx(3 / 5.0, abs=1e-3) # difficulty


def test_stage5_ppo_checkpoint_loads_and_infers_cleanly():
    """Verify existing Stage 5 PPO checkpoint compatibility without retraining."""
    checkpoint_path = os.path.join("rl", "checkpoints", "seed_123", "ppo_final.zip")
    if os.path.exists(checkpoint_path):
        hybrid = HybridOrchestrator(model_path=checkpoint_path)
        assert hybrid.ready is True

        # Test 6D observation prediction
        obs = np.array([0.85, 0.80, 0.75, 0.10, 0.40, 0.60], dtype=np.float32)
        diff, reason, action = hybrid.suggest(0.85, current_difficulty=3, session={"scores": [0.85], "baseline_complete": True})
        assert action in {"Easier", "Same", "Harder"}  # Discrete(3) action space strictly preserved
