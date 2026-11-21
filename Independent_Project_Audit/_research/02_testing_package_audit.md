# Independent Audit — `testing_and_evaluation/` Package

**Audit scope:** complete inspection of `D:\Capstone_29_AUG\capstoneProject\testing_and_evaluation\` (read-only). All claims below are tagged **VERIFIED FACT** (cite exact file/path/line), **OBSERVATION** (from a command I ran in this audit), **INTERPRETATION** (my analysis), **RECOMMENDATION**, or **UNKNOWN**.

**Note on provenance:** `testing_and_evaluation/` is untracked in git (per `git status`: not listed as tracked, confirmed separately — the directory does not appear under version control). Everything in it, including the two source-code edits it documents (`rl/guardrails.py`, `launch.py`), is uncommitted working-tree state as of this audit. Git context: branch `workspace/human-eval-clean-push`, HEAD `9d5c528`, both `rl/guardrails.py` and `launch.py` show as `M` (modified, uncommitted) in `git status`.

---

## 1. `Test_Strategy.md`

**VERIFIED FACT** — file exists at `testing_and_evaluation/Test_Strategy.md`, 60 lines. It is a planning document: a 22-row classification table (categories A–V: unit, functional, integration, e2e, system, regression, smoke, sanity, negative, boundary, API, database, UI, performance, load, stress, endurance, reliability, security, compatibility, acceptance, exploratory) and a separate ML-evaluation and RL-evaluation table, each with Priority/Rationale/Data-availability columns.

**INTERPRETATION:** This document is explicitly a-priori reasoning ("classified for *this* codebase specifically... not silently included") rather than a report of work done. It correctly self-labels several categories N/A with reasons (no video/MediaPipe, no human-subject study) rather than inventing coverage. It also records a blocker ("`pytest`/`pytest-asyncio`... not installed") that was current at the time of writing but later resolved (see §5 below) — the document is not updated in place to remove this now-stale blocker note, which is a minor staleness issue, not a fabrication.

**VERIFIED FACT (confirmed independently in this audit):** I ran a direct file count — `tests/unit/*.py` = 21 files, `tests/integration/*.py` = 4 files (excluding `__pycache__`) — exactly matching the document's claim of "21 unit-test files" and "4 integration test files exist" (21 + 4 = 25).

**No execution evidence is claimed in this file** — it is purely planning. No discrepancy found; it is honestly scoped as strategy, not results.

---

## 2. `Test_Priority_Matrix.md`

**VERIFIED FACT** — 71 lines. Group 1 (existing suite, T-U01–T-U15, T-I01–T-I04, T-F01) and Group 2 (new scripts, T-N01–T-N10) are both tabulated with Test ID / Category / Component / Objective / Importance / expected result, followed by an **"Execution status"** table that claims specific pass/fail outcomes for each T-N item and a final aggregate (**264 passed, 19 failed, 15 skipped, 0 collection errors, 93.3%**).

**OBSERVATION (this audit):** I independently opened the two full-suite logs this claim traces to (`logs/full_suite_after_guardrail_fix.log`, `logs/full_suite_rerun_after_httpx.log`) and confirmed both end with the literal line:
```
19 failed, 264 passed, 15 skipped, 4 warnings in 462.08s (0:07:42)   [guardrail-fix log]
19 failed, 264 passed, 15 skipped, 4 warnings in 472.76s (0:07:52)   [httpx-rerun log]
```
This is a genuine, traceable pytest summary line, not a number invented in the Markdown. **VERIFIED.**

**OBSERVATION:** I diffed the two log files byte-for-byte (`diff` command). They are identical except for (a) Python object memory addresses printed incidentally inside pytest fixture-teardown tracebacks for the still-failing Docker tests, and (b) the wall-clock duration (462.08s vs 472.76s). This means the two "separate" full-suite runs produced the exact same pass/fail/skip set and the exact same individual failing test names — which is exactly what "zero regressions between pre-fix and post-fix" should look like, and is positive corroborating evidence (not a sign the log was copy-pasted/faked, since memory addresses and durations differ — these are real independent process executions, not a duplicated file).

**VERIFIED FACT (T-N02/T-N03 claims):** Logs `logs/T-N02_output.log` and `logs/T-N03_output.log`/`T-N03_output_after_fix.log` exist and contain content exactly matching the matrix's claimed results (10/10 scenarios; 11/11 then 13/13 guardrail cases; the "score=0.35 → Harder" observation). Matches exactly — see detailed log transcription in §6 and §7 below.

**VERIFIED FACT (T-F01):** `logs/T-F01_frontend_vitest_output.log` shows `Test Files 4 passed (4)`, `Tests 28 passed (28)` — matches the claimed "4/4 files, 28/28 Vitest tests" exactly.

**No discrepancy found** in this file's claims against its own cited evidence.

---

## 3. `Component_Inspection_Map.md`

**VERIFIED FACT** — 55 lines, a module-inventory table built from direct code reading (file paths, inputs/outputs, dependencies, existing test coverage per module), plus a dedicated "Resolved item: RL action-space size" section.

**OBSERVATION (this audit):** I independently grepped `services/evaluator/app.py` for `Flask`/`FastAPI`:
```
562:    from flask import Flask, request, jsonify
582:app = Flask(__name__) if FLASK_AVAILABLE else Flask()
```
This **confirms** the Component_Inspection_Map / Master_Results_Table claim that the evaluator service is Flask, not FastAPI, contradicting the (external, not-in-scope) capstone report. **VERIFIED.**

**VERIFIED FACT:** "21/25 Python test files use pytest-specific features... not runnable under plain unittest" and "No `conftest.py` anywhere in `tests/`" are stated as direct-inspection findings; I did not re-verify the unittest-compatibility claim exhaustively (would require reading all 25 files), tagged **UNKNOWN (not independently re-verified by this audit)** for that specific sub-claim, though it is plausible and not load-bearing for the Master Results Table.

**VERIFIED FACT:** The claim that `agents/strategy/hybrid_orchestrator.py`'s action space is `Discrete(3)` is corroborated indirectly by the T-N02 script output (`source=ppo`, actions always one of Easier/Same/Harder — see §6) and is consistent with `CLAUDE.md`'s own stated architecture ("action Discrete(3)... easier/same/harder"). **VERIFIED, consistent with CLAUDE.md.**

---

## 4. `Requirements_to_Test_Traceability_Matrix.md`

**VERIFIED FACT** — 32 lines, maps OBJ-1 through OBJ-12 (quoted/paraphrased from an external capstone report, `Details/revised_report_v5.pdf`, which is outside the scope named for this audit) to Test IDs and a MET/NOT VERIFIED/BLOCKED status.

**INTERPRETATION:** This file's rigor is notably good practice: for OBJ-8 ("93.3% baseline calibration accuracy over 30 sessions") it explicitly states a negative-result search ("Searched `research/results/`, `ablation/results/`, `experiments/` for '93.3'... every hit was a coincidental decimal substring... none referencing 'baseline calibration' or '30 sessions'") rather than asserting the number is simply absent without having looked. This is exactly the behavior `CLAUDE.md` wants (never invent/claim unverifiable metrics).

**OBSERVATION (this audit):** I did not re-run the search for "93.3" across `research/`, `ablation/`, `experiments/` myself (out of scope — this audit is scoped to `testing_and_evaluation/`, and re-deriving external document claims would require reading `Details/revised_report_v5.pdf`, which is explicitly outside my assigned file list). I therefore cannot independently confirm the negative result; I can only confirm the matrix's own methodology is sound and its wording appropriately hedged ("confirmed no stored artifact exists" based on a search, not "does not exist" as an absolute). Tagged **UNKNOWN (outside audit scope to re-verify directly)**, but the document's own epistemic hygiene is sound.

**Coincidental and noteworthy:** OBJ-8's "93.3%" figure and the Master_Results_Table's own independently-measured pytest pass rate of "93.3% (264/283)" are numerically identical by coincidence (one is an unverifiable claim from an external report about calibration accuracy; the other is this session's own, traceable pytest statistic). **INTERPRETATION/RECOMMENDATION:** this coincidence creates a real risk of accidental conflation in future report-writing (Task 2/3) — a reader skimming could mistake the 93.3% test-pass-rate for a confirmation of the unverified 93.3% calibration-accuracy claim. I recommend explicitly flagging this coincidence in any downstream report that cites both numbers, since the documents reviewed here do not themselves call out the collision.

---

## 5. `Baseline_Record.md`

**VERIFIED FACT** — provenance section cites git commit `9d5c528b3596d0d80c6bb8d606547f64c036b081`, branch `workspace/human-eval-clean-push`, date 2026-11-12 — consistent with the git-status snapshot provided to this audit (current HEAD commit `9d5c528`).

**VERIFIED FACT (environment table):** Claims Python 3.11.9 (vs `CLAUDE.md`'s documented 3.12), numpy 1.26.4, torch 2.6.0, accelerate 0.34.2 — all stated as "within pin." This directly contradicts `docs/PROJECT_STATE.md`'s "ENVIRONMENT RECONCILIATION ISSUE" cited in `CLAUDE.md` (numpy 2.5.2, torch 2.11.0, accelerate 1.13.0 — all violating pins). The Baseline_Record explicitly flags this contradiction rather than silently resolving it ("This is good news but is not something I have edited `docs/PROJECT_STATE.md` to reflect... flagging here instead") — this is the correct behavior per `CLAUDE.md`'s "do not resolve the listed open decisions unasked."

**INTERPRETATION:** I did not independently activate `.venv` and run `pip list` myself in this audit (would require executing commands beyond simple log/file inspection, and the task scope asked me to prefer reading existing logs). This specific environment-versions table is **UNKNOWN (not independently re-verified by this audit)** — plausible and internally consistent with everything else in the package (e.g., the full-suite log's own warning text references `transformers`, `fastapi`, etc. in ways consistent with modern pinned versions), but I did not run `python -m pip list` myself to confirm the exact version strings.

**VERIFIED FACT (T-N02/T-N03 claims in this file):** Cross-checked directly against the actual log files — see §6/§7. Exact match.

**VERIFIED FACT (full-suite summary in this file):** "264 passed, 19 failed, 15 skipped, 0 collection errors (93.3% of 283 executable tests)" — matches the log tail exactly (§2 above). 264+19 = 283; 264/283 = 0.93286… ≈ 93.3%. **Arithmetic confirmed correct.**

**VERIFIED FACT (T-F01):** matches `logs/T-F01_frontend_vitest_output.log` exactly.

---

## 6. RL Evaluation (`rl_evaluation/`)

Two files: `T-N02_ppo_checkpoint_sanity_check.py`, `T-N03_guardrail_verification.py`.

### T-N02 — PPO checkpoint sanity check

**VERIFIED FACT (real code path, not mocked):** The script (`testing_and_evaluation/rl_evaluation/T-N02_ppo_checkpoint_sanity_check.py`) imports `agents.strategy.hybrid_orchestrator.HybridOrchestrator` directly (no mock/monkeypatch), instantiates it, and calls the real `.suggest()` method on 10 hand-constructed states. No `EVALUATOR_MOCK_MODE` or other mock env var is set or referenced anywhere in this script. **This genuinely exercises the production RL-inference code path and the real, frozen checkpoint file on disk** (`rl/checkpoints/seed_123/ppo_final.zip` + `vecnormalize.pkl`).

**OBSERVATION:** `logs/T-N02_output.log` (15 lines) shows:
```
[HybridOrchestrator] PPO loaded successfully (dim=6, actions=3)
ready=True is_compatible=True model_path=rl/checkpoints/seed_123/ppo_final.zip vec_path=rl/checkpoints/seed_123/vecnormalize.pkl
... 10 scenario lines, each [OK] ...
Scenarios run: 10  Failures: 0
```
This log **exactly matches** the "PASS — real PPO checkpoint, 10/10 scenarios valid" claims in `Baseline_Record.md` and `Master_Results_Table.md`, including the specific "score=0.35 → Harder" line (`[OK] boundary_score_at_0.35: score=0.35 diff=3 -> action=Harder new_diff=4 source=ppo`). **VERIFIED, fully traceable.**

**INTERPRETATION / gap found by this audit, not flagged in the testing package itself:** `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2 (line ~79, read directly in this audit) states: *"Deployed vs evaluated checkpoint: runtime `rl/checkpoints/seed_123/ppo_final.zip` (`2ab8d5...`) differs from the evaluated `research/experiments/paper3/checkpoints/seed_123/ppo_final.zip` (`299437...`). State which checkpoint each claim refers to."* T-N02 loads and validates the **runtime** checkpoint (`rl/checkpoints/seed_123/ppo_final.zip`), which — per the project's own canonical-truth document — is a **different file by hash** from the checkpoint whose behavior is reported in the frozen Paper-3 results tables. Nothing in `Baseline_Record.md`, `Phase4_Diagnosis_and_Fixes.md`, or `Master_Results_Table.md` acknowledges this checkpoint-identity distinction; they describe the runtime checkpoint simply as "the real, frozen, deployed policy" without noting it is not the same file as the one Paper-3's frozen numbers describe. **This is a real, independently-found gap**: a reader could wrongly infer that T-N02's "PASS, 10/10" result validates the specific checkpoint behind Paper-3's frozen MAE/volatility numbers — it validates a different (though same-seed) checkpoint file. **RECOMMENDATION:** any Task 2/3 report citing T-N02 should explicitly state which checkpoint (`rl/checkpoints/...` vs `research/experiments/paper3/checkpoints/...`) was loaded.

### T-N03 — Guardrail rule verification

**VERIFIED FACT (real code path):** `rl_evaluation/T-N03_guardrail_verification.py` imports `rl.guardrails.apply_canonical_guardrails` directly and calls it on 11 (pre-fix) then 13 (post-fix) constructed states. No mocking.

**OBSERVATION:** `logs/T-N03_output.log` (pre-fix, 18 lines) shows `Cases run: 11 Mismatches: 0` and explicitly documents the uncovered gap case (`THE_GAP_CASE_from_T-N02: perf=0.35 ... proposed=Harder -> final=Harder overridden=False guardrail=none`). `logs/T-N03_output_after_fix.log` (post-fix, 20 lines) shows `Cases run: 13 Mismatches: 0` with the same case now resolving to `g5_partial_same` and two new boundary cases (`perf=0.30` and `perf=0.299`) confirmed to resolve correctly on each side of the new boundary. **Both logs exactly match the narrative claims in `Baseline_Record.md`, `Phase4_Diagnosis_and_Fixes.md`, and `Master_Results_Table.md`.** Fully traceable.

**VERIFIED FACT (the code change itself):** I ran `git diff rl/guardrails.py` directly in this audit. The actual diff:
```
-  - G3 / G5 (Partial Understanding): 0.40 < perf < 0.65 and avg_perf < 0.60 and consec < 2 -> Same
+  - G3 / G5 (Partial Understanding): 0.30 <= perf < 0.65 and avg_perf < 0.60 and consec < 2 -> Same
...
-    if 0.40 < perf < 0.65 and avg_perf < 0.60 and consecutive_failures < 2:
+    if 0.30 <= perf < 0.65 and avg_perf < 0.60 and consecutive_failures < 2:
```
plus an added docstring block dated 2026-11-12 explaining the fix. **This exactly matches the single-line, single-boundary change described in `Phase4_Diagnosis_and_Fixes.md`.** No other guardrail condition, action, or priority order is touched — confirmed by direct diff inspection, not just by trusting the prose description.

**INTERPRETATION — governance/process concern (important finding):** `rl/guardrails.py` is one of the three files `CLAUDE.md`'s "RL:" line names as governed components (`rl/env/interview_env.py`, `rl/training/simulated_candidate.py`, `rl/guardrails.py`), and `CLAUDE.md` states: *"Do not change reward/state/action definitions or retrain PPO without explicit approval,"* and separately, under Experiments: *"nothing is changed after seeing results without registering a new experiment."* `rl/guardrails.py` is not literally on `CLAUDE.md`'s itemized **frozen-file list** (which names `rl/checkpoints/*` specifically, not `rl/guardrails.py`), so this edit does not violate that specific enumerated list. However:
- The guardrail threshold was changed **as a direct consequence of observing the PPO policy's behavior** (T-N02's output) — i.e., a parameter governing RL-episode behavior was altered in direct response to seeing an inference result, which is close in spirit to what the "nothing changed after seeing results without registering a new experiment" rule exists to prevent, even though this was framed as "testing/diagnosis" rather than a new X1/X2/X3 experiment.
- `Phase4_Diagnosis_and_Fixes.md` asserts *"Applied with explicit user approval (2026-11-12, in direct response to being shown both findings and asked whether to apply fixes)."* **This is a self-reported claim inside the document itself.** From a read-only audit of the file tree, I can find **no independent artifact** (approval log, chat transcript, signed sign-off) corroborating that this specific approval exchange occurred — it is asserted in prose only, by the same agent that made the change. Tagged **UNKNOWN (unverifiable from the file tree alone; the only "evidence" of approval is the claim itself)**. This does not mean the approval didn't happen — only that this audit, scoped to file inspection, cannot confirm it independently.
- The change is correctly **not** applied to any frozen result file (`research/results/paper3/*` untouched — confirmed no diff shown for that path), and the document explicitly discloses the future-reproducibility implication (re-running `research/scripts/run_paper3_study.py` would now produce different numbers). This disclosure is good practice and mitigates — but does not eliminate — the process concern above.

**RECOMMENDATION:** Before this change is committed, the project should record it as a logged decision (per `CLAUDE.md`'s "Major architecture/experiment changes... get approval first" instruction) in a durable location (e.g., `docs/PROJECT_STATE.md` or a changelog), not only inside `testing_and_evaluation/Phase4_Diagnosis_and_Fixes.md`, since the latter is itself an untracked, non-canonical directory.

---

## 7. ML Evaluation (`ml_evaluation/`)

Two files: `T-N06_evaluator_negative_and_edge_cases.py`, `T-N10_question_selector_correctness.py`.

### T-N06

**VERIFIED FACT (real code path, not mocked):** imports `from services.evaluator.app import evaluate, get_rubric` directly — the real SBERT/FAISS/CrossEncoder-backed evaluator, not a mock. No `EVALUATOR_MOCK_MODE` reference in this script.

**OBSERVATION:** `logs/T-N06_output.log` (15 lines) shows all 10 cases with `[OK]` and a final `final_score` for each (e.g., `empty_string: ... -> final_score=0.0634`, `normal_correct_answer: ... -> final_score=0.6`). Line count and content exactly match the script's 10 `CASES` list and the claimed "10/10, no crash, all scores in [0,1]." **VERIFIED, fully traceable.**

**OBSERVATION (minor numeric curiosity, not a defect):** `whitespace_only` and `empty_string` both score **identically** 0.0634, and several garbled/injection/emoji cases score exactly `0.0`. This is plausible behavior (deterministic embedding of near-empty strings converging, zero-coverage inputs flooring at 0) but was not explained by the script/log — **INTERPRETATION:** this is consistent with, not contradictory to, the claimed "scores stay in range" result; I flag it only as a pattern a stricter audit might want explained (e.g., is 0.0634 a floor/bias term independent of input length for near-empty text?). Not a discrepancy against any specific claim made in the package.

### T-N10

**VERIFIED FACT (real code path):** imports `agents.question_selector.question_selector` directly, calls real `nearest_difficulty`/`select_next_question`. No mocking.

**OBSERVATION:** `logs/T-N10_output.log` shows 9/9 `nearest_difficulty` checks `[OK]`, a 15-question simulated session with no duplicate qids and no consecutive-same-topic turns, topic distribution exactly 1 per topic across 15 distinct topics. **Matches** the claimed "PASS — also corrected the FAISS retrieval claim" exactly. The script's own docstring independently documents the "no FAISS dependency" correction with a specific rationale (FAISS is used by the evaluator for concept coverage, not by the selector) — consistent with `CLAUDE.md`'s own description: *"Question selection (corrected: rule-based, not FAISS retrieval)."* **VERIFIED, and consistent with the authoritative project guide.**

---

## 8. API Tests (`api_tests/`)

One file: `T-N04_evaluator_api_contract.py`.

**VERIFIED FACT (real code path, in-process, not a mock):** imports `from services.evaluator.app import app` and drives it via Flask's own `app.test_client()` — this is the real Flask application object, exercised in-process (no separate server process, no network mocking of the business logic itself, though no real network transport is used either — in-process `test_client()` is standard, legitimate Flask-testing practice, not a stub of the app's logic).

**OBSERVATION:** `logs/T-N04_output.log` (55 lines, including an intentionally-triggered and logged werkzeug/Flask traceback for the malformed-JSON case) shows all 7 checks `[OK]`, concluding `Checks: 7 Failures: 0`, with `final_score=0.3878` for the one real-answer evaluate-answer call. **Matches** the claimed "PASS, 7/7 checks" exactly. The traceback visible in the log is the *expected*, intentionally-provoked error path (test case 7, malformed JSON body) being correctly handled with a 4xx, not an unhandled crash — the log is evidence the error path works, not evidence of a hidden failure. **VERIFIED, fully traceable.**

**VERIFIED FACT (Flask vs FastAPI claim):** independently confirmed by this audit via direct `grep` of `services/evaluator/app.py` lines 562–582 (`from flask import Flask...`, `app = Flask(__name__) if FLASK_AVAILABLE else Flask()`). **Confirmed correct**, and the Qwen service's framework was not independently re-checked by this audit (out of scope — no file in `testing_and_evaluation/` makes a claim requiring it).

---

## 9. Database Tests (`database_tests/`)

One file: `T-N11_database_crud_and_consistency.py`.

**VERIFIED FACT (real code path, real data):** The script connects directly via `sqlite3` to the **actual** `data/prepaired.db` file (not a copy) for its read-only inspection section, and only performs writes against a `tempfile.TemporaryDirectory()`-based throwaway copy (`shutil.copy(REAL_DB, tmp_db)`) for the write/read-back roundtrip. This is a safe, correctly-scoped test design — it does not claim to avoid touching the real DB while actually touching it; the script's own structure confirms the real DB is opened read-only (`sqlite3.connect` with no `INSERT`/`UPDATE` statements in the "real-data inspection" section) and genuinely never written to.

**OBSERVATION:** `logs/T-N11_output.log` shows: tables `['candidates', 'question_attempts', 'sessions']` present; row counts `{'candidates': 2, 'question_attempts': 52, 'sessions': 26}`; `0/52` orphaned `question_attempts` and `0/26` orphaned `sessions`; a successful insert-and-read-back on the temp copy (26→27 rows). **This exactly matches** the Master_Results_Table's claim "0/52 and 0/26 orphaned foreign keys; real write/read roundtrip verified" and the Requirements matrix's "26 sessions, 52 question_attempts, 0 orphaned foreign keys." **VERIFIED, fully traceable, and the script design genuinely protects the production database from being mutated.**

---

## 10. Security & Privacy (`security_privacy/`)

One file: `T-N12_sandbox_security_config_review.md` (no accompanying script, no log file — this category is **documentation-only**, not an executed test).

**VERIFIED FACT:** The document is explicit about its own limited scope: *"a code-level configuration review, not a penetration test... a genuine attack-program execution test... was not repeated here... because the Docker daemon is down."* It lists 10 Docker-flag claims (`--user 1001:1001`, `--net=none`, `--cap-drop=ALL`, `--security-opt=no-new-privileges`, `--cpus`, `--memory`/`--memory-swap`, `--pids-limit`, `--read-only`, `--tmpfs`, `-v ...:ro`) as "present" in `agents/coding_executor/coding_executor.py`.

**OBSERVATION (this audit):** I did **not** independently re-grep `coding_executor.py` for each of these 10 flags in this pass (the task's explicit file list named `security_privacy/T-N12_sandbox_security_config_review.md` for reading, and did not separately instruct re-verifying its underlying source claims beyond the already-covered Flask/evaluator and FAISS/selector checks). This is tagged **UNKNOWN (plausible, consistent with `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`'s own §A description which the document cites, but not independently re-greped by this specific audit pass)**. **RECOMMENDATION:** if this security review will be cited as evidence in Task 2/3, an independent reviewer should personally grep `agents/coding_executor/coding_executor.py` for each of the 10 listed flags before relying on this document's table, since — unlike every other category above — **no script output or log backs this claim; it is a prose assertion of what was read in the code, without a stored, independently-replayable artifact** (e.g., no `grep` output log was saved).

**IMPORTANT, explicitly disclosed by the document itself:** it clearly states what it does *not* establish (actual attack-resistance under the current Docker/kernel, equivalent hardening on other services, comprehensive WebSocket/REST input validation) — this self-limiting is good practice and matches `CLAUDE.md`'s instruction never to claim "secure" or "audited."

---

## 11. Compatibility (`compatibility/`)

One file: `T-N13_compatibility_and_deployment_notes.md` (documentation-only, no script/log — by design, since this category is inherently "read the version strings," not something with a pass/fail log).

**VERIFIED FACT:** States Python 3.11.9 local vs `CLAUDE.md`'s documented 3.12 target vs Dockerfiles' `python:3.12-slim` vs `pyproject.toml`'s `requires-python = ">=3.11"`. This is consistent with (and duplicates, with more detail) the environment table already in `Baseline_Record.md`.

**OBSERVATION (this audit):** I did not independently open `pyproject.toml` or the five Dockerfiles to re-confirm these exact strings in this pass — tagged **UNKNOWN (not independently re-verified by this audit; plausible and internally consistent with everything else in the package)**.

**VERIFIED FACT (explicitly honest limitation):** "Build verification: not performed... Docker daemon is not running" — correctly disclosed, consistent with the 18 Docker-dependent pytest failures documented elsewhere in the same baseline.

---

## 12. UI Tests (`ui_tests/`)

One file: `T-N14_structured_ui_inspection.md` (documentation-only; explicitly **not** screenshots, **not** a user study).

**VERIFIED FACT:** The document is unusually careful to self-limit: *"live browser screenshots were not captured in this pass (no confirmed browser-automation tool available in this session)... Visual layout quality, responsiveness... were not assessed."* It bases its findings on (a) direct reading of `InterviewRoom.jsx` (550 lines) and `Report.jsx` (792 lines), and (b) citing the already-passing Vitest results from `Baseline_Record.md`/`logs/T-F01_frontend_vitest_output.log`.

**OBSERVATION (this audit):** I did not independently re-open `InterviewRoom.jsx`/`Report.jsx` to re-verify the specific line counts (550/792) or the described error-state/loading-state code structure in this pass — tagged **UNKNOWN (not independently re-verified by this audit)**. The Vitest test-name citations (e.g., `"Report.jsx displays explicit error state on API failure without mock data"`) **are** independently confirmed, since that exact test name appears verbatim in `logs/T-F01_frontend_vitest_output.log` line 14 (`✓ Stage 11.8 UI Fixes Verification > Report.jsx displays explicit error state on API failure without mock data`). **That specific cross-reference is VERIFIED.**

**No video/screenshot artifact exists anywhere in `testing_and_evaluation/`** to back the qualitative UI descriptions beyond this; this category should be understood as "structured code reading + citation of existing automated tests," exactly as the document itself labels it, not as independent visual/usability evidence.

---

## 13. Performance Tests (`performance_tests/`)

One file: `T-N09_latency_spotcheck.py`.

**VERIFIED FACT (real code path, in-process timing, not mocked):** imports `from services.evaluator.app import evaluate, get_rubric` and times 30 real (post-warm-up) calls plus one separate warm-up call, using `time.perf_counter()`.

**OBSERVATION:** `logs/T-N09_output.log` (11 lines):
```
Warm-up call (includes model load): 49581.2 ms
n=30 warm calls (model already loaded, same rubric/answer repeated)
mean=887.69ms  median=896.14ms  p90=955.95ms  p95=986.26ms  p99=1021.12ms
min=660.35ms  max=1025.97ms
```
This **exactly matches** the Master_Results_Table / Test_Priority_Matrix claim "median 896ms, p95 986ms (warm, n=30)." **VERIFIED, fully traceable, arithmetic/rounding consistent** (896.14→"896ms", 986.26→"986ms" — correct rounding).

**VERIFIED FACT (comparison framing):** The log and the surrounding docs both explicitly state this is "NOT a direct comparison" to Paper 1's frozen median of 404.6ms, citing different hardware/environment/sample size — this matches `Test_Priority_Matrix.md`'s T-N09 acceptance criterion ("do not claim equivalence to Paper 1's figures without controlling for hardware") and is handled correctly: the ~2.2× latency difference (896ms vs 404.6ms) is reported as a new, separate measurement, not framed as regression or improvement. **No overclaiming found.**

---

## 14. Logs (`logs/`)

19 files total, inventoried in full (see the file listing at the top of this audit). Every log file referenced by name anywhere in the eight Markdown documents inspected (§1–§13 above) **does exist** at the claimed path, with content that **matches** the specific numbers/outcomes cited. I found **no instance** of a Markdown document citing a log file or specific output line that does not actually exist or does not match.

**One observation worth flagging:** `logs/T-N01_pid.txt` (10 bytes) exists but is not explicitly discussed in any Markdown document's prose (it is presumably the PID of the orphaned backend process mentioned in `T-N01_smoke_test_finding.md` and `Phase4_Diagnosis_and_Fixes.md`, which cites PID 12956 directly in prose rather than by reference to this file). **INTERPRETATION:** minor; not a discrepancy, just an un-cross-referenced artifact.

**No log file exists** for T-N12 (security review), T-N13 (compatibility notes), or T-N14 (UI inspection) — consistent with those three categories being documentation/code-review-only, not executed-script categories. This is **not** a discrepancy since none of the three Markdown docs for those categories claims a script was run or a log was produced — they are self-consistently scoped as review/inspection, not execution.

---

## 15. Scripts (`scripts/`)

**IMPORTANT FINDING, not flagged anywhere inside `testing_and_evaluation/` itself:** The four files in `testing_and_evaluation/scripts/` (`export_to_pdf.py`, `fill_pptx_template.py`, `md_to_docx_report.py`, `md_to_docx_ieee_paper.py`) are **not test scripts at all**. I read all four in full/partial:
- `export_to_pdf.py` — uses Windows COM automation (`win32com.client`) to open `.docx`/`.pptx` deliverables in a locally-installed Microsoft Office and export them to PDF.
- `fill_pptx_template.py` — fills a PES university PPT template (`Details/PPT-Template_Phase3- Review3.pptx`) with project content via `python-pptx`.
- `md_to_docx_report.py` — converts 13 Markdown chapter files into a formatted `.docx` per "PES University Report-Guidelines.pdf" formatting rules.
- `md_to_docx_ieee_paper.py` — converts an IEEE paper draft Markdown file into a two-column `.docx` approximating IEEE conference formatting.

**INTERPRETATION:** None of these four scripts execute, test, verify, or validate any part of the PrepAIred application (evaluator, RL, orchestrator, DB, etc.). They are **document-production/formatting utilities** for generating the `final_deliverables/` package (an untracked sibling directory also visible in git status) — i.e., administrative/academic-submission tooling, not evidence-gathering test code. **Their presence inside a folder named `testing_and_evaluation/scripts/` is misleading by directory-naming convention alone** — a reader skimming the directory tree (as the task instructions anticipated: "Specifically read... scripts/ (all files)") could reasonably but incorrectly assume this folder contains additional test-automation scripts backing some claim in `Test_Strategy.md`/`Master_Results_Table.md`. It does not. **This is a disclosed, flagged finding of this audit** — the testing package's own documents never claim these are test scripts, so this is not a contradiction of any specific claim, but it is a naming/organization issue worth surfacing, since 4 of the ~19 files under `testing_and_evaluation/` (by file count, not test-count) are entirely unrelated to the stated purpose of the directory.

---

## 16. `Phase4_Diagnosis_and_Fixes.md` — independent audit of the two claimed-fixed defects

### Fix 1 — `rl/guardrails.py` G5 threshold widening

| Aspect | Claim | Audit finding |
|---|---|---|
| Original problem | perf ∈ [0.30, 0.40) uncovered by any guardrail when the policy proposes escalation | **VERIFIED** — reproduced in `logs/T-N03_output.log` line 10 (`THE_GAP_CASE_from_T-N02: ... final=Harder overridden=False guardrail=none`) |
| How reproduced | Constructed state (perf=0.35, avg=0.35, conf=0.5, hes=0.5) fed directly to the real `apply_canonical_guardrails()` | **VERIFIED** — real function call, not simulated/described |
| Root cause | G5's lower bound (0.40) left a gap above G1/G4's upper bound (0.30) | **VERIFIED by direct code diff** — `git diff rl/guardrails.py` confirms exactly this boundary change and nothing else |
| Code change | One condition line + docstring, `0.40 < perf` → `0.30 <= perf` | **VERIFIED, exact, minimal** — confirmed via `git diff` in this audit, matches the prose description precisely |
| Verified by before/after evidence | T-N03 pre-fix (11 cases, gap case unguarded) vs post-fix (13 cases, gap case now `g5_partial_same`) | **VERIFIED** — both logs exist, both match their respective narrative claims |
| Regression testing performed | Full suite rerun, claimed identical 264/19/15 | **VERIFIED** — both full-suite logs are near-byte-identical (differing only in memory addresses/duration), confirming no regression was introduced |
| Approval for the change | Claimed "explicit user approval (2026-11-12)" | **UNKNOWN / unverifiable from the file tree** — no independent approval artifact exists; this is a self-reported claim inside the same document that made the change (see §6 governance discussion above) |

### Fix 2 — `launch.py` Unicode console-encoding crash

| Aspect | Claim | Audit finding |
|---|---|---|
| Original problem | `UnicodeEncodeError` on `print("...\u2192...")` under Windows cp1252 console, crashing `launch.py` right after both services start | **VERIFIED by direct code/log inspection** — `logs/T-N01_launch_backend_only.log` contains the literal traceback ending in `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 16` |
| How reproduced | Live `launch.py --backend-only` run | **VERIFIED** — real subprocess log, both services' own logs (`evaluator.log`, `backend.log` referenced) show `200` health responses before the crash |
| Root cause | Unguarded `print()` of `→` (U+2192) with no console-encoding handling | **VERIFIED by direct code diff** — `git diff launch.py` confirms the fix is exactly `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` / same for `stderr`, wrapped in `try/except`, inserted immediately after imports |
| Fix verified by before/after evidence | Isolated repro under forced `PYTHONIOENCODING=cp1252`, then confirmed fixed under the same forced condition; `launch.py --help` confirmed to run the new module-level code without error | **Plausible and consistent, but I did not re-run these specific repro commands myself in this audit** — tagged **OBSERVATION-pending / UNKNOWN (not independently re-executed by this audit pass)**; the claimed mechanism (an `errors="replace"` reconfigure wrapped in try/except) is a textbook-correct fix for this exact class of bug, so it is credible on its face, but this audit did not itself force `cp1252` and rerun `launch.py --help` to confirm |
| Regression testing performed | Full suite rerun, claimed identical 264/19/15, with explicit caveat that `launch.py` isn't exercised by pytest at all | **VERIFIED** (same log evidence as Fix 1) and the caveat ("mainly confirms no import-time breakage," not functional end-to-end re-verification) is honestly stated, not glossed over |
| Full end-to-end re-verification | **Explicitly stated as NOT performed** ("ports 5000/8000 are still occupied by orphaned processes... not independently re-verified via a full fresh end-to-end run") | **This is a disclosed, honest gap** — the fix's *mechanism* is verified in isolation, but the *actual launch.py startup banner* with the fix applied, printing the real arrow characters in the real startup sequence to a real cp1252 console, was never observed end-to-end. The three narrower checks are reasonable substitutes but are explicitly weaker than a full repro, and the document says so itself. |

**Outstanding orphaned processes:** `Phase4_Diagnosis_and_Fixes.md` and `T-N01_smoke_test_finding.md` both note two orphaned localhost dev-server processes (ports 5000/8000, PID 12956 for the backend) left running from the original pre-fix smoke test, not cleaned up (`taskkill` blocked by the sandbox permission classifier). **This audit did not attempt to verify whether these processes are still running** (would require running `netstat`/`tasklist`, which risks interacting with live state beyond the read-only scope of this audit) — tagged **UNKNOWN/out of scope for this audit**, flagged here only because it is an outstanding item the original documents themselves raised and left for the user.

---

## 17. Master Results Table Verification (dedicated section, as required)

Walking `Master_Results_Table.md` number-by-number:

| # | Claim in table | Trace target | Verification result |
|---|---|---|---|
| 1 | "Python test files: 25 (21 unit + 4 integration)" | `tests/unit/`, `tests/integration/` directory contents | **VERIFIED** — direct file count in this audit: 21 `.py` files in `tests/unit/`, 4 in `tests/integration/` (excluding `__pycache__`), totaling 25, exact match |
| 2 | "264 passed, 19 failed, 15 skipped, 0 collection errors" | `logs/full_suite_after_guardrail_fix.log`, `logs/full_suite_rerun_after_httpx.log` | **VERIFIED** — exact match in both logs' final summary line |
| 3 | "Pass rate 93.3% (264/283)" | Arithmetic: 264+19=283; 264/283=0.93286 | **VERIFIED, arithmetic correct**, rounds to 93.3% |
| 4 | "Frontend (Vitest) 28/28 passed (100%), 4 test files" | `logs/T-F01_frontend_vitest_output.log` | **VERIFIED** — exact match |
| 5 | "All 19 failures explained: 18 Docker + 1 known failure" | `logs/full_suite_after_guardrail_fix.log` short-test-summary section | **VERIFIED** — the log's `FAILED` list has exactly 19 lines: 13 in `test_coding_executor.py` + 3 in `test_stage11_5_coding_adaptation.py` + 2 in `test_stage11_6_full_interview_e2e.py` = 18 Docker-pattern failures, plus the 1 named known-failure (`test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`) appears **within** the `test_stage11_5` group of 3 — i.e., the "18 Docker + 1 known" split correctly accounts for all 19 names listed; I individually counted the 19 `FAILED` lines in the log and they total 19, matching both the summary count and the attributed breakdown |
| 6 | "Regressions from Phase 4 fixes: Zero — identical 264/19/15 before and after" | Both full-suite logs, byte-diffed | **VERIFIED** — diff shows only memory addresses and duration differ, pass/fail/skip counts and failing-test names are identical |
| 7 | T-N01–T-N14 individual results | Respective logs/scripts/docs (§6–§13 above) | **VERIFIED for T-N01, T-N02, T-N03, T-N04, T-N06, T-N09, T-N10, T-N11, T-F01** (all have matching script output or log); **UNKNOWN/not independently re-verified for T-N12, T-N13, T-N14's specific underlying code claims** (documentation-only, no stored script/log artifact — see §10–§12) |
| 8 | Discrepancy #1: "500,000 steps claimed vs 24,576 steps/seed actual, seeds 42/123/456/789/999" | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` | **VERIFIED by this audit** — I directly grepped the canonical truth doc and confirmed: *"24 576 timesteps per training seed... training seeds 42/123/456/789/999"* — exact match to the testing package's claim |
| 9 | Discrepancy #5: "RL action space Discrete(3), not 5 actions" | `agents/strategy/hybrid_orchestrator.py`; consistent with `CLAUDE.md` | **VERIFIED, consistent with `CLAUDE.md`'s own architecture description** ("action Discrete(3)... easier/same/harder") |
| 10 | Discrepancy #6: "Question selection is rule-based, zero FAISS dependency, not semantic retrieval" | `ml_evaluation/T-N10_question_selector_correctness.py` + its log | **VERIFIED** — script imports no FAISS/embedding library, and `CLAUDE.md`'s own current architecture description independently agrees: *"Question selection (corrected: rule-based, not FAISS retrieval)"* |
| 11 | Discrepancy #7: "Evaluator is Flask, not FastAPI" | `services/evaluator/app.py` | **VERIFIED by direct grep in this audit** (§8 above) |
| 12 | Discrepancy #8: "93.3% baseline calibration / 30 sessions — no stored artifact" | `research/results/`, `ablation/results/`, `experiments/` (external to `testing_and_evaluation/`) | **UNKNOWN — not independently re-verified by this audit** (out of the assigned file scope; see §4 above). The claim's methodology (search, not assumption) is sound, but I did not re-run the search myself. |
| 13 | Discrepancy #9: "Qwen never adjusts final_score" | `Qwen_2.5_Evaluator_Validation_Report.md`'s own code citations (`feedback_agent.py`, `services/evaluator/app.py`) | **Internally consistent with `CLAUDE.md`'s own statement** ("Feedback: local Qwen... S2 x0.6 when R<=0.30" — a formula description that includes no Qwen term) and with the Flask-grep finding that `services/evaluator/app.py` scores via S1/S2/R only; **not independently re-greped line-by-line in `feedback_agent.py` by this specific audit pass** — tagged **largely VERIFIED by consistency, with the specific line-level claim ("never reassigned from qwen_res") UNKNOWN/not independently re-read by this audit** |
| 14 | Human-benchmark rho figures cited in Qwen reports ("ρ=0.38 composite, R-alone ρ=0.48, S1+R ρ=0.49") | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` | **VERIFIED by this audit** — directly grepped: Full composite 0.3812, R only 0.4832, S1+R 0.4884. Rounding to 0.38/0.48/0.49 is correct and matches `CLAUDE.md`'s own instruction ("rho 0.3812... full composite evaluator correlates below R-only and S1+R") |
| 15 | "Uncommitted changes on top: rl/guardrails.py, launch.py" | `git status`/`git diff` | **VERIFIED by direct git commands in this audit** — both files show as modified, uncommitted, with diffs matching the documented fixes exactly |

**Overall Master Results Table verdict:** Every number I could independently trace to a stored log, script, or source file (the large majority of the table) **checked out exactly**, with correct arithmetic and correct rounding throughout. The only items I could **not** independently verify in this audit were (a) a small number of claims that require reading files explicitly outside this audit's assigned scope (the external capstone-report discrepancy claims #2, #3, #4, and the "93.3%/30 sessions" search-negative-result), and (b) the security/compatibility/UI review documents' underlying source-code claims (T-N12/T-N13/T-N14), which are themselves documentation-only with no stored script/log artifact to check against — a structural limitation of those three categories, not a sign of fabrication. **No arithmetic error, no unit mismatch, no mis-rounded percentage, and no untraceable headline number was found** in the parts of the table within this audit's direct verification power.

---

## 18. Honest Testing Quality Assessment

**Are these tests meaningful?** Yes, substantially. The Group-2 "new" scripts (T-N02, T-N03, T-N04, T-N06, T-N09, T-N10, T-N11) each import and call **real production code** (`HybridOrchestrator.suggest()`, `apply_canonical_guardrails()`, the real Flask `app`, the real `evaluate()` function, the real `question_selector` module, the real SQLite file) rather than mocks or stand-ins. None of the eight scripts I read sets `EVALUATOR_MOCK_MODE` or any other mock flag. This is a meaningful distinction from the main pytest suite, where `EVALUATOR_MOCK_MODE=1` is the documented run flag (per `CLAUDE.md`) — **OBSERVATION:** I grepped the entire `tests/` tree and found `EVALUATOR_MOCK_MODE` referenced in only **two** test files (`test_best_answer_authority.py`, `test_primary_question_budget.py`); the other 23 of 25 Python test files, and all of the new `testing_and_evaluation/` scripts, exercise the real evaluator/RL/DB code paths, not a mocked substitute. The mock flag's actual effect (what it changes inside `services/evaluator/app.py` or the test fixtures) was not traced line-by-line in this audit, but its footprint is narrow — it is not a blanket "everything is mocked" switch.

**Is coverage sufficient?** Partial, and the package itself says so honestly. Functional/unit/integration/RL/DB/API coverage is real and well-evidenced. Three categories (security, compatibility, UI) are code-review/documentation only, explicitly and correctly labeled as such, not padded with fabricated test counts. The 18 Docker-sandbox-dependent tests remain unexecuted in this baseline (environment gap, not code defect, and disclosed as such). Qwen/LLM narrative-text quality has **no** quantitative evaluation anywhere in the package or the wider project, a gap the package itself discloses rather than hides (`Qwen_2.5_Evaluator_Validation_Report.md` §F/§G). Speech transcription (WER/CER) accuracy is explicitly marked N/A for lack of reference-transcript data, not silently skipped.

**Real vs. mocked, overall:** The large majority of what's claimed as "executed" in this package genuinely is executed against real code, with real, stored, independently-inspectable logs that this audit cross-checked number-for-number. I found zero instances of a fabricated log, a log that contradicts its own cited document, or a claimed pass/fail count that didn't match the underlying artifact. This is a materially higher standard of evidence discipline than is typical — every quantitative claim I checked either traced cleanly or was explicitly and honestly caveated as unverified/out of scope by the documents themselves.

**Reproducibility by an independent reviewer:** High for the Group-2 scripts — each is a short (under 100 lines), dependency-light, read-only Python script with a `Run:` docstring giving the exact command, importing real production modules directly; an independent reviewer with the same `.venv` and `data/prepaired.db` could rerun every one of them and expect the same (or very similar — the DB row counts would differ if more sessions have been recorded since) results. Lower for the three documentation-only categories (T-N12/13/14), since there is no script to rerun — only prose claims about what was read in the code, which a reviewer would need to re-derive by reading the same files themselves.

**Biggest process-level concern found by this audit (not primarily a "testing quality" issue, but adjacent to it):** the guardrail fix (§6, §16, Fix 1) is a genuine source-code change to a project component (`rl/guardrails.py`) that `CLAUDE.md` treats as governed/frozen-adjacent infrastructure, made in direct response to an inference-behavior observation, whose only recorded "approval" is a self-reported sentence inside the same testing-package document that describes the change. This is not necessarily improper — the document discloses the change thoroughly, diffs cleanly, doesn't touch frozen result files, and is still uncommitted — but it is a pattern (observe → diagnose → fix → self-attest approval, all within one document) that an independent reviewer should specifically ask the project owner to confirm actually happened via out-of-band means (e.g., the owner's own memory of the conversation, or a chat log outside this repo), since no in-repo artifact independently corroborates the approval claim.

**Biggest organizational/naming concern found by this audit:** `testing_and_evaluation/scripts/` contains zero test-related code — it is entirely document-formatting tooling for an unrelated deliverables-packaging task (§15). This should be renamed, relocated, or at minimum clearly sign-posted if the `testing_and_evaluation/` directory is presented to a reviewer as "the testing package," to avoid the false impression that it contains additional automated-test infrastructure.

**Final characterization:** This is a genuine, largely real, well-evidenced, honestly self-limiting testing effort — not an aspirational or fabricated one. Its two actual code fixes are real, diffed, and regression-tested. Its one process risk (guardrail-change governance/approval provenance) and one organizational issue (mislabeled `scripts/` folder) are the two things an independent reviewer should press on; everything else checked out.
