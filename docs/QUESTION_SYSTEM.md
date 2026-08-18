# PrepAIred — Question & Rubric Bank Specification

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Dataset Overview & Scope

The PrepAIred technical curriculum is grounded in a curated bank of **125 rubric-annotated questions** covering core C systems programming and foundational Data Structures & Algorithms:

- **Total Questions:** 125 curated technical problems in [`data/questions/qns.json`](data/questions/qns.json).
- **Total Rubrics:** 125 corresponding fine-grained rubrics in [`data/rubrics/rubrics_final_clean.json`](data/rubrics/rubrics_final_clean.json).
- **Curriculum Domains:**
  - **C Systems Programming:** Pointers, Memory Management (`malloc`/`free`), Bit Manipulation, Storage Classes, Linkage, Preprocessor, Structs & Unions, Enums, Advanced C.
  - **Data Structures & Algorithms:** Arrays, Strings, Linked Lists, Stacks, Queues, Binary Trees, BSTs, Heaps, Graph Representations & Traversals, Sorting Algorithms, Binary Search, Dynamic Programming, Backtracking, Recursion, Amortized Analysis.

---

## 2. Question Schema Specification

Every question object adheres to the following canonical JSON schema:

```json
{
  "id": "q_two_sum",
  "text": "Explain your approach to find two indices in an array that add up to a target sum.",
  "type": "verbal",
  "difficulty": 3,
  "difficulty_float": 0.6,
  "topic": "arrays",
  "category": "dsa",
  "time_limit_sec": 75,
  "bloom_level": "L3",
  "expected_concepts": [
    "Hash map for O(1) lookup",
    "Calculate complement target minus current",
    "Single-pass O(N) time complexity"
  ],
  "mandatory_concepts": [
    "Time complexity comparison"
  ],
  "common_mistakes": [
    "Nested loops quadratic overhead",
    "Handling duplicate elements incorrectly"
  ],
  "reference_answer": "An optimal single-pass approach uses a hash map storing value to index mappings...",
  "constraints": "Array size up to 10^5, exactly one valid solution exists",
  "code_template": "int* twoSum(int* nums, int numsSize, int target, int* returnSize) {\n    // Implementation\n}"
}
```

---

## 3. Rubric Schema & Logic Markers

Each rubric provides the structured ground truth utilized by the Stage 1 Evaluator (`services/evaluator/`):

```json
{
  "qid": "q_two_sum",
  "logic_context": "Reference solution explanation...",
  "logic_markers": {
    "mandatory": [
      "Time complexity stated as O(N)"
    ],
    "concept_groups": [
      ["Hash map lookup", "Hash table", "Hash map"],
      ["Complement calculation", "target minus current value"],
      ["Single-pass traversal", "linear scan"]
    ],
    "advanced_bonus": [
      "Handling collisions in hash map",
      "Memory space trade-off analysis"
    ]
  },
  "common_mistakes": [
    "Suggesting brute force O(N^2) as optimal",
    "Claiming sorting without accounting for O(N log N) overhead"
  ],
  "scoring_policy": {
    "mandatory_cap": 0.60,
    "bonus_weight": 0.05,
    "penalty_weight": 0.07
  }
}
```

---

## 4. Difficulty & Format Distribution

- **Difficulty Levels (1–5 scale):**
  - Level 1 (Beginner / Foundational): ~10%
  - Level 2 (Easy): ~20%
  - Level 3 (Intermediate): ~40%
  - Level 4 (Advanced): ~20%
  - Level 5 (Staff / Hard): ~10%
- **Format Distribution:**
  - `verbal` (Theory, architecture, conceptual explanations): ~75%
  - `code` (Interactive C implementation in Docker sandbox): ~25%

---

## 5. Empirical Claims Status

| Question System Claim | Status | Repository Evidence |
|---|---|---|
| 125 curated questions and matching rubrics | **`TESTED`** | Implemented in `data/questions/` and `data/rubrics/`; verified via `test_personalization_questions.py` |
| Valid metadata (IDs, topics, concepts, templates) | **`TESTED`** | Verified via `test_personalization_questions.py` |
| Curriculum scope designed by CS educators | **`TESTED`** | Curated and reviewed by experienced CS educators; validated via schema tests |
