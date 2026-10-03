# Application end-to-end audit (2026-10-02)

Scope: does the application still work? All checks were run by me in this audit, in a **scratch clone of HEAD** (`5b3ba25`) so the tracked `data/prepaired.db` in the repository was not touched. Python 3.11 scratch venv outside the repository's dependency pins (numpy/torch/sentence-transformers newer than the pins); `uvicorn`, `websockets`, `faiss-cpu`, `playwright` were added to that venv for the audit. Node 22.
Classification: **Verified working / Partially verified / Not tested / Failed**.

## Summary
| Area | Result |
|---|---|
| Backend Python suite (`tests/unit` + `tests/integration`) | **Failed (environment)**: 23 failed, 36 errors, 409 passed, 15 skipped. Failing set = the same 59 test IDs as a clean export of the frozen baseline. No regression. |
| New multi-agent tests (6 files) | **Verified working**: 80 passed, 1 skipped |
| Frontend tests (`npx vitest run`) | **Verified working**: 4 files, 28/28 |
| Frontend production build (`npm ci && npm run build`) | **Verified working** (58 modules, 1.7 s) |
| Real backend startup, `/health`, REST session creation, WebSocket workflow | **Verified working** (real uvicorn server, flag off and on) |
| Real production evaluator | **Not verifiable here**: weights are an LFS pointer, HF downloads blocked (HTTP 403). The backend fails closed (see E2E-1). |
| Full interview session via real server with recorded evaluator payloads (REPLAY) | **Verified working**, flag off and flag on |
| Real server reproduces XA trajectories | **Verified**: difficulty-history prefix equals the XA record for k=0, seed 0 (B0 18 entries, M1 17 entries) |
| Fault injection through the real server (12 faults) | **Verified working** |
| Crash/restart recovery (kill -9, restart, resume) | **Verified working** (flag on) |
| Browser: login → topic setup → interview room with first question | **Partially verified** (flag off only) |
| Voice answer, speech-to-text, microphone, code sandbox, live LLM | **Not tested** (no STT weights, no Docker daemon, no LLM weights) |
| Multi-agent mode through the shipped UI/backend | **Not possible**: the shipped backend never sets `multiagent_enabled`; the web client has no agent display (finding, documented in the paper) |

## Commands and results
Tests (identical commands for the frozen export from `git archive 54a5b73` and for HEAD):
```
EVALUATOR_MOCK_MODE=1 python -m pytest tests/unit tests/integration -q -p no:cacheprovider -rfEs
frozen: 306 passed, 14 skipped, 23 failed, 36 errors      HEAD: 409 passed, 15 skipped, 23 failed, 36 errors
comm of sorted failing/erroring IDs: 59 vs 59, 0 only at HEAD, 0 only in frozen   (also after installing faiss-cpu)
python -m pytest tests/unit/test_ma_contracts_arbitration.py tests/unit/test_ma_agents.py tests/unit/test_guardrail_impl.py \
   tests/unit/test_evaluator_semantics_and_seam.py tests/unit/test_circuit_breaker_semantics.py tests/integration/test_ma_workflow.py
80 passed, 1 skipped (golden-score test needs materialised cross-encoder weights)
cd apps/web && npm ci && npm run build && npx vitest run      # build ok; 28 passed
```
**Classification of the 59 failing/erroring tests** (each first error read):
| Tests | Count | Cause | Class |
|---|---|---|---|
| `test_evaluator.py`, `..._logical_reasoning_adversarial.py`, `..._v4_adversarial_development_suite.py`, `test_evaluator_feedback_integration.py` | 36 errors | model download via proxy returns HTTP 403 (also `faiss` missing until installed) | environment-related, pre-existing |
| `test_stage11_3_followup_and_evaluation.py` | 3 failed | same model download | environment-related, pre-existing |
| `test_coding_executor.py` | 13 failed | `sandbox_error` (no Docker daemon) | environment-related, pre-existing |
| `test_stage11_5_coding_adaptation.py`, `test_stage11_6_full_interview_e2e.py` | 3 + 3 failed | `sandbox_error`; one test in 11_5 is the repository's documented known failure | environment-related + known |
| `test_live_websocket_session_recovery.py` | 1 failed | no scored turn because the real evaluator is unavailable | environment-related |
None was flaky in two runs. The behaviour these 59 tests cover (real evaluator scoring, Docker coding sandbox) is **not verified** here.

