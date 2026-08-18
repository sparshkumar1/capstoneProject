# Experiment 3 — Formative Feedback Grounding & Actionability Comparison

**Experiment ID:** EXP-3
**Target Submission:** IEEE ICALT 2026 / IEEE EDUCON 2026 (Section IV & V)
**Priority:** **MEDIUM PRIORITY**

---

## 1. Research Question & Pre-Registered Hypothesis

- **Research Question:** Does candidate-specific structured feedback differ measurably from generic feedback in transcript grounding, misconception diagnosis, and actionable remediation?
- **Pre-Registered Hypothesis:** Candidate-specific structured feedback achieves significantly higher verbatim transcript grounding, higher coverage of rubric gaps, and zero hallucinated claims compared to static generic feedback templates.

---

## 2. Feedback Conditions (Independent Variable)

1. **Condition A — Generic Template Baseline:** Static score-bracket text templates (e.g. *"Average response. Practice your technical explanation and memory complexity."*) providing zero individualized concept diagnoses.
2. **Condition B — Evaluator-Structured Non-LLM Feedback:** Deterministic feedback generated from Stage 1 Evaluator metadata (listing exact covered concepts, missing concepts, and score breakdown).
3. **Condition C — Qwen-7B Grounded Formative Feedback:** LLM-synthesized narrative feedback incorporating verbatim candidate transcript quotes, targeted misconception corrections, and step-by-step remediation advice.

---

## 3. Dependent Variables & Metrics

1. **Transcript Lexical Grounding Ratio:** Jaccard overlap between feedback vocabulary and candidate spoken answer:
   $$\text{Grounding Ratio} = \frac{|T_{\text{feedback}} \cap T_{\text{candidate}}|}{|T_{\text{candidate}}|}$$
2. **Rubric Gap Coverage:** Proportion of rubric concepts labeled as missing ($S_2 < 0.42$) that are explicitly addressed in the feedback advice.
3. **Actionability Index:** Count of distinct imperative remediation directives (e.g. *"State auxiliary space complexity"*, *"Verify NULL pointers"*).
4. **Hallucination Proxy Rate:** Frequency with which feedback attributes claims or terms to the candidate that were not present in the transcript.

---

## 4. Execution Command (Stage 16)

```bash
python experiments/experiment_3_feedback/runner.py --config experiments/experiment_3_feedback/config.json
```

*Results Status in Stage 15:* **RESULTS NOT YET GENERATED (Design & Pre-Registration Frozen)**
