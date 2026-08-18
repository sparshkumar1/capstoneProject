# Stage 17 — Final Research Paper Construction, Evidence Traceability, & Claim Audit Report

**Document ID:** `STAGE-17-REPORT`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Authoritative Manuscript:** [`docs/paper_draft_ieee.md`](docs/paper_draft_ieee.md)
**Traceability Document:** [`docs/PAPER_RESULTS_TRACEABILITY.md`](docs/PAPER_RESULTS_TRACEABILITY.md)
**Status:** COMPLETE, VERIFIED, AND FROZEN

---

## 1. Final Paper Title
**"A Personalized Adaptive Framework for Multimodal Technical Interview Assessment and Preparation"**

---

## 2. Strongest Evidence-Supported Central Contribution
The central contribution is an **integrated multimodal adaptive assessment framework** that combines:
1. A calibrated multi-component answer evaluator ($S_1+S_2+R$) with anti-keyword dampening,
2. A 6D candidate-state representation tracking technical performance, speech hesitation, confidence, and pacing,
3. A guardrail-augmented PPO difficulty controller,
4. A 3-level question deduplication and weakness-targeting selector, and
5. An empirical characterization of the trade-offs between generative LLM feedback and deterministic rubric recovery.

---

## 3. Why That Contribution Was Selected
Rather than artificially isolating a single machine learning technique (such as PPO, Qwen, or WhisperX) as an isolated "magic bullet," the empirical data demonstrates that the system's primary value arises from the **closed-loop interaction and calibrated separation of concerns** across these components:
- PPO provides positive adaptation correlation ($\rho = +0.1572$), but requires deterministic guardrails (G1–G6) to prevent oscillation.
- The evaluator achieves high correlation with human ratings ($\rho = 0.8358$), but depends on $S_1+S_2$ for primary scoring variance and $R$ for keyword dampening.
- Qwen-7B delivers superior lexical transcript grounding ($0.2496$), but non-LLM structured recovery delivers strictly superior rubric gap coverage ($100.0\%$) with sub-50ms latency.

---

## 4. Supporting Experiments
- **EXP-1:** Adaptive Difficulty Controller ($150$ simulated episodes).
- **EXP-2:** Multi-Component Evaluator Ablation ($140$ scorings, $20$ items, $3$ blinded human raters).
- **EXP-3:** Formative Feedback Grounding Benchmark ($60$ evaluations, Tesla T4 GPU).
- **EXP-4:** Personalization & Trajectory Divergence ($60$ simulated sessions).
- **EXP-5:** Leave-One-Out Behavioral Isolation Ablation ($70$ standardized sessions).

---

## 5. Numerical Claims Audit
- **Total Numerical Claims in Manuscript:** 27 distinct statistical and architectural metrics.
- **Number of Claims Successfully Traced:** 27 / 27 (100% dataflow traceability to raw machine-readable JSON/CSV files).
- **Unverified / Fabricated Claims:** Exactly 0.

---

## 6. Unsupported Claims Removed & Weakened
1. **Removed Claims of "Human-Validated Platform":** Explicitly clarified that human validation is restricted to evaluator inter-rater reliability on $n=20$ pilot items ($\alpha = 0.8255$); whole-system candidate hiring outcomes remain `NOT YET VALIDATED`.
2. **Weakened RL Performance Claims:** Replaced claims of "PPO improves candidate learning" with "PPO produced a statistically distinguishable adaptation trajectory relative to fixed and rule-based controllers in simulation ($\rho = +0.1572$)."
3. **Weakened Feedback Superiority Claims:** Replaced generic "Qwen is superior" phrasing with an explicit characterization of the empirical trade-off: Qwen-7B excels at transcript lexical grounding ($0.2496$), while non-LLM structured recovery excels at rubric concept gap coverage ($100.0\%$).
4. **Weakened Personalization Claims:** Replaced "Personalization improves hiring rates" with "Candidate-state selection eliminated question repetition ($0.0\%$) and produced distinct trajectory divergence ($d = 14.21$)."

---

## 7. Claim Status Classification in `docs/CLAIMS_CHECK.md`

