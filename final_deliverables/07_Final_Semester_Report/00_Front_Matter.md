# Front Matter

**Format authority:** `Details/Report-  Guidelines.pdf` (UE23CS441A, Capstone Project Phase-3) and the blank templates in `Details/Report initial Pages(Pg 1-10)/`. This content should be transferred into those official templates (Times New Roman, specified font sizes, cream hard-bound cover) rather than submitted as this Markdown file.

**Assumption flagged for confirmation:** the team, SRNs, and guide below are carried forward from the real Phase-2 submission on the reasoning that this is the same capstone project continuing into Phase-3. **Please confirm or correct before final formatting** — if any team member, the guide, or the project title has changed for Phase-3, update throughout.

---

## Inner Title Page

**Dissertation on**

**"PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System"**

*Submitted in partial fulfilment of the requirements for the award of degree of*

**Bachelor of Technology**
in
**Computer Science & Engineering**

**UE23CS441A — Capstone Project Phase-3**

Project_ID: PW26_UD05 *(carried forward from Phase-2 — please confirm this is unchanged for Phase-3)*

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

*in partial fulfilment for the completion of seventh-semester Capstone Project Phase-3 (UE23CS441A) in the Program of Study - Bachelor of Technology in Computer Science and Engineering under rules and regulations of PES University, Bengaluru during the period August – December 2026. It is certified that all corrections/suggestions indicated for internal assessment have been incorporated in the report. The dissertation has been approved as it satisfies the 7th-semester academic requirements in respect of project work.*

Signature: ______________ (Dr Uma D, Guide) — Signature: ______________ (Dr. Shylaja S S, Chairperson) — Signature: ______________ (Dr. Sridhar K S, Registrar)

**External Viva** — Name of Examiners / Signature with Date: *[left blank — to be completed at submission, not by this process]*

---

## Declaration

*We hereby declare that the Capstone Project Phase-3 entitled "PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System" has been carried out by us under the guidance of Dr Uma D, Professor, and submitted in partial fulfilment of the course requirements for the award of degree of Bachelor of Technology in Computer Science and Engineering of PES University, Bengaluru during the academic semester August – December 2026. The matter embodied in this report has not been submitted to any other university or institution for the award of any degree.*

PES1UG23CS909 — Sparsh Kumar — *[Signature]*
PES1UG23CS924 — Naveen S Khadd — *[Signature]*
PES1UG24CS811 — Manasa S A — *[Signature]*
PES1UG23CS120 — Athreya Shashidhara — *[Signature]*

---

## Acknowledgement

*(Order per `Report-Guidelines.pdf`: Guide → Project Coordinator → Chairperson → Registrar → Chancellor → Vice-Chancellor → Parents → Family and Friends)*

We would like to express our gratitude to Prof. Dr Uma D, Department of Computer Science and Engineering, PES University, for continuous guidance, assistance, and encouragement throughout the development of this UE23CS441A - Capstone Project Phase-3.

We are grateful to the project coordinator, Dr. Chaitra B, for organizing, managing, and helping with the entire process.

We take this opportunity to thank Dr. Shylaja S S, Chairperson, Department of Computer Science and Engineering, PES University, for all the knowledge and support we have received from the department. We would like to thank Dr. Sridhar K S, Registrar, PES University, for his help.

We are deeply grateful to Prof. Jawahar Doreswamy, Chancellor – PES University, and Dr. Suryaprasad J, Vice-Chancellor, PES University, for providing various opportunities and enlightenment every step of the way. Finally, this project could not have been completed without the continual support and encouragement we have received from our family and friends.

---

## Abstract

**Corrected against this report's own verified findings.** An earlier pass restored the Abstract verbatim from the Phase-2 report, which knowingly reintroduced three figures Chapter 8/Chapter 10 of this same report independently find do not match the verified implementation: 500,000 PPO training steps, "seven autonomous sub-agents," and a 93.3% baseline calibration accuracy with no traceable artifact. This pass replaces those three with the figures this report verifies elsewhere (24,576 timesteps/seed across 5 seeds; single-controller orchestrator, not multi-agent; Spearman ρ = 0.3812 human-correlation evidence), so the Abstract is internally consistent with the rest of the report. See the correction and validation report for the prior disclosed conflict.

Most existing technical interview preparation tools are static. Platforms such as LeetCode give every candidate the same sequence of questions regardless of how they are performing, offer no structured feedback, and do not capture any multimodal signal at all. PrepAIred is our attempt at closing that gap. At its core is a Proximal Policy Optimisation (PPO) agent, trained for 24,576 timesteps per seed across five seeds, that adjusts question difficulty based on how the candidate is doing. Answer quality is scored by a three-component semantic evaluator — Sentence-BERT similarity, FAISS-based concept coverage, and CrossEncoder reasoning-quality assessment — while a separate pipeline built on Whisper and Librosa pulls out prosodic signal such as confidence and hesitation from the candidate's speech. A locally hosted Qwen LLM generates hints and follow-up questions, and a dedicated FeedbackAgent turns every answer into a structured fifteen-field report covering misconception detection, concept gaps, and communication quality. All of this is coordinated by a single central InterviewOrchestrator; there is no multi-agent negotiation between separate components. Testing across three synthetic candidate profiles shows the system adapting difficulty correctly and degrading gracefully in all four critical failure scenarios we tried. Against human judgment, the composite evaluator reaches a Spearman correlation of ρ = 0.3812 — a moderate result that we report as exploratory rather than conclusive, since that is what the current evidence supports.

---

## Table of Contents, List of Tables, List of Figures

*To be generated from final chapter/section/table/figure numbering once this report is transferred into the official Word template and paginated (the chapter structure is fixed below; page numbers are a function of final typesetting, not content, and are intentionally left blank here).*

| Chapter | Title |
|---|---|
| 1 | Introduction |
| 2 | Problem Definition |
| 3 | Literature Review |
| 4 | Project Requirements Specification (PRS) |
| 5 | High-Level Design (HLD) |
| 6 | Low-Level Design (LLD) |
| 7 | System Design (Detailed) |
| 8 | Proposed Methodology |
| 9 | Implementation and Pseudocode |
| 10 | Experimentation, Results, and Discussion |
| 11 | Conclusion and Future Work |
| 12 | Bibliography / References |
