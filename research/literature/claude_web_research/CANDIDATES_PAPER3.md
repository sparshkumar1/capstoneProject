# Paper 3 candidates (guardrailed adaptive-difficulty RL). Search date 2026-09-21

Dimensions as in Paper 1 file.

| ID | Source | Year / venue | Status | DT | ME | EV | CO | NT | SQ | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| W3-01 | Kadam, Banerjee, Christopher, Praveen Kumar, Satpathi, *A simulation framework for benchmarking reinforcement learning policies in adaptive mock-interview tutoring*, Simul. Model. Pract. Theory 151, Art. 103316 | Sep 2026 (online 9 Jul 2026), doi 10.1016/j.simpat.2026.103316 | **V-TEXT (abstract, highlights, intro, contributions, section snippets); methods/results paywalled** | 3 | 3 | 3 | 3 | 3 | 3 | Mandatory target. See `CORE_PAPER3.md` for the full comparison |
| W3-02 | Axak, Kushnaryov, Tatarnykov, *Adaptive Learning Control via Proximal Policy Optimization* | ICST-2025, CEUR-WS Vol. 4048, paper 37 | **V-TEXT (PDF text read in part)** | 3 | 2 | 2 | 3 | 3 | 1 | PPO vs DQN vs rule-based tutor in a custom Gym student simulator; single fixed seed, 50,000 timesteps; replay on ASSISTments-2017 |
| W3-03 | Che, Guo, Isleem, Wang, *The necessity of multimodal feedback for learning effective pedagogical policies with RL*, Sci. Rep. | 2025 | V-PAGE (PMC) | 2 | 2 | 3 | 3 | 3 | 2 | PPO tutor with 3 actions; ablated agent no better than random; learned policy chose "repeat" for 99.9% of actions; heuristic "Repeat" reward about equal to PPO |
| W3-04 | Olukola, Rahimi, *Pedagogical Safety in Educational RL*, arXiv:2604.04237 | Apr 2026, preprint | V-PAGE | 2 | 2 | 2 | 2 | 3 | 1 | Reward hacking index; constrained architecture; simulated, 120 sessions |
| W3-05 | Li, Gibbons, Rockova, *Deep Computerized Adaptive Testing*, Psychometrika (arXiv:2502.19275) | 2026 | V-PAGE | 1 | 2 | 2 | 2 | 1 | 3 | Double deep Q-learning for item selection under multivariate IRT |
| W3-06 | *An adaptive testing item selection strategy via a deep RL approach*, Behav. Res. Methods, doi 10.3758/s13428-024-02498-x | 2024 | V-SNIP; authors not verified | 2 | 2 | 2 | 2 | 2 | 3 | DQN item selection vs maximum Fisher information |
| W3-07 | Alshiekh et al., *Safe Reinforcement Learning via Shielding*, AAAI 2018 | 2018 | V-SNIP + metadata (dblp blocked) | 1 | 3 | 0 | 0 | 2 | 3 | Definition source for "shield": safety specified in a temporal-logic fragment |
| W3-08 | Carr et al., *Safe RL via Shielding under Partial Observability*, AAAI 2023, doi 10.1609/aaai.v37i12.26723 | 2023 | V-SNIP (authors CARRY P3-16) | 1 | 2 | 0 | 0 | 1 | 3 | |
| W3-09 | Pelanek, *Applications of the Elo rating system in adaptive educational systems*, Comput. Educ. 98:169-179 | 2016, doi 10.1016/j.compedu.2016.03.017 | V-SNIP + metadata | 2 | 2 | 1 | 3 | 2 | 3 | Elo/IRT-style baseline literature; PrepAIred did not run an Elo/IRT baseline |
| W3-10 | Agarwal et al., *Deep RL at the Edge of the Statistical Precipice*, NeurIPS 2021 | 2021 | V-SNIP + metadata | 0 | 3 | 3 | 0 | 1 | 3 | Reporting practice with few seeds; interval estimates |
| W3-11 | Lakens, *Equivalence Tests: A Practical Primer*, SPPS 8(4):355-362 | 2017 | V-SNIP + metadata | 0 | 3 | 3 | 0 | 1 | 3 | TOST and equivalence bounds |
| W3-12 | Riedmann, Schaper, Lugrin, *RL in Education: A Systematic Literature Review*, IJAIED | 2025 | V-SNIP (89 manuscripts, 2000-2024 per search summary); also CARRY P3-10 | 2 | 2 | 3 | 3 | 3 | 3 | Baseline categories in reviewed studies |
| W3-13 | Doroudi, Aleven, Brunskill, *Where's the Reward?*, IJAIED 2019 (author list not verified) | 2019 | V-SNIP (appears in W3-01 reference list) | 2 | 2 | 2 | 1 | 2 | 3 | |
| W3-14 | Spain et al., *A reinforcement learning approach to adaptive remediation in online training*, J. Def. Model. Simul., doi 10.1177/15485129211028317 | 2022 | V-SNIP (also in W3-01 references) | 2 | 1 | 1 | 1 | 2 | 2 | |
| W3-15 | Pure-Past Action Masking, AAAI 2024 (ojs.aaai.org article 30163) and guard-layer/action-masking papers | 2024-2026 | V-SNIP | 0 | 2 | 0 | 0 | 2 | 2 | Runtime action-restriction family; placement of PrepAIred's guardrail |
| W3-16 | PolyInterview arXiv:2607.10310; *The AI interviewer* Sci. Rep. (article s41598-026-46517-7); Conversate | 2024-2026 | V-SNIP | 2 | 0 | 1 | 0 | 1 | 1 | Adaptive interviewing systems without policy benchmarking |
| W3-17 | *Real-World Testing Matters in RL for Education*, AAMAS 2025 | 2025 | V-SNIP (PDF downloaded, unread) | 1 | 1 | 2 | 0 | 2 | 2 | Would support "simulation-only" limitation; must be read before citing |
| CARRY | P3-01 Ion et al. 2025 (adaptive knowledge assessment in simulated coding interviews), P3-03 Ruan et al. 2024, P3-04..P3-09, P3-11..P3-14, P3-16..P3-23 | various | CARRY | - | - | - | - | - | - | Not re-verified |

Not searched or only touched: knowledge tracing + RL, bandit-based adaptive assessment beyond one CARRY item, curriculum RL (teacher-student), Elo/IRT vs RL head-to-head comparisons, HRL pedagogical policies beyond CARRY. See `UNRESOLVED_GAPS.md`.
