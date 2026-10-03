"""Replay harness: drives the REAL InterviewOrchestrator with recorded evaluator outputs.

Class of evidence produced with this harness: deterministic REPLAY / STUB runs.
 - Evaluator: stored outputs of the production evaluator for the 64 benchmark answers
   (research/results/paper2/paper2_evaluator_raw.json). No evaluator is executed.
 - Qwen (follow-up / feedback / hint): NOT run (no local weights in this environment). Either the service is
   'down' (the orchestrator's own non-LLM fallbacks run) or a SCRIPTED stub returns constructed JSON.
 - Timer: elapsed time is fixed (0.6 x allowed) so no timing modifier is applied.
 - PPO: the checkpoint is not loaded unless a run explicitly enables it.
Nothing here measures LLM quality.  See paper/adcom2027/protocol/.
"""
from __future__ import annotations

import asyncio
import copy
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
os.environ.setdefault("EVALUATOR_MOCK_MODE", "1")

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator  # noqa: E402
from agents.timing.timer import QuestionTimer  # noqa: E402

RAW = REPO / "research/results/paper2/paper2_evaluator_raw.json"
BENCH = REPO / "research/data/evaluator_benchmark/benchmark_dataset.csv"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(p).read_bytes())
    return h.hexdigest()


def load_cases():
    """64 recorded evaluator outputs, grouped by question id (8 questions x 8 answers)."""
    rows = json.loads(RAW.read_text(encoding="utf-8"))
    by_q = defaultdict(list)
    for r in sorted(rows, key=lambda r: r["case_id"]):
        by_q[int(r["qid"])].append(r)
    assert len(by_q) == 8 and all(len(v) == 8 for v in by_q.values())
    return by_q


def load_questions():
    qs = {}
    with open(BENCH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qid = int(row["qid"])
            if qid not in qs:
                qs[qid] = {"id": f"bq{qid}", "text": row["question"], "topic": row["topic"], "difficulty": 3,
                           "type": "verbal", "reference_answer": row["reference_answer"]}
    return qs


def session_plan(k: int, by_q=None, qs=None):
    """Session k (0..7): for each of the 8 questions the k-th recorded answer. Covers each of the 64 answers once."""
    by_q = by_q or load_cases()
    qs = qs or load_questions()
    questions, answers, cases = [], {}, {}
    for qid in sorted(by_q):
        c = by_q[qid][k]
        q = dict(qs[qid])
        q["expected_concepts"] = list(c["raw_eval"].get("expected_concepts", []))
        questions.append(q)
        answers[q["id"]] = c["raw_eval"]["candidate_answer"]
        cases[q["id"]] = c
    return questions, answers, cases


class ReplayEvaluator:
    """evaluator_fn(transcript, question): returns the stored production-evaluator payload for that answer."""

    def __init__(self, cases, fault=None):
        self.by_text = {c["raw_eval"]["candidate_answer"]: c["raw_eval"] for c in cases.values()}
        self.fault = fault          # None | callable(call_index, payload) -> payload | raises
        self.calls = 0

    def __call__(self, transcript, question):
        self.calls += 1
        base = self.by_text.get(transcript)
        if base is None:
            raise KeyError("no recorded evaluator output for transcript")
        payload = copy.deepcopy(base)
        if self.fault is not None:
            return self.fault(self.calls, payload)
        return payload


@contextmanager
def fixed_timer(ratio=0.6):
    def stop(self, snapshot, attempts=1, retries=0):
        el = snapshot.allowed_time_sec * ratio
        return {"time_taken_sec": round(el, 3), "allowed_time_sec": snapshot.allowed_time_sec,
                "time_overrun_sec": 0.0, "time_ratio": ratio, "time_norm": ratio, "is_overrun": False,
                "attempts": attempts, "retries": retries, "question_id": snapshot.question_id,
                "question_type": snapshot.question_type}
    with patch.object(QuestionTimer, "stop", stop):
        yield


@contextmanager
def qwen_mode(mode="down", script=None):
    """'down': every HTTP call fails -> orchestrator's non-LLM fallbacks.  'scripted': constructed JSON replies.
    The HTTP client class is replaced by a light stand-in (same call surface, no SSL-context construction)."""
    import httpx
    calls = {"n": 0, "urls": []}

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, *a, **k):
            calls["n"] += 1
            calls["urls"].append(str(url))
            if mode == "down":
                raise httpx.ConnectError("qwen service not running (harness)")
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = script(str(url), k.get("json") or {}) if script else {}
            return resp

    with patch("httpx.AsyncClient", FakeClient):
        yield calls


