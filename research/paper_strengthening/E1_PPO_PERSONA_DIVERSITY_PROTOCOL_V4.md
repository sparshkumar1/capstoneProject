# E1 — PPO Persona-Diversity Development Experiment: Protocol V4 (FINAL)

**Status: design only, frozen for registration. Not executed, not tagged, not committed, not pushed. No code written. No training run.** V1, V2, and V3 are preserved unmodified. This final consolidated review found six substantive, concrete defects in V3 — none cosmetic, several caught only by actually reading the relevant code or computing the relevant numbers rather than assuming them. All are fixed below. This version is intended as final; §8 states explicitly why no further round is expected to be needed.

## 0. What changed from V3, and why each change was necessary

1. **RNG-matching between B0 and B2 was not precisely specified (§1.2).** V3 said the two arms were "matched" but never pinned down whether the underlying random draws feeding `SimulatedCandidate`'s own noise are identical between corresponding B0/B2 cells before the `k`-transform is applied. Left unspecified, an implementation could accidentally give the two arms different noise realizations, adding avoidable noise to the one comparison the whole protocol exists to make. **Fixed** with an explicit, single-formula RNG-derivation requirement.
2. **B0 could be silently dropped from confirmatory evaluation (§2, §4).** V3's development-stage gate described choosing "the arm(s)" to carry forward based on B2's behavior relative to B0, without explicitly guaranteeing B0 is *always* included whenever B2 is. Since the decisive scientific question is B2-vs-B0, not B2-vs-Condition-A, this was a real gap. **Fixed**: whenever the study proceeds to confirmatory evaluation at all, both arms are evaluated on the identical locked scenarios, unconditionally.
3. **The confirmatory decision criteria only referenced "vs. Condition A," not the three required contrasts (§4).** **Fixed**: B0-vs-Condition-A, B2-vs-B0, and B2-vs-Condition-A are now all named, all always reported, with B2-vs-B0 identified explicitly as the decisive test.
4. **Five confirmatory evaluation seeds are not well justified given how cheap evaluation is (§3).** **Fixed** with a concrete, non-power-claim rationale (below) and an increase to 20 confirmatory evaluation seeds, matching `X3-A`'s own established convention; training seeds remain at 5, with the cost asymmetry between training and evaluation stated as the reason these two counts are treated differently.
5. **Two concrete arithmetic/design errors in the held-out profiles (§2.4).** V3's profile table wrote `round(skill*5,1) → 2.25` — an internal inconsistency (2.25 is not rounded to 1 decimal place) — and used `skill=0.88` for one profile, which **is** `nervous_expert`'s exact skill value in `PERSONA_TARGETS`, so it was not actually a new, unseen skill value. **Fixed**: the exact `X3-A` target formula (`round(10*skill)/2.0`, read directly from `x3a_lib.py::persona_grid()`) is now used verbatim, and all three profile skills are computer-verified to collide with no existing grid (`PERSONA_TARGETS`, `X3-A`'s 8-point grid, or B0/B2's 6-point grid).
6. **`x3a_lib.py` cannot actually be reused unmodified for B0/B2/the held-out profiles, and V3 overstated that it could (§5).** Direct reading of `x3a_lib.py::simulate()` shows it hardcodes `SimulatedCandidate(skill=skill, persona=ptype, seed=eval_seed)` internally — it has no parameter for a custom candidate object or a `k` value, so it cannot be pointed at the decoupling wrapper as-is. **Fixed**: `x3a_lib.py`'s lower-level helpers (`shield()`, `make_policy()`, `PPOPolicy`) genuinely are reusable unmodified; a small, new, disclosed adapter function is specified (§5) that reimplements only `simulate()`'s loop shape while calling those two helpers unmodified and constructing the candidate via the decoupling wrapper instead.

## 1. The matched intervention, precisely specified

### 1.1 Arm definitions (unchanged from V3)

| Arm | Candidate construction | Purpose |
|---|---|---|
| **B0** | Wrapper around `SimulatedCandidate(skill=s, persona="normal")`; `(s,k)` cycles through the 6×4=24-cell grid with `k` fixed at `0.0` | Matched skill-only control |
| **B2** | Same wrapper; `(s,k)` cycles through `s∈{0.20,0.35,0.50,0.65,0.80,0.90} × k∈{0.0,0.30,0.45,0.60}` | Tests decoupling's incremental value over B0 |

