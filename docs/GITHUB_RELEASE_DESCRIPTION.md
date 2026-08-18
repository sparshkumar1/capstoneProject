# Release Notes — PrepAIred v1.0 (Tag: `paper-v1.0`)

**Release Version:** `v1.0.0-frozen`
**Git Tag:** `paper-v1.0`
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md) (*IEEE Transactions on Learning Technologies Draft*)
**Master Manual & Viva Booklet:** [`docs/PREPAIRED_COMPLETE_BOOKLET.md`](PREPAIRED_COMPLETE_BOOKLET.md)
**Independent Tester Guide:** [`docs/FRIEND_REPRODUCTION_CHECKLIST.md`](FRIEND_REPRODUCTION_CHECKLIST.md)
**Repository Remote:** `https://github.com/sparshkumar1/capstoneProject.git`

---

## 🌟 Executive Overview

We are proud to announce the **v1.0 official release** of **PrepAIred**, an open-source, multimodal, closed-loop adaptive technical interview preparation platform.

This release provides the **frozen research artifact**, complete multi-agent production source code, test suites, and reproduction harnesses corresponding to the submitted IEEE TLT research manuscript.

---

## 🔬 Core Research & Engineering Highlights

1. **Calibrated Multi-Component Neural Evaluator ($S_1+S_2+R$):**
   - Combines Sentence-BERT surface semantics ($S_1$, $w=0.15$), FAISS dense concept retrieval ($S_2$, $w=0.35$), and Cross-Encoder joint reasoning entailment ($R$, $w=0.50$).
   - Features **reasoning-dependent anti-keyword dampening**: cuts concept credit by $40\%$ if reasoning $R \le 0.30$, eliminating keyword-gaming vulnerabilities.
   - Validated against 3 blinded human expert raters on 20 benchmark items (Spearman $\rho = \mathbf{0.8358}, p = \mathbf{4.46 \times 10^{-6}}$, Krippendorff's $\alpha = \mathbf{0.8255}$, $\text{MAE} = 0.2585$).

2. **Pedagogically Shielded PPO Difficulty Controller:**
   - On-policy Actor-Critic reinforcement learning agent operating over a continuous 6D candidate state space $\mathbf{s}_t = [\bar{s}_t, c_t, h_t, \tau_t, s_t, d_t] \in [0, 1]^6$.
   - Constrained by **6 deterministic safety guardrails** preventing difficulty oscillations and cognitive overload.
   - Demonstrated statistically significant adaptive progression ($\rho = +0.1572 \pm 0.08$) compared to fixed and heuristic baselines across 150 simulated candidate episodes.

3. **Dual Qwen LLM Architecture:**
   - **Research Benchmark (EXP-3):** `Qwen2.5-7B-Instruct` bfloat16 on NVIDIA Tesla T4 GPU (Grounding: $0.2496$, Gap Coverage: $72.5\%$, Latency: $9.78\text{s}$).
   - **Local CPU Live Demo:** `Qwen2.5-1.5B-Instruct-GGUF` (Q4_K_M) via `llama.cpp` on 12 CPU threads (Mean generation latency: **$2.195\text{s}$**, RSS RAM: **$1.36\text{ GB}$**).
   - **Deterministic Fallback:** Sub-50ms structured recovery when LLM is offline, with strict attribution tracking (`non_llm_structured_recovery`).

4. **Hardened Docker C Coding Sandbox:**
   - Ephemeral container isolation with Linux kernel `cgroups` (128MB RAM, 32 PIDs, 2.0s CPU timeout, `--net=none`, read-only root).

5. **Exhaustive Automated Verification:**
   - **177 backend tests passed** (1 skipped CUDA), **7 frontend tests passed**, **8 standalone evaluator tests passed**, and **480 / 480 pre-registered experimental trials verified**.

---

## 🚀 Quick Start in 60 Seconds

```bash
# 1. Clone the repository
git clone https://github.com/sparshkumar1/capstoneProject.git
cd capstoneProject

# 2. Setup Python environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows (or source .venv/bin/activate on Linux/macOS)
pip install -r requirements/base.txt -r requirements/evaluator.txt -r requirements/rl.txt
pip install -e .

# 3. Setup Frontend
npm --prefix apps/web install

# 4. Run Verification Suite
python -m pytest tests/ -v
npm --prefix apps/web test -- --run
python scripts/reproduce_paper.py
```

---

## 📌 Scientific Integrity & Invariants

- **Draft Manuscript Status:** The manuscript [`docs/paper_draft_ieee.md`](paper_draft_ieee.md) is an IEEE Transactions on Learning Technologies research draft. It is not yet peer-reviewed or accepted.
- **Simulation Boundary:** EXP 1, 4, and 5 utilize simulated candidate personas in Gymnasium environments to prove algorithmic convergence and stability. Longitudinal human learning gains represent documented future work.
- **Human Calibration:** Human ground-truth validation is grounded in the 20-item expert benchmark dataset ($n=140$ scorings, 3 blinded raters, $\alpha = 0.8255$).
- **External Third-Party Validation: PENDING:** The repository has been internally verified and a self-contained independent reproduction protocol has been prepared. Independent third-party reproduction has not yet been completed.
- **Privacy & Security:** Zero private credentials, zero candidate PII, and zero proprietary API dependencies are included in this release.
