<!-- PAPER 3 MANUSCRIPT DRAFT v1 (2026-09-21). Markdown source; venue not final. Controlled decomposition / equivalence evaluation, simulation only. -->
<!-- Numbers trace to research/confirmatory/X3-A/results, research/analysis/x3a_o7/results, research/analysis/phase1/x3_0 and research/experiments/paper3/frozen_config.yaml (see claim_ledger.md). No number was recomputed except (D) tallies read from the stored turn log. -->

# A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews

*Authors and affiliations: withheld in this draft (anonymity requirement of the target venue is not verified).*

**Abstract—** Adaptive difficulty controllers for technical-interview practice are often reported with a learned policy and a rule-based constraint layer bundled together, so the learned component's own contribution is unclear. We report a controlled comparison in simulation, in which a learned proximal-policy-optimisation (PPO) difficulty controller and a state-blind Constant-Same policy run under an identical application-level rule-based guardrail layer. Using five frozen PPO checkpoints, 40 authored candidate personas and 20 evaluation seeds, the registered primary endpoint was the persona-level difference in mean absolute error (MAE) between the session difficulty and an authored target difficulty, analysed with a two-way cluster bootstrap over personas and training seeds against a registered equivalence margin of ±0.12. The difference (PPO minus Constant-Same) was −0.0350 (95% interval [−0.0818, +0.0021]), classified equivalent within the margin; superiority (upper bound below −0.20) was not met, and the classification was unchanged in three registered sensitivity analyses. The equivalence does not show that the two policies behave identically: in a five-persona replay the guardrail layer matched on 563 of 1250 turns but changed the proposed action on 99, the final-action sequence differed from Constant-Same in 50 of 125 sessions, and PPO's trajectory volatility was higher than that of Constant-Same. The evidence is simulation-only, uses authored personas, targets and margin, and the checkpoints were trained against a single simulated candidate. It supports no claim of learned-policy benefit or of benefit to real learners.

**Keywords—** adaptive difficulty; equivalence testing; reinforcement learning; simulated candidates; rule-based guardrails; technical interviews

---

## I. Introduction

Adaptive systems for interview or tutoring practice adjust question difficulty in response to a learner's performance. When the adjustment policy is learned, and when a hand-written constraint layer sits between the policy and the learner, a measured outcome cannot be attributed to the learned component without a comparison in which the constraint layer is held fixed. Two questions follow: what does the learned policy add once the same constraints apply to a much simpler policy, and how differently do the two policies actually behave?

The literature makes both questions relevant. Simulation-based studies of adaptive mock-interview tutoring already compare rule-based heuristics with several reinforcement-learning methods, including PPO [1]. Reviews of reinforcement learning in education report inconsistent baselines, frequent reliance on simulated users, and that a minority of studies show learned policies significantly outperforming all baselines [2], [3]. Studies that compare learned tutoring policies with simple alternatives report cases in which the learned policy did not differ significantly from an expert policy [4], in which effect sizes may be too small for contextual policies to improve on policies that give the same action to all students [5], and in which a trained policy collapsed towards one action and performed close to a constant heuristic [7]. Constraint layers around learned tutoring policies have been studied as constrained optimisation, and comparisons of structural constraints with post-hoc filtering exist [8]. Equivalence conclusions require a stated margin and an interval inside it [12], [13]; evaluating reinforcement-learning results requires uncertainty over runs [10], [11].

What is less often reported is a comparison of a learned difficulty policy with a state-blind constant action under the same guardrail layer, with an equivalence analysis and an account of how often the guardrails act and how often the two policies actually diverge. This study provides that comparison for one set of frozen checkpoints in one simulator. It does not propose a new application, algorithm, simulator or benchmark; adaptive mock-interview tutoring with simulation, an item-response-theory-based learner model, a finite-horizon Markov decision process and a heuristic, DQN, PPO, PETS and MBPO comparison is already reported in [1], whose body we did not read beyond its abstract, highlights and contribution statements.

We evaluated the registered contrast between PPO with the guardrail layer and Constant-Same with the same layer, using persona-level tracking error, and we report guardrail accounting, trajectory divergence and volatility alongside. The registered primary result is an equivalence classification, with a difference of −0.0350 and an interval of [−0.0818, +0.0021] against a margin of ±0.12. Secondary analyses show that the policies are not behaviourally identical.

