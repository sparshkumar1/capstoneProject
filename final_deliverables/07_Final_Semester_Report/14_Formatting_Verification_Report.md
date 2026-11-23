# 14. Formatting Verification Report — Phase-3 Final Semester Report

**Purpose:** record whether, and how, the final document was actually checked against
`Details/Report-  Guidelines.pdf`'s mandatory formatting rules — not merely asserted to comply.

## 1. Build method

The 13 Markdown chapter files in this folder were converted to `.docx` using
`final_deliverables/07_Final_Semester_Report/build_final_report.py` — a direct copy of the project's own
existing, already-proven builder (`testing_and_evaluation/scripts/md_to_docx_report.py`, used unmodified to
build `final_deliverables/02_University_Project_Report/PrepAIred_Phase3_Report.docx`), re-pointed at this
folder's files and output path only. The docx was then exported to PDF via Microsoft Word COM automation
(`Document.ExportAsFixedFormat`), the same method used throughout this engagement for every other Word-based
deliverable, so the exported PDF's layout matches the editable `.docx` by construction.

## 2. Guideline-rule-by-rule check (against `Details/Report-  Guidelines.pdf`, rules 1–23)

**Revision note (this pass):** the user directly asked whether every rule had actually been followed. Re-reading
the guideline PDF's literal text against the build script at that point found two rules previously marked
"Partial" were now satisfiable and have been fixed (12; 20–21, which a prior pass had wrongly marked N/A), and
surfaced one genuine, concrete miss that had not been caught before: **there was no header at all**, and the
footer did not match the required three-way layout. Both are now fixed and re-verified below, not just reworded.

