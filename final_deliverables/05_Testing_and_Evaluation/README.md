# Testing and Evaluation Package — Index

The full testing and evaluation package lives at the repository root in **`testing_and_evaluation/`** (not duplicated here, to avoid maintaining two copies and risking them drifting apart — all internal cross-references between report chapters, the IEEE paper, and these documents point to that location).

## Contents of `testing_and_evaluation/`

| File/Dir | Contents |
|---|---|
| `Test_Strategy.md` | 22 testing categories + ML/RL evaluation, classified by relevance to this codebase |
| `Test_Priority_Matrix.md` | Concrete test IDs, objectives, acceptance criteria, execution status |
| `Component_Inspection_Map.md` | Verified module-by-module architecture map |
| `Requirements_to_Test_Traceability_Matrix.md` | 12 stated objectives mapped to evidence, final MET/unverifiable/blocked status |
| `Baseline_Record.md` | Environment, git commit, full baseline test-run provenance |
| `baseline_results/` | Full automated-suite results with root-cause attribution, smoke-test findings |
| `Phase4_Diagnosis_and_Fixes.md` | The two real defects found and fixed, with full diagnosis and verification |
| `Master_Results_Table.md` | **Single source of truth** — every number cited elsewhere traces back here |
| `Qwen_2.5_Evaluator_Validation_Report.md` | Full investigation: Qwen's actual role, verified by code, in the evaluation pipeline |
| `Qwen_2.5_Viva_Explanation.md` | Condensed, defend-in-the-room version of the above |
| `rl_evaluation/`, `ml_evaluation/`, `api_tests/`, `database_tests/`, `security_privacy/`, `compatibility/`, `ui_tests/`, `performance_tests/` | 11 independently runnable, newly authored test scripts/reviews, each with real logged output |
| `logs/` | Raw output logs for every test run referenced anywhere in the deliverables |
| `scripts/` | Markdown-to-DOCX/PPTX conversion scripts used to generate the final report/paper/slides |

Every claim in `final_deliverables/02_University_Project_Report/`, `03_Research_Paper/`, and `04_Final_Presentation/` traces back to a file in this package.
