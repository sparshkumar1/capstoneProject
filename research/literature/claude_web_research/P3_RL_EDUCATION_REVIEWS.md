# Paper 3: two RL-in-education reviews (final closure pass, 2026-09-21)

Used only to position the broader literature. Literature note; changes no claim.

## Sources and access
- **A. Riedmann, Schaper, Lugrin (2025).** "Reinforcement Learning in Education: A Systematic Literature Review," *International Journal of Artificial Intelligence in Education*, vol. 35, pp. 2669-2723, published 10 July 2025, doi 10.1007/s40593-025-00494-6, open access. Page text read in the in-app browser (V-TEXT). The extracted text was cut at 60,000 characters, so statements that something is "absent" apply to the part read only.
- **B. Doroudi, Aleven, Brunskill (2019).** "Where's the Reward? A Review of Reinforcement Learning for Instructional Sequencing," *IJAIED* 29(4), 568-620 (volume and pages as listed in search results; the DOI is 10.1007/s40593-019-00187-x). Author version PDF from the first author's university page read as text (V-TEXT); page numbers of the author version differ from the journal's.

## A. Riedmann et al. (2025)
- Scope: PRISMA review of "89 manuscripts from three databases (IEEE Xplore, Google Scholar, and ACM) published between 2000 and 2024".
- Evaluation setting (their classification): live with learners n = 41; "based on real interaction datasets (n = 23), or with simulated users (n = 24)". Simulation is therefore a common evaluation mode.
- Baselines: "random baselines were used by one-third of all reviewed papers (n = 31)"; expert-crafted baselines 19; comparisons to other RL approaches 20; "Some papers also used heuristic policies (n = 4)"; 18 publications specified no baseline (counts as extracted; the categories overlap).
- Statistics: "Among the studies that were accompanied by statistical testing (n = 35)". "only 20% of the reviewed papers were able to demonstrate that at least one RL policy significantly outperformed all baselines, this rises to 51% if only papers with statistical tests for significance are considered."
- Algorithm finding: "only 36% of DRL approaches significantly outperformed the baseline", against "61% of papers utilizing classical RL methods, such as Q-learning or policy iteration"; the authors read this as classical approaches still appearing "effective and sufficient for various educational settings".
- Limitations named in the abstract: "methodological issues, and the need for broader and more large-scale deployments and evaluations with actual users relative to only using simulated data."
- Adaptation: instructional sequencing (content, pace, difficulty) is more common than guidance-related adaptation.
- Not found in the text read: equivalence testing, non-adaptive constant-action controls under identical constraints, guardrail intervention accounting (absence within the extracted text only).

## B. Doroudi et al. (2019)
- Method: a historical narrative (three waves) plus a review of "all of the empirical research that has compared RL-induced instructional policies to baseline methods of sequencing".
- Finding: "over half of the studies found that RL-induced policies significantly outperform baselines"; five clusters of studies; "reinforcement learning has been most successful in cases where it has been constrained with ideas and theories from cognitive psychology and the learning sciences", complemented by "more robust offline analyses that do not rely heavily on the assumptions of one particular model".
- Relevant observation (as reported by the review): a greedy heuristic policy was justified by simulations showing it "can be approximately as good as the optimal policy according to two different cognitive models (ACT-R and MCM)" (attributed there to Lindsey et al. 2014 and Khajah et al. 2014, which were not opened). This is an older precedent for "a simple policy approximates a learned or optimal one" in simulation, recorded as background only.
- The review covers work up to 2019 and does not treat modern PPO controllers.

## What this means for Paper 3 positioning
| Question | Answer from the two reviews |
|---|---|
| Common RL algorithms | Q-learning, SARSA, DQN and other deep RL, policy-gradient and actor-critic families are all present; PPO is described as a standard method (A). Classical RL is reported as at least as often successful as deep RL (A). |
| Adaptive sequencing approaches | Content selection, pace and difficulty (A); theory-constrained RL works best (B). |
| Simulation versus real users | Simulated evaluation is common (24 of 89 in A) and is named as a limitation relative to live evaluation; B also stresses model-dependence. |
| Typical methodological limitations | No statistical test in many papers (A: only 35 with tests); baseline choice inconsistent, with random baselines dominating (A); reliance on one learner model (B). |
| Position of a decomposition/equivalence study | Consistent with the reviews' methodological recommendations: report a non-adaptive or simple control, use tests and intervals, and state that simulation results make no learner-outcome claim. Not a new finding about RL in education. |

The reviews do not contain a direct competitor for the control design. They also do not license any claim that a state-blind constant action is a standard baseline; the reviews' baseline categories are random, expert, non-adaptive, heuristic and other RL approaches.

## Quotation status
Every quoted passage above matched the source text (see QUOTE_AUDIT.md section 5). The counts for Riedmann et al. are as extracted from the page text and should be rechecked against the printed version before use.
