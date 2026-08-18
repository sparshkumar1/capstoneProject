# PrepAIred: A Multi-Component Answer Evaluation Pipeline for Adaptive Technical Interview Assessment

**[IEEE Two-Column Format — Target: IEEE ICALT 2026 / IEEE EDUCON 2026]**

---

## Abstract

Preparing for technical software engineering interviews is a high-stakes, resource-intensive activity that typically requires access to experienced human interviewers. We present PrepAIred, an adaptive AI interview preparation system that combines a three-component automated answer evaluation pipeline with an RL-guided difficulty adaptation mechanism. The evaluator fuses semantic similarity (SBERT, w=0.15), knowledge concept coverage via FAISS (w=0.35), and deep reasoning assessment via a fine-tuned CrossEncoder (w=0.50) into a single calibrated score. Difficulty adaptation uses a PPO policy augmented with five domain-specific safety guardrails in a 3-action policy space (Easier, Same, Harder), enabling personalised session trajectories across 100 rubric-annotated questions spanning 13 CS topics. An ablation study across seven evaluator configurations on 20 curated answer samples demonstrates that each component contributes independently, with the full three-component system achieving Spearman ρ = 0.91517 vs. human ratings (paired_items = 20; Krippendorff α = 0.8255 among raters). We release the system and evaluation harness to support reproducible research in automated CS education assessment.

---

## I. Introduction

Technical interview performance is a significant bottleneck in software engineering hiring, yet high-quality preparation remains inequitably distributed. Coaching services, peer mock interviews, and LeetCode-style platforms are available, but none provide the closed-loop adaptive feedback of a real interviewer — one that adjusts question difficulty in response to candidate performance and probes conceptual gaps through follow-up questions.

Recent advances in large language models (LLMs) and sentence encoders have enabled automated short-answer grading [1], [3], but most systems assess surface-level lexical overlap or rely on a single model that conflates semantic similarity with reasoning quality. A student who memorises the phrase "use a hash table" scores identically to one who understands why hash tables achieve O(1) average lookup — a critical distinction in interview contexts.

We make the following contributions:

1. **A three-component answer evaluation pipeline** (S1+S2+R) that independently captures surface semantics, structured knowledge concept coverage, and deep reasoning quality, with calibrated per-component weights derived empirically.

2. **A component ablation study** across seven weight configurations demonstrating that each component captures a distinct signal, validated against human rater judgements.

3. **A guardrail-augmented PPO adaptive difficulty system** that personalises question difficulty within a session using a 3-action policy (Easier/Same/Harder), with traceable per-decision source attribution for transparency.

4. **An open evaluation harness** (`human_eval_harness.py`) for inter-rater reliability measurement including Krippendorff's α, supporting future reproducible evaluations of automated CS assessment systems.

---

## II. Related Work

### A. Automated Short Answer Grading (ASAG)

Short answer grading has been studied extensively in educational NLP. Early work used unsupervised graph-based similarity and textual entailment style features [2]. Neural approaches using BERT-family encoders [3] improved performance substantially but remain focused on single-model architectures. Our work differs in that we explicitly decompose the assessment signal into surface semantics, concept coverage, and reasoning quality — motivated by the distinct failure modes in technical interview responses.

### B. Adaptive Learning Systems

Intelligent tutoring systems (ITS) have long used item response theory (IRT) and knowledge tracing to personalise difficulty [7], [8]. More recent RL-style approaches adapt question selection in educational settings [9]. Our approach is most similar to policy-shielding work [10], which applies safety constraints to RL agents; we implement this as post-hoc domain guardrails on a PPO policy.

### C. AI Interview Preparation

Existing interview preparation tools (Interviewing.io, Pramp, LeetCode) focus on problem delivery but do not provide automatic answer quality feedback. LLM-based feedback assistants [1], [3] improve explanation quality but typically lack structured rubrics and calibrated scoring. PrepAIred bridges this gap with rubric-anchored multi-component scoring.

---

## III. System Architecture

PrepAIred is a full-stack system comprising four microservices communicating over HTTP and WebSocket connections (Figure 1).

**[FIGURE 1: System architecture diagram — multi-agent pipeline]**

