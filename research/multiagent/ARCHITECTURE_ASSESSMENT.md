# PREPAIred multi-agent programme — Phase 1 architecture assessment

Branch `research/adcom2027-multiagent-final`, created from `adcom2027/multiagent` @ `3ccad11` (which carries the
strict-contract and circuit-breaker defaults). Frozen references (never modified): `cb888f2` (research snapshot) and its
parent `54a5b73` (engineering freeze). Working tree was clean at the start. Date: 2026-10-02. Deadline: 2026-10-15
(taken from the task text; the official CFP is not reachable from this sandbox and is not verified).

Evidence labels: **code** (read in source), **run** (executed here), **claim** (stated by the brief or an earlier document, not re-checked).

## 0. Environment facts that constrain the programme
- No Qwen GGUF weights in the repo (`services/qwen/app.py` expects `models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf`); Git LFS tracks only the evaluator
  weights. **Consequence: no live-LLM experiment can be run in this sandbox. Anything involving LLM text is either not run or run on the user's workstation.**
- The scratch venv (`…/scratchpad/av`, Python 3.11) runs the suite; the project's own venv (Windows, 3.12) is not available. The 407-test total (363 unit + 16 integration + 28 frontend)
  is a **claim**; `apps/web/node_modules` is absent, so the 28 frontend tests cannot be run here without `npm install` (network access not tested).
- **Pre-change baseline on this branch (run):** `23 failed, 329 passed, 14 skipped, 36 errors` (35 s). Same failing set as the `cb888f2` snapshot; failures are Docker-sandbox,
  FAISS/model-download and the project's one documented known failure. This is the number later runs are compared against, not the 407.

## A. What already exists
| Component | Code | Nature |
|---|---|---|
| Session controller (hub) | `agents/orchestrator/interview_orchestrator.py` (2,436 lines, class at :126) | one `asyncio.Lock`, one state dict, fixed per-turn pipeline (`handle_voice_answer` :379) |
| Evaluator | `services/evaluator/app.py` via `apps/backend/main.py::_run_integrated_evaluator` | learned scorer, authoritative for scores |
| Strict contract + validator | `_is_unit_score` + `_evaluate_verbal`; `agents/validation/score_validator.py` | deterministic |
| Feedback | `agents/orchestrator/feedback_agent.py` (+ Qwen `/feedback`, lexical validator `_validate_feedback_output`) | LLM-optional text generator with template fallback |
| Follow-up | `_decide_and_inject_followup` / `_inject_followup_question` (:1846/:1885) + Qwen `/followup` | threshold policy + LLM text, cap 2 consecutive |
| Difficulty | `agents/strategy/hybrid_orchestrator.py::suggest` (PPO, frozen checkpoint, `deterministic=True`) then `_apply_guardrails` (:1655, inline copy) | learned policy + rules |
| Circuit breaker | `agents/orchestrator/circuit_breaker.py` (`QWEN_BREAKER`, process-global) | deterministic |
| Question flow | `_select_and_send_question`, `_prepare_next_question`, `_rebuild_remaining_questions`, `_next_type_from_action` | deterministic |
| RL env/training | `rl/env/interview_env.py`, `rl/training/*`, `rl/guardrails.py` | frozen |
| ADCOM artefacts | `paper/adcom2027/*` (replay harness, E1–E5, 71-check verifier, manuscript) | prior single-controller study |

## B. What can be reused
Replay harness (`paper/adcom2027/experiments/harness.py`), the experiment-record conventions (pre-registration tags, `RUN_LEDGER.md`, number-generation scripts),
the strict contract, the breaker (with fixes), the PPO wrapper (as an input to arbitration), the evaluator's evidence payload, Paper-3's persona harness
(`research/confirmatory/X3-A/x3a_lib.py`, read-only) for a SYNTHETIC policy-level comparison, and the existing multi-component tests.

## C. What is genuinely agentic today
By the weak notion of agency (autonomy, social ability, reactivity, pro-activeness): only the PPO policy is a reactive, learned decision-maker. No module
has private state that persists across turns except (i) the audio module's `_sessions` dict and (ii) the global breaker. No peer communication, no planning,
no negotiation. **The existing system is an orchestrator-based pipeline, as the earlier review concluded; none of the existing roles is an agent in any strong sense.**

## D. Deterministic infrastructure (stays deterministic)
Authoritative scoring and score validation, timer, baseline schedule, budget/termination rules, bounds [1,5], persistence (SQLite), sandbox, STT, hard session limits, guardrails,
schema/range checks, state commit. The brief asks for exactly this split; I keep it.

