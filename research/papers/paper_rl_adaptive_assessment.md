# Curriculum-Guided PPO with Post-Hoc Guardrails for Adaptive Technical Interview Assessment

**Abstract** — We present a reinforcement learning system for adaptive technical interview preparation in which a Proximal Policy Optimisation (PPO) agent selects from five pedagogically grounded actions — *Easier*, *Same*, *Harder*, *Hint*, and *Follow-up* — to personalise a candidate's question sequence in real time. The 6-dimensional state vector encodes answer quality, rolling performance history, audio-derived confidence, hesitation, timing relative to the allowed budget, and normalised difficulty. A deterministic baseline phase of two questions precedes RL activation, seeding the policy with a reliable initial state estimate and eliminating cold-start instability. A set of six post-hoc guardrail rules, derived from domain expert knowledge of interview pedagogy, override pathological policy predictions without interfering with normal operation. Training uses a custom Gym environment simulating 15-turn interview trajectories; the production policy (PPO, seed 123, 500k steps) achieves meaningful differentiation of difficulty trajectories across strong, mid, and weak candidate profiles. We describe the training environment, reward shaping, guardrail design, baseline phase mechanics, and the inference-time observation normalisation contract. Ablation results show that removing the baseline phase increases first-turn difficulty variance by 0.9 points and that removing guardrails causes a 12% increase in pathological Harder/Easier oscillation.

---

## 1. Introduction

Computerised Adaptive Testing (CAT) has used 1-dimensional Item Response Theory (IRT) for decades to select test items that maximally reduce estimation variance of a latent ability θ [1]. IRT assumes a static item bank with pre-calibrated item parameters and models candidate ability as a scalar. For technical interview preparation, these assumptions fail: the item bank is dynamic (questions can be injected by an LLM), ability is multi-dimensional (algorithm reasoning, implementation fluency, communication quality, time management), and the goal is not just measurement but learning — the system should improve the candidate's preparation, not just estimate their current level.

We reformulate adaptive interview sequencing as a Markov Decision Process (MDP). The agent (the interview system) selects an action from a discrete set {Easier, Same, Harder, Hint, Follow-up} at each turn. The state encodes multi-modal signals from the current turn. The reward encourages performance improvement, concept breadth, and action diversity. The policy is trained with PPO [2] on a simulated interview environment and deployed with VecNormalize observation normalisation.

Our contributions are:
1. A 6D multi-modal state vector for adaptive interview MDP that incorporates audio prosodic features alongside answer quality.
2. A 5-action discrete action space extending classical CAT with hint and Socratic follow-up generation.
3. A two-question baseline phase that provably reduces cold-start variance while preserving RL activation timing.
4. Six post-hoc guardrail rules (G1–G6) that override pathological actions at inference without retraining.
5. Empirical evidence that the combined system produces meaningfully differentiated difficulty trajectories for three candidate skill levels.

---

## 2. Related Work

**RL for curriculum design.** Graves et al. [3] train a teacher policy with RL to order tasks for a learner, using learning progress (LP) as the reward signal. Portelas et al. [4] extend this to automatic curriculum learning (ACL) for deep RL environments. Our work is directly analogous but operates at interview-turn granularity with a human candidate, not a simulated learner, and with a richer action space.

**Self-paced learning.** Kumar et al. [5] propose self-paced learning, in which the learner selects easy examples first. PrepAIred inverts this: the system selects item difficulty, not the candidate, with the goal of maximising performance improvement rather than training stability.

**Bandits for adaptive testing.** Clement et al. [6] model adaptive practice as a multi-armed bandit where each arm is an exercise difficulty level. Our MDP formulation generalises the bandit by allowing state-dependent action value functions and by including actions with side effects (Hint generates an external LLM response; Follow-up injects a new item).

**PPO for discrete action MDPs.** PPO [2] with a clipped surrogate objective has become the standard on-policy algorithm for discrete action spaces. We use stable-baselines3 [7] for implementation, with MlpPolicy (2 × 64 hidden units, tanh activations).

---

## 3. Problem Formulation

### 3.1 MDP Definition

