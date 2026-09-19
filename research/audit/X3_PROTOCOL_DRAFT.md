# X3 Protocol Draft — Paper 3 controlled decomposition (2026-09-19)

**Status: DRAFT. Not registered, not hashed, not tagged, not executed.** Fields marked **[FIX IN PHASE 2]** are completed and reviewed before hashing/tagging (`PREREGISTRATION_SPEC.md`). No X3 evaluation, persona generation for confirmatory use, or training may start before the tag. This draft changes no PPO, reward, state, action, guardrail or simulator definition.

Locked decisions (`PHASE0_DECISION_LOCK.md`): reframe as a controlled decomposition (shield vs rules/oracle vs heuristic/controller vs learned policy); PPO is a **studied component, not the headline claim**; X3-0 and X3-A approved; X3-B conditionally approved; **δ = 0.12 MAE (equivalence), m = 0.20 MAE (superiority)**; **X3-B trigger frozen before X3-A** (§6); **no PPO hyperparameter tuning; no reward redesign; no second simulator yet**.

## 0. Central question
In a simulated adaptive-difficulty task, how much of the tracking performance is attributable to (i) the guardrail shield, (ii) rule-based policies (oracle rules, heuristic, proportional controller) and (iii) a learned PPO policy, once trivial and state-blind policies receive the same shield?

## 1. Fixed context (from frozen artifacts; not changed by X3)
- Simulator, guardrail module (rules G0, G4, G1, G2, G5, G6 as in `frozen_config.yaml`), reward weights (0.60 / 0.30 / 0.10 / −0.10), state (6-D) and action (Discrete(3)) definitions and PPO hyperparameters are those of the frozen study (`frozen_config.yaml`, SHA-256 `d3da2184…4d9e`); X3 changes none of them.
- The PPO reward is largely imitation of a rule oracle, and the evaluation metric (mean |difficulty − persona target|) is not the training objective; the frozen checkpoints were trained for 24 576 steps in an environment (T = 15, continuous 0.1 steps) that differs from the evaluation environment (T = 10, integer ±1). These are disclosed limitations, not defects to be fixed inside X3-A.
- Persona targets in the frozen study equal `round(10·skill)/2` for all five personas (arithmetic; not stated in the config). Simulation-only; no learner claim.

## 2. X3-0 — Corrected accounting from stored data (analysis, no new experiment)
**Inputs (frozen, read-only).** `paper3_seed_results.csv`, `paper3_baseline_results.csv`, `paper3_ablation_results.csv`, `paper3_guardrail_results.csv`, `paper3_raw_results.json`, frozen checkpoints and code for replay.
**Outputs (new stored files, new script, manifest).** (1) attempted boundary actions for raw proposal and final action, per seed/persona/session, with denominators; (2) rule activations vs action overrides (563 vs 99) with per-rule, per-persona and per-session breakdown, no-op share, direction of overrides; (3) five-seed volatility table (MAE, volatility, oscillation) for heuristic / PPO+G / raw PPO / Const-Same+G; (4) corrected P1-14 ablation rows; (5) persona-level paired differences and their SD (**input to the X3-A sample-size rationale**); (6) per-turn logs including perf/conf/hes for the replayed conditions, which the frozen study did not store. Replay results register as `PENDING-REGISTRATION → VALID` only after being stored and hash-verified. **Nothing in the frozen files is modified.**

## 3. X3-A — Stage 1 decomposition (evaluation-only on existing checkpoints)
**Question.** With the five frozen PPO checkpoints, what do the shield, rule policies, heuristic and PPO contribute across a pre-specified persona set?

