# P0-5 — Paper 3 "PPO has lower volatility than the heuristic (0.088 vs 0.160)"

Forensic pass, 2026-09-19. Frozen values are **not** replaced; corrections are proposed as an addendum only. No training was run.
Sources: frozen `paper3_summary_results.csv`, `paper3_baseline_results.csv`, `paper3_seed_results.csv`, `paper3_raw_results.json`, `PAPER3_FINAL_REPORT.md`; and a replay of the frozen evaluation code (scratchpad only), which reproduces all per-seed frozen volatilities.

## 0. Bottom line

- **0.088 is the seed-123-only value** (both "PPO Raw (Seed 123)" and "PPO+Guardrails (Seed 123)"). It is not a five-seed aggregate and has no other definition.
- **The five-seed guarded PPO volatility is 0.186 (range 0.088–0.268), which is *higher* than the heuristic's 0.160.** The same frozen summary table lists both.
- **The frozen results already contain the opposite of the "smoother" narrative:** `paper3_raw_results.json` stores `volatility_reduction_pct = −140.21`, i.e. guardrails *increase* volatility by about 140 % relative to raw PPO (0.078 → 0.186).
- The claim as written (PPO < heuristic, 0.088 vs 0.160) is **not supported** in the five-seed evidence. The correct comparison is "no reliable difference (2 of 5 seeds below the heuristic)".

## 1. Definition and provenance

- Volatility = `Σ |Δ difficulty| / max_steps` for each session (`execute_paper3_study.py`, `run_session_trajectory`), then averaged over the 25 sessions of a condition. The heuristic's 0.160 means 1.6 difficulty changes per 10 turns; seed 123's 0.088 means 0.88 per 10 turns.
- Sessions: 5 personas × 5 evaluation seeds, identical for the heuristic and every PPO seed, so a paired comparison is possible.
- Where the claim appears: `research/results/paper3/PAPER3_FINAL_REPORT.md:18`; `research/CLAUDE_HANDOFF/PAPER3_FINAL_FREEZE.md:93`; `MANUSCRIPT_AUTHORING_GUIDELINES.md:21`; `CANONICAL_SCIENTIFIC_TRUTH.md:85`; claim matrix row 20.
- **Why seed 123?** The frozen config (`frozen_config.yaml`) lists five training seeds and **no primary-seed field or rationale**. Seed 123 is hard-coded as the "main" PPO row in the script (`execute_paper3_study.py:575-578, 710-713, 779`) and is also the seed of the legacy checkpoint loaded by the deployed app. The config was committed in the same commit as the results (`b7cad49`), so Git cannot show that seed 123 was designated *before* the results were seen. I make no inference about intent. Of the five guarded seeds, seed 123 has the lowest volatility (0.088; others 0.128–0.268) and is the only one whose paired difference from the heuristic has a CI excluding 0 (§2).

## 2. Evidence *(frozen = replay for every per-seed value)*

### 2.1 Per training seed

| Seed | Raw PPO vol. | Guarded PPO vol. | Guarded − heuristic (0.160), paired over 25 sessions, 95 % bootstrap CI |
|---|---|---|---|
| 42 | 0.160 | 0.268 | +0.108 [−0.032, +0.260] |
| **123** | 0.088 | **0.088** | **−0.072 [−0.112, −0.032]** |
| 456 | 0.036 | 0.208 | +0.048 [−0.064, +0.168] |
| 789 | 0.040 | 0.240 | +0.080 [−0.056, +0.224] |
| 999 | 0.064 | 0.128 | −0.032 [−0.096, +0.032] |
| **Mean over seeds** | **0.078** (SD 0.051) | **0.186** (population SD 0.068 as frozen; sample SD 0.076) | pooled 125 sessions: **+0.026 [−0.024, +0.078]** (pseudo-replicated by seed) |

