# PrepAIred — Formative Feedback & Reporting System

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Formative Feedback Philosophy

Effective educational feedback in technical interview preparation must be **grounded in evidence, constructive, transparent, and actionable**. Generic praise or unanchored LLM critiques fail to help candidates diagnose specific cognitive misconceptions.

PrepAIred anchors all candidate-facing feedback directly on:
1. **Verbatim Transcript Evidence:** Quotes the candidate's actual assertions without synthetic paraphrasing.
2. **Evaluator Decomposition:** Exposes covered concepts ($S_2$), reasoning entails ($R$), and specific missing logic markers.
3. **Actionable Remediation:** Provides 2–3 concrete steps the candidate can take to elevate their answer to staff-level clarity.
4. **Pacing Diagnostics:** Reports timing quality without penalizing thoughtful pacing.

---

## 2. Structured Feedback Contract

Following each turn, `FeedbackAgent` (`agents/orchestrator/feedback_agent.py`) produces a rich feedback dictionary conforming to:

```json
{
  "final_score": 0.7250,
  "grade": "Good",
  "score_breakdown": {
    "semantic_similarity": 0.81,
    "concept_coverage": 0.67,
    "reasoning_quality": 0.75,
    "timing_modifier": 0.00
  },
  "what_candidate_said": "I used a hash map to store elements as I iterate...",
  "what_was_correct": [
    "Hash map lookup provides O(1) average time complexity",
    "Single-pass traversal approach"
  ],
  "what_was_incorrect": [],
  "what_was_incomplete": [
    "Did not specify memory space complexity trade-off"
  ],
  "missing_concepts": [
    "Auxiliary space complexity O(N)"
  ],
  "how_to_answer": "For Two Sum, articulate the hash map complement calculation clearly and state both time and auxiliary space complexity upfront.",
  "stronger_answer_guide": "Structure your answer in three phases: (1) Core algorithm, (2) Invariants, (3) Space-time complexity bounds.",
  "actionable_improvements": [
    "State auxiliary space complexity explicitly",
    "Trace through a duplicate-element example"
  ],
  "narrative_feedback": "Solid response (72.5%). You demonstrated clear understanding of the hash map approach...",
  "decision_source": "qwen_7b_llm",
  "llm_status": "available"
}
```

---

## 3. Feedback Tone & Adaptive Guidance

The narrative feedback adapts its tone based on the candidate's performance grade:

- **Excellent ($\ge 0.75$):** Concise reinforcement, praises algorithmic precision, suggests staff-level optimizations (cache locality, memory footprint, concurrency).
- **Good ($[0.60, 0.75)$):** Encouraging tone, highlights correct algorithmic direction, identifies missing edge cases or complexity derivations.
- **Average ($[0.40, 0.60)$):** Constructive tone, explicitly bridges correct intuition to missing mechanistic steps.
- **Poor ($< 0.40$):** Supportive and foundational, diagnoses the exact misconception, provides a 2-sentence model explanation, and advises tracing small examples.

---

## 4. Code Feedback & Compilation Diagnostics

For hands-on coding questions, `FeedbackAgent.generate_code_feedback` provides compiler-level and runtime diagnostics:

- **Accepted:** Reports full test pass rate, execution duration (ms), memory footprint, and suggests refactoring for clean code and comments.
- **Wrong Answer:** Identifies failing test cases without spoiling private solutions, advising on boundary testing.
- **Compilation Error:** Extracts GCC error snippets, line numbers, and actionable compiler fix advice.
- **Runtime Error (Segfault):** Flags null-pointer dereference or out-of-bounds indexing patterns (`malloc` without NULL checks).
- **Timeout / Memory Limit:** Pinpoints infinite loops or recursive stack overflows.

---

## 5. Empirical Claims Status

| Feedback System Claim | Status | Repository Evidence |
|---|---|---|
| Grounded feedback structure with all required fields | **`TESTED`** | `test_stage11_3_followup_and_evaluation.py` |
| Verbatim transcript grounding without fabrication | **`TESTED`** | `test_qwen_followup_feedback.py` |
| Formative feedback improves candidate learning | **`NOT YET VALIDATED`** | Longitudinal pre/post trial required |
