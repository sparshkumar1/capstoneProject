# PrepAIred — Cloud Architecture

Status: deployment config prepared and committed; **no cloud instance has been provisioned yet** (see `Cloud_Testing_Report.md` — nothing below is claimed as tested until that file says otherwise).

## Why this shape

A read-only code inspection (not the project's old docs) found:

- There is **no Ollama anywhere in the codebase.** `services/qwen/app.py` loads `Qwen2.5-1.5B-Instruct` directly via `llama-cpp-python` from a local GGUF file (CPU inference, no GPU required), with an HF-`transformers` fallback and a deterministic mock mode if neither loads.
- The Flask evaluator microservice (`services/evaluator/app.py`, port 5000) is **not called over HTTP** by the live app — `apps/backend/main.py` imports it directly as a Python module and runs it in-process. Its SBERT/FAISS/CrossEncoder weights just need to be importable inside the backend's own container.
- Every 2026 PaaS free tier checked (Render, Fly.io, Railway, Hugging Face Spaces) separates "free" from "persistent disk" — persistent storage is a paid add-on on all of them now. Oracle Cloud's "Always Free" Ampere A1 shape was the one option found that is simultaneously free indefinitely and has real persistent disk — but standard Oracle signup collects a credit card for identity verification, which you ruled out. **Azure for Students never requests or stores a payment method at all**, at the cost of being a $100/year credit rather than a permanent free tier. See `Hosting_Provider_Comparison.md` and `Cost_and_Resource_Analysis.md` for the full trade-off and the stop-when-idle strategy that makes the credit last.
- Several hardcoded `localhost` assumptions and one real security gap (unauthenticated admin routes) had to be fixed in code before any of this could work off one machine — see the "Code changes made" section below.

## Target shape: one Azure for Students VM

```
                        Internet (HTTPS, port 443 only)
                               |
                         [ Caddy :80/:443 ]   <- automatic Let's Encrypt cert for PUBLIC_DOMAIN
                          /            \
                 /api/*, /ws/*          everything else
                         |                     |
                [ backend :8000 ]      [ frontend :80 (static) ]
                  (127.0.0.1-only,          (127.0.0.1-only,
                   not internet-facing)      not internet-facing)
                         |
             in-process: evaluator (SBERT/FAISS/CrossEncoder),
             RL/PPO difficulty controller, WhisperX STT
                         |
                HTTP -> [ qwen :8001 ]  (127.0.0.1-only; llama-cpp-python, GGUF, CPU)
                         |
                  SQLite on the VM's real disk (PREPAIRED_DB_PATH)
```

One VM, one Docker Compose stack (`docker-compose.yml`), one public URL. Only Caddy's 80/443 are bound to `0.0.0.0`; every application container port is bound to `127.0.0.1` on the host, so nothing but Caddy is reachable from the internet even if the cloud firewall is misconfigured.

The standalone `evaluator` Flask container is kept in `docker-compose.yml` (not removed — it's unused by the live wiring but still a valid entry point if someone calls it directly) but isn't on the critical path; the backend's own container needs the evaluator's model weights because it imports that module in-process.

The C-code execution sandbox (`agents/coding_executor/`) needs a reachable Docker daemon. Per your decision, it's left disabled for this deployment: no Docker is installed inside the backend container for it, so `_resolve_docker_prefix()` returns `None` and coding questions return a clear `sandbox_error` instead of a confusing failure — the orchestrator already handles this gracefully, no code change was needed. Because the VM itself is a real Linux host (not a managed container platform), this constraint is weaker than on most PaaS: Docker could be installed on the VM directly later without the Docker-in-Docker problem a shared-container platform would have.

## Code changes made for this migration

All in this repo, no frozen artifacts touched (`rl/checkpoints/`, `research/`, evaluation formula, PPO code untouched):

1. **Admin auth gap fixed** (`apps/backend/main.py`): previously `/api/login` trusted the client's `admin: true` flag with zero server-side check, and all four `/api/admin/*` routes had no auth gate at all — anyone could hit them unauthenticated. Now `/api/login` validates `adminPass` against an `ADMIN_PASSWORD` env var (never committed) via constant-time comparison, issues a short-lived (12h) bearer token on success, and the four admin routes require it via a FastAPI dependency (`require_admin_token`). `apps/web/src/api.js` sends it as `X-Admin-Token` on `/api/admin/*` calls, read from the same `localStorage` entry the app already uses for the signed-in candidate.
2. **Hardcoded Qwen URL** (`agents/orchestrator/feedback_agent.py`, `agents/orchestrator/interview_orchestrator.py`): both hardcoded `http://localhost:8001`, which cannot work across containers. Now read from a `QWEN_URL` env var (default unchanged for local dev).
3. **Hardcoded CORS allow-list** (`apps/backend/main.py`): now overridable via a comma-separated `CORS_ORIGINS` env var, default unchanged.
4. **SQLite path** (`services/storage/database.py`): now overridable via `PREPAIRED_DB_PATH` so it can point at the VM's persistent volume instead of the repo-relative default.
5. **`Dockerfile.backend` was missing real dependencies**: it only installed `requirements/backend.txt`, but the backend imports the evaluator, the RL/PPO controller, and the WhisperX audio stack in-process — each guarded by `try/except`, so the container would previously build and start fine but silently fall back to mock scores, heuristic difficulty, and no real transcription. Now installs `base + backend + evaluator + rl + audio`.
6. **`docker-compose.yml`**: fixed the Qwen GGUF volume mount (was pointing at `services/qwen/models`, but the code reads `<repo-root>/models/gguf/...`), fixed the dead `PREPAIRED_QWEN_URL` env var name (code reads `QWEN_URL`), bound every container's host port to `127.0.0.1`, added a `caddy` service for the single public HTTPS entrypoint.
7. **`Dockerfile.frontend`**: now accepts `VITE_API_URL`/`VITE_WS_URL` as build args (Vite bakes these in at build time, not runtime — they weren't wired through from `docker-compose.yml` before).
8. **`.env.example`**: rewritten to separate variables the code actually reads from ones that were purely aspirational (most of the original file), and fixed two more wrong names (`DOCKER_SANDBOX_IMAGE` → `SANDBOX_DOCKER_IMAGE`; `QWEN_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct` was never real — the model is the 1.5B GGUF — and isn't read by any code anyway).

See `Deployment_Instructions.md` for the account-creation and VM steps, and `Environment_Variables.md` for the full variable reference.
