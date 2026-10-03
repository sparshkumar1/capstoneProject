# Executive Handover Dossier for Teacher Review
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `FINAL_HANDOVER.md`  
**Candidate Directory:** `paper/adcom2027_final_v12_candidate/`  
**Date:** 3 October 2026  
**Target Milestone:** Faculty Advisor / Teacher Review (5 October 2026)  
**Final Conference Deadline:** 15 October 2026  
**Candidate Classification:** **AUTHOR-REVIEW CANDIDATE / CONDITIONALLY READY FOR SUBMISSION**

---

## 1. Executive Summary and Strategic Refocus

This handover dossier delivers the complete research revision and manuscript finalization for PREPAIred targeting the **31st International Conference on Advanced Computing and Communications (ADCoM 2027)**, to be published in the Springer **Communications in Computer and Information Science (CCIS)** series.

In strict adherence to the project instructions, the research was refocused away from general fault tolerance and reliability benchmarks onto a singular, scientifically defensible narrative: **multi-agent coordination, agent specialization, and decision-making**.

> **Authoritative Manuscript:** [`paper/adcom2027_final_v12_candidate/ADCOM2027_PREPAIred_v12_specialization_blind.pdf`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/ADCOM2027_PREPAIred_v12_specialization_blind.pdf)  
> **Page Count:** Exactly 20 pages (maximum allowable Springer CCIS budget)  
> **Bibliography:** Exactly 20 verified reference entries in `splncs04` format  
> **Claim Verification:** **43 / 43 quantitative claims verified (100%)** via [`verification/verify_paper.py`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/verification/verify_paper.py)

---

## 2. Answers to Mandatory Evaluation Questions (A–H)

### A. What is the actual central scientific contribution?
The central contribution is an empirical and architectural investigation of whether decomposing pedagogical reasoning into specialized stateful agents with a coordination layer yields measurable behavioral, trajectory, or decision-making advantages over a single-controller baseline:
1. **Architecture:** A hub-orchestrated platform extended with two bounded-authority agents (Strategy Agent with weakness memory; Coaching Agent with coaching history) communicating via unidirectional peer messaging and governed by threshold-gated arbitration.
2. **Coordination Dynamics:** An empirical demonstration that stateful coordination alters difficulty trajectories in 100% of replay sessions, smoothing oscillations ($-2.67$ level changes, $-1.88$ reversals) while reducing uncoordinated PPO agreement ($1.000 \to 0.774$).
3. **The Limits of Specialization:** An architectural and empirical proof that under deterministic decision rules, agent specialization provides **zero trajectory optimization or decision-quality advantage** ($M_3 = M_1$, 160/160 identical sessions; $\mathbb{P}(\text{agree}) = 1.0$). The value of specialization is strictly architectural (software modularity, independent testing, and bulkhead fault containment), balanced against $+1.04$\,ms median per-turn dispatch overhead.

### B. Which findings demonstrate coordination-related behavioral differences?
- **Trajectory Divergence:** Full coordination ($M_1$) altered difficulty paths relative to baseline ($B_0$) in **all 160 replay sessions (100.0%)**.
- **Oscillation Reduction:** Mean level changes decreased from $15.12$ to $12.45$ ($-2.67$, cluster-bootstrap 95% CI $[-4.50, -0.24]$); directional reversals decreased from $11.74$ to $9.87$ ($-1.88$, cluster CI $[-3.12, -0.27]$). Both deltas are negative in 7 of 8 candidate clusters.
- **PPO Agreement Reduction:** PPO agreement dropped from $1.000$ to $0.774$ ($-0.226$, cluster CI $[-0.284, -0.170]$), with Strategy proposals superseding PPO before the guardrail layer in an average of $11.9$ decisions per session.
- **Proactive Probing:** Added $+0.59$ turns per session on average (cluster CI $[0.00, +1.76]$).
- **Threshold Gating:** Setting threshold $\tau = 0.0$ replicates the unarbitrated collapse ($2.225$ level changes, $0.014$ agreement), isolating the threshold as the primary coordination gate.

### C. Has the value of agent specialization been empirically established, or does it remain unresolved?
- **Established Empirically:** Specialization provides **zero algorithmic decision advantage** in deterministic settings. Ablating Coaching ($M_3$) produces difficulty trajectories 100% identical to the full two-agent system ($M_1$) in all 160 sessions. Under deterministic rules, a unified agent produces mathematically identical proposals ($\mathbb{P}(\text{agree}) = 1.0$). Specialization introduces a measurable runtime penalty ($+1.04$\,ms median latency per turn).
- **Established Architecturally:** Specialization provides bulkhead failure containment (a coaching exception does not drop strategy difficulty adaptation) and independent codebase modularity.
- **Unresolved:** Whether an LLM-backed specialized agent outperforms a unified LLM agent in subjective coaching quality remains an open, unresolved question because no live generative LLM ran in replay, and the physical merged-agent class experiment was pre-registered but unexecuted.

### D. Which results are independently reproducible?
All 43 quantitative claims in the revised manuscript are 100% independently reproducible from raw JSONL and CSV artifacts in `research/multiagent/results/`. Running `python verification/verify_paper.py` passes 43/43 checks in under 10 seconds.

### E. What are the most important threats to validity?
1. **The 8-Cluster Structure:** The 160 replay sessions reuse 8 recorded candidate answer sets across 20 question orders.
2. **Cluster $k=1$ Sensitivity:** Proactive probe turn gains ($+0.59$) are driven entirely by cluster $k=1$; in clusters 0 and 2--7, proactive probing added 0.00 turns.
3. **Absence of Live Human/LLM Interaction:** Replay uses pre-recorded evaluator scores (`EVALUATOR_MOCK_MODE=1`). No student learning, pedagogical efficacy, or LLM hallucination claims are made.
4. **Unexercised Acoustic Regions:** Neutral acoustic defaults in replay data prevented exercising the 11.8% divergent guardrail boundary and prevented Strategy Agent *stretch* proposals.

