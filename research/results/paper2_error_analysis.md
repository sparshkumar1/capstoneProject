# Paper 2 Qualitative Error & Boundary Failure Analysis

Comprehensive failure analysis of edge cases across the 64-case benchmark:

## 1. Systematic Failure Categories
1. **Ungrammatical Keyword Chains (CrossEncoder Collocations):** When keywords form multi-word collocations, CrossEncoder gives partial reasoning ($R \approx 0.40 - 0.50$), requiring ScoreValidator caps.
2. **Concise Answers vs Completeness:** Extremely concise answers (e.g. 1 sentence) receive lower sentence-depth scores despite correct core logic.
3. **Subtle Plausible Misconceptions:** Factually incorrect claims that closely mirror correct phrasing require exact misconception entries in rubrics to trigger penalties.

## 2. Category Boundary Scores
- **concise_correct**: Mean = 0.397 (Min: 0.000, Max: 0.740)
- **contradictory**: Mean = 0.281 (Min: 0.098, Max: 0.437)
- **incorrect**: Mean = 0.159 (Min: 0.000, Max: 0.304)
- **keyword_stuffed**: Mean = 0.344 (Min: 0.000, Max: 0.603)
- **misconception**: Mean = 0.228 (Min: 0.000, Max: 0.450)
- **paraphrase**: Mean = 0.361 (Min: 0.124, Max: 0.640)
- **partial_incomplete**: Mean = 0.207 (Min: 0.000, Max: 0.448)
- **suboptimal_correct**: Mean = 0.304 (Min: 0.190, Max: 0.417)
- **verbose_correct**: Mean = 0.591 (Min: 0.292, Max: 0.871)
- **verbose_wrong**: Mean = 0.324 (Min: 0.113, Max: 0.542)
