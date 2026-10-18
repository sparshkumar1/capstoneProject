"""O2/O3/O4 oracles of protocol MA-MUT v2 (coordinator-level). Prints one JSON line prefixed 'JSON_RESULT '.
Usage: python oracle_coordinator.py REPO_EXPORT
"""
import asyncio
import hashlib
import json
import random
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "research/multiagent/experiments"))

from agents.multiagent.coaching_agent import CoachingAgent  # noqa: E402
from agents.multiagent.coaching_render import PROTECTED_KEYS, apply_coaching_plan  # noqa: E402
from agents.multiagent.contracts import CoachingPlan, Evidence, StrategyProposal, TurnObservation  # noqa: E402
from agents.multiagent.coordinator import AgentCoordinator  # noqa: E402
from agents.multiagent.strategy_agent import StrategyAgent  # noqa: E402
from rl.guardrails import apply_canonical_guardrails  # noqa: E402

TAU, TIMEOUT, RATE = 0.6, 0.15, 0.3
ACT = {0: "Easier", 1: "Same", 2: "Harder"}
IDX = {v: k for k, v in ACT.items()}
FAULTS = [("strategy", k) for k in ["crash", "timeout", "malformed", "forbidden_key", "stale", "nan_confidence", "adversarial_valid"]] \
    + [("coaching", k) for k in ["crash", "malformed", "stale", "ungrounded"]]
STRUCTURAL = {"crash", "timeout", "malformed", "forbidden_key", "stale", "nan_confidence"}


def norm(s):  # independent re-implementation (oracle must not import the code under test)
    return " ".join(str(s).lower().split())


class Faulty:
    """Same fault semantics as research/multiagent/experiments/xb_faults.py::FaultyAgent."""

    def __init__(self, inner, target, kind, rate, seed, sleep_s):
        self.inner, self.target, self.kind, self.rate, self.sleep_s = inner, target, kind, rate, sleep_s
        self.rng = random.Random(seed)
        self.injected = 0

    def export_state(self):
        return self.inner.export_state()

    def propose(self, obs, peer=None):
        always = self.kind in ("adversarial_valid", "ungrounded")
        if not (always or self.rng.random() < self.rate):
            return self.inner.propose(obs, peer=peer)
        self.injected += 1
        k = self.kind
        if k == "crash":
            raise RuntimeError("injected crash")
        if k == "timeout":
            import time
            time.sleep(self.sleep_s)
            return self.inner.propose(obs, peer=peer)
        if k == "malformed":
            return {"difficulty_action": "Sideways"} if self.target == "strategy" else {"depth": "extreme"}
        if k == "forbidden_key":
            return {"difficulty_action": "Harder", "confidence": 0.99, "final_score": 1.0}
        if k == "nan_confidence":
            return {"session_id": obs.session_id, "turn_id": obs.turn_id, "state_version": obs.state_version,
                    "difficulty_action": "Harder", "confidence": float("nan")}
        if k == "stale":
            if self.target == "strategy":
                return StrategyProposal(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version + 3,
                                        difficulty_action="Harder", confidence=0.95, evidence=(Evidence(ref="score"),))
            return CoachingPlan(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version + 3, confidence=0.9)
        if k == "adversarial_valid":
            action = "Harder" if obs.score < 0.5 else "Easier"
            return StrategyProposal(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version,
                                    difficulty_action=action, confidence=0.95, mode="stretch", evidence=(Evidence(ref="score"),))
        if k == "ungrounded":
            return CoachingPlan(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version,
                                emphasize=("quantum entanglement",), confidence=0.9, evidence=(Evidence(ref="score"),))
        raise ValueError(k)


def load_payloads():
    raw = json.load(open(REPO / "research/results/paper2/paper2_evaluator_raw.json"))
    by_q = {}
    for c in raw:
        by_q.setdefault(c["qid"], []).append(c)
    return [[by_q[q][k] for q in sorted(by_q)] for k in range(8)]      # session k: k-th recorded answer of each question


def base_action(score):
    return "Harder" if score >= 0.7 else ("Easier" if score < 0.4 else "Same")


def guard(level, score, hist, consecutive):
    avg = sum(hist) / max(len(hist), 1)

    def fn(cand):
        a, over, gid = apply_canonical_guardrails(score, avg, 0.5, 0.5, 0.5, level, IDX[cand], consecutive)
        return (ACT[a], gid) if over else (cand, None)
    return fn


