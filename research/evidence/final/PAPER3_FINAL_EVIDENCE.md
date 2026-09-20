# Paper 3 — final evidence integration (2026-09-20)

Supersedes nothing; extends `research/evidence/PAPER3_EVIDENCE_PACKAGE.md` (which said O7 was NOT RUN) with the O7 result. No X3-A rerun, no new training, no new experiment, no change to any frozen artifact.

## 1. Evidence chain (all simulation, all frozen)
| Stage | Evidence | Anchor |
|---|---|---|
| Registered primary (X3-A) | Δ = PPO+G − Constant-Same+G persona-level tracking MAE = −0.0350, 95% CI [−0.0818, +0.0021] (two-way cluster bootstrap, 40 personas × 5 training seeds, B = 10,000, seed 42), margin ±0.12 → **Equivalent**; X3-B trigger not fired | tags `prereg/X3-A/v1`, `freeze/X3-A/v1`; `x3a_decision.json` sha256 `dfa9c0f7…73a0ad`; claim X3A-C001 |
| Secondary sensitivity (O7) | R0 reproduced the registered result exactly (|Δ| = 0.0); A persona-only −0.0350 [−0.0673, −0.0052]; B seed-level t (df 4) −0.0350 [−0.0758, +0.0057]; C leave-one-seed-out points −0.0463…−0.0234, all classes Equivalent; superiority never met | tags `prereg/X3-A-O7/v1` (`5217542e…`), `freeze/X3-A-O7/v1` (`4bcb9696…`); `research/analysis/x3a_o7/results/*` (hashes in `run_record/O7_RUN_RECORD.json`); `O7_INTERPRETATION.md` |
| Descriptive decomposition | PPO+G vs Constant-Same+G: volatility +0.149 [0.067, 0.254], oscillation +0.251 [0.130, 0.386]; PPO uses its observation (zeroed +0.370, partner +0.254); PPO+G lower MAE than heuristic and proportional controller, indistinguishable from Oracle-rule | X3A-C002…C006 |

## 2. Registered interpretation of the combined evidence
Under identical guardrails, in simulation and on the five frozen checkpoints, the learned policy's tracking error was equivalent, within a pre-registered ±0.12 margin, to a state-blind constant action, and this classification did not change under three pre-specified secondary analyses. Its volatility and oscillation were higher. O7 is secondary and does not replace the primary result. Framing: **controlled decomposition / negative-equivalence result**, not PPO superiority.

Qualifiers from O7 that must travel with the claim: the persona-only interval (A) and two leave-one-out intervals exclude zero on the PPO-favourable side, while the registered and seed-level intervals include zero, so "no effect" must not be written; the persona-level SD (0.1015) is ~3× the mean difference; one seed (123) has a slightly positive difference (+0.0100) and seed 42 the most favourable (−0.0816); the closest any interval comes to the lower margin is −0.0948.

## 3. Standing limitations (unchanged)
Simulation only; trained against one default simulated candidate with unseeded noise (checkpoints not regenerable); 39 of 40 grid personas unseen in training; the persona target is an authored rule and the reward/oracle coupling was not re-audited; guardrails were in the training loop; the seed population is hypothetical (five trainings); MAE ignores path shape; the guardrail layer is a rule-based constraint layer, **not a formal shield**; the runtime demo policy differs from the X3-A training state definition.

## 4. What is not supported
PPO improves or is superior on tracking; PPO lowers volatility; guardrails eliminate boundary violations; real-interview, human-learning or deployment claims; speech/multimodal robustness; "no effect" from equivalence; any use of O7 to re-label the registered result.

## 5. Extensions
X3-B (retraining / broader personas) was **not** started and is not triggered by the registered result. If the paper needs a method-level PPO claim, that requires a new preregistration (proposal only; not written here). Literature gaps to close before novelty wording: equivalence-margin justification for tracking MAE; RL-evaluation methodology with matched non-learning controls; CAT/IRT and adaptive-controller literature; persona-simulator validity.

## 6. Readiness
**WRITING READY WITH LIMITATIONS** (see the publication-readiness table in `research/evidence/final/FINAL_MASTER_EVIDENCE_FREEZE.md`).
