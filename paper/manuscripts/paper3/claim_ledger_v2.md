# PAPER 3 — CLAIM LEDGER v2 (audit-v2 reconciliation, 2026-09-21)

Covers claims whose wording changed in manuscript v2 or that were verified anew; unchanged claims remain in `claim_ledger.md` (v1), whose wording is superseded where it conflicts. Paths under `research/`. Types: PRE = pre-specified primary; SENS = pre-specified sensitivity; DESC = descriptive; LIM = limitation.

| ID | Claim | Source file | Source line/artifact | Result | Type | Safe wording (v2) | Risk | Paper | Section |
|---|---|---|---|---|---|---|---|---|---|
| L2-P3-01 | Primary equivalence | `confirmatory/X3-A/results/x3a_decision.json` | primary contrast | Δ −0.0350; [−0.0818, +0.0021]; margin ±0.12; Equivalent; superiority (upper < −0.20) not met | PRE | "equivalent under the pre-specified ±0.12 margin" | High | P3 | Abstract, V-A |
| L2-P3-02 | Seven sensitivity estimates all Equivalent | `analysis/x3a_o7/results/x3a_o7_results.json` | A, B, C | −0.0350 [−0.0673, −0.0052]; −0.0350 [−0.0758, +0.0057]; LOSO: −0.0234, −0.0463, −0.0335, −0.0372, −0.0348 with intervals in Table II | SENS | "seven sensitivity estimates from three pre-specified analyses" | Medium | P3 | V-B, Fig. 1 |
| L2-P3-03 | Margin is author-selected | `experiments/paper3/frozen_config.yaml`; `X3-A` protocol | — | no external empirical justification found | LIM | "pre-specified and author-selected; … none is offered here" | High | P3 | IV, VI |
| L2-P3-04 | Repository-registered protocol | git tags (`git tag -l`) | X3 tags | local, unpushed | DESIGN | "committed and tagged in the project repository before the run; no external registry entry was made" | Medium | P3 | IV |
| L2-P3-05 | Guardrail activation | `analysis/phase1/x3_0/x3_0c_replay_turn_log.csv` | `PPO+G`, `activation` | 563 of 1250 (45.0%) | DESC | "activated on 563 of 1250 turns (45.0%)" — never "matched" | **High** (v1 error) | P3 | Abstract, V-C |
| L2-P3-06 | Action overrides | same | `override` | 99 of 1250 (7.9%); 464 no-op activations | DESC | "changed the selected action on 99 (7.9% of all turns) … 464 no-op activations" | High | P3 | V-C |
| L2-P3-07 | Sessions with at least one override | same | grouped by session | 41 of 125 | DESC | as stated | Low | P3 | V-C |
| L2-P3-08 | Override directions | same | (raw_action, final_action) | Easier→Same 30; Same→Easier 30; Harder→Easier 34; Harder→Same 5 (sum 99) | DESC (D) | "30 blocked decreases; 39 blocked increases (34 + 5); 30 forced decreases" | Medium | P3 | V-C, Fig. 2 |
| L2-P3-09 | Divergence counts | `analysis/phase1/x3_0/x3_0c_followup.json` | — | final-action sequence 50/125; executed path 25/125; session MAE 5/125 | DESC | three definitions, never interchanged | Medium | P3 | V-D, Fig. 3 |
| L2-P3-10 | Boundary-saturated attempted actions | `x3_0c_replay_summary.csv` | `attempted_boundary_final_action` | 232 (guardrails) / 136 (raw PPO) | DESC | "boundary-saturated attempted actions before simulator clipping"; not "violations" | Medium | P3 | Table III |
| L2-P3-11 | Volatility (grid) | `confirmatory/X3-A/results/x3a_secondary_contrasts.csv` | PPO+G − CS+G, volatility | +0.14877 [0.0666, 0.25445] | DESC | "more volatile; no claim of reduced volatility" | Medium | P3 | V-E |
| L2-P3-12 | Volatility (replay) | `x3_0c_replay_summary.csv` | pooled | PPO+G 0.1864; PPO raw 0.0776; Constant-Same+G 0.08 | DESC | Fig. 3B | Medium | P3 | V-E |
| L2-P3-13 | Training-time Same share | `x3_0a_training_action_shares.csv` | last logging window | 0.5069–0.5345 | DESC | evaluation-time share **not stored, not computed** | Medium | P3 | V-G |
| L2-P3-14 | Reward contains an oracle-alignment term (0.60); coupling not re-audited | `experiments/paper3/frozen_config.yaml`; `rl/env/interview_env.py` | reward weights | as stated | LIM | as stated in Scope | High | P3 | III, VII |
| L2-P3-15 | Training vs evaluation and runtime mismatch | `PAPER3_FINAL_CLAIM_MATRIX.md` P3-F5; `X3_0B_STATIC_CODE_NOTE.md` | — | guardrails in loop; 15 vs 10 turns; continuous vs integer; single training candidate; deployed policy differs | LIM | as stated | High | P3 | III, VII |
| L2-P3-16 | Kadam et al. as direct prior art (abstract-level reading) | https://doi.org/10.1016/j.simpat.2026.103316 | landing page | QA 3.1/5.1/5.5 | external | "body not read" retained | Medium | P3 | I, II |
