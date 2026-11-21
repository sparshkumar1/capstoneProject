# Master Results Table — Phase 2/3 Complete

**Single source of truth for Task 2/3/4.** Every number here traces to a stored log/script in `testing_and_evaluation/`. Git commit at time of this baseline: `9d5c528b3596d0d80c6bb8d606547f64c036b081` (branch `workspace/human-eval-clean-push`), with two uncommitted-but-applied fixes on top (`rl/guardrails.py`, `launch.py` — see `Phase4_Diagnosis_and_Fixes.md`; not yet committed, per "only commit when asked").

## 1. Automated test suite (final, post-fix)

| Metric | Value |
|---|---|
| Python test files | 25 (21 unit + 4 integration) |
| Final result | **264 passed, 19 failed, 15 skipped, 0 collection errors** |
| Pass rate (executable tests) | **93.3%** (264/283) |
| Frontend (Vitest) | **28/28 passed (100%)**, 4 test files |
| All 19 failures explained | 18 × Docker daemon not running (environment gap, not code defect); 1 × pre-existing documented known failure (`CLAUDE.md`), reproduced identically |
| Regressions from Phase 4 fixes | **Zero** — identical 264/19/15 before and after both fixes |
| Full logs | `testing_and_evaluation/logs/full_suite_rerun_after_httpx.log` (pre-fix baseline), `full_suite_after_guardrail_fix.log` (post-fix, authoritative) |

**Later update (2026-11-13), historical figures above left unchanged:** Docker Desktop is now running in this
environment. A focused re-run of the 19 previously Docker-attributed failures found all 19 now pass with no code
change — see `final_evaluation/16_Docker_Verification_Report.md` for the full, itemized before/after table and
evidence. This table's 264/19/15 figures describe the Docker-unavailable baseline as it was recorded and are not
altered; they are not the current state of the Docker-dependent subset.

## 2. New targeted tests written and run this session (10 scripts/docs, all with real executed output)

| ID | Category | Result | Key finding |
|---|---|---|---|
| T-N01 | Smoke | Services OK; **launcher crashed (Unicode) — found & fixed** | `baseline_results/T-N01_smoke_test_finding.md` |
| T-N02 | RL inference | **PASS** 10/10 | Real checkpoint loads and runs correctly |
| T-N03 | Guardrail verification | **PASS** 13/13 (post-fix) | **Found & fixed a real guardrail coverage gap** |
| T-N04 | Evaluator API contract | **PASS** 7/7 | Also found evaluator is Flask, not FastAPI as claimed |
| T-N06 | Evaluator negative/edge-case | **PASS** 10/10 | No crash on empty/garbled/injection-like/emoji input |
| T-N09 | Latency spot-check | Measured | Median 896ms, p95 986ms (warm, n=30, this host) |
| T-N10 | Question selection correctness | **PASS** | Also corrected the "FAISS retrieval" claim — it's rule-based |
| T-N11 | Database CRUD/consistency | **PASS** | 0/52 and 0/26 orphaned foreign keys; real write/read roundtrip verified |
| T-N12 | Sandbox security config review | Confirmed | All claimed Docker isolation flags verified present in code |
| T-N13 | Compatibility/deployment | Documented | Python 3.11.9 local vs 3.12 Docker target; Docker build untestable (daemon down) |
| T-N14 | Structured UI inspection | Documented | Deliberate error/loading-state handling confirmed in both main views |

## 3. Defects found and fixed (Phase 4)

| # | Defect | Severity | Status |
|---|---|---|---|
| 1 | Guardrail coverage gap: perf ∈ [0.30, 0.40) unguarded against difficulty escalation | Real pedagogical-safety gap | **FIXED**, verified, zero regressions |
| 2 | `launch.py` crashes with `UnicodeEncodeError` on Windows cp1252 consoles right after successful startup | Real usability/reliability defect | **FIXED**, verified, zero regressions |

## 4. Confirmed discrepancies between `Details/revised_report_v5.pdf` (the real Phase-2 report) and the actual codebase

(Full detail: `reference_material_analysis/Previous_Project_Report_Analysis.md`)

