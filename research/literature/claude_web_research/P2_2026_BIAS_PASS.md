# Paper 2: current (2025-2026) evaluator-bias pass (gap-closure pass, 2026-09-21)

Literature note only. Nothing here alters the Paper 2 canonical evidence. PrepAIred-side facts are those in the project brief (evaluator 0.15*S1 + 0.35*S2_eff + 0.50*R with S2 x0.6 when R<=0.30; N=64, three raters; rho 0.3812, CI [0.1575, 0.5774]; ICC(2,1) 0.9528; ablation shows R-only 0.4832 and S1+R 0.4884 above the full composite 0.3812; concise-correct and paraphrase answers under-scored; CrossEncoder provenance incomplete). Established phenomena are not called novel because they were measured in technical interview answers.

## Sources inspected in this pass
| Ref | Source | Label | Bears on |
|---|---|---|---|
| [48] | Fujinuma, "Contrastive Decoding Mitigates Score Range Bias in LLM-as-a-Judge," Findings of ACL 2026, pp. 13404-13418, doi 10.18653/v1/2026.findings-acl.657 (arXiv:2510.18196) | V-PAGE for the ACL page; arXiv PDF text read for the quote check | score-range bias |
| [49] | Shi et al., "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge," IJCNLP-AACL 2025, pp. 292-314, doi 10.18653/v1/2025.ijcnlp-long.18 | V-PAGE | position bias |
| [50] | Soumik, "Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines," arXiv:2604.23178 | V-PAGE | style, verbosity, position bias; mitigations |
| [51] | Willis and Third, "AMATI at BEA 2026 Shared Task 2: Automatic Short Answer Grading with Inductive Logic Programming and a Large Language Model," BEA 2026, pp. 1217-1223, doi 10.18653/v1/2026.bea-1.89 | V-PAGE | hybrid symbolic + LLM grading |
| [57] | Report on the BEA 2026 Shared Task on Rubric-based Short Answer Scoring for German, ACL Anthology 2026.bea-1.85 | V-SNIP (search listing) | rubric-based short-answer scoring |
| [52] | Cong et al., "Estimating LLM Grading Ability and Response Difficulty in Automatic Short Answer Grading via Item Response Theory," arXiv:2605.00238 | V-PAGE | semantic alignment and difficulty |
| [53] | Deng, Farber, Lee, Tang, "Rubric-Conditioned LLM Grading: Alignment, Uncertainty, and Robustness," arXiv:2601.08843 | V-PAGE | rubric-conditioned grading; synonym perturbation |
| [18] | Cho, Ruberto, Terragni, metamorphic testing of LLMs for NLP, ICSME 2025 (arXiv:2511.02108) | V-TEXT for arXiv v1; V-SNIP for the conference listing | metamorphic testing |
| [16], [17], [15] | Norman et al.; Schleifer et al.; Moon et al. | V-TEXT for the quotes checked (see QUOTE_AUDIT.md) | as before |

## What each source contributes
- **Score-range bias [48].** LLM judge outputs are "highly sensitive to pre-defined score ranges" (abstract, verified); up to 11.7% relative Spearman improvement with contrastive decoding (their number); primary testbed is summarisation. It concerns LLM judges that emit a number on a stated scale. PrepAIred's evaluator is not an LLM judge and its score is a weighted similarity mixture, so this is contextual: it shows score-scale calibration is a known reliability dimension for judge-style scorers. Not a direct precedent.
- **Position bias [49].** Pairwise and list-wise comparison; not applicable to a pointwise scorer. Background only. No PrepAIred claim depends on it.
- **Verbosity/style bias [50], [16], [20].** Heterogeneous by judge: some prefer longer, some concise [50]; verbosity below 0.011 for 21 judges under one protocol [16]. The conclusion for Paper 2 is unchanged: length and surface-form sensitivity is a documented family with judge-dependent magnitude, so a per-scorer measurement is warranted and is not novel as a phenomenon.
- **Paraphrase / semantic-equivalence robustness.** [53] finds LLM rubric graders sensitive to synonym substitutions (abstract level), and [15] finds code judges biased by semantically neutral surface variations. [52] links harder responses to weaker semantic alignment with the reference answer (a similarity-based signal), though its abstract-level text does not test paraphrases directly. Together they make "meaning-preserving variation changes automatic scores" an established observation; the specific finding that a similarity-composite under-scores concise-correct and paraphrased technical answers was still not found by name in the sources checked.
- **Hybrid symbolic + LLM grading [51].** A neuro-symbolic short-answer grader (ILP rules plus an LLM) exists and its combination improved the 3-way task (German, BEA 2026). Hybrid formulations are therefore an active line; PrepAIred's S1/S2/R mixture (embedding, retrieval, cross-encoder) is not novel as a formulation. The BEA shared task [57] also shows rubric-based scoring benefits from systems that operationalise rubric semantics (per the shared-task summary in search results, not read in full), which is a design dimension the composite (as described in the project brief: similarity, retrieval and cross-encoder terms) does not use.
- **Metamorphic testing [18].** A catalogue of 191 relations for NLP tasks, implemented subset and about 560K tests in arXiv v1 (36 relations, three LLMs); a later listing of the same work reports 38 relations, four LLMs and about 550K tests. The counts differ by version, so cite counts only after choosing a version. Grader-specific metamorphic suites were not found in the searched scope.
- **Human-machine agreement.** Williamson et al. and the LLM-human agreement synthesis [19] stand; no new source changes the recommended treatment.

## Decisions for Paper 2 claims
| Claim | Action | Reason |
|---|---|---|
| Concise/paraphrase under-scoring as a finding | NARROW (unchanged) | Surface-form and paraphrase/synonym sensitivity of automatic graders is established ([15], [20], [53]); present it as a measurement in technical-interview answers |
| Metamorphic-style testing | NARROW (unchanged) | Method established ([18]); grader-specific suite not found |
| Human-agreement methodology (reliability gate, chance-corrected agreement, cluster-aware intervals) | RETAIN as rigor, not novelty | Standard practice |
| Hybrid evaluator formulation | REMOVE as a novelty claim; REFRAME as the system under test | Components standard; hybrid symbolic-plus-LLM graders exist ([51]) |
| Exploratory agreement (rho 0.3812) | RETAIN, exploratory | unchanged |

## Effect on the conclusion
The Paper 2 novelty conclusion is unchanged. Newly found work increases the number of sources documenting surface-form and perturbation sensitivity in automatic graders. Most threatened existing claim: the paraphrase and concise-answer under-scoring finding presented as a discovery (P2-B). Nothing found contradicts the recommended framing as a diagnostic measurement study.

## Not searched or still thin
Technical-domain short-answer scoring (programming and systems concepts), measurement-invariance/psychometric validity of automated scoring, NLI/cross-encoder ASAG beyond carried items, and concept-coverage scorers specifically. Full texts of [50]-[53] were not read.
