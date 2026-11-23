# 24. Architecture and Baseline Comparison Specification v2 — Equivalence Contract

**Status: SPECIFICATION ONLY — Configuration B does not exist as code.** Supersedes-in-review document 20
(`20_Architecture_and_Baseline_Comparison_Specification.md`), unmodified and preserved. This revision responds
directly to the external review's verdict on document 20: *"Good architectural specification. It needs a much
more precise equivalence contract before coding begins."* This document **is** that contract.

---

## 1. What carries over unchanged from document 20

Section 1 (Configuration A as implemented, including the re-verified Qwen-never-scores and verbal/coding-
separation findings) and the general principle that Configuration B must not be artificially weakened both
carry over unchanged. This document replaces only document 20's §2 ("what cannot be made fully equivalent") with
a precise, binding equivalence contract, and adds a dedicated error-handling equivalence table the reviewer
identified as missing.

---

## 2. The equivalence contract

For each functionality, this table specifies Configuration A's current implementation, exactly how Configuration
B must reproduce it, and the binding condition that makes the two comparable. **Where this table says "reuse,"
it means Configuration B's harness must call the identical function/module from the production codebase — not a
reimplementation, however faithful the reimplementation is intended to be.** This eliminates an entire class of
"was the difference architecture or was it a subtle reimplementation bug" confound before it can arise.

| Functionality | Configuration A | Configuration B requirement | Binding condition |
|---|---|---|---|
| PPO inference | `HybridOrchestrator.suggest()` (`agents/strategy/hybrid_orchestrator.py:184-248`) | **Reuse the same module's `build_rl_observation()` and the same loaded `PPO` model object** via a direct call, not routed through a new `HybridOrchestrator` instance wrapper | Same checkpoint file, same hash: `ppo_final.zip` SHA-256 `2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575`; same `vecnormalize.pkl` SHA-256 `1481ca2c11cb1c2f9ae055c5350fc168359900daea2da3897a6b63f4dfc29df2` (both hashes computed directly from the repository files during this revision, not asserted from memory) |
| Observation construction | `build_rl_observation()` (`hybrid_orchestrator.py:55-158`) | **Reuse the identical function**, called with the identical session-state dict shape | No tolerance for a "simplified" re-derivation — import and call the exact function |
| Observation normalization | `VecNormalize` mean/var loaded from `vecnormalize.pkl` at `HybridOrchestrator._try_load()` | **Reuse the identical normalization arrays**, loaded once from the same file | Same hash as above |
| Action validation | Strict rejection unless `action_space == Discrete(3)` and `observation_space == Box(6,)` (`hybrid_orchestrator.py:278-292`) | **Reuse the identical validation gate** before accepting the loaded checkpoint | No relaxed or additional validation in either configuration |
| Deterministic inference setting | `model.predict(norm_obs, deterministic=True)` | **Identical call signature**, `deterministic=True` | Non-negotiable; stochastic inference would introduce a confound unrelated to architecture |
| Fallback when PPO unavailable/incompatible | `HybridOrchestrator._heuristic_action()` (`hybrid_orchestrator.py:251-257`) | **Reuse the identical function** as a shared utility, not a re-derived equivalent | Guarantees bit-identical fallback behaviour in both configurations |
| Guardrail layer | Orchestrator's **private** copy, `interview_orchestrator.py:1529-1573` (not the canonical `rl/guardrails.py` — see §3 of `23_Revised_Experimental_Proposal_v2.md`) | **Extract this method into a standalone shared function** (e.g. `apply_live_guardrails(...)`, a pure refactor with no behavioural change) that **both** configurations import and call | Bit-identical behaviour including the known, uncorrected `0.40 < perf < 0.65` boundary (deliberately not fixed as part of this work — fixing it is a separate, explicitly out-of-scope engineering decision, per `23_...v2.md` §5.3) |
| Feedback construction (template path) | `FeedbackAgent.generate()` / `.generate_code_feedback()` (`agents/orchestrator/feedback_agent.py:85-360`) | **Reuse the identical methods** on the existing `FeedbackAgent` class (or an identical instance), called directly rather than through the orchestrator's dispatch | Same misconception dictionary, same trend/justification logic, same templates |
| Qwen prompts and HTTP client | `FeedbackAgent._query_qwen_feedback()` (`feedback_agent.py:525-573`), `_build_followup_prompt`/`_build_feedback_prompt` (`services/qwen/app.py:416-460,460-520`) | **Reuse the identical prompt-building and HTTP-call functions**, same endpoint, same timeout, same retry count | Same Qwen model/version, same prompt text for identical inputs — no Configuration-B-specific prompt engineering |
| Question selection | `select_questions()` (`apps/backend/main.py:590-727`, a plain function, already shared infrastructure) | **Reuse the identical function** | Identical inputs (topics, num, difficulty, exclude_ids, candidate_state) must produce identical outputs in both configurations — this is a plain deterministic function, so this is directly testable as a precondition, not just an assumption |
| Score validation | `ScoreValidator.validate()` (`agents/validation/score_validator.py`) | **Reuse the identical class/method** | Same `mandatory_cap`, `max_mistake_penalty`, `coding_failure_multiplier` constants |
| Timing modifier | `QuestionTimer.compute_timing_modifier()` (`agents/timing/timer.py`) | **Reuse the identical class/method** | Same `delta_fast`/`delta_overrun`/`fast_threshold`/`min_score_for_fast_bonus` constants |
| Evaluator (verbal) | `services/evaluator/app.py:evaluate()` | **Reuse the identical function** (already a standalone service-call, no orchestrator-specific wrapping to replicate) | Same model artifacts, same formula |
| Coding sandbox | `agents/coding_executor/coding_executor.py:evaluate_c_submission()` | **Reuse the identical function** | Same Docker image, same security flags, same timeout/memory/pids limits |
| Rollback/retry invariants | `InterviewOrchestrator._rollback_tentative_attempt()` (`interview_orchestrator.py:790-817`) — restores `scores`/`answers`/`difficulty_history`/follow-up counters to exact pre-attempt length | **Reproduce the identical invariant**: after a rollback, every tracked array/counter must return to its exact pre-attempt state | Verified by a dedicated equivalence test (§4) before any comparative data collection, not assumed from the design description |
| Best-attempt selection | `InterviewOrchestrator._select_best_attempt()` (`interview_orchestrator.py:914-934`) — highest score, then fewest missing concepts, then most recent | **Reuse the identical selection function** | Same priority order, same tie-breaking |
| Persistence | `services/storage/database.py` (18 plain functions, already shared infrastructure) | **Reuse identically**; Configuration B's runs must write to a separate, clearly labeled table/namespace so comparative-run data is never mixed into production session history | Schema-identical; namespace-separated |

