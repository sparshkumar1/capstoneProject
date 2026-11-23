# RL Evaluation Results — Final Evaluation Phase

No RL implementation, reward function, environment definition, policy checkpoint, or training script was modified in this phase, **except** the single, narrowly-scoped guardrail-fallback consistency fix documented in `Application_Code_Changes.md` (Change 3), which does not touch the environment's observation/action/reward machinery.

## 1. Environment Validation

### 1.1 Observation/action space
Re-confirmed directly from `rl/env/interview_env.py`: `Box(low=0, high=1, shape=(6,), dtype=float32)`; `Discrete(3)` with `{0: Easier, 1: Same, 2: Harder}`. Unchanged from the prior audit.

### 1.2 Official Gymnasium environment checker — new this phase
Run for the first time against this environment in this engagement:
```
from gymnasium.utils.env_checker import check_env
check_env(InterviewEnv(), skip_render_check=True)
```
**Result: PASSED, no warnings or errors raised** — both before and after the guardrail-fallback fix (rerun for regression). This is genuine, new, positive evidence: the environment is spec-compliant with Gymnasium's own API contract (correct `reset()`/`step()` signatures, correct space types, correct return tuple shapes), independently confirmed by the standard tool for this purpose rather than only by this project's own ad hoc scripts.

### 1.3 Reset/step/termination/seeding
Re-confirmed unchanged from the prior audit: `reset()` draws `difficulty ~ Uniform(0.3, 0.7)` unless fixed at construction; every episode terminates at exactly `max_steps` (default 15), `truncated` is always `False`; the environment's own `np_random` is correctly seeded via `super().reset(seed=seed)`, but the separately-constructed `SimulatedCandidate`'s RNG stream is independent and not auto-reseeded by the environment's `reset(seed=...)` — a reproducibility detail that requires both seeds to be set together by the caller, unchanged and not a new finding.

## 2. PPO Checkpoint Identity — Resolved This Phase

Per instructions, this is a **provenance resolution, not a file replacement** — no checkpoint was swapped, retrained, or deleted.

| | Deployed (`rl/checkpoints/seed_123/ppo_final.zip`) | Evaluated (`research/experiments/paper3/checkpoints/seed_123/ppo_final.zip`) |
|---|---|---|
| SHA-256 (recomputed fresh this phase) | `2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575` | `299437ea0dcdd7a5eed51326e80854bd3bb55341194420b619c5da3d675e24e0` |
| Used by | `agents/strategy/hybrid_orchestrator.py` at runtime (live system, confirmed via `T-N02`, this phase and prior) | The frozen Paper-3 result tables (`paper3_seed_results.csv`, `paper3_baseline_results.csv`) |
| Seed label | `seed_123` | `seed_123` |
| **Are they the same file?** | **No.** Different hash, confirmed independently twice (prior audit and this phase, identical result both times) | |

**Resolution:** these are **two different checkpoint files that share only a seed *label*, not file identity** — the hashes prove this conclusively; a shared seed number is not evidence of an identical trained artifact (they could differ due to a re-save, a different training run promoted later under the same label, or a checkpointing/serialization difference). **No claim in this project's evidence record should assert that the live, deployed policy is the exact same artifact the frozen Paper-3 numbers describe, unless that claim is re-derived specifically against the deployed file's hash.** This phase's own `T-N02`/`T-N03` re-confirmations (§3 below) are explicitly scoped to the **deployed** checkpoint only — they validate that the live system's policy loads and behaves validly; they are not a re-validation of the frozen Paper-3 result tables, which rest on the other file.

**Not done, and why:** replacing the deployed checkpoint with the evaluated one (or vice versa) was considered and explicitly rejected — doing so would itself be an undocumented, untested change to live system behavior, contrary to "resolve the provenance without replacing or retraining the policy." If the two files should in fact be made identical, that is a deliberate decision for the project owner to make and verify end-to-end (re-running `T-N02`/`T-N03` against the replacement before deployment), not something to do silently as a side effect of a provenance audit.

## 3. Policy Behaviour Evaluation — Re-Confirmed, Deployed Checkpoint Only

`T-N02` (10 constructed profiles: strong/weak/boundary/nervous-expert/floor/ceiling/declining/improving) re-run fresh this phase, before and after the guardrail-fallback fix: **10/10 valid, all `source=ppo`**, identical results both times. Every result records the raw action, whether a guardrail overrode it, which rule fired (if any), and the resulting difficulty — raw-policy and shielded-application behaviour are never merged into one undifferentiated "the system adapted correctly" statement, consistent with this phase's instruction.

## 4. PPO vs. Baseline — Re-Verified, Terminology Corrected

