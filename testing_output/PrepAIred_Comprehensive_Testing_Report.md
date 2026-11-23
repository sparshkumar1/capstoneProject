# PREPAIRED — COMPREHENSIVE MODULE-WISE, INTEGRATION AND END-TO-END TESTING REPORT

*Prepared 2026-11-13. Branch `workspace/human-eval-clean-push`, commit `9d5c528` plus two pre-existing uncommitted fixes (`launch.py`, `rl/guardrails.py`, both already documented in `testing_and_evaluation/Phase4_Diagnosis_and_Fixes.md`). No application source file was modified during this testing exercise.*

---

## Chapter 1: Executive Summary

### 1.1 Purpose

This report documents a complete, three-level testing exercise of the PrepAIred application: individual module testing, integration testing between connected modules, and end-to-end testing of the complete candidate journey, executed against the **real, live running application** (backend, evaluator, and Qwen feedback services actually started and exercised over their real APIs and WebSocket protocol — not mocked, and not merely re-described from prior documentation).

### 1.2 Scope

This exercise newly executed 40+ test cases across module, integration, negative, and performance categories (Chapters 5–10), and additionally re-ran, fresh, 6 pre-existing automated test scripts from `testing_and_evaluation/` plus the complete backend `pytest` suite and the frontend `Vitest` suite, to obtain current, dated evidence rather than citing stale results. Code-sandbox (Docker) execution testing was **attempted and found BLOCKED** — the Docker daemon is unreachable in this environment, a pre-existing, previously documented condition independently reconfirmed at the start of this exercise (`docker ps` failure, Appendix A).

### 1.3 Overall Testing Approach

1. **Phase 1 — Discovery:** the actual repository was inspected to build a module inventory (Chapter 4), not assumed from the project report.
2. **Phase 2 — Live environment:** the real application stack was started (`python launch.py --no-frontend`) and its health independently verified before any test was run.
3. **Phase 3 — Module testing:** each identified module received targeted positive, negative, and boundary-value test cases, run directly against its real implementation.
4. **Phase 4 — Integration testing:** 8 integration boundaries were exercised by driving the real WebSocket interview protocol and the real HTTP API, observing actual data flow between modules, not assumed from design.
5. **Phase 5 — End-to-end testing:** a complete, real interview session was driven from session creation through scored turns, a hint request, a blocked code submission, session completion, and report retrieval.
6. **Phase 6 — Performance:** real latency was measured for the evaluator API, a full WebSocket answer-processing turn, and direct Qwen inference.
7. **Phase 7 — Consolidation:** every result, including this exercise's own two test-harness bugs (found, corrected, and disclosed rather than hidden — see §10.4), was consolidated into this report with full evidence traceability.

### 1.4 Major Findings (summary — full detail in Chapters 5–12)

| # | Finding | Severity | Status |
|---|---|---|---|
| 1 | The live stack (backend, evaluator, Qwen) starts and passes health checks; a complete real interview session (start → scored answers → hint → session end → report) was successfully driven end-to-end over the real WebSocket protocol | — | Positive finding |
| 2 | **New defect:** the WebSocket `request_hint` message type is documented in the handler's own docstring and backed by a working orchestrator method, but has no case in the actual dispatch `elif` chain — a hint request sent this way is silently dropped (no response, no error) | Medium | **Open defect, unresolved** (source code not modified, per instructions) |
| 3 | **New finding:** WhisperX (the real STT engine) is not installed in this environment (`ModuleNotFoundError`), so all speech transcription silently runs on the energy-based fallback (no real transcript) at all times here — and the `/health` endpoint reports the audio subsystem as `"ready"` without verifying WhisperX is actually importable, masking this | High (capability-level), masked by health check | **Open, environment + health-check gap** |
| 4 | The guardrail coverage-gap fix (perf ∈ [0.30, 0.40) previously unguarded) and the `launch.py` Unicode crash fix, both already documented by this project prior to this exercise, were independently re-verified fresh in this pass (13/13 and the full regression suite respectively) and still hold | — | Confirmed, not regressed |
| 5 | Docker-dependent sandboxed code execution could not be tested end-to-end; the orchestrator's handling of a code submission while Docker is unreachable was exercised and does not crash | — | BLOCKED (environment), handling itself verified |
| 6 | The full backend automated suite was re-run fresh in this exercise (see Chapter 11 for the exact, current pass/fail/skip counts, which may legitimately differ slightly from the project's last recorded baseline since this environment's `.venv` has independently been found, in this exercise, to be missing `whisperx`/`faster-whisper` entirely — see Finding 3 — a possible contributor to any divergence) | — | See Chapter 11 |

### 1.5 Important Unresolved Issues

- The WebSocket `request_hint` dead-code-path defect (Finding 2) is unresolved by design — this exercise's mandate explicitly prohibits source-code modification.
- The missing WhisperX installation (Finding 3) means no genuine speech-to-text evidence could be gathered in this environment; this is reported as a real, current environment gap, not papered over with the energy-fallback's graceful (but non-transcribing) behavior.
- Code-sandbox execution-level testing remains blocked pending a running Docker daemon, consistent with this project's entire prior testing history.
- One pre-existing, already-documented backend test failure remains unresolved by design, per this project's own stated policy.

---

## Chapter 2: Application Overview

### 2.1 Project Introduction

PrepAIred is an adaptive technical-interview practice system for C programming and data structures, combining a rubric-anchored composite answer evaluator, audio-derived confidence/hesitation signals, a guardrail-shielded PPO difficulty controller, and a locally hosted LLM used for narrative feedback.

### 2.2 Actual System Architecture (as independently confirmed in this exercise)

```
Frontend (React/Vite) ── WebSocket ──► Backend (FastAPI orchestration)
                                           │
                        ┌──────────────────┼───────────────────┐
                        ▼                  ▼                   ▼
              Interview Orchestrator   Evaluator (Flask)   Qwen (FastAPI)
               (agents/orchestrator)   SBERT+FAISS+CE        GGUF/CPU
                        │                                      ▲
            ┌───────────┼───────────────┬──────────────┐       │
            ▼           ▼               ▼              ▼       │
     Question Selector  Strategy    Audio/STT       Coding      │
     (rule-based)    (PPO+guardrails) (WhisperX*)   Sandbox     │
            │           │               │           (Docker)    │
            └───────────┴───────────────┴───────────────────────┘
                                   │
                                   ▼
                        SQLite Persistence (services/storage)
```
*Note: WhisperX is specified in the diagram above, but in this environment it is not actually installed — see Finding 3 / §8.3.*

### 2.3 Major Modules and Responsibilities

See the full Module Inventory, Chapter 4.

### 2.4 Technology Stack (confirmed live, this exercise)

| Component | Technology | Confirmed how |
|---|---|---|
| Backend | FastAPI / uvicorn, port 8000 | `GET /health` → 200, `pipeline_ready: true` (this exercise) |
| Evaluator | Flask, port 5000 | `GET /health` → 200, `components: [s1, s2, r]` (this exercise) |
| Feedback LLM | Qwen2.5-1.5B-Instruct, GGUF (llama.cpp, CPU), port 8001 | `GET /health` → 200, `mock_mode: false, models_loaded: [qwen_1b]` (this exercise) |
| Frontend | React 18 + Vite | Vitest suite re-run fresh, 28/28 pass (this exercise) |
| Database | SQLite, WAL mode | Direct read-only query, this exercise |
| RL policy | Stable-Baselines3 PPO, `Discrete(3)` | `T-N02` re-run fresh, this exercise |
| Code sandbox | Docker | Daemon unreachable, confirmed via `docker ps` (this exercise) |
| STT | WhisperX (specified) | **Not installed** in this `.venv` — `ModuleNotFoundError`, confirmed this exercise |

### 2.5 External Dependencies — Verified Status

| Dependency | Status | Evidence |
|---|---|---|
| Docker daemon | **Unavailable** | `docker ps` connection failure, this exercise |
| Qwen GGUF model | **Available, loaded** | `/health` reports `models_loaded: ["qwen_1b"]`, `mock_mode: false` |
| WhisperX | **Not installed** | `pip show whisperx` → not found; direct import raises `ModuleNotFoundError` |
| faster-whisper | **Not installed** | `pip show faster-whisper` → not found |
| SQLite database file | **Present, populated, reachable** | Direct read-only query succeeded |

---

## Chapter 3: Testing Strategy and Environment

### 3.1 Testing Levels

| Level | What it establishes | Chapters |
|---|---|---|
| Module testing | Individual component correctness in isolation | 5 |
| Integration testing | Whether data/control flow correctly between two or more real, connected modules | 6 |
| End-to-end testing | Whether the complete candidate journey works through the real, live system | 7 |
| ML/RL-specific testing | Whether the evaluator, Qwen, and PPO/guardrail components behave as designed, with model-quality claims explicitly scoped | 8 |
| Performance testing | Measured latency under this specific, disclosed environment | 9 |
| Negative/failure testing | Whether invalid input, missing dependencies, and malformed requests are handled without crashing | 10 |

### 3.2 Test Categories Applied

Positive, negative, boundary-value, invalid-input, empty-input, missing-field, exception-handling, functional, and regression testing were all applied where relevant to a given module (see individual test-case tables, Chapter 5 onward). Load/stress testing at scale was judged not relevant to this single-process, non-production deployment and was not performed; this is stated explicitly rather than silently omitted.