### F. Is the shared-dataset publication issue resolved?
**NOT YET RESOLVED (Action Required by Faculty Advisor on 5 October).**  
The 64 recorded evaluator payloads are shared with sibling papers (notably the teammate's concurrent v5 paper). [`DATASET_AND_OVERLAP_AUDIT.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/DATASET_AND_OVERLAP_AUDIT.md) outlines three clear options:
- **Option 1 (RECOMMENDED):** Deposit the 64-answer replay corpus to Zenodo as an independent benchmark artifact (*TIRC-64*) and cite it as an external stimulus set.
- **Option 2:** Provide a transparent disclosure in the CMT Chair Notes.
- **Option 3:** Generate a fresh independent synthetic dataset prior to camera-ready submission.

### G. Does the final manuscript satisfy the verified submission requirements?
**YES.**
- Format: Springer CCIS `llncs.cls` with `splncs04.bst`.
- Page Budget: **Exactly 20 pages** (References end on Page 20 at ~55% height).
- Double-Blind Review: **0 deanonymizing hits** via [`scripts/blind_audit.py`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/scripts/blind_audit.py).
- Font Embedding: **0 un-embedded fonts** across all 20 pages.
- Track Alignment: Directly targets ADCoM 2027 Track 2 (*Agent-Native Development and Lifecycle Engineering*).

### H. Which decisions still require the author's or advisor's approval?
1. **Shared Dataset Disclosure Decision:** Approve Option 1 (Zenodo benchmark deposit) or Option 2 (CMT chair note) in [`DATASET_AND_OVERLAP_AUDIT.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/DATASET_AND_OVERLAP_AUDIT.md).
2. **Page Sheet Geometry Verification:** Confirm whether the ADCoM CMT portal mandates ISO A4 (595 $\times$ 842 pt) or accepts US Letter (612 $\times$ 792 pt).
3. **Authorization for Submission:** Authorize final submission upload prior to the 15 October 2026 deadline.

---

## 3. Candidate Readiness Verdict

$$\mathbf{FINAL\;VERDICT:}\quad \textbf{AUTHOR-REVIEW CANDIDATE / CONDITIONALLY READY FOR SUBMISSION}$$

The manuscript is scientifically cohesive, typographically polished, and empirically verified. Submission to Microsoft CMT remains conditionally held pending the faculty advisor's decision on benchmark disclosure on **5 October 2026**.

---

## 4. Cryptographic Artifact Inventory

All assets are preserved in [`paper/adcom2027_final_v12_candidate/`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/):

| File Name | Description | Size (Bytes) | SHA-256 Checksum |
|:---|:---|:---:|:---|
| [`manuscript/main.pdf`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/manuscript/main.pdf) | Compiled 20-page camera-ready PDF | 515,536 | `925D88BD6D3EAF8C46DEB9BA949A7648BD6AA6F11261E852C8E2F7D5D0F08353` |
| [`ADCOM2027_PREPAIred_v12_specialization_blind.pdf`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/ADCOM2027_PREPAIred_v12_specialization_blind.pdf) | Authoritative blind candidate PDF | 515,536 | `925D88BD6D3EAF8C46DEB9BA949A7648BD6AA6F11261E852C8E2F7D5D0F08353` |
| [`EXPERIMENT_PLAN.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/EXPERIMENT_PLAN.md) | Revised methodology, RQs, and hypotheses | 9,629 | (Generated 2026-10-03) |
| [`EXPERIMENT_RESULTS.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/EXPERIMENT_RESULTS.md) | Verified tables, CIs, LOCO, and specialization | 10,166 | (Generated 2026-10-03) |
| [`CLAIM_AUDIT.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/CLAIM_AUDIT.md) | 43/43 quantitative claim traceability | 11,452 | (Generated 2026-10-03) |
| [`DATASET_AND_OVERLAP_AUDIT.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/DATASET_AND_OVERLAP_AUDIT.md) | 64-answer provenance & 3 resolution options | 9,287 | (Generated 2026-10-03) |
| [`REPRODUCIBILITY.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/REPRODUCIBILITY.md) | Reproduction commands and environment specs | 3,235 | (Generated 2026-10-03) |
| [`FINAL_COMPLIANCE_REPORT.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/FINAL_COMPLIANCE_REPORT.md) | CCIS layout, 20-page budget, and font audit | 6,471 | (Generated 2026-10-03) |
| [`REVISION_REPORT.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/REVISION_REPORT.md) | Structural, typographical, and scientific changelog | 9,090 | (Generated 2026-10-03) |
| [`FINAL_HANDOVER.md`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/FINAL_HANDOVER.md) | Executive briefing for teacher review | 11,432 | (Generated 2026-10-03) |
| [`verification/verify_paper.py`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/verification/verify_paper.py) | Automated 43-claim verification script | 6,659 | `F7DAED34719B5CF6D3C5F9AB0710F9BB43F44D8EDF7775D432D8595D13C76B74` |
| [`scripts/blind_audit.py`](file:///C:/Users/spars/Downloads/PrepAIred/paper/adcom2027_final_v12_candidate/scripts/blind_audit.py) | Double-blind scanning script | 2,684 | `3D7B4577A9A3269F13B17514D5FCF046CFDB81B0FF12CA91F1FB7F1984D3C6CD` |
