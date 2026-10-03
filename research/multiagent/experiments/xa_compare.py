"""XA: single-controller baseline vs multi-agent configurations vs ablations on identical replay sessions (protocol MA-XA-XB v1).

Usage: python research/multiagent/experiments/xa_compare.py [--out DIR] [--seeds N] [--smoke]
Interleaves conditions within each (session, order seed) in a seeded random order (latency drift control).
Results are write-once JSONL; --smoke writes to the given --out only and is never used for reporting.
"""
import argparse
import asyncio
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ma_common as C  # noqa: E402

CFG = Path(__file__).parents[1] / "configs/ma_xa_xb_v1.json"


async def main(out: Path, seeds: int, only=None):
    cfg = C.load_config(CFG)
    gs = C.git_state()      # captured before any result file exists
    conds = {n: c for n, c in cfg["xa"]["conditions"].items() if (only is None or n in only)}
    rows = []
    with C.H.shared_ppo():
        for k in range(cfg["recorded_sessions"]):
            for seed in range(seeds):
                order = list(conds)
                random.Random(7919 * k + seed).shuffle(order)
                for name in order:
                    c = dict(conds[name])
                    if c.get("multiagent") is not None:
                        c["multiagent"] = {**c["multiagent"], "timeout_s": cfg["xa"]["timeout_s"], "tau": cfg["xb"]["agent_thresholds"]["tau"]}
                    rows.append(await C.run_one(name, c, k, seed))
            print(f"session {k} done ({len(rows)} runs)", flush=True)
    meta = {"protocol": "MA-XA-XB-v1", "config_sha256": C.sha256_file(CFG), "git": gs, "seeds": seeds,
            "conditions": list(conds)}
    C.write_once(out / "xa_runs.jsonl", "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
    C.write_once(out / "xa_meta.json", json.dumps(meta, indent=2, sort_keys=True))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    seeds = a.seeds if a.seeds is not None else C.load_config(CFG)["xa"]["order_seeds"]
    if a.smoke and a.seeds is None:
        seeds = 1
    asyncio.run(main(Path(a.out), seeds, a.only.split(",") if a.only else None))
