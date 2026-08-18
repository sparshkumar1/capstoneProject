# PrepAIred — Independent Tester & Friend Reproduction Checklist

**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md) (*IEEE Transactions on Learning Technologies Draft*)
**Master Manual & Viva Booklet:** [`docs/PREPAIRED_COMPLETE_BOOKLET.md`](PREPAIRED_COMPLETE_BOOKLET.md)
**Frozen Research Release Tag:** `paper-v1.0` (Commit: `ea15e3c`)
**Target Audience:** An independent peer reviewer, colleague, or friend reproducing PrepAIred on a separate, fresh machine.

> **External Third-Party Validation: PENDING**
> The repository has been internally verified and a self-contained independent reproduction protocol has been prepared. Independent third-party reproduction has not yet been completed.

---

## 1. System Prerequisites Checklist

Before starting, ensure your machine satisfies the following hardware and software requirements:

| Component | Minimum Requirement | Recommended | How to Verify |
|---|---|---|---|
| **Operating System** | Windows 10/11, macOS, or Ubuntu Linux (20.04+) | Windows 11 / Ubuntu 22.04 | `[System.Environment]::OSVersion` / `uname -a` |
| **Python** | Python 3.10, 3.11, or 3.12 | Python 3.11 or 3.12 | `python --version` |
| **Node.js & npm** | Node.js 18.x+ and npm 9.x+ | Node.js 20.x | `node -v` && `npm -v` |
| **Git** | Git 2.30+ | Latest Git CLI | `git --version` |
| **System RAM** | 8 GB RAM | 16 GB RAM | Task Manager / `free -h` |
| **Disk Storage** | 5 GB free disk space | 10 GB free space | `Get-PSDrive` / `df -h` |
| **Database** | **NOT REQUIRED** | Backend uses built-in in-memory session store | Zero database installation needed |
| **Docker** | Required for C coding sandbox; optional for verbal demo | Docker Desktop 4.x+ | `docker --version` |
| **GPU / CUDA** | **NOT REQUIRED** (Runs 100% on CPU) | Any modern 4+ core CPU | — |

---

# PART A — PRE-DEMO SETUP & COMPONENT VERIFICATION

### Step 1: Clone the Public Repository
```bash
git clone https://github.com/sparshkumar1/capstoneProject.git
cd capstoneProject
```

### Step 2: Configure Environment
```bash
# Windows PowerShell:
Copy-Item .env.example .env

# Linux / macOS:
cp .env.example .env
```

### Step 3: Setup Python Environment & Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment:
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# (If blocked by Windows execution policy, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

# Linux / macOS:
source .venv/bin/activate

# Upgrade pip and install all required platform dependencies
python -m pip install --upgrade pip
pip install -r requirements/base.txt -r requirements/evaluator.txt -r requirements/rl.txt -r requirements/qwen.txt
pip install -e .

```

### Step 4: Install Frontend Dependencies
```bash
npm --prefix apps/web install
```

### Step 5: Acquire Qwen 1.5B GGUF Model (~1.06 GB)
The local CPU demo uses `Qwen2.5-1.5B-Instruct-GGUF` (quantization `Q4_K_M`). Run the automated downloader script (no Hugging Face login or token required):

```bash
python scripts/download_qwen_model.py
```
- **Destination:** `models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf`
- **Expected File Size:** ~1,117 MB (~1.06 GB).

### Step 6: Verify Genuine Qwen GGUF Inference
Run the standalone live verification harness to confirm that the model loads in `llama.cpp` and generates dynamic follow-up questions:

```bash
python scripts/verify_qwen_live.py
```
- **PASS Criteria:** Output displays `VERDICT: [PASS] — GENUINE QWEN 1.5B GGUF INFERENCE CONFIRMED` with `DECISION SOURCE: qwen_1.5b_llm` and `LLM STATUS: available`.
- **FAIL Criteria:** Output displays `decision_source = "non_llm_structured_recovery"` (indicating model failed to load).

### Step 7: Run Automated Verification Suites
```bash
# 1. Backend regression suite (178 tests: 177 passed, 1 skipped CUDA)
python -m pytest tests/ -v

# 2. Frontend component suite (7 passed)
npm --prefix apps/web test -- --run

# 3. Paper reproduction harness (480 / 480 evaluations verified)
python scripts/reproduce_paper.py

# 4. Master integrated end-to-end multi-agent lifecycle
python scripts/verify_integrated_e2e.py

