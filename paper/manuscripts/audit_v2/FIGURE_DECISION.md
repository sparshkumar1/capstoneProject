# FIGURE DECISION (2026-09-21)

Rule applied: a figure is allowed only if it (1) answers a reviewer question, (2) makes a result easier to interpret, (3) uses frozen data only, (4) creates no new scientific hypothesis, and (5) fits the venue page budget. Decorative architecture diagrams, generic AI diagrams, 3D graphics and marketing figures were not considered. The evaluation-time Same share was **not** computed; no new inferential analysis was run.

## Paper 1 (target ≤ 2; generated 1)
| Candidate | Reviewer question | Decision | Reason |
|---|---|---|---|
| Per-run containment outcomes: attack × shipped/permissive × executor-status identity (Fig. 1) | "What exactly was contained, under which control, and could the status string tell?" | **Generated** | Shows the 9/7/10 denominators, no-control rows, and the status-identity finding in one view; frozen per-run records only |
| Host-observable matrix (canary hits, fork counts, hashes per attack) | "Which observable decided each result?" | Not generated | Duplicates Table II; would cost about a third of a page; the six-page budget for ICETC is tight |
| Fixed-turn matched-pair visual | "How many pairs were valid?" | Not generated | One line in Table IV; a figure would suggest more variation than 72/72 identical equalities contain |

## Paper 2 (target ≤ 3; generated 3)
| Candidate | Reviewer question | Decision | Reason |
|---|---|---|---|
| Composite vs human reference scatter with adjudicated cases ringed (Fig. 1) | "Is the 0.38 a few outliers or the whole cloud? How compressed are the scores? Which points come from adjudication?" | **Generated** | Shows compression below the identity line, the length of the correct-reference cluster, and the provenance of the 10 adjudicated points |
| Forest of Spearman with two-level intervals for configurations and baselines (Fig. 2) | "How do the composite, its components and simple baselines compare, with question-aware uncertainty?" | **Generated** | Single interval type on the whole figure (avoids mixing types); shows that word count and R-only sit above the composite with overlapping intervals |
| Category dumbbell (mean human vs mean composite, n per category) (Fig. 3) | "Where does it err?" | **Generated** | Table VI in visual form; makes the sign pattern (under-scored correct, over-scored incorrect) immediate |
| Question-aware per-question panel | "Does one question drive the result?" | Not generated | Per-question ρ (0.44–0.90, n = 8 each) and leave-one-question-out are in Table III; eight-point panels invite over-reading |
| Length-vs-score scatter | "Show the length confound" | Not generated | Would need word counts per answer; the category word-count means already appear in Table VI; adds a new descriptive panel not previously reported |

## Paper 3 (target ≤ 3; generated 3)
| Candidate | Reviewer question | Decision | Reason |
|---|---|---|---|
| Equivalence interval plot: primary + seven sensitivity estimates against ±0.12 and −0.20 (Fig. 1) | "Reconstruct 'all seven agreed'." | **Generated** | Lets a reader check the claim; frozen decision and O7 files |
| Guardrail accounting: no-match / no-op activation / override, and override direction (Fig. 2) | "How often does the guardrail actually change the action, and in which direction?" | **Generated** | Separates the three counts that were previously conflated; turn log counts only |
| Divergence counts and volatility (Fig. 3, two panels) | "Are the policies behaviourally the same?" | **Generated** | Shows 50/25/5 of 125 with their different definitions and the stored volatility values, including that guarded PPO is *more* volatile than unguarded PPO |
| Separate persona-level MAE distribution | "Where does the mean difference come from?" | Not generated | Persona-level SD is in Table I; a new distribution plot would be a new descriptive analysis |
| Evaluation-time action-share plot | "How often does PPO output Same?" | **Not generated (forbidden)** | The evaluation-time Same share is not stored; computing it would be a new analysis |

## Style and accessibility
Palette: Okabe–Ito subset (blue #0072B2, vermillion #D55E00, green #009E73) plus neutrals; checked with the dataviz palette validator (no FAIL; the pink alternative was dropped; the remaining adjacent CVD separation is in the legal band only with secondary encoding, which every figure has: distinct marker shapes and labels). Text in the ink colour, not the series colour. One axis per plot. Print-ready PDF (Type 42 fonts) and PNG at 300 dpi; single-column (3.5 in) or double-column (7.16 in). Interactivity, tooltips and dark mode are not applicable to print figures.
Not done: colour-contrast check of the light-grey row shading against printing; the figures have not been placed in any venue template.
