# Chapter 5: High-Level Design (HLD)

## 5.1 Architectural Overview

PrepAIred is a hub-and-spoke, multi-service architecture. A single authoritative orchestrator owns all session state; every other component is a stateless or independently-stateful service invoked by the orchestrator, never communicating directly with one another. This is a single-controller design — **not** a multi-agent system with inter-agent negotiation or arbitration (a separate research-paper draft describing such a layer was found, on inspection, not to correspond to anything in this codebase; see Ch.10 §10.13).

The system spans four logical layers, corrected here against the five the Phase-2 report described (the Phase-2 report's "Input Analysis Layer" and "Orchestration Layer" distinction is retained; its claim that question selection belongs to an "Evaluation Layer" alongside FAISS-based retrieval is corrected below):

1. **Candidate Layer** — the React frontend (`apps/web/`), communicating with the backend over a single persistent WebSocket connection. Contains no business logic.
2. **Input Analysis Layer** — speech-to-text and prosodic feature extraction (`agents/audio/*`), and session timing (`agents/timing/timer.py`).
3. **Orchestration Layer** — `agents/orchestrator/interview_orchestrator.py`, the sole authoritative writer of session state, serialising all mutating operations via an `asyncio.Lock`.
4. **Evaluation and Strategy Layer** — the semantic evaluator (`services/evaluator/app.py`, verified to be a **Flask** application, not FastAPI as the Phase-2 report stated — Ch.10 §10.4), the coding sandbox (`agents/coding_executor/`), the RL/guardrail strategy agent (`agents/strategy/hybrid_orchestrator.py` + `rl/guardrails.py`), the FeedbackAgent, and the question selector. **The question selector (`agents/question_selector/question_selector.py`) does not use FAISS or any semantic-retrieval mechanism, correcting the Phase-2 report's architecture diagram** — it is a deterministic nearest-difficulty-match plus least-recently-asked-topic-rotation algorithm (verified, Ch.10 §10.8). The FAISS index that does exist in the project is used exclusively inside the evaluator, for concept-coverage scoring of *answers*, not for selecting *questions*.

## 5.2 Technology Stack (verified against code)

| Layer | Technology |
|---|---|
| Backend API / WebSocket | FastAPI + uvicorn, port 8000 |
| Evaluator microservice | **Flask**, port 5000 (corrected from the Phase-2 report's "FastAPI" claim) |
| Qwen LLM microservice | FastAPI, port 8001 (this claim, unlike the evaluator's, is correct) |
| Frontend | React + Vite, port 5173 |
| RL policy | Stable-Baselines3 PPO, `Discrete(3)` action space (corrected from a claimed 5-action space) |
| Semantic similarity | sentence-transformers `all-MiniLM-L6-v2` |
| Concept coverage | FAISS flat index + a partially fine-tuned CrossEncoder (`ms-marco-MiniLM` derivative) |
| Question selection | Pure rule-based (no embedding/retrieval dependency) |
| Audio transcription | OpenAI Whisper / faster-whisper |
| Coding sandbox | Docker, isolated per-submission containers |
| Persistence | SQLite (`data/prepaired.db`) |
| Multi-service launch | `launch.py` supervisor (patched in this phase — Ch.10 §10.1) |

## 5.3 Session Lifecycle

A session progresses through five states — `created → in_progress → complete | abandoned | error` — exposed only as public methods on the orchestrator, never as direct state mutation from the dispatcher layer. Session termination is idempotent: the first `end()` call generates and caches the full report; subsequent calls return the cached version, preventing race conditions under concurrent disconnect/end-session WebSocket events.

## 5.4 Adaptive Difficulty Pipeline (high-level)

1. A fixed, deterministic baseline schedule governs the first 1–2 questions (RL inactive).
2. Once baseline is complete, the six-dimensional state vector is built from the latest answer score, rolling average, audio confidence/hesitation, session progress, and current difficulty.
3. The frozen PPO policy (`rl/checkpoints/seed_123/`) proposes a raw action from `{Easier, Same, Harder}`.
4. Six deterministic guardrail rules (`rl/guardrails.py`) are applied in strict priority order; the first rule whose condition is met overrides the raw action. **This phase found and closed a real gap in this layer** — see Ch.10 §10.3.
5. The resulting action updates difficulty (clamped to [1,5]) for the next question.

Full detail (state-vector construction, guardrail conditions, reward function as used in the project's prior frozen RL research) is in Chapter 6 (LLD) and Chapter 8 (Methodology).
