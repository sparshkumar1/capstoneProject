# Chapter 5: High-Level Design (HLD)

## 5.1 Architectural Overview

No single monolithic component in PrepAIred is responsible for the end-to-end interview process. The system is instead decomposed into specialised components, each with a clearly bounded responsibility, all coordinated by a central orchestrator. This gives the architecture separation of concerns, fault isolation, and the ability to degrade gracefully when an individual component is unavailable.

**This is a single-controller, hub-and-spoke architecture, not a multi-agent system with inter-component negotiation or arbitration.** A single authoritative orchestrator owns all session state, and every other component is a stateless or independently-stateful service that the orchestrator invokes. None of them talk to each other directly. There is one documented exception, and it is narrow: the FeedbackAgent issues its own request to the Qwen service instead of being routed through the orchestrator. That is an implementation detail, not peer-to-peer negotiation. We say this plainly because a separate, auxiliary research-paper draft describing a second, "bounded-authority" coordination layer was supplied alongside this project's materials. Direct inspection of the codebase in this phase confirmed that layer does not exist in the implementation (Chapter 10, Section 10.13). This report's architecture description is written to match the real, verified system instead.

The system spans four logical layers here, corrected against the five the Phase-2 report described. The "Input Analysis Layer" and "Orchestration Layer" distinction from that report is retained below. One claim does need correction, though: that question selection belongs to an "Evaluation Layer" alongside FAISS-based retrieval. In fact, question selection has no FAISS or embedding dependency at all (Section 5.1, item 4, and Chapter 10 Section 10.8):

1. **Candidate Layer.** Everything starts in the browser, with the candidate and the Interview UI (`apps/web/`). A candidate can answer two ways — speaking into the browser's `MediaRecorder` API, or writing code in a CodeMirror-powered editor — and both travel to the backend over one persistent WebSocket connection, which also carries everything coming back the other way: the current question, the difficulty indicator, the hint panel, real-time feedback. We kept this layer deliberately thin on purpose. No business logic lives in the frontend, which means the interview logic underneath can be tested on its own, without needing the UI at all.
2. **Input Analysis Layer.** A raw candidate response isn't usable yet — it has to become structured signals before evaluation or strategy can touch it. Three sub-pipelines run in parallel to get there: speech-to-text with forced word-level alignment (OpenAI Whisper / faster-whisper), prosodic feature extraction (Librosa), and a session timer that turns elapsed time into a normalised pace feature. The orchestrator only sees the response once these three come back together as one multimodal package. Chapter 8, Section 8.4 has the full design.
3. **Orchestration Layer.** `agents/orchestrator/interview_orchestrator.py` is the sole authoritative writer of session state. It is instantiated once per session and exposes a clean public API that the backend's WebSocket dispatcher delegates all incoming events to. An `asyncio.Lock` serialises every mutating operation to prevent race conditions, and each incoming event (voice answer, code submission, hint request, or session termination) is routed to the appropriate downstream component. It is the only component with visibility across the rest of the system; no other component talks to another directly.
4. **Evaluation and Strategy Layer.** This layer covers the semantic evaluator (`services/evaluator/app.py`), the coding sandbox (`agents/coding_executor/`), the RL/guardrail strategy layer (`agents/strategy/hybrid_orchestrator.py` + `rl/guardrails.py`), the FeedbackAgent, and the question selector. The evaluator is verified to be a **Flask** application, not FastAPI as the Phase-2 report stated (Chapter 10, Section 10.4). For verbal answers, the evaluator runs a three-component pipeline (Similarity, Concept Coverage, Reasoning) and combines the outputs into a final weighted score. That score then passes through a deterministic Score Validator for post-hoc correction. Code submissions take a different path: the coding executor runs submitted code in a sandboxed environment against predefined test cases and analyses it for algorithmic complexity and structural correctness. Both paths return a canonical score to the orchestrator through the same scoring interface. They remain two genuinely separate code paths, though: direct inspection confirmed zero cross-imports between them, consistent with the project's own stated design. **The question selector does not use FAISS or any semantic-retrieval mechanism, correcting the Phase-2 report's architecture diagrams.** The production path, `apps.backend.main.select_questions`, is a fully deterministic scored-candidate selection (difficulty distance + topic-diversity penalty + personalisation adjustment, with three-level deduplication, no randomness). Chapter 6, Section 6.6 corrects the attribution against an earlier draft of this chapter. That draft described a separate baseline/research module (`agents/question_selector/question_selector.py`, which does contain `random.choice` tie-breaking) as if it were the production design. Neither module depends on FAISS or embeddings; the FAISS index that does exist in the project is used exclusively inside the evaluator, for concept-coverage scoring of *answers*, not for selecting *questions*.

