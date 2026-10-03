"""E1 — mechanism ablation under injected faults (protocol ADCOM-E1..E3 v1, section 1-5).  REPLAY class."""
import asyncio, json, platform, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import harness as H

import os
OUT = Path(os.environ.get("ADCOM_RESULTS") or Path(__file__).parents[1] / "results")
CELLS = []   # (fault, variant, seeds)
for v in ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7"]:
    CELLS.append(("F0", v, [0]))
CELLS += [("F1", "V0", [0]), ("F1", "V6", [0]),
          ("F2", "V0", list(range(20))), ("F2", "V6", list(range(20))),
          ("F3", "V0", list(range(20))), ("F3", "V1", list(range(20))),
          ("F4", "V0", [0]), ("F4", "V1", [0]),
          ("F5", "V0", [0]), ("F5", "V7", [0])]


def longest_run(flags):
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def invariants(o, ev, run, fault):
    st = o._state
    ans = st.get("answers", [])
    ok_by_q = {}
    for qid, ok, _ in ev.log:
        ok_by_q[qid] = ok_by_q.get(qid, False) or ok
    committed = [t for t in run["turns"] if t.get("committed")]
    i1 = sum(1 for a in ans if not ok_by_q.get(a["question_id"], False))
    arrs = list(st.get("scores", [])) + list(st.get("raw_scores", []))
    i2 = sum(1 for v in arrs if not H.valid_score(v))
    i3 = sum(1 for a in ans if a["question_id"] in ev.f4_qids and float(a["score"]) > 0.65 + 1e-9) if fault == "F4" else None
    i4 = bool(run["ended"]) and not run["retry_exhausted"]
    i5 = longest_run([t["is_followup"] for t in committed])
    n_dist = len({t["qid"] for t in committed})
    i6 = not (len(st.get("scores", [])) == len(st.get("raw_scores", [])) == len(ans) == n_dist)
    i7_den = sum(1 for t in committed if t["rl_phase"] and isinstance(t["score"], (int, float)) and t["score"] < 0.30)
    i7 = sum(1 for t in committed if t["rl_phase"] and isinstance(t["score"], (int, float)) and t["score"] < 0.30
             and t["d_after"] > t["d_before"])
    src = {}
    for t in committed:
        if t["rl_phase"]:
            src[t["decision_source"]] = src.get(t["decision_source"], 0) + 1
    return {"I1_committed_without_valid_eval": i1, "I2_invalid_stored_numbers": i2, "I3_mandatory_violations": i3,
            "I4_terminated": i4, "I5_max_followup_run": i5, "I6_state_inconsistent": i6,
            "I7_up_after_low": i7, "I7_low_turns": i7_den, "n_turns": len(committed), "n_followups": sum(t["is_followup"] for t in committed),
            "n_scores": len(st.get("scores", [])), "decision_sources_rl_phase": src,
            "difficulty_path": [t["d_after"] for t in committed], "score_path": [t["score"] for t in committed],
            "followup_flags": [bool(t["is_followup"]) for t in committed],
            "decision_path": [t["decision_source"] for t in committed]}


async def one(fault, vid, seed, k, by_q, qs):
    questions, answers, cases = H.session_plan(k, by_q, qs)
    ev = H.FaultyEvaluator(cases, fault, seed)
    o = H.new_orchestrator(k, questions, ev)
    H.apply_variant(o, vid)
    with H.fixed_timer(), H.qwen_mode("down"), H.no_backoff():
        run = await H.drive2(o, answers, retry_once=(fault == "F5"))
    rec = {"fault": fault, "variant": vid, "seed": seed, "session": k}
    rec.update(invariants(o, ev, run, fault))
    return rec


async def main():
    if os.environ.get("ADCOM_SMOKE"):
        CELLS[:] = [(f, v, s[:1]) for f, v, s in CELLS]
    out = OUT / "e1_runs.jsonl"
    if out.exists():
        sys.exit("write-once: e1_runs.jsonl exists")
    by_q, qs = H.load_cases(), H.load_questions()
    t0 = time.time(); n = 0
    with H.shared_ppo(), open(out, "w") as f:
        for fault, vid, seeds in CELLS:
            for seed in seeds:
                for k in range(8):
                    rec = await one(fault, vid, seed, k, by_q, qs)
                    f.write(json.dumps(rec, sort_keys=True) + "\n"); n += 1
            print(f"{fault} {vid} done  ({n} sessions, {time.time()-t0:.0f}s)", flush=True)
    meta = {"n_sessions": n, "python": platform.python_version(), "cells": [(a, b, len(c)) for a, b, c in CELLS]}
    (OUT / "e1_meta.json").write_text(json.dumps(meta, indent=1))

if __name__ == "__main__":
    asyncio.run(main())
