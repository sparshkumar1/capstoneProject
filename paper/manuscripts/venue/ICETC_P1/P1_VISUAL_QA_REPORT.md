# P1 — visual and automated PDF QA report (2026-09-21)

**Source document:** `venue/icetc2026/ICETC_PORT_MANUSCRIPT.md` → `build_icetc_docx.py` → official ICETC IEEE Word template (`template_official/template.docx`) → Word 16 export (`export_pdf_and_count.ps1`).
**Output PDFs:** `P1_ICETC_BLINDED.pdf` (upload candidate) and `P1_ICETC_MASTER_author_identifying.pdf` (internal master; never uploaded).
**Method:** (A) `audit_v2/pdf_qa_check.py` (text, margins, overlapping words, placeholders, author-name counts, repeated lines, metadata/XMP, raw-byte scan); (B) every page of both PDFs rendered at 130 dpi and inspected by eye after the final build. The pages were re-inspected after each of the five layout fixes below, and the last full pass was on the final build. A PDF passes only if both A and B pass.

## Defects found on inspection of the earlier build, and how each was fixed at the source
| # | Defect (earlier build) | Cause | Fix (in the build, not in the PDF) |
|---|---|---|---|
| 1 | Master page 1: author block misaligned (first author's lines sat higher than the others; affiliations crowded the abstract) | five-column section with column breaks | replaced by a one-row, five-cell borderless table with top-aligned cells, inside the one-column title section, followed by a spacer that ends that section |
| 2 | Master page 5: unresolved "AUTHOR CONFIRMATION REQUIRED" text in the acknowledgment | AI-use placeholder rendered into the master | no rendered copy has an acknowledgment or placeholder now; the open disclosure question is recorded in `P1_ICETC_READINESS.md` and the checklists only |
| 3 | Section VIII heading: numeral ran into the title ("VIII.REPRODUCIBILITY") | the template's numbering tab is narrower than "VIII." | tab override for that heading only; heading shortened to "Reproducibility and Availability" so it centres like the others |
| 4 | Master: Table III split across pages 3–4 and "References" heading stranded at the bottom of a column | no keep-together rules | rows are `cantSplit` and keep with the next row; the References/Acknowledgment heading style keeps with the next paragraph |
| 5 | Blinded page 1: "Anonymous authors" line abutted the abstract; master Fig. 1 abutted the text above it | zero spacing | 6 pt after the author line; 8 pt before the figure |

A note on what could not be reproduced: the title clipping and duplicated author entries described in the brief did not appear in the PDFs rendered here (the title lies inside the margins on every build). The likely explanation is an earlier or different rendering of the DOCX; the current DOCX/PDF pair was checked as built and the defects that did appear are listed above. The PDF is what to upload; a DOCX opened in another word processor can lay out differently.

## Results for the final build
| Check | Blinded | Master |
|---|---|---|
| Page count (Word export, official template) | **5** | **5** |
| Rendered-page inspection completed | yes, pages 1–5 | yes, pages 1–5 |
| Title clipping | PASS (full title inside the margins) | PASS |
| Author-block duplication | PASS (no author block; one "Anonymous authors" line) | PASS (each of the five names appears exactly once; "PES University" five times, once per author; "Professor" once) |
| Author overlap | PASS (n/a) | PASS |
| Affiliation overlap | PASS (n/a) | PASS |
| Abstract overlap | PASS | PASS (clear vertical gap between the author table and the abstract) |
| Heading check (numbering, orphaned headings) | PASS | PASS |
| Figure/table clipping | PASS (Fig. 1 and Tables I–IV complete; no table splits across pages) | PASS |
| References (clipping, wrapping, overlap with text) | PASS (14 entries; none clipped) | PASS |
| Acknowledgment overflow | PASS (none present) | PASS (none present) |
| Placeholder / draft / AI-tool-name text in rendered PDF | PASS (0 hits) | PASS (0 hits) |
| Identifying metadata | PASS: no /Author, no /Title; XMP holds only producer, dates and an identifier; no personal path, e-mail domain, account name or institution anywhere in the file bytes | n/a (author-identifying by design; no e-mail, no personal path) |
| Column / margin overflow | PASS (all text and images inside a 30 pt margin; no overlapping words) | PASS |
| Repeated (duplicated) lines | PASS | PASS |
| Cross-version consistency | PASS: the blinded and master texts are generated from one source; they differ only in the author block; the numbers, tables and figure are identical | |

## Observations that are not defects
- Page 2 ends about 10 % short in both columns and page 5 is about 55 % empty. The first arises because the full-width Fig. 1 starts the next page; the second is the end of the paper. No content was added or removed to change either.
- In the master, Table III moves whole to page 4, which leaves some white space at the foot of page 3; this follows from keeping the table in one piece.
- Fig. 1 is an image (re-plot of stored per-run records); its labels are readable at print size but are small. It was not enlarged because that would push the page count.

## Final status
**Visual QA: PASS for both PDFs, 5 pages each.** This report does not make P1 submission-ready: the author-confirmation items (AI-use disclosure, whether git tags and short hashes stay in the blinded text, the template's "Authors' background" page, contact details) and the unverified ICETC rules listed in `P1_ICETC_READINESS.md` are still open. Any later edit to the manuscript, builder or template use requires a rebuild and a repeat of both checks.

Re-run: `python build_icetc_docx.py`, then `powershell -File export_pdf_and_count.ps1`, copy the two PDFs from `build/`, then `PYTHONPATH=<pymupdf dir> python ../../audit_v2/pdf_qa_check.py <pdf> --mode blinded|master --pages 5`, and inspect the rendered pages.
