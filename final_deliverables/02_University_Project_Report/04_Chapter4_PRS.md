# Chapter 4: Project Requirements Specification (PRS)

**Note on format:** no PES-specific PRS template was supplied alongside the report guidelines. This chapter follows standard software-engineering requirements-specification practice (functional/non-functional requirements, actors, constraints). If a department-specific PRS template exists, this chapter's content should be transferred into it.

## 4.1 Actors

- **Candidate** — the sole user role; starts a session, answers questions (verbal or code), receives adaptive difficulty and feedback, views the session report.
- **System (automated)** — the orchestrator and its sub-agents; no human operator, administrator, or interviewer role exists in the current implementation.

## 4.2 Functional Requirements

| ID | Requirement | Verified by |
|---|---|---|
| FR-1 | The system shall present interview questions from a 125-question bank spanning DSA and C-language topics. | `test_orchestrator.py`, T-N10 |
| FR-2 | The system shall accept verbal (voice-transcribed) and code (C) answers. | `test_speech_pipeline.py`, `test_coding_executor.py` |
| FR-3 | The system shall score verbal answers using a three-component semantic evaluator (S1 similarity, S2 concept coverage, R reasoning quality). | `test_evaluator.py`, T-N04, T-N06 |
| FR-4 | The system shall score code answers via isolated sandboxed execution against predefined test cases. | `test_coding_executor.py` (currently blocked on Docker daemon — see Ch.10 §10.9) |
| FR-5 | The system shall adapt question difficulty after each answer using a trained RL policy constrained by deterministic guardrails. | T-N02, T-N03 |
| FR-6 | The system shall produce a structured, multi-field feedback report after each answer. | `test_qwen_followup_feedback.py` |
| FR-7 | The system shall persist all session and turn data for later retrieval. | `test_persistence_and_history.py`, T-N11 |
| FR-8 | The system shall present a post-session report summarising performance, trends, and per-question feedback. | `apps/web/src/Report.jsx`, T-F01 |
| FR-9 | The system shall degrade gracefully (continue the session) if the RL policy, the Qwen microservice, or the audio pipeline is unavailable. | T-N01, T-U02 |

## 4.3 Non-Functional Requirements

| ID | Requirement | Status |
|---|---|---|
| NFR-1 | Evaluator response latency should be reasonable for an interactive session. | Measured (T-N09): median 896ms, p95 986ms, warm, n=30, this host — an engineering observation, not a formally specified SLA (none was supplied). |
| NFR-2 | The coding sandbox shall isolate untrusted candidate code from the host. | Configuration verified (T-N12): non-root user, `--net=none`, `--cap-drop=ALL`, `--read-only`, memory/PID limits, all confirmed present in the actual Docker invocation code. |
| NFR-3 | The system shall not fabricate metrics or feedback when underlying signals are unavailable. | Verified by design and by test (`test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` — note: this specific test currently fails on an unrelated, pre-existing, documented issue, see Ch.10 §10.11; the no-fabrication *principle* itself is upheld elsewhere, e.g. audio defaults to neutral 0.5 rather than a fabricated value when unavailable). |
| NFR-4 | The system shall be reproducible: every reported result traces to a stored artifact, config, and git commit. | Enforced throughout Ch.10 of this report. |

## 4.4 Constraints

Single-candidate sessions only; English-language input; requires a local Docker daemon for code-answer evaluation (currently unavailable in the test environment used for this report — see Ch.10); requires local compute capable of running SBERT, FAISS, a fine-tuned CrossEncoder, and a quantised local LLM.
