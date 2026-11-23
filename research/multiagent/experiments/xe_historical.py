"""XE: historical-experiment reproduction under EXPLICIT configuration, and the effect of the breaker's 5xx fix (protocol MA-XA-XB v1).

Parts
  e1    re-run the historical E1 (REPLAY) with strict_evaluator_contract=False and the breaker disabled (the configuration at the time
        E1 was run), into a new directory; compare byte-for-byte with the stored e1_runs.jsonl. Stored results are never touched.
  e5    re-run the historical E5 scenarios (SOCKET: real sockets, real 6 s timeouts) with current code and defaults; reported as a NEW run.
  b503  new SOCKET scenario: a service that answers every request with HTTP 503. Breaker semantics 'legacy' (any response = success,
        the semantics of the historical runs) vs 'fixed' (5xx = failure). Same replay session, same code otherwise.
"""
import argparse
import asyncio
import hashlib
import json
import os
import statistics
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ma_common as C  # noqa: E402

H = C.H
STORED = C.REPO / "paper/adcom2027/results"


async def part_e1(out: Path):
    gs = C.git_state()
    os.environ["ADCOM_RESULTS"] = str(out)
    out.mkdir(parents=True, exist_ok=True)
    import e1_ablation_faults as E1
    from agents.orchestrator.circuit_breaker import QWEN_BREAKER
    QWEN_BREAKER.enabled = False
    orig = H.new_orchestrator

    def historical(k, questions, evaluator, strategy="default", cfg=None):
        c = dict(cfg or {})
        c.setdefault("strict_evaluator_contract", False)
        return orig(k, questions, evaluator, strategy, c)
    H.new_orchestrator = historical
    E1.OUT = out
    t0 = time.time()
    await E1.main()
    new = hashlib.sha256((out / "e1_runs.jsonl").read_bytes()).hexdigest()
    old = hashlib.sha256((STORED / "e1_runs.jsonl").read_bytes()).hexdigest()
    rows_new = [json.loads(l) for l in open(out / "e1_runs.jsonl")]
    rows_old = [json.loads(l) for l in open(STORED / "e1_runs.jsonl")]
    diff = sum(1 for a, b in zip(rows_new, rows_old) if a != b)
    rec = {"part": "e1", "config": {"strict_evaluator_contract": False, "qwen_breaker": "disabled"}, "git": gs,
           "new_sha256": new, "stored_sha256": old, "byte_identical": new == old, "rows": len(rows_new),
           "rows_differing": diff, "seconds": round(time.time() - t0, 1)}
    (out / "xe_e1_reproduction.json").write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(json.dumps(rec))


MODE = {"m": "ok"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if MODE["m"] == "503":
            self.send_response(503); self.send_header("Content-Length", "0"); self.end_headers(); return
        from services.qwen.app import (FeedbackRequest, FollowupRequest, _synthesize_structured_feedback,
                                       _synthesize_structured_followup)
        r = (_synthesize_structured_followup(FollowupRequest(**body)) if self.path.endswith("followup")
             else _synthesize_structured_feedback(FeedbackRequest(**body))).model_dump()
        out = json.dumps(r).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)


async def b503_scenario(name, mode, legacy, k=0):
    import httpx
    from unittest.mock import patch
    from agents.orchestrator.circuit_breaker import QWEN_BREAKER
    MODE["m"] = mode
    QWEN_BREAKER.reset(); QWEN_BREAKER.enabled = True; QWEN_BREAKER.legacy_any_response_success = legacy
    qs, answers, cases = H.session_plan(k)
    ev = H.ReplayEvaluator(cases)
    o = H.new_orchestrator(k, qs, ev)
    attempts = {"n": 0}
    orig = httpx.AsyncClient.post

    async def counted(self, *a, **kw):
        attempts["n"] += 1
        return await orig(self, *a, **kw)
    t_turn, states = [], []
    with H.fixed_timer(), patch("httpx.AsyncClient.post", counted):
        res = await o.start(); root = {}
        for _ in range(40):
            if isinstance(res, dict) and res.get("type") == "session_end":
                break
            q = H._payload(res); qid = q["id"]
            if q.get("parent_question_id"):
                root[qid] = root.get(q["parent_question_id"], q["parent_question_id"])
            t0 = time.perf_counter()
            await o.handle_voice_answer(answers.get(qid) or answers.get(root.get(qid)), qid)
            t_turn.append(time.perf_counter() - t0)
            states.append(QWEN_BREAKER.state)
            res = await o.handle_next_question()
    QWEN_BREAKER.reset(); QWEN_BREAKER.legacy_any_response_success = False
    return {"name": name, "mode": mode, "breaker_semantics": "legacy" if legacy else "fixed", "turns": len(t_turn),
            "http_attempts_total": attempts["n"], "turn_s_median": statistics.median(t_turn), "turn_s_total": sum(t_turn),
            "breaker_state_after_turn": states, "committed_scores": list(o._state["scores"]), "llm_status_counts": {}}


async def part_b503(out: Path):
    gs = C.git_state()
    srv = ThreadingHTTPServer(("127.0.0.1", 8001), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    res = {}
    for name, mode, legacy in [("healthy_fixed", "ok", False), ("err503_legacy", "503", True), ("err503_fixed", "503", False)]:
        res[name] = await b503_scenario(name, mode, legacy)
        print(name, res[name]["http_attempts_total"], round(res[name]["turn_s_median"], 3), flush=True)
    srv.shutdown(); srv.server_close()
    res["_meta"] = {"git": gs, "class": "SOCKET"}
    C.write_once(out / "xe_b503.json", json.dumps(res, indent=1, sort_keys=True))


async def part_e5(out: Path):
    gs = C.git_state()
    os.environ["ADCOM_RESULTS"] = str(out)
    out.mkdir(parents=True, exist_ok=True)
    import e5_circuit_breaker as E5
    E5.OUT = out
    await E5.main()
    (out / "xe_e5_meta.json").write_text(json.dumps({"git": gs, "class": "SOCKET (new run, current code and defaults)"}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["e1", "e5", "b503"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    asyncio.run({"e1": part_e1, "e5": part_e5, "b503": part_b503}[a.part](Path(a.out)))
