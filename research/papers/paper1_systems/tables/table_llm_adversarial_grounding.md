# Adversarial Feedback Grounding & Fallback Verification (EXP-LLM-1)

Evaluation of FeedbackAgent on adversarial and out-of-distribution evaluation outputs:

| Case ID | Adversarial Scenario | Evaluator Score | Feedback Score | Score Invariant Preserved? | Concepts Grounded? | Decision Source |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| ADV-01 | **Complete Concept Omission (Score 0.0)** | 0.00 | 0.00 | **YES** | **YES** | `evaluator_structured` |
| ADV-02 | **Asserted Algorithmic Misconception** | 0.35 | 0.35 | **YES** | **YES** | `evaluator_structured` |
| ADV-03 | **Empty Response (0 Words)** | 0.00 | 0.00 | **YES** | **YES** | `evaluator_structured` |
| ADV-04 | **Adversarial Keyword Stuffed Response** | 0.42 | 0.42 | **YES** | **YES** | `evaluator_structured` |
| ADV-05 | **Contradictory / Edge Case Claims** | 0.45 | 0.45 | **YES** | **YES** | `evaluator_structured` |
