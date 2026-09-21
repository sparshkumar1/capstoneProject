> **Superseded on 2026-09-21 by `cross/FINAL_THREE_PAPER_READINESS_REPORT.md`** (final set: P1, P3 and the system paper; P2 on hold). Kept for the record; its P1 blinded-copy description of an acknowledgment/placeholder no longer applies.

# FINAL PUBLICATION READINESS REPORT (master pass, 2026-09-21)

Nothing was submitted, committed, pushed or tagged. No experiment, retraining or new analysis was run; no frozen or audited evidence file was changed. Local document builds only (Microsoft Word 16.0 for the ICETC files).

## A. Exact titles
- **P1 (IEEE ICETC 2026):** Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System
- **P2 (HOLD):** Exploratory Measurement of an Evidence-Grounded Technical-Answer Evaluator
- **P3 (HCII 2027 AIS):** A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews
- Legacy title, historical only: PrepAIred: A Reinforcement-Based LLM-Powered Technical Interview Preparation System. All three current titles were checked in every manuscript, proposal and build source; none was replaced.

## B. Author order and affiliations (author-identifying master copies only)
1. Dr. Uma D, Professor, Dept. of CSE, PES University
2. Naveen S Khadd, Dept. of CSE, PES University
3. Sparsh Kumar, Dept. of CSE, PES University
4. Athreya Shashidhara, Dept. of CSE, PES University
5. Manasa S A, Dept. of CSE, PES University

No designation is stated for authors 2–5; no e-mail, ORCID, city or country is recorded (the legacy PDF lists personal e-mail addresses; none was copied). The legacy PDF prints "Professor, Dept. of CSE" for Dr. Uma D and "Dept. of CSE" for the others; "PES University" comes from your instruction, so confirm that wording. The blinded ICETC copy contains none of this.

## C. Files changed or created in this pass (all under `paper/manuscripts/`, untracked)
- **Manuscript sources edited:** `paper1/manuscript.md`, `paper2/manuscript.md`, `paper3/manuscript.md` (author block, prose pass, table cross-references, two phrasings varied); `venue/icetc2026/ICETC_PORT_MANUSCRIPT.md` (prose pass, table references, header note); `audit_v2/_make_icetc_port.py` (keeps the port author-neutral).
- **P1:** `venue/ICETC_P1/` — `P1_ICETC_BLINDED.md/.docx/.pdf`, `P1_ICETC_MANUSCRIPT_READY.md`, `P1_ICETC_MASTER_author_identifying.docx/.pdf`, `P1_ICETC_ANONYMIZATION_CHECKLIST.md`, `P1_ICETC_READINESS.md`, `P1_PRIMARY_VENUE_PLAN.md`, `build_icetc_docx.py`, `export_pdf_and_count.ps1`, `build/`.
- **P1 backup:** `venue/ICETC_P1_BACKUP/P1_BACKUP_VENUE_PLAN.md` (status and future conversion checklist added).
- **P3:** `venue/HCII_P3/` — `P3_HCII_PROPOSAL_FINAL.md` (author metadata, LNCS references), `P3_HCII_PROPOSAL_CHECKLIST.md`, `P3_HCII_READINESS.md`, `P3_FULL_MANUSCRIPT_READY.md`, `_build_full_manuscript.py`.
- **P2:** `venue/paper2/PAPER2_SUBMISSION_HOLD.md` (note added).
- **Cross:** `cross/MENTOR_JUSTIFICATION.md` (new), `cross/ORIGINALITY_OVERLAP_AUDIT.md` (new; no equivalent existed), `cross/AI_DISCLOSURE_FACT_CHECK.md`, this report; `audit_v2/_apply_prose_pass.py`, `audit_v2/originality_scan.py` (new, reproducible).
- **Banners only:** `venue/hcii2027/HCII_AIS_PROPOSAL_800w.md` marked superseded; `venue/icetc2026/ICETC_PORT_MANUSCRIPT.md` marked as build source.

