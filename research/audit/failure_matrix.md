# Subsystem Failure Modes, Detection, and Recovery Matrix

**Audited Git Commit:** `9cfd34f`  

| Subsystem | Failure Mode | Detection Mechanism | Automated Fallback / Recovery | Candidate Experience Impact | Test Coverage |
|---|---|---|---|---|---|
| **Audio Pipeline** | Audio file corrupted or unreadable (.wav truncated) | `decode_audio` catches exception; checks `y.size == 0` | Returns default neutral prosody: `jitter=0.02, shimmer=0.05, hnr=0.0, signal_rms=0.0` | Turn proceeds; audio features do not penalize candidate | `test_stt_failure_produces_structured_failure_state` |
| **Evaluator** | FAISS asset or CrossEncoder model missing | Try/except block in `_ensure_evaluator_assets_loaded()` | Returns neutral score `0.50`, empty concept lists, and logs error | Turn evaluated as average; session does not crash | `test_evaluator_failure_produces_structured_failure_without_fabrication` |
| **Docker Sandbox** | Docker daemon unreachable or stopped | `_resolve_docker_prefix()` returns `None` | Returns `status: sandbox_error`; blocks untrusted code from running on host | Displays clean error message; protects host OS | `test_docker_unavailability_produces_structured_sandbox_error` |
| **C Compiler** | Syntax error or undeclared variable in C code | `gcc` exit code $\neq 0$ | Captures stderr up to 64KB; sets `coding_score = 0.0, status: compilation_error` | Returns exact gcc compiler diagnostics to candidate | `test_docker_detects_c_compilation_error` |
| **C Execution** | Infinite loop (`while(1)`) | Linux `timeout 2.0s` exits with code 124 | Returns `status: timeout, passed: false` | Halts execution after 2s; returns timeout verdict | `test_docker_terminates_infinite_loop_timeout` |
| **C Execution** | Segmentation fault (SIGSEGV) | Exit code 139 trapped from container | Returns `status: segmentation_fault, passed: false` | Candidate informed of memory access fault | `test_docker_runtime_error_segfault` |
| **RL Controller** | SB3 checkpoint `ppo_final.zip` missing or corrupt | `_try_load()` catches exception; sets `self.model = None` | Falls back to deterministic rule jump table: `score > 0.80 -> Harder, score < 0.40 -> Easier` | Adaptive pacing continues seamlessly | `test_rl_unavailability_produces_non_rl_heuristic_recovery` |
| **Qwen LLM** | Qwen microservice offline or times out (>6.0s) | HTTP connection timeout caught in orchestrator | Degrades to `_synthesize_structured_feedback` (deterministic template) | Candidate receives complete structured feedback instantly | `test_qwen_failure_preserves_evaluator_evidence` |
| **Qwen Output** | Qwen generates generic fluff or empty text | `_validate_feedback_output()` rejects string | Triggers deterministic structured fallback synthesizer | Candidate never sees unhelpful boilerplate | `test_validate_feedback_output_rejects_empty_and_boilerplate` |
| **SQLite DB** | Concurrent write collision | SQLite connection timeout (30.0s) + `threading.Lock()` | Write transaction queues safely without `SQLITE_BUSY` error | Zero data loss; transparent to user | `test_lock_serialises_concurrent` |
