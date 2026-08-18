# PrepAIred — Adaptive Follow-Up Questioning System

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Follow-Up Generation Philosophy

A hallmark of high-quality human technical interviewers is the ability to ask **targeted, evidence-grounded follow-up questions** when a candidate leaves a conceptual gap, asserts a misconception, or gives an incomplete answer.

In PrepAIred, follow-up questions are strictly auxiliary pedagogical probes designed to:
1. **Probe Misconceptions Directly:** Help candidates identify and correct flawed assumptions.
2. **Bridge Missing Mechanisms:** Probe partially correct answers to elicit step-by-step invariants.
3. **Explore Architectural Extensions:** Challenge strong candidates with edge cases, concurrency, and space-time trade-offs.
4. **Prevent Infinite Probing:** Enforce a strict hard cap to keep the interview on schedule.

---

## 2. Follow-Up Trigger Decision Matrix

Following answer evaluation, the orchestrator evaluates whether to trigger a follow-up:

| Condition | Candidate State / Evaluator Evidence | Trigger Action | Probe Strategy |
|---|---|---|---|
| **Misconception** | $\text{incorrect\_claims} \neq \emptyset$ | **Trigger FU #1** | Probe contradictory edge case where the flawed reasoning fails |
| **Missing Core Concept** | $\text{missing\_concepts} \neq \emptyset \land S_{\text{tech}} \in [0.35, 0.65]$ | **Trigger FU #1** | Ask for the missing operational mechanism or invariant |
| **High Mastery** | $S_{\text{tech}} \ge 0.75 \land \text{grade} = \text{"Excellent"}$ | **Trigger FU #1** | Probe scalability, cache locality, memory overhead, or concurrency |
| **Vague / Low Depth** | $S_{\text{tech}} < 0.40 \land \text{word\_count} < 20$ | **Trigger FU #1** | Prompt for concrete step-by-step variable transition and complexity |
| **Gap Resolved** | Follow-up answer score $\ge 0.70$ | **Proceed to Next** | Stop follow-ups; resume main question queue |
| **Gap Persists** | Follow-up answer score $< 0.50$ | **Trigger FU #2** | Re-probe with alternative phrasing |
| **Hard Cap Reached** | $\text{consecutive\_followups} \ge 2$ | **Proceed to Next** | Enforce hard cap; proceed to next main question |

---

## 3. Two-Turn Hard Cap & Isolation from Baseline Counting

To maintain pacing and prevent derailment:
1. **Consecutive Hard Cap:** At most **2 consecutive follow-up questions** are allowed per main topic before automatically progressing to the next main question.
2. **Main Question Count Isolation:** Follow-up questions increment `followups_count` and log under `followup_history`, but **never** increment `main_questions_count`.
3. **Baseline Phase Protection:** Follow-up questions answered during the baseline phase do not count toward baseline establishment ($N_{\text{main}} \ge 2$).

---

## 4. Live Qwen LLM vs. Deterministic Structured Recovery

```
                             Trigger Follow-Up
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
       [Live Qwen Service]                     [Offline Recovery Path]
      - Ollama / GPU active                   - Microservice offline / error
      - Prompt grounded in gaps               - Deterministic rubric gap probe
      - decision_source: "qwen_1.5b_llm"      - decision_source: "non_llm_structured_recovery"
      - llm_status: "available"               - llm_status: "llm_unavailable"
```

### Attribution Schema

- **Case A (Live LLM):** Output object contains `decision_source = "qwen_1.5b_llm"` and `llm_status = "available"`.
- **Case B (Offline Structured Fallback):** Output object contains `decision_source = "non_llm_structured_recovery"` and `llm_status = "llm_unavailable"`.
- **Zero Fabrication Guarantee:** The system never labels deterministic structured recovery as Qwen LLM generation.

---

## 5. Empirical Claims Status

| Follow-Up Claim | Status | Repository Evidence |
|---|---|---|
| Follow-up trigger decision matrix | **`TESTED`** | `test_stage11_3_followup_and_evaluation.py` |
| 2-Turn hard cap enforcement | **`TESTED`** | `test_stage11_3_followup_and_evaluation.py` |
| Attribution distinction (Live vs Offline) | **`TESTED`** | `test_qwen_followup_feedback.py` |
| Follow-up effectiveness in improving interview outcomes | **`NOT YET VALIDATED`** | Longitudinal human study required |
