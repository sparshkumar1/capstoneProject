# Comprehensive Manuscript Revision Report (v7 to v9 Candidate)
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `REVISION_REPORT.md`  
**Candidate Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Status:** Complete Audit of Structural, Typographical, and Scientific Changes

---

## 1. Revision Overview and Architectural Baseline

This report documents all structural, typographical, and scientific revisions implemented between the v7 multi-agent baseline (`paper/adcom2027_final/`) and the final v9 submission candidate (`paper/adcom2027_final_v9_candidate/`).

### Strict Governance Principles
- **Read-Only Preservation:** The earlier candidate directories (`paper/adcom2027/`, `paper/adcom2027_final/`, and `paper/adcom2027_final_v8_candidate/`) were treated as strictly immutable and read-only.
- **Zero Repository Mutation:** No git branches, commits, PRs, or remote pushes were executed.
- **Independent Verification:** All modifications were audited against raw execution artifacts in `research/multiagent/results/`, ensuring 100% data fidelity.

---

## 2. Summary of Key Modifications

| Category | Issue in Earlier Drafts | Resolution in v9 Candidate | Scientific Rationale |
|:---|:---|:---|:---|
| **Bibliography** | 18 references; missing classical fault-tolerance and security foundations. | Added Saltzer & Schroeder (1975) (`ss75`) and Avižienis et al. (2004) (`alrl04`), bringing total references to **exactly 20**. | Grounds bounded-authority and fault containment in established dependable computing literature. |
| **Table 1 Layout** | Exceeded `\textwidth` by 19.69 pt, overflowing right margin. Caption had broken hyphenation (`author-ity;`). | Re-engineered column widths to `1.5cm, 2.5cm, 2.3cm, 2.8cm, 2.0cm`. Cleaned caption whitespace. | Ensures strict Springer CCIS margin compliance and eliminates visual clutter. |
| **Table 5 Layout** | Column 2 caused underfull hbox (`badness 10000`) due to long unbroken strings (`authority_violation>0`). | Applied `>{\raggedright\arraybackslash}p{7.6cm}` to column 2 in `tables/xa_pred.tex` and `tables/xb_pred.tex`. | Prevents unsightly stretched word spacing and irregular justification. |
| **Page Budget** | Earlier draft fluctuated between 18 and 19 pages with float queue blockages. | Re-balanced float placements and section breaks, achieving **exactly 20 pages** (inclusive of all 20 references). | Maximizes allowable Springer CCIS space (20-page cap) without trailing orphan lines. |
| **Coaching Wording** | Earlier text implied Coaching Agent directly generates generative natural language. | Explicitly clarified that Coaching Agent outputs structured plans formatted by deterministic renderer `coaching_render.py`. | Prevents reviewers from misinterpreting deterministic rule templates as generative LLM hallucination risks. |
| **Statistical Rigor** | Earlier drafts relied solely on naive session-level bootstrap intervals. | Added cluster bootstrap (Field & Welsh 2007) and leave-one-cluster-out (LOCO) sensitivity analysis to Section 6. | Honestly accounts for intra-cluster correlation from reusing 8 candidate answer sets. |
| **Contradicted Results** | Predictions A9, A10, and B6 contradicted initial pre-registered expectations. | Unflinchingly presented contradicted outcomes in text and Table 5 with clear architectural explanations. | Preserves scientific integrity by refusing to cherry-pick or suppress unexpected empirical findings. |

---

## 3. Page-by-Page Visual Inspection Record (20 Pages)

All 20 pages were rendered to high-resolution raster images (150 DPI) via `pdftoppm` and visually inspected:

