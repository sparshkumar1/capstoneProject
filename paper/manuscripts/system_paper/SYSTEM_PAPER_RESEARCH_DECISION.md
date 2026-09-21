# System paper — research decision memo (2026-09-21)

**Status: RECOMMENDATION for the authors and mentor. Nothing is adopted, registered, approved, implemented or executed. No results exist.** Evidence base: `SYSTEM_PAPER_IMPLEMENTATION_STATE.md` and `SYSTEM_PAPER_HESITATION_INVESTIGATION.md`.

## 1. Direct assessment
**As things stand, the system paper cannot support a strong publication claim.** There is no human evidence of any kind. The one adaptive component that could be studied (the deployed PPO+guardrail policy) has never been evaluated, even in simulation. The live system is audio + text, with the audio channel reduced to one unvalidated confidence number, and the PPO checkpoint that was analysed hardly responds to it. Only one of the three candidate study conditions exists at runtime. P3's own result (equivalence with a constant policy in simulation) gives no reason to expect the adaptive controller to matter for people, so an "adaptation improves outcomes" paper would be testing an unmotivated hypothesis with a system whose question bank is small (125 items, 10 of them coding) and whose difficulty labels are authored, not validated. Ethics has not even been asked. A paper claiming effectiveness, or "multimodal" adaptation, would not be defensible.

## 2. What kind of paper the current implementation can support
| Option | Verdict |
|---|---|
| **A. Real-user effectiveness paper** (adaptation or practice improves performance) | **Not supportable now.** It needs a powered randomized study with independent blinded outcome measures, three runtime conditions, validated parallel question forms and ethics approval; none exists, no effect-size or variance input exists for a power analysis, and an underpowered null would be uninformative. Keep it as a possible follow-up, and only if the pilot below supplies the variance estimates a power analysis needs |
| **B. System + usability/feasibility paper with a small randomized pilot** | **Recommended.** It matches what exists: an integrated audio+text prototype whose component status can be described honestly, whose reliability and usability can be measured, and whose pilot can give first, clearly labelled exploratory estimates (and the variance inputs a later powered study needs). Its claims are limited by design, and the paper says so. It still needs ethics clearance and modest engineering |
| C. Evaluator-validation paper | Belongs to the held P2 and its missing records; not a system paper |

**Decision proposed: B.** Frame every claim at the level the design supports: feasibility, reliability, usability, and exploratory effect estimates with intervals. No claim that the system or its adaptation improves interview performance unless a later powered study shows it.

## 3. Recommended research question (for type B)
*Primary:* **Can candidates complete a full practice session with the integrated audio-and-text system reliably and with acceptable usability?**
*Secondary (exploratory, pre-declared):* (a) What is the estimated difference in blinded-rated post-test change between practice with a constant-difficulty policy and with the deployed PPO+guardrail policy, with an interval wide enough to be honest about its uncertainty? (b) How closely do the automated evaluator's scores track independent human ratings of the same held-out answers in this population? (c) How often do measured hesitation and `1 − confidence` disagree (if both are logged)?

The title must not contain "multimodal" or an effectiveness word until the results justify it. Acceptable neutral wording: "…An Audio-and-Text Adaptive Technical-Interview Practice System: Description and Pilot Evaluation".

## 4. The hesitation discrepancy and what it means for the design
See the investigation file. Recommendation: keep the current behaviour, describe it truthfully as "confidence and its complement", and add per-turn logging of both values (needs approval). Do not wire the measured hesitation into the checkpoint's input for the first study; that would create an untested input distribution. The author must say whether omitting the writer was deliberate.

## 5. What is required to implement and evaluate the three policies
A policy may be called a **baseline** only after it is implemented in the live system, frozen, and evaluated (below). Today: PPO exists but is unevaluated at deployment; the threshold rule exists only as a fallback and is not a baseline; Constant-Same does not exist at runtime.

