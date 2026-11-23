# Performance and Reliability — Final Evaluation Phase

**Primary record:** `testing_output/PrepAIred_Comprehensive_Testing_Report.pdf` Chapter 9, produced earlier in this engagement against the real, live stack, is the authoritative, already-complete performance record (evaluator Flask API, in-process evaluator, full WebSocket turn, Qwen GGUF inference — medians, p95, n, methodology, and the explicit non-comparability caveat against the original Paper-1 hardware). **Not reproduced in full here** to avoid duplicating a single source of truth; this document records only what changed or was added in this phase.

## What this phase adds

### Docker sandbox — re-attempted, still environment-blocked

`docker ps` / `docker version` re-run fresh at the start of this phase: identical connection failure (`failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`) to every prior check in this engagement. **Status remains BLOCKED, honestly, not silently converted to PASS or SKIP.** The 18 Docker-dependent pytest tests and this phase's own regression run (§`03_Test_Execution_Summary.md`) both reflect this.

### Code-change reliability re-confirmation

After the three application changes in `Application_Code_Changes.md`, the live backend, evaluator, and Qwen services were observed to remain healthy and responsive throughout this phase's testing (health checks, admin endpoint calls, the second disposable Qwen test instance) — **zero crashes, zero unhandled exceptions, zero service interruptions** attributable to the changes, across the full session.

### Gymnasium environment checker — new reliability-adjacent evidence

See `06_RL_Evaluation_Results.md` §1.2 — the official `check_env()` tool passing with no warnings is itself a form of interface-reliability evidence (correct `reset()`/`step()` contracts under the checker's own fuzzing of inputs), not previously run in this engagement.

### Admin-dashboard restart reliability — new, direct evidence

`Application_Code_Changes.md`, Change 2: the live backend auto-reloaded (via its own `uvicorn --reload` mechanism, a real process restart, not merely a code hot-swap) partway through this phase. The admin endpoints continued to correctly show historical session data immediately afterward, now sourced from the persisted database rather than being lost — direct, executed evidence of the specific restart-reliability property the prior audit's admin-dashboard finding was about.

## Security/Privacy — category re-confirmed, scope unchanged

`testing_and_evaluation/security_privacy/T-N12_sandbox_security_config_review.md` remains a **static code review**, explicitly not re-labeled as an executed penetration or dynamic security test, consistent with this phase's explicit instruction not to claim penetration testing from source inspection alone. Docker's continued unavailability means no dynamic/attack-execution security testing could be performed this phase either. No destructive or unauthorized test was run.