**What this table deliberately does not allow:** any row where Configuration B "reimplements equivalent logic."
Every row is either "reuse the identical production function" or, for the one row where a true architectural
difference is the point (control-flow consolidation itself — i.e., which class calls which function, in what
order, inside one controller vs. several), that difference is the experimental variable, not a confound to
control for.

---

## 3. Error-handling equivalence table (new, per reviewer's P0-adjacent requirement)

For each failure mode, Configuration A's current, already-implemented behaviour (cited to its source) is the
**required** behaviour for Configuration B. Configuration B may not omit any of these; if the consolidated
control flow makes a particular failure mode structurally impossible to reproduce identically, that must be
disclosed as an explicit, named implementation difference before any comparative run, not discovered afterward.

| Failure mode | Configuration A's current behaviour (source) | Required of Configuration B |
|---|---|---|
| Evaluator unavailable | `InterviewOrchestrator._fail_closed_evaluator_unavailable()` (`interview_orchestrator.py:542-587`): no score recorded, no difficulty change, attempt not counted, timer restarts | Identical: no fabricated score, no state mutation, candidate may retry |
| Docker/sandbox unavailable | `DockerCSandbox.compile_and_execute()` (`coding_executor.py:165-186`): returns `status: "sandbox_error"`, `passed: False`, `coding_score: 0.0`, never executes unsandboxed | Identical structured failure; untrusted code must never run outside the sandbox in either configuration |
| Qwen/feedback-LLM unavailable | Orchestrator falls back to `_synthesize_structured_followup`/deterministic template (`interview_orchestrator.py:1807-1814`; `feedback_agent.py`'s deterministic justification path) | Identical deterministic fallback, reusing the same function (per §2's "feedback construction" row) |
| Invalid/incompatible PPO checkpoint | `HybridOrchestrator._try_load()` rejects and sets `ready=False`/`is_compatible=False` (`hybrid_orchestrator.py:259-321`); orchestrator falls back to the non-RL heuristic recovery path | Identical rejection logic (reused per §2) and identical fallback |
| Invalid/malformed feedback-LLM response | `_validate_feedback_output()` (`services/qwen/app.py:583`) rejects non-conforming output before it reaches the candidate | Identical validation, reused directly |
| Persistence failure (SQLite write fails) | Orchestrator's `save_attempt`/`save_session` call sites wrap in `try/except Exception: pass` and continue without crashing the turn (e.g. `interview_orchestrator.py:456-460`) | Identical non-fatal degradation — a persistence failure must not crash or corrupt an in-progress interview in either configuration |
| Interrupted interview (WebSocket disconnect) | `orch.mark_abandoned()` (`interview_orchestrator.py:276-278`), called from `apps/backend/main.py`'s `WebSocketDisconnect` handler | Identical session-status transition |
| Retry/rollback | See §2's dedicated row | See §2 |

---

## 4. Pre-comparison verification requirement (Stage 3 gate)

Before any comparative benchmark run begins (Stage 3 of `23_Revised_Experimental_Proposal_v2.md` §9),
Configuration B's harness must pass a **dedicated equivalence test suite**, separate from the comparative
experiment itself, that exercises every row of §2 and §3 and confirms bit-identical output given identical
input. This test suite's pass/fail result is a **gate**, not a result to be reported in the comparative
findings — it establishes that the harness is measuring architecture, not reimplementation drift, before a
single candidate-facing comparison is collected.

---

## 5. What remains an open, disclosed limitation

- Control-flow consolidation itself (one class vs. several specialised classes) is, by design, not something
  that can be made "equivalent" between A and B — it is the variable under test, and is documented as such
  here rather than listed as a gap.
- Error-isolation *granularity* (where a try/except boundary sits) may differ structurally even when the
  *behaviour* is made identical per §3; if Configuration B's consolidated structure cannot replicate a specific
  isolation boundary at all, that must be disclosed by name before the comparative run, consistent with
  `23_Revised_Experimental_Proposal_v2.md` §6's rule 4.
