# Chapter 7: System Design (Detailed)

## 7.1 End-to-End Turn Sequence

The following sequence was reconstructed from direct code inspection (Chapters 5–6) and independently exercised end-to-end during this phase's testing (Chapter 10) — it is not a design aspiration but a verified, executed data flow.

```
Candidate (browser)
   │  voice_answer / code_submission  (WebSocket JSON event)
   ▼
Backend dispatcher (apps/backend/main.py, FastAPI)
   │  routes to orchestrator method, no domain logic here
   ▼
InterviewOrchestrator (asyncio.Lock-serialised)
   │
   ├──► [if voice] Audio Analysis Agent: transcribe (Whisper) + prosody (Librosa)
   │                 → confidence_score, hesitation_score (default 0.5 each if unavailable)
   │
   ├──► [if verbal] Evaluator (Flask, :5000): evaluate(question, transcript, rubric)
   │                 → S1, S2, R, final_score, grade, covered/missing concepts
   │    [if code]    Coding Executor (Docker sandbox): compile + run against test cases
   │                 → pass/fail per case, canonical score
   │
   ├──► Score Validator: apply mandatory_cap / mistake_penalty / coding_failure_multiplier
   │                 → corrected canonical score
   │
   ├──► Strategy Agent (HybridOrchestrator): build 6D state → PPO.predict() → guardrails
   │                 → next difficulty, action taken, guardrail_id (if overridden)
   │
   ├──► FeedbackAgent: assemble 15-field report; if score ≤ 0.65, call Qwen (:8001)
   │                 for detailed feedback / follow-up question generation
   │
   ├──► Question Selector: nearest_difficulty() + topic-rotation → next question
   │
   └──► Logger: append turn record to turns.jsonl; update summary.json
   │
   ▼
Response (WebSocket): next_question / feedback / difficulty_indicator → Candidate
```

## 7.2 Concurrency and State-Integrity Design

The orchestrator is the **sole** writer of authoritative session state (`self._state`), guarded by a per-instance `asyncio.Lock` acquired at the entry of every public mutating method. This specifically defends against a real hazard in a WebSocket-driven async backend: a client retransmitting an event after a network hiccup, which could otherwise deliver two concurrent evaluations of the same answer and corrupt the rolling-average performance history or the difficulty trajectory. Session termination (`end()`) is idempotent via a cached-report check inside the same lock, defending against the WebSocket-disconnect-and-explicit-end-session race common on mobile connections.

## 7.3 Failure-Isolation Design

Each component in the sequence above is designed to fail independently without crashing the session:

| Component unavailable | Observed fallback |
|---|---|
| RL/PPO checkpoint missing or incompatible | Deterministic score-threshold heuristic (verified present in code, Ch.6 §6.2) |
| Audio pipeline unavailable | Confidence/hesitation default to neutral 0.5, not fabricated | 
| Qwen microservice unavailable | Template-based feedback substituted (per existing test `test_qwen_followup_feedback.py`) |
| Evaluator malformed/adversarial input | Returns an in-range score rather than crashing — verified directly in this phase against 10 adversarial inputs including empty, garbled, and injection-like text (Ch.10 §10.4) |

**One real violation of this design principle was found and fixed in this phase**: the top-level `launch.py` supervisor process itself (not any of the services it manages) crashed on Windows consoles due to an unguarded Unicode character in its startup banner — see Chapter 10 §10.1 for full diagnosis and the applied fix.

## 7.4 Data Flow for the Baseline-to-RL Transition

The first 1–2 questions of a session follow a fixed, deterministic difficulty schedule with the RL policy inactive (avoiding an uninformed first decision from a zero-initialised state vector). Once baseline scores are recorded, control transfers to the RL+guardrail pipeline described in Chapter 6 §6.2 for the remainder of the session.
