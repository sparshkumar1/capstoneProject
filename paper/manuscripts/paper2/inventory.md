# Paper 2 — abstract, keywords, figure/table and reference inventory (draft v1)

## Abstract
In `manuscript.md`; 221 words (limit used: 250; venue limit not verified). It states "exploratory", the two interval types, that the full composite correlated below two of its components, the word-count baseline, the under-scoring pattern, 19/21 and 11/13, and the non-validation scope.

## Keywords (6)
automatic short-answer scoring; evaluator diagnostics; human agreement; cluster bootstrap; length dependence; metamorphic testing

## Tables (5 numbered in text)
| # | Reviewer question it answers | Source |
|---|---|---|
| I | What is and is not documented about the raters? | `P0_7_HUMAN_ETHICS_FORENSIC.md`; rating template |
| II | How does the composite agree with humans, with which interval? | `paper2_summary_results.csv`; `x2a_*.csv` |
| III | What do the components and combinations achieve? | `paper2_ablation_results.csv` |
| IV | What do simple baselines achieve? | `X2-B/results/metrics_point_ci.csv`, `paired_differences.csv` |
| V | Which answer types are mis-scored, and how do the categories differ in length? | `x2a_per_category.csv`; `scores.csv` (D) |
| (in text) | Metamorphic and adversarial results | `paper2_metamorphic_results.csv`; `paper2_adversarial_results.csv` |

Human reliability (three coefficients with intervals) is in text and not tabulated.

## Figures (0 generated; 4 planned, all from stored files; none drawn yet)
| # | Content | Source |
|---|---|---|
| F1 | Evaluator measurement pipeline: benchmark → deployed evaluator → three-rater consensus → analyses (three interval types marked) | design |
| F2 | Scatter of composite versus consensus (64 points, colour by category), with per-question means | `paper2_case_level_results.csv` |
| F3 | Forest plot of ρ for composite, components and baselines, showing case-level and two-level intervals side by side | `paper2_ablation_results.csv`; `x2a_bootstrap_rho.csv`; `metrics_point_ci.csv` |
| F4 | Signed error by answer category (mean composite − human) with per-item points | `x2a_per_category.csv` |

Optional: word count versus score by category; leave-one-question-out bars.

## References (15 in text)
| # | Reference | Level | Used for |
|---|---|---|---|
| 1 | Kabra et al. 2020, arXiv:2007.06796 | abstract read; preprint | scorer overstability/gaming |
| 2 | Powers et al. 2002, Comput. Hum. Behav. | metadata verified | gaming of automated essay scoring |
| 3 | Moon et al., EACL Findings 2026 | text read (quote verified) | surface-variation bias |
| 4 | Schleifer et al., BEA 2026 (arXiv:2605.07647) | text read; workshop paper/preprint | mid-range degradation |
| 5 | Norman et al., arXiv:2606.19544 | text read; preprint | verbosity bias magnitude |
| 6 | Zheng et al., NeurIPS D&B 2023 | phrase verified | judge biases |
| 7 | Deng et al., arXiv:2601.08843 | abstract level; preprint | synonym sensitivity |
| 8 | Willis & Third, BEA 2026 | page metadata | hybrid graders |
| 9 | Filighera et al., AIED 2020 | title level; DOI from publisher URL | fooling short-answer graders |
| 10 | Yarmohammadtoosky et al., arXiv:2505.00061 | title level; preprint | grader defences |
| 11 | Ribeiro et al., ACL 2020 | metadata verified | behavioural testing |
| 12 | Cho et al., arXiv:2511.02108 | v1 text read; venue not verified | metamorphic testing catalogue |
| 13 | Field & Welsh 2007, JRSS B | metadata verified | clustered bootstrap |
| 14 | Koo & Li 2016 | metadata verified | ICC reporting |
| 15 | Li et al., arXiv:2512.14561 | phrase verified; preprint | agreement is context-dependent |

Verified references: 15. Preprints: 7 ([1], [5], [7], [10], [12], [15], and [4] as arXiv/workshop). Sources whose quote status is UNVERIFIED in `QUOTE_AUDIT.md` (Ye et al., Williamson et al.) are not cited. No new DOI, page number or venue was added.
