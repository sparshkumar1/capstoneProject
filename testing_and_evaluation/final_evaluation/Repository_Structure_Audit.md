# Repository Structure Audit — Final Evaluation Phase (Phase 3)

**Method, per instructions:** the complete existing tree was inspected before any organizational change was proposed. No file was moved, renamed, or deleted as part of producing this audit — this document is read-only output. Any actual changes made as a result are recorded separately in `Repository_Organization_Changes.md`, and are deliberately minimal.

## 1. Current Top-Level Structure (as inspected)

| Directory | Purpose (confirmed by inspection, not assumed) | Verdict |
|---|---|---|
| `agents/` | Application source: orchestrator, audio pipeline, coding executor, question selector, strategy (RL), timing, validation, feedback agent | Keep as-is — this is the application's real module home and is already well-organized by responsibility |
| `apps/backend/`, `apps/web/` | FastAPI backend and React frontend source | Keep as-is |
| `services/evaluator/`, `services/qwen/`, `services/storage/` | The three standalone microservices plus the shared persistence module | Keep as-is |
| `rl/` | RL environment, guardrails, training scripts, checkpoints | Keep as-is — this is exactly the "RL-related tests and infrastructure" the instructions emphasize preserving; confirmed intact, nothing moved |
| `tests/` | The 25-file backend pytest suite (21 unit + 4 integration) | Keep as-is — established, working, discoverable via `pytest tests/` |
| `testing_and_evaluation/` | This engagement's test strategy, baseline results, category-specific test scripts (`rl_evaluation/`, `ml_evaluation/`, `api_tests/`, `database_tests/`, `security_privacy/`, `compatibility/`, `ui_tests/`, `performance_tests/`), logs, and (as of this phase) `final_review/`, `final_evaluation/` | **Remains the single authoritative location** for this project's testing documentation and evidence, per instructions — no competing copy created |
| `testing_output/` | This engagement's earlier comprehensive module/integration/E2E testing report, its own scripts/, logs/, Testing_Evidence/, and 4 required CSVs | A **second**, separate testing-evidence directory from `testing_and_evaluation/` — see §3 for the specific, minimal recommendation |
| `scripts/` (repo root) | Setup scripts (`setup_env.sh/.bat`), a paper-reproduction script (`reproduce_paper.py`), Qwen model download, and **10 pre-existing `verify_*_e2e.py` / `verify_whisperx_runtime.py` / `verify_qwen_live.py` / `verify_live_browser_flow.py` scripts** — real, pre-existing E2E-style verification harnesses from this project's development history, confirmed by reading `verify_live_browser_flow.py` in full this phase: despite its name, it drives the real API/WebSocket surface directly (no Selenium/Playwright), the same category of evidence as this engagement's own `testing_output/scripts/e2e_harness.py`, not literal browser automation | **A real, previously-unexamined asset** — see §3 |
| `testing_and_evaluation/scripts/` | **Not test scripts** — confirmed again this phase (unchanged finding from the prior audit): 4 document-formatting utilities (`export_to_pdf.py`, `fill_pptx_template.py`, `md_to_docx_report.py`, `md_to_docx_ieee_paper.py`) for `final_deliverables/` | Misleadingly named relative to its contents — see §3 |
| `research/` | Frozen Paper 1/2/3 evidence, audits, claim registry, confirmatory experiments | Keep as-is, untouched — explicitly protected by this project's own long-standing rules |
| `ablation/`, `experiments/` | Legacy ablation results and experiment runners | Keep as-is, untouched |
| `data/`, `models/` | SQLite DB, question/rubric JSON, the Qwen GGUF model and CrossEncoder checkpoint | Keep as-is |
| `docs/` | A large set of partly-superseded historical documents (already flagged as such by this project's own `CLAUDE.md`) | Out of scope for this phase — not touched |
| `paper/`, `final_deliverables/`, `Independent_Project_Audit/`, `reference_material_analysis/`, `Details/` | This engagement's and a prior session's academic-deliverable workspaces | Keep as-is, untouched — each already has its own internal organization established earlier in this engagement |
| `ADCOM2027_Track2_Final/`, `capstonePapers/`, `submission/` | Prior, separate paper-track artifacts (the `ADCOM2027`/`capstonePapers` lineage was independently confirmed, in this engagement's own earlier audit, to describe a fictional architecture not present in the codebase) | Out of scope for this phase — not touched, not deleted (preserving historical material per instructions, even where its content has already been flagged as not applicable to the real system) |
| `orchestrator_logs/` | Per-session execution logs from real and test runs | Keep as-is |
| `tools/` | A single file, `toy_mode.py` | Keep as-is — too small to warrant restructuring |
| `.claude/`, `.github/`, `.pytest_cache/` | Tooling configuration, CI, pytest cache | Keep as-is, not application-relevant |

## 2. Git Status Check (performed before any change this phase)

Confirmed clean relative to the audited snapshot: same commit (`9d5c528`), same two pre-existing uncommitted files (`launch.py`, `rl/guardrails.py`). This phase's own four code changes (`Application_Code_Changes.md`) and new documentation files are additive, on a separate branch (`final-eval/controlled-improvements`), not mixed into main's working tree in a way that could be confused with pre-existing uncommitted work.

## 3. Specific, Justified Organizational Observations (not all acted on — see `Repository_Organization_Changes.md`)

1. **`testing_and_evaluation/scripts/` is misleadingly named.** It contains zero test automation. This was already flagged, not fixed, in the prior audit. **This phase's recommendation:** add a one-line `README.md` inside that specific folder stating its real purpose (document-formatting utilities for `final_deliverables/`), rather than moving the files — moving them risks breaking `final_deliverables/`'s own generation workflow, which was out of scope to verify exhaustively this phase. A README is the minimum change that removes the misleading impression without any risk of breaking a working path.

2. **Two separate, non-identical testing-evidence trees exist** (`testing_and_evaluation/` and `testing_output/`), created in different sessions of this same engagement, for genuinely different scopes (the former is this project's long-running testing package; the latter is a self-contained module/integration/E2E exercise with its own CSV deliverables explicitly requested as a separate package by an earlier instruction in this engagement). **This phase's recommendation:** do **not** merge them — the earlier instruction that produced `testing_output/` explicitly required a "separate testing deliverables directory," and merging now would break that deliverable's own self-containment and its explicit file-path promises (e.g. `testing_output/Testing_Results_Master.csv`). Instead, add one cross-reference line in each directory's top-level context so a reader of one knows the other exists and why they're separate — see `Repository_Organization_Changes.md`.

3. **The repo-root `scripts/` directory's E2E-verification scripts were not previously cross-referenced from `testing_and_evaluation/`**, creating a risk that a reader auditing "all E2E evidence" would miss them. **This phase's recommendation:** add one line to `testing_and_evaluation/final_evaluation/04_End_to_End_Results.md` (already present, see above) and this document noting their existence and category — done, not requiring a file move.

4. **No root-level repository overview accurately describes the current structure** (the existing root `README.md` is already independently flagged, in this engagement's earlier `Independent_Project_Audit`, as containing stale badges/figures — a content-accuracy issue distinct from, and out of scope for, this phase's structural concerns). **Not fixed this phase** — correcting the README's content is a documentation-accuracy task already registered as a P0 item in the `Independent_Project_Audit`'s own improvement roadmap; duplicating that recommendation here would be redundant, not additive.

## 4. What Was Deliberately NOT Changed (and why)

Per the explicit "avoid unnecessary restructuring" instruction, this phase does **not**: rename any major directory; move the application into a `src/` layout; relocate `rl/`'s tests or checkpoints; touch `research/`, `ablation/`, or `experiments/`; change any import path; or introduce a new top-level testing framework. Every RL test file, checkpoint, and research artifact remains at its original path — confirmed by `git status` showing no deletions or renames anywhere in the tree as a result of this phase.
