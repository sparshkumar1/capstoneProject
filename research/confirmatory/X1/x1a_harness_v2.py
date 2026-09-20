#!/usr/bin/env python
"""X1-A fault-injection campaign harness (Paper 1). Protocol: research/confirmatory/X1/PROTOCOL_X1-A_v2.md (build B rerun of the v1 campaign).

Scenario = an enumerated dependency fault class; the unit of analysis is the scenario, never the trial. PASS/FAIL is computed
from observables by the criteria below. Every scenario has a no-fault control and oracle-perturbation controls (a synthetic
defective observation that the oracle must reject). Faults are injected in-process against the real orchestrator / executor /
storage code; nothing external is contacted.

    --dry-run                           one repetition of the fast scenarios, temp output, not evidence
    --run --registered-commit <40>      official run (protocol tag gate), write-once output
"""
import asyncio, copy, hashlib, json, math, os, re, sqlite3, subprocess, sys, tempfile, threading, time, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import AsyncMock, patch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
os.environ.setdefault("EVALUATOR_MOCK_MODE", "1")
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
import agents.orchestrator.feedback_agent as fa
import agents.coding_executor.coding_executor as ce
from services.storage.database import init_db, get_or_create_candidate, save_attempt, get_question_attempts, get_connection

PROTOCOL_TAG = "prereg/X1-A/v2"
SUT_TAG = "sut/X1/build-B"
OUT_REL = "research/confirmatory/X1/results/x1a_v2"
REPS = 5
QWEN_TIMEOUT = fa.QWEN_TIMEOUT                       # 6.0 s, read from the SUT
SLA_QWEN_DOWN_S = 5.0                                 # refused connection x2 attempts + 0.1 s sleeps + orchestration, pre-specified
SLA_QWEN_SLOW_S = 2 * QWEN_TIMEOUT + 3.0              # two attempts at the client timeout + 3 s slack
SLA_DOCKER_DOWN_S = 2.0
COMPILE_TIMEOUT_S = 10.0                              # hard-coded in the executor
SLA_COMPILE_S = COMPILE_TIMEOUT_S + 3.0
DB_BUSY_TIMEOUT_S = 30.0                              # sqlite3.connect(timeout=30.0) in services/storage/database.py
FIXED_EVAL = {"final_score": 0.90, "raw_evaluator_score": 0.90, "grade": "Excellent",
              "score_breakdown": {"semantic_similarity": 0.8, "concept_coverage": 0.9, "reasoning_quality": 0.95, "overall": 0.9},
              "covered_concepts": ["pointer dereference", "pointer arithmetic"], "correct_claims": ["pointer dereference"],
              "missing_concepts": [], "incorrect_claims": [], "weakest_gap": "None - comprehensive answer",
              "decision_source": "evaluator_cross_encoder", "mandatory_pass": True, "mistake_penalty": 0.0}
QUESTION = {"id": "x1a_q1", "text": "Explain what a pointer is in C.", "topic": "pointers", "difficulty": 3, "type": "verbal",
            "expected_concepts": ["pointer dereference", "pointer arithmetic"], "reference_answer": "A pointer holds an address."}
ANSWER = "A pointer stores the address of another variable and dereferencing it reads the value stored there."
QUEUE = 6
DRY = "--dry-run" in sys.argv


def cj(x):
    return json.dumps(x, sort_keys=True, default=str)


def finite01(v):
    return isinstance(v, (int, float)) and math.isfinite(v) and 0.0 <= v <= 1.0


# ----------------------------------------------------------------------------------------- Qwen stub (local)
class Stub:
    mode = "ok"                                       # ok | slow

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            self.rfile.read(n)
            if Stub.mode == "slow":
                time.sleep(QWEN_TIMEOUT + 2.0)
            body = json.dumps({"what_candidate_said": "stub", "what_was_correct": ["stub"], "what_was_incorrect": [], "what_was_incomplete": [],
                               "missing_concepts": [], "how_to_answer": "stub", "stronger_answer_guide": "stub", "actionable_improvements": [],
                               "narrative_feedback": "stub narrative", "decision_source": "qwen_feedback_stub"}).encode()
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                pass

    srv = None

    @classmethod
    def start(cls, mode):
        cls.mode = mode
        if cls.srv is None:
            cls.srv = ThreadingHTTPServer(("127.0.0.1", 8001), cls.H)
            cls.srv.daemon_threads = True
            threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def stop(cls):
        if cls.srv is not None:
            cls.srv.shutdown()
            cls.srv.server_close()
            cls.srv = None


