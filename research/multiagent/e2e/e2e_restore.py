import asyncio, json, sys, urllib.request
import websockets
sys.path.insert(0,"paper/adcom2027/experiments")
import harness as H
PORT=sys.argv[1]; PHASE=sys.argv[2]; SID=sys.argv[3] if len(sys.argv)>3 else None
_qs,_answers,_cases=H.session_plan(0); _root={}
def http(m,p,b=None):
    r=urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=m,data=json.dumps(b).encode() if b is not None else None,headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r,timeout=60).read())
def ans(q):
    par=q.get("parent_question_id"); 
    if par: _root[q["id"]]=_root.get(par,par)
    return _answers.get(q["id"]) or _answers.get(_root.get(q["id"])) or "unrecorded"
async def drain(ws):
    out=[]
    while True:
        try: out.append(json.loads(await asyncio.wait_for(ws.recv(),3)))
        except asyncio.TimeoutError: return out
async def main():
    if PHASE=="1":
        s=http("POST","/api/sessions",{"candidate_id":"restore_probe","num_questions":8,"interview_mode":"demo_rl","baseline_questions":2})
        sid=s["id"]
        async with websockets.connect(f"ws://127.0.0.1:{PORT}/ws/interview/{sid}",max_size=None) as ws:
            await ws.send(json.dumps({"type":"start","payload":{}})); q=json.loads(await ws.recv())["payload"]
            for t in range(4):
                await ws.send(json.dumps({"type":"voice_answer","payload":{"transcript":ans(q),"question_id":q["id"],"attempts":1}})); await drain(ws)
                await ws.send(json.dumps({"type":"next_question","payload":{}})); q=json.loads(await ws.recv())["payload"]
        print("SID",sid); print("scores after phase1 turns: 4 answered")
    else:
        async with websockets.connect(f"ws://127.0.0.1:{PORT}/ws/interview/{SID}",max_size=None) as ws:
            await ws.send(json.dumps({"type":"next_question","payload":{}})); m=json.loads(await ws.recv())
            print("after restore, first message:",m["type"],str(m.get("payload"))[:100])
            q=m["payload"]; n=0
            while m["type"]=="question" and n<12:
                await ws.send(json.dumps({"type":"voice_answer","payload":{"transcript":ans(q),"question_id":q["id"],"attempts":1}})); ev=await drain(ws)
                if any(e["type"]=="session_end" for e in ev): break
                await ws.send(json.dumps({"type":"next_question","payload":{}})); m=json.loads(await ws.recv()); q=m["payload"]; n+=1
            await ws.send(json.dumps({"type":"end_session","payload":{}})); 
            while True:
                e=json.loads(await asyncio.wait_for(ws.recv(),60))
                if e["type"]=="session_end": break
        rep=http("GET",f"/api/sessions/{SID}/report")
        ma=rep.get("multiagent") or {}
        print("score_history",rep["score_history"]); print("agent_calls",ma.get("agent_calls"),"records",ma.get("records"))
asyncio.run(main())
