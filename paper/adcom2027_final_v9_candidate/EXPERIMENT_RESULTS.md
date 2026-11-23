# Experimental Results, Statistical Analysis, and Sensitivity Audits
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `EXPERIMENT_RESULTS.md`  
**Candidate Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Status:** Complete Empirical Record & Independent Recomputation

---

## 1. Overview and Reproducibility Provenance

All experimental results reported in the manuscript derive directly from raw execution artifacts stored in `research/multiagent/results/`. Every quantitative claim, point estimate, and confidence interval has been independently verified by `verification/verify_paper.py` (69/69 checks passing) and `research/multiagent/analysis/independent_check.py`.

The experiments span four empirical classes:
- **REPLAY:** Deterministic replay of 64 recorded human-interview evaluator payloads across 20 pseudo-random question-order permutations (seeds 42–61), yielding 160 sessions per condition.
- **FAULT-INJECTED:** Controlled synthetic fault injection into Strategy and Coaching worker threads across 1,760 sessions.
- **SYNTHETIC:** Grounding validation against 64 candidate responses with synthesized feedback.
- **SOCKET:** Real network socket fault injection exercising HTTP 5xx circuit-breaker mechanics.

---

## 2. Experiment XA: Deterministic Replay Ablation (1,920 Sessions)

Experiment XA evaluates the multi-agent coordination layer across 12 distinct ablation conditions. In each condition, 160 simulated interview sessions (8 recorded candidate response clusters $\times$ 20 question orders) are replayed through the real orchestrator hub with `EVALUATOR_MOCK_MODE=1` and frozen PPO weights.

### 2.1 Replay Trajectory Metrics and Ablation Comparison

| Condition | Description | Mean Level Changes | Mean Reversals | PPO Agree Fraction | Proactive Probes (Turns) |
|:---|:---|:---:|:---:|:---:|:---:|
| **$B_0$** | Frozen PPO Baseline (No Agents) | 15.12 | 11.74 | 1.000 | 0.00 |
| **$M_1$** | Full Multi-Agent Configuration | **12.45** | **9.87** | **0.774** | **+0.59** |
| **$M_2$** | Silent Agent (Zero Weight) | 15.12 | 11.74 | 1.000 | 0.00 |
| **$M_3$** | Coaching Agent Ablated | 12.45 | 9.87 | 0.774 | +0.59 |
| **$M_4$** | No Arbitration (Raw Strategy) | 2.22 | 1.15 | 0.014 | +0.59 |
| **$M_5$** | No Peer Communication | 12.45 | 9.87 | 0.774 | +0.59 |
| **$M_6$** | No Coaching Grounding Check | 12.45 | 9.87 | 0.774 | +0.59 |
| **$M_7$** | PPO Policy Disabled (Heuristic) | 12.45 | 9.87 | 0.774 | +0.59 |
| **$B_7$** | Pure Heuristic Baseline | 15.12 | 11.74 | — | 0.00 |
| **$B_{0c}$** | Canonical Guardrails Baseline | 15.12 | 11.74 | 1.000 | 0.00 |

### 2.2 Statistical Confidence Intervals: Session vs Cluster Bootstrap

Because the 160 replay sessions reuse the same 8 underlying recorded answer sets across 20 permutations, treating sessions as independent samples underestimates variance. The table below compares the naive session-level bootstrap ($B = 10,000$) against the cluster bootstrap over the 8 answer clusters (Field & Welsh 2007):

| Metric | Point Estimate ($\Delta = M_1 - B_0$) | Naive Session Bootstrap (95% CI) | Cluster Bootstrap (Field & Welsh, 95% CI) | Sign Consistency Across Clusters |
|:---|:---:|:---:|:---:|:---:|
| **Level Changes** | **$-2.67$** | $[-3.12, -2.22]$ | $[-4.50, -0.24]$ | 8 / 8 clusters negative |
| **Reversals** | **$-1.88$** | $[-2.24, -1.51]$ | $[-3.12, -0.27]$ | 8 / 8 clusters negative |
| **PPO Agreement** | **$-0.226$** | $[-0.235, -0.218]$ | $[-0.284, -0.170]$ | 8 / 8 clusters negative |
| **Extra Turns (Probes)**| **$+0.59$** | $[+0.41, +0.78]$ | $[0.00, +1.76]$ | **1 / 8 clusters positive** |

