# Chapter 10: Experimentation, Results, and Discussion

**Reproducibility statement, stated once here and governing this entire chapter:** every number below traces to a stored log file or an independently runnable script under `testing_and_evaluation/` in the project repository, generated at git commit `9d5c528b3596d0d80c6bb8d606547f64c036b081` (branch `workspace/human-eval-clean-push`) plus two subsequently applied, documented fixes (§10.1, §10.3). Environment: Python 3.11.9, Stable-Baselines3 2.8.0, sentence-transformers 2.7.0, pytest 9.2.0, on Windows 11 (MINGW64/Git Bash). Full environment and command record: `testing_and_evaluation/Baseline_Record.md` and `Master_Results_Table.md`.

## 10.1 Smoke Testing and the `launch.py` Defect

**Objective:** confirm the full application stack starts correctly. **Procedure:** `python launch.py --backend-only` (evaluator + backend only, the lightest supervised-startup path).

**Result:** both services (evaluator :5000, Flask; backend :8000, FastAPI/uvicorn) started successfully and reached a `ready` state within the launcher's own 45-second readiness check. The backend's own `/health` endpoint confirmed `"pipeline_ready": true`, with the real production evaluator loaded and the real 125-question/125-rubric bank loaded.

**Finding:** `launch.py` itself crashed immediately after startup with `UnicodeEncodeError`, caused by an unguarded `→` (U+2192) character in its startup-banner `print()` statements, on a Windows console using the default `cp1252` code page. The crash occurred in the launcher's own process, after the service subprocesses had already been spawned, leaving them running but orphaned — un-monitored, with no clean Ctrl-C shutdown path.

**Classification:** genuine implementation bug (platform-encoding-dependent), not an environment/dependency gap.

