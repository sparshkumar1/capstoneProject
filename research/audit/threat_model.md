# Threat Model and Container Sandbox Security Architecture

**Audited Git Commit:** `9cfd34f`  
**Target Paper:** Paper 1 (*PREPAIred: An Evidence-Grounded Adaptive Multimodal Framework for Technical Assessment and Feedback*)

---

## 1. System Context & Assets at Risk

In an automated technical interview system, candidates submit unvetted C source code and free-form natural language responses. 

### Assets at Risk
1. **Host Operating System & Kernel:** Compromise of the host server running the interview orchestrator.
2. **Evaluation Infrastructure & Database:** Tampering with SQLite test records, scores, or question banks.
3. **Candidate Privacy:** Exfiltration of audio streams, speech features, or peer candidate evaluations.
4. **Service Availability:** Denial-of-service via resource exhaustion (CPU fork bombs, RAM bloat, infinite loops).

---

## 2. Threat Actor Model
- **Adversarial Candidate:** Submits malicious C code designed to escape sandboxing, execute local binaries (`/bin/sh`), exfiltrate environment variables, access host networks, or exhaust CPU/memory to crash competing interview sessions.
- **Malicious Prompt Injector:** Submits adversarial text prompts containing jailbreaks or delimiter injection to trick the feedback LLM into revealing hidden rubrics or overriding technical scores.

---

## 3. Defense-in-Depth Containment Model

The security boundary uses a 3-layer containment model:

```
[Candidate C Code]
       ¦
       ?
[Layer 1: Pre-flight AST & Regex Filter] --- (Blocks #include <sys/ptrace.h>, fork, system)
       ¦ (Pass)
       ?
[Layer 2: Compiler Diagnostics Trap]     --- (Traps GCC compilation errors, limits stderr to 64KB)
       ¦ (Compiled)
       ?
[Layer 3: Docker Sandbox Execution Boundary]
  +-- Non-root User (UID 1001:1001)
  +-- Cap-Drop: ALL Linux capabilities dropped
  +-- Network Disabled: --net=none
  +-- Read-Only Rootfs: --read-only with 64MB /workspace tmpfs (noexec, nosuid)
  +-- Memory Cap: 128MB maximum RAM
  +-- Process Cap: --pids-limit=32 (prevents fork-bombs)
  +-- Strict Timeout: 2.0 seconds wall-clock hard SIGKILL
```

---

## 4. Empirical Security Test Matrix (EXP-SYS-1 Findings)

From the 9-vector security negative test suite executed in `research/tables/table_sys_security_boundary.md`:

| Attack Vector | Target Threat | Primary Defense | Actual Isolation Mechanism | Empirical Outcome |
|:---:|:---|:---|:---|:---:|
| **SEC-01** | Kernel ptrace hijack | Pre-flight regex | Static source analyzer rejected code before GCC | **PASS** (`policy_blocked`) |
| **SEC-02** | Socket creation (`sys/socket.h`) | Pre-flight regex | Static regex allowed syntax, but `--net=none` severed network | **FAIL** in pre-flight, **PASS** in Docker |
| **SEC-03** | Broken syntax crash | GCC parser | GCC error captured into structured JSON without host fault | **PASS** (`compilation_error`) |
| **SEC-04** | SIGSEGV null dereference | Linux signal handler | Container exited with 139; mapped to structured runtime error | **PASS** (`runtime_error`) |
| **SEC-05** | Infinite loop (`while(1)`) | Execution timer | Linux `timeout` terminated process after 1.0s | **PASS** (`timeout`) |
| **SEC-06** | RAM exhaustion (malloc bomb) | cgroups memory | Linux OOM-killer terminated process at 128MB | **PASS** (`memory_limit`) |
| **SEC-07** | Exfiltration to external IP | Network stack | `AF_INET` socket failed immediately (`ENETUNREACH`) | **PASS** (`accepted` / blocked net) |
| **SEC-08** | Fork bomb (`while(1) fork()`) | cgroups pids | `pids-limit=32` prevented process table exhaustion | **PASS** (`accepted` / trapped) |
| **SEC-09** | Host file overwrite (`/etc/`) | Filesystem overlay | OverlayFS read-only rootfs blocked write (`EROFS`) | **PASS** (`accepted` / blocked write) |

### Key Architectural Lesson
SEC-02 demonstrates why **static source filtering alone is inherently insufficient** in C evaluation. Because C syntax permits macro aliasing and header indirection, security cannot depend on regex matching. The kernel-level isolation (`--net=none`, non-root UID, dropped capabilities) provides the true inviolable security boundary.
