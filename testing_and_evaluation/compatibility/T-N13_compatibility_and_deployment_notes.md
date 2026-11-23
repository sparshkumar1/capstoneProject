# T-N13 — Compatibility and Deployment Notes

## Python version

| Context | Python version |
|---|---|
| `CLAUDE.md` documented target | 3.12 |
| Local `.venv` (this session, measured directly) | **3.11.9** |
| `Dockerfile.backend`, `Dockerfile.evaluator`, `Dockerfile.qwen` | `python:3.12-slim` — matches the documented target |
| `pyproject.toml` | `requires-python = ">=3.11"` (compatible with both) |

**Finding:** the local dev `.venv` and the documented/Dockerized target diverge (3.11.9 vs 3.12), but both satisfy `pyproject.toml`'s `>=3.11` constraint, so this is not a hard incompatibility — just a version drift between the local dev environment and the deployment target. Not changed in this pass (per the scope of this testing phase); flagged for the user's awareness, consistent with `docs/PROJECT_STATE.md`'s existing "do not resolve unasked" posture on environment questions.

## Docker images

5 Dockerfiles present: `Dockerfile.backend` (python:3.12-slim), `Dockerfile.evaluator` (python:3.12-slim), `Dockerfile.qwen` (python:3.12-slim), `Dockerfile.frontend` (node:20-alpine, multi-stage build), `Dockerfile.sandbox` (alpine:3.19, the C-compilation sandbox image). `docker-compose.yml` references all 5.

**Build verification: not performed.** The Docker daemon is not running in this environment (confirmed earlier via `docker ps`/`docker version` — client v29.7.2 present, "failed to connect to the docker API... check if the daemon is running"). `docker build` requires a running daemon the same as `docker run`, so this blocker is identical to the one documented for the 18 sandboxed-code-execution test failures in `baseline_results/Full_Suite_Baseline_Results.md` — not a separate issue, the same root cause. If Docker Desktop is started, both the 18 test failures and a full `docker build` dry-run for all 5 images become possible in one pass.

## OS / shell

`MINGW64_NT-10.0-26300` (Windows 11 Pro via Git Bash/MSYS). All testing in this session was performed on this single platform; no cross-platform (native Linux, macOS) compatibility testing was performed or is claimed.

## Package manager / frontend

`apps/web/node_modules` present and functional — confirmed directly (T-F01, 28/28 Vitest tests passed without any new `npm install` needed). `npm run build` (production build) was not run in this pass — only `npm run test:ci` (test suite) and `npm run dev` were exercised (the latter indirectly, via `launch.py`'s frontend service definition, not actually started since all smoke tests used `--backend-only`).
