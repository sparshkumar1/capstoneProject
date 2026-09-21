# CROSS-PAPER OVERLAP REPORT (2026-09-21)

Method: body text of each `manuscript.md` (comments and reference lists removed) was split into sentences of at least 8 words; exact duplicates and shared 8-word sequences were counted across the three pairs; figures, tables, literature sections, contribution statements and conclusions were then compared by hand.

## 1. Automated results
| Pair | Exact duplicate sentences | Shared 8-word sequences | Nature of shared sequences |
|---|---|---|---|
| Paper 1 – Paper 2 | 0 | 12 | anonymity notice; "the repository has not been publicly released in this draft"; "pins so exact dependency reproduction is not guaranteed" |
| Paper 1 – Paper 3 | 0 | 11 | anonymity notice; "the repository was not pushed to a public registry so ..." |
| Paper 2 – Paper 3 | 0 | 8 | anonymity notice only |

Body lengths (words, tables included): Paper 1 4,337; Paper 2 4,770; Paper 3 4,324. Shared 8-grams are under 0.6% of any manuscript's 8-gram set. No paragraph is copied.

## 2. Manual comparison
| Element | Paper 1 | Paper 2 | Paper 3 | Overlap assessment |
|---|---|---|---|---|
| Opening problem | operator needs to know what containment, authority and failure-handling properties were demonstrated | a single agreement figure hides baselines, clustering and error patterns | learned policy and guardrail bundled, so the learned component's contribution is unclear | distinct |
| Literature sections | sandbox benchmarks, fault injection, grader injection | short-answer scoring, judge biases, gaming, metamorphic testing, clustered bootstrap | RL in education, simple baselines, constraint layers, equivalence testing | no reference is cited by more than one paper (14, 15 and 14 references respectively) |
| Shared system description | one paragraph: orchestrator, evaluator, Qwen feedback, sandbox, SQLite | evaluator formula and cross-encoder only | simulator and guardrail only | The prototype is described only where the study needs it; no paragraph duplicates another |
| Contribution paragraphs | four scoped-evidence items (containment, failure handling, Qwen fixed-turn, status-string oracle) | four exploratory-measurement items (agreement, components/baselines, error analysis, perturbations) | four decomposition items (matched comparison, registered equivalence, guardrail accounting, limits) | distinct; ownership follows the locked division |
| Figures/tables | none shared; planned figures are experiment-specific | none shared | none shared | no duplicated table or figure |
| Conclusions | scoped properties and where evidence stops | exploratory diagnostics and confirmatory requirements | equivalence within margin plus behavioural divergence | distinct |
| Limitations | shares only the generic "repository not released", "no independent reproduction" | same generic statements | same generic statements | Generic reproducibility disclosures repeat by design; content differs |

## 3. Residual overlap and cross-references
- **Shared statements (acceptable):** the anonymity notice; that the repository is not publicly released; that artifact availability is not independent reproduction; that registration tags are local (Papers 1 and 3).
- **Shared numbers/concepts:** none. Paper 1 does not report evaluator accuracy; Paper 2 does not report containment; Paper 3 does not describe the evaluator or sandbox. The composite evaluator appears in Paper 1 only as "an evidence-based answer evaluator" component.
- **Cross-citation:** none of the drafts cites another. Conceptual cross-references (for example, Paper 1 pointing to Paper 2 for evaluator agreement) were not added because none of the papers is published or under review; add after submission status is known.
- **Claim duplication:** no claim is duplicated. The Paper 1 ownership items (containment, authority boundary, failure handling, operational behaviour), Paper 2 items (agreement, diagnostics, error patterns, robustness) and Paper 3 items (learned versus simpler policy under shared guardrails) are disjoint.
- **Risk:** the same project and author-controlled local tagging appear in Papers 1 and 3; a venue that checks for salami publication should see three distinct research questions, data and outcomes. AI-agent assistance in design and execution is disclosed in the Paper 1 draft (its claim matrix records it); whether and how to disclose AI assistance for Papers 2 and 3 is an author decision, because the X2 and X3 execution records were not reviewed for that question in this pass.