## E. What must change (and the smallest design that is honest)
**Design decision 1 — what "agent" means here (honest framing, not a rename).** I will implement agents as *proposers with bounded authority and private state*, not
as LLM loops. With no LLM available in this sandbox, a "genuinely multi-agentic" claim cannot rest on LLM autonomy. What can be built, tested and measured here:
1. **Strategy Agent.** Keeps a private, persistent *weakness ledger* across turns (per-concept miss counts, probe history, trend). Reads an immutable `TurnObservation`; emits a structured
   `StrategyProposal` (difficulty action ∈ {Easier, Same, Harder}, probe request {concept, kind}, strategy mode, confidence, evidence references). It acts proactively (schedules probes
   of persistent weaknesses that no single-turn threshold would trigger) and reactively (to the PPO proposal and evaluator evidence).
2. **Coaching Agent.** Keeps a private per-candidate *coaching history* (which hints/examples were already given, repeated misconceptions). Emits a structured `CoachingPlan`
   (depth, hint/no-hint, example/no-example, misconception emphasis, remediation tag, tone), consumed by the feedback generator (template path and the LLM path).
3. **Grounding validator (deterministic, not an agent).** Checks that every concept a coaching/feedback plan cites is present in the evaluator's evidence payload.
   Labelled a validator, not an agent, in all text.
4. **Arbitrator (deterministic, not an agent).** Resolves proposals from guardrails, PPO, Strategy and Coaching by a documented precedence; records accepted/rejected/modified + reason.
5. **Coordinator.** Calls agents with a timeout, validates output against schemas and the authority matrix, applies arbitration, and hands the *authoritative commit* back to the hub.
   The hub remains the only writer of authoritative state.

What I will **not** claim: decentralised intelligence, LLM-driven autonomy (unless a workstation run actually produces it), multi-agent RL, or that the agents "improve coaching".
Whether *rule-and-memory agents with typed messages* deserve the word "agent" is exactly what a reviewer will ask; the paper will state the criteria (private persistent state, bounded
authority, proactive proposals, explicit communication) and say the decision mechanism is rule/ledger-based in this implementation, with an optional LLM backend as future/workstation work.
If the user prefers LLM-backed decision-making as the paper's headline, that needs a workstation and is a different (larger) programme; I flag it rather than assume it.

**Design decision 2 — authority.** The hub commits state. Agents never write `_state`; they return proposals. Proposals carry `state_version`; the coordinator rejects stale ones
(optimistic concurrency). Hard constraints (bounds, budget, baseline phase, infrastructure failure, evaluator-unavailable) are applied by the arbitrator before and after any proposal.

**Design decision 3 — arbitration precedence (to be tested, not assumed optimal):**
1. hard session constraints (bounds [1,5], budget, baseline phase, evaluator unavailable/infra failure) — absolute
2. guardrail overrides (the existing rule layer, applied last to the selected candidate; G3/G5 hold, G6 raises, so they are not only 'safer-direction' rules) — whenever a rule fires it wins over every proposal
3. validated Strategy proposal with confidence ≥ τ and ≤ 1 step from the current difficulty — wins over PPO when it disagrees (recorded as a *conflict*)
4. PPO action
5. non-RL heuristic fallback (when PPO is unavailable)
Rationale: the strategy agent sees misconception persistence that PPO's 6-D state cannot; guardrails are the pre-existing safety layer. The *ablation* (remove arbitration / remove Strategy / PPO-only)
measures what this choice does; it is a design hypothesis, and PPO-vs-Strategy superiority is **not** assumed.

**Design decision 4 — PPO role.** PPO remains the difficulty policy. In the multi-agent config its output is an *input proposal* to arbitration (not removed, not relabelled as an agent, not MARL).

**Design decision 5 — guardrail divergence (brief §10.4).** Evidence (earlier run; re-run planned): the deployed inline `_apply_guardrails` disagrees with `rl/guardrails.py` on 12.4 % of a synthetic grid
(hes = 1 − conf), and the deployed orchestrator never imports `rl.guardrails`; Paper 3 and the training env use the canonical one. Plan: add a config key `guardrail_impl` with values
`legacy_inline` (unchanged; default for the baseline config, preserves historical behaviour) and `canonical` (calls `rl.guardrails.apply_canonical_guardrails`); the multi-agent config uses `canonical`.
Add regression tests pinning the *known* divergence set for `legacy_inline` and the parity of the canonical path with Paper 3's call signature. **Approval flag:** switching the shipped default changes deployed behaviour; I will not change the default without the user's decision.

**Design decision 6 — scorer semantics (brief §10.6).** Set the CrossEncoder activation explicitly to sigmoid (the semantics the calibration assumed under the `<3.0` pin) and add a unit test with a fake model returning logits,
plus a golden-score test that skips when the LFS weights are absent. Historical stored scores are not transformed; earlier offline reconstruction with sigmoid reproduced stored R (mean |Δ| 0.020).

**Design decision 7 — historical experiments.** Introduce explicit experiment configs (`research/multiagent/configs/*.yaml`) carrying `strict_evaluator_contract`, `qwen_breaker`, `guardrail_impl`, `multiagent`, seeds and commit.
Historical E1/E2 re-runs use the old flags explicitly (`strict_evaluator_contract: false`, breaker disabled) and are labelled HISTORICAL-REPLAY; old outputs are not overwritten.

