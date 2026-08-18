# PrepAIred — Personalization & Dynamic Question System

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Personalization Principles & Objectives

The PrepAIred personalization engine is designed to dynamically adapt question sequencing to the candidate's real-time performance, conceptual gaps, and pacing, avoiding repetitive questioning while ensuring foundational validation:

1. **Foundational Easy/Easy-Medium Guarantee:** Question 1 is strictly constrained to difficulty $\le 2$ (Easy / Easy-Medium) to establish an accurate baseline without cognitive overload.
2. **Multi-Level Deduplication:** Ensures candidates never encounter identical or semantically repetitive questions within a session.
3. **Adaptive Weakness Remediation:** Candidates struggling on a concept receive targeted foundational probes before escalating difficulty.
4. **Adaptive Strength Advancement:** Candidates demonstrating high mastery on foundational concepts are probed with deeper trade-off questions.
5. **Format Balancing:** Alternates between conceptual verbal questions and sandboxed C coding questions based on session progress.

---

## 2. Three-Level Deduplication Architecture

The authoritative question selector ([`apps.backend.main:select_questions`](apps/backend/main.py#L461-L570)) implements three complementary filtering layers:

```
Question Pool (125 Questions)
  │
  ├──► Level 1: Exact Question ID Filtering (seen_ids)
  │      └─ Excludes all previously asked or queued question IDs
  │
  ├──► Level 2: Normalized Text String Matching (seen_texts)
  │      └─ Lowercases, strips punctuation, and matches exact text strings
  │
  └──► Level 3: Lexical Jaccard Token Overlap Filtering (threshold >= 0.75)
         └─ Computes word set intersection over union against all session questions
         └─ Blocks near-duplicate variants and paraphrased question clones
```

### Jaccard Lexical Similarity Formula

$$\text{Jaccard}(Q_A, Q_B) = \frac{|T(Q_A) \cap T(Q_B)|}{|T(Q_A) \cup T(Q_B)|}$$

Where $T(Q)$ is the set of alphanumeric tokens of length $\ge 3$ excluding English stop words. Any candidate question with $\text{Jaccard} \ge 0.75$ against any question in the candidate's session history is rejected.

---

## 3. Dynamic Selection Scoring Function

When selecting questions from the candidate pool, each eligible question $q$ is scored according to:

$$\text{Score}(q) = \text{Penalty}_{\text{diff}}(q) + \text{Penalty}_{\text{diversity}}(q) + \text{Bonus}_{\text{adaptation}}(q)$$

1. **Difficulty Proximity Penalty:**
   $$\text{Penalty}_{\text{diff}}(q) = |q.\text{difficulty} - \text{target\_difficulty}|$$
   *(If $q$ is the first question and $q.\text{difficulty} > 2$, add an extra penalty of $+5.0$)*.

2. **Topic Diversity Penalty:**
   $$\text{Penalty}_{\text{diversity}}(q) = \text{count}(\text{topic}) \times 0.40$$
   *(Penalizes topics that have already been asked frequently in the current session)*.

3. **Personalization Adaptation Bonus:**
   $$\text{Bonus}_{\text{adaptation}}(q) = \begin{cases}
   -0.30 & \text{if } q.\text{topic} \in \text{Weaknesses} \text{ and } \text{target\_difficulty} \le 2 \\
   -0.30 & \text{if } q.\text{topic} \in \text{Strengths} \text{ and } \text{target\_difficulty} \ge 4 \\
   0.00 & \text{otherwise}
   \end{cases}$$

The question minimizing $\text{Score}(q)$ is selected and appended to the queue.

---

## 4. Verbal vs. Coding Format Balancing

Questions in the 125-item question bank are categorized into `verbal` (theory, architecture, concept explanation) and `code` (hands-on C implementation).

- The selector maintains two separate pools: `type_buckets["verbal"]` and `type_buckets["code"]`.
- When alternating turns, the selector prioritizes the alternating format unless a candidate demonstrates a streak that necessitates continuous verbal probing (such as addressing consecutive conceptual misconceptions).
- Coding questions provide explicit test harness structures and starter templates executed inside the isolated Docker sandbox.

---

## 5. Empirical Claims Status

| Personalization Claim | Status | Evidence in Repository |
|---|---|---|
| 3-Level Deduplication prevents repeated questions | **`TESTED`** | Verified via `test_personalization_questions.py` |
| Easy/Easy-Medium first question constraint ($\le 2$) | **`TESTED`** | Verified via `test_personalization_questions.py` |
| Trajectory divergence between strong & weak candidates | **`TESTED`** | Verified via `test_e2e_personalization_trajectories.py` |
| Personalization improves human learning outcomes | **`NOT YET VALIDATED`** | Requires future multi-session human trials |
