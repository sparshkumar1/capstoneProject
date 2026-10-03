# Submission checklist (nothing has been submitted)

Status: PASS / FAIL / PARTIAL / NOT VERIFIED. Date of this review: 2026-10-02.

| # | Item | Status | Note |
|---|---|---|---|
| 1 | Official ADCOM 2027 CFP, deadline (15 Oct 2026 per the brief), page limit, track list | NOT VERIFIED | accsindia.org and springer.com are blocked by the environment's network policy; a web search confirmed only the 31st ADCOM, Bengaluru, 10–11 June 2027. All CFP details come from the brief. |
| 2 | Current Springer CCIS template and author instructions | NOT VERIFIED | The build uses `llncs` with `runningheads` and the bundled `splncs04` style; the current official version could not be retrieved or compared. |
| 3 | Page limit ≤ 20 including references | PASS | 19 pages as built; counting rules of the official template unverified. |
| 4 | Double-blind (no names, affiliations, URLs, product name, metadata) | PARTIAL | `scripts/blind_audit.py`: 0 hits in sources, PDF text and metadata; independent grep agrees. Anonymity cannot be proven against reviewers who know the authors' related manuscripts. |
| 5 | Undefined references / overfull boxes | PARTIAL | 0 undefined references; two small overfull boxes (≈20 pt) remain in table 1 (visually inspected, text not cut). |
| 6 | Fonts embedded, no identifying metadata | PASS | `pdffonts`, `pdfinfo`. |
| 7 | Every figure/table/page visually inspected | PARTIAL | Pages 1–17 and 19 rendered and viewed after the final layout fixes; page 18 (first references page) only in an earlier build. |
| 8 | Every number in the text matches stored results | PASS | `verification/verify_paper.py`: 59/59. |
| 9 | Registered experiments reproducible from a clean clone | PASS | Tables regenerate identically; XA/XB/XC analyses regenerate identical CSVs from raw runs; a 24-session XA re-run matches all trajectory fields. Latency values are machine-dependent and not expected to match. |
| 10 | References: bibliographic details | PARTIAL | 18 references. Titles, venues, years checked through a search interface (no full texts read; no DOI/Crossref check; some preprints). Unverified at full-text level. |
| 11 | Each citation supports its sentence | PARTIAL | Checked against titles and abstracts only. |
| 12 | Originality and concurrent submission | NOT VERIFIED | `OVERLAP_AUDIT.md` compares against two sibling manuscripts; each venue's policy and the authors' actual submission status were not retrievable. Authors must decide and disclose. |
| 13 | Python test suite green | FAIL | 23 failed, 36 errors, 409 passed, 15 skipped. The failing set (59 IDs) is identical to the frozen baseline run on a clean export. Causes seen: Docker sandbox, model downloads, LFS pointer weights, one documented known failure. |
| 14 | New tests pass | PASS | 80 passed, 1 skipped (needs materialised cross-encoder weights). |
| 15 | Frontend tests | PASS | 28/28. |
| 16 | Live-LLM and human evidence | FAIL (absent) | None exists. The paper says so in the abstract, method, limits and conclusion. |
| 17 | Author information record for camera-ready | NOT VERIFIED | Not part of the repository; the authors must supply it outside the blinded PDF. |
| 18 | CMT upload, declarations, ethics/AI-use statement | NOT VERIFIED | Not performed. |

---
## Addendum 2026-10-02 (end-to-end audit cycle; history above preserved)
Superseding details are in `APPLICATION_END_TO_END_AUDIT.md` (addenda 1 and 2), `FINAL_CHANGELOG.md` and `FINAL_INDEPENDENT_AUDIT.md`. Summary: the multi-agent layer is now reachable in the shipped backend through the server-side `PREPAIRED_MULTIAGENT` variable (default off; commit 3dbb4ed); both end-to-end sessions (flag off/on) completed with 40 feedback events each (0 vs 40 coaching plans) using a recorded-evaluator substitute; fresh regression: frozen 306/14/23/36, HEAD 421/15/23/36 with the identical 59 failing IDs; frontend 28/28 and build OK; post hoc leave-one-cluster-out analysis added (k=1 is influential; the level-change interval excludes zero only with all eight sets or without k=1); paper 19 pages, claim audit 69/69, blind audit clean. Still open: official CFP/template, full-text reference checks and similarity check, real evaluator/live LLM/human evidence, two-agent necessity, author decisions listed in `FINAL_SUBMISSION_CHECKLIST.md`.
