# Front Matter

**Format authority:** `Details/Report-  Guidelines.pdf` (UE23CS441A, Capstone Project Phase-3) and the blank templates in `Details/Report initial Pages(Pg 1-10)/`. This content should be transferred into those official templates (Times New Roman, specified font sizes, cream hard-bound cover) rather than submitted as this Markdown file.

**Assumption flagged for confirmation:** the team, SRNs, and guide below are carried forward from the real Phase-2 submission (`revised_report_v5.pdf`) on the reasoning that this is the same capstone project continuing into Phase-3. **Please confirm or correct before final formatting** — if any team member, the guide, or the project title has changed for Phase-3, update throughout.

---

## Inner Title Page

**Dissertation on**

**"PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System"**

*Submitted in partial fulfilment of the requirements for the award of degree of*

**Bachelor of Technology**
in
**Computer Science & Engineering**

**UE23CS441A — Capstone Project Phase-3**

Project_ID: PW26_UD05

**Submitted by:**

| Name | SRN |
|---|---|
| Sparsh Kumar | PES1UG23CS909 |
| Naveen S Khadd | PES1UG23CS924 |
| Manasa S A | PES1UG24CS811 |
| Athreya Shashidhara | PES1UG23CS120 |

*Under the guidance of*
**Dr Uma D**, Professor

**August – December 2026**

DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING
FACULTY OF ENGINEERING
**PES UNIVERSITY**
(Established under Karnataka Act No. 16 of 2013)
100ft Ring Road, Bengaluru – 560 085, Karnataka, India

---

## Certificate

*This is to certify that the dissertation entitled* **'PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System'** *is a bonafide work carried out by*

Sparsh Kumar (PES1UG23CS909), Naveen S Khadd (PES1UG23CS924), Manasa S A (PES1UG24CS811), Athreya Shashidhara (PES1UG23CS120)

*in partial fulfilment for the completion of Capstone Project Phase-3 (UE23CS441A) in the Program of Study - Bachelor of Technology in Computer Science and Engineering under rules and regulations of PES University, Bengaluru during the period Aug 2026 – Dec 2026. It is certified that all corrections/suggestions indicated for internal assessment have been incorporated in the report. The dissertation has been approved as it satisfies the academic requirements in respect of project work.*

Signature: Dr Uma D (Guide) — Signature: Dr. Shylaja S S (Chairperson) — Signature: Dr. K S Sridhar (Registrar)

**External Viva** — Name of Examiners / Signature with Date: *[left blank — not to be filled by AI]*

---

## Declaration

*We hereby declare that the Capstone Project Phase-3 entitled "PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System" has been carried out by us under the guidance of Dr Uma D, Professor and submitted in partial fulfilment of the course requirements for the award of degree of Bachelor of Technology in Computer Science and Engineering of PES University, Bengaluru during the academic semester August – December 2026. The matter embodied in this report has not been submitted to any other university or institution for the award of any degree.*

PES1UG23CS909 — Sparsh Kumar — *[Signature]*
PES1UG23CS924 — Naveen S Khadd — *[Signature]*
PES1UG24CS811 — Manasa S A — *[Signature]*
PES1UG23CS120 — Athreya Shashidhara — *[Signature]*

---

## Acknowledgement

*(Order per `Report-Guidelines.pdf`: Guide → Project Coordinator → Chairperson → Registrar → Chancellor → Vice-Chancellor → CEO → Parents → Family and Friends)*

We would like to express our gratitude to Prof. Dr Uma D, Department of Computer Science and Engineering, PES University, for continuous guidance, assistance, and encouragement throughout the development of this UE23CS441A - Capstone Project Phase-3.

We are grateful to the project coordinator, Dr. Chaitra B, for organizing, managing, and helping with the entire process.

We take this opportunity to thank Dr. Shylaja S S, Chairperson, Department of Computer Science and Engineering, PES University, for all the knowledge and support we have received from the department. We would like to thank Dr. K.S. Sridhar, Registrar, PES University for his help.

We are deeply grateful to Prof. Jawahar Doreswamy, Chancellor – PES University, and Dr. Suryaprasad J, Vice-Chancellor, PES University, for providing various opportunities and enlightenment every step of the way. Finally, this project could not have been completed without the continual support and encouragement we have received from our family and friends.

---

## Abstract (≤150 words per the guideline)

PrepAIred is an adaptive technical-interview preparation platform that evaluates spoken and written candidate responses through a three-component semantic evaluator (Sentence-BERT similarity, FAISS-based concept coverage, CrossEncoder reasoning quality), adapts question difficulty using a frozen Proximal Policy Optimisation (PPO) policy constrained by six deterministic pedagogical guardrails, and generates structured per-turn feedback via a local Qwen2.5 microservice. This phase extends the Phase-2 implementation with a comprehensive, evidence-based testing programme: 264 of 283 automated tests pass (93.3%), with every remaining failure fully attributed to either an environment dependency (Docker) or one previously documented, deliberately deferred issue. Testing surfaced and led to the correction of a genuine guardrail-coverage gap and a platform-specific launcher defect, and identified eight factual discrepancies between the Phase-2 report and the current implementation, each corrected here. This report documents the verified architecture, methodology, implementation, and test evidence underlying the current system.

---

## Table of Contents, List of Tables, List of Figures

*To be generated from final chapter/section/table/figure numbering once all chapters are finalized and transferred into the formatted template (page numbers depend on final pagination).*