@contextmanager
def shared_ppo():
    """Memoise PPO.load so the 8 x N sessions do not re-read the same frozen checkpoint (predict is stateless)."""
    from stable_baselines3 import PPO
    cache, orig = {}, PPO.load.__func__ if hasattr(PPO.load, "__func__") else PPO.load

    def load(path, *a, **k):
        key = str(path)
        if key not in cache:
            cache[key] = orig(PPO, path, *a, **k)
        return cache[key]
    with patch.object(PPO, "load", staticmethod(load)):
        yield


def new_orchestrator(k, questions, evaluator, strategy="default", cfg=None):
    cfg = dict(cfg or {})
    base = {"c_topics": ["pointers"], "dsa_topics": ["graphs"], "duration_minutes": 30, "num_questions": 8,
            "interview_mode": "standard"}
    base.update(cfg)
    o = InterviewOrchestrator(f"adcom_s{k}", {"experience": "intermediate"}, base,
                              evaluator_fn=evaluator, select_questions_fn=lambda *a: list(questions))
    o._select_questions_fn = None           # keep the fixed queue (as the repository's own tests do)
    o._question_queue = [dict(q) for q in questions]
    o._state["questions"] = list(o._question_queue)
    o._state["question_ids"] = [q["id"] for q in questions]
    if strategy is None:
        o._strategy = None
    return o


def _payload(res):
    return res["payload"] if isinstance(res, dict) and "payload" in res else res


async def drive(o, answers, max_turns=40, max_retries=2):
    """Drive one session to completion. Returns list of per-turn records (primary + follow-ups)."""
    turns, root = [], {}
    res = await o.start()
    for _ in range(max_turns):
        if isinstance(res, dict) and res.get("type") == "session_end":
            break
        q = _payload(res)
        qid = q["id"]
        parent = q.get("parent_question_id")
        if parent:
            root[qid] = root.get(parent, parent)
        text = answers.get(qid) or answers.get(root.get(qid)) or "unrecorded"
        r = None
        for attempt in range(max_retries + 1):
            r = await o.handle_voice_answer(text, qid)
            if r.get("next_action") != "retry_answer":
                break
        turns.append({"qid": qid, "is_followup": bool(q.get("is_followup")), "parent": parent,
                      "next_action": r.get("next_action"),
                      "score": (r.get("feedback") or {}).get("final_score"),
                      "feedback": r.get("feedback"), "difficulty_update": r.get("difficulty_update")})
        if r.get("next_action") == "retry_answer":
            break
        res = await o.handle_next_question()
    else:
        turns.append({"qid": None, "error": "max_turns_exceeded"})
    return turns


# ───────────────────────── protocol ADCOM-E1..E3 v1 additions ─────────────────────────
import math  # noqa: E402
import time  # noqa: E402
import numpy as np  # noqa: E402

_REAL_SLEEP = asyncio.sleep


@contextmanager
def no_backoff():
    """Skip the orchestrator's 0.1 s retry back-off sleeps (E1 only; E2 measures the real delays)."""
    async def fast(delay, *a, **k):
        await _REAL_SLEEP(0)
    with patch("asyncio.sleep", fast):
        yield


