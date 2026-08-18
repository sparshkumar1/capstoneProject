# PrepAIred — Real Isolated C Coding Sandbox Specification

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Sandbox Security & Architecture

Evaluating candidate C code in an automated interview setting poses substantial security risks (arbitrary system calls, fork bombs, disk wiping, network exfiltration, infinite loops). PrepAIred implements an **isolated Docker-based execution sandbox** managed by `DockerCSandbox` ([`agents/coding_executor/coding_executor.py`](agents/coding_executor/coding_executor.py)).

```
Candidate C Source Code
  │
  ├──► 1. Pre-Execution Policy Static Analysis (sandbox_policy.py)
  │      └─ Banned dangerous headers: <windows.h>, <sys/socket.h>, <netinet/in.h>
  │
  ├──► 2. Isolated Container Invocation (prepaired-c-sandbox:latest)
  │      ├─ Unprivileged runner (UID:GID 1001:1001)
  │      ├─ Dropped capabilities (--cap-drop=ALL)
  │      ├─ Disabled privileges (--security-opt=no-new-privileges)
  │      ├─ Network disabled (--net=none)
  │      ├─ Read-only container root
  │      └─ Dedicated executable tmpfs (/workspace:rw,exec,size=32m)
  │
  ├──► 3. Compilation with Strict GCC 13+ Flags
  │      └─ gcc -O2 -Wall -Wextra -Werror=return-type candidate.c test_harness.c -o solution
  │
  └──► 4. Sandboxed Execution Against Test Cases
         ├─ Memory Limit: 128 MB RAM (--memory=128m --memory-swap=128m)
         ├─ Process Limit: 32 PIDs (--pids-limit=32)
         ├─ CPU Limit: 1.0 core (--cpus=1.0)
         ├─ Execution Timeout: 2.0 seconds (hard process kill at 4.0s)
         └─ Output Truncation: 64 KB (65,536 bytes)
```

---

## 2. Hard Governance & Resource Limits

| Resource Limit | Value | Enforcement Mechanism | Failure Classification |
|---|---|---|---|
| **Memory Limit** | `128 MB` | Docker cgroups (`--memory=128m --memory-swap=128m`) | `memory_limit_exceeded` / `OOMKilled` |
| **Execution Timeout** | `2.0 s` | Subprocess timeout timer | `timeout` / `SIGKILL` |
| **Process / Thread Limit**| `32 PIDs` | Docker cgroups (`--pids-limit=32`) | `runtime_error` (Resource Fork Denied) |
| **CPU Limit** | `1.0 core` | Docker cgroups (`--cpus=1.0`) | Throttled compute |
| **Output Truncation** | `64 KB` | Stream byte buffer truncation | `output_truncated` |
| **Filesystem Root** | Read-Only | Docker engine (`--read-only`) | Write Denied (`EROFS`) |
| **Network Interface** | Disabled | Docker engine (`--net=none`) | Socket Denied (`EACCES`) |
| **User Privileges** | `1001:1001` | Non-root `sandbox` user | Root Access Denied (`EPERM`) |

---

## 3. Test Harness Execution & Pass Rate Scoring

A coding problem provides $N$ test cases (including boundary edge cases and performance tests).

- **Execution Flow:** The test harness compiles the candidate function against a test runner that executes each case sequentially and captures outputs.
- **Pass Rate Calculation:**
  $$\text{Pass Rate} = \frac{\text{Passed Test Cases}}{\text{Total Test Cases}} \in [0.0, 1.0]$$
- **Mandatory Test Case Policy:** If a question rubric designates specific test cases as mandatory (e.g. empty array handling), failing any mandatory case caps the score at $0.60$.
- **Latency Separation:** Total test execution time in milliseconds (`execution_time_ms`) is recorded for debugging and performance profiling, but is **never** injected into the 6D RL state vector.

---

## 4. Execution Status Classification

| Status | Trigger Condition | Technical Score Impact |
|---|---|---|
| `accepted` | All test cases pass ($N/N$) | $\text{Pass Rate} = 1.00$ |
| `wrong_answer` | Code compiles and runs, but $K < N$ test cases pass | $\text{Pass Rate} = K / N$ |
| `compilation_error` | GCC compiler exits with non-zero returncode | $\text{Pass Rate} = 0.00$, compiler log returned |
| `runtime_error` | Segmentation fault (`SIGSEGV`) or bus error | $\text{Pass Rate} = 0.00$, crash signal returned |
| `timeout` | Execution exceeds 2.0s without termination | $\text{Pass Rate} = 0.00$, timeout flag returned |
| `memory_limit_exceeded` | Process killed by OOM cgroup limit | $\text{Pass Rate} = 0.00$, OOM flag returned |
| `policy_blocked` | Source contains prohibited system headers | $\text{Pass Rate} = 0.00$, policy violation returned |

---

## 5. Empirical Claims Status

| Coding Sandbox Claim | Status | Repository Evidence |
|---|---|---|
| Docker C container sandbox execution | **`TESTED`** | Implemented in `agents/coding_executor/`; verified via 20 unit tests in `test_coding_executor.py` |
| GCC compilation error & segfault capture | **`TESTED`** | `test_coding_executor.py` |
| Resource limit enforcement (128MB RAM, 32 PIDs, 2s) | **`TESTED`** | `test_coding_executor.py` |
| Security isolation (net=none, cap-drop=ALL, non-root) | **`TESTED`** | `test_coding_executor.py` |
