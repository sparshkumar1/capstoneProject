# PrepAIred — Speech Prosody & Demographic Fairness Claim Audit

**Date:** September 2026  
**Status:** COMPLETE & FROZEN  
**Audit Scope:** Acoustic speech features, demographic bias, non-native accents, speech differences, and fairness claims across repository documentation and manuscripts.

---

## 1. Executive Summary & Core Scientific Constraint

A comprehensive audit of terms (`accent`, `non-native`, `fairness`, `bias`, `equitable`, `protected`) was conducted across all active research documentation, manuscripts, and production codebases.

### The Scientific Truth Boundary:
1. **What PrepAIred DOES Guarantee (Architectural Acoustic Insulation):**
   - Acoustic speech features (hesitation, speaking rate, pitch variability, audio confidence) are strictly excluded from candidate technical scoring.
   - Technical correctness ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$) is derived exclusively from text transcripts and sandbox C execution test cases.
   - Audio prosody variance—whether caused by non-native accents, speech disfluencies (stuttering), or hardware noise—cannot mathematically alter or degrade technical evaluation scores.
   - Pacing guardrails (Guardrail G2) use acoustic hesitation solely as an anxiety-protective dampener to halt difficulty escalation, never to penalize or grade candidates.

2. **What PrepAIred CANNOT and DOES NOT Claim (Empirical Demographic Fairness):**
   - PrepAIred **DOES NOT** claim empirical demographic parity, equalized odds, or proven cross-accent fairness across diverse human demographic groups.
   - No human demographic dataset (annotated by race, gender, nationality, native language, or neurodiversity) has been collected or evaluated on acoustic prosody.
   - All claims in papers and documentation must strictly frame fairness as **architectural insulation from correctness evaluation**, rather than empirical demographic fairness.

---

## 2. Exhaustive Keyword Audit Across Repository

| Keyword Searched | Files Located | Audit Finding & Claim Status |
| :--- | :--- | :--- |
| `accent` | `research/audit/speech_ethics.md`, `research/audit/privacy_data_flow.md`, `research/archive/old_audits/unknowns.md` | **COMPLIANT:** Correctly frames accent variance as a risk mitigated by architectural decoupling. Explicitly states demographic evaluations across accents are pending future work. |
| `non-native` | `research/audit/speech_ethics.md`, `research/audit/reviewer_simulation.md`, archived draft | **COMPLIANT:** Identified as an explicit vulnerability of commercial confidence classifiers; PrepAIred disclaims off-the-shelf classifiers and insulates technical grading from pause cadence. |
| `fairness` | `research/audit/speech_ethics.md`, `research/archive/old_audits/unknowns.md` | **COMPLIANT:** Explicitly labeled as "Demographic Speech Fairness: UNKNOWN". Warns that synthetic simulations cannot evaluate true human demographic fairness. |
| `bias` | `research/audit/speech_ethics.md`, `research/papers/paper3_rl/README.md`, `outline.md`, `data_lineage.md` | **COMPLIANT:** Describes acoustic bias insulation where hesitation is used only to stabilize pacing, never penalize or bias grading. |
| `equitable` | `INTERVIEW_PREPARATION_GUIDE.md`, archived draft | **COMPLIANT:** Used strictly in educational context describing the goal of broadening access to interview preparation via local, open-weight execution without expensive commercial API subscriptions. |
| `protected` | `services/evaluator/assets/rubrics.json`, `tests/`, `research/scripts/` | **COMPLIANT:** Refers to memory protection in OS questions (read-only memory segments, SIGSEGV), file protection in `.gitignore`, or RL deterministic guardrails. |

---

## 3. Code-Level Verification of Architectural Insulation

### 3.1 Technical Evaluator (`services/evaluator/app.py`)
- Endpoint `/evaluate` schema:
  - Input: `question`, `user_answer`, `c_code`, `category`, `difficulty`, `ideal_answer`, `rubric_id`.
  - **No audio payload, spectrogram, acoustic feature, or hesitation scalar is accepted or processed by the evaluation engine.**
  - Aggregate score is strictly:
    $$\text{Final} = 0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$$
  - Acoustic features have **zero weight** ($0.00$) in score computation.

### 3.2 Score Validator (`agents/validation/score_validator.py`)
- Enforces numeric bounds, category rubrics, and penalty clamping on semantic and code scores.
- Does not contain or process acoustic prosody fields.

### 3.3 Orchestrator & RL Pacing Agent (`agents/orchestrator/interview_orchestrator.py`)
- Acoustic prosody is ingested solely into the 6D observation vector:
  $$\mathbf{s} = [S_{\text{tech}}, S_{\text{code}}, \text{Hesitation}, \text{Rate}, \text{Progress}, D_{\text{norm}}]$$
- **Guardrail G2 Enforcement (`_apply_guardrails`):**
  ```python
  if hesitation > 0.70:
      # Pacing dampener: force action to Stay (0) or Down (-1), never Up (+1)
      # Protects anxious candidates from premature escalation
  ```
- Hesitation is strictly a **unilateral safety dampener** preventing escalation when a candidate exhibits high vocal anxiety despite passing technical thresholds.

---

## 4. Required Paper Terminology Guidance

When writing manuscripts (Paper 1, Paper 2, Paper 3), authors must strictly adhere to the following phrasing standards:

| Approved Phrase / Formulation | Prohibited / Unsubstantiated Formulation |
| :--- | :--- |
| "Acoustic prosody is insulated from technical scoring, ensuring speech variances do not degrade candidate correctness marks." | ❌ "The system is fair and unbiased across diverse accents and dialects." |
| "Acoustic features inform pedagogical pacing dampening without participating in technical grading." | ❌ "The system has proven demographic parity across non-native English speakers." |
| "Empirical demographic fairness across cultural and speech cohorts remains an explicit open research direction." | ❌ "PrepAIred eliminates bias against neurodiverse candidates." |

---

## 5. Audit Conclusion

The repository's documentation and codebase maintain strict integrity:
1. No unsubstantiated claims of empirical demographic fairness exist in active manuscripts.
2. The architectural insulation of technical scoring from speech prosody is verified end-to-end in code.
3. Limitations regarding real-world demographic and accent generalization are explicitly documented.
