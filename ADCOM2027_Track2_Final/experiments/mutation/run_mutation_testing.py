"""Driver for protocol MA-MUT v1. Applies one textual mutant at a time to a SCRATCH export of the repository,
runs the oracles in subprocesses, restores the file, and writes mutation_results.json.
Usage: python run_mutation_testing.py --repo REPO_EXPORT --python PY --out OUTDIR [--only MU01,MU02]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

A = "agents/multiagent/"
# (id, file, old, new, family, description)
MUTANTS = [
    ("MU01", A + "authority.py", "if str(k).lower() in FORBIDDEN_KEYS:", "if False:", "authority",
     "forbidden-key scan disabled"),
    ("MU02", A + "authority.py", '"score", "final_score", "raw_score",', '"score", "raw_score",', "authority",
     "'final_score' removed from forbidden keys"),
    ("MU03", A + "authority.py", "                stack.append(v)\n", "                pass\n", "authority",
     "forbidden-key scan not recursive"),
    ("MU04", A + "arbitration.py",
     "if strategy.confidence < tau:\n            records.append(_rec(obs, STRATEGY, strategy.difficulty_action",
     "if strategy.confidence <= tau:\n            records.append(_rec(obs, STRATEGY, strategy.difficulty_action",
     "arbitration", "tau boundary < changed to <="),
    ("MU05", A + "arbitration.py",
     "if strategy.confidence < tau:\n            records.append(_rec(obs, STRATEGY, strategy.difficulty_action",
     "if False:\n            records.append(_rec(obs, STRATEGY, strategy.difficulty_action",
     "arbitration", "difficulty confidence gate removed"),
    ("MU06", A + "arbitration.py", "elif not strategy.evidence:", "elif False:", "arbitration",
     "evidence requirement removed"),
    ("MU07", A + "arbitration.py",
     "    if guardrail_fn is not None:\n        g_action, rule = guardrail_fn(candidate)",
     "    if False and guardrail_fn is not None:\n        g_action, rule = guardrail_fn(candidate)",
     "guardrail", "guardrail layer skipped after selection"),
    ("MU08", A + "arbitration.py", "FOLLOWUP_HARD_CAP = 2", "FOLLOWUP_HARD_CAP = 3", "arbitration",
     "follow-up hard cap 2 -> 3"),
    ("MU09", A + "arbitration.py", "return min(5, level + 1)", "return min(6, level + 1)", "arbitration",
     "upper difficulty bound 5 -> 6"),
    ("MU10", A + "arbitration.py", "elif normalize_concept(probe.concept) not in seen_concepts:", "elif False:",
     "arbitration", "probe concept grounding removed"),
    ("MU11", A + "arbitration.py", "if obs.infrastructure_failure:", "if False:", "arbitration",
     "infrastructure-failure hard constraint removed"),
    ("MU12", A + "coordinator.py",
     "or proposal.session_id != obs.session_id or obs.state_version != self.current_version:",
     "or proposal.session_id != obs.session_id:", "version",
     "hub-version comparison removed from stale check"),
    ("MU13", A + "coordinator.py",
     "if proposal.state_version != obs.state_version or proposal.turn_id != obs.turn_id \\",
     "if False and proposal.state_version != obs.state_version or proposal.turn_id != obs.turn_id \\", "version",
     "stale-proposal check removed"),
    ("MU14", A + "coordinator.py", "        if key in self._answered:", "        if False:", "version",
     "duplicate-answer rejection removed"),
    ("MU15", A + "coordinator.py",
     "        except Exception as exc:                     # agent crash\n            breaker.record_failure()",
     "        except Exception as exc:                     # agent crash\n            pass", "breaker",
     "crash does not count toward circuit breaker"),
    ("MU16", A + "coordinator.py", "        if self.enforce_grounding:", "        if False:", "grounding",
     "coaching grounding check disabled in code"),
    ("MU17", A + "coordinator.py", "proposal = raw if isinstance(raw, model) else model.model_validate(raw)",
     "proposal = raw if isinstance(raw, model) else model.model_construct(**raw)", "schema",
     "schema validation replaced by unvalidated construction"),
    ("MU18", A + "grounding.py", "return tuple(c for c in plan.emphasize if normalize_concept(c) not in ev)",
     "return tuple()", "grounding", "ungrounded_concepts always empty"),
    ("MU19", A + "contracts.py", 'model_config = ConfigDict(extra="forbid", frozen=True)',
     'model_config = ConfigDict(extra="ignore", frozen=True)', "schema",
     "unknown fields ignored instead of rejected"),
    ("MU20", A + "coaching_render.py", "if any(feedback.get(k) != original.get(k) for k in PROTECTED_KEYS):",
     "if False:", "authority", "protected evaluator-field guard in renderer removed"),
    ("MU21", A + "contracts.py", "Confidence = Field(ge=0.0, le=1.0, allow_inf_nan=False)",
     "Confidence = Field(ge=0.0, le=1.0, allow_inf_nan=True)", "schema", "NaN confidence allowed by schema"),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_oracles(repo, py, env):
    t0 = time.time()
    p1 = subprocess.run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                         "paper/adcom2027_final_v13_candidate/tests/test_coordination_and_specialization.py"],
                        cwd=repo, env=env, capture_output=True, text=True, timeout=900)
    o1_fail = p1.returncode != 0
    failed = [ln.split("::")[-1].split(" ")[0] for ln in p1.stdout.splitlines() if ln.startswith("FAILED")]
    p2 = subprocess.run([py, str(Path(__file__).with_name("oracle_coordinator.py")), str(repo)], cwd=repo, env=env,
                        capture_output=True, text=True, timeout=1800)
    line = [ln for ln in p2.stdout.splitlines() if ln.startswith("JSON_RESULT ")]
    replay = json.loads(line[0][12:]) if line else {"error": (p2.stderr or p2.stdout)[-400:]}
    return {"o1_failed": o1_fail, "o1_failed_tests": failed, "replay": replay, "seconds": round(time.time() - t0, 1)}


def judge(res, base):
    r = res["replay"]
    if "error" in r:
        return {"O1": res["o1_failed"], "O2": True, "O3": True, "O4": True}
    o2 = any(v["violations"] or v["harness_errors"] for v in r["o2"].values())
    o3 = r["o3"] != base["replay"]["o3"]
    o4 = r["o4"]["nominal_digest"] != base["replay"]["o4"]["nominal_digest"]
    return {"O1": res["o1_failed"], "O2": o2, "O3": o3, "O4": o4}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--python", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, EVALUATOR_MOCK_MODE="1",
               PYTHONPATH=os.pathsep.join([os.environ.get("PYTHONPATH", ""), str(repo)]))
    files = sorted({m[1] for m in MUTANTS})
    orig = {f: (repo / f).read_bytes() for f in files}
    orig_sha = {f: sha(repo / f) for f in files}
    results = {"protocol": "MA-MUT-v2", "protocol_sha256": sha(Path(__file__).with_name("Mutation_Protocol.md")),
               "driver_sha256": sha(__file__), "oracle_sha256": sha(Path(__file__).with_name("oracle_coordinator.py")),
               "file_sha256_before": orig_sha, "mutants": []}
    base = run_oracles(repo, a.python, env)
    rp = base["replay"]
    bj = {"O1": base["o1_failed"], "replay_error": "error" in rp}
    if "error" not in rp:
        bj["O2"] = any(v["violations"] or v["harness_errors"] for v in rp["o2"].values())
    results["baseline"] = {"raw": base, "judged_failures": bj}
    print("BASELINE", bj, base["seconds"], "s", flush=True)
    if any(bj.values()):
        (out / "mutation_results.json").write_text(json.dumps(results, indent=1, sort_keys=True))
        sys.exit("baseline invalid")
    try:
        for mid, f, old, new, fam, desc in MUTANTS:
            if a.only and mid not in a.only.split(","):
                continue
            src = orig[f].decode("utf-8")
            n = src.count(old)
            if n != 1:
                results["mutants"].append({"id": mid, "error": f"pattern occurs {n} times"})
                print(mid, "PATTERN ERROR", n)
                continue
            (repo / f).write_bytes(src.replace(old, new).encode("utf-8"))
            try:
                res = run_oracles(repo, a.python, env)
            finally:
                (repo / f).write_bytes(orig[f])
            j = judge(res, base)
            killed = any(j[k] for k in ("O1", "O2", "O3", "O4"))
            r2 = res["replay"]
            results["mutants"].append({
                "id": mid, "file": f, "family": fam, "description": desc, "killed": killed, "oracles": j,
                "o1_failed_tests": res["o1_failed_tests"], "seconds": res["seconds"],
                "o2_violating_scenarios": [k for k, v in r2.get("o2", {}).items() if v["violations"] or v["harness_errors"]],
                "o3_changed_scenarios": [k for k, v in r2.get("o3", {}).items() if v != base["replay"]["o3"].get(k)],
                "replay_error": r2.get("error")})
            print(mid, "KILLED" if killed else "SURVIVED", j, flush=True)
    finally:
        for f in files:
            (repo / f).write_bytes(orig[f])
    results["file_sha256_after"] = {f: sha(repo / f) for f in files}
    assert results["file_sha256_after"] == orig_sha, "restore failed"
    (out / "mutation_results.json").write_text(json.dumps(results, indent=1, sort_keys=True))
    print("DONE")
