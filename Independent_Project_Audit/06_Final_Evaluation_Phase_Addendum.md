# 06. Addendum — Final Evaluation Phase (Controlled Improvements), 2026-11-13

*This addendum is appended to the original five-document audit (01–05) above, which remains unmodified. It summarizes a later, separately-scoped engagement phase ("Final Comprehensive Testing, Evaluation and Results Improvement") that ran after the original audit, on branch `final-eval/controlled-improvements`. Tagging convention follows the original audit: every claim is marked **VERIFIED FACT**, **OBSERVATION**, **INTERPRETATION**, **RECOMMENDATION**, or **UNKNOWN**.*

## 6.1 Scope of this phase

**VERIFIED FACT.** This phase had three authorized parts: (1) extended testing/evaluation evidence generation, (2) controlled, narrowly scoped application code improvements (explicitly authorized, superseding the original audit's no-code-change constraint, with an explicit prohibition on architecture replacement or algorithm redesign), (3) incremental repository organization. Full source record: `testing_and_evaluation/final_evaluation/` (14 documents) and `testing_and_evaluation/final_review/Initial_Testing_Audit.md`.

## 6.2 Application code changes made this phase

**VERIFIED FACT.** Exactly three application source files were modified, each a narrow bug fix with its own before/after evidence (`testing_and_evaluation/final_evaluation/Application_Code_Changes.md`):

| # | File(s) | Defect | Fix | Verification |
|---|---|---|---|---|
| 1 | `services/qwen/app.py` | LLM-emitted JSON string fields were iterated character-by-character instead of treated as single-item lists (7 call sites) | New `_as_str_list()` type-checked coercion helper | Reproduced live against the real model before the fix, confirmed absent after; 5/5 unit cases |
| 2 | `apps/backend/main.py`, `services/storage/database.py` | Admin dashboard showed only in-memory sessions, losing all history on backend restart | New read-only `list_sessions()` function, merged with live sessions (no schema change) | 27 historical sessions recovered, cross-checked against a raw SQL query |
| 3 | `rl/env/interview_env.py` | The dormant, inference-time guardrail-fallback code path still used the pre-fix G5 boundary (`perf>0.40`), inconsistent with the already-fixed `rl/guardrails.py` (`perf>=0.30`) — a latent, non-exercised inconsistency, not a live safety gap, since the primary guardrail path was already fixed | Synced the fallback path's boundary to match | 5/5 new boundary cases pass after the fix (0/5 before, by construction) |

**VERIFIED FACT.** No model weight, PPO checkpoint, reward function, database schema, or frontend file was modified. No new PPO training was run.

## 6.3 Regression verification

**VERIFIED FACT.** The full backend `pytest` suite was re-run both before and after all three code changes: **264 passed, 19 failed, 15 skipped** both times (18 of the 19 failures Docker-daemon-dependent; 1 the pre-existing documented known issue), confirming zero regressions. Frontend `Vitest`: 28/28, both times. Full attribution: `testing_and_evaluation/final_evaluation/03_Test_Execution_Summary.md`.

## 6.4 New evidence generated this phase

**VERIFIED FACT.**

| Finding | Result |
|---|---|
| Gymnasium `check_env()` run against `InterviewEnv` (new test, not previously run in this project) | PASSED, no warnings |
| PPO checkpoint identity — deployed (`rl/checkpoints/seed_123/ppo_final.zip`) vs. evaluated (`research/experiments/paper3/checkpoints/seed_123/ppo_final.zip`) | Re-verified via SHA-256: `2ab8d514...` vs `299437ea...` — **confirmed genuinely distinct files**, neither modified nor swapped |
| ρ=0.4825 vs 0.4832, and ρ=0.4897 vs 0.4884 (a pair of close-but-not-identical numbers flagged as a risk of future mislabeling in the original audit, doc 02) | Reconciled against primary source files (`paper2_ablation_results.csv`, `X2B_REPORT.md`): **both pairs are correct, already-distinct quantities; no numeric error exists in any prior document** |
| Qwen narrative-feedback quality, 12-criterion rubric, 4 real captured samples (not previously evaluated in this project) | 1 output-corruption defect found and fixed (§6.2 item 1); 1 residual limitation documented, not fixed — a factually-confused explanation in one sample and hallucinated structured-field content in another |
| Hint/report generation mechanism | Confirmed template-only (pure f-string formatting), **not** LLM-generated, despite labels in some earlier materials implying otherwise |

## 6.5 Correction to this audit's own earlier framing

**OBSERVATION.** The original audit (docs 01–05) and the IEEE paper / presentation produced in a separate engagement phase describe Qwen's role primarily in terms of feedback, hints, and follow-up generation together. This phase's direct investigation established that only feedback and follow-up generation are genuinely LLM-backed; hint and session-report generation are deterministic templates. This does not change any numeric finding in docs 01–05 (which already correctly state Qwen never touches the numeric score), but any future revision of those documents, or of the IEEE paper / presentation, should state the hint/report distinction precisely rather than imply uniform LLM generation.

## 6.6 PPO behavior — unchanged, investigated further

**VERIFIED FACT, carried forward unchanged from doc 02/04.** The pre-registered confirmatory result (`X3A-C001`) stands: PPO+Guardrails is not statistically distinguishable from a constant-action-plus-guardrails baseline under the pre-specified δ=0.12 MAE margin.

**INTERPRETATION, new this phase.** Root-cause analysis of the reward function (`testing_and_evaluation/final_evaluation/11_Experiment_Provenance_Register.md` §3) indicates the policy's near-constant "Same" behavior is structurally explained by the reward's ~60% weighting toward agreement with a rule oracle plus a stability penalty, both computed on the post-guardrail action — not by a training failure.

**RECOMMENDATION, not executed this phase.** A fully specified, ready-to-run alternative-reward experimental protocol (new checkpoint directory, same algorithm/hyperparameters/seeds, same confirmatory-grid methodology) is recorded for any future, separately pre-registered experiment. The original frozen checkpoints and results were not touched.

## 6.7 Repository organization

**VERIFIED FACT.** Two README files were added (`testing_and_evaluation/scripts/README.md`, `testing_output/README.md`); zero files were moved, renamed, or deleted. Full detail: `testing_and_evaluation/final_evaluation/Repository_Structure_Audit.md` and `Repository_Organization_Changes.md`.

## 6.8 Net effect on this audit's original verdict (doc 05)

**INTERPRETATION.** This phase's findings do not change the original Executive Verdict's overall characterization of the project. It closes two of the original roadmap's items (the admin-dashboard data-loss gap, and the ambiguity around the two close ρ-value pairs) with direct fixes/reconciliation, and adds one new disclosed limitation (Qwen narrative-text quality) that was previously an unexamined gap rather than a known issue. The PPO equivalence finding, the evaluator's exploratory-only validation status, and the CrossEncoder provenance gap remain exactly as characterized in the original verdict.