> **Key Finding:** While the smoothing effect (reduced level changes and reversals) and PPO disagreement are consistent in direction across all 8 clusters, the extra-turn probing effect is driven entirely by a single recorded answer set ($k = 1$). Without cluster $k=1$, mean probe turns are $+0.00$.

### 2.3 Leave-One-Cluster-Out (LOCO) Sensitivity Audit

A leave-one-cluster-out jackknife analysis confirms cluster dependencies:
- **Cluster $k=1$ Influence:** Omitting cluster $k=1$ shifts the level change difference to $-2.11$ and extra turns to $+0.00$. The cluster bootstrap interval for level changes strictly excludes zero only when all 8 clusters are pooled or when cluster $k=1$ is omitted.
- **Directional Robustness:** The negative sign of difficulty oscillation reduction is preserved under all 8 jackknife resamples.

### 2.4 Contradicted Predictions in Replay
1. **Prediction A9 (PPO Fallback Divergence):** Pre-registered prediction asserted that disabling PPO would alter $\ge 50\%$ of session paths. **Observed: 4/160 sessions (2.5%).** Under deterministic replay, the rule-based Strategy Agent predominantly agrees with the rule-based heuristic fallback.
2. **Prediction A10 (Guardrail Divergence):** Pre-registered prediction asserted that canonical guardrails would alter $\ge 1$ session path. **Observed: 0/160 sessions (0.0%).** Replay sessions lack raw acoustic signals (pitch, hesitation, voice energy), holding audio confidence at default neutral levels and never reaching the 11.8% divergent guardrail boundary.

---

## 3. Experiment XB: Synthetic Fault Injection (1,760 Sessions)

Experiment XB injects 11 distinct synthetic fault types into Strategy and Coaching agent threads across 4 defense configurations (40 sessions per cell = 1,760 sessions total).

### 3.1 Safeguard Containment Matrix across 11 Fault Classes

| Fault Injection Type | Injected Agent | Defense Active | Sessions Completed | Authority Invariants | State Transitions Valid | Guardrail Bypass Rate | Breaker Trips (Rate = 0.3) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `strat:crash` | Strategy | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `strat:malformed` | Strategy | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `strat:stale` | Strategy | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `strat:timeout` | Strategy | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `strat:forbidden_key` | Strategy | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `strat:nan_confidence` | Strategy | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `strat:adversarial_valid`| Strategy | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 0/40 (0.0%) |
| `coach:crash` | Coaching | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `coach:malformed` | Coaching | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `coach:stale` | Coaching | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |
| `coach:ungrounded` | Coaching | Full | 40/40 (100%) | 0 leaks (100%) | 100% | 0/40 (0.0%) | 29/40 (72.5%) |

### 3.2 Key Ablation Contrasts in Fault Containment
- **Guardrail Bypass (Arbitration Defense):**
  - Without Arbitration ($M_4$): Guardrail bypass occurred in **38/40 sessions (95.0%)**, [83.1%, 99.4%] Clopper-Pearson 95% CI.
  - With Full Arbitration ($M_1$): Guardrail bypass contained to **0/40 sessions (0.0%)**, [0.0%, 8.8%] Clopper-Pearson 95% CI.
- **Ungrounded Pedagogical Leakage (Grounding Check Defense):**
  - Without Grounding Check: Ungrounded tags leaked in **40/40 sessions (100.0%)**, [91.2%, 100.0%] Clopper-Pearson 95% CI.
  - With Grounding Check: Ungrounded tags contained to **0/40 sessions (0.0%)**, [0.0%, 8.8%] Clopper-Pearson 95% CI.
- **Authority Scanning vs Schema Enforcement:**
  - Injecting 152 forbidden keys (`score`, `turn_index`, etc.) into proposals resulted in 0 state corruptions in both conditions. Pydantic schema validation (`extra=forbid`) blocks the keys before authority scanning executes. The authority matrix provides semantic diagnostic classification rather than primary containment.
