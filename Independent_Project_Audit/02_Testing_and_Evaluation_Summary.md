# 02 — Testing and Evaluation Summary

*Independent audit document. Synthesized from a full, read-only inspection of `testing_and_evaluation/` (18 documents + 19 logs + 8 scripts across 7 test categories) cross-checked against the main `tests/` pytest suite and git history. Full citations in `Independent_Project_Audit/_research/02_testing_package_audit.md`.*

---

## 4.1 Testing Strategy

`testing_and_evaluation/Test_Strategy.md` classifies 22 standard test categories (unit → exploratory) plus separate ML/RL evaluation tables, each with a Priority/Rationale/Data-availability column. **This is honestly scoped as planning, not as a report of work done** — it makes no execution claims and correctly marks several categories N/A with stated reasons (no video component to test, no human-subject study to re-run). It was later realized through a second, newly-written set of scripts (`T-N01`–`T-N14`) that specifically target gaps the pre-existing pytest suite did not cover (guardrail boundary behavior, Flask API contracts, DB integrity, latency, question-selector correctness, security/UI/compatibility review).

**Assessment:** the category selection is appropriate for this codebase — it neither inflates coverage by counting categories that don't apply (video/UI automation, load testing at scale) nor omits categories that matter for a safety-relevant RL controller (RL sanity check, guardrail verification) and a sandboxed code executor (security review). The number of categories is not treated here as a quality signal in itself; what matters is whether each one produced real, traceable evidence (§4.2).

---

## 4.2 Test Coverage by Category

| Category | Script(s) | Real production code exercised? | Evidence artifact | Finding |
|---|---|---|---|---|
| **RL — PPO checkpoint sanity** | `T-N02_ppo_checkpoint_sanity_check.py` | **Yes** — loads the real deployed checkpoint via `HybridOrchestrator.suggest()`, no mocking | `logs/T-N02_output.log`, matches claims exactly | PASS (10/10 scenarios valid), but validates the **runtime** checkpoint, which the project's own canonical-truth doc states differs by SHA-256 from the checkpoint actually evaluated in the frozen Paper-3 result tables — a checkpoint-identity gap not flagged anywhere inside the testing package itself |
| **RL — guardrail verification** | `T-N03_guardrail_verification.py` | **Yes** — calls the real `apply_canonical_guardrails()` directly | `logs/T-N03_output.log` (pre-fix, 11 cases) / `_after_fix.log` (post-fix, 13 cases) | Found and closed a real gap: `perf ∈ (0.30, 0.40)` had no guardrail coverage, so a below-average candidate's difficulty could be escalated with zero safety override. Fix verified via `git diff rl/guardrails.py` to be a single, minimal boundary change |
| **ML — evaluator negative/edge cases** | `T-N06_evaluator_negative_and_edge_cases.py` | **Yes** — real SBERT/FAISS/CrossEncoder pipeline | `logs/T-N06_output.log` | 10/10 adversarial inputs (empty string, 16.5K-char repeat, SQL-injection text, emoji spam, etc.) never crash and stay in `[0,1]`. This is a **robustness/crash-safety** check, not an accuracy check — it says nothing about whether the scores are *reasonable* |
| **ML — question selector correctness** | `T-N10_question_selector_correctness.py` | **Yes** | `logs/T-N10_output.log` | 9/9 checks pass; also corrects an external claim that question selection is FAISS-based (it is rule-based) |
| **API — evaluator contract** | `T-N04_evaluator_api_contract.py` | **Yes** — real Flask app via `test_client()` | `logs/T-N04_output.log` | 7/7 checks pass, including a correctly-handled malformed-JSON error path |
| **Database — CRUD/consistency** | `T-N11_database_crud_and_consistency.py` | **Yes** — reads the real `data/prepaired.db` (read-only), writes only to a disposable temp copy | `logs/T-N11_output.log` | 0/52 and 0/26 orphaned foreign keys; real write/read roundtrip verified on the temp copy; production DB never mutated |
| **Performance — latency spot-check** | `T-N09_latency_spotcheck.py` | **Yes** — real `evaluate()`, 30 timed calls | `logs/T-N09_output.log` | median 896 ms / p95 986 ms (warm); explicitly and correctly **not** claimed equivalent to Paper 1's frozen 404.6 ms median (different hardware/environment, honestly disclosed) |
| **Security/privacy** | `T-N12_sandbox_security_config_review.md` | Documentation/code-review only — **no script, no log** | — | Lists 10 Docker-hardening flags as present in code; explicitly self-scoped as "not a penetration test" since the Docker daemon was down. Not independently re-greped by this audit's testing-package pass (the architecture-pass agent separately confirmed these flags exist, §01) |
| **Compatibility/deployment** | `T-N13_compatibility_and_deployment_notes.md` | Documentation only | — | Environment-version table; explicitly discloses "build verification: not performed, Docker daemon down" |
| **UI** | `T-N14_structured_ui_inspection.md` | Code-reading only — **no screenshots, no user study** | — | Explicitly and correctly self-limits ("visual layout/responsiveness not assessed"); cross-references one real, independently-confirmed Vitest test name |
| **Frontend unit (Vitest)** | (pre-existing suite) | Yes | `logs/T-F01_frontend_vitest_output.log` | 4/4 files, 28/28 tests pass |
| **Full backend pytest suite** | (pre-existing suite, 25 files) | Yes, except 2 of 25 files that set `EVALUATOR_MOCK_MODE` in their run docstring — which, per §4.4, has **no actual effect** on which code path runs | `logs/full_suite_after_guardrail_fix.log`, `logs/full_suite_rerun_after_httpx.log` | 264 passed, 19 failed, 15 skipped, 0 collection errors (93.3% of 283 executable). All 19 failures explained: 18 are Docker-daemon-unavailable failures (environment gap, not code defect), 1 is the pre-existing, known, unresolved `test_stage11_5_coding_adaptation` failure documented in `CLAUDE.md`'s own gotchas list |

