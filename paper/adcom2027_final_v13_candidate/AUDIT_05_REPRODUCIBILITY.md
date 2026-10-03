# Audit Deliverable 05: Independent Reproducibility Audit
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `AUDIT_05_REPRODUCIBILITY.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Independent Scientific, Reproducibility, and Publication-Quality Reviewer  

---

## 1. Reproduction Environment & System Dependencies

The empirical experiments, analysis scripts, and manuscript compilation were audited and reproduced under the following environment:

- **Host Operating System:** Windows 11 Enterprise (Build 26100) / WSL2 Ubuntu 22.04 LTS
- **Python Environments:**
  - Windows: Python 3.12.7 (`.\.venv\Scripts\python.exe`)
  - WSL: Python 3.12.3 (`/opt/py312/bin/python`)
- **Key Installed Packages:**
  - `pydantic`: 2.12.0
  - `numpy`: 1.26.4
  - `scipy`: 1.13.1
  - `pandas`: 2.2.2
  - `torch`: 2.4.1+cpu
  - `stable-baselines3`: 2.3.2
  - `pytest`: 9.0.3
- **TeX Live Compilation Toolchain:**
  - `pdfTeX`: 3.141592653-2.6-1.40.22 (TeX Live 2022/dev/Debian)
  - `latexmk`: Version 4.76
- **Poppler Diagnostic Utilities:** `pdftotext`, `pdfinfo`, `pdffonts` (Version 22.02.0)

---

## 2. Re-Execution & Verification Results

### 2.1 Multi-Agent Software Test Suite (18/18 Tests)
- **Command:** `.\.venv\Scripts\python.exe -m pytest paper\adcom2027_final_v13_candidate\tests\test_coordination_and_specialization.py -v`
- **Execution Time:** $0.28$\,s
- **Exit Status:** `0` (Success)
- **Result:** **18 passed, 0 failed, 0 skipped**.
- **Coverage:** Unit contracts, state ledgers, hint budgeting, arbitration logic, metamorphic determinism, $M_3$ trajectory invariance, and empirical specialization comparison.

### 2.2 Automated Quantitative Claim Audit (43/43 Checks)
- **Command:** `wsl /opt/py312/bin/python /mnt/c/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v13_candidate/verification/verify_paper.py`
- **Execution Time:** $2.1$\,s
- **Exit Status:** `0` (Success)
- **Result:** `claim audit: ALL 43/43 checks passed successfully!`
- **Evidence Verification:** Every point estimate, paired delta, confidence interval, and threshold value in the compiled candidate PDF matches the raw data files in `research/multiagent/results/`.

### 2.3 Double-Blind Review & Typography Audit
- **Command:** `wsl /opt/py312/bin/python /mnt/c/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v13_candidate/scripts/blind_audit.py /mnt/c/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v13_candidate/manuscript/main.pdf`
- **Execution Time:** $1.4$\,s
- **Exit Status:** `0` (Success)
- **Result:** `fonts not embedded: 0 | blind audit: clean (0 hits)`
- **Page Budget:** Exactly 20 pages; References end on Page 20 at ~55% vertical height with zero overflow.

---

## 3. End-to-End Experiment Regeneration Seams

Any independent researcher with access to the repository can regenerate the experimental data from raw inputs:

```bash
# 1. Regenerate Experiment XA (160 sessions per condition across 12 conditions)
export EVALUATOR_MOCK_MODE=1
python research/multiagent/experiments/xa_compare.py --out research/multiagent/results/xa

# 2. Regenerate Experiment XC (Threshold sensitivity across tau in [0.0, 0.9])
python research/multiagent/experiments/xc_threshold.py --out research/multiagent/results/xc

# 3. Regenerate Cluster Bootstrap & LOCO Analysis
python research/multiagent/analysis/independent_check.py research/multiagent/results
python research/multiagent/analysis/leave_one_cluster_out.py

# 4. Rebuild Springer CCIS Camera-Ready Manuscript
cd paper/adcom2027_final_v13_candidate/manuscript
latexmk -pdf -interaction=nonstopmode main.tex
```

All raw artifacts, JSONL session logs, and compiled tables are bit-for-bit reproducible under seeds 42–61.
