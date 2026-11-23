# Audit Deliverable 02: Evidence and Claim Ledger
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `AUDIT_02_EVIDENCE_AND_CLAIM_LEDGER.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Independent Scientific, Reproducibility, and Publication-Quality Reviewer  

---

## 1. Classification Methodology & Status Definitions

Every major quantitative statement, point estimate, confidence interval, architectural claim, and qualitative interpretation in the v13 manuscript is audited below. Statuses are assigned based on empirical truth:

- **VERIFIED:** Statistically and quantitatively recomputed from raw artifact files and confirmed present in the compiled manuscript PDF.
- **REPRODUCED:** Independently rerun or re-executed via test scripts/verification seam with identical output.
- **PARTIALLY VERIFIED:** Supported by architectural invariants or proxy ablations, but missing direct end-to-end experimental execution (e.g., unified controller evaluated via $M_3$ trajectory invariance and proposal equivalence rather than a physical standalone class).
- **CONTRADICTED:** Pre-registered prediction refuted by the empirical data (documented transparently in the manuscript).
- **UNVERIFIED:** Claim lacks traceable experimental artifacts or cannot be reproduced from code.
- **NOT APPLICABLE (N/A):** Out-of-scope historical claim excised from camera-ready manuscript.

---

## 2. Comprehensive Evidence & Claim Ledger

### 2.1 Quantitative Trajectory & Coordination Claims (Experiment XA)

| # | Manuscript Claim / Value | Location in v13 | Source Artifact | Verification Method | Status | Auditor Scientific Assessment |
|:---:|:---|:---|:---|:---|:---:|:---|
| **C01** | Baseline $B_0$ mean level changes: $15.12$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Code verified; represents baseline oscillation frequency. |
| **C02** | Baseline $B_0$ mean reversals: $11.74$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Code verified; represents baseline difficulty direction reversals. |
| **C03** | Baseline $B_0$ PPO agreement: $1.000$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Tautological baseline identity ($\text{PPO agrees with PPO}$). |
| **C04** | Baseline $B_0$ probe turns: $0.00$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Baseline has no Strategy Agent weakness ledger. |
| **C05** | Baseline $B_0$ median latency: $0.546$\,ms | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Pure hub dispatch latency without multi-agent validation. |
| **C06** | Full $M_1$ mean level changes: $12.45$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Reduced level changes under stateful Strategy Agent. |
| **C07** | Full $M_1$ mean reversals: $9.87$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Reduced reversals under stateful Strategy Agent. |
| **C08** | Full $M_1$ PPO agreement: $0.774$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Strategy Agent overrides PPO when confidence $\ge 0.6$. |
| **C09** | Full $M_1$ probe turns: $+0.59$ | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Driven entirely by Cluster 1 (+4.75); clusters 0, 2–7 show 0.00. |
| **C10** | Full $M_1$ median latency: $1.589$\,ms | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Two-agent dispatch + schema validation overhead. |
| **C11** | Full $M_1$ agent calls: $47.7$ / session | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Strategy + Coaching called once per turn. |
| **C12** | Full $M_1$ supersessions: $11.9$ / session | Sec 6, Tab 2 | `xa_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Number of turns where Strategy supersedes PPO baseline. |
| **C13** | Paired $\Delta$ Level Changes: $-2.67$ | Sec 6, Tab 3 | `xa_paired.csv` | Paired difference $M_1 - B_0$ | **VERIFIED** | Trajectory smoothing; negative in 7 of 8 clusters. |
| **C14** | Naive 95% CI Level Changes: $[-3.19, -2.13]$ | Sec 6, Tab 3 | `xa_paired.csv` | Student-$t$ across 160 runs | **VERIFIED** | Pseudoreplicated CI; understates cluster uncertainty. |
| **C15** | Cluster 95% CI Level Changes: $[-4.50, -0.24]$ | Sec 6, Tab 3 | `cluster_bootstrap.json` | Field & Welsh 10k cluster bootstrap | **VERIFIED** | Cluster-aware uncertainty respecting 8-cluster design. |
| **C16** | Paired $\Delta$ Reversals: $-1.88$ | Sec 6, Tab 3 | `xa_paired.csv` | Paired difference $M_1 - B_0$ | **VERIFIED** | Directional reversal reduction; negative in 7 of 8 clusters. |
| **C17** | Naive 95% CI Reversals: $[-2.28, -1.46]$ | Sec 6, Tab 3 | `xa_paired.csv` | Student-$t$ across 160 runs | **VERIFIED** | Pseudoreplicated CI. |
| **C18** | Cluster 95% CI Reversals: $[-3.12, -0.27]$ | Sec 6, Tab 3 | `cluster_bootstrap.json` | Field & Welsh 10k cluster bootstrap | **VERIFIED** | Statistically significant at cluster level. |
| **C19** | Paired $\Delta$ PPO Agreement: $-0.226$ | Sec 6, Tab 3 | `xa_paired.csv` | Paired difference $M_1 - B_0$ | **VERIFIED** | Drop in PPO adherence due to multi-turn strategy overrides. |
| **C20** | Cluster 95% CI PPO Agreement: $[-0.284, -0.170]$ | Sec 6, Tab 3 | `cluster_bootstrap.json` | Field & Welsh 10k cluster bootstrap | **VERIFIED** | Negative across all 8 clusters. |
| **C21** | Paired $\Delta$ Probe Turns: $+0.59$ | Sec 6, Tab 3 | `xa_paired.csv` | Paired difference $M_1 - B_0$ | **VERIFIED** | Proactive probes added by Strategy Agent. |
| **C22** | Cluster 95% CI Probe Turns: $[0.00, +1.76]$ | Sec 6, Tab 3 | `cluster_bootstrap.json` | Field & Welsh 10k cluster bootstrap | **VERIFIED** | Lower bound touches 0.00 due to cluster 1 concentration. |
| **C23** | Latency Delta: $+1.04$\,ms ($[+1.00, +1.08]$\,ms) | Sec 6, Tab 3 | `xa_paired.csv` | Median paired difference | **VERIFIED** | Pure software contract serialization overhead. |
| **C24** | 100% of Replay Trajectories Altered (160/160) | Sec 6.1 | `xa_runs.jsonl` | Session trajectory comparison | **VERIFIED** | Every single session differs from baseline under M1. |
| **C25** | Cluster $k=1$ Probes: $+4.75$ turns | Sec 6.1 | `leave_one_cluster_out.json` | Cluster breakdown | **VERIFIED** | Probes concentrate 100% in cluster 1; 0 in clusters 0, 2–7. |
| **C26** | LOCO Shift Omitting Cluster 1: $-3.76$ | Sec 6.1 | `leave_one_cluster_out.json` | Jackknife LOCO analysis | **VERIFIED** | Omitting cluster 1 intensifies level change reduction. |
| **C27** | LOCO CI Omitting Cluster 1: $[-4.81, -2.78]$ | Sec 6.1 | `leave_one_cluster_out.json` | Jackknife LOCO analysis | **VERIFIED** | Confirms high sensitivity to cluster selection. |

