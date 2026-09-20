# Paper 2 - result tables (exact frozen numbers; n = 64 answers, 8 questions unless stated)
**Table 1. Agreement of the composite with consensus human score**
| Statistic | Value | Interval |
|---|---|---|
| Spearman rho (pooled) | 0.3812 | case bootstrap [0.1575, 0.5774] (B=2000); two-level cluster [0.1529, 0.6490]; question-only [0.3066, 0.5888] (B=10000, seed 42) |
| Within-question rho (demeaned) | 0.5796 | - |
| Bias vs human / Bland-Altman limits | -0.1338 | [-0.7943, 0.5267] |
| Lin's CCC | 0.3297 | - |
| Leave-one-question-out rho | 0.3517 to 0.4341 | - |
| Leave-one-rater-out rho (all 64 / 54 non-adjudicated) | 0.3552-0.3815 / 0.4147-0.4618 | - |
**Table 2. Human reliability**: ICC(2,1) 0.9528; ICC(2,k) 0.9838; Krippendorff alpha (interval) 0.9523 (3 raters, 64 items).
**Table 3. Components and baselines (Spearman rho vs consensus)**: composite 0.3812; R-only 0.4832 [0.2501, 0.6762]; S1+R 0.4884; composite minus R-only -0.102 [-0.2849, 0.1174]; length-only 0.4897 [0.2186, 0.708] (AUROC 0.8864 [0.7838, 0.963]); derived CrossEncoder 0.4825 (AUROC 0.7821); upstream CrossEncoder 0.1454 [-0.1532, 0.4535] (AUROC 0.5842); BM25 0.3812 (0.7259); TF-IDF 0.245 (0.6364); reference-token overlap 0.4301 (0.7834); derived minus upstream 0.337 [0.0418, 0.6057].
**Table 4. Robustness diagnostics**: metamorphic relations 19/21 (3 base cases x 7 relations); adversarial attacks 11/13 contained against author-set ceilings; adversarial vs correct-reference AUROC composite 0.7206 [0.5836, 0.8926], R-only 0.7821 [0.6477, 0.9279], difference -0.0615 [-0.1676, 0.0659] (34 adversarial vs 22 correct); at tau=0.60 composite accepts 2 of 34 adversarial answers and 0.3636 of correct-reference answers; at tau=0.75, 0 of 34 and 0.1364.
**Table 5. Category means (descriptive; computed from the frozen paper2_case_level_results.csv, read-only)**: category, n, mean human gold, mean model score, difference. verbose_correct 8, 0.984, 0.591, -0.393; concise_correct 8, 0.912, 0.397, -0.515; paraphrase 4, 0.844, 0.361, -0.483; suboptimal_correct 2, 0.725, 0.304, -0.421; partial_incomplete 8, 0.520, 0.207, -0.312; keyword_stuffed 8, 0.305, 0.345, +0.040; contradictory 4, 0.153, 0.281, +0.128; misconception 8, 0.108, 0.228, +0.120; verbose_wrong 8, 0.105, 0.324, +0.219; incorrect 6, 0.087, 0.159, +0.072. No intervals (2-8 cases per category). Reading: correct answers are under-scored in every correct/partial category, including verbose_correct; verbose_wrong is over-scored.
