# Comprehensive Scientific & Methodological Audit (Phase One)
**Project:** PREPAIred — ADCoM 2027  
**Candidate Working Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Principal Research Engineer & Methodological Reviewer  

---

## 1. Executive Summary

This scientific audit evaluates every substantive claim in *Bounded-Authority Agents in an Orchestrated Interview-Practice System: Coordination, Arbitration and Fault Containment*. Every quantitative claim (69 in total) has been independently recomputed directly from raw JSONL and CSV experimental logs in `research/multiagent/results/`. Every architectural mechanism has been traced to its enforcing Python implementation.

### Key Audit Findings
1. **Empirical Precision:** 69 of 69 quantitative claims are byte-level reproducible and match the extracted text of the built PDF (`claim audit: 69/69 checks passed`).
2. **Evidence Classification:** All results are strictly categorized by evidence class:
   - **REPLAY:** Recorded evaluator outputs from 64 constructed answers across 8 technical question categories, replayed through the real orchestrator. No live LLM inference was executed during replay.
   - **FAULT-INJECTED:** 1,760 sessions injecting 11 distinct fault types into agent output envelopes to evaluate boundary enforcement.
   - **SOCKET:** Real local socket experiments measuring timeout overhead under HTTP hang conditions.
   - **SYNTHETIC:** 39,930-point parametric grid evaluating rule divergence between deployed and canonical guardrail implementations.
3. **Negative & Contradicted Findings Honestly Disclosed:**
   - Pre-registered prediction A9 (agents change trajectory $\ge 50\%$ when PPO is unavailable) was **contradicted** (agents only changed 4 of 160 sessions, 2.5%).
   - Pre-registered prediction A10 (canonical guardrails change trajectory in $\ge 1$ session vs legacy) was **contradicted** (0 changes across all 160 sessions due to constant confidence/hesitation in replay).
   - Pre-registered prediction B6 (breaker opens in $\ge 80\%$ of sessions at 0.3 fault rate) was **contradicted** (opened in 29 of 40 sessions, 72.5%).
   - RQ4 corrections explicitly document that an earlier audit overclaimed malformed-score fixes, which were actually defence-in-depth rather than resolving a production bug.
4. **Unflinching Scope & Threats to Validity:**
   - No human educational efficacy, learning gains, or interview placement success is claimed.
   - PPO policy is frozen and centralized; the paper explicitly disclaims multi-agent reinforcement learning.
   - Replay candidate does not react adaptively to changes in question difficulty.

---

## 2. Claim-to-Evidence Matrix (69 Verified Claims & Major Architectural Assertions)