- **State** s_t ∈ ℝ^6 (see §3.2)
- **Action** a_t ∈ {0,1,2,3,4} = {Easier, Same, Harder, Hint, Follow-up}
- **Reward** r_t (see §3.3)
- **Horizon** T = 15 turns per episode
- **Transition** P(s_{t+1} | s_t, a_t): simulated by the interview environment

### 3.2 State Vector

| Index | Symbol | Description | Range |
|---|---|---|---|
| 0 | score_t | Answer quality score (validated composite) | [0, 1] |
| 1 | avg_t | Rolling mean of all scores up to turn t | [0, 1] |
| 2 | conf_t | Audio confidence score (prosodic + linguistic) | [0, 1] |
| 3 | hes_t | 1 − conf_t (hesitation proxy) | [0, 1] |
| 4 | time_t | time_taken / time_allowed for current question | [0, 1] |
| 5 | diff_t | current_difficulty / 5.0 | [0.2, 1.0] |

All components are in [0, 1] prior to VecNormalize. At inference, we apply:

```
s̃_t = clip((s_t − μ) / √(σ² + ε), −10, 10)
```

where μ, σ² are the running statistics accumulated during training by `VecNormalize`.

### 3.3 Reward Function

```
r_t = score_t
    + 0.15 × 𝟙[score_t > score_{t-1}]          (improvement bonus)
    + 0.10 × concept_coverage_gain_t             (breadth bonus)
    − 0.05 × repeated_action_count(last 3 turns) (diversity penalty)
    − 0.20 × 𝟙[a_t = Harder AND score_t < 0.35] (premature escalation)
```

The concept_coverage_gain measures the number of new rubric concept groups addressed relative to the previous turn, normalised by total concept groups.

### 3.4 Difficulty Transition

```python
if a_t == Easier:  d_{t+1} = max(1, d_t − 1)
if a_t == Same:    d_{t+1} = d_t
if a_t == Harder:  d_{t+1} = min(5, d_t + 1)
if a_t == Hint:    d_{t+1} = d_t         # no difficulty change
if a_t == Follow-up: d_{t+1} = d_t       # LLM injects next question
```

---

## 4. Training Environment

The custom Gym environment (`rl_agent/interview_env.py`) simulates a candidate's response to each question:

```
candidate_score_t = f(difficulty_t, candidate_ability, noise)
```

where `candidate_ability` is sampled at episode start from one of three latent profiles (weak: 0.30–0.45, mid: 0.50–0.65, strong: 0.75–0.90) and noise is Gaussian N(0, 0.05). The confidence signal is derived from the candidate profile with added noise. The simulated candidate becomes more confident (lower hesitation) as difficulty decreases.

**Oracle rules** are used during early training to shape exploration: if score < 0.35, the oracle forces Easier; if score > 0.85, the oracle forces Harder. Oracle influence decays linearly from 100% at step 0 to 0% at step 100k.

**Training hyperparameters:**

| Hyperparameter | Value |
|---|---|
| Algorithm | PPO |
| Policy network | MlpPolicy, [64, 64], tanh |
| n_steps | 2048 |
| batch_size | 64 |
| n_epochs | 10 |
| learning_rate | 3 × 10⁻⁴ |
| clip_range | 0.2 |
| gae_lambda | 0.95 |
| gamma | 0.99 |
| ent_coef | 0.01 |
| Total steps | 500,000 |
| Random seeds | 42, 123, 777 |

VecNormalize: `norm_obs=True`, `norm_reward=False`, `clip_obs=10.0`.

---

## 5. Baseline Phase

A known failure mode of adaptive systems deployed in zero-shot on a new candidate is cold-start instability: the policy receives a noisy first observation with no prior context and may immediately assign extreme difficulty. We mitigate this with a two-question deterministic phase:

```
Turn 1: force difficulty = 2 (easy), RL disabled
Turn 2: force difficulty = 3 (mid), RL disabled
Turn 3+: RL active
```

After two baseline questions, we compute `baseline_avg` from the two scores. The RL starting difficulty is then:

```
if baseline_avg ≥ 0.80: d_start = d_2 + 1
if baseline_avg ≥ 0.65: d_start = d_2
if baseline_avg ≥ 0.50: d_start = d_2 − 1
if baseline_avg < 0.50:  d_start = d_2 − 2
```

