# Merged-Agent Feasibility Study & Experimental Protocol
**Project:** PREPAIred — ADCoM 2027  
**Artifact Path:** `paper/adcom2027_final_v12_candidate/MERGED_AGENT_EXPERIMENT.md`  
**Date:** 3 October 2026  
**Status:** Pre-registered Experimental Protocol & Feasibility Audit (**UNEXECUTED**)

---

## 1. Executive Summary & Objective

In the PREPAIred architecture, decision-making and pedagogical guidance are partitioned across two distinct stateful agent roles:
1. **Strategy Agent:** Manages a private weakness ledger (tracking per-concept misses and probe history), proposing difficulty step actions ($\text{Easier}, \text{Same}, \text{Harder}$) and proactive follow-up probes.
2. **Coaching Agent:** Manages coaching history (tracking hints and examples given), proposing feedback depth, instructional emphasis, and remediation tags.
3. **Peer Messaging:** Strategy sends a unidirectional peer message (`TurnObservation.peer`) into Coaching to align feedback tone and depth with strategic intent (e.g. encouraging depth on `recover`, concise on `stretch`).

### Research Question (RQ_merge)
*Does partitioning Strategy and Coaching into distinct bounded-authority agents with unidirectional peer messaging yield measurable benefits in fault containment, decision stability, or execution overhead compared to a single unified Technical-Coach Agent?*

---

## 2. Theoretical Grounding & Pre-specified Hypotheses

### Hypothesis 1 ($H_1$: Decision Equivalence in Fault-Free Replay)
Under identical heuristic decision rules and deterministic peer-message translation, a unified agent executing in the absence of faults will produce identical difficulty actions, follow-up probe requests, and coaching plans to the two-agent architecture across all turns:
$$\mathbb{P}(\text{Decision}_{\text{merged}} = \text{Decision}_{\text{split}} \mid \text{fault-free}) = 1.0$$
*Implication:* Agent separation does not provide superior decision-making power under deterministic rules; any justification for separation must derive from software engineering properties (containment, modularity, blast-radius restriction).

### Hypothesis 2 ($H_2$: Fault Containment & Blast-Radius Restriction)
In the two-agent architecture, an unhandled exception, syntax corruption, or timeout occurring within the Coaching Agent leaves the Strategy proposal intact and vice versa:
$$\text{Containment}_{\text{coaching\_fault}}(\text{Strategy}) = 1.0 \quad \text{and} \quad \text{Containment}_{\text{strategy\_fault}}(\text{Coaching}) = 1.0$$
In the merged architecture, a single unhandled exception or malformed payload within either sub-task causes the entire turn dispatch to fail closed, dropping both strategy and coaching proposals:
$$\text{BlastRadius}(\text{merged}) > \text{BlastRadius}(\text{split})$$

### Hypothesis 3 ($H_3$: Latency & Dispatch Overhead)
The two-agent architecture requires two serialization passes, two Pydantic schema validations, and two dispatch invocations per turn. The unified agent requires a single dispatch and validation:
$$\Delta t = t_{\text{split}} - t_{\text{merged}} \approx 0.3 \text{ to } 0.6\,\text{ms per turn}$$

---

## 3. Architectural Specification

### 3.1 Control Architecture ($M_{\text{split}}$ — Baseline M1)
- **Class:** `StrategyAgent` (`agents/multiagent/strategy_agent.py`) and `CoachingAgent` (`agents/multiagent/coaching_agent.py`).
- **Turn Flow:**
  1. Hub constructs immutable `TurnObservation`.
  2. Hub dispatches `StrategyAgent.propose(obs, peer=None)`.
  3. Coordinator validates `StrategyProposal` against schema and forbidden keys.
  4. Hub dispatches `CoachingAgent.propose(obs, peer=strat_proposal)`.
  5. Coordinator validates `CoachingPlan` against schema and evidence grounding.
  6. Hub executes arbitration: Strategy proposal competes with frozen PPO action; Coaching plan is applied by deterministic renderer.

### 3.2 Unified Architecture ($M_{\text{merged}}$)
- **Class:** `UnifiedCoachAgent` (`agents/multiagent/unified_agent.py`).
- **Turn Flow:**
  1. Hub constructs immutable `TurnObservation`.
  2. Hub dispatches `UnifiedCoachAgent.propose(obs)`.
  3. Internal execution resolves weakness ledger rules, determines strategy action, passes resulting intent to coaching logic, and synthesizes `UnifiedProposal`.
  4. Coordinator validates `UnifiedProposal` via a combined schema validator.
  5. Arbitration resolves difficulty; deterministic renderer formats feedback.

---

## 4. Controlled Experimental Protocol

To ensure valid comparative inference without introducing confounding variables:

1. **Dataset:** Identical 64 constructed answer payloads across 8 question categories.
2. **Replay Seeds:** 20 question-order permutations $\times$ 8 answer sets = 160 sessions per condition (matching Experiment XA).
3. **Fault Matrix:** 40 sessions per cell across the 11 fault classes (matching Experiment XB):
   - `coach:crash`, `coach:malformed`, `coach:stale`, `coach:ungrounded`
   - `strat:adversarial_valid`, `strat:crash`, `strat:forbidden_key`, `strat:malformed`, `strat:nan_confidence`, `strat:stale`, `strat:timeout`
4. **Primary Metrics:**
   - Trajectory agreement rate ($p_{\text{agree}}$ between $M_{\text{split}}$ and $M_{\text{merged}}$).
   - Mean level changes and reversal count per session.
   - PPO action agreement fraction.
   - Cross-functional fault spillover rate: proportion of turns where a coaching formatting defect corrupts difficulty progression.
   - Per-turn latency overhead (p50 and p95).
5. **Statistical Test Plan:**
   - Paired percentile bootstrap (10,000 resamples) for continuous metrics.
   - Cluster bootstrap across the 8 question clusters (Field & Welsh 2007) to account for dependent answer reuse.
   - Clopper-Pearson exact 95% confidence intervals for fault containment proportions.

---

## 5. Feasibility Assessment & Current Status

| Parameter | Estimate / Audit Value |
|:---|:---|
| **Code Implementation Effort** | ~120 lines of Python (`UnifiedCoachAgent` + schema) |
| **Execution Time (Replay XA)** | ~25 seconds for 160 sessions |
| **Execution Time (Fault XB)** | ~45 seconds for 440 sessions |
| **Statistical Analysis Time** | ~15–20 minutes (bootstrap resampling & cluster intervals) |
| **Total Estimated Work** | **30–35 minutes** |
| **Execution Status** | **UNEXECUTED (Pre-registered protocol only)** |

### Why This Experiment Was Not Executed in v8:
1. **Zero-Mutation Constraint:** Strict repository safety directives prohibit committing new agent code or modifying production architecture without explicit user authorization.
2. **Scientific Completeness:** The existing verified v7/v8 manuscript addresses its four primary research questions (RQ1–RQ4) with 69 verified quantitative claims. Introducing an unapproved experimental variant hours before the teacher review deadline poses unnecessary regression risk.
3. **Clear Next Step:** If the author and teacher approve running this comparison on 5 October, the protocol above is self-contained and reproducible.
