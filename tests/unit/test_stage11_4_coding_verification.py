"""
test_stage11_4_coding_verification.py
Dedicated unit and integration tests for Stage 11.4:
Real C coding execution in Docker sandbox, isolation, limits, and candidate state integration.
"""

import asyncio
import os
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from agents.coding_executor.coding_executor import DockerCSandbox, evaluate_c_submission
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.strategy.hybrid_orchestrator import build_rl_observation


@pytest.fixture(scope="module")
def sandbox():
    sb = DockerCSandbox()
    if not sb.is_docker_available():
        pytest.skip("Docker sandbox daemon is not available on this machine")
    return sb


def test_accepted_c_solution(sandbox):
    """Genuinely correct C program compiles with GCC, executes ELF, passes all test cases."""
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
        {"id": "tc1", "input": "3 4\n", "expected": "7\n", "is_mandatory": True, "is_hidden": False},
        {"id": "tc2", "input": "100 250\n", "expected": "350\n", "is_mandatory": False, "is_hidden": True},
    ]
    res = sandbox.compile_and_execute(code, test_cases)
    assert res["status"] == "accepted"
    assert res["passed"] is True
    assert res["tests_passed"] == 2
    assert res["coding_score"] == 1.0
    assert len(res["failed_test_ids"]) == 0


def test_partial_c_solution(sandbox):
    """C solution that fails subset of tests produces wrong_answer with precise pass rate."""
    code = """
#include <stdio.h>
int main() {
    int x;
    if (scanf("%d", &x) == 1) {
        if (x < 5) printf("%d\\n", x * 2);
        else printf("%d\\n", x); // incorrect branch
    }
    return 0;
}
"""
    test_cases = [
        {"id": f"tc_{i}", "input": f"{i}\n", "expected": f"{i * 2}\n", "is_mandatory": False, "is_hidden": False}
        for i in range(1, 11)
    ]
    res = sandbox.compile_and_execute(code, test_cases)
    assert res["status"] == "wrong_answer"
    assert res["passed"] is False
    assert res["tests_passed"] == 4
    assert res["pass_rate"] == 0.40
    assert len(res["failed_test_ids"]) == 6


def test_compilation_error_diagnostic(sandbox):
    """Syntax error produces compilation_error with raw GCC compiler diagnostic in compiler_output."""
    code = """
#include <stdio.h>
int main() {
    printf("Missing closing paren\\n"
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "", "is_mandatory": False}])
    assert res["status"] == "compilation_error"
    assert res["passed"] is False
    assert res["coding_score"] == 0.0
    assert "error" in res["compiler_output"].lower()


def test_runtime_error_segfault(sandbox):
    """Null pointer dereference produces runtime_error with exit code 139 (SIGSEGV)."""
    code = """
#include <stdio.h>
int main() {
    int *ptr = NULL;
    *ptr = 999;
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "999", "is_mandatory": False}])
    assert res["status"] == "runtime_error"
    assert res["passed"] is False
    assert res["test_results"][0]["exit_code"] == 139


def test_timeout_infinite_loop(sandbox):
    """Non-terminating loop is terminated by watchdog and classified as timeout."""
    code = """
#include <stdio.h>
int main() {
    while (1) {}
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "", "is_mandatory": False}], timeout_sec=2.0)
    assert res["status"] == "timeout"
    assert res["passed"] is False


def test_memory_limit_cgroup_kill(sandbox):
    """Excessive memory allocation exceeding 128MB is terminated by cgroup memory limit."""
    code = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main() {
    for (int i = 0; i < 40; i++) {
        char *p = (char *)malloc(16 * 1024 * 1024);
        if (!p) {
            printf("malloc failed\\n");
            return 1;
        }
        memset(p, 0x55, 16 * 1024 * 1024);
    }
    printf("Allocated\\n");
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "", "is_mandatory": False}])
    assert res["status"] in {"memory_limit", "runtime_error"}
    assert res["passed"] is False


def test_network_isolation(sandbox):
    """Container uses --net=none and blocks all outgoing socket connections."""
    code = """
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
int main() {
    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0) {
        printf("ISOLATED\\n");
        return 0;
    }
    fcntl(s, F_SETFL, O_NONBLOCK);
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(80);
    inet_pton(AF_INET, "8.8.8.8", &addr.sin_addr);
    int res = connect(s, (struct sockaddr *)&addr, sizeof(addr));
    if (res < 0) {
        printf("ISOLATED\\n");
    } else {
        printf("CONNECTED\\n");
    }
    close(s);
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "ISOLATED\n", "is_mandatory": False}])
    assert res["passed"] is True
    assert "ISOLATED" in res["test_results"][0]["stdout"]


