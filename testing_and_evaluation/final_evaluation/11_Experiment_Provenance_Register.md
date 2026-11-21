# Experiment Provenance Register — Final Evaluation Phase

## 1. PPO Checkpoint Identity — Register Entry

See `06_RL_Evaluation_Results.md` §2 for full detail. Register summary:

| Field | Deployed | Evaluated |
|---|---|---|
| Path | `rl/checkpoints/seed_123/ppo_final.zip` | `research/experiments/paper3/checkpoints/seed_123/ppo_final.zip` |
| SHA-256 | `2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575` | `299437ea0dcdd7a5eed51326e80854bd3bb55341194420b619c5da3d675e24e0` |
| Resolution | **Confirmed distinct files**, not swapped or merged this phase. Every future claim about "the live PPO policy" must cite the deployed hash; every claim about "the frozen Paper-3 results" must cite the evaluated hash. No single sentence should describe both without this distinction. |

## 2. Why the Constant-"Same" Policy Dominates — Investigation Summary (no retraining performed)

Already established, and not re-derived from scratch this phase (the underlying code was re-read and the conclusion re-confirmed, not newly discovered):

1. The reward function (`rl/env/interview_env.py`) is ~60% weighted toward `decision_component = ±1` for agreeing/disagreeing with a **hand-coded rule oracle**, plus a critical-state bonus/penalty layer that is itself oracle-derived — not toward the persona-target tracking MAE the policy is actually evaluated on.
2. The `stability_penalty` term (repeat-Easier and oscillation penalties) creates a direct, structural incentive to output "Same" repeatedly, independent of whether "Same" is the pedagogically correct action in a given state.
3. `paper3_training_curves.csv` (re-read this phase, unchanged) shows the action distribution shifting from near-uniform at the start of training to "Same"-dominant (~50%) by the end, consistently across all 5 seeds — a real, reproducible training dynamic, not noise.
4. The guardrail layer sits **between** the policy's proposal and the environment's actual transition (confirmed again this phase via the guardrail-fallback work in `Application_Code_Changes.md`), meaning the policy's training reward is computed on the *post-guardrail* action — the policy is structurally rewarded for agreeing with whatever the guardrail ultimately selects, which further suppresses any incentive to propose a different, potentially-more-informative action.

**Conclusion:** the constant-"Same" tendency is not a training-stability failure or a bug — it is the reward function's own structure working as designed, optimizing for oracle agreement and stability rather than for tracking accuracy. This is a genuine **reward-objective misalignment**, not an implementation defect, and is therefore explicitly outside the scope of this phase's "bug fix" category — correcting it requires a new, separately-governed experiment (below), not a patch.

## 3. Candidate Experimental Protocol — Reward Redesign (NOT EXECUTED this phase)

Per instructions, a real, focused improvement effort for PPO's incremental value was seriously considered. It was **not executed** in this phase, for a specific, disclosed reason: actually training a new PPO candidate requires (a) a new, hashed, git-tagged pre-registration per this project's own existing experiment-governance rules (`research/audit/PREREGISTRATION_SPEC.md`, `PHASE0_DECISION_LOCK.md`), (b) a non-trivial training wall-clock budget per seed × 5 seeds for a comparable multi-seed design, and (c) a held-out confirmatory evaluation matching `X3A-C001`'s own rigor to be comparably trustworthy — none of which can be responsibly compressed into this phase's remaining time without producing exactly the kind of rushed, under-verified result this project's own evidence culture explicitly warns against. Delivering a precise, ready-to-execute protocol is judged the more honest and more valuable output than a half-executed training run.

### Protocol: `prereg/X4-A/v1` (draft, not registered — registration is the project owner's decision)

**Research question:** does a reward function weighted primarily toward the persona-target tracking metric (rather than oracle-agreement) produce a policy whose contribution over a constant-action-plus-guardrail baseline is detectably different from zero, under the same confirmatory-grid protocol `X3A-C001` already uses?

