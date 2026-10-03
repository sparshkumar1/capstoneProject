"""XB: agent-level fault injection x ablated safeguards on replay sessions (protocol MA-XA-XB v1).

Faults are injected into the agent's output at a seeded rate (or always, for 'adversarial_valid' and 'ungrounded', which are
schema-valid but harmful proposals). The real StrategyAgent / CoachingAgent run on every non-faulted turn.
"""
import argparse
import asyncio
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ma_common as C  # noqa: E402
from agents.multiagent.coaching_agent import CoachingAgent  # noqa: E402
from agents.multiagent.contracts import CoachingPlan, Evidence, StrategyProposal  # noqa: E402
from agents.multiagent.strategy_agent import StrategyAgent  # noqa: E402

CFG = Path(__file__).parents[1] / "configs/ma_xa_xb_v1.json"


class FaultyAgent:
    def __init__(self, inner, target, kind, rate, seed, sleep_s):
        self.inner, self.target, self.kind, self.rate, self.sleep_s = inner, target, kind, rate, sleep_s
        self.rng = random.Random(seed)
        self.injected = 0

    def export_state(self):
        return self.inner.export_state()

    def propose(self, obs, peer=None):
        always = self.kind in ("adversarial_valid", "ungrounded")
        hit = always or self.rng.random() < self.rate
        if not hit:
            return self.inner.propose(obs, peer=peer)
        self.injected += 1
        k = self.kind
        if k == "crash":
            raise RuntimeError("injected crash")
        if k == "timeout":
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
            action = "Harder" if obs.score < 0.5 else "Easier"          # always the opposite of what the evidence suggests
            return StrategyProposal(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version,
                                    difficulty_action=action, confidence=0.95, mode="stretch", evidence=(Evidence(ref="score"),))
        if k == "ungrounded":
            return CoachingPlan(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version,
                                emphasize=("quantum entanglement",), confidence=0.9, evidence=(Evidence(ref="score"),))
        raise ValueError(k)


async def main(out: Path, seeds: int, faults_filter=None):
    cfg = C.load_config(CFG)
    gs = C.git_state()      # captured before any result file exists
    xb = cfg["xb"]
    rows = []
    with C.H.shared_ppo():
        for target, kinds in xb["faults"].items():
            for kind in kinds:
                if faults_filter and f"{target}:{kind}" not in faults_filter:
                    continue
                for vname, v in xb["variants"].items():
                    cond = {"multiagent": {**v, "timeout_s": xb["timeout_s"], "tau": xb["agent_thresholds"]["tau"]}}
                    for k in range(cfg["recorded_sessions"]):
                        for seed in range(seeds):
                            inner_s, inner_c = StrategyAgent(), CoachingAgent()
                            fa = FaultyAgent(inner_s if target == "strategy" else inner_c, target, kind, xb["fault_rate"],
                                             seed=31 * k + seed, sleep_s=xb["timeout_s"] * 3)
                            agents = {target: fa}
                            if target == "strategy":
                                agents["coaching"] = inner_c
                            else:
                                agents["strategy"] = inner_s
                            row = await C.run_one(f"{target}:{kind}|{vname}", cond, k, seed, extra_agents=agents)
                            row.update({"target": target, "fault": kind, "variant": vname, "injected": fa.injected})
                            rows.append(row)
                print(f"{target}:{kind} done ({len(rows)} runs)", flush=True)
    meta = {"protocol": "MA-XA-XB-v1", "config_sha256": C.sha256_file(CFG), "git": gs, "seeds": seeds}
    C.write_once(out / "xb_runs.jsonl", "\n".join(json.dumps(r, sort_keys=True, default=str) for r in rows) + "\n")
    C.write_once(out / "xb_meta.json", json.dumps(meta, indent=2, sort_keys=True))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--only", default=None, help="comma list of target:fault")
    a = ap.parse_args()
    seeds = a.seeds if a.seeds is not None else C.load_config(CFG)["xb"]["order_seeds"]
    asyncio.run(main(Path(a.out), seeds, a.only.split(",") if a.only else None))
