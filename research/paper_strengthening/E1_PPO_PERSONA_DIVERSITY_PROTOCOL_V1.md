# E1 — PPO Persona-Diversity Development Experiment: Protocol V1

**Status: design only. Not registered, not executed, not tagged, not committed, not pushed. No code has been changed. No training has been run.** This tests a hypothesis (train/evaluation persona-distribution shift, `PPO_TRAINING_EXPERIENCE_AUDIT.md`) — it is not presented as an established causal conclusion, and the design below is built to be able to falsify it, not just confirm it.

## 0. What was inspected to build this design

- `rl/training/simulated_candidate.py` (`SimulatedCandidate`): the sole candidate-behavior model. `skill` is a **free, continuous float in [0,1]**, the only unconstrained diversity axis it exposes. `persona` is a **fixed categorical set of 5 names**, each with hand-written, hard-clamped behavior overrides (e.g. `nervous_expert` is clamped to `perf ∈ [0.82, 0.94]` with an explicit code comment: *"Without the upper cap, perf can exceed 0.95 → oracle picks Harder → agent over-learns Harder for this persona"* — the existing personas were deliberately shaped, at least in this instance, to keep the oracle's Harder rule from firing, not to represent a naturalistic population).
- `research/scripts/execute_paper3_study.py`: `PERSONA_TARGETS` gives the exact (skill, target_difficulty) pairs used for the 5 **confirmatory evaluation** personas (`struggling_junior` 0.20→1.0, `overconfident_fail` 0.30→1.5, `normal` 0.60→3.0, `lucky_guesser` 0.80→4.0, `nervous_expert` 0.88→4.5); `train_ppo_seed()` (hyperparameters: `learning_rate=3e-4, n_steps=2048, batch_size=64, n_epochs=10, gamma=0.99, gae_lambda=0.95, clip_range=0.2`, policy `MlpPolicy [64,64]`, `TIMESTEPS_PER_SEED=24576`, training seeds `[42,123,456,789,999]`) builds `AlignedInterviewEnv(dim4_mode="aligned_progress")`, a subclass of `rl/env/interview_env.py::InterviewEnv` that changes only the progress dimension, nothing else.
- `rl/env/interview_env.py::InterviewEnv.__init__` takes an optional `simulated_candidate` argument, defaulting to `SimulatedCandidate()` (skill 0.6, persona "normal") when none is given; **`reset()` never resamples or replaces `self.sim_candidate`** (confirmed directly, and independently already established by `X3_0B_STATIC_CODE_NOTE.md` finding N1). This is the exact, single point in the code where persona/skill diversity would need to be introduced.
- No hyperparameter, reward term, state dimension, or action is touched anywhere in this design.

## 1. Controlled intervention

| Condition | Training candidate | Reward | State | Action space | Hyperparameters | Guardrails |
|---|---|---|---|---|---|---|
| **A (existing, unchanged)** | Single fixed candidate: `skill=0.6, persona="normal"` | Unchanged (`hybrid`, weights 0.60/0.30/0.10, unchanged) | Unchanged (6-D) | Unchanged (3 discrete) | Unchanged | Unchanged (enabled in training, per N9) |
| **B (new, development-only)** | **Broadened synthetic skill distribution** (§2), persona field fixed to `"normal"` for every draw | **Identical to A** | **Identical to A** | **Identical to A** | **Identical to A** | **Identical to A** |

**Isolation guarantee:** Condition B changes exactly one thing relative to A — which candidate `InterviewEnv` is constructed with at each training episode. It does not add a new reward term, does not change any state dimension's definition, does not add or remove actions, and does not change any SB3 hyperparameter. This is enforced structurally (§7's precise change plan touches only episode-start candidate construction, nothing else in the file), not just declared.

**Baselines, unchanged, evaluated under identical guardrails as both PPO conditions:** Constant-Same+G (existing frozen); the existing threshold heuristic+G (existing frozen). Neither is retrained or modified.

## 2. Training design — the synthetic population, explicitly described

**What Condition B trains on:** at the start of every training episode, `self.sim_candidate` is replaced with a fresh `SimulatedCandidate(skill=s, seed=<derived>, persona="normal")`, where `s` is drawn from a **fixed, disclosed, purely synthetic grid**:

```
SKILL_GRID = [0.15, 0.1969, 0.2438, 0.2906, 0.3375, 0.3844, 0.4313, 0.4781,
              0.525, 0.5719, 0.6188, 0.6656, 0.7125, 0.7594, 0.8063, 0.8531, 0.9]
# 17 evenly spaced points from 0.15 to 0.90 (step ≈ 0.047)
```

