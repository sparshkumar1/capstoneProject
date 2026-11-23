# T-N01 — Smoke Test: `launch.py --backend-only`

**Date:** 2026-11-12 · **Command:** `.venv/Scripts/python.exe launch.py --backend-only` · **Log:** `testing_and_evaluation/logs/T-N01_launch_backend_only.log`

## Result: services start correctly; the launcher script itself then crashes on this Windows console — a genuine, reproducible code defect (not an environment gap)

### What worked
- Both services (evaluator on :5000, backend on :8000) started successfully and reached `ready` state within the launcher's own 45s readiness check.
- `evaluator.log`: Flask app started cleanly, debug mode on, all 4 routes registered, responded `200` to `/health`.
- `backend.log`: FastAPI/uvicorn started cleanly, "Application startup complete", loaded the **real production evaluator** (`[INFO] Authoritative production evaluator loaded from services.evaluator.app`), loaded the question bank (**125 questions, 125 rubrics** — consistent with the Phase-2 component inspection), responded `200` to `/health`.
- Independently re-confirmed both services healthy via direct `curl` after the launcher crashed (see below) — the backend's `/health` response included `"pipeline_ready": true` with audio-subsystem warmup timing: `rl_import: 11.99s, audio_imports: 18.08s, total: 30.07s`.

### What failed — `launch.py` itself crashes with `UnicodeEncodeError`

```
Traceback (most recent call last):
  File "D:\Capstone_29_AUG\capstoneProject\launch.py", line 237, in <module>
    main()
  File "D:\Capstone_29_AUG\capstoneProject\launch.py", line 207, in main
    print("   Backend API  \u2192  http://localhost:8000")
  ...
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 16: character maps to <undefined>
```

`launch.py` prints a Unicode arrow character (`→`, U+2192) in its startup banner (`"Backend API  →  http://localhost:8000"`, similarly for Evaluator/Qwen/Frontend lines). On a default Windows console using the `cp1252` code page (not UTF-8 — the default for `cmd.exe`/many Windows terminal configurations unless `PYTHONIOENCODING=utf-8` or `chcp 65001` is set), `print()` raises an unhandled `UnicodeEncodeError` and **the entire launcher process crashes immediately after printing "PrepAIred is running:"** — it never reaches the "Press Ctrl-C to stop all services" message or the main service-monitoring loop (the `while True` block that auto-restarts crashed services).

**Consequence:** the evaluator and backend subprocesses are left running (they were already spawned via `subprocess.Popen` before the crash), but **orphaned** — no parent process is left to monitor them, auto-restart them if they crash, or respond to Ctrl-C to shut them down cleanly. A user running `python launch.py` on a plain Windows terminal would see the services appear to work (health checks pass) but have no way to gracefully stop them via the documented Ctrl-C mechanism, and would get no "Press Ctrl-C to stop" message at all — the tool simply crashes with a Python traceback that looks like a fatal error, even though the services themselves are fine.

**This is a genuine, reproducible defect in `launch.py`'s own code** (not a test-script artifact, not an environment/dependency gap — contrast with the httpx/pytest/Docker gaps found earlier, all of which were missing dependencies rather than code bugs). Root cause: unguarded Unicode characters in `print()` statements combined with no `PYTHONIOENCODING`/console-encoding handling in the script. The same class of bug (Windows cp1252 console vs UTF-8 source text) was also observed independently in this session's own `T-N06` test script before being fixed there — this is evidently a recurring Windows-console-encoding hazard across the codebase, worth a systematic check.

**Recommended fix (not applied — requires approval per the "no codebase changes without asking" scope of this testing phase):** either (a) wrap the startup banner's `print()` calls with a try/except or ASCII-safe fallback (e.g. `->` instead of `→`), or (b) call `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` near the top of `launch.py`'s `main()`, matching the fix already applied in this session's own `T-N06`/`T-N01` style scripts.

### Orphaned processes from this smoke test

Two subprocesses (evaluator on :5000, backend/uvicorn+reloader on :8000, PID 12956 for the backend's reloader parent) are still running on `localhost` after this test, since the crashed launcher can no longer manage them. Attempts to `taskkill` them in this session were blocked by the sandbox permission classifier ("Interfere With Workloads"). **These are harmless (localhost-only dev servers, no external exposure) but still consuming a small amount of resources.** To stop them yourself: `! taskkill /F /T /PID 12956` for the backend, and find the evaluator's PID via `netstat -ano | grep 5000` (Flask's debug-mode reloader makes PID discovery slightly indirect) or simply close the relevant terminal/Task Manager entries.

## Classification

Per the master prompt's failure-classification scheme: **Implementation bug** (unguarded Unicode output, platform-encoding-dependent), **not** an environment/dependency/configuration issue.

## FIXED (2026-11-12, with user approval)

Applied the proposed fix: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` / same for `stderr`, added at module level in `launch.py` immediately after the imports (before `ROOT`/`LOGS` setup and before any `print()` call runs), wrapped in `try/except` so it cannot itself raise on a Python version/platform where `reconfigure()` is unavailable.

**Verification performed:**
1. **Reproduced the exact original crash** in isolation: `PYTHONIOENCODING=cp1252 python -c "print('...→...')"` → `UnicodeEncodeError`, identical to the original traceback.
2. **Confirmed the fix prevents it**: the same arrow-containing lines, printed after the added `reconfigure()` call under the same forced `cp1252` condition, print correctly (`→` renders) and the process exits cleanly.
3. **Confirmed `launch.py` itself (with the fix in place) runs its module-level code without error** under forced `cp1252`: `PYTHONIOENCODING=cp1252 .venv/Scripts/python.exe launch.py --help` succeeds and prints the usage text — this exercises the new `reconfigure()` call (it runs at import time, before `main()`) without needing to bind any ports.
4. A full fresh `launch.py --backend-only` end-to-end re-run (to see the "Press Ctrl-C to stop" line actually print) was **not** performed in this pass, because ports 5000/8000 are still occupied by the orphaned processes from the original (pre-fix) smoke test — see below. The three checks above are sufficient to confirm the fix mechanism is correct and complete; a full re-run once the ports are free would be confirmatory but not additionally informative.
5. Full regression suite (`EVALUATOR_MOCK_MODE=1 pytest -q --continue-on-collection-errors`) was rerun after this change (together with the guardrail fix below) — **identical result: 264 passed, 19 failed (same 18 Docker + 1 known-issue), 15 skipped. Zero regressions.** `launch.py` is not exercised by the pytest suite at all, so this mainly confirms the change didn't break any import path.

**Still outstanding (unrelated to the fix itself):** the two orphaned processes from the *original* (pre-fix) smoke test are still running on `localhost:5000`/`:8000`. `taskkill` was blocked by the sandbox permission classifier both before and after this fix; not retried via a different tool, since that would work around the same denial for the same underlying action. Stop them yourself when convenient (`! taskkill /F /T /PID 12956` for the backend reloader found earlier, and whichever PID `netstat -ano | grep :5000` shows for the evaluator) — they are harmless (localhost-only) and not blocking any further work.
