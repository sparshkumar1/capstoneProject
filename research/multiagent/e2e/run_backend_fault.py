"""TEST LAUNCHER (audit only). Real backend + replay evaluator + multi-agent ON; the agent is replaced by a faulty one chosen by candidate_id 'e2e_fault_<kind>'."""
import os, sys, time
sys.path.insert(0, "paper/adcom2027/experiments"); sys.path.insert(0, ".")
import harness as H
import apps.backend.main as main
import uvicorn
from agents.multiagent.contracts import Evidence, StrategyProposal, CoachingPlan
from agents.multiagent.strategy_agent import StrategyAgent
qs, answers, cases = H.session_plan(0)
main._run_integrated_evaluator = H.ReplayEvaluator(cases)
main.select_questions = lambda *a, **k: [dict(q) for q in qs]
class S:
    def __init__(s, kind): s.kind = kind
    def propose(s, obs, peer=None):
        k = s.kind
        if k == "crash": raise RuntimeError("injected crash")
        if k == "slow": time.sleep(1.0); return StrategyAgent().propose(obs)
        if k == "forbidden": return {"difficulty_action": "Harder", "confidence": 0.99, "final_score": 1.0}
        if k == "terminate": return {"difficulty_action": "Harder", "confidence": 0.99, "terminate": True}
        if k == "stale": return StrategyProposal(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version + 5, difficulty_action="Harder", confidence=0.99, evidence=(Evidence(ref="score"),))
        if k == "malformed": return {"difficulty_action": "Sideways"}
        if k == "nan": return {"session_id": obs.session_id, "turn_id": obs.turn_id, "state_version": obs.state_version, "difficulty_action": "Harder", "confidence": float("nan")}
        if k == "lowconf": return StrategyProposal(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, difficulty_action="Harder", confidence=0.3, evidence=(Evidence(ref="score"),))
        if k == "noevidence": return StrategyProposal(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, difficulty_action="Harder", confidence=0.9, evidence=())
        if k == "adversarial": return StrategyProposal(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, difficulty_action="Harder" if obs.score < 0.5 else "Easier", confidence=0.95, mode="stretch", evidence=(Evidence(ref="score"),))
        raise ValueError(k)
class C:
    def __init__(s, kind): s.kind = kind
    def propose(s, obs, peer=None):
        if s.kind == "crash": raise RuntimeError("coach crash")
        return CoachingPlan(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, emphasize=("quantum entanglement",), confidence=0.9, evidence=(Evidence(ref="score"),))
_orig = main.InterviewOrchestrator
def _wrap(*a, **k):
    cfg = dict(k.get("config") or {}); cfg["multiagent_enabled"] = True
    cid = str((k.get("candidate") or {}).get("id", ""))
    ma = {"timeout_s": 0.3}
    if "fault_" in cid:
        kind = cid.split("fault_", 1)[1]
        if kind.startswith("coach_"): ma["agents"] = {"coaching": C(kind[6:])}
        else: ma["agents"] = {"strategy": S(kind)}
    cfg["multiagent"] = ma; k["config"] = cfg
    return _orig(*a, **k)
main.InterviewOrchestrator = _wrap
uvicorn.run(main.app, host="127.0.0.1", port=int(os.environ.get("PORT", "8002")), log_level="warning")
