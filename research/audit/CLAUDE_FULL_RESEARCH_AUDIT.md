# CLAUDE Full Research Audit — PREPAIred

**Date:** 2026-09-19 · **Branch:** workspace/human-eval-clean-push · **HEAD:** 8641adf · **Auditor:** Claude Code (independent pass)
**Scope:** verification and recommendations only. No manuscript text, no training, no tuning, no frozen artifact touched.
**Companion files:** `CLAUDE_NUMERICAL_VERIFICATION.csv`, `CLAUDE_IMPROVEMENT_PLAN.csv`, `CLAUDE_STALE_ARTIFACT_AUDIT.csv`, `CLAUDE_TOOLING_STATUS.md`.
**Method note:** Serena's live process was still stale in this session, so code was inspected with Read/Grep. Paper 3 numbers were checked by replaying the *evaluation* loop (no training) from the frozen checkpoints in a scratch directory; every reported Paper 3 table value reproduced exactly, which supports reproducibility of the evaluation but is separate from the interpretive problems below.

## 17/19. Verdict up front

**NOT_READY — FIX REQUIRED.** Headline arithmetic is largely reproducible, but seven P0 issues make several manuscript-level claims unsafe or wrong as currently documented (section 16). None requires changing frozen artifacts; all require user decisions on claim wording, and three (CrossEncoder provenance, Paper 3 framing, Paper 1 fault evidence) may require new, pre-approved work.

## 1–4. Understanding, architecture, data flow, role separation (as verified in code)

- **What:** technical-interview preparation system: text/voice answers scored by a three-signal evaluator; difficulty adapted by a PPO policy behind rule guardrails; Qwen2.5-1.5B produces feedback/follow-up wording; coding answers run in a Docker C sandbox.
- **Stack confirmed:** React/Vite/Monaco (`apps/web/src`), FastAPI backend (`apps/backend/main.py`, 1215 lines), `InterviewOrchestrator` (2163 lines), evaluator (`services/evaluator/app.py`), `ScoreValidator`, SQLite, WhisperX/faster-whisper + Parselmouth audio (`agents/audio`), `HybridOrchestrator` (PPO wrapper). **Absent (not to be imported):** MediaPipe/video, Mistral, ChromaDB, company transfer learning. `requirements/rl.txt` still lists `opencv-python` (unused remnant).
- **Evaluator (verified):** `0.15*S1 + 0.35*S2_eff + 0.50*R (+bonus −penalty)`, cap `min(…, mandatory_cap=0.60)`, `S2_eff = S2` if `R>0.30` else `0.6*S2`, `CONCEPT_THRESHOLD=0.30`, `MANDATORY_THRESHOLD=0.40` (`app.py:95,260,377-393`). Recomputed from stored components: 64/64 rows consistent, 15 rows with R≤0.30. SBERT is loaded by name (`all-MiniLM-L6-v2`, not hash-pinned); CrossEncoder from `models/tuned_model2` (**see P0-1**).
- **Role separation:** Qwen is called only for hints/follow-ups/feedback (`interview_orchestrator.py` ~903-1386, 1626-1692); no path from Qwen text to score, difficulty or `is_best` was found in the greps performed (a full data-flow proof was not attempted). Difficulty comes from `HybridOrchestrator` (PPO) with guardrails; scoring from evaluator → `ScoreValidator` (clamp, NaN/Inf → 0.0 with `is_infrastructure_failure`). Best-attempt selection is database-side (per Paper 1 reports; not re-derived).
- **Acoustic insulation — nuance:** acoustic signal features (prosody, hesitation, confidence from audio) are not passed to the evaluator. However the evaluator itself applies a **lexical hedging penalty on the transcript** (`maybe/not sure/probably/guess/umm/uhh/uh`, −0.03 when content is weak, `app.py:244-252`). "100% insulated" should read "acoustic features never reach the evaluator; a small transcript-hedging penalty exists". No fairness/accent claim is supported.
- **Infrastructure failure semantics (verified in code/tests):** `validated_score=0.0` with `evaluation_status` / `is_infrastructure_failure` flags (4 asserts in the Paper 1 script; `test_score_validator.py`, `test_paper3_blockers.py` pass). RL/UI/best-answer suppression behaviour was covered by the passing integration tests but not independently traced end-to-end.