### Common prerequisites (all three)
1. **A `difficulty_policy` configuration value** (e.g., `constant_same`, `rule_based`, `ppo`) chosen at session creation and recorded with the session; one code path (`_adapt_difficulty`, after the warm-up phase) branches on it. No hard-coded thresholds.
2. **Decide what "constant" means given the warm-up.** The live system starts at level 2, moves to 3, then applies a baseline-average level shift (`_baseline_target_difficulty`) before PPO takes over. Options: (i) all arms share the warm-up and level assignment and "constant" means "hold that level afterwards" (recommended: identical exposure until the arms diverge), or (ii) skip the warm-up for the constant arm. This differs from P3 (fixed at 3.0, no warm-up) and must be stated.
3. **Remove the type confound.** The chosen action also decides whether the next question is verbal or coding (`_next_type_from_action`), so arms would differ in question-type mix as well as difficulty. The study needs one fixed, arm-independent schedule of question types (or the type rule frozen identically across arms).
4. **Follow-ups and coding turns.** Decide whether LLM-generated follow-ups are on, and make their handling identical across arms (they inject questions and can change the path).
5. **Guardrail policy.** P3 compared policies *both under the guardrail*. Decide whether all arms run the same guardrails (then "constant" can still move when a guardrail fires) and report the counts per arm; the guardrail uses `hes = 1 − conf`.
6. **Per-turn logging** of proposed action, final action, guardrail name, difficulty, question type, confidence, the hesitation proxy (and the measured value if approved), timings and failures, persisted with the session; verify what the current store already keeps (not verified here).
7. **Environment record.** The `.venv` violates three pins and the checkpoint must be loaded and checked (`is_compatible`) in the study environment; record the environment, git commit and file hashes with each session.
8. **Tests:** scripted sessions showing that the constant arm's raw action is always "Same", the rule arm follows its frozen thresholds, and the PPO arm equals the frozen checkpoint's predictions; an equivalence check of the runtime policies against the simulator implementations (in the manner of the X3-0c replay).

### Constant-Same
Implement as a raw-action override (always "Same") followed by the same guardrails as the other arms. Already evaluated **in simulation** (P3, Constant-Same+G, on the P3 simulator), not in the live code and not with people; the live implementation therefore needs the runtime/simulation equivalence test above.

