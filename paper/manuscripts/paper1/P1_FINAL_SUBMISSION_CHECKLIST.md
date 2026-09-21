# P1 — final submission checklist (ICETC 2026; not submitted)

Upload candidate: `venue/ICETC_P1/P1_ICETC_BLINDED.pdf` (5 pages). Nothing has been submitted, registered, paid, committed, pushed or tagged. Tick a box only when the fact has actually been confirmed.

## Venue facts (official pages read 2026-09-21; recheck on the day)
- [ ] Submission deadline 10 Oct 2026 and notification 10 Nov 2026 still shown on the current official site (the older CFP PDF carries an earlier date; the site records the later extensions).
- [ ] Double-blind requirement still stated on `cfp.html`; two-column IEEE format; minimum 5 pages.
- [ ] ICETC's own AI-use / disclosure rule: **not found**. Ask the organisers or find the rule.
- [ ] ICETC's prior-submission / concurrent-submission rule: **not found**.
- [ ] Camera-ready date, registration and fee: **not found**.
- [ ] Extra-page charge: stated two ways on two official pages; irrelevant at 5 pages.
- [ ] Whether the template's "Authors' background" page is needed at submission and how it is kept from reviewers: **unresolved**.

## Author confirmations (nothing here may be invented)
- [ ] Author list, order and wording "Dept. of CSE, PES University"; designation for Dr. Uma D only.
- [ ] E-mail, ORCID, city, country, corresponding author (needed for the master and camera-ready, not for the blinded copy).
- [ ] AI-use facts (tool, version, sections affected, level of author review) and where the venue wants them.
- [ ] Decision on git tags and short hashes in the blinded text (`P1_ICETC_ANONYMIZATION_CHECKLIST.md` item 10); do not push the branch or tags during review.
- [ ] Wording of the repository-availability statement.
- [ ] The authors have read the blinded PDF end to end and agree with every claim.

## Document gates (all checked on the final build)
- [x] Exact title; no legacy title.
- [x] Blinded PDF: 5 pages; no names, institution, e-mail domains, product name, acknowledgments or personal paths; no /Author or /Title; XMP contains no identifying string.
- [x] Rendered pages of both PDFs inspected by eye; automated checks pass (`venue/ICETC_P1/P1_VISUAL_QA_REPORT.md`).
- [x] No placeholder or draft text in any rendered PDF.
- [x] 14 references, every one cited, every citation resolves; unverified venues labelled.
- [x] Every number traces to `paper1/manuscript.md` (numeric trace: 0 unmatched).
- [x] SEC-05 shown as five attacks; frozen note untouched.
- [ ] Rebuild and repeat both QA steps after ANY further edit.

## Scientific gates
- [x] No inferential statistics; "k/5" stated to be a count.
- [x] Limitations stated: same-agent regression evidence, author-written oracles, ptrace filter, SEC-08/SEC-09 oracle limits, untested follow-up channel, timeout mismatch, one environment, package-pin violation, repository not public.
- [x] No learning, grade, usability or outcome claim.

## Classification
**READY AFTER AUTHOR CONFIRMATION**, with ICETC's disclosure and prior-submission rules still to be verified. Not "READY FOR SUBMISSION" until the unchecked boxes above are resolved.
