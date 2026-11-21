# Initial Testing Audit — Final Evaluation Phase

**Scope:** classification of every artifact in `testing_and_evaluation/` as it existed at the start of this phase (commit `9d5c528`, no drift from the prior `Independent_Project_Audit`), using the 7-category scheme this phase mandates. This supersedes, for classification purposes, the narrower PASS/FAIL framing used in earlier passes — the same underlying logs and scripts are reused, not re-executed from scratch, except where explicitly noted.

**Classification scheme:**
1. Executed automated test
2. Executed manual test
3. Static code inspection
4. Documentation-only review
5. Planned test
6. Environment-blocked test
7. Unverified claim

---

## Document-level artifacts

| Document | Classification | Basis |
|---|---|---|
| `Test_Strategy.md` | 4 — Documentation-only (a-priori plan) | Self-describes as planning, not results; independently confirmed by prior audit |
| `Test_Priority_Matrix.md` | Mixed — see per-script rows below; the matrix itself is category 4 (a report aggregating categories 1/3/4) | — |
| `Component_Inspection_Map.md` | 3 — Static code inspection | Module-inventory table built from direct code reading |
| `Requirements_to_Test_Traceability_Matrix.md` | 4 — Documentation-only (maps external report objectives to evidence, including explicit negative-result searches) | — |
| `Baseline_Record.md` | 4 — Documentation-only (consolidates categories 1/3 results; not itself an execution) | — |
| `Phase4_Diagnosis_and_Fixes.md` | 4 — Documentation-only, describing two category-1 diagnoses/fixes (`launch.py`, `rl/guardrails.py`) | Diffs independently re-confirmed this phase |
| `Master_Results_Table.md` | 4 — Documentation-only (numerical source of truth) | Appended to, not overwritten, this phase — see `12_Final_Master_Results.md` |
| `Qwen_2.5_Evaluator_Validation_Report.md` | 3 + 4 — Static code inspection (score-separation claim) presented as documentation | Score-separation claim re-confirmed live this phase (§Phase 1, ML/Qwen results) |
| `Qwen_2.5_Viva_Explanation.md` | 4 — Documentation-only | — |

## Script-level artifacts (`testing_and_evaluation/{category}/*.py`)

