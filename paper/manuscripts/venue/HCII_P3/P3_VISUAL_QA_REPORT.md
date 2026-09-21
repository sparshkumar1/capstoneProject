# P3 — visual and automated QA report (2026-09-21)

**Overall status: BLOCKED for the full paper (no Springer/HCII template applied; author-confirmation placeholders remain in the Declarations). Proposal text: PASS on the checks that apply.** This report does not make either P3 item submission-ready.

## What exists and what does not
- **Proposal** (`proposal_text.txt`, embedded in `P3_HCII_PROPOSAL_FINAL.md`): the submitted representation is text entered into HCII's proposal form. A preview PDF was generated only to inspect it visually.
- **Full paper** (`P3_FULL_MANUSCRIPT_READY.md`): Markdown only. The Springer/HCII template is not available or applied, so there is **no template-format DOCX/PDF and no page count**. A generic single-column layout preview was generated (`preview/P3_full_PREVIEW.pdf`, from `audit_v2/preview_md_to_html.py` through Word) purely to inspect headings, tables, figures and references. **Its page count says nothing about the paper's length in the Springer template and is deliberately not recorded.** Official range: 10–20 pages, typically 12. Any earlier page estimate stays withdrawn.

## Defects found by inspecting rendered pages, and fixes made at the source
| # | Defect | Cause | Fix |
|---|---|---|---|
| 1 | Fig. 1: the dashed lines at −0.12 and +0.12 and the dotted line at −0.20 struck through their own labels ("−0.12" looked like "−0.2 2") | labels centred on the lines | labels now sit beside the lines (`figures/make_fig_p3.py`) |
| 2 | Fig. 2: the labels "Matched, no change" and "Overridden" ran together | label positions overlapped | "Matched,\nno change" on two lines, centred on its bar |
| 3 | Fig. 3 (right): the dashed Constant-Same line struck through the "pooled 0.0776" label | no label background | white label background |
| 4 | References rendered as one run-on paragraph | one reference per line without blank lines; Markdown merges them | `_build_full_manuscript.py` now writes one paragraph per reference; the text is otherwise identical (only blank lines changed; body 5,283 words, abstract 240 words) |

The three figures were re-plotted from the same stored files by the same script; the printed values are unchanged (563 activations, 99 overrides, 464 no-ops; all eight intervals as before). No analysis was rerun.

## Results
| Check | Full paper (preview) | Proposal (preview) |
|---|---|---|
| Source document | `P3_FULL_MANUSCRIPT_READY.md` | `proposal_text.txt` |
| Output PDF | none in template format; layout preview only | layout preview only (2 pages of generic layout; not a form representation) |
| Page count | not measured (no template) | not applicable (word-limited: 762 of 800 words, references excluded) |
| Rendered-page inspection completed | partly: the first page, every page with a figure, table or the reference list, and the Declarations page were viewed after the fixes (pages 2, 4 and 10 of the preview, which are running prose, were not viewed). Repeat as a full every-page pass once the template is applied | yes |
| Title | PASS: exact title; no legacy title | title is entered separately in the form |
| Author block | PASS: names once each, in order, "Dept. of CSE, PES University", designation for Dr. Uma D only | not part of the text |
| Abstract / four HCII headings | abstract 240 words present; the proposal has the four official headings (Objective and significance; Methods and approach; Results and findings; Contributions and implications) | PASS |
| Headings and numbering (1–14) | PASS | |
| Figures | PASS after fixes 1–3 | |
| Tables (1–4) | PASS: complete, readable, none clipped | |
| References | PASS after fix 4: 14 entries, Springer-style numeric, each cited; every citation resolves | |
| Placeholders / draft text | **FAIL: Declarations still carry author-confirmation brackets** (authors' contact details, ethics confirmation, AI-use statement, availability, competing interests) | PASS (none) |
| Metadata | not applicable (no template PDF) | not applicable |
| Column/margin overflow, overlap | PASS (automated checker: nothing outside a 30 pt margin; no overlapping words) | PASS |
| Terminology (simulation only; equivalence not superiority; "application-level rule-based guardrail"; activations ≠ interventions; PPO not "better") | PASS on the text read; no PPO-superiority, learner-benefit or real-user claim | PASS |
| Cross-version consistency (proposal vs full paper: title, RQ, numbers) | PASS: same Δ −0.0350, interval [−0.0818, +0.0021], margin ±0.12, superiority −0.20, 563 / 99 / 464, 41 of 125, 50 / 25 / 5; volatility +0.149 (rounded from 0.14877) in the proposal | |

## Before P3 can be called submission-ready
1. Authors confirm or supply the Declarations content (no placeholder may remain).
2. Apply the Springer/HCII template when available, export, render every page, run the checker, record the real page count here.
3. Re-inspect all pages after any layout change.
4. Proposal: the authors enter it in the form and verify what the form actually asks for (fields and any separate abstract limit are unverified).
