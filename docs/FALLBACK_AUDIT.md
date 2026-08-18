# FALLBACK_AUDIT.md — Authoritative Architecture & Fallback Removal Specification

**Document Version:** 1.0.0 (Stage 8 Verification & Audit)
**System:** PrepAIred Automated Technical Interview Pipeline

---

## 1. Core Architectural Principle

PrepAIred implements a genuinely personalized, multi-agent automated technical interview architecture. Intelligent agent decisions are **never silently replaced** with generic, static, or fabricated answers when a model or service is unavailable.

If an intelligent component becomes unreachable, the pipeline reports an **explicit structured failure state** (`evaluator_unavailable`, `llm_unavailable`, `stt_unavailable`, `sandbox_error`) rather than pretending that the intelligent agent succeeded.

---

## 2. Authoritative Components & Responsibilities

| Component | Authoritative Location | Primary Responsibility | Failure Behavior |
|---|---|---|---|
| **Verbal Evaluator Agent** | `services/evaluator/app.py` | Multi-Task Cross-Encoder technical evaluation ($S_{\text{tech}}$) | Explicit `evaluator_unavailable` (score 0.0, no fabricated score) |
| **Follow-Up Agent** | `services/qwen/app.py` | Grounded follow-up question generation probing gaps | Explicit failure; no injection if grounded probe cannot be synthesized |
| **Qwen Feedback Agent** | `agents/orchestrator/feedback_agent.py` & `services/qwen/app.py` | Personalized narrative feedback grounded in candidate evidence | Explicit `llm_unavailable` state; preserves authoritative evaluator evidence |
| **Speech / STT Pipeline** | `agents/audio/` & WhisperX / Wav2Vec2 | Authoritative transcript and genuine acoustic features from raw audio | Explicit `stt_unavailable`; browser preview never promoted to evaluation |
| **Question System** | `agents/question_selector/` & `InterviewOrchestrator` | State-driven question selection based on history, topics, and difficulty | Explicit question selection failure; no random or generic fallback |
| **RL Difficulty Agent** | `agents/strategy/hybrid_orchestrator.py` | 6D PPO adaptive difficulty adjustment (`Discrete(3)`) | Attributed transparently (`"ppo"` vs `"baseline_warmup"` vs `"guardrail_gX"` vs `"question_selection_heuristic"`) |
| **Coding Sandbox** | `agents/coding_executor/` & Docker | Isolated C compilation and execution with strict resource limits | Explicit `sandbox_error` if Docker unreachable; no fake stdout or simulation |
| **Candidate State Manager** | `InterviewOrchestrator._state` | Persistent candidate evidence tracking | Canonical single source of truth across turns |

---

## 3. Fallback Classification Audit Table

Every fallback-like mechanism in the codebase was audited and classified into exactly one of five categories:
- **`REMOVE`:** Fabricated or obsolete interview-intelligence fallback (deleted).
- **`KEEP`:** Verified algorithmic safeguard or documented default.
- **`INFRASTRUCTURE RECOVERY`:** Legitimate system recovery (retries, timeouts, audio DSP) with transparent attribution.
- **`DOCUMENT`:** Auxiliary safety layer (e.g. static pre-flight scan).
- **`RESEARCH`:** Aspirational claim in draft documentation requiring synchronization in Stage 13.

