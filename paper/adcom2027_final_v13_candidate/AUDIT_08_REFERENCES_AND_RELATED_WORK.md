# Audit Deliverable 08: Literature and Citation Audit
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `AUDIT_08_REFERENCES_AND_RELATED_WORK.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Independent Scientific, Reproducibility, and Publication-Quality Reviewer  

---

## 1. Citation Inventory & Authoritative Verification

All 20 citations appearing in `manuscript/refs.bib` and cited within `main.tex` have been audited against authoritative bibliographic standards:

| # | BibTeX Key | Primary Authors | Year | Venue / Publisher | Topic Category | Verification Status |
|:---:|:---|:---|:---:|:---|:---|:---:|
| 1 | `wj95` | Wooldridge \& Jennings | 1995 | *Knowledge Engineering Review* | Multi-Agent Systems (Weak Agency definition) | **VERIFIED** |
| 2 | `mast` | Cemri et al. | 2025 | arXiv:2503.13657 (UC Berkeley) | LLM Multi-Agent System Failures | **VERIFIED** |
| 3 | `autogen` | Wu et al. | 2023 | arXiv:2308.08155 (Microsoft) | Multi-Agent Conversation Frameworks | **VERIFIED** |
| 4 | `metagpt` | Hong et al. | 2024 | ICLR 2024 | Collaborative Multi-Agent Frameworks | **VERIFIED** |
| 5 | `resil` | Huang et al. | 2025 | ICML 2025 (PMLR 267) | Multi-Agent Resilience & Faulty Agents | **VERIFIED** |
| 6 | `masfire` | Jia et al. | 2026 | arXiv:2602.19843 | Multi-Agent Reliability Evaluation | **VERIFIED** |
| 7 | `judge` | Zheng et al. | 2023 | NeurIPS 2023 (Datasets Track) | LLM-as-a-Judge Evaluation | **VERIFIED** |
| 8 | `ppo` | Schulman et al. | 2017 | arXiv:1707.06347 (OpenAI) | Proximal Policy Optimization | **VERIFIED** |
| 9 | `sb3` | Raffin et al. | 2021 | *Journal of Machine Learning Research* | Stable-Baselines3 RL Implementations | **VERIFIED** |
| 10 | `zara` | Yazdani et al. | 2025 | arXiv:2507.02869 | Automated Interview Feedback Systems | **VERIFIED** |
| 11 | `virt` | Gomez et al. | 2025 | ACM CSCW Companion '25 | AI Mock Interview Readiness | **VERIFIED** |
| 12 | `chase` | Vaishampayan \& Brown | 2025 | IEEE/ACM CHASE 2025 | Code Feedback Trust in Mock Interviews | **VERIFIED** |
| 13 | `nygard` | Nygard | 2007 | Pragmatic Bookshelf | Circuit Breaker & Software Stability | **VERIFIED** |
| 14 | `cp34` | Clopper \& Pearson | 1934 | *Biometrika* | Exact Binomial Confidence Intervals | **VERIFIED** |
| 15 | `shield` | Alshiekh et al. | 2018 | AAAI 2018 | Safe RL via Shielding / Guardrails | **VERIFIED** |
| 16 | `safe` | García \& Fernández | 2015 | *Journal of Machine Learning Research* | Safe Reinforcement Learning Survey | **VERIFIED** |
| 17 | `marl` | Bușoniu et al. | 2008 | IEEE TSMC-C | Multi-Agent Reinforcement Learning | **VERIFIED** |
| 18 | `fw07` | Field \& Welsh | 2007 | *JRSS Series B* (Statistical Methodology) | Clustered Data Bootstrapping | **VERIFIED** |
| 19 | `ss75` | Saltzer \& Schroeder | 1975 | *Proceedings of the IEEE* | Principle of Least Privilege | **VERIFIED** |
| 20 | `alrl04` | Avizienis et al. | 2004 | IEEE TDSC | Dependable & Secure Computing Taxonomy | **VERIFIED** |

---

## 2. In-Text Context & Citation Validity

Every in-text citation supports the factual statement for which it is invoked:
- `\cite{wj95}` is invoked to define *weak agency* (agents possessing private state, proactive proposals, and messaging, without claiming full autonomy).
- `\cite{ss75}` is invoked to justify the *principle of least privilege* in authority boundaries (agents possess propose-only rights; state writes remain exclusive to the hub).
- `\cite{fw07}` is invoked to justify the cluster-bootstrap resampling procedure, correcting for pseudoreplication across the 8 answer clusters.
- `\cite{nygard}` is invoked for the per-agent circuit breaker design pattern.
- `\cite{ppo,sb3}` are invoked for the frozen single-policy baseline.
- `\cite{shield,safe}` are invoked for the safety guardrail clamping layer.

Zero spurious, halluncinated, or non-existent papers are included in `refs.bib`.
All citations compile cleanly with numbered citations under Springer's `splncs04.bst`.
