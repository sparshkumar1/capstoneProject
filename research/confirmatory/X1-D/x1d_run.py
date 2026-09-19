"""X1-D runner: JUnit test report + evaluator/SQLite latency on the SUT. Run with the SUT's project .venv:
   .venv/Scripts/python.exe -B research/confirmatory/X1-D/x1d_run.py
Refuses to run if results/ exists; verifies the protocol tag; writes a manifest first."""
import csv
import io
import json
import os
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "research" / "tools"))
sys.path.insert(0, str(REPO))
import run_manifest as rm  # noqa: E402

CFG_PATH = HERE / "x1d_config.json"
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
PREREG = REPO / "research" / "preregistration" / "X1-D"
OUT = HERE / "results"


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def verify_protocol():
    man = json.loads((PREREG / "protocol_manifest.json").read_text(encoding="utf-8"))
    for rel, h in man["files"].items():
        assert rm.sha256_file(REPO / rel) == h, f"protocol dependency changed: {rel}"
    tag = CFG["protocol_tag"]
    tc = git("rev-list", "-n", "1", tag)
    assert tc, "protocol tag missing"
    assert subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", tc, "HEAD"]).returncode == 0
    msg = git("tag", "-l", "--format=%(contents)", tag)
    assert rm.sha256_file(PREREG / "PROTOCOL.md") in msg and rm.sha256_file(PREREG / "protocol_manifest.json") in msg
    sut = git("rev-list", "-n", "1", CFG["sut_tag"])
    assert sut, "SUT tag missing"
    return {"type": "prereg_git_tag", "tag": tag, "tag_commit": tc, "sut_tag": CFG["sut_tag"], "sut_commit": sut,
            "protocol_sha256": rm.sha256_file(PREREG / "PROTOCOL.md")}


def wcsv(name, rows):
    b = io.StringIO()
    w = csv.DictWriter(b, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return rm.write_new(OUT / name, b.getvalue())


def stats(v, rng, B=10000):
    v = np.asarray(v, float)
    out = {}
    for nm, q in (("median", 50), ("p95", 95), ("p99", 99)):
        pt = float(np.percentile(v, q))
        bs = [np.percentile(v[rng.integers(0, len(v), len(v))], q) for _ in range(B)]
        out[nm] = (pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
    return out


def main():
    if OUT.exists():
        raise SystemExit("refusing to run: results/ exists")
    protocol = verify_protocol()
    m = rm.Manifest("X1-D-run", OUT, __file__, config_path=CFG_PATH, protocol=protocol, seeds={"bootstrap": 42},
                    non_locked_reason="SUT project .venv (unlocked by design of X1-D; versions recorded)")
    outs = []
    t0 = time.time()
    env = dict(os.environ, **CFG["test_report"]["env"])
    args = [a.replace("{out}", str(OUT)) for a in CFG["test_report"]["command"]]
    p = subprocess.run([sys.executable, "-B", *args], cwd=str(REPO), env=env, capture_output=True, text=True)
    outs.append(rm.write_new(OUT / "pytest_console.txt", (p.stdout or "") + "\n--- STDERR ---\n" + (p.stderr or "")))
    print("pytest exit", p.returncode, f"{time.time() - t0:.0f}s")
    sys.stdout.flush()
    junit = OUT / "junit.xml"
    if junit.exists():
        outs.append(junit)
    # latency (real evaluator, not mock)
    os.environ.pop("EVALUATOR_MOCK_MODE", None)
    import pandas as pd
    from services.evaluator.app import evaluate, get_rubric, _ensure_evaluator_assets_loaded
    from services.storage.database import init_db, get_or_create_candidate, save_session, save_attempt
    cl = pd.read_csv(REPO / "research/results/paper2/paper2_case_level_results.csv")
    with open(REPO / "research/annotation/FROZEN_HUMAN_RATINGS/RATER_1_COMPLETED.csv", encoding="utf-8-sig", newline="") as f:
        tx = {r["item_id"]: r for r in csv.DictReader(f)}
    trip = [(tx[r.case_id]["question"], tx[r.case_id]["candidate_answer"], int(r.qid)) for r in cl.itertuples()]
    t = time.perf_counter()
    _ensure_evaluator_assets_loaded()
    load_ms = (time.perf_counter() - t) * 1000
    lat = []
    for i in range(101):
        q, a, qid = trip[i % len(trip)]
        t = time.perf_counter()
        evaluate(q, a, get_rubric(qid))
        lat.append((time.perf_counter() - t) * 1000)
    first, warm = lat[0], lat[1:]
    db = OUT / "_latency_tmp.db"
    init_db(db)
    c = get_or_create_candidate("lat@test.com", "Lat", db_path=db)
    save_session({"id": "s", "candidate_id": c["id"]}, db_path=db)
    wr = []
    for i in range(100):
        t = time.perf_counter()
        save_attempt({"id": str(uuid.uuid4()), "session_id": "s", "candidate_id": c["id"], "question_id": f"q{i}", "raw_score": .8,
                      "validated_score": .8, "attempt_type": "primary", "transcript": "t", "feedback_json": {}}, db_path=db)
        wr.append((time.perf_counter() - t) * 1000)
    raw_rows = [{"series": "evaluator_first_request", "i": 0, "ms": f"{first:.4f}"}, {"series": "asset_load", "i": 0, "ms": f"{load_ms:.4f}"}]
    raw_rows += [{"series": "evaluator_warm", "i": i, "ms": f"{v:.4f}"} for i, v in enumerate(warm)]
    raw_rows += [{"series": "sqlite_write", "i": i, "ms": f"{v:.4f}"} for i, v in enumerate(wr)]
    outs.append(wcsv("latency_raw.csv", raw_rows))
    rng = np.random.default_rng(42)
    rows = []
    for nm, v in (("evaluator_warm", warm), ("sqlite_write", wr)):
        for k, (pt, lo, hi) in stats(v, rng).items():
            rows.append({"series": nm, "n": len(v), "stat": k, "value_ms": round(pt, 3), "ci_low_ms": round(lo, 3), "ci_high_ms": round(hi, 3)})
    outs.append(wcsv("latency_stats.csv", rows))
    root = ET.parse(junit).getroot()
    ts = root if root.tag == "testsuite" else root.find("testsuite")
    summ = {"tests": int(ts.get("tests")), "failures": int(ts.get("failures")), "errors": int(ts.get("errors")), "skipped": int(ts.get("skipped")),
            "pytest_exit_code": p.returncode,
            "failed_tests": [f"{tc.get('classname')}::{tc.get('name')}" for tc in ts.iter("testcase") if tc.find("failure") is not None or tc.find("error") is not None]}
    outs.append(rm.write_new(OUT / "test_report_summary.json", json.dumps(summ, indent=2)))
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(str(db) + suffix)
        except OSError:
            pass
    print(m.finish(outs), summ)
    print(json.dumps(rows))


if __name__ == "__main__":
    main()