| Category | Count | Claim Rows Matching Category |
|---|:---:|---|
| **`IMPLEMENTED`** | **0** | — |
| **`TESTED`** | **8** | Claim #3 (Dampening), #4 (PPO Action Space), #6 (Guardrails G1–G6), #9 (Docker Sandbox), #12 (WhisperX Prosody), #13 (Timing Formulation), #14 (Multi-Agent Decoupling), #15 (125 Question Bank) |
| **`EXPERIMENTALLY VALIDATED`** | **6** | Claim #1 (Evaluator $S_1+S_2+R$), #5 (PPO Adaptation $\rho = +0.1572$), #7 (3-Level Deduplication $0.0\%$), #8 (Trajectory Divergence $d = 14.21$), #10 (Follow-Up Probing), #11 (Feedback Grounding & Gap Coverage) |
| **`HUMAN VALIDATED`** | **1** | Claim #2 (Human Inter-Rater Reliability Krippendorff's $\alpha = 0.8255$) |
| **`NOT YET VALIDATED`** | **1** | Claim #16 (Whole-System Human Interview Efficacy & Longitudinal Learning Gains) |
| **Total** | **16** | **All 16 Authoritative Claim Rows ($0 + 8 + 6 + 1 + 1 = 16$)** |

---

## 8. Subsystem Empirical Evidence Summaries

### A. PPO Difficulty Adaptation (EXP-1)
- $150$ simulated episodes ($3 \times 5 \times 10$).
- PPO with guardrails achieved $\rho = +0.1572 \pm 0.08$ vs. Fixed ($\rho = 0.0, p = 6.15 \times 10^{-4}$) and Rule-Based ($\rho = -0.2572, p = 5.30 \times 10^{-8}$).

### B. Multi-Component Evaluator (EXP-2)
- $140$ scorings across $7$ configurations.
- Full pipeline and $S_1+S_2$ achieved $\rho = 0.8358$ ($p = 4.46 \times 10^{-6}$) vs. 3 blinded human raters ($\alpha = 0.8255$). $S_1+S_2$ achieved lower MAE ($0.1907$ vs. $0.2585$).

### C. Formative Feedback (EXP-3)
- $60$ evaluations across $3$ conditions.
- Qwen2.5-7B-Instruct (Tesla T4 GPU) achieved transcript lexical grounding of $0.2496$ (95% CI: $[0.1758, 0.3331]$) vs. Structured ($0.0383$) and Generic ($0.0000$).
- Structured Recovery achieved $100.0\%$ rubric gap coverage vs. Qwen ($72.5\%$) and Generic ($0.0\%$).

### D. Personalization & Deduplication (EXP-4)
- $60$ simulated sessions ($3 \times 2 \times 10$).
- 3-level deduplication eliminated question repetition ($0.0\%$ vs. $6.0\%$ random, $p < 0.001$).
- Trajectory divergence between strong and struggling candidate profiles reached Euclidean distance $d = 14.21$.

### E. Component Ablation (EXP-5)
- $70$ standardized sessions across $7$ conditions.
- Removing RL dropped adaptation $\rho \to 0.0000$; removing follow-ups dropped probing from $0.50 \to 0.00$ probes/session; clean component isolation confirmed with zero cross-modal crashes.

---

## 9. Limitations & Threats to Validity
1. **Pilot Evaluation Scale:** Evaluator human ground-truth benchmarking was conducted on $n=20$ curated technical answers.
2. **Simulation-Based RL Validation:** PPO adaptation was measured against synthetic candidate personas; human student transfer requires longitudinal trials.
3. **Automated Lexical Proxies:** EXP-3 grounding metrics assess verbatim token overlap and rubric string matching rather than human pedagogical perception.
4. **Hardware Boundary:** Unquantized 7B LLM generation is impractical on local CPU hosts (>22 min/turn) and requires dedicated GPU infrastructure.

---

## 10. Regression Test Verification Results
- **EXP-3 Unit Suite:** `pytest tests/unit/test_qwen_followup_feedback.py -v` $\to$ **14 passed, 0 failed** in 41.99s (100% pass).
- **Backend Full Suite:** `.venv\Scripts\python.exe -m pytest tests\unit\ tests\integration\ -v` $\to$ **178 passed, 0 failed** in 356.88s (100% pass).
- **Frontend Vitest Suite:** `npm run --prefix apps/web test:ci` $\to$ **7 passed, 0 failed** in 1.82s (100% pass).

---

## 11. Final Verification Declaration

```
================================================================================
STAGE 17 COMPLETE — AUTHORITATIVE SCIENTIFIC PAPER & TRACEABILITY FROZEN
================================================================================
```
- Manuscript: [`docs/paper_draft_ieee.md`](docs/paper_draft_ieee.md) (All 29 required sections, 12 tables, 8 figures).
- Traceability: [`docs/PAPER_RESULTS_TRACEABILITY.md`](docs/PAPER_RESULTS_TRACEABILITY.md) (100% numerical claim dataflow).
- Audit Report: [`docs/stage17_paper_audit.md`](docs/stage17_paper_audit.md).
- Status: **STOPPED**. Stage 18 has NOT been started.
