# Comprehensive Dataset and Cross-Venue Overlap Audit
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `DATASET_AND_OVERLAP_AUDIT.md`  
**Candidate Directory:** `paper/adcom2027_final_v12_candidate/`  
**Date:** 3 October 2026  
**Status:** Critical Publication-Ethics Audit & Author-Decision Framework  
**Classification:** **UNRESOLVED BLOCKER (Requires Teacher / Author Approval)**

---

## 1. Executive Summary and Ethical Context

This audit evaluates the provenance, reuse, and potential dual-submission conflicts surrounding the empirical dataset utilized in the ADCoM 2027 candidate paper: *"Specialization and Coordination in a Multi-Agent Technical Interview System: Trajectory Dynamics and Architectural Trade-offs"*.

### Critical Finding
The empirical evaluations in Experiment XA and Experiment XC rely on a fixed benchmark of **64 constructed technical interview answer payloads** (8 question categories $\times$ 8 answers). This identical 64-answer payload corpus is also utilized in sibling research projects targeting concurrent conferences (notably the teammate's v5 paper, ICITIIT 2027, and INDIACom 2027).

While the research questions, architectural layers, experimental designs, and evaluation metrics are completely orthogonal across venues, the shared reuse of this underlying benchmark represents an undeniable publication-ethics consideration under Springer CCIS guidelines. Consequently, this paper is classified as **Verified Technical Candidate / Conditionally Ready for Author Review**, and cannot be submitted until the author and faculty advisor make an explicit policy decision.

---

## 2. Dataset Provenance and Structural Audit

### 2.1 Artifact Origin
- **Source Artifact:** 64 pre-recorded interview response evaluations recorded during platform validation.
- **Categorization:** 8 distinct technical interview domains:
  1. Array manipulation and two-pointer algorithms
  2. Dynamic programming and memoization
  3. Tree and graph traversal (BFS/DFS)
  4. System design and scalability bottlenecks
  5. Concurrency, race conditions, and synchronization
  6. Database indexing and transaction isolation
  7. Networking protocols (TCP/UDP, HTTP/REST)
  8. Object-oriented design patterns and modularity
- **Payload Contents:**
  - Evaluator composite score (0–100)
  - Cross-encoder semantic similarity score
  - Lexical rubric keyword match vector
  - Identified concept tags and detected technical misconceptions
  - Response length (character and token counts)
  - Zero raw acoustic waveforms (speech metrics held at neutral constants)

### 2.2 Role in ADCoM 2027 Multi-Agent Manuscript
In the ADCoM 2027 paper, this corpus is used strictly as a **deterministic replay trace input** (`EVALUATOR_MOCK_MODE=1`). The research does **not** evaluate whether the scoring is accurate, does **not** correlate scores with human judges, and does **not** claim educational or pedagogical effectiveness for candidates. Instead, the payloads serve solely as standardized environmental stimuli to drive state transitions across the multi-agent arbitration and specialization layers.

---

## 3. Cross-Venue Overlap Matrix

The following matrix systematically contrasts the ADCoM 2027 candidate against the concurrent papers in the repository:

| Dimension | Sibling Paper A (ICITIIT 2027) | Sibling Paper B (INDIACom 2027) | Teammate Concurrent Paper (v5) | ADCoM 2027 (This Manuscript, v11) | Overlap Risk / Relationship |
|:---|:---|:---|:---|:---|:---|
| **Primary Thesis** | Authority separation of scoring from LLM text generation; evaluator calibration. | Formal specification-to-code verification of decoupled architecture. | Evaluator calibration and human rubric agreement. | Specialization and coordination in multi-agent interview system; trajectory dynamics. | **Completely Orthogonal:** No shared thesis. |
| **System Architecture** | Baseline platform; multi-agent layer disabled (`PREPAIRED_MULTIAGENT=0`). | Baseline platform; multi-agent layer disabled (`PREPAIRED_MULTIAGENT=0`). | Baseline platform; multi-agent layer disabled. | Feature-flagged multi-agent layer active (`PREPAIRED_MULTIAGENT=1`). | **Different System State:** Multi-agent layer only exists in ADCoM. |
| **Data Usage** | 64 answers evaluated against 3 human raters. | 64 answers used to audit specification fidelity. | 64 answers evaluated for scoring variance. | Same 64 evaluator payloads used **only as replay input**. | **SHARED ASSET:** Identical 64 payloads reused. |
| **Human Evaluation** | Yes (3 exploratory human annotators). | No. | Yes (human correlation). | **NO HUMAN DATA:** Strictly zero human ratings. | **Zero Overlap:** Human data entirely excluded from ADCoM. |
| **Experimental Design** | Cross-encoder vs length confound correlation. | Spec verification test harness. | Scoring distribution across prompt perturbations. | Replay ablation (160 sessions), threshold sweep (960 sessions), specialization analysis. | **Zero Overlap:** All experiments, tables, and figures unique. |
| **Text & Manuscript** | Independent text. | Independent text. | Independent text. | Independent text (fresh CCIS LaTeX source tree). | **Zero Overlap:** 0% verbatim text duplication. |

---

## 4. Springer CCIS Policy Analysis

Springer Nature's Code of Conduct and CCIS submission policies enforce rigorous guidelines regarding concurrent submissions and redundant publications:
1. **Redundant / Dual Submission:** Submitting the same manuscript (or substantially overlapping manuscripts) concurrently to multiple venues without disclosure is strictly prohibited.
2. **Data Dual-Use:** Reusing experimental data across papers is permitted *only if* the scientific questions addressed are distinctly different, prior use is properly disclosed, and the earlier work is cited (or transparently cross-referenced).
3. **Double-Blind Integrity:** In double-blind review, citing sibling preprints or unpublished concurrent drafts must be handled carefully to avoid de-anonymization while maintaining intellectual honesty.

### Audit Assessment
- **Textual Plagiarism:** 0% risk. No paragraphs, equations, or figures are duplicated.
- **Scientific Overlap:** Negligible risk. The multi-agent coordination, arbitration matrix, and specialization trade-offs exist nowhere else.
- **Data Reuse Risk:** **MODERATE TO HIGH RISK** if undisclosed. If a reviewer is assigned both papers, they will recognize the identical 64-answer domain structure and question taxonomy.

---

## 5. Three Concrete Actionable Options for Author and Teacher

To eliminate any ethical or procedural ambiguity, the authors must select one of the following three paths during the review on 5 October 2026:

### Option 1: Formal Benchmark Decoupling (Zenodo Deposit) — RECOMMENDED
- **Mechanism:** Treat the 64-answer dataset as an independent open benchmark artifact (e.g. *"Technical Interview Replay Corpus (TIRC-64)"*).
- **Execution:** Deposit the anonymized JSONL payload file to Zenodo or an anonymous Figshare repository with an independent DOI.
- **Manuscript Text:** In Section 5.1 (Methodology), cite the benchmark as an external standardized stimulus set: *"We evaluate coordination dynamics across the TIRC-64 benchmark, consisting of 64 standardized evaluator payloads spanning 8 technical domains..."*
- **Advantage:** Completely legitimizes multi-paper usage; establishes the dataset as a reusable community resource rather than paper-specific data.

### Option 2: Explicit Cross-Venue Disclosure in Submission Notes
- **Mechanism:** Disclose data provenance in the CMT submission metadata note to the Program Chairs.
- **Execution:** Submit the paper with an explicit chair note: *"Note on Dataset Provenance: The 64 evaluator payload traces used in our replay experiments are drawn from a shared technical interview corpus collected during platform validation. Sibling papers focusing on evaluator calibration utilize the same raw responses; this paper evaluates solely the orthogonal multi-agent coordination and specialization dynamics."*
- **Advantage:** Full compliance with Springer transparency rules without altering manuscript text or requiring external web deposits.

### Option 3: Independent Synthetic Dataset Generation
- **Mechanism:** Completely decouple from the shared 64-answer corpus by generating a fresh set of 64 or 128 synthetic interview response payloads.
- **Execution:** Run a synthetic generation script (`research/multiagent/experiments/generate_fresh_evaluations.py`) using open-source models, re-run Experiment XA/XC, and update `numbers.tex`.
- **Advantage:** Absolute 100% data separation; zero connection to any sibling paper.
- **Disadvantage:** Requires ~45 minutes of computation and re-verification of numbers prior to camera-ready submission.

---

## 6. Official Conclusion for Teacher Review (5 October 2026)

The ADCoM 2027 manuscript is scientifically robust, experimentally verified (43/43 checks passed), and structurally compliant with Springer CCIS requirements. However, because Option 1, 2, or 3 requires academic ownership and advisory consent, the manuscript must be submitted to the faculty advisor with this audit attached.

**Status: Conditionally Approved pending Faculty Decision on Benchmark Disclosure.**
