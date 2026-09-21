# Paper 3 — Evidence Package (simulation-only; frozen X3-A chain)

**Wording alignment (2026-09-21; no number, table, hash or registered conclusion changed).** Framing: controlled policy decomposition / equivalence evaluation of PPO plus an application-level rule-based guardrail versus Constant-Same plus the same guardrail, in simulation; Kadam et al. 2026 is prior art for the application and its simulation-based policy comparison. The word "shield" survives only inside verbatim registered strings and artifact labels and is read as "application-level rule-based guardrail". Status note: §3 below ("O7 NOT RUN") is a superseded status from 2026-09-20; O7 was subsequently run and frozen (see `research/evidence/final/PAPER3_FINAL_EVIDENCE.md`); §3 is left as written for history.

Date: 2026-09-20. Status: **compiled from stored, frozen results; O7 robustness analysis specified and implemented but NOT run** (see §3). Nothing in this file changes a registered result. All numbers below are read from `research/confirmatory/X3-A/results/` or `research/claims/CLAIM_REGISTRY.csv`; none was recomputed in this block.

## 1. Registered primary result (unchanged)
| Item | Value |
|---|---|
| Contrast | PPO+Guardrails (G) minus Constant-Same+G, persona-level tracking MAE |
| Point | −0.03504548324999993 (registered `x3a_decision.json`; −0.0350) |
| 95 % CI (two-way percentile cluster bootstrap, 40 personas × 5 training seeds, B = 10,000, `default_rng(42)`) | [−0.0817733424749999, +0.002138055112500022] ([−0.0818, +0.0021]) |
| Equivalence margin / superiority margin | ±0.12 / 0.20 |
| Registered classification | **Equivalent** (lower > −0.12 and upper < +0.12) |
| Persona-level SD / Cohen's d_z | 0.1015 / −0.345 |
| X3-B trigger | not fired |
| Registered interpretation (verbatim string in `x3a_decision.json`, which uses the word "shield" for the guardrail layer) | "no detectable PPO contribution beyond the shield in these checkpoints (equivalence within ±0.12 MAE)"; manuscript reading: no detectable PPO contribution beyond the application-level rule-based guardrail in these checkpoints (equivalence within ±0.12 MAE) |

The interval crossing zero is **not** re-read as equivalence; the classification follows the registered rule (interval inside ±0.12). Claim IDs: X3A-C001.

## 2. Policy/guardrail comparison (stored per-condition means, 5 PPO training seeds for PPO rows)
Source: `x3a_condition_summary.csv` (values are means per session; the file does not label the stratum; I take it to be the 40-persona grid because Constant-Same+G MAE 1.10386 equals the grid value in X3A-C003). "Activations" = guardrail rules that fired; "overrides" = cases where the final action differed from the policy's proposal; "attempted boundary" = out-of-range action attempts before clamping. Sessions have 10 turns.

| Condition | MAE | Volatility | Oscillation | Activations | Overrides | Attempted boundary |
|---|---|---|---|---|---|---|
| Constant-Same (fixed) off | 1.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| Constant-Same + G | 1.1039 | 0.0975 | 0.0000 | 2.393 | 1.411 | 0.436 |
| Random off | 1.3958 | 0.5686 | 0.5785 | 0 | 0 | 0.983 |
| Random + G | 1.2227 | 0.5115 | 0.5715 | 3.289 | 2.188 | 1.440 |
| Heuristic off | 1.5386 | 0.1825 | 0.0063 | 0 | 0 | 0 |
| Heuristic + G | 1.5330 | 0.1810 | 0.0038 | 2.561 | 0.676 | 0.514 |
| Oracle-rule off | 1.1815 | 0.1576 | 0.0469 | 0 | 0 | 3.161 |
| Oracle-rule + G | 1.1758 | 0.1401 | 0.0421 | 2.696 | 0.395 | 2.938 |
| Proportional controller off | 1.3734 | 0.2554 | 0.2482 | 0 | 0 | 0.001 |
| Proportional controller + G | 1.3697 | 0.2328 | 0.1957 | 2.710 | 1.169 | 0.374 |
| **PPO off (raw)** | 0.9383 | 0.0804 | 0.0745 | 0 | 0 | 0.561 |
| **PPO + G (guarded)** | 1.0688 | 0.2463 | 0.2506 | 3.191 | 1.479 | 1.608 |
| PPO, state zeroed, + G | 1.4386 | 0.2675 | 0.0862 | 2.776 | 1.418 | 6.354 |
| PPO, state shuffled, + G | 1.3226 | 0.3282 | 0.2651 | 2.751 | 1.564 | 2.349 |