drawn **cyclically** (episode `i` uses `SKILL_GRID[i % 17]`), not by random sampling — this guarantees exactly even coverage across the whole grid regardless of how many episodes a given training run completes (at ~1,638 episodes per 24,576-timestep run, each grid point is visited ~96 times per seed), and removes sampling-luck as a confound between Condition B's training seeds.

**What this population explicitly is, and is not:**
- It is **a purely synthetic sweep of the simulator's one native continuous parameter**, chosen because it is the only axis `SimulatedCandidate` exposes without hand-written behavioral overrides. It is disclosed as such, with no claim of representing any real candidate population.
- It **only ever uses `persona="normal"`** — the one persona branch in `simulated_candidate.py` with no hand-tuned clamps — so Condition B is never trained on the four named archetypes (`struggling_junior`, `overconfident_fail`, `lucky_guesser`, `nervous_expert`) that constitute the confirmatory evaluation set. **This is deliberate, not an oversight**: training on the literal evaluation personas would make any subsequent evaluation on those same personas circular (train-on-the-test-set), exactly the class of leakage this project's D1 audits have repeatedly had to guard against. Condition B's training population and the confirmatory evaluation population are **disjoint by construction** — they share no persona identity and, because the four named archetypes' behavior comes from hard clamps rather than skill alone (e.g. `lucky_guesser`'s `skill=0.80` alone would not naturally clamp `perf ≥ 0.95` without its persona-specific override), sweeping skill under `persona="normal"` does not implicitly reconstruct their behavior either.
- The range `[0.15, 0.90]` is chosen to bracket the evaluation personas' skill values (0.20–0.88) without exactly touching either boundary, so training sees a broad, continuous span of natural-sigmoid behavior around and beyond the confirmatory personas' operating points, without literally sampling their exact skill values.
- **What is deliberately left out of Condition B, and why:** any conf/hesitation *decoupling* from the natural sigmoid-driven correlation (the mechanism that makes `nervous_expert`/`overconfident_fail` distinctive). This keeps the intervention to a single, clean axis (skill diversity only), consistent with the instruction not to change multiple things at once. If Condition B is only partially successful, a decoupling axis is named in §5 as a candidate *next* development-only extension, not built now.

**Training seeds:** the same 5 values as Condition A (`42, 123, 456, 789, 999`), so SB3/PPO's own optimization randomness is directly comparable seed-for-seed. The skill-grid cycling uses a **separate, explicitly seeded** stream (`np.random.RandomState(seed + 10_000)` for the episode-seed offsets used to construct each episode's `SimulatedCandidate`), so policy-optimization randomness and persona-sampling randomness are never conflated.

**Training budget:** **primary arm uses the identical budget as Condition A** (`TIMESTEPS_PER_SEED = 24576`), to isolate the effect of persona diversity alone without also changing how much the policy trains. A **secondary, explicitly-labeled extended-budget arm** (4×, `98304` timesteps) is included as a diagnostic only — to check whether a null primary result is budget-limited rather than distribution-limited — and is never used to decide retain/abandon on its own (§5).

## 3. Development evaluation

All four policies (Condition A's existing frozen checkpoints; Condition B's new checkpoints; Constant-Same+G; Heuristic+G) are evaluated **identically**: same `run_session_trajectory`-style replay, same 5 confirmatory personas (`PERSONA_TARGETS`, unchanged), same 5 confirmatory eval seeds (`1001,2002,3003,4004,5005`), same guardrails, same 10-turn sessions — **exactly the existing, frozen evaluation procedure, unmodified**, so the primary MAE metric's implementation and meaning are preserved exactly (no redefinition of `target_tracking_error`).

Reported for every condition:
- **Pooled MAE** (mean over all 125 sessions), matching the existing frozen metric exactly.
- **Per-persona MAE** and the **equally-weighted mean over the 5 personas** (not weighted by session count, matching the topic-equal-weighting discipline already established for D1's estimator, applied here to personas instead of topics).
- **Action distributions** (raw/final, by persona) and the guardrail-coverage/override decomposition from `rl_guardrail_coverage_decomposition.py`, re-applied to Condition B's replay — directly re-testing whether the demonstrated "Harder blind spot" (0-of-120 guardrail-free oracle-Harder agreement under Condition A) narrows under Condition B.
- **Across-seed variation**: all 5 of Condition B's training seeds reported individually and pooled, exactly as Condition A already is (`x3_0c_replay_summary.csv`'s existing per-seed/pooled format).
- **Training stability and cost**: reward and action-share curves (matching the existing `training_curves.csv` schema) per seed; wall-clock training time; peak memory, if measurable without new tooling.
- **Oracle-agreement vs. MAE, kept explicitly separate**: any improvement in oracle-matching (guardrail-free states) is reported as a **mechanism-consistency check**, never substituted for, or conflated with, the MAE result — exactly the distinction the prior audit's §6 required for the existing decomposition, carried forward here.

