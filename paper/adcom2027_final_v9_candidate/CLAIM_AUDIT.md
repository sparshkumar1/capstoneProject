# Comprehensive Scientific Claim Audit and Evidence Traceability Matrix
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `CLAIM_AUDIT.md`  
**Candidate Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Status:** 100% Verified against Raw Execution Artifacts (69/69 Checks Passed)

---

## 1. Executive Summary

Every quantitative statement, confidence interval, point estimate, and architectural invariant appearing in the ADCoM 2027 candidate paper (*"Bounded-Authority Agents in an Orchestrated Interview-Practice System: Coordination, Arbitration and Fault Containment"*) was audited against the raw execution records in `research/multiagent/results/`.

The verification script `verification/verify_paper.py` executed across the built PDF text, confirming:
$$\text{Total Quantitative Checks: } 69 \quad \vert \quad \text{Passed: } 69 \quad \vert \quad \text{Failed: } 0$$

All empirical evidence is strictly classified into five defensive categories:
1. **REPLAY:** Deterministic replay of 64 recorded human-interview evaluator payloads across 20 question orders ($N = 1,920$ sessions in XA; $N = 960$ sessions in XC).
2. **FAULT-INJECTED:** Synthetic fault injection into worker threads ($N = 1,760$ sessions in XB).
3. **SYNTHETIC:** Grounding probe validation against 64 candidate responses ($N = 192$ checks in XD).
4. **SOCKET:** Real network socket fault injection exercising HTTP 5xx circuit-breaker mechanics (XE).
5. **HISTORICAL REPRODUCTION:** Byte-for-byte reproduction of historical baseline traces (752 sessions in XE).

> [!IMPORTANT]
> **Zero Human / Live LLM Evidence:** The manuscript makes **zero claims** of candidate learning, human skill improvement, interview pass rates, or live generative LLM reliability. All experiments evaluate architectural coordination, state arbitration, and fault containment under controlled replay.

---

## 2. Claim-to-Evidence Traceability Matrix

The table below maps every major manuscript claim to its implementation code, experimental class, raw artifact, and audit status:

