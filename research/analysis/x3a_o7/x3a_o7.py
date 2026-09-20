#!/usr/bin/env python
"""X3-A / O7 frozen-data sensitivity analysis (secondary robustness evidence).

Specification: research/audit/X3A_O7_SENSITIVITY_SPEC.md (Revision 3). This script implements exactly
R0 (independent reproduction gate), A, B, C. Nothing else.

Independence (spec 2.4): imports NOTHING from x3a_analyze.py / x3a_lib.py / x3a_run.py or any harness
module; uses only the standard library, numpy and scipy.

Provenance chain (post-Codex repair 1). All expected hashes live in the locked registration artifact
research/analysis/x3a_o7/O7_REGISTRATION.json (never computed from mutable files at run time):
  0. (official run only) HEAD must EQUAL the commit of the registered annotated tag named in the registration,
     the tag must resolve to the full commit SHA supplied via --registered-commit and recorded in the tag
     message, and the registration + this script must be byte-identical to their blobs at that tag;
  1. registration + this script must be tracked and clean against HEAD (official run only);
  2. environment/version/lock hashes (official run only);
  3. x3a_decision.json full SHA-256 == registered value (bytes are NOT parsed here);
  4. every registered upstream X3-A manifest: full SHA-256 == registered value, status == completed,
     registered gate passed (where a gate is required), every output it lists exists under the repository
     and hashes to the recorded value, and the registered must-list outputs (sessions.csv, x3a_decision.json)
     are listed with the registered hashes;
  5. ONLY THEN: cells are loaded, R0 is computed, the output directory is created, x3a_decision.json is read
     (from the same bytes that were hashed) and compared; A/B/C run only if R0 passes.

Official run (locked environment only):
    envs/LOCK-X3-2026-09-19/Scripts/python.exe research/analysis/x3a_o7/x3a_o7.py --registered-commit <40-hex>
Mechanics self-test on SYNTHETIC data in a temporary tree (never touches the repository):
    <any python with numpy+scipy> research/analysis/x3a_o7/x3a_o7.py --selftest

Hard stop: any provenance/environment/key-set failure, or an R0 mismatch above ABS_TOL, stops the analysis
before A/B/C. No tolerance is introduced, no other draw order is tried.
"""
import csv
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats as sps

REPO = Path(__file__).resolve().parents[3]
REG_REL = "research/analysis/x3a_o7/O7_REGISTRATION.json"
SCRIPT_REL = "research/analysis/x3a_o7/x3a_o7.py"
OUT_REL = "research/analysis/x3a_o7/results"
ENV_REL = "envs/LOCK-X3-2026-09-19"

EXPECTED_ENV = {"python": (3, 12, 7), "numpy": "2.5.2", "scipy": "1.17.1"}
ABS_TOL = 1e-12
B = 10000
RNG_SEED = 42
TRAIN_SEEDS = [42, 123, 456, 789, 999]                       # protocol: numeric ascending
EVAL_SEEDS = [k * 1001 for k in range(1, 21)]                # 1001, 2002, ..., 20020 (x3a_config.json)
TYPES = ["normal", "nervous_expert", "lucky_guesser", "overconfident_fail", "struggling_junior"]
SKILLS = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
PERSONAS = sorted("%s@%.2f" % (t, s) for t in TYPES for s in SKILLS)   # default ascending string sort
COND_PPO, COND_CS = "PPO | G", "Constant-Same | G"
STRATUM = "grid"
MARGIN, SUPERIOR = 0.12, 0.20


class Stop(Exception):
    pass


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------
# registration, git lock, environment, provenance
# ----------------------------------------------------------------------------------------------
def load_registration(repo):
    p = Path(repo) / REG_REL
    if not p.is_file():
        raise Stop("registration artifact missing: %s" % p)
    reg = json.loads(p.read_text(encoding="utf-8"))
    for k in ("sessions", "decision", "lock", "upstream_manifests"):
        if k not in reg:
            raise Stop("registration lacks %r" % k)
    return reg


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=60)


TAG_FIELDS = ("registration-commit", "registration-sha256", "script-sha256")