**Development/confirmatory separation, made explicit and enforced:**
- **Development phase:** all of the above, run and inspected freely, used to decide whether Condition B is worth reporting at all, to catch training instability, and to choose between the primary (24,576-step) and extended-budget (98,304-step) arms if both are run. Nothing in this phase is reported as a final result.
- **Confirmatory phase:** exactly one, pre-declared configuration (primary budget unless the development phase's own stability/action-share diagnostics — not its MAE outcome — indicate the primary budget is clearly still converging, in which case the extended-budget arm is declared confirmatory *before* looking at its MAE) is run once, on the same 5 confirmatory personas/seeds already used by every other frozen policy, and its numbers are the ones reported in the manuscript. **No checkpoint is selected by looking at multiple candidates' MAE and picking the best-scoring one** — the configuration choice is fixed by a stability criterion decided during development, not by confirmatory performance.

## 4. Baselines and ablations

| Arm | Purpose |
|---|---|
| Condition A (existing frozen PPO+G) | Reference: has the blind spot already been closed, or not, relative to what exists today? |
| Condition B, primary budget (new PPO+G) | Core test: does persona diversity alone change anything? |
| Condition B, extended budget (new PPO+G) | Diagnostic ablation: is a null primary result budget-limited? |
| Constant-Same+G (existing frozen) | Is *any* learned policy needed at all? |
| Heuristic+G (existing frozen) | Is a simple non-RL policy still preferable regardless of B's outcome? |
| **Narrow training-exposure diagnostic** | For Condition B's own training run (properly instrumented this time — see §7's logging fix), directly re-computes the training-time oracle-action distribution and reward-for-correct-Harder statistics from `PPO_TRAINING_EXPERIENCE_AUDIT.md`, this time **seed-attributable**, reported **separately from, not substituted for,** the primary MAE evaluation. |

This establishes two separate questions cleanly: (i) does broadened training improve PPO *over its existing version* (A vs. B, both PPO+G), and (ii) does it make PPO *competitive with the simpler baselines* (B vs. Constant-Same+G and Heuristic+G) — a positive answer to (i) does not imply a positive answer to (ii), and both are reported regardless of each other's outcome.

## 5. Decision criteria — fixed before any confirmatory run, not chosen after seeing results

