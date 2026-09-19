# X2-B report - old-benchmark exploratory arm (2026-09-19)

Protocol `prereg/X2-B/v1`; arm: the frozen 64 constructed answers to 8 questions (EXPLORATORY/SENSITIVITY; the derived model's results on these items were already known). **The X2-C (confirmatory) arm was not run** (blocked by the human/ethics gate). No categorical verdict is drawn; no MAE-type or composite metric is reported for the upstream arm. Gates passed: G-MODEL-HASH, G-METRIC-CONTROLS, G-DERIVED-REPRO; derived-reproduction max |mapped raw - stored R| = 0.000500.

| Scorer | Spearman [CI] | Kendall tau-b [CI] | AUROC correct vs adversarial [CI] |
|---|---|---|---|
| derived_ce | 0.4825 [0.244, 0.6953] | 0.348 [0.1743, 0.5364] | 0.7821 [0.6422, 0.9254] |
| upstream_ce | 0.1454 [-0.1532, 0.4535] | 0.099 [-0.1024, 0.3216] | 0.5842 [0.4076, 0.7732] |
| tfidf | 0.245 [-0.0049, 0.5536] | 0.177 [0.0102, 0.4208] | 0.6364 [0.4787, 0.8121] |
| bm25 | 0.3812 [0.1374, 0.6266] | 0.267 [0.096, 0.4703] | 0.7259 [0.5909, 0.8681] |
| token_overlap | 0.4301 [0.1652, 0.6574] | 0.2996 [0.1037, 0.4943] | 0.7834 [0.6334, 0.9249] |
| length_only | 0.4897 [0.2186, 0.708] | 0.3725 [0.1616, 0.5759] | 0.8864 [0.7838, 0.963] |
| ref_S1 | 0.207 [-0.0231, 0.5027] | 0.1406 [-0.0171, 0.3607] | 0.627 [0.478, 0.8175] |
| ref_S2_eff | 0.3006 [-0.0057, 0.6523] | 0.2528 [0.0062, 0.5526] | 0.6444 [0.4743, 0.8675] |
| ref_R_mapped | 0.4832 [0.2453, 0.6956] | 0.3492 [0.1747, 0.5379] | 0.7821 [0.6422, 0.9254] |
| ref_composite_deployed | 0.3812 [0.1529, 0.6473] | 0.2715 [0.1142, 0.5015] | 0.7206 [0.5769, 0.8943] |

**Primary contrast (derived minus upstream, mapping-independent; two-level cluster bootstrap):** spearman 0.337 [0.0418, 0.6057]; kendall_tau_b 0.249 [0.0339, 0.4595]; auroc 0.1979 [0.0277, 0.3668].
Secondary contrasts against TF-IDF, BM25, token overlap and length-only are in `paired_differences.csv`; permutation-null reference in `permutation_null.csv` (within-question permutations of the human gold). All comparisons are descriptive; no multiplicity control. Cautions: 8 question clusters; constructed answers; labels are construction categories; the upstream model is a public MS MARCO ranking model applied to (question + reference, answer) pairs.
