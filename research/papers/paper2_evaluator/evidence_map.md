# Paper 2 Evidence Map
| Claim / RQ | Evidence Asset | File Path | Metric / Finding |
|---|---|---|---|
| Human Alignment | 7-Way Ablation Benchmark | 	ables/table_eval_ablation.md | $\\rho = 0.7400$ ( < 0.001$),  = 0.6690$, MAE .2092$ vs Human Rater 1 |
| Anti-Gaming | Adversarial Keyword Test | 	ables/table_eval_adversarial.md |  \\le 0.30$ dampens concept coverage by 40% on superficial answers |
| Threshold Optimization | Threshold Sweep | 	ables/table_eval_threshold.md | Optimal cosine threshold $\\theta = 0.42$ balances precision and recall |
| Metamorphic Robustness | Metamorphic Results | 	ables/metamorphic_results.md | 100% pass on Paraphrase, Irrelevant Addition, Concept Deletion, Negation |
| Error Diagnostics | Confusion Matrix & Gaps | 	ables/table_eval_error_analysis.md | Correctly isolates false positives and asserts misconceptions |
