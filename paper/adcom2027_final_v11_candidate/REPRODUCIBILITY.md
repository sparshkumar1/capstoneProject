# Independent Reproducibility and Audit Instructions
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `REPRODUCIBILITY.md`  
**Candidate Directory:** `paper/adcom2027_final_v11_candidate/`  
**Date:** 3 October 2026

---

## 1. System and Environment Requirements

All experiments, analyses, and manuscript builds can be reproduced on a standard Linux environment (or Windows Subsystem for Linux, Ubuntu 22.04 LTS):

- **Python Runtime:** Python 3.11 or 3.12
- **Core Dependencies:** `numpy`, `scipy`, `pandas`, `pydantic>=2.0`, `torch`, `stable-baselines3`, `gymnasium`, `pytest`
- **TeX Environment:** TeX Live with `latexmk`, `pdflatex`, and standard packages (`amsmath`, `amssymb`, `microtype`, `tikz`, `booktabs`)
- **Poppler Utilities:** `pdftotext`, `pdfinfo`, `pdffonts`
- **Hardware Requirements:** Standard multi-core x86_64 CPU; $\le 4$\,GB RAM; zero GPU acceleration required (all evaluations execute in deterministic mock evaluator mode).

---

## 2. One-Step Verification Commands

From the candidate directory (`paper/adcom2027_final_v11_candidate/`):

### 2.1 Automated Claim Verification (43/43 Checks)
Recomputes every quantitative claim directly from raw JSONL and CSV execution artifacts and verifies its exact presence in the compiled PDF text:
```bash
python verification/verify_paper.py
# Expected Output: claim audit: ALL 43/43 checks passed successfully!
```

### 2.2 Double-Blind Review Audit (0 Hits)
Scans LaTeX source files, bibliography, figures, tables, and compiled PDF text and metadata for deanonymizing identifiers:
```bash
python scripts/blind_audit.py ADCOM2027_PREPAIred_v11_specialization_blind.pdf
# Expected Output: blind audit: clean (0 hits)
```

### 2.3 Compiling the Manuscript PDF (Exactly 20 Pages)
Compiles the Springer CCIS LaTeX source tree:
```bash
cd manuscript
latexmk -pdf -interaction=nonstopmode main.tex
# Expected Output: Output written on main.pdf (20 pages).
```

---

## 3. Re-running Replay Experiments from Scratch

To regenerate the raw result artifacts from first principles:

### 3.1 Experiment XA (160 Replay Sessions per Condition)
```bash
export EVALUATOR_MOCK_MODE=1
python research/multiagent/experiments/xa_compare.py --out research/multiagent/results/xa
```
- Replays 64 recorded candidate answer payloads across 8 domains and 20 question orders (seeds 42--61).
- Execution time: $\approx 25$ seconds.

### 3.2 Experiment XC (Confidence Threshold Decomposition)
```bash
python research/multiagent/experiments/xc_threshold.py --out research/multiagent/results/xc
```
- Evaluates 6 threshold values ($\tau \in [0.0, 0.9]$) across 160 replay sessions.
- Execution time: $\approx 20$ seconds.

### 3.3 Post-Hoc Cluster Bootstrapping and LOCO Analysis
```bash
python research/multiagent/analysis/independent_check.py research/multiagent/results
python research/multiagent/analysis/leave_one_cluster_out.py
```
- Executes 10,000 cluster-bootstrap resamples (Field & Welsh 2007) and 8-way jackknife leave-one-cluster-out sensitivity analysis.

### 3.4 Recomputing the Guardrail Disagreement Grid
```bash
pytest tests/unit/test_guardrail_impl.py -v
# Pins the 4,728 of 39,930 (11.8%) disagreement points between inline and canonical guardrails.
```
