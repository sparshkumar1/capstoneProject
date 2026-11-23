# Troubleshooting Guide

## Caddy / HTTPS

- **"too many certificate requests" or cert never issues**: Let's Encrypt needs port 80 reachable from the internet *before* it can validate the domain and port 443 to serve the cert after. Check the Azure VM's Network Security Group allows both, and that `PUBLIC_DOMAIN` actually resolves to the VM's IP (`dig <domain>` or `nslookup <domain>` from outside the VM) before starting the stack.
- **Caddy container restarting in a loop**: `docker compose logs caddy` — almost always a DNS/port issue above, or `PUBLIC_DOMAIN` unset (compose will refuse to start with a clear error, by design — see the `${PUBLIC_DOMAIN:?...}` guard in `docker-compose.yml`).

## Qwen / Admin login

- **Qwen replies look generic/templated instead of model-generated**: check `curl http://127.0.0.1:8001/health` on the VM — if `mock_mode: true`, the GGUF file wasn't found. Re-run `scripts/download_qwen_model.py` and confirm `models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf` exists and is ~1GB, then `docker compose restart qwen`.
- **Admin login always fails with "Incorrect admin password"**: `ADMIN_PASSWORD` isn't set in the VM's `.env`, or doesn't match what you're typing. There's no default — this is intentional (see `Cloud_Architecture.md` for why).
- **Admin dashboard requests return 401**: the token (`X-Admin-Token`) expires after 12 hours (`ADMIN_TOKEN_TTL_S` in `apps/backend/main.py`) — log out and back in. If it's immediate, confirm the frontend was built with the env change picked up (rebuild: `docker compose up -d --build frontend`) and that `apps/web/src/api.js`'s `_adminToken()` is reading the same `localStorage` key the login flow writes to (`prepaired.candidate`).

## Coding-question sandbox

- **Coding questions return `sandbox_error` / "Docker sandbox daemon is unreachable"**: expected and intentional for this deployment — Docker isn't installed inside the backend container, so `_resolve_docker_prefix()` in `agents/coding_executor/coding_executor.py` returns `None`. This was a deliberate choice (see `Cloud_Architecture.md`) to avoid Docker-in-Docker complexity. If you want it live: install Docker on the VM itself (it's a real VM, not a managed container platform, so this doesn't require DinD) and give the backend container access to the host's Docker socket — not done as part of this pass.

## Database

- **Data disappears after a redeploy**: `PREPAIRED_DB_PATH` isn't pointing at the bind-mounted `./data` volume, or the volume mount in `docker-compose.yml` was removed. Confirm `docker compose config` shows the `backend` service's `volumes` including `./data:/app/data` and `PREPAIRED_DB_PATH=/app/data/prepaired.db`.
- **"database is locked" under load**: SQLite's WAL mode + the app's own `threading.Lock()` handle single-process concurrency, but this setup only runs one backend worker (`--workers 1` in `docker-compose.yml`) on purpose — SQLite here isn't safe for multiple backend replicas writing concurrently. Don't scale the backend service past 1 replica without migrating off SQLite first.

## General

- **Backend container exits immediately on first start**: check it isn't failing a guarded import loudly in a way that isn't actually guarded — `docker compose logs backend`. Compare against `Dockerfile.backend`'s installed requirement files; if a dependency was added to `apps/backend/main.py`'s import list without updating the Dockerfile, this is the first place to look.
- **Out of memory / OOM-killed containers**: `docker stats` to see per-container RAM; the backend container (torch + sentence-transformers + faiss + whisperx + SB3) is the heaviest. The `Standard_B2ms` shape gives 8GB total across all containers — if this is tight, the evaluator standalone container (`services/evaluator/app.py` via `Dockerfile.evaluator`) can be stopped (`docker compose stop evaluator`) since the live app doesn't call it over HTTP.
