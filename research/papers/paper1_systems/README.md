# Paper 1: Systems Architecture, Sandboxing & Fault Tolerance

- **Working Title:** *PREPAIred: An Evidence-Grounded Adaptive Multimodal Framework for Technical Interview Assessment and Feedback*
- **Target Venues:** **ATIS 2026** (Bengaluru, Nov 7 Deadline) / **IEEE Access**
- **Domain:** Systems Architecture, Security Sandboxing, Software Engineering for AI

---

## 1. Abstract
Automated technical interview systems often suffer from brittle monolithic architectures, hallucinated grading from large language models (LLMs), and security vulnerabilities during untrusted code execution. We present PREPAIred, an asynchronous hub-and-spoke assessment framework that completely decouples technical grading from free-form LLM generation and isolates untrusted candidate C code inside an ephemeral, non-root Linux container sandbox. By combining sub-millisecond scoring dispatch, Socratic follow-up state machines, and persistent multi-attempt tracking via SQLite WAL, PREPAIred delivers resilient, candidate-centered evaluations. Comprehensive security negative testing demonstrates robust defense against kernel ptrace tampering, fork bombs, memory exhaustion, and network exfiltration. Subsystem latency profiling confirms sub-millisecond policy inference and median evaluation turn latencies of 167 ms for conceptual queries. Single-component removal experiments establish 100% operational resilience under simulated subsystem outages.

---

## 2. Core Contributions
1. **Asynchronous Hub-and-Spoke Multimodal Architecture:** Decouples technical scoring, acoustic feature extraction, and feedback generation to prevent cascading system failures.
2. **Defense-in-Depth C Execution Sandbox:** Enforces strict kernel containment (`--cap-drop=ALL`, `--net=none`, non-root UID 1001, tmpfs `/workspace`, 128MB RAM, 32 PIDs) with automated recovery for compiler faults, memory corruption, and timeouts.
3. **Structured Socratic Follow-up State Machine:** Traps concept omissions and triggers targeted socratic prompts while preserving session momentum and multi-attempt candidate history.
4. **Comprehensive Empirical Systems Validation:** 9-vector security negative testing, 50-iteration subsystem latency benchmarks, and 6-configuration architectural ablation.

---

## 3. Associated Empirical Assets
- **Table 1:** Subsystem Latency Benchmark (`research/tables/table_sys_latency_benchmark.md`)
- **Table 2:** Docker Security Boundary Negative Tests (`research/tables/table_sys_security_boundary.md`)
- **Table 3:** Architectural Component Removal Reliability (`research/tables/table_sys_architectural_ablation.md`)
- **Figure 1:** Subsystem Latency Profiling Distribution (`research/figures/sys_subsystem_latency.png`)
- **Figure 2:** Multi-Layer Containment Architecture Diagram
