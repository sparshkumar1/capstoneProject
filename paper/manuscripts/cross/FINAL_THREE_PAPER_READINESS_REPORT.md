# Final three-paper readiness report (2026-09-21)

Nothing was submitted, committed, pushed or tagged. No experiment, retraining or new analysis was run and no frozen or audited evidence file was changed. Figures were re-plotted from the same stored files with corrected label placement. Readiness classes: READY FOR SUBMISSION / READY AFTER AUTHOR CONFIRMATION / REQUIRES VENUE VERIFICATION / REQUIRES NEW RESEARCH / NOT CURRENTLY DEFENSIBLE. No acceptance prediction is made.

## Bucket summary
| READY NOW (content and layout, for the authors' read-through) | REQUIRES AUTHOR CONFIRMATION | REQUIRES NEW RESEARCH | REQUIRES VENUE VERIFICATION |
|---|---|---|---|
| P1 blinded PDF (5 pages, visual QA passed); P3 proposal text (762 words) | author metadata wording, contact details, corresponding author; AI-use facts; git tags/hashes in the blinded P1 text; "Authors' background" page; repository wording; P3 Declarations (ethics line, availability, competing interests); the form fields for the P3 proposal | the entire system paper (study, arms, ethics, ratings) | ICETC: AI-disclosure, prior-submission, camera-ready, fee; HCII: AI policy, fee, proposal-form fields, Springer template and length; ICALT: AI-use, prior-submission, author guidelines; AIED 2027: no call yet |

## PAPER 1 — ICETC 2026
- **Exact title:** Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System
- **Venue:** IEEE ICETC 2026 (10 Oct 2026; notification 10 Nov 2026).
- **Contribution:** scoped, property-by-property evidence account for one pipeline (oracle, weakened control, layer attribution); not a new method.
- **Evidence complete?** Yes for its stated scope (X1-C, X1-A, X1-B-I frozen; numeric trace 0 unmatched).
- **Major weaknesses:** one application/environment; author-written attacks and oracles; same-agent regression evidence; weak education fit (assessment-integrity argument only, no learning outcome).
- **Minor weaknesses:** preprint references (labelled); small figure labels; artifact not public; the frozen SEC-05 note (four) disagrees with the raw data (five) and the manuscript follows the raw data.
- **Changed in this pass:** rendering defects fixed at the source (author table, heading VIII, table splitting, orphaned References heading, spacing, placeholder removed from the master); a short introduction paragraph on education/assessment fit and "learning outcomes" in the not-evaluated list (no number changed); new reviewer-risk audit and final checklist.
- **Blinded status:** `venue/ICETC_P1/P1_ICETC_BLINDED.pdf`, 5 pages; every page inspected visually and automated checks pass (no names, institution, e-mail, product name, acknowledgment or personal path; no /Author or /Title; XMP clean).
- **Remaining author decisions:** AI-use disclosure facts and where ICETC wants them; whether git tags/short hashes stay (they are not on any remote today; do not push while under review); the "Authors' background" page; contact details.
- **Submission readiness: READY AFTER AUTHOR CONFIRMATION** (plus venue verification of ICETC's disclosure and prior-submission rules).

## PAPER 3 / RL — HCII 2027 AIS
- **Exact title:** A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews
- **Venue:** HCI International 2027, Adaptive Instructional Systems (proposal 9 Oct 2026; outcome 20 Nov 2026; full paper 29 Jan 2027; 10–20 pages, typically 12; single-blind).
- **Proposal status:** 762 of 800 words, four official headings, numbers traced; not submitted.
- **Full-paper status:** content-complete 14-section draft (about 5,283 body words, abstract 240, 3 figures, 4 tables, 14 references); **no page count exists** because the Springer template is not applied; Springer/LNCS-style references.
- **Evidence complete?** For the simulation study, yes; nothing about real learners.
- **Scientific limitations:** authored simulator, personas and targets; author-selected margin; five seeds; 24,576 timesteps; one default training candidate; training/evaluation and runtime state mismatches; no real candidates; no IRT/CAT/Elo baseline.
- **Changed in this pass:** three figures re-plotted with corrected labels (a dashed line through labels; overlapping labels); references now one paragraph each; visual QA report; values unchanged.
- **Remaining author decisions:** Declarations (contact details, ethics line, AI-use statement, availability, competing interests); proposal form fields; template and length once available.
- **Submission readiness:** proposal **READY AFTER AUTHOR CONFIRMATION**; full paper **REQUIRES VENUE VERIFICATION** (template) and author confirmation; visual QA **BLOCKED** until the template is applied.

## SYSTEM PAPER
- **Working title:** "PREPAIred: An End-to-End Multimodal Adaptive Technical Interview Preparation System" (provisional; "multimodal" is not supported by the audit).
- **Selected/shortlisted venue:** none selected. ICALT 2027 shortlisted from verified facts (5 pages including references; double-blind; 15 Jan 2027). AIED 2027: no call published.
- **Actual implementation status:** audio + text prototype: orchestrator, evaluator, sandbox, local feedback model, STT, confidence score, PPO + application-level guardrails, UI. Full table in `system_paper/SYSTEM_PAPER_RESEARCH_AUDIT.md`.
- **Missing components:** video/face/MediaPipe (not implemented); hesitation scorer not wired into the live state (runtime hesitation = 1 − confidence); no runtime Constant-Same or rule-based conditions.
- **Required new experiments and human study:** randomized comparison with pre/post held-out questions and independent blinded ratings (`system_paper/SYSTEM_PAPER_STUDY_PROTOCOL.md`); sample size not chosen; treat as pilot if participants are limited.
- **Ethics status:** **BLOCKED** — no institutional determination exists; the enquiry draft (`research/audit/INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`) is unsent.
- **Baseline status:** not implemented at runtime (plan written). **Ablation status:** small matrix proposed; nothing run.
- **Manuscript status:** internal pre-research draft; no results; not to be labelled final. Visual QA **N/A – BLOCKED**.
- **Submission readiness: REQUIRES NEW RESEARCH.**

## P2 (HOLD)
Not among the final three; evidence preserved; no claims merged elsewhere; not classed for submission (NOT CURRENTLY DEFENSIBLE today because of provenance and ethics records).

## CROSS-PAPER
- **Overlap audit:** `cross/THREE_PAPER_OVERLAP_AUDIT.md` and `cross/ORIGINALITY_OVERLAP_AUDIT.md`: no substantial text overlap with the legacy paper; cross-paper overlap technical or boilerplate; no shared references between P1 and P3. Repository-level screen only; no "100 %" claim.
- **Shared evidence:** none between P1 and P3; the system paper may cite them but not reuse them as effect evidence.
- **Shared figures:** none.
- **Publication-order issues and prior-publication risks:** ICETC decision 10 Nov and HCII proposal outcome 20 Nov fall before the ICALT deadline; related-submission rules for ICALT and ICETC are not stated or not found; CSEDU and SAC contingencies prohibit concurrent submission.
- **Remaining venue-policy questions:** see the buckets above and `cross/AI_DISCLOSURE_FACT_CHECK.md`.
- **Discrepancy noted:** the brief's ICALT track "Technology-supported Assessment" appears on the official page as "Technology-Enhanced Assessment in Formal and Informal Education (TeASSESS)".
- **Paper 4:** no (`cross/PAPER_4_FEASIBILITY_MEMO.md`).

## Files that must not be touched
Everything under `research/` (results, protocols, tags, audits, evidence), `rl/checkpoints/`, `ablation/results/`, `experiments/*` results and figures, and the P1/P3 numbers; the frozen SEC-05 note stays as it is.

## Blockers, in one list
1. Author confirmations (AI-use facts; contact details; git-identifier decision; "Authors' background" page; repository wording; P3 Declarations).
2. Unverified venue rules (ICETC AI disclosure, prior submission, camera-ready, fee; HCII AI policy and form fields; ICALT AI use and prior submission).
3. Springer/HCII template not available, so P3 length and its final visual QA are pending.
4. System paper: new research, ethics determination, runtime baselines, hesitation-wiring decision.
5. Mentor document: `cross/MENTOR_JUSTIFICATION_THREE_PAPERS.md` (the earlier three-paper version from the previous pass is `cross/MENTOR_JUSTIFICATION.md`).