**Retain the intervention (report Condition B as the paper's PPO result) only if all of the following hold, evaluated on the confirmatory personas/seeds, using the existing paired-difference/bootstrap methodology already established for Condition A vs. Constant-Same+G (persona-level paired difference, mean over training seeds, SD over 5 personas, ddof=1):**
1. **No pooled regression:** Condition B's pooled MAE is not worse than Condition A's pooled MAE.
2. **A pre-specified minimal meaningful per-persona improvement:** at least one of `struggling_junior` or `overconfident_fail` (the two personas where the prior audit found concentrated, populated opportunity) improves its MAE by **≥ 0.05 MAE units** relative to Condition A — chosen because it is an order of magnitude larger than the existing PPO+G-vs-Constant-Same+G difference (mean 0.0044) and roughly a quarter of the heuristic's existing margin over PPO (~0.20), i.e. large enough to plausibly matter, not a noise-sized threshold picked after the fact.
3. **No other persona regresses by ≥ 0.05 MAE units** relative to Condition A (no trading one persona's improvement for another's regression).
4. **The mechanism check moves in the expected direction:** the guardrail-free oracle-Harder agreement rate (0-of-120 under Condition A) is measurably higher than zero under Condition B — required as a consistency check on *why* any MAE change occurred, not sufficient by itself to retain.

**Revise within development (do not yet run a confirmatory comparison) if:** Condition B shows a directional improvement smaller than the §5.2 threshold, or improves the mechanism check without yet moving MAE, or the primary-budget arm shows training curves that have not converged by the training-budget's end (SB3 reward/action-share still trending) — in which case the extended-budget arm is promoted to the confirmatory configuration, decided on this stability evidence alone, before that arm's own MAE is inspected.

**Abandon (report Condition B as evidence against, not for, the persona-diversity hypothesis) if:**
- Pooled MAE regresses relative to Condition A or relative to Constant-Same+G, **or**
- The mechanism check shows no improvement at all despite the training-distribution change (directly falsifies the leading hypothesis from `PPO_TRAINING_EXPERIENCE_AUDIT.md`), **or**
- Training is unstable across multiple seeds (e.g., action-share oscillation or reward variance materially exceeding Condition A's own seed-to-seed spread, using Condition A's existing `training_curves.csv` as the stability reference).

**Complexity-vs-heuristic check, applied regardless of the above outcome, per the explicit instruction not to assume improving Harder improves the objective:** even if Condition B is retained by criteria 1–4, it is reported honestly against the Heuristic+G baseline. **If Heuristic+G's pooled MAE still beats Condition B's**, the manuscript states plainly that the demonstrated improvement over Condition A does not, by itself, justify PPO's added complexity relative to the simpler policy — this is not treated as a failure of the experiment, but as its own reportable finding, exactly matching this project's established practice of reporting the full evidence rather than only the flattering half.

## 6. Publication value under each outcome

- **Positive (retained per §5):** upgrades the paper's PPO finding from "no measurable advantage, cause unclear" to "the original null result is partly attributable to a narrow, single-candidate training distribution; broadening it produces a demonstrated, mechanism-linked, per-persona improvement" — a genuinely stronger, more precise scientific contribution, whether or not PPO ends up beating the heuristic (§5's complexity check is reported either way).
- **Mixed (revise/partial):** still reportable and valuable — a careful, honest account of exactly which personas improved, which didn't, and why the mechanism check does or doesn't track the MAE result, consistent with this project's audit-discipline framing (Phase D throughout this session).
- **Negative (abandoned per §5):** also a genuine contribution — it would mean the distribution-shift hypothesis, despite strong static-code and training-log support, does **not** fully explain or fix the evaluation-time behavior, and would redirect future work toward the untested alternatives already named (state/action-space limitations, training instability, or a more fundamental reward-structure issue) rather than further distribution-diversity attempts.
- **In every case, explicitly and permanently:** no claim is made, or may be made, about improved real interview effectiveness, human learning gains, or generalization beyond this synthetic simulator. Every number produced by E1 describes simulated-persona difficulty-tracking only, exactly like every existing P3 result.

## 7. Registration and reproducibility

### Precise implementation-change plan (not yet made; requires approval before any code is written)
**Exactly one new file, zero changes to any existing file:**
- New file (proposed path): `research/paper_strengthening/scripts/e1_diverse_persona_env.py`.
- Contents: a single class `DiversePersonaInterviewEnv(AlignedInterviewEnv)` (imported, unmodified, from `research.scripts.execute_paper3_study`, itself unmodified) that overrides **only** `reset()`:
  1. compute the next skill from the fixed `SKILL_GRID` (§2), cycling by an internal episode counter;
  2. construct `SimulatedCandidate(skill=skill, seed=<derived from the persona-sampling RNG stream>, persona="normal")` and assign it to `self.sim_candidate`;
  3. call `super().reset(seed=seed, options=options)` unchanged for everything else (difficulty initialization, observation construction).
