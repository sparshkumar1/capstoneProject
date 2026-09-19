# Technical Answer Evaluation: Scoring Guidelines & Rubric

## 1. Overview & Objective
You are asked to evaluate candidate answers to technical interview questions covering Computer Science fundamentals: Data Structures, Algorithms, C Memory Management, and Concurrency.

Your evaluations provide independent ground-truth judgments of technical quality.

---

## 2. Evaluation Scale (0.00 – 1.00)
Assign an overall score as a decimal value from **0.00** (completely unacceptable/incorrect) to **1.00** (optimal, complete, and thoroughly explained).

| Score Band | Qualitative Rating | Description & Core Characteristics |
| :---: | :--- | :--- |
| **0.85 – 1.00** | **Optimal / Complete** | Fully correct, achieves optimal time/space complexity, accurately explains underlying mechanisms, covers relevant edge cases. Clear and coherent. |
| **0.65 – 0.84** | **Correct / Suboptimal or Minor Gaps** | Algorithmic logic is sound and correct, but relies on a suboptimal complexity (e.g. brute-force where an optimal approach exists) or omits minor implementation details. |
| **0.40 – 0.64** | **Partial / Incomplete** | Mentions the correct general direction or core data structure (e.g. 'use a hash map') but lacks step-by-step procedural mechanics or leaves significant gaps. |
| **0.15 – 0.39** | **Superficial / Misconception** | Exhibits significant technical misconceptions, contradictory statements, or uses technical jargon without understanding. |
| **0.00 – 0.14** | **Unacceptable / Off-Topic** | Irrelevant, completely incorrect, evasive ('I don't know'), empty, or random keyword list. |

---

## 3. Evaluation Criteria
When evaluating each answer, consider three fundamental aspects:
1. **Relevance & Problem Alignment:** Does the answer directly address the specific question asked, or does it deflect to general filler?
2. **Concept Accuracy:** Are key data structures and algorithmic operations correctly identified and explained?
3. **Reasoning & Causality:** Are steps logically connected into a valid causal sequence that actually solves the problem?

### Keyword Stuffing & Jargon Policy:
If an answer simply recites keywords or jargon without coherent grammatical or algorithmic structure explaining the step-by-step logic, the score **MUST NOT exceed 0.40**.

---

## 4. Rating Instructions
1. Open `RATING_SHEET_64_CASES.csv` in your preferred spreadsheet editor (Excel, Google Sheets, or text editor).
2. For each of the 64 items, read the Question and Candidate Answer.
3. Enter your score in the `score_0_to_1` column (e.g., `0.85`, `0.70`, `0.35`). Any decimal in `[0.00, 1.00]` is valid.
4. (Optional) Provide brief notes or rationale in the `rater_comments` column.
5. Save the completed file and return it to the study administrator.
