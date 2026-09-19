# X3-0a report - stored-file-only accounting (frozen Paper 3)

Script-generated from the frozen CSV files (no replay, no RNG). Labels: STORED = value read from a frozen file; RECOMPUTED = computed from stored values here. Definitions: `X3_0_PRERUN_NOTE.md`.

1. **Totals (RECOMPUTED = STORED).** Guarded rule activations 563 (122/101/115/120/105); guarded attempted boundary actions 232 (26/71/41/33/61). Denominator: 5 seeds x 25 sessions x 10 turns = 1 250 turns; activation rate 0.450 per turn.
2. **Spread convention.** The stored `0.186 +/- 0.068` is a population SD (ddof=0); the sample SD is 0.076. MAE SD 0.006 is the sample SD (0.0058). State the convention when quoting.
3. **Seed-123 guardrail file (STORED rows).** 101 rule activations but only 12 actually changed the action (11.9 %); historical-mismatch run: 112 activations, 11 overrides. The five-seed override count (99) is NOT recomputable from stored files (only seeds 123 and mismatch stored rows exist) and requires the replay (X3-0c).
4. **Seed-123 attempted boundary actions (STORED).** raw 60, guarded 71: the shield did not reduce attempted boundary actions for this seed (it changes trajectories); "0 violations" refers to the post-clip range, not attempts.
5. **Ablation table provenance (E-10/E-11, RECOMPUTED).** In the "PPO + Guardrails (5 Seeds)" row, MAE and volatility equal the five-seed means, but oscillation, interventions and violations do not (0.187 / 112 / 0 vs five-seed 0.160 / 563 / 232); they trace to the historical-mismatch run (`x3_0a_ablation_provenance.csv`). The three Dimension-4 rows (aligned_progress, aligned_response_time, zero_progress) are identical to all reported digits.
6. **Stored probe sweep (seed-123 checkpoint, other coordinates at the neutral point).** 8 of 66 probes choose a non-Same action; coordinates s0_perf, s2_conf, s3_hes, s4_progress always give Same. This is a descriptive property of one checkpoint at one neutral point, not a general statement about the policy.
7. **Stored training-time action shares (stochastic policy, last logging window).** Same share 0.507-0.534 across the five training seeds.

Not established here: raw attempted boundary total across seeds (136), five-seed override count (99), Constant-Same + guardrails MAE (0.673): replay only (X3-0c, gated).
