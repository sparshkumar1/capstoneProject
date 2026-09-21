# [PROVISIONAL TITLE — NOT LOCKED] PREPAIred: An End-to-End Multimodal Adaptive Technical Interview Preparation System

*Dr. Uma D (Professor), Naveen S Khadd, Sparsh Kumar, Athreya Shashidhara, Manasa S A; Dept. of CSE, PES University.*

> **INTERNAL PRE-RESEARCH DRAFT. Not a submission candidate and not a results paper.** No user study, no baseline comparison and no ablation has been run; therefore this file contains no results, no effectiveness claim and no abstract. It holds only the parts that can be written truthfully today (system description from the repository audit, and the design of the missing evaluation). The word "multimodal" in the provisional title is **not** supported by the audit and must be removed or justified before the title is locked. Do not label this file final until the new empirical work exists. Built from `SYSTEM_PAPER_RESEARCH_AUDIT.md`.

## Abstract
*Not written. It can be written only after the evaluation exists; a draft abstract now would have to invent findings.*

## 1. Introduction (outline)
- Problem: preparing for technical interviews needs feedback on code and spoken answers and practice at a suitable difficulty.
- Gap to be stated only after a literature review whose references are verified (none is collected for this paper yet).
- Research question (proposed, not adopted): `SYSTEM_PAPER_RQ.md`.
- Contributions: only those that will be true after the study (see the RQ file).

## 2. Related work
*Not written. References for adaptive instructional systems, automated technical assessment and speech-based feedback must be gathered from Zotero or verified sources; none is asserted here. P1 (dependability of the pipeline) and P3 (simulated policy comparison) are companion manuscripts under preparation; they are cited only once publicly available, and never as evidence that the system helps people.*

## 3. The system as implemented (write-up of the audit)
The prototype integrates: a session orchestrator with persistence; a text/content answer evaluator (a weighted combination of a sentence-embedding similarity, a retrieval-grounded similarity and a cross-encoder score); a Docker-based C compiler and runner sandbox; a local language-model service for feedback and follow-up questions; browser audio capture with speech-to-text and acoustic features that yield a confidence score; a PPO difficulty controller behind an application-level rule-based guardrail, preceded by a fixed warm-up phase; and a web interface. Status of each component: **Table 1 in the audit**. Points that must appear in any description:
- Only audio and text are used; **no video or facial signal** exists.
- The audio channel reaches adaptation through a confidence score; the runtime "hesitation" input is derived from that score (`1 − confidence`), not from the hesitation scorer.
- The evaluator has only exploratory validation against human reference scores on constructed answers.
- The controller has simulation-only evidence and one deployed checkpoint.
- **Architecture figure:** to be drawn from the audit table showing only implemented components; components not implemented (video, hesitation wiring, runtime constant/rule-based arms) are omitted or visibly marked as not implemented.

## 4. Evaluation design
See `SYSTEM_PAPER_STUDY_PROTOCOL.md`, `..._BASELINE_PLAN.md`, `..._ABLATION_PLAN.md`. Status: **blocked** pending ethics, approval and arms.

## 5. Results
**NOT AVAILABLE. NO DATA EXIST.** This section stays empty until the study is executed and analysed under a registered protocol.

## 6. Discussion, limitations, conclusion
Limitations already known: unvalidated confidence score and no accent or disability evaluation; evaluator provenance gaps; feedback quality unassessed; one deployed checkpoint with a training/runtime state mismatch; environment pin violations; one machine; no real-user data.

## Declarations
Ethics, consent, data availability and any AI-use statement must be written from confirmed facts only; none is drafted.