| ID | Location | Manuscript Statement | Category | Supporting Experiment / Code | Raw Evidence Path | Verification Procedure | Verification Outcome | Uncertainty / Bounds | Action |
|:---:|:---|:---|:---:|:---|:---|:---|:---:|:---:|:---:|
| **C01** | Abstract, Sec. 6.1 | B0 mean level changes: 15.12 per session | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean across 160 sessions | **REPRODUCED** | Mean: 15.12 | Retain |
| **C02** | Abstract, Sec. 6.1 | M1 mean level changes: 12.45 per session | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean across 160 sessions | **REPRODUCED** | Mean: 12.45 | Retain |
| **C03** | Sec. 6.1, Tab. 3 | B0 reversals mean: 11.74 per session | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean across 160 sessions | **REPRODUCED** | Mean: 11.74 | Retain |
| **C04** | Sec. 6.1, Tab. 3 | M1 reversals mean: 9.87 per session | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean across 160 sessions | **REPRODUCED** | Mean: 9.87 | Retain |
| **C05** | Sec. 6.1, Tab. 3 | B0 PPO agreement: 0.626 | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean fraction | **REPRODUCED** | Mean: 0.626 | Retain |
| **C06** | Sec. 6.1, Tab. 3 | M1 PPO agreement: 0.400 | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean fraction | **REPRODUCED** | Mean: 0.400 | Retain |
| **C07** | Sec. 6.1, Tab. 4 | M1-B0 paired level changes CI: `[-3.19, -2.13]` | REPLAY | Experiment XA bootstrap | `results/xa/xa_runs.jsonl` | 10k paired percentile bootstrap | **REPRODUCED** | Point: -2.67 | Retain |
| **C08** | Sec. 6.1, Tab. 4 | M1-B0 paired reversals CI: `[-2.28, -1.46]` | REPLAY | Experiment XA bootstrap | `results/xa/xa_runs.jsonl` | 10k paired percentile bootstrap | **REPRODUCED** | Point: -1.88 | Retain |
| **C09** | Sec. 6.1, Tab. 4 | M1-B0 paired turns CI: `[+0.34, +0.85]` | REPLAY | Experiment XA bootstrap | `results/xa/xa_runs.jsonl` | 10k paired percentile bootstrap | **REPRODUCED** | Mean: +0.59 turns | Retain |
| **C10** | Sec. 6.1, Tab. 4 | M1-B0 median latency difference: `[+1.00, +1.08]` ms | REPLAY | Experiment XA pooled bootstrap | `results/xa/xa_paired.csv` | Clustered turn-level bootstrap | **REPRODUCED** | $\Delta$ p50: +1.04 ms | Retain |
| **C11** | Sec. 6.1 | Agent call frequency: 47.7 agent calls per session | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean M1 calls | **REPRODUCED** | Mean: 47.7 | Retain |
| **C12** | Sec. 6.1 | Strategy conflict decisions: 11.9 per session | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute mean M1 conflicts | **REPRODUCED** | Mean: 11.9 | Retain |
| **C13** | Sec. 6.1, Tab. 3 | M4 (no arbitration) level changes: 2.2 per session | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute M4 condition mean | **REPRODUCED** | Mean: 2.225 | Retain |
| **C14** | Sec. 6.1, Tab. 3 | M4 PPO agreement collapse: 0.014 | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute M4 PPO agreement | **REPRODUCED** | Mean: 0.014 | Retain |
| **C15** | Sec. 6.1, Tab. 3 | M4 guardrail bypass: 3 sessions contained bypass | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Count sessions with bypass > 0 | **REPRODUCED** | Count: 3 of 160 | Retain |
| **C16** | Sec. 6.1, Tab. 3 | B0 turn latency p50: 0.546 ms | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute pooled turn p50 | **REPRODUCED** | Median: 0.546 ms | Retain |
| **C17** | Sec. 6.1, Tab. 3 | M1 turn latency p95: 4.411 ms | REPLAY | Experiment XA (`xa_summary.csv`) | `results/xa/xa_summary.csv` | Recompute pooled turn p95 | **REPRODUCED** | 95th %ile: 4.411 ms | Retain |
| **C18** | Sec. 6.1, Tab. 5 | M7 vs B7 (no PPO) trajectory difference: 4 of 160 sessions | REPLAY | Experiment XA (`xa_runs.jsonl`) | `results/xa/xa_runs.jsonl` | Count trajectory divergences | **REPRODUCED** | 2.5% (A9 Contradicted) | Retain |
| **C19** | Abstract, Sec. 6.1 | M1 trajectory difference from B0: all 160 sessions | REPLAY | Experiment XA (`xa_runs.jsonl`) | `results/xa/xa_runs.jsonl` | Count trajectory divergences | **REPRODUCED** | 160 of 160 (100%) | Retain |
| **C20** | Sec. 6.1 | Clopper-Pearson 95% lower bound for 160/160: 0.977 | REPLAY | Binomial exact interval (`cp34`) | Computed via SciPy | Clopper-Pearson exact bound | **REPRODUCED** | `[0.977, 1.000]` | Retain |
| **C21** | Sec. 6.2, Tab. 6 | Injected forbidden keys: 152 injections | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Enumerate injected keys | **REPRODUCED** | Exactly 152 | Retain |
| **C22** | Sec. 6.2 | Authority vs Schema violation classification: 152/152 | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Check reason counters | **REPRODUCED** | 152 auth / 0 schema | Retain |
| **C23** | Sec. 6.2, Tab. 6 | Injected adversarial valid proposals: 930 injections | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Count injections across cells | **REPRODUCED** | Exactly 930 | Retain |
| **C24** | Sec. 6.2, Tab. 6 | Guardrail bypass under adversarial valid without arbitration: 38 of 40 | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Count bypass sessions in no-arb | **REPRODUCED** | 38 of 40 (0 in full) | Retain |
| **C25** | Sec. 6.2, Tab. 6 | Guardrail bypass in Strategy fault cells without arbitration: 34 of 40 | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Count bypass sessions across 6 cells | **REPRODUCED** | 34 of 40 in all 6 cells | Retain |
| **C26** | Sec. 6.2 | Adversarial valid final decision source: 10.8 decisions/session | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Recompute mean source count | **REPRODUCED** | Mean: 10.8 | Retain |
| **C27** | Sec. 6.2, Tab. 6 | Injected ungrounded coaching plans: 950 ungrounded plans | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Count ungrounded injections | **REPRODUCED** | Exactly 950 | Retain |
| **C28** | Sec. 6.2, Tab. 6 | Ungrounded concept leak without grounding check: 40 of 40 sessions | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Count leaks in no-grounding cell | **REPRODUCED** | 40 of 40 (0 in full) | Retain |
| **C29** | Sec. 6.2, Tab. 6 | Strategy timeout pooled p95 turn latency: 154.4 ms | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Compute 95th quantile of turn_ms | **REPRODUCED** | 154.4 ms (vs 4.4 clean) | Retain |
| **C30** | Sec. 6.2, Tab. 6 | Clean pooled p95 turn latency: 4.4 ms | REPLAY | Experiment XA (`xa_runs.jsonl`) | `results/xa/xa_runs.jsonl` | Compute 95th quantile clean M1 | **REPRODUCED** | 4.4 ms | Retain |
| **C31** | Sec. 6.2, Tab. 6 | Circuit breaker open frequency at 0.3 fault rate: 29 of 40 sessions | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Count breaker_open reasons | **REPRODUCED** | 29 of 40 (72.5%) | Retain |
| **C32** | Sec. 6.2, Tab. 6 | Circuit breaker open percentage: 72.5% | FAULT | Experiment XB (`xb_runs.jsonl`) | `results/xb/xb_runs.jsonl` | Compute percentage 29/40 | **REPRODUCED** | 72.5% (B6 Contradicted) | Retain |
| **C33** | Sec. 6.4, Tab. 8 | XD faithful acceptance on overlap-free subset: 47/47 | FAULT | Experiment XD (`xd_grounding.json`) | `results/xd/xd_grounding.json` | Recompute category counts | **REPRODUCED** | 47 of 47 (100%) | Retain |
| **C34** | Sec. 6.4, Tab. 8 | XD faithful acceptance with numbered placeholders: 64/64 | FAULT | Experiment XD (`xd_grounding.json`) | `results/xd/xd_grounding.json` | Recompute relabelled counts | **REPRODUCED** | 64 of 64 (100%) | Retain |
| **C35** | Sec. 6.4, Tab. 8 | XD truncated paraphrase credit acceptance interval: `[0.937, 1.000]` | FAULT | Experiment XD exact interval | `results/xd/xd_grounding.json` | Clopper-Pearson 57/57 | **REPRODUCED** | `[0.937, 1.000]` | Retain |
| **C36** | Sec. 7 | Earlier audit invariant I7 violation: 3 of 8 (V2) vs 7 of 8 (full) | FAULT | Experiment XE_E1 (`e1_runs.jsonl`) | `paper/adcom2027/results/e1_runs.jsonl` | Count I7 violations in old logs | **REPRODUCED** | 3/8 vs 7/8 (RQ4) | Retain |
| **C37** | Sec. 7 | E1 historical reproduction byte-identical rows: all 752 sessions | FAULT | Experiment XE_E1 reproduction | `results/xe_e1/xe_e1_reproduction.json` | Verify row-by-row SHA equality | **REPRODUCED** | 752 of 752 rows identical | Retain |
| **C38** | Sec. 7 | Malformed score HTTP attempts: 160 legacy vs 2 fixed | FAULT | Experiment XE_B503 | `results/xe_b503/xe_b503.json` | Compare retry attempt counts | **REPRODUCED** | 160 vs 2 attempts | Retain |
| **C39** | Sec. 7 | Circuit breaker hang_B median turn time: 24.72 s | SOCKET | Experiment XE_E5 (`e5_circuit_breaker.json`) | `results/xe_e5/e5_circuit_breaker.json` | Recompute baseline median time | **REPRODUCED** | 24.72 s (80 attempts) | Retain |
| **C40** | Sec. 7 | Circuit breaker hang_S_P30 median turn time: 3.09 s | SOCKET | Experiment XE_E5 (`e5_circuit_breaker.json`) | `results/xe_e5/e5_circuit_breaker.json` | Recompute P30 median time | **REPRODUCED** | 3.09 s (13 attempts) | Retain |
| **C41** | Sec. 7 | Circuit breaker hang_S_P60 median turn time: 6.20 s | SOCKET | Experiment XE_E5 (`e5_circuit_breaker.json`) | `results/xe_e5/e5_circuit_breaker.json` | Recompute P60 median time | **REPRODUCED** | 6.20 s (25 attempts) | Retain |
| **C42** | Sec. 6.3, Tab. 7 | XC tau=0 level changes collapse: 2.225 per session | REPLAY | Experiment XC (`xc_summary.csv`) | `results/xc/xc_summary.csv` | Verify TAU0 level changes | **REPRODUCED** | Mean: 2.225 | Retain |
| **C43** | Sec. 6.3, Tab. 7 | XC tau=0 PPO agreement collapse: 0.014 | REPLAY | Experiment XC (`xc_summary.csv`) | `results/xc/xc_summary.csv` | Verify TAU0 agreement | **REPRODUCED** | Mean: 0.014 | Retain |
| **C44** | Sec. 6.3 | XC pre-registered predictions outcome: All 5 supported | REPLAY | Experiment XC (`xc_predictions.csv`) | `results/xc/xc_predictions.csv` | Check verdicts for C1–C5 | **REPRODUCED** | 5 of 5 SUPPORTED | Retain |
| **C45** | Sec. 6.1 | Post-hoc cluster bootstrap level changes CI: `[-4.50, -0.24]` | REPLAY | Post-hoc analysis (`cluster_bootstrap.json`) | `results/post_hoc/cluster_bootstrap.json` | Recompute 8-cluster bootstrap CI | **REPRODUCED** | `[-4.50, -0.24]` | Retain |
| **C46** | Sec. 6.1 | Post-hoc cluster bootstrap reversals CI: `[-3.12, -0.27]` | REPLAY | Post-hoc analysis (`cluster_bootstrap.json`) | `results/post_hoc/cluster_bootstrap.json` | Recompute 8-cluster bootstrap CI | **REPRODUCED** | `[-3.12, -0.27]` | Retain |
| **C47** | Sec. 6.1 | Post-hoc cluster bootstrap follow-ups CI: `[+0.00, +1.76]` | REPLAY | Post-hoc analysis (`cluster_bootstrap.json`) | `results/post_hoc/cluster_bootstrap.json` | Recompute 8-cluster bootstrap CI | **REPRODUCED** | `[+0.00, +1.76]` | Retain |
| **C48** | Sec. 6.1 | Follow-up increase cluster count: only 1 of the 8 clusters | REPLAY | Post-hoc analysis (`cluster_bootstrap.json`) | `results/post_hoc/cluster_bootstrap.json` | Count clusters showing increase | **REPRODUCED** | 1 of 8 clusters | Retain |
| **C49** | Sec. 6.1 | LOCO drop k=1 mean level changes delta: -3.76 | REPLAY | Leave-one-cluster-out (`leave_one_cluster_out.json`) | `results/post_hoc/leave_one_cluster_out.json` | Recompute LOCO excluding k=1 | **REPRODUCED** | Mean: -3.76 | Retain |
| **C50** | Sec. 6.1 | LOCO drop k=1 CI: `[-4.81, -2.78]` | REPLAY | Leave-one-cluster-out (`leave_one_cluster_out.json`) | `results/post_hoc/leave_one_cluster_out.json` | Recompute LOCO excluding k=1 | **REPRODUCED** | `[-4.81, -2.78]` | Retain |
| **C51** | Sec. 6.1 | LOCO agreement stability: excludes zero in all 8 drops | REPLAY | Leave-one-cluster-out (`leave_one_cluster_out.json`) | `results/post_hoc/leave_one_cluster_out.json` | Verify all 8 drop intervals | **REPRODUCED** | 8 of 8 exclude zero | Retain |
| **C52** | Sec. 6.1 | Total Strategy proposals emitted: 3,814 proposals | REPLAY | Post-hoc analysis (`strategy_confidence_distribution.json`) | `results/post_hoc/strategy_confidence_distribution.json` | Sum proposal counts | **REPRODUCED** | Exactly 3,814 | Retain |
| **C53** | Sec. 6.1 | Strategy remediate (conf 0.80) count: 1,300 | REPLAY | Post-hoc analysis (`strategy_confidence_distribution.json`) | `results/post_hoc/strategy_confidence_distribution.json` | Extract remediate count | **REPRODUCED** | Exactly 1,300 | Retain |
| **C54** | Sec. 6.1 | Strategy recover (conf 0.80) count: 928 | REPLAY | Post-hoc analysis (`strategy_confidence_distribution.json`) | `results/post_hoc/strategy_confidence_distribution.json` | Extract recover 0.80 count | **REPRODUCED** | Exactly 928 | Retain |
| **C55** | Sec. 6.1 | Strategy recover (conf 0.70) count: 312 | REPLAY | Post-hoc analysis (`strategy_confidence_distribution.json`) | `results/post_hoc/strategy_confidence_distribution.json` | Extract recover 0.70 count | **REPRODUCED** | Exactly 312 | Retain |
| **C56** | Sec. 6.1 | Strategy steady (conf 0.45) count: 1,274 | REPLAY | Post-hoc analysis (`strategy_confidence_distribution.json`) | `results/post_hoc/strategy_confidence_distribution.json` | Extract steady count | **REPRODUCED** | Exactly 1,274 | Retain |
| **C57** | Sec. 6.1 | Strategy stretch proposals count: 0 (unexercised) | REPLAY | Post-hoc analysis (`strategy_confidence_distribution.json`) | `results/post_hoc/strategy_confidence_distribution.json` | Check stretch proposals | **REPRODUCED** | Exactly 0 | Retain |
| **C58** | Sec. 6.1 | Level changes decrease by answer set: decreased in 7 of 8 sets | REPLAY | Post-hoc cluster breakdown | `results/post_hoc/leave_one_cluster_out.json` | Count clusters with decrease | **REPRODUCED** | 7 of 8 sets | Retain |
| **C59** | Sec. 4, Sec. 7 | Guardrail grid disagreement points: 4,728 of 39,930 | SYNTHETIC | Code execution (`InterviewOrchestrator` vs `apply_canonical_guardrails`) | Enforcing code | Full 39,930 parametric grid sweep | **REPRODUCED** | Exactly 4,728 points | Retain |
| **C60** | Sec. 4, Sec. 7 | Guardrail grid disagreement percentage: 11.8% | SYNTHETIC | Code execution | Enforcing code | Recompute percentage | **REPRODUCED** | Exactly 11.84% | Retain |
| **C61–C69** | Tables 3–8 | Table cell alignment, sample counts, and exact p-values | VARIOUS | Raw result logs | `results/` | Automated assertion matching in `verify_paper.py` | **REPRODUCED** | 100% matched | Retain |

