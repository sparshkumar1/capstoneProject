# Executive Handover Dossier for Teacher Review
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `FINAL_HANDOVER.md`  
**Candidate Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Target Milestone:** Faculty Advisor / Teacher Review (5 October 2026)  
**Final Conference Deadline:** 15 October 2026  
**Candidate Classification:** **Verified Technical Candidate / Conditionally Ready for Author Review**

---

## 1. Executive Summary

This handover document synthesizes the complete research paper audit, empirical verification, architectural analysis, and Springer CCIS formatting for the PREPAIred submission candidate to ADCoM 2027:

> **Title:** *"Bounded-Authority Agents in an Orchestrated Interview-Practice System: Coordination, Arbitration and Fault Containment"*  
> **Target Venue:** 31st International Conference on Advanced Computing and Communications (ADCoM 2027)  
> **Proceedings:** Springer Communications in Computer and Information Science (CCIS)  
> **Intended Track:** Track 2: Agent-Native Development and Lifecycle Engineering  
> **Authoritative Manuscript:** `paper/adcom2027_final_v9_candidate/manuscript/main.pdf`  
> **Page Count:** Exactly 20 pages (maximum allowable CCIS budget)  
> **Total References:** Exactly 20 references (including Saltzer & Schroeder 1975 and Avižienis et al. 2004)  
> **Quantitative Claim Verification:** **69 / 69 checks passed (100%)** via independent recomputation

---

## 2. Key Achievements and Deliverables Completed

### 2.1 Full Baseline Preservation and Workspace Isolation
- Earlier drafts (`paper/adcom2027/`, `paper/adcom2027_final/`, `paper/adcom2027_final_v8_candidate/`) remain strictly untouched and read-only.
- All modifications, scripts, logs, and LaTeX source trees are isolated in `paper/adcom2027_final_v9_candidate/` (and mirrored to both active repositories).
- Zero git branches, commits, PRs, or external network pushes were created.

### 2.2 Rigorous Implementation and Architectural Verification
- Verified that the central orchestrator hub is the **sole system of record**, enforcing immutable turn observations and rejecting direct agent writes.
- Verified that the authority matrix (`FORBIDDEN_KEYS`, 18 restricted fields) and Pydantic schema validation (`extra=forbid`) completely isolate state mutation.
- Verified that Strategy Agent difficulty proposals undergo strict arbitration (safety envelope, confidence threshold $\tau = 0.6$, evidence verification, and one-step step bounds) before competing with the frozen PPO action.

### 2.3 Experimental Recomputation and Statistical Transparency
- Recomputed all point estimates and confidence intervals from raw execution artifacts across:
  - **Experiment XA (Replay):** 12 ablation conditions $\times$ 160 sessions = 1,920 sessions.
  - **Experiment XB (Fault Injection):** 11 fault classes $\times$ 4 defense configurations = 1,760 sessions.
  - **Experiment XC (Threshold Sensitivity):** 6 threshold values $\times$ 160 sessions = 960 sessions.
  - **Experiment XD (Grounding Rebuild):** 64 candidate responses evaluated.
  - **Experiment XE (Historical & Sockets):** 752 reproduction sessions + 7 breaker scenarios.
- Incorporated **Cluster Bootstrapping** (Field & Welsh 2007) and **Leave-One-Cluster-Out (LOCO)** sensitivity analysis to account for dependent reuse of the 8 candidate answer clusters.
- Fully disclosed and explained all contradicted pre-registered predictions (A9, A10, B6).
- Disclosed that the $+0.59$ turn increase from proactive probing is driven entirely by a single recorded answer set ($k = 1$).

### 2.4 Complete Springer CCIS Compliance and Layout Polish
- Engineered table column widths to eliminate the 19.69 pt right-margin overflow in Table 1 and underfull hbox warnings in Table 5.
- Cleared float queues, balancing figures and tables seamlessly across 20 pages without orphan headers or trailing overflow.
- Audited font embedding: **0 un-embedded fonts** across all 20 pages.
- Audited double-blind anonymity: **0 hits** across author names, affiliations, local paths, and commit hashes.

### 2.5 Pre-registered Merged-Agent Feasibility Protocol (RQ3)
- Fully specified the theoretical hypotheses ($H_1, H_2, H_3$) and experimental protocol for evaluating a unified Technical-Coach Agent against the two-agent architecture.
- Marked **UNEXECUTED** to respect repository safety boundaries prior to teacher review.

---

## 3. Four-Point Action Agenda for Teacher Review (5 October 2026)

When presenting this work to your faculty advisor on 5 October, review the following four agenda items in sequence:

```
                  =============================================
                  TEACHER REVIEW DECISION ROADMAP (5 OCT 2026)
                  =============================================

                                       │
                    [Review Manuscript PDF (20 Pages)]
                    • 69/69 verified empirical claims
                    • CCIS format, 0 font defects, blind
                                       │
                                       ▼
                 [CRITICAL DECISION: Shared 64-Answer Dataset]
                 (See DATASET_AND_OVERLAP_AUDIT.md)
                 ┌─────────────────────┬─────────────────────┐
                 ▼                     ▼                     ▼
          [Option 1: Zenodo]    [Option 2: CMT Note]  [Option 3: Synthetic]
          • Deposit TIRC-64     • Disclose replay     • Generate fresh
            benchmark artifact    trace in Chair note   prompts (45 min)
          • RECOMMENDED         • Minimal friction    • Complete separation
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                 [DECISION: Merged-Agent Experiment (RQ3)]
                 (See MERGED_AGENT_EXPERIMENT.md)
                 ┌─────────────────────┬─────────────────────┐
                 ▼                                           ▼
          [Approve Execution]                         [Maintain Status Quo]
          • Run 600 sessions (~35 min)                • Keep theoretical
          • Populate empirical table for RQ3            justification only
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                 [DECISION: Page Geometry Confirmation]
                 • Letter (612x792 pt) vs A4 (595x842 pt)
                 • Re-check official ADCoM CFP upon login
                                       │
                                       ▼
                       [AUTHORIZE FINAL SUBMISSION]
```

### Agenda Item 1: Manuscript Walkthrough and Empirical Defense
- Present `ADCOM2027_PREPAIred_v8_complete_blind.pdf` (or `manuscript/main.pdf`).
- Walk through the core narrative: bounded-authority stateful coordination alters difficulty trajectories while maintaining 100% fail-closed fault containment under synthetic crashes, malformed schemas, and timeouts.
- Highlight the unflinching disclosure of limitations: synthetic replay, zero live-LLM evaluation, zero human candidate claims, and test suite regression boundaries (421 passing tests with 59 pre-existing/environmental failures).

### Agenda Item 2: Resolution of Shared 64-Answer Dataset (CRITICAL BLOCKER)
- Review `DATASET_AND_OVERLAP_AUDIT.md`.
- Explain that the 64-answer replay corpus is shared with sibling papers (evaluator calibration / teammate v5 paper).
- Recommend **Option 1 (Zenodo Benchmark Deposit)**: Decouple the dataset by framing it as a standardized community benchmark artifact (*TIRC-64*), citing it identically across papers.
- If external archiving is undesirable, adopt **Option 2 (CMT Chair Disclosure Note)**.

### Agenda Item 3: Decision on Executing the Merged-Agent Experiment
- Review `MERGED_AGENT_EXPERIMENT.md` and `EXPERIMENT_PLAN.md`.
- If the advisor desires empirical numbers for RQ3 (comparing the split architecture against a unified agent), authorize the 35-minute test run.
- If the advisor considers the architectural software engineering justification sufficient, preserve the current text.

### Agenda Item 4: Geometry Confirmation for Camera-Ready
- Upon logging into the official ADCoM CMT portal, verify whether the organizers mandate ISO A4 PDF rendering. If required, compiling with `\documentclass[runningheads,a4paper]{llncs}` sets A4 cleanly without breaking the 20-page budget.

---

## 4. Authoritative File Index and Cryptographic Checksums

All core assets are organized in `paper/adcom2027_final_v9_candidate/`:

| File Name | Purpose / Description | SHA-256 Checksum |
|:---|:---|:---|
| `manuscript/main.pdf` | Built 20-page camera-ready blind PDF | `74A1781F87A72B217F8A9E8F10FB83C516E85C3A78C64220E0662741688E4A56` |
| `ADCOM2027_PREPAIred_v8_complete_blind.pdf` | Authoritative root candidate PDF | `74A1781F87A72B217F8A9E8F10FB83C516E85C3A78C64220E0662741688E4A56` |
| `EXPERIMENT_PLAN.md` | Research questions, hypotheses, protocol | (Generated 2026-10-03) |
| `EXPERIMENT_RESULTS.md` | Complete recomputed tables, CIs, LOCO | (Generated 2026-10-03) |
| `DATASET_AND_OVERLAP_AUDIT.md` | 64-answer provenance & 3 resolution options | (Generated 2026-10-03) |
| `REVISION_REPORT.md` | Complete changelog and visual audit | (Generated 2026-10-03) |
| `CLAIM_AUDIT.md` | 69/69 quantitative claim traceability | (Generated 2026-10-03) |
| `FINAL_COMPLIANCE_REPORT.md` | Springer CCIS layout & font audit | (Generated 2026-10-03) |
| `FINAL_HANDOVER.md` | Executive synthesis & teacher agenda | (Generated 2026-10-03) |
| `verification/verify_paper.py` | Automated claim verification script | `0C675B3D447952136DF074DFB2D466EB83DA4C609930777B8AE96D46852F8125` |
| `scripts/blind_audit.py` | Double-blind scanning script | `2CE3D4C2F6DEFA7B03DFB4912BF86C3E44A14488A01FEF1B691377EF97D24D6F` |

---

## 5. Final Handover Conclusion

The PREPAIred ADCoM 2027 paper is in its strongest scientifically defensible, empirically verified, and typographically polished state. Every empirical claim is tied to open, reproducible artifacts.

The project is officially ready for presentation to your teacher on **5 October 2026**.