## Required changes — files likely touched
New: `agents/multiagent/{contracts,authority,strategy_agent,coaching_agent,grounding,arbitration,coordinator,trace}.py`; `research/multiagent/{configs,protocols,experiments,results,analysis}/`; tests `tests/unit/test_ma_*.py`, `tests/integration/test_ma_*.py`.
Modified (minimal, behind config flags, default off): `interview_orchestrator.py` (config keys, coordinator hook in `handle_voice_answer`, `_adapt_difficulty`, follow-up decision; `guardrail_impl`), `feedback_agent.py` (optional `coaching_plan` input),
`circuit_breaker.py` (5xx = failure, probe release, per-name instances), `services/evaluator/app.py` (explicit activation; placeholder-string leakage), `requirements/evaluator.txt` (pin).
Not touched: anything in the CLAUDE.md frozen set, `rl/checkpoints/*`, reward/state/action definitions, existing tests' expectations.

## Risks
1. **"Agent" label risk** (above) — mitigated by criteria + honest decision-mechanism statement; may still be judged as rules-with-extra-steps.
2. **No live LLM** — all new evidence is REPLAY/SYNTHETIC; LLM-path claims limited to code and unit tests.
3. **Simulator coupling (M7 in the prior audit):** Paper 3's persona simulator has its 50 %-performance point at the evaluation target; a rule agent that tracks perf ≈ 0.5 would look good *by construction*. Any SYNTHETIC tracking result must be reported with that caveat and with Constant-Same-without-guardrails as the reference.
4. **Hub is a 2,436-line god object**; hooks must be small. Duplicate handlers (`handle_code_submission`) must get the same hooks or be explicitly out of scope.
5. Behavioural changes to defaults would invalidate prior papers' reproducibility notes — hence flags default off.
6. Time: 13 days; the order below is chosen so each stage leaves a coherent state.

## Experiments planned (to be pre-registered with a hashed, tagged protocol before running)
Metrics are fixed in advance: valid-decision rate, schema-violation rate, stale/duplicate rejection counts, conflict and fallback rates, invariant violations (I1–I7 style), session completion, difficulty-adaptation behaviour
(action distribution, oscillation), agent-call counts, p50/p95 per-turn latency, grounding acceptance (corrected payloads). Units: session (replay), persona (SYNTHETIC policy-level, seed as second factor).
- **XA (REPLAY, deterministic):** baseline controller vs multi-agent config on the 8×8 recorded-answer sessions; ablations: −Strategy, −Coaching, −arbitration, −grounding, −PPO, −communication (agents see no peer messages), rule-only fallback.
- **XB (REPLAY + FAULT-INJECTED):** agent faults (malformed, timeout, crash, stale state_version, duplicate response, conflicting proposals) × {authority checks on/off}; FAULT→DETECTION→RESPONSE→STATE→USER→LIMITATION table generated from outputs.
- **XC (SYNTHETIC):** persona-level difficulty tracking in the Paper-3 harness (read-only), Strategy Agent as a policy vs PPO+G vs Constant-Same (±G), with the M7 caveat.
- **XD (REPLAY, grounding):** rebuilt probe with unambiguous payloads; report corrected rates and separately the artefact count (17/64 overlapping placeholder).
- **XE (historical):** E1/E2 re-runs with explicit old flags, E2 breaker with 5xx/cancel/concurrency cases; each labelled with commit/config.
- Latency/overhead: measured on the same harness; model-call counts reported; token counts unavailable (no LLM) and stated as such.

## Paper consequences
The ADCOM manuscript is rewritten around the implemented system and the evidence actually produced; old results enter only as HISTORICAL with corrections (13/14, Finding 1 reframed, Clopper–Pearson reported or dropped, guardrail divergence, placeholder artefact, scorer-activation note).
Track fit is reassessed after XA–XE; "Core multi-agent systems" is claimed only for what the design supports (centralised, role-specialised, bounded-authority agents; no decentralised intelligence; PPO not MARL).
Overlap with ICITIIT/INDIACom/ICETC Paper 1 is re-examined once the new contribution (arbitrated proposals with private-state agents) is concrete; the author decides on submission.

## Staged order of work
1. Contracts, authority matrix, trace schema, state versioning (+ unit tests).
2. Arbitrator + coordinator (+ tests incl. conflicts/stale/duplicate/timeouts).
3. Strategy Agent, Coaching Agent, grounding validator (+ tests).
4. Orchestrator integration behind `multiagent_enabled` (default off) in verbal path (and code path or documented exclusion); regression run.
5. Remediations: breaker semantics, guardrail unification flag, CrossEncoder activation, placeholder leak.
6. Pre-register protocols; run XA–XE; analysis scripts; tables/figures from outputs.
7. Rewrite manuscript; claim/citation/blind/PDF audits; reproducibility package; final audit report.
Each stage ends with: targeted tests, full-suite comparison against the baseline above, a local commit (no push).