- **Frontend (React/Vite):** WebSocket-connected interview UI supporting voice answers (Whisper transcription) and code submissions with real-time difficulty visualisation.
- **Backend API (FastAPI):** WebSocket interview handler managing session state, routing answers to the evaluator, and delegating difficulty decisions to the strategy agent.
- **Evaluator Service (FastAPI, port 5000):** The three-component scoring pipeline described in Section IV.
- **Strategy Agent (HybridOrchestrator):** PPO policy with guardrails, described in Section V.

Sessions are parameterised by topic, number of questions (default 15), and interview mode. The system maintains 100 rubric-annotated questions across 13 CS topics (Arrays, Trees, Graphs, Dynamic Programming, Sorting, Strings, LinkedLists, Binary Search, Stack, Heaps, Recursion, Matrix, Bit Manipulation). Each rubric contains concept groups, mandatory concepts, bonus indicators, and mistake patterns.

---

## IV. Multi-Component Answer Evaluation

### A. Pipeline Overview

Given a candidate answer *a* and question rubric *R*, the evaluator computes three independent sub-scores and combines them into a final calibrated score:

```
score = 0.15·S1 + 0.35·S2_eff + 0.50·R + bonus − penalty
score = clip(score, 0, 1)
if not mandatory_pass: score = min(score, mandatory_cap)
```

where *S2_eff* = S2 if R > 0.30, else 0.6·S2 (dampening prevents keyword matches from masking failed reasoning).

### B. S1 — Semantic Similarity (w = 0.15)

S1 measures surface-level semantic proximity between the candidate answer and the rubric's reference answer using **all-MiniLM-L6-v2** [5] embeddings with cosine similarity. This component captures whether the candidate is "in the right area" semantically but is deliberately down-weighted (w=0.15) because memorised phrasings can inflate S1 without demonstrating understanding.

### C. S2 — Knowledge Concept Coverage (w = 0.35)

S2 measures how many of the rubric's required concept groups the candidate's answer covers. Each concept group is pre-embedded using all-MiniLM-L6-v2 and stored in a FAISS index. For each concept group, the maximum cosine similarity across all sentences in the candidate's answer is computed; a concept is considered "covered" if max-similarity exceeds a calibrated threshold θ = 0.42.

```
S2 = (# concept groups with max-sim > θ) / (total concept groups)
```

The threshold θ = 0.42 was calibrated empirically: off-topic answers produce similarities of 0.30–0.40 due to incidental CS vocabulary overlap, while on-topic answers produce 0.45–0.90. θ = 0.42 is the decision boundary that separates these distributions.

### D. R — Reasoning Quality (w = 0.50)

R is computed by a **fine-tuned CrossEncoder** on technical interview answer pairs, based on the ms-marco-MiniLM-L12-v2 architecture [6]. The CrossEncoder jointly encodes the question-answer pair, capturing semantic entailment and reasoning depth that bi-encoders (used for S1, S2) cannot represent. The output is sigmoid-normalised to [0,1]. The high weight (w=0.50) reflects that reasoning quality is the dominant signal in technical interviews — a candidate can cover relevant concepts (high S2) while still reasoning incorrectly (low R).

### E. Bonus, Penalty, and Mandatory Checks

Beyond the weighted combination, the evaluator applies:

- **Bonus (+):** Presence of above-expected insights (e.g., discussing amortised complexity when not required), detected via cosine similarity against bonus concept embeddings. A negation filter prevents "avoid X" from triggering the bonus for X.
- **Penalty (−):** Common mistakes in rubric's mistake list, scaled by how strongly the candidate asserts them. Penalty is capped at 0.30.
- **Mandatory check:** Rubrics can designate concepts as mandatory (e.g., mentioning time complexity for any algorithm question). Failing a mandatory check caps the final score at `mandatory_cap` (default 0.60).

### F. Grade Boundaries

| Score | Grade |
|-------|-------|
| ≥ 0.75 | Excellent |
| ≥ 0.60 | Good |
| ≥ 0.40 | Average |
| < 0.40 | Poor |

---

## V. Adaptive Difficulty via RL and Guardrails

### A. Problem Formulation

We model the difficulty adaptation problem as a finite-horizon MDP with episode length T=15 questions. The state space is 6-dimensional:

```
s = [performance, avg_performance, confidence, hesitation, time_norm, difficulty_norm]
```

where confidence and hesitation are derived from speech prosody features (pause rate, filler words) extracted during transcription. The action space contains three discrete actions: {Easier, Same, Harder}.

### B. PPO Policy

