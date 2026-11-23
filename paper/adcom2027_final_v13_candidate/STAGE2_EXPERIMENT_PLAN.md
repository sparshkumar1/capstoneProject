# Stage 2 Experiment Plan & Prioritization Matrix
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `STAGE2_EXPERIMENT_PLAN.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor / Investigator:** Independent Scientific and Research Auditor  

---

## 1. Objective and Scientific Rationale

Stage 1 established the baseline audit: all quantitative claims in the current manuscript are traceable, the test suite passes, and the 20-page camera-ready layout is compliant. However, several critical scientific and causal questions remain unresolved:
1. **The Specialization Question (P0):** Prior candidates relied on proxy ablation ($M_3$) and metamorphic unit tests rather than an executed, standalone unified controller. A real `UnifiedCoachAgent` baseline must be constructed, unit-tested, and evaluated in a paired replay experiment to measure exact decision agreement, trajectory divergence, and execution latency under identical environmental conditions.
2. **The Mechanism of Trajectory Invariance ($M_3 \equiv M_1$) (P0):** We must empirically and architecturally explain *why* difficulty trajectories under $M_3$ are 100% identical to $M_1$, identifying the precise responsibility boundaries and unidirectional communication constraints that enforce this invariance.
3. **Cluster $k=1$ Dominance & Response Characteristic Analysis (P1):** Proactive probing is concentrated 100% in Cluster 1 (+4.75 turns vs +0.00 in Clusters 0, 2–7). We must characterize the specific evaluator score and concept-miss features of Cluster 1 to explain this concentration.
4. **Analysis of Contradicted Predictions A9 & A10 (P1):** Predictions A9 (disabling PPO alters trajectory in $\ge 50\%$) and A10 (canonical guardrails alter trajectory in $\ge 5\%$) failed. We must examine the architectural causes of these empirical failures to extract scientific insights regarding policy alignment and neutral acoustic defaults.

---

## 2. Experiment Prioritization Matrix

| ID | Priority | Experiment | Scientific Question | Why Existing Evidence Insufficient | Independent Variable | Primary Outcome | Statistical Method | Expected Value | Cost |
|:---:|:---:|:---|:---|:---|:---|:---|:---|:---|:---:|
| **E1** | **P0** | **Standalone Unified Agent Implementation & Paired Replay Comparison ($M_{\text{unified}}$ vs $M_{\text{split}}$)** | Does separating Strategy and Coaching into specialized agents produce measurable decision, trajectory, or operational differences over a unified controller with equivalent logic and information? | Currently, the unified agent was pre-registered in `MERGED_AGENT_EXPERIMENT.md` but unexecuted as a standalone class. Evidence relies on proxy ablation $M_3$. | Controller Architecture ($M_{\text{split}}$ vs $M_{\text{unified}}$) | Decision agreement ($\mathbb{P}$), Level changes, Reversals, Probes, Median/P95 latency, Agent calls | Paired session differences, Wilcoxon signed-rank, 95% CIs | **CRITICAL:** Closes the primary reviewer vulnerability regarding RQ2. | Low (CPU deterministic replay, $\approx 30$\,s) |
| **E2** | **P0** | **Mechanistic Invariance Audit ($M_3 \equiv M_1$)** | What architectural invariants enforce exact difficulty trajectory equivalence between the full system and the coaching-ablated system? | Prior audit observed $M_3 \equiv M_1$ empirically but did not formalize the structural proof (exclusive authority, lack of reverse communication, read observation isolation). | Coaching agent presence ($M_1$ on vs $M_3$ off) | Trajectory divergence, authority leakage, state inspection | Exhaustive 160-session diff, contract inspection | **HIGH:** Turns a negative finding into an architectural contribution. | Zero (analytical & trace audit) |
| **E3** | **P1** | **Cluster $k=1$ Empirical Dissection** | Which measurable properties of Cluster 1 (Trees & Graph Traversals) drive the entire proactive probing gain ($+4.75$ turns)? | Current manuscript identifies Cluster 1 dominance but does not explain *why* concepts in Cluster 1 persist while other clusters resolve. | Cluster Index ($k \in [0, 7]$) | Concept miss frequency, repeated miss rate, remediation trigger rate | Per-cluster descriptive statistics & feature distribution | **HIGH:** Reframes cluster dependence from a weakness to a finding on trace characteristics. | Low ($\approx 10$\,s data inspection) |
| **E4** | **P1** | **Architectural Attribution of Contradicted Predictions (A9 & A10)** | Why did disabling PPO ($M_7$) alter only 2.5% of sessions, and why did canonical guardrails ($B_{0c}$) alter 0.0% of sessions? | Predictions were recorded as contradicted, but the architectural explanation was only sketched. | PPO availability ($M_1$ vs $M_7$); Guardrail version ($B_0$ vs $B_{0c}$) | Heuristic decision agreement, acoustic feature values in replay payloads | Decision-by-decision rule trace comparison | **MEDIUM:** Demonstrates rigorous scientific humility and architectural insight. | Low (trace audit) |
| **E5** | **P2** | **Dispatch Overhead & Serialization Profiling** | What is the precise per-turn latency decomposition across schema validation, circuit breakers, and agent execution? | Currently reported as $+1.04$\,ms median per-turn delta without detailed micro-benchmark breakdown. | Serialization architecture (2 Pydantic models vs 1 unified model) | CPU cycle time, P50, P95, P99 latency distribution | 1,000-iteration micro-benchmark with bootstrap CIs | **MEDIUM:** Strengthens operational trade-off discussion. | Low ($\approx 5$\,s) |
| **E6** | **P3** | **Stochastic Seed Scaling (Seeds > 20)** | Does increasing the question permutation seeds from 20 to 50 alter trajectory variance? | Current N=160 uses 20 permutations. Adding seeds increases runtime without increasing candidate payload diversity. | Permutation seeds ($N_s = 400$) | Trajectory variance | Bootstrap CI | **LOW:** Does not resolve the 8-cluster bottleneck; risks pseudoreplication. | Medium ($\approx 2$\,min) |

---

## 3. Execution Strategy

We will execute **E1, E2, E3, E4, and E5** strictly in priority order:
1. Implement `UnifiedCoachAgent` in `agents/multiagent/unified_agent.py` in the candidate workspace.
2. Build unit and integration tests verifying equivalent state, equivalent heuristic logic, and equivalent proposal synthesis.
3. Run the paired replay experiment across all 160 sessions (8 clusters $\times$ 20 seeds) with matched seeds.
4. Measure decision agreement, trajectory metrics, and runtime latency.
5. Analyze the mechanism behind $M_3 \equiv M_1$ and the Cluster 1 characteristics.
6. Record all empirical findings in `STAGE2_SCIENTIFIC_FINDINGS.md`.