Registered secondary contrasts (X3A-C002…C006, persona-level, 40 personas × 5 seeds, two-way bootstrap): PPO+G minus Constant-Same+G volatility **+0.14877 [0.0666, 0.25445]**, oscillation +0.25061 [0.13027, 0.38584]; guardrail on vs off on Constant-Same (labelled "shield" in the registered artifacts): MAE 1.104 vs 1.000 (difference 0.10386 [−0.18375, 0.38796]); PPO uses its observation (zeroed +0.36982 [0.09077, 0.64148]; partner observation +0.25382 [0.10948, 0.41417]); PPO+G lower MAE than Heuristic+G (−0.46414 [−0.7134, −0.22601]) and proportional controller+G (−0.30084 [−0.51982, −0.09469]), not distinguishable from Oracle-rule+G; rule ablation: removing G1 lowers MAE by 0.087 for PPO+G [−0.239, 0.038] and 0.146 for Constant-Same+G [−0.349, 0.036]; removing G2/G4/G5/G6 changes MAE by less than 0.03.

**Reading of the table (descriptive, not new inference).** Under the same guardrails the learned policy's tracking error is equivalent to a state-blind constant action within the registered margin, and its volatility and oscillation are higher. Raw PPO (guardrails off) has lower MAE and volatility than guarded PPO in the stored means; the direction is not tested here and the evaluated checkpoints were **trained with guardrails on** (P3-C019). The Oracle-rule and proportional controller are, per the config, documented as exploiting the persona-target rule (upper *references*, not fair competitors).

## 3. O7 robustness analysis — status **NOT RUN**
- Specification: `research/audit/X3A_O7_SENSITIVITY_SPEC.md` (Revision 3). Implementation: `research/analysis/x3a_o7/x3a_o7.py` (independent of `x3a_analyze.py`; environment/hash assertions; recorded draw order; R0 hard gate; targets read from `x3a_decision.json` only after R0 is computed; A, B, C; write-once outputs). Mechanics self-test on **synthetic** data passed (no frozen data read, no official output written).
- **Why it has not been run:** the specification's execution condition (1b) requires an independent (Codex) review of the R0 code, and condition (2) requires the script/spec to be hashed and tagged with a run manifest. The independent review could not be performed from this session (no Codex access), and no tag was created. The run was therefore held; nothing was approximated or run in the meantime.
- Consequently **this package contains no A/B/C results**. Table row placeholders from the spec (§7) stay "to be computed".

## 4. Claim-per-evidence table
| Claim (allowed wording) | Evidence | Status |
|---|---|---|
| Under identical guardrails PPO's persona-level tracking MAE is equivalent to Constant-Same within ±0.12 (point −0.0350, CI [−0.0818, +0.0021]) | X3A-C001 | VALID, registered, confirmatory-for-this-protocol, simulation only |
| PPO+G is more volatile/oscillatory than Constant-Same+G | X3A-C002 | VALID |
| PPO uses its observation (zeroed/partner observation raise MAE) | X3A-C004 | VALID |
| PPO+G has lower tracking MAE than the frozen heuristic and the proportional controller on the grid | X3A-C005 | VALID (descriptive relation to weak comparators) |
| The application-level rule-based guardrail did not improve constant-Same tracking on the grid | X3A-C003 | VALID |
| Rule G1 removal lowers MAE (CI includes 0) | X3A-C006 | VALID, small |
| Guardrail rules fire far more often than they change the action (frozen five-persona study: 563 activations/1250 turns = 45.0 %, 99 overrides = 7.9 %, attempted out-of-range before clamping 232 = 18.6 %) | P3-C005/C006/C008 | VALID, historical frozen study |
| Tracking MAE cannot distinguish some alternating trajectories (5 of 25 path-differing sessions differ in MAE) | P3-C023 | VALID |
| Frozen PPO trained against one default simulated candidate, unseeded noise, evaluated checkpoint ≠ deployed checkpoint | P3-C016…C019 | VALID limitations |