# 5. Live browser application API flow
python scripts/verify_live_browser_flow.py
```

---

# PART B — REAL LIVE INTERACTIVE APPLICATION DEMO

To demonstrate the full interactive PrepAIred system with live UI, neural evaluation, RL adaptation, Qwen follow-ups, and coding execution, start the microservices across **4 separate terminals** (all with `.venv` activated):

```
+-------------------------------------------------------------------------------+
|                       4-TERMINAL SERVICE STARTUP LAYOUT                       |
+-------------------------------------------------------------------------------+
| Terminal 1 (Qwen Microservice :8001):                                         |
|     .\.venv\Scripts\Activate.ps1                                              |
|     python -m services.qwen.app                                               |
|                                                                               |
| Terminal 2 (Evaluator Microservice :5000):                                    |
|     .\.venv\Scripts\Activate.ps1                                              |
|     python services/evaluator/app.py                                          |
|                                                                               |
| Terminal 3 (FastAPI Backend Server :8000):                                    |
|     .\.venv\Scripts\Activate.ps1                                              |
|     python -m uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload|
|                                                                               |
| Terminal 4 (React Web Client :3000):                                          |
|     npm --prefix apps/web run dev                                             |
+-------------------------------------------------------------------------------+
```

### Health Check Verification Commands
Before opening the browser, verify that all services are operational:
- **Qwen Health:** `http://localhost:8001/health` $\to$ `{"status": "ok", "models_loaded": ["qwen_1b"], "model_types": {"qwen_1b": "gguf"}, "primary_demo_engine": "llama.cpp (CPU)"}`
- **Evaluator Health:** `http://localhost:5000/health` $\to$ `{"status": "ok", "components": ["s1", "s2", "r"]}`
- **Backend API Docs:** `http://localhost:8000/docs` $\to$ Swagger UI loads cleanly
- **Frontend Client:** `http://localhost:3000` $\to$ PrepAIred Login screen renders

## 2. Complete 24-Step Live Interactive Demo Walkthrough

Follow this exact 24-step sequence to demonstrate every single subsystem of the PrepAIred platform in the real application:

### Subsystem Startup (Steps 1–4)
1. **Step 1: Start Qwen Microservice (Port 8001)**
   - Terminal 1: `python -m services.qwen.app`
   - *Expected:* `[QwenService] GGUF model qwen_1b ready (threads=8)`
2. **Step 2: Start Evaluator Microservice (Port 5000)**
   - Terminal 2: `python services/evaluator/app.py`
   - *Expected:* Evaluator service running with Sentence-BERT and CrossEncoder loaded.
3. **Step 3: Start FastAPI Backend Server (Port 8000)**
   - Terminal 3: `python -m uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload`
   - *Expected:* Backend API running on `http://localhost:8000`.
4. **Step 4: Start React Web Frontend (Port 3000)**
   - Terminal 4: `npm --prefix apps/web run dev`
   - *Expected:* Vite client running on `http://localhost:3000`.

### User Setup & Interview Initialization (Steps 5–6)
5. **Step 5: Login in Browser**
   - Open `http://localhost:3000` in Chrome / Edge / Firefox. Enter Candidate Name (`Alex Candidate`) and Email (`alex@example.com`).
6. **Step 6: Start Interview Session**
   - Select technical domain (**Arrays / Two Sum** or **Hash Tables**) and click **"Start Practice Interview"**.

### Evaluator & RL Adaptation Verification (Steps 7–10)
7. **Step 7: Submit Text Technical Answer**
   - Type answer: `"I iterate through the array once and store complements in a hash map to achieve O(N) time and O(N) space."`
8. **Step 8: Observe Evaluator Score Breakdown**
   - Verify score $>0.80$ (Grade: Excellent), showing $S_1$ (semantic), $S_2$ (concept coverage), and $R$ (reasoning quality).
9. **Step 9: Observe RL Adaptive Difficulty Update**
   - PPO difficulty policy executes on candidate state vector $\mathbf{s}_t$ and transitions difficulty to Harder.
10. **Step 10: Observe Genuine Qwen 1.5B GGUF Follow-Up Question**
    - Observe targeted follow-up question probe generated dynamically.
    - Terminal 1 logs token generation; metadata confirms `"decision_source": "qwen_1.5b_llm"`, `"llm_status": "available"`.

### Live Speech / Microphone Input Pipeline (Steps 11–16)
11. **Step 11: Click Microphone Button**
    - Click **"Record Audio"** in the browser interview room.
12. **Step 12: Speak a Real Verbal Answer**
    - When prompted by the browser, allow microphone access and speak your answer (e.g. explaining hash collision resolution).
13. **Step 13: Verify Recording & Audio Upload**
    - Click **"Stop & Submit"**. Audio waveform animates and uploads WebM/WAV to `/api/transcribe`.
14. **Step 14: Verify Speech-to-Text Transcription**
    - Transcribed spoken text renders in the candidate answer view.
15. **Step 15: Verify Hesitation, Prosody & Confidence Output**
    - Acoustic pipeline extracts acoustic confidence $c_t$, hesitation score $h_t$, and speaking rate, ingesting into candidate state.
