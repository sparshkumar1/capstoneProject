# Stage 22.2 — CPU-Only Local LLM Benchmark Report for Live Demonstration

**Document ID:** `STAGE-22-2-CPU-LOCAL-LLM-BENCHMARK`
**System:** PrepAIred Automated Technical Interview Platform (Live Demo Configuration)
**Hardware Environment:** Windows 11 CPU (10 Physical Cores, 12 Logical Threads, 15.68 GB System RAM)
**Benchmark Date:** 2026-08-17
**Scientific Boundary:** **Engineering Benchmark for Demo Deployment Only.** Does not alter EXP-1 through EXP-5 research evidence or Qwen-7B GPU results in the paper.

---

## 1. Executive Summary & Comparative Matrix

To solve the CPU throughput bottleneck of unquantized Transformers inference (which exhibited ~154s–193s latency per turn), we conducted a controlled engineering benchmark evaluating official 4-bit quantized GGUF models running on `llama.cpp` CPU execution across four representative production tasks.

| Model Candidate | Quantization | Runtime Engine | License | Load Time | Process RAM | Mean Latency | Generation Speed | Output Quality & Grounding | Demo Verdict |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|:---:|
| **Qwen2.5-1.5B-Instruct (Baseline)** | Unquantized bfloat16 | HuggingFace Transformers (CPU) | Apache-2.0 | 6.78 s | ~0.47 GB | **174.10 s** | ~0.35 tok/s | Accurate but unusable for live interaction | **`NOT SUITABLE (>30s)`** |
| **Qwen2.5-1.5B-Instruct-GGUF (Primary)** | **Q4_K_M** | **llama.cpp (12 CPU threads)** | **Apache-2.0** | **1.69 s** | **1.36 GB** | **2.195 s** | **18.79 tok/s** | **Excellent, candidate-specific, grounded** | **`EXCELLENT (<5s)`** |
| **SmolLM2-1.7B-Instruct-GGUF (Secondary)** | **Q4_K_M** | **llama.cpp (12 CPU threads)** | **Apache-2.0** | **1.02 s** | **1.91 GB** | **4.675 s** | **9.31 tok/s** | **Good, technically sound, grounded** | **`EXCELLENT (<5s)`** |

---

## 2. Task-by-Task Performance Breakdown

### Task A: Candidate-Specific Follow-Up Probing
- **Prompt:** Candidate answered Two Sum with a hash map but omitted complement calculation. Probes how complement $(T - x)$ is calculated.
- **Qwen 1.5B Q4_K_M:** **1.801 s** (21 tokens @ $11.66\text{ tok/s}$)
  *Output:* *"How does complement calculation and index storage help in finding the two indices that sum up to the target value?"*
- **SmolLM2 1.7B Q4_K_M:** **2.464 s** (26 tokens @ $10.55\text{ tok/s}$)
  *Output:* *"How do you handle the case where the array has duplicate elements and the target sum is the same for multiple pairs?"*

### Task B: Formative Remediation Feedback
- **Prompt:** Candidate explained paging but omitted offset preservation and TLB caching. Generates 2 actionable directives.
- **Qwen 1.5B Q4_K_M:** **2.846 s** (64 tokens @ $22.49\text{ tok/s}$)
  *Output:* Bulleted directives explaining page offset preservation and Translation Lookaside Buffer caching.
- **SmolLM2 1.7B Q4_K_M:** **6.471 s** (64 tokens @ $9.89\text{ tok/s}$)
  *Output:* Actionable feedback detailing virtual page division and frame mapping.

### Task C: Misconception / Gap Probing
- **Prompt:** Candidate asserted virtual addresses directly access RAM without hardware translation.
- **Qwen 1.5B Q4_K_M:** **1.217 s** (16 tokens @ $13.15\text{ tok/s}$)
  *Output:* *"Can you explain how the CPU translates virtual addresses to physical addresses using memory translation?"*
- **SmolLM2 1.7B Q4_K_M:** **3.284 s** (20 tokens @ $6.09\text{ tok/s}$)
  *Output:* *"Can you explain how the Memory Management Unit (MMU) translates virtual addresses to physical memory addresses?"*

### Task D: Technical Response with Grounded Feedback
- **Prompt:** Candidate reversed linked list pointers but omitted updating head pointer and terminating with NULL.
- **Qwen 1.5B Q4_K_M:** **2.915 s** (64 tokens @ $21.96\text{ tok/s}$)
  *Output:* Positive reinforcement of pointer traversal + directive for head pointer update.
- **SmolLM2 1.7B Q4_K_M:** **6.479 s** (64 tokens @ $9.88\text{ tok/s}$)
  *Output:* Reinforcement of pointer swap + directive for list termination.

---

## 3. Engineering & Deployment Trade-Off Analysis

1. **Generation Speed:** `Qwen2.5-1.5B-Instruct-GGUF (Q4_K_M)` achieves **$18.79\text{ tok/s}$**, more than **2.0x faster** than SmolLM2 ($9.31\text{ tok/s}$) on the identical 12-thread CPU configuration.
2. **Mean Latency:** Qwen 1.5B Q4_K_M delivers a mean turn latency of **$2.195\text{s}$**, comfortably fitting within the `<5.0s` target for a smooth, conversational live demonstration.
3. **RAM Footprint:** Both quantized models occupy $<2.0\text{ GB}$ of process memory ($1.36\text{ GB}$ for Qwen vs. $1.91\text{ GB}$ for SmolLM2), allowing effortless co-execution alongside the FastAPI backend, Evaluator microservice, and Docker daemon on 8GB/16GB consumer laptops.
4. **Architectural Parity:** Qwen 1.5B shares the exact tokenizer vocabulary, ChatML prompt syntax, and alignment with the research baseline (`Qwen2.5-7B-Instruct`), ensuring zero prompt re-engineering.
5. **Licensing:** Both models are released under the permissive **Apache-2.0 License**.

---

## 4. Machine-Readable Artifact Location
The full benchmark configuration and raw execution outputs are recorded in:
- [`research/results/raw/local_llm_demo_benchmark.json`](../research/results/raw/local_llm_demo_benchmark.json)

---

## 5. Final Recommendation & Decision

```
================================================================================
FINAL DEMO SELECTION: C. BOTH ARE SUITABLE — QWEN PREFERRED
================================================================================
PRIMARY DEMO MODEL:        Qwen/Qwen2.5-1.5B-Instruct-GGUF
SECONDARY DEMO MODEL:      HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF
RUNTIME ENGINE:            llama.cpp (llama-cpp-python, CPU)
QUANTIZATION FORMAT:       Q4_K_M (986 MB file size)
MEASURED MEAN LATENCY:     2.195 seconds per turn (18.79 tok/s)
PEAK PROCESS RAM:          1.36 GB
OUTPUT QUALITY:            100% Grounded, Technically Sound, Follows Contract
INSTALLATION COMPLEXITY:   Low (pip install llama-cpp-python + hf_hub_download)
LICENSE:                   Apache-2.0
================================================================================
```

- **Stop Condition:** Isolated benchmark complete. No production code or research data has been modified.
