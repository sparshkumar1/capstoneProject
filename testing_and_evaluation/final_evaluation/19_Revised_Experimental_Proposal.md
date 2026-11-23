# 19. Revised Experimental Proposal — Specialised, Orchestrator-Coordinated Architecture vs. a Unified Single-Controller Baseline

**Status: PROPOSED — NOT YET EXECUTED. Supersedes-in-review, does not replace,**
`testing_and_evaluation/final_evaluation/18_MultiAgent_vs_SingleAgent_Evaluation_Proposal.md`, **which remains
unchanged on disk.** This is a separate, corrected document produced for review, per the explicit instruction to
preserve the original. See `22_Change_Log_and_Verification_Report.md` for an itemized diff between this document
and document 18.

**Preservation statement:** no production code, test code, dataset, checkpoint, PPO artifact, guardrail module,
or historical result file was modified to produce this document. Nothing in Phases 2–8 below has been
implemented or executed. This remains a specification awaiting explicit human approval before any baseline is
built or any experiment is run.

---

## 1. Objective (revised)

Evaluate whether PrepAIred's existing **specialised, orchestrator-coordinated architecture** — a hub-and-spoke
system in which one central controller invokes a trained RL policy, deterministic guardrails, a deterministic
semantic evaluator, a template-and-optionally-LLM-backed feedback generator, a Docker execution sandbox, and a
separate LLM microservice — provides measurable advantages over a unified single-controller architecture for
adaptive technical interview preparation.

This revises the prior objective, which assumed (without establishing) that the baseline comparison was
specifically "multi-agent vs. single-agent." Document 17's architecture audit found no verified peer-to-peer
agent communication in the current implementation (§2 below); the comparison is therefore correctly framed as
**specialisation-plus-orchestration vs. unification**, not multi-agent vs. single-agent in the strict autonomous
sense.

The research investigates:

1. Whether specialised components provide measurable benefits.
2. Whether central orchestration effectively integrates these components.
3. Whether the existing architecture improves evaluation quality.
4. Whether it improves adaptive questioning and difficulty progression.
5. Whether it integrates verbal, speech and coding evidence effectively.
6. Whether it improves end-to-end interview workflow reliability.
7. Whether any improvements justify additional computational and architectural complexity.

**Explicit non-assumptions:** this study does not assume the current architecture is a fully collaborative
multi-agent system, does not assume it will outperform a unified baseline, and will not be used as a basis to
redesign the production application to appear more multi-agent than the evidence supports.

---

## 2. Phase 1 — Architecture verification (prior work, status: completed, subject to spot-check)

`testing_and_evaluation/final_evaluation/17_Architecture_Audit_Report.md` is treated as completed Phase 1 work,
not redone here. Its central, directly load-bearing finding for this proposal:

> **"Orchestrated modular pipeline with agent-like components."** A grep sweep of every file under `agents/`
> for cross-imports between sibling agent modules returned zero matches (query:
> `^from agents\.|^import agents\.|^from services\.|^import services\.`); a second grep for relative imports
> returned only package-internal re-exports. No agent calls another agent directly. The sole exception is
> `FeedbackAgent._query_qwen_feedback` (`agents/orchestrator/feedback_agent.py:525`), which calls the Qwen
> microservice directly rather than through the orchestrator — a stateless HTTP call, not peer agent negotiation.

This proposal treats that finding as **verified by direct code inspection in this engagement**, not merely
asserted. Two additional points raised during review of the task specification were independently re-verified
against the current source during this revision:

- **"Do not claim Qwen calculates numerical scores."** Re-verified directly: every occurrence of `final_score`
  in `services/qwen/app.py` (lines 418, 462, 525, 624, 718, 828) reads it from `ev.get("final_score", ...)`,
  where `ev` is the `structured_evaluation` dict supplied in the request payload — i.e. the evaluator's
  pre-computed score, passed through verbatim. Qwen's `FeedbackResponse` schema (line 375) does carry a
  `final_score: float` field, but **no code path in this file computes that value independently of the
  evaluator's input.** `agents/orchestrator/feedback_agent.py`'s `generate()` (lines 170-198) corroborates this
  from the caller's side: even when a Qwen response is available, the returned `final_score` is
  `round(score, 4)` where `score = float(eval_result.get("final_score", 0.5))` (line 98) — the evaluator's
  score, not anything taken from `qwen_res`. **Qwen does not calculate scores in this system; it is never the
  source of a numeric evaluation.**
