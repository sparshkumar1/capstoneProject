# PREPAIred Author Action Items & Pre-Submission Decisions (V10)

**Date**: 2026-09-30  
**Target Manuscript**: PrepAIred System Architecture & Empirical Evaluation (V10)  
**Status**: Review-Ready Draft | Pending Final Author Decisions  

---

## 1. TARGET VENUE SELECTION & TEMPLATE CONVERSION

- **Action Needed**: Formally select the target conference venue from the researched candidates:
  - **Option 1 (Recommended Primary)**: **INDIACom 2027** (21st INDIACom, New Delhi, India; IEEE Conference ID #68305; Indexed in Scopus and IEEE Xplore).
    - Page Budget: 6 pages standard, up to 2 extra pages allowed with fee (total 8 pages).
    - Fit: `manuscript_v10_blind.pdf` is **7 pages**, fitting comfortably within INDIACom's 6+2 page limit.
    - Review Process: Double-blind.
  - **Option 2 (Recommended Backup)**: **IEEE COEP CON 2027** (Pune, India; IEEE Conference Record #68112).
    - Page Budget: Strict 6 pages. Would require minor tightening of Section II and Section X.B to compress from 7 to 6 pages.
- **Next Step**: Download the selected conference's official template (IEEE Word/LaTeX template) and import the verified text from `PROPOSED_REVISION_DRAFT_V10_BLIND.md`.

---

## 2. AUTHOR METADATA & INSTITUTIONAL STATEMENTS

The following items cannot be decided or invented by automated agents and require explicit author confirmation:

| Item | Current Working Placeholder | Required Author Action |
|---|---|---|
| **Corresponding Author** | Marked as `[pending author confirmation]` in title page. | Author team must designate one author (e.g., Dr. Uma D or Sparsh Kumar) and supply preferred correspondence address. |
| **Email Verification** | `Manasaarun882@gmail.com` used across build pipeline. | Manasa S A to confirm email address format (confirm `.com`). |
| **Funding Statement** | Currently omitted from manuscript. | If funded by an institutional or government grant, provide the grant number and agency; otherwise confirm: *"This research received no external funding."* |
| **Conflict of Interest** | Currently omitted from manuscript. | Confirm standard IEEE declaration: *"The authors declare that they have no conflicts of interest."* |
| **Institutional Ethics Sign-off** | Described in §XIII as exploratory internal benchmark without formal ethics review. | For the future confirmatory study (X2-C), dispatch the drafted institutional ethics enquiry letter (`research/audit/INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`) to the PES University Ethics Board. |

---

## 3. DATA AND CODE AVAILABILITY COMMITMENT

- **Manuscript Wording (§XIV)**:
  > *"The evaluator source code, RL training/environment code, and the 64-item benchmark dataset... are maintained in the authors' project repository. A public release of the repository, or of a de-identified subset sufficient to reproduce Tables III–VI, has not been finalized at the time of writing."*
- **Action Needed**: Decide whether to prepare an anonymized Zenodo archive (or GitHub repository) containing the evaluation scripts and the 64-item benchmark dataset upon paper acceptance.

---

## 4. AI-TOOL USE DISCLOSURE (VENUE-SPECIFIC)

- **Policy Status**: General IEEE policy requires authors to disclose the use of generative AI tools in the creation of manuscript text or data in the Acknowledgments section or paper submission portal.
- **Action Needed**: Upon submitting to the selected venue's portal, check their specific AI declaration prompt and supply the drafted disclosure:
  > *"During the preparation of this work, the authors used Claude Code (Anthropic) for code verification, analysis script execution, and manuscript formatting assistance. The authors reviewed and edited all content and take full responsibility for the integrity of the research."*
