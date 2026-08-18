# PrepAIred — A Personalized Adaptive Framework for Multimodal Technical Interview Assessment and Preparation

[![Research Manuscript](https://img.shields.io/badge/Manuscript-IEEE%20TLT%20Draft-blue.svg)](docs/paper_draft_ieee.md)
[![Master Booklet](https://img.shields.io/badge/Manual-Master%20Booklet-purple.svg)](docs/PREPAIRED_COMPLETE_BOOKLET.md)
[![Tester Guide](https://img.shields.io/badge/Reproduction-Friend%20Checklist-teal.svg)](docs/FRIEND_REPRODUCTION_CHECKLIST.md)
[![Traceability](https://img.shields.io/badge/Results-100%25%20Traceable-success.svg)](docs/PAPER_RESULTS_TRACEABILITY.md)
[![Tests](https://img.shields.io/badge/Tests-178%20Passed-brightgreen.svg)](docs/SYSTEM_TESTING.md)
[![Reproducibility](https://img.shields.io/badge/Reproducibility-Verified-orange.svg)](docs/REPRODUCIBILITY.md)
[![Release Tag: paper-v1.0](https://img.shields.io/badge/Release-paper--v1.0-blueviolet.svg)](docs/GITHUB_RELEASE_DESCRIPTION.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **PrepAIred** is an open-source, multimodal, closed-loop adaptive technical interview preparation platform. It combines speech prosody analysis, calibrated neural short-answer grading ($S_1+S_2+R$), containerized Docker C execution, and safety-guardrailed Proximal Policy Optimization (PPO) reinforcement learning for dynamic difficulty adaptation.

---

## 🏛️ System Architecture

![Figure 1: PrepAIred System Architecture](research/results/figures/figure1_system_architecture.png)

```
Candidate (Audio/Code/Text)
   │
   ├──► [1] Audio & Prosody Analysis (Whisper STT, Pacing, Hesitation ht, Confidence ct)
   │
   ├──► [2] Calibrated Neural Evaluator (S1 SBERT + S2 FAISS + R CrossEncoder Entailment)
   │          └─ Anti-Keyword Dampening: S2_eff = (S2 if R > 0.30 else 0.60 * S2)
   │
   ├──► [3] 6D Candidate State Vector: st = [s_avg, ct, ht, tau_t, st, dt] in [0, 1]^6
   │
   ├──► [4] Guardrailed PPO Difficulty Controller (PPO Policy + 6 Safety Guardrails)
   │          └─ Action: Delta d in {-1 (Easier), 0 (Same), +1 (Harder)}
   │
   ├──► [5] 3-Tier Question Selector & Personalization (0.0% Question Repetition)
   │
   ├──► [6] Hardened Docker C Coding Sandbox (128MB RAM, 32 PIDs, 2.0s, --net=none)
   │
   └──► [7] Formative Feedback & Targeted Probing (Local Qwen GGUF / Structured Fallback)
```

---

## 🔬 Key Research Findings (Pre-Registered $n=480$ Evaluations)

1. **Adaptive Difficulty Adaptation (EXP-1, $n=150$):** `[RESEARCH RESULT]`
   PPO with safety guardrails achieves statistically significant positive difficulty adaptation ($\rho = +0.1572 \pm 0.08$) relative to static fixed ($\rho = 0.0, p = 6.15 \times 10^{-4}$) and heuristic rule-based controllers ($\rho = -0.2572, p = 5.30 \times 10^{-8}$) in simulation.
2. **Neural Answer Evaluation (EXP-2, $n=140$):** `[RESEARCH RESULT / HUMAN VALIDATED]`
   The multi-component scoring pipeline ($S_1+S_2+R$) achieves strong rank correlation ($\rho = \mathbf{0.8358}, p = \mathbf{4.46 \times 10^{-6}}, \text{MAE} = 0.2585$) with blinded human expert ratings on a 20-sample benchmark (human inter-rater reliability Krippendorff's $\alpha = \mathbf{0.8255}$).
3. **Formative Feedback Trade-Offs (EXP-3, $n=60$):** `[RESEARCH RESULT]`
   Generative `Qwen2.5-7B-Instruct` (Tesla T4 GPU) exhibits higher transcript lexical grounding ($0.2496$ vs. $0.0383, p = 2.56 \times 10^{-3}$), while deterministic structured recovery guarantees strictly superior rubric gap coverage ($100.0\%$ vs. $72.5\%, p = 9.11 \times 10^{-4}$) at sub-50ms latency.
4. **Personalization & Deduplication (EXP-4, $n=60$):** `[RESEARCH RESULT]`
   3-level deduplication completely eliminates question repetition ($0.0\%$ vs. $6.0\%, p < 0.001$), producing distinct trajectory divergence ($d = 14.21$) between candidate ability profiles in simulation.
5. **System Behavioral Decoupling (EXP-5, $n=70$):** `[RESEARCH RESULT]`
   100% clean subsystem isolation confirmed across 7 leave-one-out conditions without cascading crashes.

*Scientific Boundary: Candidate longitudinal learning gains and whole-system hiring efficacy represent documented future longitudinal trials. External third-party reproduction is pending (independent reproduction protocol provided in docs/FRIEND_REPRODUCTION_CHECKLIST.md).*


---

## ⚡ Dual Configuration Architecture

```
================================================================================
CONFIG A: RESEARCH SCIENTIFIC EVIDENCE (EXP-3)
================================================================================
- Model: Qwen/Qwen2.5-7B-Instruct (bfloat16) on NVIDIA Tesla T4 GPU (CUDA 12.8)
- Measured Latency: 9.78s per turn (Grounding = 0.2496, Gap Coverage = 72.5%)
- Raw Artifacts: research/results/raw/experiment_3_qwen_raw.json
- Scope: Frozen scientific evidence supporting the manuscript.
================================================================================

================================================================================
CONFIG B: LIVE DEMO & CLASSROOM DEPLOYMENT (CPU-ONLY)
================================================================================
- Model: Qwen/Qwen2.5-1.5B-Instruct-GGUF (Q4_K_M, 1.06 GB)
- Runtime Engine: llama.cpp / llama-cpp-python (CPU-Only, 12 threads)
- Measured Latency: ~1.8s - 2.9s per task (Mean = 2.195s, 18.79 tok/s)
- Process RAM: ~1.36 GB RSS
- Fallback System: Sub-50ms deterministic rubric-grounded recovery
- Scope: High-speed local live demo without dedicated GPUs.
================================================================================
```

---

## 🚀 Quick Start — Reproduction & Local Demo

### 1. Clone & Configure Environment
```bash
# Clone the repository
git clone https://github.com/sparshkumar1/capstoneProject.git
cd capstoneProject

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows PowerShell (or source .venv/bin/activate on Linux/macOS)

# Install dependencies
pip install --upgrade pip
pip install -r requirements/base.txt -r requirements/evaluator.txt -r requirements/rl.txt
pip install -e .

# Install frontend dependencies
npm --prefix apps/web install
```

### 2. Run Automated Verification Suites
```bash
# Backend test suite (178 tests: 177 passed, 1 skipped CUDA)
python -m pytest tests/ -v

# Frontend component suite (7 passed)
npm --prefix apps/web test -- --run

# Deterministic Paper Reproduction Harness (480 / 480 verified)
python scripts/reproduce_paper.py
```

### 3. Launch Local Demo Services
```bash
# Terminal 1: Evaluator Microservice (Port 5000)
python services/evaluator/app.py

# Terminal 2: FastAPI Backend Server (Port 8000)
uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: React Web Client (Port 5173)
npm --prefix apps/web run dev
```
Open your browser at `http://localhost:5173` to start an interactive mock interview.

---

## 📚 Complete Project Documentation Index

- **Master Manual & Defense Guide:** [`docs/PREPAIRED_COMPLETE_BOOKLET.md`](docs/PREPAIRED_COMPLETE_BOOKLET.md) (Complete 31-section compendium)
- **Independent Tester Checklist:** [`docs/FRIEND_REPRODUCTION_CHECKLIST.md`](docs/FRIEND_REPRODUCTION_CHECKLIST.md) (Step-by-step external tester protocol)
- **IEEE Research Manuscript Draft:** [`docs/paper_draft_ieee.md`](docs/paper_draft_ieee.md) (29-section formal manuscript)
- **Results Traceability Matrix:** [`docs/PAPER_RESULTS_TRACEABILITY.md`](docs/PAPER_RESULTS_TRACEABILITY.md) (100% dataflow verification)
- **Claims Verification Matrix:** [`docs/CLAIMS_CHECK.md`](docs/CLAIMS_CHECK.md) (16-claim evidence ledger)
- **System Testing Compendium:** [`docs/SYSTEM_TESTING.md`](docs/SYSTEM_TESTING.md) (Full test inventory)
- **GitHub Release Notes:** [`docs/GITHUB_RELEASE_DESCRIPTION.md`](docs/GITHUB_RELEASE_DESCRIPTION.md) (`paper-v1.0`)
- **Repository Tree Inventory:** [`docs/FINAL_REPOSITORY_TREE.md`](docs/FINAL_REPOSITORY_TREE.md)

---

## 🛡️ Hardened Coding Sandbox Policy

Untrusted candidate C code executes in an isolated Docker container (`Dockerfile.sandbox`):
- **Memory:** $128\text{ MB}$ limit (`--memory=128m --memory-swap=128m`)
- **PIDs:** $32\text{ max}$ (`--pids-limit=32` to stop fork bombs)
- **Timeout:** $2.0\text{ seconds}$ CPU wall time
- **Network:** Completely disabled (`--net=none`)
- **Filesystem:** Read-only root with transient memory tmpfs

---

## 📜 Licenses

- **Platform Code:** MIT License ([LICENSE](LICENSE))
- **Qwen2.5-1.5B-Instruct-GGUF:** Apache-2.0 License
- **Qwen2.5-7B-Instruct:** Apache-2.0 License
- **Sentence-Transformers (MiniLM):** Apache-2.0 License

---

## 📖 Citation

```bibtex
@article{kumar2026prepaired,
  title={A Personalized Adaptive Framework for Multimodal Technical Interview Assessment and Preparation},
  author={Kumar, Sparsh and PrepAIred Research Group},
  journal={IEEE Transactions on Learning Technologies (Under Review)},
  year={2026}
}
```
