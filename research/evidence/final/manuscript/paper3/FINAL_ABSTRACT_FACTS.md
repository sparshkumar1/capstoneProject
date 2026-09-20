# Paper 3 - abstract facts (every number from a frozen artifact; see research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md)
- Question: does a learned (PPO) difficulty controller add tracking benefit once rule-based guardrails are present? Simulation only.
- Design: 40 authored personas x 5 training seeds; unit = persona (training seed = second random factor); comparison PPO+guardrails vs state-blind Constant-Same+guardrails; registered margins +/-0.12 (equivalence) and -0.20 (superiority); two-way cluster bootstrap B=10,000, seed 42.
- Primary: delta tracking MAE = -0.0350, 95% CI [-0.0818, +0.0021] -> Equivalent; superiority not met; X3-B not triggered.
- Sensitivity (O7, secondary): reproduced exactly; persona-only -0.0350 [-0.0673, -0.0052]; seed-level t (df 4) [-0.0758, +0.0057]; leave-one-seed-out points -0.0463 to -0.0234; all Equivalent.
- Secondary: PPO more volatile (+0.14877 [0.0666, 0.25445]); PPO uses its observation (zeroed observation +0.36982 MAE); PPO+G below heuristic+G and proportional+G, indistinguishable from oracle-rule+G.
- Guardrail accounting (five-persona frozen study): 563 activations / 1250 turns (45.0%); action overrides 99 / 1250 (7.9%).
- Required qualifiers: equivalence is not "no effect"; simulation only; reward contains oracle-alignment components; authored persona rule; +/-0.12 margin is a design choice; no Elo/IRT/CAT baseline.
