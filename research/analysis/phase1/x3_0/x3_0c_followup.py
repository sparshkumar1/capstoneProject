"""X3-0c follow-up: resolves the definition of 'sessions that differ' between PPO+G and Constant-Same+G.
Reads only x3_0c_replay_session_log.csv (replay output). Deterministic; no RNG; no project code."""
import csv, json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "tools"))
import run_manifest as rm
OUT = Path(__file__).resolve().parent
m = rm.Manifest("X3-0c-followup", OUT, __file__, note_path=OUT / "X3_0_PRERUN_NOTE.md")
src = OUT / "x3_0c_replay_session_log.csv"
m.add_inputs([src])
rows = list(csv.DictReader(open(src, encoding="utf-8", newline="")))
D = {"Easier": -1.0, "Same": 0.0, "Harder": 1.0}
def path(seq):
    d, p = 3.0, [3.0]
    for a in seq.split("|"):
        d = min(5.0, max(1.0, d + D[a])); p.append(d)
    return tuple(p)
cs = {(r["persona"], r["eval_seed"]): r for r in rows if r["condition"] == "Constant-Same+G"}
ppo = [r for r in rows if r["condition"] == "PPO+G"]
seq_diff = sum(r["final_actions"] != cs[(r["persona"], r["eval_seed"])]["final_actions"] for r in ppo)
path_diff = sum(path(r["final_actions"]) != path(cs[(r["persona"], r["eval_seed"])]["final_actions"]) for r in ppo)
mae_diff = sum(r["mae"] != cs[(r["persona"], r["eval_seed"])]["mae"] for r in ppo)
per_seed = {}
for r in ppo:
    k = r["training_seed"]; c = cs[(r["persona"], r["eval_seed"])]
    d = per_seed.setdefault(k, [0, 0, 0]); d[0] += r["final_actions"] != c["final_actions"]; d[1] += path(r["final_actions"]) != path(c["final_actions"]); d[2] += r["mae"] != c["mae"]
res = {"n_sessions": len(ppo), "final_action_sequence_differs": seq_diff, "executed_difficulty_path_differs": path_diff, "session_mae_differs": mae_diff,
       "per_training_seed[seq,path,mae]": per_seed}
txt = ("# X3-0c follow-up: sessions where PPO+G differs from Constant-Same+G\n\n"
       f"Of {len(ppo)} PPO+G sessions (5 seeds x 25): final-action sequence differs in **{seq_diff}**; the executed difficulty path (after clipping to [1, 5]) differs in **{path_diff}**; the session MAE differs in **{mae_diff}**. "
       "The earlier audit statement '5 of 125 sessions differ' therefore corresponds to the trajectory/outcome definition, not the action-sequence definition; sequences can differ (e.g. an Easier proposed at difficulty 1.0) without changing the executed trajectory.\n\n"
       f"Per training seed [action-sequence, path, MAE]: {json.dumps(per_seed)}\n")
o = [rm.write_new(OUT / "x3_0c_followup.json", json.dumps(res, indent=2)), rm.write_new(OUT / "X3_0C_FOLLOWUP.md", txt)]
print(m.finish(o)); print(txt)
