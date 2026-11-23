# End-to-end audit tools (test harness, not product code)

Purpose: drive the **real** FastAPI backend (REST + WebSocket + `InterviewOrchestrator` + frozen PPO + SQLite snapshots) and the web client, with the multi-agent flag off and on.
The evaluator is **replaced by recorded production-evaluator payloads (REPLAY)** because the real scorer cannot load its weights offline; this verifies the integration, not scoring.
The shipped backend does not expose `multiagent_enabled`; `run_backend_replay.py` (MA=1) injects it, `run_backend_fault.py` also swaps in faulty agents by `candidate_id` (`e2e_fault_<kind>`).
Run from the repository root **in a scratch clone** (the backend writes `data/prepaired.db`, a tracked file):
```
export EVALUATOR_MOCK_MODE=1
PORT=8000 python research/multiagent/e2e/run_backend_replay.py &          # flag off
MA=1 PORT=8001 python research/multiagent/e2e/run_backend_replay.py &     # flag on
PORT=8002 python research/multiagent/e2e/run_backend_fault.py &           # faulty agents
E2E_OUT=out python research/multiagent/e2e/e2e_client.py 8000 off         # one full session; also: 8001 on, 8002 fault_crash|slow|forbidden|terminate|stale|malformed|nan|lowconf|noevidence|adversarial|coach_crash|coach_ungrounded
python research/multiagent/e2e/e2e_restore.py 8001 1                      # phase 1; kill and restart the backend; then: ... 2 <session id>
# UI (vite dev server on :3000 proxying to :8000): python research/multiagent/e2e/ui_smoke.py off <outdir>
```
Needs: fastapi, uvicorn, websockets, httpx (and playwright + Chromium for the UI script). Nothing here is evidence about candidate learning, scoring or LLM behaviour.