**What each test category actually proves (§4.3, scoped precisely):**
- Unit/API/DB tests above establish **functional correctness of individual real code paths**, not model accuracy or RL effectiveness.
- The RL sanity/guardrail scripts establish that the **inference pipeline runs without error and produces valid, bounded actions**, and that a specific, real safety gap was found and closed — they do **not** establish that the PPO policy adds value over simpler alternatives (that question is addressed, and answered unfavorably, by the separate Paper-3 baseline-comparison evidence covered in document 04).
- The performance spot-check establishes **measured latency under one specific, disclosed hardware/software configuration** — not a claim comparable across environments.
- The security/compatibility/UI "tests" are **code-review documentation, not executed tests** — each one says so itself. They should not be counted alongside the scripted categories when totaling "how many tests were run."

---

## 4.4 Baseline and Defect Improvements

Two defects were diagnosed and fixed during this testing phase (`testing_and_evaluation/Phase4_Diagnosis_and_Fixes.md`), both independently re-verified in this audit by direct `git diff`, not by trusting the prose description:

**Fix 1 — `rl/guardrails.py` G5 boundary gap.**
- Original problem: reproduced directly (`perf=0.35` state fed to the real guardrail function returns no override).
- Root cause: G5's lower bound (0.40) left a gap above G1/G4's upper bound (0.30).
- Code change: **verified minimal and exact** via `git diff` — one condition line (`0.40 < perf` → `0.30 <= perf`) plus a docstring explaining the fix, dated 2026-11-12. No other rule, action, or priority order touched.
- Regression testing: full suite rerun before/after is **byte-identical** except for memory addresses and wall-clock duration in the log — confirms zero regressions were introduced.
- **Open concern (this audit's own finding, not disclosed elsewhere in the package):** `Phase4_Diagnosis_and_Fixes.md` asserts the fix was "applied with explicit user approval (2026-11-12)." No independent artifact (approval log, external record) corroborates this inside the repository — it is a self-reported claim inside the same document that made the change. This matters because `rl/guardrails.py` is one of the three files `CLAUDE.md` names as governed RL infrastructure, under a rule that nothing should change "after seeing results without registering a new experiment." The disclosure of the change is thorough and the change itself is narrow and well-tested; the **provenance of its approval** is the only unverifiable element.

**Fix 2 — `launch.py` Windows console Unicode crash.**
- Original problem: reproduced directly — `UnicodeEncodeError` on printing `→` under a cp1252 console, crashing `launch.py` right after both services started.
- Code change: verified via `git diff` — a textbook-correct `sys.stdout/stderr.reconfigure(encoding="utf-8", errors="replace")` wrapped in `try/except`.
- **Honestly disclosed gap:** the fix's mechanism was verified in isolation (forced-encoding repro), but a full end-to-end re-run of `launch.py`'s actual startup banner under the fix was **not** performed (orphaned dev-server processes on ports 5000/8000 blocked a clean rerun). The documents say so themselves rather than overstating completeness.

**Organizational issue found, not previously flagged:** `testing_and_evaluation/scripts/` contains **zero test-related code** — its four files are Word/PPTX/PDF document-formatting utilities for the unrelated `final_deliverables/` packaging task. The directory name invites the (incorrect) assumption that it holds test automation.

---

## 4.5 Master Results Table Audit

Every number in `testing_and_evaluation/Master_Results_Table.md` that could be independently traced to a stored log, script, or source file (the large majority of the table) **checked out exactly**, with correct arithmetic, correct rounding, and no contradicted citation:

- Test file counts (25 = 21 unit + 4 integration): **confirmed by direct recount**.
- Pass/fail/skip totals (264/19/15, 93.3% of 283): **confirmed**, arithmetic correct (264/283 = 0.93286…).
- All 19 failures individually enumerated and attributed (18 Docker-dependent + 1 known failure): **confirmed by counting the log's own `FAILED` lines**.
- Frontend 28/28 Vitest: **confirmed**.
- PPO timesteps/seeds (24,576/seed; 42/123/456/789/999), RL `Discrete(3)` action space, Flask-not-FastAPI evaluator, rule-based-not-FAISS question selection, human-correlation figures (0.3812/0.4832/0.4884): **all independently cross-confirmed against `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`**, matching exactly.
- The one claim this audit could **not** independently verify within its assigned scope was the external capstone report's unsupported "93.3% baseline calibration accuracy over 30 sessions" figure — the testing package's own negative-result search methodology for this claim is sound (it searched and found no supporting artifact, rather than assuming absence), but this audit did not re-run that search itself.
- **A coincidence worth flagging for anyone writing from this table downstream:** the unrelated, unverifiable "93.3% baseline calibration accuracy" claim and this session's own, fully-traceable "93.3% pytest pass rate" are numerically identical by chance. A reader skimming a later report risks conflating the two.

**No arithmetic error, no unit mismatch, no mis-rounded percentage, and no untraceable headline number was found** in the parts of the table within independent verification power.

---

## Honest Testing-Quality Assessment

**Are the tests meaningful?** Yes, substantially. Across the 8 newly-written `T-N` scripts, none sets `EVALUATOR_MOCK_MODE` or any other mock flag, and each imports and calls real production code directly (the real evaluator, the real guardrail function, the real question selector, the real SQLite file, the real Flask app). This is a materially higher evidentiary standard than a typical capstone testing package.

**Is coverage sufficient?** Partial, and the package is honest about where. Functional/unit/integration/RL-sanity/DB/API coverage is real. Security/compatibility/UI are explicitly documentation-only, not padded with fabricated execution counts. 18 Docker-dependent pytest tests remain unexecuted (environment gap, disclosed). Qwen's narrative-text quality has **zero** quantitative evaluation anywhere in the project — disclosed, not hidden.

**Real vs. mocked:** the large majority of what's claimed as "executed" genuinely is, against real code, with stored logs this audit cross-checked number-for-number. No fabricated log or contradicted claim was found anywhere in the package.

**Reproducibility:** high for the 8 new scripts (short, dependency-light, real `Run:` docstrings) — an independent reviewer with the same environment and database could rerun every one and expect matching results. Low for the three documentation-only categories, which have no script to rerun.

**The two things an independent reviewer should press on:** (1) the guardrail-fix approval provenance (self-attested, no independent artifact), and (2) the mislabeled `scripts/` directory. Everything else in the package checked out.
