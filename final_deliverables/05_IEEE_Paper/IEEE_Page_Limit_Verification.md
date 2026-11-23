# IEEE Page-Limit Verification

**Deliverable:** `Final_IEEE_Paper_Anonymous.pdf`
**Requirement:** strict maximum of six (6) pages, including references, no cover page, no appendix.

## Method used

1. The paper was built as `Final_IEEE_Paper_Anonymous.docx` from the official IEEE conference Word template (`paper/manuscripts/venue/ICETC_P1/template_official/template.docx` — the same official template already used and venue-confirmed elsewhere in this project's paper workspace), using a direct OOXML content-replacement script adapted from this project's own proven build pipeline (`paper/manuscripts/venue/ICETC_P1/build_icetc_docx.py`, which previously produced a real, visually-QA'd, 5-page IEEE submission for this project).
2. The built `.docx` was opened in Microsoft Word via COM automation, `Document.Repaginate()` was called to force a full, current pagination pass (not a cached/stale count), and `Document.ComputeStatistics(wdStatisticPages)` was read directly — this is Word's own authoritative page count for the document as it would print/export, not an estimate.
3. The document was then exported to PDF (`Document.ExportAsFixedFormat`, PDF format) from that same paginated state, so the exported PDF's page count matches the measured count by construction.
4. The exported PDF was independently re-opened and every page was rendered to an image and visually inspected (see `IEEE_Paper_Quality_Audit.md` — Visual Review) to confirm the page count and the absence of a stray trailing/blank page.

## Result

| Build pass | Body words (before References) | Word's `ComputeStatistics(wdStatisticPages)` | Figures | Tables |
|---|---|---|---|---|
| Prior (system-testing-summary subsection only) | 3,652 | 5 | 3 | 3 |
| Intermediate (2026-11-13, Table IV + limitations sentence added, not yet trimmed) | 3,765 (3,840 incl. headings/captions) | 6 — **page 6 found nearly empty (only refs [11]-[15]), flagged and corrected** | 3 | 4 |
| **Current (2026-11-13, final, rebalanced)** | 3,635 (3,721 incl. headings/captions per Word's count) | **5** | 3 | 4 |

**The current `Final_IEEE_Paper_Anonymous.pdf` contains exactly 5 pages**, confirmed directly by Word's own pagination engine (`Repaginate()` + `ComputeStatistics(wdStatisticPages)`), not estimated, and visually re-inspected page-by-page (rendered to images) to confirm a clean, fully-balanced final page with no stray near-empty page. The intermediate 6-page build (Table IV added without trimming elsewhere) produced a page 6 that was almost entirely blank -- only references [11]-[15] in the top-left corner -- a genuine "unexpected blank page / severe column imbalance" defect. It was corrected not by removing the new evidence (Table IV and the Limitations addition are both still present) but by tightening wording elsewhere (Related Work, Implementation Details, and the two new additions themselves), bringing the body back under the page-5 threshold. This is **within** the required 6-page maximum, with a small, normal amount of headroom remaining.

**Build note:** this rebuild used the same proven pipeline as the prior 5-page build (`build_ieee_system_paper.py`, adapted from `paper/manuscripts/venue/ICETC_P1/build_icetc_docx.py`, same official IEEE template), re-run after editing the source Markdown (`ieee_system_paper.md`) to add a new Table IV ("Post-deployment verification evidence") to §VII-D and one sentence to §VII-E (Limitations), reflecting evidence from a later, separately-scoped engagement phase (`testing_and_evaluation/final_evaluation/`). Figure 1 (architecture) was also regenerated with functional-group color-coding and a legend for improved readability; its underlying 9-component topology and arrow set are unchanged from the verified original.

## Why content was not padded to force exactly 6 pages

An earlier, shorter draft of this paper (before the "System Testing Summary" subsection and its supporting table were added) also measured at 5 pages, with roughly 40% of the final page's second column empty. Content was deliberately expanded once — adding a genuinely new, evidence-backed subsection (§VII-D, system testing results not covered elsewhere in the paper) rather than restating existing material — to make better use of the page budget, consistent with the task's "manage the page budget intelligently" instruction. After that addition, the final page is well-filled (see the rendered page images in the quality audit) with only a small, normal amount of trailing white space after the reference list, which is typical and expected for a reference-list-terminated two-column IEEE page and was not artificially padded further. No font size, margin, line spacing, or figure size was altered from the official template's own defaults to manipulate the page count in either direction.

## No cover page or extra pages

The built document contains no separate title/cover page — the title, anonymous author block, abstract, and keywords all appear at the top of page 1 in the standard one-column IEEE title-block layout before the two-column body begins, exactly as the official template specifies. No appendix, supplementary section, or extra reference page exists beyond the single `References` section that ends on page 5.

## Note on the LaTeX source

`Final_IEEE_Paper_Source.tex` is a content-equivalent secondary artifact. No LaTeX distribution (`pdflatex`/`xelatex`/`latexmk`) was available in the environment used to build this deliverable, so the `.tex` file has **not** been locally compiled and its resulting page count has **not** been verified by this process. `Final_IEEE_Paper_Anonymous.pdf` (from the Word-template build above) is the authoritative, page-verified deliverable. Before relying on the `.tex` file for submission, compile it with a standard IEEEtran installation and re-run this same verification procedure — font metrics and line-breaking differ between the Word and LaTeX toolchains, so page-count parity should not be assumed without checking.