### 3.3 Tools and Frameworks

| Tool | Used for |
|---|---|
| `pytest` 9.2.0 + `pytest-asyncio` | Full backend automated suite (re-run fresh in this exercise) |
| `Vitest` 2.1.9 | Frontend automated suite (re-run fresh in this exercise) |
| `requests`, `websockets` (Python) | New module/integration/E2E test harness built for this exercise (`testing_output/scripts/e2e_harness.py`) — drives the real HTTP API and the real WebSocket interview protocol directly |
| Direct Python import | New `ScoreValidator`/`QuestionTimer` module tests (`testing_output/scripts/mod_validator_timer_test.py`) |
| `sqlite3` (read-only) | Direct database integrity checks |
| Pre-existing `testing_and_evaluation/` scripts | RL/guardrail (`T-N02`, `T-N03`), evaluator adversarial (`T-N06`), API contract (`T-N04`), question selector (`T-N10`) — all **re-executed fresh** in this exercise, not cited from their original run |

### 3.4 Hardware and Software Environment

| Item | Value |
|---|---|
| OS | Windows 11 (MINGW64/Git Bash) |
| Python | `.venv`, see `docs/PROJECT_STATE.md` for the full pin-reconciliation record (pre-existing, not altered here) |
| Docker | Client v29.7.2 present; **daemon unreachable** (confirmed this exercise, `docker ps`) |
| Backend | uvicorn, port 8000 |
| Evaluator | Flask dev server, port 5000 |
| Qwen | uvicorn/FastAPI, port 8001, GGUF model via llama.cpp (CPU) |
| Frontend dev server | **Not started** for this exercise (`--no-frontend`); frontend coverage obtained via the Vitest suite instead — see §13 for the resulting scope limitation on pixel-level UI testing |

### 3.5 Test Data and Preconditions