| Script | Classification | Real production code? | Mock/stub? | Reproducible? | This-phase status |
|---|---|---|---|---|---|
| `rl_evaluation/T-N02_ppo_checkpoint_sanity_check.py` | **1 — Executed automated test** | Yes, real deployed checkpoint via the real `HybridOrchestrator` | No | Yes — re-run fresh this phase, 10/10, identical result | Re-confirmed, and re-confirmed again after Change 3 (G5 fallback fix) for regression |
| `rl_evaluation/T-N03_guardrail_verification.py` | **1 — Executed automated test** | Yes, real `apply_canonical_guardrails()` | No | Yes — re-run fresh, 13/13, identical | Re-confirmed, and extended this phase with 5 new cases specifically targeting the previously-untested dormant fallback path (see `Application_Code_Changes.md`, Change 3) |
| `ml_evaluation/T-N06_evaluator_negative_and_edge_cases.py` | **1 — Executed automated test** | Yes, real `evaluate()` | No | Yes — re-run fresh, 10/10, identical | Re-confirmed |
| `ml_evaluation/T-N10_question_selector_correctness.py` | **1 — Executed automated test** | Yes, real selector | No | Yes — re-run fresh, 11/11, identical | Re-confirmed |
| `api_tests/T-N04_evaluator_api_contract.py` | **1 — Executed automated test** | Yes, real Flask app via `test_client()` | No (in-process test client, not a mock of application logic) | Yes — re-run fresh, 7/7, identical | Re-confirmed |
| `database_tests/T-N11_database_crud_and_consistency.py` | **1 — Executed automated test** | Yes, real DB read-only + disposable-copy write test | No | Yes (not re-run this phase; superseded in scope by the new `list_sessions()` evidence in `Application_Code_Changes.md`, which independently re-confirms 0 orphaned rows via a fresh, differently-scoped query) | Not re-run this phase; its claim is independently corroborated, not contradicted |
| `security_privacy/T-N12_sandbox_security_config_review.md` | **3 — Static code inspection**, self-disclosed as such | N/A (no script) | N/A | N/A — no stored script/log artifact, by design | Unchanged this phase; Docker remains unreachable (see `09_Performance_and_Reliability.md`), so no execution upgrade was possible |
| `compatibility/T-N13_compatibility_and_deployment_notes.md` | **3 — Static code inspection** | N/A | N/A | N/A | Unchanged |
| `ui_tests/T-N14_structured_ui_inspection.md` | **3 — Static code inspection** (explicitly not screenshots, not a user study) | N/A | N/A | N/A | Unchanged — see `04_End_to_End_Results.md` for this phase's own, separate, real backend/WebSocket E2E evidence, which is additive, not a replacement for this category |
| `performance_tests/T-N09_latency_spotcheck.py` | **1 — Executed automated test** | Yes, real `evaluate()` in-process | No | Yes | Superseded by this phase's fresh performance evidence (see `09_Performance_and_Reliability.md`), which re-ran both the in-process and a new real-HTTP measurement |
| `scripts/*.py` (4 files: `export_to_pdf.py`, `fill_pptx_template.py`, `md_to_docx_report.py`, `md_to_docx_ieee_paper.py`) | **Not a testing artifact at all** | N/A | N/A | N/A | Confirmed again this phase (consistent with the prior audit's finding): these are document-formatting utilities for `final_deliverables/`, misleadingly located under a directory named `testing_and_evaluation/`. See `Repository_Structure_Audit.md` (Phase 3) for the (minimal) organizational recommendation. |

## The full pytest / Vitest suites

| Suite | Classification | Status this phase |
|---|---|---|
| Backend `pytest` (25 files) | **1 — Executed automated test** | Re-run fresh before code changes (264 passed/19 failed/15 skipped, identical to prior baseline) and again after all three code changes in Phase 2 (see `03_Test_Execution_Summary.md` for the post-fix count) |
| Frontend `Vitest` (4 files) | **1 — Executed automated test** | Re-run fresh before and after code changes: 28/28 both times |

## Items previously counted under a single aggregate that this phase separates explicitly

Per this phase's instruction not to combine categories into a misleading pass percentage:

- The **18 Docker-dependent pytest failures** remain classified as **6 — Environment-blocked**, not FAIL-in-the-ordinary-sense and not silently converted to anything else. Docker's unreachability was independently reconfirmed at the start of this phase (`docker ps` connection failure, same error signature as previously documented).
- The **1 pre-existing known pytest failure** (`test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`) remains classified as **1 — Executed automated test, FAIL**, left unresolved by this project's own stated policy (not silently patched).
- The three documentation-only categories (`security_privacy`, `compatibility`, `ui_tests`) remain classified as **3 — Static code inspection**, never miscounted as executed tests in any total in this phase's documents.
- Claims in `Requirements_to_Test_Traceability_Matrix.md` that could not be independently re-verified in a prior pass (e.g. the "93.3% baseline calibration accuracy" figure from an external report, already searched for and not found) remain classified as **7 — Unverified claim**, not re-asserted as resolved.

## New classification this phase adds

- The admin-dashboard SQLite-vs-in-memory gap: previously **3 — Static code inspection** (described, not fixed). This phase both fixes it (`Application_Code_Changes.md`, Change 2) and independently **executes** a verification (direct `list_sessions()` call in an isolated process, cross-checked against a raw `sqlite3` query) — now **1 — Executed automated test**.
- The G5 guardrail fallback duplicate: previously **3 — Static code inspection**. This phase fixes it and **executes** the first-ever test of the dormant fallback path itself (by forcing it to run via monkeypatching) — now **1 — Executed automated test**.
- Qwen narrative-output quality: previously **7 — Unverified claim** (explicitly disclosed as not evaluated in the prior testing report). This phase conducts a structured, criteria-based review of real captured outputs — see `07_Qwen_Feedback_Quality_Evaluation.md`. This is **2 — Executed manual test** (a single-reviewer structured qualitative review, not a blinded multi-rater study — the scope is stated honestly, per this phase's instruction not to fabricate human quality ratings).