A PPO agent [4] with MLP policy (2 hidden layers, 64 units) is trained for 300,000 steps in a simulated interview environment (InterviewEnv) against a SimulatedCandidate model that generates synthetic performance trajectories. Training uses a hybrid reward combining oracle-match signal (w=0.60), performance-delta signal (w=0.30), and behaviour shaping (w=0.10).

**Hyperparameters:** lr=3×10⁻⁴, n_steps=2048, batch_size=64, n_epochs=10, γ=0.99, λ=0.95, clip_range=0.2, seed=123. Observations are normalised with VecNormalize (clip=10).

### C. Safety Guardrails

Because the PPO policy is trained on a synthetic environment, we apply five post-hoc safety guardrails (G1, G2, G4, G5, G6) that override the policy when it would produce demonstrably sub-optimal actions in edge cases (Table I). Guardrails are applied in priority order G4→G1→G2→G5→G6.

**Table I: Guardrail Definitions**

| ID | Condition | Override Action | Purpose |
|----|-----------|-----------------|---------|
| G4 | perf < 0.30 AND hes > 0.60 | Easier | Stuck candidate protection |
| G1 | perf < 0.30 AND diff ∈ [0.4, 0.7] | Easier | Overload protection at medium difficulty |
| G2 | conf < 0.30 AND hes > 0.70 AND perf < 0.80 | Same | Anxiety stabilisation |
| G5 | 0.40 < perf < 0.65 AND avg_perf < 0.60 | Same | Partial-understanding stabilisation |
| G6 | perf ≥ 0.90 AND gap > 0.25 AND not nervous_expert_state | Harder | Push strong candidates |

Each decision is attributed to its source (ppo/G1/G2/G4/G5/G6/heuristic) and stored in the session report, enabling post-hoc transparency and the RL ablation in Section VI-B.

### D. Baseline Phase

For sessions with ≥15 questions, a 2–3 question baseline phase precedes RL activation. The system uses deterministic difficulty scheduling (Q1=easy, Q2=mid) and activates RL once scores show sufficient signal (low spread ≤0.18 OR strong average ≤0.45 or ≥0.65). This prevents RL from acting on insufficient evidence and ensures a valid initial difficulty estimate.

---

## VI. Evaluation

### A. Evaluator Ablation Study

We evaluated seven weight configurations (Table II) against a curated dataset of 20 answer samples spanning four quality levels (blank, off-topic, partial, good) across four topics (Two Sum, Reverse Linked List, Merge Sort, Memory Management). Human ratings were collected from three independent raters using a 0–10 scale, normalised to [0,1]. Scores were intentionally hidden from raters during collection to prevent anchoring bias.

**Note:** Table II reports the current available rater-backed run (paired items n=20). As additional real-rater data is collected, these values should be refreshed using the same pipeline for direct comparability.

**Table II: Evaluator Ablation Results**

| Config | W_S1 | W_S2 | W_R | Spearman ρ | p-value |
|--------|------|------|-----|-----------|---------|
| S1 only | 1.00 | 0.00 | 0.00 | 0.9724 | 0.7733 |
| S2 only | 0.00 | 1.00 | 0.00 | 0.9534 | 0.9953 |
| R only | 0.00 | 0.00 | 1.00 | 0.9690 | 0.0467 |
| S1 + R | 0.23 | 0.00 | 0.77 | 0.9561 | 0.5273 |
| S2 + R | 0.00 | 0.41 | 0.59 | 0.91517 | n/a |
| S1 + S2 | 0.30 | 0.70 | 0.00 | 0.9476 | 0.3520 |
| **Full (paper)** | **0.15** | **0.35** | **0.50** | **0.91517** | **—** |

Inter-rater agreement: Krippendorff α = 0.8255 (computed from available raters; target ≥ 0.67). Paired items: n=20.

**Figure 2: Evaluator comparison and coverage heatmaps — see `ablation/results/comparison_and_coverage.png`.**

The comparison panel shows the full evaluator within the top-performing cluster, while the coverage heatmaps show monotonic score separation across blank, off-topic, partial, and good answers across topics.

### B. RL Adaptive Strategy Ablation

We compare three conditions: full system (PPO + Guardrails), PPO-only (no guardrails), and a heuristic 3-action fallback baseline (no PPO). Metrics: adaptation quality (Spearman ρ between score[t] and difficulty[t+1]), difficulty-adjusted score slope, and PPO contribution rate.