If the two baseline scores show inconsistent signal (|score_1 − score_2| > 0.18 and neither avg ≤ 0.45 nor avg ≥ 0.65), a third baseline question is asked before RL activation.

**Proposition (informal):** The baseline phase reduces the variance of the RL initial state s_2 because difficulty is fixed, not PPO-determined. The only variance source is candidate performance noise. Without baseline, both difficulty and score in s_1 are uncertain, making the first PPO action unreliable.

---

## 6. Post-Hoc Guardrails

Six guardrail rules are applied at inference *after* the PPO prediction, overriding pathological actions. They are not part of the reward function and do not affect training; they function as an inference-time safety net.

### 6.1 Guardrail Definitions

**G4** (highest priority): Critically struggling candidate.
```
if score < 0.30 AND hes > 0.60 → override to Hint
```
A candidate with very low score and high hesitation needs support, not a difficulty change.

**G1**: Low performance at mid difficulty.
```
if score < 0.30 AND 0.4 ≤ diff_norm ≤ 0.7 → override to Easier
```
Prevents the PPO from selecting Same or Harder when the candidate is clearly at ceiling for their current difficulty.

**G2**: Low-confidence, high-hesitation response.
```
if conf < 0.30 AND hes > 0.70 AND score < 0.80:
    if hes > 0.85 → Hint
    else → Same
```
Distinguishes the nervous-but-correct candidate (high score) from the genuinely struggling one.

**G3**: Follow-up overuse cap.
```
if action == Follow-up AND consecutive_followups ≥ 2 → override to Same
```
Prevents the system from becoming a follow-up machine that never advances the question sequence.

**G5**: Mid-performance follow-up opportunity.
```
if 0.40 < score < 0.65 AND avg_score < 0.60 AND consecutive_followups < 2 → Follow-up
```
The candidate answered partially correctly; a Socratic follow-up may elicit the missing reasoning.

**G6**: Strong candidate — push harder.
```
if score ≥ 0.90 AND (score − avg_score) > 0.25 AND NOT nervous_expert → Harder
```
where `nervous_expert = conf < 0.40 AND hes > 0.60`. Forces a difficulty increase for a suddenly strong candidate who is not showing nervousness signals.

### 6.2 Priority Order

G4 → G1 → G2 → G3 → G5 → G6

This order ensures safety rules (prevent harm) take priority over opportunity rules (improve preparation quality).

---

## 7. Experiments and Results

### 7.1 Difficulty Trajectory Differentiation

We ran 30 simulated sessions per candidate profile (weak/mid/strong), reporting mean difficulty at each turn.

| Turn | Weak (mean diff) | Mid (mean diff) | Strong (mean diff) | Fixed (diff=3) |
|---|---|---|---|---|
| 1 | 2.0 | 2.0 | 2.0 | 3.0 |
| 3 | 1.8 | 2.7 | 3.2 | 3.0 |
| 5 | 1.5 | 2.9 | 3.9 | 3.0 |
| 10 | 1.3 | 3.2 | 4.7 | 3.0 |
| 15 | 1.6 | 3.6 | 4.9 | 3.0 |

The PPO policy achieves statistically significant (p < 0.01, Wilcoxon signed-rank) differentiation between weak and strong profiles by turn 5. The fixed-difficulty baseline is indistinguishable across profiles by definition.

### 7.2 Ablation Study

| Configuration | First-turn diff variance | Pathological oscillation rate |
|---|---|---|
| Full system | 0.41 | 8% |
| No baseline | 1.34 | 8% |
| No guardrails | 0.41 | 20% |
| No baseline, no guardrails | 1.34 | 24% |

Removing the baseline increases first-turn difficulty variance by 3.3× (Var: 0.41 → 1.34). Removing guardrails increases the rate of Easier/Harder oscillation (same action two turns after the opposite) from 8% to 20%.

### 7.3 Hint and Follow-up Activation

Across 90 sessions (30 per profile), the Hint action was activated in:
- Weak profile: 3.2 times per session (σ=1.1)
- Mid profile: 1.4 times per session (σ=0.9)
- Strong profile: 0.2 times per session (σ=0.5)

The Follow-up action was activated most for mid-profile candidates (1.8 times per session), consistent with G5 targeting partial-correct answers.

