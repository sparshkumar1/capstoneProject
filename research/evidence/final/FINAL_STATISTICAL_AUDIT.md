# Final statistical / scientific audit (2026-09-20)

**Method.** Read-only script (`stat_audit.py`, scratch copy not committed; logic described here) compared every headline statistic quoted in the three claim matrices with the frozen source artifact (tolerance 6e-4 on values printed to 4 decimals). No value was recomputed from altered data; no frozen file was modified. **Result: 29 headline checks, 0 mismatches** (list below). Values not covered by the script are copied from the claim registry (each row names its artifact and hash) and were not re-derived in this sprint; they are marked *registry*.

## Checked directly against artifacts (all OK)
| Statistic | Artifact | Observed |
|---|---|---|
| Composite Spearman ρ, CI, n | `research/results/paper2/paper2_summary_results.csv` | 0.3812, [0.1575, 0.5774], n=64, percentile bootstrap B=2000 |
| Two-level / question-only intervals | `research/analysis/phase1/x2_a/x2a_bootstrap_rho.csv` | [0.1529, 0.6490] / [0.3066, 0.5888], 10,000 valid replicates each |
| R-only, S1+R, full composite | `research/results/paper2/paper2_ablation_results.csv` | 0.4832 [0.2501, 0.6762]; 0.4884; 0.3812 |
| Derived/upstream CrossEncoder, TF-IDF, BM25, token overlap, length-only | `research/confirmatory/X2-B/results/metrics_point_ci.csv` | 0.4825; 0.1454 [−0.1532, 0.4535]; 0.245; 0.3812; 0.4301; 0.4897 [0.2186, 0.708], AUROC 0.8864 |
| X3-A primary | `research/confirmatory/X3-A/results/x3a_decision.json` | −0.035045, [−0.081773, +0.002138], Equivalent, margins 0.12 / 0.2, 40 personas × 5 seeds, SD 0.101545, d_z −0.3451, X3-B trigger false |
| O7 A / B / C / R0 | `research/analysis/x3a_o7/results/x3a_o7_results.json` | A [−0.06725, −0.005227]; B [−0.075779, +0.005688] (t df 4 = 2.77645, seed-level SD 0.032806); C removed-seed points from −0.0463 (seed 123 removed) to −0.0234 (seed 42 removed); R0 PASS |
| X3-A secondary contrasts | `research/confirmatory/X3-A/results/x3a_secondary_contrasts.csv` | volatility/oscillation, observation-zeroing/shuffle, comparator and G1-removal rows as quoted (the file labels these "descriptive (no error control)") |

## Cross-checks and notes per statistic family
| Family | Exact dataset / N | Method and structure | Seed / software | Exploratory or confirmatory | Multiplicity | Direction check | Population check |
|---|---|---|---|---|---|---|---|
| P2 agreement (ρ, CIs, ablation, baselines) | 64 author-constructed answers, 8 questions, 3 raters | Case bootstrap (independence assumed) **and** two-level/question cluster bootstrap; baselines paired against the same items | B=2000 (case), B=10,000 seed 42 (cluster); env not locked (registry X-C004) | **Exploratory** | Many descriptive contrasts on 64 items; **no correction applied — intervals are descriptive** | Composite below R-only and S1+R (registry P2-C007; two-level difference includes 0) | All P2 numbers refer to the same 64 items; the older ρ 0.6975 (N=20, 1 rater) and 0.74/0.9152/0.8358 are superseded and not used |
| P2 reliability | 64 items, 3 raters | ICC(2,1), ICC(2,k), Krippendorff α (registry P2-C008, *registry*) | — | Exploratory | — | — | Reliability of raters with incomplete provenance |
| P2 diagnostics (metamorphic 19/21, adversarial 11/13, AUROC, τ acceptance) | 21 relation checks; 34 adversarial vs 22 correct | Descriptive counts; percentile AUROC intervals (*registry*) | — | Exploratory | None | Composite − R-only AUROC −0.0615 [−0.1676, 0.0659] (includes 0) | Author-set ceilings |
| P3 primary and O7 | 40 grid personas × 5 training seeds, 20 evaluation seeds per persona (registry X3A-C007 text) | Two-way cluster bootstrap (persona and training seed) B=10,000, seed 42; O7-B seed-level t (df 4); O7-C leave-one-seed-out; equivalence by CI inclusion (95% two-sided CI inside ±0.12) | Locked env `LOCK-X3-2026-09-19`: Python 3.12.7, numpy 2.5.2, scipy 1.17.1 | Primary = registered (locally tagged before running); O7 = registered secondary | Single primary contrast; secondary contrasts uncorrected and labelled descriptive | Negative Δ = PPO+G lower MAE (better); interval crosses 0 → no superiority | Persona = unit; five seeds are a hypothetical population; one seed (123) positive (+0.0100) |
| P3 frozen five-persona study | 5 personas × 5 seeds (registry P3-C002…C009) | Descriptive means/SDs (population SD convention noted, sample SD 0.076) | Frozen checkpoints; candidate noise unseeded | Descriptive | — | — | Different persona set and unit from X3-A; never pooled with it |
| X1 campaigns | 90 / 60 / 72 runs | Deterministic repetitions, per-scenario counts | — | Engineering validation; protocols local-tagged; independent Antigravity methodology review completed (sound only after claim narrowing) | Not applicable (no inference) | — | Two builds reported separately |

## Discrepancies found
1. **None between quoted values and artifacts.**
2. **Interval methods differ across sources and must not be mixed:** R-only has a case-bootstrap interval [0.2501, 0.6762] (ablation file) and a two-level interval [0.246, 0.6983] (`x2a_bootstrap_rho.csv`); the paper must state which method each interval uses.
3. **BM25's ρ equals the composite's to four decimals (0.3812)** in the X2-B file; reported as observed, no interpretation.
4. **Spread convention:** the stored "± 0.068" for guarded volatility is a population SD (ddof=0); the sample SD is 0.076 (registry P3-C020).
5. **Frozen five-persona result vs X3-A:** the heuristic beat PPO in the five-persona study, whereas PPO+G had lower MAE than heuristic+G on the 40-persona grid (−0.46414 [−0.7134, −0.22601]). Different personas, unit and inference; both are reported, never merged.
6. The environment used for frozen results was not a recorded locked environment except X3-A/O7 (`LOCK-X3-2026-09-19`); the `.venv` violates its pins (registry X-C004).

## Not verified in this sprint (registry-only)
P2-C008 (ICC/α), P2-C013 (19/21, 11/13), X2A-C003…C009, X2B-C001…C002, and all Paper 3 descriptive rows other than the checked primary/O7/secondary values. They carry the registry's artifact hashes; a full recompute was not repeated (recompute tiers are in `CLAIM_REGISTRY.csv`).
