# Adversarial Threshold Provenance: $0.35$ and $0.40$

**Date:** September 2026  
**Status:** COMPLETE & FROZEN  
**Audit Scope:** Provenance, methodology status (exploratory engineering specification vs. pre-registered trial threshold), and operational consumers of the $0.35$ and $0.40$ thresholds across the technical evaluator, adversarial test suites, and RL orchestrator.

---

## 1. Executive Summary & Epistemological Status

Across the PREPAIred research artifacts and test suites, two thresholds appear repeatedly as acceptance ceilings for adversarial and flawed submissions:
- **$\theta_{\text{fail}} = 0.35$**: Used as the maximum allowed score for severe adversarial attacks (contradictions, algorithmic misconceptions, repetitive token stuffing) and the failure threshold in RL pacing.
- **$\theta_{\text{bound}} = 0.40$**: Used as the maximum allowed score for subtle adversarial attacks (correct keywords with flawed reasoning, prompt injection headers) and as the mandatory concept matching threshold (`MANDATORY_THRESHOLD = 0.40`).

### Epistemological Classification:
> **Status:** **Exploratory Engineering Robustness Thresholds** (Post-hoc heuristic calibration).  
> **Explicit Negative Finding:** Neither $0.35$ nor $0.40$ was pre-registered in an open-science registry (e.g., OSF, AsPredicted) prior to system implementation. They were calibrated empirically during Phase 2 development and regression testing to align with the qualitative rubric boundary separating "Poor / Failing" answers from "Marginal / Average" answers.
>
> In all academic publications, these thresholds must be described as **empirically determined engineering criteria**, not pre-registered psychometric baselines.

---

## 2. Traceability Matrix & Operational Consumers

| Threshold Value | Location / Codebase Artifact | Functional Role | Origin / Derivation Method | Epistemic Status |
| :---: | :--- | :--- | :--- | :---: |
| **0.35** | `research/scripts/run_adversarial_suite.py`<br>(ADV-06, ADV-09, ADV-10) | Maximum acceptable evaluator score under severe adversarial vectors (repetition, misconceptions, contradictions). | Bound set to ensure attacks cannot achieve an "Average" grade ($[0.40, 0.70]$). | Exploratory heuristic |
| **0.35** | `research/scripts/generate_benchmark_cases.py`<br>(64-case benchmark) | Target expected score ceiling for adversarial benchmark cases. | Mirrors adversarial suite ceiling to flag pipeline leakage. | Exploratory heuristic |
| **0.35** | `agents/orchestrator/interview_orchestrator.py`<br>(Guardrail G4: Failure Relief) | Trigger for failure relief: two consecutive scores $< 0.35$ forces difficulty decrement. | Pedagogical heuristic: score $< 0.35$ indicates total breakdown in student grasp. | Exploratory heuristic |
| **0.35** | `rl/environment.py`<br>(Reward shaping) | Premature escalation penalty: penalizes agent if it chooses `Harder` when candidate score $< 0.35$. | Reinforcement learning curriculum design. | Exploratory heuristic |
| **0.40** | `services/evaluator/app.py:260`<br>(`MANDATORY_THRESHOLD`) | Hard matching cosine threshold for mandatory concept gating. | Calibrated against SBERT embedding cosine distributions on key CS terms. | Expert heuristic |
| **0.40** | `research/scripts/run_adversarial_suite.py`<br>(ADV-02, ADV-07) | Maximum acceptable evaluator score for hybrid attacks (syntactic score injections, correct terms with invalid reasoning). | Bound set strictly below the $0.45$ threshold to ensure hybrid attacks remain categorized as "Poor". | Exploratory heuristic |
| **0.40** | Rubric Qualitative Boundary | Threshold separating "Poor" ($< 0.40$) from "Average" ($[0.40, 0.70]$). | Pedagogical four-tier grading scale (Poor, Average, Good, Excellent). | Exploratory heuristic |

---

## 3. Empirical Calibration Analysis

### 3.1 Why 0.35 for Blatant Attacks?
In the tripartite formula:
$$\text{BaseScore} = 0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$$
- When an adversary submits pure keyword repetitions (ADV-06) or blatant misconceptions (ADV-09):
  - $S_1$ (cosine semantic similarity) can reach $\approx 0.30 - 0.45$ due to shared lexical vocabulary.
  - $S_2$ (concept coverage) might match 1 or 2 concepts ($\approx 0.25 - 0.50$).
  - However, $R$ (CrossEncoder reasoning entailment) drops to $\le 0.20$.
  - With reasoning dampening active ($R \le 0.30 \implies S_{2,\text{eff}} = S_2 \times 0.60$):
    $$\text{Score} \approx 0.15(0.35) + 0.35(0.30 \times 0.60) + 0.50(0.15) = 0.0525 + 0.063 + 0.075 = 0.1905$$
  - The ceiling of $0.35$ provides an upper bound that accommodates embedding noise while guaranteeing the response never passes into an acceptable grade.

### 3.2 Why 0.40 for Subtle Hybrid Attacks?
- In hybrid vectors like ADV-07 ("We use a hash map and calculate target - x, but then sort in O(N^3)..."):
  - The candidate expresses genuine partial knowledge ($S_1 \approx 0.50$, $S_2 \approx 0.75$).
  - But CrossEncoder detects logical breakdown ($R \approx 0.25$).
  - After dampening, the unpenalized score reaches $\approx 0.38 - 0.42$.
  - Setting the adversarial threshold ceiling at $0.40$ ensures that any subtle error that corrupts the algorithmic integrity is stopped before it crosses into the "Average" (passing) tier.

---

## 4. Publication Reporting Requirements for Paper 2

In Paper 2 ("Technical Evaluator"):
1. **Explicitly state that thresholds were determined post-hoc**:
   *"The adversarial evaluation bounds ($\theta_{\text{fail}} = 0.35$ and $\theta_{\text{bound}} = 0.40$) were established post-hoc based on the qualitative tier boundaries of the grading rubric, serving as engineering acceptance criteria rather than pre-registered hypotheses."*
2. **Report exact sensitivity**:
   Show that small perturbations around $0.35$ (e.g., $0.30$ to $0.38$) do not alter the passing/failing categorization of the 13 adversarial suite vectors.
