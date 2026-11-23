# Evidence Audit — Claim-by-Claim Reconciliation

**Method:** every figure below was traced to a specific file, or declared untraceable. Nothing here was accepted on the strength of a manuscript sentence or prior summary alone. Read-only pass; no code changed, no experiment run, no checkpoint touched. One exception, logged explicitly: a deterministic function call using the real, unmodified scoring code with representative inputs (§4), performed to verify a suspected defect — no data collection, no training, no stochastic result.

## 1. Answer-evaluation correlation figures

| Figure cited | Where it appears | Source found | Status |
|---|---|---|---|
| 0.796 | Original PDF, §X.B, abstract | Not found anywhere in the repository (full-text search of all `.md`, `.py`, `.json`, `.csv`; two coincidental digit matches in unrelated RL replay logs, confirmed unrelated by inspecting surrounding columns) | **Untraceable — do not use** |
| 0.785 | `services/evaluator/models/tuned_model2/best_model_info.json` (`val_spearman`, epoch 5, step 660) | Real file, but its training data, split, and whether it overlaps the evaluation benchmark are **not documented** (`CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §B: "its data are unknown") | **Real number, not usable as a validation claim** |
| 0.3812 | `research/results/paper2/paper2_summary_results.csv` — full composite (S1+S2_eff+R) vs. human reference | `FROZEN-VERIFIED`; 64 constructed answers, 8 questions, case-bootstrap CI [0.1575, 0.5774] | **Usable, with exploratory-scope caveats** |
| 0.4832 | Same file — R-only | `FROZEN-VERIFIED`; CI [0.2501, 0.6762] | **Usable, with exploratory-scope caveats** |
| 0.4884 | Same file — S1+R (0.23/0.77) | `FROZEN-VERIFIED`; CI [0.2624, 0.6751] | **Usable, with exploratory-scope caveats** |
| 0.6975 | Older documents | `NOT ESTABLISHED` as current — single rater, N=20, 4 of 8 topics shared with the 64-item set (pilot/dev overlap) | **Superseded pilot — never cite as current** |
| 0.7400 / 0.9152 / 0.8358 | Older documents | Canonical file marks these explicitly invalid (stale CSV artefact; synthetic proxy raters; human/synthetic hybrid) | **Withdrawn — never cite** |

**Resolution for this paper:** report R-only (ρ=0.4832) as the headline reasoning-alignment figure, cross-reference the full composite (0.3812) and S1+R (0.4884) in a small ablation table (data already collected, see §5 of `RESEARCH_STRATEGY.md`), and state plainly that the full weighted composite is not shown to outperform simpler combinations on this benchmark (CIs overlap; not a claim of statistically significant difference, a claim of absence of demonstrated benefit).

## 2. CrossEncoder checkpoint provenance

- File: `services/evaluator/models/tuned_model2/model.safetensors`, SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`.
- **Verified fact:** a partially fine-tuned derivative of `cross-encoder/ms-marco-MiniLM-L-6-v2` — encoder layers 0–3 byte-identical to upstream; layers 4–5, pooler, and classifier head differ (16.28% of parameters changed).
- **Not available in the repository:** training data, training code, data split, hyperparameters, author, date. Whether any benchmark question/reference overlaps the fine-tuning data is undetermined.
- **Resolution:** the manuscript may correctly say "partially fine-tuned derivative with incomplete provenance." It may not say "off-the-shelf," "zero-shot," or "fine-tuned on [any specific dataset]" — none of the latter is supported. An enquiry draft exists (`research/audit/MODEL_PROVENANCE_REQUEST.md`) but has not been sent; resolving this fully requires contacting whoever produced the checkpoint, which is outside the scope of a code/data audit.

## 3. Reinforcement learning

| Claim | Verified status |
|---|---|
| "PPO smoothly adjusts difficulty based on candidate state" (original draft, presented as a confirmed result) | **Contradicted by frozen data.** `research/experiments/paper3/` (frozen, tag `v1.0-paper3-complete`, commit `b7cad49`): PPO+guardrails MAE 0.677 (five seeds) vs. constant-"Same"+guardrails MAE 0.673 (`AUDIT-REPLAY`, same guardrail code); 120/125 sessions produce identical guardrail-adjusted actions. Heuristic rule MAE 0.473, better than every PPO variant tested. Canonical file states verbatim: "Claim 'PPO improves tracking' is withdrawn." |
| Guardrail attribution | `AUDIT-REPLAY`, `paper3_seed_results.csv`: 563 rule activations recorded, but only 99/1250 turns (7.9%) actually changed PPO's proposed action; the guardrail *layer* (not necessarily every individual rule) accounts for the gap between guarded and unguarded performance. |
| Deployed vs. evaluated checkpoint | **Different files.** Runtime `rl/checkpoints/seed_123/ppo_final.zip` (SHA-256 `2ab8d514…4575`) ≠ evaluated `research/experiments/paper3/checkpoints/seed_123/ppo_final.zip` (SHA-256 `299437ea…24e0`). The deployed checkpoint was produced by `retrain_quick.py` and has not itself been separately evaluated. |
| "Reproduce the existing PPO-vs-constant study" (governing prompt, Phase 2) | **Not re-run in this pass.** The frozen result above is an `AUDIT-REPLAY` of already-frozen data (a re-analysis of stored per-turn logs with a constant-action policy substituted), not a fresh training/evaluation run. A genuine reproduction (retraining from the same seeds and config) has not been attempted here and would require the same seeds, `frozen_config.yaml`, and a registered protocol before execution, since it touches PPO training. |

**Resolution:** the manuscript must state the equivalence finding as a finding, not soften it. This is not optional — it is the most heavily audited, most explicitly "withdrawn claim"-flagged fact in the entire canonical record.

## 4. Speech-delivery channel — speaking-rate unit mismatch (new finding, this pass)

- **Live computation** (`agents/audio/transcriber.py:221`): `speaking_rate = word_count / (total_speech_time / 60.0)` — this is **words per minute** by construction. Realistic values: 100–200 (confirmed by test fixtures using 140.0 and 181.27 for this exact field, `tests/unit/test_stage11_3_followup_and_evaluation.py:444`, `scripts/verify_stage11_3_followup_e2e.py:79`).
- **Consumption** (`agents/audio/confidence_scorer.py:40-44`): compares this same field against the range `[2.1, 4.3]`, center `3.2`. The parallel hesitation scorer (`agents/audio/hesitation_scorer.py:52-57`) does the same, with an explicit code comment: `"optimal 2.1–4.3 words/sec"`. These are **words per second**, not words per minute — a ~60× scale mismatch.
- **Call path confirmed:** `apps/backend/main.py:649-650` passes the raw transcription dict (containing the WPM-scale field) directly into both scoring functions, with no unit conversion anywhere in between.
- **Deterministic verification performed in this pass** (real, unmodified code; representative WPM inputs; no new data, no training):

  ```
  rate=100.0 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
  rate=140.0 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
  rate=160.0 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
  rate=181.27 WPM -> rate_score=0.000  hesitation.rate_deviation=1.000
  ```

- **Consequence:** `rate_score` carries weight 0.13 in `C_final` (Eq. 17); it is pinned to its worst-case value (0.000) for every realistic real-world speaking rate, contributing nothing but a fixed penalty regardless of actual delivery quality. The parallel hesitation-scorer term is pinned to its maximum (1.000) under the same condition. Both are silent — no error, no warning, no test failure, because the existing unit tests for these two scorer functions (`tests/unit/test_speech_pipeline.py:112-127`) supply hand-picked words/sec-scale values (3.0, 2.0, 3.25) directly, never exercising the real transcriber's WPM output through the real scoring path in the same test.
- **Not yet determined:** whether any integration test exercises the full transcriber → scorer path end to end with assertions on the resulting numeric scores (as opposed to just checking the pipeline runs). This would need a further, narrowly scoped code read before claiming the defect is entirely uncaught by the suite; not completed in this pass.
- **This is a code-verifiable defect, not a claim requiring new experiments or approval to state.** Fixing it (a unit conversion, or aligning the threshold to WPM) would be a system change requiring approval before implementation, per project rules — this audit documents the defect only and does not fix it.

## 5. Test suite

- Canonical record: "'213 tests passed' has no stored log; a stored record shows 204 passed / 1 skipped." One known failing test in the current tree: `tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` (`obs[4]` 0.0 vs. expected 0.22).
- The manuscript's Table VI ("20/20 Vitest Passed," all backend modules "Passed") is not traceable to this stored record and overstates completeness. **Not independently re-run in this pass** — re-running the full suite was out of scope for a read-only audit and would itself need to be logged as a new, dated run rather than silently substituted for the old claim.

## 6. LLM partial-evaluation ablation (latency/RAM)

- Table VII figures (73.22 s / 34.01 s, 14.17 GB / 11.20 GB, 0.00 score drift): **not found anywhere in the repository**, including superseded `docs/`. No script named or resembling a `/partial_eval` ablation was found.
- **Resolution:** this table cannot be included in any submitted version without either (a) locating the original run's artifacts outside this repository, or (b) reproducing it as a new, registered experiment (see `EXPERIMENT_PLAN.md`, Experiment 4).

## 7. Security / containment claims

Out of scope for this paper per the governing prompt ("do not substitute the separate P1 security paper"). Noted only so the manuscript does not inadvertently claim anything about containment or authority-boundary properties that belongs to P1's evidence, not this system paper's.

## 8. Summary table for the manuscript

| Manuscript claim | Correct replacement |
|---|---|
| "0.796... confirming strong ranking alignment" | "ρ = 0.4832 (R-only), moderate, exploratory, 64-item benchmark" |
| "fine-tuned CrossEncoder" (unqualified) | "partially fine-tuned derivative, training provenance incomplete" |
| "PPO smoothly adjusts... " (as confirmed result) | "PPO + guardrails statistically indistinguishable from constant-difficulty + guardrails; guardrail layer, not the learned policy, accounts for the gain over an unguarded baseline" |
| "independent speech confidence model... extracts... speaking rate" (implying it functions) | Must disclose the unit mismatch and its measured effect (rate term pinned to worst-case for all realistic real speech) until fixed and re-verified |
| Table VI "Passed" across the board | 204 passed / 1 skipped (last stored record); 1 known unresolved failure |
| Table VII ablation | Remove, or replace with a newly registered and executed experiment |