---

### 2.2 Specialization & Ablation Claims (RQ2)

| # | Manuscript Claim / Value | Location in v13 | Source Artifact | Verification Method | Status | Auditor Scientific Assessment |
|:---:|:---|:---|:---|:---|:---:|:---|
| **C28** | Condition $M_3$ (No Coaching) $\equiv M_1$ Trajectories (160/160) | Sec 6.3 | `xa_runs.jsonl` | Compare $M_3$ vs $M_1$ difficulty paths | **VERIFIED** | Identical difficulty paths in 100% of replay sessions. |
| **C29** | Decision Equivalence: $\mathbb{P}(\text{agree}) = 1.0$ | Sec 6.3, Tab 6 | Metamorphic test suite | `test_specialization_comparison.py` | **REPRODUCED** | Deterministic single controller produces identical proposals. |
| **C30** | Specialization Provides Zero Algorithmic Advantage | Sec 6.3, Sec 7 | Empirical & theoretical analysis | Contrast $M_1, M_3, M_{\text{unified}}$ | **VERIFIED** | Honest scientific finding: specialization does not improve decisions. |
| **C31** | Bulkhead Fault Containment in Split Architecture | Sec 6.3, Tab 6 | Architectural contract isolation | Unit test validation | **VERIFIED** | Architectural property: coaching exception does not drop strategy. |
| **C32** | Standalone `UnifiedCoachAgent` Execution | Sec 5.3, Tab 6 | Pre-registered in `MERGED_AGENT_EXPERIMENT.md` | Codebase inspection | **PARTIALLY VERIFIED** | Evaluated via proxy $M_3$ ablation and test suite; no standalone class. |
| **C33** | Subjective LLM Coaching Quality Unresolved | Sec 6.3, Sec 8 | Replay protocol analysis | Evaluator mock inspection | **VERIFIED** | Properly disclosed: no live generative LLM ran in replay. |

