# Phase 1 completion report (2026-09-19)

**Status: COMPLETE. Integrity: PASS** (`research/analysis/phase1/PHASE1_INTEGRITY_REPORT.md`). All Phase-1 work is exploratory/descriptive re-analysis of frozen evidence; nothing is confirmatory; no frozen artifact was modified; the project `.venv` was not modified.

## 1. What was done
| Step | Output (new files under `research/analysis/phase1/`) | Label | Manifest |
|---|---|---|---|
| 1A Paper 1 stored data | `paper1/`: `p1_claim_survival.csv` (41 statements), security oracle check, concurrency and latency re-analysis, `P1_STORED_ANALYSIS_REPORT.md` | PHASE1-STORED | `manifest_P1-STORED.json` |
| 1B X2-A | `x2_a/`: config + pre-run note committed before the single run; 13 result tables; `X2A_REPORT.md` | sensitivity / descriptive / exploratory | `manifest_X2-A.json` |
| 1C X3-0a stored files | `x3_0/`: seed table, spread conventions, ablation provenance, activations vs overrides, probes, `X3_0A_REPORT.md` | PHASE1-STORED | `manifest_X3-0a.json` |
| 1C X3-0b static code | `x3_0/X3_0B_STATIC_CODE_NOTE.md` (N1, N2, new N9, N10) | CODE | - |
| 1C X3-0c replay | `x3_0/`: gate G-REPRO, replay summary, persona paired table, turn/session logs, follow-up, `X3_0C_REPORT.md` | PHASE1-REPLAY | `manifest_X3-0c.json`, `manifest_X3-0c-followup.json` |
| 1C X3-0d integrity | `PHASE1_INTEGRITY_REPORT.md` | - | - |
| Registry | `research/claims/CLAIM_REGISTRY.csv`: 43 -> 101 rows; `P3-C007/8/9` now VALID (replay); registry README updated | - | - |
| Tooling | `research/tools/run_manifest.py`; `envs/replay-Lobs` (git-ignored) with lock record `research/locks/replay-Lobs.*` | - | - |

## 2. Key findings (all traceable to the artifacts above)
**Paper 1 (stored data).** Of 41 statements: 10 VALID, 13 WITHDRAWN, 8 DESIGN-ONLY, 8 EXPLORATORY, 2 HISTORICAL. 4 of 9 attacks have `observed_status == expected_outcome`; `host_safe` is a literal; fault (10/10) and Qwen (5/5) PASS values are literals; `FeedbackValidator` exists in no source file. Latency resolved: the 21.0 ms figure is the P95 of 25 sequential uncontended writes; 419.5 ms / 719.1 ms are per-operation figures under 25 threads (throughput flat at 47-52 ops/s, closed-loop ratio 0.80-0.85). The stored evaluator mean, P95 and P99 are all set by one sample (derived about 32.4 s); the median 404.6 ms is the only warm-representative stored value. The "150-200 ops/s ceiling" and the summary text "40-60 ms / <15 ms / All < SLA" have no supporting measurement.
**X2-A (old 64-case benchmark).** Composite rho 0.3812: two-level cluster CI [0.1529, 0.6490] (question-only [0.3066, 0.5888]). Composite minus R-only -0.102 [-0.285, 0.117]. Within-question rho 0.580 (pooled 0.381): much of the loss is between questions. Composite bias -0.134 (CCC 0.330). Pilot-overlap 0.709 vs 0.425 (descriptive). Rater leave-one-out 0.355-0.382; on the 54 non-adjudicated items 0.415-0.462. Exploratory adversarial analysis: composite AUROC 0.721 vs R-only 0.782 (difference includes zero); composite accepted 2 of 34 adversarial answers at tau 0.60 (and only 36 % of correct-reference answers), R-only 0 at the matched accept-rate. **The composite is not observed to be safer than R-only; H3 of X2-C is at risk.**
**X3-0 (frozen Paper 3).** Gate G-REPRO passed 32/32 in the separately built environment. Replay: raw attempted boundary actions 136, overrides 99, unchanged activations 464, 41 of 125 sessions with an override, Constant-Same+G MAE 0.6728 (PPO+G 0.6772), Constant-Same+G volatility 0.080 vs PPO+G 0.186. Persona-level PPO+G minus Constant-Same+G: mean 0.0044, SD 0.0097 (n = 5; descriptive). "5 of 125 sessions differ" refers to session MAE; the executed path differs in 25 and the action sequence in 50 (MAE is blind to oscillation about half-integer targets). Stored data: 12 of 101 seed-123 activations changed the action; spread convention of 0.068 is a population SD.
**New static findings.** N1/N10 (single default training candidate, three training scripts), N2 (unseeded candidate RNG), **N9: the training environment applied the shield in the loop** (frozen PPO was trained with guardrails on). These change how X3-A must be worded and how X3-B must be specified (D-N2).

## 3. Verification
- Frozen baseline: 366 / 366 hashes identical; gold, CrossEncoder, Paper-3 config and both seed-123 checkpoints unchanged.
- 5 run manifests: status completed, inputs unchanged before/after, outputs re-hashed, no failures; X3-0c gate recorded.
- Registry: 101 unique IDs; no PENDING-REGISTRATION rows; T1 artifact hashes verified on 86 rows; every Phase-1 VALID/EXPLORATORY row has an artifact hash. Exploratory labels: X2A-C006, C008, C009 EXPLORATORY; X2-A intervals VALID as sensitivity statements only.
- Tracked-file changes: only the pre-existing `.env.example`; Phase-1 commits `fb969b2`, `d9ba681`, `9e982fe`, `3cc4191` (all on `workspace/human-eval-clean-push`; nothing pushed).
- Pre-existing `__pycache__` files under `research/scripts` and `rl` date from 16:06-16:47 (before this work); Phase-1 processes ran with `-B`.

## 4. Deviations and limitations (stated, not repaired)
- The replay environment lock records versions but not wheel hashes (`--no-cache-dir` install); a hash-pinned lock is required before any confirmatory run.
- The project-level environment remains unlocked; numpy 2.5.2 and torch 2.11.0 violate `requirements/*.txt` pins exactly as the `.venv` does.
- X3-0 outputs were seen before X3-A is tagged (disclosed; no parameter of X3-A/B is derived from them).
- The audit statement "5 of 125 sessions differ" was under a different definition; not forced to match.

## 5. Gate to Phase 2
Integrity passed; no unresolved frozen-hash issue. Open decisions and blockers are in `SPRINT_DECISIONS_AND_BLOCKERS.md`.
