# Experimental Methodology, Research Questions, and Protocol Specification
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `EXPERIMENT_PLAN.md`  
**Candidate Directory:** `paper/adcom2027_final_v11_candidate/`  
**Date:** 3 October 2026  
**Status:** Methodological Specification for Coordination & Agent Specialization

---

## 1. Research Scope and Alignment

In accordance with the project directives, this research investigates **multi-agent coordination and agent specialization** within an adaptive, orchestrated technical interview preparation system. Rather than evaluating general-purpose agent reliability or fault management, the empirical investigation evaluates:
1. **Multi-Agent Coordination:** How stateful coordination between the Strategy and Coaching agents alters interview session trajectories, difficulty transitions, directional reversals, and proactive follow-up probing relative to an uncoordinated, frozen single-policy baseline ($B_0$).
2. **Agent Specialization:** Whether decomposing pedagogical responsibilities across specialized agents (Strategy vs Coaching) provides measurable value over a unified controller operating on equivalent state and rules, and which benefits represent demonstrable evidence versus software engineering hypotheses.
3. **Decision-Making:** The mechanisms governing dynamic difficulty selection, follow-up probe selection, coaching actions, and their consistency across turns.

---

## 2. Research Questions and Formal Hypotheses

### RQ1: Coordination and Intervention Dynamics
*How does stateful coordination between the Strategy and Coaching agents affect the decisions and session trajectories of the technical interview preparation system, compared with the frozen single-policy baseline ($B_0$)?*

- **Independent Variable:** Coordination architecture ($B_0$: uncoordinated frozen PPO controller vs $M_1$: full coordinated multi-agent system).
- **Dependent Variables:** Trajectory divergence rate, mean level changes per session, mean directional reversals per session, PPO action agreement fraction, and mean proactive probe turns.
- **Baseline:** $B_0$ (frozen PPO policy, 6-D state vector, no concept memory).
- **Experimental Unit:** An interview session comprising 8 technical questions with dynamic difficulty adaptation.
- **Hypotheses:**
  - **$H_{\text{XA-1}}$ (Intervention Completeness):** Multi-agent coordination alters the difficulty path relative to $B_0$ in 100\% of sessions (160/160).
  - **$H_{\text{XA-2}}$ (Oscillation Smoothing):** Stateful weakness tracking reduces high-frequency difficulty oscillations, yielding fewer level changes ($\Delta \approx -2.67$) and reversals ($\Delta \approx -1.88$).
  - **$H_{\text{XA-3}}$ (Proactive Probing):** Rule-driven weakness detection introduces additional follow-up probe turns ($\Delta \approx +0.59$ turns).
  - **$H_{\text{XA-4}}$ (Transparency When Inactive):** When agent proposals are suppressed ($M_2$), trajectory paths are 100\% identical to $B_0$.

### RQ2: Value of Agent Specialization
*Does separating Strategy and Coaching into distinct specialized agents provide measurable benefits over a unified technical coaching agent operating on equivalent information and tasks?*

- **Independent Variable:** Architectural partitioning ($M_{\text{split}}$: two specialized agents with disjoint ledgers and peer messaging vs $M_{\text{unified}}$: single unified agent managing joint state).
- **Dependent Variables:** Decision agreement fraction, difficulty trajectory divergence, follow-up probe selection, per-turn dispatch/serialization latency, and failure blast radius.
- **Baseline:** $M_{\text{split}}$ ($M_1$ full configuration).
- **Experimental Unit:** Replay session and turn-level dispatch.
- **Hypotheses:**
  - **$H_{\text{spec-1}}$ (Behavioral Equivalence under Deterministic Rules):** Under equivalent observation inputs and identical decision heuristics, a unified agent produces mathematically identical difficulty actions, follow-up probes, and coaching plans ($\mathbb{P}(\text{agree}) = 1.0$).
  - **$H_{\text{spec-2}}$ (Trajectory Invariance under Coaching Ablation):** Ablating the Coaching Agent ($M_3$) produces difficulty trajectories 100\% identical to the full two-agent system ($M_1$), proving that Strategy decisions are decoupled from coaching state.
  - **$H_{\text{spec-3}}$ (Dispatch Overhead):** Partitioning into two agents incurs two serialization passes and two schema validations, increasing median turn latency by $\approx 1.0$\,ms relative to uncoordinated execution.
  - **$H_{\text{spec-4}}$ (Blast Radius Asymmetry):** Specialized agents provide bulkhead fault isolation (coaching failure spares strategy difficulty adaptation), whereas a monolithic controller drops both functions upon unhandled exception.

### RQ3: Coordination Mechanisms
*Which implemented coordination components---stateful decision tracking, agent-to-agent information exchange, threshold-gated arbitration, or PPO interaction---are responsible for observable differences in system decisions?*

