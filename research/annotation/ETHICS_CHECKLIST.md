# PREPAIred — Human Participant Research & Ethics Checklist

**Date:** September 2026  
**Status:** **HUMAN ADMINISTRATIVE CHECK REQUIRED**  
**Audited Target:** Paper 2 Evaluator Benchmark Human Annotation Study (64 items, 3 expert raters)

---

> [!CAUTION]
> ### 🛑 MANDATORY HUMAN ADMINISTRATIVE ACTION REQUIRED
> **Automated AI systems and software scripts CANNOT sign off on human research ethics, grant IRB exemptions, or distribute evaluation packages.**
>
> Prior to releasing the three rater packages (`PREPAIred_Rater_1_Package.zip`, `PREPAIred_Rater_2_Package.zip`, `PREPAIred_Rater_3_Package.zip`) to human evaluators, the Principal Investigator / Human Research Lead **MUST personally complete, review, and sign this administrative checklist**.

---

## 1. Institutional Ethics & Regulatory Review

- [ ] **1.1 Institutional Review Board (IRB) / Ethics Review Board (ERB) Determination:**
  - *Determination:* Has the human rating protocol been evaluated by the appropriate institutional ethics board (or verified under an exempt category for anonymous educational benchmarking / quality assurance)?
  - *Status:* `[ ] EXEMPT  /  [ ] APPROVED  /  [ ] EXPEDITED  /  [ ] PENDING`
  - *Protocol / Exemption ID:* ___________________________
  - *Institutional Affiliation:* ___________________________

- [ ] **1.2 Scope of Human Involvement:**
  - The study involves evaluating *synthesized and benchmark interview answers*, NOT live student interview performance.
  - Human participants act strictly as **expert evaluators / judges**, not test subjects undergoing psychological assessment.
  - No biometric data, video feeds, or voice recordings are collected from the raters.

---

## 2. Participant Consent & Informational Transparency

- [ ] **2.1 Informed Consent Form (ICF):**
  - Raters are provided with a written explanation of the research purpose, anticipated time commitment (approximately 1.5 to 2.5 hours for 64 items), and intended publication venues (e.g., ICTCS / IEEE Transactions on Education).
  - Consent explicitly includes permission to publish anonymized rating scores and statistical agreement metrics.

- [ ] **2.2 Voluntary Participation & Right of Withdrawal:**
  - Raters are explicitly informed that participation is entirely voluntary and they may withdraw at any time without penalty or academic consequence.

- [ ] **2.3 Fair Compensation / Recognition:**
  - Expert evaluators are either fairly compensated for their professional grading time (at standard professional/institutional hourly consulting rates) or provided formal co-authorship / acknowledgments in accordance with IEEE/ACM authorship criteria.

---

## 3. Data Protection, Privacy & Anonymization

- [ ] **3.1 Strict Rater De-Identification:**
  - Personal identifiable information (PII) of raters (names, personal email addresses, institutional IDs) will NOT be included in the public repository or published research datasets.
  - Raters are cryptographically anonymized and referenced strictly as `Rater 1`, `Rater 2`, and `Rater 3`.

- [ ] **3.2 Secure Data Storage & Provenance Tracking:**
  - Completed CSV files (`RATING_SHEET_64_CASES.csv`) returned by raters will be stored in a secured, non-public staging directory prior to cryptographic hashing and commit.
  - Exact SHA-256 hashes will be recorded in the audit trail to ensure immutability and provenance.

- [ ] **3.3 Compliance with Applicable Data Regulations:**
  - Verified compliant with institutional data handling policies and applicable data protection regulations (e.g., GDPR Article 89 for scientific research, Digital Personal Data Protection Act).

---

## 4. Scientific Independence & Anti-Contamination Safeguards

- [ ] **4.1 Independent Blind Evaluation:**
  - Raters confirm they will perform evaluations independently without conferring with one another during initial scoring.
  - Raters confirm they have NOT received any automated system scores, model weights, or algorithm rankings.

- [ ] **4.2 Adjudication Protocol Agreement:**
  - Raters have reviewed and agreed to the pre-specified and frozen adjudication protocol (`research/annotation/HUMAN_RATING_PROTOCOL.md`) for resolving items where score divergence exceeds $0.20$.

---

## 5. Administrative Sign-Off & Release Authorization

**DO NOT DISTRIBUTE PACKAGES UNTIL SIGNED BY HUMAN INVESTIGATOR.**

| Role | Name | Signature / Authorization | Date |
| :--- | :--- | :--- | :--- |
| **Principal Investigator** | _________________________ | _________________________ | ____________ |
| **Lead Ethics Coordinator** | _________________________ | _________________________ | ____________ |

---

**Release Directive:**  
Upon signature, proceed to **HUMAN GATE 1** in `research/audit/HUMAN_GATE_1_READY.md` to authorize distribution of the rater packages.
