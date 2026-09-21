# Paper 3 core literature (guardrailed adaptive-difficulty RL), 2026-09-21

## MANDATORY DIRECT COMPARISON: Kadam et al. (2026) vs PrepAIred Paper 3

**Source.** S. Kadam, S. Banerjee, J. Christopher, P. T. V. Praveen Kumar, D. K. Satpathi, "A simulation framework for benchmarking reinforcement learning policies in adaptive mock-interview tutoring," *Simulation Modelling Practice and Theory*, vol. 151, Art. 103316, Sep. 2026 (online 9 Jul 2026), doi 10.1016/j.simpat.2026.103316, ISSN 1569-190X, article type "Full-length article".

**Access and verification (read this first).** The ScienceDirect page is paywalled for this institution. Through the browser pane I read directly: the abstract, the five highlights, the full introduction, the list of five contributions, the opening lines of five sections ("Section snippets"), and the first 5-10 references. **V-TEXT for those parts.** I did **not** read the methods sections, equations, tables, figures or numerical results. Every "not verified" below means exactly that. A full copy is required before any statement in the manuscript compares numbers, state dimensions, reward terms or seeds.

**Exact short passages (page text).**
- "The novelty of the work lies in the integrated benchmarking setup rather than in proposing a new generic reinforcement learning algorithm."
- "The tutoring process is formulated as a finite-horizon Markov decision process where actions jointly determine question difficulty, learning outcome, and remediation modality."
- "we evaluate several policy classes including rule-based heuristics, model-free reinforcement learning methods (DQN, PPO), and model-based approaches (PETS, MBPO)."
- Highlights: "PPO demonstrates stable learning under limited interactions." "Constrained MDP formulation for mock interview tutoring."
- Discussion snippet: "PPO consistently achieves higher cumulative rewards while maintaining relatively stable question accuracy across different random seeds."
- "the simulator is used here as a controlled policy-comparison environment rather than as a fully validated model of human learning behaviour."
- Simulation limitations snippet: "The learner model used in this study is assumption-based: responses are generated using an IRT-inspired model, mastery evolves through probabilistic update rules, and remediation effects are simulated ..." (the source continues "rather than estimated"; end the quote with an ellipsis).

**Gap-closure pass (2026-09-21): the fuller, field-by-field verification is in `KADAM_VERIFICATION.md`. Full text was still NOT accessible; the table below is unchanged and its "not verified" entries stand.** The prior-art check for adaptive testing, bandits, knowledge tracing and interview systems is in `P3_ADAPTIVE_ASSESSMENT_PRIOR_ART.md`.

| Field | Kadam et al. 2026 | PrepAIred Paper 3 | Verified? |
|---|---|---|---|
| Application/problem | Adaptive mock-interview tutoring: alternating assessment (question) and remediation (resource); sequencing of questions and content | Adaptive difficulty control in a multimodal technical-interview preparation system | Yes (intro) |
| Learner simulator | Stochastic simulator with latent mastery over multiple learning outcomes; assumption-based; simulated remediation effects from heterogeneous resources | Simulated candidates/personas (persona is the statistical unit) | Yes for theirs (abstract, limitations snippet) |
| IRT | Yes: IRT-based response model ("IRT-inspired" in limitations) | Not the core of the reported comparison; no Elo/IRT baseline run | Yes |
| MDP formulation | Finite-horizon constrained MDP | Episodic simulated interview environment with 6-D state | Yes for theirs |
| State | Mastery over learning outcomes plus interaction signals (dimension not verified) | 6-D in [0,1]: performance, average performance, confidence, hesitation, progress, difficulty/5 | Theirs partly |
| Actions | Factorized multi-discrete: learning outcome x difficulty x remediation modality | Discrete(3): easier / same / harder | Yes |
| Difficulty adaptation | Part of the joint action; curriculum blueprint constrains the difficulty distribution | The whole action space; adaptation only along difficulty | Yes |
| PPO | Yes (model-free baseline) | Yes (SB3 PPO, MLP [64,64]) | Yes |
| DQN | Yes | No | Yes |
| Model-based RL | Yes: PETS, MBPO adapted to the factorized action space | No | Yes |
| Heuristic | Yes: rule-based heuristic among policy classes (its rules not verified) | Yes: heuristic controller; currently better than PPO in the frozen comparison | Existence yes; performance vs RL not verified |
| Reward | Shared reward definition across policies (contents not verified) | Reward with oracle-like alignment terms (per current position) | Theirs no |
| Metrics | Time-to-mastery, question accuracy, post-content gain, mean frustration, blueprint adherence, seed stability, computational cost | Difficulty-tracking MAE, volatility, guardrail interventions | Yes (intro list) |
| Seeds | "sensitivity to random seeds" and "seed protocol" stated; number not verified | Multiple training seeds; persona as unit | Number no |
| Training/evaluation setup | Same simulator, reward, state and seed protocol for all policies; fixed interaction budgets | Training and evaluation environments differ (known limitation) | Theirs partly |
| Findings | PPO stable, higher cumulative reward (discussion snippet); instructional modality influences simulated learning gains; differences in efficiency, stability, time-to-mastery | PPO+guardrail approximately equivalent to Constant-Same+guardrails under a +/-0.12 MAE margin; heuristic better | Theirs at highlight/snippet level |
| Limitations | Assumption-based learner model; no validation with real learner data | Simulation-only; oracle-like reward; policy mostly "Same"; guarded PPO more volatile | Yes |
| Guardrails/safety | "Constraints": interaction budget and curriculum blueprint inside the constrained MDP; no post-policy intervention layer reported in what I read | Post-policy application-level rule with intervention accounting | Partly |
| Real users | None (future work) | None | Yes |

