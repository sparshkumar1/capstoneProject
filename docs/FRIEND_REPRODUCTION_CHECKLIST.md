# PrepAIred — Independent Tester & Friend Reproduction Checklist

**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Authoritative Booklet:** [`docs/PREPAIRED_COMPLETE_BOOKLET.md`](PREPAIRED_COMPLETE_BOOKLET.md)
**Release Tag:** `paper-v1.0` (Commit: `ea15e3c`)
**Target Audience:** An independent tester, friend, or external reviewer setting up PrepAIred on a fresh machine without prior knowledge of the codebase.

> **External Third-Party Validation: PENDING**
> The repository has been internally verified and a self-contained independent reproduction protocol has been prepared. Independent third-party reproduction has not yet been completed.

---


## 1. Prerequisites Checklist

Before starting, verify you have the following installed on your system:

- [ ] **Operating System:** Windows 10/11, macOS, or Ubuntu Linux (20.04+)
- [ ] **Python:** Python 3.10 or 3.11 (`python --version`)
- [ ] **Node.js & npm:** Node.js 18+ and npm 9+ (`node -v`, `npm -v`)
- [ ] **Git:** Git CLI (`git --version`)
- [ ] **RAM:** Minimum 8 GB RAM (16 GB recommended for local LLM mode)
- [ ] **Storage:** Minimum 5 GB free disk space
- [ ] **Optional (for live C coding sandbox):** Docker Desktop running (`docker --version`)

---

## 2. Step-by-Step Clean Setup Protocol

### Step 1: Clone Repository
```bash
git clone https://github.com/sparshkumar1/capstoneProject.git
cd capstoneProject
```

### Step 2: Configure Environment
Copy the example environment file:
```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

### Step 3: Python Environment & Dependencies
```bash
# Create Virtual Environment
python -m venv .venv

# Activate Virtual Environment:
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/evaluator.txt
pip install -r requirements/rl.txt
pip install -e .
```

### Step 4: Frontend Dependencies
```bash
npm --prefix apps/web install
```

### Step 5: (Optional for Local LLM Mode) Download Qwen 1.5B GGUF Model
If you want to test the local Qwen LLM for generative follow-ups on CPU:
1. Create the model directory:
   ```bash
   mkdir -p models/gguf
   ```
2. Download `qwen2.5-1.5b-instruct-q4_k_m.gguf` (~1.06 GB) from Hugging Face:
   - URL: `https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf`
   - Place the file at: `models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf`
3. If this step is skipped, PrepAIred will automatically execute in **deterministic structured recovery fallback mode**, which requires zero external model downloads.

---

## 3. Verification & Validation Steps

### Step 6: Run Full Backend Test Suite
```bash
python -m pytest tests/ -v
```
- **Expected Result:** **177 passed, 1 skipped** (CUDA gated), **0 failed**.

### Step 7: Run Frontend Test Suite
```bash
npm --prefix apps/web test -- --run
```
- **Expected Result:** **7 passed, 0 failed**.

### Step 8: Run Deterministic Paper Reproduction Harness
```bash
python scripts/reproduce_paper.py
```
- **Expected Result:**
  - **480 / 480 evaluations verified** across EXP 1–5.
  - Figures 1–8 regenerated in `research/results/figures/`.

---

## 4. Live Interactive Demo Walkthrough

### Step 9: Start Services
Open three terminal windows (with `.venv` activated):

**Terminal 1 — Evaluator Microservice (Port 5000):**
```bash
python services/evaluator/app.py
```

**Terminal 2 — FastAPI Backend (Port 8000):**
```bash
uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3 — React Web Client (Port 5173):**
```bash
npm --prefix apps/web run dev
```

### Step 10: Run Mock Interview
1. Open your browser and navigate to `http://localhost:5173`.
2. Log in with candidate username (e.g. `test_user`).
3. Select technical topic (e.g., *Arrays / Two Sum*).
4. Answer Question 1 verbally or type an answer.
5. Observe:
   - Evaluator score breakdown ($S_1, S_2, R$).
   - Anti-keyword dampening penalty if answer lacks reasoning.
   - PPO adaptive difficulty transition (Easier / Same / Harder).
   - Targeted follow-up question.
6. Try a live C coding question in Monaco Editor.
7. Complete session and view the **Comprehensive Performance Report**.

---

## 5. Independent Tester Feedback Form

Please complete this feedback form and submit it to the project maintainers:

```
================================================================================
PREPAIRED INDEPENDENT REPRODUCTION FEEDBACK FORM
================================================================================
Tester Name / Identifier: _____________________________________________________
Date of Test:             _____________________________________________________
Operating System:         [ ] Windows 10/11   [ ] macOS   [ ] Ubuntu Linux
Python Version:           _____________________________________________________
Node.js Version:          _____________________________________________________
CPU Model & Cores:        _____________________________________________________
RAM (GB):                 _____________________________________________________
Dedicated GPU (if any):   [ ] None (CPU Only) [ ] NVIDIA GPU: __________________

TEST SUITE RESULTS:
- Backend PyTest:         [ ] PASS (177 passed)     [ ] FAIL (Errors: ________)
- Frontend Vitest:        [ ] PASS (7 passed)       [ ] FAIL (Errors: ________)
- Paper Reproduction:     [ ] PASS (480 verified)   [ ] FAIL (Errors: ________)

LOCAL LIVE DEMO EXPERIENCE:
- Evaluator Service:      [ ] Started Cleanly       [ ] Failed (Log: _________)
- Backend Server:         [ ] Started Cleanly       [ ] Failed (Log: _________)
- Web Client:             [ ] Started Cleanly       [ ] Failed (Log: _________)
- Qwen LLM Mode:          [ ] Loaded GGUF (~2.2s)   [ ] Fallback Mode Tested

TOTAL SETUP TIME (Minutes): ____________________________________________________

ISSUES OR CONFUSING DOCUMENTATION ENCOUNTERED:
1. _____________________________________________________________________________
2. _____________________________________________________________________________
3. _____________________________________________________________________________

OVERALL VERDICT:
[ ] 100% REPRODUCIBLE (Setup worked without code/config modifications)
[ ] REPRODUCIBLE WITH MINOR WORKAROUND (Explain: _____________________________)
[ ] BLOCKED / FAILED (Explain: _______________________________________________)
================================================================================
```