The research question is: *Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?* The contribution is controlled decomposition and equivalence evidence: (1) a matched-policy comparison under identical guardrails; (2) a registered equivalence result with three registered sensitivity analyses; (3) guardrail accounting that separates rule activations from action overrides; and (4) an explicit list of what the simulation cannot support. Equivalence within a margin is not evidence of no difference, and no claim of learned-policy superiority or of learner benefit is made.

## II. Related Work

**Adaptive mock-interview tutoring and reinforcement learning in education.** Kadam et al. report a simulation framework for benchmarking policies in adaptive mock-interview tutoring, with an item-response-theory-based response model, a finite-horizon Markov decision process and a comparison of a heuristic, DQN, PPO, PETS and MBPO under a common simulator, reward, state and seed protocol [1]. They describe the simulator as a controlled policy-comparison environment and not as a fully validated model of human learning. Riedmann et al. review 89 manuscripts on reinforcement learning in education and report that only 20% demonstrated a policy significantly outperforming all baselines (51% among papers with statistical tests), and call for more evaluation with actual users [2]. Doroudi et al. review reinforcement learning for instructional sequencing and report that policies constrained by learning-science theory were most successful [3]. This study is one further controlled comparison within that setting; it does not use the simulator or policies of [1].

**Simple baselines and near-equivalence.** Batch reinforcement-learning pedagogical policies did not differ significantly from an expert policy in one condition of a student study (N = 84) and did in a second condition with explanations (p = 0.046) [4]; a large-scale tutoring study reports that effect sizes may often be too small for contextual policies to improve on well-optimised policies that deliver the same action to all students [5]; in a simulated classroom, reinforcement learning and greedy heuristics gave similar results [6]; and a trained tutoring policy has been reported to choose one action in 99.9% of its final choices and to perform close to the constant heuristic [7]. These are heterogeneous settings, and none is evidence for the present simulator.

**Constraint layers.** In safe reinforcement learning, a "shield" denotes enforcement of a formally specified safety property [9]. The layer studied here is a hand-written set of rules with no formal specification and no safety guarantee, so we call it an application-level rule-based guardrail. Work on pedagogically constrained tutoring policies compares structural constraints with post-hoc filtering [8].

**Evaluation methodology.** Reporting uncertainty over runs and seeds [10], [11], and equivalence testing with a stated smallest effect of interest [12], [13], frame the analysis. We found no literature basis for the registered margin of ±0.12, which is a design choice. Elo-type rating systems provide simple adaptive baselines in educational systems [14]; none was run here.

## III. Simulator, Policies and Guardrail Layer

**State, actions and simulator.** The controller observes a 6-dimensional state in [0, 1] (latest score, rolling mean of the last five scores, confidence, hesitation, progress, and difficulty divided by 5) and chooses among three actions: Easier, Same, Harder. A simulated candidate has a persona type and a skill and produces a performance, confidence, hesitation and response-time signal for the current difficulty. Difficulty lies in [1, 5] and starts at 3.0 in evaluation; each action moves difficulty by one integer step, clipped at the bounds. The simulator, the persona types and the target rule are authored by the study team. Simulated candidate outputs are not calibrated to real candidates.

**Personas and target.** The primary stratum is a full factorial of five persona types (normal, nervous expert, lucky guesser, overconfident-fail, struggling junior) and eight skills (0.20 to 0.90), giving 40 personas. Each persona's target difficulty is round(10·skill)/2 (1.0 to 4.5), an authored rule not tuned per persona. A session has 10 turns. The tracking error of a session is the mean absolute difference between the difficulty at each turn and the target.

