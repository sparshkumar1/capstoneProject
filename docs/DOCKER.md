# DOCKER.md — Isolated C Coding Execution Sandbox Specification

**Document Version:** 1.0.0 (Stage 7 Specification)
**System:** PrepAIred Automated C Coding Sandbox

---

## 1. Overview & Architectural Role

Candidate C code submitted during technical interviews is **untrusted**. The PrepAIred platform executes all candidate C code inside an isolated Docker sandbox container to prevent host compromise, network tampering, and resource starvation.

```
Candidate C Code
      ↓
Pre-Flight Static Policy Scan (sandbox_policy.py)
      ↓
Ephemeral Docker Container (prepaired-c-sandbox:latest)
      ↓
GCC Compilation inside Container tmpfs (/workspace)
      ↓
Test Harness Execution inside Sandbox
      ↓
Captured stdout / stderr / exit code / execution time
      ↓
Expected Output Comparison & Mandatory Test Verification
      ↓
Authoritative Coding Result (accepted / wrong_answer / compilation_error / timeout / runtime_error / memory_limit)
      ↓
Candidate State (coding_attempted, coding_accepted, coding_pass_rate, coding_history)
      ↓
Existing 6D PPO Projection (No dimensionality expansion)
```

---

## 2. Docker Sandbox Configuration & Security Controls

| Dimension | Configuration | Purpose |
|---|---|---|
| **Base Image** | `alpine:3.19` | Minimal attack surface with GCC, musl-dev, and standard C library. |
| **User Privileges** | `--user 1001:1001` (`sandbox`) | Non-root, unprivileged execution inside the container. |
| **Network Access** | `--net=none` | Complete network severance (no outbound/inbound socket connections). |
| **Capabilities** | `--cap-drop=ALL` | Drops all Linux kernel capabilities (e.g. `CAP_SYS_ADMIN`, `CAP_NET_RAW`). |
| **Privilege Escalation** | `--security-opt=no-new-privileges` | Blocks processes from gaining additional privileges via `setuid`/`setgid`. |
| **CPU Allocation** | `--cpus=1.0` | Restricts container execution to at most 1 CPU core. |
| **Memory Limits** | `--memory=128m --memory-swap=128m` | Caps RAM and swap at 128MB to prevent host memory exhaustion. |
| **Process Limits** | `--pids-limit=32` | Restricts maximum concurrent threads/processes to prevent fork-bombs. |
| **Base Filesystem** | `--read-only` | Container root filesystem (`/`) is mounted strictly read-only. |
| **Workspace Filesystem** | `--tmpfs /workspace:rw,exec,size=32m,uid=1001,gid=1001,mode=1777` | Dedicated in-memory tmpfs mount where compilation and execution are permitted. |
| **Execution Timeout** | `2.0s` – `5.0s` per test case | Kills hung processes and infinite loops automatically. |
| **Output Buffering** | `64 KB` (`65536` bytes) | Truncates stdout/stderr buffers to prevent memory denial on host. |
| **Ephemeral Cleanup** | `--rm` flag & temporary directory lifecycle | Discards container state and host temporary inputs immediately on exit. |

---

## 3. Compilation & Execution Commands

### Compilation Phase:
```bash
gcc -O2 -Wall -Wextra -std=c11 /workspace/solution.c -o /workspace/solution -lm
```
- Exit code `0` $\implies$ Compilation successful; advance to test execution.
- Exit code $\neq 0$ $\implies$ Status `compilation_error`; capture `compiler_output`, skip test execution.

### Test Execution Phase:
```bash
/workspace/solution < /tmp/stdin.txt
```
- Exit code `0` and matching output $\implies$ `passed: True`, `status: "ok"`.
- Exit code `0` and mismatched output $\implies$ `passed: False`, `status: "wrong_answer"`.
- Exit code $\in \{137, 139, 134, 136\}$ $\implies$ `status: "runtime_error"` (SIGSEGV / SIGABRT / SIGFPE) or `"memory_limit"` (SIGKILL/OOM).
- Timeout expired $\implies$ `status: "timeout"`.

---

## 4. Public vs. Hidden Test Cases & Scoring

- **Public Tests:** Inputs, expected outputs, and actual candidate outputs are visible in candidate feedback.
- **Hidden Tests:** Inputs and outputs are masked (`"(hidden test output)"`) to prevent hardcoding.
- **Mandatory Tests:** If a test case is marked `is_mandatory: True` and fails, the submission cannot be `accepted` and `coding_score` is capped at $\le 0.30$.

---

## 5. RL Compatibility & Invariant

- **6D PPO Observation Unchanged:** Coding performance updates the candidate state (`coding_attempted`, `coding_accepted`, `coding_pass_rate`), which is projected into the foundational 6D state:
  $$\mathbf{s} = [s_0(\text{perf}), s_1(\text{avg\_perf}), s_2(\text{conf}), s_3(\text{hes}), s_4(\text{time\_norm}), s_5(\text{diff})]$$
- **Timing Separation:** Candidate thinking/response time is recorded in $s_4$ (`time_norm`); sandbox compilation and execution time are tracked separately in `execution_time_ms` and do not corrupt $s_4$.
- **No RL Retraining:** The existing Stage 5 PPO checkpoint (`rl/checkpoints/seed_123/ppo_final.zip`) remains compatible.

---

## 6. Known Security & Implementation Limitations

1. **Linux Kernel Dependency:** Container isolation leverages Linux cgroups and namespaces via Docker/WSL2; host-kernel zero-day vulnerabilities are not mitigated solely by user-space flags.
2. **Offline Local Fallback:** When Docker daemon is not active on the host machine, the system returns `sandbox_error` rather than executing untrusted C code directly on the host.
