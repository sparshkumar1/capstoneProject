# 20. Architecture and Baseline Comparison Specification

**Status: SPECIFICATION ONLY — Configuration B does not exist as code.** This document explains the actual
architecture (Configuration A, as implemented), and specifies exactly what a scientifically fair Configuration B
would consist of, so that implementation can be reviewed and approved before any code is written. Nothing here
has been built.

---

## 1. Configuration A — the existing architecture, as it actually exists

This section is a condensed, citation-preserving summary of `17_Architecture_Audit_Report.md`; see that document
for full evidence trails. It is reproduced here so this specification is self-contained for reviewers who have
not read the full audit.

### 1.1 Classification matrix (carried over, unchanged)

| Component | File | Class | Autonomous? | Decides independently? | Live path? |
|---|---|---|---|---|---|
| InterviewOrchestrator | `agents/orchestrator/interview_orchestrator.py` | B | No (reactive) | Conditional branching, not autonomy | Yes |
| HybridOrchestrator (PPO) | `agents/strategy/hybrid_orchestrator.py` | A/B | No (stateless per call) | Yes, via a trained forward pass | Yes |
| Guardrails (live copy) | `interview_orchestrator.py:1529-1573` | C | No | Fixed rules only | Yes |
| Guardrails (canonical) | `rl/guardrails.py` | C | No | Fixed rules only | **No** (training/eval only) |
| FeedbackAgent | `agents/orchestrator/feedback_agent.py` | B | No | Template logic + optional LLM text | Yes |
| DockerCSandbox | `agents/coding_executor/coding_executor.py` | C | No | Fixed comparison rules | Yes |
| Qwen microservice | `services/qwen/app.py` | B | No | Generates text only; **never computes the numeric score** (re-verified, §1.3 below) | Yes |
| Evaluator | `services/evaluator/app.py` | C | No | Fixed weighted formula | Yes |
| ScoreValidator / QuestionTimer / SessionLogger / storage | various | D | No | Fixed arithmetic / CRUD | Yes |
| select_questions (production) | `apps/backend/main.py:590` | C | No | Fixed scoring heuristic | Yes |
| question_selector.py | `agents/question_selector/question_selector.py` | E | — | — | **No** (self-documented baseline/research artifact) |
| InterviewEnv / simulated_candidate | `rl/env/interview_env.py`, `rl/training/simulated_candidate.py` | E | — | — | **No** (training/eval only) |

### 1.2 Communication topology

Hub-and-spoke, verified by a repository-wide grep for cross-agent imports (zero matches) — see
`17_Architecture_Audit_Report.md` §4.1. All interaction is either (a) the orchestrator calling a helper
component directly, or (b) `FeedbackAgent` calling the Qwen microservice directly over HTTP (the one documented
exception). No component negotiates, votes, or exchanges messages with a peer component as an equal; every
decision has exactly one producing code path.

### 1.3 Responsibility boundaries re-verified for this specification

Two boundary claims were specifically re-checked against current source during this task (not merely restated
from the prior audit), because the comparison design depends on them being accurate:

- **Qwen never computes a numeric score.** Every `final_score` assignment in `services/qwen/app.py` (lines 418,
  462, 525, 624, 718, 828) reads `ev.get("final_score", ...)` from the caller-supplied `structured_evaluation`
  dict — the evaluator's own score, echoed back, never independently derived. `FeedbackAgent.generate()`
  (`feedback_agent.py:98,170-198`) discards whatever `final_score` a Qwen response might contain and uses
  `eval_result.get("final_score", 0.5)` instead. **Implication for Configuration B:** a unified controller must
  likewise treat the evaluator (SBERT/FAISS/CrossEncoder) as the sole source of numeric scores, with any LLM
  component restricted to narrative text — anything else would make Configuration B not comparable to A on this
  axis.
- **Verbal evaluation and Docker C execution are two separate code paths**, confirmed (again) by the absence of
  any cross-import between `services/evaluator/app.py` and `agents/coding_executor/coding_executor.py`.
  **Implication for Configuration B:** the unified controller must also keep these as two separately invoked
  tools (same two underlying services), not merge them into one scoring function — merging them would change
  what is being measured (a capability difference, not an architecture difference).

---

## 2. Configuration B — unified single-controller baseline (specification)

### 2.1 Design principle

Configuration B consolidates the **control and coordination logic** currently distributed across
`InterviewOrchestrator` + `HybridOrchestrator` + the orchestrator's guardrail method + `FeedbackAgent`'s
decision logic into **one controller class**, while preserving calls to the **same underlying tools, models,
and deterministic services** wherever technically possible. The experimental variable is *how many specialised
decision-making classes mediate a turn, and whether a central orchestrator dispatches between them*, not *which
models or tools exist*.

### 2.2 What is consolidated (changes between A and B)