def assert_registration_tag(repo, reg, registered_commit, script_path=None):
    """Official runs execute only at an immutable, registered execution point (final repair 1).
    A commit cannot contain its own SHA, so the registered full commit SHA is (a) written into the immutable
    annotated tag message together with the SHA-256 of the registration and of this script and (b) supplied
    out-of-band via --registered-commit. All of the following must hold: tag exists; is annotated; resolves to
    the supplied commit; HEAD == that commit exactly (descent is NOT enough); the tag message's three fields are
    present exactly once and agree; the registration and this script are byte-identical to their blobs at the tag
    (raw `git cat-file blob`, no filters); the blobs hash to the tag message values; and the running script is the
    registered file."""
    repo = Path(repo).resolve()
    rt = reg.get("registration_tag") or {}
    name = rt.get("name")
    if not name or not isinstance(name, str):
        raise Stop("registration lacks registration_tag.name")
    if not re.fullmatch("[0-9a-f]{40}", registered_commit or ""):
        raise Stop("a full 40-hex registered commit SHA must be supplied with --registered-commit")
    ref = "refs/tags/" + name
    r = _git(repo, "cat-file", "-t", ref)
    if r.returncode != 0:
        raise Stop("registered tag %s does not exist" % name)
    if r.stdout.strip() != "tag":
        raise Stop("registered tag %s is not an annotated tag" % name)
    commit = _git(repo, "rev-parse", ref + "^{commit}").stdout.strip()
    if commit != registered_commit:
        raise Stop("registered tag %s resolves to %s, not the registered commit %s" % (name, commit, registered_commit))
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if head != commit:
        raise Stop("HEAD %s is not the registered tag commit %s" % (head, commit))
    fields = {}
    for line in _git(repo, "tag", "-l", "--format=%(contents)", name).stdout.splitlines():
        for f in TAG_FIELDS:
            if line.startswith(f + ": "):
                if f in fields:
                    raise Stop("tag message repeats field %s" % f)
                fields[f] = line[len(f) + 2:].strip()
    if set(fields) != set(TAG_FIELDS):
        raise Stop("tag message lacks required fields %s" % sorted(set(TAG_FIELDS) - set(fields)))
    if fields["registration-commit"] != commit:
        raise Stop("tag message registration-commit %s != tag commit %s" % (fields["registration-commit"], commit))
    if Path(script_path or __file__).resolve() != (repo / SCRIPT_REL).resolve():
        raise Stop("the running script is not %s" % SCRIPT_REL)
    hashes = {}
    for rel, key in ((REG_REL, "registration-sha256"), (SCRIPT_REL, "script-sha256")):
        b = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", "%s:%s" % (commit, rel)],
                           capture_output=True, timeout=60)
        if b.returncode != 0:
            raise Stop("%s is not in the tagged commit" % rel)
        if b.stdout != (repo / rel).read_bytes():
            raise Stop("%s working bytes differ from its blob at the registered tag" % rel)
        hashes[key] = sha256_bytes(b.stdout)
        if hashes[key] != fields[key]:
            raise Stop("%s hash %s != tag message %s" % (rel, hashes[key], fields[key]))
    return {"tag": name, "tag_object": _git(repo, "rev-parse", ref).stdout.strip(), "commit": commit, **hashes}


def assert_registration_locked(repo):
    """Official runs only: the registration and this script are tracked and unmodified against HEAD."""
    for rel in (REG_REL, SCRIPT_REL):
        if _git(repo, "ls-files", "--error-unmatch", "--", rel).returncode != 0:
            raise Stop("%s is not tracked in git (commit and tag before an official run)" % rel)
        if _git(repo, "status", "--porcelain", "--", rel).stdout.strip():
            raise Stop("%s differs from HEAD (commit and tag before an official run)" % rel)


def repo_file(repo, rel):
    """Resolve a repository-relative path (backslashes tolerated); must be a regular file inside the repo."""
    repo = Path(repo).resolve()
    p = (repo / str(rel).replace("\\", "/")).resolve()
    try:
        p.relative_to(repo)
    except ValueError:
        raise Stop("path escapes the repository: %s" % rel)
    if not p.is_file():
        raise Stop("not a regular file: %s" % rel)
    return p


def assert_environment(repo, reg):
    problems = []
    if tuple(sys.version_info[:3]) != EXPECTED_ENV["python"]:
        problems.append("python %s != %s" % (sys.version_info[:3], EXPECTED_ENV["python"]))
    if np.__version__ != EXPECTED_ENV["numpy"]:
        problems.append("numpy %s != %s" % (np.__version__, EXPECTED_ENV["numpy"]))
    import scipy
    if scipy.__version__ != EXPECTED_ENV["scipy"]:
        problems.append("scipy %s != %s" % (scipy.__version__, EXPECTED_ENV["scipy"]))
    if platform.system() != "Windows" or sys.maxsize <= 2 ** 32:
        problems.append("not 64-bit Windows")
    try:
        Path(sys.prefix).resolve().relative_to((Path(repo) / ENV_REL).resolve())
    except ValueError:
        problems.append("interpreter prefix %s is not inside %s" % (sys.prefix, ENV_REL))
    for label in ("lock_json", "requirements"):
        ent = reg["lock"][label]
        got = sha256(repo_file(repo, ent["path"]))
        if got != ent["sha256"]:
            problems.append("%s sha256 %s != registered %s" % (label, got, ent["sha256"]))
    if problems:
        raise Stop("ENVIRONMENT FAILURE: " + "; ".join(problems))