| Page | Primary Content | Layout & Typographical Quality | Status |
|:---:|:---|:---|:---:|
| **1** | Title, Blind Authors, Abstract, Keywords, Section 1 Intro | Clean layout; title and anonymous headers balanced; abstract justified; no hyphenation flaws. | PASS |
| **2** | Section 1 (cont.), Section 2 Related Work | Foundational citations (Wooldridge & Jennings, AutoGen, MetaGPT, MAST) properly placed; column widths balanced. | PASS |
| **3** | Section 2 (cont.), Section 3 Architecture, Section 3.1 | Evaluator formula ($0.15S_1{+}0.35S_2^{\mathrm{eff}}{+}0.50R$) cleanly rendered; PPO and guardrails integrated. | PASS |
| **4** | Table 1 (Authority Matrix), Section 3.2 Agents | Table 1 strictly within `\textwidth`; column borders aligned; caption hyphenation clean. | PASS |
| **5** | Section 3.2 (Strategy Agent, Coaching Agent), Section 3.3, Section 4 | Decision rules, heuristic parameters, and state versioning clearly formatted; Section 4 precedence clean. | PASS |
| **6** | Figure 1 (Architecture diagram), Figure 2 (Turn sequence) | Both TikZ diagrams sharply rendered; dashed vs solid arrows distinct; fills legible in greyscale/color. | PASS |
| **7** | Figure 3 (Validation pipeline diagram), Section 4 text, Section 5 | TikZ validation flow legible; Section 4 resumes seamlessly below Figure 3; Section 5 Methodology starts. | PASS |
| **8** | Table 2 (Fault Matrix), Section 5 (cont.) | Table 2 fits margins; fault categories, detection seams, responses, and limitations cleanly tabulated. | PASS |
| **9** | Section 5 (XA, XB, XC, Statistics) | Clear classification of REPLAY, FAULT-INJECTED, SOCKET, SYNTHETIC; cluster bootstrap description clear. | PASS |
| **10** | Table 3 (XA Summary), Pre-registered predictions, Section 6, 6.1 | Table 3 numbers aligned; Section 6 Results begins; claim numbers match raw artifacts. | PASS |
| **11** | Table 4 (XA Paired Differences), Section 6.1 text | Paired bootstrap intervals and p50 latency deltas aligned; leave-one-cluster-out discussion clear. | PASS |
| **12** | Table 5 (Registered Predictions & Outcomes: XA and XB) | Column 2 ragged-right formatting eliminates underfull hbox; prediction outcomes aligned. | PASS |
| **13** | Table 6 (XB Fault Containment), Section 6.2 text, Section 6.3 | Table 6 fits margins; containment metrics and Clopper-Pearson exact bounds intact. | PASS |
| **14** | Table 7 (XC Thresholds), Table 8 (XD Grounding), Section 6.4 | Clean presentation of threshold sensitivity ($\tau \in \{0.0 \dots 0.9\}$) and rebuilt lexical grounding audit. | PASS |
| **15** | Section 6.4 (cont.), Section 7 (Corrections to Earlier Audit / RQ4) | Discussion of 13/14 predictions, malformed score claim narrowing, and byte-reproducible historical baseline. | PASS |
| **16** | Section 8 Discussion (RQ1–RQ4) | Comprehensive answers to all 4 research questions grounded in empirical results. | PASS |
| **17** | Section 9 Limitations (Scope, Replay, Heuristics), Section 10 | Unflinching disclosure of synthetic data, lack of live human/LLM evaluation, and heuristic threshold tuning. | PASS |
| **18** | Section 9 (Coverage, Trust boundary, Deployment surface, Environment, Provenance) | Honest disclosure of 421 passing tests vs historical baseline; test regression bounds established. | PASS |
| **19** | Section 10 Conclusion, References (Items 1–11) | Conclusion concise; references begin cleanly in standard Springer `splncs04` format. | PASS |
| **20** | References (Items 12–20: sb3, ppo, chase, shield, autogen, zara, judge, ss75, alrl04) | References conclude cleanly at ~70% of page height; zero overflow; no orphan lines. | PASS |

---

## 4. Verification and Compliance Confirmation

1. **Claim Audit:** `verify_paper.py` executed via WSL Python 3.12 environment: **69/69 checks passed** (0 failures).
2. **Double-Blind Audit:** `blind_audit.py` executed: **0 deanonymizing hits** (no names, institutions, repository paths, or unblinded URLs).
3. **Font Embedding:** Audited via `pdffonts`: **0 un-embedded fonts** (100% embedded Type 1 / TrueType fonts).
4. **PDF Metrics:**
   - File Path: `paper/adcom2027_final_v9_candidate/manuscript/main.pdf`
   - File Size: 450,635 bytes
   - Total Pages: Exactly 20 pages
   - Dimensions: 612 $\times$ 792 pts (US Letter) — *Note on A4 conversion documented in Compliance Report.*
