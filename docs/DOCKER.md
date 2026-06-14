Docker and Compose
==================

This repo includes Docker support for the core stack:

- `Dockerfile.evaluator` for the evaluator service on port 5000
- `Dockerfile.backend` for the FastAPI backend on port 8000
- `Dockerfile.frontend` for the Vite app served by Nginx on port 5173
- `Dockerfile.qwen` for the optional Qwen service on port 8001
- `docker-compose.yml` for local orchestration

Quick start
-----------

```powershell
docker compose up --build
```

This starts evaluator, backend, and frontend. The Qwen service is optional and only starts when you enable its profile:

```powershell
docker compose --profile qwen up --build
```

Notes
-----

- The default compose stack does not require the large Qwen model weights.
- Large model checkpoints and generated artifacts are excluded from the repo context via `.dockerignore` and should be mounted or hosted externally.
- The backend mounts `data/`, `logs/`, and `orchestrator_logs/` so session outputs remain visible on the host.
- The evaluator mounts its `assets/` and `models/` directories read-only so the service can run without rebuilding artifacts into the image.

If you need to run only the API stack without the frontend, use:

```powershell
docker compose up --build evaluator backend
```