- Guarded seeds below the heuristic: **123 and 999 (2 of 5)**. Raw seeds below the heuristic: 123, 456, 789, 999 (4 of 5).
- Guarded oscillation rate by seed: 0.261 / 0.027 / 0.197 / 0.178 / 0.139 (mean 0.160) vs heuristic 0.000. (The frozen 5-seed oscillation "0.160" is numerically equal to the heuristic's volatility "0.160" — different metrics, easy to confuse.)
- The "± 0.068" in the frozen table is a population SD (ddof = 0); the sample SD is 0.076.

### 2.2 The direction of the guardrail effect on volatility

Raw PPO mean volatility 0.078 → guarded 0.186 (frozen: `volatility_reduction_pct = −140.21`). The low volatility belongs to the *unguarded* PPO (which mostly proposes "Same" — 67–96 % of its actions by seed), and the guardrails raise it about 2.4× (0.078 → 0.186). The claim that the guarded system is "smoother than the heuristic" mixes a raw-PPO property with a guarded-system result.

### 2.3 Low volatility is largely inactivity, not smooth adaptation

| Persona | Heuristic vol. | PPO+G seed 123 | PPO+G 5-seed mean | Const-Same+G (control) | Heuristic MAE | PPO+G MAE |
|---|---|---|---|---|---|---|
| normal | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| nervous_expert | 0.200 | **0.000** | 0.000 | 0.000 | 0.591 | 1.500 |
| lucky_guesser | 0.200 | **0.000** | 0.000 | 0.000 | 0.909 | 1.000 |
| overconfident_fail | 0.200 | 0.240 | **0.688** | 0.200 | 0.591 | 0.591 |
| struggling_junior | 0.200 | 0.200 | 0.244 | 0.200 | 0.273 | 0.273–0.346 |

- PPO+guardrails never changes difficulty for the two high-skill personas (volatility 0), and there its MAE equals the fixed baseline's (1.5 and 1.0); the heuristic changes difficulty there and tracks better. Lower volatility here reflects **not adapting**.
- Volatility concentrates in *overconfident_fail* under guardrails (0.688 vs the heuristic's 0.200). A constant "Same" policy with the same guardrails has volatility 0.080, close to seed 123's 0.088. So seed 123's number is what a state-blind "Same"-mostly policy gives.
- Volatility is a cost-side statistic; reporting it alone favours doing nothing (the Fixed baseline has volatility 0).

## 3. Correct comparison against the heuristic

Using only frozen values plus the paired replay:

- Same 25 sessions per condition; heuristic volatility 0.160 (MAE 0.473).
- Guarded PPO across five training seeds: volatility **0.186** (0.088–0.268), MAE **0.677**; per-seed contrasts in §2.1; pooled contrast **+0.026 [−0.024, +0.078]** — *no reliable difference*, with the caveat that the pooled interval treats 125 sessions from five checkpoints as independent (the seed is the replication unit for training variability; persona for evaluation variability).
- Raw PPO: volatility 0.078, MAE 0.958 (worse tracking than both the guarded system and the heuristic).
- **The defensible statement is a trade-off table, not a superiority claim:** heuristic (0.473 MAE, 0.160 vol., 0 oscillation) vs guarded PPO (0.677, 0.186 [0.088–0.268], 0.160 oscillation) vs raw PPO (0.958, 0.078). The heuristic is better on tracking and oscillation; volatility is not distinguishable.

## 4. What can and cannot be claimed

**Supportable:** "Across five training seeds, PPO+guardrails volatility ranged 0.088–0.268 (mean 0.186) against 0.160 for the heuristic; two of five seeds were lower. Guardrails increased volatility relative to raw PPO (0.078 → 0.186)."
**Not supportable:** "PPO has lower volatility than the heuristic (0.088 vs 0.160)"; "PPO provides smoother curriculum pacing"; "guardrails reduce volatility"; any statement attributing the 0.088 to PPO rather than to a seed.

## 5. Fix (recommendation only — USER DECISION REQUIRED)

- Addendum/errata replacing the seed-123 comparison with the five-seed table in §2.1/§3; keep the frozen values as the historical record; do not edit `PAPER3_FINAL_REPORT.md` or the handoff files.
- If a volatility advantage for PPO is to be claimed at all, it needs a pre-specified analysis (see P0-2 §5): more personas, seed as replication unit, guardrail-only control, and a joint MAE-volatility criterion.
- **Rerun required? No** for the correction; every number already exists.

## 6. Classification

`ANALYSIS_ERROR` (single-seed value presented as PPO's volatility; comparison contradicts the five-seed table and the stored `volatility_reduction_pct`). Not an evidence gap.
