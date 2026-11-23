"""E5 — circuit breaker before/after (protocol amendment A3). SOCKET class. Real sockets and real 6 s timeouts."""
import asyncio, json, os, statistics, sys, time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent))
import harness as H
import e2_handoff_cost as E2
import httpx
from agents.orchestrator.circuit_breaker import QWEN_BREAKER

OUT = Path(os.environ.get("ADCOM_RESULTS") or Path(__file__).parents[1] / "results")


async def scenario(name, mode, enabled, pacing=None, recover_after=None, k=0):
    E2.MODE["m"] = mode
    fake = {"t": 0.0}
    QWEN_BREAKER.reset(); QWEN_BREAKER.enabled = enabled; QWEN_BREAKER.clock = (lambda: fake["t"]) if pacing else __import__("time").monotonic
    by_q, qs = H.load_cases(), H.load_questions()
    questions, answers, cases = H.session_plan(k, by_q, qs)
    ev = H.ReplayEvaluator(cases)
    o = H.new_orchestrator(k, questions, ev)
    attempts = {"n": 0}; orig = httpx.AsyncClient.post

    async def counted(self, *a, **kw):
        attempts["n"] += 1
        return await orig(self, *a, **kw)
    t_turn, http_turn, states, llm_flags = [], [], [], []
    with H.fixed_timer(), patch("httpx.AsyncClient.post", counted):
        res = await o.start(); root = {}; turn = 0
        for _ in range(40):
            if isinstance(res, dict) and res.get("type") == "session_end":
                break
            q = H._payload(res); qid = q["id"]
            if q.get("parent_question_id"):
                root[qid] = root.get(q["parent_question_id"], q["parent_question_id"])
            if recover_after is not None and turn == recover_after:
                E2.MODE["m"] = "ok"
            a0 = attempts["n"]; t0 = time.perf_counter()
            r = await o.handle_voice_answer(answers.get(qid) or answers.get(root.get(qid)), qid)
            t_turn.append(time.perf_counter() - t0); http_turn.append(attempts["n"] - a0)
            states.append(QWEN_BREAKER.state)
            llm_flags.append(attempts["n"] - a0 > 0)
            if pacing: fake["t"] += pacing
            turn += 1
            res = await o.handle_next_question()
    QWEN_BREAKER.reset(); QWEN_BREAKER.enabled = True; QWEN_BREAKER.clock = __import__("time").monotonic
    return {"name": name, "mode": mode, "breaker_enabled": enabled, "pacing_s": pacing, "turns": len(t_turn),
            "turn_s_median": statistics.median(t_turn), "turn_s_max": max(t_turn), "turn_s_total": sum(t_turn),
            "http_attempts_total": attempts["n"], "http_per_turn": http_turn, "breaker_state_after_turn": states,
            "committed_scores": list(o._state["scores"]), "turn_s": t_turn}


async def main():
    out = OUT / "e5_circuit_breaker.json"
    if out.exists():
        sys.exit("write-once")
    srv = {"s": E2.start_server()}

    def server(up):
        if up and srv["s"] is None:
            srv["s"] = E2.start_server()
        if not up and srv["s"] is not None:
            srv["s"].shutdown(); srv["s"].server_close(); srv["s"] = None
    smoke = bool(os.environ.get("ADCOM_SMOKE"))
    plan = [("ok_S_P60", "ok", True, 60, None), ("refuse_S_P60", "refuse", True, 60, None)]
    if not smoke:
        plan = [("hang_B", "hang", False, None, None), ("hang_S_P30", "hang", True, 30, None),
                ("hang_S_P60", "hang", True, 60, None), ("hang_S_P120", "hang", True, 120, None)] + plan + \
               [("recover_S_P60", "hang", True, 60, 8)]
    res = {}
    for name, mode, en, p, rec in plan:
        server(mode != "refuse")
        res[name] = await scenario(name, mode, en, p, rec)
        r = res[name]; print(name, round(r["turn_s_median"], 2), round(r["turn_s_total"], 1), r["http_attempts_total"], flush=True)
    out.write_text(json.dumps(res, indent=1, sort_keys=True))

if __name__ == "__main__":
    asyncio.run(main())