## 5. Paper 1 (systems/security)

| Claim | Finding |
|---|---|
| 9/9 attacks contained | Reproduced as recorded, but the pass criterion accepts almost any returned status (including `accepted`) and never compares `expected_outcome`. Evidence shows *host survived*, not that each named defence engaged (SEC-02/06/07/09 observed `wrong_answer`). Word conservatively. |
| 10/10 faults recovered | **Not measured by the script.** Every FLT row is a literal `"PASS"` (line 423); only four ScoreValidator asserts execute. Some behaviours may be covered by other tests, but no mapping exists and no test injects a Qwen outage/timeout. **P0.** |
| Qwen 5/5 isolation | Literal `PASS` strings (lines 668-706); architecture supports the claim but the study did not test it. **P0 (same item).** |
| Concurrency 0/0 | Real counters in code (lines 468-530). 287 operations = 7+35+70+175 ✓. Thread-based SQLite operations only (not end-to-end HTTP). |
| Latency | Raw samples not stored. Stored mean/median/P95/P99 imply one ≈32 s first-call sample; "warm mean 1960.8 ms" is contaminated (inferred, not stored). Three inconsistent latency statements exist in the Paper 1 package (40–60 ms; 3.2→11.4 ms; 16→719 ms). |
| Regression 213/1/0 of 214 | No source found; stored report says 213 collected/213 passed/0 skipped; current collection is 226. 78 targeted tests passed in this audit. |

Docker wording ("defence-in-depth, shares host kernel") is consistent with the code and threat model.

## 6. Paper 2 (evaluator alignment)

Independently recomputed from raw files — **MATCH**: Spearman 0.3812 (p 0.00189), Pearson 0.4042, Kendall 0.2715, MAE 0.2920, RMSE 0.3601; all seven ablation correlations; ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff α 0.9523; metamorphic 19/21 (failures META-02/03 MG-5); adversarial 11/13 (ADV-10, ADV-11); hashes of gold, raters, configs. Bootstrap CIs agree to ±0.002 (different resample stream).
Findings a reviewer will raise:
1. **Benchmark composition:** 64 = 8 questions × 8 categories (docs say 10 topics; README says 8 questions/domain, 11 categories). Cases within a question share rubric/reference, so the case-level bootstrap treats clustered cases as independent; no cluster-robust CI was reported.
2. **Error structure:** correct-but-concise/paraphrased answers are strongly under-scored (concise_correct MAE 0.515, model mean 0.40 vs human 0.91; overall bias −0.134). The composite ρ is driven mostly by the wrong-vs-right category contrast.
3. **Full composite < R-only and S1+R** — reported honestly; explanation ("safety-hardened") is a hypothesis, not measured. Unweighted raw 0.15/0.35/0.50 without dampening/bonus/penalty gives ρ=0.4059, so the dampening/bonus/penalty layer costs ≈0.025 ρ (measured), the remainder of the gap versus R-only comes from the S1/S2 mix (measured by the ablations).
4. **Adversarial "contained" = score ≤ author-set ceiling** (0.15–0.85, `adversarial_threshold_provenance.md`); 13 attacks; finite engineering evidence.
5. **CrossEncoder provenance — P0** (below).
6. **Independence of tuning:** θ=0.30 and the R≤0.30 dampening were selected on the N=20 single-rater pilot (`threshold_provenance.md`), which shares 4 of the 8 benchmark questions. The evaluator code (`app.py`) is unchanged since 2026-08-27, before annotation; final gold was not used for tuning (supported by git dates and the frozen configs). The CrossEncoder's fine-tuning data is unidentified, so leakage from it cannot be excluded or confirmed (it predates the benchmark: weights dated April).
7. **Human evidence quality:** hashes and reliability are reproducible; who the raters are, consent/IRB and adjudicator identity are undocumented (ETHICS_CHECKLIST unsigned). Rater files are timestamped 14:21/14:48/14:52 and adjudication 15:07 on the same day as protocol freeze (13:45–13:59) — not proof of anything, but an unexplained-provenance risk a reviewer may question. **Report as documentation gap, not as an allegation.**

