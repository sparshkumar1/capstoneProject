# Faculty Advisor Decision Memo: Dataset Provenance, Cross-Venue Reuse, and Submission Policy
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `DATASET_OVERLAP_DECISION_MEMO.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Target Milestone:** Faculty Advisor / Teacher Review (5 October 2026)  
**Final Conference Submission Deadline:** 15 October 2026  
**Auditor Classification:** **CRITICAL UNRESOLVED BLOCKER (Action Required by Faculty Advisor)**  

---

## 1. Executive Summary & Purpose

This decision memorandum outlines the verified facts, publication-ethics context, and available resolution strategies regarding the shared 64-answer evaluation corpus used in the ADCoM 2027 candidate paper:
> *"Specialization and Coordination in a Multi-Agent Technical Interview System: Trajectory Dynamics and Architectural Trade-offs"*

The technical research, multi-agent implementation, and experimental evidence for the paper are complete and verified. However, **submission to the conference portal (Microsoft CMT) is CONDITIONALLY BLOCKED** pending the faculty advisor's formal review and selection of one of the three policy options outlined below on **5 October 2026**.

---

## 2. Verified Facts & Empirical Context

1. **Shared Artifact:** The 160 replay sessions in Experiment XA and 960 sessions in Experiment XC rely on **64 pre-recorded interview answer evaluation payloads** across 8 computer science domains (8 clusters $\times$ 8 answers).
2. **Concurrent Paper Reuse:** This identical 64-payload corpus is utilized in concurrent research manuscripts within the same student research group:
   - Sibling Paper A: Targeting ICITIIT 2027 (focusing on evaluator scoring and human rubric agreement).
   - Sibling Paper B: Targeting INDIACom 2027 (focusing on specification-to-code formal verification).
   - Teammate Concurrent Paper: Evaluator calibration and prompt perturbation (v5).
3. **Disjoint Scientific Objectives:**
   - The ADCoM 2027 paper does **not** evaluate scoring accuracy, does **not** claim educational efficacy, does **not** correlate scores with human raters, and contains **0% human annotator data**.
   - The multi-agent coordination layer (`PREPAIRED_MULTIAGENT=1`), Strategy Agent, Coaching Agent, and threshold arbitration layer exist **exclusively in the ADCoM 2027 manuscript**.
   - The 64 payloads serve strictly as **standardized environmental stimuli / replay inputs** (`EVALUATOR_MOCK_MODE=1`) to drive state transitions across the multi-agent arbitration layer.
4. **Zero Verbatim Duplication:** The manuscript is written in a fresh, independent LaTeX source tree. Text overlap with sibling manuscripts is 0.0% (outside of standard system component proper nouns).

---

## 3. Applicable Publication Ethics Policies

Under the Springer Code of Conduct, the Committee on Publication Ethics (COPE) guidelines, and standard computer science conference policies:
- **Dual Submission / Self-Plagiarism Definition:** Submitting the same scientific contribution or substantial textual/analytical overlap to multiple venues simultaneously is strictly prohibited.
- **Dataset Reuse Policy:** Reusing an open benchmark dataset or standardized stimulus corpus across distinct papers addressing different research questions is standard and permissible across computer science (e.g., evaluating different algorithms on ImageNet, GLUE, or HumanEval).
- **The Grey Area:** When the underlying dataset is an *unpublished, locally constructed corpus* created by the same research group, simultaneous submission without transparent disclosure can trigger referee suspicion of "salami slicing" or dual submission if reviewers overlap between conferences.

---

## 4. Evaluation of the Three Available Options

### Option 1 (RECOMMENDED): Public Benchmark Deposit (Zenodo / Open Science)
- **Mechanism:** Package the 64-answer evaluation payloads as an open-access research benchmark: *The Technical Interview Replay Corpus (TIRC-64)*. Deposit to Zenodo (or Figshare) with a CC-BY-4.0 license, minting a citable DOI.
- **Framing in Manuscript:** Cite TIRC-64 in Section 5.1 as an external, standardized stimulus corpus:
  > *"All replay evaluations are driven by the Technical Interview Replay Corpus (TIRC-64) [X], a fixed benchmark of 64 pre-recorded technical interview evaluation payloads..."*
- **Advantages:** Completely legitimizes dataset reuse across all sibling papers; establishes the dataset as an independent community contribution; adheres to open science best practices.
- **Work Required:** $\approx 1$ hour to generate metadata JSON, README, and upload to Zenodo.
- **Reruns Needed:** Zero. All existing experimental results remain 100% valid.

### Option 2: Transparent Submission Disclosure in CMT Chair Notes
- **Mechanism:** Retain the current manuscript framing, but include a formal disclosure note in the "Notes to Track Chairs" field during Microsoft CMT submission:
  > *"Disclosure Note: This paper evaluates multi-agent coordination and specialization. The 64 deterministic replay payloads used as environmental stimuli in Section 5 originate from platform validation testing and are shared with a concurrent submission by our research group that investigates candidate evaluation calibration. The two papers examine completely disjoint architectural layers and share zero text, figures, experiments, or research claims."*
- **Advantages:** Requires zero external repository hosting; provides complete transparency to program chairs while maintaining double-blind review integrity for peer reviewers.
- **Risks:** Program chairs may request clarification if institutional double-submission policies are exceptionally strict.
- **Work Required:** 15 minutes to format submission note.
- **Reruns Needed:** Zero.

### Option 3: Independent Synthetic Dataset Regeneration
- **Mechanism:** Generate 64 brand-new candidate answer payloads across the 8 domains using an independent synthetic LLM prompt generation script. Re-run Experiment XA (160 sessions $\times$ 12 conditions) and Experiment XC (960 sessions) on the new corpus.
- **Advantages:** Eliminates 100% of overlap with sibling papers at the data level.
- **Disadvantages:** Significant compute and engineering overhead; invalidates the currently verified 43/43 claim ledger; requires regenerating all tables, CIs, LOCO analyses, and re-compiling the manuscript.
- **Work Required:** $\approx 6$–8 hours of computation and manual re-audit.
- **Reruns Needed:** Full regeneration of Experiments XA, XC, cluster bootstrap, and verification scripts.

---

## 5. Explicit Questions for Faculty Advisor (5 October 2026)

The faculty advisor must review and decide on the following specific questions during the scheduled review on **5 October 2026**:

1. **Policy Approval:** Does the advisor approve **Option 1 (Zenodo Benchmark Deposit)** as the preferred strategy for handling the shared 64-answer replay corpus?
2. **Sibling Paper Coordination:** Are the co-authors of the concurrent v5 paper and ICITIIT/INDIACom papers aligned with citing TIRC-64 as a shared benchmark artifact?
3. **Portal Sheet Geometry:** Can the advisor confirm whether the ADCoM 2027 CMT submission portal enforces strict ISO A4 ($595 \times 842$\,pt) geometry or accepts standard US Letter ($612 \times 792$\,pt) as compiled by `llncs.cls`?
4. **Final Submission Authorization:** Subject to the selected disclosure strategy, does the advisor authorize final camera-ready upload prior to the **15 October 2026** conference deadline?

---

## 6. Official Auditor Status

$$\mathbf{STATUS:}\quad \textbf{UNRESOLVED ETHICAL BLOCKER — CONDITIONAL READINESS}$$

No automated agent or author proxy can unilaterally make this publication-ethics decision. Final submission readiness remains **CONDITIONALLY HELD** until the faculty advisor signs off on Section 5 during the 5 October 2026 review.