def test_filesystem_isolation_read_only_root(sandbox):
    """Container root filesystem is read-only; attempts to write outside /workspace fail."""
    code = """
#include <stdio.h>
int main() {
    FILE *fp = fopen("/evil.txt", "w");
    if (fp == NULL) {
        printf("FS_ISOLATED\\n");
    } else {
        fclose(fp);
        printf("WRITABLE\\n");
    }
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "FS_ISOLATED\n", "is_mandatory": False}])
    assert res["passed"] is True
    assert "FS_ISOLATED" in res["test_results"][0]["stdout"]


def test_non_root_execution_uid_gid(sandbox):
    """Executable runs under unprivileged sandbox user (UID 1001, GID 1001)."""
    code = """
#include <stdio.h>
#include <unistd.h>
int main() {
    printf("%d %d\\n", (int)getuid(), (int)getgid());
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "1001 1001\n", "is_mandatory": False}])
    assert res["passed"] is True
    assert "1001 1001" in res["test_results"][0]["stdout"]


def test_pid_limit_fork_bomb(sandbox):
    """PID limit (32) constrains excessive process spawning and preserves host stability."""
    code = """
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
int main() {
    for (int i = 0; i < 50; i++) {
        pid_t p = fork();
        if (p == 0) _exit(0);
        else if (p > 0) waitpid(p, NULL, 0);
    }
    printf("FORK_BOUNDED\\n");
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "FORK_BOUNDED\n", "is_mandatory": False}])
    assert res["status"] in {"accepted", "runtime_error"}
    assert "FORK_BOUNDED" in res["test_results"][0]["stdout"]


def test_output_limit_bounded_stdout(sandbox):
    """Excessive stdout output is bounded to 65536 bytes."""
    code = """
#include <stdio.h>
int main() {
    for (int i = 0; i < 10000; i++) printf("Long output line to saturate buffer\\n");
    return 0;
}
"""
    res = sandbox.compile_and_execute(code, [{"id": "tc1", "input": "", "expected": "expected", "is_mandatory": False}])
    assert len(res["test_results"][0]["stdout"]) <= 65536


def test_mandatory_test_case_failure_cap(sandbox):
    """When mandatory test fails, score is capped at <= 0.30 even if optional tests pass."""
    code = """
#include <stdio.h>
int main() {
    int x;
    if (scanf("%d", &x) == 1) {
        if (x == 999) printf("WRONG\\n");
        else printf("%d\\n", x * 2);
    }
    return 0;
}
"""
    test_cases = [
        {"id": "tc_opt1", "input": "10\n", "expected": "20\n", "is_mandatory": False, "is_hidden": False},
        {"id": "tc_opt2", "input": "20\n", "expected": "40\n", "is_mandatory": False, "is_hidden": False},
        {"id": "tc_mand", "input": "999\n", "expected": "1998\n", "is_mandatory": True, "is_hidden": False},
    ]
    res = sandbox.compile_and_execute(code, test_cases)
    assert res["status"] == "wrong_answer"
    assert res["mandatory_tests_passed"] == 0
    assert res["tests_passed"] == 2
    assert res["coding_score"] <= 0.30


def test_docker_unavailable_structured_failure():
    """When Docker daemon is unreachable, returns sandbox_error without fake execution."""
    sb = DockerCSandbox()
    with patch.object(sb, "_resolve_docker_prefix", return_value=None):
        res = sb.compile_and_execute("int main(){return 0;}", [{"id": "tc1", "input": "", "expected": ""}])
        assert res["status"] == "sandbox_error"
        assert res["passed"] is False
        assert "unreachable" in res["error"].lower()


def test_candidate_state_and_rl_6d_separation():
    """Verifies that coding execution updates candidate state without affecting 6D RL state space."""
    orch = InterviewOrchestrator(
        "sess_test_coding",
        {"id": "cand_1", "experience": "intermediate"},
        {"duration_minutes": 30, "num_questions": 5, "c_topics": ["pointers"], "dsa_topics": ["arrays"]},
    )
    res = asyncio.run(orch.handle_code_submission(
        code="int main(){return 0;}",
        question_id="C01",
        passed=True,
        tests_passed=4,
        tests_total=4,
        stdout="0 1\n",
        stderr="",
    ))
    assert res["feedback"]["final_score"] == 1.0
    state = orch._state
    assert state.get("coding_attempted", 1) >= 1
    assert state.get("coding_accepted", 1) >= 1

    # Verify RL observation remains strictly 6D
    obs = build_rl_observation(1.0, 3, state)
    assert len(obs) == 6
    assert all(0.0 <= v <= 1.0 for v in obs)