## D. Originality / overlap (`cross/ORIGINALITY_OVERLAP_AUDIT.md`)
No substantial overlap found between P1, P2, P3 or the proposal and the legacy PDF or its three archived drafts: 0 duplicate sentences and 0 shared 8-word sequences; at 5-word granularity the only matches are the author block and one heading. Cross-paper overlap is technical or boilerplate (the shared grader-injection citation topic, reproducibility and availability disclosures, the author-metadata note); two shared phrasings were reworded. Overlap with the project's own preparation notes is 0–1.3% of 8-word sequences (shared frozen facts). This is a repository-level screen; it does not use an external plagiarism service and no "100%" claim is made.

## E. Remaining scientific inconsistencies
- **SEC-05:** the frozen note `X1C_RESULT_NOTE.md` lists four status-indistinguishable attacks and says SEC-05's status differed; the raw `results.csv` (both campaigns) shows it identical, so five. The manuscripts follow the raw data; the frozen note is untouched (documented in `paper1/P1_SEC05_RECONCILIATION.md`).
- **Legacy vs current:** the legacy paper's system description (for example its model size) and headline numbers differ from the current evidence; they were not carried over and were not re-verified.
- No other inconsistency was found across title, authors, definitions, sample sizes, seeds, metrics, intervals, p-value labelling, tables, figures, references and claim strength. The composite formula appears only in P2; P3's guardrail terms appear only in P3; P1 terms (baseline/repaired SUT) appear only in P1.

## F. Venue-policy uncertainty
ICETC: camera-ready date, prior-submission rule, ICETC's own AI-disclosure rule, fee; the extra-page charge is stated two ways on two official pages (irrelevant at 5 pages); the template's "Authors' background" page. HCII: AI policy, registration fee, proposal-form fields, Springer template page count; Springer Nature AI policy detail pages (only the landing page was read). CSEDU: SciTePress template, any post-rejection rule, acknowledgments-versus-disclosure handling. EDUCON: abstract-stage rule. ATIS: FAQ answers. SAC: page limit and blind status.

## G. Author-confirmation items
Institution wording ("PES University"); e-mail, ORCID, city, country, corresponding author; AI-use facts (tools, versions, sections, review extent, X2/X3 involvement); whether to keep git tags and hashes in the blinded P1 text; the "Authors' background" page; repository release wording; P3 ethics line; P2 decisions D-2, D-5, D-6.

## H. Blinded-manuscript status (P1)
`P1_ICETC_BLINDED.pdf`: no names, affiliations, e-mail domains, product name, acknowledgments or AI-disclosure text; the PDF has no /Author or /Title entry and the DOCX creator is "Anonymous"; text scan 0 hits. One judgement remains: the cited git tags and short hashes are not on any remote today (checked with `git branch -r --contains` and `git ls-remote --tags`), so they do not resolve publicly, but pushing the branch or tags during review could expose the repository owner's account; repository visibility could not be checked.

## I. P1 page count
**5 pages** (blinded and master), measured from Word's export of the official ICETC IEEE Word template; the last page holds the conclusion and references, columns balanced. Nothing was padded or trimmed to reach it.

## J. P3 proposal
**762 words** of 800, references excluded, unchanged; four official headings intact; 29 numbers traced (one rounding, 0.14877 shown as +0.149); references now in LNCS style.

## K. P3 full manuscript
About **5,280 body words** (excluding declarations and references), abstract 240 words, 3 figures, 4 tables, 14 references (all cited). **No page count exists** because the Springer template is not available or applied; the earlier 13–15 page figure was a rough word-based guess and is withdrawn. Official range 10–20 pages.

## L. P2
HOLD. Exact title confirmed; author block added for consistency; prose scaffolding rewritten; no result, limitation or venue decision changed; no submission package prepared. Ethics, consent, rater, blinding and provenance gaps unchanged and not invented.

