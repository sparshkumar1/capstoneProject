# Paper 3: final novelty position and focused final gap check (final closure pass, 2026-09-21)

Literature note only. It is a proposal for independent review. It does not change Paper 3's conclusions, the preregistration, frozen evidence or any claim file. The actual result stays as recorded in the frozen X3-A evidence: guardrailed PPO versus Constant-Same with the same guardrails, Delta MAE -0.0350, 95% CI [-0.0818, +0.0021], registered equivalence margin +/-0.12 (two-way cluster bootstrap over 40 personas x 5 training seeds). These figures were read from the frozen evidence files (read-only) and match the values given in the instruction.

## 1. What Kadam et al. establishes as prior art (verified parts; see KADAM_VERIFICATION.md)
- adaptive mock-interview tutoring as an application;
- simulation-based evaluation of policies before deployment;
- IRT-based simulated learners;
- RL policy comparison (DQN, PPO, PETS, MBPO) against a rule-based heuristic;
- PPO as a compared policy in that application;
- benchmark-style, multi-seed, multi-metric policy evaluation under a shared simulator, state, reward and seed protocol.

## 2. Framings that must not be used for Paper 3
- introducing RL to adaptive mock interviews;
- introducing PPO for adaptive interview difficulty;
- introducing a new adaptive mock-interview simulator;
- introducing a new RL benchmark for mock interviews;
- the first PPO adaptive-interview framework (no "first" wording of any kind).

## 3. Remaining defensible distinction (proposal, not applied)
A controlled decomposition and equivalence study of one specific interview-difficulty policy: PPO plus application-level guardrails versus Constant-Same plus the same guardrails, in the same simulated environment, judged on a registered criterion (difficulty-tracking MAE with a +/-0.12 margin), with explicit guardrail-intervention accounting and persona-level statistics.

**Proposed claim (do not apply; for independent claim review):** "controlled decomposition and preregistered equivalence evaluation of a guardrailed learned difficulty policy against a state-blind constant action in a simulated technical-interview setting."

What this claim does not say: that PPO is superior (the registered result is equivalence, and the heuristic scored better than PPO in the frozen comparison); that the setting, PPO or the simulator is new; that anything was tested with real candidates.

Residual uncertainty: Kadam et al. may contain a constant or random baseline, an equivalence analysis or a guardrail in the sections not accessible. The distinction is therefore stated relative to what could be read, and the manuscript must say only "we did not compare against their simulator or policies".

## 4. Terminology: "guardrail" versus "shield"
The guardrail is an application-level rule applied to the policy's action, with intervention counts. It carries no formal safety specification and no verified guarantee. The word "shield" has a specific meaning in the safe-RL literature (Alshiekh et al., AAAI 2018: enforcing a temporal-logic safety specification during learning and execution). That definition was not reopened in this pass (QUOTE_AUDIT row 3.13 stays UNVERIFIED), and the guardrail does not meet it on the project's own description. Use "guardrail" or "application-level rule"; do not use "shield" unless the exact definition is reopened and satisfied.

Related usage found in this pass (context, not competitor): Olukola and Rahimi (arXiv:2604.04251, full text read) contrast structural action-space constraints with "post-hoc filtering" applied only at evaluation, and report that reward shaping and post-hoc filtering "fail to separate from unconstrained baselines in all settings" of their tabular, simulated and dataset experiments. This shows that a filter-versus-learning comparison in educational RL has been studied, so intervention accounting and a guard layer must not be presented as new ideas. Their task (prerequisite-graph concept sequencing under a constrained MDP) and design (no state-blind constant baseline, no equivalence margin, as far as the text read shows) differ.

## 5. Broader RL-in-education positioning
See P3_RL_EDUCATION_REVIEWS.md. The reviews support three statements: simulation-only evaluation is a recognised limitation; baselines and statistical testing are inconsistent across the field; simple or classical methods are often competitive. They support a decomposition/equivalence study as a methodological contribution, and do not make it a new finding.

## 6. Focused final gap check (scope: the seven areas requested)
Only the areas below were searched, with a handful of queries in this pass, on top of the earlier passes recorded in PROVENANCE.md. The search stops here because no materially new direct competitor was found.

| Area | Result | Overlap class |
|---|---|---|
| Adaptive mock-interview tutoring | Kadam et al. 2026 remains the only interview-policy benchmark found. PolyInterview [44] is an interview platform without a difficulty policy. An interview-coach robot design study (Zhang et al., arXiv:2601.15600, abstract read, N=8) has no RL or difficulty policy. A student-authored review (IJRPR 2025, full text read) lists an "adaptive interview scoring with BERT and reinforcement learning" item attributed to "Kaur P. et al. 2024"; that underlying paper could not be located by search and the review has no experiment. Treat as UNVERIFIED and not usable. | direct: Kadam (already known); others contextual |
| RL-based adaptive interview difficulty | no additional item found beyond Kadam; the unverifiable Kaur item above | none new |
| CAT / IRT plus RL | Tang 2026, Wang 2024, Li et al. (Deep CAT), Qiu and Chen 2025, already classified as methodological or background (P3_ADAPTIVE_ASSESSMENT_PRIOR_ART.md); no new item | methodological |
| RL plus heuristic adaptive assessment | Jiang et al. [42] ("similar results"), Che et al. [28] (constant heuristic matches PPO), Schmucker et al. [41] (uniform policies close to contextual ones); Doroudi et al. report a greedy heuristic approximately as good as optimal in two simulated learner models (as reported in that review) | methodological / observational precedent for "simple approx learned" |
| Guardrailed adaptive difficulty | Olukola and Rahimi [29], MC-CPO (arXiv:2604.04251, V-TEXT): filter versus structural constraint in tutoring RL, 10 seeds; no constant baseline or equivalence margin seen | methodological |
| State-blind constant-action baselines | Che et al. [28] (constant "Repeat" heuristic); no study with a state-blind constant action under identical guardrails found | observational precedent only |
| Equivalence evaluation of learned adaptive policies | none found. Olukola and Rahimi (arXiv:2604.04237, full text read) explicitly warn that "The non-significant p-value should not be read as evidence of equivalence" (a caution, not an equivalence test). Lakens [35] supplies the method | methodological |

**Conclusion of the gap check.** No materially new direct competitor was found. This is a scope-limited statement: "not found by the queries listed in PROVENANCE.md, with Kadam et al. methods unread". No forward-citation index was available with the permitted tools, so citations to Kadam or Che could not be enumerated.

## 7. Effect on the Paper 3 novelty position
Unchanged in direction from the earlier passes. The application, PPO, IRT-simulated learners, heuristic comparison and benchmark framing are prior art. The observation that a learned tutoring policy is not better than a simple one has precedents ([28], [41], [42], and Doroudi et al.'s report). The narrower control design (identical guardrails, state-blind constant action, preregistered equivalence margin, intervention accounting) was not found in any source read. Confidence: medium; the residual risk is the unread portion of Kadam et al.