def verify_provenance(repo, reg):
    """Repair 1: authenticate x3a_decision.json and the upstream X3-A manifests BEFORE anything else.
    Returns a record; raises Stop on the first failure. Parses no result value."""
    rec = {"decision": {}, "sessions": {}, "manifests": []}
    dec = reg["decision"]
    dpath = repo_file(repo, dec["path"])
    got = sha256(dpath)
    if got != dec["sha256"]:
        raise Stop("DECISION SHA-256 MISMATCH: %s registered %s, found %s" % (dec["path"], dec["sha256"], got))
    rec["decision"] = {"path": dec["path"], "sha256": got}
    ses = reg["sessions"]
    got = sha256(repo_file(repo, ses["path"]))
    if got != ses["sha256"]:
        raise Stop("SESSIONS SHA-256 MISMATCH: registered %s, found %s" % (ses["sha256"], got))
    rec["sessions"] = {"path": ses["path"], "sha256": got}
    for m in reg["upstream_manifests"]:
        mp = repo_file(repo, m["path"])
        raw = mp.read_bytes()
        if sha256_bytes(raw) != m["sha256"]:
            raise Stop("UPSTREAM MANIFEST SHA-256 MISMATCH: %s" % m["path"])
        d = json.loads(raw.decode("utf-8"))
        if d.get("status") != m["required_status"]:
            raise Stop("upstream manifest %s status %r != %r" % (m["path"], d.get("status"), m["required_status"]))
        if d.get("failures"):
            raise Stop("upstream manifest %s records failures" % m["path"])
        gate = m.get("required_gate")
        if gate:
            g = d.get("gate") or {}
            if g.get("name") != gate["name"] or g.get("passed") is not True:
                raise Stop("upstream manifest %s gate %r is not the registered passed gate %r" % (m["path"], g, gate))
        listed = {}
        for o in d.get("outputs", []):
            key = str(o["path"]).replace("\\", "/")
            listed[key] = o["sha256"]
            if sha256(repo_file(repo, key)) != o["sha256"]:
                raise Stop("UPSTREAM OUTPUT CHANGED: %s (listed by %s)" % (key, m["path"]))
        for key, want in m["must_list_outputs"].items():
            if listed.get(key) != want:
                raise Stop("upstream manifest %s does not list %s with the registered hash" % (m["path"], key))
            if sha256(repo_file(repo, key)) != want:
                raise Stop("registered output %s differs from its registered hash" % key)
        rec["manifests"].append({"path": m["path"], "sha256": m["sha256"], "status": d["status"],
                                 "gate": d.get("gate"), "outputs_verified": len(listed)})
    return rec


# ----------------------------------------------------------------------------------------------
# data preparation, statistics (UNCHANGED procedure)
# ----------------------------------------------------------------------------------------------
def load_cells(path):
    """Read the CSV and build the 40x5 PPO|G matrix and the 40-vector Constant-Same|G, after key-set assertions."""
    ppo, cs = {}, {}
    n_rows = 0
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            n_rows += 1
            if r["stratum"] != STRATUM:
                continue
            if r["condition"] == COND_PPO:
                tgt = ppo
            elif r["condition"] == COND_CS:
                tgt = cs
            else:
                continue
            key = (r["training_seed"], r["persona_id"], r["eval_seed"])
            if key in tgt:
                raise Stop("DUPLICATE KEY %r in %s" % (key, r["condition"]))
            tgt[key] = float(r["mae"])
    want_eval = [str(e) for e in EVAL_SEEDS]
    if set(k[0] for k in ppo) != set(str(s) for s in TRAIN_SEEDS):
        raise Stop("PPO|G training seeds %r" % sorted(set(k[0] for k in ppo)))
    if set(k[1] for k in ppo) != set(PERSONAS) or set(k[2] for k in ppo) != set(want_eval):
        raise Stop("PPO|G persona or evaluation-seed set differs from the expected sets")
    if len(ppo) != len(TRAIN_SEEDS) * len(PERSONAS) * len(EVAL_SEEDS):
        raise Stop("PPO|G row count %d" % len(ppo))
    if set(k[0] for k in cs) != {"-"}:
        raise Stop("Constant-Same|G training-seed marker %r" % sorted(set(k[0] for k in cs)))
    if set(k[1] for k in cs) != set(PERSONAS) or set(k[2] for k in cs) != set(want_eval):
        raise Stop("Constant-Same|G persona or evaluation-seed set differs from the expected sets")
    if len(cs) != len(PERSONAS) * len(EVAL_SEEDS):
        raise Stop("Constant-Same|G row count %d" % len(cs))

    def cell(tgt, ts, p):
        return float(np.mean([v for (a, b, c), v in tgt.items() if a == ts and b == p]))
    A = np.array([[cell(ppo, str(s), p) for s in TRAIN_SEEDS] for p in PERSONAS])
    Bv = np.array([cell(cs, "-", p) for p in PERSONAS])
    return A - Bv[:, None], {"csv_rows": n_rows, "ppo_keys": len(ppo), "cs_keys": len(cs),
                             "personas": len(PERSONAS), "train_seeds": TRAIN_SEEDS, "eval_seeds": len(EVAL_SEEDS)}


def boot_two_way(D, seed=RNG_SEED, reps=B):
    """Spec 2.4 step 4: fresh generator; per replicate persona indices first, then seed indices."""
    rng = np.random.default_rng(seed)
    n, s = D.shape
    stats = np.empty(reps)
    for b in range(reps):
        pi = rng.integers(0, n, n)
        si = rng.integers(0, s, s)
        stats[b] = D[np.ix_(pi, si)].mean()
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(D.mean()), float(lo), float(hi)


def boot_persona_only(Dbar, seed=RNG_SEED, reps=B):
    rng = np.random.default_rng(seed)
    n = len(Dbar)
    stats = np.empty(reps)
    for b in range(reps):
        stats[b] = Dbar[rng.integers(0, n, n)].mean()
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(Dbar.mean()), float(lo), float(hi)


def classify(lo, hi):
    if hi < -SUPERIOR:
        return "PPO-superior"
    if lo > MARGIN:
        return "PPO-adverse"
    if lo > -MARGIN and hi < MARGIN:
        return "Equivalent"
    return "Inconclusive"


