# Final Testing Strategy — Final Evaluation Phase

## Why these tests, specifically, for this architecture

This phase does not run a generic 22-category checklist. Every test or investigation below was selected because it answers a specific, open question this project's own prior evidence record (the `Independent_Project_Audit` and the comprehensive testing report produced earlier in this engagement) left unresolved:

| Question left open | Test/investigation this phase runs | Why it is the right test |
|---|---|---|
| Are the two flagged numeric pairs (0.4825/0.4832, 0.4897/0.4884) really inconsistent? | Direct reconciliation against the two primary CSV/report sources, not a re-summary | Only reading the actual source rows (not a prior summary of them) can answer this |
| Is the deployed PPO checkpoint really unverified against Gymnasium's own interface contract? | `gymnasium.utils.env_checker.check_env()` | The standard, independent tool for exactly this question — not previously run |
| Which of the two PPO checkpoint files is which, precisely? | Direct SHA-256 recomputation, cross-referenced against both the live inference path and the frozen result CSVs | The only test that can resolve a provenance question is checking the provenance artifacts directly |
| Does the admin dashboard really lose data on restart? | A real, process-isolated call to the new `list_sessions()` function, cross-checked against a raw `sqlite3` query | Proves the specific restart-survival property, not just "the function runs" |
| Is Qwen's narrative output actually any good? | A structured, criteria-based review of real, live-captured outputs | The only way to answer a quality question is to read real output against stated criteria — not to re-assert that no evaluation exists |
| Does the dormant guardrail-fallback duplicate actually still have the bug? | Direct execution of the fallback path via monkeypatching, with the exact `T-N03` boundary cases | The fallback is otherwise unreachable in normal operation — it must be forced to run to be tested at all |

Tests **not** run this phase, and why: browser-level pixel UI automation (no reliable browser-automation tool available in this environment for this specific session; the existing Vitest component suite plus this engagement's real backend/WebSocket E2E evidence are judged to provide more verified value per unit of effort than attempting a fragile, one-off browser script); new PPO training (explicitly out of scope for "evaluation," not "retraining," per instructions, and a properly-governed experiment of this kind requires its own pre-registration — see `11_Experiment_Provenance_Register.md` for the ready-to-execute protocol instead); WER/CER computation (no reference-transcript data exists — see `08_Speech_Evaluation.md`).

## Status definitions used throughout this phase's documents

| Status | Meaning | Never used to mean |
|---|---|---|
| PASS | Executed, met its predefined acceptance criterion | A static review, or a test that didn't actually run |
| FAIL | Executed, did not meet its criterion | — |
| BLOCKED | Could not execute due to an identified external/environmental blocker (named explicitly) | PASS, or silently omitted from totals |
| NOT RUN | Identified but not executed this phase | FAIL |
| PARTIAL | Some but not all planned conditions evaluated | PASS |
| REVIEW ONLY | Static inspection, not an executed test | An executed test |
| NOT APPLICABLE | Not relevant to the verified implementation | — |

Acceptance criteria for every new test in this phase (the Qwen rubric, the fallback-path boundary cases, the admin-merge check) were defined **before** execution — stated in each test's own description in `07_Qwen_Feedback_Quality_Evaluation.md` / `Application_Code_Changes.md` — not adjusted afterward to fit the observed result.