![architecture](fig_5_1_architecture.png)

**Figure 5.1.** High-level system architecture: a single orchestrator coordinating specialised, bounded-authority components (hub-and-spoke, not a multi-agent topology). Category colours distinguish component roles; see Chapter 10, Section 10.13 for the classification methodology.

## 5.2 Technology Stack (verified against code)

**Table 5.1.** Technology stack (verified against code).

| Layer | Technology |
|---|---|
| Backend API / WebSocket | FastAPI + uvicorn, port 8000 |
| Evaluator microservice | **Flask**, port 5000 (corrected from the Phase-2 report's "FastAPI" claim) |
| Qwen LLM microservice | FastAPI, port 8001 (this claim, unlike the evaluator's, is correct) |
| Frontend | React + Vite, port 5173 |
| RL policy | Stable-Baselines3 PPO, `Discrete(3)` action space (corrected from a claimed 5-action space including Hint/Follow-up) |
| Semantic similarity | sentence-transformers `all-MiniLM-L6-v2` |
| Concept coverage | FAISS flat index + a partially fine-tuned CrossEncoder (`ms-marco-MiniLM` derivative) |
| Question selection | Pure rule-based (no embedding/retrieval dependency) |
| Audio transcription | OpenAI Whisper / faster-whisper, with forced alignment |
| Audio feature extraction | Librosa |
| Coding sandbox | Docker, isolated per-submission containers |
| Persistence | SQLite (`data/prepaired.db`) |
| Multi-service launch | `launch.py` supervisor (patched in this phase; Chapter 10, Section 10.1) |

## 5.3 Design Principles

Three principles guided every architectural decision in PrepAIred. **Separation of concerns** comes first: every component has a single, clearly bounded responsibility, so each one can be tested and replaced independently without touching the others. This is exactly what let this phase's dependency-injection-based test suite (Chapter 9, Section 9.1) exercise every logical branch of the orchestrator without starting any external service. **Graceful degradation** comes second: every layer implements a fallback so that one component failing does not disrupt the candidate's session. This phase's testing (Chapter 10) confirmed the principle holds for the evaluator, audio pipeline, and RL policy fallback paths. It also found and fixed the one place where it did not: the application launcher itself. **Orchestrator sovereignty** is the third: all domain logic lives inside the orchestrator. That keeps the backend's WebSocket dispatcher a thin router with no knowledge of interview semantics, verified directly by inspecting `apps/backend/main.py` (Chapter 7, Section 7.1). Chapters 6, 8, and 9 present the detailed design and implementation of each component.

## 5.4 Session Lifecycle

A session moves through five states (`created → in_progress → complete | abandoned | error`), and these are exposed only as public methods on the orchestrator, never as direct state mutation from the dispatcher layer. Session termination is idempotent: the first `end()` call generates and caches the full report, and every later call just returns that cached version without re-running any generation logic. This keeps things consistent under the concurrent disconnect-and-end-session events that are common on mobile connections.

## 5.5 Adaptive Difficulty Pipeline (high-level)

1. RL sits out the first one or two questions entirely. Question 1 is pinned at difficulty 2 (easy) and question 2 at difficulty 3 (mid) by a fixed schedule, no policy involved. If those two scores disagree sharply enough that the candidate's real ability level is still unclear, a third baseline question runs before RL is allowed to take over.
2. The RL policy doesn't start from a blank slate — its initial difficulty is seeded from the average of those baseline scores, so the first real RL decision already has a reasonably well-informed state vector to work from rather than an uninformed prior.
3. The six-dimensional state vector draws on the latest answer score, the rolling average, audio confidence/hesitation, session progress, and current difficulty.
4. The frozen PPO policy (`rl/checkpoints/seed_123/`) then proposes a raw action from `{Easier, Same, Harder}`.
5. Six deterministic guardrail rules apply in strict priority order, and the first one whose condition is met overrides the raw action. **This phase found and closed a real gap in this layer** in the canonical module, `rl/guardrails.py`; see Chapter 10, Section 10.3. **The live orchestrator evaluates its own separate, hand-duplicated copy of these rules, not `rl/guardrails.py` directly.** **That copy has three confirmed, disclosed divergences from the canonical fix** (Chapter 6, Section 6.3; Chapter 10, Section 10.3; Chapter 11, Section 11.4).
6. The resulting action updates difficulty (clamped to [1,5]) for the next question.

Chapter 6 (LLD) and Chapter 8 (Methodology) give the full detail: state-vector construction, guardrail conditions and rationale, and the reward function as used in the project's prior frozen RL research.
