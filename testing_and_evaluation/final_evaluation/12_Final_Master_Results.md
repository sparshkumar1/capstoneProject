# Final Master Results — Final Evaluation Phase (consolidated pointer)

This document consolidates this phase's results into one place without restating or duplicating `testing_and_evaluation/Master_Results_Table.md` §1–8 (the Phase 2/3 baseline, preserved unmodified) or §9 (this phase's own append). It exists because the final evaluation phase instructions asked for one definitive "final master results" document; it is a synthesis layer, not a new source of numbers — every figure below traces to one of the 14 documents in this directory or to `Master_Results_Table.md`.

## 1. Code changes (3, all on `final-eval/controlled-improvements`)

| # | File(s) | Bug | Fix | Evidence |
|---|---|---|---|---|
| 1 | `services/qwen/app.py` | LLM-emitted JSON string fields iterated character-by-character instead of wrapped as single-item lists (7 call sites) | `_as_str_list()` helper, type-checked coercion | Live before/after against the real model; unit test 5/5 |
| 2 | `apps/backend/main.py`, `services/storage/database.py` | Admin dashboard only showed in-memory sessions; lost on restart | New read-only `list_sessions()` + merge-with-live-sessions logic | 27 historical sessions recovered, verified via isolated process call + raw SQL |
| 3 | `rl/env/interview_env.py` | Dormant guardrail-fallback path still used the pre-fix G5 boundary (`0.40<perf`), inconsistent with `rl/guardrails.py`'s already-fixed `0.30<=perf` | Synced boundary to match | 5/5 new boundary cases pass post-fix (0/5 before, as expected) |

## 2. Regression status

**264 passed / 19 failed / 15 skipped, both before and after all 3 changes** (full detail and per-test attribution: `03_Test_Execution_Summary.md`). Frontend: 28/28, both times. **Zero regressions.**

## 3. Numeric reconciliations (no errors found, both pairs confirmed as distinct, correctly-used quantities)

| Pair | Resolution |
|---|---|
| ρ=0.4825 (`derived_ce`, X2-B) vs ρ=0.4832 (`R only`, Paper-2 ablation) | Different scorers (X2-B's own re-derived CrossEncoder-only pipeline vs. the frozen Paper-2 ablation's R-only condition) — not the same number, no error |
| ρ=0.4897 (`length_only`, X2-B) vs ρ=0.4884 (`S1+R`, Paper-2 ablation) | Different conditions entirely (a length-bias control vs. a composite-weight ablation) — not the same number, no error |

Full detail: `05_ML_Evaluation_Results.md` §2.

## 4. PPO checkpoint identity

Deployed (`rl/checkpoints/seed_123/ppo_final.zip`, hash `2ab8d5...`) and evaluated (`research/experiments/paper3/checkpoints/seed_123/ppo_final.zip`, hash `299437...`) are **confirmed genuinely distinct files**, not a mislabeling or swap. Neither was modified. Full detail: `06_RL_Evaluation_Results.md` §2.

## 5. PPO behavior finding (unchanged this phase)

The pre-registered `X3A-C001` confirmatory result stands: PPO+Guardrails is not statistically distinguishable from a constant-action-plus-guardrails baseline under the pre-specified δ=0.12 MAE margin. This phase adds root-cause analysis (reward structure favors "Same") and a fully specified, unexecuted alternative-reward protocol (`11_Experiment_Provenance_Register.md` §3) — it does **not** add new training evidence.

## 6. Qwen narrative-quality findings (new this phase)

- Hint and report generation confirmed template-only (not LLM) — corrects an implicit assumption in prior deliverables.
- Feedback-generation JSON-corruption bug found and fixed (item #1 above).
- Two residual quality limitations documented, not fixed this phase: a factually-confused corrective explanation in one real sample, and hallucinated structured-field content (echoing score metadata as a "missing concept") in another. Full detail: `07_Qwen_Feedback_Quality_Evaluation.md`.

## 7. Repository organization (Phase 3)

2 new README files added (`testing_and_evaluation/scripts/README.md`, `testing_output/README.md`); **zero files moved, renamed, or deleted**. Full detail: `Repository_Structure_Audit.md`, `Repository_Organization_Changes.md`.

## 8. Where to look for everything else

| Topic | Document |
|---|---|
| Full testing-artifact classification | `final_review/Initial_Testing_Audit.md` |
| Code-change before/after detail | `Application_Code_Changes.md` |
| ML/evaluator reconciliation detail | `05_ML_Evaluation_Results.md` |
| RL/PPO detail | `06_RL_Evaluation_Results.md` |
| Qwen quality rubric detail | `07_Qwen_Feedback_Quality_Evaluation.md` |
| Speech/WER protocol (not executed) | `08_Speech_Evaluation.md` |
| Performance/reliability | `09_Performance_and_Reliability.md` |
| E2E status | `04_End_to_End_Results.md` |
| Checkpoint/experiment provenance register + reward-redesign protocol | `11_Experiment_Provenance_Register.md` |
| Repository structure audit | `Repository_Structure_Audit.md` |
| IEEE-relevance guidance for this phase's findings | `13_IEEE_Research_Evidence_Recommendations.md` |
| Top-level synthesis | `14_Executive_Summary.md` |
