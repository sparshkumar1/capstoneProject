"""E2 — cost of the LLM handoff path with a healthy / refusing / hanging service (protocol v1 section 6). SOCKET class.
A local server binds localhost:8001 (the address hard-coded in the orchestrator and the feedback agent)."""
import asyncio, json, statistics, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import harness as H
import httpx
from services.qwen.app import (FeedbackRequest, FollowupRequest, _synthesize_structured_feedback,
                               _synthesize_structured_followup)

import os
OUT = Path(os.environ.get("ADCOM_RESULTS") or Path(__file__).parents[1] / "results")
MODE = {"m": "ok"}
HITS = {"n": 0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_POST(self):
        HITS["n"] += 1
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if MODE["m"] == "hang":
            time.sleep(40)
            return
        if self.path.endswith("followup"):
            r = _synthesize_structured_followup(FollowupRequest(**body)).model_dump()
        else:
            r = _synthesize_structured_feedback(FeedbackRequest(**body)).model_dump()
        out = json.dumps(r).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)


def start_server():
    srv = ThreadingHTTPServer(("127.0.0.1", 8001), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


async def run_mode(mode, k=0):
    MODE["m"] = mode
    by_q, qs = H.load_cases(), H.load_questions()
    questions, answers, cases = H.session_plan(k, by_q, qs)
    ev = H.ReplayEvaluator(cases)
    o = H.new_orchestrator(k, questions, ev)
    attempts = {"n": 0}
    orig = httpx.AsyncClient.post

    async def counted(self, *a, **kw):
        attempts["n"] += 1
        return await orig(self, *a, **kw)
    t_turn, t_next, http_per_turn = [], [], []
    from unittest.mock import patch
    with H.fixed_timer(), patch("httpx.AsyncClient.post", counted):
        res = await o.start(); root = {}
        for _ in range(40):
            if isinstance(res, dict) and res.get("type") == "session_end":
                break
            q = H._payload(res); qid = q["id"]
            if q.get("parent_question_id"):
                root[qid] = root.get(q["parent_question_id"], q["parent_question_id"])
            text = answers.get(qid) or answers.get(root.get(qid))
            a0 = attempts["n"]; t0 = time.perf_counter()
            r = await o.handle_voice_answer(text, qid)
            t_turn.append(time.perf_counter() - t0); http_per_turn.append(attempts["n"] - a0)
            t0 = time.perf_counter()
            res = await o.handle_next_question()
            t_next.append(time.perf_counter() - t0)
    llm_status = {}
    for a in o._state["answers"]:
        s = (a.get("feedback") or {}).get("llm_status"); llm_status[s] = llm_status.get(s, 0) + 1
    return {"mode": mode, "turns": len(t_turn), "followup_turns": sum(1 for a in o._state['answers'] if str(a['question_id']).startswith('fu_')),
            "turn_s_median": statistics.median(t_turn), "turn_s_max": max(t_turn), "turn_s_total": sum(t_turn),
            "next_s_median": statistics.median(t_next), "http_attempts_per_turn_median": statistics.median(http_per_turn),
            "http_attempts_total": attempts["n"], "server_hits": HITS["n"], "llm_status_counts": llm_status,
            "turn_s_all": t_turn}


async def main():
    out = OUT / "e2_handoff_cost.json"
    if out.exists():
        sys.exit("write-once")
    results = {}
    results["refuse"] = await run_mode("refuse")           # nothing listening yet
    srv = start_server()
    HITS["n"] = 0
    results["ok"] = await run_mode("ok")
    HITS["n"] = 0
    if not os.environ.get("ADCOM_SMOKE"):
        results["hang"] = await run_mode("hang")
    out.write_text(json.dumps(results, indent=1, sort_keys=True))
    for m, r in results.items():
        print(m, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != "turn_s_all"})

if __name__ == "__main__":
    asyncio.run(main())