**Policies.** *PPO*: the five frozen checkpoints (training seeds 42, 123, 456, 789, 999), each trained for 24,576 timesteps with a stable-baselines PPO (MLP 64×64, learning rate 3·10⁻⁴, γ = 0.99, clip 0.20), evaluated deterministically. The training reward is a weighted sum containing a decision-alignment term (agreement of the chosen action with an authored oracle rule, weight 0.60), an outcome-change term, a shaping term, a stability penalty and critical-state terms. Each checkpoint was trained against a single default simulated candidate (persona normal, skill 0.60, target 3.0), with the guardrail layer active inside the training environment, 15-turn episodes and continuous 0.1 difficulty steps; evaluation uses 10 turns and integer steps. The candidate's noise was unseeded in training, so the checkpoints are frozen artifacts and cannot be regenerated. *Constant-Same*: always proposes Same and has no state input. *Comparators for secondary contrasts*: a threshold heuristic, an oracle rule, a controller acting on the gap between the rolling-average score and the current difficulty (documented as exploiting the persona target rule), a uniform random policy, and PPO with the observation zeroed or taken from another persona.

**Application-level rule-based guardrail layer.** Rules are applied in a fixed priority order to the proposed action. G0 (infrastructure failure) holds difficulty; G4 (score below 0.30 and hesitation above 0.60) forces Easier; G1 (score below 0.30 at mid difficulty) forces Easier; G2 (confidence below 0.30, hesitation above 0.70, score below 0.80) forces Same; G5 (score between 0.40 and 0.65 with rolling mean below 0.60) forces Same; G6 (score at least 0.90 and a large gap, not a nervous expert) forces Harder. The layer is identical for both policies. We distinguish three counts: a *rule activation* is a turn on which any rule matched; an *action override* is a turn on which the final action differs from the proposed action; and an *attempted boundary action* is a final action that would move difficulty beyond [1, 5] before clipping. The frozen code names the activation flag "overridden", which is not the meaning used here. We call none of these counts "interventions". The layer has no formal safety specification, and no safety guarantee is claimed; boundary-saturated attempted actions are counted before simulator clipping and are not called violations.

## IV. Study Design

**Registered primary comparison (X3-A).** The contrast is PPO with guardrails minus Constant-Same with guardrails. The unit is the persona: for each persona, session tracking error is averaged over 20 evaluation seeds, and the PPO term is averaged over the 5 training seeds. The estimate is the mean of persona-level differences over the 40 personas. The interval is a two-way cluster bootstrap that resamples the 40 personas and the 5 training seeds with replacement (B = 10,000, seed 42, 95% percentile). The registered classification rule is: *equivalent* if the interval lies entirely inside (−0.12, +0.12); *PPO-superior* if its upper bound is below −0.20; *PPO-adverse* if its lower bound is above +0.12; otherwise inconclusive. The margins were fixed by the study team before the analysis; no literature justification for ±0.12 was found. A follow-up retraining experiment (X3-B) was to run only if the class were not equivalent; it was not triggered. Sessions and turns are descriptive.

**Registered sensitivity analyses (O7).** Three analyses were registered before they were run, as secondary evidence: a persona-only bootstrap (checkpoints fixed), a seed-level t interval (df = 4), and leave-one-seed-out. A reproduction gate reproduced the primary estimate exactly.

**Secondary contrasts.** Volatility (mean absolute difficulty change per turn), oscillation, observation use, comparators, guardrail on versus off and rule ablations are descriptive, with no multiplicity control.

**Five-persona frozen replay.** The behavioural accounting in Sections V-C and V-D uses an evaluation-only replay of the frozen checkpoints on five previously fixed personas (skills 0.20, 0.30, 0.60, 0.80, 0.88; targets 1.0, 1.5, 3.0, 4.0, 4.5), 5 evaluation seeds and 5 training seeds (25 sessions of 10 turns per condition; 125 PPO sessions). It is a separate, descriptive dataset and its results are never merged with the 40-persona result.

**Registration status.** The protocol and sensitivity analyses carry annotated git tags created before the runs; the repository was not pushed to a public registry, so registration is author-controlled and not externally time-stamped.

## V. Results

### A. Primary equivalence result

**Table I. Registered primary result (40 personas × 5 training seeds; tracking MAE, PPO+guardrail minus Constant-Same+guardrail).**

| Quantity | Value |
|---|---|
| Difference | −0.0350 |
| 95% two-way cluster bootstrap interval | [−0.0818, +0.0021] |
| Persona-level SD of differences; Cohen's d_z | 0.1015; −0.345 |
| Equivalence margin; superiority threshold | ±0.12; −0.20 |
| Classification | Equivalent (interval inside ±0.12); superiority not met |
| Mean MAE: Constant-Same+G; PPO+G (descriptive) | 1.1039; 1.0688 |

