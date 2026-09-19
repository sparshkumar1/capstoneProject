# Reproduction Guide: Paper 1 (Systems, Security & Sandboxing)

**Target Venue:** *ATIS 2026* / *IEEE Access*  
**Paper Title:** *PREPAIred: An Evidence-Grounded Adaptive Multimodal Framework for Technical Interview Assessment and Feedback*

---

## 1. Prerequisites
- Docker Engine installed and running (`docker --version`).
- Sandbox image built:
  ```powershell
  # If image needs rebuilding:
  docker build -t prepaired-c-sandbox:latest -f Dockerfile.sandbox .
  ```
- Python virtual environment activated:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

---

## 2. Execute Systems Experiments

Run the automated systems validation suite:
```powershell
python research/scripts/run_systems_experiments.py
```

This single command automatically executes:
1. **EXP-SYS-1: Docker Security Negative Tests (`SEC-01` to `SEC-09`)**
   - Tests kernel ptrace restrictions, socket header rules, compiler traps, SIGSEGV signals, 2.0s timeouts, 128MB OOM kills, network disconnection, 32-PID fork bomb caps, and read-only rootfs.
   - Raw output: `research/raw/sys_security_raw.json`
   - Formatted table: `research/tables/table_sys_security_boundary.md`

2. **EXP-SYS-2: Subsystem Latency Profiling (50 iterations per subsystem)**
   - Benchmarks audio prosody extraction, technical evaluator ($S_1 + S_2 + R$), score validator, PPO inference, Socratic follow-up FSM, grounded feedback synthesizer, SQLite WAL writes, and Docker sandbox execution.
   - Raw output: `research/raw/sys_latency_benchmark_raw.json`
   - Formatted table: `research/tables/table_sys_latency_benchmark.md`
   - Generated figure: `research/figures/sys_subsystem_latency.png`

3. **EXP-SYS-3: Single-Component Removal Resilience Study (`ARCH-01` to `ARCH-06`)**
   - Tests end-to-end turn latencies and crash resilience when disabling Audio, PPO, Qwen LLM, Docker sandbox, or SQLite WAL persistence.
   - Raw output: `research/raw/sys_arch_ablation_raw.json`
   - Formatted table: `research/tables/table_sys_architectural_ablation.md`

4. **EXP-LLM-1: Feedback Grounding & Fallback Stress Test**
   - Evaluates FeedbackAgent under empty responses, zero scores, misconceptions, and adversarial inputs.
   - Raw output: `research/raw/llm_grounding_raw.json`
   - Formatted table: `research/tables/table_llm_adversarial_grounding.md`

---

## 3. Verify Engineering Test Suite
```powershell
pytest tests/unit/test_docker_sandbox.py tests/unit/test_database.py tests/unit/test_orchestrator.py -v
```
All tests must report `PASSED`.