## 7. Paper 3 (RL) — most serious findings

Reproduced exactly (replay of frozen evaluation): Fixed 1.200, Heuristic 0.473, seed MAEs 0.687/0.673/0.676/0.673/0.676 (mean 0.6772, SD 0.0055), raw PPO 0.958; checkpoint and result hashes all MATCH.
**But:**
1. **Learned policy adds no measured value beyond guardrails.** Constant "Always-Same + guardrails" (audit diagnostic) = MAE 0.673, volatility 0.080, oscillation 0.000 — the same as or better than guarded PPO (0.673–0.687; vol 0.088–0.268). Raw PPO varies widely across seeds (0.804–1.138, SD 0.161) and almost never chooses Harder in evaluation (0–20/250). The "0.006 seed stability" is the stability of the *guardrail-dominated outcome*.
2. **Heuristic dominates on tracking** (0.473) and, at five seeds, on volatility too (PPO+G 0.186±0.068 vs 0.160; oscillation 0.160 vs 0.000). The "lower volatility 0.088 vs 0.160" is the seed-123 value (the lowest-volatility seed). Guardrails *raise* volatility (0.078→0.186; raw JSON records −140.21%).
3. **Safety claims:** actual out-of-range transitions are 0 for *every* policy because the simulator clips difficulty; attempted pre-clip violations under guardrails = 232 (often more than raw). Report values "0" are hard-coded literals. "563 interventions on 45% of turns" counts rule activations; only 99 (7.9%) changed the PPO action. G4 is immediate ✓ (code confirms; `consecutive_failures` unused for G4).
4. **Frozen-CSV bug:** Safety-Shield ablation rows reuse a leaked loop variable (interventions 112, oscillation 0.187, violations 46/0 belong to the historical-mismatch condition); the report silently shows 563 instead. The frozen CSV therefore disagrees with the frozen report.
5. **Effect size:** d≈0.87 is reproducible (0.865 ddof=0 with seed 123; 0.859 with 0.677; 0.848 ddof=1; paired dz 0.743). p reported as "<0.001" is 0.00108 (paired t) / 0.004 (Wilcoxon) and depends on treating 25 sessions as independent. Effective units are 5 personas (Fixed has 4 unique values; persona-level paired t p=0.204). PPO beats Fixed in only 2 of 5 personas and loses to Heuristic in 2.
6. **Dimension-4 ablation:** identical aggregate MAE and identical final actions (250/250) after guardrails — verified. The stated mechanism ("policy insensitive to s4") is only partly supported: unguarded, zero-progress moves MAE 0.804→0.956 with 23/250 raw actions changed; mismatch-vs-canonical raw differences under guardrails are 10 and all occur where a guardrail is active (claim verified). Equality comes from guardrail masking of a near-constant policy.
7. **Sensitivity sweep contradicts the report's narrative** (only avg_perf and difficulty change the action at the neutral point).
8. **Train/eval mismatch and objective:** training env T=15, continuous difficulty (step 0.1), random start; evaluation loop T=10, integer difficulty (step 1), start 3. Reward is 60% imitation of a hand-coded oracle (whose rules R1/R5 equal guardrails G4/G5); persona target-tracking is not the training objective. Simulation is author-defined (personas, targets, candidate model) — circular by design; only simulation-scoped claims are defensible.
9. **Convergence:** rolling reward is still rising slightly between 12–16k (≈0.16–0.18) and ≥20k (≈0.18–0.20); 12 rollouts total. "Approximately stable" only.
10. **Provenance:** results and checkpoints first enter git at b7cad49 (`v1.0-paper3-complete` annotated tag → b7cad49 ✓); the long SHA in the handoff docs is wrong; `training_meta.json` hard-codes 375f4f8; the app's runtime PPO (`rl/checkpoints/seed_123`, sha 2ab8d514…) is not the evaluated checkpoint (299437ea…).