---

## 3. Code-to-Manuscript Architectural Verification

Every architectural claim was inspected against the active Python codebase in `agents/multiagent/` and `agents/orchestrator/`:

1. **Sole State Writer Invariant:**
   - *Claim:* Only the `InterviewOrchestrator` hub writes session state; agents possess zero state-write privileges.
   - *Code Evidence:* In `agents/multiagent/authority.py`, the permission matrix explicitly forbids keys: `score`, `transcript`, `history`, `session_id`, `state_version`, `evaluator_results`. The coordinator validates that agent proposals contain only `difficulty_action`, `probe_request`, or `coaching_plan`.
2. **Schema & Authority Separation:**
   - *Code Evidence:* `agents/multiagent/coordinator.py` scans proposals recursively for forbidden keys before Pydantic schema validation. In Experiment XB, 152 forbidden key injections were classified as `authority_violation` with enforcement enabled, and cascaded to `schema_violation` when the authority check was ablated.
3. **Optimistic Concurrency & State Versioning:**
   - *Code Evidence:* `TurnObservation` carries `state_version`. If an agent proposal returns with a stale version, `agents/multiagent/coordinator.py` rejects it with reason code `stale_state`.
4. **Deterministic Precedence & Arbitration:**
   - *Code Evidence:* In `agents/orchestrator/interview_orchestrator.py`, the turn flow strictly executes: (1) Hard infrastructure bounds $\rightarrow$ (2) Arbitrated proposal if confidence $\ge \tau$ and cited evidence $\ge 1$ $\rightarrow$ (3) Frozen PPO action $\rightarrow$ (4) Guardrail rule overrides (G1–G6).
5. **State Snapshot & Recovery:**
   - *Code Evidence:* Commit `1ac4555` introduced multi-agent telemetry persistence via nullable `session_snapshots.multiagent_json`, ensuring that upon server restart, weakness ledgers and decision counts are restored.
