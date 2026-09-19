# X3-0c report - evaluation-only replay of the frozen checkpoints

Environment: `envs/replay-Lobs` (not the project `.venv`); frozen code imported, `main()` never called; manifest `manifest_X3-0c.json`. Evidence label: REPLAY (new derived data; non-locked environment; lock files in `research/locks/`).

**Gate G-REPRO: PASSED** (32/32 checks; guarded activations 122/101/115/120/105 and attempted-boundary 26/71/41/33/61 reproduced exactly; seed-123 activation rows equal the stored guardrail file as a multiset). Details: `x3_0c_gate_G-REPRO.csv`.

G-NEW values (replay; reference values from the earlier audit replay shown for comparison, not as targets):
| Quantity | Replay | Audit value |
|---|---|---|
| Raw PPO attempted boundary actions, 5 seeds (guardrails off) | 136 | 136 |
| Guarded attempted boundary actions, 5 seeds | 232 | 232 |
| Rule activations, 5 seeds | 563 | 563 |
| Action overrides (raw != final) | 99 | 99 |
| Unchanged activations | 464 | 464 |
| Sessions with >= 1 override | 41 of 125 | 41 of 125 |
| Constant-Same + G MAE (25 sessions) | 0.6728 | about 0.673 |
| PPO + G MAE, pooled | 0.6772 | 0.677 |
| PPO raw MAE, pooled | 0.9578 | 0.958 |
| PPO+G sessions whose final-action sequence differs from Constant-Same+G | 50 of 125 | 5 of 125 |

Persona-level paired difference PPO+G minus Constant-Same+G (mean over training seeds): mean 0.0044, SD over the 5 personas (ddof=1) 0.0097 (`x3_0c_persona_paired.csv`; input to the X3-A precision rationale only; n = 5 frozen personas, the checkpoints were trained on one candidate, see X3-0b).

Scope: replay of frozen code on the five frozen personas and evaluation seeds; simulation only; no learner claim; no parameter of X3-A/B is set from these values (pre-run note, non-leakage statements).
