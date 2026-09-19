# Metamorphic Testing Suite Provenance: 6/7 vs. 13/15 Suites

**Date:** September 2026  
**Status:** COMPLETE & FROZEN  
**Audit Scope:** Provenance, relation definitions, evaluation methodologies, and failure root causes for the 6/7 (7-relation) and 13/15 (15-case cross-topic) metamorphic test suites.

---

## 1. Executive Summary

In PREPAIred's research documentation and Paper 2 manuscripts, two metamorphic pass rates are cited:
1. **6/7 Passed (85.7%):** Evaluated in `research/scripts/run_paper2_study.py` on Question 1 (Arrays & Hashing) across 7 distinct metamorphic transformation relations.
2. **13/15 Passed (86.7%):** Evaluated in `research/scripts/run_metamorphic_tests.py` and documented in `research/results/metamorphic_final_analysis.md`, expanding 5 core metamorphic relations across 3 diverse DSA topics (Arrays, Linked Lists, Binary Trees).

Both suites are authentic, reproducible, and complementary. Neither is an error or contradiction; they represent two distinct evaluation granularities:
- The **7-Relation Suite** tests a broad spectrum of semantic and syntactic transformations (including reordering and repetition) on a single canonical question.
- The **15-Case Multi-Topic Suite** stress-tests the 5 primary relations across diverse data structure paradigms to evaluate generalization.

---

## 2. Detailed Comparison of the Two Suites

| Attribute | 7-Relation Suite (6/7 Pass) | 15-Case Multi-Topic Suite (13/15 Pass) |
| :--- | :--- | :--- |
| **Execution Script** | `research/scripts/run_paper2_study.py` (lines 155–200) | `research/scripts/run_metamorphic_tests.py` |
| **Primary Documentation** | `research/results/paper2_final_results.md` | `research/results/metamorphic_final_analysis.md`, `research/tables/metamorphic_results.md` |
| **Question Coverage** | 1 DSA Problem (Q1: Arrays & Hashing / Two Sum) | 3 DSA Problems (Q1: Arrays, Q3: Linked Lists, Q10: Binary Trees) |
| **Relations Tested** | 7 Relations:<br>• MG-1: Paraphrase Invariance<br>• MG-2: Irrelevant Text Addition<br>• MG-3: Concept Deletion<br>• MG-4: Negation Inversion<br>• MG-5: Keyword Injection<br>• MG-6: Sentence Reordering<br>• MG-7: Duplicate Sentence Addition | 5 Core Relations across 3 Problems (15 total cases):<br>• Paraphrase Invariance (3 cases)<br>• Irrelevant Text Addition (3 cases)<br>• Keyword Injection (3 cases)<br>• Concept Deletion (3 cases)<br>• Negation Inversion (3 cases) |
| **Pass Rate** | **6 / 7 (85.7%)** | **13 / 15 (86.7%)** |
| **Specific Failures** | **MG-1 (Paraphrase Invariance):** Failed ($\Delta = -0.1885$, exceeded $|\Delta| \le 0.10$). | **MG-3 (Keyword Injection):** Failed in Linked Lists (Score = $0.5781 > 0.50$) and Binary Trees (Score = $0.6644 > 0.50$). |

---

## 3. Analysis of Specific Failures

### 3.1 Failure in 7-Relation Suite: MG-1 (Paraphrase Invariance on Q1)
- **Base Answer:** Standard Two Sum explanation using hash map and complement ($s = 0.6386$).
- **Transformed Text:** *"A hash table is used to save elements previously seen and their positions. During a pass over the array, for item x we calculate target - x. If this difference is already in the table, output both positions. If not, insert x and its index."*
- **Transformed Score:** $0.4501$ ($\Delta = -0.1885$, failing $|\Delta| \le 0.10$).
- **Root Cause:** SBERT and FAISS exhibit lexical sensitivity when candidates substitute canonical DSA vocabulary (e.g., using "positions" instead of "indices", "save" instead of "store"). While the semantic meaning is preserved, concept matching cosine similarities dropped below threshold.
- **Scientific Decision:** Reported honestly without post-hoc tuning to demonstrate that embedding-based evaluators retain residual lexical sensitivity.

### 3.2 Failures in 15-Case Suite: MG-3 (Keyword Injection on Linked Lists & Trees)
- **Linked Lists Keyword Injection (META-02):**
  - Payload: `"Three pointers prev curr next pointer redirection in-place O(1) memory head update reverse singly linked list."`
  - Score: $0.5781 > 0.50$ (**FAIL**).
  - CrossEncoder reasoning entailment: $R = 0.519 > 0.30$.
- **Binary Trees Keyword Injection (META-03):**
  - Payload: `"Queue FIFO level order breadth first search root left child right child depth order traversal enqueue dequeue."`
  - Score: $0.6644 > 0.50$ (**FAIL**).
  - CrossEncoder reasoning entailment: $R = 0.465 > 0.30$.
- **Root Cause:** In dense keyword lists containing all required domain vocabulary, the pre-trained MiniLM CrossEncoder cross-attention attends strongly to lexical overlap with reference answers, generating $R > 0.30$. Because $R > 0.30$, reasoning dampening ($S_{2,\text{eff}} = S_2 \times 0.60$) does not trigger.
- **Architectural Remedy:** This failure directly motivated the implementation of the **ScoreValidator** syntactic guardrail, which checks for grammatical structure and caps ungrounded keyword strings at $\le 0.40$.

---

## 4. Publication Reporting Directives for Paper 2

1. **Table Presentation:**
   - Present both suites clearly labeled:
     - *Table A: 7-Relation Single-Problem Metamorphic Robustness (Pass Rate: 6/7, 85.7%)*
     - *Table B: Cross-Topic Metamorphic Generalization (Pass Rate: 13/15, 86.7%)*
2. **Scientific Transparency:**
   - Explicitly discuss the failures (MG-1 lexical sensitivity and MG-3 CrossEncoder keyword attention) as positive proof that PREPAIred's hybrid architecture (SBERT + FAISS + CrossEncoder + deterministic ScoreValidator guardrails) is necessary to close vulnerabilities that pure neural models cannot handle alone.
