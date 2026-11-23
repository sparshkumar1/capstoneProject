# Existing-Evidence Analysis — Evaluator Ablation, Re-examined

**Method:** re-analysis only. Every number below is either read directly from a frozen file or recomputed from already-stored, already-computed columns (`S1`, `S2`, `S2_eff`, `R`, `final_score`, `human_gold_score`, `qid` in `research/results/paper2/paper2_case_level_results.csv`). No model was called, no new score was generated, no frozen file was modified. Recomputation script: `research/paper_strengthening/scripts/reanalyze_evaluator_ablation.py` (seed 20260921, disclosed and fixed). Raw output: `research/paper_strengthening/results/evaluator_reanalysis.json`.

## 1. Provenance check

- Benchmark: `research/data/evaluator_benchmark/final_human_gold.csv`, SHA-256 `363dbe6d84…` — 64 items, 8 questions, 10 categories, three raters (54 mean-of-three, 10 adjudicated).
- Frozen config: `research/experiments/paper2/frozen_config.yaml`, SHA-256 `f057baf1b2…`.
- Checkpoint: `services/evaluator/models/tuned_model2/model.safetensors`, SHA-256 `6a241a55be…`.
- **Provenance discrepancy found and resolved:** `research/results/paper2/PAPER2_FINAL_REPORT.md` (the original evaluation report) states the CrossEncoder is *"Off-the-shelf... deployed in zero-shot inference without PrepAIred-specific fine-tuning"* and calls the checkpoint directory name `tuned_model2` *"strictly a scaffolding artifact."* This is superseded: a later byte-level weight comparison (`research/audit/P0_1_CROSSENCODER_FORENSIC.md`, folded into `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §B) found encoder layers 4–5, the pooler, and the classifier head differ from the public upstream checkpoint (16.28% of parameters), which is not consistent with zero-shot deployment. Per this project's own rule ("if this file conflicts with any other document, the canonical file wins"), **the original report's "off-the-shelf" claim is withdrawn**; the checkpoint is a partially fine-tuned derivative with incomplete training provenance. This paper must use the corrected wording, not the original report's.

## 2. Cross-check: recomputed vs. frozen ablation numbers

Recombining the stored `S1`/`S2`/`R` columns under the already-published weights reproduces the frozen ablation CSV's Spearman ρ exactly for all seven configurations (S1 only 0.207, S2 only 0.3021, R only 0.4832, S1+S2 0.2894, S1+R 0.4884, S2+R 0.4171, full composite 0.3812). This is a successful independent validation of the frozen result, not a new finding — but it confirms the stored numbers are internally consistent and computed the way they claim to be.

## 3. Question-clustered reanalysis (the actual new contribution of this pass)

The frozen CIs bootstrap over the 64 *items*, which the benchmark's own documentation notes are drawn from only 8 underlying questions — the case-bootstrap therefore overstates the effective sample size. Re-running the bootstrap by resampling the 8 **questions** (with all of a resampled question's items carried along) gives a more honest picture of what 8 independent units can actually support:

| Configuration | Item-level ρ (frozen, for reference) | Question-clustered bootstrap mean ρ | Question-clustered 95% CI |
|---|---|---|---|
| S1 only | 0.207 | 0.252 | [0.147, 0.397] |
| S2 only | 0.302 | 0.329 | [0.119, 0.600] |
| **R only** | **0.483** | **0.496** | **[0.441, 0.577]** |
| S1+S2 | 0.289 | 0.330 | [0.169, 0.583] |
| **S1+R** | **0.488** | **0.509** | **[0.434, 0.627]** |
| S2+R | 0.417 | 0.453 | [0.338, 0.628] |
| Full composite | 0.381 | 0.414 | [0.299, 0.587] |

R-only and S1+R are the only two configurations whose question-clustered interval sits clearly above the others and stays relatively tight; the full composite's interval is wider and centered lower.

## 4. Is the full hybrid evaluator actually superior? A direct, paired answer

Rather than comparing overlapping confidence intervals (which is not a valid significance test), a paired, question-clustered bootstrap was run directly on the *difference* in per-item absolute error between the full composite and R-only:

- Mean absolute error, full composite: **0.292**. Mean absolute error, R-only: **0.276**.
- Question-clustered bootstrap of the mean difference (full − R-only): **+0.015**, 95% CI **[−0.015, +0.051]**.

**The CI includes zero.** Given only 8 independent questions, this data does not support a claim that the full hybrid weighting is more accurate than the CrossEncoder alone — nor does it support the reverse. What it does support: **the full composite's added complexity (semantic similarity and concept-coverage terms, plus dampening, bonus and penalty logic) is not shown to buy measurable accuracy over the reasoning-verification term by itself, on this benchmark.** This is the correct, non-overclaiming way to state the finding — a "not shown to help" result, not a "shown to hurt" result, and not a null-equivalence claim stated with more confidence than 8 questions can support either.

## 5. Per-question heterogeneity (why the interval is wide)

| Question | Mean human score | Mean full-composite score | Mean R-only score |
|---|---|---|---|
| 1 | 0.478 | 0.404 | 0.435 |
| 3 | 0.492 | 0.542 | 0.551 |
| 7 | 0.473 | 0.173 | 0.338 |
| 10 | 0.406 | 0.469 | 0.461 |
| 15 | 0.472 | 0.230 | 0.430 |
| 22 | 0.385 | 0.239 | 0.427 |
| 41 | 0.482 | 0.484 | 0.352 |
| 50 | 0.490 | 0.066 | 0.244 |

Two questions (7 and 50) show large under-scoring by the full composite relative to human raters (question 50: human 0.49 vs. full-composite 0.066 — a near-total miss), and R-only under-scores less severely on both. This kind of per-question volatility, with only 8 questions total, is exactly why neither configuration's superiority can be confirmed here, and it is itself worth reporting: **the evaluator's behavior is not uniform across questions**, and a confirmatory study needs enough distinct questions to average this out rather than let one or two questions dominate the result.

## 6. What this analysis licenses the manuscript to say

- Cite R-only (ρ=0.4832, question-clustered CI [0.44, 0.58]) as the strongest single-component result and the closest thing to a stable finding this benchmark supports.
- State plainly that the full hybrid weighting is not shown to outperform R-only or S1+R on this benchmark, with the paired-difference CI as direct evidence, not just "the CIs overlap."
- Report the per-question heterogeneity as a limitation of the benchmark's size (8 questions), not of the evaluator per se.
- Continue to describe all of this as **exploratory**, per the benchmark's own locked scope statement (θ=0.30 and the dampening floor were themselves chosen using an earlier, overlapping 20-item pilot, so this 64-item result is not a clean confirmatory test even of the configuration it evaluates).
- Correct the CrossEncoder's provenance description per §1 — do not repeat the original report's "off-the-shelf" language.

## 7. What this analysis does not license

- It does not license claiming the dampening mechanism (Eq. 3) specifically helps or hurts — that requires the category-level breakdown proposed as Experiment A2 in `EXPERIMENT_PLAN.md`, not yet run in this pass.
- It does not license a confirmatory claim about which configuration is "best" — 8 questions is too few to certify that, and the paper should say so rather than imply otherwise by picking whichever point estimate is highest.
- It does not touch, and has no bearing on, the RL/PPO findings (§ separate document) or the speaking-rate defect (§ separate document) — these are independent evidentiary threads.