## 8/9. Numerical and statistical audit
See `CLAUDE_NUMERICAL_VERIFICATION.csv` (61 rows: MATCH / ROUNDING / EXPLAINABLE / MISMATCH / UNVERIFIABLE). Statistical-unit summary: Paper 2 unit = case (clustered by 8 questions); Paper 3 unit = session (clustered by 5 personas; 5 training seeds separate) — seed SD and session uncertainty were kept separate in the reports, but pseudo-replication inflates significance.

## 10. Leakage / contamination
Proven: human gold hash unchanged; gold not used to tune evaluator (app.py last changed 2026-08-27; frozen configs predate annotation); Paper 3 did not touch Paper 2 gold (hash verified at each stage); adjudication rows in gold equal the adjudication form. Not proven: independence of the CrossEncoder fine-tuning data; that the 64 constructed answers are unrelated to pilot answers (question overlap is certain, answer overlap not checked); rater/adjudicator identity and blindness (asserted only).

## 11. Reproducibility
Paper 2: numbers reproduce from stored files. Paper 3: evaluation replay reproduces every table value and all hashes; training not re-run. Environment: `.venv` violates pins (numpy 2.5.2, torch 2.11.0, accelerate 1.13.0); replay still matched. Paper 1: latencies/faults cannot be reproduced from stored artifacts. Git: 375f4f8 full SHA ✓, tag `v1.0-paper3-complete` → b7cad49 ✓, long SHA in docs ✗, results for all three papers first committed at b7cad49, HEAD 8641adf descends from both.

## 12–14. Repository, stale artifacts, claim matrix
Stale-term sweep and classifications: `CLAUDE_STALE_ARTIFACT_AUDIT.csv`. Key: **root `research/CANONICAL_SCIENTIFIC_TRUTH.md` (named "sole authority" in CLAUDE.md) still states ρ=0.6975, N=20** and differs from the handoff copy; `CLAUDE.md` itself is stale. Claim matrix (24 rows): rows 16, 19, 20 (limitation text), 21, 22 (mechanism), 25 and 10 need correction/reclassification; refuted/NOT_SUPPORTED rows were not resurrected. Handoff PAPER*_FINAL_REPORT.md files are byte-identical to `research/results/*`; `FINAL_RESEARCH_MANIFEST.json` copies identical; canonical copies differ.

## 15. Peer-review attack summary
Circularity (Paper 3 oracle/guardrails/personas author-defined); missing control (guardrails-only); heuristic beats PPO; pseudo-replicated sessions; tautological OOB safety metric; weak Paper 1 oracles/hard-coded PASS; CrossEncoder provenance contradiction; clustered 8-question benchmark with systematic under-scoring of concise answers; human-subjects documentation gap; latency contamination. A third researcher could reproduce Paper 2 and Paper 3 tables exactly, but not Paper 1 latency/fault evidence.

## 16. Improvement recommendations (all USER DECISION REQUIRED)
P0 (7): (1) CrossEncoder provenance/fine-tuning data; (2) Paper 3 guardrails-only control / reframing; (3) OOB & violation claim; (4) intervention count wording; (5) volatility claim; (6) Paper 1 fault/Qwen evidence; (7) human-subjects/ethics/rater provenance. P1/P2/P3 items, including frontend accessibility (aria, live regions, explicit infra-failure state), W&B for *new* runs only, docs fixes, are itemised with change type, rerun need and research impact in `CLAUDE_IMPROVEMENT_PLAN.csv`. No technology replacement is recommended; SB3 2.7.1/Gymnasium 0.29.1/wandb 0.30.0 work as installed.

## 18. Unresolved questions for the user
1. What produced `best_model_info.json`/the top-layer changes in `tuned_model2` (data, labels, script, date)?
2. Are the three raters and adjudicator real, independent educators; is consent/IRB documented; was any AI assistance used in ratings or rationales?
3. Should Paper 3 be reframed around guardrails, or extended (new pre-specified controls)?
4. Which CANONICAL file is authoritative going forward?
5. Which checkpoint should the deployed app use?

## 19. Final verdict
**NOT_READY — FIX REQUIRED.** Drafting should wait for decisions on P0-1 to P0-7. Frozen artifacts are intact (hashes verified; `git diff --check` clean; only the five audit files are new). Nothing was written in `research/` other than `research/audit/CLAUDE_*`.