# ----------------------------------------------------------------------------------------- turn helpers
def _orch():
    o = InterviewOrchestrator("x1a", {"experience": "intermediate"},
                              {"c_topics": ["pointers"], "dsa_topics": ["graphs"], "duration_minutes": 30, "num_questions": QUEUE,
                               "interview_mode": "standard"})
    o._select_questions_fn = None
    o._question_queue = [copy.deepcopy(QUESTION)] + [dict(QUESTION, id="x1a_q%d" % i) for i in range(2, QUEUE + 1)]
    o._state["questions"] = list(o._question_queue)
    return o


async def turn(transcript=ANSWER, evaluator=None):
    """One real answer turn. `evaluator(transcript, question)` is the injected evaluator function (real orchestrator code path)."""
    o = _orch()
    await o.start()
    o._evaluator_fn = evaluator or (lambda t, q: copy.deepcopy(FIXED_EVAL))
    t0 = time.time()
    exc = None
    resp = {}
    try:
        resp = await o.handle_voice_answer(transcript, QUESTION["id"])
    except Exception as e:
        exc = repr(e)
    dt = time.time() - t0
    fb = resp.get("feedback", {}) or {}
    return {"exception": exc, "seconds": round(dt, 3), "llm_status": fb.get("llm_status"), "decision_source": fb.get("decision_source"),
            "fb_final_score": fb.get("final_score"), "fb_grade": fb.get("grade"), "fb_status": fb.get("status"), "stt_status": fb.get("stt_status"),
            "covered": fb.get("covered_concepts"), "state_scores": list(o._state.get("scores", [])),
            "infra_errors": list(o._state.get("infrastructure_errors", [])), "next_action": resp.get("next_action"),
            "difficulty_update": resp.get("difficulty_update"), "fb_keys_infra": [k for k in fb if "infra" in k.lower()]}


def run(coro):
    return asyncio.run(coro)


def docker_ids():
    return set(subprocess.run(["docker", "ps", "-a", "-q"], capture_output=True, text=True).stdout.split())


# ----------------------------------------------------------------------------------------- scenarios
# Each scenario: name, dependency, mode, fn(rep)->(fault_obs, control_obs), oracle(fault,control)->dict, perturbations [(name, fn(obs)->obs)]
def qwen_scenarios(kind):
    def fn(rep):
        Stub.stop()
        Stub.start("ok")
        ctrl = run(turn())
        Stub.stop()
        if kind == "slow":
            Stub.start("slow")
        fault = run(turn())
        Stub.stop()
        Stub.start("ok")
        rec = run(turn())                              # recovery on the next request
        Stub.stop()
        fault["recovery_llm_status"] = rec["llm_status"]
        return fault, ctrl

    sla = SLA_QWEN_DOWN_S if kind == "down" else SLA_QWEN_SLOW_S

    def oracle(f, c):
        return {"no_exception": f["exception"] is None, "returns_within_sla": f["seconds"] <= sla, "llm_status_unavailable": f["llm_status"] == "llm_unavailable",
                "source_not_llm": "qwen" not in str(f["decision_source"]).lower(), "score_equals_no_fault": f["fb_final_score"] == c["fb_final_score"],
                "state_scores_equal_no_fault": f["state_scores"] == c["state_scores"], "concepts_equal_no_fault": f["covered"] == c["covered"],
                "control_used_llm": c["llm_status"] == "available", "recovers_next_request": f["recovery_llm_status"] == "available"}
    perts = [("claims_llm_available", lambda o: dict(o, llm_status="available", decision_source="qwen_feedback")),
             ("too_slow", lambda o: dict(o, seconds=sla + 30.0)), ("score_changed", lambda o: dict(o, fb_final_score=0.5)),
             ("exception", lambda o: dict(o, exception="RuntimeError('x')"))]
    return ("FLT-01" if kind == "down" else "FLT-02", "Qwen service " + ("unavailable (port closed)" if kind == "down" else "slower than the client timeout"), fn, oracle, perts)