Both policies had a mean tracking error close to one difficulty level. Constant-Same without guardrails has a mean error of exactly 1.000, because the starting difficulty (3.0) lies at the centre of the target range, so a policy that never moves is a strong reference in this simulator. Equivalence within ±0.12 means the interval lies inside the registered margin; it is not evidence that the difference is zero, and it does not support a claim that PPO tracks better. The interval's upper bound (+0.0021) is close to zero and its lower bound (−0.0818) is well above the superiority threshold.

### B. Sensitivity analyses

**Table II. Registered sensitivity analyses (difference = PPO+G minus Constant-Same+G).**

| Analysis | Difference | 95% interval | Class |
|---|---|---|---|
| Registered primary | −0.0350 | [−0.0818, +0.0021] | Equivalent |
| Persona-only bootstrap (checkpoints fixed) | −0.0350 | [−0.0673, −0.0052] | Equivalent |
| Seed-level t interval (df = 4) | −0.0350 | [−0.0758, +0.0057] | Equivalent |
| Leave out seed 42 | −0.0234 | [−0.0614, +0.0092] | Equivalent |
| Leave out seed 123 | −0.0463 | [−0.0948, −0.0043] | Equivalent |
| Leave out seed 456 | −0.0335 | [−0.0874, +0.0070] | Equivalent |
| Leave out seed 789 | −0.0372 | [−0.0873, −0.0005] | Equivalent |
| Leave out seed 999 | −0.0348 | [−0.0898, +0.0078] | Equivalent |

All eight intervals lie inside ±0.12 and none has an upper bound below −0.20, so superiority was never established. Three of these intervals (persona-only, leaving out seed 123, leaving out seed 789) exclude zero on the side numerically favouring PPO; the persona-only interval excludes checkpoint-to-checkpoint variability by design. These results leave the registered classification unchanged but do not license the statement that PPO tracks better. Seed-level differences were −0.0816 (seed 42), +0.0100 (123), −0.0411 (456), −0.0266 (789) and −0.0359 (999); the persona-level SD (0.1015) is about three times the mean difference. Sensitivity analyses are secondary and do not replace the registered result.

### C. Guardrail accounting (five-persona replay)

**Table III. Guardrail accounting for PPO+guardrail, five-persona replay (125 sessions, 1250 turns).**

| Count | Value | Definition |
|---|---|---|
| Rule activations | 563 of 1250 turns (45.0%) | any rule matched |
| Action overrides | 99 of 1250 turns (7.9%) | final action differs from proposed action |
| Activations that did not change the action | 464 | matched rule agreed with the proposal |
| Sessions with at least one override | 41 of 125 | — |
| Attempted boundary actions before clipping: guardrails on / raw PPO | 232 (18.6%) / 136 (10.9%) | final action beyond [1, 5]; not violations |

By rule, activations were G5 205, G4 167, G1 111 and G2 80; G6 never matched. Overrides came from G1 (49), G2 (35) and G4 (15); G5 (205 activations) never changed the action, and all overrides arose in two of the five personas. By direction (D): 30 turns replaced a proposed Easier by Same (a blocked decrease), 30 replaced Same by Easier, and 39 replaced a proposed Harder (34 by Easier and 5 by Same), so the layer both raised and lowered the difficulty proposed by PPO and did not act only towards easier questions. The 563 activations are not interventions: 82.4% of them coincided with the proposed action. For Constant-Same with the layer, 100 of 250 turns activated a rule, 43 were overrides and 10 of 25 sessions had at least one override.

### D. Where the policies diverge

Constant-Same with guardrails had a mean tracking error of 0.6728 in the five-persona replay, against 0.6772 for PPO with guardrails (pooled). Of the 125 PPO+guardrail sessions, the final-action sequence differed from that of Constant-Same+guardrails in 50, the executed difficulty path (after clipping) differed in 25, and the session tracking error differed in 5. The three counts follow different definitions and are not interchangeable: a proposed Easier at difficulty 1.0, for example, changes the action sequence without changing the executed path. Tracking error therefore cannot distinguish policies whose paths differ in shape without differing in mean distance to the target. Session-level divergence on the 40-persona grid is not stored in a summary and is not reported here.

