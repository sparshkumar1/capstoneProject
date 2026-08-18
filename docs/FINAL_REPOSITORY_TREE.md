# PrepAIred — Actual Repository Tree & Directory Manifest (Stage 24.5)

**Document ID:** `FINAL-REPOSITORY-TREE-STG24-5`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Authoritative Defense Booklet:** [`docs/PREPAIRED_COMPLETE_BOOKLET.md`](PREPAIRED_COMPLETE_BOOKLET.md)
**Execution Date:** 2026-08-18

---

## 1. Top-Level Repository Structure

```
PrepAIred/
├── ablation/                  # Human evaluation calibration benchmark & Krippendorff alpha analysis
├── agents/                    # Multi-agent orchestrator, strategy, audio, timing, question selector
├── apps/
│   ├── backend/               # FastAPI REST and WebSocket API backend
│   └── web/                   # React 18 / Vite candidate frontend web client
├── data/
│   ├── questions/             # 125 curated technical interview questions (qns.json)
│   └── rubrics/               # 125 fine-grained evaluation rubrics (rubrics_final_clean.json)
├── docs/                      # Authoritative research paper, defense booklet, audits, traceability
├── experiments/               # Pre-registered experimental execution harnesses (EXP 1-5)
├── models/                    # Local GGUF model storage (excluded from git tracking)
├── research/
│   ├── results/               # Machine-readable raw JSON, processed CSVs, tables, and figures
│   ├── papers/                # Reference literature and prior conference drafts
│   └── capstone/              # Capstone proposal and project artifacts
├── rl/                        # Gymnasium environment, PPO training pipeline, and trained checkpoints
├── scripts/                   # One-click paper reproduction harness & environment setup scripts
├── services/                  # Standalone Evaluator and Qwen microservices
├── submission/                # Self-contained venue submission package (IEEE TLT)
├── tests/                     # Comprehensive regression unit and integration test suites
├── Dockerfile.sandbox         # Isolated C execution container definition
├── docker-compose.yml         # Multi-container orchestration specification
├── README.md                  # Master repository documentation & quick start guide
├── LICENSE                    # MIT open-source license
├── .env.example               # Clean environment configuration template
└── .gitignore                 # Binary and secret exclusion specifications
```

---

## 2. Directory Manifest & Classification

| Directory | Primary Domain | Purpose & Function | Important Files | Public Status |
|---|---|---|---|:---:|
| **`ablation/`** | Research & Human Eval | Contains the 20-sample human calibration benchmark, raw multi-rater scorings, and Krippendorff $\alpha$ calculation scripts. | `ablation_human_eval.py`, `results/ratings_3raters.json` | **PUBLIC** |
| **`agents/`** | Production Subsystems | Implements modular interview agents: audio analysis, coding sandbox execution, question deduplication, PPO strategy, timer, and interview orchestrator. | `agents/orchestrator/interview_orchestrator.py`, `agents/audio/transcriber.py`, `agents/strategy/hybrid_orchestrator.py` | **PUBLIC** |
| **`apps/backend/`**| Production Backend | FastAPI service managing WebSocket live interview sessions, turn orchestration, audio processing, and diagnostic reporting. | `apps/backend/main.py` | **PUBLIC** |
| **`apps/web/`** | Production Frontend | React 18 / Vite single-page application providing real-time audio capture, Monaco code editor, and diagnostic report visualizers. | `apps/web/src/InterviewRoom.jsx`, `apps/web/src/MonacoEditor.jsx`, `apps/web/src/Report.jsx` | **PUBLIC** |
| **`data/`** | Production & Research | Curated dataset of 125 technical CS questions and 125 fine-grained evaluation rubrics. | `data/questions/qns.json`, `data/rubrics/rubrics_final_clean.json` | **PUBLIC** |
| **`docs/`** | Documentation & Audits | Complete scientific manuscript (`paper_draft_ieee.md`), 34-part defense booklet (`PREPAIRED_COMPLETE_BOOKLET.md`), traceability matrices, and audit records. | `paper_draft_ieee.md`, `PREPAIRED_COMPLETE_BOOKLET.md`, `PAPER_RESULTS_TRACEABILITY.md` | **PUBLIC** |
| **`experiments/`** | Research Harnesses | Pre-registered experiment runners for EXP-1 (RL difficulty), EXP-2 (Evaluator ablation), EXP-3 (Feedback), EXP-4 (Personalization), and EXP-5 (System ablation). | `experiments/difficulty/run_exp1.py`, `experiments/evaluation/run_exp2.py`, etc. | **PUBLIC** |
| **`models/`** | Local Storage | Directory for local GGUF model weights (`qwen2.5-1.5b-instruct-q4_k_m.gguf`). | Excluded from version control via `.gitignore` | **LOCAL ONLY** |
| **`research/results/`**| Frozen Research Data | Immutable raw JSON logs ($n=480$), processed CSV summaries, LaTeX tables, and 8 publication figures at 300 DPI. | `raw/experiment_1_difficulty_raw.json` to `raw/experiment_5_ablation_raw.json`, `figures/` | **PUBLIC** |
| **`rl/`** | Production & Training | Gymnasium interview environment, PPO hyperparameter configs, retraining scripts, and trained policy weights. | `rl/env/interview_env.py`, `rl/checkpoints/seed_123/ppo_final.zip` | **PUBLIC** |
| **`scripts/`** | Reproducibility | Deterministic one-click paper reproduction script (`reproduce_paper.py`) and platform setup automation. | `scripts/reproduce_paper.py`, `scripts/setup_env.sh` | **PUBLIC** |
| **`services/`** | Microservices | Standalone Evaluator microservice (port 5000) and Qwen inference microservice (port 8001). | `services/evaluator/app.py`, `services/qwen/app.py` | **PUBLIC** |
| **`submission/`** | Venue Submission | Self-contained packaging bundle for IEEE Transactions on Learning Technologies (TLT). | `submission/manuscript/`, `submission/figures/`, `submission/supplementary/` | **PUBLIC** |
| **`tests/`** | Quality Assurance | 178 backend regression unit/integration tests and frontend component tests. | `tests/unit/`, `tests/integration/` | **PUBLIC** |