def flt03():
    def fn(rep):
        def down(t, q):
            raise ConnectionError("evaluator 503")
        Stub.stop()
        Stub.start("ok")
        f = run(turn(evaluator=down))
        c = run(turn())
        Stub.stop()
        return f, c

    def oracle(f, c):
        infra = (f["fb_status"] == "evaluator_unavailable") or f["decision_source"] == "evaluator_unavailable" or bool(f["fb_keys_infra"]) or bool(f["infra_errors"])
        return {"no_exception": f["exception"] is None, "infrastructure_failure_flagged": bool(infra), "no_zero_score_recorded_as_candidate_failure": 0.0 not in f["state_scores"],
                "no_fabricated_score": not any(isinstance(s, float) and s > 0 for s in f["state_scores"]), "control_scores_normally": c["state_scores"] != [] and 0.0 not in c["state_scores"]}
    perts = [("infra_not_flagged", lambda o: dict(o, fb_status="ok", decision_source="evaluator", fb_keys_infra=[], infra_errors=[])),
             ("zero_recorded", lambda o: dict(o, state_scores=[0.0])), ("fabricated_score", lambda o: dict(o, state_scores=[0.7]))]
    return ("FLT-03", "Evaluator service unavailable (exception on call)", fn, oracle, perts)


def flt04(value):
    def fn(rep):
        Stub.stop()
        Stub.start("ok")
        ev = lambda t, q: dict(copy.deepcopy(FIXED_EVAL), final_score=value, raw_evaluator_score=value)
        f = run(turn(evaluator=ev))
        c = run(turn())
        Stub.stop()
        return f, c

    def oracle(f, c):
        return {"no_exception": f["exception"] is None, "feedback_score_finite_in_unit_interval": finite01(f["fb_final_score"]),
                "state_scores_finite_in_unit_interval": bool(f["state_scores"]) and all(finite01(s) for s in f["state_scores"]),
                "control_valid": all(finite01(s) for s in c["state_scores"]) and bool(c["state_scores"])}
    perts = [("raw_invalid_stored", lambda o: dict(o, state_scores=[value], fb_final_score=value)), ("exception", lambda o: dict(o, exception="x"))]
    return ("FLT-04[%s]" % value, "Evaluator returns an invalid score (%s)" % value, fn, oracle, perts)


def flt05():
    def fn(rep):
        before = docker_ids()
        with patch.object(ce.shutil, "which", lambda name, *a, **k: None):
            t0 = time.time()
            r = ce.DockerCSandbox().compile_and_execute("int main(void){return 0;}\n", [{"id": "t", "input": "", "expected": ""}])
            dt = time.time() - t0
        f = {"status": r.get("status"), "passed": r.get("passed"), "seconds": round(dt, 3), "new_containers": sorted(docker_ids() - before), "error": r.get("error")}
        t0 = time.time()
        c0 = ce.DockerCSandbox().compile_and_execute('#include <stdio.h>\nint main(void){printf("HELLO");return 0;}\n', [{"id": "t", "input": "", "expected": "HELLO"}])
        f["recovery_status"] = c0.get("status")
        return f, {"status": c0.get("status"), "seconds": round(time.time() - t0, 3)}

    def oracle(f, c):
        return {"status_sandbox_error": f["status"] == "sandbox_error", "not_accepted": f["status"] != "accepted" and f["passed"] is False,
                "no_hang": f["seconds"] <= SLA_DOCKER_DOWN_S, "no_container_created": not f["new_containers"], "structured_error_message": bool(f["error"]),
                "control_accepts": c["status"] == "accepted", "recovers_when_daemon_reachable": f["recovery_status"] == "accepted"}
    perts = [("false_accepted", lambda o: dict(o, status="accepted", passed=True)), ("hang", lambda o: dict(o, seconds=60.0)),
             ("container_created", lambda o: dict(o, new_containers=["abc"]))]
    return ("FLT-05", "Docker daemon unreachable (docker and wsl CLIs not found)", fn, oracle, perts)


class _SleepCompile:
    def __init__(self):
        self.calls = 0

    def __getattr__(self, k):
        return getattr(subprocess, k)

    def run(self, cmd, *a, **kw):
        if isinstance(cmd, list) and len(cmd) > 1 and cmd[1] == "run" and "-i" not in cmd[:5]:   # the compile container
            cmd = list(cmd[:-1]) + ["sleep 60"]
            self.calls += 1
        return subprocess.run(cmd, *a, **kw)


