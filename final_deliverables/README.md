# PrepAIred — Phase-3 Final Deliverables

Everything in this directory was produced in a single testing-and-documentation phase built on top of the existing Phase-2 implementation. **No source code outside `rl/guardrails.py` and `launch.py` was modified** (both changes are documented, minimal, user-approved, and regression-verified — see `05_Testing_and_Evaluation` → `Phase4_Diagnosis_and_Fixes.md`).

## Directory guide

| Directory | What's in it | Status |
|---|---|---|
| `02_University_Project_Report/` | Full PES Phase-3 project report: front matter + 11 chapters + bibliography, as Markdown source, `.docx` (formatted per the PES guidelines), and `.pdf` | Content, formatting, and visual inspection complete; 2 citations and the front-matter team/guide details need your confirmation |
| `03_Research_Paper/` | IEEE-style paper (Markdown source, `.docx`, `.pdf`), rescoped to the real, verified system | Content, formatting, and visual inspection complete; target venue and 2 reference placeholders need your input |
| `04_Final_Presentation/` | `PrepAIred_Phase3_Review3.pptx`/`.pdf` (built directly from your supplied template, all 16 slides populated, 9 slides have speaker notes) + the source content/notes document | Content, formatting, and visual inspection complete; Slide 4 (panel feedback) and Slide 6 (live demo) are explicit placeholders needing your input |
| `05_Testing_and_Evaluation/` | Index pointing to the full testing package at the repo root (`testing_and_evaluation/`) | Complete |
| `06_Supporting_Documentation/` | Viva preparation document (likely panel questions + honest answers) | Complete |
| `FINAL_ACADEMIC_DELIVERABLE_COMPLETION_CHECKLIST.md` | Requirement-by-requirement completion status | Complete |

## The one-paragraph summary, if you only read one thing

This phase ran a complete, evidence-graded testing programme on PrepAIred (264/283 automated tests passing, every failure attributed), found and fixed two real defects (a guardrail safety gap and a Windows launcher crash), found and corrected nine factual discrepancies between the prior project report and the actual code (most notably: question selection isn't FAISS-based, the evaluator is Flask not FastAPI, and Qwen never touches the numeric score), and used all of that as the evidentiary basis for a complete university report, a rescoped and honestly-scoped IEEE paper, and a presentation deck — all generated as real, structurally-verified `.docx`/`.pptx` files, not just Markdown drafts.

## Related repository locations (not duplicated here)

- `testing_and_evaluation/` — the full testing package (scripts, logs, results)
- `reference_material_analysis/` — Phase-1 analysis of the supplied reference documents, including the citation-verification work and the research-paper scope decision
- `rl/guardrails.py`, `launch.py` — the two files modified in this phase, with inline comments explaining the fix

## Outstanding items requiring you (not blockers to anything else)

See `FINAL_ACADEMIC_DELIVERABLE_COMPLETION_CHECKLIST.md`'s "Outstanding items" section for the complete list. In short: confirm Phase-3 team/guide details, supply Review-2 panel feedback, supply or help script a live demo, resolve two flagged literature references, and decide whether to start Docker Desktop and/or commit the two code fixes.
