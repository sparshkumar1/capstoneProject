# PrepAIred

Adaptive AI interview preparation platform with multi-agent orchestration, reinforcement-learning-based difficulty control, voice and code evaluation, and structured formative feedback.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Repository Structure](#repository-structure)
- [Architecture](#architecture)
- [Architecture Diagram / Image](#architecture-diagram--image)
- [Agents and Main Modules](#agents-and-main-modules)
- [RL Method (Brief)](#rl-method-brief)
- [Services and Ports](#services-and-ports)
- [Quick Demo](#quick-demo)
- [API Endpoints (Backend)](#api-endpoints-backend)
- [API Endpoints (Evaluator)](#api-endpoints-evaluator)
- [API Endpoints (Qwen Service)](#api-endpoints-qwen-service)
- [Setup](#setup)
- [Running the Project](#running-the-project)
- [Typical Interview Flow](#typical-interview-flow)
- [Logging and Outputs](#logging-and-outputs)
- [Research Artifacts](#research-artifacts)
- [Contributing](#contributing)
- [Citation](#citation)
- [Known Improvement Areas](#known-improvement-areas)
- [License](#license)

## Overview

PrepAIred is an end-to-end system for technical interview practice (C and DSA focused) that runs a live, adaptive interview loop:

1. Ask a question from the curated bank.
2. Accept candidate response (voice/text/code).
3. Evaluate content quality and reasoning.
4. Validate/adjust score with guardrails.
5. Generate actionable feedback.
6. Adapt next-step strategy using RL policy.
7. Repeat until session end and generate final report.

The platform is designed around an orchestrator-centered multi-agent architecture so each component has a focused responsibility.

## Key Features

- Adaptive interview progression with PPO strategy + guardrails
- Baseline warm-up phase before RL activation
- Voice pipeline with confidence and hesitation signals
- Coding sandbox with safety checks and timeout control
- Multi-component evaluator (semantic, concept, reasoning)
- Validation layer for post-hoc score correction
- Rich per-turn feedback (strengths, misses, misconceptions, tips)
- Session logging and analytics
- Real-time WebSocket interview experience
- Unified launcher for all services

## Repository Structure

```text
PrepAIred/
├─ README.md
├─ launch.py
├─ .env.example
├─ pyproject.toml
├─ requirements/
│  ├─ base.txt
│  ├─ backend.txt
│  ├─ evaluator.txt
│  ├─ qwen.txt
│  ├─ rl.txt
│  └─ dev.txt
│
├─ apps/
│  ├─ backend/          ← FastAPI server (main.py + .env.example)
│  └─ web/              ← React/Vite frontend
│     ├─ package.json
│     ├─ vite.config.js
│     ├─ index.html
│     └─ src/           ← All JSX/JS/CSS source files
│
├─ services/
│  ├─ evaluator/        ← Standalone evaluator FastAPI service (port 5000)
│  │  ├─ app.py
│  │  ├─ assets/        ← FAISS index, pkl, qns.json, rubrics.json
│  │  └─ models/        ← Fine-tuned sentence transformer models
│  └─ qwen/             ← Qwen LLM microservice (port 8001)
│     ├─ app.py
│     └─ evaluate_upgraded.py
│
├─ agents/
│  ├─ orchestrator/     ← InterviewOrchestrator (session lifecycle hub)
│  ├─ strategy/         ← HybridOrchestrator (PPO + heuristic fallback)
│  ├─ feedback/         ← FeedbackAgent (15-field structured feedback)
│  ├─ validation/       ← ScoreValidator (post-hoc guardrails)
│  ├─ timing/           ← QuestionTimer
│  ├─ audio/            ← Audio pipeline (STT, confidence, hesitation)
│  ├─ coding_executor/  ← Sandboxed code runner
│  └─ question_selector/← QuestionSelector (difficulty/topic-aware)
│
├─ rl/
│  ├─ env/              ← InterviewEnv (Gymnasium)
│  ├─ training/         ← Training scripts
│  ├─ checkpoints/      ← Trained PPO artifacts (ppo_final.zip, vecnormalize.pkl)
│  ├─ logs/             ← Training logs
│  └─ experiments/
│
├─ data/
│  ├─ questions/        ← qns.json
│  ├─ rubrics/          ← rubrics_final_clean.json
│  ├─ sessions/
│  ├─ reports/
│  └─ vector_store/
│
├─ logs/
│  ├─ services/         ← Service stdout logs (backend.log, evaluator.log, ...)
│  └─ sessions/         ← Per-session turn logs
│
├─ tests/
│  ├─ unit/             ← test_orchestrator.py (14 tests)
│  ├─ integration/
│  ├─ api/
│  ├─ ws/
│  └─ e2e/
│
├─ scripts/
│  ├─ setup/
│  ├─ dev/
│  └─ release/
│
├─ docs/
│  ├─ architecture/
│  ├─ api/
│  ├─ runbooks/
│  └─ diagrams/
│
└─ research/
   ├─ papers/           ← Draft manuscripts (3 papers)
   ├─ capstone/         ← Capstone report + guidelines
   └─ experiments/
```

## Architecture

### Core Control

- **InterviewOrchestrator** coordinates session lifecycle and agent calls.
- **Strategy agent** suggests next action: Easier / Same / Harder.
- **Hint and Follow-up** are guardrail-triggered interventions, not RL actions.
- **Question selector** chooses next question by difficulty/topic constraints.

### Evaluation Layer

- **Evaluator** computes semantic, concept, and reasoning scores.
- **Validation agent** applies guardrails and score adjustments.
- **Coding executor** runs code in sandboxed process with test cases.

### Output Layer

- **Feedback agent** produces structured, actionable feedback.
- **Logger** stores turn-level events and session summaries.
- **Report generation** compiles full session outcomes.

### Audio Layer

- Speech-to-text
- Prosodic features
- Confidence/hesitation scoring
- RL state-signal extraction

## Architecture Diagram / Image

### Mermaid Diagram

```mermaid
flowchart TD
	C[Candidate] --> UI[Interview UI]
	UI --> O[Interview Orchestrator]
	O --> QS[Question Selector]
	O --> ST[Strategy Agent PPO]
	O --> EV[Evaluator]
	O --> VA[Validation Agent]
	O --> FB[Feedback Agent]
	O --> TM[Timer Agent]
	O --> LG[Logger Agent]
	UI --> AU[Audio Analysis Agent]
	AU --> O
	UI --> CE[Coding Executor Sandbox]
	CE --> O
	O --> UI
```

### Add Your Diagram Images

If you want static architecture images in GitHub preview, place images under `docs/diagrams/` and add links like:

```markdown
![System Architecture](docs/diagrams/system_architecture.png)
![Adaptive Interview Flow](docs/diagrams/adaptive_interview_flow.png)
```

## Agents and Main Modules

- Orchestrator: `agents/orchestrator/interview_orchestrator.py`
- Strategy (RL): `agents/strategy/hybrid_orchestrator.py`
- Feedback: `agents/orchestrator/feedback_agent.py`
- Evaluator API: `services/evaluator/app.py`
- Audio pipeline: `agents/audio/main.py`
- Validation: `agents/validation/score_validator.py`
- Timer: `agents/timing/timer.py`
- Code sandbox: `agents/coding_executor/coding_executor.py`
- Backend server: `apps/backend/main.py`
- Qwen service: `services/qwen/app.py`

## RL Method (Brief)

- Algorithm: PPO (Stable-Baselines3)
- State (6D): performance, rolling average, confidence, hesitation, time_norm, difficulty
- Actions (3): Easier, Same, Harder
- Guardrail interventions: Hint, Follow-up
- Baseline phase: deterministic initial questions before RL control
- Runtime safety: post-policy guardrails to prevent unstable actions
- Trained artifacts: `rl/checkpoints/seed_123/ppo_final.zip`, `vecnormalize.pkl`

## Services and Ports

`launch.py` starts these services in order:

1. Evaluator API: `http://localhost:5000`
2. Qwen microservice (optional, single-model): `http://localhost:8001`
3. Backend API/WebSocket: `http://localhost:8000`
4. Frontend dev server (optional): usually `http://localhost:5173`

## Quick Demo

Run these exact commands in Windows PowerShell from repository root.

### 1) Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies (one-time)

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements\backend.txt
python -m pip install -r requirements\evaluator.txt
python -m pip install -r requirements\rl.txt
cd apps\web
npm install
cd ..\..
```

### 3) Launch full stack

```powershell
python launch.py
```

### 4) Open app

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`

### 5) API-only demo (no Qwen, no frontend)

```powershell
python launch.py --backend-only
```

### 6) Smoke-test key endpoints

```powershell
curl http://localhost:8000/health
curl http://localhost:5000/api/evaluator/current-question
```

## API Endpoints (Backend)

From `frontend/main.py`:

- `GET /health`
- `POST /api/login`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `POST /api/sessions/{session_id}/end`
- `GET /api/sessions/{session_id}/report`
- `POST /api/transcribe`
- `POST /api/run_code`
- `GET /api/admin/sessions`
- `GET /api/admin/stats`
- `GET /api/admin/sessions/{session_id}`
- `WS /ws/interview/{session_id}`

## API Endpoints (Evaluator)

From `Evaluator_final/Evaluator/evaluate.py`:

- `POST /api/evaluator/set-question`
- `POST /api/evaluator/evaluate-answer`
- `GET /api/evaluator/last-result`
- `GET /api/evaluator/current-question`

## API Endpoints (Qwen Service)

From `services/qwen/app.py`:

- `GET /health`
- `POST /hint`
- `POST /followup`
- `POST /partial_eval`
- `POST /report`

The Qwen service is intentionally kept as a single model tier so the runtime stays simpler to explain, easier to validate, and easier to keep consistent across prompts.

## Setup

### Prerequisites

- Python 3.11+ (3.12 works for most components)
- Node.js 18+
- npm
- Optional GPU for local LLM acceleration

### 1) Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Install Python dependencies

```powershell
python -m pip install -r requirements\backend.txt
python -m pip install -r requirements\evaluator.txt
python -m pip install -r requirements\rl.txt
```

If FAISS install fails on Windows:

1. Use conda package for `faiss-cpu`, or
2. Use Python 3.11 specifically for evaluator stack

### 3) Install frontend dependencies

```powershell
cd apps\web
npm install
cd ..\..
```

## Running the Project

### Recommended (single command)

```powershell
python launch.py
```

Options:

```powershell
python launch.py --no-qwen
python launch.py --no-frontend
python launch.py --backend-only
```

### Manual startup (advanced)

Terminal 1:

```powershell
cd services\evaluator
python app.py
```

Terminal 2:

```powershell
cd services\qwen
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

Terminal 3:

```powershell
cd apps\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 4:

```powershell
cd apps\web
npm run dev
```

## Typical Interview Flow

1. User logs in and starts session.
2. Orchestrator sends first question.
3. Candidate answers via voice or code.
4. Evaluation + validation + feedback pipeline executes.
5. Strategy agent adapts difficulty/action.
6. Next question sent over WebSocket.
7. Final report generated at session end.

## Logging and Outputs

- Launcher logs: `logs/<service>.log`
- Evaluator session/result JSON outputs under evaluator directories
- Orchestrator logs/session analytics under orchestrator logging paths
- RL artifacts and training logs under `rl_agent/rl_runs/`

## Research Artifacts

**Human evaluation pipeline:** see `ablation/HUMAN_EVAL_README.md` for an interactive rater harness, synthetic-proxy generator for testing, averaging scripts, and analysis commands used to produce the figures in `ablation/results/`.

Draft manuscripts:

- `research/papers/paper_systems_agentic_architecture.md`
- `research/papers/paper_rl_adaptive_assessment.md`
- `research/papers/paper_aied_multiagent_feedback.md`

Capstone report:

- `research/capstone/PrepAIred_Capstone_Report_Phase2.md`

## Contributing

Contributions are welcome for research and engineering improvements.

1. Fork the repository.
2. Create a feature branch.
3. Keep changes focused and include tests where possible.
4. Run backend/frontend locally and verify no regressions.
5. Open a pull request with a clear summary and validation steps.

Suggested contribution areas:

- RL policy evaluation and ablations
- Evaluator quality and rubric alignment
- Frontend UX and accessibility
- Reliability, monitoring, and test coverage
- Documentation and reproducibility scripts

## Citation

If you use PrepAIred in academic work, cite it as:

```bibtex
@misc{prepaired2026,
	title        = {PrepAIred: Adaptive Interview Preparation with Multi-Agent Orchestration and RL-Guided Strategy},
	author       = {PrepAIred Project Team},
	year         = {2026},
	howpublished = {GitHub repository},
	note         = {Includes orchestrator architecture, evaluator pipeline, and adaptive interview loop}
}
```

## Known Improvement Areas

- Unify dependency entrypoints (root requirements path consistency)
- Add reproducible one-click setup scripts for all platforms
- Expand integration tests for service combinations and failure paths
- Add fairness and robustness benchmarking for audio-heavy scenarios
- Add formal experiment scripts for publication-ready reproducibility

## License

Add your preferred license file (for example MIT/Apache-2.0) if you plan to open-source publicly.