| Rule | Requirement | Verified how | Result |
|---|---|---|---|
| 1 | A4, 1.5 line spacing, 2.00cm margins (L/R/T/B) | Read directly from `set_doc_defaults()`/`configure_chapter_section()`: `Cm(2.0)` on all four margins on every section (front matter and every per-chapter section); `line_spacing = 1.5` | **Pass** |
| 8 | Chapters numbered in Arabic numerals | Each chapter file's own `# Chapter N: ...` heading, visually confirmed in the rendered PDF | **Pass** |
| 9 | Sections/subsections in decimal form (4.1, 4.2; 4.1.1 etc.) | Every chapter file's `##`/`###` headings use this convention throughout | **Pass** |
| 10 | Chapter title centered, size 18; section/subsection left-justified, 16/14 | Read directly from `add_heading()`: level-1 → `Pt(18)` centered; level-2 → `Pt(16)` left; level-3 → `Pt(14)` left. Visually confirmed | **Pass** |
| 11 | Times New Roman; 1.5 spacing (text only); body justified, size 12 | Read directly from `set_doc_defaults()`/`add_body_paragraph()`. Visually confirmed on every chapter page | **Pass**, with one disclosed, deliberate non-conformance: the guideline document is internally self-contradictory — its "Details" table says Title/Subtitle should be "12 (Bold and Underline)," "Bookman Style," left-justified, while its own "Content organization" bullets immediately below unambiguously specify Chapter=18pt centered / Section=16pt / Subsection=14pt left, which is what rule 10 also states. This build follows the unambiguous, twice-stated 18/16/14/12 rule, not the Bookman/underline clause — confirmed this is also what the real Phase-2 PDF actually does (direct visual inspection of `revised_report_v5.pdf`'s own "Chapter 1 :Introduction" page: bold serif, not Bookman, no underline) |
| 12 | Figures and tables numbered chapter-wise | **Fixed in this pass.** 12 tables and 3 figures now carry explicit "Table N.M."/"Figure N.M." captions in the chapter Markdown (e.g. `04_Chapter4_PRS.md` "Table 4.1. Functional requirements."), each cross-checked via a Word COM pass that located the caption text and confirmed its real page number matches the List of Tables/List of Figures entry. Visually confirmed on the rendered PDF (List of Tables page; Chapter 5/8 figure pages) | **Pass** |
| 13 | Conclusion chapter must reference plan-of-work carried from Capstone-2 | Chapter 11, §11.6, states the carried-forward plan of work. **Caveat not previously disclosed:** the guideline's exact wording is "the plan of work carried out in Capstone-2" (i.e. what Phase-2 itself proposed as future work), not merely "work this phase hands off to a future phase." Chapter 11 does the latter explicitly; whether it also explicitly maps back to Phase-2's own stated future-work items was not independently re-checked in this pass | **Pass on the literal text present; the backward-mapping nuance is flagged, not verified either way** |
| 14 | References numbered serially, cited in square brackets, IEEE style | Chapter 12 uses `[1]`…`[16]`, IEEE reference format | **Pass** |
| 15 | SI units; equations numbered in decimal form | The report's formulas (evaluator weighted score, reward function, guardrail conditions) remain inline/in code blocks, not separately numbered display equations (e.g. no "(1)", "(2)") — **still not fixed in this pass**; genuinely not addressed, not merely re-labelled | **Partial — flagged, not silently passed** |
| 16 | No verbatim reproduction without quotation/citation | Phase-2 prose reused in this report was paraphrased/adapted, not block-quoted; `revised_report_v5.pdf` is cited by name throughout | **Pass** |
| 17 | Grammar/spelling correctness | No automated spellcheck or grammar tool was run against the final text in any pass of this engagement | **Not verified — no tool-based check was ever performed; do not read the absence of a row above as a pass** |
| 19 | Project report must be hard-bound | Physical binding of a printed copy — outside what an AI-produced document can verify | **N/A to this deliverable — flagged for the user** |
| 20 | Cream outer cover, plastic cover; **Header: left=project title, right=institution logo; Footer: left="Dept of CSE", middle=semester date range, right=page number** | **The header/footer half of this rule was wrongly marked N/A in the previous pass of this document — that was incorrect:** a header and a specific three-column footer layout are both things an AI-produced `.docx` genuinely can implement, and the previous build did not implement the header at all and got the footer's column layout wrong (page number was alone on its own line, not in a right-aligned column alongside Dept of CSE/date). Both are now implemented via `configure_chapter_section()`/`_fill_header()`/`_fill_footer()` and visually confirmed on a rendered body page (header: italic project title left, PES University logo right; footer: "Dept of CSE" / "August - Dec, 2026" / page number, in three tab-stopped columns). The cover colour/material remains physical-only and out of scope | **Header/footer: Pass (corrected this pass). Cover colour/material: N/A to this deliverable** |
| 21 | Chapter's opening page: footer only, no header; header+footer start from the Introduction chapter | **Also corrected in this pass.** Each of the 12 chapters now occupies its own Word section with `different_first_page_header_footer=True`: the chapter's first page has an empty header and the normal three-column footer; every later page in that chapter has both. Visually confirmed: Chapter 1's opening page (no header, footer present) vs. its next page (header present) | **Pass (corrected this pass)** |
| 22–23 | Plagiarism check, repository upload | User actions, not content-formatting rules | **N/A to this deliverable — flagged for the user** |

## 3. What "verified" means here, concretely

Every "Pass" row above was checked by one of two methods, stated per row: (a) reading the exact line of the build
script that enforces the rule, or (b) visually inspecting the rendered PDF page image for that specific property.
Rows 15 and 17 are reported as not (fully) satisfied because that is genuinely true of the current build, not a
wording choice — claiming "Pass" there would be a formatting claim not backed by an actual check. Rows 12, 20, and
21 were previously mis-assessed (12 as a merely-known, unfixed gap; 20–21 as flatly N/A, which undersold what was
actually achievable); this pass corrected the document code, re-ran the Word-COM page-number verification pass,
and visually re-inspected the result, rather than just correcting the wording of this report in isolation.

## 4. Page count and visual integrity

The exported PDF (`PrepAIred_Phase3_Final_Report.pdf`) is **71 pages**, up from the 64 pages before this pass's
figure/table/header/footer additions. Regions visually inspected in this pass, beyond what prior passes already
checked: the Certificate page (confirmed the "External Viva" block now fits entirely on one page, a separate
user-reported defect fixed earlier in this engagement), the List of Figures and List of Tables pages (confirmed
real, non-placeholder page numbers matching the actual chapter pages), Chapter 5's and Chapter 8's new figure
pages, and a chapter-opening page vs. a chapter-continuation page side by side (confirming the header/footer
rule). A full page-by-page visual QA pass across all 71 pages is still not claimed as done.

## 5. What this report does not, and cannot, verify

Physical binding, cover material and colour, and plagiarism-check percentage are not — and cannot be — verified
by this process; they require the user's own action before final submission. Grammar/spelling (rule 17) has
never been run through an automated checker in this engagement and is listed above as genuinely unverified,
not assumed clean.
