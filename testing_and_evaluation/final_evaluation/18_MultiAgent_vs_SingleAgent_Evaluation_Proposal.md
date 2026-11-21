# 18. Multi-Agent vs. Single-Agent Architectural Evaluation — Task Specification / Proposal

**Status: PROPOSED — NOT YET EXECUTED.** This document records the task specification for a comparative
experiment as given, pending the explicit approval the specification itself requires before any new baseline is
implemented or any code is changed ("First inspect the architecture and propose the experimental design. Obtain
approval before implementing a new baseline or making any code changes."). No experiment described below has
been run, no single-agent baseline has been built, and no production code has been touched. This document is the
proposal only, reproduced and organized for review.

**Related prior work:** Phase 1's architecture-inspection requirement is already substantially satisfied by
`testing_and_evaluation/final_evaluation/17_Architecture_Audit_Report.md` (this engagement's prior deliverable),
which inspected every agent/component, documented the orchestrator and communication workflow, distinguished
genuine decision components from deterministic pipelines, and produced an implementation-grounded architecture
diagram (Mermaid). That report should be treated as the Phase 1 input to this proposal rather than redone from
scratch; its central finding — a hub-and-spoke orchestrator with no genuine inter-agent communication — directly
shapes what Phase 7's "coordination-disabled" ablation would even mean in this codebase (see §7 below).

---

## Objective

Conduct a rigorous comparative experiment to evaluate whether PrepAIred's existing multi-agent architecture
provides measurable advantages over a unified single-agent architecture.

The objective is to establish the architectural value of specialised agents, orchestration and inter-agent
coordination using controlled experiments and reproducible evidence.

This is an evaluation-only task initially. Do not modify the existing production application.

---

## Phase 1: Architecture Inspection

1. Inspect the complete existing PrepAIred architecture.
2. Identify every agent, its responsibilities, inputs, outputs and interactions.
3. Document the orchestrator and the complete agent communication workflow.
4. Identify shared models, deterministic components, external tools and state-management mechanisms.
5. Distinguish genuine autonomous or specialised agents from ordinary functions, services and deterministic
   pipelines.
6. Produce an architecture diagram based on the actual implementation.

Do not invent agents or attribute capabilities to agents that they do not possess.

*(See the "Related prior work" note above — this phase has a direct prior-session input ready for review.)*

---

## Phase 2: Establish the Experimental Baseline

Design two configurations:

**A. Existing multi-agent architecture:**
- Preserve the existing specialist agents.
- Preserve the existing orchestrator.
- Preserve existing model and tool integrations.
- Preserve existing evaluation and state-management behaviour.

**B. Single-agent comparison baseline:**
- Use one unified agent/controller to perform the equivalent interview workflow.
- Give it equivalent access to the underlying models, tools, candidate information and deterministic evaluation
  components wherever possible.
- Preserve the same task definitions and evaluation criteria.
- Do not intentionally weaken the baseline.
- Document any unavoidable architectural differences.

The experimental variable must be the architecture and coordination strategy, not differences in model quality,
information availability or tool access.

---

## Phase 3: Benchmark Design

Create a reproducible benchmark containing representative interview scenarios:

1. Verbal technical answer evaluation.
2. Incorrect and partially correct answers.
3. Adaptive question selection.
4. Candidate difficulty progression.
5. Speech and confidence integration.
6. C coding evaluation.
7. Compilation and runtime errors.
8. Coding and verbal evidence integration.
9. Candidate-state preservation.
10. Complete interview lifecycle.

Use the existing datasets and historical test scenarios wherever appropriate.

Do not modify frozen datasets or historical results.

Document dataset provenance, scenario distribution and reference-answer construction.

---

## Phase 4: Evaluation Metrics

Measure:

- Expert-reference evaluation agreement.
- Evaluation consistency.
- Question relevance.
- Difficulty alignment.
- Feedback correctness and usefulness.
- Multimodal evidence integration.
- Coding workflow correctness.
- Candidate-state consistency.
- End-to-end task completion.
- Agent coordination errors.
- End-to-end latency.
- Token consumption and computational cost.

Define the primary endpoint and secondary endpoints before running the experiment.

Use blinded human evaluation for subjective feedback and question quality wherever feasible.

---

## Phase 5: Experimental Execution

1. Run both configurations against identical benchmark scenarios.
2. Use paired comparisons.
3. Control model versions, prompts, tools, input information and execution conditions.
4. Repeat stochastic runs using documented seeds.
5. Record raw outputs, metrics, logs, execution time and failures.
6. Preserve all raw experimental evidence.
7. Ensure the benchmark can be reproduced.

Do not selectively exclude unfavourable scenarios or runs.

---

## Phase 6: Statistical Analysis

Use appropriate paired statistical tests.

Report:
- Sample size.
- Mean and standard deviation.
- Median and interquartile range where appropriate.
- Confidence intervals.
- Statistical significance.
- Effect sizes.
- Multiple-comparison correction.
- Practical significance.

Do not claim superiority solely because a p-value is below 0.05.

---

## Phase 7: Additional Architectural Ablation

If technically feasible, evaluate a third configuration:

**C. Multi-agent architecture with inter-agent coordination disabled or appropriately controlled.**

This helps determine whether the improvements arise from specialised agents, coordination, or both.

Do not compromise the integrity of the existing production system to create this configuration.

*(Note for the approver: per the Phase 1 prior work referenced above, the current implementation already has no
genuine inter-agent coordination to disable — all helper components are called only by the orchestrator, with
one documented exception. A coordination-disabled ablation in this specific codebase would most likely reduce to
comparing "orchestrator + specialised deterministic/learned components" against "orchestrator + specialised
components with the PPO/guardrail/Qwen decision points replaced by fixed defaults," which is a different
question from removing agent-to-agent messaging. This distinction should be resolved explicitly during design
approval, not assumed.)*

---

## Phase 8: Deliverables

Produce:

1. Architecture comparison diagram.
2. Experimental methodology.
3. Benchmark specification.
4. Reproducible evaluation scripts.
5. Raw experimental results.
6. Statistical analysis.
7. Comparison tables and visualisations.
8. Ablation analysis, if feasible.
9. Limitations and validity considerations.
10. A research-ready findings section.

Clearly distinguish actual results from proposed experiments and unexecuted work.

---

## Preservation Constraints

- Do not refactor the production application.
- Do not change the existing multi-agent architecture.
- Do not retrain or replace PPO.
- Do not alter frozen datasets or checkpoints.
- Do not delete historical experiment results.
- Do not fabricate results or statistical significance.
- Do not manipulate the baseline to guarantee multi-agent superiority.
- Do not submit or publish anything externally without approval.

**First inspect the architecture and propose the experimental design. Obtain approval before implementing a new
baseline or making any code changes.**

---

## Desired Research Outcome

Establish, using reproducible evidence, whether PrepAIred's multi-agent architecture improves interview
evaluation quality, adaptive questioning, multimodal coordination and end-to-end workflow performance compared
with a fair single-agent baseline.

The final discussion should emphasise demonstrated architectural contributions and practical benefits while
accurately reporting all measured trade-offs.

---

## Document Status Summary

| Item | Status |
|---|---|
| Phase 1 (architecture inspection) | Available from prior session work (`17_Architecture_Audit_Report.md`); not redone here |
| Phase 2–8 (baseline, benchmark, metrics, execution, statistics, ablation, deliverables) | **Not started** — awaiting explicit approval of the experimental design before any baseline is implemented or code is changed |
| Production code / frozen artifacts | **Untouched** |

This document is the specification only. No benchmark has been built, no single-agent baseline exists, no
experiment has been run, and no result of any kind — statistical or otherwise — is reported here.
