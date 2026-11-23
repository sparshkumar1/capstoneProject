# Chapter 4: Project Requirements Specification (PRS)

**Note on format:** no PES-specific PRS template came with the report guidelines. So this chapter follows standard software-engineering requirements-specification practice: functional and non-functional requirements, actors, constraints. If a department-specific PRS template does exist, this chapter's content should be moved into it.

## 4.1 Actors

- **Candidate**: the sole user role. Starts a session, answers questions (verbal or code), receives adaptive difficulty and feedback, and views the session report.
- **System (automated)**: the orchestrator and the specialised components it coordinates. No human operator, administrator, or interviewer role exists in the current implementation.

## 4.2 Functional Requirements

**Table 4.1.** Functional requirements.

| ID | Requirement | Verified by |
|---|---|---|
| FR-1 | The system shall present interview questions from a 125-question bank spanning DSA and C-language topics. | `test_orchestrator.py`, T-N10 |
| FR-2 | The system shall accept verbal (voice-transcribed) and code (C) answers. | `test_speech_pipeline.py`, `test_coding_executor.py` |
| FR-3 | The system shall score verbal answers using a three-component semantic evaluator (S1 similarity, S2 concept coverage, R reasoning quality). | `test_evaluator.py`, T-N04, T-N06 |
| FR-4 | The system shall score code answers via isolated sandboxed execution against predefined test cases. | `test_coding_executor.py`; configuration verified at T-N12, and execution-level confirmed on all 18 Docker-dependent tests once a reachable daemon was available (Ch.10 Section 10.18). A separate, secondary quick-run endpoint (`/api/run_code`) had its own test-case-lookup defect, found and fixed in this report's final correction pass (Ch.10 Section 10.20); the primary scoring path exercised by these tests was not affected. |
| FR-5 | The system shall adapt question difficulty after each answer using a trained RL policy constrained by deterministic guardrails. | T-N02, T-N03 |
| FR-6 | The system shall produce a structured, multi-field feedback report after each answer. | `test_qwen_followup_feedback.py` |
| FR-7 | The system shall persist all session and turn data for later retrieval. | `test_persistence_and_history.py`, T-N11 |
| FR-8 | The system shall present a post-session report summarising performance, trends, and per-question feedback. | `apps/web/src/Report.jsx`, T-F01 |
| FR-9 | The system shall degrade gracefully (continue the session) if the RL policy, the Qwen microservice, or the audio pipeline is unavailable. | T-N01, T-U02 |

## 4.3 Non-Functional Requirements

**Table 4.2.** Non-functional requirements.

| ID | Requirement | Status |
|---|---|---|
| NFR-1 | Evaluator response latency should be reasonable for an interactive session. | Measured (T-N09): median 896ms, p95 986ms, warm, n=30, this host (an engineering observation, not a formally specified SLA; none was supplied). |
| NFR-2 | The coding sandbox shall isolate untrusted candidate code from the host. | Configuration verified (T-N12): non-root user, `--net=none`, `--cap-drop=ALL`, `--read-only`, memory/PID limits, all confirmed present in the actual Docker invocation code; execution-level behaviour of each flag confirmed via dedicated tests once a reachable daemon was available (Ch.10 Section 10.18). |
| NFR-3 | The system shall not fabricate metrics or feedback when underlying signals are unavailable. | Partially verified: by design, and by test for the general no-fabrication principle elsewhere in the codebase (e.g. audio confidence/hesitation default to a neutral 0.5 instead of a fabricated value when unavailable). **Not** verified by test for the specific state-preservation case: `test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` currently fails (see Ch.10, Section 10.11); this requirement should not be read as fully verified while that cited test still fails. |
| NFR-4 | The system shall be reproducible: every reported result traces to a stored artifact, config, and git commit. | Enforced throughout Ch.10 of this report. |

## 4.4 Constraints

Single-candidate sessions only; English-language input; requires a local Docker daemon for execution-level code-answer verification; requires local compute capable of running SBERT, FAISS, a fine-tuned CrossEncoder, and a quantised local LLM.
