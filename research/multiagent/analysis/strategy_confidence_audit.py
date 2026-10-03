"""Post hoc audit (not part of any registered protocol): distribution of Strategy Agent proposal mode x confidence in the full multi-agent
configuration (M1) over the same 160 replay sessions as XA. Deterministic re-run of M1; no new experimental condition.
Usage: EVALUATOR_MOCK_MODE=1 python strategy_confidence_audit.py OUT.json"""
import asyncio, collections, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "experiments"))
import ma_common as C  # noqa: E402
from agents.multiagent import coordinator as co  # noqa: E402

cnt = collections.Counter()
orig = co.AgentCoordinator._message


def patched(self, obs, sender, recipient, kind, payload, confidence=None):
    if kind == "proposal" and sender == "strategy":
        cnt[f"{payload.get('mode')}|{round(confidence, 2):.2f}"] += 1
    return orig(self, obs, sender, recipient, kind, payload, confidence)


co.AgentCoordinator._message = patched


async def main():
    with C.H.shared_ppo():
        for k in range(8):
            for seed in range(20):
                await C.run_one("M1", {"multiagent": {"timeout_s": 2.0, "tau": 0.6}}, k, seed)

asyncio.run(main())
out = {"sessions": 160, "proposals": sum(cnt.values()), "mode|confidence": dict(sorted(cnt.items())), "git": C.git_state()}
Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
Path(sys.argv[1]).write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=1))
