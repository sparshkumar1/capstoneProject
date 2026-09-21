# P3 INDEPENDENT AUDIT (2026-09-21, audit-v2 pass)

Scope: `paper3/manuscript_v1_archive.md` (audited) → `paper3/manuscript.md` (v2). Evidence re-read (read-only): `research/confirmatory/X3-A/results/x3a_decision.json`, `x3a_secondary_contrasts.csv`, `research/analysis/x3a_o7/results/x3a_o7_results.json`, `research/analysis/phase1/x3_0/x3_0c_replay_turn_log.csv`, `x3_0c_replay_summary.csv`, `x3_0c_facts.json`, `x3_0c_followup.json`, `audit/P0_4_GUARDRAIL_FORENSIC.md`, `evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md`.

## 1. New findings

| ID | Finding | Evidence | Action |
|---|---|---|---|
| P3-F1 | **Prohibited wording present.** The v1 abstract said "the guardrail layer matched on 563 of 1250 turns". | v1 abstract | Replaced everywhere by activation / override / no-op wording; mandated sentence placed at the start of Section V-C (563 activations = 45.0%; 99 overrides = 7.9% of all turns; 464 no-op activations; 41/125 sessions with ≥ 1 override). |
| P3-F2 | "Registered" without qualification implied more than a local tag. | tags are local, unpushed | Global change to "pre-specified"; one definitional sentence (Section IV "Registration status") says the protocol and harness were committed and tagged in the project repository before the run and that no external registry entry was made; contribution list uses "repository-registered". |
| P3-F3 | Override directions. The brief cites 30 blocked decreases and 39 blocked increases, which sum to 69, not 99. Turn-log tally (verified): Easier→Same 30 (blocked decreases), Harder→Easier 34 + Harder→Same 5 = 39 (blocked increases), **Same→Easier 30 (forced decreases)** = 99. | `x3_0c_replay_turn_log.csv`, `PPO+G`: {(Easier,Same):30, (Same,Easier):30, (Harder,Easier):34, (Harder,Same):5}; also `P0_4` §3 | Not a conflict; the brief omitted the third group. All three groups are stated (Section V-C, Fig. 2). |
| P3-F4 | "three registered sensitivity analyses" hid that there are seven estimates (persona-only; seed-level t; five leave-one-seed-out). | `x3a_o7_results.json` A, B, C | Table II now names each analysis, comparison, method, estimate, interval and class; abstract says "seven sensitivity estimates from three pre-specified analyses"; Fig. 1 plots all eight intervals. |
| P3-F5 | The frozen decision JSON's `interpretation_rule` string uses the word "shield" and "beyond the shield". | `x3a_decision.json` | Historical field text; not quoted in the manuscript. The manuscript uses "application-level rule-based guardrail". |
| P3-F6 | Margin wording. v1: "fixed by the study team before the analysis; no literature justification". | — | v2: "pre-specified and author-selected; no external empirical justification was identified, and none is offered here" (Section IV; Related Work; Discussion). |
| P3-F7 | The frozen O7 record labels the seed-level t interval "NOT a replacement CI for the registered estimand". | `x3a_o7_results.json` B.note | Manuscript already states sensitivity analyses are secondary; the phrase "conditional seed-level sensitivity" is implicit in Table II ("five seed-level differences"). |
| P3-F8 | Runtime state mismatch was stated in one clause. | `PAPER3_FINAL_CLAIM_MATRIX.md` P3-F5 | Expanded: the deployed demonstration policy is a different checkpoint from the evaluated seed-123 checkpoint and differs from the training state definition; no claim about the application. |
| P3-F9 | Simulation and reward disclosures were spread across sections. | — | Consolidated in "Scope": authored simulator, personas, target structure, oracle-alignment reward term (0.60), five training seeds as a hypothetical population, training/evaluation differences, no Elo/IRT/CAT baseline. |
| P3-F10 | Missing reviewer answer for "equivalence means PPO adds little". | — | Sentence added to the anticipated-objections paragraph. |

## 2. Area audit

