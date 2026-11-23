"""E4 — before/after of the strict evaluator->hub contract (protocol amendment A2). REPLAY class."""
import asyncio, json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import harness as H
from e1_ablation_faults import invariants

OUT = Path(os.environ.get("ADCOM_RESULTS") or Path(__file__).parents[1] / "results")
TYPES = {"None": None, "NaN": float("nan"), "high": "high", "1.7": 1.7, "-0.3": -0.3}


class Ev(H.FaultyEvaluator):
    def __init__(self, cases, kind, seed=0):
        super().__init__(cases, "F0", seed)
        self.k2 = kind

    def __call__(self, transcript, question):
        k = self.k2
        if k.startswith("F3each:"):
            self.calls += 1; qid = question["id"]
            p = json.loads(json.dumps(self.by_text[transcript], default=str)); import copy
            p = copy.deepcopy(self.by_text[transcript]); p["final_score"] = TYPES[k.split(":")[1]]
            self.log.append((qid, H.valid_score(p["final_score"]), "F3")); return p
        if k == "F6":
            self.calls += 1; qid = question["id"]; import copy
            p = copy.deepcopy(self.by_text[transcript])
            if self.rng.random() < 0.10:
                p["final_score"] = list(TYPES.values())[int(self.rng.integers(5))]
            self.log.append((qid, H.valid_score(p["final_score"]), "F6")); return p
        self.kind = k if k in ("F0", "F2") else "F0"
        return super().__call__(transcript, question)


CELLS = [("F0", [0])] + [(f"F3each:{t}", [0]) for t in TYPES] + [("F2", list(range(20))), ("F6", list(range(20)))]


async def one(kind, strict, seed, k, by_q, qs):
    questions, answers, cases = H.session_plan(k, by_q, qs)
    ev = Ev(cases, kind, seed)
    o = H.new_orchestrator(k, questions, ev, cfg={"strict_evaluator_contract": strict})
    with H.fixed_timer(), H.qwen_mode("down"), H.no_backoff():
        run = await H.drive2(o, answers)
    rec = {"cell": kind, "strict": strict, "seed": seed, "session": k}
    rec.update(invariants(o, ev, run, "F0"))
    committed_scores = list(o._state.get("scores", []))
    rec["committed_scores"] = committed_scores
    return rec


async def main():
    if os.environ.get("ADCOM_SMOKE"):
        CELLS[:] = [(c, sd[:1]) for c, sd in CELLS]
    out = OUT / "e4_runs.jsonl"
    if out.exists():
        sys.exit("write-once")
    by_q, qs = H.load_cases(), H.load_questions()
    with H.shared_ppo(), open(out, "w") as f:
        for kind, seeds in CELLS:
            for strict in (False, True):
                for seed in seeds:
                    for k in range(8):
                        f.write(json.dumps(await one(kind, strict, seed, k, by_q, qs), sort_keys=True) + "\n")
            print(kind, "done", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
