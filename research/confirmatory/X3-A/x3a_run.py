"""X3-A runner. Modes:
  --dry-run        gate G-HARNESS (incl. mutation controls) + pipeline test on the 5 frozen personas (non-confirmatory fixture);
                   writes to research/confirmatory/X3-A/dryrun/ (never to results/).
  --confirmatory   preflight (protocol tag + hashes + lock verification + G-HARNESS) then the full run into research/confirmatory/X3-A/results/.
Run inside envs/LOCK-X3-2026-09-19:  envs/LOCK-X3-2026-09-19/Scripts/python.exe -B research/confirmatory/X3-A/x3a_run.py --confirmatory
"""
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "research" / "tools"))
sys.path.insert(0, str(HERE))
import run_manifest as rm  # noqa: E402
import x3a_lib as L  # noqa: E402

CFG_PATH = HERE / "x3a_config.json"
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
PREREG = REPO / "research" / "preregistration" / "X3-A"
CK = REPO / "research" / "experiments" / "paper3" / "checkpoints"
LABEL = {"const_same": "Constant-Same", "random": "Random", "heuristic": "Heuristic", "oracle": "Oracle-rule", "controller": "Controller", "ppo": "PPO"}


def sh(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def sha(p):
    return rm.sha256_file(p)


# ---------------------------------------------------------------- preflight
def verify_lock():
    lock = json.loads((REPO / CFG["lock_files"]["lock_json"]).read_text(encoding="utf-8"))
    req = (REPO / CFG["lock_files"]["requirements"]).read_text(encoding="utf-8")
    assert sha(REPO / CFG["lock_files"]["requirements"]) == lock["requirements_sha256"], "requirements file changed"
    import importlib.metadata as md
    norm = lambda n: re.sub(r"[-_.]+", "-", n).lower()
    have = {norm(d.metadata["Name"]): d.version for d in md.distributions()}
    bad = []
    for m in re.finditer(r"^([A-Za-z0-9_.\-]+)==([^\s\\]+)", req, flags=re.M):
        n, v = norm(m.group(1)), m.group(2)
        if have.get(n) != v:
            bad.append((n, v, have.get(n)))
    assert not bad, f"installed packages differ from the lock: {bad}"
    return sha(REPO / CFG["lock_files"]["lock_json"])


def verify_protocol():
    man = json.loads((PREREG / "protocol_manifest.json").read_text(encoding="utf-8"))
    for rel, h in man["files"].items():
        assert sha(REPO / rel) == h, f"protocol dependency changed: {rel}"
    tag = CFG["protocol_tag"]
    tcommit = sh("rev-list", "-n", "1", tag)
    assert tcommit, f"tag {tag} missing"
    assert subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", tcommit, "HEAD"]).returncode == 0, "tag commit is not an ancestor of HEAD"
    msg = sh("tag", "-l", "--format=%(contents)", tag)
    assert sha(PREREG / "PROTOCOL.md") in msg and sha(PREREG / "protocol_manifest.json") in msg, "tag message does not carry the protocol hashes"
    return {"type": "prereg_git_tag", "tag": tag, "tag_commit": tcommit, "protocol_path": "research/preregistration/X3-A/PROTOCOL.md",
            "protocol_sha256": sha(PREREG / "PROTOCOL.md"), "protocol_manifest_sha256": sha(PREREG / "protocol_manifest.json")}


# ---------------------------------------------------------------- gate G-HARNESS
def gate_harness(out_dir):
    sys.path.insert(0, str(REPO / "research" / "scripts"))
    import execute_paper3_study as fm
    env_log = out_dir / "_env_log_unused.csv"
    Orig = fm.AlignedInterviewEnv
    fm.AlignedInterviewEnv = lambda **kw: Orig(log_file=str(env_log), **kw)
    OrigPPO = fm.PPO
    rows, ok_all = [], True

    def cmp_one(policy, pkind, persona, eseed, mdir, guard, stub=None, ppo=None, **mut):
        f = fm.run_session_trajectory(policy, persona, "aligned_progress", eseed, mdir, guard, 10)
        p = fm.PERSONA_TARGETS[persona]
        pol = L.make_policy(pkind, eval_seed=eseed, ppo=ppo, mutant=mut.get("pmutant"))
        n = L.simulate(pol, persona, p["skill"], p["target_difficulty"], eseed, guard, disabled=mut.get("disabled", frozenset()), mutant=mut.get("smutant"))
        keys = ["target_tracking_error", "volatility", "oscillation_rate", "final_difficulty", "guardrail_interventions", "constraint_violations", "raw_actions", "final_actions", "guardrail_ids"]
        return sum(1 for k in keys if f[k] != n[k])

    class ConstModel:
        def predict(self, obs, deterministic=True):
            return np.array([1]), None

    def stub_ppo():
        class FP:
            @staticmethod
            def load(path):
                return ConstModel()
        return FP

    def run_block(name, policy, pkind, guard, seeds=(None,), stub=False, ppo_of=None, mutant=None):
        mism = n = 0
        for ts in seeds:
            mdir = CK / f"seed_{ts}" if ts else None
            if stub:
                mdir = CK / "seed_123"
                fm.PPO = stub_ppo()
            ppo = ppo_of(ts) if ppo_of else None
            for persona in fm.PERSONA_TARGETS:
                for es in fm.EVAL_SEEDS:
                    mism += cmp_one(policy, pkind, persona, es, mdir, guard, ppo=ppo, **(mutant or {}))
                    n += 1
            fm.PPO = OrigPPO
        return name, mism, n

    ppo_cache = {}

    def ppo_of(ts):
        if ts not in ppo_cache:
            m, v = L.load_ppo(CK / f"seed_{ts}", env_log)
            ppo_cache[ts] = L.PPOPolicy(m, v)
        return ppo_cache[ts]

    t = CFG["training_seeds"]
    blocks = [run_block("Fixed", "Fixed", "const_same", False), run_block("Heuristic", "Heuristic", "heuristic", False),
              run_block("PPO raw (5 seeds)", "PPO", "ppo", False, seeds=t, ppo_of=ppo_of),
              run_block("PPO+G (5 seeds)", "PPO", "ppo", True, seeds=t, ppo_of=ppo_of),
              run_block("Constant-Same+G (stub)", "PPO", "const_same", True, stub=True)]
    for name, mism, n in blocks:
        ok = mism == 0
        ok_all &= ok
        rows.append({"check": f"equivalence: {name}", "sessions": n, "mismatching_fields": mism, "expected": "0", "passed": ok})
    # random-state shield equivalence
    from rl.guardrails import apply_canonical_guardrails as frozen_shield
    rs = np.random.RandomState(CFG["gate_harness"]["random_state_seed"])
    bad = 0
    N = CFG["gate_harness"]["random_state_tests"]
    for i in range(N):
        perf, avg, conf, hes = rs.random_sample(4)
        if i % 5 == 0:
            perf = rs.choice([0.0, 0.3, 0.35, 0.4, 0.65, 0.8, 0.9, 0.95, 1.0])
            hes = rs.choice([0.0, 0.6, 0.65, 0.7, 1.0])
            conf = rs.choice([0.0, 0.3, 0.4, 1.0])
        d = rs.choice([0.2, 0.4, 0.6, 0.8, 1.0])
        a = int(rs.randint(0, 3))
        f = frozen_shield(perf=float(perf), avg_perf=float(avg), conf=float(conf), hes=float(hes), progress=0.5, difficulty=float(d),
                          proposed_action=a, consecutive_failures=0, is_infrastructure_failure=False)
        n_ = L.shield(float(perf), float(avg), float(conf), float(hes), float(d), a)
        bad += int(tuple(f) != tuple(n_))
    rows.append({"check": f"shield copy equals frozen shield on {N} random/edge states", "sessions": N, "mismatching_fields": bad, "expected": "0", "passed": bad == 0})
    ok_all &= bad == 0
    # mutation (positive) controls: must be DETECTED
    muts = [("mutant: G5 removed from shield (PPO+G seed 123)", "PPO", "ppo", True, (123,), {"disabled": frozenset(["G5"])}),
            ("mutant: G4 threshold 0.31 (PPO+G seed 123)", "PPO", "ppo", True, (123,), {"smutant": "g4_thr"}),
            ("mutant: heuristic Easier-threshold 0.50 instead of 0.40", "Heuristic", "heuristic", False, (None,), {"pmutant": "heur_lo"}),
            ("INFORMATIONAL (not gating): heuristic Harder-threshold 0.60 instead of 0.75", "Heuristic", "heuristic", False, (None,), {"pmutant": "heur_thr"}),
            ("INFORMATIONAL (not gating): heuristic Harder-threshold 0.76 instead of 0.75", "Heuristic", "heuristic", False, (None,), {"pmutant": "heur_thr_subtle"})]
    for name, pol, pk, g, seeds, mut in muts:
        _, mism, n = run_block(name, pol, pk, g, seeds=seeds, ppo_of=ppo_of if pk == "ppo" else None, mutant=mut)
        det = mism > 0
        if name.startswith("INFORMATIONAL"):
            rows.append({"check": name, "sessions": n, "mismatching_fields": mism, "expected": "informational", "passed": "n/a"})
            continue
        ok_all &= det
        rows.append({"check": name, "sessions": n, "mismatching_fields": mism, "expected": ">0 (mutant must be detected)", "passed": det})
    fm.AlignedInterviewEnv = Orig
    return ok_all, rows


# ---------------------------------------------------------------- run
def condition_specs():
    c = CFG["conditions"]
    base, ppo = [], []
    for k in c["base_policies"]:
        for s in c["shield"]:
            base.append({"name": f"{LABEL[k]} | {s}", "kind": k, "shield": s == "G", "disabled": frozenset()})
    if "const_same" in c["ablation_on"]:
        for r in c["ppo"]["ablation_rules"]:
            base.append({"name": f"Constant-Same | G-minus-{r}", "kind": "const_same", "shield": True, "disabled": frozenset([r])})
    for mode in c["ppo"]["modes"]:
        for s in c["ppo"]["shield"]:
            nm = "PPO" if mode == "intact" else f"PPO-state-{mode}"
            ppo.append({"name": f"{nm} | {s}", "mode": mode, "shield": s == "G", "disabled": frozenset()})
    for r in c["ppo"]["ablation_rules"]:
        ppo.append({"name": f"PPO | G-minus-{r}", "mode": "intact", "shield": True, "disabled": frozenset([r])})
    return base, ppo


def run_all(strata, eval_seeds, out_dir):
    base, ppo_specs = condition_specs()
    env_log = out_dir / "_env_log_unused.csv"
    rows = []

    def rec(cond, ts, plist, pi, p, es, r):
        rows.append({"condition": cond, "training_seed": ts, "stratum": p["stratum"], "persona_id": p["persona_id"], "persona_index": pi, "eval_seed": es,
                     "target": p["target"], "mae": f"{r['mae_x']:.6f}", "volatility": f"{r['vol_x']:.6f}", "oscillation": f"{r['osc_x']:.6f}",
                     "final_difficulty": r["final_difficulty"], "activations": r["guardrail_interventions"], "overrides": r["overrides"],
                     "attempted_boundary": r["constraint_violations"], "oracle_agreement": f"{r['oracle_agreement']:.3f}",
                     "raw_actions": "|".join(r["raw_actions"]), "final_actions": "|".join(r["final_actions"])})

    for plist in strata:
        for spec in base:
            for pi, p in enumerate(plist):
                for es in eval_seeds:
                    pol = L.make_policy(spec["kind"], persona_index=pi, eval_seed=es)
                    r = L.simulate(pol, p["type"], p["skill"], p["target"], es, spec["shield"], spec["disabled"], CFG["max_steps"])
                    rec(spec["name"], "-", plist, pi, p, es, r)
        for ts in CFG["training_seeds"]:
            model, vn = L.load_ppo(CK / f"seed_{ts}", env_log)
            pools = {}
            for spec in ppo_specs:
                if spec["mode"] != "intact" or spec["disabled"]:
                    continue
                pool = {}
                for pi, p in enumerate(plist):
                    for es in eval_seeds:
                        pol = L.PPOPolicy(model, vn).act
                        r = L.simulate(pol, p["type"], p["skill"], p["target"], es, spec["shield"], spec["disabled"], CFG["max_steps"])
                        rec(spec["name"], ts, plist, pi, p, es, r)
                        for st, ob in r["obs_log"].items():
                            pool[(p["persona_id"], es, st)] = ob
                pools[spec["shield"]] = pool
            n = len(plist)
            k = max(1, n // 3)
            for spec in ppo_specs:
                if spec["mode"] == "intact" and not spec["disabled"]:
                    continue
                for pi, p in enumerate(plist):
                    partner = plist[(pi + k) % n]["persona_id"]
                    for es in eval_seeds:
                        pp = L.PPOPolicy(model, vn, mode=spec["mode"], pool=pools[spec["shield"]] if spec["mode"] == "shuffle" else None, partner=partner)
                        r = L.simulate(pp.act, p["type"], p["skill"], p["target"], es, spec["shield"], spec["disabled"], CFG["max_steps"])
                        rec(spec["name"], ts, plist, pi, p, es, r)
    return rows


def rows_to_csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main():
    mode = "--confirmatory" if "--confirmatory" in sys.argv else ("--dry-run" if "--dry-run" in sys.argv else None)
    assert mode, "specify --dry-run or --confirmatory"
    out_dir = HERE / ("results" if mode == "--confirmatory" else "dryrun")
    if out_dir.exists():
        raise SystemExit(f"refusing to run: {out_dir} already exists (no silent reruns)")
    protocol = {"type": "dry-run fixture (non-confirmatory)"}
    lock_hash = verify_lock() if mode == "--confirmatory" else (verify_lock() if (REPO / CFG["lock_files"]["lock_json"]).exists() else None)
    if mode == "--confirmatory":
        protocol = verify_protocol()
    m = rm.Manifest("X3-A-" + ("run" if mode == "--confirmatory" else "dryrun"), out_dir, __file__, config_path=CFG_PATH, protocol=protocol,
                    seeds={"training": CFG["training_seeds"], "eval": CFG["eval_seeds"], "bootstrap": CFG["bootstrap"]["seed"]},
                    lock_id=CFG["lock_id"], env_lock_sha256=lock_hash, gate={"name": "G-HARNESS", "passed": None, "details": "pending"})
    m.add_inputs([HERE / "x3a_lib.py", HERE / "x3a_run.py", REPO / "rl/guardrails.py", REPO / "rl/env/interview_env.py", REPO / "rl/training/simulated_candidate.py"])
    for s in CFG["training_seeds"]:
        m.add_model("ppo_checkpoint", CK / f"seed_{s}" / "ppo_final.zip", s)
        m.add_model("vecnormalize", CK / f"seed_{s}" / "vecnormalize.pkl", s)
    t0 = time.time()
    ok, grows = gate_harness(out_dir)
    m.set_gate("G-HARNESS", bool(ok), f"{sum(1 for r in grows if r['passed'] is True)}/{sum(1 for r in grows if r['passed'] != 'n/a')} gating checks passed")
    outs = [rm.write_new(out_dir / "gate_G-HARNESS.csv", rows_to_csv(grows))]
    print("G-HARNESS passed:", ok, f"({sum(1 for r in grows if r['passed'] is True)}/{sum(1 for r in grows if r['passed'] != 'n/a')})", f"{time.time()-t0:.0f}s")
    if not ok:
        m.note("G-HARNESS FAILED: run aborted before any result was produced", failure=True)
        print(m.finish(outs, status="failed"))
        raise SystemExit(1)
    grid, frozen = L.persona_grid(), L.persona_frozen()
    strata = [frozen] if mode == "--dry-run" else [grid, frozen]
    rows = run_all(strata, CFG["eval_seeds"], out_dir)
    outs.append(rm.write_new(out_dir / "sessions.csv", rows_to_csv(rows)))
    outs.append(rm.write_new(out_dir / "personas.csv", rows_to_csv([{k: v for k, v in p.items()} for p in grid + frozen])))
    print(m.finish(outs), len(rows), "session rows", f"{time.time()-t0:.0f}s total", m.d["failures"])


if __name__ == "__main__":
    main()