def flt06():
    def fn(rep):
        before = docker_ids()
        real = ce.subprocess
        ce.subprocess = _SleepCompile()
        try:
            t0 = time.time()
            r = ce.DockerCSandbox().compile_and_execute("int main(void){return 0;}\n", [{"id": "t", "input": "", "expected": ""}])
            dt = time.time() - t0
        finally:
            ce.subprocess = real
        time.sleep(3.0)
        leftover = sorted(docker_ids() - before)
        for cid in leftover:                                   # cleanup AFTER the observation; recorded
            subprocess.run(["docker", "rm", "-f", cid], capture_output=True)
        f = {"status": r.get("status"), "seconds": round(dt, 3), "compiler_output": str(r.get("compiler_output", ""))[:120],
             "leftover_containers_after_3s": leftover, "cleanup": "docker rm -f on leftovers after observation"}
        c0 = ce.DockerCSandbox().compile_and_execute('#include <stdio.h>\nint main(void){printf("HELLO");return 0;}\n', [{"id": "t", "input": "", "expected": "HELLO"}])
        f["next_submission_status"] = c0.get("status")
        return f, {"status": c0.get("status")}

    def oracle(f, c):
        return {"terminated_by_compile_timeout": COMPILE_TIMEOUT_S - 1 <= f["seconds"] <= SLA_COMPILE_S, "status_reflects_timeout": f["status"] == "compilation_error" and "timed out" in f["compiler_output"].lower(),
                "not_accepted": f["status"] != "accepted", "no_orphan_container_3s_after_return": not f["leftover_containers_after_3s"],
                "next_submission_runs": f["next_submission_status"] == "accepted"}
    perts = [("hang", lambda o: dict(o, seconds=120.0)), ("orphan", lambda o: dict(o, leftover_containers_after_3s=["abc"])), ("accepted", lambda o: dict(o, status="accepted"))]
    return ("FLT-06", "Compiler outlives the compile timeout (compile step replaced by `sleep 60`)", fn, oracle, perts)


def _db(tmp):
    p = Path(tmp) / ("x1a_%s.db" % uuid.uuid4().hex[:6])
    init_db(p)
    cand = get_or_create_candidate("%s@x1a.dev" % uuid.uuid4().hex[:8], "X1A", db_path=p)
    return p, cand["id"]


def _attempt(cid):
    return {"candidate_id": cid, "session_id": "s1", "question_id": "q_lock", "attempt_type": "primary", "answer_type": "verbal", "transcript": "a",
            "raw_score": 0.9, "validated_score": 0.9, "missing_concepts": []}


def flt07(hold_s, label):
    def fn(rep):
        with tempfile.TemporaryDirectory() as tmp:
            p, cid = _db(tmp)
            holder = sqlite3.connect(str(p), timeout=1.0, isolation_level=None, check_same_thread=False)
            holder.execute("BEGIN IMMEDIATE")
            rel = threading.Timer(hold_s, lambda: holder.execute("ROLLBACK"))
            rel.start()
            t0 = time.time()
            exc, res = None, None
            try:
                res = save_attempt(_attempt(cid), db_path=p)
            except Exception as e:
                exc = "%s: %s" % (type(e).__name__, e)
            dt = time.time() - t0
            rel.join()
            holder.close()
            rows = len(get_question_attempts(cid, "q_lock", db_path=p))
            after_exc = None
            try:
                save_attempt(_attempt(cid), db_path=p)
            except Exception as e:
                after_exc = repr(e)
            rows_after = len(get_question_attempts(cid, "q_lock", db_path=p))
            f = {"hold_s": hold_s, "seconds": round(dt, 3), "exception": exc, "acknowledged": exc is None and res is not None, "rows_after_operation": rows,
                 "rows_after_release_and_retry": rows_after, "retry_exception": after_exc}
            tmp2 = tempfile.mkdtemp()
            p2, cid2 = _db(tmp2)
            t0 = time.time()
            save_attempt(_attempt(cid2), db_path=p2)
            c = {"seconds": round(time.time() - t0, 3), "rows": len(get_question_attempts(cid2, "q_lock", db_path=p2))}
            return f, c

    short = hold_s < DB_BUSY_TIMEOUT_S

    def oracle(f, c):
        d = {"rows_equal_acknowledged_writes": f["rows_after_operation"] == (1 if f["acknowledged"] else 0), "no_partial_rows": f["rows_after_operation"] in (0, 1),
             "writes_succeed_after_release": f["retry_exception"] is None and f["rows_after_release_and_retry"] == f["rows_after_operation"] + 1, "control_writes": c["rows"] == 1}
        if short:
            d.update({"succeeds_after_wait": f["acknowledged"], "waited_for_release": f["seconds"] >= f["hold_s"] - 0.5})
        else:
            d.update({"fails_visibly": f["exception"] is not None and "locked" in str(f["exception"]).lower(), "fails_near_busy_timeout": DB_BUSY_TIMEOUT_S - 2 <= f["seconds"] <= DB_BUSY_TIMEOUT_S + 3})
        return d
    perts = [("silent_loss", lambda o: dict(o, exception=None, acknowledged=True, rows_after_operation=0)), ("partial_row", lambda o: dict(o, rows_after_operation=2)),
             ("stuck_after_release", lambda o: dict(o, retry_exception="OperationalError('locked')"))]
    return ("FLT-07%s" % label, "SQLite write lock held %.0f s (busy timeout %.0f s)" % (hold_s, DB_BUSY_TIMEOUT_S), fn, oracle, perts)


