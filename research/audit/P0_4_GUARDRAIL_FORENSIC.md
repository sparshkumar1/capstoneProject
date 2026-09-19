# P0-4 — Paper 3 guardrail intervention count (563 / 99 / 7.9 %)

Forensic pass, 2026-09-19. No frozen result was modified; no training was run.
Sources: frozen `paper3_seed_results.csv`, `paper3_guardrail_results.csv`, `paper3_raw_results.json`, and a replay of the frozen evaluation code from the frozen checkpoints *(replay; scratchpad only)*. The replay reproduces the frozen per-seed counts exactly (122 / 101 / 115 / 120 / 105).

## 0. Bottom line

- **All three numbers are arithmetically right, but they measure different things.**
  - **563** = guardrail *rule activations* (the frozen field `guardrail_interventions` is incremented whenever any rule matches, whether or not the rule changes the action).
  - **99** = turns on which the guardrail *changed PPO's proposed action* (raw ≠ final).
  - **7.9 %** = 99 / 1,250; **45.0 %** = 563 / 1,250.
- **Denominator (verified):** 5 training seeds × 5 personas × 5 evaluation seeds = **125 guarded sessions × 10 turns = 1,250 turns.** (Per seed: 25 sessions, 250 turns.)
- **The frozen sentence "intervene on 45.0 % of turns to rescue struggling candidates" is wrong.** 82.4 % of activations (464 of 563) left PPO's action unchanged; 44 % of all activations (250) come from the *normal* persona holding "Same"; only 64 turns (5.1 %) made the difficulty lower than PPO proposed.
- Report **two separate measures** (activation rate and override rate) plus the breakdowns in §3, and name them precisely.

## 1. Exact accounting *(replay; 125 guarded sessions)*