Source: `research/results/paper3/paper3_baseline_results.csv` (hash re-verified unchanged this phase: `50a184d3508d9879a579c7d7f01b98652dc8a96e7c2d0ff86f544d8fbce9fff9`), 5 personas × 5 evaluation seeds, matched across all conditions.

| Condition | Tracking MAE |
|---|---|
| Fixed | 1.200 |
| Heuristic (rule-based) | 0.473 |
| PPO (raw) | 0.804 |
| PPO + Guardrails | 0.673–0.687 |

**Confirmatory test** (`X3A-C001`, a pre-registered, held-out 40-persona grid, protocol `prereg/X3-A/v1`): the 95% CI for (PPO+Guardrails MAE − Constant-"Same"+Guardrails MAE) is **[−0.0818, 0.0021]**.

### Terminology correction, applied in this phase's own documents going forward

A confidence interval containing zero supports the conclusion: **"no statistically detectable difference between PPO+Guardrails and a constant-action-plus-guardrails baseline, under the tested conditions."** This phase does **not** use the word "equivalence" for this result unless a pre-specified equivalence margin and a formal equivalence test (e.g. TOST) were used to produce it. Checking `research/audit/PHASE0_DECISION_LOCK.md` (frozen, read-only this phase): an equivalence margin (δ=0.12 MAE) **was** pre-specified for Paper 3 before this result was produced, and `X3A-C001`'s own registry entry classifies the result as "EQUIVALENT" under that pre-specified margin — meaning the stronger "equivalence" terminology **is** actually justified here, by the project's own pre-registration record, not merely asserted after the fact. This phase verified that the margin was pre-specified (not chosen after seeing the result) by confirming its presence in the frozen decision-lock document, which predates the confirmatory run. **Both framings are therefore defensible**: "no statistically detectable difference" is the conservative, always-safe description; "equivalence (under the pre-specified δ=0.12 MAE margin)" is also justified here specifically because the margin was genuinely pre-registered — this phase's documents use the latter, fuller phrasing when citing `X3A-C001` specifically, and the former, more conservative phrasing for any other CI-crosses-zero result that was not run under a pre-specified margin.

**The rule-based Heuristic still beats every PPO variant** on the primary tracking-MAE metric — this remains the single most load-bearing, unfavorable-to-PPO finding in the project's evidence record, and this phase did not find any methodological flaw that would weaken it (the comparison uses identical personas, identical seeds, identical metric, across all four conditions — verified again this phase by re-reading the CSV's own column structure, not just trusting a prior summary).

## 5. Univariate vs. Multivariate Policy Sensitivity

Re-read `research/results/paper3/paper3_sensitivity_results.csv` this phase (unchanged, hash not independently re-verified this specific file — lower priority given time budget, flagged as deferred). Confirmed: the stored sweep is **univariate only** — each of the 6 state dimensions is varied individually while the other 5 are held at a fixed neutral point (`s0 = [0.5,0.5,0.5,0.5,0.5,0.6]`). The policy outputs "Same" across the full range for `perf`, `conf`, `hes`, and `progress` individually in this sweep; only `difficulty` (and the low extreme of `avg_perf`) moves the action.

**Explicitly stated distinction, per this phase's instruction:** this univariate result does **not** establish that the policy is insensitive to joint/interaction effects among these variables — the `T-N02` scenario tests (which vary multiple fields together, e.g. a declining-trend profile combining performance, average, and hesitation) **do** show directionally sensible behavior that a purely-univariate reading would not predict. No multivariate interaction sweep was run this phase (would require a new, non-trivial grid-search script over the 6-D space) — recorded as a concrete, specific recommendation in `14_Executive_Summary.md`, not attempted superficially.

**No new PPO training was undertaken this phase.** Investigation into *why* the reward structure produces this behavior (the reward is ~60-90% weighted toward imitating a hand-coded oracle rather than the tracking metric itself) was already completed in the prior `Independent_Project_Audit` and is not repeated here; a concrete, ready-to-execute experimental redesign protocol (not executed) is provided in `11_Experiment_Provenance_Register.md`.

## 6. Guardrail Rules — Full Re-Verification Including the Previously-Dormant Fallback

See `Application_Code_Changes.md`, Change 3, for the complete before/after evidence. Summary: all 6 guardrail rules (`G1` stuck/overload, `G2` anxiety, `G4` stuck-highest-priority, `G5` partial-understanding, `G6` strong-performer, plus the infra-failure override) re-verified at their exact boundaries in **both** the primary `rl/guardrails.py` path (13/13, unchanged) **and**, for the first time, the dormant inline fallback in `rl/env/interview_env.py` (5/5 targeted boundary cases, now fixed and consistent with the primary path).
