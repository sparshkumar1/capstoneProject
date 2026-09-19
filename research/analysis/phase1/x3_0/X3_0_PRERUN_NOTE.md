# X3-0 pre-run note (Phase 1, written before any X3-0 output was computed) - 2026-09-19

**Status.** Exploratory/descriptive accounting of an already-frozen study. Not a registered protocol; no confirmatory role. Authority: sprint instruction (Phase 1C) and `PHASE1_PREFLIGHT_DECISION_MEMO.md` sections 1, 5, 7. This note is hashed by the run manifests of X3-0a and X3-0c.

## Definitions (fixed here; taken from the frozen code, not chosen from results)
| Term | Definition | Source |
|---|---|---|
| Session | one call of `run_session_trajectory` = 10 turns (`max_steps=10`) for one (condition, persona, evaluation seed) | `execute_paper3_study.py:296-304` |
| Rule activation | a turn on which `apply_canonical_guardrails` returned `overridden=True` (a guardrail rule fired). The frozen field `guardrail_interventions` counts activations | `:397-409, :453` |
| Action override | a turn on which the final action differs from the raw proposed action (`raw_action != final_action`) | this note (the P0-4 correction) |
| Unchanged activation | an activation on which final action == raw action | this note |
| Attempted boundary action | a turn on which the executed action would take difficulty below 1.0 or above 5.0 (`next_diff < 1.0 or > 5.0`) before clipping. The frozen field `constraint_violations` counts these for the FINAL (executed) action | `:421-427` |
| Raw attempted boundary | the same test applied to the raw proposed action along the raw-action trajectory (guardrails off) | this note |
| Volatility, oscillation, tracking MAE | as in the frozen script (`:430-452`) | frozen |
| SD | both population (ddof=0) and sample (ddof=1) are reported; the frozen summary's `0.186 +/- 0.068` is checked against both | this note |

## X3-0a (stored files only)
Inputs (read-only, hashed before/after): `paper3_seed_results.csv`, `paper3_summary_results.csv`, `paper3_baseline_results.csv`, `paper3_ablation_results.csv`, `paper3_guardrail_results.csv`, `paper3_sensitivity_results.csv`, `paper3_convergence_results.csv`, `paper3_training_curves.csv`. Outputs: per-seed table and totals (563 / 232), spread and SD conventions, corrected ablation-row provenance (E-10/E-11), seed-123 and historical-mismatch activations vs overrides by rule / persona / direction, stored-probe sensitivity summary, stored training-time action shares. No RNG. All numbers script-written; assertions against the registry values. Any recomputed value that differs from the stored value stops the run (reported as a discrepancy, not repaired).

## X3-0b (static code)
A dated note stating what the frozen training loops used, with file:line references (`X3_0B_STATIC_CODE_NOTE.md`).

## X3-0c (replay; only after the gate)
Evaluation-only replay of the frozen five checkpoints with `run_session_trajectory` (imported, `main` never called). **Gate G-REPRO (must pass before any G-NEW value is computed or registered):** guarded attempted-boundary counts per training seed = 26 / 71 / 41 / 33 / 61 and guarded activation counts = 122 / 101 / 115 / 120 / 105, plus the seed-123 activation-by-rule counts of the stored guardrail file. If the gate fails: nothing is registered; the mismatch is preserved and reported. G-NEW values: raw attempted boundary total (audit value 136), overrides (audit value 99), unchanged activations, sessions with an attempt, Constant-Same + guardrails MAE (audit value about 0.673), per-persona MAE, per-turn logs. Constant-Same is implemented only by replacing the checkpoint's `predict` with a constant-action stub, leaving every other line of the frozen loop untouched. Environment: separately built and documented environment (`envs/replay-Lobs`), not the project `.venv`.

## Non-leakage statements
1. No X3-0 output changes delta = 0.12, m = 0.20, the outcome classification, the X3-B trigger, or any X3-A/X3-B design choice. X3-0c per-persona SD is used **only** for the X3-A precision (sample-size) rationale and is disclosed as such.
2. X3-0 results are seen before X3-A is tagged; the X3-B "method-level claim" decision is therefore **not blind**; disclosed per PREREGISTRATION_SPEC B.1.
3. No PPO training, no hyperparameter change, no reward change, no new persona, no threshold change.
