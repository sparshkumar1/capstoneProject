"""
PrepAIred — Single agentic launcher.

Starts all required services in the correct order:
  1. Evaluator API        (port 5000)
  2. Qwen Microservice    (port 8001)  — optional, skipped if model not found
  3. Backend API          (port 8000)
  4. Frontend dev server  (port 5173)  — optional, skipped if npm not found

Usage:
    python launch.py                  # start all services
    python launch.py --no-qwen        # skip Qwen (saves VRAM)
    python launch.py --no-frontend    # API-only mode
    python launch.py --backend-only   # only ports 5000 + 8000

All services write logs to ./logs/<service>.log
Ctrl-C shuts everything down cleanly.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
import signal
from pathlib import Path

ROOT   = Path(__file__).resolve().parent
LOGS   = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

PYTHON = sys.executable
NPM = "npm.cmd" if os.name == "nt" else "npm"

# ── Service definitions ────────────────────────────────────────────────────────

SERVICES: list[dict] = [
    {
        "name":    "evaluator",
        "port":    5000,
        "cwd":     ROOT / "services" / "evaluator",
        "cmd":     [PYTHON, "app.py"],
        "ready_msg": "Uvicorn running",
        "ready_markers": ["Uvicorn running", "Running on http://"],
        "optional": False,
    },
    {
        "name":    "qwen",
        "port":    8001,
        "cwd":     ROOT / "services" / "qwen",
        "cmd":     [PYTHON, "-m", "uvicorn", "app:app", "--port", "8001", "--host", "0.0.0.0"],
        "ready_msg": "Application startup complete",
        "optional": True,
        "flag":    "no_qwen",
    },
    {
        "name":    "backend",
        "port":    8000,
        "cwd":     ROOT / "apps" / "backend",
        "cmd":     [PYTHON, "-m", "uvicorn", "main:app", "--reload", "--port", "8000", "--host", "0.0.0.0"],
        "ready_msg": "Application startup complete",
        "optional": False,
    },
    {
        "name":    "frontend",
        "port":    5173,
        "cwd":     ROOT / "apps" / "web",
        "cmd":     [NPM, "run", "dev"],
        "ready_msg": "Local:",
        "optional": True,
        "flag":    "no_frontend",
    },
]

_procs: list[subprocess.Popen] = []


def _log_path(name: str) -> Path:
    return LOGS / f"{name}.log"


def _start(svc: dict, flags: argparse.Namespace) -> subprocess.Popen | None:
    flag = svc.get("flag")
    if flag and getattr(flags, flag, False):
        print(f"  [skip] {svc['name']} (--{flag.replace('_', '-')} set)")
        return None

    cwd = svc["cwd"]
    if not cwd.exists():
        if svc["optional"]:
            print(f"  [skip] {svc['name']} — directory not found: {cwd}")
            return None
        print(f"  [ERROR] Required service dir missing: {cwd}")
        sys.exit(1)

    log = open(_log_path(svc["name"]), "w", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(ROOT)}

    print(f"  [{svc['name']}] starting on port {svc['port']}  (log: logs/{svc['name']}.log)")
    proc = subprocess.Popen(
        svc["cmd"],
        cwd=str(cwd),
        stdout=log,
        stderr=subprocess.STDOUT,
        env=env,
    )
    return proc


def _extract_frontend_url(log_content: str) -> str | None:
    clean = re.sub(r"\x1b\[[0-9;]*m", "", log_content)
    match = re.search(r"(https?://(?:localhost|127\.0\.0\.1):\d+)", clean, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1).rstrip("/")


def _wait_ready(svc: dict, proc: subprocess.Popen, timeout: int = 30) -> bool:
    """Poll the log for the ready message."""
    log_path = _log_path(svc["name"])
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            print(f"  [ERROR] {svc['name']} exited early (code {proc.returncode})")
            return False
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8", errors="ignore")
            clean_content = re.sub(r"\x1b\[[0-9;]*m", "", content)
            if svc["name"] == "frontend":
                detected_url = _extract_frontend_url(clean_content)
                if detected_url:
                    svc["detected_url"] = detected_url
                    port_match = re.search(r":(\d+)$", detected_url)
                    if port_match:
                        svc["detected_port"] = int(port_match.group(1))
                        return True

            markers = svc.get("ready_markers") or [svc["ready_msg"]]
            if any(marker.lower() in clean_content.lower() for marker in markers):
                return True
        time.sleep(0.5)
    return False  # timed out — still treat as started


def _shutdown(signum=None, frame=None):
    print("\n\nShutting down PrepAIred services...")
    for p in reversed(_procs):
        try:
            p.terminate()
        except Exception:
            pass
    for p in reversed(_procs):
        try:
            p.wait(timeout=5)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print("All services stopped. Goodbye.")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="PrepAIred unified launcher")
    parser.add_argument("--no-qwen",     action="store_true", help="Skip Qwen microservice (saves VRAM)")
    parser.add_argument("--no-frontend", action="store_true", help="Skip npm dev server")
    parser.add_argument("--backend-only",action="store_true", help="Only start evaluator + backend")
    args = parser.parse_args()

    if args.backend_only:
        args.no_qwen     = True
        args.no_frontend = True

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    print("=" * 60)
    print("  PrepAIred — Adaptive Interview System")
    print("=" * 60)
    print()
    print("Starting services:")

    for svc in SERVICES:
        proc = _start(svc, args)
        if proc is None:
            continue
        _procs.append(proc)
        # Small stagger so ports don't collide during startup
        time.sleep(1.5)

    print()
    print("Waiting for services to become ready...")
    started_services = [s for s in SERVICES if not (s.get("flag") and getattr(args, s["flag"], False))]
    for svc, proc in zip(started_services, _procs):
        ok = _wait_ready(svc, proc, timeout=45)
        status = "ready" if ok else "starting (check log)"
        shown_port = svc.get("detected_port", svc["port"])
        print(f"  [{svc['name']}:{shown_port}] {status}")

    print()
    print("=" * 60)
    print("  PrepAIred is running:")
    print("   Backend API  →  http://localhost:8000")
    print("   Evaluator    →  http://localhost:5000")
    if not getattr(args, "no_qwen", False):
        print("   Qwen LLM     →  http://localhost:8001")
    if not getattr(args, "no_frontend", False):
        frontend_svc = next((s for s in started_services if s.get("name") == "frontend"), None)
        frontend_url = frontend_svc.get("detected_url") if frontend_svc else None
        print(f"   Frontend     →  {frontend_url or 'http://localhost:5173'}")
    print()
    print("  Press Ctrl-C to stop all services.")
    print("=" * 60)

    # Keep main thread alive — services run as subprocesses
    try:
        while True:
            # Auto-restart a crashed non-optional service
            for i, (svc, proc) in enumerate(
                zip([s for s in SERVICES if s.get("flag") not in (None, "")], _procs)
            ):
                if proc.poll() is not None and not svc.get("optional"):
                    print(f"  [WARN] {svc['name']} crashed — restarting...")
                    new_proc = _start(svc, args)
                    if new_proc:
                        _procs[i] = new_proc
            time.sleep(5)
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()
