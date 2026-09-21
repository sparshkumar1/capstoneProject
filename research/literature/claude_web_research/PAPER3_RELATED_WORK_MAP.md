# Paper 3 related-work map (planning only)

| Subsection | Strongest sources | What each contributes | How our work differs | Suggested placement | Do NOT claim |
|---|---|---|---|---|---|
| A. RL for adaptive tutoring and interviews | [26] Kadam 2026; [27] Axak 2025; [28] Che 2025; [36] Riedmann 2025; CARRY Ion 2025, Ruan 2024 | Closest application-level benchmark; PPO tutors; policy collapse; review of baselines | Controlled decomposition, equivalence result, guardrails | II-A (Kadam et al. named as closest) | PPO superiority; "first RL adaptive interview" |
| B. Adaptive testing, IRT, Elo | [30] Deep CAT; [37] DQN item selection; [33] Pelanek 2016; CARRY Vesin 2022 | Mature comparator strand incl. RL vs information-based selection | No Elo/IRT baseline run | II-B; also limitations | That PPO was compared to CAT/Elo |
| C. Safe RL, shielding, runtime enforcement | [31] Alshiekh 2018; [32] Carr 2023; [29] Olukola and Rahimi 2026; action-masking/guard-layer papers (V-SNIP) | Formal shield definition; constraint layers in tutoring RL | Application-level, non-formal rule | II-C | "Shield"; formal safety guarantee; "zero violations" |
| D. Simulation-only evaluation | [26]; [27]; [28] (all simulation); V-SNIP AAMAS 2025 real-world testing paper | Shared limitation; simulator validity is assumption-based | Same limitation, stated | II-D / Section VI | Real-user claims |
| E. Statistical reporting for RL comparisons | [34] Agarwal 2021; [35] Lakens 2017 | Interval estimates with few runs; equivalence testing | Preregistered margin; persona as unit | Section III (methods) | Novelty of the statistics |

Gaps: knowledge tracing + RL, curriculum RL, bandit CAT, and a full read of [26] are not done.

## Gap-closure additions (2026-09-21)
- RL item selection in adaptive testing: [37], [38], [30], [39]. Knowledge tracing with RL: [40]. Bandits in tutoring: [41]. RL versus heuristics in simulated classrooms: [42]. Reviews and evaluation practice: [45], [46]. Interview platforms: [44]. Direct application-level precedent: [26] (partially accessible only).
- Frame Paper 3 against [26] with verified statements only; disclose [28], [41], [42] as observational precedents.

## Final-closure addition (2026-09-21)
Add a paragraph on RL in education reviews (Riedmann et al. [36]; Doroudi et al. [45]) before the application-level precedent (Kadam [26]); position the paper as a controlled decomposition/equivalence study. Cite Olukola and Rahimi [58] for the filter-versus-constraint comparison. See P3_FINAL_NOVELTY_POSITION.md and P3_RL_EDUCATION_REVIEWS.md.
