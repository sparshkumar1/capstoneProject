# Stage 19 — Final Peer-Review & Publication Readiness Audit

**Document ID:** `STAGE-19-PUB-AUDIT`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Traceability Reference:** [`docs/PAPER_RESULTS_TRACEABILITY.md`](PAPER_RESULTS_TRACEABILITY.md)
**Claims Matrix:** [`docs/CLAIMS_CHECK.md`](CLAIMS_CHECK.md)
**Audit Date:** 2026-08-16
**Audit Standard:** Strict Academic Peer-Review Readiness & Scientific Defensibility

---

## 1. Executive Summary & Audit Scope

This audit provides a rigorous, skeptical peer-review assessment of the PrepAIred scientific manuscript and research repository. The evaluation strictly assesses whether the paper's claims match the empirical boundaries established by the 480 pre-registered evaluation trials ($150 + 140 + 60 + 60 + 70 = 480$) and identifies potential vulnerabilities that reviewers in top-tier AI/EdTech venues (e.g., IEEE Transactions on Learning Technologies, AIED, EDM, ACM L@S) will target.

---

## 2. Part 1 — Determination of the Defensible Research Contribution

### 2.1 Comparative Analysis of Contribution Framings

| Framing Option | Description | Evidence Support Status | Scientific Defensibility |
|---|---|:---:|---|
| **A. Pure PPO / RL Novelty** | Claiming a fundamental algorithmic innovation in reinforcement learning. | **`REJECTED`** | Algorithmic formulation uses standard PPO with discrete action selection. Claiming RL novelty would trigger immediate rejection by ML reviewers. |
| **B. Personalization Learning Gains** | Claiming that personalization improves candidate interview success or learning retention. | **`REJECTED`** | Validation is currently based on synthetic candidate simulations (EXP-4) and deduplication metrics ($0.0\%$). No longitudinal human learning gain trials have been executed yet. |
| **C. Generic Multimodal Pipeline** | Claiming novelty purely through integrating WhisperX, SBERT, CrossEncoders, and Docker. | **`REJECTED`** | Merely gluing off-the-shelf libraries together constitutes standard software engineering, not a scientific paper contribution. |
| **D. Standalone Evaluator Benchmark** | Positioning the multi-component answer evaluator as the sole contribution. | **`PARTIAL`** | While EXP-2 demonstrates high correlation ($\rho = 0.8358$) and rater agreement ($\alpha = 0.8255$), the human test set is limited to $n=20$ pilot items. |
| **E. Evidence-Grounded Feedback** | Focusing solely on Qwen-7B vs. non-LLM feedback. | **`PARTIAL`** | Feedback is evaluated on lexical grounding and rubric gap proxies ($n=20$), not human pedagogical utility. |
| **F. Integrated Personalized Adaptive Framework (SELECTED)** | Positioning PrepAIred as a closed-loop adaptive assessment framework coupling candidate-state modeling, guardrail-shielded PPO adaptation, calibrated multi-component scoring ($S_1+S_2+R$), and an empirical trade-off analysis between generative LLM and structured rubric feedback. | **`STRONGLY SUPPORTED`** | **Scientifically Defensible.** It accurately reflects the full empirical scope across all 5 experiments, cleanly admits simulation vs. human boundaries, and avoids unverified hiring or learning gain claims. |

### 2.2 Selected Central Contribution Statement
> *"The primary scientific contribution of this work is an integrated, closed-loop adaptive assessment framework for technical interviews that couples a 6D candidate-state representation with a guardrail-augmented PPO difficulty controller, a calibrated three-component answer evaluator ($S_1+S_2+R$), 3-level question deduplication, and an empirical characterization of the trade-offs between generative LLM transcript grounding and deterministic rubric gap recovery."*

---

## 3. Part 2 — Research Questions Audit Table