| # | Claim in report | Actual (verified against code) |
|---|---|---|
| 1 | PPO trained "over 500,000 steps", seeds 42/123/777 | Frozen study: 24,576 steps/seed, seeds 42/123/456/789/999 (canonical truth) |
| 2 | 4-level evaluator fallback via `qwen_integration/evaluate_upgraded.py` etc., Qwen partial credit at S1>0.40/S2<0.60 | No such module paths exist; real rule is `S2_eff = S2 if R>0.30 else S2*0.60` |
| 3 | Ch.6.6 "Ablation Study" (ρ=0.580 adaptation correlation etc.) | No matching stored artifact found anywhere |
| 4 | Ch.6.1–6.4 calibration/fine-tuning experiment numbers | No matching stored artifact located (not exhaustively ruled out) |
| 5 | RL action space has 5 actions (incl. Hint/Follow-up) | Code confirms `Discrete(3)` = Easier/Same/Harder only |
| 6 | Question selection retrieves from a "Faiss VectorStore" | Zero FAISS dependency in `question_selector.py`; pure rule-based (nearest-difficulty + topic-rotation) |
| 7 | Evaluator microservice is FastAPI | Confirmed Flask (`app = Flask(__name__)`) — Qwen service genuinely is FastAPI |
| 8 | Abstract: "93.3% baseline calibration accuracy over 30 sessions" | Confirmed: no stored artifact anywhere in the repo supports this figure |
| 9 | Qwen performs "partial-credit adjustment" on the evaluator score | Confirmed false by code: `final_score` is set from a deterministic variable before Qwen is called and never reassigned from its response; Qwen is confined to narrative text/hints/follow-ups. See `Qwen_2.5_Evaluator_Validation_Report.md`. |

## 5. Requirements traceability summary