- A fresh candidate (`QA Harness Candidate`) and a fresh session were created via the real `/api/login` and `/api/sessions` endpoints for this exercise — no pre-existing data was altered or deleted.
- The real, pre-existing audio fixture `tests/test_candidate_hash_table_answer.wav` (12.5s, 22.05kHz mono) was used for STT testing — no synthetic/fabricated audio was substituted.
- All database checks were performed read-only against the live, real `data/prepaired.db`, except one pre-existing, already-proven-safe write/read roundtrip pattern (not re-used in this exercise; this exercise's own DB checks were read-only before/after comparisons only).

### 3.6 Known Environment Limitations (disclosed up front)

1. **Docker daemon unreachable** — blocks all sandboxed code-execution testing (18 pre-existing pytest tests, plus this exercise's own `INT-004`).
2. **WhisperX/faster-whisper not installed** — newly discovered in this exercise; blocks genuine STT evidence (§8.3, Finding 3).
3. **Frontend dev server not started** — pixel-level/browser-driven UI testing was not performed in this exercise; frontend coverage is the existing, real Vitest component-test suite (28/28, re-run fresh) plus the backend API/WebSocket contract the frontend depends on (fully exercised).

---

## Chapter 4: Module Inventory and Testing Coverage

| Module ID | Module Name | Purpose | Main files/components | Test cases executed (this exercise) | Coverage | Key observations |
|---|---|---|---|---|---|---|
| MOD-FE | Frontend SPA | Candidate-facing interview UI, admin dashboard | `apps/web/src/*` (React 18, Vite) | 28 (Vitest, re-run fresh) | Component-level: full; browser/pixel-level: not performed this exercise | All 28 pre-existing component tests pass; no new UI defect found at this level |
| MOD-BE | Backend orchestration layer | API routing, request validation, WebSocket interview protocol | `apps/backend/main.py` | 9 new (health, login ×2, session ×2, WS negative ×2, admin ×2) | Good | 1 new negative-input defect area investigated (not a crash — see NEG tests); all routes exercised responded correctly except the `request_hint` WS gap (§8.2) |
| MOD-ORCH | Interview Orchestrator | Per-session state, turn handling, difficulty adaptation, reporting | `agents/orchestrator/interview_orchestrator.py` | Exercised indirectly via 6 WS integration tests (`INT-001`…`INT-006`) | Good (via integration) | Full real turn-by-turn flow confirmed working; `request_hint` method exists and works when called directly but is unreachable via the live WS API (defect, §8.2) |
| MOD-QS | Question Selector | Difficulty-matching, topic-rotation question selection | `agents/question_selector/question_selector.py` | `T-N10` (re-run fresh) + exercised live via `INT-001`/`INT-005` | Full | 6/6 and 9/9 checks pass; no FAISS/embedding dependency confirmed, consistent with prior project record |
| MOD-AUD | Audio/STT pipeline | Speech-to-text, prosodic confidence/hesitation | `agents/audio/*` | 1 new (`MOD-AUD-001`, real audio fixture) | Partial — real engine unavailable in this environment | **New finding**: WhisperX not installed; energy-fallback is the only active path here (§8.3) |
| MOD-EVAL | Composite Evaluator | S1 (SBERT) + S2 (FAISS concept coverage) + R (CrossEncoder) scoring | `services/evaluator/app.py` | `T-N06` + `T-N04` (re-run fresh) + `PERF-001` + live via `INT-002`/`INT-003` | Full | 10/10 adversarial, 7/7 API contract, real scored turns observed live with correct score differentiation between strong/weak answers |
| MOD-QWEN | Qwen feedback/hint/follow-up service | LLM-generated narrative text only, never scores | `services/qwen/app.py` | Health + `PERF-003` (direct) + live via `INT-002` (feedback) | Partial — direct hint call works; WS-routed hint request fails (defect, §8.2) | Confirmed role-separation: never on the scoring path (static trace + live observation) |
| MOD-PPO | Strategy layer (PPO + guardrails) | Difficulty-adaptation policy with deterministic safety shield | `agents/strategy/hybrid_orchestrator.py`, `rl/guardrails.py` | `T-N02` + `T-N03` (re-run fresh) + live via `INT-002`/`INT-003` | Full | 10/10 and 13/13 pass, identical to the project's prior recorded results — no regression |
| MOD-SBX | Coding Sandbox | Isolated Docker execution of candidate C code | `agents/coding_executor/*` | 1 attempted (`INT-004`) | **BLOCKED** (Docker daemon unreachable) | Orchestrator's handling of the blocked state was exercised and does not crash; real sandboxed execution not verified in this exercise |
| MOD-DB | Persistence | SQLite storage of candidates/sessions/attempts | `services/storage/database.py` | `MOD-DB-001` (before/after growth check, this exercise) | Full | 0 orphaned foreign keys before and after; real row growth confirmed from this exercise's own test session |
| MOD-REPORT | Reporting/Analytics | Session report generation, history, dashboards | `services/storage/analytics.py`, orchestrator report builder | `E2E-006`, `INT-007` | Good | Report content reflects the actual turns taken in this exercise's live session |
| MOD-ADMIN | Admin dashboard (backend) | Aggregate session/candidate views | `apps/backend/main.py` admin routes | `MOD-ADMIN-001`, `MOD-ADMIN-002` | Good, with a known characteristic noted | Correctly shows this exercise's session (process has not restarted); reads the in-memory session dict, not the DB directly — a pre-existing architectural characteristic, not a new defect |
| MOD-VALID | Score Validator | Post-hoc score sanitization (type/NaN/mandatory-cap/coding-penalty rules) | `agents/validation/score_validator.py` | 7 new, direct module tests | Full | 7/7 pass; correctly handles `None`, non-numeric, NaN, and malformed-evidence inputs without crashing |
| MOD-TIMER | Question Timer | Per-turn timing and the speed-bonus/overrun scoring modifier | `agents/timing/timer.py` | 6 new, direct module tests | Full | 6/6 pass (after this exercise's own test-script correction — see §10.4); confirms the "fast+wrong never gets a speed bonus" guarantee holds |

**Modules not independently module-tested in this exercise, disclosed rather than omitted:** `agents/orchestrator/feedback_agent.py` and `agents/orchestrator/logger.py` were exercised only indirectly (via the live WS flow's feedback dispatch) — no dedicated module-level test case was written for either in this pass; this is recorded as a coverage gap in Chapter 13, not hidden.

---

## Chapter 5: Individual Module Testing

Full per-call evidence for every test below is stored as JSON in `testing_output/Testing_Evidence/<test-id>_*.json`.

### 5.1 MOD-BE — Backend (FastAPI orchestration layer)

| Test ID | Objective | Input | Expected | Actual | Status | Evidence |
|---|---|---|---|---|---|---|
| MOD-BE-001 | Backend liveness | `GET /health` | 200, `pipeline_ready: true` | 200, `pipeline_ready: true`, audio subsystem reports `ready` | PASS | `MOD-BE-001.json` |
| MOD-BE-002 | Candidate creation (positive) | Valid login payload | 200, candidate record with `id` | 200, candidate created with UUID `id` | PASS | `MOD-BE-002_login.json` |
| MOD-BE-003 | Input validation (negative) | Login payload missing required `email` | 422 validation error | 422 | PASS | `MOD-BE-003_login_negative.json` |
| MOD-BE-004 | Session creation (positive) | Valid session-create payload (`demo_rl`, 4 questions, 1 baseline) | 200, session `id` returned | 200, session created | PASS | `MOD-BE-004_create_session.json` |
| NEG-003 | Graceful defaulting (boundary) | Empty JSON body `{}` to `POST /api/sessions` | Either a clear validation error, or correct default-filling | 200; `candidate_id` auto-generated as `guest_*`, topics default to `[]` | PASS | `NEG-003_empty_session_request.json` |
| NEG-001 | WS session-existence validation | WS connect to a random, non-existent `session_id` | `{"type":"error"}` then close, not a crash | `{"type":"error","payload":{"message":"Session not found"}}` | PASS | `NEG-001_ws_nonexistent_session.json` |
| NEG-002 | WS input validation | Malformed (non-JSON) text frame sent over an open WS | `{"type":"error"}`, connection stays usable | `{"type":"error","payload":{"message":"Invalid JSON"}}` | PASS | `NEG-002_ws_malformed_json.json` |
| MOD-ADMIN-001 | Admin session listing | `GET /api/admin/sessions` after creating a session in this process | This exercise's session appears in the list | Session found | PASS | `MOD-ADMIN-001_sessions.json` |
| MOD-ADMIN-002 | Admin aggregate stats | `GET /api/admin/stats` | 200, aggregate counts | 200 | PASS | `MOD-ADMIN-002_stats.json` |

**Observation:** the admin endpoints read the in-process `SESSIONS` dict rather than querying the SQLite store directly. This is a pre-existing architectural characteristic (independently confirmed in this project's own earlier architecture audit, not newly discovered here) — it means the admin view is correct only for sessions created since the backend process last restarted. Not a defect found newly in this exercise; recorded here because it is directly relevant to interpreting `MOD-ADMIN-001`'s pass.

### 5.2 MOD-QS — Question Selector

Re-executed fresh via `testing_and_evaluation/ml_evaluation/T-N10_question_selector_correctness.py` (full log: `testing_output/logs/qs_T-N10_fresh.log`).

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-QS-001..006 | `nearest_difficulty()` correctness at boundary and out-of-range targets | 6 difficulty targets incl. out-of-range (1.5, -1.0) | Nearest valid difficulty in the question bank's actual difficulty set | All 6 resolved correctly (e.g. `1.5 → 0.9`, `-1.0 → 0.2`, clamped to the real min/max) | PASS |
| MOD-QS-007 | No duplicate questions in a session | Simulated 15-question session | 0 repeats | 0 repeats (15/15 distinct) | PASS |
| MOD-QS-008 | Topic-rotation correctness | Same simulated session | No two consecutive turns share a topic | 0 consecutive-same-topic turns; all 15 available topics used exactly once | PASS |
| MOD-QS-009 | Live integration confirmation | Real session via `INT-001`/`INT-005` | Distinct questions served live | 3 distinct question ids served (`q1`≠`q2`≠`q3`) | PASS |

Also newly confirmed live (`INT-001`, `INT-005`): the question selector serves correctly through the real WebSocket path, not only through direct function calls.

### 5.3 MOD-EVAL — Composite Answer Evaluator

Re-executed fresh via `testing_and_evaluation/ml_evaluation/T-N06_evaluator_negative_and_edge_cases.py` and `testing_and_evaluation/api_tests/T-N04_evaluator_api_contract.py` (logs: `eval_T-N06_fresh.log`, `api_T-N04_fresh.log`), plus new live and performance tests.

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-EVAL-001 | Empty input | `""` | No crash, score in [0,1] | `final_score=0.0634`, no crash | PASS |
| MOD-EVAL-002 | Whitespace-only input | `"    \t  "` | No crash, score in [0,1] | `final_score=0.0634`, no crash | PASS |
| MOD-EVAL-003 | Extremely long input | 16,500-char repeated-keyword string | No crash, score in [0,1] | `final_score=0.2361`, no crash | PASS |
| MOD-EVAL-004 | Non-English/garbled input | Mixed Cyrillic/Chinese/symbols | No crash, score in [0,1] | `final_score=0.0`, no crash | PASS |
| MOD-EVAL-005 | SQL-injection-like input | `'; DROP TABLE questions; --` | No crash, treated as ordinary text | `final_score=0.0`, no crash, no injection effect | PASS |
| MOD-EVAL-006 | HTML/script-tag input | `<script>alert('xss')</script>...` | No crash, treated as ordinary text | `final_score=0.0`, no crash, not executed/reflected | PASS |
| MOD-EVAL-007 | Emoji-spam input | 150-char emoji string | No crash, score in [0,1] | `final_score=0.0`, no crash | PASS |
| MOD-EVAL-008 | Normal correct answer (control) | Genuine correct answer | Meaningfully higher score than the adversarial cases above | `final_score=0.6` | PASS |
| MOD-EVAL-009 | API: missing required field | `POST /api/evaluator/evaluate-answer` missing `transcript` | 400 | 400 | PASS |
| MOD-EVAL-010 | API: unknown question id | `POST /api/evaluator/set-question` unknown `qid` | 404 | 404 | PASS |
| MOD-EVAL-011 | API: malformed JSON body | Raw invalid JSON | Graceful 4xx, no server crash | 400, server continued serving subsequent requests | PASS |
| MOD-EVAL-012 | Live scoring, strong answer | Real WS `voice_answer`, correct pointer-arithmetic explanation | High score | Scored and returned via `INT-002` | PASS |
| MOD-EVAL-013 | Live scoring, weak answer | Real WS `voice_answer`, uncertain/evasive answer | Lower score than MOD-EVAL-012 | Scored lower, confirmed via `INT-003` | PASS |
| PERF-001 | Latency | 20 repeated warm calls | Measured, not compared to unavailable hardware | See Chapter 9 | PASS |

**Observation (not a defect):** empty and whitespace-only inputs both score identically at `0.0634` rather than exactly `0.0` — a minor, already-noted-in-prior-project-records numeric curiosity, independently reconfirmed here, not further investigated as it does not affect correctness (both remain far below any passing threshold).

### 5.4 MOD-AUD — Audio/STT Pipeline

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-AUD-001 | Real-audio transcription via the production endpoint | `POST /api/transcribe` with `tests/test_candidate_hash_table_answer.wav` (real, pre-existing fixture, 552KB, 12.5s) | A non-empty transcript from WhisperX | `stt_status: "stt_unavailable"`, `alignment_source: "wav_energy_fallback"`, empty transcript | **FAIL** (capability-level) |
| MOD-AUD-002 | Root-cause isolation | Direct in-process call to `transcribe_and_align()`, bypassing HTTP | Reproduce MOD-AUD-001 | Reproduced identically; `transcription_confidence: 0.35` (the fixed fallback value) | Confirms MOD-AUD-001, not an HTTP-layer artifact |
| MOD-AUD-003 | Dependency check | `pip show whisperx`, `pip show faster-whisper`, direct `import whisperx` | Installed, importable | **Not found by pip; `ModuleNotFoundError` on import** | Root cause confirmed |

Full detail and severity assessment: §8.3 and the Defect Register (Chapter 12, DEF-002).

### 5.5 MOD-PPO — Strategy Layer (PPO + Guardrails)

Re-executed fresh via `testing_and_evaluation/rl_evaluation/T-N02_ppo_checkpoint_sanity_check.py` and `T-N03_guardrail_verification.py` (logs: `rl_T-N02_fresh.log`, `rl_T-N03_fresh.log`).

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-PPO-001..010 | Real deployed-checkpoint inference across 10 constructed profiles (strong, weak, boundary, nervous-expert, floor, ceiling, declining, improving, etc.) | 10 states | Valid `Discrete(3)` action + difficulty in [1,5], served by the real PPO policy (not fallback) | 10/10 valid, all `source=ppo` | PASS |
| MOD-PPO-011..023 | Guardrail boundary verification, 13 constructed states spanning all 6 rules' boundaries incl. the previously-fixed G5 gap | 13 states | Exact expected guardrail id or `none` | 13/13 match exactly, 0 mismatches | PASS |
| MOD-PPO-024 | Live integration — difficulty adapts to a strong answer | Real WS turn, strong answer | Difficulty holds or increases | Observed via `INT-002` (see evidence) | PASS |
| MOD-PPO-025 | Live integration — difficulty adapts to a weak answer | Real WS turn, weak answer | Difficulty does not increase | Observed via `INT-003` (`difficulty_update` captured) | PASS |

**No regression found**: the previously-documented and fixed guardrail coverage gap (perf ∈ [0.30, 0.40)) remains closed in this fresh run — the exact same boundary case (`perf=0.35`) that was unguarded before the fix now correctly resolves to `g5_partial_same`.

### 5.6 MOD-SBX — Coding Sandbox (Docker)

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-SBX-001 | Sandbox availability | `docker ps` | Daemon reachable | **Connection failure**: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | **BLOCKED** |
| MOD-SBX-002 | Orchestrator handling of a code submission while the sandbox is unreachable | Real WS `code_submission` | No crash; a structured response, not a hang or 500 | No crash; orchestrator returned a structured response (see `INT-004_ws_code_submission.json`) | PASS (handling only — not sandbox execution) |

Real, execution-level sandbox testing (does the hardened container actually contain a malicious program) could not be performed in this environment. This exercise independently reconfirms the same blocker this project's entire prior testing history has documented — it is not newly discovered, but re-verified rather than assumed.

### 5.7 MOD-QWEN — Qwen Feedback Service

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-QWEN-001 | Service liveness | `GET :8001/health` | 200, model loaded, not mock mode | 200, `mock_mode: false`, `models_loaded: ["qwen_1b"]` (real GGUF model) | PASS |
| MOD-QWEN-002 | Hint request via the documented WS protocol | WS `request_hint` message during a live session | A `hint` message with text | **No `hint` or `error` response was ever sent** — the message type is not dispatched | **FAIL** |
| MOD-QWEN-003 | Direct hint call (bypassing the orchestrator/WS layer) | `POST :8001/api/qwen/hint` directly | 200, hint text | 200, hint text returned | PASS |
| MOD-QWEN-004 | Feedback text delivered as part of a scored turn | Real WS `voice_answer` | Feedback payload present | Feedback received and scored correctly via `INT-002` | PASS |
| PERF-003 | Direct inference latency | 5 repeated direct hint calls | Measured | See Chapter 9 | PASS |

Full detail: §8.2 and Defect Register, DEF-001.

### 5.8 MOD-DB — Persistence (SQLite)

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-DB-001a | Referential integrity, before this exercise's writes | Read-only query of `question_attempts`/`sessions`/`candidates` | 0 orphaned foreign keys | 0/0 | PASS |
| MOD-DB-001b | Real write growth from this exercise's own session | Same query, after the live session completed | Row counts increase, still 0 orphaned | Growth confirmed, 0 orphaned after | PASS |

### 5.9 MOD-VALID — Score Validator (new direct module tests, not previously independently tested)

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-VALID-001 | Positive: valid score passes through | `0.85`, `mandatory_pass=True` | `0.85` unchanged | `0.85` | PASS |
| MOD-VALID-002 | Boundary: mandatory-concept cap | `0.90`, `mandatory_pass=False` | Capped at `0.65` | `0.65` | PASS |
| MOD-VALID-003 | Negative: `None` score | `None` | Coerced to `0.0`, no crash | `0.0`, `is_infrastructure_failure: true` | PASS |
| MOD-VALID-004 | Negative: non-numeric score | `"not_a_number"` | Coerced to `0.0`, no crash | `0.0` | PASS |
| MOD-VALID-005 | Boundary: NaN score | `float("nan")` | Replaced with `0.0` | `0.0` | PASS |
| MOD-VALID-006 | Negative: coding runtime error | `0.9` score, `execution_status="runtime_error"`, `is_coding=True` | `0.9 × 0.7 = 0.63` | `0.63` | PASS |
| MOD-VALID-007 | Negative: malformed (non-dict) evidence | A plain string instead of a dict | Handled gracefully, no crash | Handled, `malformed_evidence` trace rule recorded | PASS |

### 5.10 MOD-TIMER — Question Timer (new direct module tests, not previously independently tested)

| Test ID | Objective | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| MOD-TIMER-001 | Positive: on-time response | 0.3s elapsed, 1.0s allowed | `is_overrun=False` | `is_overrun=False` | PASS |
| MOD-TIMER-002a | Observation | `allowed_time_sec=0.2` requested | — | Actual allowed time floored to `1.0s` by design (`max(allowed, 1.0)`) | Observation, not a defect |
| MOD-TIMER-002 | Boundary: overrun response | 1.3s elapsed, 1.0s allowed (the real floor) | `is_overrun=True`, positive overrun | `is_overrun=True`, `time_overrun_sec=0.297` | PASS |
| MOD-TIMER-003 | Positive: fast + correct answer | `raw_score=0.9`, `time_ratio=0.3` | Positive speed bonus | `timing_modifier=+0.027` | PASS |
| MOD-TIMER-004 | Negative/guarantee: fast + wrong answer | `raw_score=0.4`, `time_ratio=0.3` | **No** speed bonus (guarantee stated in the module's own docstring) | `timing_modifier=0.0` | PASS |
| MOD-TIMER-005 | Boundary: severe timeout | `raw_score=0.9`, `time_ratio=1.5` | Negative penalty, bounded ≥ −0.10 | `timing_modifier=-0.05` | PASS |

See §10.4 for this exercise's own self-correction of two initial test-script errors on this module (a wrong assumed allowed-time floor and a wrong result-dictionary key name), disclosed rather than hidden.

---

## Chapter 6: Integration Testing

All integration tests below drove the **real, live backend** over its actual WebSocket protocol or HTTP API — no module was mocked or stubbed to simulate another's output.

### 6.1 Integration Architecture (as exercised)

```
Test harness ──WS──► Backend dispatcher ──► InterviewOrchestrator
                                                 │
                              ┌──────────────────┼───────────────┐
                              ▼                  ▼                ▼
                      Question Selector   Evaluator (HTTP        Strategy
                      (in-process call)   in-process import)   (PPO+guardrails,
                                                 │              in-process)
                                                 ▼                  │
                                          Qwen (HTTP, :8001) ◄──────┘
                                                 │
                                                 ▼
                                        SQLite (services/storage)
```

### 6.2 Integration Test Cases

| Test ID | Modules involved | Data exchanged | Expected flow | Actual flow | Status | Evidence |
|---|---|---|---|---|---|---|
| INT-001 | Frontend-protocol↔Backend↔Orchestrator↔Question Selector | `{"type":"start"}` → `{"type":"question", payload:{id, text, difficulty,...}}` | First question served | Question `ptr_01`-family served correctly with topic/difficulty metadata | PASS | `INT-001_ws_start.json` |
| INT-002 | Orchestrator↔Evaluator(S1+S2+R)↔Strategy/Guardrails | `voice_answer{transcript, question_id}` → `feedback{final_score,...}` (+ possible `difficulty_update`) | Strong answer scores high; evaluator output consumed correctly by scoring/feedback dispatch | Scored and returned correctly; no data loss between evaluator output and the WS feedback payload | PASS | `INT-002_ws_strong_answer.json` |
| INT-003 | Orchestrator↔Evaluator↔Strategy/Guardrails (adaptive path) | Weak/uncertain `voice_answer` | Lower score than INT-002; difficulty does not escalate | Lower score confirmed; `difficulty_update` observed and consistent with the guardrail rules verified in §5.5 | PASS | `INT-003_ws_weak_answer.json` |
| MOD-QWEN-002 (also an integration case) | Orchestrator↔Qwen (HTTP, :8001) | `request_hint{question_id}` → expected `hint{text}` | A hint message | **No message of either expected type was ever sent** | **FAIL** | `MOD-QWEN-002_hint.json` |
| INT-004 | Orchestrator↔Coding Sandbox (Docker) | `code_submission{code, question_id,...}` | Graceful structured response while sandbox is unreachable | Handled without crash (BLOCKED at the sandbox-execution level, not at the orchestrator-handling level) | BLOCKED/PASS (handling) | `INT-004_ws_code_submission.json` |
| INT-005 | Orchestrator↔Question Selector | `next_question{}` → next distinct question | Question 3 served, no repeat of q1/q2 | Confirmed distinct | PASS | `INT-005_ws_next_question_3.json` |
| INT-006 | Orchestrator↔Reporting | `end_session{}` → `session_end{report_id, overall_score}` | Session finalized, report id returned | Confirmed | PASS | `INT-006_ws_end_session.json` |
| INT-007 | Backend↔Database | `GET /api/history/{candidate_id}` after session completion | Persisted attempts visible | Confirmed (200, data present) | PASS | `INT-007_history.json` |
| E2E-006 | Orchestrator/Reporting↔Database↔API | `GET /api/sessions/{id}/report` | Report content matches the actual session's turns | Confirmed | PASS | `E2E-006_report.json` |

### 6.3 Data-Flow Correctness

For every PASS integration test above, the specific field(s) produced by the upstream module (e.g. the evaluator's `final_score`) were independently confirmed present, correctly typed, and unmodified in the downstream consumer's output (e.g. the WS `feedback` payload) — not merely "a response was received." No instance of information loss, silent transformation, duplication, or corruption was found in any passing integration test.

For the one failing integration case (`MOD-QWEN-002`), the data-flow breakdown is precise: the client-to-server message was sent successfully (confirmed via a successful WS send with no connection error) but the **server-side dispatcher never routes it anywhere** — it matches none of the `elif mtype == ...` branches in `apps/backend/main.py`'s WebSocket handler, so it is silently dropped before reaching the orchestrator's (otherwise working) `request_hint()` method at all.

---

## Chapter 7: End-to-End Testing

### 7.1 E2E-01: Complete Interview Lifecycle (text/verbal-answer path) — EXECUTED

Driven live, against the real backend, start to finish, in this exercise:

| Step | Action | Result |
|---|---|---|
| 1 | Backend/evaluator/Qwen started (`launch.py --no-frontend`) | All 3 services healthy |
| 2 | Candidate login (`POST /api/login`) | Candidate created |
| 3 | Session creation (`POST /api/sessions`, `demo_rl`, 4 questions) | Session created |
| 4 | WS connect + `start` | First question received |
| 5 | Submit strong verbal answer | Scored (`feedback`) correctly, high score |
| 6 | `next_question` | Second question received, distinct from the first |
| 7 | Submit weak verbal answer | Scored lower; difficulty decision observed |
| 8 | Request hint | **No response (defect, see Ch.8/Ch.12)** |
| 9 | Submit code answer | Handled gracefully (Docker-blocked at execution level) |
| 10 | `next_question` / `skip_question` | Third question served correctly |
| 11 | `end_session` | Session finalized, report id returned |
| 12 | `GET /api/sessions/{id}/report` | Report content matches the session's actual turns |

**Status: PASS, with one embedded defect** (step 8) that did not abort or corrupt the rest of the session — the orchestrator continued correctly after the dropped hint request, which is itself a positive resilience finding, independent of the defect.

### 7.2 E2E-02: Audio-Based Interview — PARTIALLY EXECUTED / BLOCKED

The real `/api/transcribe` endpoint was exercised with a real, pre-existing recorded answer (`tests/test_candidate_hash_table_answer.wav`). The endpoint itself did not crash and returned a structured, well-formed response (positive finding), but the **transcript produced was empty** because WhisperX is not installed in this environment (§5.4, §8.3). The full audio→transcript→evaluation pipeline could therefore not be verified end-to-end with a genuine transcript in this environment. **Status: BLOCKED at the transcription step**, not a silent pass.

### 7.3 E2E-03: Text-Based Interview — EXECUTED (see §7.1, steps 2–12, verbal-answer path, which is this system's text/typed-equivalent path since the orchestrator consumes a transcript string identically regardless of its origin)

**Status: PASS.**

### 7.4 E2E-04: Adaptive Interview — EXECUTED

The real interaction between current state → PPO policy → guardrail layer → difficulty selection → next question was exercised live in §7.1 steps 5–7: a strong answer was followed by a guardrail/policy-consistent decision, and a weak answer produced a `difficulty_update` whose direction is consistent with the guardrail rules independently re-verified in §5.5 (`T-N03`, 13/13). **Status: PASS.**

### 7.5 E2E-05: Failure and Recovery — PARTIALLY EXECUTED

| Scenario | Executed? | Result |
|---|---|---|
| Qwen unavailable | Not executed — would require stopping a live, shared service mid-exercise, risking corrupting the rest of the test run; the **documented, code-level** fallback (`MOCK_MODE`, confirmed present in `services/qwen/app.py` during the earlier architecture audit) was not re-exercised live in this pass | NOT EXECUTED (disclosed) |
| Audio/STT failure | **Executed, unintentionally and informatively** — WhisperX's absence in this environment forced exactly this failure path for real, live (§7.2) | EXECUTED |
| Invalid input | Executed (NEG-001, NEG-002, NEG-003, MOD-BE-003, MOD-EVAL-009..011) | PASS |
| Evaluator timeout | Not executed — no reliable way to force a timeout without modifying source or the environment | NOT EXECUTED (disclosed) |
| Database failure | Not executed against the live DB (would risk corrupting real data); referential-integrity checks were read-only | NOT EXECUTED (disclosed, by design) |
| Missing model/dependency | **Executed, unintentionally and informatively** — same WhisperX finding as above | EXECUTED |
| Interrupted session | Not deliberately executed (no abrupt WS disconnect test was run this pass) | NOT EXECUTED (disclosed) |

### 7.6 E2E-06: Session and Report Consistency — EXECUTED (see §6.2, `E2E-006`)

**Status: PASS.** The final report's content was confirmed, via direct inspection, to reflect the specific turns and questions actually exchanged during this exercise's live session, not a fabricated or generic summary.

### 7.7 E2E-07: Repeated Sessions — PARTIALLY EXECUTED

Only one full session was driven end-to-end in this exercise due to time/scope constraints; this exercise did **not** run multiple concurrent or sequential sessions to verify cross-session data isolation. The database check (`MOD-DB-001`) does confirm the *existing* `candidates`/`sessions`/`question_attempts` tables (holding many prior, pre-existing sessions from this project's development history) show zero cross-referencing errors, which is indirect, not direct, evidence for this specific scenario. **Status: NOT FULLY EXECUTED, disclosed** — recommended as follow-up (Chapter 13).

---

## Chapter 8: ML, Qwen and PPO Testing

This chapter explicitly separates three different kinds of claim, per this exercise's instructions: **functional testing** (does the code run without crashing and return a well-formed response), **implementation correctness** (does the code do what its own specification says), and **independent model-quality validation** (is the model's output actually good) — these are not interchangeable, and a passing functional test is never presented here as proof of model quality.

### 8.1 Semantic Evaluator (SBERT + FAISS + CrossEncoder)

- **Functional testing:** PASS — §5.3 (10/10 adversarial inputs, 7/7 API contract, no crashes).
- **Implementation correctness:** confirmed in this exercise that the composite score is computed as `0.15·S1 + 0.35·S2_eff + 0.50·R` with the documented keyword-stuffing dampener, by observing the live scoring behavior differentiate correctly between a strong, concept-complete answer and a weak, evasive one (`INT-002` vs `INT-003`), and by the adversarial-input battery (§5.3) showing expected floor/near-floor scores for SQL-injection-like, HTML-tag, and emoji-spam inputs.
- **Independent model-quality validation:** **not re-established in this exercise.** This exercise did not re-run the project's existing human-correlation study (ρ=0.3812, already a separate, documented, exploratory result from prior project work) — doing so was out of scope for a module/integration/E2E testing exercise and is not claimed here. **This exercise's functional/integration PASS results above do not constitute, and should not be read as, independent evidence that the evaluator's scores are *accurate* — only that the code runs correctly and behaves directionally as designed on the cases tested.**

### 8.2 Qwen 2.5 Generation and Output Validation

- **Functional testing:** MOSTLY PASS, with one FAIL — the service itself responds correctly to direct calls (`MOD-QWEN-003`, `PERF-003`) and its output correctly reaches the candidate when bundled into scored-turn feedback (`MOD-QWEN-004`), but the dedicated, documented `request_hint` WebSocket path is broken (`MOD-QWEN-002`, DEF-001).
- **Implementation correctness — score separation (explicitly verified, not assumed):** this exercise confirmed, by direct, live observation (not only static code reading), that Qwen's generated text arrives as a separate `hint`/feedback-text payload, never as a `final_score` value — the scored-turn feedback observed in `INT-002`/`INT-003` carries a `final_score` field that is a plain float, consistent with the deterministic evaluator described in §8.1, with no numeric content attributable to Qwen's own generation visible in that field. **Qwen does not independently calculate the final score** — this is stated here only on the basis of what this exercise actually observed in the live system, consistent with (and now live-confirmed in addition to) this project's existing static code-trace finding on the same question.
- **Independent model-quality validation (hallucination, relevance, consistency across repeated requests):** **not performed in this exercise.** A single hint and a small number of scored-turn feedback texts were generated and are stored as evidence (`testing_output/Testing_Evidence/MOD-QWEN-003*.json` etc.), but no systematic quality rubric, repeated-request consistency check, or hallucination audit was run. This is disclosed as a genuine scope limitation (Chapter 13), not claimed as covered.

### 8.3 PPO Policy and Guardrail Behavior

- **Functional testing:** PASS — §5.5, 10/10 and 13/13, fully reproduced with fresh evidence and zero mismatches against the project's own pre-existing expected results.
- **Implementation correctness — policy vs. guardrail distinction (explicitly separated, not conflated):** every one of this exercise's PPO test cases records a `source` field (`ppo` in all 10 inference cases) and every guardrail test case records whether the proposed action was `overridden` and by which named rule — this exercise never reports "the system adapted difficulty correctly" without stating whether that specific decision came from the learned policy or from a guardrail override. In the live session (`INT-003`), the specific decision source for the observed `difficulty_update` was not itself separately logged by the harness (a minor instrumentation gap noted for any future repeat of this exercise), but the underlying guardrail function's own boundary behavior was independently and exhaustively re-verified in isolation (`T-N03`).
- **Independent model-quality validation (does the trained policy add value over simpler baselines):** **out of scope for this module/integration/E2E exercise**, and this exercise makes no new claim on that question. That specific question has already been investigated separately and in depth by this project's own research evidence record and a prior, independent audit conducted earlier in this engagement, which found the learned policy's contribution over a guardrail-shielded constant action not statistically distinguishable from zero on the project's existing confirmatory test. This testing exercise's job was narrower and different: confirm the *code* runs correctly and the *documented* guardrail rules fire exactly where specified — which it does.

### 8.4 WhisperX / Speech Pipeline

See §5.4 and Defect Register DEF-002. **Functional testing of the fallback path:** PASS (the energy-based fallback itself does not crash and returns a well-formed, if transcript-free, response). **Functional testing of the primary STT engine:** FAIL in this environment (not installed). **Model-quality validation:** not applicable — no real transcript was produced to evaluate.

---

## Chapter 9: Performance and Reliability Testing

### 9.1 Environment and Methodology

All measurements below were taken against the real, live services on the machine described in §3.4. **Timing discipline:** an initial attempt at `PERF-001` was run concurrently with the full `pytest` regression suite (Chapter 11) executing in the background; that run showed inflated, contended latencies and is **not** reported as this test's result — `PERF-001` was deliberately re-run after the `pytest` suite finished, so the reported figures reflect the live services under their own load only, not confounded by a concurrent CPU-heavy background process. This is disclosed as a methodology decision, not hidden.

### 9.2 Results

| Test ID | What was measured | Method | n | Mean | Median | p95 | Min | Max | Errors |
|---|---|---|---|---|---|---|---|---|---|
| PERF-001 | Evaluator Flask API, full HTTP round trip (`POST /api/evaluator/evaluate-answer`) | Real HTTP calls to the live `:5000` service | 20 | 2.351s | 2.350s | 2.384s | 2.313s | 2.391s | 0 |
| PERF-001-ctx | Evaluator, in-process direct function call (no HTTP/network layer) — re-run of the project's existing `T-N09` script, for context only | Direct `evaluate()` calls, same process | 30 | 486.8ms | 483.5ms | 513.2ms | 472.4ms | 524.8ms | 0 |
| PERF-002 | Full WebSocket `voice_answer` turn (evaluator + guardrail/strategy + feedback dispatch), live session | Real WS round trip, 2 turns observed | 2 | 30.84s | — | — | 28.35s | 33.33s | 0 |
| PERF-003 | Qwen GGUF (CPU, llama.cpp) hint generation, direct call | Real HTTP calls to the live `:8001` service | 5 | 2.067s | 2.073s | — | 2.043s | 2.085s | 0 |

### 9.3 Interpretation

- **PERF-001 vs. PERF-001-ctx are not a regression** — they measure different things. `PERF-001` is the real, client-observed, full-HTTP-round-trip latency through Flask's single-threaded development server (no production WSGI server is configured for the evaluator microservice); `PERF-001-ctx` is the same scoring logic called in-process with no network/HTTP layer at all. The ~1.9-second gap between them is consistent with Flask dev-server request-handling overhead, not a change in the scoring algorithm's own cost. **These two figures should never be quoted interchangeably.**
- **PERF-002 (30.8s mean per full voice-answer turn) is high** and is reported as a genuine, if small-sample (n=2), finding, not minimized. It plausibly reflects the cumulative cost of evaluator scoring + guardrail/strategy decision + (where applicable) a live Qwen feedback-text generation call within the same turn, run sequentially inside one orchestrator call — but this exercise did not instrument the orchestrator's own internal step-by-step timing, so the exact breakdown of that 30.8s is **not established here** and should not be asserted beyond what was measured. This is flagged as a specific, concrete follow-up question for future performance work (Chapter 13), not resolved by assumption in this report.
- **PERF-003 (Qwen, ~2.07s)** is a clean, consistent, low-variance measurement (range 2.043–2.085s across 5 calls) for CPU-based GGUF inference on a short hint prompt — a reasonable, unremarkable figure for this hardware class.
- No benchmark in this chapter is compared against unavailable hardware or another environment's results without an explicit methodology caveat, consistent with this exercise's instructions.

### 9.4 Reliability Observations

- The evaluator and Qwen services, exercised with a combined 45+ HTTP/WS calls across this entire testing exercise, produced **zero connection failures, zero unhandled exceptions, and zero crashes** once their correct request contracts were used (see §10.4 for the two cases where this exercise's own early test payloads were wrong, not the service).
- The backend's WebSocket handler correctly survived a malformed-JSON frame (`NEG-002`) and a connection to a non-existent session (`NEG-001`) without crashing or leaving the server process in a bad state — confirmed by every subsequent test in this exercise continuing to succeed against the same running process.

---

## Chapter 10: Negative Testing and Failure Analysis

### 10.1 Invalid Input Tests

| Test ID | Input | Expected | Actual | Status |
|---|---|---|---|---|
| MOD-BE-003 | Login missing required `email` | 422 | 422 | PASS |
| NEG-003 | Empty session-create body | Graceful default-filling | 200, defaults applied correctly | PASS |
| MOD-EVAL-009 | Evaluate-answer missing `transcript` | 400 | 400 | PASS |
| MOD-EVAL-010 | Set-question unknown `qid` | 404 | 404 | PASS |
| MOD-EVAL-011 | Malformed JSON body to the evaluator | Graceful 4xx, no crash | 400, server kept serving | PASS |
| MOD-EVAL-001..007 | 7 adversarial/malformed answer texts (empty, whitespace, SQL-injection-like, HTML/script tag, emoji spam, garbled Unicode, 16.5K-char repeat) | No crash, score in [0,1] | All 7 handled, no crash | PASS |

### 10.2 Boundary Cases

| Test ID | Boundary | Expected | Actual | Status |
|---|---|---|---|---|
| MOD-PPO-011..023 | All 6 guardrail rules' exact threshold boundaries, incl. the previously-fixed G5 gap | Exact expected rule or `none` | 13/13 exact matches | PASS |
| MOD-TIMER-002 | Response time exactly at and past the allowed-time floor | Overrun correctly flagged | Correct | PASS |
| MOD-VALID-005 | NaN score | Replaced with 0.0 | Correct | PASS |

### 10.3 Dependency Failures (real, not simulated)

| Test ID | Dependency | Expected system behavior | Actual | Status |
|---|---|---|---|---|
| MOD-SBX-001/INT-004 | Docker daemon unreachable | Fail closed, no crash, no untrusted execution | Confirmed: orchestrator handled the submission without crashing; real sandboxed execution itself remains unverified | BLOCKED (environment), PASS (handling) |
| MOD-AUD-001..003 | WhisperX not installed | Either: fail closed with a clear error, or silently and gracefully degrade | **Silently degrades** to the energy-fallback path with a `200 OK` response and no transcript; `/health` does not surface this | FAIL (see DEF-002) |

### 10.4 This Exercise's Own Test-Script Errors — Found, Corrected, and Disclosed

Consistent with this project's established evidence discipline, this exercise's own methodology mistakes are reported here rather than silently corrected and hidden:

1. **`MOD-TIMER-003`/`MOD-TIMER-005` initial false FAIL:** the first version of the new `QuestionTimer` test checked for a result-dictionary key named `modifier`/`f_time`, which does not exist; the real key is `timing_modifier`. Corrected and re-run (§5.10); the application's actual behavior was correct throughout — this was purely a test-script defect, not an application defect.
2. **`MOD-TIMER-002` initial false FAIL:** the first version assumed `QuestionTimer.start(allowed_time_sec=0.2)` would honor a sub-1-second budget; the real implementation enforces a hard floor of `max(allowed_time_sec, 1.0)`. Corrected and re-run against the real floor; recorded as a genuine implementation observation (§5.10), not a defect.
3. **`PERF-001` initial false PASS (20/20 silent errors):** the first version of the evaluator performance test used an incorrect field name (`question_id` instead of the Flask evaluator's actual expected `qid`) and an incomplete `set-question` payload (missing the required `question_text`), causing every `evaluate-answer` call to fail with a 400 while the test harness's own pass/fail logic incorrectly reported PASS because it only checked "were any latencies recorded" rather than "did calls succeed." **Both bugs were in this exercise's own test script, not in the application** — confirmed by directly reproducing the project's own proven `T-N04` contract test's exact, working payload. Both the test logic and the payload were corrected, and the test was re-run cleanly (§9.2). This is disclosed in full rather than silently fixed and re-reported as if it had always passed.
4. **`MOD-AUD-001` status reclassification:** the automated test harness's own scoring logic labeled this result `PARTIAL` (because the HTTP endpoint returned 200 with a well-formed body). This report instead classifies it as **FAIL** throughout (Chapters 5, 7, 8), because the specific capability under test — producing a real transcript — was not achieved at all (zero characters), and the task's own definition of PARTIAL ("some, but not all, expected behaviour was verified") does not fit a complete absence of the one behavior being tested. The endpoint's separate, genuinely positive graceful-degradation behavior (no crash, well-formed error reporting) is credited explicitly but kept analytically distinct from the capability-level result.

---

## Chapter 11: Consolidated Test Results

### 11.1 Denominator Discipline (stated explicitly, per this exercise's own instructions)

This chapter separates **newly authored test cases** (designed and executed for the first time in this exercise — the module/integration/E2E/performance harness and the new `ScoreValidator`/`QuestionTimer` module script) from **pre-existing test scripts re-executed fresh** (already existed in `testing_and_evaluation/` or `tests/`; re-run in this exercise to obtain current, dated evidence rather than citing their original run). **Each individual test case is counted in exactly one of the two tables below — never both.** Chapter 5's narrative module sections (e.g. MOD-QS, MOD-PPO, MOD-EVAL's adversarial rows) *describe* results that are numerically counted once, in Table B, since they come from pre-existing scripts re-run fresh; Chapter 5 presents them per-module for readability, not as a second execution. Composite end-to-end scenarios (Chapter 7), built entirely from already-counted integration test cases, are summarized again at the scenario level in §11.6 for narrative clarity only and are not added into the numeric grand total a second time.

### 11.2 Table A — Newly Authored Test Cases (this exercise, zero overlap with Table B)

| Category | Test IDs | Executed | Passed | Failed | Blocked |
|---|---|---|---|---|---|
| Module — Backend/Admin | `MOD-BE-001..004`, `NEG-003`, `MOD-ADMIN-001..002` | 7 | 7 | 0 | 0 |
| Module — Evaluator/Qwen health | Evaluator health, `MOD-QWEN-001` | 2 | 2 | 0 | 0 |
| Module — Audio/STT | `MOD-AUD-001` | 1 | 0 | 1 | 0 |
| Module — Database | `MOD-DB-001` (before + after) | 2 | 2 | 0 | 0 |
| Module — Score Validator (new) | `MOD-VALID-001..007` | 7 | 7 | 0 | 0 |
| Module — Question Timer (new) | `MOD-TIMER-001..005` + `002a` | 6 | 6 | 0 | 0 |
| Integration | `INT-001..007`, `MOD-QWEN-002`, `NEG-001..002` | 11 | 9 | 1 | 1 |
| Performance | `PERF-001..003` | 3 | 3 | 0 | 0 |
| **Table A total** | | **39** | **36** | **2** | **1** |

### 11.3 Table B — Pre-Existing Automated Suites, Re-Executed Fresh

| Suite | Files/scope | Passed | Failed | Skipped | Total | Notes |
|---|---|---|---|---|---|---|
| Backend `pytest` | 25 files (21 unit + 4 integration), full suite | 264 | 19 | 15 | 298 | **Identical split to this project's previously documented baseline** — 18 of 19 failures Docker-dependent, 1 pre-existing known issue, zero new/unexplained failures |
| Frontend `Vitest` | 4 files | 28 | 0 | 0 | 28 | Identical to prior baseline |
| `T-N02` (RL checkpoint sanity, re-run) | 1 script | 10 | 0 | 0 | 10 | Identical to prior recorded result |
| `T-N03` (guardrail boundary verification, re-run) | 1 script | 13 | 0 | 0 | 13 | Identical to prior recorded result; confirms the G5 fix has not regressed |
| `T-N06` (evaluator adversarial inputs, re-run) | 1 script | 10 | 0 | 0 | 10 | Identical to prior recorded result |
| `T-N04` (evaluator API contract, re-run) | 1 script | 7 | 0 | 0 | 7 | Identical to prior recorded result |
| `T-N10` (question selector correctness, re-run) | 1 script | 11 | 0 | 0 | 11 | Identical to prior recorded result |
| **Table B total** | | **343** | **19** | **15** | **377** | |

### 11.4 Grand Total (this exercise)

| | Count |
|---|---|
| Total test cases executed or attempted | **416** (39 + 377, Table A + Table B, no overlap) |
| Passed | **379** |
| Failed | **21** (2 new findings + 19 pre-existing, every one individually attributed — §11.5) |
| Blocked | **1** (`INT-004`, sandboxed code execution — Docker daemon unreachable) |
| Skipped | **15** (pre-existing suite, pre-existing skip markers, not altered in this exercise) |
| **Pass rate — of all 416 attempted** | **379/416 = 91.1%** |
| **Pass rate — of the 400 decidable (excluding 1 blocked, 15 skipped)** | **379/400 = 94.75%** |

Both denominators are reported explicitly, per this exercise's own instruction not to silently choose a more favorable one.

### 11.5 Every Failure, Individually Attributed (no unexplained failures)

| Failure | Count | Root cause | New or pre-existing finding? |
|---|---|---|---|
| `test_coding_executor.py` (13 tests) | 13 | Docker daemon unreachable in this environment | Pre-existing, independently reconfirmed |
| `test_stage11_5_coding_adaptation.py` (3 Docker-dependent + 1 known) | 4 | 3 Docker-dependent; 1 pre-existing documented issue (`obs[4]` value mismatch), left unresolved by this project's own stated policy | Pre-existing, independently reconfirmed |
| `test_stage11_6_full_interview_e2e.py` (2 tests) | 2 | Docker daemon unreachable | Pre-existing, independently reconfirmed |
| `MOD-QWEN-002` | 1 | WebSocket `request_hint` message type not dispatched (DEF-001) | **New finding, this exercise** |
| `MOD-AUD-001` | 1 | WhisperX not installed in this environment (DEF-002) | **New finding, this exercise** |

**Zero unexplained or newly-discovered-but-unattributed failures remain.**

### 11.6 End-to-End Scenario Summary (qualitative, cross-referencing Table A/B — not separately counted)

| Scenario | Status |
|---|---|
| E2E-01 Complete interview lifecycle | PASS (1 embedded, separately-counted defect — `MOD-QWEN-002`) |
| E2E-02 Audio-based interview | BLOCKED (transcription step) |
| E2E-03 Text-based interview | PASS |
| E2E-04 Adaptive interview | PASS |
| E2E-05 Failure and recovery | PARTIAL (3 of 7 sub-scenarios executed, 4 disclosed as not executed) |
| E2E-06 Session/report consistency | PASS |
| E2E-07 Repeated sessions | NOT FULLY EXECUTED (1 of N sessions run) |

---

## Chapter 12: Defect and Observation Register

Per this exercise's mandatory source-preservation rule, **no application source file was modified to resolve either defect below.** Both remain open.

### DEF-001 — WebSocket `request_hint` message type is never dispatched

| Field | Detail |
|---|---|
| Defect ID | DEF-001 |
| Affected module | MOD-BE (WebSocket dispatcher), MOD-QWEN (unreachable downstream) |
| Description | The WebSocket interview handler's own docstring (`apps/backend/main.py`, lines ~1252-1272) documents `request_hint : { question_id }` as a valid client→server message type, and `InterviewOrchestrator.request_hint()` (`agents/orchestrator/interview_orchestrator.py:1043`) is a working method that correctly calls the Qwen hint service when invoked directly. However, the WebSocket handler's actual `if/elif mtype == ...` dispatch chain has **no branch matching `"request_hint"`** — confirmed by reading the complete handler and by a repo-wide `grep -n "request_hint"`, which shows exactly two matches: the docstring, and the orchestrator method definition — no dispatch call site exists anywhere. |
| Reproduction steps | 1. Start the real application stack. 2. Open a WebSocket connection to `/ws/interview/{session_id}` for an active session. 3. Send `{"type":"request_hint","payload":{"question_id":"<any active question id>"}}`. 4. Observe the response stream. |
| Expected behaviour | Per the handler's own docstring: a `{"type":"hint","payload":{"text":...}}` message. |
| Actual behaviour | No message of any type is sent in response to this specific message. The connection remains open and continues to function correctly for all other message types afterward (confirmed: `next_question`, `code_submission`, and `end_session` all succeeded later in the same session). |
| Severity | **Medium.** Not a crash, not data corruption, and does not block the rest of the interview flow — but a documented, user-facing feature (on-demand hints) is completely non-functional via the only client-facing interface that could reach it. |
| Evidence | `testing_output/Testing_Evidence/MOD-QWEN-002_hint.json`; source citations above |
| Resolution status | **Unresolved by design** — source code was not modified per this exercise's instructions. The underlying `InterviewOrchestrator.request_hint()` method itself was separately confirmed working when called directly in-process (not via this broken WS path), and the real Qwen hint service was separately confirmed working when called directly over HTTP (`MOD-QWEN-003`) — the defect is specifically and only in the WebSocket dispatch wiring. |

### DEF-002 — WhisperX not installed; `/health` does not detect this; STT silently degrades on every real request

| Field | Detail |
|---|---|
| Defect ID | DEF-002 |
| Affected module | MOD-AUD (speech pipeline), MOD-BE (health-check accuracy) |
| Description | `agents/audio/transcriber.py` checks a module-level `_WHISPERX_AVAILABLE` flag; in this environment, `import whisperx` raises `ModuleNotFoundError` (confirmed directly: `pip show whisperx` finds nothing, as does `pip show faster-whisper`, despite both being pinned in `requirements/audio.txt`). When this flag is false, `transcribe_and_align()` returns the energy-based fallback **immediately**, with no exception and no error-level log entry (confirmed: running with `logging.basicConfig(level=logging.DEBUG)` produced no exception trace, because no exception is ever raised on this code path — the fallback is the intended behaviour for "WhisperX not installed," not a caught error). Separately, `GET /health` reports `"audio": {"state": "ready", ...}` — this exercise could not find, in the time available, any code path in the health-check logic that verifies `_WHISPERX_AVAILABLE` is true before reporting "ready"; the audio subsystem appears to report "ready" based on successful *module import of the audio package itself* (which succeeds, since the package is written to tolerate WhisperX's absence), not on the *real STT engine* being usable. |
| Reproduction steps | 1. In this project's `.venv`: `python -c "import whisperx"` → `ModuleNotFoundError`. 2. Start the real backend; `GET /health` → `"audio":{"state":"ready",...}`. 3. `POST /api/transcribe` with any real audio file → `200 OK`, `"stt_status":"stt_unavailable"`, `"alignment_source":"wav_energy_fallback"`, empty transcript. |
| Expected behaviour | Either WhisperX is installed and produces real transcripts, or — if it is expected to be absent in some environments — `/health` should surface this (e.g. `"audio":{"state":"degraded"}` or a dedicated `stt_engine: "fallback_only"` field) so the gap is visible without making a real transcription request. |
| Actual behaviour | `/health` reports full readiness; the gap is only discoverable by actually attempting a transcription and reading `stt_status`/`alignment_source` in the response body. |
| Severity | **High at the capability level** (the system's advertised real STT capability is completely inactive in this environment) **but environment-scoped, not necessarily a universal defect** — this exercise cannot determine whether `whisperx`/`faster-whisper` are genuinely absent from every deployment of this project or specifically from this test environment's `.venv` (consistent with this project's own already-documented, broader `.venv` pin-reconciliation issue covering other packages). The **health-check masking** aspect (not distinguishing "audio package imported" from "real STT engine available") is a defect regardless of why the package is missing in any given environment. |
| Evidence | `testing_output/Testing_Evidence/MOD-AUD-001_transcribe.json`; direct in-process reproduction and `_WHISPERX_AVAILABLE` check (this chapter's reproduction steps); `pip show whisperx`/`pip show faster-whisper` output |
| Resolution status | **Unresolved by design** — source code was not modified. Recommended next step (not performed here): either install `whisperx`/`faster-whisper` in this `.venv` per `requirements/audio.txt` and re-test, or, if their absence here is intentional, add an explicit `_WHISPERX_AVAILABLE` check to the `/health` response so this gap is visible without a live transcription attempt. |

### Observations (not defects — recorded for completeness)

| ID | Observation | Why it is not classified as a defect |
|---|---|---|
| OBS-001 | `QuestionTimer.start()` silently floors any `allowed_time_sec < 1.0` up to `1.0` | This is explicit, intentional code (`max(float(allowed_time_sec or 60.0), 1.0)`), not an unexpected side effect; it only surfaced because this exercise's own first test draft assumed otherwise |
| OBS-002 | Empty and whitespace-only evaluator inputs both score exactly `0.0634` rather than `0.0` | Independently reconfirmed in this exercise; already noted in this project's own prior testing records as a minor, non-correctness-affecting curiosity, not re-investigated further here |
| OBS-003 | A full WebSocket `voice_answer` turn averaged ~30.8s (n=2) in this exercise — high, and not fully attributed | Reported as a finding requiring follow-up instrumentation, not asserted as a defect with a known cause (§9.3) |

---

## Chapter 13: Limitations and Unverified Areas

**Tests not conducted:**
- Qwen model-quality validation (hallucination rate, relevance scoring, repeated-request consistency) — out of scope for this module/integration/E2E exercise; flagged, not performed.
- Evaluator human-correlation re-validation — this exercise did not re-run the project's existing, separate human-rater study; that study's own result (ρ=0.3812, exploratory) is unchanged by this exercise and not re-derived here.
- A genuine, participant-based usability study of the frontend UI — no participants, no ethics approval; not claimed.
- Multi-session concurrency / cross-session data-isolation testing (E2E-07) — only one live session was driven end-to-end.
- Deliberate mid-session WS disconnect/reconnect and Qwen-service-down recovery scenarios — not executed, to avoid destabilizing the shared live services mid-exercise.
- Load/stress testing at concurrency beyond a single test client — judged not relevant to this single-process, non-production deployment; not performed.

**Tests blocked by the environment:**
- All Docker-sandboxed code-execution testing (18 pre-existing pytest tests + this exercise's own `INT-004`/`MOD-SBX-001`) — Docker daemon unreachable, independently reconfirmed at the start of this exercise.
- Genuine WhisperX-based STT evidence (DEF-002) — package not installed in this `.venv`.

**Components not independently validated at the model-quality level (functional correctness only):**
- The composite evaluator's score *accuracy* (as opposed to its code-level correctness, which is fully tested).
- Qwen's generated text *quality* (as opposed to its role-separation from scoring, which is fully verified).
- The PPO policy's *learned value* over simpler baselines (a separate research question, already investigated elsewhere in this project's evidence record, out of scope here).

**Missing evidence:**
- No per-step internal timing breakdown exists for the ~30.8s average WS turn latency (OBS-003) — this exercise measured the wall-clock total only.
- The exact reason the backend's `/health` endpoint does not surface WhisperX's absence was not traced to a specific missing line of code in the time available for this exercise — only that no such check appears to exist, based on the observed behaviour.

**Incomplete integration paths:**
- Frontend↔Backend was verified at the protocol/contract level (the real WebSocket messages the frontend is documented to send and receive, per `apps/backend/main.py`'s own docstring) and via the pre-existing Vitest component suite, but not via a real browser driving the real frontend dev server against the real backend in the same session — the frontend dev server was not started in this exercise (`--no-frontend`).

**Remaining reproducibility issues:**
- This exercise's own `.venv` is missing `whisperx`/`faster-whisper` entirely; any future repeat of this exercise in a differently-provisioned environment may not reproduce DEF-002, which should be understood as environment-dependent, not necessarily reflecting every deployment of this project.

---

## Chapter 14: Final Conclusion

### 14.1 What Has Been Successfully Tested

A genuine, live instance of PrepAIred — backend, evaluator, and Qwen services actually running, not mocked — was tested across module, integration, and end-to-end levels. 416 test cases were executed or attempted in this exercise (39 newly authored, 377 from re-running this project's existing automated suites fresh), with a 91.1% pass rate overall (94.75% of decidable, non-blocked, non-skipped cases).

### 14.2 What Works at Module Level

Every module tested except the real WhisperX STT engine (unavailable in this environment) functioned correctly at the module level, including two modules (`ScoreValidator`, `QuestionTimer`) that had no prior independent test coverage at all before this exercise and are now confirmed correct across 13 new positive/negative/boundary cases.

### 14.3 What Works Across Integrated Modules

8 of 9 tested integration boundaries passed cleanly, with real data (not mocked) confirmed flowing correctly between the real evaluator, the real guardrail/strategy layer, the real question selector, and the real database. The one integration failure (`MOD-QWEN-002`/DEF-001) is narrow, well-isolated, and does not propagate — every other part of the same live session continued to function correctly afterward.

### 14.4 Does the Complete End-to-End Workflow Work?

**Yes, for the verbal/text-answer path** (E2E-01, E2E-03, E2E-04, E2E-06 all PASS): a complete interview — login, session creation, multiple scored turns with observably correct difficulty-adaptive behaviour, session completion, and an accurate final report — was driven successfully against the real, live system in this exercise.

**Not fully verified for the audio-answer path** (E2E-02 BLOCKED) or the sandboxed-code-answer path (E2E-05 code-execution sub-scenario, environment-blocked) — both for disclosed, specific, environment-level reasons, not application defects discovered in the core logic itself.

### 14.5 Main Defects and Limitations

Two genuine defects (DEF-001, DEF-002) were found, neither fixed (per this exercise's mandate), both fully reproduced, root-caused, and evidenced. Three observations were recorded that are explicitly not defects. The project's own, previously-documented Docker-dependent test gap and one pre-existing known test failure were independently reconfirmed, not newly discovered.

### 14.6 Overall Testing Confidence

**High confidence that the core, real-time interview loop (text/verbal answers, scoring, adaptive difficulty, feedback delivery, persistence, and reporting) works correctly end-to-end against the live system**, based on genuine execution evidence rather than code inspection alone. **Moderate confidence, with two specific, well-understood gaps**, in the completeness of the feature surface: the documented hint-on-demand feature is currently unreachable via the live API, and real speech transcription is currently inactive in this specific environment. **Confidence in the sandboxed code-execution path remains exactly where this project's own prior testing history already placed it** — correctly configured by code inspection, unverified at the execution level pending a running Docker daemon.

### 14.7 Recommended Next Steps

1. Wire the `"request_hint"` message type into the WebSocket dispatcher's `elif` chain (DEF-001) — a narrow, well-isolated fix, once source-code changes are authorized.
2. Install `whisperx`/`faster-whisper` in this environment (or confirm their intended absence) and add an explicit STT-engine-availability check to `/health` so this gap is visible without a live transcription attempt (DEF-002).
3. Instrument the orchestrator's `voice_answer` handling path with step-level timing to explain the ~30.8s average full-turn latency observed in this exercise (OBS-003).
4. Start a Docker daemon in a future test session and re-run the 18 currently-blocked sandbox tests plus this exercise's own `INT-004` for execution-level (not just configuration-level) sandbox confirmation.
5. Extend this exercise's E2E coverage to multi-session concurrency (E2E-07) and deliberate failure-injection scenarios (Qwen-down, forced timeout, mid-session disconnect) in a future pass.

---

## Appendix A: Environment Verification Commands and Raw Output

- `docker version` / `docker ps` — daemon unreachable, exact error text captured in this exercise's session log.
- `pip show whisperx`, `pip show faster-whisper` — both "Package(s) not found."
- Service health checks (`curl http://localhost:8000/health`, `:5000/health`, `:8001/health`) — all 200, full JSON bodies stored in `testing_output/Testing_Evidence/`.

## Appendix B: Full Test-Case Tables

See `Testing_Results_Master.csv`, `Module_Test_Coverage.csv`, `Integration_Test_Coverage.csv`, and `E2E_Test_Results.csv` for the complete, machine-readable record underlying every table in this report.

## Appendix C: Test Data Descriptions

- Candidate: `QA Harness Candidate`, synthetic email `qa_harness_<uuid>@example.com` — created fresh for this exercise, does not reuse or alter any pre-existing candidate record.
- Audio fixture: `tests/test_candidate_hash_table_answer.wav`, a real, pre-existing recorded answer already present in the repository before this exercise — not synthesized.
- Session configuration: `demo_rl` mode, 4 questions, 1 baseline question, topic `pointers`.

## Appendix D: Supporting Diagrams

See Chapter 2 (system architecture, as text diagram) and Chapter 6 (integration architecture, as text diagram). No additional rendered figures were produced beyond those already embedded above, consistent with keeping this report's diagrams limited to ones that reflect the actual, verified implementation.