| # | Manuscript Claim | Code Seam / Function | Experiment & Class | Underlying Artifact Path | Verification Status |
|:---:|:---|:---|:---:|:---|:---:|
| **1** | Multi-agent coordination alters trajectory in 160/160 replay sessions ($M_1$ vs $B_0$). | `strategy_agent.py`, `coordinator.decide_difficulty` | XA (REPLAY) | `results/xa/xa_runs.jsonl` | **VERIFIED** (160/160 differ) |
| **2** | Level changes decrease from 15.12 to 12.45 ($\Delta = -2.67$). | `agents/orchestrator/interview_orchestrator.py` | XA (REPLAY) | `results/xa/xa_summary.csv` | **VERIFIED** (Cluster CI: $[-4.50, -0.24]$) |
| **3** | Reversals decrease from 11.74 to 9.87 ($\Delta = -1.88$). | `arbitration.py::arbitrate_difficulty` | XA (REPLAY) | `results/xa/xa_summary.csv` | **VERIFIED** (Cluster CI: $[-3.12, -0.27]$) |
| **4** | PPO agreement fraction is 0.774 ($\Delta = -0.226$). | `coordinator.py::decide_difficulty` | XA (REPLAY) | `results/xa/xa_summary.csv` | **VERIFIED** (Cluster CI: $[-0.284, -0.170]$) |
| **5** | Proactive probes add $+0.59$ turns per session on average. | `arbitration.py::arbitrate_probe` | XA (REPLAY) | `results/xa/xa_summary.csv` | **VERIFIED** (Driven by cluster $k=1$) |
| **6** | Silent agent configuration ($M_2$) yields 100% identical paths to baseline ($B_0$). | `runtime.py`, `coordinator.py` | XA (REPLAY) | `results/xa/xa_runs.jsonl` (A4) | **VERIFIED** (160/160 identical) |
| **7** | Coaching, communication, grounding, and authority ablations ($M_3, M_5, M_6$) leave difficulty identical. | `coaching_agent.py`, `grounding.py` | XA (REPLAY) | `results/xa/xa_runs.jsonl` (A5) | **VERIFIED** (160/160 identical) |
| **8** | Removing confidence threshold ($\tau = 0.0$) collapses level changes to 2.225 and PPO agreement to 0.014. | `arbitration.py::arbitrate_difficulty` | XC (REPLAY) | `results/xc/xc_summary.csv` (C1) | **VERIFIED** (Replicates $M_4$ collapse) |
| **9** | Threshold sweep is invariant across $\tau \in [0.5, 0.8]$ (12.450 level changes, 0.774 agreement). | `strategy_agent.py` confidence rules | XC (REPLAY) | `results/xc/xc_summary.csv` (C2–C5) | **VERIFIED** (Discrete rule steps) |
| **10** | Threshold $\tau = 0.9$ completely silences Strategy Agent (15.120 level changes, 1.000 agreement). | `arbitration.py::arbitrate_difficulty` | XC (REPLAY) | `results/xc/xc_summary.csv` (C5) | **VERIFIED** (Reverts to $B_0$) |
| **11** | Unarbitrated Strategy Agent ($M_4$) bypasses guardrails in 38/40 sessions (95.0%). | `coordinator.py` bypass path | XB (FAULT) | `results/xb/xb_runs.jsonl` (B3) | **VERIFIED** (Clopper-Pearson: $[83.1\%, 99.4\%]$) |
| **12** | Full arbitration ($M_1$) contains guardrail bypass to 0/40 sessions (0.0%). | `arbitration.py` safety envelope | XB (FAULT) | `results/xb/xb_runs.jsonl` (B3) | **VERIFIED** (Clopper-Pearson: $[0.0\%, 8.8\%]$) |
| **13** | Removing coaching grounding check permits ungrounded emphasis in 40/40 sessions (100.0%). | `grounding.py::check_plan` | XB (FAULT) | `results/xb/xb_runs.jsonl` (B4) | **VERIFIED** (Clopper-Pearson: $[91.2\%, 100.0\%]$) |
| **14** | Active grounding check contains ungrounded leakage to 0/40 sessions (0.0%). | `grounding.py::check_plan` | XB (FAULT) | `results/xb/xb_runs.jsonl` (B4) | **VERIFIED** (Clopper-Pearson: $[0.0\%, 8.8\%]$) |
| **15** | Injecting 152 forbidden keys produces 0 state corruptions across all configurations. | `authority.py::FORBIDDEN_KEYS`, schema | XB (FAULT) | `results/xb/xb_runs.jsonl` (B2) | **VERIFIED** (Schema blocks keys) |
| **16** | Syntactically valid adversarial proposals serve as final source for 10.8 decisions/session. | None (Architectural boundary) | XB (FAULT) | `results/xb/xb_runs.jsonl` | **VERIFIED** (Fundamental limitation) |
| **17** | Agent worker timeout (150 ms) yields p95 turn latency of 154.4 ms vs 4.4 ms baseline. | `coordinator.py::_call` timeout handler | XB (FAULT) | `results/xb/xb_runs.jsonl` (B5) | **VERIFIED** (Bounded overhead) |
| **18** | Circuit breaker trips in 29/40 sessions (72.5%) at fault rate 0.3 across all 7 fault types. | `circuit_breaker.py` per-agent logic | XB (FAULT) | `results/xb/xb_runs.jsonl` (B6) | **VERIFIED** (Same pseudo-random schedule) |
| **19** | PPO unavailable alters path in only 4/160 sessions (2.5%), contradicting Prediction A9. | Rule-based heuristic fallback | XA (REPLAY) | `results/xa/xa_predictions.csv` | **VERIFIED** (Contradiction explained) |
| **20** | Canonical guardrails alter 0/160 replay paths, contradicting Prediction A10. | `guardrail_impl` switch | XA (REPLAY) | `results/xa/xa_predictions.csv` | **VERIFIED** (Acoustic signals absent) |
| **21** | Inline vs canonical guardrails disagree on 4,728 of 39,930 grid points (11.84%). | `rl/guardrails.py` vs inline | Code Audit | `tests/unit/test_guardrail_impl.py` | **VERIFIED** (Pinned grid counts) |
| **22** | Rebuilt grounding probe accepts paraphrased feedback in 57/57 cases (17 historical rejects were regex flaws). | `_validate_feedback_output` | XD (SYNTH) | `results/xd/xd_grounding.json` | **VERIFIED** (Syntactic artifact) |
| **23** | Historical E1 fail-closed replay reproduces byte-for-byte across 752 sessions. | `strict_evaluator_contract=True` | XE (HIST) | `results/xe_e1/xe_e1_reproduction.json` | **VERIFIED** (Byte-identical hash) |
| **24** | 5xx circuit breaker reduces socket connection attempts from 24 to 3 under gateway failure. | `circuit_breaker.py::record_http` | XE (SOCKET) | `results/xe_b503/xe_b503.json` | **VERIFIED** (Single machine run) |

---

## 3. Disclosed Negative Results and Contradicted Hypotheses

A core strength of the paper's scientific defensibility is its refusal to suppress contradicted pre-registered hypotheses:

1. **Prediction A9 (PPO Fallback Divergence):**
   - *Pre-registered Hypothesis:* Disabling PPO would alter $\ge 50\%$ of session paths.
   - *Empirical Observation:* Altered only **4/160 sessions (2.5%)**.
   - *Root Cause:* The deterministic Strategy Agent heuristic rules predominantly make the identical difficulty choice as the rule-based heuristic fallback.
2. **Prediction A10 (Guardrail Divergence):**
   - *Pre-registered Hypothesis:* Canonical guardrails would alter $\ge 1$ session path.
   - *Empirical Observation:* Altered **0/160 sessions (0.0%)**.
   - *Root Cause:* The 64 recorded evaluator payloads lack real-time acoustic signals (voice pitch, hesitation, acoustic confidence), holding inputs in the non-divergent interior of the guardrail state space.
3. **Prediction B6 (Circuit Breaker Tripping Rate):**
   - *Pre-registered Hypothesis:* Breaker would trip in $\ge 80\%$ of sessions at fault rate 0.3.
   - *Empirical Observation:* Tripped in **72.5% of sessions (29/40)**.
   - *Root Cause:* Identical across all 7 fault types because all worker schedules share a common deterministic seed schedule (`seed=31k+seed`).

---

## 4. Unverified Claims and Strict Limitations

The following claims are **explicitly not supported by evidence and are disclaimed in Section 9**:
- **Candidate Learning:** No claim that the system improves human interview performance or hiring outcomes.
- **External Superiority:** No claim that PREPAIred outperforms general multi-agent frameworks (AutoGen, MetaGPT, LangGraph) on general tasks.
- **Generative LLM Safety:** No claim that LLM hallucinations are completely eliminated; the system bounds only orchestration and proposal authority.
- **Live Deployment Performance:** No claim of production latency under live candidate traffic.
