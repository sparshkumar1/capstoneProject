# Speech Prosody Ethics, Demographic Risk, and Architectural Safeguards

**Scope:** Analysis of acoustic speech processing, potential bias, and non-discrimination safeguards.

---

## 1. Demographic and Acoustic Variance Risks
1. **Linguistic Background & Non-Native Accents:**
   - Non-native speakers often exhibit different pitch tracks, higher pause ratios, and varied cadence.
   - Using off-the-shelf "confidence classifiers" trained on native English speakers introduces severe demographic bias.
2. **Speech Impediments and Neurodiversity:**
   - Conditions such as stuttering or dysfluency naturally produce high pause counts and pitch variations that standard classifiers falsely label as "unpreparedness" or "anxiety."
3. **Hardware and Environmental Acoustic Noise:**
   - Inexpensive microphones, background ambient noise, or room reverberation degrade signal-to-noise ratio, artificially inflating jitter/shimmer and reducing Harmonics-to-Noise Ratio (HNR).

---

## 2. Strict Architectural Safeguards in PrepAIred

### Invariant 1: Technical Grading Insulation
- **Rule:** Speech prosody **NEVER modifies the technical evaluation score**.
- **Implementation:** Technical scoring ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$) is derived strictly from text transcripts and C code execution.
- **Evidence:** Verified in `services/evaluator/app.py` and `agents/validation/score_validator.py`. Audio vectors are completely excluded from evaluation aggregation.

### Invariant 2: Anxiety-Protective Pacing
- **Rule:** Speech hesitation and confidence are used strictly as a **downward or stabilizing dampener** in the RL pacing policy to protect nervous candidates.
- **Implementation (Guardrail G2):** If a candidate scores well but exhibits high acoustic hesitation (`hesitation > 0.70`), guardrail G2 prevents difficulty from escalating, keeping difficulty at `Same` to allow the candidate to regain composure.
- **Evidence:** `InterviewOrchestrator._apply_guardrails()` lines 910–920.

---

## 3. Scientific Limitations & Future Human Cohort Work
- Simulation studies using synthetic candidate personas cannot evaluate true human demographic fairness.
- Prior to deploying speech-augmented pacing in real-world educational or hiring contexts, formal demographic parity and equality of opportunity evaluations across gender, accent, and neurodiverse cohorts must be conducted.