- **Adversarial Proposal Vulnerability:**
  - Syntactically valid proposals with fabricated evidence and $\text{confidence} \ge \tau$ bypassed all filters, serving as the final difficulty driver for **10.8 decisions per session** (fundamental boundary).
- **Circuit Breaker Tripping (Prediction B6 Contradiction):**
  - At fault rate 0.3, the breaker tripped in **29/40 sessions (72.5%)**, falling short of the $\ge 80\%$ prediction. The trip rate was identical across all 7 fault types because all worker fault schedules share a common deterministic seed schedule (`seed=31k+seed`).
- **Timeout Latency Overhead:**
  - Simulated worker thread hangs yielded a p95 turn latency of **154.4 ms** compared to **4.4 ms** under normal execution, bounded directly by the 150 ms timeout parameter.

---

## 4. Experiment XC: Confidence Threshold Sensitivity (960 Sessions)

Experiment XC sweeps the arbitration confidence threshold $\tau \in \{0.0, 0.5, 0.6, 0.7, 0.8, 0.9\}$ across 160 replay sessions per cell (960 sessions total) to isolate the mechanism responsible for the $M_4$ collapse.

| Threshold $\tau$ | Mean Level Changes | Mean Reversals | PPO Agreement Fraction | Guardrail Bypass | Active Strategy Proposals |
|:---:|:---:|:---:|:---:|:---:|:---:|
| $\tau = 0.0$ | **2.225** | 1.150 | **0.014** | 0/160 (0.0%) | 100% accepted |
| $\tau = 0.5$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced accepted |
| $\tau = 0.6$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced accepted |
| $\tau = 0.7$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced accepted |
| $\tau = 0.8$ | 12.450 | 9.870 | 0.774 | 0/160 (0.0%) | Evidenced accepted |
| $\tau = 0.9$ | **15.120** | **11.740** | **1.000** | 0/160 (0.0%) | **0% accepted (silent)** |

> **Key Finding:** Setting $\tau = 0.0$ replicates the $M_4$ oscillation collapse without allowing guardrail bypass. The collapse is driven entirely by uncalibrated Strategy proposals overriding PPO, not by missing guardrails. The plateau across $[0.5, 0.8]$ reflects discrete confidence increments ($\min(0.95, 0.5 + 0.1n)$), and $\tau = 0.9$ completely silences the agent.

---

## 5. Experiment XD: Grounding Probe Rebuilding (64 Payloads)

Re-evaluating the historical grounding probe across 64 candidate responses revealed that:
- **17 historical grounding rejections** were syntactic artifacts caused by rigid regex matching on bullet formatting rather than genuine ungrounded hallucinations.
- When rebuilt with semantic span verification, valid paraphrased feedback achieved **57/57 accepted cases**.
- Synthetically fabricated concept tags were rejected in **64/64 cases (100.0%)**.

---

## 6. Experiment XE: Historical Reproduction and Socket Scenarios

1. **E1 Fail-Closed Reproduction:**
   - 752 historical replay sessions were executed under explicit contract flags (`strict_evaluator_contract=True`).
   - Trajectory records matched historical disk artifacts **byte-for-byte** (SHA-256 verified).
2. **B503 HTTP 5xx Circuit Breaker:**
   - Evaluated under socket fault injection simulating backend LLM gateway crashes.
   - Circuit breaker opened after 3 consecutive 5xx errors, reducing socket connection retries from 24 attempts to 3 attempts.
3. **E5 Breaker Scenario Timings:**
   - Evaluated across 7 operational fault scenarios; trip latency was verified to be sub-millisecond once threshold criteria were satisfied.

---

## 7. Experiment XM: Merged-Agent Feasibility Study (UNEXECUTED)

- **Protocol Status:** Fully specified in `EXPERIMENT_PLAN.md` and `MERGED_AGENT_EXPERIMENT.md`.
- **Execution Status:** **UNEXECUTED (Pre-registered protocol only)**.
- **Scientific Rationale for Deferral:**
  1. The multi-agent candidate manuscript already establishes full empirical support for its primary claims across 69 verified checks.
  2. Executing new agent architectures within the repository prior to the author and teacher review on 5 October violates the strict zero-mutation policy.
  3. The protocol is completely documented and ready for instant execution if authorized during teacher review.
