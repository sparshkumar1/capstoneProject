# PrepAIred — Multi-Component Answer Evaluation Specification

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Architectural Overview & Rationale

Traditional automated short answer grading systems frequently rely on a single sentence embedding model, conflating surface lexical similarity with deep conceptual reasoning. A candidate repeating keyword phrases like *"use a hash map"* can score high on semantic similarity while failing to explain collision handling or complexity trade-offs.

PrepAIred solves this failure mode by decomposing answer assessment into a **calibrated three-component neural pipeline** ($S_1 + S_2 + R$):

```
Candidate Answer + Question Rubric
  │
  ├──► [S1] Semantic Similarity (all-MiniLM-L6-v2, w = 0.15)
  │      └─ Cosine similarity against reference answer
  │
  ├──► [S2] Knowledge Concept Coverage (FAISS Index, w = 0.35)
  │      └─ Max sentence cosine similarity against rubric concept groups (θ = 0.42)
  │      └─ Dampened: S2_eff = (S2 if R > 0.30 else 0.60 * S2)
  │
  └──► [R]  Reasoning & Entailment (Fine-Tuned CrossEncoder, w = 0.50)
         └─ Joint cross-attention over question-answer pair
```

---

## 2. Mathematical Formulation of the Technical Score

$$S_{\text{tech}} = \text{clip}\Big( 0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R + \text{Bonus} - \text{Penalty},\ 0.0,\ 1.0 \Big)$$

If the candidate misses any mandatory concept ($\text{mandatory\_pass} = \text{False}$), the final technical score is capped:

$$S_{\text{tech}} = \min\big(S_{\text{tech}},\ \text{mandatory\_cap}\big) \qquad (\text{default } \text{mandatory\_cap} = 0.60)$$

---

## 3. Detailed Component Specifications

### 3.1 S1 — Semantic Similarity ($w = 0.15$)
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors).
- **Operation:** Computes cosine similarity between the candidate's full answer embedding $\mathbf{e}_{\text{cand}}$ and the rubric reference answer embedding $\mathbf{e}_{\text{ref}}$:
  $$S_1 = \max\left(0.0,\ \frac{\mathbf{e}_{\text{cand}} \cdot \mathbf{e}_{\text{ref}}}{\|\mathbf{e}_{\text{cand}}\| \|\mathbf{e}_{\text{ref}}\|}\right)$$
- **Role:** Broad topical grounding; intentionally assigned a low weight ($0.15$) to prevent memorized phrasing from inflating scores.

### 3.2 S2 — Concept Coverage via FAISS ($w = 0.35$)
- **Vector Store:** FAISS index storing pre-computed 384-dimensional embeddings of all concept groups across rubrics.
- **Operation:** For each required concept group $C_j$ in the rubric, computes the maximum cosine similarity across all individual sentences $s_k$ in the candidate's transcript:
  $$\text{Sim}(C_j) = \max_{s_k \in \text{Sentences}} \cos(\mathbf{e}_{C_j}, \mathbf{e}_{s_k})$$
  A concept group is considered *covered* if $\text{Sim}(C_j) \ge \theta_{\text{concept}} = 0.42$.
  $$S_2 = \frac{\sum_{j=1}^M \mathbb{I}[\text{Sim}(C_j) \ge 0.42]}{M}$$
- **Anti-Keyword Dampening Rule:**
  $$S_{2,\text{eff}} = \begin{cases}
  S_2 & \text{if } R > 0.30 \\
  0.60 \times S_2 & \text{if } R \le 0.30 \text{ (low reasoning dampening)}
  \end{cases}$$

### 3.3 R — Reasoning & Entailment ($w = 0.50$)
- **Model:** Fine-tuned CrossEncoder (`models/tuned_model2`) based on `cross-encoder/ms-marco-MiniLM-L-12-v2`.
- **Operation:** Jointly encodes the concatenated question-answer pair $(Q, A)$ through 12 cross-attention transformer layers, producing a raw logit converted to $[0, 1]$ via sigmoid:
  $$R = \sigma(\text{CrossEncoder}(Q \oplus A))$$
- **Role:** Captures logical coherence, causal explanation, and conceptual entailment. Assigned the highest weight ($0.50$) because technical interviews prioritize understanding over keyword recitation.

---

## 4. Bonus, Mistake Penalty & Mandatory Checks

1. **Insight Bonus (+0.03 to +0.05):** Awarded when the candidate explains advanced concepts (e.g. cache locality, amortized complexity) specified in the rubric's `advanced_bonus` list. A negation filter blocks "avoid X" from triggering the bonus for X.
2. **Mistake Penalty (-0.07 per mistake, max -0.30):** Applied when candidate assertions exceed $\theta = 0.55$ similarity against rubric `common_mistakes`.
3. **Mandatory Concept Check:** Rubrics designate non-negotiable concepts (e.g. stating $O(N)$ time complexity). Omission caps the final score at $0.60$.

---

## 5. Grade Classification Boundaries

| Calibrated Score Range | Formative Grade | Qualitative Description |
|---|---|---|
| $[0.75, 1.00]$ | **Excellent** | Comprehensive understanding, optimal algorithms, rigorous complexity analysis |
| $[0.60, 0.75)$ | **Good** | Solid foundational logic, minor edge case or efficiency omissions |
| $[0.40, 0.60)$ | **Average** | Partial answer, key mechanisms omitted, hand-wavy explanations |
| $[0.00, 0.40)$ | **Poor** | Severe conceptual gaps, invalid reasoning, or off-topic response |

---

## 6. Empirical Validation & Claims Status

| Evaluator Claim | Status | Empirical Repository Evidence |
|---|---|---|
| 3-Component ($S_1 + S_2 + R$) pipeline implementation | **`TESTED`** | Implemented in `services/evaluator/app.py`; verified via 13 unit tests in `test_evaluator.py` |
| Component weights ($0.15/0.35/0.50$) calibration | **`EXPERIMENTALLY VALIDATED`** | 7-configuration ablation study on 20 samples ($\rho = 0.8358, p = 4.46 \times 10^{-6}$) |
| Human inter-rater reliability among raters | **`HUMAN VALIDATED`** | 3 independent human raters on 20 samples, Krippendorff's $\alpha = 0.8255$ |
| Full-system candidate skill improvement | **`NOT YET VALIDATED`** | Longitudinal pre/post human trial required |
