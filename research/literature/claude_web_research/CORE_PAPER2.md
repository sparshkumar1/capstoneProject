# Paper 2 core literature (evaluator validity / measurement), 2026-09-21

Quotes are tool-extracted from opened landing pages; re-check before print. CARRY items are not repeated here (see the earlier master matrix: Mohler 2009/2011, SemEval-2013 Task 7, Sung 2019, Camus 2020, SBERT, ASAG surveys, Filighera 2024, Condor and Pardos 2024, CheckList, Raina 2024, LC-AlpacaEval).

## Core 1. EACL 2026 Findings: biases in LLM judges for code (W2-01)
- Moon, Hwang, Lee, Kang, Kim, Jung. *Don't Judge Code by Its Cover*. Findings of ACL: EACL 2026, pp. 1364-1389, doi 10.18653/v1/2026.findings-eacl.70. **V-PAGE.**
- Question: do LLM judges fairly grade semantically equivalent code with superficial variation? Six bias types; five programming languages; multiple LLM judges.
- Result (authors): "all tested LLM judges are susceptible to both positive and negative biases, resulting in inflated or unfairly low scores"; also vulnerable when asked to generate tests before scoring.
- Overlap: surface-form sensitivity of an automatic evaluator, both inflation and deflation. Difference: judges code, not natural-language interview answers; LLM judge, not an SBERT/FAISS/CrossEncoder composite.
- Use: the current-year peer-reviewed example that surface-variation bias is established; supports framing PrepAIred's bias as a new measurement in a different setting.

## Core 2. Reliability without Validity (W2-02)
- Norman, Rivera, Hughes, arXiv:2606.19544 (Jun 2026, preprint). **V-PAGE.** 21 judges, 9 providers, about 541,000 judgments over MT-Bench, JudgeBench, RewardBench.
- Findings (authors): kappa deflation of 33-41 pp on MT-Bench; rankings shift up to 14 positions; high test-retest reliability with severe position bias; verbosity effect below 0.011 under single pairwise rubrics.
- Relevance: a recent measured result that verbosity bias can be small for modern judges. This weakens any assumption that "verbosity bias" is a robust, universal phenomenon and argues for measuring it per scorer. It also supports reporting chance-corrected agreement. It concerns LLM judges on pairwise chat benchmarks, not PrepAIred's setting.

## Core 3. Quality-conditioned agreement in ASAS (W2-03) - strongest recent direct precedent for "systematic error by answer quality"
- Schleifer, Ariely, Beigman Klebanov, Salman, Alexandron, BEA 2026 (arXiv:2605.07647). **V-PAGE.**
- Finding (authors): "All AI models perform well on fully correct and fully incorrect responses, but exhibit substantial degradation on mid-range responses"; few-shot LLMs worse than fine-tuned models on mid-range; human experts consistently reliable.
- Overlap: automated short-answer scoring with quality-dependent error and human comparison. Difference: biology exam items, fine-tuned/few-shot models, not similarity-composite scorer; degradation is by quality band, not concise/paraphrase/verbose categories.
- Threat to novelty of "systematic scorer error pattern is hidden by aggregate correlation": moderate. Use: cite as evidence that aggregate agreement can mask stratum-specific failure.

## Core 4. LLM-human agreement synthesis (W2-06)
- Li, Chen, Fan, Young-Johnson, Lim, Feng, arXiv:2512.14561 (Dec 2025, rev. May 2026). **V-PAGE.** 65 studies (Jan 2022 to Aug 2025), essay scoring.
- Finding (authors): "LLM-human agreement is highly context-dependent." The earlier note of a "0.30-0.80" range came from a search summary and was never verified (UNVERIFIED; do not use). The phrase "highly context-dependent" itself is verified in the PDF text.
- Relevance: PrepAIred's rho = 0.3812 (N = 64, 3 raters, question-cluster CI [0.1575, 0.5774]) sits at or near the low end of that reported spread, so weak agreement is not out of range, but the synthesis concerns essays and LLM scorers, so it is not a like-for-like benchmark. Do not use it to excuse the value.

