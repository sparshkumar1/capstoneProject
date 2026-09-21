# PREPAIred — Canonical Scientific Truth (CURRENT)

**Version:** 1.0 · **Created:** 2026-09-19 (Phase 0) · **Status:** the single authoritative current source for verified metrics, formulas and claim status.
**Supersedes for scientific facts:** `research/CANONICAL_SCIENTIFIC_TRUTH.md` (root, commit `9cfd34f` era) and `research/CLAUDE_HANDOFF/CANONICAL_SCIENTIFIC_TRUTH.md` (handoff, "b7cad49" era). Both remain in the repository unchanged as historical records; see `research/audit/SCIENTIFIC_TRUTH_SUPERSESSION.md` for the statement-level map.

## How to use and change this file
1. Numbers and wording here are limited to what has been checked against a stored artifact. Every fact carries an **evidence label** and, where possible, an artifact path. Permitted manuscript wording lives in `research/claims/CLAIM_REGISTRY.csv`.
2. **Evidence labels.** `FROZEN-VERIFIED` = read from a frozen stored file and re-read in the Phase-0 pass or in the audit (`research/audit/CLAUDE_NUMERICAL_VERIFICATION.csv`). `AUDIT-REPLAY` = evaluation-only replay of frozen code/checkpoints, not stored in a frozen file (scripts not archived; to be regenerated as stored artifacts in Phase 1). `AUDIT-DIAGNOSTIC` = exploratory calculation on stored frozen data, not a registered result. `CODE` = read from source. `UNVERIFIED` / `NOT ESTABLISHED` = do not assert.
3. **Do not edit in place without** a changelog entry (bottom) and user approval. New experiments add facts here only after their protocol has been executed, analysed and registered.
4. If this file conflicts with any other document, this file wins, unless a `WITHDRAWN`/`SUPERSEDED` registry row says otherwise. If it conflicts with a stored frozen result file, the frozen file wins for *the number* and this file must be corrected.
5. **Simulation-only and pilot-only evidence is never a real-user claim.**

---

## A. System architecture (as implemented) — `CODE`, `AUDIT`
- Hub-and-spoke orchestrator (`agents/orchestrator/interview_orchestrator.py`) with session state, question queue, attempts and follow-up logic.
- Evaluator (`services/evaluator/app.py`): `BaseScore = 0.15·S1 + 0.35·S2_eff + 0.50·R`; `S2_eff = S2` if `R > 0.30`, else `0.6·S2`; final score adds a bonus/penalty and a cap (code). `S1` = SBERT (`all-MiniLM-L6-v2`) cosine similarity; `S2` = FAISS concept coverage at cosine threshold θ = 0.30; `R` = CrossEncoder output mapped `R = clip((raw − 0.20)/0.70, 0, 1)` (`app.py:163-168`). The R mapping constants presuppose the output range of the tuned checkpoint.
- Small lexical hedging penalty (0.03) applies to transcripts containing hedge words when `S2 < 0.50` and `R < 0.40` (`app.py`; audit P1-10). Acoustic features have no parameter in `evaluate`.
- Sandbox: Docker C sandbox launched with non-root user, `--net=none`, `--cap-drop=ALL`, `--read-only`, no-new-privileges, memory and PID limits (`agents/coding_executor/coding_executor.py`). **These are configuration facts, not measured effectiveness.**
- Persistence: SQLite in WAL mode. Feedback text: local Qwen2.5-1.5B-Instruct, which has no input path into `evaluate`. **No `FeedbackValidator` class exists** (audit P0-6); feedback is therefore *unvalidated*.
- Video/MediaPipe: not present.

