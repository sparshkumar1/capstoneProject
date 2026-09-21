# Paper 2 citation map: planned claim -> supporting -> challenging -> wording

| Planned claim | Supporting source(s) | Challenging source(s) | Recommended wording |
|---|---|---|---|
| Exploratory agreement is moderate-to-weak (rho 0.3812, N=64) | [19] agreement is context-dependent; [17] mid-range degradation | none needed | "exploratory; not evidence of human-level grading" |
| Aggregate agreement can hide category-specific error | [17] Schleifer 2026 | none | "aggregate correlation masked category-level errors" |
| Concise-correct/paraphrased answers under-scored | [15] surface-form bias; [20] MT-Bench verbosity | [16] verbosity small for modern LLM judges (different scorer) | "a known class of sensitivity, measured here in a technical-interview setting" |
| Keyword/concept stuffing tests | [22], [23], [24] | none | "re-measurement; not a new attack" |
| Metamorphic-style testing | [18], [8] | [22], [23] (existing adversarial testing) | "metamorphic-style perturbations" |
| Human reliability gate (ICC 0.9528) | [25] | none | "reliability assessed before comparison" |
| Composite below simpler components | ablation in project evidence | none | "safety-hardened composite; accuracy cost reported" |

## Gap-closure additions (2026-09-21)
| Claim | Support | Challenge | Wording note |
|---|---|---|---|
| Paraphrase and concise under-scoring | [15], [53], [52] (abstract level for the last two) | [16] small verbosity effects for some judges | "a known class of surface-form sensitivity" |
| Hybrid evaluator | none needed | [51] hybrid graders exist | describe as the system under test |
| Metamorphic-style tests | [18] (cite one version's counts) | none grader-specific found | "metamorphic-style perturbation tests" |
| Score scale sensitivity | [48] | | contextual only |
