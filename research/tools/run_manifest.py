"""Run-manifest helper for new (non-frozen) analyses. Stdlib only.

Implements the Phase-1 subset of research/audit/RUN_MANIFEST_SPEC.md
(schema "1.0-phase1", see research/audit/PHASE1_PREFLIGHT_DECISION_MEMO.md section 2).

Rules enforced:
* every output path must be under research/analysis/ (allow-list) and must not already exist
  (only the manifest itself may be rewritten, by this helper, at finish());
* every input file is hashed at start() and again at finish(); a change is recorded as a failure;
* the environment (Python, package metadata + imported version/file, site-packages listing hash)
  is recorded before and after; a listing change is recorded as a failure;
* nothing in the project is imported or executed by this module.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib
import importlib.metadata as md
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOWED_ROOTS = [(REPO / "research" / "analysis").resolve(), (REPO / "research" / "confirmatory").resolve(), (REPO / "research" / "preregistration").resolve()]
ALLOWED_OUT = ALLOWED_ROOTS[0]
PKGS = ["numpy", "pandas", "scipy", "scikit-learn", "torch", "stable-baselines3",
        "gymnasium", "sentence-transformers", "transformers", "faiss-cpu", "PyYAML"]
MODULE_OF = {"scikit-learn": "sklearn", "stable-baselines3": "stable_baselines3",
             "sentence-transformers": "sentence_transformers", "faiss-cpu": "faiss",
             "PyYAML": "yaml"}


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git(*args) -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                              timeout=60).stdout.strip()
    except Exception as exc:  # pragma: no cover
        return f"ERROR:{exc}"


def site_packages_listing_sha256() -> str:
    sp = Path(sys.prefix) / "Lib" / "site-packages"
    if not sp.is_dir():
        sp = next((Path(p) for p in sys.path if p.endswith("site-packages")), sp)
    rows = []
    for e in sorted(os.scandir(sp), key=lambda x: x.name):
        st = e.stat()
        rows.append(f"{e.name}\t{st.st_size if e.is_file() else -1}\t{st.st_mtime_ns}")
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def package_probe() -> dict:
    out = {}
    for name in PKGS:
        rec = {"metadata": None, "module_version": None, "module_file": None}
        try:
            rec["metadata"] = md.version(name)
        except Exception:
            pass
        modname = MODULE_OF.get(name, name)
        try:
            m = importlib.import_module(modname)
            rec["module_version"] = getattr(m, "__version__", None)
            rec["module_file"] = getattr(m, "__file__", None)
        except Exception as exc:
            rec["module_version"] = f"IMPORT_FAILED:{type(exc).__name__}"
        out[name] = rec
    return out


def hardware() -> dict:
    ram = None
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
        s = MS()
        s.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
        ram = round(s.ullTotalPhys / 2**30, 1)
    except Exception:
        pass
    return {"cpu": platform.processor(), "cores": os.cpu_count(), "ram_gb": ram, "gpu": None}


class Manifest:
    def __init__(self, analysis_id: str, out_dir, entrypoint: str, config_path=None,
                 note_path=None, seeds=None, non_locked_reason="unlocked .venv; see environment block",
                 gate=None, protocol=None, lock_id=None, env_lock_sha256=None):
        self.out_dir = Path(out_dir).resolve()
        if not any(r in self.out_dir.parents or r == self.out_dir for r in ALLOWED_ROOTS):
            raise ValueError(f"outputs must be under one of {[str(r) for r in ALLOWED_ROOTS]}: {self.out_dir}")
        self.path = self.out_dir / f"manifest_{analysis_id}.json"
        if self.path.exists():
            raise FileExistsError(f"refusing to overwrite {self.path}")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.d = {"manifest_version": "1.0-phase1", "analysis_id": analysis_id, "status": "started",
                  "started_utc": _now(), "finished_utc": None,
                  "protocol": {"type": "phase1_preflight_note",
                               "note_path": str(note_path) if note_path else None,
                               "note_sha256": sha256_file(note_path) if note_path else None},
                  "code": {}, "config": {}, "environment": {}, "seeds": seeds or {},
                  "inputs": [], "models": [], "outputs": [], "gate": gate or {}, "deviations": [],
                  "failures": []}
        if protocol:
            self.d["protocol"] = protocol
        ep = Path(entrypoint).resolve()
        status = _git("status", "--porcelain")
        self.d["code"] = {"git_commit": _git("rev-parse", "HEAD"),
                          "git_tags_at_head": [t for t in _git("tag", "--points-at", "HEAD").split() if t],
                          "git_dirty": bool(status), "dirty_diff_sha256": hashlib.sha256(
                              _git("diff", "HEAD").encode()).hexdigest(),
                          "entrypoint": str(ep.relative_to(REPO)) if REPO in ep.parents else str(ep),
                          "entrypoint_sha256": sha256_file(ep), "command_line": " ".join(sys.argv)}
        if config_path:
            cp = Path(config_path).resolve()
            self.d["config"] = {"config_path": str(cp.relative_to(REPO)), "config_sha256": sha256_file(cp)}
        self.d["environment"] = {
            "lock_id": lock_id, "env_lock_sha256": env_lock_sha256, "non_locked_reason": (None if lock_id else non_locked_reason),
            "os": platform.platform(), "python": sys.version.replace("\n", " "),
            "executable": sys.executable, "packages": package_probe(),
            "site_packages_listing_sha256_before": site_packages_listing_sha256(),
            "site_packages_listing_sha256_after": None, "hardware": hardware(),
            "env_flags": {k: os.environ.get(k) for k in
                          ("PYTHONDONTWRITEBYTECODE", "HF_HUB_OFFLINE", "WANDB_MODE")}}
        for name, rec in self.d["environment"]["packages"].items():
            if rec["metadata"] and rec["module_version"] and not str(rec["module_version"]).startswith("IMPORT") \
                    and rec["metadata"] != rec["module_version"] and not str(rec["module_version"]).startswith(rec["metadata"]):
                self.d["deviations"].append(f"version disagreement for {name}: metadata {rec['metadata']} vs module {rec['module_version']}")
        self._write()

    def add_inputs(self, paths):
        for p in paths:
            p = Path(p).resolve()
            self.d["inputs"].append({"path": str(p.relative_to(REPO)), "sha256_before": sha256_file(p),
                                     "sha256_after": None})
        self._write()

    def add_model(self, role, path, training_seed=None):
        p = Path(path).resolve()
        self.d["models"].append({"role": role, "path": str(p.relative_to(REPO)),
                                 "sha256": sha256_file(p), "training_seed": training_seed})
        self._write()

    def note(self, text, failure=False):
        self.d["failures" if failure else "deviations"].append(text)

    def set_gate(self, name, passed, details=""):
        self.d["gate"] = {"name": name, "passed": passed, "details": details}

    def finish(self, outputs, status="completed"):
        for i in self.d["inputs"]:
            i["sha256_after"] = sha256_file(REPO / i["path"])
            if i["sha256_after"] != i["sha256_before"]:
                self.d["failures"].append(f"INPUT CHANGED: {i['path']}")
        after = site_packages_listing_sha256()
        self.d["environment"]["site_packages_listing_sha256_after"] = after
        if after != self.d["environment"]["site_packages_listing_sha256_before"]:
            self.d["failures"].append("site-packages listing changed during the run")
        self.d["outputs"] = []
        for p in outputs:
            p = Path(p).resolve()
            self.d["outputs"].append({"path": str(p.relative_to(REPO)), "sha256": sha256_file(p)})
        self.d["finished_utc"] = _now()
        self.d["status"] = "failed" if self.d["failures"] else status
        self._write()
        return self.d["status"]

    def _write(self):
        self.path.write_text(json.dumps(self.d, indent=2, sort_keys=False), encoding="utf-8")


def write_new(path, text: str, encoding="utf-8"):
    """Create a new file under research/analysis/; refuse to overwrite or to leave the allow-list."""
    p = Path(path).resolve()
    if not any(r in p.parents for r in ALLOWED_ROOTS):
        raise ValueError(f"outside allow-list: {p}")
    if p.exists():
        raise FileExistsError(f"refusing to overwrite {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding=encoding, newline="\n")
    return p
