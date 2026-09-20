# X1-A protocol — claim-scoped fault-injection campaign (Paper 1)

Registered by commit + annotated tag `prereg/X1-A/v1` BEFORE the X1-A evidence run. Harness `x1a_harness.py` (criteria are code, hashed by the tag).
Design source: `research/audit/X1_PROTOCOL_DRAFT.md` §3–§4 and `P0_P1_DECISION_PLAN.md` §8.2. Written by the executing agent; independent methodology review pending.

## 1. Question
For each enumerated dependency fault class that the request path can meet, does the SUT (a) return, (b) avoid fabricating or mis-recording a score, (c) flag the fault, and (d) recover on the next request?
Unit of analysis = the scenario (fault class), never the trial. Deterministic faults use 5 repetitions as a flakiness check, reported as counts (no CI on deterministic replicates, no pooling).

## 2. SUT
Tag `release/app-repair/v1` (commit `980747ff…`); `agents/` and `services/` must equal it. Faults are injected **in-process** against the real `InterviewOrchestrator.handle_voice_answer` path, `DockerCSandbox`, and `services/storage/database.py`; the evaluator/Qwen dependencies are replaced only where the fault itself is the injection (a raising evaluator function; a local stub HTTP server on port 8001 for the Qwen service; a patched executable lookup; a shimmed compile command; a second SQLite connection). No external host is contacted.

## 3. Dependency enumeration (request path) and scenario derivation
| Dependency | Code reference | Failure mode → scenario | Status |
|---|---|---|---|
| Qwen service (feedback) | `agents/orchestrator/feedback_agent.py:_query_qwen_feedback` (client timeout 6.0 s, 2 attempts) | unavailable → FLT-01; slower than timeout → FLT-02 | executed |
| Evaluator | `interview_orchestrator._evaluate_verbal` | unavailable → FLT-03; invalid score (NaN, Inf, 999, −3) → FLT-04 | executed |
| Docker daemon | `coding_executor._resolve_docker_prefix` | unreachable → FLT-05 | executed |
| Compiler toolchain | `coding_executor` compile step (10 s `subprocess` timeout) | outlives the timeout → FLT-06 | executed |
| SQLite | `database.get_connection` (busy timeout 30 s), `save_attempt` | write lock held 2 s (a) / 34 s (b) → FLT-07 | executed |
| Empty input | `handle_voice_answer` empty-transcript branch, `validate_source_safety` | empty/whitespace transcript, empty code → FLT-10 | executed |
| WebSocket transport | `apps/backend/main.py` | reset mid-evaluation → FLT-08 | **not executed** (needs a full backend + WebSocket client harness) |
| Audio/feature extraction | `agents/audio/` | crash → FLT-09 | **not executed** (needs the audio pipeline) |
No claim is supported for FLT-08/09. The scenario list was fixed here from this enumeration, before any X1-A evidence run.

## 4. Scenarios, criteria (all computed by the harness)
Every scenario has a **no-fault control** (same call without the fault) and **oracle-perturbation controls**: a synthetic defective observation (e.g. "false accepted", "score recorded as 0.0", "orphan container", "silent loss") that the same oracle must reject. Perturbation controls test the oracle only; they are **not** mutant builds of the SUT (draft §3 asks for mutant builds; that stronger control was not built here and is a limitation).
- **FLT-01/02 Qwen down / slow:** no exception; returns within SLA (5.0 s down; 2×6.0+3.0 = 15.0 s slow); `llm_status == llm_unavailable`; decision source not Qwen; feedback score, session scores and covered concepts equal the no-fault control; the control did use the LLM stub; next request recovers (`llm_status == available`).
- **FLT-03 evaluator unavailable:** no exception; an infrastructure-failure indication exists (`status == evaluator_unavailable`, or `decision_source == evaluator_unavailable`, or any `*infra*` key, or `infrastructure_errors` entry); **no 0.0 recorded as a candidate score**; no positive fabricated score; control scores normally.
- **FLT-04 invalid score:** for each of NaN, Inf, 999.0, −3.0: no exception; feedback score and every recorded session score finite and in [0, 1]; control valid.
- **FLT-05 Docker unreachable:** `sandbox_error`, not accepted, returns within 2.0 s, no container created, error message present; control accepts; recovery accepts.
- **FLT-06 compiler hang:** ended by the compile timeout (9–13 s); status `compilation_error` with "timed out" in the compiler output; not accepted; **no container still present 3 s after the call returns** (leftovers are then removed and recorded); next submission runs.
- **FLT-07a/b SQLite lock:** rows stored equal acknowledged writes; no partial rows; writes succeed after release; (a) succeeds after waiting for the release; (b) fails visibly with a "locked" error near the 30 s busy timeout (28–33 s).
- **FLT-10 empty input:** no exception for empty and whitespace transcripts; structured no-input outcome (`stt_status == stt_unavailable`, grade `Ungraded`); empty code → `policy_blocked` with a reason. Whether the empty answer consumes an attempt is recorded but is **not** a criterion (no rule is specified).

## 5. Interpretation rules (fixed now)
- Per scenario: `criteria_met` x/5, failed criteria named, `oracle_valid` (every perturbation rejected). No "x/y" across scenarios.
- A scenario whose criteria fail in the fault run is a **defect finding**, reported as found. Fixes only under a new build tag, complete campaign rerun, both results retained (draft §2). A scenario whose oracle is not valid cannot support a claim.
- "Fault-tolerant" may be written **only** if every executed scenario passes with a valid oracle, and then only scoped to the executed fault classes. Otherwise the property is narrowed or dropped ("failure-aware" wording) and failed scenarios are named.
- Not allowed: "recovers from 10/10 faults", any claim for FLT-08/09, generalisation beyond these classes, timing claims beyond the stated SLAs.

## 6. Disclosure: dry run
Before registration the harness was dry-run once for plumbing. The dry run printed only harness errors and oracle-control validity (one threading bug in the lock-holder was found and fixed; the slow scenarios FLT-02/06/07b were plumbing-checked the same way). The author did not see and did not adjust criteria to the SUT outcomes.

## 7. Limits
Single machine; in-process injection rather than process/network-level faults; the Qwen dependency is a local stub (the real model is used in X1-B, not here); no concurrency; SLAs are derived from constants in the SUT code, not from measured behaviour; single evaluator stub result.