16. **Step 16: Continue Interview**
    - Click **"Next Question"** to proceed to the coding round.

### Containerized C Coding Sandbox (Steps 17–21)
17. **Step 17: Enter Coding Question**
    - Monaco Code Editor opens with C template.
18. **Step 18: Write C Code**
    - Write C implementation (e.g. pointer addition or dynamic array allocation).
19. **Step 19: Click "Run Code"**
    - Submit code to backend `/api/run_code`.
20. **Step 20: Verify Isolated Docker Sandbox Execution**
    - Untrusted C code compiles (`gcc -O2`) inside an isolated container (128MB RAM, 32 PIDs, `--net=none`) and displays test results.
21. **Step 21: Continue Interview**
    - Submit final code solution and continue.

### Session Finalization & Report Synthesis (Steps 22–24)
22. **Step 22: Finish Interview**
    - Click **"Finish Interview"** to finalize the multi-turn session.
23. **Step 23: Open Final Performance Debrief Report**
    - Browser navigates to `/report/{id}` dashboard.
24. **Step 24: Verify Detailed Recommendations & Radar Charts**
    - Verify overall score, radar competency dimensions (Correctness, Reasoning, Complexity, Communication), concept strengths, and targeted remediation tips.

---

## 3. How to Distinguish Genuine Qwen Inference vs. Fallback

| Inspection Point | Genuine Qwen 1.5B GGUF Execution | Fallback Recovery Mode |
|---|---|---|
| **Response JSON / Report** | `"decision_source": "qwen_1.5b_llm"` | `"decision_source": "non_llm_structured_recovery"` |
| **LLM Status Field** | `"llm_status": "available"` | `"llm_status": "llm_unavailable"` |
| **Qwen Terminal 1 Log** | `[QwenService] Generated 45 tokens in ~2.1s` | No token generation logged |
| **Verification Command** | `python scripts/verify_qwen_live.py` returns `[PASS]` | Returns `[FAIL]` if model missing |

---

## 4. Independent Tester Feedback Report Template

Please complete this feedback report after attempting reproduction and share your results:

```
================================================================================
PREPAIRED INDEPENDENT REPRODUCTION FEEDBACK REPORT
================================================================================
Tester Name / GitHub Handle: __________________________________________________
Date of Test:                __________________________________________________
Operating System:            [ ] Windows 10/11   [ ] macOS   [ ] Ubuntu Linux
Python Version:              __________________________________________________
Node.js Version:             __________________________________________________
CPU Model & Cores:           __________________________________________________
Total System RAM (GB):       __________________________________________________
Docker Desktop Running:      [ ] Yes   [ ] No (Skipped coding sandbox)
Physical Microphone Used:    [ ] Yes   [ ] No (Used text answer mode)

PRE-DEMO VERIFICATION RESULTS:
[ ] Step 1: Git clone successful
[ ] Step 2: Environment (.env) configured
[ ] Step 3: Python virtual environment created & activated
[ ] Step 4: Python dependencies installed cleanly
[ ] Step 5: Node dependencies installed cleanly
[ ] Step 6: Qwen 1.5B GGUF downloaded via scripts/download_qwen_model.py
[ ] Step 7: Live Qwen GGUF verified via scripts/verify_qwen_live.py
[ ] Step 8: PyTest backend suite (177 passed)
[ ] Step 9: Vitest frontend suite (7 passed)
[ ] Step 10: reproduce_paper.py (480 evaluations verified)
[ ] Step 11: verify_integrated_e2e.py (all subsystems verified)
[ ] Step 12: verify_live_browser_flow.py (all 8 application phases passed)

LIVE BROWSER INTERACTIVE DEMO RESULTS:
[ ] 4 Microservice Terminals Started Cleanly (:8001, :5000, :8000, :5173)
[ ] Health endpoints verified on all ports
[ ] Login & session creation completed in browser
[ ] Evaluator scoring & anti-keyword dampening observed
[ ] RL difficulty adaptation observed
[ ] Genuine Qwen follow-up probe generated with attribution ('qwen_1.5b_llm')
[ ] Audio speech transcription & prosody tested (or text fallback verified)
[ ] Coding question executed in Docker sandbox
[ ] Final performance debrief report generated and reviewed

TOTAL SETUP & DEMO TIME (Minutes): _____________________________________________

OBSERVED ISSUES / UNEXPECTED BEHAVIORS:
1. _____________________________________________________________________________
2. _____________________________________________________________________________
3. _____________________________________________________________________________

OVERALL INDEPENDENT REPRODUCTION VERDICT:
[ ] PASS — 100% Reproducible without code or configuration modifications
[ ] PASS WITH MINOR WORKAROUND (Describe: ______________________________________)
[ ] FAIL / BLOCKED (Describe: __________________________________________________)
================================================================================
```