### E. Volatility

On the 40-persona grid, PPO with guardrails was more volatile than Constant-Same with guardrails (difference +0.14877, 95% interval [0.0666, 0.25445]) and had a higher oscillation rate (+0.25061 [0.13027, 0.38584]). Guarded PPO was also more volatile than PPO without guardrails (mean volatility 0.2463 versus 0.0804; point values, no stored interval), and in the five-persona replay the pooled values were 0.1864 for guarded PPO and 0.0776 for raw PPO (oscillation 0.1603 and 0.0613); Constant-Same with guardrails had a volatility of 0.080 and an oscillation of 0.0. The guarded policy is therefore not smoother than the unguarded one in these data. Volatility is a secondary metric and was analysed descriptively.

### F. Secondary contrasts (descriptive)

**Table IV. Secondary contrasts on the 40-persona grid (difference in MAE unless stated; no multiplicity control).**

| Contrast | Difference | 95% interval |
|---|---|---|
| PPO+G, zeroed observation minus PPO+G | +0.36982 | [0.09077, 0.64148] |
| PPO+G, observation from another persona minus PPO+G | +0.25382 | [0.10948, 0.41417] |
| PPO+G minus heuristic+G | −0.46414 | [−0.7134, −0.22601] |
| PPO+G minus rolling-average controller+G | −0.30084 | [−0.51982, −0.09469] |
| PPO+G minus oracle-rule+G | −0.10698 | [−0.21823, 0.00841] |
| Constant-Same+G minus Constant-Same without guardrails | +0.10386 | [−0.18375, 0.38796] |
| PPO without guardrails minus Constant-Same without guardrails | −0.06166 | [−0.18481, 0.06173] |
| Removing rule G1: PPO+G / Constant-Same+G | −0.08725 / −0.14557 | [−0.23925, 0.03782] / [−0.34944, 0.03637] |

PPO reads its observation: replacing it with zeros or another persona's observation raised the tracking error. That shows the policy is state-dependent; it does not show that the state dependence improves tracking relative to Constant-Same (Table I). The comparators are authored controllers, and the oracle rule and the rolling-average controller share the persona-target structure. In the five-persona replay the heuristic had a lower tracking error (0.473) than PPO with guardrails (0.677); the two comparisons use different persona sets and are reported separately. On the grid the guardrail layer did not improve tracking for Constant-Same (1.104 with versus 1.000 without), and the five-persona improvement from 1.200 (Fixed at 3.0) to 0.673 did not generalise to the grid. Removing single rules other than G1 changed tracking error by less than 0.03.

### G. Action distribution

The training-time share of the Same action for the stochastic policy in the last logging window was 0.5069, 0.5130, 0.5345, 0.5168 and 0.5247 for seeds 42, 123, 456, 789 and 999 (24,576 timesteps each). In a stored probe sweep of the seed-123 checkpoint, 8 of 66 probes chose an action other than Same, at one neutral point of the other state coordinates. The evaluation-time Same share was not stored in the publication summary and is therefore not quantified here. A policy that often proposes Same is close to the state-blind comparator by construction, which is compatible with the equivalence result but is not tested as its explanation.

## VI. Discussion

**Equivalence.** *Shows:* under the registered simulator, shared guardrail layer and these five checkpoints, the mean tracking error of PPO and Constant-Same differed by −0.0350, and the interval lies inside ±0.12. *Does not show:* that the two policies are the same, that PPO has no effect (three sensitivity intervals exclude zero), or that a differently trained PPO would be equivalent. *Prior work:* learned policies matching simple or expert policies are reported in other settings [4]–[7]; the equivalence framing follows [12], [13], and here the registered rule requires the whole 95% interval inside the margin. *Why it matters:* the result constrains what can be attributed to the learned policy in this design: the tracking result does not identify a contribution of the learned component beyond the guardrails. *Practical implication:* none for learners; the study makes no claim about real interviews. *Limit:* the ±0.12 margin has no external justification; whether ±0.12 difficulty levels is practically small has not been evaluated.