**Conditions (base policy × shield {off, on}).** Fixed (difficulty 3.0); Constant-Same; Random (20 draws averaged as one condition); Heuristic (frozen definition); **Oracle-rule policy** (`oracle_action_from_obs`, rules R1–R7; the reward's teacher); **Proportional controller** (difficulty ≈ 5 × running mean performance, specified exactly and hashed before running; documented as exploiting the persona target rule and reported as an *upper reference*, not a fair competitor); PPO (five checkpoints). Additional evaluation-only controls: **state-shuffle / state-constant PPO** (observations permuted across turns within a session, or held constant, at evaluation) and **guardrail-rule ablation** (each of G1, G2, G4, G5 individually off) on PPO+G and Const-Same+G. Optional if cheap and pre-specified: Constant-Easier/Harder + G as diagnostics.

**Personas.** ≥ 24 personas from a **pre-specified generator [FIX IN PHASE 2]**: skill grid × confidence bias × hesitation/anxiety, with the target set by the documented rule `target = round(10·skill)/2` (stated as an authored rule) — not hand-tuned per persona. The five frozen personas are included and flagged as the training-distribution subset; the remaining personas test generalisation of the checkpoints and are reported as a separate stratum. The generator, its seed and the resulting persona table are hashed before any checkpoint is evaluated. Whether training sampled the five frozen personas has **not** been verified and must be established before interpreting the strata **[FIX IN PHASE 2]**.

**Seeds.** 20 evaluation seeds per persona, fixed list **[FIX IN PHASE 2]** (the frozen evaluation seeds 1001…5005 may be a subset); the five existing training seeds (42/123/456/789/999); same seed sets across conditions; `deterministic=True`.

**Endpoints.**
- **Primary:** Δ = mean paired difference in persona-level tracking MAE, **PPO+G − Constant-Same+G**, averaged over training seeds (negative = PPO better).
- Secondary: PPO+G vs Heuristic+G and vs Oracle+G; raw PPO vs Fixed; shuffled/constant-state PPO vs intact PPO (does PPO use state?); oracle agreement (the trained objective); boundary-saturated action rate; volatility; oscillation; override and activation rates; per-rule ablation effects.

**Unit and inference.** Unit = **persona**; training seed = second random factor; evaluation seeds nested (averaged within persona × training seed). Two-way cluster bootstrap over personas and training seeds (B ≥ 10 000; RNG seed logged), 95 % percentile CI; effect sizes: mean paired difference (difficulty units) and Cohen's d_z on persona-level differences. Sensitivity: mixed model `MAE ~ policy + (1 | persona) + (1 | train_seed)`. Sessions/turns are descriptive only. With 5 training seeds the seed dimension gives wide intervals; this is stated, not hidden.

**Sample-size rationale.** ≥ 24 personas; precision target CI half-width ≈ 2.07·SD_d/√24 with SD_d the persona-level paired SD estimated from the frozen data in X3-0 and written into the protocol before tagging **[FIX IN PHASE 2]**.

**Outcome classification (frozen; drives the X3-B trigger).** Let CI = the 95 % CI of Δ.
| Class | Rule |
|---|---|
| **Equivalent** | CI wholly inside (−0.12, +0.12) |
| **PPO superior** | upper CI bound ≤ −0.20 (PPO better by at least m) |
| **PPO adverse** | lower CI bound ≥ +0.12 (PPO worse by more than δ) |
| **Inconclusive** | none of the above (includes CI spanning zero and wider than δ; and improvements larger than δ but not established as ≥ m) |

**Stopping rule.** Fixed personas, seeds, conditions and endpoints; no optional stopping; no persona added, removed or reweighted after data exist; no tuning of margins, thresholds, guardrails or PPO.

**Interpretation rules.**
- *Equivalent:* "no detectable PPO contribution beyond the shield in these checkpoints" (an equivalence result within ±0.12 MAE).
- *PPO superior:* a claim about **these checkpoints** in this simulator only; a method-level claim additionally requires X3-B.
- *PPO adverse:* PPO+G is worse than a state-blind action with the same shield; reported.
- *Inconclusive:* never reported as "no effect".
- Heuristic/Oracle/controller comparisons are reported whichever way; a heuristic that beats PPO is a finding, not an anomaly.
- The tracking result is interpreted with the oracle-agreement endpoint: PPO is judged on what it was trained for as well as on tracking.

**Contamination controls.** margins (δ = 0.12, m = 0.20), classification rule, endpoints, persona generator/table, controller definition and seed lists hashed **before** any checkpoint is evaluated on generated personas; the five frozen personas are not used to choose anything; environment locked; per-turn logs stored.
**Artifacts.** config, persona table + generator seed, checkpoint hashes, per-turn logs (perf/conf/hes/action/final action/rule IDs), CSVs, manifest, analysis script.

## 4. X3-B — Stage 2 training-consistent study (conditionally approved; requires the trigger)
**Trigger.** See §6. If not triggered, X3-B is not run and no method-level PPO claim is made.
**Scope (locked constraints).** Reward, state, action and PPO hyperparameters **unchanged** from the frozen config (no tuning, no reward redesign); no second simulator; no outcome-only reward arm.
**Question.** In an environment consistent with evaluation and at a stated budget series, what does a learned policy add over the shield and over behaviour cloning?
**Design.** Learner {PPO, behaviour cloning of the oracle (supervised classifier), none} × training budget {series fixed in advance, e.g., 25 k / 100 k / 500 k timesteps [FIX IN PHASE 2]} × shield in the loop {on, off}; evaluation in the same environment definition; ≥ 10 training seeds; the X3-A baselines re-run in that environment; same persona set and evaluation seeds as X3-A.
**Environment definition.** Evaluation-consistent training environment (turn count T and difficulty grid) specified in Phase 2 **[FIX IN PHASE 2]**. Because this touches environment definitions that `CLAUDE.md` reserves to the user, the user confirms the exact definition before the trigger is evaluated.
**Endpoints, unit, inference, margins, classification, interpretation.** As in X3-A (same δ and m), plus learning curves and oracle agreement per budget.
**Seeds and reproducibility.** model `seed=`, environment seeding, evaluation seeds; SB3/PyTorch versions and hardware recorded; identical seeds are not assumed to reproduce across platforms; W&B **for new runs only** (`wandb.init()` before the callback; explicit `model_save_path`/`model_save_freq`; config, seed, commit and lock hash logged; no API key in the repo).
**Stopping.** fixed budgets; no early stopping on results; failed runs are reported.
**Artifacts.** new frozen config, checkpoints + hashes, W&B run IDs, per-turn logs, manifest, lock.

## 5. Reporting rules for Paper 3 (fixed now)
1. Framing: controlled decomposition of shield, rules/oracle, heuristic/controller and learned policy; PPO's contribution is an empirical finding.
2. Terminology: "rule activations" (563) vs "action overrides" (99); "boundary-saturated / attempted boundary actions" (never "violations", never "0"); five-seed volatility 0.186 (never 0.088 as aggregate).
3. Unit: persona (training seed second factor); sessions descriptive.
4. Reward described as imitation of a rule oracle plus a rule-based shield; train ≠ evaluation environment disclosed for frozen checkpoints.
5. Simulation only; no learner, learning-gain or deployment claim; the deployed checkpoint is not the evaluated one.

## 6. X3-B trigger (frozen before X3-A is executed)
- **Rule.** X3-B is run **if** the X3-A outcome class is **Inconclusive**, **or** if the authors decide, *before X3-A is executed and recorded in the tagged protocol or a dated decision note*, that a **method-level PPO claim** ("PPO as a method improves/does not improve …") is to be made.
- If X3-A is Equivalent, PPO-superior or PPO-adverse and no method-level claim was pre-declared, X3-B is **not** run; conclusions are limited to the tested checkpoints and environment.
- The decision about a method-level claim is recorded (date, decision-maker) **[FIX IN PHASE 2, by the user]** and cannot be changed after X3-A data exist.

## 7. Open items **[FIX IN PHASE 2]**
Persona generator and N; evaluation seed list; controller definition; SD_d from X3-0; whether training sampled the frozen personas; optional diagnostics list; X3-B environment definition and budget series; method-level-claim decision; analysis script skeleton hash.