## Core 5. Gaming and adversarial studies of graders (W2-09, W2-10, W2-11)
- Yarmohammadtoosky et al., arXiv:2505.00061 (Apr 2025): three gaming strategies against transformer graders in medical education; adversarial training and ensembles improve robustness. **V-PAGE.**
- Filighera, Steuer, Rensing, AIED 2020 (Springer chapter, doi 10.1007/978-3-030-52237-7_15): universal adversarial triggers against ASAG. **V-SNIP + metadata.**
- *The Vulnerability of AI-Based Scoring Systems to Gaming Strategies: A Case Study*, J. Educ. Meas. 2025 (doi 10.1111/jedm.12427). **V-SNIP; page returned 403; authors not verified.**
- Relevance: keyword stuffing/gaming of automated scorers is established; PrepAIred's concept-coverage stuffing tests are a re-measurement, not a new phenomenon.

## Core 6. Judge-bias foundations (W2-07, W2-08)
- Zheng et al., NeurIPS 2023 D&B (arXiv:2306.05685): position, verbosity, self-enhancement bias named; over 80% agreement with human preferences. **V-PAGE.**
- Ye et al., arXiv:2410.02736 (CALM): twelve bias types; venue not shown on the page. **V-PAGE.**
- Use: establish that length and format bias in automatic evaluators is a named, previously measured family.

## Core 7. Metamorphic testing (W2-04, W2-05)
- Cho, Ruberto, Terragni, arXiv:2511.02108 (ICSME 2025): arXiv v1 text (read in full in the gap-closure pass) reports 191 MRs for NLP collected, 36 implemented, three LLMs, about 560K tests (561,267 executions); a later listing of the same work reports 38 MRs, four LLMs, about 550K tests. Counts are version-dependent; cite one version. No grading-specific relations were seen. **V-TEXT (v1).**
- Gupta ReliabilityBench: "action metamorphic relations" for agents. **V-PAGE.**
- Relevance: metamorphic testing of LLMs and agents is established; applying it to an answer grader was not found. PrepAIred's use should be described as behavioural/metamorphic-style perturbation testing of a grader, not as an unprecedented method.

## Core 8. Automated-scoring evaluation framework (W2-12)
- Williamson, Xi, Breyer, EM:IP 31(1):2-13, 2012, doi 10.1111/j.1745-3992.2011.00223.x. **V-SNIP + metadata.** Elements (search summary): fit to purpose, human-machine agreement, association with independent measures, generalizability, subgroup impact.
- Relevance: inter-rater reliability as a gate and human-machine agreement as an evaluation criterion are standard in educational measurement; not novel. The framework also lists dimensions PrepAIred has not covered (independent measures, subgroup impact, generalizability across forms).

## Gap-closure pass additions (2026-09-21)
Full detail: `P2_2026_BIAS_PASS.md` and `QUOTE_AUDIT.md`.
- Score-range bias (Fujinuma, Findings of ACL 2026): LLM judge outputs are "highly sensitive to pre-defined score ranges". Contextual only; PrepAIred's evaluator is not an LLM judge.
- Position bias (Shi et al., IJCNLP-AACL 2025): pairwise/list-wise; not applicable to a pointwise scorer; background only.
- Verbosity and style bias mitigation (Soumik, arXiv:2604.23178): heterogeneous verbosity effects by judge (abstract level).
- Hybrid symbolic + LLM grading exists (AMATI, BEA 2026): a hybrid formulation is not a novelty claim.
- Rubric-conditioned grading (Deng et al., arXiv:2601.08843) reports sensitivity to synonym substitution (abstract level); ASAG response difficulty is linked to weaker semantic alignment with the reference (Cong et al., arXiv:2605.00238, abstract level). These make meaning-preserving variation as a source of score change an established observation.
- Norman et al. verified: "all 21 models register <0.011" for verbosity bias under their protocol; scope is pairwise chat benchmarks.
- Conclusion unchanged; most threatened claim: P2-B (paraphrase and concise-answer under-scoring presented as a discovery).