def analyses(D, reps=B):
    out = {}
    Dbar = D.mean(axis=1)
    Delta = D.mean(axis=0)
    p, lo, hi = boot_persona_only(Dbar, reps=reps)
    out["A"] = {"point": p, "ci_low": lo, "ci_high": hi, "class": classify(lo, hi),
                "sd_persona_level": float(np.std(Dbar, ddof=1)), "B": reps, "seed": RNG_SEED}
    t = float(sps.t.ppf(0.975, len(Delta) - 1))
    sd = float(np.std(Delta, ddof=1))
    half = t * sd / math.sqrt(len(Delta))
    m = float(np.mean(Delta))
    out["B"] = {"point": m, "ci_low": m - half, "ci_high": m + half, "class": classify(m - half, m + half),
                "t_0.975_df4": t, "sd_seed_level": sd, "delta_s": [float(x) for x in Delta],
                "min": float(Delta.min()), "max": float(Delta.max()),
                "note": "conditional seed-level sensitivity interval; five aggregates, df=4; normality cannot be "
                        "assessed; NOT a replacement CI for the registered estimand"}
    reg_point = float(D.mean())
    rows = []
    for j, seed in enumerate(TRAIN_SEEDS):
        keep = [k for k in range(len(TRAIN_SEEDS)) if k != j]
        pt, lo4, hi4 = boot_two_way(D[:, keep], reps=reps)
        rows.append({"removed_seed": seed, "point": pt, "ci_low": lo4, "ci_high": hi4, "class": classify(lo4, hi4),
                     "abs_change_from_registered_point": abs(pt - reg_point)})
    out["C"] = {"rows": rows,
                "point_range": [min(r["point"] for r in rows), max(r["point"] for r in rows)],
                "max_abs_change": max(r["abs_change_from_registered_point"] for r in rows),
                "classes": sorted(set(r["class"] for r in rows)),
                "jackknife_se_cross_reference": sd / math.sqrt(len(Delta))}
    return out


# ----------------------------------------------------------------------------------------------
# pipeline
# ----------------------------------------------------------------------------------------------
def write_once(path, text):
    with open(path, "x", encoding="utf-8") as f:
        f.write(text)


def git_info(repo):
    def run(*a):
        try:
            return _git(repo, *a).stdout.strip()
        except Exception as e:  # provenance only
            return "unavailable: %s" % e
    return {"head": run("rev-parse", "HEAD"),
            "status_short_o7_and_x3a": run("status", "--short", "--", "research/analysis/x3a_o7",
                                            "research/confirmatory/X3-A")}


def _norm(p):
    """Resolved, case-normalised absolute path string (Windows-safe; symlinks/junctions and 8.3 names resolved)."""
    return os.path.normcase(str(Path(p).resolve()))


def _within(child, parent):
    c, p = _norm(child), _norm(parent)
    try:
        return os.path.commonpath([c, p]) == p
    except ValueError:                                   # different drives
        return False


def assert_output_isolation(repo, out_dir, official):
    """Output-namespace isolation (final gate repair 1).
    official=True may write ONLY to the canonical result directory <repo>/OUT_REL (and only after the
    registration/environment gates below). official=False may NOT write to the canonical O7 result location, nor
    anywhere inside the real repository this script lives in, nor inside the repository being analysed; it may
    write only to a directory under the system temporary directory, and only when the analysed tree is itself a
    temporary tree (synthetic data), so an un-gated 'unofficial' run can never be produced from the real frozen
    data or land in an official namespace."""
    canonical = Path(repo) / OUT_REL
    if official:
        if _norm(out_dir) != _norm(canonical):
            raise Stop("official output must be exactly %s, not %s" % (OUT_REL, out_dir))
        return
    tmp = tempfile.gettempdir()
    for canon in (canonical, REPO / OUT_REL):
        if _within(out_dir, canon) or _within(canon, out_dir):
            raise Stop("non-official run may not use the canonical O7 output location %s" % OUT_REL)
    for label, path in (("output directory", out_dir), ("analysed tree", repo)):
        if _within(path, REPO) or _within(REPO, path):
            raise Stop("non-official run: %s %s overlaps the real repository" % (label, path))
        if not _within(path, tmp):
            raise Stop("non-official run: %s %s is not under the temporary directory %s" % (label, path, tmp))