| Quantity | Count | Rate |
|---|---|---|
| Turns | 1,250 | — |
| Rule activations (`guardrail_interventions`) | **563** | **45.0 %** of turns |
| Activations that **changed** the action (raw ≠ final) | **99** | **7.9 %** of turns; 17.6 % of activations |
| Activations that **did not change** the action (rule output = PPO's proposal) | **464** | 37.1 % of turns; **82.4 %** of activations |
| Sessions with ≥ 1 activation | 75 / 125 | 60.0 % |
| Sessions with ≥ 1 action change | 41 / 125 | 32.8 % |

### Per training seed (250 turns each)

| Seed | Activations | Action changes | Change rate |
|---|---|---|---|
| 42 | 122 | 37 | 14.8 % |
| 123 | 101 | 12 | 4.8 % |
| 456 | 115 | 20 | 8.0 % |
| 789 | 120 | 18 | 7.2 % |
| 999 | 105 | 12 | 4.8 % |
| **Total** | **563** | **99** | **7.9 %** |

The frozen `paper3_guardrail_results.csv` independently gives **12** changes among the 101 seed-123 rows, matching the replay.

## 2. By rule

| Rule | Activations | Changed the action | No-op activations |
|---|---|---|---|
| G5 partial understanding → Same | 205 | **0** | 205 |
| G4 stuck → Easier | 167 | 15 | 152 |
| G1 overload → Easier | 111 | 49 | 62 |
| G2 anxiety → Same | 80 | 35 | 45 |
| G6 strong performer → Harder | **0** | 0 | 0 |
| G0 infrastructure failure | not exercised (`is_infrastructure_failure=False` in the evaluation call) | — | — |
| **Total** | **563** | **99** | **464** |

Also: `consecutive_failures` is fixed at 0 in the evaluation call, so the "consec < 2" condition of G5 is always true and the failure-count logic is untested in Paper 3. G6 never fires in this study.

## 3. What the 99 overrides actually did

| Direction (PPO proposal → final action) | Turns | Interpretation |
|---|---|---|
| Harder → Easier | 34 | rule stopped an escalation and lowered difficulty |
| Same → Easier | 30 | rule lowered difficulty for a stuck/overloaded candidate |
| Easier → Same | 30 | rule (G2 anxiety) **blocked a decrease** PPO wanted |
| Harder → Same | 5 | rule stopped an escalation |

- Only **64 of 99** overrides (5.1 % of all turns) lowered difficulty relative to PPO's proposal; **30 overrides prevented PPO from lowering difficulty**. Describing the whole 563 as "rescuing struggling candidates" is not supported.
- **39 overrides (3.1 % of turns)** replaced a "Harder" proposal (34 + 5).

### By persona

| Persona | Turns | Activations | Action changes |
|---|---|---|---|
| normal | 250 | **250** (every turn: G5/G2 holding "Same") | **0** |
| struggling_junior | 250 | 202 | 50 |
| overconfident_fail | 250 | 111 (all G1) | 49 |
| nervous_expert | 250 | 0 | 0 |
| lucky_guesser | 250 | 0 | 0 |

The activation count is inflated by the "normal" persona (44.4 % of activations, zero effect). All 99 overrides come from two personas.

## 4. Caveats on interpretation

1. **Path dependence.** After an override the session follows a different difficulty path, so per-turn rates are properties of each executed trajectory. There is no fixed "would-have-been" trajectory; "7.9 %" is not the probability that a raw PPO proposal would be unsafe in general.
2. **Field naming.** In the frozen code the variable is `overridden` / `guardrail_interventions` but it means "a rule matched" (`rl/guardrails.py` returns `True` for any matched rule). The ablation-table entry "PPO + Guardrails (5 Seeds): interventions 112" is the historical-mismatch condition's count (a leaked loop variable at `execute_paper3_study.py:761-775`), not the 5-seed 563.
3. **Frozen trace coverage.** `paper3_guardrail_results.csv` holds **213 rows**: 101 for seed 123 and 112 for the historical-mismatch condition. It does **not** contain "all 563 guardrail activations" as `PAPER3_FINAL_FREEZE.md:26` states; the other four seeds' per-turn traces exist only in a replay, and the 563 is reconstructed from `paper3_seed_results.csv`.
4. **Persona/rule dependence.** The rates are properties of five hand-specified personas; they do not estimate rates for real learners.

## 5. What to report

Give **all of the following, separately labelled** (each value already exists in frozen files or the replay):

1. **Activation rate:** 563 / 1,250 = 45.0 % of turns (rule matched). Name it "guardrail activations", never "interventions"/"rescues".
2. **Override (action-change) rate:** 99 / 1,250 = **7.9 %** of turns (per-seed 4.8–14.8 %), with the direction table in §3. This is the primary "intervention rate".
3. **No-op activation share:** 464 / 563 = 82.4 % (rule agreed with PPO).
4. **Session-level:** 41 / 125 (32.8 %) sessions had at least one override.
5. **By rule and by persona** (§2, §3).

Recommended primary statement (numbers only from this file): "Guardrail rules matched on 45.0 % of turns (563/1,250), but changed the PPO-proposed action on 7.9 % (99/1,250), concentrated in two of five personas and in 41 of 125 sessions."

## 6. What must not be claimed

- "563 interventions / 45 % of turns to rescue struggling candidates".
- "The guardrails overrode PPO on 45 % of turns."
- "Guardrails only ever make difficulty easier" (30 overrides blocked a decrease; G2 holds difficulty).
- Any per-turn safety-outcome claim (no outcome data).

## 7. Classification

`ANALYSIS_ERROR` / `DOCUMENTATION_ERROR` — **the numbers are correct; their description is wrong.** Not an evidence gap: the needed counts exist. **No rerun required.**

## 8. Fix (recommendation only — USER DECISION REQUIRED)

Errata/addendum file replacing the FREEZE §6 wording with §5 above; correct the "trace of all 563" description of `paper3_guardrail_results.csv`; rename the field in any *new* analysis (do not edit frozen artifacts).
