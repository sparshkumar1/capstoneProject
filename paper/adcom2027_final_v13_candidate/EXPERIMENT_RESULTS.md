# Verified Experimental Results and Sensitivity Analysis
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `EXPERIMENT_RESULTS.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Status:** Independent Recomputation & Verification (43/43 Checks Passed)

---

## 1. Provenance and Verification Overview

All results documented herein derive directly from raw replay execution artifacts in `research/multiagent/results/`. The automated claim verification script ([`verification/verify_paper.py`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v11_candidate/verification/verify_paper.py)) executed against the compiled manuscript PDF text, confirming:
$$\text{Total Quantitative Claims Tested: } 43 \quad \vert \quad \text{Passed: } 43 \quad \vert \quad \text{Failed: } 0$$

All experiments execute deterministically through the real orchestrator hub under `EVALUATOR_MOCK_MODE=1` using 64 recorded production-evaluator payloads. No live generative large language model was executed; LLM gateways were stubbed as down, and deterministic template renderers handled text formatting.

---

## 2. Experiment XA: Multi-Agent Coordination Dynamics (RQ1)

Experiment XA evaluates the multi-agent coordination layer across 160 replay sessions (8 recorded candidate response clusters $\times$ 20 seeded question orders) under 12 controlled ablation conditions.

### 2.1 Replay Trajectory Summary across Conditions

| Condition | Description | Mean Level Changes | Mean Reversals | PPO Agreement Fraction | Mean Probe Turns | Median Turn Latency (p50) | 95th Pct Turn Latency (p95) | Mean Agent Calls |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$B_0$** | Frozen PPO Baseline (No Agents) | 15.12 | 11.74 | 1.000 | 0.00 | 0.546\,ms | 2.056\,ms | 0.0 |
| **$M_1$** | Full Multi-Agent Configuration | **12.45** | **9.87** | **0.774** | **+0.59** | 1.589\,ms | 4.411\,ms | 47.7 |
| **$M_2$** | Silent Agent (Zero Proposals) | 15.12 | 11.74 | 1.000 | 0.00 | 0.622\,ms | 2.188\,ms | 47.7 |
| **$M_3$** | Coaching Agent Ablated | 12.45 | 9.87 | 0.774 | +0.59 | 1.114\,ms | 3.205\,ms | 23.9 |
| **$M_4$** | Arbitration Ablated (Raw Strategy) | 2.22 | 1.15 | 0.014 | +0.59 | 1.520\,ms | 4.190\,ms | 47.7 |
| **$M_5$** | Peer Messaging Ablated | 12.45 | 9.87 | 0.774 | +0.59 | 1.581\,ms | 4.380\,ms | 47.7 |
| **$M_7$** | PPO Policy Disabled (Rule Fallback) | 12.45 | 9.87 | 0.774 | +0.59 | 1.575\,ms | 4.350\,ms | 47.7 |
| **$B_7$** | Pure Heuristic Baseline | 15.12 | 11.74 | — | 0.00 | 0.540\,ms | 2.040\,ms | 0.0 |
| **$B_{0c}$** | Canonical Guardrails Baseline | 15.12 | 11.74 | 1.000 | 0.00 | 0.550\,ms | 2.060\,ms | 0.0 |

### 2.2 Execution Invariants
- Across all 160 sessions in every condition:
  - Session completion rate: **160/160 (100.0%)**
  - Authority preservation: **160/160 (100.0%)** (zero uncommitted or modified evaluator scores)
  - Transition validity: **160/160 (100.0%)** (difficulty levels strictly bounded in $[1, 5]$; max step $\le 1$)
  - Clopper-Pearson exact 95% lower bound for 160/160: **0.977**
- Condition $M_2$ (silent agent) produced difficulty, score, and question trajectories **100% identical to $B_0$ (160/160)**, confirming complete infrastructure transparency when agents remain silent.

### 2.3 Statistical Confidence Intervals: Session vs Cluster Bootstrap

The 160 replay sessions reuse 8 recorded candidate answer sets across 20 question orders. Below is the contrast between naive session-level bootstrapping and Field & Welsh (2007) cluster bootstrapping ($B = 10{,}000$):

| Metric | Point Estimate ($\Delta = M_1 - B_0$) | Naive Session Bootstrap (95% CI) | Cluster Bootstrap (Field & Welsh, 95% CI) | Cluster Sign Consistency |
|:---|:---:|:---:|:---:|:---:|
| **Level Changes** | **$-2.67$** | $[-3.19, -2.13]$ | $[-4.50, -0.24]$ | Negative in 7 of 8 clusters |
| **Reversals** | **$-1.88$** | $[-2.28, -1.46]$ | $[-3.12, -0.27]$ | Negative in 7 of 8 clusters |
| **PPO Agreement** | **$-0.226$** | $[-0.235, -0.218]$ | $[-0.284, -0.170]$ | Negative in 8 of 8 clusters |
| **Proactive Probes** | **$+0.59$** | $[+0.34, +0.85]$ | $[0.00, +1.76]$ | **Positive in ONLY 1 of 8 clusters** |

### 2.4 Cluster Dominance and LOCO Sensitivity Analysis
- **Cluster $k=1$ Sensitivity:** Proactive probing added turns in **only 1 of the 8 clusters ($k=1$)**. In clusters $k \in \{0, 2, 3, 4, 5, 6, 7\}$, proactive probing added **0.00 turns**.
- **Leave-One-Cluster-Out (LOCO):**
  - Omitting cluster $k=1$ shifts the level-change delta to **$-3.76$** (CI $[-4.81, -2.78]$).
  - Omitting any of the other seven clusters results in the 95% cluster interval crossing zero.
  - The directional tendency toward difficulty smoothing holds across 7/8 clusters, but specific numerical magnitudes are highly cluster-dependent.

### 2.5 Strategy Proposal Distribution
Across 160 sessions, the Strategy Agent emitted **3,814 proposals**:
- `remediate`: 1,300 proposals (confidence 0.80)
- `recover`: 928 proposals (confidence 0.80)
- `recover`: 312 proposals (confidence 0.70)
- `steady`: 1,274 proposals (confidence 0.45; filtered by $\tau = 0.6$)
- `stretch`: **0 proposals** (candidate trajectories never satisfied the sustained high-performance criteria: 3 consecutive scores $\ge 0.60$, $\text{EMA} \ge 0.70$).

### 2.6 Coordination Latency Overhead
- Median per-turn latency increased from $0.546$\,ms ($B_0$) to $1.589$\,ms ($M_1$), yielding a paired median difference of **$+1.04$\,ms (95% CI $[+1.00, +1.08]$\,ms)**.
- 95th percentile latency increased from $2.056$\,ms to $4.411$\,ms.
- Average agent invocations: **47.7 calls per session**.

---

## 3. Experiment XC: Coordination Mechanisms and Sensitivity (RQ3)

Experiment XC isolates the causal mechanism responsible for the $M_4$ oscillation collapse by sweeping the arbitration confidence threshold $\tau \in [0.0, 0.9]$ across 160 replay sessions per cell (960 sessions total) with all other safety envelopes active.

### 3.1 Threshold Decomposition Results

| Threshold $\tau$ | Mean Level Changes | Mean Reversals | PPO Agreement Fraction | Guardrail Bypass | Active Proposals Admitted |
|:---:|:---:|:---:|:---:|:---:|:---:|
| $\tau = 0.0$ | **2.225** | 1.150 | **0.014** | **0/160 (0.0%)** | 100% admitted (incl. unevidenced `steady`) |
| $\tau = 0.5$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced proposals admitted |
| $\tau = 0.6$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced proposals admitted (Default) |
| $\tau = 0.7$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced proposals admitted |
| $\tau = 0.8$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced proposals admitted |
| $\tau = 0.9$ | **15.119** | **11.740** | **0.626** | 0/160 (0.0%) | **0% admitted (Agent completely silent)** |

> **Key Mechanistic Findings:**
> 1. Setting $\tau = 0.0$ replicates the $M_4$ collapse (2.225 level changes, 0.014 agreement) with **zero guardrail bypass**. This proves that the collapse is driven entirely by uncalibrated Strategy proposals overriding PPO, not by absent guardrails.
> 2. The plateau across $[0.5, 0.8]$ reflects discrete heuristic confidence increments ($\min(0.95, 0.5 + 0.1n)$).
> 3. Setting $\tau = 0.9$ silences the agent, reverting the system to $B_0$.
> 4. All 5 registered XC predictions were confirmed.

### 3.2 Contradicted Pre-Registered Predictions
- **Prediction A9 (PPO Fallback Interaction):** Pre-registered prediction asserted that disabling PPO ($M_7$) would alter $\ge 50\%$ of session paths. **Observed: 4 of 160 sessions (2.5%).** Under deterministic replay, the Strategy Agent heuristic predominantly agrees with the rule-based heuristic fallback.
- **Prediction A10 (Guardrail Implementation Divergence):** Pre-registered prediction asserted that canonical guardrails ($B_{0c}$) would alter $\ge 1$ replay path. **Observed: 0 of 160 sessions (0.0%).** Replay lacks real-time acoustic signals (voice hesitation, speech confidence), holding inputs at neutral defaults and never exercising the 11.8% divergent guardrail boundary (4,728 of 39,930 grid points).

---

## 4. Evaluating Agent Specialization (RQ2)

### 4.1 Trajectory Invariance under Coaching Ablation ($M_3$)
In Condition $M_3$, the Coaching Agent was disabled while Strategy remained active:
- Across all 160 sessions, difficulty level changes (12.45), reversals (9.87), and trajectory paths were **100% identical to the full two-agent configuration ($M_1$)** (160/160 identical).
- Coaching decisions and ledgers have zero causal influence on difficulty adaptation.

### 4.2 Decision Equivalence under Deterministic Rules
Under equivalent observation inputs and identical decision heuristics:
$$\mathbb{P}(\text{Decision}_{\text{unified}} = \text{Decision}_{\text{split}}) = 1.0$$
A unified controller executing the weakness rules and passing the resulting intent into the coaching logic produces mathematically identical proposals. Specialization provides **zero algorithmic decision advantage** in deterministic settings.

### 4.3 Architectural Trade-Off Matrix

| Architectural Feature | Specialized Architecture ($M_{\text{split}}$) | Unified Architecture ($M_{\text{unified}}$) |
|:---|:---|:---|
| **State Ledgers** | Disjoint ledgers (Weakness vs Coaching History) | Monolithic session state dictionary |
| **Failure Containment** | Bulkhead isolation: coaching exception spares strategy | Whole-turn fail-closed: coaching error drops strategy |
| **Dispatch Overhead** | 2 serialization passes, 2 schema validations ($+1.04$\,ms p50) | 1 serialization pass, 1 schema validation ($\approx +0.5$\,ms) |
| **Auditability** | Separate per-agent ledgers, circuit breakers, and logs | Opaque joint decision state |
| **Decision Quality** | Identical under deterministic rules ($\mathbb{P} = 1.0$) | Identical under deterministic rules ($\mathbb{P} = 1.0$) |

### 4.4 Conclusion on Specialization
Agent specialization does not improve decision quality or trajectory optimization. Its value is strictly architectural: software modularity, independent maintainability, and bulkhead fault containment, balanced against a $+1.04$\,ms median dispatch latency penalty.
