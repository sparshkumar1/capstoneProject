# Paper 2 Outline: Grounded Technical Answer Evaluation
**Target Venue:** ICTCS 2026 / IEEE Transactions on Education (ToE)
**Title:** Evidence-Grounded Technical Answer Evaluation Using Semantic, Concept, and Reasoning Signals

## Section 1: Introduction
- Challenges of scoring conceptual explanations in computer science education.
- Vulnerabilities of keyword matching (gaming) vs LLM scoring (hallucination).
- Core thesis: Multi-signal scoring with reasoning-conditioned concept dampening aligns with human expertise while resisting adversarial gaming.

## Section 2: Related Work
- Short-answer grading (SAG) in STEM.
- Semantic sentence representations (SBERT).
- Dense vector retrieval and concept matching (FAISS).
- Cross-encoder reasoning entailment.

## Section 3: Evaluation Framework Methodology
- Tripartite formulation: .15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$.
- FAISS vector indexing of rubric concept groups.
- Anti-gaming dampener: {2,\text{eff}} = S_2 \times 0.60$ when  \le 0.30$.
- ScoreValidator guardrails and mandatory concept caps.

## Section 4: Empirical Evaluation
- EXP-EVAL-1: 7-way ablation benchmark against expert human educator (=20$).
- EXP-EVAL-2: Adversarial keyword-stuffing resistance.
- EXP-EVAL-3: Concept threshold sensitivity sweep ($\theta \in [0.20, 0.70]$).
- EXP-EVAL-4: Qualitative error analysis and misconception confusion matrix.
- EXP-EVAL-5: Metamorphic robustness testing across 5 invariant relations.

## Section 5: Discussion, Ethics & Limitations
- Pilot sample size framing (=20$) and multi-rater roadmap.
- Complete insulation of acoustic prosody from technical scoring.