### Rule-based adaptation
- **Freeze one rule before any data.** Three versions exist: live fallback (harder above 0.80, easier below 0.40), legacy Experiment 1 (same 0.80/0.40), and P3's frozen "Heuristic" (0.75/0.40). Choose one, justify it without reference to study outcomes, and do not tune it.
- **It becomes a baseline only if evaluated:** (i) in the simulator under a new registered experiment (hashed protocol, tagged, run manifest as the repository's rules require), and (ii) as an arm (or, if participants are limited, at minimum in simulation with the limitation stated). The legacy Experiment 1 result does not count: it is legacy, unaudited here, and P3 did not evaluate this rule.

### PPO
- **Which checkpoint?** The deployed one (`rl/checkpoints/seed_123`, `2ab8d514…`) was never evaluated in P3; the evaluated one (`299437ea…`) is not deployed. Either evaluate the deployed checkpoint in simulation first (new registered experiment), or deploy the evaluated one from a separate, configured path. Replacing or retraining anything under `rl/checkpoints/` needs explicit approval.
- **State definition:** the runtime uses progress t/T where training used a latency dimension (`rl_state_definition.md` §s4), and hesitation is a proxy. State both as limitations, not as details.
- Record the checkpoint and VecNormalize hashes with every session.

## 6. Minimum scientifically credible end-to-end human study (type B)
**Two arms:** (1) Constant-Same + guardrail; (2) deployed (or explicitly chosen) PPO + guardrail. A third, rule-based arm only if its evaluation (above) is complete and participants allow; otherwise it is omitted and the paper says so.

**Design:** between-participant randomized pilot. Each participant does a **pre-test** (held-out questions, no system, no feedback), **one fixed-length practice session** in the assigned arm, and a **post-test** on a parallel held-out form. Forms counterbalanced across participants (half take form X at pre-test, half form Y); the assignment is recorded in advance.
- **Randomization:** allocation sequence generated and stored before enrolment (seeded), stratified by self-reported experience, concealed from raters; participants not told which policy they have (they cannot see it, but must be told adaptation may vary).
- **Held-out forms:** questions not in the practice pool, matched on topic and labelled difficulty, independently rated for equivalence before use. **Constraint found:** the bank has only 125 questions (10 coding, difficulty labels authored, few items at the extremes), and the practice pool must span five levels; new questions are probably needed and, to be independent, should not be written or tuned by the developers. This is a real feasibility issue.
- **Outcomes:**
  - *Primary (for the type-B claim):* feasibility: proportion of sessions completed without a blocking system failure (evaluator/STT/sandbox/timeout), with failures itemized. **Co-primary:** a standard validated usability scale (instrument and citation to be chosen and verified).
  - *Secondary, exploratory:* blinded human rubric score change (post − pre) by arm, with an interval; perceived usefulness and workload; session time; evaluator-versus-human agreement on held-out answers; guardrail activations and action changes per arm; frequency of measured-versus-proxy hesitation disagreement.
  - The primary outcomes and analysis are **fixed and registered before data collection**; nothing is promoted to primary afterwards.
- **Independent evaluation:** at least two (preferably three) raters who are independent of the development team, trained on a calibration set, blind to arm and time point, rating every held-out answer with a rubric written and frozen beforehand; reliability reported with an interval; an adjudication rule fixed in advance; rater identity, qualifications, relationship to participants and instructions recorded at the time (the earlier rating round lacks this). The automated evaluator is not the outcome measure.
- **Participants:** adult learners preparing for technical interviews with basic C and data-structures knowledge (the system's content), able to use a browser with a microphone, English-language sessions. Voluntary; preferably not students in a course taught or graded by the authors (to be settled with the ethics office). Recruitment source, inclusion/exclusion criteria and compensation to be fixed with the institution. **No participant number is proposed as sufficient.**
- **Analysis plan:** intention-to-treat; primary comparison via a pre-specified model (post-test adjusted for pre-test; rater and item effects as needed), effect sizes with 95 % intervals; feasibility and usability descriptively with intervals; no significance-based dichotomy as the headline; a multiplicity policy for secondary outcomes; missing-data handling and system failures reported in full; any equivalence claim only with a margin justified independently of the data (P3's ±0.12 is in other units and was author-selected; it cannot be reused).
- **Power-analysis inputs (all currently unknown, so none is computed):** smallest effect size of interest on the rubric scale and its justification; standard deviation of post-test scores adjusted for the pre-test; pre/post correlation; rater reliability and number of items per form; expected attrition; alpha and target power; if an equivalence test is used, the margin. If the number of available participants is small the study is declared a pilot up front: it reports estimates and intervals, makes no powered confirmatory claim, and its variance estimates become the inputs for a later powered study.
- **Ethics, consent and data:** see `SYSTEM_PAPER_ETHICS_CHECKLIST.md`. No determination exists. Before any recruitment: institutional determination and consent/information sheet; audio handling verified (audio goes to a temporary file in `/api/transcribe`; deletion to be confirmed by code review); what the SQLite store keeps of transcripts and candidate details; pseudonymous IDs; retention and deletion; raters' consent; withdrawal procedure; statement on publication of aggregate results and any data sharing; note that the confidence score has not been evaluated across accents or speech differences.

## 7. Timeline and venue reality check
ICALT 2027's deadline is 15 January 2027 (about 16 weeks away), and its five-page limit includes references and authors' information. Ethics clearance (duration unknown), engineering, new held-out questions, recruitment, blinded rating and analysis all have to fit. That is not established as feasible. If ethics clearance does not arrive within weeks, plan for a later venue instead of compressing the design. AIED 2027 has no published call.

## 8. What must be completed before manuscript writing
1. Author decisions (see `SYSTEM_PAPER_BLOCKERS.md`): intent behind the hesitation wiring; paper type; research question; which PPO checkpoint; guardrail treatment; definition of "constant"; frozen rule thresholds.
2. Ethics determination and consent materials.
3. Implementation prerequisites (§5) with tests.
4. Registered evaluation of the rule-based policy and of the deployed checkpoint in simulation (or a stated decision to omit them).
5. Held-out question forms and rater arrangements.
6. Protocol hashed and tagged; run manifest approved.
7. The pilot executed; only then are results, figures and the abstract written, followed by the rendered-PDF visual QA.

Until 1–6 are done, `SYSTEM_PAPER_MANUSCRIPT.md` stays an internal pre-research draft with no Results section and no PDF.
