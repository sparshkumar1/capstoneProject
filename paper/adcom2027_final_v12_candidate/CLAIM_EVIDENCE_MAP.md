# Comprehensive Claim-to-Evidence Traceability Map
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `CLAIM_EVIDENCE_MAP.md`  
**Candidate Directory:** `paper/adcom2027_final_v12_candidate/`  
**Date:** 3 October 2026  
**Status:** 100% Verified against Raw Execution Artifacts and Codebase Implementation

---

## 1. Evidence Classification
- **REPLAY:** 64 pre-recorded production-evaluator payloads executed deterministically through the real orchestrator hub under `EVALUATOR_MOCK_MODE=1` across 20 question orders (seeds 42–61).
- **SYNTHETIC:** Mathematical state-space grid evaluations (e.g., 39,930-point guardrail grid recomputation).
- **ANALYTICAL / CODE AUDIT:** Formal proofs, architectural contracts, and deterministic execution equivalence.
- **EXCLUDED / NOT CLAIMED:** Live LLM generation, human learning efficacy, student interview placement.

---

## 2. Traceability Map (All 43 Quantitative Claims)

| Claim # | Manuscript Location | Core Claim / Value | Implementation Seam | Experiment / Evidence Class | Source Artifact | Verification Script | Statistical Method | Status |
|:---:|:---|:---|:---|:---:|:---|:---|:---:|:---:|
| **1** | Sec. 6.1, Table 1 | Baseline $B_0$ mean level changes: **15.12** | `InterviewOrchestrator._apply_guardrails` | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Mean | **VERIFIED** |
| **2** | Sec. 6.1, Table 1 | Multi-agent $M_1$ mean level changes: **12.45** | `MultiAgentCoordinator.decide_difficulty` | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Mean | **VERIFIED** |
| **3** | Sec. 6.1, Table 1 | Baseline $B_0$ mean reversals: **11.74** | `InterviewOrchestrator` | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Mean | **VERIFIED** |
| **4** | Sec. 6.1, Table 1 | Multi-agent $M_1$ mean reversals: **9.87** | `MultiAgentCoordinator` | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Mean | **VERIFIED** |
| **5** | Sec. 6.1, Table 1 | Baseline $B_0$ PPO agreement fraction: **1.000** | PPO policy wrapper | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Fraction | **VERIFIED** |
| **6** | Sec. 6.1, Table 1 | Multi-agent $M_1$ PPO agreement fraction: **0.774** | `arbitration.py` | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Fraction | **VERIFIED** |
| **7** | Sec. 6.1, Table 2 | Level changes delta: **$-2.67$**, naive 95% CI **$[-3.19, -2.13]$** | Paired session difference | XA, REPLAY | `results/xa/xa_paired.csv` | `verify_paper.py` | Paired Bootstrap | **VERIFIED** |
| **8** | Sec. 6.1, Table 2 | Reversals delta: **$-1.88$**, naive 95% CI **$[-2.28, -1.46]$** | Paired session difference | XA, REPLAY | `results/xa/xa_paired.csv` | `verify_paper.py` | Paired Bootstrap | **VERIFIED** |
| **9** | Sec. 6.1, Table 2 | Extra probe turns delta: **$+0.59$**, naive 95% CI **$[+0.34, +0.85]$** | `strategy_agent.py` | XA, REPLAY | `results/xa/xa_paired.csv` | `verify_paper.py` | Paired Bootstrap | **VERIFIED** |
| **10** | Sec. 6.1, Table 2 | Turn latency median delta: **$[+1.00, +1.08]$\,ms** | `runtime.py` dispatch | XA, REPLAY | `results/xa/xa_paired.csv` | `verify_paper.py` | Paired Bootstrap | **VERIFIED** |
| **11** | Sec. 6.1, Par. 5 | Mean agent invocations per session: **47.7** | `coordinator.py` | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Mean | **VERIFIED** |
| **12** | Sec. 6.1, Par. 2 | Mean decisions where Strategy supersedes PPO: **11.9** | `arbitration.py` | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Mean | **VERIFIED** |
| **13** | Sec. 6.1, Par. 5 | Baseline $B_0$ pooled median turn latency: **0.546\,ms** | Core hub turn loop | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Quantile (p50) | **VERIFIED** |
| **14** | Sec. 6.1, Par. 5 | Multi-agent $M_1$ pooled median turn latency: **1.589\,ms** | Core hub + Coordinator | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Quantile (p50) | **VERIFIED** |
| **15** | Sec. 6.1, Par. 5 | Multi-agent $M_1$ pooled 95th pct latency: **4.411\,ms** | Core hub + Coordinator | XA, REPLAY | `results/xa/xa_summary.csv` | `verify_paper.py` | Quantile (p95) | **VERIFIED** |
| **16** | Sec. 6.1, Par. 2 | Trajectory path divergence ($M_1$ vs $B_0$): **all 160 sessions** | Path comparator | XA, REPLAY | `results/xa/xa_runs.jsonl` | `verify_paper.py` | Count | **VERIFIED** |
| **17** | Sec. 6.1, Par. 1 | Exact 95% Clopper-Pearson lower bound for 160/160: **0.977** | Binomial lower bound | XA, REPLAY | `results/xa/xa_runs.jsonl` | `verify_paper.py` | Clopper-Pearson | **VERIFIED** |
| **18** | Sec. 6.1, Par. 3 | Level changes cluster bootstrap 95% CI: **$[-4.50, -0.24]$** | Field & Welsh (2007) cluster boot | XA, REPLAY | `results/post_hoc/cluster_bootstrap.json` | `verify_paper.py` | Cluster Bootstrap | **VERIFIED** |
| **19** | Sec. 6.1, Par. 3 | Reversals cluster bootstrap 95% CI: **$[-3.12, -0.27]$** | Field & Welsh (2007) cluster boot | XA, REPLAY | `results/post_hoc/cluster_bootstrap.json` | `verify_paper.py` | Cluster Bootstrap | **VERIFIED** |
| **20** | Sec. 6.1, Par. 3 | PPO agreement cluster bootstrap 95% CI: **$[-0.284, -0.170]$** | Field & Welsh (2007) cluster boot | XA, REPLAY | `results/post_hoc/cluster_bootstrap.json` | `verify_paper.py` | Cluster Bootstrap | **VERIFIED** |
| **21** | Sec. 6.1, Par. 3 | Extra turns cluster bootstrap 95% CI: **$[0.00, +1.76]$** | Field & Welsh (2007) cluster boot | XA, REPLAY | `results/post_hoc/cluster_bootstrap.json` | `verify_paper.py` | Cluster Bootstrap | **VERIFIED** |
| **22** | Sec. 6.1, Par. 3 | Clusters showing proactive probe turn increase: **only 1 of the 8 ($k=1$)** | Per-cluster probe audit | XA, REPLAY | `results/post_hoc/cluster_bootstrap.json` | `verify_paper.py` | Cluster Count | **VERIFIED** |
| **23** | Sec. 6.1, Par. 3 | LOCO jackknife omitting cluster 1 mean: **$-3.76$** | 8-way jackknife LOCO | XA, REPLAY | `results/post_hoc/leave_one_cluster_out.json` | `verify_paper.py` | Jackknife LOCO | **VERIFIED** |
| **24** | Sec. 6.1, Par. 3 | LOCO jackknife omitting cluster 1 95% CI: **$[-4.81, -2.78]$** | 8-way jackknife LOCO | XA, REPLAY | `results/post_hoc/leave_one_cluster_out.json` | `verify_paper.py` | Jackknife LOCO | **VERIFIED** |
| **25** | Sec. 6.1, Par. 3 | PPO agreement excludes zero under all 8 jackknife drops: **True** | 8-way jackknife LOCO | XA, REPLAY | `results/post_hoc/leave_one_cluster_out.json` | `verify_paper.py` | Jackknife LOCO | **VERIFIED** |
| **26** | Sec. 6.1, Par. 3 | Oscillation reduction sign consistent across clusters: **7 of the 8** | Cluster sign count | XA, REPLAY | `results/post_hoc/leave_one_cluster_out.json` | `verify_paper.py` | Cluster Count | **VERIFIED** |
| **27** | Sec. 6.1, Par. 4 | Total Strategy Agent proposals emitted: **3,814** | `strategy_agent.py` | XA, REPLAY | `results/post_hoc/strategy_confidence_dist.json` | `verify_paper.py` | Count | **VERIFIED** |
| **28** | Sec. 6.1, Par. 4 | Strategy proposals `remediate` (conf 0.80): **1,300** | `strategy_agent.py` | XA, REPLAY | `results/post_hoc/strategy_confidence_dist.json` | `verify_paper.py` | Count | **VERIFIED** |
| **29** | Sec. 6.1, Par. 4 | Strategy proposals `recover` (conf 0.80): **928** | `strategy_agent.py` | XA, REPLAY | `results/post_hoc/strategy_confidence_dist.json` | `verify_paper.py` | Count | **VERIFIED** |
| **30** | Sec. 6.1, Par. 4 | Strategy proposals `recover` (conf 0.70): **312** | `strategy_agent.py` | XA, REPLAY | `results/post_hoc/strategy_confidence_dist.json` | `verify_paper.py` | Count | **VERIFIED** |
| **31** | Sec. 6.1, Par. 4 | Strategy proposals `steady` (conf 0.45): **1,274** | `strategy_agent.py` | XA, REPLAY | `results/post_hoc/strategy_confidence_dist.json` | `verify_paper.py` | Count | **VERIFIED** |
| **32** | Sec. 6.1, Par. 4 | Strategy proposals `stretch`: **0** | `strategy_agent.py` | XA, REPLAY | `results/post_hoc/strategy_confidence_dist.json` | `verify_paper.py` | Count | **VERIFIED** |
| **33** | Sec. 6.2, Par. 2 | XC threshold $\tau = 0.0$ mean level changes: **2.225** | `arbitration.py` sweep | XC, REPLAY | `results/xc/xc_summary.csv` | `verify_paper.py` | Mean | **VERIFIED** |
| **34** | Sec. 6.2, Par. 2 | XC threshold $\tau = 0.0$ PPO agreement fraction: **0.014** | `arbitration.py` sweep | XC, REPLAY | `results/xc/xc_summary.csv` | `verify_paper.py` | Fraction | **VERIFIED** |
| **35** | Sec. 6.2, Par. 2 | All registered XC predictions supported: **All 5 registered XC** | Pre-registered hypotheses | XC, REPLAY | `results/xc/xc_predictions.csv` | `verify_paper.py` | Prediction Check | **VERIFIED** |
| **36** | Sec. 6.2, Par. 4 | Contradicted A9 (PPO ablated $M_7$ vs $B_7$): **4 of 160 sessions (2.5%)** | Pre-registered hypothesis | XA, REPLAY | `results/xa/xa_predictions.csv` | `verify_paper.py` | Count | **VERIFIED** |
| **37** | Sec. 6.2, Par. 5 | Contradicted A10 (Canonical guardrails $B_{0c}$ vs $B_0$): **0 of 160 sessions (0.0%)** | Pre-registered hypothesis | XA, REPLAY | `results/xa/xa_predictions.csv` | `verify_paper.py` | Count | **VERIFIED** |
| **38** | Sec. 6.2, Par. 5 | Guardrail grid disagreement points: **4,728 of 39,930** | `rl/guardrails.py` vs inline | SYNTHETIC | `tests/unit/test_guardrail_impl.py` | `verify_paper.py` | Grid Recomputation | **VERIFIED** |
| **39** | Sec. 6.2, Par. 5 | Guardrail grid disagreement percentage: **11.8%** | `rl/guardrails.py` vs inline | SYNTHETIC | `tests/unit/test_guardrail_impl.py` | `verify_paper.py` | Grid Recomputation | **VERIFIED** |
| **40** | Sec. 6.3, Par. 1 | Coaching ablated ($M_3$) difficulty trajectory identical: **160 of 160 sessions** | Ablation run comparator | XA, REPLAY | `results/xa/xa_runs.jsonl` | `verify_paper.py` | Count | **VERIFIED** |
| **41** | Sec. 6.3, Par. 2 | Decision equivalence under deterministic rules: **$\mathbb{P}(\text{agree}) = 1.0$** | Decision logic analysis | ANALYTICAL | Formal Equivalence | `verify_paper.py` | Probability | **VERIFIED** |
| **42** | Sec. 6.3, Par. 3 | Specialized architecture per-turn latency overhead: **$+1.04$\,ms** | `runtime.py` benchmark | XA, REPLAY | `results/xa/xa_paired.csv` | `verify_paper.py` | Median Delta | **VERIFIED** |
| **43** | Sec. 8, Par. 7 | Test suite regression status: **421 passed**, **59 pre-existing/env failures** | Test runner output | REPO AUDIT | `pytest tests/` execution | `verify_paper.py` | Test Count | **VERIFIED** |