**Answers required by the master prompt.**
- *Existing overlap:* the "RL policies benchmarked against a rule-based heuristic (and DQN, PPO, model-based methods) in a simulator with IRT-based learners for adaptive mock-interview tutoring" problem space is occupied by this paper at the application/problem-definition level, including PPO, a heuristic baseline, a simulated learner and multi-seed evaluation. It was published online 9 Jul 2026, before PrepAIred's frozen work is written up.
- *What is different:* (a) PrepAIred's decision is one-dimensional (difficulty), theirs is a factorized action including outcome and remediation modality; (b) PrepAIred adds a post-policy guardrail layer with intervention accounting; theirs encodes constraints inside the MDP (as far as I read); (c) PrepAIred's headline is a preregistered equivalence test against a state-blind constant action under the same guardrails, a control design I did not see in what I read; (d) the statistical unit is the persona with training seed as a second factor; (e) PrepAIred reports a negative/equivalence result, whereas their headline is that PPO is stable and reaches higher reward.
- *What remains novel (within the searched literature; scope = queries in PROVENANCE.md and the partial read):* the controlled decomposition of a learned policy vs a state-blind constant action under identical constraints with a registered equivalence margin, and the intervention-accounting of the guard layer. I cannot claim more.
- *What is no longer novel:* RL (PPO) for adaptive difficulty/tutoring in simulation; PPO vs a rule-based baseline; simulated learners; IRT-based response simulation; "simulation-based benchmark for RL tutoring policies for mock interviews"; factorised action spaces are theirs, not ours.
- *Recommended framing (proposal for review only):* not "PPO for adaptive interview difficulty", and not "a benchmark for RL in mock interviews". Frame as a controlled decomposition/negative-result study: how much of the behaviour of a guardrailed adaptive-difficulty controller is attributable to the learned policy versus the constraint layer, with an equivalence test, in a simulated technical-interview setting. Cite Kadam et al. as the closest application-level benchmark and state plainly that it evaluates policy classes with a heuristic baseline, and that PrepAIred's contribution is the control comparison, not the setting.

**Reviewer characterization question ("incremental PPO application?").** Yes, if the paper is framed around PPO or the interview setting. The 2026 paper, the 2025 Axak et al. paper and Che et al. together make that framing weak.

## Other core sources

**Che et al., Sci. Rep. 2025 (W3-03), V-PAGE.** PPO tutor with three discrete interventions in a simulator; full agent mean reward 6.563 vs random 5.231, heuristic "Repeat" 6.564, heuristic "Hint" 5.564; the ablation without cognitive-behavioural signals scored 5.213, "as good as a random baseline"; the trained agent selected task repetition for 99.9% of actions. These numbers are as extracted by the fetch tool; re-verify. Relevance: a published precedent in which a PPO tutoring policy collapses to one action and a constant-action heuristic matches it. This is the strongest *observational* threat to novelty of "PPO is approximately a constant policy". Difference: no guard layer, no registered equivalence test, and the authors present the result as a success.

**Axak, Kushnaryov, Tatarnykov, CEUR Vol. 4048, ICST-2025 (W3-02), V-TEXT.** PPO vs DQN vs rule-based tutor in a custom Gym simulator; "a fixed random seed was used across all runs"; 50,000 timesteps; replay on 0.9 million ASSISTments-2017 logs; PPO reported +17% NDCG and +4.4% IPS-reward over the rule-based baseline. Relevance: claims PPO superiority with one seed, the opposite of PrepAIred's evidence standard. Difference in rigor is a legitimate contrast, phrased neutrally.

**Olukola and Rahimi, arXiv:2604.04237 (W3-04), V-PAGE.** Simulated tutoring, 120 sessions, 18,000 interactions; the constrained architecture reduced the reward-hacking index from 0.317 to 0.102. Relevance: constraints in tutoring RL are studied; PrepAIred's oracle-like reward terms should be assessed against this reward-alignment concern.

**Adaptive testing with RL (W3-05, W3-06).** Deep CAT (Psychometrika 2026, double deep Q-learning under multivariate IRT) and a DQN item-selection study (Behav. Res. Methods 2024) compare RL against information-based item selection. Relevance: the CAT/IRT strand is a mature comparator family; an Elo/IRT baseline was not run in PrepAIred and is a missing comparator.

**Shielding and runtime enforcement (W3-07, W3-08, W3-15).** Alshiekh et al. (AAAI 2018) define shields as restricting agent actions during learning and test time to satisfy a safety specification in a temporal-logic fragment (search summary; original not opened). PrepAIred's guardrail is an application-level, post-policy rule and does not use a formal specification or verified safety guarantee; it must not be called a shield. Guard-layer/action-masking work exists as a related family.

**Methodology (W3-10, W3-11).** Agarwal et al. (NeurIPS 2021) on interval estimates with few runs; Lakens (SPPS 2017) on TOST equivalence testing. These support the evaluation design but do not make it novel.

**Reviews (W3-12).** Riedmann et al. (IJAIED 2025), 89 manuscripts 2000-2024 (search summary): baseline categories in reviewed studies. Earlier pass (CARRY P3-10) recorded that random baselines dominate and non-adaptive controls are recommended; not re-verified here.

## Final-closure pointer (2026-09-21)
The final Paper 3 novelty position, guardrail terminology and the focused final gap check are in `P3_FINAL_NOVELTY_POSITION.md`; the two RL-in-education reviews are in `P3_RL_EDUCATION_REVIEWS.md`; the Kadam status is in `KADAM_VERIFICATION.md` (Table A verified; Table B remainder unverified). The comparison table above is retained; where it says a Kadam field is "not verified", that still stands for state dimension, reward, seeds, numbers, constant baseline and any post-policy guardrail.
