# P0-3 — Paper 3 "0 violations / eliminates 100 % of out-of-bounds transitions"

Forensic pass, 2026-09-19. No frozen result was modified; no training was run. Numbers marked *(replay)* come from replaying the frozen evaluation code with the frozen checkpoints (scratchpad only); numbers marked *(frozen)* are read directly from frozen files.

## 0. Bottom line

1. **Verified from code:** difficulty is clamped by the simulator for *every* policy, so "0 actual out-of-bounds transitions" is **guaranteed by construction and carries no information about PPO or the guardrails.**
2. **The frozen results themselves contradict the "0 violations" headline.** The violation counter in the frozen code counts *attempted* out-of-range actions before clamping. The correctly computed counter for PPO+guardrails is **232** over 5 seeds *(frozen: `paper3_seed_results.csv`)*, not 0. The "0" in the summary table, the report and the handoff is **hard-coded** in the script.
3. **The guardrails do not reduce attempted out-of-range actions; they increase them** (raw PPO 136 → guarded 232 over 1,250 turns each *(replay)*), because the rules are boundary-unaware.
4. **"0 violations" is not a meaningful safety metric.** Report attempted-boundary-action counts/rates (separately for the raw and the final action), the activation/override measures from P0-4, and do not present the clamp invariant as a result.

## 1. Code verification

| Fact | Location |
|---|---|
| Difficulty transition: `next_diff = current_difficulty ± 1.0`; `constraint_violations += 1` if `next_diff < 1.0 or next_diff > 5.0` (checked **before** clipping); then `current_difficulty = float(np.clip(next_diff, 1.0, 5.0))` | `research/scripts/execute_paper3_study.py:421-427` |
| The counter therefore counts **attempted** out-of-range moves of the *final* (post-guardrail) action. The post-clip state can never leave [1, 5], whatever the policy | same, lines 425-427 |
| `apply_canonical_guardrails()` contains no boundary logic. Its docstring lists "Boundary Clamp: difficulty remains strictly within [1, 5]" but the function body has no such rule (G4, G1, G2, G5, G6 only). G4 returns "Easier" whenever `perf < 0.30 and hes > 0.60`, regardless of the current difficulty | `rl/guardrails.py:1-15` (docstring) vs `:57-101` (code) |
| The same clamp exists independently in every consumer of the action: orchestrator `max(1, …)` / `min(5, …)` | `agents/orchestrator/interview_orchestrator.py:1530-1531, 1560-1561`; `agents/strategy/hybrid_orchestrator.py:244-246`; training env `rl/env/interview_env.py:402-404` |
| Hard-coded zeros in the summary tables: `"constraint_violations": 0` for "PPO + Guardrails (Aligned, Seed 123)" and for the 5-seed row; and `"constraint_violations": 0` in the ablation "PPO + Guardrails (5 Seeds)" row. (The "PPO Raw" row uses the real count, 60.) | `execute_paper3_study.py:886`, `:895`, `:774` |

## 2. What the frozen files actually say

| File | PPO+guardrails violations |
|---|---|
| `paper3_seed_results.csv` (per training seed 42/123/456/789/999) | **26 / 71 / 41 / 33 / 61 = 232** |
| `paper3_baseline_results.csv`, "PPO+Guardrails (Seed 123)" | **71** (real count) |
| `paper3_baseline_results.csv`, "PPO Raw (Seed 123)" | 60 |
| `paper3_summary_results.csv`, `PAPER3_FINAL_REPORT.md`, `PAPER3_FINAL_FREEZE.md`, handoff docs | **0** (hard-coded) |

So the frozen results contain both the real count and the contradictory "0"; the report and handoff used the latter.

## 3. The three separate quantities (replay of the frozen checkpoints, 125 guarded sessions × 10 turns = 1,250 turns per condition)

| Quantity | Raw PPO (no guardrails) | PPO + guardrails | Notes |
|---|---|---|---|
| **Attempted out-of-range action** (pre-clip; the frozen "constraint_violations") | **136** turns (10.9 %); 21 / 125 sessions | **232** turns (18.6 %); 39 / 125 sessions | all 232 and all 136 are attempts to go **below difficulty 1** ("Easier" at the floor); **0** attempts above 5 for PPO |
| Per-seed attempts (42 / 123 / 456 / 789 / 999) | 0 / 60 / 2 / 40 / 34 | 26 / 71 / 41 / 33 / 61 | guardrails increased attempts in 4 of 5 seeds |
| **Actual post-clip difficulty range** | [1, 3] | [1, 3] | always inside [1, 5] — by clamp, for every policy (see §4) |
| **Guardrail rule activations** | 0 | 563 (45.0 %) | see P0-4 |
| Origin of the 232 guarded attempts | — | 112 produced by rule G4 ("stuck → Easier") at the floor; 120 by PPO's own "Easier" on turns where no rule fired | struggling_junior 154, overconfident_fail 78 |