- A second new file, a training driver (proposed path: `research/paper_strengthening/scripts/e1_train_condition_b.py`), that calls the **existing, unmodified** `train_ppo_seed`-equivalent PPO construction (same hyperparameters, same `PPO(...)` call signature) but passes a `DiversePersonaInterviewEnv` instance instead of the default `AlignedInterviewEnv()`, and additionally re-enables the existing per-step CSV logger (`rl/env/interview_env.py`'s built-in logging, already present and unmodified) pointed at a **new, non-gitignored, seed-and-condition-named path** (e.g. `research/paper_strengthening/results/e1_training_logs/condition_B_seed{N}.csv`), closing the attribution gap identified in `PPO_TRAINING_EXPERIENCE_AUDIT.md` §7.
- **`rl/env/interview_env.py`, `rl/guardrails.py`, `rl/training/simulated_candidate.py`, and `research/scripts/execute_paper3_study.py` are not modified in any way.** Condition A's existing frozen checkpoints, results, and replay artifacts are not touched, regenerated, or overwritten.

### Run manifest (proposed fields, matching the project's existing `RUN_MANIFEST_SPEC.md` conventions)
- **Experiment ID:** `E1-ppo-persona-diversity`.
- **Code:** the two new files above (paths and, once written, their SHA-256) plus the exact commit hash of every frozen file they import (`execute_paper3_study.py`, `rl/env/interview_env.py`, `rl/guardrails.py`, `rl/training/simulated_candidate.py`) at the time of the run.
- **Seeds:** training seeds `[42,123,456,789,999]` (shared with Condition A); persona-sampling stream seeds `[seed+10000 for seed in training seeds]`; evaluation seeds `[1001,2002,3003,4004,5005]` (shared with every existing frozen policy).
- **Config:** `SKILL_GRID` (§2, fixed and disclosed), `TIMESTEPS_PER_SEED` (24,576 primary / 98,304 extended-budget diagnostic), all PPO hyperparameters (unchanged, copied verbatim from `train_ppo_seed`).
- **Dataset/environment version:** none beyond the code commit — this experiment generates no external dataset, only simulated trajectories.
- **Compute estimate:** Condition A's 5 seeds took a combined ~7 minutes (`elapsed_sec: 83.84` per seed × 5, per `training_meta.json`); Condition B's primary arm at the identical budget should be comparable (~7–10 minutes combined, CPU-only, no GPU required for this small MLP policy); the extended-budget diagnostic arm (4×) scales to roughly ~28–40 minutes combined if run.
- **Evaluation:** identical replay procedure and G-REPRO-style gate check (reproduce Condition A's own already-published numbers from the same replay code path, as a pre-execution sanity check that nothing about the evaluation harness itself changed) before trusting any Condition B number.

### Proposed hash and tag (not created; for approval only)
- **Protocol file (this document):** `research/paper_strengthening/E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V1.md`.
- **SHA-256:** computed and reported in the accompanying chat response (matching the D1 protocol series' own registration convention).
- **Proposed Git tag (not created):** `prereg/E1-ppo-persona-diversity/v1`.

### What is explicitly preserved
All frozen P3 artifacts (`research/experiments/paper3/*`), all D1 protocol versions (V1–V14), `EXPERIMENT_PLAN.md`, `FINAL_MANUSCRIPT_EVIDENCE_V2.md`, and every prior report in `research/paper_strengthening/` are untouched by this document and would remain untouched by executing this protocol as designed (Condition A's checkpoints and results are read, never regenerated).

## 8. Methodological weaknesses, stated plainly

1. **Training-optimization randomness and persona-sampling randomness are seeded independently but both ultimately depend on the same base seed value** — a genuinely independent randomization scheme (e.g., an unrelated seed stream for persona sampling) would be cleaner; the chosen `seed+10000` offset is a reasonable, disclosed compromise, not a fully independent design.
2. **The single-axis (skill-only) diversity choice may be too narrow to fix a blind spot that also depends on conf/hesitation decoupling** (§2) — if Condition B is abandoned, this confound (diversity was real but incomplete) cannot be distinguished from "distribution shift isn't the cause" without a follow-up decoupling-axis experiment, which is explicitly out of scope here.
3. **With only 5 personas and 5 training seeds, the per-persona improvement criterion (§5.2) is likely underpowered for a formal inferential claim** — exactly the kind of small-sample limitation this project has repeatedly had to disclose elsewhere (D1's own topic-count limitations, the 8-question evaluator benchmark). The §5 criteria are deliberately magnitude-based, not significance-based, for this reason, but a magnitude threshold chosen without a proper power analysis is itself a judgment call, disclosed here rather than hidden.
4. **The extended-budget arm's promotion rule (chosen by training-stability diagnostics, not by its own MAE) still requires a human judgment call about what counts as "clearly still converging"** — this is a real, if disclosed and pre-specified, source of residual researcher discretion.
5. **Even a fully successful Condition B only demonstrates something about this specific simulator's dynamics** — nothing here narrows the much larger, separately-documented gap between this entire simulation study and any claim about real candidates (already the subject of the blocked, human-study `system_paper` track, out of scope for this experiment entirely).

## 9. Recommendation

**Worth registering and running as a development-only experiment, with the confirmatory run gated on the development phase's own stability check, not on a preview of its MAE.** Reasoning: the leading hypothesis is now supported by two independent lines of evidence (static code reading, N1; and the training-log audit's execution-level cross-check), the intervention is cleanly isolated to a single axis, the decision criteria are pre-specified and include an explicit abandonment path, and the cost is small (single-digit minutes of CPU training per arm) relative to the value of either resolving or ruling out the paper's most promising remaining lead on the RL finding. It is not recommended as anything more binding than that: a bounded, falsifiable, cheap-to-abandon bet, not a commitment to report a positive PPO result regardless of what the data show.

**Not started. No code written. No training run. No tag created. No commit or push. Awaiting explicit approval before writing `e1_diverse_persona_env.py` / `e1_train_condition_b.py` or executing anything.**