- **Independent Variables:** Specific coordination components ablated or varied ($M_4$: unarbitrated, $M_5$: no peer messaging, $M_7$: no PPO policy, XC: threshold $\tau \in [0.0, 0.9]$).
- **Dependent Variables:** Level changes, reversals, PPO agreement fraction, guardrail bypass rate, and coaching presentation attributes.
- **Hypotheses:**
  - **$H_{\text{mech-1}}$ (Threshold Criticality):** Setting confidence threshold $\tau = 0.0$ collapses arbitration behavior, replicating the $M_4$ oscillation collapse without permitting guardrail bypass.
  - **$H_{\text{mech-2}}$ (Threshold Invariance Band):** Trajectory dynamics are invariant across $\tau \in [0.5, 0.8]$ due to discrete heuristic confidence steps.
  - **$H_{\text{mech-3}}$ (Peer Messaging Isolation):** Ablating Strategy-to-Coaching peer messaging ($M_5$) leaves difficulty trajectories unchanged, modifying only coaching tone, depth, and remediation tags.
  - **$H_{\text{mech-4}}$ (PPO Interaction):** Disabling the PPO policy ($M_7$) produces minor trajectory divergence ($< 10\%$) due to high alignment between the Strategy heuristic rules and the baseline rule fallback.

---

## 3. Replay Benchmark and Cluster Structure

### 3.1 Benchmark Dataset
- **Composition:** 64 pre-recorded production-evaluator payloads across 8 technical interview question domains (arrays, dynamic programming, trees/graphs, system design, concurrency, databases, networking, object-oriented design).
- **Content per Payload:** Composite score (0--100), fine-tuned cross-encoder semantic score, rubric keyword matches, extracted concept tags, and response length metrics.
- **Execution Mode:** Deterministic replay with `EVALUATOR_MOCK_MODE=1`. Zero live LLM generation; the LLM service is stubbed as down, and deterministic template engines format follow-ups and candidate feedback.

### 3.2 The 8-Cluster Structure and Statistical Validity
- Replay sessions combine the 8 recorded candidate answer sets with 20 seeded pseudo-random question orders (seeds 42--61), yielding $N = 160$ sessions per condition.
- Because these 160 sessions reuse the same 8 underlying response sets, they are **clustered and dependent**.
- Treating sessions as independent samples underestimates standard errors. We therefore implement:
  1. **Naive Session Bootstrap ($B = 10{,}000$):** Characterizes order-permutation variance.
  2. **Cluster Bootstrap (Field & Welsh 2007, $B = 10{,}000$):** Resamples entire candidate answer clusters $k \in \{0\dots 7\}$ with replacement to provide defensible population-level confidence intervals.
  3. **Leave-One-Cluster-Out (LOCO):** Jackknife sensitivity analysis systematically omitting each cluster $k \in \{0\dots 7\}$ to assess cluster dominance.

---

## 4. Experimental Conditions Matrix

| Condition | Multi-Agent Flag | Strategy Agent | Coaching Agent | Peer Messaging | Arbitration Gate | PPO Policy | Mechanism Evaluated |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **$B_0$** | False | Inactive | Inactive | None | None | Active | Baseline (uncoordinated PPO) |
| **$M_1$** | True | Active | Active | Active | $\tau = 0.6$ | Active | Full coordinated system |
| **$M_2$** | True | Silent | Silent | Inactive | $\tau = 0.6$ | Active | Coordination layer transparency |
| **$M_3$** | True | Active | Inactive | Inactive | $\tau = 0.6$ | Active | Decoupling of Strategy from Coaching |
| **$M_4$** | True | Active | Active | Active | $\tau = 0.0$ (Raw) | Active | Complete removal of arbitration checks |
| **$M_5$** | True | Active | Active | Inactive | $\tau = 0.6$ | Active | Isolation of peer message flow |
| **$M_7$** | True | Active | Active | Active | $\tau = 0.6$ | Inactive | Strategy heuristic vs rule fallback |
| **$B_7$** | False | Inactive | Inactive | None | None | Inactive | Pure rule-based baseline |
| **$B_{0c}$** | False | Inactive | Inactive | None | None | Active | Canonical guardrail implementation |
| **XC** | True | Active | Active | Active | $\tau \in [0.0, 0.9]$ | Active | Isolation of threshold gating |
| **$M_{\text{unified}}$** | True | Unified | Unified | Internal | $\tau = 0.6$ | Active | Monolithic controller comparison |

---

## 5. Execution Boundaries and Integrity Safeguards

1. **Zero Repository Mutation:** No unapproved branches, commits, or PRs are generated.
2. **Fixed Random Seeds:** Deterministic replay uses fixed order seeds (42--61).
3. **Write-Once Artifacts:** All execution artifacts are read-only.
4. **Honest Reporting:** Contradicted predictions and cluster dependencies are reported without suppression.
