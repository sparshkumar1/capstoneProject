# Live Demonstration & CPU Local LLM Integration Guide (Stage 22.3)

**Document ID:** `LIVE-DEMO-CPU-LOCAL-LLM-CONFIG`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Architecture:** Windows 11 / Linux / macOS (CPU-Only, 8GB+ System RAM)
**Integrated Engine:** `llama.cpp` / `llama-cpp-python` with `Qwen2.5-1.5B-Instruct-GGUF` (Q4_K_M)
**Status:** **`100% INTEGRATED & VERIFIED`**

---

## 1. Dual Configuration Demarcation (Absolute Scientific Rule)

PrepAIred strictly decouples its **Research Scientific Evidence** from its **Local Live Demonstration Deployment**:

```
================================================================================
CONFIG A: RESEARCH SCIENTIFIC EVIDENCE (EXP-3)
================================================================================
- Model: Qwen/Qwen2.5-7B-Instruct (Full Precision / bfloat16)
- Model Revision: a09a35458c702b33eeacc393d103063234e8bc28
- Environment: Google Colab NVIDIA Tesla T4 GPU (14.56 GB VRAM, CUDA 12.8)
- Measured Performance: Lexical Grounding = 0.2496, Gap Coverage = 72.5%, Latency = 9.78s
- Immutable Raw Data: research/results/raw/experiment_3_qwen_raw.json
- Scope: Frozen scientific evidence supporting the research manuscript (Table VI).
================================================================================

================================================================================
CONFIG B: LOCAL LIVE DEMO / CLASSROOM DEPLOYMENT (STAGE 22.3)
================================================================================
- Model: Qwen/Qwen2.5-1.5B-Instruct-GGUF
- Quantization Format: Q4_K_M (986 MB file size)
- Runtime Engine: llama.cpp / llama-cpp-python (n_threads=12, n_ctx=2048)
- Target Hardware: Standard Consumer Laptop CPU (No GPU required, ~1.36 GB RAM)
- Measured Latency: ~1.8s - 2.9s per task (Mean = 2.195s across benchmark tasks)
- Fallback System: Sub-50ms deterministic rubric-grounded recovery
- License: Apache-2.0
================================================================================
```

---

## 2. Model Acquisition & Directory Layout

To download and set up the official GGUF model for local CPU inference:

```bash
# 1. Install llama-cpp-python CPU wheel
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 2. Download official Q4_K_M GGUF model (986 MB)
python -c "
from huggingface_hub import hf_hub_download
from pathlib import Path
out_dir = Path('models/gguf')
out_dir.mkdir(parents=True, exist_ok=True)
hf_hub_download(
    repo_id='Qwen/Qwen2.5-1.5B-Instruct-GGUF',
    filename='qwen2.5-1.5b-instruct-q4_k_m.gguf',
    local_dir=str(out_dir)
)
print('Model ready at models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf')
"
```

*Note: The `models/gguf/` directory and `*.gguf` files are explicitly excluded from version control in `.gitignore`.*

---

## 3. Microservice Startup & Live Execution

### Step 1: Start Qwen Microservice (Port 8001)
```bash
python services/qwen/app.py
```
*Console output:*
```
[QwenService] Loading GGUF model qwen_1b from models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf (threads=12)...
[QwenService] GGUF model qwen_1b ready in 1.02s
INFO: Uvicorn running on http://0.0.0.0:8001
```

### Step 2: Start Evaluator Microservice (Port 5000)
```bash
python services/evaluator/app.py
```

### Step 3: Start Backend API (Port 8000)
```bash
uvicorn apps.backend.main:app --reload --port 8000
```

### Step 4: Start Frontend Client (Port 5173)
```bash
cd apps/web
npm run dev
```

---

## 4. Attribution & Fallback Behavior

- **When Qwen 1.5B Generates:**
  - `decision_source`: `"qwen_1.5b_llm"`
  - `llm_status`: `"available"`
- **When Qwen Service is Offline:**
  - `decision_source`: `"non_llm_structured_recovery"`
  - `llm_status`: `"llm_unavailable"`
- **Zero Fabrication Guarantee:** Deterministic fallback directives are never mislabeled as LLM output.

---

## 5. Measured Laptop Benchmark Summary

| Benchmark Task | Target Concept / Gap | Measured CPU Latency | Output Speed | Attribution |
|---|---|:---:|:---:|:---:|
| **Task A: Follow-Up Probing** | Complement calculation $(T - x)$ | **1.801 s** | $11.66\text{ tok/s}$ | `qwen_1.5b_llm` |
| **Task B: Formative Feedback** | Offset preservation & TLB caching | **2.846 s** | $22.49\text{ tok/s}$ | `qwen_1.5b_llm` |
| **Task C: Misconception Probe** | MMU hardware translation | **1.217 s** | $13.15\text{ tok/s}$ | `qwen_1.5b_llm` |
| **Task D: Technical Grounding** | Linked list termination with NULL | **2.915 s** | $21.96\text{ tok/s}$ | `qwen_1.5b_llm` |
| **Mean Across Tasks** | **Consolidated Performance** | **2.195 s** | **18.79 tok/s** | **`PASS (<5s)`** |
