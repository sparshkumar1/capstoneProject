# Environment Variables — Cloud Deployment

Source of truth for names/defaults is `.env.example` (root). This file adds the *why* and the *where it's read*, and flags which ones are new as of this migration.

## Live-consumed (changes behavior)

| Variable | Read in | Required? | Notes |
|---|---|---|---|
| `QWEN_URL` | `agents/orchestrator/feedback_agent.py`, `agents/orchestrator/interview_orchestrator.py` | No (defaults to `http://localhost:8001`) | **New as of this migration** — was hardcoded. In `docker-compose.yml` set to `http://qwen:8001` (container-network name). |
| `ADMIN_PASSWORD` | `apps/backend/main.py` | Yes, to use admin login at all | **New as of this migration.** No default — if unset, admin elevation is always rejected (previously: unauthenticated, anyone could claim `admin: true`). Set via your hosting platform's secret store or a non-committed `.env`, never hardcode it. |
| `CORS_ORIGINS` | `apps/backend/main.py` | No | **New.** Comma-separated origins. Not actually exercised in the Caddy-fronted deployment (frontend and API share one origin, so no cross-origin requests happen) — kept for local multi-origin dev. |
| `PREPAIRED_DB_PATH` | `services/storage/database.py` | No (defaults to `<repo>/data/prepaired.db`) | **New.** Point at a mounted persistent volume for anything other than a single long-lived host. |
| `PREPAIRED_GGUF_PATH` | `services/qwen/app.py` | No | Pre-existing. Override the GGUF model file location. |
| `ENABLE_GPU_RESEARCH_MODELS` | `services/qwen/app.py` | No | Pre-existing. `1`/`true` allows a HF-`transformers` fallback download if the GGUF file is missing. Left `0` — the deployment is CPU-only, no GPU provisioned. |
| `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` | `services/qwen/app.py` | No | **New.** Setting `LLM_BASE_URL` switches this service from the local GGUF engine to a hosted OpenAI-compatible chat completions endpoint (e.g. Groq); `decision_source` reports `qwen_hosted_llm` in that mode. Unset (default) = unchanged local GGUF behavior. `LLM_API_KEY` is a real secret — never commit it. |
| `QWEN_FEEDBACK_MAX_NEW_TOKENS` | `services/qwen/app.py` | No | Pre-existing, default 512. |
| `SANDBOX_DOCKER_IMAGE` | `agents/coding_executor/coding_executor.py` | No | Pre-existing. `.env.example` previously named this `DOCKER_SANDBOX_IMAGE` (wrong — never read). Moot for this deployment since the sandbox is disabled (no Docker daemon reachable from inside the backend container). |
| `PREPAIRED_WARMUP_STT_MODELS`, `PREPAIRED_DISABLE_WARMUP`, `PREPAIRED_AUDIO_WAIT_TIMEOUT_S` | `apps/backend/main.py` | No | Pre-existing backend warmup tuning. |
| `PUBLIC_DOMAIN` | `deploy/Caddyfile` (via compose interpolation) + `docker-compose.yml` frontend build args | Yes, for the Caddy/VM deployment | **New.** The hostname Caddy requests a Let's Encrypt cert for, and what the frontend is built to call. |
| `VITE_API_URL`, `VITE_WS_URL` | `apps/web/src/api.js`, `apps/web/src/useInterviewWS.js` | No (fall back to `localhost:8000`) | Pre-existing, already live-consumed. **Baked in at frontend build time, not container runtime** — set via `docker-compose.yml`'s `frontend.build.args`, derived from `PUBLIC_DOMAIN`. |

## Declared but not read by any current code (kept in `.env.example` as documentation only)

`EVALUATOR_URL`, `BACKEND_URL`, `EVALUATOR_MODEL_DIR`, `EVALUATOR_ASSETS_DIR`, `RL_MODEL_PATH`, `RL_VEC_PATH`, `SECRET_KEY`, `WHISPERX_DEVICE`, `WHISPERX_MODEL_SIZE`, `WHISPERX_COMPUTE_TYPE`, `WHISPERX_LANGUAGE`, `WANDB_*`.

Don't assume setting these changes behavior — verified by repo-wide grep for `os.environ`/`os.getenv` during the architecture inspection (2026-11-15). If you need one of these to actually do something, it needs a code change first, not just an env var.

## Secrets handling

- `ADMIN_PASSWORD` is the only real secret this deployment introduces. Set it via the hosting platform/VM's own secret mechanism (e.g. a `.env` file on the VM with restrictive permissions, loaded by `docker compose --env-file`), never committed, never put in `docker-compose.yml` directly.
- `SECRET_KEY` in `.env.example` is a pre-existing placeholder that is not read by any code (no JWT/session-signing exists) — don't treat it as doing anything today.
