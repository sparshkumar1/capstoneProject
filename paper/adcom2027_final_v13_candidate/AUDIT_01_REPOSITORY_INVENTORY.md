# Audit Deliverable 01: Repository and Artifact Inventory
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `AUDIT_01_REPOSITORY_INVENTORY.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Independent Scientific, Reproducibility, and Publication-Quality Reviewer  

---

## 1. Repository Context & Version Control State

- **Repository Root:** `C:\Users\spars\Downloads\PrepAIred`
- **Active Git Branch:** `audit/claude-research-baseline`
- **HEAD Commit Hash:** `cb888f28ee57a4d14c966307020ed039d8dbfd9b`
- **HEAD Commit Date:** Thu Oct 1 17:43:19 2026 +0530
- **HEAD Commit Author:** `sparshkumar1`
- **HEAD Commit Subject:** `docs(research): verified research and manuscript audit baseline`
- **Working-Tree Status:** Clean for tracked repository files. All audit additions, candidate revisions, and test suites are strictly isolated within untracked candidate directories (`paper/adcom2027_final_v13_candidate/`) and mirrored in `..\PrepAIred-recovery-review\`. Zero git commits, branch mutations, or push operations have been performed.

---

## 2. Core Artifact Inventory

| Artifact | Actual Location | Version / Date | Status | Evidence (Hash / File Metrics) |
|:---|:---|:---:|:---:|:---|
| **Manuscript PDF** | `paper/adcom2027_final_v13_candidate/ADCOM2027_PREPAIred_v13_specialization_blind.pdf` | v13 Blind / 2026-10-03 | **AUTHORITATIVE** | 515,536 bytes; Exactly 20 pages; SHA-256: `925D88BD6D3EAF8C46DEB9BA949A7648BD6AA6F11261E852C8E2F7D5D0F08353` |
| **LaTeX Source Tree** | `paper/adcom2027_final_v13_candidate/manuscript/` (`main.tex`, `sec_*.tex`, `numbers.tex`, `refs.bib`) | v13 Source / 2026-10-03 | **AUTHORITATIVE** | `main.tex` SHA-256: `3A19F8C7E398343006BD9A0ED6F8288F59D6B6ED7DBD693205C370803E947158`; compiles via `latexmk -pdf` (pdfTeX-1.40.22) with 0 errors |
| **Experiment XA Results** | `research/multiagent/results/xa/` (`xa_runs.jsonl`, `xa_summary.csv`, `xa_paired.csv`, `xa_predictions.csv`, `xa_meta.json`) | 2026-10-02 | **AUTHORITATIVE** | 160 deterministic replay runs per condition (8 clusters × 20 seeds); `xa_summary.csv` SHA-256: `2C9C21588F2705351A3ED29B300F020875482596606B723137BBB55655D68607` |
| **Experiment XC Results** | `research/multiagent/results/xc/` (`xc_runs.jsonl`, `xc_summary.csv`, `xc_predictions.csv`, `xc_meta.json`) | 2026-10-02 | **AUTHORITATIVE** | 960 runs (6 thresholds $\tau \in [0.0, 0.9]$ × 160 runs); `xc_summary.csv` SHA-256: `257C3387E5F69B1A018F0EA52A6727693C438DF788EDE3BCFC5E844167AD62B4` |
| **Experiment XM (Merged Agent)** | Pre-registered: `paper/adcom2027_final_v13_candidate/MERGED_AGENT_EXPERIMENT.md`; Implemented in `tests/test_coordination_and_specialization.py` | 2026-10-03 | **PARTIALLY VERIFIED / UNEXECUTED AS STANDALONE** | Standalone code file `agents/multiagent/unified_agent.py` does not exist in repo. Comparison verified empirically via Condition $M_3$ trajectory invariance ($160/160$ sessions identical) and metamorphic test suite ($\mathbb{P}=1.0$, serialization overhead) |
| **Evaluation Dataset** | 64 recorded answer payloads across 8 clusters used in `research/multiagent/experiments/xa_compare.py` | 2026-09-30 | **DOCUMENTED / CONDITIONAL** | Recorded evaluator JSON responses across 8 CS domains; shared with sibling papers; documented in `DATASET_AND_OVERLAP_AUDIT.md` |
| **Test Suite** | `paper/adcom2027_final_v13_candidate/tests/test_coordination_and_specialization.py` and `tests/` | 2026-10-03 | **VERIFIED** | 18/18 passing in 0.28s; SHA-256: `DA74995BBC96BA7E0FDF1BF4AD3350BF8C8F20599070EF24E50ADF6D3CF8373F`; Unit, integration, ledger, arbitration, invariant, and specialization tests |
| **Figures & Tables** | `manuscript/sec_arch.tex` (TikZ Figs 1–3), `tables/` (`authority.tex`, `xa_summary.tex`, `xa_paired.tex`, `xa_pred.tex`, `xc.tex`, `specialization.tex`) | 2026-10-03 | **AUTHORITATIVE** | All 6 tables and 3 vector TikZ figures generated, embedded, and compiling within exact 20-page budget |
| **Post-Hoc Statistics** | `research/multiagent/results/post_hoc/` (`cluster_bootstrap.json`, `leave_one_cluster_out.json`, `strategy_confidence_distribution.json`) | 2026-10-02 | **AUTHORITATIVE** | Field & Welsh 10,000 cluster bootstrap resamples; 8-way LOCO jackknife analysis; `cluster_bootstrap.json` SHA-256: `BBC615BE0A61BCBD41F7E93DE4CCF744B4A596128B80871260510B693C15E514` |

---

## 3. Obsolete / Legacy Artifact Inventory (Historical Context)

The following artifacts belong to prior research scopes (Experiment XB synthetic fault injection, Experiment XD semantic grounding, Experiment XE historical bug regressions) and have been deprecated or excised from the ADCoM 2027 camera-ready narrative:

| Obsolete Artifact | Location | Original Role | Reason for Deprecation |
|:---|:---|:---|:---|
| `research/multiagent/experiments/xb_faults.py` | `research/multiagent/experiments/` | 1,760 synthetic fault injections across 11 fault classes | Fault injection and fault tolerance excised from ADCoM Track 2 research narrative |
| `research/multiagent/results/xb/` | `research/multiagent/results/xb/` | Raw data for Table 6 fault containment matrix | Preserved on disk for historical provenance; not cited in v13 main text |
| `research/multiagent/experiments/xe_historical.py` | `research/multiagent/experiments/` | Reproduction of E1/E5 historical bug regressions | Single-agent software post-mortems deprecated from 20-page camera-ready manuscript |
| `paper/adcom2027_final_v13_candidate/manuscript/sec_carry.tex` | `paper/adcom2027_final_v13_candidate/manuscript/` | Legacy Section 7 detailing historical E1/E5 bug audits | Excised from `main.tex`; replaced by dedicated Agent Specialization section |
