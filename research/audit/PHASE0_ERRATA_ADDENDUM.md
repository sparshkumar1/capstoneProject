# Phase 0 Errata / Addendum (2026-09-19)

**Nature of this file.** A new corrections record. It supersedes wording and interpretation in frozen documents; it does **not** edit, regenerate or replace any frozen file, and it changes no stored result. Each entry gives the original statement, the location, the correction, the evidence and its label. Labels: `FROZEN-VERIFIED` (stored frozen file, re-read in Phase 0), `CODE` (source read), `AUDIT-REPLAY` (evaluation-only replay of frozen code/checkpoints during the P0 pass; numbers not stored in a frozen file; to be regenerated as stored artifacts in Phase 1 / X3-0), `AUDIT-DIAGNOSTIC` (exploratory calculation on stored data). Detail: `P0_*_FORENSIC.md`, `P0_P1_DECISION_PLAN.md`.

Corrections that need new computation to be *stored* (marked `AUDIT-REPLAY`) are already correct as statements of what the frozen code produces; they become registered artifacts only after Phase 1.

---

## E-01 (P0-1) CrossEncoder is not "off-the-shelf"
- **Original:** "off-the-shelf CrossEncoder … zero-shot … no PREPAIred-specific fine-tuning or domain adaptation" — `research/CLAUDE_HANDOFF/CANONICAL_SCIENTIFIC_TRUTH.md` §A, §B; repeated in handoff/guidelines and audit documents.
- **Correction:** the deployed file is a **partially fine-tuned derivative** of `cross-encoder/ms-marco-MiniLM-L-6-v2` with **incomplete provenance**. Embeddings and layers 0–3 equal upstream; layers 4–5, pooler and classifier differ (16.28 % of parameters). SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`. Training data/code/split/hyperparameters/author are not in the repository. Leakage against the benchmark is **undetermined**.
- **Evidence:** `FROZEN-VERIFIED` (tensor comparison in `P0_1_CROSSENCODER_FORENSIC.md`), `CODE` (`app.py:163-168` R mapping presupposes the derivative's range).
- **Consequence:** numbers unchanged; wording changed; upstream sensitivity is X2-B.

## E-02 (P0-2) PPO contribution is not identified
- **Original:** the frozen report/handoff attribute the tracking improvement to PPO ("PPO + Guardrails reduces error…").
- **Correction:** under the same guardrails a constant-"Same" base policy gives MAE 0.673, equal to PPO + guardrails (0.673–0.687); 5 of 125 sessions differ. The guardrails account for essentially all of the improvement over Fixed (1.200). The heuristic (0.473) beats every PPO variant. Raw PPO's gain over Fixed is modest and seed-dependent (0.804–1.138). **PPO's contribution under guardrails is not identified.**
- **Evidence:** `AUDIT-REPLAY` (`P0_2_PPO_CONTRIBUTION_FORENSIC.md`); stored means `FROZEN-VERIFIED` (`paper3_seed_results.csv`, `paper3_baseline_results.csv`).
- **Consequence:** Paper 3 is reframed as a controlled decomposition (X3-0/X3-A); "PPO improves tracking" is withdrawn.

## E-03 (P0-3) "0 out-of-bounds violations / eliminates 100 %"
- **Original:** `constraint_violations = 0` in `paper3_summary_results.csv` rows "PPO + Guardrails (Aligned, Seed 123)" and "(5-Seed Mean +/- SD)"; "0 actual out-of-bounds difficulty transitions" (handoff canonical §E line 86); "eliminate 100 % of out-of-bounds transitions" (`PAPER3_FINAL_FREEZE.md:109`; `PAPER3_FINAL_REPORT.md:35`).
- **Correction:** the zeros are **hard-coded literals** (`research/scripts/execute_paper3_study.py:774, 886, 895`). The stored counter in `paper3_seed_results.csv` is **attempted out-of-range actions before the clamp**: 26 / 71 / 41 / 33 / 61 = **232** (guarded, 1 250 turns = 18.6 %). Replay of raw PPO: **136** (10.9 %). All attempts are "Easier" at the difficulty floor and are no-ops. The environment clamps difficulty to [1, 5] for **every** policy (a constant "Harder" policy with no guardrails also never leaves [1, 5]), so 0 actual out-of-bounds states is an **implementation invariant**, not a result attributable to the guardrails. The guardrail module has no boundary rule (its docstring lists one that the code lacks).
- **Terminology to use:** *boundary-saturated (attempted boundary) actions*, reported for the raw proposal and the final action separately. Do not use "violations".
- **Evidence:** `FROZEN-VERIFIED` (seed CSV 232 and hard-coded literals in the stored script), `CODE` (clamp, guardrail module), `AUDIT-REPLAY` (136).

## E-04 (P0-4) "563 guardrail interventions"
- **Original:** "563 total guardrail interventions across 5 seeds" (handoff §E; summary CSV; report).
- **Correction:** 563 is the number of **rule activations** (45.0 % of 1 250 turns; column `guardrail_interventions` of `paper3_seed_results.csv`: 122 + 101 + 115 + 120 + 105). The number of turns where the final action **differed** from PPO's proposed action (**actual action overrides**) is **99 (7.9 %)**; 464 activations (82.4 %) left the action unchanged; 41 of 125 sessions had at least one override. The 213-row `paper3_guardrail_results.csv` is a seed-123 / historical-mismatch trace and does not contain 563 rows.
- **Evidence:** 563 `FROZEN-VERIFIED`; 99 / 464 / 41 `AUDIT-REPLAY` (`P0_4_GUARDRAIL_FORENSIC.md`; replay reproduced the per-seed frozen counts).
- **Terminology:** *rule activation* (563) and *action override* (99). "Intervention" without a definition is not to be used. Overrides are path-dependent; no counterfactual claim.

## E-05 (P0-5) Volatility 0.088 vs 0.160
- **Original:** "PPO provides lower trajectory volatility (0.088 vs 0.160)" (handoff §E line 85); "smoother than the heuristic".
- **Correction:** 0.088 is **seed 123 only**, the lowest-volatility of five seeds. Five-seed guarded volatility per seed: 0.268 / 0.088 / 0.208 / 0.240 / 0.128; **mean 0.186** (population SD 0.068 as stored). Heuristic 0.160. `AUDIT-REPLAY`: raw PPO mean 0.078; guardrails raised volatility about 2.4× (stored `volatility_reduction_pct = −140.21`). Guarded − heuristic (pooled) +0.026, CI [−0.024, +0.078], `AUDIT-DIAGNOSTIC`; no reliable difference. Low volatility partly reflects not adapting (constant-Same + guardrails 0.080).
- **Evidence:** `FROZEN-VERIFIED` (`paper3_seed_results.csv`; recomputed mean 0.1864), `AUDIT-REPLAY`.
- **Not to be used:** 0.088 as the aggregate; "PPO is smoother than the heuristic".

## E-06 (P0-6) Paper 1 "10/10", "5/5", "9/9", "213"
- **Original:** "10/10 fault scenarios recovered", "5/5 Qwen boundary tests passed", "9/9 attack vectors contained", "213 passed" (handoff §C; `PAPER1_FINAL_REPORT.md`).
- **Correction:** fault (10/10) and Qwen (5/5) rows are **literal PASS strings** written by the script, not computed outcomes (evidence classes: fault 1 evidenced / 5 partial / 4 none; Qwen 3 partial / 2 none). All nine attack programs ran; **four** outcomes discriminate (SEC-01, 03, 04, 05); the others do not identify which control acted. "213 passed" has no stored log (a stored record shows 204 passed / 1 skipped, 383.87 s). `FeedbackValidator` does not exist. Concurrency and latency measurements are real but scope-limited.
- **Framing:** failure-aware, sandboxed architecture; "secure" removed; "fault-tolerant" conditional on X1-A.
- **Evidence:** `FROZEN-VERIFIED` (scripts and CSVs), `AUDIT` (`P0_6_PAPER1_EVIDENCE_FORENSIC.md`).

## E-07 (P0-7) Human provenance wording
- **Original:** "3 independent blind CS educators" (handoff §D) and equivalent phrases.
- **Correction:** the repository does not document rater/adjudicator identity, qualification, independence, consent, compensation, timestamps of sending/return, Gate-1 approval or any institutional determination. Only the frozen protocol, hash-pinned rater files and gold data are established. No inference about what occurred is made.
- **Evidence:** `AUDIT` (`P0_7_HUMAN_ETHICS_FORENSIC.md`).

## E-08 (P1-11) Nonexistent long commit hash
- **Original:** `b7cad49b6b7a54460f4eeb4ecb0292bfcb78e12f` (handoff canonical header; `FINAL_RESEARCH_MANIFEST.*`, other documents).
- **Correction:** `git rev-parse b7cad49` = **`b7cad49529c335317ad284dba700f770d1964f6a`**; the annotated tag `v1.0-paper3-complete` (tag object `8e5c304f…`) resolves to that commit. Cite the tag and the real hash. Note: frozen Paper 1–3 results first enter Git at `b7cad49`, not at `375f4f8`.
- **Evidence:** `FROZEN-VERIFIED` (`git rev-parse`, re-run in Phase 0).

## E-09 (P1-13) Session-level statistics are pseudo-replicated
- **Original:** "Evaluation Unit: Session trajectory (N = 25)"; "Cohen's d ≈ 0.87 (p < 0.001)"; `CLAUDE.md` (pre-Phase-0) "statistical unit is the session".
- **Correction:** the 25 sessions per condition are 5 personas × 5 evaluation seeds; sessions within a persona are not independent. The statistical unit for the primary contrast is the **persona**, with the training seed as a second random factor and evaluation seeds nested. Persona-level paired t-test on the five personas: p = 0.204 (`AUDIT`, `CLAUDE_NUMERICAL_VERIFICATION.csv`). Session-level tests are descriptive only. `CLAUDE.md` corrected.
- **Evidence:** `FROZEN-VERIFIED` design (`frozen_config.yaml`, 5 personas × 5 seeds); `AUDIT`.

## E-10 (P1-14) Leaked loop variable in the ablation "Safety Shield" rows
- **Original:** `research/results/paper3/paper3_ablation_results.csv`, category "Safety Shield (Guardrails)": "Raw PPO (No Guardrails, 5 Seeds)": guardrail_interventions 0, constraint_violations **46**; "PPO + Guardrails (5 Seeds)": guardrail_interventions **112**, constraint_violations **0**.
- **Correction:** the 46 (raw row) and 112 (guarded row) equal the values of the **"PPO + Guardrails (Historical Mismatch)"** run in `paper3_baseline_results.csv` (112 interventions, 46 violations), i.e. they were taken from a loop variable left over from a different run (audit finding P1-14); the guarded row's 0 is the hard-coded literal (E-03). The correct five-seed values are: guarded rule activations **563**, guarded attempted boundary actions **232** (`paper3_seed_results.csv`); raw PPO attempted boundary actions **136** (`AUDIT-REPLAY`); MAE 0.958 raw and 0.677 guarded and volatility 0.078 raw and 0.186 guarded (these four are stored in the same ablation rows and agree with the per-seed data); heuristic volatility 0.160.
- **Evidence:** `FROZEN-VERIFIED` (ablation CSV rows and baseline CSV rows read in Phase 0; seed CSV totals 563 / 232).

## E-11 (P1-15) Dimension-4 ablation equality
- **Original:** `aligned_progress`, `aligned_response_time`, `zero_progress` all give MAE 0.673, volatility 0.088, oscillation 0.027, interventions 101, violations 71 — explained as "low neutral sensitivity of s4".
- **Correction:** under guardrails the **final actions were identical on 250/250 turns**, so the equality arises from guardrail masking (and, in this run, a policy dominated by "Same"), not from evidence that PPO is insensitive to dimension 4. The frozen sensitivity sweep (neutral state) shows only `avg_perf` and `difficulty` change the action. The "historical mismatch" row (0.640 / 0.192) shows the runtime dimension-4 definition matters when guardrails are the only shield (raw runs differ).
- **Evidence:** `FROZEN-VERIFIED` (ablation CSV), `AUDIT-REPLAY` (250/250).

---

## Additional wording corrections carried by this addendum (no new numbers)
- **P1-7:** the deployed checkpoint (`rl/checkpoints/seed_123/ppo_final.zip`, `2ab8d514…4575`) differs from the evaluated one (`research/experiments/paper3/checkpoints/seed_123/ppo_final.zip`, `299437ea…24e0`). Each claim must name its checkpoint.
- **P1-10:** acoustic features do not reach `evaluate`, but a lexical hedging penalty (≤ 0.03) applies to transcripts; "100 % acoustic insulation" is withdrawn.
- **P1-1:** the benchmark README's "8 questions per domain" and "11 categories" are wrong; the data contain 8 questions in total and 10 categories.
- **New in Phase 0 (concurrency latency):** the handoff sentence "write latency scales from 16.3 ms (1 session) to 21.0 ms P95 (25 sessions)" conflates two stored tables. `paper1_concurrency_results.csv` shows per-operation mean latency 16.303 / 83.054 / 181.23 / 419.47 ms and P95 17.938 / 126.497 / 263.788 / 719.124 ms at 1 / 5 / 10 / 25 sessions (0 lock errors, 0 isolation violations); 21.0 ms is the single-session SQLite write P95 in `paper1_latency_results.csv` (n = 25 samples). `FROZEN-VERIFIED`.
- **P1-8:** the evaluator "warm latency mean 1960.8 ms" is contaminated by a cold-start-scale outlier (P99 26 369 ms); report median/percentiles.

## Registered as WITHDRAWN in the claim registry
All strings in `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §H.
