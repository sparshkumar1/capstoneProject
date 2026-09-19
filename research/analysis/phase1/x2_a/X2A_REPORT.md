# X2-A report - old-benchmark sensitivity / descriptive / exploratory analyses (2026-09-19)

**Every number below is read from the stored X2-A CSV files (`x2a_*.csv`) by `x2a_report.py`.** Data: the frozen 64 constructed answers to 8 questions, whose primary results were already known; question set overlaps the pilot. **No analysis here is confirmatory.** Labels: SENS = sensitivity analysis of a frozen estimand; DESC = descriptive; EXPL = exploratory with a pre-specified rule (hypothesis-generating for X2-C H3). Configuration, seed (42) and B (10 000) were fixed and committed before the run; the analysis was run once (`manifest_X2-A.json`).

## 1. Question-cluster uncertainty for the composite (SENS)
Composite Spearman rho = 0.3812. Two-level cluster bootstrap (resample 8 questions, then answers within question) 95 % percentile interval [0.1529, 0.649]; question-only resampling [0.3066, 0.5888]. The frozen case-level interval [0.1575, 0.5774] treated the 64 answers as independent. R-only: 0.4832 [0.246, 0.6983] (two-level). Only 8 clusters: the interval is coarse. Composite minus R-only: -0.102 [-0.2849, 0.1174] (two-level); the interval includes zero, so the data neither establish nor exclude a difference.

## 2. Influence of single questions and raters (SENS)
- Leave-one-question-out composite rho ranges 0.3517 to 0.4341 across the 8 left-out questions (`x2a_loqo.csv`).
- Rater leave-one-out (gold = mean of the two remaining raters), composite rho: all 64 items 0.3552, 0.3815, 0.3781 (omitting R1, R2, R3); on the 54 non-adjudicated items 0.4147, 0.4499, 0.4618; frozen gold on the 54 non-adjudicated items 0.4454. The frozen gold adjudicated 10 items; the leave-one-out golds do not.

## 3. Structure of the disagreement (DESC)
- Within-question (demeaned) composite rho = 0.5796, higher than the pooled 0.3812: much of the loss of agreement is between questions (composite means differ by question more than human means do; `x2a_per_question.csv`).
- Bias (composite minus human): Bland-Altman bias -0.1338 (95 % limits [-0.7943, 0.5267]); Lin's CCC 0.3297. Spearman correlation of the residual with answer length (words) -0.3077.
- Per-category means and signed bias: `x2a_per_category.csv` (n = 2 to 8 per category; within-category rho computed only for n >= 8 and not interpreted).

## 4. Pilot-overlap contrast (DESC; exploratory; not a held-out validation)
Composite rho on pilot-overlap questions 1 3 10 41 (n = 32): 0.7092; other questions 7 15 22 50 (n = 32): 0.4249. R-only: 0.5838 vs 0.449. Point estimates only; question difficulty also differs between the two sets; this pattern is compatible with, but does not establish, optimism from the pilot-based settings.

## 5. Adversarial false-accept analysis (EXPL; rule pre-specified, data already seen)
Adversarial set = keyword_stuffed, misconception, contradictory, incorrect, verbose_wrong (n = 34); correct-reference set = concise_correct, verbose_correct, suboptimal_correct, paraphrase (n = 22); partial_incomplete excluded from both.
- Threshold-free AUROC (correct-reference vs adversarial), two-level bootstrap: composite 0.7206 [0.5836, 0.8926]; R-only 0.7821 [0.6477, 0.9279]; S1+R 0.7807; S1 0.627. Composite minus R-only -0.0615 [-0.1676, 0.0659] (includes zero).
- Composite at the documented grade boundaries (no explicit accept threshold exists): tau = 0.60: 2 of 34 adversarial answers accepted (false-accept rate 0.0588, cluster CI [0.0, 0.1852]) but only 0.3636 of correct-reference answers accepted; tau = 0.75: 0 of 34 accepted, 0.1364 of correct-reference answers accepted.
- Matched to the composite's accept-rate on the correct-reference set, false accepts at tau = 0.60: R-only 0, S1+R 1, S1 5, S2_eff 4 (composite 2); at tau = 0.75: all 0 for R-only.
- Reading (exploratory): on this seen, constructed set the composite is **not** observed to be safer than R-only or S1+R; H3 (composite false-accept < R-only) is not supported here and should be expected to be at risk in X2-C. The composite is also conservative on correct answers (low accept rate). Adversarial counts are small (34); intervals are wide.

## Not concluded / cautions
No claim of validity, replication or absence of effect follows from any X2-A output. Nothing here sets a parameter of X2-B or X2-C (tau rule, category sets, rho_min, sample size). Registry: only the two-level bootstrap interval is proposed as a scoped VALID sensitivity statement; everything else is DESC/EXPLORATORY.
