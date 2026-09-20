"""Run manifest v2 for NEW confirmatory runs and analyses. Stdlib only. Legacy run_manifest.py is untouched.

Addresses the validated findings in research/audit/CODEX_FINDINGS_VALIDATION.md (O5/O20, O8, O10/M3, O12, O17,
O19, M1) and the five post-Codex blocking repairs, with the minimum needed for new runs:

* exclusive, atomic creation: the output directory is created with os.mkdir (fails if it exists), a sentinel
  ``.run.lock`` is created with O_EXCL, the manifest is written to a temp file and moved with os.replace;
* the protocol manifest is PARSED and is authoritative (repair 2): its ``files`` map (path -> SHA-256) must equal
  the caller's dependency declarations exactly (no omissions, no extras), every declared file must equal both its
  recorded hash and its content at the protocol tag, its ``protocol`` field must match the protocol path, the
  entrypoint must be a declared file, every declared ``.py`` file must be covered by a declared code root (or be
  the entrypoint), and an optional ``code_roots`` list in the manifest must equal the supplied code roots. No
  automatic import discovery is attempted;
* the annotated tag exists, HEAD descends from the tag commit, the tag message contains the SHA-256 of the
  protocol and of the protocol manifest, both equal their content AT THE TAG;
* declared inputs and models: FULL SHA-256 (+ size), optional expected digests enforced (no prefix matching),
  re-hashed at finish();
* outputs (repair 3): finish() accepts only regular, non-symlink, single-link files that resolve beneath this
  run's exclusively-created out_dir (never the manifest/lock files); anything else aborts the run and raises;
* upstream linkage (repair 4 + final repair 2): link_upstream()/verify_completed() require a completed v2 manifest
  whose gate passed, whose SHA-256 equals the expected one when given, and whose recorded output hashes still
  match; the same validation is repeated at finish() (a change makes the downstream run ``failed``) and is
  RECURSIVE: every upstream's own recorded upstream links and outputs are revalidated down the whole chain, with
  cycles failing closed;
* alias rejection (final repair 3): after path normalisation ('\' -> '/', './', 'x/../') two protocol-manifest
  keys with the same logical path are refused, never silently collapsed;
* initialisation/abort safety (repair 5): an initial "started" manifest is written before any validation; any later
  failure writes an explicit "aborted" manifest; if no manifest can be written the partial run directory is
  removed, and if that also fails an ``INIT_FAILED_DO_NOT_USE.txt`` marker is left; abort() never raises because
  of a malformed partial-output path;
* working-tree state under declared code roots is inventoried with hashes and refuses the run unless allow_dirty;
* environment: installed-distribution list and hash; a declared lock must be satisfied by the installed set.

Tests: research/tools/test_run_manifest_v2.py (synthetic, temporary git repositories only).
Not in scope: locking down the interpreter, hashing every installed file, sandboxing, deterministic experiments.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.metadata as md
import json
import os
import platform
import posixpath
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

SCHEMA = "2.0"
DEFAULT_REPO = Path(__file__).resolve().parents[2]
LIMITATIONS = [
    "installed-package inventory is by distribution metadata, not a hash of every installed file",
    "git tag annotation is trusted as the registration record; the tool checks it matches file content at the tag",
    "no protection against a hostile local user editing the manifest after completion",
]


class ManifestError(RuntimeError):
    pass


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git(repo, *args, text=True, check=False):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=text, timeout=120)
    if check and r.returncode != 0:
        raise ManifestError("git %s failed: %s" % (" ".join(args), (r.stderr or "").strip()))
    return r


def installed_distributions() -> dict:
    out = {}
    for d in md.distributions():
        name = (d.metadata["Name"] or "").lower().replace("_", "-")
        if name:
            out[name] = d.version
    return dict(sorted(out.items()))


def parse_pins(requirements_path) -> dict:
    pins = {}
    for line in Path(requirements_path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip().rstrip("\\").strip()
        if "==" in line and not line.startswith("-"):
            name, ver = line.split("==", 1)
            pins[name.split("[")[0].strip().lower().replace("_", "-")] = ver.split(";")[0].strip()
    return pins


def _norm(rel) -> str:
    return str(rel).replace("\\", "/")


def _logical(rel) -> str:
    """Canonical logical spelling: separators unified, './' and 'x/../' collapsed."""
    return posixpath.normpath(_norm(rel))


def _repo_regular_file(repo: Path, rel) -> Path:
    """A repository-relative path that must resolve inside the repository to a regular file."""
    p = (repo / _norm(rel)).resolve()
    try:
        p.relative_to(repo)
    except ValueError:
        raise ManifestError("path escapes the repository: %s" % rel)
    if not p.is_file():
        raise ManifestError("not a regular file: %s" % rel)
    return p


# ---------------------------------------------------------------------------------------------------
# upstream validation (repair 4): one implementation used at link time, at finish() and by verify_completed()
# ---------------------------------------------------------------------------------------------------
def _validate_upstream(rec: dict, repo: Path, _stack=(), _done=None) -> None:
    """Validate one recorded upstream link AND, recursively, that upstream's own recorded upstream links.
    Cycles (a manifest reachable from itself) fail closed; already validated (path, sha) pairs are skipped."""
    done = set() if _done is None else _done
    mp = _repo_regular_file(repo, rec["manifest_path"])
    if mp in _stack:
        raise ManifestError("upstream cycle detected at %s" % rec["manifest_path"])
    raw = mp.read_bytes()
    if sha256_bytes(raw) != rec["manifest_sha256"]:
        raise ManifestError("upstream manifest changed: %s" % rec["manifest_path"])
    if (mp, rec["manifest_sha256"]) in done:
        return
    d = json.loads(raw.decode("utf-8"))
    if d.get("manifest_version") != SCHEMA or d.get("status") != "completed" or d.get("selftest"):
        raise ManifestError("upstream manifest not a completed v2 run: status=%s selftest=%s"
                            % (d.get("status"), d.get("selftest")))
    if d.get("failures"):
        raise ManifestError("upstream manifest records failures")
    if not (d.get("gate") or {}).get("passed"):
        raise ManifestError("upstream gate did not pass")
    listed = {_norm(o["path"]): o["sha256"] for o in d.get("outputs", [])}
    recorded = {_norm(o["path"]): o["sha256"] for o in rec["outputs"]}
    if listed != recorded:
        raise ManifestError("upstream output list differs from the list recorded at link time")
    for rel, want in listed.items():
        if sha256_file(_repo_regular_file(repo, rel)) != want:
            raise ManifestError("upstream output changed: %s" % rel)
    for nested in d.get("upstream", []):                 # the upstream's own recorded links (pinned by its hash)
        _validate_upstream(nested, repo, _stack + (mp,), done)
    done.add((mp, rec["manifest_sha256"]))


def verify_completed(manifest_path, repo=None, expected_sha256=None) -> dict:
    """Verify a completed v2 manifest: the manifest itself (completed, gate passed, no failures, outputs and their
    hashes unchanged), every direct upstream link, and recursively every upstream's own upstream links.
    If any manifest or output anywhere in the chain changed after completion, this raises.
    Returns the linkage record used for later revalidation."""
    repo = Path(repo or DEFAULT_REPO).resolve()
    p = Path(manifest_path).resolve()
    try:
        rel = str(p.relative_to(repo)).replace("\\", "/")
    except ValueError:
        raise ManifestError("manifest must be inside the repository: %s" % manifest_path)
    raw = p.read_bytes()
    sha = sha256_bytes(raw)
    if expected_sha256 is not None and sha != expected_sha256:
        raise ManifestError("manifest SHA-256 %s != expected %s" % (sha, expected_sha256))
    d = json.loads(raw.decode("utf-8"))
    rec = {"manifest_path": rel, "manifest_sha256": sha, "run_id": d.get("run_id"),
           "protocol_tag": (d.get("protocol") or {}).get("tag"), "outputs": d.get("outputs", [])}
    _validate_upstream(rec, repo)
    return rec


class Manifest:
    def __init__(self, run_id, out_dir, entrypoint, *, protocol_tag, protocol_path, protocol_manifest_path,
                 dependencies, code_roots=(), inputs=(), models=(), expected_digests=None, lock_requirements=None,
                 lock_id=None, seeds=None, allow_dirty=False, allowed_roots=None, repo=None, selftest=False):
        self.repo = Path(repo or DEFAULT_REPO).resolve()
        self.selftest = bool(selftest)
        self.closed = False
        self.created = False
        roots = allowed_roots or [self.repo / "research" / "analysis", self.repo / "research" / "confirmatory",
                                  self.repo / "research" / "evidence" / "runs"]
        self.out_dir = Path(out_dir).resolve()
        # checks that fail BEFORE any directory exists (nothing to clean up)
        if self.selftest:
            if Path(tempfile.gettempdir()).resolve() not in self.out_dir.parents:
                raise ManifestError("selftest output must be under the system temp directory")
        elif not any(r.resolve() in self.out_dir.parents for r in roots):
            raise ManifestError("output directory must be a new subdirectory of %s" % [str(r) for r in roots])
        self.expected = dict(expected_digests or {})
        self.path = self.out_dir / ("manifest_%s.json" % run_id)
        self.out_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.mkdir(self.out_dir)                      # exclusive creation: no check-then-create
        except FileExistsError as e:
            raise ManifestError("output directory already exists (write-once): %s" % self.out_dir) from e
        self.created = True
        self.d = {"manifest_version": SCHEMA, "run_id": run_id, "status": "started", "selftest": self.selftest,
                  "started_utc": _now(), "finished_utc": None, "protocol": {}, "code": {}, "environment": {},
                  "seeds": seeds or {}, "inputs": [], "models": [], "upstream": [], "keysets": [], "outputs": [],
                  "gate": {}, "failures": [], "deviations": [], "limitations": LIMITATIONS}
        try:
            fd = os.open(self.out_dir / ".run.lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, ("%s pid=%d\n" % (_now(), os.getpid())).encode())
            os.close(fd)
            self._write()                               # "started" is on disk before any validation can fail
            self._validate_protocol(protocol_tag, protocol_path, protocol_manifest_path, dependencies,
                                    entrypoint, code_roots)
            self._record_code(entrypoint, code_roots, allow_dirty)
            self._record_environment(lock_requirements, lock_id)
            for p in inputs:
                self.add_input(p)
            for role, p, seed in models:
                self.add_model(role, p, seed)
            self._write()
        except BaseException as exc:
            self._init_failure(exc)
            raise

    # ---- initialisation failure handling (repair 5) --------------------------------------------
    def _init_failure(self, exc):
        try:
            self.abort("initialisation failed: %s: %s" % (type(exc).__name__, exc))
            if json.loads(self.path.read_text(encoding="utf-8")).get("status") == "aborted":
                return
        except Exception:
            pass
        try:
            shutil.rmtree(self.out_dir)                 # we created this directory exclusively; remove the partial run
            return
        except Exception:
            pass
        try:
            (self.out_dir / "INIT_FAILED_DO_NOT_USE.txt").write_text(
                "initialisation failed (%s); this directory is NOT a valid run\n" % type(exc).__name__)
        except Exception:
            pass

    # ---- protocol / code / environment -------------------------------------------------------------
    def _rel(self, p):
        return str(Path(p).resolve().relative_to(self.repo)).replace("\\", "/")

    def _at_tag_sha(self, tag, rel):
        r = _git(self.repo, "show", "%s:%s" % (tag, rel), text=False)
        if r.returncode != 0:
            raise ManifestError("%s does not exist at tag %s" % (rel, tag))
        return sha256_bytes(r.stdout)

    def _validate_protocol(self, tag, protocol_path, manifest_path, dependencies, entrypoint, code_roots):
        if _git(self.repo, "cat-file", "-t", tag).stdout.strip() != "tag":
            raise ManifestError("%s is not an annotated tag" % tag)
        tag_commit = _git(self.repo, "rev-parse", "%s^{commit}" % tag, check=True).stdout.strip()
        head = _git(self.repo, "rev-parse", "HEAD", check=True).stdout.strip()
        if _git(self.repo, "merge-base", "--is-ancestor", tag_commit, head).returncode != 0:
            raise ManifestError("HEAD %s does not descend from tag commit %s" % (head, tag_commit))
        message = _git(self.repo, "tag", "-l", "--format=%(contents)", tag, check=True).stdout
        rec = {"tag": tag, "tag_commit": tag_commit, "head": head, "files": {}, "dependencies": []}
        for label, p in (("protocol", protocol_path), ("protocol_manifest", manifest_path)):
            rel, cur = self._rel(p), sha256_file(p)
            if cur != self._at_tag_sha(tag, rel):
                raise ManifestError("%s differs from its content at %s" % (rel, tag))
            if cur not in message:
                raise ManifestError("tag message of %s does not contain the SHA-256 of %s" % (tag, rel))
            rec["files"][label] = {"path": rel, "sha256": cur}
        # ---- the protocol manifest is authoritative (repair 2) ----
        pm = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        files = pm.get("files")
        if not isinstance(files, dict) or not files:
            raise ManifestError("protocol manifest has no 'files' map of declared dependencies")
        declared, aliases = {}, {}
        for k, v in files.items():
            logical = _logical(k)
            if logical.startswith("..") or logical.startswith("/") or (len(logical) > 1 and logical[1] == ":"):
                raise ManifestError("protocol manifest path is not repository-relative: %r" % k)
            if logical in aliases:
                raise ManifestError("protocol manifest declares the same logical path twice: %r and %r -> %s"
                                    % (aliases[logical], k, logical))
            aliases[logical] = k
            declared[logical] = v
        supplied = {self._rel(p) for p in dependencies}
        if len(supplied) != len(list(dependencies)):
            raise ManifestError("duplicate dependency declarations supplied")
        if set(declared) != supplied:
            raise ManifestError("dependency declarations differ from the protocol manifest: missing %s, extra %s"
                                % (sorted(set(declared) - supplied), sorted(supplied - set(declared))))
        if pm.get("protocol") and _norm(pm["protocol"]) != rec["files"]["protocol"]["path"]:
            raise ManifestError("protocol manifest names %s but %s was supplied"
                                % (pm["protocol"], rec["files"]["protocol"]["path"]))
        for rel, want in sorted(declared.items()):
            cur = sha256_file(_repo_regular_file(self.repo, rel))
            if cur != want:
                raise ManifestError("dependency %s hash %s != protocol manifest %s" % (rel, cur, want))
            if cur != self._at_tag_sha(tag, rel):
                raise ManifestError("dependency %s differs from its content at %s" % (rel, tag))
            rec["dependencies"].append({"path": rel, "sha256": cur})
        # code-root coverage
        ep_rel = self._rel(entrypoint)
        roots = [self._rel(r) for r in code_roots]
        if ep_rel not in declared:
            raise ManifestError("entrypoint %s is not a declared dependency of the protocol manifest" % ep_rel)
        if "code_roots" in pm and sorted(_norm(r) for r in pm["code_roots"]) != sorted(roots):
            raise ManifestError("supplied code roots differ from the protocol manifest's code_roots")
        covered = lambda rel: rel == ep_rel or any(rel == r or rel.startswith(r.rstrip("/") + "/") for r in roots)
        uncovered = sorted(r for r in declared if r.endswith(".py") and not covered(r))
        if uncovered:
            raise ManifestError("declared executable files not covered by a code root: %s" % uncovered)
        self.d["protocol"] = rec

    def _record_code(self, entrypoint, code_roots, allow_dirty):
        ep = Path(entrypoint).resolve()
        roots = [self._rel(r) for r in code_roots] + [self._rel(ep)]
        st = _git(self.repo, "status", "--porcelain", "--untracked-files=all", "--", *roots, check=True).stdout
        dirty = []
        for line in st.splitlines():
            rel = line[3:].strip().strip('"')
            f = self.repo / rel
            dirty.append({"status": line[:2], "path": rel, "sha256": sha256_file(f) if f.is_file() else None})
        if dirty and not allow_dirty:
            raise ManifestError("modified/untracked files under code roots: %s" % [d["path"] for d in dirty])
        self.d["code"] = {"git_commit": _git(self.repo, "rev-parse", "HEAD", check=True).stdout.strip(),
                          "entrypoint": self._rel(ep), "entrypoint_sha256": sha256_file(ep),
                          "code_roots": roots, "dirty_files_under_code_roots": dirty, "allow_dirty": allow_dirty,
                          "command_line": " ".join(sys.argv)}

    def _record_environment(self, lock_requirements, lock_id):
        dists = installed_distributions()
        env = {"os": platform.platform(), "python": sys.version.replace("\n", " "), "executable": sys.executable,
               "distributions": dists, "distributions_sha256": sha256_bytes(json.dumps(dists).encode()),
               "lock_id": lock_id, "lock_requirements_sha256": None, "lock_mismatches": [], "extras_not_in_lock": []}
        if lock_requirements:
            pins = parse_pins(lock_requirements)
            env["lock_requirements_sha256"] = sha256_file(lock_requirements)
            env["lock_mismatches"] = ["%s pinned %s installed %s" % (n, v, dists.get(n))
                                      for n, v in pins.items() if dists.get(n) != v]
            env["extras_not_in_lock"] = sorted(set(dists) - set(pins))
            if env["lock_mismatches"]:
                self.d["environment"] = env
                raise ManifestError("installed set does not satisfy the lock: %s" % env["lock_mismatches"][:5])
        self.d["environment"] = env

    # ---- declared bindings ---------------------------------------------------------------------------
    def _bind(self, p):
        p = Path(p).resolve()
        rel = self._rel(p)
        digest = sha256_file(p)
        want = self.expected.get(rel)
        if want is not None and want != digest:                     # full digest, no prefix matching
            raise ManifestError("%s digest %s != expected %s" % (rel, digest, want))
        return {"path": rel, "sha256_before": digest, "sha256_after": None, "bytes": p.stat().st_size}

    def add_input(self, p):
        self.d["inputs"].append(self._bind(p))
        self._write()

    def add_model(self, role, p, training_seed=None):
        rec = self._bind(p)
        rec.update({"role": role, "training_seed": training_seed})
        self.d["models"].append(rec)
        self._write()

    def link_upstream(self, upstream_manifest_path, expected_sha256=None):
        self.d["upstream"].append(verify_completed(upstream_manifest_path, self.repo, expected_sha256))
        self._write()

    def assert_keyset(self, label, observed, expected):
        obs, exp = set(observed), set(expected)
        rec = {"label": label, "expected_n": len(exp), "observed_n": len(obs),
               "missing": sorted(map(str, exp - obs))[:20], "unexpected": sorted(map(str, obs - exp))[:20]}
        self.d["keysets"].append(rec)
        if exp != obs:
            self.d["failures"].append("KEYSET MISMATCH %s" % label)
            self._write()
            raise ManifestError("key-set mismatch for %s: %s" % (label, rec))
        self._write()

    def set_gate(self, name, passed, details=""):
        self.d["gate"] = {"name": name, "passed": bool(passed), "details": details}

    def note(self, text, failure=False):
        self.d["failures" if failure else "deviations"].append(text)

    # ---- outputs (repair 3) --------------------------------------------------------------------------
    def _check_outputs(self, outputs):
        recs, seen = [], set()
        for p in outputs:
            pp = Path(p)
            try:
                rp = pp.resolve(strict=True)
            except (OSError, RuntimeError) as e:
                raise ManifestError("declared output does not exist: %s (%s)" % (p, e))
            if self.out_dir not in rp.parents:
                raise ManifestError("output %s is outside this run's directory %s" % (p, self.out_dir))
            if rp.name == self.path.name or rp.name == ".run.lock" or rp.name.startswith("."):
                raise ManifestError("manifest/lock/hidden files cannot be declared as outputs: %s" % p)
            st = os.lstat(pp)
            if pp.is_symlink() or not rp.is_file() or st.st_nlink != 1:
                raise ManifestError("output %s is not a regular, single-link, non-symlink file" % p)
            if rp in seen:
                raise ManifestError("output declared twice: %s" % p)
            seen.add(rp)
            try:
                path = str(rp.relative_to(self.repo)).replace("\\", "/")
            except ValueError:
                path = str(rp)
            recs.append({"path": path, "run_relative": str(rp.relative_to(self.out_dir)).replace("\\", "/"),
                         "sha256": sha256_file(rp)})
        return recs

    # ---- lifecycle -----------------------------------------------------------------------------------
    def finish(self, outputs):
        try:
            recs = self._check_outputs(outputs)
        except ManifestError as exc:
            self.abort("invalid output declaration: %s" % exc)
            raise
        for rec in self.d["inputs"] + self.d["models"]:
            try:
                rec["sha256_after"] = sha256_file(self.repo / rec["path"])
            except OSError as exc:
                rec["sha256_after"] = None
                self.d["failures"].append("INPUT UNREADABLE: %s (%s)" % (rec["path"], exc))
                continue
            if rec["sha256_after"] != rec["sha256_before"]:
                self.d["failures"].append("INPUT CHANGED: %s" % rec["path"])
        for up in self.d["upstream"]:                    # repair 4: revalidate, not merely remember
            try:
                _validate_upstream(up, self.repo)
                up["revalidated_at_finish"] = True
            except (ManifestError, OSError, ValueError, KeyError) as exc:
                up["revalidated_at_finish"] = False
                self.d["failures"].append("UPSTREAM INVALID AT FINISH: %s: %s" % (up.get("manifest_path"), exc))
        self.d["outputs"] = recs
        if not self.d["gate"]:
            self.d["failures"].append("no gate recorded")
        elif not self.d["gate"]["passed"]:
            self.d["failures"].append("gate %s did not pass" % self.d["gate"]["name"])
        self.d["status"] = "failed" if self.d["failures"] else "completed"
        self._close()
        return self.d["status"]

    def abort(self, reason, partial_outputs=()):
        """Never raises because of a malformed partial-output path or an unwritable manifest."""
        if self.closed:
            return
        self.d.setdefault("failures", []).append("ABORTED: %s" % reason)
        partial = []
        for p in partial_outputs:
            try:
                pp = Path(p)
                entry = {"path": str(p)}
                if pp.is_file():
                    entry["sha256"] = sha256_file(pp)
                try:
                    entry["path"] = str(pp.resolve().relative_to(self.repo)).replace("\\", "/")
                except ValueError:
                    entry["note"] = "outside the repository or malformed"
                partial.append(entry)
            except Exception as exc:                 # malformed path etc.: record and continue
                partial.append({"path": repr(p), "error": "%s: %s" % (type(exc).__name__, exc)})
        self.d["outputs_partial"] = partial
        self.d["status"] = "aborted"
        try:
            self._close()
        except Exception:
            self.closed = True
            try:
                (self.out_dir / "ABORTED_MANIFEST_UNWRITABLE.txt").write_text("run aborted: %s\n" % reason)
            except Exception:
                pass

    def _close(self):
        self.d["finished_utc"] = _now()
        self.closed = True
        self._write()

    def _write(self):
        tmp = self.out_dir / (".%s.tmp" % self.path.name)
        tmp.write_text(json.dumps(self.d, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)                                   # atomic on the same volume

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is not None and not self.closed:
            self.abort("%s: %s\n%s" % (et.__name__, ev, "".join(traceback.format_tb(tb))[-1500:]))
        return False


if __name__ == "__main__":
    print("library module; tests: python research/tools/test_run_manifest_v2.py")
