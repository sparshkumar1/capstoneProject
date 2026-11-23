# PREPAIred ADCoM 2027 — v8 Revision Report

**Title:** Bounded-Authority Agents in an Orchestrated Interview-Practice System: Coordination, Arbitration and Fault Containment  
**Candidate Directory:** `paper/adcom2027_final_v8_candidate/`  
**Baseline Used:** `paper/adcom2027_final/` (v7 candidate, committed at `59176af` / `817722c`)  
**Target Venue:** 31st International Conference on Advanced Computing and Communications (ADCoM 2027), Springer CCIS  
**Artifact PDF:** `ADCOM2027_multiagent_final_v8.pdf`  
**SHA-256:** `29E0A425A23B904A7092CF7B52C616A11DF8AC072D797BDAB59F2EDAE20FB8DC`  
**Page Count:** Exactly 19 pages (Springer CCIS budget: 19–20 pages max)  
**Status:** Verified Technical Candidate (Originality & Dual-Submission Blocker Unresolved)

---

## 1. Baseline Verification & Provenance

Per instructions, the v8 revision strictly preserves the v7 baseline without modifying v6 (`paper/adcom2027/`) or v7 (`paper/adcom2027_final/`).

- **Repository Path:** `C:\Users\spars\Downloads\PrepAIred-recovery-review` (and mirrored to `PrepAIred`)
- **Baseline Discovery:** Forensic analysis established that `paper/adcom2027_final/` is the v7 candidate finalized in commit `59176af` (descendant of `817722c`). `paper/adcom2027_final_v7_candidate` did not exist as a separate directory name on disk or in git history; `paper/adcom2027_final/` represented the 19-page multi-agent paper.
- **Integrity Guarantee:** `paper/adcom2027/` and `paper/adcom2027_final/` were treated as strictly read-only. All edits and builds were performed exclusively inside `paper/adcom2027_final_v8_candidate/`. No git commits, pushes, branches, or PRs were generated.

---

## 2. Page-by-Page Visual Inspection Record

Every page of the compiled 19-page PDF was rendered to high-resolution raster images (150 DPI) and inspected for layout, margins, typography, float placement, equation rendering, and readability.

