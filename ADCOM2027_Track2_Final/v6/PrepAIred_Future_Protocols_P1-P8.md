# PrepAIred Future Experimental Protocols: P1–P8

**Status of this document: planned research protocols only. No experiment described here has been run. No result, sample, or number from these protocols is reported in the manuscript.** Every protocol ends with **[RESULT PENDING - NOT RUN]**.

Conventions used in all protocols:

- *Structural unit.* The completed replay study treats the 8 replay clusters as the independent structural unit (20 question orders per cluster are dependent). Unless stated otherwise, new replay-based protocols keep this unit and use a cluster bootstrap over clusters (B and seed to be registered in advance) plus leave-one-cluster-out (LOCO) sensitivity analysis. Protocols that introduce new stimuli must define their own structural unit and state it before data are generated.
- *Registration.* Each protocol must be written into a hashed, tagged protocol file and an approved run manifest before any run; nothing is changed after seeing results without registering a new experiment.
- *Evidence classes.* Use REPLAY, FAULT-INJECTED, SYNTHETIC, SIMULATED, and (for P8 only) HUMAN, and never present one class as another.
- *Wording.* Predictions below are expectations to be registered, not findings.

## Motivation map

| Protocol | Motivating existing finding |
|---|---|
| P1 | Current behavior may be reproducible with simpler controllers; stronger baselines test necessity |
| P2 | Replay uses fixed candidate responses and leaves closed-loop learning/adaptation unresolved |
| P3 | XD accepted unsupported paraphrased credit in 57/57 applicable cases |
| P4 | Current agents are rule/ledger based and replay uses no live LLM |
| P5 | Evaluator validity is not established and R is associated with length |
| P6 | XC uses discrete/structured confidence values and τ = 0.60 lies on a plateau |
| P7 | Authority is central to the paper's safety claim and can be tested as an explicit invariant |
| P8 | No human evaluation or candidate-learning evidence is currently present |

---

## P1 — Stronger baselines

1. **Motivation.** M1 differs from B0 in difficulty trajectory, but M1 adds two agents, a ledger, and arbitration together. The finding may be reproducible by a simpler controller.
2. **Hypothesis.** H1 (necessity-weakening): a single rules engine using the same weakness ledger reproduces M1's trajectory-level effects (level changes, reversals, PPO agreement), which would weaken the claim that multi-agent decomposition is behaviorally necessary. H0: it does not.
3. **Research question.** Are the observed trajectory effects attributable to the two-agent architecture combined with PPO, or can simpler controllers reproduce them?
4. **Conditions.** (a) single rules engine with the same weakness ledger; (b) staircase or Elo-style difficulty controller **[AUTHOR TO CONFIRM: definition of planned staircase/Elo baseline]**; (c) PPO alone; compared with existing B0, B7, and M1 under identical replay.
5. **Dataset / stimuli.** The existing 64 constructed answers, 8 clusters, recorded evaluator outputs; no new stimuli.
6. **Sample size.** Same replay design as the completed study (8 clusters × 20 order seeds = 160 sessions per condition). **[AUTHOR TO CONFIRM: planned sample size]** if a larger design is wanted.
7. **Randomization / seeds.** Same order seeds 0–19 and the same bootstrap settings as XA, so conditions are paired.
8. **Primary metrics.** Level changes, reversals, PPO agreement where applicable, final decision-source distribution.
9. **Secondary metrics.** Follow-up/probe turns, per-turn latency (descriptive), difficulty-path identity rate versus M1.
10. **Cluster-aware analysis.** Cluster is the structural unit; paired differences with cluster bootstrap and LOCO.
11. **Pre-stated predictions.** To be registered before running. No numerical expectation is stated here; each condition's effect is compared with the M1−B0 difference using the registered interval rule.
12. **Pass/fail criteria.** *Pass (architecture-specific):* no simpler controller matches M1 on the registered primary metrics within the registered equivalence margin **[AUTHOR TO CONFIRM: equivalence margin]**. *Fail:* at least one simpler controller does.
13. **Failure modes / threats.** A weakly implemented baseline favoring M1; tuning effort mismatch between baselines; a staircase controller that cannot use the same observation fields.
14. **Interpretation if positive.** The architecture contributes behavior not obtained by the tested simpler controllers, in this replay setting only.
15. **Interpretation if null.** The coordination claim narrows to "introducing any ledger-informed override changes behavior".
16. **Status.** **[RESULT PENDING - NOT RUN]**

---

## P2 — Closed-loop candidate simulator

