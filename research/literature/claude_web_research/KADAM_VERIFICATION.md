# Kadam et al. (2026): final field-by-field verification and comparison (final closure pass, 2026-09-21)

Literature note for later independent review. It changes no claim, result or frozen file. This file supersedes the earlier version of the same name; nothing that was VERIFIED there has been downgraded.

**Source.** S. Kadam, S. Banerjee, J. Christopher, P. T. V. Praveen Kumar, D. K. Satpathi, "A simulation framework for benchmarking reinforcement learning policies in adaptive mock-interview tutoring," *Simulation Modelling Practice and Theory*, vol. 151, Art. 103316, Sep. 2026 (online 9 Jul 2026), doi 10.1016/j.simpat.2026.103316. Peer-reviewed journal article.
URL used: https://www.sciencedirect.com/science/article/pii/S1569190X26000651 (in-app browser; page text read again in this pass).

## Access basis (read first)
The accessible source is the ScienceDirect landing page. It exposes the abstract, five highlights, the complete introduction (including the five listed contributions), the opening words of nine section snippets (design rationale, results and discussion, simulation limitations, conclusion), the first 10 of 42 references (the page's "View more references" control extends this), and an AI-writing declaration. The methods, equations, tables, figures and numerical results are not exposed. The article body remains behind a subscription ("People Education Society University does not subscribe to this content"). No paywall workaround was used; a preprint, code release, Zotero copy and repo copy were searched for and none was found.

Per the user's instruction in this pass, the elements listed in Table A are treated as VERIFIED from the accessible source. They were re-read in the page text and match; none is inferred. Everything in Table B stays NOT VERIFIED and no sentence in any paper may fill it in.

## Table A. Elements VERIFIED from the accessible source
| Element | Status | Exact accessible text (short) | Where |
|---|---|---|---|
| Simulation-based benchmark for adaptive mock-interview tutoring | VERIFIED | "a simulation framework for benchmarking question–content sequencing policies in adaptive mock-interview tutoring systems" | abstract |
| IRT-based learner-response model | VERIFIED (existence and role) | "an Item Response Theory-based response model together with simulated remediation effects from heterogeneous learning resources"; the limitations snippet says "IRT-inspired" | abstract; limitations snippet |
| Finite-horizon MDP | VERIFIED | "formulated as a finite-horizon Markov decision process where actions jointly determine question difficulty, learning outcome, and remediation modality" | abstract |
| Actions jointly set outcome, difficulty and modality | VERIFIED | same sentence; contributions call it a "factorized multi-discrete action space" | abstract; contributions |
| Rule-based heuristic | VERIFIED (existence) | "rule-based heuristics" among "several policy classes"; "the heuristic baseline" | abstract; introduction |
| DQN | VERIFIED (existence) | "model-free reinforcement learning methods (DQN, PPO)" | abstract |
| PPO | VERIFIED (existence and role as a compared policy) | same; highlight "PPO demonstrates stable learning under limited interactions" | abstract; highlights |
| PETS | VERIFIED (existence) | "model-based approaches (PETS, MBPO)"; PETS adapted "to a discrete and factorized tutoring action space" | abstract; introduction |
| MBPO | VERIFIED (existence) | same | abstract; introduction |
| Common simulator, state, reward, seed comparison | VERIFIED | "Using the same simulator, reward specification, state representation, and seed protocol, we compare a rule-based heuristic, model-free RL methods (DQN and PPO), and model-based RL methods (PETS and MBPO)." | contributions |
| Multi-metric evaluation | VERIFIED (names) | "time-to-mastery, question accuracy, post-content gain, mean frustration, blueprint adherence, seed stability, and computational cost" | contributions |
| Simulation-only evaluation | VERIFIED | "the results presented in this study are based on simulation experiments"; "Validation with real learner interaction data remains an important direction for future work" | introduction |
| Stated novelty | VERIFIED | "The novelty of the work lies in the integrated benchmarking setup rather than in proposing a new generic reinforcement learning algorithm" | abstract |

## Table B. Full field status (requested fields)
| Field | Status | What is accessible / what is not |
|---|---|---|
| Learner model | PARTIALLY VERIFIED | Accessible: latent mastery profile over learning outcomes; responses generated "probabilistically based on learner ability and question difficulty"; mastery evolves through "probabilistic update rules"; assumption-based. NOT accessible: IRT variant, parameter values, number of outcomes, update equations. |
| IRT parameterization / formula | NOT VERIFIED | Only "IRT-based" (abstract) and "IRT-inspired" (limitations). No 1PL/2PL/3PL statement. |
| State | PARTIALLY VERIFIED | "a learner state representing mastery over learning outcomes and interaction signals". Dimension, features, normalisation: NOT VERIFIED. |
| Actions | VERIFIED (structure) | Outcome x difficulty x modality, factorized multi-discrete. Number of levels per factor: NOT VERIFIED. |
| Reward | NOT VERIFIED | Only that the reward specification is shared and that the objective is "to maximize learning progress while respecting" budgets and blueprint constraints. |
| Horizon / budget | PARTIALLY VERIFIED | "finite-horizon", "fixed interaction budgets", one interaction is "one question–response cycle". Horizon length and budget value: NOT VERIFIED. |
| Constraints | PARTIALLY VERIFIED | Interaction budgets and curriculum-blueprint requirements "that regulate the distribution of question difficulties", inside the constrained MDP. Whether any post-policy filter or guardrail exists: NOT VERIFIED (none is described in the accessible text; that is not proof of absence). |
| Simulator | PARTIALLY VERIFIED | Stochastic; assumption-based; simulated remediation effects; frustration modelled. Calibration to data, code availability: NOT VERIFIED. |
| PPO | PARTIALLY VERIFIED | Existence, role as a model-free baseline, highlight and discussion statements (see Results). Library, network, hyperparameters, timesteps, action-space handling: NOT VERIFIED. |
| DQN | PARTIALLY VERIFIED | Existence only. Hyperparameters and factorized-action adaptation: NOT VERIFIED. |
| PETS | PARTIALLY VERIFIED | Existence and stated adaptation to a discrete factorized action space; the introduction warns that planning "in large multi-discrete action spaces can introduce model bias and instability". Implementation: NOT VERIFIED. |
| MBPO | PARTIALLY VERIFIED | Existence and stated adaptation. Implementation: NOT VERIFIED. |
| Heuristic | PARTIALLY VERIFIED | Existence only. Rules and whether it is the strongest baseline: NOT VERIFIED. |
| Training | NOT VERIFIED | Not accessible. |
| Evaluation | PARTIALLY VERIFIED | Same simulator, reward, state and "seed protocol" for all policies; the results section "focuses on learning performance, computational trade-offs, stability across random seeds, and pedagogical effectiveness across instructional modalities". Protocol details: NOT VERIFIED. |
| Seeds | NOT VERIFIED | "seed protocol" and "stability across random seeds" are mentioned. Number, role and any persona-level unit: nothing accessible. |
| Metrics | VERIFIED (names) | Seven metric names above. Definitions and units: NOT VERIFIED. |
| Results | PARTIALLY VERIFIED (qualitative only) | Discussion snippet: "Under the current simulator configuration, policy-gradient methods appear to provide a good balance between learning performance and training stability. In particular, PPO consistently achieves higher cumulative rewards while maintaining relatively stable question accuracy across different random seeds." Highlight: "Instructional modality influences simulated learning gains." Every number, and whether PPO beat the heuristic: NOT VERIFIED. |
| Objective | VERIFIED | Maximise learning progress under interaction-budget and blueprint constraints; benchmark for "evaluating sequential tutoring policies prior to deployment in real educational systems". |
| Limitations | PARTIALLY VERIFIED | Assumption-based learner model; simulator "a controlled policy-comparison environment rather than ... a fully validated model of human learning behaviour"; no real-learner validation. The rest of the limitations paragraph is cut off. |
| Exact novelty claim | VERIFIED | Abstract sentence in Table A; five contributions (simulator-based benchmarking framework, constrained sequential decision formulation, factorized action-space design, comparative evaluation of policy classes "under identical assumptions", multi-metric evaluation). |
| Exact PPO / DQN / PETS / MBPO hyperparameters | NOT VERIFIED | Not accessible. |
| Exact baseline set beyond heuristic, DQN, PPO, PETS, MBPO | NOT VERIFIED | The accessible text lists five controllers ("we benchmark five tutoring controllers"). |
| Constant-action or random baseline | NOT VERIFIED | Nothing accessible either way. |
| Post-policy safety / guardrail layer | NOT VERIFIED | Nothing accessible either way. |
| Code or data release | NOT VERIFIED | No statement seen. |

## KADAM / OUR comparison
Our-side statements come from the project's frozen evidence (X3-A: Delta MAE -0.0350, 95% CI [-0.0818, +0.0021], registered margin +/-0.12, two-way cluster bootstrap over 40 personas x 5 training seeds; read-only check in this pass) and the project brief. They are not restated from any other source.

**PROBLEM.** KADAM: benchmark policy classes for question-content-remediation sequencing in adaptive mock-interview tutoring. OUR: control the difficulty of the next question in a technical-interview preparation system and ask how much of a guardrailed controller's behaviour is attributable to a learned policy.
**SIMULATOR.** KADAM: stochastic latent-mastery learner, IRT-based ("IRT-inspired"), simulated remediation, frustration modelled; details NOT VERIFIED. OUR: simulated candidate personas with performance, confidence and hesitation signals; simulation-only.
**STATE.** KADAM: mastery over outcomes plus interaction signals; dimension NOT VERIFIED. OUR: 6-D in [0,1] (performance, average performance, confidence, hesitation, progress, difficulty/5).
**ACTIONS.** KADAM: factorized outcome x difficulty x modality. OUR: Discrete(3) easier / same / harder.
**PPO USE.** KADAM: one of five compared controllers; reported stable, higher cumulative reward (discussion sentence). OUR: the learned policy in a controlled decomposition against a state-blind constant action under identical guardrails; multiple training seeds; persona as the statistical unit.
**HEURISTIC.** KADAM: a rule-based baseline exists; rules and standing NOT VERIFIED. OUR: a heuristic controller that scores better than raw and guarded PPO on difficulty-tracking MAE in the frozen comparison.
**REWARD.** KADAM: shared across policies; contents NOT VERIFIED. OUR: as defined in the frozen project.
**EVALUATION.** KADAM: seven metrics, fixed interaction budgets, seed protocol; seed count NOT VERIFIED. OUR: difficulty-tracking MAE, volatility, guardrail intervention accounting, preregistered +/-0.12 equivalence margin, persona-level inference.
**NOVELTY CLAIM (KADAM).** "the integrated benchmarking setup rather than ... a new generic reinforcement learning algorithm". **DEFENSIBLE CONTRIBUTION (OUR).** A controlled decomposition and preregistered equivalence evaluation of a guardrailed learned difficulty policy against a state-blind constant action, in simulation.

**EXACT OVERLAP (verified parts only).** adaptive mock-interview tutoring; simulated learners with an IRT-based response model; finite-horizon sequential formulation; difficulty as a controlled quantity; PPO as a compared policy; a rule-based heuristic as a compared policy; benchmark-style, multi-seed, simulation-only policy evaluation; real-learner validation stated as future work; constraints built into the decision problem.
**EXACT DIFFERENCE (verified parts only).** their action space is factorized (outcome, difficulty, modality), ours is difficulty only; they compare DQN, PETS, MBPO as well, we do not; they state a benchmark/setup novelty, we intend a decomposition/equivalence contribution; their constraints are budgets and a curriculum blueprint inside the MDP, ours is a post-policy rule with intervention accounting (absent from the accessible text, not proven absent).
**Cannot be stated as a difference.** state, reward, seed count, heuristic quality, whether they include a constant or random baseline, an equivalence analysis or a guardrail, whether PPO beat their heuristic.

**NOVELTY THREAT.** High for any framing around PPO, adaptive mock-interview RL, the simulator, the benchmark or the heuristic comparison. Unresolved for the control comparison until the full text is read.

**SAFE FRAMING (proposal only).** "Under identical guardrails, a learned PPO difficulty policy was statistically equivalent, within a preregistered +/-0.12 MAE margin, to a state-blind constant action in simulation. Kadam et al. [26] benchmark PPO, DQN, PETS, MBPO and a rule-based heuristic for adaptive mock-interview tutoring with IRT-based simulated learners; we propose neither a new benchmark nor a new algorithm, and we do not compare against their simulator or policies." Do not add any sentence about what [26] lacks.

## Additional reading recorded here (not part of Kadam)
The introduction's own gap claim: "Within the mock-interview systems reviewed, prior work has mainly focused on feedback generation, behavioural analysis, and usability, whereas adaptive sequencing of questions and remediation resources based on evolving learner mastery has received limited attention [11], [12]." This is Kadam et al.'s statement about their own review, not evidence about the field. The visible reference list includes Doroudi et al. 2019 and Riedmann et al. 2025; both were read in this pass (see P3_RL_EDUCATION_REVIEWS.md).

## What would close the remaining gap
A legitimate full-text copy (institutional access, author-provided or open-access). Then read: state dimension, IRT form, horizon and budget, reward, hyperparameters, seed count and role, the PPO-versus-heuristic results, presence of a constant or random baseline, and any post-policy safety layer. Until then the high-level novelty position is locked (P3_FINAL_NOVELTY_POSITION.md) and these details are carried as "not verified".
