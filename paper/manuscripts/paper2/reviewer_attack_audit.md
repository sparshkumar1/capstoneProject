# Paper 2 — adversarial reviewer-attack audit (draft v1, 2026-09-21)

Sentences are quoted from `manuscript.md`. Risk is the residual risk in the current draft. The full objection-by-objection analysis is in `PAPER2_HIGH_RISK_REVIEW.md`.

| # | Vulnerable sentence | Attack | Risk | Stronger, truthful wording | Evidence |
|---|---|---|---|---|---|
| 1 N=64 | "The two-level interval spans roughly 0.15–0.65, which is compatible with weak to moderately strong association." | "64 answers cannot support any conclusion." | MEDIUM | Keep; add "the study is not powered to detect a specified effect" only if a power statement is desired; none was computed, so do not add one. | `x2a_bootstrap_rho.csv` |
| 2 8 questions | "With 8 clusters, all percentile intervals are coarse." | "Eight clusters make cluster bootstrap unreliable." | MEDIUM | Already stated; also cite [13] as one-way theory only (done in II). | `x2a_config.json` |
| 3 author construction | "The benchmark is author-constructed, small and not representative of natural candidate answers" | "So the study measures the authors' expectations." | HIGH | Retain; Section VII adds "artifact is possible and the benchmark cannot exclude it". Do not soften. | claim matrix P2-D1; `P0_7` §4 |
| 4 rater independence | "We call the resulting score *three-rater human consensus*." | "Independent? Qualified?" | HIGH | Table I already states not documented. Never add "independent" or "expert". | `P0_7` |
| 5 rater blinding | "they contained no category label and no evaluator score" | "Blinded how? You cannot show what raters saw." | MEDIUM | The sentence is limited to sheet content; Table I row states blinding beyond the sheet is not documented. | rating template header; `annotation_protocol_audit.md` (a design audit, not an attestation) |
| 6 ethics/provenance | "Consent, compensation, ethics or institutional determination — not documented" | "Ethics violation?" | HIGH | Documented as "not documented", which is not "did not occur". Author must decide how to phrase an ethics statement for the venue. | `ETHICS_CHECKLIST.md` (unsigned), `P0_7` |
| 7 p-value | "The stored Spearman p-value for the composite is 0.0018863, a case-level, nominal p-value under independent-case assumptions" | "p-values ignoring clustering are invalid." | LOW | Already labelled; not used as evidence. | `paper2_summary_results.csv` |
| 8 length baseline | "a word-count baseline correlated with the consensus at 0.4897" | "So the evaluator is a length detector." | MEDIUM | "does not show that the evaluator uses length" (present). | `metrics_point_ci.csv`; `x2a_agreement.csv` residual −0.3077 |
| 9 CE provenance | "The training code, training data and hyperparameters could not be recovered." | "Irreproducible; possibly trained on the test set." | HIGH | Retain; "overlap cannot be excluded" is stated. | `P0_1` |
| 10 composite < R-only | "The full composite is not the best-correlating configuration" | "Then why publish the composite?" | MEDIUM | The composite is the system under measurement, not a contribution; the finding is reported. | `paper2_ablation_results.csv` |
| 11 pilot overlap | "compatible with optimism from the pilot-based settings" | "Contamination." | MEDIUM | Keep "not held-out validation"; consider removing "optimism" wording if the venue is strict. | `x2a_overlap.csv`; `X2A_REPORT.md` §4 |
| 12 human agreement | "reflects clearly separated categories" | "ICC 0.95 means the task is trivial." | LOW | Retained: this is the point. | `P0_7` §4 |
| 13 generalisation | "results describe this constructed benchmark" | "Overreach in the title/abstract?" | LOW | Title says "Exploratory". | — |
| 14 adjudication | "the human score for the keyword-stuffed category comes from adjudication alone" | "Category-level results rest on one adjudicator." | MEDIUM | Disclosed in IV and VIII. | `HUMAN_GATE_3_COMPLETION.md` |
| 15 category interpretation | "the pattern is a compressed scale that places correct answers in the 0.3–0.6 range" | "Mechanism claim without test." | MEDIUM | "The mechanism was not tested" follows; the range statement is descriptive (0.361–0.591 means). Consider "on average" if reviewers object. | `x2a_per_category.csv` |
| 16 new descriptive figures | "(D) mean word counts …; 38 of 64 answers" | "Statistics not previously reported." | LOW | Marked (D); user should confirm inclusion. | `scores.csv`; `paper2_case_level_results.csv` |

## Author decisions needed
- Whether to keep the two new descriptive summaries (mean words by category; 38/64 under-scored). Both are read-only arithmetic on frozen files; the second is also recorded in `research/audit/P0_P1_DECISION_PLAN.md`.
- The ethics and rater-provenance disclosure text for the chosen venue.
- Per-question ρ upper end is 0.9048 (rounded 0.90 in the manuscript; the brief's ".91" is not the correctly rounded value).
