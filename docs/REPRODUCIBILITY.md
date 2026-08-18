# PrepAIred — Master Reproducibility Guide (Stage 23)

**Document ID:** `REPRODUCIBILITY-GUIDE-STG23`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Execution Date:** 2026-08-17

---

## 1. Executive Summary & Verification Rule

This guide provides deterministic, one-click reproduction instructions for all numerical findings, tables, figures, and statistical analyses presented in the IEEE research manuscript.

```
================================================================================
REPRODUCIBILITY SCOPE MATRIX
================================================================================
EXP-1 (Adaptive Difficulty Controller):  150 runs (3 controllers x 5 personas x 10 seeds)
EXP-2 (Evaluator Component Ablation):    140 scorings (7 configs x 20 items, 3 raters)
EXP-3 (Formative Feedback Benchmark):     60 evaluations (3 conditions x 20 items, Tesla T4)
EXP-4 (Personalization & Divergence):     60 sessions (3 selectors x 2 profiles x 10 seeds)
EXP-5 (Leave-One-Out System Ablation):    70 sessions (7 conditions x 10 seeds)
--------------------------------------------------------------------------------
TOTAL REPRODUCIBLE EVALUATIONS:          480 / 480 (100.0% MACHINE-READABLE)
================================================================================
```

---

## 2. One-Click Paper Reproduction Command

To reproduce all 480 pre-registered evaluations and regenerate Figures 1–8 at 300 DPI:

```bash
python scripts/reproduce_paper.py
```

*Expected Terminal Output:*
```
Generated: research/results/figures/figure1_system_architecture.png
Generated: research/results/figures/figure2_candidate_state_loop.png
Generated: research/results/figures/figure3_experimental_methodology.png
Generated: research/results/figures/figure4_adaptive_difficulty.png
Generated: research/results/figures/figure5_evaluator_ablation.png
Generated: research/results/figures/figure6_feedback_comparison.png
Generated: research/results/figures/figure7_personalization_divergence.png
Generated: research/results/figures/figure8_leave_one_out_ablation.png
All 8 figures generated successfully.
[PASS] All 480 pre-registered evaluations verified from frozen raw data.
```

---

## 3. Environment & Provenance Specifications

- **Python Version:** 3.12.7 (x86_64)
- **Key Libraries:** `torch==2.5.1`, `transformers==4.49.0`, `sentence-transformers==3.4.1`, `stable-baselines3==2.5.0`, `llama-cpp-python==0.3.35`, `faiss-cpu==1.10.0`
- **PPO Checkpoint:** `rl/checkpoints/seed_123/ppo_final.zip` (Trained policy weights)
- **Pre-Registered Random Seeds:** `seed_123`, `seed_456`, `seed_789`, `seed_101`, `seed_202`
- **Research GPU Environment:** Google Colab / Cloud NVIDIA Tesla T4 GPU (14.56 GB VRAM, CUDA 12.8, Driver 535.104.05)

---

## 4. Distinction Between Research Reproduction and Live Demo

```
================================================================================
REPRODUCTION VS. DEMO OPERATIONAL DEMARCATION
================================================================================
TRACK 1: SCIENTIFIC REPRODUCTION (EXP 1–5)
- Script: python scripts/reproduce_paper.py
- Input Data: research/results/raw/*.json (Immutable frozen datasets)
- Hardware: CPU sufficient for statistical analysis; Tesla T4 for EXP-3 GPU inference

TRACK 2: LIVE DEMONSTRATION DEPLOYMENT
- Startup: python services/qwen/app.py && python apps/backend/main.py
- Model: Qwen2.5-1.5B-Instruct-GGUF (Q4_K_M, 986 MB)
- Hardware: Consumer Laptop CPU (12 threads, ~1.36 GB RAM, no GPU required)
================================================================================
```