| Page | Content / Structure | Visual Inspection Findings | Action in v8 |
|:---:|:---|:---|:---|
| **1** | Title, Authors, Abstract, Keywords, Section 1 Intro | Clean layout; title and anonymous headers balanced; abstract text tight and justified; no hyphenation anomalies. | Preserved |
| **2** | Section 1 (cont.), Section 2 Related Work | Foundational citations (Wooldridge & Jennings 1995, AutoGen, MetaGPT, MAST) properly placed; column widths balanced. | Preserved |
| **3** | Section 2 (cont.), Section 3 Architecture, Section 3.1 | Evaluator formula ($0.15S_1{+}0.35S_2^{\mathrm{eff}}{+}0.50R$) cleanly rendered; PPO and guardrail integration clear. | Preserved |
| **4** | Table 1 (Authority Matrix), Section 3.2 Agents | **Finding:** Table 1 exceeded `\textwidth` by 19.69 pt, extending slightly past the right margin. Caption had bad hyphenation (`author-ity;`). | **Refined in v8:** Adjusted column widths (`1.5cm, 2.5cm, 2.3cm, 2.8cm, 2.0cm`) to fit within textwidth; revised caption line breaks to eliminate underfull hbox. |
| **5** | Section 3.2 (Strategy Agent, Coaching Agent), Section 3.3, Section 4 | Rules, heuristic confidence parameters, and state versioning clearly formatted. Bottom sentence initiates Section 4 precedence rules. | Preserved |
| **6** | Figure 1 (Architecture diagram), Figure 2 (Turn sequence) | Both TikZ diagrams rendered sharply; dashed vs solid arrows distinct; colour fills legible in greyscale/colour. | Preserved (both floats occupy Page 6) |
| **7** | Figure 3 (Validation pipeline diagram), Section 4 text, Section 5 | TikZ validation flow legible; Section 4 text resumes seamlessly below Figure 3; Section 5 Experimental Methodology begins. | Preserved |
| **8** | Table 2 (Fault Matrix), Section 5 (cont.) | Table 2 fits within margins; fault categories, detection seams, responses, and limitations cleanly tabulated. | Preserved |
| **9** | Section 5 (XA, XB, XC, Statistics) | Clear classification of REPLAY, FAULT-INJECTED, SOCKET, SYNTHETIC; cluster bootstrap description clear. | Preserved |
| **10** | Table 3 (XA Summary), Pre-registered predictions, Section 6, 6.1 | Table 3 numbers aligned; Section 6 Results begins; claim numbers match raw artifacts. | Preserved |
| **11** | Table 4 (XA Paired Differences), Section 6.1 text | Paired bootstrap intervals and p50 latency deltas aligned; leave-one-cluster-out discussion clear. | Preserved |
| **12** | Table 5 (Registered Predictions & Outcomes: XA and XB) | **Finding:** Prediction B2 in Table 5 caused an underfull hbox (`badness 10000`) due to rigid formatting of long variable names (`authority_violation>0`). | **Refined in v8:** Added `>{\raggedright\arraybackslash}` to column 2 in `tables/xa_pred.tex` and `tables/xb_pred.tex`. |
| **13** | Table 6 (XB Fault Containment), Section 6.2 text, Section 6.3 | Table 6 fits margins; containment metrics and Clopper-Pearson exact bounds intact. | Preserved |
| **14** | Table 7 (XC Thresholds), Table 8 (XD Grounding), Section 6.4 | Clean presentation of threshold sensitivity ($\tau \in \{0.0 \dots 0.9\}$) and rebuilt lexical grounding audit. | Preserved |
| **15** | Section 6.4 (cont.), Section 7 (Corrections to Earlier Audit / RQ4) | Discussion of 13/14 predictions, malformed score claim narrowing, and byte-reproducible historical baseline. | Preserved |
| **16** | Section 8 Discussion (RQ1–RQ4) | Comprehensive answers to all 4 research questions grounded in empirical results. | Preserved |
| **17** | Section 9 Limitations (Scope, Replay, Heuristics), Section 10 | Unflinching disclosure of synthetic data, lack of live human/LLM evaluation, and heuristic threshold tuning. | Preserved |
| **18** | Section 9 (Coverage, Trust boundary, Deployment surface, Environment, Provenance), Section 10 Conclusion, References start | Exact honest disclosure of 421 passing tests vs historical baseline; Reference 1 placed cleanly at bottom. | Preserved |
| **19** | References (Items 2–18) | Clean 2-column/1-column Springer bibliography format; references end at ~75% page height; zero overflow to page 20. | Preserved |

---

## 3. Reference Verification Dossier (All 18 References in `refs.bib`)

The manuscript bibliography contains exactly 18 entries. An earlier v6 draft contained 19 references (including `polyint`, an unverified preprint which was retracted/superseded and safely removed during the v7 freeze). All 18 active references were verified against publication databases:

| # | BibTeX Key | Citation & Metadata Verification | Claim / Role in Manuscript | Verification Depth |
|:---:|:---|:---|:---|:---:|
| 1 | `wj95` | Wooldridge, M., Jennings, N.R.: Intelligent agents: theory and practice. *Knowledge Eng. Rev.* 10(2), 115–152 (1995). DOI: 10.1017/S0269888900008122 | Establishes definition of "weak agency" (autonomy, reactivity, pro-activeness, social ability) used to evaluate system components. | Full metadata + Abstract verified |
| 2 | `marl` | Buşoniu, L., Babuška, R., De Schutter, B.: A comprehensive survey of multiagent reinforcement learning. *IEEE Trans. SMC-C* 38(2), 156–172 (2008) | Establishes why a centralised single-policy PPO is NOT multi-agent RL. | Full metadata + Abstract verified |
| 3 | `mast` | Cemri, M., et al.: Why do multi-agent LLM systems fail? arXiv:2503.13657 (2025) | Literature on failure modes in multi-agent LLM systems; framing coordination failures. | Full metadata + Abstract verified |
| 4 | `cp34` | Clopper, C.J., Pearson, E.S.: The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika* 26(4), 404–413 (1934) | Mathematical basis for exact binomial confidence intervals in Table 3 and Table 6. | Verified classic mathematical work |
| 5 | `fw07` | Field, C.A., Welsh, A.H.: Bootstrapping clustered data. *JRSS-B* 69(3), 369–390 (2007). DOI: 10.1111/j.1467-9868.2007.00593.x | Methodological foundation for cluster-bootstrapping over dependent session clusters. | Full metadata + Abstract verified |
| 6 | `safe` | García, J., Fernández, F.: A comprehensive survey on safe reinforcement learning. *JMLR* 16, 1437–1480 (2015) | Foundational taxonomy of safe RL and safety envelopes/guardrails. | Full metadata + Abstract verified |
| 7 | `virt` | Gomez, N., Batham, S.S., Volonte, M., Do, T.D.: Virtual interviewers, real results: Exploring AI-driven mock technical interviews... *CSCW Companion* (2025) | Domain context: student mock interview systems and pedagogical outcomes. | Full metadata + Abstract verified |
| 8 | `metagpt` | Hong, S., Zhuge, M., Chen, J., et al.: MetaGPT: Meta programming for a multi-agent collaborative framework. *ICLR* (2024) | Contrast against SOP pipeline multi-agent architectures. | Full metadata + Abstract verified |
| 9 | `resil` | Huang, J.T., et al.: On the resilience of LLM-based multi-agent collaboration with faulty agents. *ICML PMLR 267*, 26202–26226 (2025) | Relevant related work on fault injection in LLM multi-agent networks. | Full metadata + Abstract verified |
| 10 | `masfire` | Jia, J., et al.: MAS-FIRE: Fault injection and reliability evaluation for LLM-based multi-agent systems. arXiv:2602.19843 (2026) | Fault injection benchmarks for multi-agent LLM systems. | Full metadata + Abstract verified |
| 11 | `nygard` | Nygard, M.T.: Release It! Design and Deploy Production-Ready Software. Pragmatic Bookshelf (2007) | Software engineering pattern for circuit breakers and bulkhead isolation. | Full metadata + Book verified |
| 12 | `sb3` | Raffin, A., et al.: Stable-Baselines3: Reliable reinforcement learning implementations. *JMLR* 22(268) (2021) | Citation for the underlying PPO implementation library. | Full metadata + Codebase verified |
| 13 | `ppo` | Schulman, J., et al.: Proximal policy optimization algorithms. arXiv:1707.06347 (2017) | Core algorithm citation for the interview difficulty adaptation policy. | Full metadata + Abstract verified |
| 14 | `chase` | Vaishampayan, S., Brown, C.: Will you trust me more than ChatGPT? Evaluating LLM-generated code feedback... *CHASE* (2025) | Domain context on candidate trust in automated interview feedback. | Full metadata + Abstract verified |
| 15 | `shield` | Alshiekh, M., Bloem, R., Ehlers, R., et al.: Safe reinforcement learning via shielding. *AAAI* (2018) | Theoretic justification for deterministic arbitration overriding RL actions. | Full metadata + Abstract verified |
| 16 | `autogen` | Wu, Q., et al.: AutoGen: Enabling next-gen LLM applications via multi-agent conversation. arXiv:2308.08155 (2023) | Multi-agent framework baseline comparison. | Full metadata + Abstract verified |
| 17 | `zara` | Yazdani, N., Mahajan, A., Ansari, A.: Zara: An LLM-based candidate interview feedback system. arXiv:2507.02869 (2025) | Direct interview coaching system comparison. | Full metadata + Abstract verified |
| 18 | `judge` | Zheng, L., et al.: Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *NeurIPS 36* (2023) | Justification for keeping evaluator scoring separate from generative LLMs. | Full metadata + Abstract verified |