| Responsibility | Configuration A (existing) | Configuration B (proposed) |
|---|---|---|
| Turn-lifecycle control flow | `InterviewOrchestrator` (dedicated class, `interview_orchestrator.py`, 2300 lines) | Folded into the single controller's own turn-handling method(s) |
| Difficulty decision | `HybridOrchestrator.suggest()` called as a separate object | Same PPO checkpoint, same `build_rl_observation()` logic, called as a plain function/method inside the single controller — not a separate class instance the controller "delegates to" |
| Guardrail override | `InterviewOrchestrator._apply_guardrails()`, a private method on the orchestrator | Same six rules, implemented as a plain function called inline by the single controller (functionally identical logic, no separate "agent" framing) |
| Structured feedback construction | `FeedbackAgent` (separate class, `feedback_agent.py`) | Same template logic and same Qwen-call-with-fallback pattern, implemented as a method on the single controller rather than a delegated object |
| Timing modifier | `QuestionTimer` (separate class) | Same fixed-formula logic, inlined |
| Score validation | `ScoreValidator` (separate class) | Same fixed-rule logic, inlined |

### 2.3 What remains shared (must be identical in both configurations)

- The evaluator service (`services/evaluator/app.py`) — same SBERT/FAISS/CrossEncoder pipeline, same weighted
  formula (`0.15·S1 + 0.35·S2_eff + 0.50·R`), called by both configurations as an external tool/function.
- The Docker sandbox (`agents/coding_executor/coding_executor.py`) — same security configuration, same
  compile/execute/compare logic, called identically by both.
- The Qwen microservice (`services/qwen/app.py`) — same model, same endpoints, called identically by both, with
  the same constraint that it supplies narrative text only (§1.3).
- The PPO checkpoint (`rl/checkpoints/seed_123/`) — same weights, same strict action/observation-space
  validation, same deterministic-inference call, invoked by both (in A, via `HybridOrchestrator`; in B, via a
  direct call from the single controller).
- The question bank and the production `select_questions()` scoring heuristic (`apps/backend/main.py:590`) —
  identical in both, since it is already a plain function, not a class the orchestrator "delegates to" in any
  agent-like sense.
- The candidate-state schema and SQLite persistence layer (`services/storage/database.py`).
- Benchmark scenarios, personas, random seeds, and evaluation rubrics (per
  `19_Revised_Experimental_Proposal.md` §5–§6).

### 2.4 What cannot be made fully equivalent, and why

- **Code organization is, by definition, different** — Configuration B has no separate `HybridOrchestrator`/
  `FeedbackAgent`/`ScoreValidator`/`QuestionTimer` classes; this is the entire point of the comparison, not a
  confound to eliminate. It is documented here so reviewers do not mistake it for an oversight.
- **Error-isolation boundaries differ.** In Configuration A, a failure inside `FeedbackAgent.generate()` is
  caught at the orchestrator's call site (`interview_orchestrator.py:1479-1480`, a bare `except Exception: pass`
  that falls back to returning `eval_result` as-is). In a single-controller design, the equivalent try/except
  would need to be placed around the inlined feedback-construction code block instead of around a delegated
  method call. This is an unavoidable structural difference that should be documented per-scenario if it
  produces an observable difference in failure behaviour (metric category G, `19_...md` §6).
- **Testability and logging granularity may differ** — Configuration A's `SessionLogger` calls are scattered at
  each sub-component's call site; a single controller may log at coarser or finer granularity depending on how
  it is implemented. This must be normalized in the comparison harness (log the same events at the same
  semantic points) rather than left to vary incidentally.
- **This is not a reimplementation of Qwen, the evaluator, the sandbox, or the PPO checkpoint** — those remain
  byte-for-byte the same artifacts in both configurations. Any observed difference in E (coding workflow) or D
  (multimodal integration) outcomes must therefore be attributable to *how* the single controller sequences and
  interprets their outputs, not to the tools themselves being different.

### 2.5 Technical feasibility assessment

Building Configuration B is technically feasible without touching production code: it requires a new, separate
module (e.g. under a new `research/architecture_comparison/` directory, never inside `agents/` or
`apps/backend/`) that imports the same underlying tool-level functions/classes (`evaluate_c_submission`,
`services.evaluator.app.evaluate`, `HybridOrchestrator`'s model-loading logic or a direct `PPO.load()` call,
the Qwen HTTP client pattern) and reimplements only the control flow currently spread across
`InterviewOrchestrator`/`FeedbackAgent`/`ScoreValidator`/`QuestionTimer` as methods on one class. No change to
`agents/`, `apps/backend/`, `services/`, or `rl/` is required to build it. **This assessment is not an
implementation** — it confirms feasibility for the approval decision; the module does not exist yet.

---

## 3. Fairness checklist (to be verified at implementation time, not yet satisfied because nothing is built)

- [ ] Same PPO checkpoint hash used by both configurations.
- [ ] Same evaluator formula and model artifacts (SBERT/CrossEncoder weights) used by both.
- [ ] Same Docker image and security flags used by both.
- [ ] Same Qwen model and prompt templates used by both (or, if Configuration B's single controller builds its
      own prompts, they must be reviewed for equivalence to A's, not weakened versions).
- [ ] Same question bank, same benchmark scenario set, same personas, same seeds.
- [ ] Same evaluation rubric applied by the same (blinded) raters to both configurations' outputs.
- [ ] No functionality present in A (fail-closed handling, retry/rollback, best-attempt selection, follow-up
      injection policy) silently dropped from B without being explicitly reimplemented or explicitly documented
      as an intentional, disclosed difference.

This checklist is the concrete operationalization of the master task's instruction "do not intentionally weaken
the baseline."
