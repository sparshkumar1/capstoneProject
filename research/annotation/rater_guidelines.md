# Human Rater Guidelines: Technical Answer Evaluation

## 1. Purpose
These guidelines define the standardized protocol for human expert evaluation of technical interview answers to Data Structures and Algorithms (DSA) and systems questions. These ratings serve as ground-truth baselines for evaluating the PREPAIred multi-signal evaluation pipeline.

---

## 2. Evaluation Scale (0.00 – 1.00)

Human raters assign an overall technical quality score on a bounded continuous scale from 0.00 to 1.00:

| Score Band | Rating Label | Qualitative Description | Example Characteristics |
|---|---|---|---|
| **0.85 – 1.00** | **Optimal / Complete** | Fully correct, optimal time/space complexity, covers key mechanisms, clear edge case handling. | Accurately explains 1-pass hash table with (N)$ time and (N)$ space; details pointer redirection with 3 pointers. |
| **0.65 – 0.84** | **Correct / Suboptimal or Minor Gaps** | Algorithmic logic is correct but relies on suboptimal complexity or omits minor implementation details. | Correct 2-pass approach or (N^2)$ brute force where optimal exists, but logic is sound and fully explained. |
| **0.40 – 0.64** | **Partial / Incomplete** | Mentions the correct general direction or core data structure but lacks procedural steps or leaves major gaps. | States 'use a hash map' or 'use two pointers' without explaining how lookups or pointer updates occur. |
| **0.15 – 0.39** | **Superficial / Misconception** | Significant technical misconceptions, flawed logic, or superficial domain buzzwords without substance. | Conflates BFS with DFS; claims reversing a linked list requires allocating a new array for all nodes. |
| **0.00 – 0.14** | **Unacceptable / Off-Topic** | Irrelevant, completely incorrect, evasive ('I do not know'), empty, or random keyword stuffing. | Explains sorting when asked for hash table two-sum; ungrounded list of buzzwords. |

---

## 3. Sub-Criteria Rationale

When determining the score, raters should consider three distinct facets:

1. **Semantic Relevance ($ equivalent):** Does the answer address the specific prompt asked, or does it deflect to general conversational or introductory filler?
2. **Concept Coverage ($ equivalent):** Are essential algorithmic terminology and structural primitives mentioned (e.g., hash table, pointer, queue, FIFO, recursive base cases)?
3. **Reasoning Entailment ($ equivalent):** Are the concepts logically connected into a valid causal sequence? Does the explanation actually solve the problem, or does it merely mention the words?

### Keyword Stuffing Warning:
> **Critical Rule:** If a candidate simply lists keywords (e.g., *'hash map, array indices, lookup, target minus value, (n)$'*) without grammatical or algorithmic structure explaining the step-by-step logic, the score **MUST NOT** exceed **0.40**.

---

## 4. Rater Blinding & Independence
- Raters must evaluate responses without seeing:
  - System scores ($, $, $, composite score).
  - Candidate identity, speech features, or history.
  - Ratings of any other evaluators.
- Responses must be presented in randomized order.
