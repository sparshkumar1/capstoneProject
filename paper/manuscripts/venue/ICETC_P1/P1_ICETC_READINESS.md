# P1 — ICETC 2026 readiness (master pass, 2026-09-21)

No submission, commit, push or tag. No experiment, rerun or new analysis. Frozen files untouched.

**Exact title:** Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System (the legacy PrepAIred title is not used).

## Status
| Item | Status |
|---|---|
| Template | Official ICETC IEEE Word template (`template_official/template.docx`, from icetc.org/files/); body rebuilt with the template's own styles and numbering by `build_icetc_docx.py` |
| **Exact PDF page count** | **5 pages** for both the blinded copy and the author-identifying master (Word 16.0 export of the official template; the last page carries the conclusion and references only, columns balanced). Minimum 5 met; no extra-page charge under either reading of the two official pages. The count was not adjusted by padding or trimming |
| Blinded copy | `P1_ICETC_BLINDED.pdf/.docx/.md`; anonymisation checked (`P1_ICETC_ANONYMIZATION_CHECKLIST.md`) |
| Author-identifying master | `P1_ICETC_MASTER_author_identifying.pdf/.docx`, `P1_ICETC_MANUSCRIPT_READY.md`: authors in the supplied order with designation and affiliation, in a one-row author table; no acknowledgment and no placeholder text in any rendered file (the open AI-use disclosure question is tracked below, not in the PDF) |
| Visual QA | Rendered pages of both PDFs inspected by eye and automated checks run on the final build: PASS, 5 pages each. See `P1_VISUAL_QA_REPORT.md` |
| Education / assessment fit | A short introduction paragraph now ties the pipeline to technical-interview practice and assessment integrity and states that no learning, grade, usability or outcome measure is reported; "learning outcomes" added to the not-evaluated list. No number changed |
| Figures and tables | 1 figure and 4 tables; numbering automatic; every table and the figure is now cited by number in the text; the figure re-plots stored per-run records (`figures/make_fig_p1.py`, `cross/FIGURE_PROVENANCE.md`) |
| References | 14; every one is cited and every citation resolves; existence and metadata checked earlier (`audit_v2/REFERENCE_AUDIT.md`); unverified venues and abstract-level readings are labelled in the list |
| Numbers | 0 numbers in the blinded copy absent from `paper1/manuscript.md`; all X1 counts unchanged |
| Statistics | none inferential; "k/5" is stated to be a repeatability count |
| Prose pass | templated "Shows / Does not show" discussion scaffolding rewritten as plain prose; a sentence about an unavailable tool review removed; one shared sentence with P2 and one opening phrase reworded; meaning and numbers unchanged |
| SEC-05 | five attacks with identical executor status (SEC-02, -05, -07, -08, -09); SEC-05 separated by execution time; frozen note not edited (`paper1/P1_SEC05_RECONCILIATION.md`) |

## What is not settled
1. **AI-use disclosure:** none in either rendered copy; ICETC's own rule not found (IEEE's policy for IEEE-published proceedings places such a disclosure in the acknowledgments); the facts (tool, version, sections affected, level of author review) are unconfirmed (D-4). If ICETC or IEEE requires a disclosure, the authors supply the confirmed facts and it is added to the master and, if the rules allow it without revealing identity, to the blinded copy; nothing is drafted for them.
2. **Git tags and hashes** in the blinded text (checklist item 10; not resolvable publicly today).
3. **Template's "Authors' background" page** (checklist item 11).
4. ICETC camera-ready date, prior-submission rule and fee: not found.
5. Author e-mail addresses, ORCID iDs, city and country: not supplied and not invented (only needed for the master and the camera-ready).
6. The page count is Word's rendering of this file; submit the exported PDF unchanged.

## Verdict
The blinded PDF is complete as a manuscript. Before upload the authors must settle items 1–3. No acceptance prediction.