**What is preserved, unchanged:**
- The existing Gym environment's observation space (6-D), action space (`Discrete(3)`), and guardrail layer (`rl/guardrails.py`) — **not modified**.
- The existing PPO algorithm, network architecture (`[64,64]` MLP), and hyperparameters (`lr=3e-4, gamma=0.99, gae_lambda=0.95, clip_range=0.20, n_steps=2048, batch_size=64, n_epochs=10`) — **not modified**, to isolate the reward-function variable specifically.
- The existing 5 training seeds (`42, 123, 456, 789, 999`) and 5 evaluation seeds — **reused**, for direct comparability.
- The original checkpoints, `paper3_seed_results.csv`, `paper3_baseline_results.csv`, and every other frozen Paper-3 artifact — **untouched, never overwritten**.

**What changes, as a new, separately-versioned environment subclass (not an edit to the frozen `InterviewEnv`):**
```
reward_X4A = w1 * (-abs(difficulty_after - persona_target))   # direct tracking-error signal, new
           + w2 * outcome_component                            # unchanged from the original (perf delta)
           + w3 * stability_penalty                             # retained, reduced weight (candidate: w3 -> half of original)
           # decision_component (oracle-agreement) REMOVED or reduced to a small w4 term, documented either way
```
Exact weights `w1..w4` to be fixed **before** training (pre-registered), not tuned after seeing results.

**New checkpoint identifiers:** `rl/checkpoints_x4a/seed_{42,123,456,789,999}/ppo_final.zip` (a new directory, never overwriting `rl/checkpoints/` or `research/experiments/paper3/checkpoints/`).

**Evaluation:** identical matched-baseline design to `paper3_baseline_results.csv` (Fixed / Heuristic / X4A-raw / X4A+Guardrails) **plus** a confirmatory held-out-grid test against Constant-"Same"+Guardrails, run under the same equivalence-margin convention `X3A-C001` used (δ=0.12 MAE, pre-specified).

**Decision rule, pre-specified:** if the new confirmatory CI excludes zero in the favorable direction (X4A+Guardrails measurably better than constant-action+guardrails), report it as a genuine, new, positive finding, clearly labeled as a different experiment from the original frozen Paper-3 result, not a replacement of it. If the CI still contains zero (or excludes zero unfavorably), report that too, with equal rigor — this protocol's own existence is not a promise of a favorable outcome.

**This document is the deliverable for this investigation track.** No training was run; no new checkpoint exists; the original Paper-3 evidence is completely unchanged and unreplaced.

## 4. EVALUATOR_MOCK_MODE — Investigation Outcome

Re-confirmed this phase (grep re-run, unchanged): set in `.github/workflows/ci.yml`, `docker-compose.yml`, and two test-file docstrings, but read by **zero** application or test code anywhere in the repository. **Decision, per this phase's instruction to investigate rather than mandate a fix:** recorded as a documentation-accuracy item, not implemented either way (wiring it would be a new, untested behavioral change to the test harness; removing every reference touches CI/CD configuration, judged out of scope for this phase's narrow code-change budget). Recommendation for the project owner: either wire it into `services/evaluator/app.py`'s asset-loading guard, or strike the references from `CLAUDE.md`/CI/docker-compose/test docstrings so the documented test command matches actual behavior — either is a legitimate, low-risk choice; this phase takes no position on which.

## 5. Flask Evaluator Necessity — Investigation Outcome

Re-confirmed this phase: `grep -rn "localhost:5000"` across the repository (excluding `.venv`) finds no caller outside `launch.py` (which starts the process) and this phase's/the prior phase's own test scripts. `apps/backend/main.py` imports `evaluate()`/`get_rubric()` directly, never over HTTP. **No change made** — removing the Flask server is a product-surface decision (it may be intended as a standalone integration point for future use, e.g. direct curl-based debugging or a future non-Python caller) that was judged outside this phase's narrow, bug-fix-only code-change scope. Recorded as confirmed-investigated, not acted on.