1. **Motivation.** Replay fixes candidate responses; closed-loop adaptation and the Harder branch were not meaningfully exercised (no stretch proposals occurred).
2. **Hypothesis.** The architectural distinctions (coordination changes trajectories; specialization changes organization) persist when later observations depend on prior actions.
3. **Research question.** Do the effects persist under closed-loop simulated candidates with learning dynamics?
4. **Conditions.** B0, M1, M2, M4, Msplit, Munified (a subset sufficient to test the distinctions) under simulated personas: improving, plateauing, anxious, guessing, high-performing.
5. **Dataset / stimuli.** A simulator with persona-specific dynamics and the existing question bank. The high-performing persona is required so the Harder branch can be exercised. Personas are SIMULATED evidence and are not claimed to equal human learning.
6. **Sample size.** **[AUTHOR TO CONFIRM: planned sample size]** (personas × seeds × questions).
7. **Randomization / seeds.** Fixed, registered simulator seeds; personas and seeds shared across conditions; held-out personas never used for any controller or simulator tuning.
8. **Primary metrics.** Difficulty tracking error against persona ability, adaptation responsiveness, trajectory stability.
9. **Secondary metrics.** Level changes, reversals, Strategy admission rate, time to reach persona-appropriate level.
10. **Cluster-aware analysis.** Persona is the structural unit (seeds nested within persona); persona-level bootstrap and leave-one-persona-out; sessions and turns are descriptive.
11. **Pre-stated predictions.** Registered before running; none stated here.
12. **Pass/fail criteria.** *Pass:* the sign of the M1−B0 effect and the null Msplit−Munified result are preserved on held-out personas. *Fail:* sign reversal or specialization divergence.
13. **Failure modes / threats.** Simulator mismatch with real candidates; persona definitions that encode the controller's own assumptions; train/evaluation leakage.
14. **Interpretation if positive.** The distinctions are not artifacts of fixed replay, within simulated personas.
15. **Interpretation if null.** The replay-level conclusions are limited to open-loop stimuli.
16. **Status.** **[RESULT PENDING - NOT RUN]**

---

## P3 — Stronger grounding check

1. **Motivation.** XD: the lexical validator accepted unsupported paraphrased credit in 57/57 applicable cases.
2. **Hypothesis.** A semantic (embedding- or NLI-based) validator reduces unsupported-credit acceptance relative to the lexical validator.
3. **Research question.** Can semantic grounding reduce the specific weakness exposed by the lexical validator?
4. **Conditions.** Current lexical validator versus an embedding-based validator versus an NLI-based validator **[AUTHOR TO CONFIRM: planned model identities]**.
5. **Dataset / stimuli.** The XD authored probe set (64 evaluator payloads, seven constructed feedback categories), extended only by pre-registered additional categories if any.
6. **Sample size.** At least the XD applicable cases; **[AUTHOR TO CONFIRM: planned sample size]**.
7. **Randomization / seeds.** Fixed probe construction seeds; thresholds chosen on a development subset and frozen before the test subset.
8. **Primary metrics.** Unsupported-credit acceptance rate; supported-credit acceptance rate.
9. **Secondary metrics.** False rejection rate, precision/recall or a justified alternative, latency.
10. **Cluster-aware analysis.** Payload nested within question; question-level (or cluster-level) bootstrap.
11. **Pre-stated predictions.** Registered before running.
12. **Pass/fail criteria.** *Pass:* lower unsupported-credit acceptance with supported-credit acceptance not below a registered floor **[AUTHOR TO CONFIRM: floor]**.
13. **Failure modes / threats.** Probe set authored by the same team as the validator; threshold overfitting; trading false acceptance for false rejection.
14. **Interpretation if positive.** Stronger grounding addresses the lexical weakness on authored probes, not semantic correctness in general.
15. **Interpretation if null.** The weakness is not removed by the tested semantic validators.
16. **Status.** **[RESULT PENDING - NOT RUN]**

---

## P4 — LLM-backed Strategy Agent

