# Chapter 2: Problem Definition

## 2.1 Problem Statement

Existing technical-interview preparation tools give every candidate a fixed sequence of questions at a fixed or self-selected difficulty. Where scoring exists at all, it's a binary pass/fail or a coarse numeric check, and none of it explains *why* an answer was scored as it was. Three specific, interrelated problems follow from that:

1. **No individualised difficulty adaptation.** A single fixed-difficulty question pool cuts both ways. It's too easy for advanced candidates, who get no useful challenge or signal from it. And it's too discouraging for candidates still building foundational competence, who get no scaffolded path to improvement.
2. **No structured, actionable feedback.** A numeric score alone doesn't tell a candidate which specific concept was missing, or which claim was factually wrong. It also says nothing about how their verbal delivery (hesitation, filler words, pacing) shaped the overall impression their answer made.
3. **No multimodal signal capture.** Existing tools evaluate only the textual or code content of an answer. Prosodic information (confidence, hesitation, pacing) gets discarded entirely, despite being a demonstrably relevant part of real interview performance.

## 2.2 Objectives

**Functional objectives** (as implemented and now verified in this phase; see Chapter 10 for the specific evidence behind each):

- Select the next question's difficulty adaptively, using a reinforcement-learning policy constrained by deterministic pedagogical guardrails, verified against 13 constructed boundary cases (Chapter 10, Section 10.3).
- Score free-form verbal answers through a rubric-anchored, multi-component semantic evaluator. This was verified against the project's existing human-rated benchmark (64 constructed answers, 8 questions, 3 raters) and against 10 newly constructed adversarial/edge-case inputs (Chapter 10, Section 10.4). Code answers take a completely separate path: isolated sandboxed execution against predefined test cases, not the semantic evaluator. This is detailed in Chapter 6, Section 6.2 vs. Chapter 8.
- Capture prosodic audio signals (confidence, hesitation) and use them in both the adaptive-difficulty decision and the candidate-facing feedback.
- Produce a structured, fifteen-field per-turn feedback report covering strengths, factual errors, missing concepts, and communication observations.
- Execute and evaluate candidate-submitted C code inside an isolated sandbox. This was verified at the configuration level (Chapter 10, Section 10.6), and, with a live Docker daemon, at the execution level too, via the full 18-test Docker-dependent suite (Chapter 10, Section 10.18).
- Persist all session and turn data to a relational store with verified referential integrity (Chapter 10, Section 10.5).

**Non-functional objectives:**

- Graceful degradation: no single component's failure should crash a live session. This phase found and fixed one violation of that objective (the application launcher's Windows crash, Chapter 10, Section 10.1). It confirmed the objective otherwise holds for the evaluator, audio pipeline, and RL policy fallback paths.
- Reasonable latency: this phase measured evaluator response time for the first time (median 896ms warm, Chapter 10, Section 10.7) as a baseline for future optimisation. This figure is distinct from, and not claimed to reproduce, the project's earlier Paper-1 latency measurement, which was taken under different hardware and conditions.
- A scoped, documented security posture for the one component that executes untrusted input (candidate-submitted code), verified at the configuration level and, in this phase's later extension, at the execution level too (Chapter 10, Section 10.18).

## 2.3 Scope

**In scope:** adaptive technical interviews over spoken/typed verbal answers and C code submissions, covering Data Structures & Algorithms and C-language topics (the current 125-question bank), single-candidate sessions, and the testing/verification programme documented in Chapter 10.

**Explicitly out of scope** (stated here to prevent scope creep in later chapters, in keeping with the discipline applied throughout this phase): video or facial/behavioural analysis, which isn't implemented. Also out of scope is a multi-agent "bounded-authority coordination" layer described in an auxiliary research-paper draft; on inspection, it was confirmed not to exist in the codebase (see Chapter 10, Section 10.13). New PPO training, reward redesign, or RL experiment campaigns are out too, governed by the project's existing experiment-preregistration requirements and not undertaken in this phase. And formal human-subject usability or learning-outcome evaluation is left as future work.

## 2.4 Assumptions and Constraints

- The system assumes a single candidate per session and English-language spoken or typed input. It also assumes a locally available compute environment able to run SBERT, FAISS, a fine-tuned CrossEncoder, and a quantised 1.5B-parameter local LLM.
- Code evaluation needs a Docker daemon on the host. That daemon wasn't actually running when this phase's testing started, so the resulting gap in test coverage got written up and fully attributed rather than papered over (Chapter 10, Section 10.9). It didn't stay unresolved, either — once a reachable daemon came online, a later, separately-scoped extension went back and closed it (Chapter 10, Section 10.18).
- We haven't independently verified audio-pipeline accuracy in terms of word-error-rate, mainly because there is no verified reference-transcript dataset to measure it against. That's a limit on what this report can claim, and it stays open rather than being resolved here.
