# testing_and_evaluation/ — scope note

The project's **authoritative, ongoing** testing and evaluation documentation package — the single place to look for current test strategy, baseline results, and category-specific test scripts. (For the separate, self-contained comprehensive-testing-report deliverable, see `testing_output/README.md` instead — the two are intentionally not merged.)

## Top-level documents

| File | Contents |
|---|---|
| `Test_Strategy.md` | The project-specific testing-category classification this package follows |
| `Master_Results_Table.md` | **Single source of truth** for test results — append-only; never overwritten, see its own in-file history |
| `Baseline_Record.md` | Environment/command record for reproducing results |
| `Requirements_to_Test_Traceability_Matrix.md`, `Test_Priority_Matrix.md`, `Component_Inspection_Map.md` | Coverage/traceability matrices |
| `Phase4_Diagnosis_and_Fixes.md`, `Qwen_2.5_Evaluator_Validation_Report.md`, `Qwen_2.5_Viva_Explanation.md` | Specific investigation write-ups |

## Subdirectories

| Directory | Contents |
|---|---|
| `rl_evaluation/`, `ml_evaluation/`, `api_tests/`, `database_tests/`, `security_privacy/`, `performance_tests/`, `compatibility/`, `ui_tests/` | Category-specific test scripts, each independently runnable |
| `final_review/`, `final_evaluation/` | A later, separately-scoped engagement phase's extended evidence and analysis (14+ documents) |
| `baseline_results/`, `logs/` | Raw captured output from test runs |
| `scripts/` | **Document-formatting utilities used to build the academic deliverables, not test scripts** — see `scripts/README.md`. Do not confuse these with the actual test scripts above. |

No file in this directory is imported by application code; `tests/` (project root) holds the pytest/Vitest suites that are.
