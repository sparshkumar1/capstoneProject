# Paper 3 — abstract, keywords, figure/table and reference inventory (draft v1)

## Abstract
In `manuscript.md`; 228 words (limit used: 250; venue limit not verified). It reports the equivalence result, that superiority was not met, the three sensitivity analyses, the non-identical behaviour (563/99, 50/125, higher volatility), and the scope limits.

## Keywords (6)
adaptive difficulty; equivalence testing; reinforcement learning; simulated candidates; rule-based guardrails; technical interviews

## Tables (4 in text)
| # | Reviewer question it answers | Source |
|---|---|---|
| I | What was the registered primary result and margin? | `x3a_decision.json`; `x3a_condition_summary.csv` |
| II | Does the classification survive the registered sensitivity analyses? | `x3a_o7_results.json` |
| III | How often did the guardrail layer act, and how often did it change the action? | `x3_0c_facts.json`; `x3_0c_replay_summary.csv` |
| IV | What do the secondary contrasts (state use, comparators, guardrail on/off, rule ablation) show? | `x3a_secondary_contrasts.csv` |

Policy-comparison design is described in Sections III–IV (text); divergence counts and volatility are in V-D and V-E (text, to be tabulated if space allows).

## Figures (0 generated; 4 planned, all from stored files)
| # | Content | Source |
|---|---|---|
| F1 | Experimental design: policies × shared guardrail layer × personas/seeds; primary and registered sensitivity analyses | design |
| F2 | Equivalence forest plot: registered result and 7 sensitivity intervals against the ±0.12 and −0.20 lines | `x3a_decision.json`; `x3a_o7_results.json` |
| F3 | Guardrail action accounting: activations, overrides by direction and rule (five-persona replay) | `x3_0c_replay_turn_log.csv`; `x3_0c_facts.json` |
| F4 | Volatility: PPO+G, PPO (no guardrail), Constant-Same+G on the grid, and the five-persona replay | `x3a_condition_summary.csv`; `x3_0c_replay_summary.csv` |

## References (14 in text)
| # | Reference | Level | Used for |
|---|---|---|---|
| 1 | Kadam et al. 2026, Simul. Model. Pract. Theory 151, 103316 | publisher landing page (abstract, highlights, contributions); body unread | direct prior art; only verified elements cited |
| 2 | Riedmann et al. 2025, IJAIED 35 | page text read (60,000-character extract) | RL-in-education review statistics |
| 3 | Doroudi et al. 2019, IJAIED 29(4) | author version read | review finding on constrained RL |
| 4 | Sanz Ausin et al. AIED 2020 | summary read; conference year/venue from record | policy vs expert policy |
| 5 | Schmucker et al. arXiv:2508.00270 | text read; preprint | uniform vs contextual policies |
| 6 | Jiang et al. arXiv:2511.15032 | abstract; preprint | similar results of RL and greedy heuristics |
| 7 | Che et al. Sci. Rep. 2025 | PMC page read | single-action collapse |
| 8 | Olukola & Rahimi arXiv:2604.04251 | full text read; preprint | structural constraints vs post-hoc filtering |
| 9 | Alshiekh et al. AAAI 2018 | metadata only; definition not reopened | terminology contrast |
| 10 | Agarwal et al. NeurIPS 2021 | metadata verified | uncertainty over runs |
| 11 | Henderson et al. AAAI 2018 | metadata verified | RL evaluation |
| 12 | Schuirmann 1987 | metadata verified | equivalence (TOST) |
| 13 | Lakens et al. 2018 | metadata verified | equivalence tutorial |
| 14 | Pelánek 2016 | metadata verified | Elo baselines |

Verified references: 14; preprints: 3 ([5], [6], [8]). Sources with UNVERIFIED status in `QUOTE_AUDIT.md` (Alshiekh definition, the "Kaur 2024" item) are not quoted; Alshiekh is cited for terminology only. Not cited: Carr 2023, Axak 2025, Ion 2025, CodeGENCAT 2026 (first-pass, not upgraded). No DOI, page range or venue was added beyond verified entries.