def run_pipeline(repo, out_dir, *, official, reps=B, trace=None, registered_commit=None):
    """Full O7 pipeline. `official` enables the git-lock and locked-environment checks (not applicable to the
    synthetic self-test, which uses a temporary tree). `trace` (list) receives ordered events for tests."""
    repo = Path(repo).resolve()
    assert_output_isolation(repo, out_dir, official)     # before anything is read or created
    ev = (trace.append if trace is not None else (lambda e: None))
    stamp = datetime.now(timezone.utc).isoformat()
    reg = load_registration(repo)
    tag_rec = None
    if official:
        tag_rec = assert_registration_tag(repo, reg, registered_commit)
        ev("registration_tag_ok")
        assert_registration_locked(repo)
        assert_environment(repo, reg)
    ev("environment_ok")
    prov = verify_provenance(repo, reg)
    ev("provenance_ok")
    spath = repo_file(repo, reg["sessions"]["path"])
    D, keyrec = load_cells(spath)
    if sha256(spath) != reg["sessions"]["sha256"]:
        raise Stop("sessions.csv changed while being read")
    ev("cells_loaded")
    r0 = boot_two_way(D, reps=reps)                      # R0 computed BEFORE the decision file is read
    ev("r0_computed")
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise Stop("output directory exists (write-once): %s" % out_dir)
    os.mkdir(out_dir)                                    # exclusive: raises if it already exists
    ev("out_dir_created")
    raw = repo_file(repo, reg["decision"]["path"]).read_bytes()
    if sha256_bytes(raw) != reg["decision"]["sha256"]:   # same bytes that are parsed are re-authenticated
        write_once(out_dir / "r0_record.json", json.dumps({"stage": "R0", "status": "ABORTED",
                   "reason": "decision file changed after provenance check"}, indent=2))
        raise Stop("decision file changed between provenance check and read")
    dec = json.loads(raw.decode("utf-8"))
    ev("decision_read")
    targets = {"point": dec["point"], "ci_low": dec["ci_low"], "ci_high": dec["ci_high"]}
    diffs = {"point": abs(r0[0] - targets["point"]), "ci_low": abs(r0[1] - targets["ci_low"]),
             "ci_high": abs(r0[2] - targets["ci_high"])}
    passed = all(v <= ABS_TOL for v in diffs.values())
    rec = {"stage": "R0", "status": "PASS" if passed else "FAIL", "abs_tol": ABS_TOL,
           "computed": {"point": r0[0], "ci_low": r0[1], "ci_high": r0[2]}, "registered": targets,
           "abs_diff": diffs, "key_set_record": keyrec, "provenance": prov, "started_utc": stamp,
           "official": official, "B": reps, "registered_commit": registered_commit, "registration_tag": tag_rec,
           "environment": {"python": sys.version, "numpy": np.__version__, "scipy": __import__("scipy").__version__,
                           "executable": sys.executable},
           "registration_sha256": sha256(repo / REG_REL),
           "script_sha256": sha256(__file__), "git": git_info(repo)}
    write_once(out_dir / "r0_record.json", json.dumps(rec, indent=2))
    if not passed:
        raise Stop("R0 FAILED (abs diffs %r); nothing else was run" % diffs)
    ev("r0_passed")
    res = analyses(D, reps=reps)
    res["registered_REG"] = {**targets, "class": dec["classification"], "note": "unchanged result of record"}
    res["r0_status"] = "PASS"
    write_once(out_dir / "x3a_o7_results.json", json.dumps(res, indent=2))
    lines = ["# X3-A O7 sensitivity results (secondary robustness evidence)", "",
             "R0: PASS (abs diffs %s). Registered result unchanged: point %.6f, CI [%.6f, %.6f], class %s." % (
                 diffs, targets["point"], targets["ci_low"], targets["ci_high"], dec["classification"]), "",
             "| Analysis | Point | 95% CI | Class |", "|---|---|---|---|",
             "| REG (registered) | %.4f | [%.4f, %.4f] | %s |" % (targets["point"], targets["ci_low"],
                                                                 targets["ci_high"], dec["classification"]),
             "| A persona-only | %.4f | [%.4f, %.4f] | %s |" % (res["A"]["point"], res["A"]["ci_low"],
                                                              res["A"]["ci_high"], res["A"]["class"]),
             "| B conditional seed-level (df=4) | %.4f | [%.4f, %.4f] | %s |" % (
                 res["B"]["point"], res["B"]["ci_low"], res["B"]["ci_high"], res["B"]["class"]), ""]
    lines += ["C leave-one-seed-out: " + "; ".join("-%d: %.4f [%.4f, %.4f] %s" % (
        r["removed_seed"], r["point"], r["ci_low"], r["ci_high"], r["class"]) for r in res["C"]["rows"]), ""]
    write_once(out_dir / "x3a_o7_report.md", "\n".join(lines))
    ev("abc_written")
    return "\n".join(lines)


def official_run(argv):
    rc = argv[argv.index("--registered-commit") + 1] if "--registered-commit" in argv[:-1] else None
    print(run_pipeline(REPO, REPO / OUT_REL, official=True, registered_commit=rc))


# ----------------------------------------------------------------------------------------------
# synthetic self-test (temporary tree only)
# ----------------------------------------------------------------------------------------------
SELFTEST_REPS = 200


