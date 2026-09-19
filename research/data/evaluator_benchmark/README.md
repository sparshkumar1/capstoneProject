# PREPAIred Evaluator Benchmark (64-Case Balanced Cross-Domain Dataset)

**Provenance:** Priority 1 Implementation  
**Target Paper:** Paper 2 (*Evidence-Grounded Technical Interview Answer Evaluation*)  
**Cases Count:** $N = 64$ balanced question-answer pairs  
**Dataset Files:**
- `benchmark_dataset.csv`: Delimited tabular representation with blinded labels for rater scoring.
- `benchmark_cases.json`: Structured JSON format containing full rubrics, question metadata, and ground truth categories.

---

## 1. Domain Coverage (8 Fundamental CS Topics)
The benchmark spans 8 essential computer science domains with 8 questions per domain:
1. **Arrays & Vectors:** Dynamic resizing, sliding windows, two-pointer boundaries, contiguous memory layout.
2. **Linked Lists:** Pointer reversal, cycle detection (Floyd's algorithm), dummy head sentinel nodes, node deletion.
3. **Trees & Traversal:** Binary search tree invariants, level-order traversal (BFS queue), DFS recursions, tree height.
4. **Pointers & Memory:** Stack vs. heap allocation, pointer arithmetic, memory leaks, dangling pointers, `free()` semantics.
5. **Dynamic Programming:** Optimal substructure, overlapping subproblems, state transitions, memoization vs. tabulation.
6. **Graphs & Search:** Adjacency list vs. matrix representations, BFS shortest path in unweighted graphs, DFS cycle detection, topological sort.
7. **Binary Search:** Loop termination bounds (`low <= high`), mid-index calculation avoiding integer overflow, invariant maintenance.
8. **Concurrency & Threading:** Race conditions, mutex locking primitives, deadlocks, critical section protection.

---

## 2. Linguistic & Technical Quality Categories (11 Typologies)
To stress-test semantic alignment, concept extraction, and cross-encoder reasoning, the benchmark balances 11 response categories:
- **Correct:** Technically sound, complete explanations covering all required rubric concepts.
- **Partially Correct:** Accurate core logic with 1–2 minor omissions or unstated edge cases.
- **Incorrect:** Conceptually flawed logic or invalid algorithmic assertions.
- **Concise Correct:** Crisp, direct explanations without superfluous filler.
- **Verbose Correct:** Complete, correct answers embedded within extensive technical prose.
- **Verbose Wrong:** Confidently articulated pseudo-technical explanations that are fundamentally flawed.
- **Keyword-Stuffed:** Artificially packed with technical jargon to test reasoning dampening ($R \le 0.30$).
- **Paraphrased:** Mathematically and logically identical to reference answers using alternate terminology.
- **Contradictory:** Mixed statements containing a valid claim immediately contradicted by an invalid assertion.
- **Concept-Missing:** Explanations that accurately describe symptoms but omit the required foundational mechanism.
- **Common Misconceptions:** Widely held student errors (e.g., confusing BFS queue with stack, assuming binary search applies to unsorted arrays).

---

## 3. Human Ground Truth & Blinding Protocols
- **Rater Guidelines:** Documented in `research/annotation/rater_guidelines.md`.
- **Rater Template:** Provided in `research/annotation/rating_template_64cases.csv`.
- **Blinding:** Raters are completely blinded to evaluator predictions, machine learning scores, category assignments, and other raters' decisions.
- **Data Integrity Rule:** Human rater labels for this 64-case suite are currently pending human annotation (`REQUIRES_NEW_DATA`). In strict accordance with scientific integrity guidelines, no synthetic labels or simulated proxy judgments have been fabricated.