def flt10():
    def fn(rep):
        Stub.stop()
        Stub.start("ok")
        f = run(turn(transcript=""))
        w = run(turn(transcript="   "))
        c = run(turn())
        Stub.stop()
        f["whitespace"] = {k: w[k] for k in ("exception", "stt_status", "fb_grade", "state_scores")}
        code = ce.DockerCSandbox().compile_and_execute("", [{"id": "t", "input": "", "expected": ""}])
        f["empty_code_status"] = code.get("status")
        f["empty_code_reason"] = code.get("policy_reasons")
        return f, c

    def oracle(f, c):
        return {"no_exception_empty_transcript": f["exception"] is None, "no_exception_whitespace": f["whitespace"]["exception"] is None,
                "structured_no_input_outcome": f["stt_status"] == "stt_unavailable" and f["fb_grade"] == "Ungraded", "whitespace_same_outcome": f["whitespace"]["stt_status"] == "stt_unavailable",
                "empty_code_structured": f["empty_code_status"] == "policy_blocked" and bool(f["empty_code_reason"]), "control_scores_normally": c["state_scores"] == [0.9] or bool(c["state_scores"])}
    perts = [("exception", lambda o: dict(o, exception="x")), ("scored_as_real", lambda o: dict(o, stt_status=None, fb_grade="Excellent")),
             ("empty_code_accepted", lambda o: dict(o, empty_code_status="accepted"))]
    return ("FLT-10", "Empty transcript / whitespace transcript / empty code", fn, oracle, perts)


def scenarios(fast_only=False):
    s = [qwen_scenarios("down"), qwen_scenarios("slow"), flt03()] + [flt04(v) for v in (float("nan"), float("inf"), 999.0, -3.0)] + [flt05(), flt06(), flt10(), flt07(2.0, "a"), flt07(34.0, "b")]
    if fast_only:
        s = [x for x in s if x[0] not in ("FLT-02", "FLT-06", "FLT-07b")]
    return s


NOT_EXECUTED = {"FLT-08": "WebSocket reset mid-evaluation: requires the full backend + WebSocket client harness; not built in this campaign, so no claim about it is supported",
                "FLT-09": "Audio/feature-extractor crash: requires the audio pipeline; not executed, so no claim about it is supported"}