**Why an equivalence result is informative.** The design isolates the learned component: the same constraint layer is applied to both policies, the null is a state-blind constant, the equivalence rule was registered before the run, sensitivity analyses were registered, and behaviour is accounted for separately. The result is informative because it shows that, in this simulator and for these checkpoints, adding a learned policy to a guardrail layer did not measurably change mean tracking error, while the divergence analysis shows where the policy does change behaviour (50 of 125 final-action sequences, 25 of 125 executed paths, higher volatility). It is not a product success result and does not indicate that PPO is unhelpful in general.

**Behaviour beyond the mean.** *Shows:* PPO reads the state (zeroing or shuffling raised tracking error), is more volatile, and is overridden by the layer on 7.9% of five-persona turns. *Does not show:* that state-dependence helps tracking, or that guardrail activation counts measure safety outcomes. *Limit:* the guardrail accounting comes from five authored personas.

**Anticipated objections.** *Is Constant-Same the right null?* It is state-blind and is a strong reference here because difficulty starts at the centre of the target range; other nulls (an Elo or item-response baseline) were not run. *Is the margin justified?* No external justification was found. *Is the reward aligned with the evaluation target?* The reward includes an oracle-alignment term and the target is an authored rule, and the coupling was not re-audited; PPO was not trained to minimise the tracking error. *Is PPO undertrained?* Each checkpoint was trained for 24,576 timesteps against one candidate; the effect of longer or broader training was not tested. *Does the simulator bias the result?* It may; it is authored and not calibrated. *Is training different from evaluation?* Yes (Section III). *Does PPO respond to the state?* Yes, in this simulator.

## VII. Threats to Validity and Limitations

**Scope.** Simulation only: no human learners, no real-candidate evidence, and no evidence of learning outcomes. The simulator, persona structure, target difficulty rule and comparator controllers are authored. The reward contains oracle-alignment terms and the coupling to the evaluation target was not re-audited.

**Training and evaluation.** Five checkpoints from one training seed set, a hypothetical population (df = 4 in the seed-level analysis); each trained against a single candidate, so 39 of the 40 grid personas were unseen; training used the guardrail layer inside the loop, 15-turn episodes and continuous steps, while evaluation uses 10-turn integer steps; the training candidate's noise was unseeded, so checkpoints cannot be regenerated. The demonstration policy deployed in the application differs from the training state definition, and no claim is made about the application.

**Design.** The ±0.12 margin is a design choice without literature justification; tracking error ignores path shape; no Elo, item-response or adaptive-testing baseline; the heuristic tracked better than PPO with guardrails in the five-persona replay and worse on the grid; the guardrail layer has no formal specification; evaluation-time action shares and grid-level session divergence are not stored; the five-persona accounting rests on five authored personas; the registration tags are local and unpushed. Secondary contrasts have no multiplicity control.

**Equivalence.** Equivalence is not "no effect", and it applies to these checkpoints in this simulator. A retraining experiment across a persona distribution was not run.

## VIII. Reproducibility and Artifact Availability

The registered analysis ran in a locked environment (Python 3.12.7, recorded lock file), with a harness gate that reproduced the frozen evaluation loop on the five-persona study exactly and required deliberately altered rule or heuristic variants to be detected before the run. Two dry runs of that gate failed its mutant-detection check before any confirmatory data existed and were resolved by replacing the mutant with one the fixture exercises, and a first primary-run attempt was aborted when its process was killed; the records of all three are retained. The primary analysis used bootstrap seed 42 with B = 10,000; the sensitivity analysis reproduced the primary estimate with zero difference. Checkpoints and the session-level results of the 40-persona study are hash-pinned in the project repository. Retraining the checkpoints from the recorded seeds is not reproducible because of unseeded candidate noise; the checkpoints are frozen artifacts and not regenerated. The repository is not publicly released in this draft. Artifact availability is not independent reproduction, which has not been performed.

## IX. Conclusion

