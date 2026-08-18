# PrepAIred — Reinforcement Learning & Adaptive Difficulty Design

**Document Version:** 2.0.0 (Authoritative Stage 13 Consolidation)
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform

---

## 1. Problem Formulation as a Finite-Horizon MDP

Difficulty adaptation in PrepAIred is formulated as a discrete-action, finite-horizon Markov Decision Process (MDP):

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma, T \rangle$$

- **Episode Horizon ($T$):** $T = 15$ questions per interview session.
- **Discount Factor ($\gamma$):** $\gamma = 0.99$.

---

## 2. Exact 6-Dimensional State Space ($\mathcal{S} \subset \mathbb{R}^6$)

The observation vector $\mathbf{s} \in [0.0, 1.0]^6$ is constructed strictly from authoritative runtime measurements without synthetic dimension expansion:

$$\mathbf{s} = \begin{bmatrix}
s_0: \text{performance} \\
s_1: \text{average\_performance} \\
s_2: \text{confidence} \\
s_3: \text{hesitation} \\
s_4: \text{time\_norm} \\
s_5: \text{difficulty\_norm}
\end{bmatrix}$$

### Dimension Definitions & Sources

| Index | Name | Range | Source | Runtime Semantic |
|---|---|---|---|---|
| $s_0$ | `performance` | $[0.0, 1.0]$ | Neural Evaluator / Sandbox | Latest evaluated question score (verbal $S_{\text{tech}}$ or coding pass rate). |
| $s_1$ | `average_performance` | $[0.0, 1.0]$ | Candidate State History | Rolling mean of the last 5 answer scores ($\frac{1}{K}\sum_{i=N-K+1}^N S_i$). |
| $s_2$ | `confidence` | $[0.0, 1.0]$ | Speech Prosody / Prior State | Acoustic confidence derived from speech pipeline (falls back to prior verbal turn or $s_0$ if no prior speech exists). |
| $s_3$ | `hesitation` | $[0.0, 1.0]$ | Speech Prosody / Prior State | Acoustic pause & filler rate ($1.0 - \text{confidence}$). |
| $s_4$ | `time_norm` | $[0.0, 1.0]$ | `QuestionTimer` | Normalized question duration: $\text{clip}\left(\frac{t_{\text{elapsed}}}{t_{\text{allowed}}}, 0.0, 1.0\right)$. |
| $s_5$ | `difficulty_norm` | $[0.0, 1.0]$ | Candidate State | Normalized current difficulty level: $\frac{\text{current\_difficulty}}{5.0}$. |

> [!IMPORTANT]
> **Coding Latency Separation Invariant:** Docker C sandbox compilation and execution time (`execution_time_ms`) is strictly tracked in `coding_history` and is **never** injected into $s_4$ (`time_norm`) or any other RL observation dimension.

---

## 3. Exact Discrete Action Space ($\mathcal{A}$)

The RL policy controls difficulty adjustments through a discrete 3-action space:

$$\mathcal{A} = \text{Discrete}(3) = \{0, 1, 2\}$$

| Action Index | Action Name | Difficulty Transition $\Delta d$ | Semantic Meaning |
|---|---|---|---|
| `0` | **Easier** | $d_{t+1} = \max(1, d_t - 1)$ | Decrease difficulty by 1 level (minimum level 1) |
| `1` | **Same** | $d_{t+1} = d_t$ | Maintain current difficulty level |
| `2` | **Harder** | $d_{t+1} = \min(5, d_t + 1)$ | Increase difficulty by 1 level (maximum level 5) |

---

## 4. Reward Function Formulation

