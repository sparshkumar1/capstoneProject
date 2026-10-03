"""XC: threshold decomposition/sensitivity on identical replay sessions (protocol MA-XC v1). Results are write-once."""
import argparse, asyncio, json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ma_common as C  # noqa: E402

CFG = Path(__file__).parents[1] / "configs/ma_xc_v1.json"


async def main(out: Path):
    cfg = C.load_config(CFG)
    gs = C.git_state()
    rows = []
    with C.H.shared_ppo():
        for k in range(cfg["recorded_sessions"]):
            for seed in range(cfg["order_seeds"]):
                order = list(cfg["taus"])
                random.Random(104729 * k + seed).shuffle(order)
                for name in order:
                    cond = {"multiagent": {"timeout_s": cfg["timeout_s"], "tau": cfg["taus"][name]}}
                    rows.append(await C.run_one(name, cond, k, seed))
            print(f"session {k} done ({len(rows)} runs)", flush=True)
    meta = {"protocol": "MA-XC-v1", "config_sha256": C.sha256_file(CFG), "git": gs, "conditions": list(cfg["taus"])}
    C.write_once(out / "xc_runs.jsonl", "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
    C.write_once(out / "xc_meta.json", json.dumps(meta, indent=2, sort_keys=True))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    asyncio.run(main(Path(ap.parse_args().out)))
