# Scientific Truth — Supersession Record (2026-09-19, Phase 0)

**Purpose.** Designate `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` as the single authoritative current source and record, statement by statement, what in the older canonical files is superseded. **No older file was edited, moved or deleted.** Both remain byte-identical (hashes below) and are read as historical records only.

| File | SHA-256 (verified unchanged in Phase 0) | Status from 2026-09-19 |
|---|---|---|
| `research/CANONICAL_SCIENTIFIC_TRUTH.md` ("root", audited commit `9cfd34f`) | `d8ac0c0ac9ca570d21c5ec2fe41c4784cf22b244c610069a2df6b4b152571a4a` | **Historical / superseded** (declared "sole authority" in the older `CLAUDE.md`; that declaration is withdrawn) |
| `research/CLAUDE_HANDOFF/CANONICAL_SCIENTIFIC_TRUTH.md` ("handoff", cited commit `b7cad49b6b7a…`) | `7714dc1685871766f27add4325eefd108d9688d8b1d3db64393f47fe2bbedce9` | **Historical / superseded** (more recent than root and closer to the frozen results, but contains withdrawn claims) |
| `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` | (living document; version in its changelog) | **Authoritative current source** |

## 1. Source-of-truth hierarchy (from 2026-09-19)
1. Frozen raw result files and their hashes (the number itself).
2. `research/claims/CLAIM_REGISTRY.csv` (permitted wording and status per claim).
3. `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`.
4. This supersession record and the `PHASE0_ERRATA_ADDENDUM.md` corrections.
5. Historical audit and handoff documents (read as history; never as a source of numbers).
6. README, `docs/*`, badges (never a source of numbers).

A lower level never overrides a higher one. If level 3 disagrees with level 1 for a number, level 3 must be corrected.

## 2. Statement-level supersession map

### 2.1 Root file (`research/CANONICAL_SCIENTIFIC_TRUTH.md`)
| Root statement (section) | Status | Current position (authority) |
|---|---|---|
| §D "Verified Human Metric: Spearman ρ = 0.6975 … N = 20 … 1 rater" | **SUPERSEDED as the current human result.** Kept only as a development pilot. | Current human result: 64 constructed answers, 3 raters, ρ = 0.3812 (CURRENT §C); exploratory/initial evidence pending the confirmatory benchmark |
| §M.1 "Human rater ground truth is N=20 expert educator evaluations" | Superseded | CURRENT §C |
| §N Paper 2 "human pilot correlation (ρ = 0.6975)" | Superseded | CURRENT §C |
| §F "Authoritative Training Budget: 300,000 steps (`retrain_quick.py:32`)" | **Does not describe the frozen Paper 3 study** | CURRENT §D.1: 24 576 timesteps per training seed (frozen config) |
| §N Paper 3 "21 % volatility reduction vs heuristic baselines" | Withdrawn | CURRENT §D.2: five-seed guarded volatility 0.186 vs heuristic 0.160 |
| §E "Pedagogical Guardrails (G1–G4)" (G1 low score, G2 hesitation, G3 oscillation, G4 high score) | Does not match the frozen config | Frozen config: G0, G4, G1, G2, G5, G6 (definitions in `frozen_config.yaml`) |
| §K / §I "`FeedbackAgent` validates output against boilerplate, length and contradiction"; "Feedback Validator" | Not supported: no `FeedbackValidator` exists (audit P0-6) | CURRENT §A: feedback is unvalidated |
| §L "205 / 205 PASSED … Frontend 20 / 20" | No stored log in the audited files; a current known failing test exists | Cite only a dated stored test report (X1-D) |
| §O "Publication Venue Plan" (ATIS 2026, ICTCS 2026, SmartCom 2027, dates) | Unconfirmed; project rule says target venue is **TBD** | Not a scientific fact; do not cite |
| §B "Fine-tuned CrossEncoder (`models/tuned_model2/`, base …)" | Directionally correct (the weights are fine-tuned), but training data/code/records are not documented | CURRENT §B |
| §C "100 questions / 100 rubrics / 1,518 vectors / 40 benchmark cases" | Not re-verified in Phase 0 | Treat as `UNVERIFIED` until checked |
| §G "80.50 % action agreement; 0.020 final difficulty discrepancy" | Not re-verified in Phase 0 | `UNVERIFIED` |
| §M.3 "Container cold-start ~1.5 s per compile turn" | Not re-verified in Phase 0 | `UNVERIFIED` |
| §H sandbox flags (`--pids-limit=32`, 128 MB, 64 MB tmpfs, 2.0 s) | Configuration values not re-verified in Phase 0 (handoff says 32 MB tmpfs) | CURRENT §A lists flags only; exact limits from code when needed |

