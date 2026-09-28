# E1-Improve V2 — Extending the Deterministic PPO+Heuristic Gate (EXPLORATORY)

**Status: exploratory, development-only, bounded iteration. Not confirmatory.** Builds on `E1_IMPROVE_V1_REPORT.md` (SHA-256 `b9276887a67a5e7eaa3cc5977791037e6fe8a3fdcf92c8f7dec57198caf184ca`). Uses `EVAL_SEEDS_DEV = [1001,2002,3003,4004,5005]` only. No confirmatory seed or held-out profile is touched. No reward/state/action/evaluator/target-formula/guardrail-semantics change. No retraining. `x3a_lib.py` (SHA-256 `3badbb39dbf4974a53899ab013c9d0091f40aad718d34fc1b7502e6d4771e506`) and `rl/guardrails.py` (SHA-256 `c4198975227a03f9a672e982d0a3aa62ea60c41331c51ef55285410c409666ba`) are read-only dependencies, both re-verified unchanged since E1's own registration.

## 1. Guardrail enumeration (Task 1.2), read directly from `rl/guardrails.py::apply_canonical_guardrails` and cross-checked against `x3a_lib.py::shield` (verified byte-identical in logic; `x3a_lib.shield` omits only the `is_infrastructure_failure`/`consecutive_failures` parameters, both fixed at their default/false values in every E1 evaluation call)

Priority order, as coded (first match wins, strict early-return):

| Rule | Predicate (exact) | Action forced | Uses only pre-shield obs? |
|---|---|---|---|
| G0 (infra failure) | `is_infrastructure_failure == True` | Same | **No** — external system flag, not a function of `[perf,avg_perf,conf,hes,progress,difficulty]`; never set `True` anywhere in `x3a_lib.simulate`/`e1_simulate_adapter.simulate_diverse` (always default `False`). **Ineligible as a gate** — not observable and never active in this simulation harness. |
| G4 | `perf < 0.30 and hes > 0.60` | Easier | Yes |
| G1 | `perf < 0.30 and 0.4 <= diff_norm <= 0.7` | Easier | Yes |
| G2 | `conf < 0.30 and hes > 0.70 and perf < 0.80` | Same | Yes |
| G5 (aka "G3/G5" in the guardrails.py docstring — one rule, not two) | `0.40 < perf < 0.65 and avg_perf < 0.60` (`consecutive_failures < 2` always true here, fixed at 0) | Same | Yes |
| G6 | `perf >= 0.90 and gap > 0.25 and not nervous`, `gap = perf - diff_norm`, `nervous = (0.80<perf<0.95 and hes>0.65) or (conf<0.40 and hes>0.60)` | Harder | Yes |
| (none) | — | raw `proposed` action passed through unchanged | — |

## 2. Which clauses can safely serve as a deterministic MAE-changing gate (Task 1.3) — proved by direct code reading, before any new evaluation is run

**Theorem, verified against the literal `return` statements in `shield()`/`apply_canonical_guardrails()`:** for G4, G1, G2, G5, and G6 (using each rule's **own full firing predicate**), the shield's returned action is a **constant, independent of the `proposed` argument** whenever that rule's predicate is true (e.g. `if conf<0.30 and hes>0.70 and perf<0.80: return ACTION_SAME, True, "g2_..."` — the return does not reference `action` at all). **Consequence: gating the raw proposal (PPO vs. Heuristic) using any of these five rules' own full predicate as the trigger condition cannot change the final, post-shield action, and therefore cannot change `target_tracking_error`/MAE** — whichever raw proposal is substituted in, the shield overrides it identically. This is a **mechanical property of the frozen shield code**, not a new threshold or a tuned decision; it is stated here, predeclared, before running any new evaluation, and is then verified empirically in §5, not merely assumed.

**The one region where gating can matter** is a region where **no** guardrail fires, so the raw proposal survives the shield unmodified. E1-Improve V1's already-implemented gate (`e1improve_hybrid_gate.py`, unmodified, reused as-is) uses exactly such a region: G6's own `nervous` **sub-clause** `perf>=0.90 and conf<0.40 and hes>0.60` — the second disjunct of G6's exclusion condition — which is a region where **G6 itself does not fire** (because `not nervous` is `False` there) and, as separately checked, none of G4/G1/G2/G5 fire either (their perf ranges are disjoint from `perf>=0.90`). This is **not** one of the five "full predicate" gates being newly tested in this iteration; it is retained unchanged as the **control** condition, labeled `G6-nervous` throughout to distinguish it from the newly-tested `G6-full` gate (G6's complete three-part predicate, which — per the theorem above — is predicted to be a no-op).

