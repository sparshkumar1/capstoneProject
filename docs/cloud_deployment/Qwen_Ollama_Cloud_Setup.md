# Qwen Model — Cloud Setup

## Correcting a premise

The original migration brief assumed Qwen 2.5 runs through Ollama, possibly a 7B variant. A read-only inspection of `services/qwen/app.py` (2026-11-15) found **no Ollama anywhere in this codebase** — no call to port 11434, no `ollama` import, confirmed by a repo-wide grep. The only mentions of Ollama are historical, in docs describing a design that was already replaced. This is good news for cloud cost: the actual model is much smaller than assumed.

## What actually runs

- Model: `Qwen/Qwen2.5-1.5B-Instruct`, loaded from a local **GGUF file** (`models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf`) via `llama-cpp-python`. CPU inference — no GPU required or provisioned.
- Fallback 1 (if the GGUF file is missing and `ENABLE_GPU_RESEARCH_MODELS=1`): downloads `Qwen/Qwen2.5-1.5B-Instruct` from Hugging Face via `transformers`, 4-bit quantized if CUDA is present. Not used in this deployment (left `0` — no GPU).
- Fallback 2 (if neither loads): a deterministic, rubric-grounded structured generator (`_synthesize_structured_followup`/`_synthesize_structured_feedback`) — the app never hard-fails for a missing model, it just returns `decision_source: "non_llm_structured_recovery"`. This is why **the model file must actually be present** for the deployment to use the real LLM rather than this fallback — presence isn't verified by anything except checking the `/health` endpoint after deploy (see `Cloud_Testing_Report.md`, Test 4).
- Loading is lazy/background: the service accepts HTTP requests immediately on port 8001 while the model loads in a background thread.
- No streaming, no network dependency once the GGUF file is local — a single blocking completion call per request.

## Getting the model onto the VM

The GGUF file (~1GB, q4_k_m quantization) is not checked into git. On the Azure VM, before `docker compose up`:

```bash
# from the repo root, with the project's Python env available
python scripts/download_qwen_model.py
```

This populates `models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf`, which `docker-compose.yml` bind-mounts read-only into the `qwen` container (fixed in this migration — the compose file previously mounted the wrong directory, `services/qwen/models`, which the code never reads).

## Why this stays local-to-the-VM rather than a hosted inference API

A 1.5B GGUF model at 4-bit quantization runs acceptably on 2 CPU cores with a few GB of RAM — well within the Oracle Always-Free Ampere A1 shape (2 OCPU/12GB RAM) shared with the rest of the stack. This avoids needing a third-party hosted-inference account (and its own free-tier limits/rate limits/cold starts) for a model this small. If the project later moves to a genuinely large Qwen variant, revisit Phase 2 of the original brief (hosted inference providers) — the `QWEN_URL` env var introduced in this migration (`agents/orchestrator/feedback_agent.py`, `agents/orchestrator/interview_orchestrator.py`) is exactly the swap point: point it at any OpenAI-compatible or custom hosted endpoint without further code changes, as long as the response shape matches what `feedback_agent.py`/`interview_orchestrator.py` expect from the local service today (not verified — would need adapting the request/response contract, not just the URL, if the hosted API's shape differs).

## Not exposed publicly

The `qwen` container's port 8001 is bound to `127.0.0.1` only (`docker-compose.yml`) — reachable from the backend container via the internal Docker network (`http://qwen:8001`, via `QWEN_URL`), never directly from the internet. Caddy is the only service with a port bound to `0.0.0.0`.
