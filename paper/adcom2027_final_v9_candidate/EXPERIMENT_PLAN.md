# Experimental Methodology, Research Questions, and Protocol Specification
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `EXPERIMENT_PLAN.md`  
**Candidate Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Status:** Pre-registered Protocol Specification & Methodological Framework

---

## 1. Research Questions and Theoretical Scope

The empirical investigation in this manuscript evaluates whether introducing stateful, bounded-authority agents into a centralized, hub-orchestrated technical interview practice system alters behavioral dynamics while maintaining strict fault containment. The research is organized around four primary research questions:

### RQ1: Coordination Fidelity and Intervention Dynamics
*How does bounded-authority stateful multi-agent arbitration alter dynamic trajectory difficulty, reversal frequency, and proactive probing compared to the frozen single-policy baseline (B0)?*
- **Operationalization:** Evaluate trajectory divergence, mean level changes per session, reversal counts (flips in direction), PPO action agreement fraction, and additional follow-up turns across deterministic replay sessions.
- **Evidence Class:** REPLAY (deterministic replay of 64 recorded human-interview evaluator payloads across 20 question-order seeds = 160 sessions per ablation condition).

### RQ2: Safeguard Containment and Fault Blast Radius
*How effectively do architectural safeguards (Pydantic schema validation, immutable turn observation, forbidden-key authority scanning, evidence-grounded coaching checks, and per-agent circuit breakers) contain diverse synthetic agent faults without corrupting state or halting sessions?*
- **Operationalization:** Measure session completion rates, authority preservation, transition validity, guardrail bypass rates, ungrounded emphasis leakage, and circuit breaker trip rates across 11 fault classes.
- **Evidence Class:** FAULT-INJECTED (synthetic fault injection into agent workers across 1,760 sessions).

### RQ3: Architectural Necessity and Agent Partitioning
*Does partitioning Strategy and Coaching into distinct bounded-authority agents with unidirectional peer messaging yield measurable benefits in fault containment, decision stability, or execution overhead compared to a single unified Technical-Coach Agent?*
- **Operationalization:** Compare blast radius under single-agent failure, state version isolation, turn dispatch latency, and trajectory equivalence under fault-free conditions.
- **Status:** Pre-registered protocol (UNEXECUTED in current candidate to respect repository freeze boundaries; detailed protocol below).

### RQ4: Historical Drift and Specification Alignment
*Can historical empirical claims (E1 fail-closed behavior, E5 5xx circuit-breaker mitigation, grounding probe validity, and inline vs canonical guardrail divergence) be reproduced byte-for-byte or reconciled against ground-truth code?*
- **Operationalization:** Byte-level historical reproduction, synthetic prompt suite evaluation, and socket-level fault simulation.
- **Evidence Class:** SYNTHETIC / SOCKET / HISTORICAL REPRODUCTION.

---

## 2. Formal Hypotheses and Outcome Predictions

### 2.1 Coordination & Intervention Dynamics (Experiment XA)
- **$H_{\text{XA-1}}$ (Intervention Completeness):** The full multi-agent configuration ($M_1$) alters the difficulty trajectory relative to the frozen baseline ($B_0$) in 100% of replay sessions (160/160).
- **$H_{\text{XA-2}}$ (Smoothing Effect):** Stateful weakness tracking reduces high-frequency difficulty oscillations, yielding fewer level changes ($15.12 \to 12.45$) and fewer reversals ($11.74 \to 9.87$) per session.
- **$H_{\text{XA-3}}$ (Proactive Probing):** Rule-driven follow-up probing introduces a slight increase in session length ($+0.59$ turns per session on average).
- **$H_{\text{XA-4}}$ (Transparency When Silent):** When agent contributions are suppressed ($M_2$), trajectory outputs are bit-for-bit identical to baseline ($B_0$) in 160/160 sessions.
- **$H_{\text{XA-5}}$ (Orthogonal Decoupling):** Ablating Coaching, communication, grounding, or authority checks does not alter difficulty trajectories in fault-free replay ($M_3, M_5, M_6 = M_1$).
- **$H_{\text{XA-6}}$ (PPO Independence Contradiction — A9):** Contradicting initial expectations, disabling PPO policy evaluation changes the trajectory in only 4/160 sessions (2.5%), demonstrating that Strategy Agent heuristic rules dominate replay decisions.
- **$H_{\text{XA-7}}$ (Guardrail Divergence Contradiction — A10):** Contradicting initial expectations, replacing legacy inline guardrails with canonical `rl/guardrails.py` alters 0/160 replay paths, because replay lacks real-time acoustic features (audio confidence, hesitation) necessary to trigger the divergent guardrail boundary.

### 2.2 Safeguard Containment & Fault Blast Radius (Experiment XB)
- **$H_{\text{XB-1}}$ (Fail-Closed Robustness):** Across all 11 fault classes and 1,760 sessions, session completion, authority preservation (0 forbidden writes), and state transition validity remain at 100.0%.
- **$H_{\text{XB-2}}$ (Schema vs Authority Defense):** Forbidden-key injection is blocked by schema validation (`extra=forbid`) even without runtime authority scanning; authority scanning alters classification diagnostics, not containment.
- **$H_{\text{XB-3}}$ (Guardrail Bypass Containment):** Disabling arbitration allows Strategy Agent bypass of guardrails in 38/40 sessions (95.0%); full arbitration contains bypass to 0/40 sessions (0.0%).
- **$H_{\text{XB-4}}$ (Grounding Enforcement):** Removing the coaching grounding check permits ungrounded pedagogical emphasis in 40/40 sessions (100.0%); grounding validation contains leakage to 0/40 sessions (0.0%).
- **$H_{\text{XB-5}}$ (Adversarial Proposal Vulnerability):** Syntactically valid, high-confidence, evidenced adversarial proposals bypass validation, serving as the final difficulty source for 10.8 decisions per session (fundamental limitation).
- **$H_{\text{XB-6}}$ (Circuit Breaker Tripping — B6 Contradiction):** At fault rate 0.3, the per-agent circuit breaker trips in 72.5% of sessions (29/40), falling short of the pre-registered $\ge 80\%$ prediction due to fixed pseudo-random schedule seeding.

