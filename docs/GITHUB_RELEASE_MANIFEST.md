# PrepAIred — Master GitHub Release & Distribution Manifest (Stage 24)

**Release ID:** `PREPAIRED-RELEASE-MANIFEST-V1.0`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Submission Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Authoritative Defense Booklet:** [`docs/PREPAIRED_COMPLETE_BOOKLET.md`](PREPAIRED_COMPLETE_BOOKLET.md)
**Traceability Reference:** [`docs/PAPER_RESULTS_TRACEABILITY.md`](PAPER_RESULTS_TRACEABILITY.md)
**Execution Date:** 2026-08-17
**Recommended Release Tag:** `paper-v1.0`

---

## 1. Tracked Subsystems & Assets Inventory

| Component / Subsystem | Physical Path | Description / Scope | Version / Provenance |
|---|---|---|:---:|
| **Scientific Manuscript** | `docs/paper_draft_ieee.md` | Authoritative 29-section IEEE TLT manuscript | Frozen v1.0 |
| **Comprehensive Booklet** | `docs/PREPAIRED_COMPLETE_BOOKLET.md`| Master 34-part academic & viva defense guide | Final v1.0 |
| **Traceability Ledger** | `docs/PAPER_RESULTS_TRACEABILITY.md` | 100% dataflow verification matrix | 16/16 claims |
| **Claims Matrix** | `docs/CLAIMS_CHECK.md` | Evidence ledger for all scientific claims | 16/16 verified |
| **Master Documentation** | `README.md` | Public repository overview & quick start | 27 sections |
| **Backend API Service** | `apps/backend/` | FastAPI REST & WebSocket orchestrator | Python 3.12 |
| **Frontend Web Client** | `apps/web/` | React 18 / Vite interactive candidate UI | Node 18+ |
| **Evaluator Service** | `services/evaluator/app.py` | SBERT + FAISS + CrossEncoder scoring engine | Standalone port 5000 |
| **Qwen Microservice** | `services/qwen/app.py` | `llama-cpp-python` GGUF engine & fallback | Standalone port 8001 |
| **Docker C Sandbox** | `Dockerfile.sandbox`, `agents/coding_executor/` | GCC execution sandbox with cgroups isolation | 128MB RAM, 32 PIDs |
| **PPO Policy Checkpoint** | `rl/checkpoints/seed_123/ppo_final.zip` | Trained difficulty adaptation policy weights | Stable-Baselines3 |
| **Reproducibility Suite**| `scripts/reproduce_paper.py`, `docs/REPRODUCIBILITY.md`| One-click reproduction of all 480 runs | Deterministic |
| **Venue Submission Pkg** | `submission/` | Standalone bundle for IEEE TLT submission | Self-contained |
| **Regression Test Suite**| `tests/` | 178 backend and 7 frontend test files | 100% pass rate |

---

## 2. Excluded Binary & Large Model Artifacts

| Excluded Artifact | Disk Footprint | Exclusion Rule | Download Source & Setup Command |
|---|:---:|---|---|
| **Qwen2.5-1.5B-Instruct-GGUF (Q4_K_M)** | 986 MB | Excluded via `*.gguf` in `.gitignore` | `hf_hub_download(repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF", filename="qwen2.5-1.5b-instruct-q4_k_m.gguf", local_dir="models/gguf")` |
| **Qwen2.5-7B-Instruct (Full Weights)** | ~14.5 GB | Excluded via `models/` in `.gitignore` | Evaluated in cloud GPU research environment (`a09a35458c702b33eeacc393d103063234e8bc28`) |
| **WhisperX Model Checkpoints** | ~1.5 GB | Managed dynamically by `faster-whisper` | Cached locally in `~/.cache/huggingface/` |
| **Virtual Environments (`.venv/`)** | ~3.5 GB | Excluded via `.venv/` in `.gitignore` | Recreated via `pip install -r requirements.txt` |
| **Node Modules (`node_modules/`)** | ~250 MB | Excluded via `node_modules/` in `.gitignore`| Recreated via `cd apps/web && npm install` |

---

## 3. Security, License & Portability Verification

- **Security Scan:** 0 real secrets, 0 API keys, 0 private credentials, 0 candidate PII discovered.
- **Portability Scan:** 0 hardcoded machine-specific paths in production code; dynamic root pathing via `pathlib.Path(__file__).resolve().parent`.
- **Licensing Audit:**
  - Platform Source Code: MIT License ([`LICENSE`](../LICENSE))
  - Qwen2.5 Models (1.5B GGUF & 7B): Apache-2.0 License
  - Sentence-Transformers / MiniLM: Apache-2.0 License
  - PyTorch: BSD-3-Clause License
  - Stable-Baselines3: MIT License
  - Docker Engine: Apache-2.0 License

---

## 4. Master Reproduction & Verification Status

```
================================================================================
FINAL VERIFICATION STATUS SUMMARY
================================================================================
- Backend Unit & Integration Tests:     177 passed, 1 skipped (gated CUDA), 0 failed
- Frontend Component UI Tests:          7 passed, 0 failed
- Evaluator Standalone Verification:    8/8 passed
- Qwen 1.5B GGUF Integration Suite:     7/7 passed
- Production Multi-Turn E2E Run:        1 complete session passed
- Offline Speech Prosody Extraction:    Passed (speech 2.43s, hes 0.26, conf 0.81)
- Live Microphone Status:               NOT VERIFIED (No physical hardware in CLI)
- Master Paper Reproduction:            480/480 evaluations verified from raw data
================================================================================
```
