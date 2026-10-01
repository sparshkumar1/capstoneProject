# Prioritized Final Action Items for PrepAIred Publication & Viva

**Date**: 2026-09-30  
**Auditor**: Independent Software Verification Engineer & Research Mentor  
**Scope**: Actionable Roadmap Categorized by Essential Requirements, Venue-Dependent Tasks, and Optional Enhancements  

---

## 1. TIER 1: ESSENTIAL PRE-SUBMISSION AUTHOR ACTIONS
*(Must be completed by the author team before formal conference submission)*

| Priority | Action Item | Responsible Party | Description & Rationale |
|:---:|---|---|---|
| **E-1** | **Formally Select Target Venue** | Author Team & Guide | Choose between **INDIACom 2027** (BVICAM, New Delhi, IEEE Conf. ID 74162; permits 6+2 pages, aligns well with current 7-page blind PDF) and **IEEE COEP CON 2027** (Pune Section). |
| **E-2** | **Designate Corresponding Author** | Author Team | Officially designate either Dr. Uma D (Faculty Guide) or Sparsh Kumar (Student Lead) as the corresponding author, and supply the corresponding institutional email address. |
| **E-3** | **Finalize Institutional Acknowledgment & Grant Status** | Author Team | Confirm whether internal PES University capstone project funding or external department grants supported this research. Update the acknowledgment paragraph in `manuscript_v10_author.html` prior to final camera-ready generation. |
| **E-4** | **Confirm Conflict of Interest Statement** | All 5 Authors | Complete standard IEEE author disclosure declaring that no financial or institutional conflicts of interest exist. |

---

## 2. TIER 2: VENUE-DEPENDENT TECHNICAL & FORMATTING TASKS
*(Applicable only after the specific venue is confirmed)*

| Priority | Action Item | Trigger Condition | Implementation Guidance |
|:---:|---|---|---|
| **V-1** | **Condense Blind PDF to Strict 6 Pages** | Required ONLY if the chosen venue enforces a strict 6-page limit without paid overlength pages. | Apply the 1-page condensing plan: combine Table I and Table II into a compact single-column specification; tighten CSS line-height on math displays from 1.15 to 1.05; compress Section X.B narrative slightly. (No scientific claims or results are altered). |
| **V-2** | **IEEE PDF eXpress Pre-flight Verification** | Required by all IEEE-sponsored conferences upon paper acceptance or camera-ready submission. | Upload the generated PDF to the conference's IEEE PDF eXpress portal to ensure 100% font embedding, subsetting, and standard margin compliance. |
| **V-3** | **Electronic IEEE Copyright Form (eCF)** | Triggered during final paper submission. | Transfer standard IEEE publication copyright through the conference submission management portal. |
| **V-4** | **Separate Title Page Submission** | Required by double-blind conferences requiring author identity in a separate document. | Submit `research/paper_audit_v10/PROPOSED_REVISION_DRAFT_V10_TITLEPAGE.md` alongside `manuscript_v10_blind.pdf`. |

---

## 3. TIER 3: OPTIONAL ENHANCEMENTS & CAPSTONE VIVA PREPARATION
*(Optional for initial conference review; recommended for Capstone Review 2 and future journal extensions)*

| Priority | Action Item | Target Context | Benefits & Notes |
|:---:|---|---|---|
| **O-1** | **Live Docker Sandbox Demonstration** | Phase 3 Review 2 (12–16 Oct 2026) | Prepare a local live Docker daemon demonstration showcasing ephemeral container creation, compilation, test-case assertion, and timeout cleanup on Linux/WSL2. |
| **O-2** | **Live Multi-Turn Voice Interview Demonstration** | Capstone Demonstration | Set up an interactive demonstration connecting browser Web Speech API / Whisper STT with the audio confidence and hesitation analyzers. |
| **O-3** | **Extended Human Cohort Study ($N \ge 30$)** | Future Journal Extension (IEEE Access / TLT) | Conduct formal multi-rater evaluations on real student interview sessions under institutional IRB / ethics approval to evaluate real-time candidate learning trajectories and long-term skill retention. |
| **O-4** | **GPU-Accelerated Qwen2.5 Benchmark** | Future Optimization | Measure real-time token generation latency on a dedicated CUDA GPU (e.g., RTX 4090 or A100) to confirm sub-500ms conversational response latency in production. |

---

## 4. CONCLUSION & IMMEDIATE NEXT STEP

The PrepAIred V10 manuscript and codebase are **technically sound, fully verified, and review-ready**. The immediate next step is for the team to hold a brief alignment meeting to resolve **Actions E-1 and E-2** (Venue Selection and Corresponding Author), after which formal submission can proceed immediately.