The training reward function $r(s, a, s')$ balances performance optimization, steady learning trajectory, and avoidance of erratic difficulty swings:

$$r(s, a, s') = r_{\text{score}} + r_{\text{progress}} + r_{\text{penalty}}$$

Where:
1. **Score Component:** $r_{\text{score}} = s_0$ (evaluator score in $[0, 1]$).
2. **Improvement Progress Bonus:** $r_{\text{progress}} = +0.10$ if candidate score improves by $\ge 0.15$ following a difficulty transition.
3. **Premature Escalation Penalty:** $r_{\text{penalty}} = -0.20$ if action `Harder` is selected when candidate score $s_0 < 0.50$.
4. **Repetitive Oscillation Penalty:** $r_{\text{oscillation}} = -0.05$ if action alternates rapidly between `Easier` and `Harder` on consecutive turns.

---

## 5. PPO Architecture & Training Hyperparameters

- **Algorithm:** Proximal Policy Optimization (PPO) via Stable-Baselines3.
- **Policy Network:** Multi-Layer Perceptron (Actor-Critic architecture with 2 shared hidden layers of 64 units, tanh activations).
- **Observation Normalization:** `VecNormalize` running mean and variance filter ($\text{clip}=10.0$).
- **Total Timesteps:** 300,000 steps in `InterviewEnv`.

| Hyperparameter | Value | Description |
|---|---|---|
| Learning Rate ($\alpha$) | $3 \times 10^{-4}$ | Constant Adam learning rate |
| Horizon Steps ($n_{\text{steps}}$) | $2048$ | Steps collected per rollout per worker |
| Batch Size | $64$ | Minibatch optimization size |
| Epochs ($n_{\text{epochs}}$) | $10$ | PPO optimization epochs per update |
| GAE Lambda ($\lambda$) | $0.95$ | Generalized Advantage Estimation factor |
| Discount Factor ($\gamma$) | $0.99$ | Horizon discount factor |
| PPO Clip Range ($\epsilon$) | $0.20$ | Surrogate objective clipping threshold |
| Random Seed | $123$ | Fixed deterministic seed |

---

## 6. Safety Guardrails (G1–G6)

To protect candidates from sub-optimal policy outputs in edge cases, the system applies six deterministic post-hoc guardrails in priority order:

| Guardrail ID | Condition | Override Action | Rationale / Target |
|---|---|---|---|
| **G4** | $\text{perf} < 0.30 \land \text{hes} > 0.60$ | `Easier` | Critical struggling candidate under severe cognitive load |
| **G1** | $\text{perf} < 0.30 \land \text{diff} \in [2, 4]$ | `Easier` | Low performance at moderate difficulty |
| **G2** | $\text{conf} < 0.30 \land \text{hes} > 0.70 \land \text{perf} < 0.80$ | `Same` | Low confidence + high hesitation (avoid premature escalation) |
| **G3** | $\text{consecutive\_followups} \ge 2$ | Proceed to Main | Hard cap to prevent infinite probing rabbit-holes |
| **G5** | $0.40 < \text{perf} < 0.65 \land \text{avg\_perf} < 0.60$ | `Same` | Stabilize candidate in moderate performance range |
| **G6** | $\text{perf} \ge 0.90 \land \text{diff} < 5$ | `Harder` | Accelerate advanced candidate progression |

---

## 7. Baseline Warmup Phase

For sessions configured with $\ge 15$ questions (or mode `demo_rl`):
- **Questions 1–3:** RL is initially inactive (`decision_source = "baseline_warmup"`, `rl_status = "baseline_warmup"`).
- **Difficulty:** Fixed progression: Question 1 = Level 2 (Easy), Question 2 = Level 2 or 3.
- **Activation Criterion:** RL activates after 2–3 questions when score consistency is established (score spread $\le 0.18$ or clear separation $\le 0.45$ / $\ge 0.65$).

---

## 8. Empirical Claims Status

| RL Claim | Empirical Classification | Repository Evidence |
|---|---|---|
| 6D Observation vector & 3-Action space | **`TESTED`** | Implemented in `agents/strategy/hybrid_orchestrator.py`; verified via `test_rl_env.py`, `test_coding_executor.py` |
| PPO inference with VecNormalize running | **`TESTED`** | Implemented in `agents/strategy/`; verified with `rl/checkpoints/seed_123/ppo_final.zip` |
| Guardrail overrides G1–G6 | **`TESTED`** | `test_orchestrator.py`, `test_rl_env.py` |
| PPO superiority over human heuristics | **`NOT YET VALIDATED`** | Comparative longitudinal human study required |