## 3. Candidate gates, predeclared before any new result is inspected (Task 2.2, Task 5)

| Label | Trigger predicate (verbatim from `shield()`, no new threshold) | Predicted effect on final MAE |
|---|---|---|
| `none` | never | baseline (no gate) |
| `G6-nervous` (control, = existing V1 gate, unmodified) | `perf>=0.90 and conf<0.40 and hes>0.60` | Reproduces V1's reported result exactly (sanity check) |
| `G4-full` | `perf<0.30 and hes>0.60` | **Predicted no-op on final MAE** (shield-dominated) |
| `G1-full` | `perf<0.30 and 0.4<=diff_norm<=0.7` | **Predicted no-op on final MAE** |
| `G2-full` | `conf<0.30 and hes>0.70 and perf<0.80` | **Predicted no-op on final MAE** |
| `G5-full` | `0.40<perf<0.65 and avg_perf<0.60` | **Predicted no-op on final MAE** |
| `G6-full` | `perf>=0.90 and gap>0.25 and not nervous` | **Predicted no-op on final MAE** |
| `combo-all` | logical OR of `G6-nervous` and all five `-full` gates above | **Predicted identical final-MAE behavior to `G6-nervous` alone** (adding no-op-region triggers to an OR cannot change final actions) |
| `Heuristic+G` (standalone) | — | strongest existing deployable baseline (reference, unchanged) |

**Overlap rule (Task 3, "if gate conditions overlap, define deterministic order-independent behavior"):** `combo-all`'s gates are combined with a plain logical **OR** — if *any* enabled predicate is true for the current pre-shield state, the Heuristic's raw proposal is used instead of the wrapped policy's; otherwise the wrapped policy's raw proposal is used. Because this is a symmetric OR over independent boolean predicates (not a priority cascade), the result is identical regardless of the order the predicates are checked in — stated and implemented that way explicitly (`research/paper_strengthening/scripts/e1improve_v2_gates.py::make_gated_policy_v2`).

**No new threshold is introduced anywhere in this protocol.** Every predicate above is copied verbatim from `shield()`/`apply_canonical_guardrails()`.

## 4. Checkpoints evaluated (Task 3)

- Condition A — existing, frozen, deployed checkpoint (`research/experiments/paper3/checkpoints/seed_<s>/`, 5 seeds, unchanged).
- B2 @ 16,384 steps — `research/paper_strengthening/results/e1improve_checkpoint_trace/B2/seed_<s>/b2_seed<s>_16384_steps.zip` (5 seeds, from E1-Improve V1's checkpoint trace, unchanged, not retrained).
- B2 @ 24,576 steps — E1's original primary-budget checkpoint (`research/paper_strengthening/results/e1_training/B2/seed_<s>/`, 5 seeds, unchanged).
- B0 (primary) — included **only** for the `G6-nervous` control gate, to directly reproduce E1-Improve V1's already-reported `0.4389 → 0.4011` result as a harness-correctness check; not run against the five new individual gates or `combo-all` (out of the requested scope for this round).

## 5. Selection rule (Task 5), fixed before any new result is inspected

A new gate (or `combo-all`) is preferred over the existing `G6-nervous` control **only if, for at least 2 of the 3 primary checkpoints (Condition A, B2@16384, B2@24576)**: (a) its pooled dev MAE is strictly lower than `G6-nervous`'s on that checkpoint, **and** (b) it has **zero** per-cell regressions `>=0.05` relative to that checkpoint's fully-ungated baseline (the same threshold used throughout E1/E1-Improve). If no candidate satisfies both conditions, **the existing `G6-nervous` gate is retained unchanged as the deployed recommendation**, and this iteration is reported as not having improved on it — not reframed, not threshold-adjusted after the fact.

## 6. Reproducibility

Config: reuses `e1_config.json` unchanged (training seeds, dev eval seeds, skill/k grid). No new training. Environment lock: `LOCK-X3-2026-09-19`, already verified current. New files only: `e1improve_v2_gates.py`, `e1improve_v2_eval.py`, `tests/test_e1improve_v2_gates.py`. `e1improve_hybrid_gate.py` (V1) is imported, not modified, for the `G6-nervous` control.
