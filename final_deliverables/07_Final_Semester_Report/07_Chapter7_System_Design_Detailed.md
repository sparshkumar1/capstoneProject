# Chapter 7: System Design (Detailed)

## 7.1 End-to-End Turn Sequence

The sequence below comes from direct code inspection (Chapters 5–6) and was independently exercised end-to-end during this phase's testing (Chapter 10). It describes a verified, executed data flow, not a design aspiration.

```
Candidate (browser)
   │  voice_answer / code_submission  (WebSocket JSON event)
   ▼
Backend dispatcher (apps/backend/main.py, FastAPI)
   │  routes to orchestrator method, no domain logic here
   ▼
InterviewOrchestrator (asyncio.Lock-serialised)
   │
   ├──► [if voice] Input Analysis: transcribe (Whisper) + prosody (Librosa)
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
   ├──► Strategy layer (HybridOrchestrator): build 6D state → PPO.predict() → guardrails
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

Notice that every branch on the dispatcher side collapses to a single method call on the orchestrator — `apps/backend/main.py` itself holds no conditional logic, no state inspection, and no score computation. That's deliberate: keeping the dispatcher blind to interview domain logic is what lets the orchestrator get tested on its own and swapped out later without touching the transport layer at all.

## 7.2 Concurrency and State-Integrity Design

The orchestrator is the **sole** writer of authoritative session state, guarded by a per-instance `asyncio.Lock` acquired at the entry of every public mutating method. This guards specifically against a real hazard in a WebSocket-driven async backend: a client retransmitting an event after a network hiccup could otherwise deliver two concurrent evaluations of the same answer. That could corrupt the rolling-average performance history or the difficulty trajectory. Session termination is idempotent through a cached-report check inside that same lock, which guards against the WebSocket-disconnect-and-explicit-end-session race that is common on mobile connections.

## 7.3 Failure-Isolation Design

Each component in the sequence above fails independently, by design, without crashing the session:

**Table 7.1.** Graceful-degradation fallback behaviour.

| Component unavailable | Observed fallback |
|---|---|
| RL/PPO checkpoint missing or incompatible | Deterministic score-threshold heuristic (verified present in code, Chapter 6 Section 6.3) |
| Audio pipeline unavailable | Confidence/hesitation default to neutral 0.5, not fabricated |
| Qwen microservice unavailable | Template-based feedback substituted (per existing test `test_qwen_followup_feedback.py`) |
| Evaluator malformed/adversarial input | Returns an in-range score instead of crashing; verified directly in this phase against 10 adversarial inputs including empty, garbled, and injection-like text (Chapter 10, Section 10.4) |
| Docker daemon unreachable | Structured `sandbox_error` status returned; untrusted code is never executed outside the sandbox under any observed code path |

**This phase found and fixed one real violation of this design principle**: the top-level `launch.py` supervisor process itself (not any of the services it manages) crashed on Windows consoles. The cause was an unguarded Unicode character in its startup banner. See Chapter 10, Section 10.1 for the full diagnosis and the applied fix.

## 7.4 Data Flow for the Baseline-to-RL Transition

The first one to two questions of a session follow a fixed, deterministic difficulty schedule with the RL policy inactive, which avoids an uninformed first decision from a zero-initialised state vector. Once baseline scores are recorded, their average seeds the RL policy's starting difficulty (Chapter 5, Section 5.5). Control then passes to the RL-plus-guardrail pipeline described in Chapter 6, Section 6.3 for the rest of the session.
