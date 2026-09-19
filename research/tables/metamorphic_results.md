# Metamorphic Robustness Testing Results (EXP-EVAL-5)

Metamorphic relation testing evaluating semantic invariance, monotonicity, and adversarial resistance:

| Metamorphic Relation | Description | Expected Constraint | Pass Rate | Mean Metric | Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Paraphrase Invariance** | MG-1_paraphrase | `|Delta score| <= 0.10` | 3/3 (100.0%) | Mean |Delta| = 0.0441 | **PASS** |
| **Irrelevant Text Addition** | MG-2_irrelevant_addition | `Delta score <= +0.05` | 3/3 (100.0%) | Mean Delta = -0.0250 | **PASS** |
| **Keyword Stuffing Resistance** | MG-3_keyword_injection | `Score <= 0.50 (Dampened)` | 1/3 (33.3%) | Mean Score = 0.5537 | **PARTIAL** |
| **Concept Deletion Monotonicity** | MG-4_concept_deletion | `Delta score < 0` | 3/3 (100.0%) | Mean Delta = -0.2646 | **PASS** |
| **Falsification / Negation Inversion** | MG-5_negation_inversion | `Delta score <= -0.20` | 3/3 (100.0%) | Mean Delta = -0.2543 | **PASS** |

## Detailed Test Case Executions

| Case ID | Relation | Base Score | Transformed | Delta | Base R | Trans R | Verdict | Notes |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| META-01 | `MG-1_paraphrase` | 0.6386 | 0.6000 | -0.0386 | 0.619 | 0.577 | **PASS** | |Delta|=0.0386 <= 0.10 |
| META-01 | `MG-2_irrelevant_addition` | 0.6386 | 0.6300 | -0.0086 | 0.619 | 0.602 | **PASS** | Delta=-0.0086 <= +0.05 |
| META-01 | `MG-3_keyword_injection` | 0.6386 | 0.4185 | -0.2201 | 0.619 | 0.388 | **PASS** | Score=0.4185 <= 0.50 (R=0.388, S2=0.500) |
| META-01 | `MG-4_concept_deletion` | 0.6386 | 0.2914 | -0.3472 | 0.619 | 0.284 | **PASS** | Delta=-0.3472 < 0 |
| META-01 | `MG-5_negation_inversion` | 0.6386 | 0.4171 | -0.2215 | 0.619 | 0.364 | **PASS** | Delta=-0.2215 <= -0.20 |
| META-02 | `MG-1_paraphrase` | 0.7016 | 0.6510 | -0.0506 | 0.721 | 0.605 | **PASS** | |Delta|=0.0506 <= 0.10 |
| META-02 | `MG-2_irrelevant_addition` | 0.7016 | 0.6306 | -0.0710 | 0.721 | 0.707 | **PASS** | Delta=-0.0710 <= +0.05 |
| META-02 | `MG-3_keyword_injection` | 0.7016 | 0.5781 | -0.1235 | 0.721 | 0.519 | **FAIL** | Score=0.5781 <= 0.50 (R=0.519, S2=0.750) |
| META-02 | `MG-4_concept_deletion` | 0.7016 | 0.5949 | -0.1067 | 0.721 | 0.551 | **PASS** | Delta=-0.1067 < 0 |
| META-02 | `MG-5_negation_inversion` | 0.7016 | 0.4416 | -0.2600 | 0.721 | 0.429 | **PASS** | Delta=-0.2600 <= -0.20 |
| META-03 | `MG-1_paraphrase` | 0.7827 | 0.7396 | -0.0431 | 0.706 | 0.628 | **PASS** | |Delta|=0.0431 <= 0.10 |
| META-03 | `MG-2_irrelevant_addition` | 0.7827 | 0.7872 | +0.0045 | 0.706 | 0.715 | **PASS** | Delta=+0.0045 <= +0.05 |
| META-03 | `MG-3_keyword_injection` | 0.7827 | 0.6644 | -0.1183 | 0.706 | 0.465 | **FAIL** | Score=0.6644 <= 0.50 (R=0.465, S2=1.000) |
| META-03 | `MG-4_concept_deletion` | 0.7827 | 0.4427 | -0.3400 | 0.706 | 0.374 | **PASS** | Delta=-0.3400 < 0 |
| META-03 | `MG-5_negation_inversion` | 0.7827 | 0.5014 | -0.2813 | 0.706 | 0.344 | **PASS** | Delta=-0.2813 <= -0.20 |
