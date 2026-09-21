# Paper 3 citation map: planned claim -> supporting -> challenging -> wording

| Planned claim | Supporting source(s) | Challenging source(s) | Recommended wording |
|---|---|---|---|
| PPO+guardrail is equivalent to Constant-Same+guardrail (+/-0.12 MAE) in simulation | [35] TOST; [34] interval reporting; [28] (collapsed PPO policy near a constant heuristic) | [27] (claims PPO advantage, single seed) | "statistically equivalent within a preregistered margin; PPO is not shown superior" |
| Application context: RL for adaptive mock-interview tutoring | [26] closest benchmark; [27]; [36] | [26] (occupies the setting) | "closest work benchmarks RL policy classes for mock-interview tutoring; we study a control comparison" |
| The guardrail is application-level | [31], [32] (definition of shield) | [29] (constraints in tutoring RL) | "not a formal shield; no safety guarantee" |
| Heuristic outperforms PPO | [28] (heuristic parity) | [27] (PPO above rule-based; weak protocol) | "descriptive; heuristic is a strong baseline in this simulator" |
| Simulation-only limitation | [26], [27], [28], [29] (all simulation) | none | "no real-user evidence" |
| Missing CAT/Elo comparator | [33], [30], [37] | none | "not run; listed as a limitation" |

## Gap-closure additions (2026-09-21)
| Claim | Support | Challenge | Wording note |
|---|---|---|---|
| Learned policy matches a simple policy | own registered result | [28], [41], [42] report similar patterns | disclose all three |
| Application space | context [44] | [26] occupies it | never claim the setting as novel |
| Constraint layer around a learned selector | own accounting | [38] candidate-window filter; [31] shielding | application-level rule, not a shield |
| RL with IRT/simulated examinees | none needed | [30], [37], [38] | machinery not claimed |
| What [26] lacks | none | unverifiable | do not write |

## Final-closure addition (2026-09-21)
New usable entries: [36] Riedmann et al. (V-TEXT, counts to recheck against print), [45] Doroudi et al. (V-TEXT, author version), [58] MC-CPO (preprint, V-TEXT). Context only: [59]. Do not cite: [60] and its "Kaur 2024" item (UNVERIFIED).