def campaign(reps, fast_only=False):
    rows, verdicts = [], {}
    for sid, desc, fn, oracle, perts in scenarios(fast_only):
        res = []
        for rep in range(1, reps + 1):
            try:
                f, c = fn(rep)
                crit = oracle(f, c)
                err = None
            except Exception as e:
                f, c, crit, err = {}, {}, {}, repr(e)
            met = bool(crit) and all(crit.values())
            res.append({"scenario": sid, "description": desc, "rep": rep, "criteria": crit, "criteria_met": met, "harness_error": err,
                        "fault_observation": f, "control_observation": c, "timestamp": datetime.now(timezone.utc).isoformat()})
            print("%-14s r%d done" % (sid, rep), flush=True) if DRY else print("%-14s r%d met=%s %s" % (sid, rep, met, ",".join(k for k, v in crit.items() if not v)), flush=True)
        rows += res
        # oracle-perturbation controls on the first repetition's observations
        ctrl = []
        base = next((r for r in res if r["fault_observation"]), None)
        if base:
            for name, p in perts:
                pf = p(copy.deepcopy(base["fault_observation"]))
                pc = oracle(pf, base["control_observation"])
                ctrl.append({"perturbation": name, "oracle_rejects": not all(pc.values()), "failed": [k for k, v in pc.items() if not v]})
        verdicts[sid] = {"description": desc, "criteria_met": "%d/%d" % (sum(r["criteria_met"] for r in res), len(res)),
                         "failed_criteria": sorted({k for r in res for k, v in r["criteria"].items() if not v}),
                         "oracle_perturbation_controls": ctrl, "oracle_valid": bool(ctrl) and all(x["oracle_rejects"] for x in ctrl)}
    return rows, verdicts


def sut_state():
    g = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
    diff = lambda p: subprocess.run(["git", "-C", str(REPO), "diff", "--quiet", SUT_TAG, "--", p]).returncode == 0
    return {"sut_tag": SUT_TAG, "sut_commit": g("rev-parse", SUT_TAG + "^{commit}"), "head": g("rev-parse", "HEAD"),
            "agents_clean": diff("agents"), "services_clean": diff("services"), "constants": {"QWEN_TIMEOUT": QWEN_TIMEOUT, "SLA_QWEN_DOWN_S": SLA_QWEN_DOWN_S,
            "SLA_QWEN_SLOW_S": SLA_QWEN_SLOW_S, "SLA_DOCKER_DOWN_S": SLA_DOCKER_DOWN_S, "COMPILE_TIMEOUT_S": COMPILE_TIMEOUT_S, "DB_BUSY_TIMEOUT_S": DB_BUSY_TIMEOUT_S},
            "python": sys.version, "not_executed": NOT_EXECUTED}


def official(argv):
    rc = argv[argv.index("--registered-commit") + 1] if "--registered-commit" in argv[:-1] else ""
    g = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
    assert re.fullmatch("[0-9a-f]{40}", rc), "40-hex --registered-commit required"
    assert g("cat-file", "-t", "refs/tags/" + PROTOCOL_TAG) == "tag"
    assert g("rev-parse", "refs/tags/%s^{commit}" % PROTOCOL_TAG) == rc == g("rev-parse", "HEAD"), "HEAD != protocol tag commit"
    for rel in ("research/confirmatory/X1/x1a_harness_v2.py", "research/confirmatory/X1/PROTOCOL_X1-A_v2.md"):
        blob = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", "%s:%s" % (rc, rel)], capture_output=True).stdout
        assert blob == (REPO / rel).read_bytes(), rel
    sut = sut_state()
    assert sut["agents_clean"] and sut["services_clean"], "SUT differs from tag"
    out = REPO / OUT_REL
    os.makedirs(out.parent, exist_ok=True)
    os.mkdir(out)
    t0 = datetime.now(timezone.utc).isoformat()
    rows, verdicts = campaign(REPS)
    with open(out / "runs.jsonl", "x", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")
    verdicts["_run"] = {"protocol_tag": PROTOCOL_TAG, "registered_commit": rc, "started_utc": t0, "finished_utc": datetime.now(timezone.utc).isoformat(),
                        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "reps": REPS}
    json.dump({"sut": sut, "verdicts": verdicts}, open(out / "verdicts.json", "x", encoding="utf-8"), indent=2, default=str)
    print(json.dumps(verdicts, indent=1, default=str))


def dry_run():
    """Plumbing check only: prints harness errors and oracle-control validity, never the SUT pass/fail criteria."""
    rows, verdicts = campaign(1, fast_only=True)
    for r in rows:
        if r["harness_error"]:
            print("HARNESS ERROR", r["scenario"], r["harness_error"])
    print(json.dumps({k: {"oracle_valid": v["oracle_valid"], "n_criteria": len(rows[0]["criteria"])} for k, v in verdicts.items()}, indent=1, default=str))


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        dry_run()
    elif "--run" in sys.argv:
        official(sys.argv)
    else:
        print(__doc__)