### 2.3 Threshold Sensitivity (Experiment XC)
- **$H_{\text{XC-1}}$ (Threshold Criticality):** Setting confidence threshold $\tau = 0.0$ collapses arbitration behavior to match the unarbitrated condition ($M_4$), producing 2.225 level changes and 0.014 PPO agreement.
- **$H_{\text{XC-2}}$ (Threshold Invariance Band):** Trajectory metrics are invariant across $\tau \in [0.5, 0.8]$ due to discrete confidence steps in Strategy rules.
- **$H_{\text{XC-3}}$ (Agent Silencing):** Setting $\tau = 0.9$ completely silences Strategy proposals, reverting system behavior to the frozen PPO baseline.

### 2.4 Merged vs Split Architecture (RQ3 Protocol)
- **$H_{\text{merge-1}}$ (Fault-Free Equivalence):** Under identical rule logic, a unified Technical-Coach Agent produces difficulty decisions and coaching plans identical to the two-agent architecture ($\mathbb{P}(\text{agree}) = 1.0$).
- **$H_{\text{merge-2}}$ (Blast Radius Asymmetry):** In the split architecture, an unhandled coaching exception leaves strategy proposals intact (containment = 1.0). In the unified architecture, coaching exceptions terminate the entire turn dispatch, dropping strategy proposals (containment = 0.0).
- **$H_{\text{merge-3}}$ (Serialization Overhead):** Unified dispatch reduces serialization and validation latency by $0.3\text{--}0.6\,\text{ms}$ per turn.

---

## 3. Experimental Design and Execution Matrix

| Exp | Description | Factors & Conditions | Sample Size | Primary Metrics | Status |
|:---|:---|:---|:---|:---|:---|
| **XA** | Deterministic Replay Ablation | 12 conditions ($B_0, M_1\dots M_7, B_7, B_{0c}$, etc.) $\times$ 8 answer sets $\times$ 20 order seeds | 1,920 sessions | Level changes, reversals, PPO agreement, extra turns | **Complete** |
| **XB** | Synthetic Fault Injection | 11 fault classes $\times$ 4 defense variants $\times$ 40 sessions | 1,760 sessions | Completion, authority, transition, bypass, breaker trips | **Complete** |
| **XC** | Confidence Threshold Sensitivity | 6 threshold values ($\tau \in \{0.0, 0.5, 0.6, 0.7, 0.8, 0.9\}$) $\times$ 160 sessions | 960 sessions | Level changes, reversals, PPO agreement, bypass | **Complete** |
| **XD** | Grounding Probe Rebuilding | 64 evaluator payloads across 3 prompt configurations | 192 evaluations | Grounding pass/fail rate, syntactic false rejections | **Complete** |
| **XE** | Historical Reproduction & Sockets | E1 reproduction (752 sessions); B503 socket (1 session); E5 breakers (7 runs) | 760 sessions | Byte-identical hash matching, retry reduction, trip latency | **Complete** |
| **XM** | Merged-Agent Feasibility Comparison | Split ($M_1$) vs Merged ($M_{\text{merged}}$) $\times$ Replay (160) + Faults (440) | 600 sessions | Blast radius, fault spillover, agreement rate, turn latency | **Pre-registered (UNEXECUTED)** |

---

## 4. Statistical Estimation Methodology

To prevent false confidence arising from dependent data reuse:
1. **Paired Bootstrap:** Standard non-parametric percentile bootstrap with $B = 10,000$ resamples for session-level point estimates.
2. **Cluster Bootstrap (Field & Welsh 2007):** Resampling entire clusters $k \in \{0\dots 7\}$ with replacement ($B = 10,000$) to account for question-order permutations sharing the identical 8 underlying candidate response sets.
3. **Leave-One-Cluster-Out (LOCO):** Jackknife sensitivity analysis systematically omitting each cluster $k \in \{0\dots 7\}$ to detect single-cluster dominance.
4. **Exact Binomial Intervals:** Clopper-Pearson 95% confidence intervals for rare events and proportions (completion, bypass, trip rates).
5. **Multiplicity Stance:** All confidence intervals are reported descriptively without post-hoc Bonferroni adjustment; hypotheses are exploratory and confirmatory rather than population-generalizing.

---

## 5. Execution Safeguards and Boundaries

1. **Deterministic Pseudo-Random Seeds:** All replay permutations use fixed seeds (`seed=42..61`), and fault injection schedules are derived deterministically (`seed=31k+seed`).
2. **Mock Evaluator Mode:** All replay experiments run with `EVALUATOR_MOCK_MODE=1` using committed payload records, ensuring zero network egress and zero stochastic LLM variance.
3. **Zero Repository Mutation:** No unapproved agent architectures or code modifications are committed to the repository; candidate evaluations remain strictly sandboxed.
