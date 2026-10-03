# Audit Deliverable 07: Architecture and Figures Audit
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `AUDIT_07_ARCHITECTURE_AND_FIGURES.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Independent Scientific, Reproducibility, and Publication-Quality Reviewer  

---

## 1. Architectural Component Reconciliation

Every component in the manuscript architecture has been cross-checked against the implementation in `agents/multiagent/` and `core/`:

| Manuscript Component | Source Code Class / Module | Implemented Responsibilities | Verified Inputs / Outputs | Auditor Verification |
|:---|:---|:---|:---|:---:|
| **Interview Orchestrator (Hub)** | `core.orchestrator.InterviewOrchestrator` | Owns session state dict, manages turn lifecycle lock, commits final state. | In: User speech/code; Out: Committed turn state | **MATCHES CODE** |
| **Evaluator** | `evaluation.evaluator` (Mocked in replay) | Computes sentence embedding, concept matching, cross-encoder score. | In: Answer text; Out: Composite score, concept lists | **MATCHES REPLAY** (`EVALUATOR_MOCK_MODE=1`) |
| **Strategy Agent** | `agents.multiagent.strategy_agent.StrategyAgent` | Maintains cross-turn weakness ledger (`miss_turns`, `resolved`, `probes`, `ema`). Proposes difficulty action and proactive probes. | In: `TurnObservation`; Out: `StrategyProposal` | **MATCHES CODE** |
| **Coaching Agent** | `agents.multiagent.coaching_agent.CoachingAgent` | Maintains coaching history (`concept_misses`, `hints_given`, `examples_given`). Proposes depth, hints, examples, tone. | In: `TurnObservation`, `peer` msg; Out: `CoachingPlan` | **MATCHES CODE** |
| **Peer Communication** | `TurnObservation.peer` parameter | Unidirectional message passing from Strategy to Coaching Agent. | In: `StrategyProposal`; Out: Modulates coaching tone/depth | **MATCHES CODE** |
| **Threshold Arbitrator** | `agents.multiagent.arbitration.arbitrate_difficulty` | Evaluates Strategy proposal confidence against threshold $\tau=0.60$. Overrides PPO baseline if $\ge \tau$. | In: Proposal, PPO action, $\tau$; Out: `DifficultyDecision` | **MATCHES CODE** |
| **Probe Arbitrator** | `agents.multiagent.arbitration.arbitrate_probe` | Enforces follow-up probe budget (`FOLLOWUP_HARD_CAP = 2`) and evidence grounding. | In: Proposal, seen concepts, $\tau$; Out: `ProbeDecision` | **MATCHES CODE** |
| **Inline Guardrails** | `core.guardrails.inline_guardrails` | Clamps transitions to $\pm 1$ step within $[1, 5]$. Enforces safety stops. | In: Candidate level; Out: Final committed level | **MATCHES CODE** |
| **Validation Pipeline** | `agents.multiagent.validation` | 4-stage pipeline: Schema validation, 18 forbidden keys, turn version match, evidence grounding. | In: Proposal; Out: Validated proposal or dropped | **MATCHES CODE** |
| **Circuit Breaker** | `agents.multiagent.circuit_breaker.CircuitBreaker` | Per-agent failure isolation (threshold 2 failures, 60s cooldown). | In: Agent invocation; Out: Open/Closed state | **MATCHES CODE** |

---

## 2. Figures Audit (Vector TikZ Rendering)

All three figures are native vector TikZ code embedded within `manuscript/sec_arch.tex`:

1. **Figure 1 (Architecture Diagram — `figures/fig1_architecture.tex`):**
   - **Visual Elements:** Clear color-coded distinction (orange = added multi-agent layer; blue = learned components like PPO and evaluator; grey = deterministic hub infrastructure).
   - **Flow Integrity:** Correctly displays unidirectional dashed lines for proposals; agents have zero arrows pointing to mutable state.
   - **Typography & Scale:** Rescaled via `\resizebox{\textwidth}{!}`; all text legible at 100% zoom.
   - **Caption:** Fully describes color scheme and least-privilege state boundary.

2. **Figure 2 (Turn Flow Sequence — `figures/fig2_turn_flow.tex`):**
   - **Sequence Integrity:** Accurately numbers steps 1 through 9. Reflects that steps 1–4 execute before state commit, and arbitration (step 8) executes after PPO baseline evaluation.
   - **Dual Paths:** Distinguishes the primary spoken answer pipeline from the code-submission pathway.
   - **Typography & Scale:** Scaled to `0.97\textwidth`; zero margin clipping.

3. **Figure 3 (Validation Pipeline — `figures/fig3_validation.tex`):**
   - **Pipeline Stages:** Accurately traces the four sequential filters: (1) Pydantic schema validation, (2) 18 forbidden keys check, (3) Turn state version match, (4) Evaluator evidence grounding.
   - **Rejection Behavior:** Accurately depicts that any rejection drops the proposal to default policy fallback without stalling the session.

---

## 3. Tables Traceability Audit

All 6 tables in the manuscript are directly traceable to raw data or code:

- **Table 1 (`tables/authority.tex`):** Authority Matrix generated directly from `agents/multiagent/authority.py`. (Verified: Table width $11.1$\,cm matches CCIS text area).
- **Table 2 (`tables/xa_summary.tex`):** Replay Summary across 6 conditions. (Verified: Exact match with `research/multiagent/results/xa/xa_summary.csv`).
- **Table 3 (`tables/xa_paired.tex`):** Paired Differences ($M_1 - B_0$) with naive Student-$t$ and Field & Welsh cluster bootstrap CIs. (Verified: Exact match with `xa_paired.csv` and `cluster_bootstrap.json`).
- **Table 4 (`tables/xa_pred.tex`):** Pre-registered predictions A1–A10. (Verified: Exact match with `xa_predictions.csv`).
- **Table 5 (`tables/xc.tex`):** Threshold sweep across $\tau \in [0.0, 0.9]$. (Verified: Exact match with `xc_summary.csv`).
- **Table 6 (`tables/specialization.tex`):** Specialization Comparison ($M_{\text{split}}$ vs $M_{\text{unified}}$). (Verified: Traceable to $M_3$ replay logs, metamorphic tests, and dispatch serialization benchmarks).
