# System paper — study protocol DRAFT (2026-09-21)

**Status: DRAFT, NOT REGISTERED, NOT APPROVED, NOT EXECUTED. Human data collection is BLOCKED** until (i) the institution's ethics/consent requirements are established and met (`SYSTEM_PAPER_ETHICS_CHECKLIST.md`), (ii) the authors adopt a research question and primary outcome, and (iii) the protocol is hashed and tagged as the repository's preregistration procedure requires (`research/audit/PREREGISTRATION_SPEC.md`, `RUN_MANIFEST_SPEC.md`). No sample size is asserted: none can be justified until the design, outcome variance and available participants are known.

## 1. Design (proposed for discussion)
- **Between-participant randomized comparison of practice conditions**, with a **pre-test and post-test on held-out questions** administered without adaptation and without the system's feedback. Held-out questions are not in the practice pool and are counterbalanced across participants and across pre/post via two or more parallel forms (parallel-form equivalence must be checked on independent ratings before use).
- **Conditions** (only those that can be implemented and controlled; see `SYSTEM_PAPER_BASELINE_PLAN.md`): A) non-adaptive constant difficulty; B) simple rule-based adaptation; C) the deployed PPO+guardrail controller. All conditions use the same questions, evaluator, feedback model, interface and session length; only the difficulty rule differs. If only two arms are feasible, A vs C or A vs B is preferable to underpowered three arms.
- **Randomization:** allocation sequence generated and recorded before enrolment (seeded, stored); stratify by self-reported experience if that is collected; allocation concealed from the raters.
- **Session structure:** fixed number of practice questions and fixed time budget per participant, so exposure is equal across arms.

## 2. Outcomes (to be fixed before data collection; proposed)
- **Primary:** change (post − pre) in the mean blinded human rubric score on held-out answers.
- **Secondary:** usability (a standard, cited instrument to be chosen and verified), perceived usefulness, workload, completion time, system failures (evaluator/STT outages, timeouts), and agreement between the automated evaluator and the human ratings on the held-out answers.
- **Not primary:** the automated evaluator's score. The evaluator is part of the intervention and has only exploratory validation (Spearman 0.3812 on constructed answers); using it as the outcome would be circular.
- The primary outcome, analysis model and exclusion rules are fixed before any outcome is seen. Anything added later is labelled exploratory.

## 3. Independent human evaluation
- **Rubric:** a written rubric fixed and documented before rating (the existing frozen rubric may be reused only if it fits and its provenance is documented; it is not automatically suitable).
- **Raters:** number, qualifications, recruitment, independence from the development team and any relationship to participants must be documented at the time (the earlier round lacks this record and it cannot be recreated). Raters are trained on a calibration set; they see answers without condition, time point or evaluator score; order randomized.
- **Reliability and adjudication:** all raters rate every held-out answer; inter-rater reliability reported with an interval; adjudication rule fixed in advance; adjudicated items counted and reported (as in the 54 mean-of-three plus 10 adjudicated split noted for the earlier benchmark).
- **Rater ethics:** raters handle participant answers, so consent/data-handling terms cover them too.

## 4. Sample size and power
- Not chosen. A power analysis needs the smallest effect of interest, the outcome's standard deviation and the correlation between pre and post; none is known here, and no pilot exists. **If the number of available participants is small, the study is a pilot or exploratory study: estimate effects with intervals, make no powered confirmatory claim, and say so in the abstract.**
- The P3 persona-level variance must not be reused; it is a simulator quantity.

## 5. Analysis (outline)
Pre-specified model for the primary outcome (e.g., adjusting the post-test for the pre-test), effect sizes with intervals, no dichotomization by p-value alone, multiplicity policy for secondary outcomes, handling of dropouts and system failures (intention-to-treat as the default; per-protocol as sensitivity), full reporting of failures.

## 6. Reproducibility and provenance
Config files for every condition (no hard-coded hyperparameters), explicit seeds for allocation, the git commit and environment (including the pin violations) recorded with each session, stored session logs with pseudonymous IDs, a run manifest, and the frozen PPO checkpoint hash. W&B is not required.

## 7. Engineering prerequisites (not done)
1. Runtime switches for condition A and B (constant and rule-based policies), with tests.
2. A decision on the hesitation wiring (`SYSTEM_PAPER_RESEARCH_AUDIT.md`).
3. A held-out question set with documented parallel-form equivalence.
4. Data-flow review for what is stored (audio is written to a temporary file in `/api/transcribe`; whether it is always deleted, and what the SQLite store keeps of transcripts and candidate details, need auditing against the consent terms).
Each changes the deployed system and needs approval; none has been started.

## 8. Stop conditions
Do not start recruitment or data collection if: ethics or consent requirements are undetermined; the primary outcome is not fixed; raters are not independent or not documented; the constant/rule arms do not exist; the run manifest is not approved.