- **"Do not combine verbal evaluation and Docker C execution into one evaluation path."** Re-verified: the audit
  already established (and this revision rechecked) that `agents/coding_executor/coding_executor.py`'s
  `evaluate_c_submission`/`DockerCSandbox` never import anything from `services/evaluator/`, and vice versa —
  two genuinely separate code paths, invoked from different orchestrator methods
  (`handle_voice_answer` vs. `handle_code_submission`).

No new architectural finding beyond what document 17 already established was required for this revision.
Phase 1 is therefore **complete and current-source-verified for the two specific caveats the task review
raised**; it is not being repeated in full.

---

## 3. Phase 1 continued — architectural decision: preserve the existing architecture

**Decision: keep the existing production architecture exactly as it is.** This proposal does not, and will not,
in any phase:

- Convert the production system into a fully collaborative multi-agent architecture.
- Introduce peer-to-peer agent communication into production code.
- Add agents merely to increase an "agent count."
- Replace the central orchestrator (`InterviewOrchestrator`).
- Replace or retrain the PPO policy or its checkpoint.
- Change guardrail behaviour (including the already-identified divergence between `rl/guardrails.py` and the
  orchestrator's private copy, documented in `17_Architecture_Audit_Report.md` §3.3/§7.2/§10 — that divergence
  is a separate, already-flagged engineering issue, outside the scope of this comparative study, and is not to
  be "fixed" as a side effect of this work).
- Rewrite the evaluation pipeline (`services/evaluator/app.py`).
- Change the Docker sandbox or its security configuration.
- Refactor any currently-working module purely for architectural appearance.

A fully collaborative multi-agent redesign is noted as a possible *future* research direction (consistent with
the framing already discussed by the project team — see `22_Change_Log_and_Verification_Report.md` §4 for how
that discussion is reflected here) and is explicitly **not** part of this task.

---

## 4. Phase 2 — Comparative experiment design

### Configuration A: existing specialised, orchestrator-coordinated architecture (reference implementation)

Unchanged, as-is:
- `InterviewOrchestrator` (`agents/orchestrator/interview_orchestrator.py`).
- The PPO policy wrapper (`agents/strategy/hybrid_orchestrator.py`) and its frozen checkpoint
  (`rl/checkpoints/seed_123/`).
- The orchestrator's private guardrail copy (`interview_orchestrator.py:1529-1573`) — used exactly as it
  currently behaves in production, including its documented divergence from `rl/guardrails.py`. This study
  evaluates the system **as deployed**, not a corrected version of it.
- `services/evaluator/app.py` (SBERT + FAISS + CrossEncoder composite).
- `agents/audio/*` speech pipeline.
- `agents/orchestrator/feedback_agent.py` + `services/qwen/app.py`.
- `agents/coding_executor/coding_executor.py` (Docker sandbox).
- `services/storage/database.py` candidate-state persistence.

Full architectural specification and classification: see `20_Architecture_and_Baseline_Comparison_Specification.md`.

### Configuration B: unified single-controller baseline

A single controller/class that performs the equivalent interview workflow, with **equivalent access to the same
underlying models, tools, and deterministic services** — the comparison must isolate *control architecture*, not
*capability availability*. Important clarification carried over from task review: a single controller may still
call the same PPO checkpoint, the same evaluator, the same Docker sandbox, and the same Qwen service as tools —
"single-controller" describes the **coordination structure** (one decision-making locus instead of several
specialised classes with the orchestrator mediating between them), not the deletion of useful functionality.

Full specification of what is consolidated, what remains shared, and what cannot be made equivalent: see
`20_Architecture_and_Baseline_Comparison_Specification.md` §2.

**Not implemented in this phase.** This proposal documents the design only.

---

