"""X3-0c - evaluation-only replay of the frozen Paper 3 checkpoints (Phase 1C).

Runs in the separately built environment envs/replay-Lobs (NOT the project .venv):
    envs/replay-Lobs/Scripts/python.exe -B research/analysis/phase1/x3_0/x3_0c_replay.py

* imports the frozen module research/scripts/execute_paper3_study.py (main() is never called; no bytecode written);
* the only change to the frozen code path is (a) the environment log file is redirected to this output directory and
  (b) SimulatedCandidate is wrapped by a subclass that RECORDS each answer (it calls the parent unchanged, so no RNG
  stream or value changes); Constant-Same is a stub that replaces PPO.load's model with a constant-action predictor;
* Gate G-REPRO must pass before any G-NEW output is written. If it fails only the gate report is written.
* Definitions: X3_0_PRERUN_NOTE.md. No training, no tuning, no RNG of its own.
"""
import csv
import io
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "tools"))
sys.path.insert(0, str(REPO / "research" / "scripts"))
import run_manifest as rm  # noqa: E402

OUT = Path(__file__).resolve().parent
NOTE = OUT / "X3_0_PRERUN_NOTE.md"
R3 = REPO / "research" / "results" / "paper3"
CK = REPO / "research" / "experiments" / "paper3" / "checkpoints"
TRAIN_SEEDS = [42, 123, 456, 789, 999]
ACT = {0: "Easier", 1: "Same", 2: "Harder"}
INV = {v: k for k, v in ACT.items()}
DELTA = {"Easier": -1.0, "Same": 0.0, "Harder": 1.0}
GATE_BND = [26, 71, 41, 33, 61]
GATE_ACT = [122, 101, 115, 120, 105]


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def wcsv(name, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return rm.write_new(OUT / name, buf.getvalue())


def main():
    m = rm.Manifest("X3-0c", OUT, __file__, note_path=NOTE, seeds={"training_seeds": TRAIN_SEEDS, "eval_seeds": "frozen EVAL_SEEDS 1001..5005",
                    "rng": "none of its own; SimulatedCandidate(seed=eval_seed) as in the frozen code"},
                    non_locked_reason="envs/replay-Lobs built 2026-09-19 from pinned versions matching the probed .venv; wheel hashes not recorded; lock files written in research/locks/",
                    gate={"name": "G-REPRO", "passed": None, "details": "pending"})
    for s in TRAIN_SEEDS:
        m.add_model("ppo_checkpoint", CK / f"seed_{s}" / "ppo_final.zip", s)
        m.add_model("vecnormalize", CK / f"seed_{s}" / "vecnormalize.pkl", s)
    frozen_script = REPO / "research" / "scripts" / "execute_paper3_study.py"
    m.add_inputs([frozen_script, REPO / "rl" / "guardrails.py", REPO / "rl" / "env" / "interview_env.py",
                  REPO / "rl" / "training" / "simulated_candidate.py", R3 / "paper3_seed_results.csv",
                  R3 / "paper3_baseline_results.csv", R3 / "paper3_guardrail_results.csv"])
    import execute_paper3_study as fm  # noqa: E402  (frozen module; imported, main never called)

    Orig_env = fm.AlignedInterviewEnv
    env_log = OUT / "_replay_env_log_unused.csv"
    fm.AlignedInterviewEnv = lambda **kw: Orig_env(log_file=str(env_log), **kw)
    Orig_cand = fm.SimulatedCandidate
    REC = []

    class RecCandidate(Orig_cand):
        def answer_question(self, difficulty, hint_applied=False):
            out = super().answer_question(difficulty, hint_applied=hint_applied)
            REC.append({"difficulty_before": float(difficulty) * 5.0, "perf": float(out["performance_score"]),
                        "conf": float(out["confidence_score"]), "hes": float(out["hesitation"]),
                        "resp_time": float(out["response_time"])})
            return out
    fm.SimulatedCandidate = RecCandidate
    Orig_PPO = fm.PPO

    class ConstModel:
        def __init__(self, a):
            self.a = a

        def predict(self, obs, deterministic=True):
            return np.array([self.a]), None

    def const_ppo(a):
        class FP:
            @staticmethod
            def load(path):
                return ConstModel(a)
        return FP

    personas = list(fm.PERSONA_TARGETS.keys())
    eval_seeds = list(fm.EVAL_SEEDS)
    assert len(personas) == 5 and eval_seeds == [1001, 2002, 3003, 4004, 5005]

    sessions = []   # one dict per session
    turns = []      # one dict per turn

    def run_cond(label, tseed, policy, mdir, guard, stub=None):
        if stub is not None:
            fm.PPO = const_ppo(stub)
        try:
            for p in personas:
                for es in eval_seeds:
                    REC.clear()
                    r = fm.run_session_trajectory(policy, p, "aligned_progress", es, mdir, guard, 10)
                    rec = list(REC)
                    assert len(rec) == 10 and len(r["raw_actions"]) == 10
                    n_over = 0
                    n_raw_oob_state = 0
                    for t in range(10):
                        raw, fin, gid = r["raw_actions"][t], r["final_actions"][t], r["guardrail_ids"][t]
                        d0 = rec[t]["difficulty_before"]
                        fin_oob = (d0 + DELTA[fin] < 1.0) or (d0 + DELTA[fin] > 5.0)
                        raw_oob = (d0 + DELTA[raw] < 1.0) or (d0 + DELTA[raw] > 5.0)
                        n_over += int(raw != fin)
                        n_raw_oob_state += int(raw_oob)
                        turns.append({"condition": label, "training_seed": tseed, "persona": p, "eval_seed": es, "turn": t + 1,
                                      "difficulty_before": round(d0, 3), "perf": round(rec[t]["perf"], 4), "conf": round(rec[t]["conf"], 4),
                                      "hes": round(rec[t]["hes"], 4), "resp_time": round(rec[t]["resp_time"], 3), "raw_action": raw,
                                      "final_action": fin, "guardrail_id": gid, "activation": gid != "none", "override": raw != fin,
                                      "final_action_attempts_boundary": fin_oob, "raw_proposal_attempts_boundary_on_visited_state": raw_oob})
                    sessions.append({"condition": label, "training_seed": tseed, "persona": p, "eval_seed": es,
                                     "mae": r["target_tracking_error"], "volatility": r["volatility"], "oscillation": r["oscillation_rate"],
                                     "final_difficulty": r["final_difficulty"], "activations": r["guardrail_interventions"],
                                     "attempted_boundary_final": r["constraint_violations"], "overrides": n_over,
                                     "raw_proposal_attempts_on_visited_states": n_raw_oob_state,
                                     "final_actions": "|".join(r["final_actions"])})
        finally:
            fm.PPO = Orig_PPO

    run_cond("Fixed", "-", "Fixed", None, False)
    run_cond("Heuristic", "-", "Heuristic", None, False)
    for s in TRAIN_SEEDS:
        run_cond("PPO raw", s, "PPO", CK / f"seed_{s}", False)
        run_cond("PPO+G", s, "PPO", CK / f"seed_{s}", True)
    run_cond("Constant-Same raw", "-", "PPO", CK / "seed_123", False, stub=1)
    run_cond("Constant-Same+G", "-", "PPO", CK / "seed_123", True, stub=1)

    def sel(cond, ts=None):
        return [x for x in sessions if x["condition"] == cond and (ts is None or x["training_seed"] == ts)]

    def mean(rows, k):
        return float(np.mean([x[k] for x in rows]))

    # ------------------------------ G-REPRO gate ------------------------------
    stored_seed = {int(r["training_seed"]): r for r in rd(R3 / "paper3_seed_results.csv")}
    stored_base = {r["condition"]: r for r in rd(R3 / "paper3_baseline_results.csv")}
    gate_rows = []
    ok_all = True

    def chk(name, got, want, tol=0.0):
        nonlocal ok_all
        ok = abs(float(got) - float(want)) <= tol + 1e-12
        ok_all &= ok
        gate_rows.append({"check": name, "replayed": round(float(got), 4), "stored_or_required": want, "tolerance": tol, "match": ok})

    for i, s in enumerate(TRAIN_SEEDS):
        g = sel("PPO+G", s)
        chk(f"seed {s} guarded activations", sum(x["activations"] for x in g), GATE_ACT[i])
        chk(f"seed {s} guarded attempted boundary", sum(x["attempted_boundary_final"] for x in g), GATE_BND[i])
        chk(f"seed {s} guarded MAE vs seed_results", round(mean(g, "mae"), 3), stored_seed[s]["target_tracking_error"], 0.0011)
        chk(f"seed {s} guarded volatility vs seed_results", round(mean(g, "volatility"), 3), stored_seed[s]["volatility"], 0.0011)
        chk(f"seed {s} guarded oscillation vs seed_results", round(mean(g, "oscillation"), 3), stored_seed[s]["oscillation_rate"], 0.0011)
    chk("Fixed MAE vs baseline_results", round(mean(sel("Fixed"), "mae"), 3), stored_base["Fixed"]["target_tracking_error"], 0.0011)
    chk("Heuristic MAE vs baseline_results", round(mean(sel("Heuristic"), "mae"), 3), stored_base["Heuristic"]["target_tracking_error"], 0.0011)
    chk("Heuristic volatility vs baseline_results", round(mean(sel("Heuristic"), "volatility"), 3), stored_base["Heuristic"]["volatility"], 0.0011)
    chk("PPO raw seed 123 MAE vs baseline_results", round(mean(sel("PPO raw", 123), "mae"), 3), stored_base["PPO Raw (Seed 123)"]["target_tracking_error"], 0.0011)
    chk("PPO raw seed 123 attempted boundary vs baseline_results", sum(x["attempted_boundary_final"] for x in sel("PPO raw", 123)), stored_base["PPO Raw (Seed 123)"]["total_constraint_violations"])
    chk("Constant-Same raw MAE equals Fixed MAE", round(mean(sel("Constant-Same raw"), "mae"), 3), round(mean(sel("Fixed"), "mae"), 3), 0.0011)
    # stored seed-123 guardrail rows (persona, eval_seed, rule, raw, final) as a multiset
    stored_rows = Counter((r["persona"], int(r["eval_seed"]), r["guardrail_id"], r["raw_action"], r["final_action"])
                          for r in rd(R3 / "paper3_guardrail_results.csv") if r["condition"] == "PPO+Guardrails (Seed 123)")
    got_rows = Counter((t["persona"], t["eval_seed"], t["guardrail_id"], t["raw_action"], t["final_action"])
                       for t in turns if t["condition"] == "PPO+G" and t["training_seed"] == 123 and t["activation"])
    same_multiset = stored_rows == got_rows
    ok_all &= same_multiset
    gate_rows.append({"check": "seed-123 activation rows (persona, eval_seed, rule, raw, final) equal stored guardrail file as multiset",
                      "replayed": sum(got_rows.values()), "stored_or_required": sum(stored_rows.values()), "tolerance": 0, "match": same_multiset})
    m.set_gate("G-REPRO", bool(ok_all), f"{sum(1 for r in gate_rows if r['match'])}/{len(gate_rows)} checks matched")
    outs = [wcsv("x3_0c_gate_G-REPRO.csv", gate_rows)]
    print("G-REPRO passed:", ok_all, f"({sum(1 for r in gate_rows if r['match'])}/{len(gate_rows)})")

    if not ok_all:
        m.note("G-REPRO FAILED: no G-NEW output written; mismatch preserved in x3_0c_gate_G-REPRO.csv; frozen study untouched", failure=False)
        outs.append(rm.write_new(OUT / "X3_0C_REPORT.md", "# X3-0c report\n\n**Gate G-REPRO FAILED.** No G-NEW value was computed or registered. See `x3_0c_gate_G-REPRO.csv`. The frozen study is untouched; the mismatch is preserved and needs investigation before any replay number is used.\n"))
        print(m.finish(outs, status="completed"))
        return

    # ------------------------------ G-NEW ------------------------------
    rows = []
    def summarise(label, ts, rr):
        return {"condition": label, "training_seed": ts, "sessions": len(rr), "mae": round(mean(rr, "mae"), 4), "mae_sd_over_sessions": round(float(np.std([x["mae"] for x in rr], ddof=1)), 4),
                "volatility": round(mean(rr, "volatility"), 4), "oscillation": round(mean(rr, "oscillation"), 4),
                "rule_activations": sum(x["activations"] for x in rr), "action_overrides": sum(x["overrides"] for x in rr),
                "unchanged_activations": sum(x["activations"] for x in rr) - sum(x["overrides"] for x in rr),
                "attempted_boundary_final_action": sum(x["attempted_boundary_final"] for x in rr),
                "sessions_with_attempted_boundary": sum(1 for x in rr if x["attempted_boundary_final"] > 0),
                "sessions_with_override": sum(1 for x in rr if x["overrides"] > 0)}
    for lab in ("Fixed", "Heuristic", "Constant-Same raw", "Constant-Same+G"):
        rows.append(summarise(lab, "-", sel(lab)))
    for lab in ("PPO raw", "PPO+G"):
        for s in TRAIN_SEEDS:
            rows.append(summarise(lab, s, sel(lab, s)))
        rows.append(summarise(lab, "pooled 5 seeds", sel(lab)))
    pooled = {r["condition"]: r for r in rows if r["training_seed"] == "pooled 5 seeds"}

    # persona-level paired differences (PPO+G minus Constant-Same+G), mean over eval seeds then over training seeds
    pers = []
    cs = {p: float(np.mean([x["mae"] for x in sel("Constant-Same+G") if x["persona"] == p])) for p in personas}
    for p in personas:
        per_seed = {s: float(np.mean([x["mae"] for x in sel("PPO+G", s) if x["persona"] == p])) for s in TRAIN_SEEDS}
        row = {"persona": p, "target": fm.PERSONA_TARGETS[p]["target_difficulty"], "constant_same_G_mae": round(cs[p], 4)}
        for s in TRAIN_SEEDS:
            row[f"ppo_G_mae_seed{s}"] = round(per_seed[s], 4)
        row["ppo_G_mae_mean_over_seeds"] = round(float(np.mean(list(per_seed.values()))), 4)
        row["delta_ppoG_minus_constsameG"] = round(row["ppo_G_mae_mean_over_seeds"] - cs[p], 4)
        pers.append(row)
    deltas = np.array([r["delta_ppoG_minus_constsameG"] for r in pers])
    pers.append({"persona": "MEAN over 5 personas", "delta_ppoG_minus_constsameG": round(float(deltas.mean()), 4)})
    pers.append({"persona": "SD over 5 personas (ddof=1)", "delta_ppoG_minus_constsameG": round(float(deltas.std(ddof=1)), 4)})

    # sessions where PPO+G final-action sequence differs from Constant-Same+G (same persona, eval seed)
    csmap = {(x["persona"], x["eval_seed"]): x["final_actions"] for x in sel("Constant-Same+G")}
    differ = sum(1 for x in sessions if x["condition"] == "PPO+G" and x["final_actions"] != csmap[(x["persona"], x["eval_seed"])])
    tot = sum(1 for x in sessions if x["condition"] == "PPO+G")

    facts = {"pooled_PPO_raw": pooled["PPO raw"], "pooled_PPO_G": pooled["PPO+G"], "constant_same_G": [r for r in rows if r["condition"] == "Constant-Same+G"][0],
             "ppoG_sessions_differing_from_constsameG": [differ, tot],
             "audit_reference_values": {"raw_attempted_boundary_total": 136, "overrides": 99, "unchanged_activations": 464, "sessions_with_override": 41, "of_sessions": 125,
                                        "constant_same_G_mae_approx": 0.673, "ppoG_sessions_differing_from_constsameG": 5},
             "persona_delta_mean": float(deltas.mean()), "persona_delta_sd_ddof1": float(deltas.std(ddof=1))}
    outs += [wcsv("x3_0c_replay_summary.csv", rows), wcsv("x3_0c_persona_paired.csv", pers), wcsv("x3_0c_replay_turn_log.csv", turns),
             wcsv("x3_0c_replay_session_log.csv", sessions), rm.write_new(OUT / "x3_0c_facts.json", json.dumps(facts, indent=2))]
    pr, pg, cg = facts["pooled_PPO_raw"], facts["pooled_PPO_G"], facts["constant_same_G"]
    rep = f"""# X3-0c report - evaluation-only replay of the frozen checkpoints

Environment: `envs/replay-Lobs` (not the project `.venv`); frozen code imported, `main()` never called; manifest `manifest_X3-0c.json`. Evidence label: REPLAY (new derived data; non-locked environment; lock files in `research/locks/`).

**Gate G-REPRO: PASSED** ({sum(1 for r in gate_rows if r['match'])}/{len(gate_rows)} checks; guarded activations 122/101/115/120/105 and attempted-boundary 26/71/41/33/61 reproduced exactly; seed-123 activation rows equal the stored guardrail file as a multiset). Details: `x3_0c_gate_G-REPRO.csv`.

G-NEW values (replay; reference values from the earlier audit replay shown for comparison, not as targets):
| Quantity | Replay | Audit value |
|---|---|---|
| Raw PPO attempted boundary actions, 5 seeds (guardrails off) | {pr['attempted_boundary_final_action']} | 136 |
| Guarded attempted boundary actions, 5 seeds | {pg['attempted_boundary_final_action']} | 232 |
| Rule activations, 5 seeds | {pg['rule_activations']} | 563 |
| Action overrides (raw != final) | {pg['action_overrides']} | 99 |
| Unchanged activations | {pg['unchanged_activations']} | 464 |
| Sessions with >= 1 override | {pg['sessions_with_override']} of {pg['sessions']} | 41 of 125 |
| Constant-Same + G MAE (25 sessions) | {cg['mae']} | about 0.673 |
| PPO + G MAE, pooled | {pg['mae']} | 0.677 |
| PPO raw MAE, pooled | {pr['mae']} | 0.958 |
| PPO+G sessions whose final-action sequence differs from Constant-Same+G | {differ} of {tot} | 5 of 125 |

Persona-level paired difference PPO+G minus Constant-Same+G (mean over training seeds): mean {facts['persona_delta_mean']:.4f}, SD over the 5 personas (ddof=1) {facts['persona_delta_sd_ddof1']:.4f} (`x3_0c_persona_paired.csv`; input to the X3-A precision rationale only; n = 5 frozen personas, the checkpoints were trained on one candidate, see X3-0b).

Scope: replay of frozen code on the five frozen personas and evaluation seeds; simulation only; no learner claim; no parameter of X3-A/B is set from these values (pre-run note, non-leakage statements).
"""
    outs.append(rm.write_new(OUT / "X3_0C_REPORT.md", rep))
    st = m.finish(outs)
    print(st, m.d["failures"], m.d["deviations"])
    print(rep)


if __name__ == "__main__":
    main()
