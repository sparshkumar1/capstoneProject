"""E2E smoke client against a RUNNING backend (real HTTP + WebSocket). Usage: e2e_client.py PORT LABEL [strong|weak|mixed]"""
import asyncio, json, sys, time, urllib.request, re
import websockets
PORT, LABEL = sys.argv[1], sys.argv[2]
MODE = sys.argv[3] if len(sys.argv) > 3 else "mixed"
sys.path.insert(0,"paper/adcom2027/experiments")
import harness as H
_qs,_answers,_cases=H.session_plan(0)
def http(method, path, body=None):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())
_root = {}
def answer_for(q, i):
    qid = q.get("id"); par = q.get("parent_question_id")
    if par: _root[qid] = _root.get(par, par)
    return _answers.get(qid) or _answers.get(_root.get(qid)) or "unrecorded answer"
async def main():
    ev = []
    s = http("POST", "/api/sessions", {"candidate_id": f"e2e_{LABEL}", "num_questions": 8, "interview_mode": "demo_rl", "baseline_questions": 2,
                                        "dsa_topics": ["Arrays", "Strings"], "c_topics": [], "duration_minutes": 30})
    sid = s["id"] if "id" in s else s.get("session_id"); ev.append(("created", sid, list(s)[:6]))
    async with websockets.connect(f"ws://127.0.0.1:{PORT}/ws/interview/{sid}", max_size=None) as ws:
        async def rx():
            m = json.loads(await asyncio.wait_for(ws.recv(), 120)); ev.append((m["type"], m["payload"])); return m
        await ws.send(json.dumps({"type": "start", "payload": {}})); m = await rx()
        turn = 0; ended = False
        while m["type"] == "question" and turn < 40:
            q = m["payload"]; qid = q.get("id")
            await ws.send(json.dumps({"type": "voice_answer", "payload": {"transcript": answer_for(q, turn), "question_id": qid, "attempts": 1}}))
            fb = await rx()
            # drain follow-on events until feedback done (hint/difficulty_update/session_end)
            nxt = None
            while True:
                try:
                    m2 = json.loads(await asyncio.wait_for(ws.recv(), 3)); ev.append((m2["type"], m2["payload"]))
                    if m2["type"] == "session_end": ended = True; break
                except asyncio.TimeoutError: break
            if ended: break
            await ws.send(json.dumps({"type": "next_question", "payload": {}})); m = await rx(); turn += 1
            if m["type"] == "session_end": ended = True; break
        if not ended:
            await ws.send(json.dumps({"type": "end_session", "payload": {}}))
            while True:
                m = await rx()
                if m["type"] == "session_end": ended = True; break
    st = http("GET", f"/api/sessions/{sid}")
    rep = http("GET", f"/api/sessions/{sid}/report")
    out = {"label": LABEL, "session": sid, "events": ev, "state_keys": list(st)[:12], "report_keys": list(rep)[:20], "report": rep}
    json.dump(out, open(f"{__import__('os').environ.get('E2E_OUT','.')}/e2e_{LABEL}.json", "w"), default=str, indent=1)
    types = [e[0] for e in ev]
    import collections; print(LABEL, "event counts", dict(collections.Counter(types)))
    fbs = [e[1] for e in ev if e[0] == "feedback"]
    print("feedback n", len(fbs), "scores", [round(float(f.get("final_score") if f.get("final_score") is not None else -1), 3) for f in fbs])
    print("coaching_plan in feedback:", sum('coaching_plan' in f for f in fbs), "of", len(fbs))
    dus = [e[1] for e in ev if e[0] == "difficulty_update"]; print("difficulty_updates", [(d.get("action"), d.get("new_difficulty")) for d in dus])
    print("report has multiagent:", "multiagent" in rep, "| ended:", ended, "| overall", rep.get("overall_score"))
asyncio.run(main())
