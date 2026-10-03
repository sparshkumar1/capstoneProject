"""Shared machinery for the multi-agent experiments (protocol MA-XA-XB v1).

Evidence class: REPLAY (recorded production-evaluator payloads for 64 constructed answers, driven through the real
InterviewOrchestrator) and FAULT-INJECTED (constructed agent faults). No LLM runs (Qwen is stubbed as 'down', so the
orchestrator's own non-LLM fallbacks serve follow-ups and feedback); the frozen PPO checkpoint runs unless a condition disables it.
Nothing here measures candidate learning, coaching quality or LLM behaviour.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import random
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "paper/adcom2027/experiments"))
import harness as H  # noqa: E402  (replay harness from the earlier ADCOM study; read-only dependency)

from agents.multiagent.grounding import ungrounded_concepts  # noqa: E402

_IDX = {"Easier": 0, "Same": 1, "Harder": 2}


def git_state():
    def run(*a):
        return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain")), "branch": run("branch", "--show-current")}


def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_config(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_session(k: int, seed: int):
    """Session k = k-th recorded answer for each of the 8 questions; seed > 0 shuffles the question order (seed 0 = original)."""
    qs, answers, cases = H.session_plan(k)
    if seed:
        order = list(range(len(qs)))
        random.Random(1000 * k + seed).shuffle(order)
        qs = [qs[i] for i in order]
    return qs, answers, cases


def condition_cfg(cond: dict) -> dict:
    cfg = {}
    if cond.get("guardrail_impl"):
        cfg["guardrail_impl"] = cond["guardrail_impl"]
    if cond.get("multiagent"):
        ma = {k: v for k, v in cond["multiagent"].items()}
        cfg["multiagent_enabled"] = True
        cfg["multiagent"] = ma
    return cfg


async def run_one(name: str, cond: dict, k: int, seed: int, extra_agents=None, timeout_s=None):
    """One replay session. Returns a flat dict of metrics (+ raw per-turn latencies)."""
    qs, answers, cases = build_session(k, seed)
    recorded = {c["raw_eval"]["candidate_answer"]: float(c["raw_eval"]["final_score"]) for c in cases.values()}
    ev = H.ReplayEvaluator(cases)
    cfg = condition_cfg(cond)
    if cfg.get("multiagent_enabled"):
        cfg["multiagent"] = dict(cfg["multiagent"])
        if extra_agents:
            cfg["multiagent"]["agents"] = extra_agents
        if timeout_s is not None:
            cfg["multiagent"]["timeout_s"] = timeout_s

    decisions, leak, bypass = [], [0], [0]
    with H.fixed_timer(), H.qwen_mode("down") as qcalls, H.no_backoff():
        o = H.new_orchestrator(f"{k}_{seed}", qs, ev, cfg=cfg)
        if cond.get("ppo") is False:
            o._strategy = None

        orig_adapt = o._adapt_difficulty

        async def adapt(score):
            before = int(o._state["current_difficulty"])
            r = await orig_adapt(score)
            decisions.append({"before": before, "action": r[2], "raw_rl": o._state.get("raw_rl_action"), "source": o._state.get("last_decision_source"),
                              "guardrail": o._state.get("guardrail_applied"), "level": int(o._state["current_difficulty"])})
            return r
        o._adapt_difficulty = adapt

        if o._ma is not None:
            coord = o._ma.coordinator
            orig_dd, orig_cp = coord.decide_difficulty, coord.coaching_plan

            def dd(obs, base_action, base_source, strategy, guardrail_fn):
                dec = orig_dd(obs, base_action, base_source, strategy, guardrail_fn)
                saved = o._last_guardrail_name
                st = o._state
                hist = st.get("rl_perf_history", [])
                avg = sum(hist) / max(len(hist), 1)
                conf = float(st.get("last_confidence_score", 0.5))
                idx = o._apply_guardrails(_IDX[dec.final_action], obs.score, avg, conf, max(0.0, 1.0 - conf),
                                          int(st["current_difficulty"]) / 5.0)
                o._last_guardrail_name = saved
                if idx != _IDX[dec.final_action]:
                    bypass[0] += 1          # the final action is one the guardrail layer would have overridden
                return dec
            coord.decide_difficulty = dd

            async def cp(obs, strategy):
                plan = await orig_cp(obs, strategy)
                if plan is not None and ungrounded_concepts(plan, obs):
                    leak[0] += 1            # an accepted plan emphasises a concept absent from the evaluator evidence
                return plan
            coord.coaching_plan = cp

        lat, turns, followups, completed = [], 0, 0, False
        t_session = time.perf_counter()
        t0 = time.perf_counter()
        res = await o.start()
        lat.append((time.perf_counter() - t0) * 1000)
        root = {}
        for _ in range(60):
            if isinstance(res, dict) and res.get("type") == "session_end":
                completed = True
                break
            q = H._payload(res)
            qid, parent = q["id"], q.get("parent_question_id")
            if parent:
                root[qid] = root.get(parent, parent)
                followups += 1
            text = answers.get(qid) or answers.get(root.get(qid)) or "unrecorded"
            t0 = time.perf_counter()
            r = await o.handle_voice_answer(text, qid)
            lat.append((time.perf_counter() - t0) * 1000)
            turns += 1
            if r.get("next_action") == "retry_answer":
                break
            t0 = time.perf_counter()
            res = await o.handle_next_question()
            lat.append((time.perf_counter() - t0) * 1000)
        total_ms = (time.perf_counter() - t_session) * 1000

    st = o._state
    hist = [int(x) for x in st.get("difficulty_history", [])]
    deltas = [b - a for a, b in zip(hist, hist[1:])]
    nz = [d for d in deltas if d != 0]
    reversals = sum(1 for a, b in zip(nz, nz[1:]) if (a > 0) != (b > 0))
    authority_ok = all(abs(a["raw_score"] - recorded.get(a["transcript"], -9)) < 1e-9 for a in st.get("answers", []))
    # levels stay in [1,5] everywhere; the +-1 step bound is checked on RL-phase decisions only (the original baseline-phase
    # schedule legitimately moves by more than one level, see protocol deviation note D1)
    rl = [d for d in decisions if d["raw_rl"] is not None or (d["source"] not in (None, "baseline_warmup")
                                                              and d["action"] not in ("Baseline", "Baseline->RL", "Pending"))]
    transition_ok = all(1 <= x <= 5 for x in hist) and all(abs(d["level"] - d["before"]) <= 1 for d in rl)
    agree = [d["action"] == d["raw_rl"] for d in rl if d["raw_rl"] is not None]
    row = {
        "condition": name, "k": k, "seed": seed, "completed": completed, "turns": turns, "followups": followups,
        "authority_ok": authority_ok, "transition_ok": transition_ok, "final_level": hist[-1] if hist else None,
        "level_changes": len(nz), "reversals": reversals, "rl_decisions": len(rl),
        "ppo_agree": (sum(agree) / len(agree)) if agree else None,
        "guardrail_fires": sum(1 for d in rl if d["guardrail"]), "strategy_source": sum(1 for d in rl if d["source"] == "strategy_agent"),
        "guardrail_bypass": bypass[0], "ungrounded_leak": leak[0],
        "qwen_attempts": qcalls["n"], "total_ms": total_ms, "turn_ms": lat,
        "diff_path": hist, "score_path": [round(float(x), 6) for x in st.get("scores", [])],
        "q_path": ["fu" if str(q).startswith("fu_") else q for q in st.get("question_history", [])],
        "ma": None,
    }
    if o._ma is not None:
        recs = o._ma.coordinator.records
        calls = o._ma.coordinator.call_counts
        ac = [r for r in recs if r.decision == "agent_call"]
        reasons = {}
        for r in ac:
            reasons[f"{r.proposer}:{r.reason_code}"] = reasons.get(f"{r.proposer}:{r.reason_code}", 0) + 1
        row["ma"] = {
            "strategy_calls": calls["strategy"], "coaching_calls": calls["coaching"], "agent_call_records": len(ac),
            "agent_valid": sum(1 for r in ac if r.reason_code == "valid"), "reasons": reasons,
            "conflicts": sum(1 for r in recs if r.reason_code == "superseded_by_strategy"),
            "coaching_plans": sum(1 for r in recs if r.decision == "coaching" and r.status == "accepted"),
            "coaching_rejected": sum(1 for r in recs if r.decision == "coaching" and r.status == "rejected"),
            "probe_strategy": sum(1 for r in recs if r.decision == "probe" and r.proposer == "strategy" and r.status != "rejected"),
            "version": o._ma.version, "commits": len(st.get("scores", [])),
        }
    return row


def write_once(path: Path, text: str):
    path = Path(path)
    if path.exists():
        raise SystemExit(f"write-once: {path} exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