10 of 12 stated project objectives (Ch.1 Introduction): **MET** (two with corrections to the report's own inaccurate description). 1 of 12: **confirmed unverifiable** (#8 above). 1 of 12: **blocked on an environment gap** (Docker daemon down), with the underlying implementation independently confirmed correct via code review. Full detail: `Requirements_to_Test_Traceability_Matrix.md`.

## 6. Reproducibility

- **Git commit (base):** `9d5c528b3596d0d80c6bb8d606547f64c036b081`, branch `workspace/human-eval-clean-push`
- **Uncommitted changes on top:** `rl/guardrails.py` (G5 widening), `launch.py` (UTF-8 stdout fix) — see `Phase4_Diagnosis_and_Fixes.md` for exact diffs and rationale
- **Environment:** Python 3.11.9, numpy 1.26.4, torch 2.6.0, stable-baselines3 2.8.0, gymnasium 0.29.1, sentence-transformers 2.7.0, faiss-cpu 1.15.0, transformers 4.57.6, fastapi 0.141.1, pytest 9.2.0, httpx 0.28.1 — all within `requirements/*.txt` pins (the previously-documented pin violations in `docs/PROJECT_STATE.md` no longer reflect this `.venv`)
- **Hardware/OS:** Windows 11 Pro, MINGW64/Git Bash (MSYS)
- **Rerun command:** `EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest -q --continue-on-collection-errors`
- **New test scripts:** all under `testing_and_evaluation/{rl_evaluation,ml_evaluation,api_tests,database_tests,security_privacy,compatibility,ui_tests,performance_tests}/`, each independently runnable, no `tests/` files modified

## 7. Outstanding items (not blockers, user's call)

1. Two orphaned localhost dev-server processes (ports 5000/8000) from the T-N01 smoke test — harmless, stop at your convenience.
2. Docker Desktop not running — starting it would unlock 18 currently-failing tests (all Docker-dependent, code already confirmed correct via T-N12).
3. `httpx` deprecation note from Starlette (suggests `httpx2` eventually) — informational, not urgent.
4. Whether to commit the two Phase-4 fixes — not done automatically, per "only commit when asked."

## 8. Phase 2/3 status: COMPLETE

All feasible categories from `Test_Strategy.md` have real, executed evidence (A–V testing categories, ML evaluation, RL evaluation — see that file for the full classification). The only categories without fresh evidence are those correctly classified OPTIONAL/N/A (load/stress/endurance testing — Paper 1 already covers load testing; no sustained-operation requirement exists) or genuinely blocked by an external environment gap (Docker-dependent coding-sandbox tests), both clearly documented rather than silently skipped.

---

## 9. FINAL EVALUATION PHASE — 2026-11-13 (appended, sections 1–8 above are preserved unmodified as the historical Phase 2/3 baseline)

**Full detail:** `testing_and_evaluation/final_evaluation/` (14 documents) and `testing_and_evaluation/final_review/Initial_Testing_Audit.md`. This section is a pointer/summary only — it does not restate or supersede any number above; where this phase's numbers differ from §1–8, both are shown with their own dates.

### 9.1 Application code changes this phase (full detail: `final_evaluation/Application_Code_Changes.md`)

| # | File | Change | Verified |
|---|---|---|---|
| 1 | `services/qwen/app.py` | Fixed a silent character-splitting bug in 7 call sites (LLM-emitted string fields iterated as individual characters instead of wrapped as one-item lists) | Live, real-model before/after capture; unit-tested |
| 2 | `apps/backend/main.py`, `services/storage/database.py` | Admin dashboard now merges persisted (SQLite) sessions with in-memory ones; new read-only `list_sessions()` function added (no schema change) | 27 historical sessions (incl. ones from weeks before this engagement) now visible, confirmed via an independent process-isolated call + a raw SQL cross-check |
| 3 | `rl/env/interview_env.py` | Synced the dormant inline guardrail-fallback's G5 boundary (`0.40<perf` → `0.30<=perf`) to match the already-fixed `rl/guardrails.py` | 5/5 boundary cases, forced-execution of the normally-dormant path |

Branch: `final-eval/controlled-improvements`. No model weight, checkpoint, reward function, database schema, or frontend file was touched.

### 9.2 New/re-run test totals this phase

| Suite | Result | Compare to §1 above |
|---|---|---|
| Backend `pytest` (post-fix) | **264 passed, 19 failed, 15 skipped** (953.32s) — full detail: `final_evaluation/03_Test_Execution_Summary.md` | **Identical** to §1's 264/19/15 baseline — zero regressions from any of the 3 code changes, confirmed by exact per-test attribution |
| Frontend `Vitest` (post-fix) | 28/28 | Unchanged from §1 |
| Gymnasium `check_env()` | **New this phase** — PASSED, no warnings, both before and after Change 3 | Not previously run in this engagement |
| `T-N02`/`T-N03` | Re-confirmed fresh, identical to §2, before and after Change 3 | Unchanged |
| Qwen quality rubric (12 criteria, 4 real samples) | **New this phase** — see `final_evaluation/07_Qwen_Feedback_Quality_Evaluation.md`; found 2 new, undocumented output-quality defects (1 fixed — Change 1; 1 documented, not fixed — hallucinated structured-field content) | Previously: "no Qwen output-quality evaluation exists" (disclosed gap) |

### 9.3 Reconciliations this phase

ρ=0.4825 vs 0.4832, and ρ=0.4897 vs 0.4884 — both reconciled against primary sources (`paper2_ablation_results.csv`, `X2B_REPORT.md`); **no numeric error found**, both pairs were already-correct references to two genuinely different quantities. Full detail: `final_evaluation/05_ML_Evaluation_Results.md` §2.

### 9.4 PPO checkpoint identity — resolved (not replaced)

Deployed `rl/checkpoints/seed_123/ppo_final.zip` (`2ab8d5...`) and evaluated `research/experiments/paper3/checkpoints/seed_123/ppo_final.zip` (`299437...`) are **confirmed distinct files**, re-verified by independent hash recomputation this phase. Neither was modified or swapped. Full detail: `final_evaluation/06_RL_Evaluation_Results.md` §2.

### 9.5 Major finding carried forward, unchanged

The pre-registered confirmatory test (`X3A-C001`) result — no statistically detectable difference between PPO+Guardrails and a constant-action-plus-guardrails baseline, under a pre-specified δ=0.12 MAE equivalence margin — is **unchanged this phase** (no new PPO training was run). A fully-specified, ready-to-execute reward-redesign experimental protocol (not executed) is recorded in `final_evaluation/11_Experiment_Provenance_Register.md` §3 for any future, separately-governed experiment.