| Area | Status |
|---|---|
| Equivalence | −0.0350 [−0.0818, +0.0021], margin ±0.12: "equivalent under the pre-specified ±0.12 margin"; superiority (upper bound < −0.20) not met. No "as well as in general", no "equally effective". |
| Baseline choice | Constant-Same is a strong reference because start difficulty 3.0 is the centre of the target range (Constant-Same without guardrails MAE = 1.000 by arithmetic (D)); other nulls not run. |
| Margin | author-selected; no external justification. |
| PPO training | five frozen checkpoints, 24,576 timesteps each, one training candidate (persona normal, skill 0.60, target 3.0), unseeded candidate noise → not regenerable. |
| Reward | alignment term (weight 0.60) with an authored oracle; coupling not re-audited. |
| Simulator/targets | authored; not calibrated. |
| Guardrail counting | three counts distinguished (activation / override / attempted boundary action); "interventions" and "violations" not used. |
| Volatility | PPO+G − CS+G +0.14877 [0.0666, 0.25445] (grid); guarded PPO 0.2463 vs raw 0.0804 (grid, point values); five-persona 0.1864 vs 0.0776; Constant-Same+G 0.08. Text: "not smoother", "no claim of reduced volatility". |
| Same-action discussion | training-time Same shares 0.5069–0.5345; 8 of 66 probes non-Same; evaluation-time share **not stored, not computed, not invented**. |
| O7 | seven estimates tabulated; three exclude zero (persona-only; leave out 123; leave out 789), stated. |
| Training/evaluation mismatch | guardrails in the training loop; 15-turn continuous vs 10-turn integer; single training candidate (39 of 40 grid personas unseen). |
| Runtime mismatch | stated (P3-F8). |

## 3. Reviewer attack pass (Phase 14)

| Attack | Manuscript sentence | Survives? | Final wording / action |
|---|---|---|---|
| "±0.12 is arbitrary." | "pre-specified and author-selected; no external empirical justification … was identified, and none is offered here." (IV) | Yes, as a stated limitation | v2 |
| "Your reward contains oracle-like alignment." | "the reward contains an oracle-alignment term (weight 0.60) whose coupling to the authored evaluation target was not re-audited; PPO was not trained to minimise the tracking error, but the alignment may favour the target structure." (VII) | Yes (disclosed) | v2 |
| "Your simulator is authored by the same group." | "The simulator, the persona types and the target rule are authored by the study team. Simulated candidate outputs are not calibrated to real candidates." (III) | Yes | unchanged |
| "You trained on one candidate." | "Each checkpoint was trained against a single default simulated candidate" (III); "39 of the 40 grid personas were unseen" (VII) | Yes | unchanged |
| "Training and evaluation differ." | Section III and VII list guardrails-in-loop, 15 vs 10 turns, continuous vs integer steps | Yes | unchanged |
| "Runtime state differs from training state." | VII: deployed policy is a different checkpoint and differs from the training state definition | Yes | v2 |
| "Constant-Same equivalence means PPO adds little." | new sentence in anticipated objections | Yes (bounded) | v2 |
| "No real candidates, no learning outcome." | Abstract last sentence; VII Scope | Yes | unchanged |
| "You report guarded PPO as smoother?" | V-E: "not smoother … no claim of reduced volatility" | n/a | unchanged |

## 4. Conclusion audit (Phase 13)

| Sentence | Established in |
|---|---|
| "registered persona-level tracking-error difference was −0.0350 …" (now "pre-specified") | V-A, Table I |
| "equivalent within ±0.12 and unchanged under three pre-specified sensitivity analyses" | V-B, Table II (seven estimates) |
| "superiority was not established" | V-A/B |
| "final-action sequences in 50 of 125 … and higher PPO volatility" | V-D, V-E |
| "guardrail activated on 45.0% … changing the selected action on 7.9%" | V-C |
| "findings concern five checkpoints in an authored simulator with an authored margin; no claim about real learners" | VII |
| Future-work sentence (persona-distribution training, rating-system baselines, real candidates) | not a result; stated as future work |

## 5. Verdict
**YELLOW.** Scientifically consistent with the frozen record. Remaining author decisions: whether to keep the descriptive (D) override-direction tally in the paper (it is also recorded in `P0_4` §3), HCII proposal submission (deadline 9 Oct 2026), and AI-use disclosure. Not a submission RED: no ethics-dependent human data are used.