## 5. Limitations that must accompany every claim
1. **Simulation only**: parametric simulated candidates (sigmoid performance model with noise); no real candidates; no validation of the simulator against real candidates.
2. **Train/eval mismatch**: PPO trained against a single default candidate (skill 0.6, "normal"); 39 of 40 grid personas were not seen in training (a 5-persona frozen stratum is reported separately and is not part of the primary estimate); candidate noise unseeded, so the checkpoints are not regenerable from the recorded seeds.
3. **Reward/oracle coupling**: the persona target is an authored rule (`target = round(10*skill)/2`), and the config documents the Oracle-rule and proportional-controller comparators as exploiting the persona-target rule. Tracking MAE therefore measures agreement with an authored target, not learning benefit. Whether the PPO training reward is coupled to the same oracle rules was **not re-audited in this block**; the limitation is carried forward as recorded.
4. **Guardrails trained-in**: policies were trained with the guardrail layer in the loop (P3-C019); PPO's contribution beyond the application-level rule-based guardrail concerns these checkpoints only.
5. **Seed population is hypothetical** (five trainings); the registered interval treats training seed as a random factor; extrapolation beyond the five checkpoints is limited. The persona set is a factorial grid, not a sample.
6. **Runtime demo is not X3-A evidence**: the runtime policy is `rl/checkpoints/seed_123` with a turn-progress fourth state dimension; X3-A training used a different fourth dimension (`research/audit/rl_state_alignment.md`).
7. Tracking MAE ignores path shape (P3-C023) and equal MAE does not mean equal behaviour.
8. **Action mix and session-level divergence (exact frozen values only).** Training-time Same share 0.5069–0.5345 per training seed (stochastic policy, last logging window; `x3_0a_training_action_shares.csv`; `X3_0A_REPORT.md` item 7). Five-persona frozen replay, 125 PPO+G sessions: final-action sequence differs from Constant-Same+G in 50, executed difficulty path in 25, session MAE in 5; sessions with at least one guardrail override 41 of 125 (`x3_0c_followup.json`; `x3_0c_replay_summary.csv`; P3-C009, P3-C023). The evaluation-time Same share and the session-level divergence on the 40-persona grid are not stored in any summary and are not reported.

## 6. Prohibited claims
PPO improves tracking; PPO is superior; PPO lowers volatility; guardrails eliminate boundary violations (attempted out-of-range actions remain frequent before clamping); the guardrail is described as a formal, safe-RL or verified mechanism, or as providing safety guarantees; PPO, RL for mock interviews, the simulator or a benchmark presented as the contribution; PPO works in real interviews; deployment evidence; speech/multimodal robustness; human learning improvement; "novel"/"first"; reading the interval crossing zero as equivalence; using O7 (when run) to replace or re-label the registered result.

## 7. Provenance
Registered chain: tags `prereg/X3-A/v1` (→ b00541f), `freeze/X3-A/v1` (→ dde2ddf); result hashes in `research/analysis/RESULT_HASHES_phase3.txt`; input `sessions.csv` SHA-256 `dd7eb669e1ffc60957f254e330185d69edf276d578b0b0029efdcf3880f1bcd8` (63,000 rows, 26 conditions); lock `envs/LOCK-X3-2026-09-19` (Python 3.12.7, numpy 2.5.2, scipy 1.17.1; lock.json SHA-256 `c8fdfda1f5034c1d56a27f756907fcb64c3a2b1cdd6e5142b8722a62b658aa03`, requirements SHA-256 `caca8dbf03e7d5dbc9b45b0e314a464c32beccf3768d79b0bd5137c92b7ecb51`). O7 script SHA-256 is recorded in the execution report.
