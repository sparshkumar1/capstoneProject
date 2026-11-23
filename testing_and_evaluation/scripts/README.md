# This folder is not a test-automation directory

Despite its location under `testing_and_evaluation/`, this folder contains **document-formatting utilities**, not test scripts:

- `export_to_pdf.py` — exports generated `.docx`/`.pptx` deliverables to PDF via Microsoft Office COM automation.
- `fill_pptx_template.py` — fills the PES University PPT template with project content.
- `md_to_docx_report.py` — converts the Markdown report chapters into a formatted `.docx`.
- `md_to_docx_ieee_paper.py` — converts the IEEE paper draft Markdown into an approximated two-column `.docx`.

All four support generating `final_deliverables/`. None of them execute, test, or validate any part of the PrepAIred application.

Actual test scripts for this project live in:
- `tests/` (repo root) — the main pytest/Vitest suites.
- `testing_and_evaluation/rl_evaluation/`, `ml_evaluation/`, `api_tests/`, `database_tests/` — the category-specific scripts referenced throughout `testing_and_evaluation/`'s own documents.
- `testing_output/scripts/` — the module/integration/E2E harness from the dedicated comprehensive testing exercise (see `testing_output/PrepAIred_Comprehensive_Testing_Report.pdf`).
- `scripts/` (repo root) — pre-existing `verify_*_e2e.py` API/WebSocket-driven verification harnesses from this project's development history.

*Added during the final-evaluation phase; see `testing_and_evaluation/final_evaluation/Repository_Structure_Audit.md` and `Repository_Organization_Changes.md` for why this file was added and what was deliberately left unchanged.*
