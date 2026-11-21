# Chapter 2: Problem Definition

## 2.1 Problem Statement

Existing technical-interview preparation tools present a fixed sequence of questions at a fixed or self-selected difficulty, score answers (where scoring exists at all) through binary pass/fail or coarse numeric checks, and provide no structured explanation of *why* an answer was scored as it was. Three specific, interrelated problems follow from this:

1. **No individualised difficulty adaptation.** A single fixed-difficulty question pool is simultaneously too easy for advanced candidates (providing no useful challenge or signal) and too discouraging for candidates still developing foundational competence (providing no scaffolded path to improvement).
2. **No structured, actionable feedback.** A numeric score alone does not tell a candidate which specific concept was missing, which claim was factually incorrect, or how their verbal delivery (hesitation, filler words, pacing) affected the overall impression of their answer.
3. **No multimodal signal capture.** Existing tools evaluate only the textual/code content of an answer, discarding prosodic information (confidence, hesitation, pacing) that is a demonstrably relevant part of real interview performance.

## 2.2 Objectives

**Functional objectives** (as implemented and now verified in this phase — see Chapter 10 for the specific evidence behind each):

- Adaptively select the next question's difficulty based on a reinforcement-learning policy constrained by deterministic pedagogical guardrails, verified against 13 constructed boundary cases (Chapter 10, §10.3).
- Score free-form verbal and code answers through a rubric-anchored, multi-component semantic evaluator, verified against the project's existing human-rated benchmark (64 constructed answers, 8 questions, 3 raters) and 10 newly constructed adversarial/edge-case inputs (Chapter 10, §10.4).
- Capture and use prosodic audio signals (confidence, hesitation) as part of both the adaptive-difficulty decision and the candidate-facing feedback.
- Produce a structured, fifteen-field per-turn feedback report covering strengths, factual errors, missing concepts, and communication observations.
- Execute and evaluate candidate-submitted C code in an isolated sandbox, verified at the configuration level (Chapter 10, §10.6) and, once a local Docker daemon is available, at the execution level via the existing 18-test suite.
- Persist all session and turn data to a relational store with verified referential integrity (Chapter 10, §10.5).

**Non-functional objectives:**

- Graceful degradation: no single component's failure should crash a live session. This phase found and fixed one violation of this objective (the application launcher's Windows crash, Chapter 10, §10.1) and confirmed the objective holds for the evaluator, audio pipeline, and RL policy fallback paths.
- Reasonable latency: evaluator response time was newly measured in this phase (median 896ms warm, Chapter 10, §10.7) as a baseline for future optimisation, distinct from and not claimed to reproduce the project's earlier Paper-1 latency measurement taken under different hardware/conditions.
- A scoped, documented security posture for the one component that executes untrusted input (candidate-submitted code), verified at the configuration level in this phase.

## 2.3 Scope

**In scope:** adaptive technical interviews over spoken/typed verbal answers and C code submissions, covering Data Structures & Algorithms and C-language topics (the current 125-question bank), single-candidate sessions, and the testing/verification programme documented in Chapter 10.

**Explicitly out of scope** (stated here to prevent scope creep in later chapters, consistent with the discipline applied throughout this phase): video or facial/behavioural analysis (not implemented); a multi-agent "bounded-authority coordination" layer described in an auxiliary research-paper draft (confirmed, on inspection, not to exist in the codebase — see Chapter 10, §10.13); new PPO training, reward redesign, or RL experiment campaigns (governed by the project's existing experiment-preregistration requirements, not undertaken in this phase); formal human-subject usability or learning-outcome evaluation (identified as future work).

## 2.4 Assumptions and Constraints

- The system assumes a single candidate per session, English-language spoken or typed input, and a locally available compute environment capable of running SBERT, FAISS, a fine-tuned CrossEncoder, and a quantised 1.5B-parameter local LLM.
- Code evaluation assumes a Docker daemon is available on the host; this phase's testing found this daemon was not running in the development environment used, and documents the resulting, fully attributed test coverage gap (Chapter 10, §10.9) rather than silently working around it.
- Audio-pipeline accuracy (word-error-rate) is not independently verified in this project, as no verified reference-transcript dataset exists; this is stated as a constraint on what can be claimed, not resolved in this phase.
