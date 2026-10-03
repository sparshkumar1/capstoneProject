"""TEST LAUNCHER (audit only; not part of the product). Starts the real FastAPI backend (real REST, WebSocket, orchestrator, PPO, SQLite persistence)
with the evaluator replaced by the recorded production-evaluator payloads (REPLAY) and a fixed 8-question session.
MA=1 injects multiagent_enabled=True into every created orchestrator (the shipped backend does not expose the flag)."""
import os, sys
sys.path.insert(0, "paper/adcom2027/experiments")
import harness as H
import apps.backend.main as main
import uvicorn
qs, answers, cases = H.session_plan(0)
ev = H.ReplayEvaluator(cases)
main._run_integrated_evaluator = ev
main.select_questions = lambda *a, **k: [dict(q) for q in qs]
if os.environ.get("MA") == "1":
    _orig = main.InterviewOrchestrator
    def _wrap(*a, **k):
        cfg = dict(k.get("config") or {}); cfg["multiagent_enabled"] = True; k["config"] = cfg
        return _orig(*a, **k)
    main.InterviewOrchestrator = _wrap
uvicorn.run(main.app, host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), log_level="info")