def _make_world(root, *, perturb_decision=0.0):
    """Build a synthetic repository tree: sessions.csv, decision, two upstream manifests, registration."""
    root = Path(root)
    res = root / "research/confirmatory/X3-A/results"
    res.mkdir(parents=True)
    (root / "research/analysis/x3a_o7").mkdir(parents=True)
    rng = np.random.default_rng(7)
    with open(res / "sessions.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["condition", "training_seed", "stratum", "persona_id", "persona_index", "eval_seed", "mae"])
        for pi, p in enumerate(PERSONAS):
            for e in EVAL_SEEDS:
                w.writerow([COND_CS, "-", STRATUM, p, pi, e, "%.6f" % rng.normal(1.0, 0.1)])
            for s in TRAIN_SEEDS:
                for e in EVAL_SEEDS:
                    w.writerow([COND_PPO, s, STRATUM, p, pi, e, "%.6f" % rng.normal(1.0, 0.1)])
    D, _ = load_cells(res / "sessions.csv")
    pt, lo, hi = boot_two_way(D, reps=SELFTEST_REPS)
    (res / "x3a_decision.json").write_text(json.dumps(
        {"point": pt + perturb_decision, "ci_low": lo, "ci_high": hi, "classification": classify(lo, hi)}))
    (res / "gate_G-HARNESS.csv").write_text("gate,passed\nG,1\n")
    rel = lambda n: "research/confirmatory/X3-A/results/" + n
    hs = lambda n: sha256(res / n)
    run_m = {"status": "completed", "failures": [], "gate": {"name": "G-HARNESS", "passed": True},
             "outputs": [{"path": rel(n).replace("/", "\\"), "sha256": hs(n)} for n in ("sessions.csv", "gate_G-HARNESS.csv")]}
    ana_m = {"status": "completed", "failures": [], "gate": {},
             "outputs": [{"path": rel("x3a_decision.json"), "sha256": hs("x3a_decision.json")}]}
    (res / "manifest_X3-A-run.json").write_text(json.dumps(run_m))
    (res / "manifest_X3-A-analysis.json").write_text(json.dumps(ana_m))
    reg = {"registration_version": "1", "registration_tag": {"name": "prereg/T/v1"},
           "sessions": {"path": rel("sessions.csv"), "sha256": hs("sessions.csv")},
           "decision": {"path": rel("x3a_decision.json"), "sha256": hs("x3a_decision.json")},
           "lock": {},
           "upstream_manifests": [
               {"path": rel("manifest_X3-A-run.json"), "sha256": hs("manifest_X3-A-run.json"),
                "required_status": "completed", "required_gate": {"name": "G-HARNESS", "passed": True},
                "must_list_outputs": {rel("sessions.csv"): hs("sessions.csv")}},
               {"path": rel("manifest_X3-A-analysis.json"), "sha256": hs("manifest_X3-A-analysis.json"),
                "required_status": "completed", "required_gate": None,
                "must_list_outputs": {rel("x3a_decision.json"): hs("x3a_decision.json")}}]}
    (root / REG_REL).write_text(json.dumps(reg))
    return root, res


def selftest():
    import shutil

    def expect_stop(fn, needle, label):
        try:
            fn()
        except Stop as e:
            assert needle in str(e), "%s: wrong Stop reason: %s" % (label, e)
            return
        raise AssertionError("%s: not stopped" % label)

    base = Path(tempfile.mkdtemp(prefix="o7_selftest_"))
    try:
        # 1. happy path + event order (provenance before cells/R0/out_dir; decision read after R0)
        root, res = _make_world(base / "w1")
        trace = []
        run_pipeline(root, base / "w1_out", official=False, reps=SELFTEST_REPS, trace=trace)
        assert trace == ["environment_ok", "provenance_ok", "cells_loaded", "r0_computed", "out_dir_created",
                         "decision_read", "r0_passed", "abc_written"], trace
        assert sorted(p.name for p in (base / "w1_out").iterdir()) == \
            ["r0_record.json", "x3a_o7_report.md", "x3a_o7_results.json"]
        # 2. write-once: second run into the same directory is refused
        expect_stop(lambda: run_pipeline(root, base / "w1_out", official=False, reps=SELFTEST_REPS), "write-once", "rerun")
        # 3. altered decision SHA (file changed after registration): stops BEFORE the output directory exists
        root, res = _make_world(base / "w2")
        (res / "x3a_decision.json").write_text(json.dumps({"point": 0.0, "ci_low": -1, "ci_high": 1,
                                                          "classification": "Equivalent"}))
        expect_stop(lambda: run_pipeline(root, base / "w2_out", official=False, reps=SELFTEST_REPS),
                    "DECISION SHA-256 MISMATCH", "altered decision")
        assert not (base / "w2_out").exists()
        # 3b. registration itself carries a wrong decision hash
        root, res = _make_world(base / "w2b")
        reg = json.loads((root / REG_REL).read_text())
        reg["decision"]["sha256"] = "0" * 64
        (root / REG_REL).write_text(json.dumps(reg))
        expect_stop(lambda: run_pipeline(root, base / "w2b_out", official=False, reps=SELFTEST_REPS),
                    "DECISION SHA-256 MISMATCH", "registered decision hash wrong")
        # 4. altered upstream manifest
        root, res = _make_world(base / "w3")
        m = json.loads((res / "manifest_X3-A-run.json").read_text())
        m["deviations"] = ["edited"]
        (res / "manifest_X3-A-run.json").write_text(json.dumps(m))
        expect_stop(lambda: run_pipeline(root, base / "w3_out", official=False, reps=SELFTEST_REPS),
                    "UPSTREAM MANIFEST SHA-256 MISMATCH", "altered manifest")
        assert not (base / "w3_out").exists()
        # 5. altered upstream output (listed by the run manifest, not sessions/decision)
        root, res = _make_world(base / "w4")
        (res / "gate_G-HARNESS.csv").write_text("gate,passed\nG,0\n")
        expect_stop(lambda: run_pipeline(root, base / "w4_out", official=False, reps=SELFTEST_REPS),
                    "UPSTREAM OUTPUT CHANGED", "altered upstream output")
        assert not (base / "w4_out").exists()
        # 6. upstream manifest not completed / gate not passed (re-registered hashes, so only status/gate can fail)
        for label, mutate, needle in (("status", lambda d: d.update(status="failed"), "status"),
                                      ("gate", lambda d: d.update(gate={"name": "G-HARNESS", "passed": False}), "gate")):
            root, res = _make_world(base / ("w5" + label))
            mp = res / "manifest_X3-A-run.json"
            d = json.loads(mp.read_text())
            mutate(d)
            mp.write_text(json.dumps(d))
            reg = json.loads((root / REG_REL).read_text())
            reg["upstream_manifests"][0]["sha256"] = sha256(mp)
            (root / REG_REL).write_text(json.dumps(reg))
            expect_stop(lambda: run_pipeline(root, base / ("w5" + label + "_out"), official=False,
                                             reps=SELFTEST_REPS), needle, label)
        # 7. must-list output missing from the manifest
        root, res = _make_world(base / "w6")
        mp = res / "manifest_X3-A-analysis.json"
        d = json.loads(mp.read_text())
        d["outputs"] = []
        mp.write_text(json.dumps(d))
        reg = json.loads((root / REG_REL).read_text())
        reg["upstream_manifests"][1]["sha256"] = sha256(mp)
        (root / REG_REL).write_text(json.dumps(reg))
        expect_stop(lambda: run_pipeline(root, base / "w6_out", official=False, reps=SELFTEST_REPS),
                    "does not list", "missing must-list")
        # 8. R0 failure: registered decision (hash-authentic) differs from the recomputation -> record FAIL, no A/B/C
        root, res = _make_world(base / "w7", perturb_decision=1e-9)
        expect_stop(lambda: run_pipeline(root, base / "w7_out", official=False, reps=SELFTEST_REPS), "R0 FAILED", "R0 fail")
        assert sorted(p.name for p in (base / "w7_out").iterdir()) == ["r0_record.json"]
        assert json.loads((base / "w7_out" / "r0_record.json").read_text())["status"] == "FAIL"
        # 9. duplicate key and mechanics (independent loop reference for indexing/bootstrap)
        root, res = _make_world(base / "w8")
        D, _ = load_cells(res / "sessions.csv")
        assert D.shape == (40, 5)
        g = np.random.default_rng(42)
        st = []
        for _ in range(SELFTEST_REPS):
            pi = g.integers(0, 40, 40)
            si = g.integers(0, 5, 5)
            st.append(np.mean([D[i, j] for i in pi for j in si]))
        lo, hi = np.percentile(st, [2.5, 97.5])
        mine = boot_two_way(D, reps=SELFTEST_REPS)
        assert abs(mine[1] - lo) < 1e-12 and abs(mine[2] - hi) < 1e-12
        res_abc = analyses(D, reps=SELFTEST_REPS)
        assert set(res_abc) == {"A", "B", "C"} and len(res_abc["C"]["rows"]) == 5
        with open(res / "sessions.csv", "a", newline="") as f:
            csv.writer(f).writerow([COND_CS, "-", STRATUM, PERSONAS[0], 0, EVAL_SEEDS[0], "1.0"])
        expect_stop(lambda: load_cells(res / "sessions.csv"), "DUPLICATE KEY", "duplicate")
        # 10. official-only guards: git lock (untracked / modified / clean) and locked-environment refusal
        g = base / "gitrepo"
        (g / "research/analysis/x3a_o7").mkdir(parents=True)
        subprocess.run(["git", "-C", str(g), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(g), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(g), "config", "user.name", "t"], check=True)
        (g / REG_REL).write_bytes(b"{}")
        (g / SCRIPT_REL).write_bytes(b"x")
        expect_stop(lambda: assert_registration_locked(g), "not tracked", "untracked registration")
        subprocess.run(["git", "-C", str(g), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(g), "commit", "-q", "-m", "c"], check=True)
        assert_registration_locked(g)
        (g / REG_REL).write_bytes(b'{"x":1}')
        expect_stop(lambda: assert_registration_locked(g), "differs from HEAD", "modified registration")
        (g / "envs").mkdir()
        (g / "envs/a.json").write_bytes(b"a")
        fake = {"lock": {"lock_json": {"path": "envs/a.json", "sha256": "0" * 64},
                         "requirements": {"path": "envs/a.json", "sha256": "0" * 64}}}
        expect_stop(lambda: assert_environment(g, fake), "ENVIRONMENT FAILURE", "environment outside lock")
        # 11. immutable registration tag (final repair 1): tag identity, HEAD == tag commit, blob bytes
        NL = chr(10)

        def tagged_repo(name, kind="good", later=False):
            root = base / name
            (root / "research/analysis/x3a_o7").mkdir(parents=True)

            def g(*a):
                return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=True)
            g("init", "-q")
            g("config", "user.email", "t@t")
            g("config", "user.name", "t")
            (root / ".gitattributes").write_bytes(b"* -text" + NL.encode())
            reg = {"registration_tag": {"name": "prereg/T/v1"}}
            (root / REG_REL).write_bytes(json.dumps(reg).encode())
            (root / SCRIPT_REL).write_bytes(b"print(1)" + NL.encode())
            g("add", "-A")
            g("commit", "-q", "-m", "reg")
            c = g("rev-parse", "HEAD").stdout.strip()
            msg = (("X3-A O7 registration" + NL) + ("registration-commit: %s" % (c if kind != "wrongcommit" else "1" * 40))
                   + NL + ("registration-sha256: %s" % (sha256(root / REG_REL) if kind != "badhash" else "0" * 64))
                   + NL + ("script-sha256: %s" % sha256(root / SCRIPT_REL)))
            if kind == "notag":
                pass
            elif kind == "lightweight":
                g("tag", "prereg/T/v1")
            else:
                g("tag", "-a", "prereg/T/v1", "-m", msg)
            if later:
                g("commit", "-q", "--allow-empty", "-m", "later")
            return root, c, reg, root / SCRIPT_REL

        def check(root, c, reg, sp, needle, label):
            expect_stop(lambda: assert_registration_tag(root, reg, c, script_path=sp), needle, label)
        r_, c_, reg_, sp_ = tagged_repo("t_good")
        rec_ = assert_registration_tag(r_, reg_, c_, script_path=sp_)
        assert rec_["commit"] == c_ and len(rec_["tag_object"]) == 40
        check(*tagged_repo("t_notag", "notag"), "does not exist", "untagged")
        check(*tagged_repo("t_light", "lightweight"), "not an annotated", "lightweight tag")
        check(*tagged_repo("t_wrongmsg", "wrongcommit"), "message registration-commit", "tag message commit wrong")
        check(*tagged_repo("t_badhash", "badhash"), "!= tag message", "tag message hash wrong")
        check(*tagged_repo("t_later", later=True), "HEAD", "HEAD != tag commit")
        expect_stop(lambda: assert_registration_tag(r_, reg_, "2" * 40, script_path=sp_), "not the registered commit",
                    "wrong registered commit")
        expect_stop(lambda: assert_registration_tag(r_, reg_, c_[:12], script_path=sp_), "40-hex", "short commit")
        expect_stop(lambda: assert_registration_tag(r_, {}, c_, script_path=sp_), "registration_tag.name", "no tag name")
        expect_stop(lambda: assert_registration_tag(r_, {"registration_tag": {"name": "nope"}}, c_, script_path=sp_),
                    "does not exist", "other tag name")
        expect_stop(lambda: assert_registration_tag(r_, reg_, c_, script_path=r_ / "elsewhere.py"), "running script",
                    "script is not the registered file")
        (r_ / REG_REL).write_bytes((r_ / REG_REL).read_bytes() + b" ")
        expect_stop(lambda: assert_registration_tag(r_, reg_, c_, script_path=sp_), "working bytes differ",
                    "registration differs from tag blob")
        r2_, c2_, reg2_, sp2_ = tagged_repo("t_scriptdiff")
        sp2_.write_bytes(b"print(2)" + NL.encode())
        expect_stop(lambda: assert_registration_tag(r2_, reg2_, c2_, script_path=sp2_), "working bytes differ",
                    "script differs from tag blob")
        # the official pipeline refuses to start without a registered commit; no output directory is created
        rootw, _ = _make_world(base / "w_off")
        expect_stop(lambda: run_pipeline(rootw, rootw / OUT_REL, official=True, reps=SELFTEST_REPS,
                                         registered_commit=None), "40-hex", "official without commit")
        assert not (rootw / OUT_REL).exists()
        # 12. output-namespace isolation (final gate repair 1)
        rootw, _ = _make_world(base / "w_iso")
        canon_real = REPO / OUT_REL
        existed = canon_real.exists()

        def iso(out, label, needle):
            expect_stop(lambda: run_pipeline(rootw, out, official=False, reps=SELFTEST_REPS), needle, label)
        iso(rootw / OUT_REL, "non-official + canonical (analysed tree)", "canonical O7 output")
        iso(REPO / OUT_REL, "non-official + canonical (real repo)", "canonical O7 output")
        iso(REPO / OUT_REL / "sub", "non-official + inside canonical", "canonical O7 output")
        iso(REPO / "research" / "analysis" / "x3a_o7" / "results_unofficial", "non-official + real repo path", "real repository")
        iso(REPO / "elsewhere_out", "non-official + arbitrary repo path", "real repository")
        assert existed == canon_real.exists(), "canonical O7 result directory was created"
        # a non-official run must not analyse the real repository (real frozen data), even into a temp directory
        expect_stop(lambda: run_pipeline(REPO, base / "w_real_out", official=False, reps=SELFTEST_REPS),
                    "real repository", "non-official on real repo")
        assert not (base / "w_real_out").exists()
        # official output must be exactly the canonical location, and official still requires its gates
        expect_stop(lambda: run_pipeline(rootw, base / "w_iso_out2", official=True, reps=SELFTEST_REPS,
                                         registered_commit="0" * 40), "official output must be exactly", "official + temp out")
        tr = []
        expect_stop(lambda: run_pipeline(rootw, rootw / OUT_REL, official=True, reps=SELFTEST_REPS, trace=tr,
                                         registered_commit="0" * 40), "does not exist", "official + canonical: tag gate")
        assert tr == [] and not (rootw / OUT_REL).exists(), "official run got past the tag gate / created output"
        expect_stop(lambda: run_pipeline(rootw, rootw / OUT_REL, official=True, reps=SELFTEST_REPS,
                                         registered_commit=None), "40-hex", "official + canonical: no commit")
        # non-official + temporary synthetic directory still passes (positive control)
        run_pipeline(rootw, base / "w_iso_ok_out", official=False, reps=SELFTEST_REPS)
        assert (base / "w_iso_ok_out" / "r0_record.json").exists()
        print("SELFTEST OK (synthetic data only; temporary tree; no official output written)")
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    try:
        if "--selftest" in sys.argv:
            selftest()
        else:
            official_run(sys.argv)
    except Stop as e:
        print("STOP:", e)
        sys.exit(2)