---

### 2.3 Coordination Mechanisms & Threshold Sensitivity (Experiment XC)

| # | Manuscript Claim / Value | Location in v13 | Source Artifact | Verification Method | Status | Auditor Scientific Assessment |
|:---:|:---|:---|:---|:---|:---:|:---|
| **C34** | Threshold $\tau=0.0$: $2.225$ changes, $0.014$ agr | Sec 6.2, Tab 5 | `xc_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Replicates unarbitrated collapse without threshold gating. |
| **C35** | Threshold Gating Prevents Collapse with 0% Guardrail Bypass | Sec 6.2 | `xc_runs.jsonl` | Guardrail bypass count | **VERIFIED** | Inline guardrail active even at $\tau=0.0$. |
| **C36** | Invariance Plateau Across $\tau \in [0.5, 0.8]$ ($12.450$ changes) | Sec 6.2, Tab 5 | `xc_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Arises from discrete heuristic confidence steps ($0.45, 0.70, 0.85$). |
| **C37** | Threshold $\tau=0.9$: $15.119$ changes, $0.626$ agr | Sec 6.2, Tab 5 | `xc_summary.csv` | Recomputed from 160 runs | **VERIFIED** | Silences Strategy Agent completely; falls back to PPO/rules. |
| **C38** | Prediction A9 Refuted: $M_7$ Alters 4/160 (2.5%) Sessions | Sec 6.2, Tab 4 | `xa_predictions.csv` | Prediction verification | **CONTRADICTED** | Refuted pre-registered prediction of $\ge 50\%$ divergence. |
| **C39** | Prediction A10 Refuted: $B_{0c}$ Alters 0/160 (0.0%) Sessions | Sec 6.2, Tab 4 | `xa_predictions.csv` | Prediction verification | **CONTRADICTED** | Neutral acoustic defaults left 11.8% grid divergence unexercised. |
| **C40** | Inline vs Canonical Disagreement: 4,728 / 39,930 ($11.8\%$) | Sec 5.2, Sec 8 | `test_guardrail_impl.py` | Full grid evaluation | **REPRODUCED** | Grid pins exact disagreement; unexercised by neutral replay. |

---

### 2.4 Critical Qualitative & Interpretive Claims

| # | Qualitative Manuscript Claim | Location | Scientific Status | Auditor Scientific Assessment |
|:---:|:---|:---:|:---:|:---|
| **Q01** | Trajectory smoothing does not establish student learning gains | Abstract, Sec 7 | **VERIFIED** | Properly caveats that variance reduction $\neq$ educational efficacy. |
| **Q02** | Reduced PPO agreement does not establish policy superiority | Sec 7 | **VERIFIED** | Properly clarifies that heuristic override $\neq$ reinforcement learning optimality. |
| **Q03** | Proactive probes do not establish pedagogical efficacy | Sec 7, Sec 8 | **VERIFIED** | Properly notes probing is an architectural mechanism, not verified pedagogy. |
| **Q04** | No live language models or human candidates participated in replay | Sec 5.1, Sec 8 | **VERIFIED** | Accurately describes replay benchmark conditions (`EVALUATOR_MOCK_MODE=1`). |
| **Q05** | Shared 64-answer dataset provenance creates cross-venue overlap risk | Sec 5.1, Sec 8 | **DOCUMENTED** | Fully detailed in `DATASET_AND_OVERLAP_AUDIT.md`; held for advisor approval. |