## M. Backup venue
CSEDU 2027 regular paper (deadline 17 Nov 2026, after the ICETC notification of 10 Nov; double-blind; SciTePress; up to 12 pages; simultaneous submission prohibited) is a documented contingency only. Not selected, not converted, no page count, not venue-ready. EDUCON 2027 is conditional on an abstract-stage rule that is unverified.

## N. Mentor justification
`cross/MENTOR_JUSTIFICATION.md` created: 30-second, 1-minute and detailed versions plus the four short answers. It does not claim that no AI was used, and gives the tool question a truthful holding answer.

## O. Confirmation
No experiment, retraining, or frozen-evidence change. `git rev-parse HEAD` = 11b7fe6e4c4cfedbd5a05c7de8aab0cd2fba1e0f (unchanged); `git status --short` = 55 entries (unchanged); `git diff --check` exit 0. Numeric trace: 0 unmatched. In-text citations: every reference is cited and every citation resolves in P1, P2 and P3.

## P. Safe to submit now versus must confirm first
**Safe to submit now (content-wise):** nothing is to be submitted without you. The following are complete and unchanged in substance, needing only your personal read-through: the P3 proposal text (762 words), subject to the metadata below.
**Must confirm first:**
- *P3 proposal:* institution wording, e-mail/ORCID/city/country, corresponding author, the form's fields, AI-statement if the form asks.
- *P1 ICETC:* AI-disclosure policy question and facts; git tags/hashes decision; "Authors' background" page; camera-ready and prior-submission rules; read the blinded PDF end to end.
- *P3 full paper:* Springer template applied and length measured; AI-disclosure facts; ethics line; repository wording.
- *P1 backup:* nothing to submit unless ICETC rejects and CSEDU's rules are re-read.
- *P2:* do not submit.

## Authoritative-file map
| Kind | Authoritative file(s) |
|---|---|
| Frozen evidence | everything under `research/` (results, protocols, tags, audits), `rl/checkpoints/`, `ablation/results/` — untouched |
| P1 general master | `paper1/manuscript.md` (author-identifying, venue-neutral); v1 in `paper1/manuscript_v1_archive.md` |
| P1 ICETC build source | `venue/icetc2026/ICETC_PORT_MANUSCRIPT.md` (author-neutral; not for upload) |
| P1 ICETC master / blinded | `venue/ICETC_P1/P1_ICETC_MASTER_author_identifying.*` and `P1_ICETC_MANUSCRIPT_READY.md` / `P1_ICETC_BLINDED.pdf` (upload candidate), `.docx`, `.md` |
| P2 (hold) | `paper2/manuscript.md`; `venue/paper2/PAPER2_SUBMISSION_HOLD.md` (+ `PAPER2_SUBMISSION_GATE.md`, `PAPER2_VENUE_GATE.md`) |
| P3 general master | `paper3/manuscript.md` |
| P3 HCII proposal / full paper | `venue/HCII_P3/P3_HCII_PROPOSAL_FINAL.md` (text in `proposal_text.txt`) / `P3_FULL_MANUSCRIPT_READY.md` |
| Backup / alternatives | `venue/ICETC_P1_BACKUP/P1_BACKUP_VENUE_PLAN.md`; `venue/SAC_P3_ALTERNATIVE/SAC_P3_NOTE.md`; `venue/atis2026/ATIS_FIT_MEMO.md` |
| Readiness and audits | `venue/*/…READINESS.md`, `cross/FINAL_THREE_PAPER_AUDIT_V2.md`, `cross/ORIGINALITY_OVERLAP_AUDIT.md`, `cross/AI_DISCLOSURE_FACT_CHECK.md`, `audit_v2/*` |
| Historical / superseded | `paper*/manuscript_v1_archive.md`, `venue/hcii2027/HCII_AIS_PROPOSAL_800w.md` (611 words), first-pass files `paper*/claim_ledger.md`, `cross/CROSS_PAPER_OVERLAP_REPORT.md`, `cross/VENUE_FIT_MATRIX.md`, and the legacy paper under `research/papers/archived/superseded_manuscripts/` |