## 5. Phase 3 — Benchmark design (expanded)

The benchmark must cover, at minimum, the following 17 scenario categories (expanded from the original
proposal's 10, per task review):

1. Correct verbal technical answers.
2. Incorrect verbal answers.
3. Partially correct answers.
4. Conceptual misconceptions (mapped against `FeedbackAgent._MISCONCEPTIONS`, `feedback_agent.py:33-60`).
5. Adaptive question selection.
6. Difficulty progression.
7. Speech confidence integration.
8. Hesitation and prosodic evidence.
9. C compilation and execution.
10. Compilation errors.
11. Runtime errors.
12. Coding and verbal evidence integration.
13. Candidate-state preservation (including the already-known separate state-preservation issue tracked outside
    this study, per `CLAUDE.md`'s "known gotchas" — that pre-existing issue is not to be conflated with a new
    finding from this benchmark).
14. Guardrail intervention (each of the six documented rules: G4, G1, G2, G3/G5, G6, plus the infrastructure-
    failure guard — see `17_Architecture_Audit_Report.md` §3.3).
15. Difficult or conflicting multimodal evidence (e.g. confident delivery with a technically wrong answer).
16. Complete interview lifecycle (start → N turns → retry/skip → end → report).
17. Failure handling and recovery (evaluator-unavailable, Docker-unavailable, Qwen-unavailable fail-closed
    paths — all three independently confirmed to exist in `17_Architecture_Audit_Report.md` §9.2).

**Sourcing requirement:** use existing datasets and historical test scenarios wherever appropriate —
specifically `research/data/evaluator_benchmark/{benchmark_cases.json, final_human_gold.csv}` (3 raters, 64
constructed answers to 8 questions — current human result, rho 0.3812, per
`research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`), `data/questions/qns.json` (125 questions with embedded
`test_cases` for coding items), and `rl/training/simulated_candidate.py` personas for difficulty-progression
scenarios. **Frozen datasets are not to be modified** — new scenarios needed beyond what these sources cover must
be newly constructed and clearly labeled as such, never retroactively merged into a frozen file.

For every scenario, document (schema, not yet populated): scenario ID, category, input information, initial
candidate state, expected behaviour, reference answer/outcome, evaluation rubric, ground-truth source, and
whether historical or newly constructed.

**Independence requirement:** benchmark construction must be finished and frozen before either configuration is
run against it. No scenario may be added, removed, or reweighted after seeing which configuration performs
better on it.

---

## 6. Phase 4 — Evaluation metrics (structured framework)

### A. Evaluation quality
Expert-reference agreement; evaluation correctness; consistency; misconception identification; partial-credit
appropriateness.

### B. Adaptive questioning
Question relevance; difficulty alignment; difficulty progression; adaptation appropriateness.

### C. Feedback quality
Technical correctness; specificity; actionability; usefulness; consistency with evaluation evidence.

### D. Multimodal integration
Correct use of speech evidence; correct integration of verbal and speech information; appropriate handling of
conflicting signals; preservation of source evidence.

### E. Coding workflow
Compilation correctness; runtime correctness; test-case evaluation correctness; error handling; sandbox security
and execution behaviour. **Note for benchmark design:** this axis must specifically include at least one
scenario that exercises the REST `/api/run_code` → WS `code_submission` round trip end-to-end (not just the
`DockerCSandbox` class in isolation), because `17_Architecture_Audit_Report.md` §5(Workflow B)/§10(Finding 2)
identified a static-inspection-only (not yet runtime-confirmed) integration gap in that specific path
(`apps/backend/main.py:1360`'s `_current_question` attribute lookup never succeeds against
`InterviewOrchestrator`). Runtime confirmation or refutation of that finding is itself a legitimate benchmark
outcome, separate from the architecture-comparison question, and must be reported as such if observed, not
silently folded into a general "coding correctness" number.

### F. State management
Candidate-state consistency; correct state transitions; preservation of speech confidence; preservation of prior
interview evidence; cross-turn consistency.

### G. End-to-end performance
Successful interview completion; task completion; integration errors; orchestrator routing errors; state-handoff
failures; recovery from failures. **Agent-coordination errors are explicitly excluded as a principal metric**,
per task review, because genuine agent-to-agent communication is not verified to exist in Configuration A (§2) —
there is nothing to measure coordination failure *between* agents; routing/integration errors within the single
orchestrator are measured instead.

### H. Computational efficiency
End-to-end latency; per-component latency; token consumption; model inference cost; memory/computational
resource usage; failure and retry overhead.

### Primary endpoint

**Recommended primary endpoint: blinded expert-rated overall interview-evaluation quality**, using a
reproducible scoring rubric, provided such a rubric can be defined and piloted before the comparative run
begins. This is a recommendation, not yet adopted — it requires sign-off together with the benchmark design and
a feasibility check on rater availability (see `21_Experimental_Results_Framework.md` §2).

All other metrics above are secondary endpoints. **Endpoints must be fixed before any run is scored**, not
selected afterward based on which configuration looks better on them.

---

## 7. Phase 5 — Experimental execution methodology

1. Both configurations receive identical benchmark scenarios, in the same order, with the same persona/scenario
   pairing.
2. Candidate personas and initial states are equivalent across configurations (same persona object reused, not
   regenerated).
3. Model versions, prompts, and tool access are controlled and recorded for both configurations.
4. Execution environments (hardware, Docker daemon state, model checkpoint hashes) are documented per run.
5. Random seeds are recorded for every stochastic component (PPO inference is deterministic at inference time
   per `hybrid_orchestrator.py:219`'s `deterministic=True`, but persona generation and any LLM sampling
   temperature are not, and must be seeded and logged).
6. Stochastic runs are repeated a pre-specified number of times (count to be fixed during sample-size
   justification, §8, not chosen post hoc).
7. Raw outputs, metrics, logs, execution time, and failures are all retained — no selective exclusion of
   unfavourable scenarios or runs.
8. Human assessments (primary endpoint) are blinded to configuration identity wherever feasible.
9. **Statistical unit:** the candidate/persona, consistent with `CLAUDE.md`'s rule for Paper 3 ("statistical
   unit is the persona... sessions and turns are descriptive only") — turns within one persona's session are not
   treated as independent samples.
10. The experiment runs isolated from the production system — no comparative run writes to `data/prepaired.db`
    or any production session store.

**Sample-size justification is required, not assumed.** A specific N must be derived from the primary
endpoint's expected variability and a pre-specified minimum detectable effect, via a power or precision analysis,
once the primary-endpoint rubric is piloted. No sample size is proposed in this document because none has yet
been justified — proposing a number now would itself violate the "do not arbitrarily select a sample size"
instruction.

---

## 8. Phase 6 — Statistical methodology (pre-specified, not yet applied to any data)

To be reported once data exists: sample size; number of personas; number of scenarios; number of repeated runs;
mean and standard deviation; median and IQR; absolute and (where meaningful) relative differences; confidence
intervals; effect sizes; statistical significance; practical significance; multiple-comparison correction.

**Methods under consideration** (final choice depends on the actual metric distributions once piloted, not fixed
a priori): paired t-tests where assumptions hold; Wilcoxon signed-rank tests otherwise; bootstrap confidence
intervals; a mixed-effects or clustered model if repeated turns per persona require it.

**Explicit constraints carried forward from task review:**
- Statistical significance (p < 0.05) alone is never sufficient to claim superiority — effect size and practical
  significance must also be reported and discussed.
- Equivalence/non-inferiority is not claimed unless a margin and methodology for it are prespecified before data
  collection — this document does not currently prespecify one, so no equivalence claim is available until it
  does.

---

## 9. Phase 7 — Decision-component ablation (corrected)

**Correction from the original proposal (document 18):** document 18 proposed "Configuration C: multi-agent
architecture with inter-agent coordination disabled." Per task review and the Phase 1 verification in §2 above,
**there is no verified inter-agent coordination in the current implementation to disable** — all specialised
components are invoked only by the orchestrator, never by each other (with the one narrow, already-documented
Qwen exception). Describing a third configuration as "coordination-disabled" would therefore not test what it
claims to test.

**Replacement: an optional decision-component ablation**, isolating which *decision mechanism* drives difficulty
adaptation, independent of the orchestrator's overall control structure:

- **C1 — PPO + guardrails** (current production behaviour, `hybrid_orchestrator.py` + orchestrator's private
  guardrail copy).
- **C2 — Guardrails only**, with the PPO proposal replaced by a fixed "Same" action before guardrails are
  applied (isolates the guardrail layer's own contribution).
- **C3 — Heuristic-only** (`hybrid_orchestrator.py:_heuristic_action`, lines 251-257 — already implemented,
  requires zero new code, as it is the existing fallback path).
- **C4 — Fixed difficulty** (no adaptation at all).

**Reuse of existing infrastructure:** `research/scripts/run_paper3_study.py` and
`research/scripts/execute_paper3_study.py` already implement exactly this Fixed/Heuristic/PPO/PPO+guardrails
comparison, and their frozen results exist (`research/results/paper3/*`,
`research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2). **These existing results answer the C1–C4
decision-component question already, for the difficulty-tracking metric specifically, under their own
methodology** (simulated candidates, persona as statistical unit, five-seed PPO runs). They do **not** answer the
new architecture-comparison question (Configuration A vs. B, §4) — that is a different experimental axis
(control structure, not decision mechanism) using different benchmark scenarios (interview-evaluation-quality
scenarios, not simulated-candidate RL training episodes). See `21_Experimental_Results_Framework.md` §3 for the
explicit separation of these two evidence bases; they must never be silently combined into one table.

**No change to production PPO, checkpoints, or guardrails** is required or permitted to run this ablation —
C2/C3/C4 are alternative code paths already present or trivially isolable in `hybrid_orchestrator.py`, run in an
isolated evaluation harness, not a modification of the deployed policy.

---

## 10. Phase 8 — Results, visualisation and discussion framework

Full metric definitions, historical-vs-new result separation, comparison-table template, and the
Results/Discussion outline are specified in `21_Experimental_Results_Framework.md`, to avoid duplicating that
content here. Summary of what that document establishes:

- A **mandatory separation** between (a) existing historical Paper 3 results (Fixed/Heuristic/PPO/PPO+guardrails
  tracking-MAE table, §D.2 of `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`) and (b) new Configuration-A-vs-B results —
  the former is not evidence for or against the new research question and must never be presented as if it were.
- A comparison-table template with every cell marked **Pending** — no fabricated, estimated, or illustrative
  values.
- Four possible evidence-supported conclusions (existing architecture better / unified baseline better /
  task-dependent trade-offs / insufficient evidence), none of which is assumed in advance.

---

## 11. Document status summary (revised)

| Item | Status |
|---|---|
| Phase 1 (architecture verification) | **Completed** in `17_Architecture_Audit_Report.md`; two specific caveats (Qwen scoring, verbal/coding separation) independently re-verified during this revision (§2 above) |
| Phase 2 (comparative design) | **Designed, not implemented** — see `20_Architecture_and_Baseline_Comparison_Specification.md`; awaiting approval |
| Phase 3 (benchmark) | **Specified, not constructed** — scenario list expanded to 17 categories; no scenario instances yet written |
| Phase 4 (metrics) | **Defined** (A–H framework + recommended primary endpoint); not yet applied to any data |
| Phase 5 (execution) | **Not executed** |
| Phase 6 (statistics) | **Methodology pre-specified**; no data exists to analyze |
| Phase 7 (decision-component ablation) | **Corrected and redesigned** (coordination-disabled → decision-component); existing Paper 3 infrastructure identified as reusable for a *different* question; not yet run for *this* question |
| Phase 8 (results/discussion) | **Framework only** — see `21_Experimental_Results_Framework.md`; zero results exist |
| Production architecture | **Unchanged** |
| New comparative results | **None exist.** Every number that would appear in a results table is currently "Pending." |

**Approval gate preserved:** implementation of Configuration B, construction of the benchmark instances, and
execution of any run described in this document requires explicit human approval before proceeding.
