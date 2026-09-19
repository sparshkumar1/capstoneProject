# X3-A deviations log

| # | Date | Event | Classification | Action |
|---|---|---|---|---|
| 1 | 2026-09-19 | First confirmatory launch (`results_attempt1_ABORTED_process_killed/`): gate G-HARNESS passed (9/9, `gate_G-HARNESS.csv`) and the manifest was written (`status: started`), but the process was terminated before `sessions.csv` was written (the launcher shell that hosted the background process exited). No session data, no result and no analysis output exist for this attempt. | Infrastructure interruption; not a scientific finding; no data seen. | Attempt retained unmodified; the run was relaunched with identical code, config, protocol tag and lock as a supervised background task (`results/`). No parameter changed. |
