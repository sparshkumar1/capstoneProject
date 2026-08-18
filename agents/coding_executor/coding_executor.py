"""
coding_executor.py — Real Isolated C Compilation and Execution Sandbox.

Authoritative C Sandbox implementation using Docker isolation:
- Unprivileged user execution (UID/GID 1001:1001)
- Network disabled (--net=none)
- Dropped Linux capabilities (--cap-drop=ALL)
- No new privileges (--security-opt=no-new-privileges)
- Strict CPU & Memory limits (128MB RAM, 32 PIDs)
- Read-only container root with dedicated writable executable tmpfs (/workspace)
- Grounded execution diagnostics (Compilation error, Segfault, Timeout, Memory limit, WA)
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .sandbox_policy import validate_source_safety


SANDBOX_IMAGE = os.getenv("SANDBOX_DOCKER_IMAGE", "prepaired-c-sandbox:latest")
DEFAULT_TIMEOUT_SEC = 2.0
DEFAULT_MEMORY_MB = 128
DEFAULT_PIDS_LIMIT = 32
DEFAULT_CPUS = 1.0
MAX_OUTPUT_BYTES = 65536


class DockerCSandbox:
    """
    Manages isolated C compilation and test harness execution within Docker.
    Supports both native Docker daemon and WSL Linux Docker daemon seamlessly.
    """

    def __init__(
        self,
        image_name: str = SANDBOX_IMAGE,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        memory_mb: int = DEFAULT_MEMORY_MB,
        pids_limit: int = DEFAULT_PIDS_LIMIT,
        cpus: float = DEFAULT_CPUS,
    ):
        self.image_name = image_name
        self.timeout_sec = timeout_sec
        self.memory_mb = memory_mb
        self.pids_limit = pids_limit
        self.cpus = cpus
        self._cmd_prefix: Optional[List[str]] = None

    def _resolve_docker_prefix(self) -> Optional[List[str]]:
        """Determine whether direct docker or WSL docker is active."""
        if self._cmd_prefix is not None:
            return self._cmd_prefix

        # 1. Try native docker CLI
        docker_cli = shutil.which("docker")
        if docker_cli:
            try:
                res = subprocess.run(
                    [docker_cli, "info"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5.0,
                )
                if res.returncode == 0:
                    self._cmd_prefix = [docker_cli]
                    return self._cmd_prefix
            except Exception:
                pass

        # 2. Try WSL2 Linux docker daemon
        wsl_cli = shutil.which("wsl")
        if wsl_cli:
            try:
                res = subprocess.run(
                    [wsl_cli, "-d", "Ubuntu-22.04", "-u", "root", "--exec", "docker", "info"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=15.0,
                )
                if res.returncode == 0:
                    self._cmd_prefix = [wsl_cli, "-d", "Ubuntu-22.04", "-u", "root", "--exec", "docker"]
                    return self._cmd_prefix
            except Exception:
                pass


        return None

    def is_docker_available(self) -> bool:
        """Check if a functional Docker daemon is reachable."""
        return self._resolve_docker_prefix() is not None

    def _to_mount_path(self, host_path: Path) -> str:
        """Convert host directory path to container/WSL-compatible path."""
        prefix = self._resolve_docker_prefix()
        posix_str = host_path.as_posix()
        if prefix and "wsl" in prefix[0].lower():
            # Translate Windows C:/... to /mnt/c/...
            if len(posix_str) >= 2 and posix_str[1] == ":":
                drive = posix_str[0].lower()
                return f"/mnt/{drive}{posix_str[2:]}"
        return posix_str

    def compile_and_execute(
        self,
        code: str,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        timeout_sec: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute candidate C code inside an isolated Docker sandbox container.
        """
        timeout = timeout_sec or self.timeout_sec
        test_cases = test_cases or []

        # 1. Pre-flight static policy check (Defense-in-depth)
        safe, reasons = validate_source_safety(code)
        if not safe:
            return {
                "status": "policy_blocked",
                "passed": False,
                "coding_score": 0.0,
                "tests_total": len(test_cases),
                "tests_passed": 0,
                "public_tests_passed": 0,
                "public_tests_total": sum(1 for c in test_cases if not c.get("is_hidden")),
                "hidden_tests_passed": 0,
                "hidden_tests_total": sum(1 for c in test_cases if c.get("is_hidden")),
                "mandatory_tests_passed": 0,
                "mandatory_tests_total": sum(1 for c in test_cases if c.get("is_mandatory")),
                "pass_rate": 0.0,
                "failed_test_ids": [c.get("id", f"tc_{i}") for i, c in enumerate(test_cases, 1)],
                "test_results": [],
                "compiler_output": "",
                "policy_reasons": reasons,
                "error": f"Pre-flight safety check failed: {', '.join(reasons)}",
            }

        # 2. Check Docker availability
        docker_prefix = self._resolve_docker_prefix()
        if not docker_prefix:
            return {
                "status": "sandbox_error",
                "passed": False,
                "coding_score": 0.0,
                "tests_total": len(test_cases),
                "tests_passed": 0,
                "public_tests_passed": 0,
                "public_tests_total": sum(1 for c in test_cases if not c.get("is_hidden")),
                "hidden_tests_passed": 0,
                "hidden_tests_total": sum(1 for c in test_cases if c.get("is_hidden")),
                "mandatory_tests_passed": 0,
                "mandatory_tests_total": sum(1 for c in test_cases if c.get("is_mandatory")),
                "pass_rate": 0.0,
                "failed_test_ids": [c.get("id", f"tc_{i}") for i, c in enumerate(test_cases, 1)],
                "test_results": [],
                "compiler_output": "",
                "policy_reasons": ["Docker sandbox daemon unavailable"],
                "error": "Docker sandbox daemon is unreachable. Untrusted code execution blocked to protect host.",
            }

        # 3. Create temporary workspace on host to mount read-only into container
        with tempfile.TemporaryDirectory(prefix="c_sandbox_") as tmpdir:
            tmppath = Path(tmpdir)
            source_file = tmppath / "solution.c"
            source_file.write_text(code, encoding="utf-8")

            # Write test cases to input directory
            tests_payload = []
            for idx, tc in enumerate(test_cases, 1):
                tc_id = str(tc.get("id", f"tc_{idx}"))
                stdin_text = str(tc.get("input", tc.get("stdin", "")))
                expected_out = str(tc.get("expected", tc.get("stdout", "")))
                is_hidden = bool(tc.get("is_hidden", False))
                is_mandatory = bool(tc.get("is_mandatory", False))
                tests_payload.append({
                    "id": tc_id,
                    "input": stdin_text,
                    "expected": expected_out,
                    "is_hidden": is_hidden,
                    "is_mandatory": is_mandatory,
                })

            mount_src = self._to_mount_path(tmppath)

            # 4. Phase 1: Compile inside isolated Docker container
            compile_cmd = docker_prefix + [
                "run", "--rm",
                "--user", "1001:1001",
                "--net=none",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                f"--cpus={self.cpus}",
                f"--memory={self.memory_mb}m",
                f"--memory-swap={self.memory_mb}m",
                f"--pids-limit={self.pids_limit}",
                "--read-only",
                "--tmpfs", "/workspace:rw,exec,size=32m,uid=1001,gid=1001,mode=1777",
                "-v", f"{mount_src}:/input:ro",
                self.image_name,
                "/bin/bash", "-c",
                "cp /input/solution.c /workspace/solution.c && gcc -O2 -Wall -Wextra -std=c11 /workspace/solution.c -o /workspace/solution -lm",
            ]

            comp_start = time.monotonic()
            try:
                comp_res = subprocess.run(
                    compile_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10.0,
                    text=True,
                )
                comp_duration_ms = round((time.monotonic() - comp_start) * 1000, 2)
            except subprocess.TimeoutExpired:
                return {
                    "status": "compilation_error",
                    "passed": False,
                    "coding_score": 0.0,
                    "tests_total": len(test_cases),
                    "tests_passed": 0,
                    "pass_rate": 0.0,
                    "failed_test_ids": [c.get("id", f"tc_{i}") for i, c in enumerate(test_cases, 1)],
                    "test_results": [],
                    "compiler_output": "Compilation timed out (>10.0s)",
                    "error": "Compilation exceeded time limit",
                    "compilation_time_ms": 10000.0,
                }
            except Exception as e:
                return {
                    "status": "sandbox_error",
                    "passed": False,
                    "coding_score": 0.0,
                    "tests_total": len(test_cases),
                    "tests_passed": 0,
                    "pass_rate": 0.0,
                    "failed_test_ids": [c.get("id", f"tc_{i}") for i, c in enumerate(test_cases, 1)],
                    "test_results": [],
                    "compiler_output": "",
                    "error": f"Docker compilation runner failed: {str(e)}",
                }

            if comp_res.returncode != 0:
                comp_err = comp_res.stderr.strip() or comp_res.stdout.strip()
                return {
                    "status": "compilation_error",
                    "passed": False,
                    "coding_score": 0.0,
                    "tests_total": len(test_cases),
                    "tests_passed": 0,
                    "public_tests_passed": 0,
                    "public_tests_total": sum(1 for c in test_cases if not c.get("is_hidden")),
                    "hidden_tests_passed": 0,
                    "hidden_tests_total": sum(1 for c in test_cases if c.get("is_hidden")),
                    "mandatory_tests_passed": 0,
                    "mandatory_tests_total": sum(1 for c in test_cases if c.get("is_mandatory")),
                    "pass_rate": 0.0,
                    "failed_test_ids": [c.get("id", f"tc_{i}") for i, c in enumerate(test_cases, 1)],
                    "test_results": [],
                    "compiler_output": comp_err[:MAX_OUTPUT_BYTES],
                    "compilation_time_ms": comp_duration_ms,
                    "error": f"Compilation failed (exit code {comp_res.returncode})",
                }

            # 5. Phase 2: Execute each test case inside fresh Docker containers
            test_results = []
            passed_count = 0
            public_passed = 0
            public_total = 0
            hidden_passed = 0
            hidden_total = 0
            mandatory_passed = 0
            mandatory_total = 0
            failed_ids = []
            overall_status = "accepted"
            total_exec_time_ms = 0.0

            for idx, tc in enumerate(tests_payload, 1):
                tc_id = tc["id"]
                stdin_input = tc["input"]
                expected_out = tc["expected"]
                is_hidden = tc["is_hidden"]
                is_mandatory = tc["is_mandatory"]

                if is_hidden:
                    hidden_total += 1
                else:
                    public_total += 1

                if is_mandatory:
                    mandatory_total += 1

                # Execute inside isolated container with stdin piped
                run_test_cmd = docker_prefix + [
                    "run", "--rm", "-i",
                    "--user", "1001:1001",
                    "--net=none",
                    "--cap-drop=ALL",
                    "--security-opt=no-new-privileges",
                    f"--cpus={self.cpus}",
                    f"--memory={self.memory_mb}m",
                    f"--memory-swap={self.memory_mb}m",
                    f"--pids-limit={self.pids_limit}",
                    "--read-only",
                    "--tmpfs", "/workspace:rw,exec,size=32m,uid=1001,gid=1001,mode=1777",
                    "-v", f"{mount_src}:/input:ro",
                    self.image_name,
                    "/bin/bash", "-c",
                    f"cp /input/solution.c /workspace/solution.c && gcc -O2 -Wall -std=c11 /workspace/solution.c -o /workspace/solution -lm && timeout {float(timeout):.1f}s /workspace/solution",
                ]

                t_start = time.monotonic()
                try:
                    proc = subprocess.run(
                        run_test_cmd,
                        input=stdin_input,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=float(timeout) + 5.0,
                        text=True,
                    )
                    t_dur_ms = round((time.monotonic() - t_start) * 1000, 2)
                    total_exec_time_ms += t_dur_ms

                    actual_stdout = proc.stdout[:MAX_OUTPUT_BYTES]
                    actual_stderr = proc.stderr[:MAX_OUTPUT_BYTES]
                    retcode = proc.returncode

                    if retcode == 0:
                        # Output comparison
                        is_pass = actual_stdout.strip() == expected_out.strip()
                        case_status = "ok" if is_pass else "wrong_answer"
                    else:
                        is_pass = False
                        # Precise classification:
                        # 124 = Timeout from Linux timeout utility
                        # 137 = SIGKILL (OOM / memory limit or external kill)
                        # 139 = SIGSEGV (Segmentation Fault)
                        # 134 = SIGABRT (Assertion/Abort)
                        # 136 = SIGFPE (Division by Zero)
                        if retcode == 124:
                            case_status = "timeout"
                        elif retcode == 137 or "out of memory" in actual_stderr.lower() or "oom" in actual_stderr.lower() or "malloc failed" in actual_stdout.lower():
                            case_status = "memory_limit"
                        elif retcode in {134, 136, 139}:
                            case_status = "runtime_error"
                        else:
                            case_status = "runtime_error"

                except subprocess.TimeoutExpired:
                    t_dur_ms = round(float(timeout) * 1000, 2)
                    total_exec_time_ms += t_dur_ms
                    actual_stdout = ""
                    actual_stderr = f"Execution timed out after {timeout}s"
                    retcode = -1
                    is_pass = False
                    case_status = "timeout"
                except Exception as e:
                    t_dur_ms = 0.0
                    actual_stdout = ""
                    actual_stderr = str(e)
                    retcode = -1
                    is_pass = False
                    case_status = "sandbox_error"

                # Record test case result
                if is_pass:
                    passed_count += 1
                    if is_hidden:
                        hidden_passed += 1
                    else:
                        public_passed += 1
                    if is_mandatory:
                        mandatory_passed += 1
                else:
                    failed_ids.append(tc_id)
                    if overall_status == "accepted":
                        overall_status = case_status

                # Prepare test result item (obfuscating expected for hidden tests)
                result_entry = {
                    "test_id": tc_id,
                    "passed": is_pass,
                    "status": case_status,
                    "is_hidden": is_hidden,
                    "is_mandatory": is_mandatory,
                    "exit_code": retcode,
                    "execution_time_ms": t_dur_ms,
                    "stdout": actual_stdout if not is_hidden else "(hidden test output)",
                    "stderr": actual_stderr if not is_hidden else "(hidden test error)",
                    "expected": expected_out if not is_hidden else "(hidden test expected)",
                }
                test_results.append(result_entry)

            total_tests = len(tests_payload)
            pass_rate = round(passed_count / max(total_tests, 1), 4)

            # Compute score with mandatory test penalty
            if mandatory_total > 0 and mandatory_passed < mandatory_total:
                # Mandatory test failed — score is capped at 0.30
                coding_score = round(min(0.30, 0.30 * pass_rate), 4)
                if overall_status == "accepted":
                    overall_status = "wrong_answer"
            else:
                coding_score = pass_rate

            is_accepted = (passed_count == total_tests) and (mandatory_passed == mandatory_total)
            if not is_accepted and overall_status == "accepted":
                overall_status = "wrong_answer"

            return {
                "status": overall_status if not is_accepted else "accepted",
                "passed": is_accepted,
                "coding_score": coding_score,
                "tests_total": total_tests,
                "tests_passed": passed_count,
                "public_tests_passed": public_passed,
                "public_tests_total": public_total,
                "hidden_tests_passed": hidden_passed,
                "hidden_tests_total": hidden_total,
                "mandatory_tests_passed": mandatory_passed,
                "mandatory_tests_total": mandatory_total,
                "pass_rate": pass_rate,
                "failed_test_ids": failed_ids,
                "test_results": test_results,
                "compiler_output": comp_res.stderr.strip()[:MAX_OUTPUT_BYTES],
                "execution_time_ms": round(total_exec_time_ms, 2),
                "policy_reasons": [],
            }


def evaluate_c_submission(
    code: str,
    test_cases: Optional[List[Dict[str, Any]]] = None,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    memory_mb: int = DEFAULT_MEMORY_MB,
) -> Dict[str, Any]:
    """
    Authoritative evaluation entry point for C coding submissions.
    """
    sandbox = DockerCSandbox(timeout_sec=timeout_sec, memory_mb=memory_mb)
    return sandbox.compile_and_execute(code, test_cases=test_cases, timeout_sec=timeout_sec)


def evaluate_code_submission(
    code: str,
    test_cases: Optional[List[Dict[str, Any]]] = None,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
) -> Dict[str, Any]:
    """
    Drop-in compatibility wrapper for evaluating code submissions.
    Routes untrusted code to the authoritative Docker C Sandbox.
    """
    return evaluate_c_submission(code, test_cases=test_cases, timeout_sec=timeout_sec)