1. **Motivation.** Agents in the completed study are rule/ledger based and replay uses no live LLM; authority mechanisms are untested for generative proposers.
2. **Hypothesis.** The typed-proposal and arbitration safeguards continue to contain invalid and adversarial proposals when the Strategy Agent is LLM-backed.
3. **Research question.** Do the authority mechanisms persist with generative agents?
4. **Conditions.** XB-matched fault-injection design with an LLM-backed Strategy Agent; optionally one small live-LLM run with faults injected at the LLM-output boundary.
5. **Dataset / stimuli.** Same replay stimuli as XB; model/version **[AUTHOR TO CONFIRM: planned LLM model/version]**; prompts and output schema registered.
6. **Sample size.** **[AUTHOR TO CONFIRM: planned sample size]**; the matched XB design uses 40 sessions per cell.
7. **Randomization / seeds.** Fixed order seeds; decoding settings (temperature, seed where supported) registered; repeated runs reported to expose stochasticity.
8. **Primary metrics.** Containment (session completes, scores authoritative, valid transitions), guardrail-bypass rate, schema-rejection rate.
9. **Secondary metrics.** Latency with the model in the loop, timeout/breaker events, proposal validity rate, injection point/fault-class breakdown.
10. **Cluster-aware analysis.** Cluster is the structural unit; stochastic repeats are nested within cluster.
11. **Pre-stated predictions.** Registered before running; none stated here.
12. **Pass/fail criteria.** *Pass:* committed-state invariants hold in all cells; *fail:* any protected-state change without central admission.
13. **Failure modes / threats.** Model nondeterminism; prompt sensitivity; cost limits on repeats; provider changes over time.
14. **Interpretation if positive.** Containment of structural faults carries over to one tested generative proposer.
15. **Interpretation if null.** Authority claims remain restricted to rule-based agents.
16. **Status.** **[RESULT PENDING - NOT RUN]**

---

## P5 — Evaluator validation and robustness

1. **Motivation.** Evaluator validity is not established; the exploratory analysis found R associated with answer length and a length-independent contribution was not established.
2. **Hypothesis.** To be registered per sub-protocol; none is asserted here.
3. **Research question.** Are evaluator scores robust to length and superficial cues, and aligned with independent ratings?
4. **Conditions.**
   - **P5A Weight selection.** Compare the 0.15/0.35/0.50 composition with R-only, a word-count baseline, equal weights, and candidate alternative weightings with R reduced or removed, using a development split and leave-one-question-out or nested cross-validation.
   - **P5B Robustness.** Padding attacks, keyword stuffing, paraphrase invariance, ASR-noise insertion, correct-short versus wrong-long pairs.
   - **P5C LLM-as-judge baseline.** Compare with an LLM-as-judge approach **[CITATION TO VERIFY]**.
   - **P5D Independently rated item set.** A length-balanced set with independent human ratings: short correct, long correct, short incorrect, long incorrect, technically correct paraphrases, keyword-stuffed answers, and other rubric-justified contrasts. Ethics approval and consent are required before rating; this dataset does not currently exist.
   - **P5E Alternative statistics.** A permutation test or a mixed-effects model as a robustness check relative to the 8-cluster bootstrap, because 8 clusters give limited resolution for the cluster bootstrap.
5. **Dataset / stimuli.** Existing 64 constructed answers (P5A, P5B); new length-balanced set (P5D).
6. **Sample size.** **[AUTHOR TO CONFIRM: planned sample size]** for P5D and for the number of raters.
7. **Randomization / seeds.** Fixed split seeds; rater assignment randomized and blinded to system scores.
8. **Primary metrics.** Rank correlation with independent ratings; length-controlled partial correlation; sensitivity to perturbations.
9. **Secondary metrics.** Calibration or an appropriate scoring metric where justified; confidence intervals; inter-rater agreement.
10. **Cluster-aware analysis.** Question is the structural unit for P5A/P5D (answers nested within question); cluster bootstrap, leave-one-question-out, and the P5E alternative.
11. **Pre-stated predictions.** Registered before running; none stated here.
12. **Pass/fail criteria.** Registered per sub-protocol, including a registered threshold for length-independent association **[AUTHOR TO CONFIRM: criteria]**.
13. **Failure modes / threats.** Rater provenance, ethics, and agreement; small samples; development/test leakage; length confounding in item construction.
14. **Interpretation if positive.** Evidence for a length-robust, externally rated evaluator, on the tested items only.
15. **Interpretation if null.** The evaluator dependence caveat in the manuscript stands, and weight changes may be warranted.
16. **Status (entire P5).** **[RESULT PENDING - NOT RUN]**

---

## P6 — Continuous or calibrated confidence

1. **Motivation.** XC's plateau over τ ∈ [0.5, 0.7] reflects a few discrete confidence values; finer threshold behavior was not resolved.
2. **Hypothesis.** Threshold behavior remains stable (admission rate and trajectory vary smoothly with τ) when confidence is continuous or calibrated.
3. **Research question.** Does the threshold behavior persist when confidence is not restricted to a few discrete values?
4. **Conditions.** Replace or supplement the heuristic min(0.95, 0.5 + 0.1n) with a continuous/calibrated confidence **[AUTHOR TO CONFIRM: confidence model definition]**; repeat the XC sweep on a registered, finer τ grid.
5. **Dataset / stimuli.** XC replay stimuli (8 clusters × 20 orders) unchanged.
6. **Sample size.** Same 160 sessions per τ; **[AUTHOR TO CONFIRM: planned τ grid]**.
7. **Randomization / seeds.** Same order seeds 0–19; calibration split registered and frozen.
8. **Primary metrics.** Strategy admission rate and level-change trajectory as functions of τ.
9. **Secondary metrics.** PPO agreement, guardrail overrides, calibration error if applicable, threshold sensitivity.
10. **Cluster-aware analysis.** Cluster bootstrap and LOCO as in XC.
11. **Pre-stated predictions.** Registered before running.
12. **Pass/fail criteria.** *Pass:* the plateau/monotonicity properties C1–C5 analogues are met on the finer grid; *fail:* abrupt, non-monotone, or cluster-specific admission behavior.
13. **Failure modes / threats.** Calibration data leakage; calibrating on the same replay clusters being evaluated.
14. **Interpretation if positive.** τ acts as a smooth admission control rather than only a coarse gate.
15. **Interpretation if null.** The XC plateau is specific to the discrete heuristic.
16. **Status.** **[RESULT PENDING - NOT RUN]**