def apply_variant(o, vid):
    if vid == "V0":
        return
    if vid == "V1":
        o._validator = None
    elif vid == "V2":
        o._apply_guardrails = lambda action_idx, *a, **k: action_idx
    elif vid == "V3":
        o._strategy = None
    elif vid == "V4":
        async def no_fu(*a, **k):
            return False
        o._decide_and_inject_followup = no_fu
    elif vid == "V5":
        orig = o._decide_and_inject_followup

        async def uncapped(*a, **k):
            o._state["consecutive_followups"] = 0
            return await orig(*a, **k)
        o._decide_and_inject_followup = uncapped
    elif vid == "V6":
        orig = o._evaluate_verbal

        async def swallow(transcript, question):
            r = await orig(transcript, question)
            if r.get("decision_source") == "evaluator_unavailable" or r.get("status") == "evaluator_unavailable":
                return {"final_score": 0.0, "grade": "Poor", "correct_claims": [], "incorrect_claims": [],
                        "missing_concepts": list(question.get("expected_concepts", [])),
                        "justification": "evaluator output absent; handed on as an ordinary answer (ablation V6)",
                        "decision_source": "evaluator_cross_encoder"}
            return r
        o._evaluate_verbal = swallow
    elif vid == "V7":
        o._rollback_tentative_attempt = lambda: None
    else:
        raise ValueError(vid)


def valid_score(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0.0 <= v <= 1.0


class FaultyEvaluator(ReplayEvaluator):
    """ReplayEvaluator + registered fault schedule + per-call log used by the invariants."""

    def __init__(self, cases, fault="F0", seed=0):
        super().__init__(cases)
        self.kind, self.seed = fault, seed
        self.rng = np.random.default_rng(seed)
        self.log = []                    # (qid, ok_valid, injected)
        self.f4_qids = set()

    def __call__(self, transcript, question):
        self.calls += 1
        qid = question.get("id")
        base = self.by_text.get(transcript)
        if base is None:
            raise KeyError("no recorded evaluator output")
        p = copy.deepcopy(base)
        injected = None
        if self.kind == "F1":
            self.log.append((qid, False, "F1")); raise RuntimeError("evaluator outage (F1)")
        if self.kind == "F2" and self.rng.random() < 0.25:
            self.log.append((qid, False, "F2")); raise RuntimeError("evaluator outage (F2)")
        if self.kind == "F3":
            vals = [None, float("nan"), "high", 1.7, -0.3]
            p["final_score"] = vals[(self.calls + self.seed) % 5]
            injected = "F3"
        if self.kind == "F4" and not p.get("mandatory_pass", True):
            p["final_score"] = 0.95
            self.f4_qids.add(qid)
            injected = "F4"
        self.log.append((qid, valid_score(p.get("final_score")), injected))
        return p


async def drive2(o, answers, retry_once=False, max_turns=40, max_retries=2):
    """Like drive(), returns a dict with the evidence the invariants need."""
    turns, root, ended, exhausted = [], {}, False, False
    res = await o.start()
    for _ in range(max_turns):
        if isinstance(res, dict) and res.get("type") == "session_end":
            ended = True
            break
        q = _payload(res)
        qid, parent = q["id"], q.get("parent_question_id")
        if parent:
            root[qid] = root.get(parent, parent)
        text = answers.get(qid) or answers.get(root.get(qid)) or "unrecorded"
        rl_phase = bool(o._state.get("baseline_complete"))
        d_before = int(o._state.get("current_difficulty", 0))
        r = None
        for attempt in range(max_retries + 1):
            r = await o.handle_voice_answer(text, qid)
            if r.get("next_action") != "retry_answer":
                break
        if r.get("next_action") == "retry_answer":
            exhausted = True
            turns.append({"qid": qid, "is_followup": bool(q.get("is_followup")), "committed": False})
            break
        if retry_once:
            await o.handle_retry(qid)
            r = await o.handle_voice_answer(text, qid)
        d_after = int(o._state.get("current_difficulty", 0))
        turns.append({"qid": qid, "is_followup": bool(q.get("is_followup")), "committed": True,
                      "score": (r.get("feedback") or {}).get("final_score"), "rl_phase": rl_phase,
                      "d_before": d_before, "d_after": d_after,
                      "decision_source": o._state.get("last_decision_source")})
        res = await o.handle_next_question()
    return {"turns": turns, "ended": ended, "retry_exhausted": exhausted}