## B. CrossEncoder (R component) provenance — `FROZEN-VERIFIED` (weights), `NOT ESTABLISHED` (training)
- File: `services/evaluator/models/tuned_model2/model.safetensors`, SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450` (byte-identical to the 2026-04-13 commit).
- **Correct wording:** a **partially fine-tuned derivative** of `cross-encoder/ms-marco-MiniLM-L-6-v2` (embeddings and encoder layers 0–3 identical to upstream; layers 4–5, pooler and classifier head changed; 16.28 % of parameters). Training data, code, split, hyperparameters and author are **not available in the repository**; provenance is **incomplete**. Whether any benchmark question or reference was in the training data is **undetermined**.
- **Withdrawn wording:** "off-the-shelf", "zero-shot", "no fine-tuning", "no PREPAIred-specific adaptation", "MiniLM-L12". The upstream weights hash (`821d1aa6…`) is not the deployed file.
- A record `best_model_info.json` describes a Huber+rank fine-tune (epoch 5, step 660, validation Spearman 0.785); its data are unknown. A sibling checkpoint was deleted 2026-08-29.
- Status of enquiry: `research/audit/MODEL_PROVENANCE_REQUEST.md` (drafted, not sent).

## C. Paper 2 — evaluator vs human ratings

### C.1 Human benchmark and ratings — `FROZEN-VERIFIED`
- `research/data/evaluator_benchmark/final_human_gold.csv`, SHA-256 `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2`. **64 constructed answers to 8 questions**, 10 answer categories (2–8 cases per category), authored by the study team in one script (`research/scripts/build_comprehensive_benchmark.py`). Three rater files (hash-pinned), 54 items by mean of three and 10 items adjudicated (spread > 0.20).
- Reliability: ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff α 0.9523 (interval). `AUDIT-DIAGNOSTIC`: category membership explains ≈ 98–99 % of rater variance, so reliability largely reflects benchmark construction.
- **Role of this benchmark (locked):** *exploratory/initial evidence*. θ = 0.30 and the dampening were chosen on an earlier N = 20 pilot that shares 4 of the 8 questions, so the 64-case result is not clean confirmation. The confirmatory set will be a new benchmark (protocol `X2_PROTOCOL_DRAFT.md`).

### C.2 Evaluator vs consensus human score — `FROZEN-VERIFIED` (`research/results/paper2/paper2_summary_results.csv`, `paper2_ablation_results.csv`)
| Configuration | Spearman ρ | 95 % CI (case bootstrap, B = 2000) | MAE |
|---|---|---|---|
| Full composite | **0.3812** | [0.1575, 0.5774] | 0.2920 |
| R only | 0.4832 | [0.2501, 0.6762] | 0.2763 |
| S1 + R (0.23/0.77) | 0.4884 | [0.2624, 0.6751] | 0.2790 |
| S2 + R (0.41/0.59) | 0.4171 | [0.1978, 0.6124] | 0.2674 |
| S1 only / S2 only / S1 + S2 | 0.2070 / 0.3021 / 0.2894 | (S1 only CI includes 0) | 0.3171 / 0.3251 / 0.3042 |

Also: Pearson 0.4042, Kendall τ 0.2715, RMSE 0.3601 (n = 64). The full composite correlates **below** R-only and S1+R; describe it as *safety-hardened*, not accuracy-optimal.
- **Scope of the claim (locked wording):** moderate rank agreement on 64 constructed answers to 8 questions. Not a general validity claim. The case-level CI treats 64 answers as independent; the effective topical sample is 8 questions. `AUDIT-DIAGNOSTIC` (to be regenerated in X2-A, not yet registered): question-cluster bootstrap CI ≈ [0.30, 0.59]; per-question ρ 0.44–0.91; pilot-overlap questions ρ ≈ 0.71 vs other questions ≈ 0.43; systematic under-scoring of correct-but-concise answers (human mean 0.91 vs model 0.40).
- Robustness (`FROZEN-VERIFIED`): metamorphic 19/21 relations passed (only 3 base cases × 7 relations); adversarial 11/13 "contained" against author-set ceilings (0.15–0.85). Descriptive only.
- **Superseded pilot:** ρ = 0.6975 (N = 20, one rater, 4 topics) is a *development pilot*, not the current human result. ρ = 0.7400 (stale CSV artefact), 0.9152 (synthetic proxy raters), 0.8358 (human/synthetic hybrid) are invalid.

### C.3 Human-subject provenance — `NOT ESTABLISHED`
Rater and adjudicator identities, qualifications, recruitment, instructions actually sent, send/return timestamps, consent, compensation, any institutional determination, and Gate-1 approval are **not documented in the repository**. The repository is silent; nothing is inferred about what occurred. Do **not** write "independent experts", "committee", "approved", "consented", "voluntary". Plan: `HUMAN_BENCHMARK_PROVENANCE_PLAN.md`; enquiry draft: `INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`.

## D. Paper 3 — adaptive difficulty control in simulation

### D.1 Design — `FROZEN-VERIFIED` (`research/experiments/paper3/frozen_config.yaml`) and `CODE`
- PPO (SB3 `MlpPolicy`, net [64, 64]), **24 576 timesteps per training seed** (12 rollouts of 2 048), training seeds 42/123/456/789/999, evaluation seeds 1001/2002/3003/4004/5005. (The "300 000 steps" and "204 800 steps" figures in older documents do not describe the frozen study.)
- State: 6-D in [0, 1] (perf, avg_perf, confidence, hesitation, progress t/T, difficulty/5); actions Easier/Same/Harder.
- Reward (config weights): decision alignment 0.60 (agreement with a hand-coded rule oracle), outcome delta 0.30, multimodal shaping 0.10, stability penalty −0.10. **The reward is largely imitation of a rule oracle; the evaluation metric (mean |difficulty − persona target|) is not the training objective.**
- Five author-defined personas (skill → target): 0.20 → 1.0, 0.30 → 1.5, 0.60 → 3.0, 0.80 → 4.0, 0.88 → 4.5 (all equal `round(10·skill)/2`; arithmetic, not stated in the config). Evaluation: T = 10 turns, integer difficulty 1–5 with ±1 steps; training environment used T = 15 with continuous 0.1 steps (training ≠ evaluation environment).
- Guardrails (frozen config): G0, G4, G1, G2, G5, G6; the module has **no boundary rule**.
- **Statistical unit: persona** (training seed = second random factor; evaluation seed nested). The frozen study analysed 25 sessions per condition (5 personas × 5 evaluation seeds); those session-level tests are pseudo-replicated and descriptive only. Persona-level paired t-test on the five personas: p = 0.204 (audit).
- **Simulation only. No learner, learning-gain or real-user claim.**

### D.2 Results — `FROZEN-VERIFIED` (`paper3_baseline_results.csv`, `paper3_seed_results.csv`, `paper3_summary_results.csv`)
| Condition | Tracking MAE | Volatility |
|---|---|---|
| Fixed (d = 3.0) | 1.200 | 0.000 |
| Heuristic | 0.473 | 0.160 |
| PPO raw, seed 123 | 0.804 | 0.088 |
| PPO + guardrails, seed 123 | 0.673 | 0.088 |
| PPO + guardrails, five seeds | 0.677 (per seed 0.687 / 0.673 / 0.676 / 0.673 / 0.676) | **0.186** (per seed 0.268 / 0.088 / 0.208 / 0.240 / 0.128) |

- **P0-5:** the five-seed guarded volatility is 0.186 (heuristic 0.160). 0.088 is seed 123 only and must not be reported as the aggregate. `AUDIT-REPLAY`: raw PPO mean volatility 0.078 (five seeds); guardrails raised volatility ≈ 2.4× (stored `volatility_reduction_pct = −140.21`).
- **P0-4:** per-seed column `guardrail_interventions` in `paper3_seed_results.csv` (122 / 101 / 115 / 120 / 105, total **563**) counts **rule activations** over 1 250 turns (45.0 %). `AUDIT-REPLAY`: **99 turns (7.9 %)** had the final action differ from PPO's proposal; 464 of 563 activations left the action unchanged; 41 of 125 sessions had at least one change.
- **P0-3:** "0 constraint violations" is a **hard-coded literal** in the summary rows (`execute_paper3_study.py:774, 886, 895`). The stored per-seed counter `constraint_violations` (26 / 71 / 41 / 33 / 61, total **232**) counts **attempted out-of-range actions before the clamp** (all "Easier" at the difficulty floor; no-ops). `AUDIT-REPLAY`: raw PPO 136 / 1 250 turns (10.9 %) vs guarded 232 / 1 250 (18.6 %). The environment clamps difficulty to [1, 5] for every policy, so "0 actual out-of-bounds states" is an implementation invariant, not a result and not evidence for the guardrails. Use the term **boundary-saturated (attempted boundary) actions**.
- **P0-2 (attribution):** `AUDIT-REPLAY`: constant-"Same" + the same guardrails gives MAE 0.673, equal to PPO + guardrails (0.673–0.687); 5 of 125 sessions differ. The guardrails account for essentially all of the improvement over Fixed; the heuristic (0.473) is better than every PPO variant. **PPO's contribution under guardrails is not identified by the frozen study.** Claim "PPO improves tracking" is withdrawn.
- **P1-15:** the identical Dimension-4 ablation MAE (0.673) arises from guardrail masking (final actions identical on 250/250 turns), not from evidence that PPO is insensitive to that dimension.
- **Deployed vs evaluated checkpoint:** runtime `rl/checkpoints/seed_123/ppo_final.zip` (`2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575`) differs from the evaluated `research/experiments/paper3/checkpoints/seed_123/ppo_final.zip` (`299437ea0dcdd7a5eed51326e80854bd3bb55341194420b619c5da3d675e24e0`). State which checkpoint each claim refers to.

## E. Paper 1 — systems evidence

`FROZEN-VERIFIED` and scope-limited unless stated.
- **Real measurements:** concurrency benchmark (1/5/10/25 threads, synthetic DB operations, no evaluator or LLM in the loop; 0 lock errors, 0 isolation violations); latency (`paper1_latency_results.csv`): evaluator n = 20, mean 1960.8 ms, **median 404.6 ms**, P95 2098.6 ms, **P99 26 369.4 ms** — the mean is dominated by a cold-start-scale outlier and raw per-sample values are not stored; SQLite write mean 17.2 ms (n = 25), read 5.0 ms (n = 25), `ScoreValidator` 0.004 ms (n = 100).
- **Concurrency latency (`paper1_concurrency_results.csv`):** per-operation mean latency rises with load from 16.3 ms (1 session) to 419.5 ms (25 sessions; P95 719.1 ms), while lock errors and isolation violations stay 0. The older sentence "write latency scales from 16.3 ms to 21.0 ms P95" conflates this table with the single-session SQLite write latency table (P95 21.0 ms, n = 25 samples) and is withdrawn.
- **Security runs:** nine attack programs were executed; four outcomes discriminate (SEC-01, 03, 04, 05); the other five do not identify which control acted. Supportable wording: "the programs ran without host compromise in this harness".
- **Not measured (literal PASS strings):** fault injection "10/10" (evidence: 1 evidenced, 5 partial, 4 none) and Qwen isolation "5/5" (3 partial, 2 none). These tables are a *design-level handling matrix*, not results. **"213 tests passed"** has no stored log (a stored record shows 204 passed / 1 skipped); one known failing test exists in the current tree (`tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`).
- **Framing (locked):** failure-aware, sandboxed architecture with a scoped systems evaluation. **"Secure" is removed. "Fault-tolerant" is conditional on X1-A evidence.** Do not claim "100 % acoustic insulation" (a small lexical hedging penalty applies to transcripts).

## F. Version-control and hash facts — `FROZEN-VERIFIED`
- Paper 3 freeze commit: `b7cad49529c335317ad284dba700f770d1964f6a`, tag `v1.0-paper3-complete` (annotated tag object `8e5c304f…`). The long hash `b7cad49b6b7a54460f4eeb4ecb0292bfcb78e12f` cited in older documents **does not exist**.
- Human-annotation freeze: tag `pre-human-annotation` → commit `45845a97a136529c7a740cd68954be8260cdb656`.
- Frozen results for papers 1–3 first appear in Git at `b7cad49`, not at `375f4f8`.
- Environment: the project `.venv` violates the pins in `requirements/*.txt` (numpy 2.5.2 vs `<2`, torch 2.11.0 vs `<2.7`, accelerate 1.13.0 vs `<1.0`). Frozen results were not generated in a recorded locked environment. New runs use `ENVIRONMENT_LOCK_SPEC.md`.

## G. Experiment status
**No confirmatory X1/X2/X3 experiment has been run.** All planned experiments are specified only in drafts (`X1/X2/X3_PROTOCOL_DRAFT.md`). Locked decisions: `research/audit/PHASE0_DECISION_LOCK.md`.

## H. Withdrawn / superseded statements (pointer)
See `research/audit/SCIENTIFIC_TRUTH_SUPERSESSION.md` and rows with `status = WITHDRAWN` in `research/claims/CLAIM_REGISTRY.csv`. Not to be used in any draft: ρ 0.6975 as current; 0.7400; 0.9152; 0.8358; "off-the-shelf"; "0 violations / eliminates 100 %"; "563 interventions"; "volatility 0.088 vs 0.160"; "PPO improves tracking"; "10/10", "5/5", "9/9 contained", "213 passed"; "100 % acoustic insulation"; "independent experts"; commit hash `b7cad49b6b7a…`; "205/205 tests"; "300 000 PPO steps"; "21 % volatility reduction"; venue names/deadlines from the older root file (venue is TBD).

## I. Changelog
| Date | Version | Change | Approval |
|---|---|---|---|
| 2026-09-19 | 1.0 | Created in Phase 0 from stored frozen artifacts and the audit record | User (Phase-0 approval) |
