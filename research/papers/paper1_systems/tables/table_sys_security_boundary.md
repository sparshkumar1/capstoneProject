# Docker Sandbox Security Boundary Negative Tests (EXP-SYS-1)

Authoritative negative security testing of container isolation parameters:

| Test ID | Security Boundary | Objective | Expected Enforcement | Actual Outcome | Verdict |
| :---: | :--- | :--- | :--- | :--- | :---: |
| SEC-01 | **Pre-flight Static Dangerous Pattern Filter** | Block prohibited direct kernel ptrace invocation before compilation | `policy_blocked` | `policy_blocked` | **PASS** |
| SEC-02 | **Pre-flight Dangerous Socket Header Filter** | Block restricted sys/socket.h network header inclusion in source | `policy_blocked` | `accepted` | **FAIL** |
| SEC-03 | **Compiler Error Trapping** | GCC compilation error is cleanly trapped without crashing host | `compilation_error` | `compilation_error` | **PASS** |
| SEC-04 | **Runtime Memory Corruption (SIGSEGV)** | Null-pointer dereference is captured as runtime_error (exit 139) | `runtime_error` | `runtime_error` | **PASS** |
| SEC-05 | **Execution Wall-Clock Timeout Enforcement** | Infinite loop is terminated within strict timeout limit (1.0s) | `timeout` | `timeout` | **PASS** |
| SEC-06 | **Memory Limit Enforcement (OOM Kill)** | Exceeding 128MB memory ceiling triggers OOM termination | `memory_limit/runtime_error/wrong_answer` | `memory_limit` | **PASS** |
| SEC-07 | **Network Isolation (--net=none)** | Outbound socket connection fails due to disabled networking | `accepted` | `accepted` | **PASS** |
| SEC-08 | **Process Limit / Fork-Bomb Resistance** | Attempted fork bomb is capped by --pids-limit=32 | `accepted/runtime_error/wrong_answer` | `accepted` | **PASS** |
| SEC-09 | **Root Filesystem Write Protection (--read-only)** | Attempt to write outside /workspace fails due to read-only rootfs | `accepted` | `accepted` | **PASS** |
