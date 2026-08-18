# PrepAIred — Master Deployment & Operational Guide (Stage 23)

**Document ID:** `DEPLOYMENT-GUIDE-STG23`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Environments:** Local Development (Windows / Linux / macOS) & Production Multi-Container Orchestration
**Execution Date:** 2026-08-17

---

## 1. Dual Configuration Demarcation (Absolute Rule)

```
================================================================================
CONFIG A: RESEARCH CONFIGURATION (EXP-3)
================================================================================
- Model: Qwen/Qwen2.5-7B-Instruct (bfloat16)
- Model Revision: a09a35458c702b33eeacc393d103063234e8bc28
- Target Environment: Google Colab / Cloud NVIDIA Tesla T4 GPU (14.56 GB VRAM, CUDA 12.8)
- Scope: Frozen scientific evidence supporting the research manuscript (Table VI).
================================================================================

================================================================================
CONFIG B: LIVE DEMO & LOCAL DEPLOYMENT (STAGE 23)
================================================================================
- Model: Qwen/Qwen2.5-1.5B-Instruct-GGUF (Q4_K_M, 986 MB file size)
- Runtime Engine: llama.cpp / llama-cpp-python (12 CPU threads)
- Target Environment: Standard Consumer Laptop / Desktop CPU (No GPU required, ~1.36 GB RAM)
- Measured Latency: ~1.8s - 2.9s per task (Mean = 2.195s, 18.79 tok/s)
- Fallback System: Sub-50ms deterministic rubric-grounded recovery
================================================================================
```

---

## 2. Prerequisites & System Requirements

- **Operating System:** Windows 10/11 (64-bit), Ubuntu 22.04 LTS+, or macOS 13+ (Apple Silicon or Intel).
- **Python Runtime:** Python 3.10, 3.11, or 3.12 (64-bit).
- **Node.js Runtime:** Node.js 18+ and npm 9+.
- **Container Runtime:** Docker Desktop or Docker Engine 24+ with rootless support.
- **Memory & Storage:** Minimum 8 GB RAM (16 GB recommended), 10 GB free disk space.

---

## 3. Fresh-Clone Installation & Environment Setup

### Step 1: Clone Repository & Create Virtual Environment
```bash
# Clone the repository
git clone https://github.com/your-username/PrepAIred.git
cd PrepAIred

# Create and activate Python virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate
```

### Step 2: Install Python Backend & Microservice Dependencies
```bash
# Core platform dependencies
pip install -r requirements.txt

# CPU llama-cpp-python wheel for local GGUF inference
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Step 3: Install Frontend Dependencies
```bash
cd apps/web
npm install
cd ../..
```

### Step 4: Configure Environment Variables
```bash
# Copy example configuration template
cp .env.example .env
```
Ensure `.env` contains:
```env
PORT=8000
EVALUATOR_URL=http://localhost:5000
QWEN_URL=http://localhost:8001
C_SANDBOX_TIMEOUT_SEC=2.0
C_SANDBOX_MEMORY_MB=128
C_SANDBOX_PIDS_LIMIT=32
```

### Step 5: Download Local Qwen 1.5B GGUF Model (986 MB)
```bash
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
print('Qwen 1.5B GGUF model ready for local CPU inference.')
"
```

### Step 6: Build Docker Coding Sandbox Image
```bash
docker build -t prepaired-c-sandbox:latest -f Dockerfile.sandbox .
```

---

## 4. Multi-Service Execution (Local Interactive Mode)

Run each microservice in a dedicated terminal or background process:

```bash
# Terminal 1: Qwen 1.5B GGUF Microservice (Port 8001)
python services/qwen/app.py

# Terminal 2: Standalone Evaluator Microservice (Port 5000)
python services/evaluator/app.py

# Terminal 3: FastAPI Backend Orchestrator (Port 8000)
uvicorn apps.backend.main:app --reload --port 8000

# Terminal 4: React 18 / Vite Frontend Client (Port 5173)
cd apps/web && npm run dev
```

---

## 5. Docker Compose Full-Stack Deployment

To launch all microservices and containerized networks in a unified orchestration:

```bash
# Start all containers in detached mode
docker-compose up -d --build

# Inspect service logs
docker-compose logs -f backend
```

---

## 6. Service Health Verification Endpoints

- **Backend API:** `GET http://localhost:8000/health` $\to$ Returns `{"status": "ok", "service": "prepaired-backend"}`
- **Evaluator Service:** `GET http://localhost:5000/health` $\to$ Returns `{"status": "ok", "service": "prepaired-evaluator"}`
- **Qwen Microservice:** `GET http://localhost:8001/health` $\to$ Returns `{"status": "ok", "models_loaded": ["qwen_1b"], "model_types": {"qwen_1b": "gguf"}}`