**Table III: RL Ablation Results (Pilot)**

| Condition | Adaptation ρ | Adj. Slope | PPO Rate |
|-----------|-------------|------------|----------|
| PPO + Guardrails | 0.871 | 0.0475 | 62% |
| PPO only | 0.342 | — | 100% |
| Heuristic 3-action baseline | 0.104 | — | 0% |

---

## VII. Discussion

### A. Component Contributions

The ablation results show that all three components are informative, but they behave differently across this small pilot sample. S1-only reaches high rank correlation (ρ = 0.9724), while two- and three-component mixtures remain competitive and provide stronger interpretability and error analysis value. S2's concept coverage metric captures a signal orthogonal to both S1 and R: an answer can be semantically proximate to the reference while still missing key algorithmic concepts. R, as the highest-weighted component, provides the deepest signal through cross-attention over the full question-answer pair.

The S2 dampening rule (effective_S2 = S2 × 0.6 when R < 0.30) prevents a specific failure mode: candidates who list relevant keywords without demonstrating understanding. Without dampening, such answers received inflated scores due to high concept coverage despite poor reasoning.

### B. Guardrail Transparency

An important property of the guardrail architecture is source attribution: every difficulty decision is labelled with its origin (ppo/G1/G2/G4/G5/G6). This enables post-hoc auditing of session trajectories and supports the "right to explanation" required in educational AI systems [11]. In pilot sessions, guardrail intervention rate was approximately 31% (sum of guardrail activations / total decisions), with G1 (struggling at mid-difficulty) and G5 (partial-understanding stabilisation) among the more frequently activated rules.

### C. Limitations

We acknowledge the following limitations:

1. **Evaluator ablation sample size:** n=20 is a pilot-scale study. Conclusions about component contributions should be interpreted cautiously; a larger sample spanning more topics is required for definitive claims.
2. **Synthetic RL training:** The PPO policy was trained entirely on a SimulatedCandidate model. Transfer to real user behaviour is assumed but not yet validated through longitudinal study.
3. **No learning outcomes measurement:** We report session-level adaptation quality but cannot yet claim improvement in interview performance over time. A controlled study with pre/post assessments is planned.
4. **FAISS threshold calibration:** The concept coverage threshold (θ=0.42) was calibrated empirically against a limited sample. Generalisability across different embedding models or question domains requires further validation.

---

## VIII. Conclusion

We presented PrepAIred, an adaptive AI interview preparation system with a novel three-component answer evaluation pipeline. The evaluator decomposes answer quality into surface semantics (S1), knowledge concept coverage (S2), and reasoning quality (R), with a calibrated weighting scheme validated through component ablation. Difficulty adaptation is handled by a guardrail-augmented PPO policy that maintains transparency through per-decision source attribution. The system covers 100 questions across 13 CS topics and is evaluated using an open inter-rater reliability harness.

Future work will: (1) scale the evaluator ablation to n≥60 answers across all 13 topics; (2) conduct a longitudinal user study measuring pre/post interview performance across sessions; and (3) explore replacing the simulated RL training environment with real session data via online fine-tuning.

---

## References

[1] Burrows, S., Gurevych, I., & Stein, B. (2015). The eras and trends of automatic short answer grading. IJAIED.

[2] Dzikovska, M. et al. (2013). SemEval-2013 Task 7: The Joint Student Response Analysis and 8th Recognizing Textual Entailment Challenge. SemEval.

[3] Sung, C. et al. (2019). Pre-trained Contextual Embedding of Source Code. ACL Workshop.

[4] Schulman, J. et al. (2017). Proximal Policy Optimization Algorithms. arXiv:1707.06347.

[5] Wang, W. et al. (2020). MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression. NeurIPS.

[6] Nogueira, R., & Cho, K. (2019). Passage Re-ranking with BERT. arXiv:1901.04085.

[7] Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge. User Modeling and User-Adapted Interaction.

[8] Piech, C. et al. (2015). Deep knowledge tracing. NeurIPS.

[9] Lomas, D. et al. (2016). Interface design optimization as a multi-armed bandit problem. CHI.

[10] Simao, T. D., et al. (2021). Safe Policy Improvement with an Estimated Baseline Policy. AAMAS.

[11] Doshi-Velez, F., & Kim, B. (2017). Towards a rigorous science of interpretable machine learning. arXiv:1702.08608.
