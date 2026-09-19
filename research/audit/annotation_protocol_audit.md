# Annotation Protocol Audit Report

**Audit Target:** PREPAIred Human Annotation Protocol and Guidelines  
**Audited Artifacts:**
- `research/annotation/rater_guidelines.md`
- `research/annotation/rating_template_64cases.csv`
- `research/annotation/README.md`  
**Audited Checkpoint Commit:** `1b11c1ab48d774a5d2db34df50834b07e0fd0810`  
**Audit Date:** September 19, 2026  
**Status:** **AUDITED & BLINDING VERIFIED**

---

## 1. Exact Rating Scale Classification

- **Rating Scale Type:** **Bounded Continuous with Qualitative Anchors (Mixed Continuous-Anchored)**.
- **Range:** $s \in [0.00, 1.00]$.
- **Anchor Bands:**
  - `0.85 – 1.00`: Optimal / Complete (Optimal complexity, comprehensive mechanisms, sound reasoning).
  - `0.65 – 0.84`: Correct / Suboptimal or Minor Gaps (Sound logic with suboptimal complexity or minor omitted details).
  - `0.40 – 0.64`: Partial / Incomplete (Core concept mentioned, procedural steps omitted, noticeable conceptual gaps).
  - `0.15 – 0.39`: Superficial / Misconception (Severe logical flaws, misconceptions, pseudo-technical vocabulary).
  - `0.00 – 0.14`: Unacceptable / Off-Topic (Evasive, empty, off-topic, or ungrammatical keyword dump).
- **Scale Integrity Directive:** This continuous $[0.0, 1.0]$ scale is preserved as frozen. It matches the evaluator model output range $[0.0, 1.0]$ and enables direct Spearman $\rho$, Pearson $r$, and MAE calculations without loss of resolution.

---

## 2. Evaluation Rubric Coverage of Response Typologies

The protocol was audited against the 11 benchmark typologies to confirm explicit guidance exists:

| Response Typology | Assigned Guidance in Rubric | Handled Clearly? | Score Guidance |
| :--- | :--- | :---: | :--- |
| **Correct** | Section 2: Optimal / Complete band | Yes | $0.85 - 1.00$ |
| **Partial** | Section 2: Partial / Incomplete band | Yes | $0.40 - 0.64$ |
| **Wrong** | Section 2: Unacceptable / Off-Topic band | Yes | $0.00 - 0.14$ |
| **Concise Correct** | Section 2: Crisp, optimal explanation covering key mechanisms | Yes | $0.85 - 1.00$ |
| **Verbose Correct** | Section 3.1: Conversational / introductory filler must not penalize correct logic | Yes | $0.85 - 1.00$ |
| **Verbose Wrong** | Section 2 & 3.3: Fluent prose containing flawed logic or invalid assertions | Yes | $0.15 - 0.39$ or $\le 0.14$ |
| **Keyword Stuffing** | Section 3: Explicit **Mandatory Cap** ($s \le 0.40$) for ungrammatical jargon lists | Yes | $\le 0.40$ (Hard Ceiling) |
| **Paraphrase** | Section 3.2 & 3.3: Focuses on causal logic and conceptual primitives over verbatim tokens | Yes | Equal to semantic reference ($0.85 - 1.00$) |
| **Contradiction** | Section 2: Significant technical flaws, conflicting claims | Yes | $0.15 - 0.39$ |
| **Concept Missing** | Section 2: Core structure present but execution/mechanics omitted | Yes | $0.40 - 0.64$ |
| **Misconception** | Section 2: Categorical errors (e.g. conflating BFS queue with stack) | Yes | $0.15 - 0.39$ |

---

## 3. Category Identity & Blinding Verification

- **Blinding Rule:** Raters must NEVER be informed of the intended typology category, model predictions, or evaluation hypotheses.
- **Audit of `rating_template_64cases.csv`:**
  - Header: `item_id,question_id,topic,question,candidate_answer,score_0_to_1,rater_comments`
  - Field Inspection:
    - [x] No `category` or `expected_quality_category` column.
    - [x] No `evaluator_score`, `model_score`, or benchmark predictions.
    - [x] No rater identifiers or inter-rater information.
    - [x] No hypothesis description (e.g., testing keyword stuffing threshold $\theta = 0.30$).
  - **Verification:** The annotation template is **100% blinded**.

---

## 4. Documented Protocol Ambiguities & Nuances

In accordance with scientific honesty principles, three nuances in the frozen protocol are documented for human raters:
1. **Suboptimal Time Complexity Threshold:**
   - *Observation:* Answers proposing $O(N^2)$ brute-force solutions for Two Sum or naive recursion for Climbing Stairs are sound in logic but suboptimal in performance. The rubric places these in `0.65 – 0.84`. Individual raters may vary between $0.60$ and $0.75$.
   - *Protocol Guidance:* Raters are advised that logically sound brute-force implementations should anchor near $0.65 - 0.70$.
2. **Continuous Decimal Precision:**
   - *Observation:* Raters may ask whether scores must be discrete steps (e.g., $0.10, 0.25, 0.50$) or continuous decimals (e.g., $0.72$).
   - *Protocol Guidance:* Any floating-point value in $[0.00, 1.00]$ is valid; increments of $0.05$ or $0.10$ are standard.
3. **Contradiction Boundary:**
   - *Observation:* Answers that start with a valid statement and immediately follow with an invalid reversal (e.g., BM-008: "Use a hash map... but hash maps do not allow lookups and you have to search linearly") fall under "Superficial / Misconception" ($0.15 - 0.39$).
   - *Protocol Guidance:* Such responses are capped at $\le 0.35$ because the contradictory statement invalidates algorithmic correctness.