## Real-server scenarios (`research/multiagent/e2e/`, summary in `research/multiagent/results/e2e_audit/summary.json`)
Backend started with `python run_backend_replay.py` (real FastAPI app, REST, WebSocket, `InterviewOrchestrator`, frozen PPO, SQLite snapshots). The evaluator is replaced by recorded payloads (REPLAY) and the question list fixed to the 8 recorded questions; MA=1 injects the flag, which the shipped backend does not expose.
| ID | Scenario | Observed |
|---|---|---|
| E2E-1 | Real production evaluator, offline | every answer returned `evaluator_unavailable`, `final_score: null`, "No score fabricated", same question re-served: **fail-closed verified** |
| E2E-2 | Full session, flag off (REST create, WS start, voice_answer / next_question loop, end, REST report) | completed; 14 feedback events (first run), 0 with `coaching_plan`, no `multiagent` in the report |
| E2E-3 | Same, flag on | completed; 14/14 feedback payloads carry a `coaching_plan`; report contains the multiagent summary (28 agent calls, 78 decision records) |
| E2E-4 | Full-length sessions (cap 40 turns) off/on | server difficulty-history prefix equals the XA record for k=0, seed 0 (B0 18 entries; M1 17 entries); score differences appear only through the answer-time component (XA fixes time ratio 0.6) |
| E2E-5 | 12 injected faults, flag on (crash, slow, forbidden key, forbidden `terminate`, stale, malformed, NaN, low confidence, no evidence, adversarial valid, coaching crash, ungrounded coaching) | all 12 sessions completed; committed scores identical to the flag-off session; crash/timeout/forbidden/stale/malformed/NaN rejected with distinct reason codes and the per-agent breaker then opened (2 failures, 12 `breaker_open`); `terminate` rejected as `authority_violation` and the session did not terminate; low-confidence/no-evidence proposals rejected; for the nine Strategy faults whose proposals were all rejected the difficulty path equals the flag-off path (in the two coaching-fault sessions the real Strategy Agent stays active, so the path differs from flag-off as in a normal flag-on session); the **adversarial well-formed proposal was accepted** (8 validated, 3 bound-clamped) and changed the path, as the paper states |
| E2E-6 | Restart: 4 turns, `kill -9`, restart, reconnect to the same session id | session resumed from the snapshot, scores continuous, agent ledgers restored; call counters/decision records restart (12 calls vs 16 turns) |
| E2E-7 | Persistence | `session_snapshots` rows written each turn (5 for 5 sessions at that point). **The `sessions` table stays empty for guest candidates**: `save_session` raises `IntegrityError: FOREIGN KEY constraint failed` and `create_session` swallows it. Pre-existing (backend and storage unchanged since the freeze). Not fixed (outside scope; recorded as a risk). |
| E2E-8 | Browser (Playwright/Chromium, Vite dev server, backend flag off) | login page renders; form → topic selection (18 topics, settings) → "Begin Interview" → interview room shows "Connected", Level 2, the first question text, mic controls; 0 page errors; console errors only for blocked external resources (fonts/CDN) and a React dev double-mount WebSocket warning |
| E2E-9 | `FeedbackCard` rendered with all 14 real flag-on and 14 flag-off payloads (throw-away vitest in the clone) | renders without exception; flag-on payloads are accepted; the UI shows the modified improvement tips but has no dedicated agent display |

## Multi-agent safety re-checked
Authority matrix (18 forbidden keys) and arbitration order read against the code and exercised through E2E-5 and the integration tests; hub is the only writer: in every fault session committed scores were unchanged and protected state (score, termination) could not be altered by an agent. Gaps: (a) the guarantee is for the implemented key list and the schema, not for arbitrary semantics (an adversarial valid proposal is accepted); (b) a worker thread of a timed-out agent cannot be killed; (c) `apply_coaching_plan` mutates the feedback dict in place before the protected-field check (cannot trigger with the current code because protected keys are never written).

## Unresolved application risks
1. Real evaluator, STT, Docker sandbox and LLM paths: not testable here.
2. Multi-agent mode is not reachable from the shipped backend or UI (requires a constructor config).
3. Guest-candidate `sessions` rows are never written (silent FK failure).
4. The 59 environment-related test failures hide the status of evaluator and coding-sandbox behaviour in this environment.

## Addendum (2026-10-02): shipped-path reachability fix and re-verification

**Finding confirmed.** Both `InterviewOrchestrator(...)` call sites in `apps/backend/main.py` (session create, session restore) built a `config` dict that never contained `multiagent_enabled`; the request model has no such field and the UI has no control. Before this change the multi-agent layer was reachable only from tests and experiments (and from the e2e launcher, which injected the flag).