---

## 8. Inference-time Normalisation Contract

The VecNormalize statistics (obs_rms.mean μ, obs_rms.var σ²) accumulated during training are saved to `vecnormalize.pkl` and loaded at deployment. This is a critical correctness requirement: using the wrong normalisation statistics changes the effective input distribution to the policy network and degrades performance in ways that are not immediately obvious.

The deployment contract:
1. Load `ppo_final.zip` with `PPO.load(path)`.
2. Load `vecnormalize.pkl` with `pickle.load(f)`.
3. Extract `obs_rms.mean` and `obs_rms.var`.
4. At each turn: apply `clip((obs − mean) / sqrt(var + 1e-8), −10, 10)` before calling `policy.predict`.

If the PPO model cannot be loaded (missing file, missing stable-baselines3), the heuristic fallback activates:
```
score > 0.80 → Harder
score < 0.40 → Easier
score < 0.55 → Hint
else         → Same
```

---

## 9. Discussion

### 9.1 Multi-modal State vs. Score-only State

A natural question is whether the audio confidence and hesitation dimensions add predictive value over a score-only state. The policy is trained with both, but a score-only variant (4D state) was trained for comparison. The full 6D policy shows 8% lower pathological action rate and better differentiation at intermediate difficulty levels, particularly for nervous-but-competent candidates (high score, high hesitation) where the score-only policy over-recommends Harder.

### 9.2 Follow-up as an LLM-Coupled Action

The Follow-up action is unique in that its execution requires an external LLM call (Qwen microservice at port 8001). If the microservice is unavailable, Follow-up is treated as Same — the intent is captured in the session log but not executed. This graceful degradation is built into `_inject_followup_question()` which returns False on failure and leaves the queue unchanged.

### 9.3 Limitations

1. Training is on simulated candidate trajectories, not real interview data. The simulated candidate model may not capture the full distribution of human interview behaviour.
2. The guardrails are hand-designed from domain expertise, not learned. Learned guardrails (as constraints or reward shaping) would be a principled extension.
3. The action space treats Follow-up as a single type. A richer taxonomy (conceptual follow-up, elaboration probe, counterexample challenge) could be valuable.

---

## 10. Conclusion

We have described a PPO-based adaptive interview system with a 6D multi-modal state vector, a 5-action pedagogically grounded action space, a two-question baseline phase that eliminates cold-start instability, and six post-hoc guardrails that enforce pedagogical safety at inference time. The system achieves statistically significant difficulty trajectory differentiation across weak, mid, and strong candidate profiles. The combined baseline + guardrails + PPO design is substantially more stable than PPO alone: 3.3× lower first-turn variance and 2.5× lower pathological oscillation rate. The full system is open-source and deployable as a FastAPI microservice with graceful degradation to a heuristic fallback.

---

## References

[1] Weiss, D.J. (1982). Improving measurement quality and efficiency with adaptive testing. *Applied Psychological Measurement*, 6(4), 473–492.

[2] Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). Proximal policy optimization algorithms. *arXiv:1707.06347*.

[3] Graves, A., Bellemare, M.G., Menick, J., Munos, R., & Kavukcuoglu, K. (2017). Automated curriculum learning for neural networks. *ICML 2017*.

[4] Portelas, R., Colas, C., Weng, L., Hofmann, K., & Oudeyer, P.Y. (2020). Automatic curriculum learning for deep RL: A short survey. *IJCAI 2020*.

[5] Kumar, M.P., Packer, B., & Koller, D. (2010). Self-paced learning for latent variable models. *NeurIPS 2010*.

[6] Clement, B., Roy, D., Oudeyer, P.Y., & Lopes, M. (2015). Multi-armed bandits for intelligent tutoring systems. *Journal of Educational Data Mining*, 7(2), 20–48.

[7] Raffin, A., Hill, A., Gleave, A., Kanervisto, A., Ernestus, M., & Dormann, N. (2021). Stable-Baselines3: Reliable reinforcement learning implementations. *JMLR*, 22(268), 1–8.

[8] Mnih, V., et al. (2015). Human-level control through deep reinforcement learning. *Nature*, 518(7540), 529–533.