**Fix applied and verified:** `sys.stdout`/`sys.stderr` reconfigured to UTF-8 with `errors="replace"` at module level, before any `print()` executes. Verified by (1) reproducing the exact original crash in isolation under forced `cp1252`, (2) confirming the same print succeeds after the fix under the same forced condition, (3) confirming `launch.py --help` (which exercises the fix's module-level code) runs cleanly under forced `cp1252`, and (4) a full regression-suite rerun showing zero new failures (§10.11).

## 10.2 PPO/RL Provenance Verification and Policy Inference Sanity Check

**Objective:** confirm the deployed RL policy's training provenance as documented in the project's existing evidence record, and confirm the deployed checkpoint functions correctly.

**Finding — training-step discrepancy:** the prior (Phase-2) project report claimed PPO was "trained over 500,000 simulated steps" across seeds (42, 123, 777). Cross-checked against this project's own existing canonical evidence record (which this phase did not generate but is required to cite accurately): the frozen training run used **24,576 timesteps per seed**, seeds **{42, 123, 456, 789, 999}**, and that same evidence record explicitly lists "300,000 PPO steps" as a previously-withdrawn, unsupported figure from other documents. Neither the "500,000" figure nor the (42,123,777) seed set traces to any stored artifact found in this phase. **This report uses the verified figures (24,576 steps/seed, the five-seed set) and flags the Phase-2 report's figures as unverified.**

**Policy inference sanity check (new test, this phase):** the real, frozen, deployed checkpoint (`rl/checkpoints/seed_123/ppo_final.zip` + `vecnormalize.pkl`) was loaded via the actual production wrapper class and exercised with 10 constructed candidate-state scenarios spanning strong/weak/boundary/nervous-expert/floor/ceiling/declining/improving profiles. **Result: 10/10 scenarios produced a valid action (Easier/Same/Harder) and a difficulty remaining within [1,5]; all 10 used the real PPO policy, not the heuristic fallback**, confirming the checkpoint is genuinely loaded and functioning in the current environment. One scenario (score=0.35, moderate confidence/hesitation) produced a raw "Harder" action for a below-average-scoring candidate — this observation is investigated further in §10.3.

## 10.3 Guardrail Verification and the G5 Coverage Gap

**Objective:** confirm the six documented post-inference guardrail rules fire exactly where their stated conditions specify.

**Procedure:** 11 constructed states, covering each rule's documented trigger boundary plus the §10.2 observation, called directly against the real `apply_canonical_guardrails()` function (no mocking).

**Result (before fix):** all 10 of the originally-documented boundary cases matched expected behaviour. **The §10.2 observation (perf=0.35) was empirically confirmed to be a real gap**: no guardrail among the five documented rules covers performance scores in the interval [0.30, 0.40) when the raw policy proposes an escalation and confidence/hesitation are moderate — a below-average-scoring candidate (below the evaluator's own 0.60–0.65 passing threshold) could have difficulty increased with no safety check intervening.

**Diagnosis:** G4/G1 require `perf < 0.30`; G5 (partial-understanding, holds difficulty at "Same") originally required `perf > 0.40`. The interval between these two thresholds was simply unguarded — a boundary-definition oversight, not a logic error within any single rule.

**Fix applied:** G5's lower bound widened from `perf > 0.40` to `perf >= 0.30`, in `rl/guardrails.py`, a single-condition, minimally scoped change. This closes the gap exactly (G4/G1 now cover [0, 0.30), G5 covers [0.30, 0.65) contiguously) without altering any other rule's condition, priority order, or returned action.

**Verification:** rerunning the 11-case test plus two new boundary cases (perf=0.30 exact new boundary; perf=0.299 confirming it still correctly falls to G1) gave **13/13 cases passing, zero mismatches**. A full regression-suite rerun (§10.11) showed zero new failures — the fix is additive and safe.

**Scope note, stated for reproducibility integrity:** this fix changes only the *current/future* behaviour of `rl/guardrails.py`. It does not and cannot retroactively alter any already-generated frozen research result produced under the previous guardrail version; those results remain accurate historical records of that prior version, and any future re-run of that research code from this point forward will reflect the corrected guardrail behaviour — a version difference that must be disclosed, not conflated with the frozen results, in any future research use of this code.

## 10.4 Evaluator API Contract, Service-Framework Correction, and Adversarial Input Testing

**Finding — framework discrepancy:** the Phase-2 report's technology-stack table states the evaluator microservice uses FastAPI. Direct code inspection confirms it is a **Flask** application (`app = Flask(__name__)`, `@app.route` handlers); the Qwen microservice, by contrast, genuinely is FastAPI as claimed. This report corrects the evaluator's framework designation throughout (Chapters 5–6).

**API contract testing (new, this phase):** using Flask's own `test_client()` against the real application object, 7 checks were run: health endpoint, missing-required-field rejection (400), unknown-question-ID rejection (404), valid question-load (200), missing-transcript rejection (400), a full valid evaluate-answer call (200, score in [0,1]), and a malformed-JSON-body request. **Result: 7/7 pass** — the service handles valid, invalid, and malformed input without crashing, consistent with the "graceful degradation" design principle stated in Chapter 7.

**Adversarial/edge-case input testing (new, this phase):** the real `evaluate()` function was called directly with 10 constructed inputs: empty string, whitespace-only, a single word, a 16,500-character repeated-keyword string, non-English/garbled Unicode text, SQL-injection-like text, an HTML script tag, punctuation-only text, emoji spam, and a genuine correct answer as a control. **Result: 10/10 handled without crashing, all scores within [0,1].** One minor observation: empty and whitespace-only input both scored 0.0634 rather than exactly 0.0 — noted as a minor observation, not a defect, and not further investigated in this pass.

## 10.5 Database Testing

**Objective:** verify relational integrity and read/write correctness of the real persistence layer (`data/prepaired.db`).

**Procedure:** direct SQLite inspection of the real, populated database (read-only), plus a write/read roundtrip performed against a disposable temporary copy (never the real file).

**Result:** all three expected tables present (`candidates`, `sessions`, `question_attempts`; 2/26/52 rows respectively). **Zero orphaned foreign keys**: 0 of 52 `question_attempts` rows reference a non-existent session; 0 of 26 `sessions` rows reference a non-existent candidate. A schema-introspected insert-then-read-back roundtrip on the disposable copy succeeded, confirming basic CRUD correctness.

## 10.6 Security Configuration Review (scoped)

**Scope statement:** this is a code-level configuration review, not a penetration test or a claim of "secure" — consistent with this project's own existing evidence record's framing that configuration facts are not the same as measured effectiveness. A full attack-execution test (as the project's prior Paper-1 research already performed, with 4 of 9 attack programs producing a discriminating outcome) was not repeated here, since the Docker daemon was unavailable in this testing environment (§10.9).

**Finding:** direct inspection of `agents/coding_executor/coding_executor.py`'s actual Docker invocation confirms every isolation flag this project's evidence record claims is genuinely present in the current code: non-root execution (`--user 1001:1001`), no network (`--net=none`), all Linux capabilities dropped (`--cap-drop=ALL`), no-new-privileges, CPU/memory/PID limits, a read-only root filesystem, and a size-bounded writable scratch directory. A secondary static pre-flight scanner blocks one dangerous pattern (`ptrace`) and enforces a source-size limit, and is self-documented as an auxiliary filter, with Docker containment as the authoritative isolation boundary.

## 10.7 Performance Spot-Check

**Objective:** a new, independent latency measurement of the real evaluator, explicitly not presented as a reproduction of the project's earlier Paper-1 latency study (different hardware/host, not comparable as an equivalence claim).

**Procedure:** 30 warm, repeated calls to the real `evaluate()` function (after one excluded warm-up call covering model loading, which took ~49.6 seconds).

**Result:** mean 887.7ms, median 896.1ms, p90 955.9ms, p95 986.3ms, p99 1021.1ms (n=30). This is presented as a baseline observation for future optimisation work, not a pass/fail performance requirement (none was formally specified).

## 10.8 Question Selection Correctness and the FAISS-Retrieval Correction

**Finding — architecture discrepancy:** the Phase-2 report's architecture diagrams and prose repeatedly describe question selection as retrieving from a "FAISS VectorStore." Direct inspection of `agents/question_selector/question_selector.py` confirms **zero FAISS or embedding dependency** in this module — it is a deterministic nearest-difficulty-match plus least-recently-asked-topic-rotation algorithm. The FAISS index that does exist in the project is used exclusively by the evaluator (§10.4), for concept-coverage scoring of answers, not for selecting questions. This report corrects this architectural claim throughout.

**Correctness testing (new, this phase):** a simulated 15-question session was run against the real selector logic. **Result:** all 15 selections were distinct questions (no repeats), topic rotation was perfect (no two consecutive turns shared a topic; all 15 available topics were used exactly once), and all 9 tested difficulty-matching queries (including out-of-range targets) returned a value genuinely present in the question bank's difficulty set.

## 10.9 Compatibility, Deployment, and the Docker-Dependent Test Gap

Local `.venv` Python is 3.11.9 against a documented/Dockerized target of 3.12 (both satisfy the project's `pyproject.toml` `>=3.11` constraint — a version drift, not a hard incompatibility). The Docker **daemon** was not running in this testing environment (client v29.7.2 present, confirmed via `docker ps`/`docker version`); this is the single root cause behind 18 of the 19 remaining automated-suite failures in §10.11 and prevented a `docker build` dry-run or a repeat of the project's Paper-1 attack-execution testing. §10.6's code-level review confirms the relevant implementation is correctly configured independent of this gap; starting the daemon in a future session would unlock direct execution-level confirmation.

## 10.10 Structured UI Inspection

A genuine participant usability study was not conducted (no participants, no ethics approval — consistent with this project's own existing evidence record's documented gap in this area) and is not claimed here. Instead, direct code inspection of the two primary React views, corroborated by 28/28 passing automated frontend tests, confirmed deliberate, substantive error/loading-state handling: an explicit loading skeleton and human-readable error card on report-fetch failure (distinguishing "no session found" from "fetch failed"); inline microphone-error and code-execution-error surfacing; and a verified anti-fabrication check (the frontend correctly shows no best-answer UI when the backend reports none exists, rather than fabricating one).

## 10.11 Full Automated Test Suite — Baseline and Final Results

| Metric | Value |
|---|---|
| Python test files | 25 (21 unit, 4 integration) |
| **Final result (post-fix)** | **264 passed, 19 failed, 15 skipped, 0 collection errors** |
| Pass rate | **93.3%** (264/283 executable) |
| Frontend (Vitest) | **28/28 passed (100%)** |
| Regressions from the two Phase-10 fixes (§10.1, §10.3) | **Zero** — identical 264/19/15 split before and after both fixes |

**Every one of the 19 remaining failures is fully attributed**: 18 to the Docker daemon being unavailable (§10.9 — an environment gap, not a code defect; all 18 are tests that execute candidate code in the sandbox), and exactly 1 to a single pre-existing, already-documented known issue (`test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` — an `obs[4]` value of 0.0 where 0.22 is expected), reproduced identically to its existing documented description and deliberately not altered in this phase, consistent with that issue's existing "unresolved, pending a decision" status. **Zero unexplained or newly-discovered defects remain in the suite.**

Two intermediate runs were performed before this final result: an initial run where `pytest`/`pytest-asyncio` were not yet installed (blocking execution entirely), and a second where a further missing dependency (`httpx`, also a pre-existing pinned project requirement, not newly introduced) caused 15 additional non-passes (12 failures + 3 collection errors) before being installed — both resolved as environment-setup steps, not code changes, and both fully documented in the testing package for reproducibility.

## 10.12 Summary of Report-vs-Code Discrepancies Found and Corrected

Nine factual discrepancies between the Phase-2 report and the verified current codebase were found during this phase and are corrected throughout this report (full individual detail in each referenced section above): (1) PPO training step count and seed set (§10.2); (2) the evaluator's described fallback-chain module paths, which do not exist in the codebase (the real mechanism is the R-gated S2 dampening rule documented in Chapter 8 §8.1); (3) an unverified Chapter-6 "Ablation Study" with no matching stored artifact; (4) unverified evaluator-calibration/CrossEncoder-fine-tuning experiment numbers, also with no matching stored artifact located; (5) RL action-space size (§10.2); (6) the FAISS-retrieval question-selection claim (§10.8); (7) the evaluator's web framework (§10.4); (8) the Phase-2 abstract's "93.3% baseline calibration accuracy over 30 sessions" figure, for which a targeted search of all plausible result directories found no supporting stored artifact (every superficial text match for "93.3" in the codebase was confirmed, on inspection, to be a coincidental decimal substring in an unrelated number); (9) the claim that Qwen performs "partial-credit adjustment" on the score, which no code path was found to support — Qwen is confirmed confined to narrative text, hints, and follow-up generation (§10.15).

## 10.13 Scope Finding: The "Bounded-Authority Multi-Agent Coordination" Research Paper

A separate research-paper draft supplied alongside this project's materials (*"Coordination, Specialization, and Bounded Authority in Adaptive Technical Interview Systems"*) describes a second coordinating agent layer (Strategy and Coaching agents with typed-proposal arbitration) and a four-campaign replay/fault-injection/ablation experimental study. **Direct, independent inspection in this phase confirmed this layer and these experiments do not exist anywhere in this codebase** — no second decision-making agent, no arbitration module, and none of the paper's specific numerical results trace to any stored artifact, consistent with a prior internal audit already on record in the project. This report's architecture description (Chapters 5–7) accordingly describes only the real, single-controller system. The research-paper draft's rigorous statistical methodology and analytical framing remain a valuable template, applicable to this project's *real* guardrail-layer findings (§10.3) in any future IEEE-format paper derived from this project — see the accompanying IEEE paper deliverable.

## 10.14 Requirements Traceability Summary

Of the 12 functional/stated objectives enumerated in Chapter 2: **10 are MET** by the evidence in this chapter (two of those with a corrected description relative to the Phase-2 report's original claim); **1 is confirmed unverifiable** (§10.12 item 8); **1 is currently blocked on an external environment gap** (§10.9) with the underlying implementation independently confirmed correctly configured. Full per-objective mapping: `testing_and_evaluation/Requirements_to_Test_Traceability_Matrix.md`.

## 10.15 Qwen 2.5 Evaluator Role Verification and the Ninth Discrepancy

A direct investigation of the actual evaluator/feedback pipeline (full detail: `testing_and_evaluation/Qwen_2.5_Evaluator_Validation_Report.md`) was conducted to answer a standard evaluation-panel question: how is an evaluator that incorporates a large language model itself verified? **The investigation's central finding reframes the question: Qwen 2.5 never computes, adjusts, or influences the numeric score anywhere in the deployed codebase.** `services/evaluator/app.py` (the module computing `final_score`) contains zero references to Qwen; `agents/orchestrator/feedback_agent.py`, where Qwen is actually called, sets `final_score` from a deterministic `score` variable computed *before* the Qwen call and never reassigns it from Qwen's response. Qwen's confirmed role is confined to narrative feedback text, contextual hints, and follow-up question generation — none of which feed back into the grade. **This corrects a ninth discrepancy** (added to the running list in §10.12): the Phase-2 report's description of Qwen as providing "partial-credit adjustment" does not correspond to any code path found. The practical consequence is favourable to the system's defensibility: because the grading decision never depends on an LLM's own judgment, the usual "how do you know the LLM-based evaluator is correct" concern does not apply to this system's scoring mechanism — it applies only, and more narrowly, to the quality of Qwen's generated explanatory text, which this investigation explicitly identifies as not independently, quantitatively validated in this project (a disclosed gap, not resolved in this phase).

## 10.16 Discussion

The testing programme in this chapter was designed, per this project's own stated evidence discipline, to establish genuine confidence rather than to maximise a test count. Its principal findings are fourfold. First, the system's core functional claims are substantially real and now independently re-verified, not merely re-asserted from the Phase-2 report. Second, systematic, code-first verification — rather than trusting prior documentation — surfaced two genuine defects (one a safety-relevant coverage gap, one a platform-compatibility crash) that prior review had not caught, and both were fixed with minimal, regression-verified changes rather than left as findings-only. Third, the same discipline surfaced nine discrepancies between the Phase-2 report's prose and the actual implementation, none of which were previously disclosed; correcting them here, with evidence rather than assertion, is itself a contribution of this phase, independent of any code change. Fourth, the Qwen investigation (§10.15) demonstrates that a system's most scrutiny-attracting component (an embedded LLM) is not always where its actual verification burden lies — in this case, that burden falls entirely on the deterministic scoring path, which was the component this phase tested most directly. Two gaps remain genuinely open rather than resolved: the Docker-daemon-dependent test coverage (§10.9), resolvable simply by starting the daemon in a future session, and the pre-existing known test failure (§10.11), explicitly left for a future decision rather than silently patched.

## 10.17 Final Evaluation Phase — Controlled Improvements and Extended Verification (2026-11-13)

A later, separately-scoped phase of this project extended the testing programme above with authorized, narrowly scoped application code fixes and additional evaluation evidence, on branch `final-eval/controlled-improvements`. Full source record: `testing_and_evaluation/final_evaluation/` (14 documents).

### 10.17.1 Code changes made and regression-verified

| # | File(s) | Defect found | Fix applied | Regression check |
|---|---|---|---|---|
| 1 | `services/qwen/app.py` | LLM-emitted JSON string fields were iterated character-by-character instead of being treated as single-item lists (7 call sites) | New type-checked `_as_str_list()` coercion helper | Reproduced live against the real model before the fix, confirmed absent after |
| 2 | `apps/backend/main.py`, `services/storage/database.py` | Admin dashboard showed only in-memory sessions, losing all history on every backend restart | New read-only `list_sessions()` function merged with live session data (no schema change) | 27 historical sessions recovered, cross-checked against a raw SQL query |
| 3 | `rl/env/interview_env.py` | The dormant, inference-time guardrail-fallback code path still used the pre-fix G5 threshold, inconsistent with the already-fixed `rl/guardrails.py` | Synced the fallback path's boundary to match | 5/5 new boundary cases pass after the fix |

**Full regression suite, re-run before and after all three changes: 264 passed, 19 failed, 15 skipped, identical both times — zero regressions.** Frontend Vitest: 28/28, both times. No model weight, PPO checkpoint, reward function, or database schema was modified; no new PPO training was run.

### 10.17.2 New evaluation evidence

| Finding | Result |
|---|---|
| Gymnasium `check_env()` on `InterviewEnv` (not previously run in this project) | **PASSED**, no warnings |
| PPO checkpoint identity (deployed vs. the checkpoint used for the §10.2/confirmatory-test evidence) | Re-verified via SHA-256 recomputation: confirmed genuinely distinct files, neither modified nor swapped |
| The 0.4825/0.4832 and 0.4897/0.4884 close-value pairs in the project's evaluator-ablation evidence | Reconciled against primary source files: both pairs are correct, already-distinct quantities; no numeric error found in any prior document |
| Qwen narrative-feedback quality (12-criterion rubric, 4 real captured samples — a category not evaluated in §10.1–10.16) | 1 output-corruption defect found and fixed (item 1 above); 1 residual limitation documented, not fixed — a factually-confused explanation in one sample and hallucinated structured-field content in another |
| Hint and session-report generation mechanism | Confirmed template-only (deterministic formatting), **not** LLM-generated — a correction to this report's own earlier description of Qwen's role (§10.15), which should be read as applying specifically to feedback and follow-up-question generation, not to hints or reports |

### 10.17.3 PPO behavior — unchanged, root cause further investigated

The §10.2–10.3 finding stands unchanged: the deployed guardrail layer, not the PPO policy, accounts for the system's measurable adaptive behavior, consistent with this project's pre-registered confirmatory equivalence test. This phase's root-cause analysis of the reward function (`testing_and_evaluation/final_evaluation/11_Experiment_Provenance_Register.md` §3) attributes the policy's near-constant "Same" output to the reward's ~60% weighting toward agreement with a rule oracle computed on the post-guardrail action, rather than to a training failure, and records — without executing — a fully specified alternative-reward experimental protocol for any future, separately pre-registered study.

### 10.17.4 Repository organization

Two README files were added (`testing_and_evaluation/scripts/README.md`, clarifying that directory holds document-formatting utilities rather than tests; `testing_output/README.md`, clarifying its relationship to `testing_and_evaluation/`). Zero files were moved, renamed, or deleted. Full detail: `testing_and_evaluation/final_evaluation/Repository_Structure_Audit.md` and `Repository_Organization_Changes.md`.

### 10.17.5 Complete test register

A single consolidated register of every test described in this chapter plus this phase's additions — 25 rows spanning automated regression suites, the 11 Phase-2/3 targeted scripts, the 6 Final-Evaluation-Phase additions, and the 4 frozen research results — is maintained at `testing_and_evaluation/final_evaluation/15_All_Tests_End_to_End_Report.md`, reproduced in full as Appendix: `PrepAIred_All_Tests_End_to_End_Report.pdf`.
