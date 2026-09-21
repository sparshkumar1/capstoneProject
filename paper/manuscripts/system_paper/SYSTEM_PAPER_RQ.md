# System paper — research question and contribution (PROPOSED, not adopted)

**Status:** proposal for the authors and mentor. Nothing here has been decided, pre-registered or approved. It rests on `SYSTEM_PAPER_RESEARCH_AUDIT.md`.

> **Superseded in part (2026-09-21):** the recommended question, paper type (system + usability/feasibility with a small randomized pilot) and study design are in `SYSTEM_PAPER_RESEARCH_DECISION.md`. The effectiveness-style RQ-S below is retained only as a possible later, powered follow-up.

## Title
Working title (provisional, not locked): "PREPAIred: An End-to-End Multimodal Adaptive Technical Interview Preparation System".
The audit does not support "multimodal" today (audio and text only; hesitation not wired into the runtime state; no video). Until that is resolved the title must not use it. Options, all provisional: "…An End-to-End Audio-and-Text Adaptive Technical Interview Preparation System…" (if the audio channel is the only additional modality) or a title naming the evaluated question once it is fixed. The legacy title is not used.

## Why the question must differ from P1 and P3
- P1: which properties of the pipeline can be demonstrated under controlled tests (dependability). P3: what a PPO controller adds beyond a state-blind constant policy in simulation (equivalence within a self-chosen margin). Neither says anything about a person using the system.
- P3's own result is an equivalence in simulation. It gives no reason to expect a learned controller to beat a constant one for real candidates, so a study that merely hypothesises "PPO helps people" would restate an unmotivated claim. The system paper's question therefore should not be about PPO superiority.

## Candidate research question (for decision)
**RQ-S.** For candidates practising technical-interview answers with the integrated system, does an adaptive-difficulty condition change held-out, blinded-rated answer quality (and reported usability and workload) compared with a non-adaptive condition, and does a simple rule-based adaptation do as well as the learned controller?

Sub-questions that can be answered only with new data:
1. Change in blinded-rated answer quality from a pre-test to a post-test on held-out questions, by condition (primary outcome; see protocol).
2. Usability and perceived usefulness by condition.
3. System reliability in use: completion, failures, evaluator/STT outages, session time.
4. Whether the automated evaluator's scores track independent human ratings of the same held-out answers in this population (a measurement question; it must not be assumed).

## Contribution list (only what can be true after the new work)
1. A documented, reproducible description of the integrated implementation, classified by evidence status (available now).
2. A controlled comparison of adaptation conditions on human outcomes (requires the study).
3. Independent human evaluation of held-out answers, reported with reliability (requires the study).
4. Honest negative or null findings if that is what the data show (a null or equivalence result is an acceptable result).
Not claimable now: any effectiveness, usability, learning or engagement statement; any multimodal claim beyond audio and text; any PPO advantage.

## Decisions the authors must make before design freeze
1. Whether the study addresses adaptation at all, or a narrower question (e.g., practice with vs without the system's feedback). The narrower question needs fewer engineering changes and does not depend on the P3 controller.
2. Whether to wire the hesitation scorer into the state, which would change a frozen-checkpoint input and create a training/runtime mismatch (needs explicit approval), or to keep the current confidence-only behaviour and describe it truthfully.
3. The primary outcome, the sample constraint (see protocol) and the ethics route (`SYSTEM_PAPER_ETHICS_CHECKLIST.md`). Data collection cannot start before these and the approvals.
