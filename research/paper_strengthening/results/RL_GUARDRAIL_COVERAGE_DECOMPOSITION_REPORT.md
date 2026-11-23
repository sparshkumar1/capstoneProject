# Guardrail-Coverage Decomposition of the Frozen P3 Replay (Item D)

**Status: read-only diagnostic reanalysis. No code changed, no simulation run, no model called, no new data generated, no retraining, nothing committed/tagged/pushed.** All numbers below are computed by `research/paper_strengthening/scripts/rl_guardrail_coverage_decomposition.py` from the already-frozen, already-gated replay artifact `research/analysis/phase1/x3_0/x3_0c_replay_turn_log.csv` (itself a G-REPRO-passed replay of the frozen `research/scripts/execute_paper3_study.py` on the frozen checkpoints in `research/experiments/paper3/checkpoints/`), plus two pure functions imported unmodified from the live code (`rl.guardrails.apply_canonical_guardrails`, `rl.env.interview_env.InterviewEnv.oracle_action_from_obs`). Full numeric output: `rl_guardrail_coverage_decomposition.json` (same directory).

## 1. Schema, verified directly from the frozen code (not assumed)

Read `research/scripts/execute_paper3_study.py::run_session_trajectory` line by line. Key facts, all confirmed:

- **The frozen evaluation script has no "oracle" concept.** It computes exactly: `raw_action` (PPO's/Heuristic's/Fixed's proposal) → `apply_canonical_guardrails()` → `final_action`. `oracle_action_from_obs` exists only in `rl/env/interview_env.py`, the **training** environment, where it shapes PPO's reward (`decision_component`). Every `oracle_action` value in this report is **recomputed** by this script from the already-stored per-turn state — a deterministic function application to frozen numbers, not a new column that was ever logged by the original study.
- **No lag.** The decision recorded for "turn t" in the CSV is computed from **that same turn's own** `(perf, avg_perf, conf, hes, progress, difficulty_before)` — the candidate answers at `difficulty_before`, and the very same loop iteration uses that answer's outcome to decide the action for the *next* question. There is no one-turn lag between the state a row records and the decision a row records (this differs from `rl/env/interview_env.py`'s own `step()`, which decides from `prev_obs`; the two files are different environments for different purposes, a distinction the project's own `rl_state_definition.md` already flags at a different level).
- `avg_perf` = rolling mean of the **last ≤5 perf values including the current turn**; `progress` = `turn / 10` (the replay used `dim4_mode="aligned_progress"` throughout); normalized difficulty = `difficulty_before / 5.0`.
- **Fidelity check (not assumed, verified):** recomputing `apply_canonical_guardrails()` from this script's own reconstructed `avg_perf`/`progress`/`diff_norm`, restricted to the 1,500 rows where the original script actually invoked guardrails (`PPO+G`: 1,250 rows; `Constant-Same+G`: 250 rows) — **0 mismatches in `final_action`, 0 mismatches in `guardrail_id`** across all 1,500 rows. This confirms the state reconstruction used for every number below is bit-exact against the frozen code's own recorded output, not merely assumed correct.
- **Data-integrity check against the already-published `X3_0C_REPORT.md`:** independently re-aggregating straight from the turn-level rows (not copying the stored summary) reproduces **563 rule activations, 99 overrides, 464 unchanged activations, 41/125 sessions with ≥1 override** — exact match on all four figures.

## 2. Totals

- **125 sessions, 1,250 turns** for `PPO+G` (5 training seeds × 5 personas × 5 eval seeds × 10 turns). Same totals for `PPO raw`. **350 sessions, 3,500 turns** across all 14 condition/seed groups in the file.
- Personas (5): `lucky_guesser`, `nervous_expert`, `normal`, `overconfident_fail`, `struggling_junior`. Eval seeds: `1001, 2002, 3003, 4004, 5005`. Training seeds: `42, 123, 456, 789, 999`.

## 3. Guardrail coverage, PPO+G (1,250 turns)

| Rule | Activations | Overrides | Override share |
|---|---|---|---|
| g5_partial_same | 205 | 0 | **0.0%** |
| g4_stuck_easier | 167 | 15 | 9.0% |
| g1_overload_protection | 111 | 49 | 44.1% |
| g2_anxiety_stabilizer_same | 80 | 35 | 43.8% |
| g6_strong_harder | **0** | — | — |
| **Total** | **563** | **99** | **17.6%** |

- **Overall coverage (any guardrail fires): 45.04%** of turns.
- **Overall override rate given activation: 17.6%** (matches the already-published seed-123-only figure of ~11.9% is *not* the same population — that was seed 123 alone; pooled across 5 seeds it's 17.6%). Of all 1,250 turns, only **7.9%** are actually changed by a guardrail — coverage and override are very different quantities and must be reported separately.
- **g6 ("strong performer → harder") never fires once**, in any of the 1,250 turns. The guardrail layer, as exercised by this persona/checkpoint combination, is entirely one-directional: it eases or holds, and never pushes harder.
- **g5 never overrides anything (0/205).** Whenever g5's precondition holds (`0.40 < perf < 0.65` and `avg_perf < 0.60`), PPO's own raw proposal was already "Same" in every single instance. This guardrail is active but functionally non-binding for this checkpoint.
- **Precondition overlap** (how often more than one rule's *precondition* is simultaneously true, even though only the first-priority one ever fires): 0 preconditions true in 687 turns, exactly 1 in 423, exactly 2 in 85, exactly 3 in 55. The three-way overlap is always `g1+g2+g4` (55 turns) — i.e., whenever the "overload" and "stuck" conditions co-occur, the "anxiety" condition is present too; `g2+g5` co-occurs 45 times and `g2+g4` 40 times. No overlap combination involving `g6` was ever observed (consistent with g6 never firing).

## 4. Guardrail-free states (687 of 1,250 turns, 54.96%)

- **Oracle action distribution in these states:** Same 56.0% (385), Easier 26.5% (182), Harder 17.5% (120). **Oracle wants a non-trivial (non-"Same") action 44.0% of the time** in guardrail-free states.
- **PPO's own raw proposal in these same states:** Same 72.8% (500), Easier 17.5% (120), Harder 9.8% (67).
- **Oracle and PPO's raw proposal agree 72.3% of the time** in guardrail-free states; they disagree in **190 of 687 turns (27.7% of free turns, 15.2% of all PPO+G turns).**

### The sharpest single finding: PPO never proposes "Harder" when the oracle wants "Harder"
The oracle-vs-PPO-raw confusion matrix in guardrail-free states is exact and complete:

| Oracle wants ↓ / PPO proposes → | Easier | Harder | Same |
|---|---|---|---|
| **Easier** (182) | 117 | 65 | 0 |
| **Harder** (120) | 0 | **0** | **120** |
| **Same** (385) | 3 | 2 | 380 |

- **Every one of the 120 turns where the oracle wants "Harder," PPO proposes "Same" instead — 0 exceptions.**
- **Every one of PPO's 67 "Harder" proposals in guardrail-free states occurs when the oracle wanted something else** (65 times the oracle actually wanted "Easier" — a directionally opposite call; 2 times the oracle wanted "Same"). PPO's raw policy, in this data, **never once proposes "Harder" in a state where the reward's own oracle target is "Harder."**
- When the oracle wants "Same" (the largest bucket), PPO agrees 380/385 times (98.7%) — strong, near-total agreement on the trivial case.
- When the oracle wants "Easier," PPO agrees 117/182 times (64.3%) and proposes the wrong direction ("Harder") 65/182 times (35.7%).

## 5. Variation across training seeds and personas

**Training seeds** (pooled across personas) are fairly homogeneous: coverage 40.4%–48.8%, override rate 4.8%–14.8% — ordinary run-to-run PPO training variance, no seed is qualitatively different from the others.

**Personas are dramatically heterogeneous** — this is not a small effect:

| Persona | Coverage | Free share | Override rate | Oracle non-trivial share (in free states) |
|---|---|---|---|---|
| normal | **100.0%** | 0.0% | 0.0% | n/a (no free turns) |
| struggling_junior | 80.8% | 19.2% | 20.0% | **89.6%** |
| overconfident_fail | 44.4% | 55.6% | 19.6% | **100.0%** |
| lucky_guesser | 0.0% | **100.0%** | 0.0% | 48.0% |
| nervous_expert | 0.0% | **100.0%** | 0.0% | **0.0%** |

- **`normal` is guardrail-covered on literally every single turn** (all 250), yet its override rate is exactly 0% — the guardrail fires (almost certainly `g5_partial_same`, matching a persona designed to sit in a mid-range, partially-understood band) but never needs to change anything, because PPO's own proposal already matches it every time. For this persona, "100% guardrail coverage" does not mean "PPO's choices are irrelevant" — it means PPO already agrees with what the guardrail would force, always.
- **`nervous_expert` and `lucky_guesser` are never guardrail-covered at all** (0/250 each) — every turn is nominally "free" for PPO to influence — but `nervous_expert`'s oracle wants a non-trivial action **0% of the time**: for this persona there is no reward-designated opportunity for PPO to exploit even though nothing is blocking it.
- **`struggling_junior`** is where real, populated opportunity concentrates: guardrail-covered 80.8% of the time, but in its remaining 19.2% free turns, the oracle wants a non-trivial action 89.6% of the time — the single persona combining meaningful free turns with a strong reward-designated reason to act differently from "Same."
- **`overconfident_fail`**: guardrail-free 55.6% of turns, and in every one of those free turns the oracle wants a non-trivial action (100%) — the other persona with concentrated, populated opportunity.

A single pooled figure ("55% of turns are guardrail-free") hides this. The real structure is: two of five personas contribute essentially all of the "free, reward-designated opportunity" turns; one persona has zero opportunity because it is fully guardrail-covered; two personas have unlimited freedom but one of them has literally nothing for a learned policy to exploit.

## 6. What this demonstrates vs. what remains a hypothesis

**Demonstrated, directly, from the data:**
1. The reward's oracle-imitation term and the deployment guardrail rule table overlap heavily in their *preconditions* (both keyed on similar perf/conf/hes/difficulty regions), and this overlap is not merely structural-on-paper: **g5's 0% override rate is empirical confirmation** that in the partial-understanding regime, PPO's learned behavior and the guardrail-enforced behavior already coincide in every observed instance.
2. **PPO's raw policy has a real, systematic, direction-specific blind spot**: it never proposes "Harder" when the reward's own oracle target is "Harder," in any of the 120 guardrail-free instances where that target occurs — and every "Harder" proposal it does make is misaligned with the oracle. This is a demonstrated property of the evaluated checkpoints on this data, not a hypothesis.
3. **Guardrail coverage and guardrail override are not the same thing**, and conflating them (as a single "coverage" percentage would) hides that one persona (`normal`) is 100%-covered but 0%-overridden, while another (`nervous_expert`) is 0%-covered but has zero reward-designated reason to differ from "Same" anyway.
4. **Opportunity is concentrated in 2 of 5 personas** (`struggling_junior`, `overconfident_fail`), not spread evenly.

**Remains a hypothesis, explicitly not proven here:**
1. That this overlap/blind-spot mechanism is the **complete** explanation for PPO+G's statistical indistinguishability from Constant-Same+G on MAE. It is a plausible, partial, quantified contributor — not a proof of sufficiency. The null MAE result could also partly reflect that, for this small ±1-level action space over only 10 turns, "Same" is already close to locally optimal regardless of any guardrail/oracle interaction.
2. **The 44.0% "oracle wants non-trivial" figure (or the 27.7%/15.2% disagreement figures) is *not* an upper bound on achievable MAE improvement**, for two independent reasons, both requested to be stated explicitly: (a) **agreement with the oracle is not the evaluation metric** — the oracle is itself an unvalidated, hand-authored heuristic, not a proven-optimal target for the MAE objective, so a policy that agreed with it 100% of the time is not guaranteed to have lower MAE, and a policy that disagreed with it could in principle do better; (b) **these figures are not policy-invariant.** They describe the state distribution actually visited by *this* checkpoint's *actual* trajectory. Because `SimulatedCandidate`'s performance is a sigmoid function of `(skill − difficulty)`, every action taken changes the difficulty of the *next* question and therefore the candidate's *next* performance — a different (improved) policy would visit a materially different empirical mix of guardrail-covered/free states and a different oracle-agreement rate, for reasons having nothing to do with whether the new policy is "better." This decomposition characterizes the currently-evaluated policy's own trajectory; it is a diagnostic, not a ceiling.

## 7. Is further PPO development justified?

**A qualified, evidence-scaled yes — but for a narrow, specific hypothesis, not a general "retrain and see" attempt, and with modest expected effect size.**

- The **absolute size of the demonstrated opportunity is small and concentrated**: only 190 of 1,250 turns (15.2%) show a guardrail-free oracle/PPO disagreement, and of the two personas where this concentrates, one (`struggling_junior`) has only 48 free turns total (19.2% of 250) to work with. This is not "PPO is barely constrained and a small tweak will unlock a large gain" — it is "there is a specific, demonstrated, narrow direction-of-error (a total absence of correctly-targeted 'Harder' proposals) worth testing a fix for."
- The **specific, falsifiable hypothesis worth testing** (already named as Item E in `SYSTEM_IMPROVEMENT_PLAN.md`, now sharpened by this data): does concentrating/reweighting the reward's decision-component signal on guardrail-free states — and specifically checking whether the reward or state representation is starving the "push harder" direction of usable gradient (e.g., because g6's precondition, and hence any positive reinforcement for a correct "Harder" call under guardrails, is *never* triggered in training either) — produce a policy that at least closes the demonstrated "Harder" blind spot, evaluated first on **development-only** persona/seed variants, never on the confirmatory set used for any eventual reported comparison.
- **What would NOT be justified:** a general, unfocused PPO retrain hoping for an overall MAE win. The heterogeneity in §5 means a pooled retrain could easily "fix" `struggling_junior`/`overconfident_fail` while doing nothing (or worse) for `normal`/`nervous_expert`/`lucky_guesser`, and MAE is measured pooled — a persona-level, not just pooled, evaluation is required for any retrain to be honestly assessed.
- **Cost/effort:** consistent with the original Item E estimate (medium-high; new reward variant, a genuine development/confirmatory persona-seed split, multi-seed retraining) — this decomposition does not change that estimate, but it does change *what specifically to try first* (targeting the demonstrated "Harder" blind spot and the two opportunity-concentrated personas, rather than an undirected reward reweighting).

## 8. Exact numerical findings and provenance

All numbers in this report are reproduced in full, machine-readable form in `research/paper_strengthening/results/rl_guardrail_coverage_decomposition.json`, generated by `research/paper_strengthening/scripts/rl_guardrail_coverage_decomposition.py`, reading only:
- `research/analysis/phase1/x3_0/x3_0c_replay_turn_log.csv` (frozen, read-only)
- `rl/guardrails.py` (`apply_canonical_guardrails`, imported unmodified)
- `rl/env/interview_env.py` (`InterviewEnv.oracle_action_from_obs`, imported unmodified)

No frozen artifact was modified. No simulation was run. No model was called. No new data was generated. Nothing was committed, tagged, or pushed.

## 9. What the manuscript can safely claim from this

- The exact coverage/override/persona-heterogeneity numbers in §3–5, cited to this report and script.
- The demonstrated "Harder" blind spot (§4/§6.2) as a specific, verified property of the evaluated PPO+G checkpoints — a stronger, more precise claim than "PPO doesn't help."
- The overlap between the reward's oracle term and the guardrail rule table (§6.1) as a **plausible, partial, quantified contributor** to the null MAE result — explicitly not as a proven complete explanation.
- The persona-heterogeneity finding (§5) as evidence that any future retraining attempt must be evaluated per-persona, not only pooled.

**What it cannot claim:** that the guardrail-free/oracle-disagreement percentages bound how much PPO could improve (§6, second point) — this would overreach the same way V11/V12's IUT bound overreached before correction, and must not be repeated here.

## 10. Single highest-impact next action

**Do not retrain PPO yet.** The next highest-value, still-cheap, still-read-only step is to **check whether g6's precondition (`perf ≥ 0.90 AND gap > 0.25 AND not nervous_expert`) is ever satisfied during PPO's own *training* rollouts** (not just this evaluation replay) — if it is rarely or never satisfied in training either, that would explain, mechanistically, *why* PPO never learns to propose "Harder" correctly (it may never have received a single positive training signal for doing so), which would turn §6.1's "plausible, partial" mechanism into a much more directly demonstrated one, and would sharpen Item E's retraining hypothesis from "reweight the reward" to a specific, testable claim about training data coverage — before spending any compute on an actual retrain.