| RQ | Formal Hypothesis | Experiment ID | Dataset / Scale | Statistical Test | Observed Result | Answered Status | Remaining Limitation |
|---|---|:---:|:---:|---|---|:---:|---|
| **RQ1 (Difficulty Adaptation)** | PPO with guardrails adapts difficulty more responsively to candidate ability than fixed or rule-based baselines. | **EXP-1** | 150 simulated episodes ($3 \times 5 \times 10$) | Wilcoxon signed-rank + Holm-Bonferroni | PPO $\rho = +0.1572 \pm 0.08$ vs Fixed $\rho = 0.0$ ($p = 6.15 \times 10^{-4}$) and Rule-Based $\rho = -0.2572$ ($p = 5.30 \times 10^{-8}$) | **`ANSWERED (SIMULATION)`** | Evaluated in simulation against synthetic personas; transfer to human cohorts requires clinical trials. |
| **RQ2 (Answer Evaluation)** | Multi-component neural evaluation ($S_1+S_2+R$) correlates strongly with blinded human expert ratings. | **EXP-2** | 20 benchmark items, 140 scorings, 3 human raters | Spearman rank correlation, Krippendorff's $\alpha$, MAE | Spearman $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$), Krippendorff $\alpha = 0.8255$, $\text{MAE} = 0.2585$ | **`ANSWERED (PILOT BENCHMARK)`** | Ground-truth dataset is $n=20$ curated technical answers across 4 core C/DSA topics. |
| **RQ3 (Feedback Grounding)** | Generative LLM provides higher transcript lexical grounding than non-LLM structured recovery, but structured recovery maximizes rubric coverage. | **EXP-3** | 20 benchmark items, 60 evaluations (Tesla T4 GPU) | Wilcoxon signed-rank + Holm-Bonferroni, Bootstrap 95% CI | Qwen Grounding = $0.2496$ vs Structured $0.0383$ ($p = 2.56 \times 10^{-3}$); Structured Gap Coverage = $100.0\%$ vs Qwen $72.5\%$ ($p = 9.11 \times 10^{-4}$) | **`ANSWERED (AUTOMATED PROXIES)`** | Evaluated via lexical overlap and string matching proxies rather than human pedagogical perception. |
| **RQ4 (Personalization)** | 3-level deduplication eliminates repetition and generates differentiated trajectories for distinct ability profiles. | **EXP-4** | 60 simulated sessions ($3 \times 2 \times 10$) | Chi-square test of proportions, Euclidean distance | Repetition: $0.0\%$ vs Random $6.0\%$ ($p < 0.001$); Weakness targeting: $16.67\%$ vs $2.0\%$; Trajectory divergence: $d = 14.21$ | **`ANSWERED (SIMULATION)`** | Candidate profiles are synthetic probabilistic models. |
| **RQ5 (Component Decoupling)** | System components operate orthogonally without cross-modal interference. | **EXP-5** | 70 standardized sessions ($7 \times 10$ seeds) | Leave-one-out behavioral delta analysis | Clean component drops verified (removing RL drops adaptation $\rho \to 0.0$; removing follow-ups drops probes $0.50 \to 0.00$) | **`ANSWERED (SYSTEM LEVEL)`** | Tested on standardized simulated interview script. |

---

## 4. Part 3 — Novelty Classification Matrix

| Major Component / Claim | Classification | Justification & Scientific Boundary |
|---|:---:|---|
| **PPO RL Algorithm** | **`ENGINEERING / INTEGRATION`** | Standard Stable-Baselines3 PPO implementation with continuous 6D state and 3 discrete actions. Novelty is in the application domain and guardrail shielding, not the RL algorithm. |
| **Anti-Keyword Dampening ($S_{2,\text{eff}}$)** | **`EMPIRICAL / NOVEL MECHANISM`** | Formulating $S_{2,\text{eff}} = S_2 \cdot \min(1.0, 1.2 R + 0.1)$ to prevent keyword stuffing from inflating technical grades without NLI entailment. |
| **Generative vs. Structured Feedback Trade-Off** | **`EMPIRICAL CONTRIBUTION`** | Rigorous empirical demonstration that non-LLM structured recovery delivers superior rubric gap coverage ($100.0\%$) and lower latency (<0.05s) than an unquantized 7B LLM ($72.5\%$, 9.78s). |
| **3-Level Question Deduplication** | **`ENGINEERING CONTRIBUTION`** | Exact ID, normalized string match, and Jaccard token overlap ($\ge 0.75$). Effective engineering solution that completely eliminates question repetition ($0.0\%$). |
| **Closed-Loop Multimodal Architecture** | **`INTEGRATION / NOVEL SYSTEM`** | Coupling speech prosody, neural short-answer grading, dockerized C execution, and difficulty adaptation in a unified educational pipeline. |

---

## 5. Part 4 — Experimental Validity & Pseudoreplication Audit

1. **Independent Experimental Units:**
   - **EXP-1:** 150 episodes across 5 distinct candidate personas and 10 random seeds. (Adequate simulation power; persona behavior is fixed across seeds).
   - **EXP-2:** 20 distinct technical items evaluated across 7 weight configurations. 3 human raters independently graded all 20 items (Krippendorff $\alpha = 0.8255$).
   - **EXP-3:** 20 distinct benchmark turns evaluated across 3 conditions (Generic, Structured, Qwen-7B). Wilcoxon signed-rank tests performed on paired items.
   - **EXP-4:** 60 sessions across 2 distinct ability profiles and 10 seeds.
   - **EXP-5:** 70 sessions across 7 leave-one-out conditions and 10 seeds.
2. **Pseudoreplication Risks:**
   - **Risk:** Treating multiple simulated sessions from the same synthetic persona as independent human subjects.
   - **Mitigation:** The manuscript explicitly defines the experimental unit as *simulated candidate sessions* and avoids claiming human cohort independence.

