# X2-B Protocol v1 - Upstream-checkpoint sensitivity and lexical/length baselines (2026-09-19)

**Status: FINAL for tagging (`prereg/X2-B/v1`).** Evaluation-only. Normative parameters: `research/confirmatory/X2-B/x2b_config.json` (hashed in `protocol_manifest.json`). Authority: the user's sprint instruction of 2026-09-19 and `research/audit/PHASE0_DECISION_LOCK.md`. Independent methodology review (ChatGPT) has **not** been performed. **Scope of this version: the OLD-benchmark arm only (exploratory/sensitivity).** The confirmatory arm on the X2-C benchmark is not covered: it is blocked by the human/ethics gate and would need a new tagged amendment naming the frozen item file.

## 1. Question and hypotheses
(a) Do the derived CrossEncoder (R) and the trivial baselines differ in rank agreement with the frozen human gold and in separating correct-reference from adversarial answers? (b) How much does the undocumented fine-tune matter, i.e. how does the derived checkpoint compare with the public upstream checkpoint `cross-encoder/ms-marco-MiniLM-L-6-v2` on identical inputs? **No directional hypothesis and no categorical verdict** ("small gap"/"large gap" thresholds were not pre-specified and are therefore not applied): the deliverable is a bounded-effect estimate of the paired differences with cluster-bootstrap intervals.

## 2. Frozen evaluator context and data
Derived model `services/evaluator/models/tuned_model2/model.safetensors` (SHA-256 `6a241a55...4450`); upstream snapshot `c5ee24cb...` (weights SHA-256 prefix `821d1aa6`, checked at run time). Data: the frozen 64 constructed answers to 8 questions (`paper2_case_level_results.csv`, texts from the frozen rater file, reference answers from `services/evaluator/assets/rubrics.json`). Because the derived model's results on these items were already known, this arm is **exploratory/sensitivity**; the upstream and baseline outputs on these items are new.

## 3. Scorers and inputs (fixed)
Pair construction exactly as the deployed evaluator (`(question + " " + reference answer).strip()`, candidate answer). Scorers: derived CrossEncoder raw output; upstream CrossEncoder raw output (same activation, same code path); TF-IDF cosine; Okapi BM25; reference-token overlap; length-only (candidate word count); stored reference rows (S1, S2_eff, mapped R, deployed composite) for the derived arm only. Exact definitions: config `scorers`. **No composite is computed for the upstream arm, no MAE-type metric is reported for it, and no mapping is invented or fitted** (locked decision).

## 4. Metrics and inference
**Primary (mapping-independent, invariant to monotone rescaling):** Spearman rho and Kendall tau-b against the human gold; AUROC for correct-reference vs adversarial answers where the labels are the construction categories fixed in the config (not derived from human scores or model outputs; `partial_incomplete` excluded from AUROC). **Primary comparison:** derived minus upstream on these three metrics. **Secondary (descriptive):** derived minus each of TF-IDF, BM25, token overlap, length-only; stored reference rows. **Inference:** two-level cluster bootstrap over the 8 questions (questions with replacement, then answers within question), B = 10 000, `default_rng(42)`, 95 % percentile; the same draws are used for all scorer pairs (paired differences). **Permutation null:** 10 000 within-question permutations of the human gold (`default_rng(43)`), reporting the null 95th percentile and a one-sided permutation p per scorer (descriptive). No multiplicity control; all comparisons are descriptive on exploratory data.

## 5. Gates and controls (abort before any upstream/baseline output if they fail)
G-MODEL-HASH (derived hash exact; upstream prefix); G-METRIC-CONTROLS (monotone, reversed and constant synthetic controls for rho, tau, AUROC); **G-DERIVED-REPRO** (the derived raw output, mapped by the deployed calibration `(raw-0.20)/0.70` clipped to [0, 1], reproduces the stored R column within 0.002 for all 64 items, which validates model loading under the locked environment and the pair construction). The full script was self-tested on synthetic text before tagging (both models loaded; statistics code exercised); no benchmark output of the upstream model or of any baseline was produced before this tag.

## 6. Stopping, ordering, reruns
Single run; the runner refuses to start if `results/` exists; a crash or infrastructure interruption is logged in `DEVIATIONS.md` and the attempt directory is retained; a rerun with unchanged code is allowed only if no output data were written; no scorer, metric or comparison may be added or changed after any output exists (that defines a new experiment).

## 7. Interpretation and reporting
Report the primary contrast and its interval as observed; do not label the fine-tune "immaterial" or "material" from these data; state that the arm is exploratory, has 8 clusters and constructed answers, and that the upstream model is a public MS MARCO ranking model used outside its training format. Provenance of the derived model remains unresolved (trainer enquiry drafted, not sent); wording stays "partially fine-tuned derivative with incomplete provenance".

## 7a. Artifacts
`results/`: gates, `scores.csv` (all per-item scores), metric tables, paired differences, permutation null, report, run manifest. Environment `LOCK-X2-2026-09-19` (hash-pinned; `research/locks/`).

## 8. Disclosures
The authors built the evaluator, the benchmark and this harness; the derived model's results on these items were known before this protocol. The derived model's config was written by a different library version (transformers 5.0.0 / sentence-transformers 5.2.3) than the locked environment (4.44.2 / 2.7.0); compatibility is verified by G-DERIVED-REPRO. The lock pins numpy 2.5.2 and torch 2.11.0, which conflict with `requirements/*.txt` (recorded; unresolved; user decision). No independent review yet.
