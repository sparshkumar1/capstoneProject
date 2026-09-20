# Paper 2 - abstract facts (frozen artifacts; see research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md)
- Setting: composite technical-answer scorer (0.15*S1 + 0.35*S2_eff + 0.50*R; S2 x0.6 when R <= 0.30) evaluated against three human raters on 64 author-constructed answers to 8 questions (10 answer categories). Exploratory; rater provenance/ethics records incomplete; no confirmatory data (blocked).
- Agreement: Spearman rho 0.3812, case-bootstrap 95% CI [0.1575, 0.5774]; two-level question-cluster interval [0.1529, 0.6490]; question-only [0.3066, 0.5888].
- Human reliability: ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff alpha (interval) 0.9523.
- Components: R-only 0.4832 [0.2501, 0.6762]; S1+R 0.4884; composite minus R-only -0.102 [-0.2849, 0.1174] (two-level interval includes zero).
- Baselines: length-only 0.4897 [0.2186, 0.708] (AUROC 0.8864); derived CrossEncoder 0.4825; BM25 0.3812; TF-IDF 0.245; reference-token overlap 0.4301; upstream CrossEncoder 0.1454 [-0.1532, 0.4535].
- Diagnostics: within-question rho 0.5796; bias -0.1338; Lin's CCC 0.3297; concise-correct and paraphrase answers under-scored; verbose-wrong can be over-scored; metamorphic 19/21; adversarial 11/13 contained against author-set ceilings.
- Required qualifiers: exploratory; small and author-constructed; 8 question clusters; not validated; composite not shown better than simpler signals.