---

## 6. Part 5–9 — Subsystem Verification Verdicts

- **EXP-1 (PPO Adaptation):** **`STRONG SIMULATION EVIDENCE`**. PPO adaptation correlation ($\rho = +0.1572$) is statistically superior to Fixed ($p < 0.001$) and Rule-Based ($p < 10^{-7}$). Allowed wording: *"PPO produces statistically significant adaptive difficulty progression in simulation relative to static and heuristic baselines."* Prohibited: *"PPO is universally superior in human training."*
- **EXP-2 (Evaluator Ablation):** **`STRONG BENCHMARK EVIDENCE`**. $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$) vs. 3 blinded human raters ($\alpha = 0.8255$). Allowed wording: *"Evaluator scores correlate strongly with blinded expert ratings on the 20-sample pilot benchmark."* Prohibited: *"Evaluator is 100% accurate and fully validated across all CS domains."*
- **EXP-3 (Formative Feedback):** **`STRONG EMPIRICAL TRADE-OFF EVIDENCE`**. Qwen-7B achieves higher lexical grounding ($0.2496$ vs. $0.0383$, $p < 0.01$), while Structured Recovery achieves higher gap coverage ($100.0\%$ vs. $72.5\%$, $p < 0.001$). Allowed wording: *"Generative LLM feedback provides significantly richer transcript grounding, while structured recovery guarantees exhaustive rubric concept coverage."*
- **EXP-4 (Personalization):** **`STRONG HEURISTIC / BEHAVIORAL EVIDENCE`**. Repetition eliminated ($0.0\%$), trajectory divergence $d = 14.21$. Allowed wording: *"Candidate-state selection eliminates question repetition and yields differentiated difficulty trajectories in simulation."*
- **EXP-5 (Ablation):** **`STRONG ARCHITECTURAL DECOUPLING EVIDENCE`**. Clean component isolation confirmed across all 7 conditions.

---

## 7. Part 10 — Statistical Methodology Review

1. **Paired Comparisons:** Wilcoxon signed-rank tests correctly applied for non-parametric paired item comparisons (EXP-1, EXP-3).
2. **Multiple Testing Correction:** Holm-Bonferroni family-wise error rate control properly computed for 3-way comparisons.
3. **Confidence Intervals:** 10,000-resample non-parametric bootstrap percentile intervals properly computed.
4. **Inter-Rater Reliability:** Krippendorff's $\alpha = 0.8255$ computed across 56 overlapping pairs.
5. **Verdict:** All statistical tests are mathematically sound, reproducible, and correctly interpreted.

---

## 8. Part 12 — Human Validation Boundaries

```
================================================================================
CRITICAL HUMAN VALIDATION BOUNDARY
================================================================================
[HUMAN VALIDATED]:
- Blinded human expert ratings on n=20 technical answer benchmark (Krippendorff alpha = 0.8255).

[NOT YET VALIDATED (DOCUMENTED FUTURE WORK)]:
- Candidate interview skill improvement.
- Candidate hiring success rates.
- Long-term knowledge retention.
- Candidate anxiety reduction.
- Whole-system longitudinal educational outcomes.
================================================================================
```

---

## 9. Part 14 — Manuscript Structure & Completeness

All 29 required sections are **PRESENT**, **COMPLETE**, and **EVIDENCE-SUPPORTED** in [`docs/paper_draft_ieee.md`](paper_draft_ieee.md):
- All 12 tables (Tables I–XII) are populated with verified data.
- All 8 figures (Figures 1–8) are generated at 300 DPI from real experimental artifacts.
- Bidirectional traceability is 100% complete in [`docs/PAPER_RESULTS_TRACEABILITY.md`](PAPER_RESULTS_TRACEABILITY.md).

---

## 10. Part 18 — Recommended Venue Category

**Primary Category:** **Intelligent Tutoring Systems / Educational Technology & AI in Education**
*Target Venues:*
- **IEEE Transactions on Learning Technologies (TLT)**
- **International Conference on Artificial Intelligence in Education (AIED)**
- **Educational Data Mining (EDM)**
- **ACM Learning @ Scale (L@S)**
- **IEEE International Conference on Advanced Learning Technologies (ICALT)**

*Fit Analysis:* Excellent fit for EdTech/AIED. Reviewers in these venues will value the closed-loop system design, the calibrated evaluator, the anti-keyword dampening, and the empirical LLM vs. non-LLM feedback trade-offs.

---

## 11. Final Publication Readiness Verdict

```
================================================================================
FINAL VERDICT: READY FOR SUBMISSION
(Paper is fully traceable, claims are strictly calibrated, and artifacts are frozen)
================================================================================
```