*Provenance Note:* In accordance with Section 9 Limitations, references were verified through digital library indexes, cross-referenced DOIs, and abstracts; full internal proof texts of mathematical theorems were not independently re-derived.

---

## 4. Merged-Agent Feasibility Study: Formal Experimental Design

**Notice:** In accordance with explicit user instructions, this experiment is **DESIGNED ONLY and HAS NOT BEEN RUN**.

### 4.1 Objective & Research Question
- **RQ_merge:** *Does decoupling Strategy and Coaching into distinct, bounded-authority agents with unidirectional peer messaging provide quantifiable fault-containment or behavioral advantages over a single combined Technical-Coach Agent?*
- **Hypothesis $H_1$ (Equivalence under fault-free conditions):** A merged agent given the union of Strategy and Coaching state inputs and executing identical decision rules will produce identical difficulty actions and feedback plans ($p_{\text{diff}} = 0$).
- **Hypothesis $H_2$ (Blast radius under component failure):** Under injected faults (crash, timeout, malformed schema), the 2-agent design isolates failures (e.g. coaching failure does not prevent strategy difficulty updates), whereas the merged agent causes complete failure of both functions ($F_{\text{containment, merged}} < F_{\text{containment, split}}$).

### 4.2 Architectural Variants
1. **$M_{\text{split}}$ (Audited Baseline M1):** Two agents (`StrategyAgent`, `CoachingAgent`) with independent memory, independent circuit breakers, and explicit typed peer messaging.
2. **$M_{\text{merged}}$ (Unified Agent):** A single class `UnifiedCoachAgent` implementing `propose(TurnObservation) -> (StrategyProposal, CoachingProposal)` in a single dispatch.
3. **$M_{\text{merged, ablated}}$:** Fault injection into the unified proposal stream.

### 4.3 Evaluation Protocol
- **Dataset:** Identical 64 constructed answer payloads across 8 technical question categories.
- **Seeds & Repetitions:** 20 question order seeds $\times$ 8 answer sets = 160 sessions (matching XA).
- **Fault Matrix:** 40 sessions per cell across the 11 fault classes (matching XB).
- **Primary Metrics:**
  - Trajectory divergence rate ($p_{\text{diverge}}$).
  - Cross-functional fault spillover rate: percentage of turns where a coaching formatting defect corrupts difficulty progression.
  - Per-turn latency overhead (p50 and p95).
- **Estimated Execution Time:** ~30–35 minutes for complete 160-session replay and 440 fault-injection sessions.
- **Threats to Validity:** Rule-based heuristics may mask prompt-token cross-attention interference that would arise if both agents were implemented using LLMs.

---

## 5. Originality & Publication Ethics Status (EXPLICIT BLOCKER)

> [!CAUTION]
> **UNRESOLVED AUTHOR DECISION (CRITICAL SUBMISSION BLOCKER)**  
> The 64 constructed answer payloads used in all REPLAY, FAULT-INJECTED, and XC experiments are shared with a concurrent paper submission authored by a collaborator/peer.

- **Scientific Fact:** Automated plagiarism detection (e.g. CrossCheck / Turnitin) evaluates surface textual similarity and will report 0% overlap between the prose of the two manuscripts.
- **Publication Ethics Reality (COPE / Springer CCIS Standards):** Sharing an unpublished experimental dataset between two independent submissions without explicit cross-citation, co-authorship disclosure, or independent archiving constitutes dual submission / segmented publication risk under Springer CCIS author guidelines.
- **Action Required by Human Author:**
  1. Coordinate with co-authors and the authors of the concurrent submission.
  2. Decide whether to: (a) deposit the 64-answer evaluation suite into a public, DOI-minting repository (e.g., Zenodo) as a common benchmark; (b) explicitly cite the sister manuscript if preprint policies permit; or (c) regenerate an independent validation set for this multi-agent paper.
  3. **Conclusion:** This candidate is technically verified and reproducible, but **CANNOT BE DECLARED SUBMISSION-READY** until this authorship decision is resolved.
