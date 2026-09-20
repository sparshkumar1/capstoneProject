# Paper 2 - figure plan (no figure fabricated)
F1 Scatter, composite score (y) vs consensus human score (x), 64 points, colour by answer category, per-question panels optional. Source: paper2_case_level_results.csv. Meaning: modest pooled association, stronger within questions.
F2 Forest plot of rho: composite, R-only, S1+R, length-only, derived CrossEncoder, upstream CrossEncoder, BM25, TF-IDF, reference overlap; x = Spearman rho; intervals from metrics_point_ci.csv (case bootstrap) with the composite also shown with the two-level cluster interval. Meaning: intervals overlap widely; no component is shown better.
F3 Bland-Altman plot, difference (composite - human) vs mean, with limits [-0.7943, 0.5267]. Source: x2a_agreement.csv inputs.
F4 Score vs word count by category (concise-correct, verbose-wrong highlighted). Source: case-level file. Meaning: length dependence.
F5 Leave-one-question-out rho bars (0.3517 to 0.4341). Source: x2a_loqo.csv.