---

## P7 — Formal / property-based authority testing

1. **Motivation.** Authority is central to the safety claim and currently supported only by the XB experiments.
2. **Hypothesis.** The invariant holds under systematically generated inputs: *no agent output can directly alter a committed score or other protected authoritative state; committed state changes only through the central admission path.*
3. **Research question.** Can the state-commit invariant be tested systematically, and do individual safeguards matter under mutation?
4. **Conditions.** Property-based generation of proposals covering forbidden-key mutation, stale-version mutation, malformed output, NaN values, invalid transitions, concurrent proposals, and duplicate proposals; plus mutation testing that disables or alters each safeguard individually.
5. **Dataset / stimuli.** Generated proposals and observations (SYNTHETIC); the real coordinator and hub.
6. **Sample size.** **[AUTHOR TO CONFIRM: planned number of generated cases and mutants]**.
7. **Randomization / seeds.** Registered generator seeds; shrinking of failing cases retained.
8. **Primary metrics.** Number of invariant violations (target: zero); mutation score (killed/total mutants).
9. **Secondary metrics.** Which safeguard caught each case; surviving mutants.
10. **Cluster-aware analysis.** Not a replay-cluster study; generated cases are independent by construction. Report the generator distribution and coverage.
11. **Pre-stated predictions.** Registered before running.
12. **Pass/fail criteria.** *Pass:* zero invariant violations over the registered case budget; every non-equivalent mutant killed or explained. *Fail:* any violation.
13. **Failure modes / threats.** Generator coverage gaps; equivalent mutants; a property that is weaker than the real invariant.
14. **Interpretation if positive.** Stronger evidence for the invariant over the generated input space, not a proof of general safety.
15. **Interpretation if null.** Violations identify missing safeguards and require redesign.
16. **Status.** **[RESULT PENDING - NOT RUN]**

---

## P8 — Small human study

1. **Motivation.** No human evaluation or candidate-learning evidence is currently present.
2. **Hypothesis.** To be registered; descriptive and exploratory in a small study.
3. **Research question.** What are the feedback quality, rubric face validity, and usability properties of the system, with appropriate ethics approval?
4. **Conditions.** (a) blinded expert review of generated feedback; (b) expert assessment of whether rubrics capture the intended technical concepts; (c) a small candidate-facing usability pilot.
5. **Dataset / stimuli.** Generated feedback and rubrics from the existing question bank; pilot sessions with consenting participants.
6. **Sample size.** **[AUTHOR TO CONFIRM: planned sample size]** (experts and candidates).
7. **Randomization / seeds.** Randomized review order; reviewers blinded to condition and system version.
8. **Primary metrics.** Expert rubric ratings and agreement; usability measures chosen before the pilot.
9. **Secondary metrics.** Free-text comments, time on task, error reports.
10. **Cluster-aware analysis.** Participant/reviewer is the structural unit; ratings nested within item; mixed-effects or participant-level bootstrap.
11. **Pre-stated predictions.** Registered before running; none stated here.
12. **Pass/fail criteria.** Registered descriptive thresholds **[AUTHOR TO CONFIRM: criteria]**; no efficacy claim is permitted from a small pilot.
13. **Failure modes / threats.** Self-selection, rater fatigue, social-desirability effects, small samples, unrepresentative participants.
14. **Interpretation if positive.** Descriptive feasibility and face validity only.
15. **Interpretation if null.** Rubric or feedback revisions before larger studies.
16. **Ethics and data handling (required before any human participation).** **Ethics approval is required before human participation.** Informed consent; data minimization; a retention policy; anonymization or pseudonymization; audio handling (recording, storage, deletion); reviewer blinding; consideration of adverse events (for example distress during mock interviews); and no use of voice-derived confidence as a psychological measure.
17. **Status.** **[RESULT PENDING - NOT RUN]**