### 1.2 Precise isolation requirement (new — closes defect 1)

**The wrapper must derive each episode's underlying noise identically for B0 and B2 at corresponding grid cells, so the only difference between the two arms is whether the `k`-offset is applied.** Concretely: for training seed `t` and episode index `i`, both arms construct their episode-`i` `SimulatedCandidate` with `seed = t*100_000 + i` (an explicit, disclosed, injective function of `(t,i)`, independent of which arm or which grid cell — the same seed value is used by B0 and B2 for the same `(t,i)` pair regardless of which `k` or `s` value that episode happens to draw). This makes the comparison a genuine **paired** design at the episode level (same underlying `perf`/`conf`/`hes` draw before the transform, for matching cells), not merely a matched-marginal-distribution design — strictly stronger than V3 specified. The persona-sampling stream (which grid cell to visit at episode `i`) remains the deterministic cycling rule from V2/V3 (`grid[i % 24]`), identical for B0 and B2, so both arms visit the same cell sequence in the same order.

**Training duration, matched explicitly (closes the other half of defect 1):** if training-curve non-convergence triggers the extended-budget diagnostic (98,304 steps, retained from V1–V3 as a conditional escape hatch), it is applied to **both B0 and B2 together** — the extended budget is never used for one arm alone, precisely so a difference in outcome cannot be attributed to a difference in how much either arm trained.

## 2. Evidentiary status — unchanged from V3, restated briefly

§0–2 of V3 (the training-evidence interpretation, the honest retrospective/prospective classification of the `lucky_guesser` hypothesis, and the `X3-A` cross-validation finding — raw/final Harder share 0.000–0.010 across all 8 `lucky_guesser` skill levels, oracle-agreement 0.482, lowest of any persona type) are carried forward **unchanged**; nothing in this review found any defect in that material.

### 2.4 Held-out profiles — corrected (closes defect 5)