### 2.2 Handoff file (`research/CLAUDE_HANDOFF/CANONICAL_SCIENTIFIC_TRUTH.md`)
| Handoff statement | Status | Current position |
|---|---|---|
| Header "Audited Commit `b7cad49b6b7a54460f4eeb4ecb0292bfcb78e12f`" | **Nonexistent hash** (P1-11) | `b7cad49529c335317ad284dba700f770d1964f6a`; tag `v1.0-paper3-complete` |
| §A/§B "off-the-shelf CrossEncoder"; "Zero-shot"; "no PREPAIred-specific fine-tuning" | **Refuted** (P0-1) | CURRENT §B |
| §C "9/9 (100 %) … contained" | Not supportable (5 of 9 outcomes non-discriminating) | CURRENT §E |
| §C "10/10 (100 %) … recovered gracefully" | Not supportable (literal PASS strings) | CURRENT §E; conditional on X1-A |
| §C "5/5 boundary tests passed … zero authority" | Not supportable as measured (literal strings; no validator) | CURRENT §E; X1-B |
| §C "Write latency scales from 16.3 ms (1 session) to 21.0 ms P95 (25 sessions)" | Conflates two tables: the concurrency file shows per-operation mean latency 16.3 → 419.5 ms (P95 719.1 ms) at 25 sessions; 21.0 ms is the single-session write P95 (n = 25 samples) | CURRENT §E; registry `P1-C002` |
| §C "Warm Evaluator 1960.8 ms mean" | Misleading (mean contaminated by a 26 s outlier) | CURRENT §E (median/percentiles; outlier labelled) |
| §C "Acoustic prosody is 100 % insulated from technical scoring" | Contradicted by a lexical hedging penalty (≤ 0.03) | CURRENT §A |
| §D "3 independent blind CS educators" | Independence, qualifications and blinding are not documented (P0-7) | CURRENT §C.3 |
| §D "Full Composite sacrifices raw correlation to enforce rubric concept coverage and prevent keyword stuffing" | An interpretation, not a tested fact | Test as an adversarial false-accept endpoint (X2-A/X2-C) before asserting |
| §E "Evaluation Unit: Session trajectory (N = 25)" | Pseudo-replicated; the true unit is the **persona** | CURRENT §D.1 |
| §E "Cohen's d ≈ 0.87 (p < 0.001)" | Session-level, pseudo-replicated; persona-level paired t p = 0.204 | CURRENT §D.1 |
| §E "PPO provides lower trajectory volatility (0.088 vs 0.160) and multimodal adaptation" | **Withdrawn** (P0-5; 0.088 is seed 123 only) | CURRENT §D.2 |
| §E "0 actual out-of-bounds transitions … 563 total guardrail interventions" | **Withdrawn** as stated (P0-3, P0-4) | CURRENT §D.2 |
| §E "Dimension-4 ablation collapses … due to low neutral sensitivity of s4" | Reworded (P1-15) | CURRENT §D.2 |
| §E "Training convergence … plateau within 20,000 steps" | Not re-verified | `UNVERIFIED` |
| §F row "ρ = 0.6975 … superseded by 64-case gold benchmark" | Correct as history | Consistent with CURRENT §C |

## 3. Rules that follow from this record
1. Frozen files and both older canonical files stay unchanged. Corrections are new files that cite the old path, line or section, the hash, and the evidence.
2. Any document that carries results has a status (`frozen | superseded | active`) either in its header or in the registry.
3. A number or wording listed as withdrawn (CURRENT §H) must not appear in `paper/`, in the app README or in any new report. The registry script (`research/claims/README.md`, planned) will check this mechanically; until it exists, reviewers check manually.
4. Regenerating a frozen result "to refresh" it is prohibited; regeneration creates a new experiment ID with its own protocol.

## 4. Protection against future sessions reviving superseded values
- `CLAUDE.md` now points to CURRENT and this record, states the current human result and the persona unit, and says ρ = 0.6975 is a superseded pilot.
- The registry marks withdrawn wording explicitly (`status = WITHDRAWN`).
- New sessions read: `CLAUDE.md` → CURRENT → registry. The older canonical files are never used as a source of numbers.
- Any future edit to CURRENT requires a changelog entry and user approval.

## 5. Not done here (by design)
No older file was edited, moved or deleted; no frozen result was touched; no venue decision was made; no unverified value was promoted to a fact.
