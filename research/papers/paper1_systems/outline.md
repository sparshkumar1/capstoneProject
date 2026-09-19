# Paper 1 Outline: Systems Architecture, Security & Fault Tolerance
**Target Venue:** ATIS 2026 / IEEE Access
**Title:** PREPAIred: An Evidence-Grounded Adaptive Multimodal Framework for Technical Interview Assessment and Feedback

## Section 1: Introduction
- Motivation: Challenges of evaluating free-form technical responses and untrusted code.
- Pitfalls of monolithic LLM grading architectures (hallucinations, non-determinism, security risks).
- Core thesis: Asynchronous decoupled architecture isolates grading from generation and enforces defense-in-depth container isolation.

## Section 2: Related Work
- Automated code evaluation systems (Online judges, sandbox models).
- LLMs in technical assessment and hallucination risks.
- Socratic tutoring systems and dialogue state tracking.

## Section 3: System Architecture
- Hub-and-spoke orchestrator (InterviewOrchestrator).
- Docker C Sandbox containment primitives (--cap-drop=ALL, --net=none, tmpfs, UID 1001).
- Multi-attempt candidate history and WAL persistence.
- Socratic follow-up FSM.

## Section 4: Security Analysis & Threat Model
- Attack surface: Malicious C source code execution.
- 9-vector security negative testing matrix (SEC-01 to SEC-09).
- Defense-in-depth: Why static filters fail (SEC-02) and kernel isolation succeeds.

## Section 5: Experimental Evaluation
- EXP-SYS-2: Subsystem latency profiling across 50 iterations.
- EXP-SYS-3: Architectural component removal resilience study.
- EXP-LLM-1: Feedback grounding and deterministic fallback verification.

## Section 6: Discussion & Conclusion
- Scalability to multi-container clusters.
- Operational reliability under production constraints.