**Exact formula, verified against `x3a_lib.py::persona_grid()` line by line:** `target_difficulty = round(10 * skill) / 2.0` (not the `skill*5` approximation V3 used, which happened to coincide at existing grid points but was not verified to be the same formula, and was applied inconsistently in V3's own table).

**Three profiles, skills computer-verified to collide with none of: `PERSONA_TARGETS` {0.20, 0.30, 0.60, 0.80, 0.88}, `X3-A`'s grid {0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90}, or B0/B2's grid {0.20, 0.35, 0.50, 0.65, 0.80, 0.90}:**

| Profile ID | skill | k | target_difficulty (`round(10·skill)/2.0`, exact) |
|---|---|---|---|
| HOLDOUT-1 | 0.27 | 0.20 | 1.5 |
| HOLDOUT-2 | 0.58 | 0.38 | 3.0 |
| HOLDOUT-3 | 0.83 | 0.52 | 4.0 |

**Classification, as instructed:** these are **held-out configurations / targeted interpolation checks within the same simulator and the same intervention family** — fixed synthetic `(skill,k)` points chosen to fall between existing grid cells, using the same decoupling mechanism as B2. They are evidence about whether the intervention generalizes to nearby, previously-unexamined points in this synthetic parameter space. **They are not, and must not be described as, evidence of broad real-world generalization** — nothing about a real candidate population is implied or tested by them. They remain, as in V3, entirely outside development and checkpoint selection: touched exactly once, at the confirmatory stage, for whichever arm(s) are being confirmed.

## 3. Evaluation precision — sample sizes selected and justified before execution

**Training seeds: 5, unchanged from every existing study of this system.** `X3-A`'s own protocol (`PROTOCOL.md`, §4) states plainly: *"With 5 training seeds the seed dimension gives a coarse but reported contribution"* — the project's own most rigorous existing confirmatory study accepted 5 training seeds as the standard for this system, not more. Training is the computationally expensive dimension (each seed is a real PPO optimization run); going beyond 5 would cost roughly linearly more compute for a dimension the project's own precedent already treats as adequately (if coarsely) covered, and — since B0 and B2 both need this — doubling training seeds would roughly double the experiment's training cost for the two arms combined. **Not increased.**

**Confirmatory evaluation seeds: increased from V3's 5 to 20, matching `X3-A`'s own convention.** Evaluation is comparatively free — it is pure inference on already-trained checkpoints, not training, so more evaluation seeds cost only a few extra seconds of simulated rollout, not more optimization. The concrete, non-power-claim rationale: for a fixed persona and training seed, averaging a metric (e.g. MAE) over `n` evaluation seeds reduces its standard error by a factor of `√n` relative to a single seed, all else equal; going from 5 to 20 evaluation seeds **reduces that standard error by a factor of `√(20/5) = 2`**, at negligible additional cost, for exactly the metric (`lucky_guesser`'s per-arm MAE) the confirmatory decision in §4 hinges on. This is a descriptive statement about noise reduction from averaging, **not a formal power calculation or a significance guarantee** — no claim is made about achieving a specific target power or a guaranteed detectable effect size, consistent with this project's standing refusal to manufacture power claims without real variance/effect-size inputs (as `SYSTEM_PAPER_RESEARCH_DECISION.md` already states elsewhere in this project for a different experiment).

**Confirmatory seed block, verified:** `EVAL_SEEDS_CONFIRMATORY = [21021, 22022, 23023, 24024, 25025, 26026, 27027, 28028, 29029, 30030, 31031, 32032, 33033, 34034, 35035, 36036, 37037, 38038, 39039, 40040]` (20 values, continuing the established increment-by-1001 pattern one full block past `X3-A`'s own `1001…20020` range). **Searched directly** against every `.py`, `.csv`, `.json`, and `.md` file under `research/`, `rl/`, `experiments/`, and `ablation/`; every apparent match inspected individually and confirmed to be a coincidental digit substring inside an unrelated hash, float, or byte-count value (e.g. `13103104` containing `31031`), not an actual seed usage. **Limits of this verification, stated honestly, unchanged from V3:** this covers the current tracked working tree only; it cannot rule out use in an untracked, gitignored, or since-deleted local run, though a collision there would not be scientifically consequential (only the *novelty* claim, not the simulation's validity, would be affected).

## 4. The decisive comparison, evaluation composition, and decision rules — corrected

### 4.1 Both arms always evaluated together (closes defects 2–3)

**Whenever this protocol proceeds to a confirmatory run at all, both B0 and B2 are evaluated on the identical, locked confirmatory scenario set (`EVAL_SEEDS_CONFIRMATORY` + the three held-out profiles) — unconditionally.** B0 is never omitted from the confirmatory stage merely because development results favored B2; the decisive scientific comparison requires both arms' confirmatory-stage numbers together, not B2's comparison against Condition A alone.

**Three contrasts, always computed and reported, all on the same locked confirmatory data:**
1. **B0 vs. Condition A (existing frozen PPO+G)** — does skill diversity alone change anything?
2. **B2 vs. B0 — the decisive test** — does confidence/hesitation decoupling add value *beyond* matched skill diversity? This is the contrast the whole matched design exists to make possible, and it is reported as the primary scientific finding of this experiment regardless of what the other two contrasts show.
3. **B2 vs. Condition A** — does the full intervention improve over the currently-deployed baseline?

Constant-Same+G and Heuristic+G remain in every comparison table as reference baselines, unchanged from V1–V3.

### 4.2 Metrics and reporting (unchanged in substance from V3, restated precisely)

Primary objective: the existing, unmodified `target_tracking_error` MAE — no redefinition. Reported for every one of the three contrasts, on the confirmatory data: pooled MAE and the equally-weighted mean over personas/profiles; per-persona/per-profile MAE, with `lucky_guesser` and the three held-out profiles specifically named; **persona-level regressions** (any persona/profile whose MAE gets worse, by how much, under any arm relative to Condition A); **variation across the 5 training seeds** for each arm; the guardrail-coverage/oracle-agreement mechanism check (secondary, reported separately, never merged with the MAE rows); and **computational cost actually incurred** (wall-clock training time per arm/seed, evaluation time, environment/hardware).

### 4.3 Decision rules, predefined and internally consistent

**Development-stage gate (before any confirmatory seed is touched):** proceed to confirmatory evaluation only if B2 shows a directional mechanism-check improvement over B0 on the development seeds (`1001…5005`), with no per-persona regression ≥0.05 MAE units relative to B0 on those same seeds. If this does not hold, **no confirmatory run is executed for either arm** — the hypothesis is reported as unsupported at the development stage.

**Confirmatory retain (B2), evaluated against both required references:**
- **Relative to B0** (the decisive contrast): `lucky_guesser`'s MAE improves by ≥0.05 MAE units, no other persona/profile regresses by ≥0.05 relative to B0, and the guardrail-free `lucky_guesser` oracle-Harder agreement rate is measurably above B0's own rate on the same confirmatory data (required, never sufficient alone — an oracle-agreement improvement with no MAE improvement over B0 is reported as exactly that, not as a retained result).
- **Relative to Condition A**: pooled MAE not worse than Condition A's; `lucky_guesser`'s MAE improves by ≥0.05 relative to Condition A; no other persona/profile regresses by ≥0.05 relative to Condition A.
- **A positive result requires improvement in the actual MAE objective, on both required contrasts — a higher oracle-agreement rate alone, under any contrast, is never sufficient and is never reported as a positive result by itself.**

**Confirmatory abandon:** pooled MAE regression for B2 relative to B0 or Condition A; or no mechanism-check movement for B2 relative to B0 despite the targeted, verified (§1.2's fidelity check, carried from V3) design — a cleaner falsification than either V1 or V2 could offer, since the grid is now verified to actually reach the target states.

**Complexity-vs-heuristic check, applied to whichever arm(s) are retained, regardless of the outcome above:** reported honestly against Heuristic+G's pooled MAE on the same confirmatory data. **This is explicitly distinguished from "improvement over existing PPO"**: an arm can show a real, retained improvement over Condition A and B0 while Heuristic+G still wins overall — both facts are reported, neither is allowed to obscure the other. If Heuristic+G still wins, the manuscript states plainly that the demonstrated improvement does not by itself justify PPO's added complexity — a reportable finding, not a failure of the experiment.

**No arm or checkpoint is ever selected by its own confirmatory-seed MAE** — the development gate (above) is the only selection mechanism, and it runs strictly before `EVAL_SEEDS_CONFIRMATORY` is touched.

## 5. Implementation plan, verified against the actual code (closes defect 6)

**What is genuinely reusable from `x3a_lib.py`, unmodified, verified by reading it directly:**
- `shield(perf, avg_perf, conf, hes, difficulty, proposed, disabled=frozenset(), ...)` — the guardrail function, takes plain numeric arguments; directly reusable for B0/B2/held-out evaluation with no adapter needed.
- `make_policy(kind, persona_index=0, eval_seed=0, ppo=None, mutant=None)` and `PPOPolicy` — policy loading/prediction; directly reusable to load Condition A's or the new arms' checkpoints.

**What is not reusable as-is, verified by reading it directly:** `simulate(policy_fn, ptype, skill, target, eval_seed, shield_on, ...)` hardcodes `cand = SimulatedCandidate(skill=skill, persona=ptype, seed=eval_seed)` on its own line — it has no parameter through which a custom candidate object, a wrapped/decoupled candidate, or a `k` value could be passed. **It cannot be pointed at B0/B2/the held-out profiles without either modifying it (not permitted — it is part of a frozen, tagged, gated study) or writing a new function that reimplements only its loop shape.**

**Precise, minimal new-file plan (zero changes to any existing file, including `x3a_lib.py`):**
1. `research/paper_strengthening/scripts/e1_diverse_persona_env.py` — defines the decoupling wrapper class (compositional, holding an internal `SimulatedCandidate(skill=s, persona="normal", seed=...)`, per §1.2's exact seed formula) and the B0/B2/held-out grid definitions.
2. `research/paper_strengthening/scripts/e1_simulate_adapter.py` — a new function, `simulate_diverse(policy_fn, wrapped_cand_factory, target, eval_seed, shield_on, max_steps=10)`, that mirrors `x3a_lib.simulate()`'s loop shape (obtain the wrapped candidate's answer, build the 6-D state, call the policy, call `x3a_lib.shield()` unmodified, apply the resulting action, track the trajectory) but constructs its candidate via the wrapper factory from file 1 instead of a raw `SimulatedCandidate`. This function **imports and calls `x3a_lib.shield` and `x3a_lib.make_policy`/`PPOPolicy` unmodified** — it duplicates only the small amount of loop logic that `x3a_lib.simulate()` does not expose as a separable, reusable piece.
3. `research/paper_strengthening/scripts/e1_train_condition_b.py` — the training driver for B0/B2 (unchanged in role from V1–V3), using the §1.2 seed-derivation formula and the same, unmodified PPO hyperparameters as Condition A.
4. Per-step training logs written to a new, non-gitignored, arm-and-seed-named path (closing the attribution gap `PPO_TRAINING_EXPERIENCE_AUDIT.md` identified), reusing the existing, unmodified `InterviewEnv` CSV logger.

**Preserved, unmodified, throughout:** `x3a_lib.py`, `x3a_config.json`, `x3a_run.py`, `x3a_analyze.py`, every file under `research/confirmatory/X3-A/results/` and `research/preregistration/X3-A/`, every frozen P3 checkpoint/result, and `rl/env/interview_env.py`, `rl/guardrails.py`, `rl/training/simulated_candidate.py`, `research/scripts/execute_paper3_study.py`.

## 6. Publication value — unchanged in substance from V3

Carried forward from V3 §5 without modification: a positive result (B2 beats B0 on the decisive contrast, corroborated by `X3-A`) is the strongest outcome, reported honestly as validation of a substantially (not purely) pre-existing, data-informed hypothesis; a mixed result (the held-out profiles behave differently from the named personas) is a genuine generalization finding; a negative result, given the now-verified intervention design, is a cleaner, more informative falsification than either prior version could offer. No claim of real interview effectiveness, human learning, or generalization beyond this synthetic simulator is supported by any outcome.

## 7. Registration package

- **Protocol file (frozen):** `research/paper_strengthening/E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V4.md`.
- **SHA-256:** reported in the accompanying chat response.
- **Proposed Git tag (not created):** `prereg/E1-ppo-persona-diversity/v4` (superseding v1–v3, none of which were ever created).
- **Run manifest fields:** training seeds `[42,123,456,789,999]` (shared with Condition A); episode-seed formula `seed = training_seed*100_000 + episode_index` (§1.2, identical for B0/B2); development seeds `[1001,...,5005]`; confirmatory seeds `EVAL_SEEDS_CONFIRMATORY` (20 values, §3, verified absent from the tracked repository); held-out profiles (§2.4, exact skills/k/targets); `TIMESTEPS_PER_SEED=24576` primary / `98304` extended-budget diagnostic (applied to both arms together only); all PPO hyperparameters unchanged, copied verbatim from `train_ppo_seed`; git commit of every frozen file imported, recorded at run time.
- **Compute estimate, unchanged from V2/V3:** on the order of minutes of CPU-only training for both arms combined at the primary budget; confirmatory evaluation (20 seeds × 2 arms + Condition A + baselines + 3 held-out profiles) is inference-only and adds negligible time.

## 8. Remaining defects: none found in this pass beyond those fixed above

Every item in this review's six numbered points was checked against the actual code or an actual computation, not assumed: the RNG-matching gap, the B0-omission risk, the missing three-contrast requirement, the seed-count justification, the held-out-profile arithmetic and skill-collision errors, and the `x3a_lib.simulate()` reuse limitation were all real and are all fixed above. No further substantive issue was identified. This version is presented as final; the next legitimate step is either approval to implement §5's three new files, or a decision not to proceed — not another audit pass of the same design.

## 9. Recommendation

**Worth registering and running, and now genuinely ready for that step.** The matched design is precise (episode-level RNG pairing, not just matched marginals); the decisive B2-vs-B0 contrast is guaranteed to be measurable under every path through the decision rules; sample sizes are chosen for a stated, non-invented reason; the held-out profiles are correct and honestly classified; and the implementation plan reflects what the existing code actually supports, including the one place it does not (`x3a_lib.simulate()`) and the precise, minimal adapter needed to work around that without touching any frozen file. Cost remains small.

**Not started. No code written. No training run. No tag created. No commit or push. Awaiting explicit approval before writing any of the three new scripts or executing anything.**