| File / Component | Mechanism | Classification | Reason & Status |
|---|---|---|---|
| `services/qwen/evaluate_upgraded.py` | Discourse marker count (`marker_hits`) and word count bonus (`length_bonus`) | **`REMOVE`** | **Removed.** Obsolete legacy evaluator; completely superseded by Cross-Encoder evaluator in `services/evaluator/app.py`. |
| `agents/orchestrator/orchestrator.py` | 5-Action Orchestrator (`ACTION_MAP` with Hint/Follow-up in RL, legacy imports) | **`REMOVE`** | **Removed.** Obsolete legacy orchestrator; superseded by `InterviewOrchestrator` in `agents/orchestrator/interview_orchestrator.py`. |
| `agents/orchestrator/conceptual_critic.py` | Legacy `ConceptualCritic` class | **`REMOVE`** | **Removed.** Obsolete legacy critic; unused in production pipeline. |
| `agents/orchestrator/interview_orchestrator.py` | `_STATIC_HINTS` & `_MISSING_Q_HINT` | **`REMOVE`** | **Removed.** Static generic topic hints replaced with explicit `llm_unavailable` state when Qwen is unreachable. |
| `agents/orchestrator/interview_orchestrator.py` | `_detailed_fallback_feedback` & `len(words)*0.015` fake score | **`REMOVE`** | **Removed.** Word-count score formula removed; verbal evaluation failures return explicit `evaluator_unavailable` structure. |
| `apps/backend/main.py` | Text-derived synthetic speech duration (`total_speech_time = len(words)/3.0`) | **`REMOVE`** | **Removed.** Synthetic acoustic timing from text strings removed; requires genuine acoustic metadata from server STT. |
| `agents/audio/transcriber.py` | `_fallback_energy_timing` | **`INFRASTRUCTURE RECOVERY`** | **`KEEP`.** Real signal processing on raw WAV audio using numpy/scipy energy analysis when phoneme alignment is missing. |
| `agents/audio/audio_features.py` | `_PARSELMOUTH_AVAILABLE` fallback to ffmpeg/numpy | **`INFRASTRUCTURE RECOVERY`** | **`KEEP`.** Real signal processing fallback extracting acoustic features directly from audio waveform. |
| `agents/orchestrator/feedback_agent.py` | `llm_status: "llm_unavailable"` structured output | **`INFRASTRUCTURE RECOVERY`** | **`KEEP`.** Transparently reports LLM status, preserves evaluator evidence, never fabricates LLM text. |
| `agents/strategy/hybrid_orchestrator.py` | `_heuristic_action` & transparent source attribution | **`INFRASTRUCTURE RECOVERY`** | **`KEEP`.** Transparently attributed as `"question_selection_heuristic"`, never falsely claimed as `"ppo"`. |
| `agents/coding_executor/sandbox_policy.py` | Static pre-flight C safety scanner | **`DOCUMENT`** | **`KEEP`.** Documented as defense-in-depth auxiliary filter; Docker container remains primary security boundary. |
| `services/evaluator/app.py` | Sentence filter negation guard (`if not filtered: filtered = sentences`) | **`KEEP`** | **`KEEP`.** Standard NLP text processing safeguard when all sentences contain negation words. |
| `research/papers/*.md` | Outdated mentions of legacy fallback chains | **`RESEARCH`** | **`DOCUMENT`.** Retained in research papers for deliberate synchronization during Stage 13. |

---

## 4. Transparent Failure Semantics

When any system service fails, PrepAIred adheres to explicit failure reporting:

1. **Evaluator Failure:**
   - Status: `evaluator_unavailable`
   - Score: `0.0` (never `0.5` or word-count heuristic)
   - Justification: `"Authoritative verbal evaluation service is unavailable. No score fabricated."`
2. **Qwen Hint / Follow-Up Failure:**
   - Status: `llm_unavailable`
   - Text: `"Personalized hint is currently unavailable (LLM service unreachable)."`
   - Error: `"Qwen service unreachable"`
3. **STT / Audio Failure:**
   - Status: `stt_unavailable`
   - Evaluation: Technical scoring not attempted; browser transcript never promoted to authoritative evaluation.
4. **Docker Sandbox Failure:**
   - Status: `sandbox_error`
   - Output: `"Docker sandbox daemon is unreachable. Untrusted code execution blocked to protect host."`
5. **RL Policy Failure & Operational Continuity:**
   - Status: `rl_unavailable`
   - Decision Source: Explicitly labeled `"non_rl_heuristic_recovery"`, `"baseline_warmup"`, or `"guardrail_gX"`.
   - Action Attribution: `raw_rl_action` is recorded as `None` (no RL action produced); never falsely attributed to `"ppo"`.
   - Research Boundary: The heuristic recovery path exists strictly for non-RL operational continuity and is **not described as part of the RL system contribution**.


---

## 5. Summary Statement

No obsolete or fabricated interview-intelligence fallbacks remain in the production path. Legitimate infrastructure recovery, transparent source attribution, and explicit structured failure states remain active.
