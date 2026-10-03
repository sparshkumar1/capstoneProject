# Audit Deliverable 04: Statistical Validity and Uncertainty Audit
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `AUDIT_04_STATISTICAL_VALIDITY.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Independent Scientific, Reproducibility, and Publication-Quality Reviewer  

---

## 1. Experimental Unit & Pseudoreplication Analysis

A critical statistical finding in this audit concerns the true degrees of freedom in the experimental design:

- **Nominal Sample Count:** 160 replay sessions per experimental condition (e.g., 1,920 total sessions across 12 conditions in Experiment XA).
- **Underlying Data Units:** **Only 64 pre-recorded candidate answer payloads grouped into 8 computer science topic clusters ($N_c = 8$).**
- **Replay Structure:** Each cluster was replayed across 20 distinct question permutation orderings (random seeds 42–61).
- **Pseudoreplication Hazard:**
  - If a statistical analysis treats each of the 160 sessions as independent observations ($N = 160$), the standard error is artificially compressed by a factor of $\approx \sqrt{20} \approx 4.47$.
  - Under naive session-level bootstrapping, the 95% confidence interval for level change reduction is $[-3.19, -2.13]$, creating an illusion of tight, unmistakable significance.
- **Cluster-Aware Correction (Field & Welsh, 2007):**
  - Resampling must occur at the cluster level ($N_c = 8$) rather than the session level.
  - Under 10,000 cluster-bootstrap resamples, the true 95% confidence interval for level changes widens to **$[-4.50, -0.24]$**, and reversals widen to **$[-3.12, -0.27]$**.
  - While both intervals exclude zero, they demonstrate that statistical generalizability is tightly bound to candidate response distribution across the 8 clusters.

---

## 2. Cluster $k=1$ Dominance & Outlier Sensitivity

Inspection of raw cluster metrics in `research/multiagent/results/post_hoc/leave_one_cluster_out.json` reveals extreme cluster dependency:

| Cluster Index ($k$) | Domain / Topic Area | Level Change Delta ($M_1 - B_0$) | Reversal Delta ($M_1 - B_0$) | Probe Turns Delta ($M_1 - B_0$) |
|:---:|:---|:---:|:---:|:---:|
| 0 | Dynamic Programming | $-2.55$ | $-1.80$ | $+0.00$ |
| **1** | **Trees & Graph Traversals** | **$+4.95$** | **$+1.90$** | **$+4.75$** |
| 2 | Sorting & Searching | $-4.05$ | $-3.10$ | $+0.00$ |
| 3 | System Design / Caching | $-5.20$ | $-3.85$ | $+0.00$ |
| 4 | Databases & SQL | $-2.40$ | $-1.65$ | $+0.00$ |
| 5 | Concurrency & Locks | $-2.85$ | $-2.15$ | $+0.00$ |
| 6 | Networking & Protocols | $-3.20$ | $-2.45$ | $+0.00$ |
| 7 | Object-Oriented Design | $-1.05$ | $-0.90$ | $+0.00$ |

### Critical Auditor Findings:
1. **Probe Turn Concentration:** In 7 of the 8 clusters (Clusters 0, 2, 3, 4, 5, 6, 7), the Strategy Agent added **exactly $0.00$ proactive probe turns**. All probe turn gains ($+0.59$ session average) occurred **exclusively in Cluster $k=1$ ($+4.75$ turns)**.
2. **Directional Inversion:** In Cluster $k=1$, the multi-agent system *increased* level changes by $+4.95$ (due to repeated remediate transitions following probed gap failures), whereas in all other 7 clusters it *reduced* level changes.
3. **Leave-One-Cluster-Out (LOCO) Sensitivity:**
   - **Omitting Cluster 1:** Level change reduction intensifies from $-2.67$ to **$-3.76$** (cluster CI $[-4.81, -2.78]$), and probe turns drop to **$0.00$** ($[0.0, 0.0]$).
   - **Omitting Cluster 2 or 3:** The cluster bootstrap confidence interval crosses zero (e.g., $[-4.54, +0.27]$), demonstrating that the statistical significance of trajectory smoothing depends on the inclusion of specific high-variance clusters.

---

## 3. Pre-Registered Predictions Audit (Table 4)

Ten formal pre-registered predictions (A1–A10) were evaluated:

| ID | Hypothesis / Prediction | Target Metric | Pre-registered Threshold | Observed Value | Empirical Outcome |
|:---:|:---|:---:|:---:|:---:|:---:|
| **A1** | Coordination alters trajectories | Sessions altered | $\ge 90\%$ | $100.0\%$ (160/160) | **CONFIRMED** |
| **A2** | Level changes reduce | $\Delta$ Level Changes | $< 0$ | $-2.67$ | **CONFIRMED** |
| **A3** | Reversals reduce | $\Delta$ Reversals | $< 0$ | $-1.88$ | **CONFIRMED** |
| **A4** | PPO agreement decreases | PPO Agreement | $< 0.85$ | $0.774$ | **CONFIRMED** |
| **A5** | Proactive probes increase | $\Delta$ Probe Turns | $> 0$ | $+0.59$ | **CONFIRMED (Cluster 1 only)** |
| **A6** | Weakness ledger adds probes | $M_1 - M_2$ Probes | $> 0$ | $+0.59$ vs $0.00$ | **CONFIRMED** |
| **A7** | Coaching ablation invariant | $M_1 \text{ vs } M_3$ Path | $100\%$ identical | $100.0\%$ (160/160) | **CONFIRMED** |
| **A8** | Dispatch overhead within bound | $\Delta t$ Latency | $< 2.0$\,ms | $+1.04$\,ms | **CONFIRMED** |
| **A9** | Disabling PPO alters trajectory | Sessions altered ($M_7$) | $\ge 50\%$ | **$2.5\%$ (4/160)** | **CONTRADICTED** |
| **A10** | Canonical guardrail alters path | Sessions altered ($B_{0c}$) | $\ge 5\%$ | **$0.0\%$ (0/160)** | **CONTRADICTED** |

### Auditor Assessment on Contradicted Predictions:
- The manuscript correctly and transparently reports the failure of Predictions A9 and A10.
- A9 failed because Strategy heuristics and baseline rule fallbacks strongly align when candidate performance is mediocre.
- A10 failed because neutral audio feature defaults in mock replay payloads never triggered the acoustic guardrail divergence points.