async def session(sessions, k, level0, scenario, kind_target=None, kind=None, rate=RATE, infra_turn=None, dup_turn=None):
    """Returns (violations:list, records:list[tuple], trajectory:list)."""
    viol, trace = [], []
    sa, ca = StrategyAgent(), CoachingAgent()
    sleep = TIMEOUT * 3
    agents = {"strategy": sa, "coaching": ca}
    fa = None
    if kind is not None:
        fa = Faulty(agents[kind_target], kind_target, kind, rate, 31 * k, sleep)
        agents[kind_target] = fa
    co = AgentCoordinator(agents["strategy"], agents["coaching"], timeout_s=TIMEOUT, tau=TAU)
    level, hist, consec, crash_run = level0, [], 0, 0
    for t, case in enumerate(sessions[k]):
        ev = case["raw_eval"]
        score = float(case["final_score"])
        hist.append(score)
        obs = TurnObservation(
            session_id=f"s{k}", turn_id=t, state_version=t, question_id=str(case["qid"]), difficulty=level, score=score,
            covered_concepts=tuple(ev.get("correct_claims", [])), missing_concepts=tuple(ev.get("missing_concepts", [])),
            incorrect_claims=tuple(ev.get("incorrect_claims", [])), scores_history=tuple(hist),
            progress=t / 8.0, consecutive_followups=consec, ppo_action=base_action(score), ppo_available=True,
            infrastructure_failure=(infra_turn == t))
        co.committed(t)
        before = fa.injected if fa else 0
        n_rec = len(co.records)
        strat = await co.strategy_proposal(obs)
        if dup_turn == t:
            again = await co.strategy_proposal(obs)
            if again is not None:
                viol.append("P7_duplicate_accepted")
        fired = (fa.injected - before) if (fa and kind_target == "strategy") else 0
        if strat is not None and fired and kind in STRUCTURAL:
            viol.append("P2_structural_fault_accepted:strategy")
        if kind == "crash" and rate >= 1.0 and kind_target == "strategy":
            last = [r for r in co.records[n_rec:] if r.decision == "agent_call"]
            if crash_run >= 2 and not any(r.reason_code == "breaker_open" for r in last):
                viol.append("P8_breaker_not_open")
            crash_run += 1
        before = fa.injected if fa else 0
        plan = await co.coaching_plan(obs, strat)
        fired_c = (fa.injected - before) if (fa and kind_target == "coaching") else 0
        if plan is not None and fired_c and kind in STRUCTURAL:
            viol.append("P2_structural_fault_accepted:coaching")
        if plan is not None:
            evid = {norm(c) for c in (*obs.covered_concepts, *obs.missing_concepts, *obs.incorrect_claims)}
            if any(norm(c) not in evid for c in plan.emphasize):
                viol.append("P4_ungrounded_plan_accepted")
            fb = {k2: f"orig_{k2}" for k2 in PROTECTED_KEYS}
            fb["actionable_improvements"] = ["x"]
            snap = dict(fb)
            apply_coaching_plan(fb, plan, "t")
            if any(fb[k2] != snap[k2] for k2 in PROTECTED_KEYS):
                viol.append("P10_protected_field_changed")
        gfn = guard(level, score, hist, consec)
        dec = co.decide_difficulty(obs, obs.ppo_action, "ppo", strat, gfn)
        if gfn(dec.final_action)[0] != dec.final_action:
            viol.append("P3_guardrail_bypass")
        if not (1 <= dec.new_level <= 5) or abs(dec.new_level - level) > 1:
            viol.append("P1_level_bounds")
        if obs.infrastructure_failure and dec.final_action != "Same":
            viol.append("P6_infra_not_same")
        pd = co.decide_probe(obs, score < 0.5, strat)
        if pd.inject and consec >= 2:
            viol.append("P5_followup_cap")
        consec = consec + 1 if pd.inject else 0
        trace.append((level, dec.final_action, dec.new_level, bool(pd.inject)))
        level = dec.new_level
    recs = sorted((r.decision, r.proposer, r.status, r.reason_code) for r in co.records)
    return viol, recs, trace


async def main():
    sessions = load_payloads()
    out = {"o2": {}, "o3": {}, "o4": {}}
    scen = [("nominal", None, None, 0.0)] + [(f"{t}:{k}", t, k, RATE) for t, k in FAULTS] + [("strategy:crash_always", "strategy", "crash", 1.0)]
    nominal_digest = hashlib.sha256()
    for name, tgt, kind, rate in scen:
        viol_n, errs, reasons, byp = 0, 0, {}, {}
        for k in range(8):
            for level0 in (1, 3, 5):
                extra = {}
                if name == "nominal":
                    extra = {"infra_turn": 3 if level0 == 3 else None, "dup_turn": 2 if level0 == 1 else None}
                try:
                    v, recs, trace = await session(sessions, k, level0, name, tgt, kind, rate, **extra)
                except Exception as e:  # coordinator raising on agent output is itself a violation (P9)
                    errs += 1
                    continue
                viol_n += len(v)
                for x in v:
                    byp[x] = byp.get(x, 0) + 1
                for r in recs:
                    key = "|".join(r)
                    reasons[key] = reasons.get(key, 0) + 1
                if name == "nominal":
                    nominal_digest.update(json.dumps([trace, recs], sort_keys=True).encode())
        out["o2"][name] = {"violations": viol_n, "harness_errors": errs, "by_property": byp}
        out["o3"][name] = dict(sorted(reasons.items()))
    out["o4"]["nominal_digest"] = nominal_digest.hexdigest()
    print("JSON_RESULT " + json.dumps(out, sort_keys=True))


asyncio.run(main())
