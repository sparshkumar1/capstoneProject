# System paper — blockers (2026-09-21)

Overall: **REQUIRES NEW RESEARCH and ethics clearance.** Nothing here has been done beyond the audit and design work listed under READY.

## READY (completed; documents only, no system change)
- Component-by-component implementation audit (`SYSTEM_PAPER_RESEARCH_AUDIT.md`, `SYSTEM_PAPER_IMPLEMENTATION_STATE.md`).
- Hesitation trace: exactly where each value originates, which documents are stale (`SYSTEM_PAPER_HESITATION_INVESTIGATION.md`).
- Finding that the deployed PPO checkpoint differs from the one P3 evaluated, and that the runtime rule fallback equals the legacy Experiment 1 rule but not P3's frozen heuristic.
- Research decision memo with recommended paper type, baseline requirements and minimum study design (`SYSTEM_PAPER_RESEARCH_DECISION.md`).
- Draft protocol, experiment matrix, baseline and ablation plans, ethics checklist, venue matrix (ICALT 2027 verified from the official page; AIED 2027: no call published).
- Provisional-title rule: no "multimodal" and no effectiveness wording.

## AUTHOR CONFIRMATION (only the authors or mentor can supply these)
1. Was omitting the writer of `last_hesitation_score` a deliberate scope decision or an oversight? Which option (keep and document / log both / wire measured) do you choose?
2. Paper type: accept type B (system + usability/feasibility + small randomized pilot), or state what evidence you can actually collect.
3. Research question and the primary outcome (to be fixed before data collection).
4. Which PPO checkpoint is the studied policy (deployed `2ab8d514…` or the P3-evaluated one), and approval to touch anything under `rl/checkpoints/` if the latter.
5. Definition of "constant" relative to the warm-up; whether all arms run the same guardrails; whether follow-ups are on; the fixed question-type schedule.
6. Which rule-based thresholds to freeze (0.80/0.40 live and legacy, or 0.75/0.40 as in P3) and whether a rule-based arm is in scope.
7. Who the ethics contact and principal investigator are; whether participants may be students of the authors; recruitment source; compensation.
8. Who the independent raters are and how their independence will be documented.
9. Target venue and whether ICALT's 15 Jan 2027 deadline is realistic, or whether to plan for a later venue.
10. Author list, contact details and AI-use facts, as for the other papers.

## REQUIRES IMPLEMENTATION (each changes the deployed system and needs approval; none started)
1. `difficulty_policy` switch with Constant-Same, rule-based and PPO conditions, no hard-coded thresholds.
2. An arm-independent question-type schedule (the action currently also selects verbal versus coding).
3. Per-turn logging of proposed and final action, guardrail, difficulty, question type, confidence, hesitation proxy (and measured value if approved), timing and failures, persisted with the session; hashes of checkpoint and VecNormalize; environment and commit.
4. Data-flow review: confirm the temporary audio file is always deleted; audit what SQLite stores about candidates and transcripts.
5. Runtime tests: constant arm always "Same"; rule arm follows the frozen thresholds; PPO arm matches the frozen checkpoint; runtime/simulator equivalence replay.
6. Checkpoint loading and compatibility check in the study environment; a decision on the `.venv` versus `requirements/` pin conflict.
7. Held-out parallel question forms (the bank has 125 items, 10 coding, authored difficulty labels); a rater interface or procedure; a usability instrument.
8. Correct or annotate the stale documents (`rl_state_definition.md`, `speech_ethics.md`, call graph) through the repository's changelog process; they are frozen files and were not edited.

## REQUIRES NEW RESEARCH / ETHICS
1. **Ethics determination and consent process (BLOCKED; no determination exists; the enquiry draft was never sent).**
2. A registered simulation evaluation of the rule-based policy and of the deployed PPO checkpoint (hashed protocol, tag, run manifest), so that "baseline" is earned.
3. Rater recruitment, training and reliability procedure with contemporaneous records.
4. Equivalence check of the held-out parallel forms on independent ratings.
5. The pilot itself, then analysis; power-analysis inputs (smallest effect of interest, SD, pre/post correlation, reliability, attrition) come from it or from justified literature, and are currently unknown.
6. If a later powered effectiveness study is wanted (type A), a separate protocol after the pilot.
7. Any evaluation of accent, speech-difference or noise effects on the confidence score before it is used to pace difficulty for real users (fairness limitation).

## Not to be done
No fake Results, no final PDF, no "multimodal" title, no submission, commit, push or tag.