**Fix (commit 3dbb4ed).** `_multiagent_server_config()` reads the server environment variable `PREPAIRED_MULTIAGENT` (1/true/yes/on). Default OFF. It is not read from requests, exposes no other agent setting, and is applied to both create and restore. No change to the hub, PPO, arbitration, guardrails or the frontend. The XA/XB/XC/XE experiments do not use this path, so their semantics are unaffected.

**Tests.** `tests/integration/test_ma_backend_flag.py`: 11 passed (flag parsing, default single-agent, env enables `_ma` for new sessions, a request body carrying `multiagent_enabled` is ignored).

**Real-server run, shipped path (no wrapper injection; flag set only via `PREPAIRED_MULTIAGENT=1`; REPLAY evaluator substitute, scratch copy).** Flag off: 40 feedback events, 0 with `coaching_plan`, report without multiagent. Flag on: 40 feedback events, 40/40 with `coaching_plan`, report carries multiagent. Scores are identical in both modes (the evaluator is replayed, so this checks integration, not scoring). Not re-run after this change: fault injection, kill/restart recovery, browser UI (earlier results stand for the pre-change code; the change does not touch those paths).
Restored sessions follow the server's current flag (it is not persisted in snapshots).

### Addendum 2 (2026-10-02): completed runs, fresh regression, commands
**Shipped-path sessions (both finished with exit 0 before the scratch backends were stopped; logs and JSON saved in `research/multiagent/results/e2e_audit/shipped_path/`, summary in `summary.json`).** Scratch copy of HEAD (its `apps/backend/main.py` identical to the committed file). Commands (scratch copy, `EVALUATOR_MOCK_MODE=1 PYTHONPATH=.`):
`PORT=8100 python research/multiagent/e2e/run_backend_replay.py`; `PREPAIRED_MULTIAGENT=1 PORT=8101 python research/multiagent/e2e/run_backend_replay.py` (no `MA=1`, so no wrapper injection); `E2E_OUT=out python research/multiagent/e2e/e2e_client.py 8100 off` and `... 8101 on`.
| | flag off (8100) | flag on (8101) |
|---|---|---|
| events | created 1, question 41, feedback 40, difficulty_update 40, session_end 1 | identical counts |
| feedback with `coaching_plan` | 0/40 | 40/40 |
| null scores | 0 | 0 |
| follow-up questions | 27 of 41 | 27 of 41 |
| session ended / overall | yes / 0.427 | yes / 0.427 |
| server log | 0 tracebacks, 0 HTTP 4xx/5xx | same |
| multi-agent report | absent | agent calls strategy 40 / coaching 40; 222 decision records (e.g. 20 validated Strategy difficulty proposals accepted, 18 PPO actions superseded, 11 low-confidence Strategy proposals rejected, 11+4 guardrail G1/G3 overrides) |
Evaluator: the launcher replaces the evaluator with the recorded production-evaluator payloads (REPLAY); `decision_source: evaluator_cross_encoder` is the label carried inside those recorded payloads, not evidence that the cross-encoder ran. This is integration evidence only; no real-model scoring, microphone, STT or Docker sandbox was exercised.
**Fault injection re-run on the current code (shipped-path scratch copy, 12 kinds, faulty agents selected by candidate id):** all 12 sessions exit 0, each with 40 feedback events, session_end and overall score 0.427 (committed scores unchanged); 0 tracebacks in the server log; outputs in `shipped_path/fault/`. Classification per kind is as in the earlier table above (not re-derived row by row here).
**Fresh Python regression (2026-10-02), `EVALUATOR_MOCK_MODE=1 pytest tests/unit tests/integration -q -p no:cacheprovider -rfEs`:** frozen-commit export 306 passed / 14 skipped / 23 failed / 36 errors; HEAD 421 passed / 15 skipped / 23 failed / 36 errors. The 59 failing/erroring test IDs are identical in both runs (`comm` of sorted IDs is empty both ways): environmental (blocked model downloads, no Docker daemon, no evaluator weights, one documented known failure). Raw output in `shipped_path/pytest_*_2026-10-02.txt`. Not green; these 59 are not shown harmless beyond that identity and their error messages.
**Frontend:** `npx vitest run` 28/28 passed (4 files); `vite build` succeeded (output directed to scratch). **Not run:** browser UI with the flag on, microphone/STT, Docker coding sandbox, real evaluator.