Interpretation of an attempt: in this simulator an "Easier" issued at difficulty 1 is a **no-op**. For the personas concerned (targets 1.0 and 1.5) it is often the *desired* behaviour. These are saturated proposals, not harms, so calling them "violations" is misleading in both directions (it is neither "0" nor a safety failure).

## 4. Is "0 violations" meaningful? No.

Control diagnostics *(replay, audit only)* run through the same code:

| Policy | Attempted out-of-range | Post-clip range |
|---|---|---|
| Fixed / constant "Same" | 0 | [3, 3] |
| Constant "Easier", **no guardrails** | 200 (all below) | [1, 3] |
| Constant "Harder", **no guardrails** | 200 (all above) | [3, 5] |
| Random actions, no guardrails (20 draws, mean) | 22 | inside [1, 5] |
| Raw PPO (5 seeds) | 136 | [1, 3] |

A constant "Harder" policy with no safety mechanism at all also has **zero actual out-of-bounds states**. The statement "0 actual out-of-bounds transitions" therefore holds for every policy in the study and cannot be credited to the guardrails or to PPO.
The phrase "eliminate 100 % of out-of-bounds difficulty transitions" (`research/CLAUDE_HANDOFF/PAPER3_FINAL_FREEZE.md:109` recommended wording; `research/CLAUDE_HANDOFF/PAPER3_FINAL_REPORT.md:35` methodological note) is **false as a causal statement**: the guardrails eliminated nothing (attempts went up), and the simulator's clamp would give 0 either way.

## 5. What can be reported (scientifically correct, all from existing data)

Report these as **separate, named measures**:

1. **Boundary-saturated action rate** (attempted out-of-range proposals, pre-clamp): 136 / 1,250 turns (10.9 %) for raw PPO; 232 / 1,250 (18.6 %) for the final action under guardrails; 21 vs 39 of 125 sessions; all at the floor; per-seed values in §3. State that they are no-ops handled by the simulator clamp.
2. **Guardrail activations and action overrides** (P0-4): 563 activations (45.0 %); 99 action changes (7.9 %).
3. **Post-clip difficulty range:** state as an *implementation invariant* ("the environment clamps difficulty to [1, 5]"), not as a result and not as evidence for the safety shield.
4. **Pedagogical-rule conformance (optional, with a stated tautology):** the guarded policy conforms to G1–G6 by construction; the informative number is how often raw PPO's proposal *contradicted* a rule (99 turns; of these, 39 proposed "Harder" against a rule that held or lowered difficulty). This is path-dependent (computed along the guarded trajectories) and per-turn candidate states are not stored, so a counterfactual on raw trajectories is not available.

If a genuine safety claim about *learner harm* is desired, it needs an independent criterion (for example, escalation to "Harder" after a stuck/failed turn judged by a rule that is not the shield's own) and, ultimately, human-in-the-loop evidence. It cannot be made from the clamp.

## 6. What must not be claimed

- "0 constraint violations" / "zero out-of-bounds" as a *result*, or "eliminates 100 % of out-of-bounds transitions".
- "Guardrails maintain boundary enforcement" — the guardrail module has no boundary logic; the environment does.
- The docstring's "Boundary Clamp" as a description of `guardrails.py` behaviour.

## 7. Fixes (recommendations only — USER DECISION REQUIRED; nothing was changed)

1. Errata/addendum file superseding the "0" entries with the real counts (232 / 71 / 136) and renaming the counter "attempted out-of-range actions (saturated proposals)". Do not edit the frozen files.
2. Optional code change (not authorised): make the guardrail module either implement or stop advertising a boundary rule; make the counter name explicit.
3. Rerun required? **No** — every needed number already exists in frozen files or the replay. Only the report/manuscript claims need correction.

## 8. Classification

`CONFIRMED` (claim is false as stated) + `ANALYSIS_ERROR` (hard-coded 0 overriding computed 232; attempts mislabelled as violations) + `DOCUMENTATION_ERROR` (guardrail docstring advertises an unimplemented boundary clamp).

## 9. Limits

- The attempted-action breakdown by producing rule uses the stored per-turn `guardrail_ids`; the replay reproduced the per-seed frozen counts exactly (26/71/41/33/61).
- Per-turn perf/conf/hes are not stored in frozen outputs, so counterfactual analyses along the raw-PPO path were not attempted.