In a controlled simulation in which a learned PPO difficulty controller and a state-blind Constant-Same policy ran under an identical rule-based guardrail layer, the registered persona-level tracking-error difference was −0.0350 (95% interval [−0.0818, +0.0021]), equivalent within ±0.12 and unchanged under three registered sensitivity analyses; superiority was not established. The two policies nonetheless differ in behaviour (final-action sequences in 50 of 125 five-persona sessions, and higher PPO volatility), and the guardrail layer acted on 45.0% of turns while changing the proposed action on 7.9%. The findings concern five checkpoints in an authored simulator with an authored margin, and they support no claim about real learners. Future work would train across a persona distribution, add rating-system baselines and, before any learner-facing claim, evaluate with real candidates.

## References

[1] S. Kadam, S. Banerjee, J. Christopher, P. T. V. Praveen Kumar, and D. K. Satpathi, "A simulation framework for benchmarking reinforcement learning policies in adaptive mock-interview tutoring," *Simul. Model. Pract. Theory*, vol. 151, Art. no. 103316, Sep. 2026, doi: 10.1016/j.simpat.2026.103316 (publisher landing page read: abstract, highlights and contribution statements; article body not read).
[2] A. Riedmann, P. Schaper, and B. Lugrin, "Reinforcement learning in education: A systematic literature review," *Int. J. Artif. Intell. Educ.*, vol. 35, pp. 2669–2723, 2025, doi: 10.1007/s40593-025-00494-6.
[3] S. Doroudi, V. Aleven, and E. Brunskill, "Where's the reward? A review of reinforcement learning for instructional sequencing," *Int. J. Artif. Intell. Educ.*, vol. 29, no. 4, pp. 568–620, 2019, doi: 10.1007/s40593-019-00187-x.
[4] M. Sanz Ausin, M. Maniktala, T. Barnes, and M. Chi, "Exploring the impact of simple explanations and agency on batch deep reinforcement learning induced pedagogical policies," in *Artificial Intelligence in Education (AIED 2020)*, 2020.
[5] R. Schmucker, N. Pachapurkar, S. Bala, M. Shah, and T. Mitchell, "Learning to optimize feedback for one million students: Insights from multi-armed and contextual bandits in large-scale online tutoring," arXiv:2508.00270, 2025 (preprint).
[6] J. Jiang, K. Hong, E. Kuczynski, and G. Pottie, "Simulated human learning in a dynamic, partially-observed, time-series environment," arXiv:2511.15032, 2025 (preprint).
[7] L. Che, P. Guo, H. F. Isleem, and Z. Wang, "The necessity of multimodal feedback for learning effective pedagogical policies with reinforcement learning," *Sci. Rep.*, 2025 (article ID s41598-025-29892-5; volume/article number not verified).
[8] O. Olukola and N. Rahimi, "MC-CPO: Mastery-conditioned constrained policy optimization for pedagogically safe intelligent tutoring systems," arXiv:2604.04251, 2026 (preprint).
[9] M. Alshiekh, R. Bloem, R. Ehlers, B. Könighofer, S. Niekum, and U. Topcu, "Safe reinforcement learning via shielding," in *Proc. AAAI Conf. Artif. Intell.*, 2018 (cited for terminology only; the definition was not reopened in this study).
[10] R. Agarwal, M. Schwarzer, P. S. Castro, A. C. Courville, and M. G. Bellemare, "Deep reinforcement learning at the edge of the statistical precipice," in *Advances in Neural Information Processing Systems*, vol. 34, 2021.
[11] P. Henderson, R. Islam, P. Bachman, J. Pineau, D. Precup, and D. Meger, "Deep reinforcement learning that matters," in *Proc. AAAI Conf. Artif. Intell.*, 2018.
[12] D. J. Schuirmann, "A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability," *J. Pharmacokinet. Biopharm.*, vol. 15, pp. 657–680, 1987, doi: 10.1007/BF01068419.
[13] D. Lakens, A. M. Scheel, and P. M. Isager, "Equivalence testing for psychological research: A tutorial," *Adv. Methods Pract. Psychol. Sci.*, vol. 1, no. 2, pp. 259–269, 2018, doi: 10.1177/2515245918770963.
[14] R. Pelánek, "Applications of the Elo rating system in adaptive educational systems," *Comput. Educ.*, vol. 98, pp. 169–179, 2016, doi: 10.1016/j.compedu.2016.03.017.
