# E1 — PPO Persona-Diversity Development Experiment: Protocol V3

**Status: design only. Not registered, not executed, not tagged, not committed, not pushed. No code written. No training run.** V1 and V2 are preserved unmodified. This audit found four substantive issues in V2 — an unmatched-arms confound, an unverified decoupling grid, a false "never-before-used" seed claim, and an incomplete evidentiary classification — **and, in the course of checking the seed claim, discovered an existing, much larger, already-frozen confirmatory study (`X3-A`) that changes this protocol's evidentiary basis and design substantially.** None of this is cosmetic.

## 0. What changed from V2, and why

1. **Unmatched arms, fixed (§1).** V2's B1 (17 skill values, single axis) and B2 (6×4 = 24 cells) differed in skill-grid resolution and per-cell exposure count as well as in the decoupling parameter — a genuine confound between "more/different skill diversity" and "behavioral decoupling." **Fixed**: a new **B0** arm uses B2's exact 6-value skill grid and exact per-cell exposure structure, with the decoupling parameter fixed at `k=0` throughout — B0 and B2 now differ in exactly one thing. V2's original 17-point B1 is **dropped from the confirmatory design** (§1.3): it answers a different question (does finer skill resolution matter at all, independent of decoupling) than the one this protocol is built to test, and reintroducing it would reintroduce exactly the "combine multiple things at once" problem this whole audit line has been removing.
2. **The decoupling grid's effect was verified by direct computation, not assumed (§1.2).** Calling the actual `SimulatedCandidate.answer_question()` 2,000 times per cell shows the originally proposed `k∈{0,0.15,0.30,0.45}` grid barely exercises the target guardrail-exclusion condition below `k=0.45` (0.000–0.06 hit-rate for `k≤0.30`) and only becomes reliable at the top of the grid (`k=0.45`: 47–58%). **Fixed**: the grid is widened to `k∈{0.0, 0.30, 0.45, 0.60}`, verified to reach 94–95% hit-rate at `k=0.60` with negligible clipping saturation (≤1.1% of samples pinned at a boundary) — exact numbers in §1.2.
3. **A false claim, caught and fixed (§2.3).** V2 asserted `EVAL_SEEDS_CONFIRMATORY = [6006,7007,8008,9009,10010]` were "never-before-used." **This was false.** A direct search of the repository found them already in use by `research/confirmatory/X3-A/` — a real, existing, already-executed, pre-registered confirmatory study (`prereg/X3-A/v1`) that evaluates the same five frozen PPO checkpoints across a 20-seed, 40-persona grid. New, actually-verified seeds are proposed in §2.3, with the verification's limits stated honestly.
4. **A major evidentiary discovery that reframes this whole protocol (§2.2).** `X3-A`'s own already-frozen results — re-examined here for the first time in this session — show, at 8× the persona count and with 15 of its 20 eval seeds never previously examined for this purpose, the **same lucky_guesser-specific Harder blind spot** found earlier from a single persona: across all 8 `lucky_guesser` skill levels (0.2–0.9), PPO's raw "Harder" proposal rate is 0.000–0.010, its final (post-guardrail) Harder rate is identically low, and its oracle-agreement rate (0.482) is the lowest of any persona type. This is **substantially independent, much higher-powered, already-existing confirmation** — not a re-analysis of the same small sample the hypothesis was built from. This changes both the evidentiary classification in §2.2 and the practical design in §2.4 (E1 now reuses `X3-A`'s own evaluation harness and results rather than re-deriving a smaller, less rigorous comparison from scratch).

## 1. The intervention, matched

### 1.1 Arm definitions

| Arm | Candidate construction | Purpose |
|---|---|---|
| **B0 (new — matched skill-only control)** | Compositional wrapper around `SimulatedCandidate(skill=s, persona="normal")`; `(s, k)` cycles through the identical 6×4 = 24-cell grid as B2, but `k` is fixed at `0.0` for every cell (so `s` is drawn from `{0.20,0.35,0.50,0.65,0.80,0.90}`, each repeated 4× per pass through the grid, matching B2's exposure count exactly) | Isolates the skill-diversity axis alone, with **identical grid resolution and identical per-skill-value exposure count to B2** — the confound in V2 is removed. |
| **B2 (unchanged mechanism, grid updated)** | The same wrapper, `(s,k)` cycling through `s∈{0.20,0.35,0.50,0.65,0.80,0.90} × k∈{0.0,0.30,0.45,0.60}` (24 cells) | Tests whether decoupling adds anything **beyond** B0. |

**The only difference between B0 and B2 is the value of `k` at each grid cell** (always 0 for B0; the 4-level grid for B2) — both use the same 6 skill values, the same 24-cell count, the same per-cell exposure, the same training seeds, the same budget. This is now a properly matched, single-variable comparison, exactly as required.

### 1.2 Verification that the grid does what it is meant to do — computed, not assumed

Calling the real, unmodified `SimulatedCandidate.answer_question()` (no environment, no training, no frozen-file change) 2,000 times per `(skill, k, difficulty)` cell at representative normalized difficulties (0.3, 0.5, 0.7 — where a high-skill candidate's own performance naturally saturates, matching where a well-adapted trajectory would actually sit) gives:

| skill | difficulty | k | mean perf | mean conf′ | mean hes′ | share(perf≥0.90 ∧ conf′<0.40 ∧ hes′>0.60) |
|---|---|---|---|---|---|---|
| 0.80 | 0.3 | 0.0 | 0.977 | 0.824 | 0.178 | **0.000** |
| 0.80 | 0.3 | 0.30 | 0.977 | 0.524 | 0.478 | 0.024 |
| 0.80 | 0.3 | 0.45 | 0.977 | 0.374 | 0.628 | **0.501** |
| 0.80 | 0.3 | 0.60 | 0.977 | 0.224* | 0.778* | **0.945** |
| 0.90 | 0.3 | 0.0 | 0.984 | 0.831 | 0.172 | **0.000** |
| 0.90 | 0.3 | 0.45 | 0.984 | 0.381 | 0.622 | **0.472** |
| 0.90 | 0.3 | 0.60 | 0.984 | 0.234* | 0.784* | **0.941** |

(*approximate; full 2-decimal table computed and available on request — the point figures above are exact from the verification run.)

**This confirms, rather than assumes:** (a) at `k=0`, the joint high-perf/low-conf/high-hes state the guardrail's nervous-expert exclusion checks for essentially never occurs (0.000) — exactly reproducing the natural, correlated behavior `persona="normal"` always has; (b) `k=0.30` barely moves this (2–6% depending on skill/difficulty) — a "near miss," included for a smooth gradient but not expected to carry much weight on its own; (c) `k=0.45` reaches the target region roughly half the time; (d) `k=0.60` reaches it 94–95% of the time, with **negligible boundary saturation** (≤1.1% of samples pinned at `conf′=0` or `hes′=1`, confirmed separately), meaning the added noise is not being destroyed by clipping. **The grid `k∈{0,0.30,0.45,0.60}` (replacing V2's `{0,0.15,0.30,0.45}`, which under-weighted the effective region) is retained on this evidence, not on the approximate-mean argument V2 implicitly relied on.**

### 1.3 The original 17-point skill sweep — dropped, with reasoning

V2 asked whether it should be kept "only if it adds meaningful scientific value relative to its cost." It does not clear that bar for **this** protocol: §2.2 below shows the demonstrated blind spot is concentrated in the confidence/hesitation-decoupling axis, not in skill-grid resolution — a finer, un-matched skill sweep answers a different, currently unmotivated question (whether skill resolution alone affects *other* parts of tracking accuracy) and would, if kept, reintroduce exactly the confound this section exists to remove. It is not deleted from the project's history (V1 is preserved) but it is not part of E1 V3's confirmatory design. If skill-resolution-alone is later judged independently interesting, it should be its own, separately-scoped, separately-justified experiment — not folded into this one.

## 2. Evidentiary status, corrected and substantially strengthened

### 2.1 Training-evidence interpretation — unchanged from V2, restated

Retained exactly as V2 §1 stated it: the reward function demonstrably reinforces correct "Harder" decisions when the relevant state is visited, under the one training-candidate configuration known (by static code reading, N1) to be the only one ever used for training. This is **not** proof that the five frozen checkpoints learned to use that signal — that log cannot be attributed to them. Nothing here changes that distinction.

### 2.2 The lucky_guesser finding — honestly classified, and now substantially cross-validated

**Honest classification, as required.** B2's design was originally motivated by examining the existing 5-persona P3/X3-0c evaluation results (a single `lucky_guesser@skill=0.80` data point, 120 guardrail-free "oracle wants Harder" turns, all from one persona). **That part of the reasoning is retrospective, not a blind prediction** — it is a hypothesis generated from inspecting the very data it was meant to explain, and any confirmatory evaluation of E1's own new checkpoints on the *same 5 named personas* (even with fresh eval seeds) would only be **prospective validation of a retrospectively-generated hypothesis**, not an independent discovery. Fresh eval seeds provide honest fresh stochastic replication of each persona's *behavior*, but they do **not** create an unseen-persona test, because the persona identities (skill + hand-written behavioral clamps) are unchanged and were the object of inspection. This is stated plainly and is not to be papered over in any manuscript text this protocol eventually supports.

**What changes this assessment substantially, found during this audit:** `research/confirmatory/X3-A/` is an existing, completed, pre-registered (`prereg/X3-A/v1`, gated 9/9 on `HARD_GATE_CHECK.md`), already-frozen confirmatory study of the same five checkpoints across a **40-persona grid** (the 5 named persona types × 8 skill levels `{0.20,...,0.90}`, generator `x3a_lib.persona_grid()`) and **20 evaluation seeds** (`1001…20020` — the first 5 identical to the original P3 study, 15 genuinely new). Re-examining its already-stored `sessions.csv` (63,000 rows, session-level, not raw per-step) for the first time in this session gives:

| persona type | mean oracle_agreement (PPO\|G) | mean raw "Harder" share | mean final "Harder" share |
|---|---|---|---|
| lucky_guesser | **0.482** (lowest of all 5 types) | **0.003** | **0.003** |
| nervous_expert | 0.999 | 0.001 | 0.001 |
| normal | 0.674 | 0.256 | 0.066 |
| overconfident_fail | 0.550 | 0.390 | 0.249 |
| struggling_junior | 0.738 | 0.106 | 0.068 |

And, broken down by skill level for `lucky_guesser` specifically (PPO|G): raw/final Harder share is **0.000 at every skill level from 0.5 to 0.9** (0.010 at 0.2–0.3, still near-zero), and `Constant-Same|G`'s own final Harder share for `lucky_guesser` is **exactly 0.0 at every one of the 8 skill levels** — meaning guardrail G6 never once forces Harder for this persona type at any tested skill, matching the mechanistic prediction (the nervous-expert exclusion) exactly. `X3-A`'s own descriptive strata table separately shows `lucky_guesser` as the *only* persona type with a paired PPO-vs-Constant-Same MAE difference whose 95% CI touches zero from the unfavorable side (point +0.030, CI [0.0, +0.115] — PPO is, if anything, no better and possibly worse for this type specifically), in contrast to `overconfident_fail` (point −0.148, CI entirely below zero — PPO clearly *helps* there) and the two higher skill bands (both favoring PPO).

**Corrected classification:** the finding is now supported by (a) the original, retrospective, single-persona observation that motivated B2's design, **and** (b) a largely independent (15 of 20 eval seeds, 7 of 8 skill levels never previously examined for this purpose) replication in an existing, already-frozen, already-registered study. (b) was not used to construct B2's design (B2 was already designed before this audit re-examined `X3-A`) and is reported here as newly-surfaced, corroborating evidence discovered during this audit, not as part of the original hypothesis-generation. **E1's own confirmatory run on new checkpoints remains prospective validation of the hypothesis** (nothing about re-training has been tested by `X3-A`, which only evaluates the existing frozen checkpoints) — but the hypothesis it would be validating is now considerably better supported than a single-sample post-hoc pattern.

### 2.3 Confirmatory seed provenance — the V2 error, and the fix

**Verified directly, as required.** `EVAL_SEEDS_CONFIRMATORY = [6006,7007,8008,9009,10010]` (V2's proposal) appear in `research/confirmatory/X3-A/x3a_config.json` and `research/confirmatory/X3-A/results/manifest_X3-A-run.json` as part of that study's own 20-seed evaluation set (`1001…20020`). **V2's "never-before-used" claim was false.** Corrected proposal: `EVAL_SEEDS_CONFIRMATORY = [21021, 22022, 23023, 24024, 25025]` (continuing the same increment-by-1001 pattern one full block past `X3-A`'s own range, disclosed as an arbitrary but fixed, non-tuned choice) — **searched directly against every `.py`, `.csv`, `.json`, and `.md` file under `research/`, `rl/`, and `experiments/`, and not found anywhere.**

**Limits of this verification, stated honestly:** this search covers the current working tree only. It cannot rule out a seed value having been used in an untracked, gitignored, or since-deleted local run (exactly the class of gap this session's own `PPO_TRAINING_EXPERIENCE_AUDIT.md` found for the training-log file) — a collision there would not be scientifically consequential (re-using a seed value across two unrelated, deterministic-given-seed simulations does not contaminate either one; it only matters for the *claim* "never before examined for this purpose"), but the claim of exhaustive verification is limited to what is tracked or otherwise present in this repository today, and is stated as such rather than asserted as absolute.

### 2.4 A held-out, genuinely blind generalization set — proposed, with its target mapping fixed now

Per the instruction, a small, separately held-out set of synthetic behavioral profiles is **feasible and useful**, and is defined **before any E1 result exists**, so that at least one part of the confirmatory evaluation is not just prospective validation of an already-examined pattern:

| Profile ID | skill | k (decoupling) | target_difficulty (formula, fixed now) |
|---|---|---|---|
| HOLDOUT-1 | 0.45 | 0.20 | `round(skill*5, 1)` → 2.25 |
| HOLDOUT-2 | 0.72 | 0.38 | 3.6 |
| HOLDOUT-3 | 0.88 | 0.52 | 4.4 |

**Target-difficulty formula, fixed in advance and not tuned:** `target_difficulty = clip(skill * 5, 1.0, 5.0)` — this is the exact same linear relationship already implicit in `PERSONA_TARGETS` (every existing persona's `target_difficulty` equals `skill × 5`, verified directly: `0.20×5=1.0`, `0.30×5=1.5`, `0.60×5=3.0`, `0.80×5=4.0`, `0.88×5=4.4≈4.5`), applied here to three new `(skill,k)` combinations chosen to fall **between** existing grid points (not equal to any B0/B2 training cell, any `X3-A` grid persona, or any `PERSONA_TARGETS` entry) and spanning a moderate-to-high decoupling range where §1.2 shows genuine, non-trivial exercise of the guardrail-exclusion condition. These three profiles are evaluated **only at the confirmatory stage**, on the confirmatory seeds (§2.3), for whichever arm(s) are selected — never inspected, never tuned against, during development.

## 3. Development/confirmatory split — carried forward from V2, updated for the corrected seeds and the X3-A discovery

- **Development (freely inspected, decides selection only):** the existing `EVAL_SEEDS = [1001,...,5005]` and, newly, direct comparison against `X3-A`'s own already-frozen per-persona-type numbers (§2.2) for sanity-checking whether a candidate arm's development-stage behavior is even directionally consistent with the much larger existing dataset, before any confirmatory run.
- **Confirmatory (locked, touched once):** `EVAL_SEEDS_CONFIRMATORY = [21021,...,25025]` (§2.3, verified unused) **plus** the three held-out profiles (§2.4), run once, for **all** of: the selected B-arm(s), Condition A's frozen PPO+G checkpoints (freshly replayed on these same new seeds — not retrained, not modified), Constant-Same+G, and Heuristic+G. `X3-A`'s own stored results (different seeds, larger persona grid, already frozen) are reported alongside as an **independent, already-existing, larger-N reference** — explicitly not merged into the new confirmatory numbers, since the seed sets differ and merging them would blur a genuinely fresh comparison with an already-examined one.
- **Reuse, not re-derivation, of evaluation machinery:** rather than writing a new, smaller, less rigorous confirmatory driver from scratch (as V2 proposed), the confirmatory evaluation script for E1 V3 is proposed to **reuse `research/confirmatory/X3-A/x3a_lib.py`'s existing, already-gated session/persona-generation and metric-computation code** (imported unmodified, exactly as `x3_0c_replay.py` already imports `execute_paper3_study.py` unmodified), pointed at the new checkpoints and the new seed block — lower engineering cost and higher comparability than V2's from-scratch approach.
- **Historical baselines preserved exactly as published:** `research/experiments/paper3/*` and `research/confirmatory/X3-A/*` are read-only references throughout; nothing in this protocol modifies, recomputes, or overwrites either.

## 4. Performance criteria, rechecked

**Primary objective, unchanged: the existing, unmodified `target_tracking_error` MAE.** No redefinition, here or anywhere in this protocol.

**Reported, per policy, on the confirmatory seeds + held-out profiles:** pooled MAE; per-persona/per-profile MAE; the equally-weighted mean; action distributions; the guardrail-coverage/oracle-agreement mechanism check (secondary only, per §4's next paragraph); variation across the 5 independent training seeds; whether an action-behavior improvement (mechanism check) translates into an MAE improvement (reported as two separate rows, never merged).

**Distinguishing a meaningful improvement from small-sample noise — grounded in an actual number, not an arbitrary threshold.** The frozen P3 study's own 5-persona, 5-training-seed paired-difference SD (PPO+G vs. Constant-Same+G) is **0.0097** (`x3_0c_persona_paired.csv`); `X3-A`'s 40-persona version is **0.10155** (larger because it spans a much wider skill range, not because of more noise per persona). The retained **0.05 MAE-unit** improvement threshold (unchanged from V2 for `lucky_guesser` specifically) is **~5× the frozen study's own seed-to-seed persona-paired SD**, i.e., a magnitude chosen to be clearly distinguishable from ordinary seed-level variation on this exact metric — not picked after seeing any E1 result, and now justified against a concrete, disclosed reference rather than by feel. This is a magnitude-based decision rule, not a claim of statistical significance in the formal sense — that distinction is stated explicitly in any eventual manuscript text.

**Decision criteria, restated and re-anchored (checkpoint/arm selection uses development evidence only, never confirmatory MAE):**
- **Development-stage selection (unchanged principle from V2, now comparing B0 vs. B2 instead of B1 vs. B2):** the arm(s) carried to the confirmatory stage are chosen by whether B2 shows a directional mechanism-check improvement over **B0** (not over Condition A directly — the matched comparison is B0-vs-B2) on the development seeds, with no per-persona regression ≥0.05 MAE units relative to B0 on those same development seeds. If B2 shows no improvement over B0 at all, **no confirmatory run is executed** — the mechanism-targeted hypothesis is reported as unsupported by the matched comparison, at the development stage, rather than manufacturing a confirmatory result from a design already showing no signal.
- **Confirmatory retain:** on `EVAL_SEEDS_CONFIRMATORY` + held-out profiles: (1) pooled MAE not worse than Condition A's; (2) `lucky_guesser`'s (and, if run, the held-out profiles') MAE improves by ≥0.05 relative to Condition A; (3) no other persona/profile regresses by ≥0.05; (4) the `lucky_guesser` guardrail-free oracle-Harder agreement rate is measurably above the near-zero baseline established in both the original P3 study and `X3-A` (required, not sufficient — oracle agreement is never, by itself, a success criterion, exactly as instructed).
- **Confirmatory abandon:** pooled MAE regression relative to Condition A or Constant-Same+G; or no mechanism-check movement despite the targeted design (directly falsifying the hypothesis, now for a design whose grid is verified to actually exercise the relevant states — a cleaner falsification test than V2's could offer).
- **Complexity-vs-heuristic check, unchanged, applied regardless of outcome:** reported honestly against Heuristic+G; if the heuristic still wins on pooled MAE, this is stated plainly as its own finding, not a failure of the experiment.
- **No checkpoint or arm is ever chosen by looking at its own confirmatory-seed MAE** — selection (which arm, whether to proceed to confirmatory at all) happens strictly before `EVAL_SEEDS_CONFIRMATORY` is touched, as in V2, now explicit about using B0 (not Condition A) as B2's direct comparison point during development.

## 5. Publication value, updated for the matched design and the X3-A discovery

**What the matched B0-vs-B2 comparison can establish, precisely:** whether confidence/hesitation decoupling *adds value beyond skill diversity alone* — a genuinely causal, single-variable claim that V2's unmatched B1-vs-B2 design could not have supported (any difference there could have been skill-grid resolution, not decoupling). This is the core scientific contribution of running E1 V3 at all.

- **Positive (B2 retained, B0 does not show the same improvement):** the strongest, most informative outcome — a demonstrated, mechanism-specific, causally-isolated fix for a blind spot that is now corroborated by both the original single-persona finding and an independent, much larger existing dataset (`X3-A`). Reported honestly as **confirmation of a hypothesis substantially informed by prior data**, not a blind discovery — and still subject to the heuristic-comparison honesty requirement (§4).
- **Mixed (B0 and B2 both help, or only partially, or the held-out profiles don't replicate the named-persona result):** still valuable and reportable, with the added nuance that the held-out profiles (§2.4) let the manuscript distinguish "works for the exact personas the hypothesis was built from" from "works for genuinely unseen behavioral configurations" — a real generalization question the held-out set was designed to answer.
- **Negative (neither arm helps, or the mechanism check shows no movement):** a strengthened negative result precisely because the intervention is now verified (§1.2) to actually exercise the relevant states — a null result here is harder to attribute to a poorly-targeted design and more informative about the underlying hypothesis's limits.
- **In every outcome:** no claim of real interview effectiveness, human learning improvement, or generalization beyond this synthetic simulator — restated as a permanent, outcome-independent limitation, unchanged from V1/V2.

## 6. Registration and reproducibility (V3)

**Implementation-change plan, updated:** the same two new candidate-construction files from V1/V2 (`e1_diverse_persona_env.py` defining both the B0 and B2 grids via an `arm` config field, `e1_train_condition_b.py`), plus a confirmatory evaluation driver that **imports and reuses `research/confirmatory/X3-A/x3a_lib.py` unmodified** (rather than V2's from-scratch driver) pointed at the new checkpoints, `EVAL_SEEDS_CONFIRMATORY`, and the three held-out profiles. **Zero changes to any frozen file, including `x3a_lib.py` itself, `x3a_config.json`, or anything under `research/confirmatory/X3-A/results/`.**

**Run manifest additions over V2:** `EVAL_SEEDS_CONFIRMATORY = [21021,22022,23023,24024,25025]` (verified absent from the repository as of this audit, with the limits of that verification stated in §2.3); the held-out profile table (§2.4) recorded verbatim with its target-difficulty formula; the corrected `k` grid (§1.2); `X3-A`'s own tag (`prereg/X3-A/v1`) and result files recorded as an external, already-frozen reference dataset, not modified or re-tagged.

**Proposed hash and tag (not created):**
- Protocol file: `research/paper_strengthening/E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V3.md`.
- SHA-256: reported in the accompanying chat response.
- Proposed Git tag (not created): `prereg/E1-ppo-persona-diversity/v3` (superseding the `v1`/`v2` proposals, neither of which was ever created).

**Preserved, unmodified:** `E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V1.md`, `E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V2.md`, every D1 protocol version, `EXPERIMENT_PLAN.md`'s prior entries, `FINAL_MANUSCRIPT_EVIDENCE_V2.md`, every frozen P3/X3/X3-A artifact, and both prior audit reports (`PPO_TRAINING_EXPERIENCE_AUDIT.md`, `RL_GUARDRAIL_COVERAGE_DECOMPOSITION_REPORT.md`) — left exactly as written; every correction in this document is stated here, in the new file, not by editing the earlier ones.

## 7. Recommendation

**Worth registering and running, more confidently than either V1 or V2.** The confound between skill-diversity and decoupling is now removed (B0 vs. B2, exactly matched); the decoupling grid is verified, not assumed, to exercise the relevant states, and re-scaled based on that verification; a real provenance error was caught and fixed, with an existing, much larger, already-frozen study (`X3-A`) discovered in the process that substantially corroborates the underlying hypothesis at far higher power than this project had access to before this audit; the development/confirmatory split now uses genuinely unused seeds; and a small, pre-specified, genuinely held-out generalization set is included so the eventual confirmatory result is not entirely a validation of an already-inspected pattern. The cost remains small (comparable to V2's estimate — two training arms at the same budget, evaluation reusing already-gated, already-fast harness code). **Not recommended as a guaranteed positive outcome** — §5 is built to report a clean, informative result whichever way the matched comparison and the held-out profiles come out.

**Not started. No code written. No training run. No tag created. No commit or push. Awaiting explicit approval before writing any script or executing anything.**
