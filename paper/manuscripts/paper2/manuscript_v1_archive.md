<!-- PAPER 2 MANUSCRIPT DRAFT v1 (2026-09-21). Markdown source; venue not final. Exploratory measurement / diagnostic study. -->
<!-- Numbers trace to frozen files under research/results/paper2, research/analysis/phase1/x2_a, research/confirmatory/X2-B and research/data/evaluator_benchmark (see claim_ledger.md). No number was recomputed except the descriptive summaries marked (D) in the text. -->

# Exploratory Measurement of an Evidence-Grounded Technical-Answer Evaluator

*Authors and affiliations: withheld in this draft (anonymity requirement of the target venue is not verified).*

**Abstract—** Automatic scorers for short technical answers are usually reported with a single agreement figure, which hides how the scorer relates to human judgement across questions, which simpler signals explain its output, and where it errs. We report an exploratory measurement study of one composite evaluator (sentence-embedding similarity, retrieval-based concept coverage and a cross-encoder) on an author-constructed benchmark of 64 answers to 8 questions in 10 answer categories, scored by three-rater human consensus. The composite's Spearman correlation with the consensus was 0.3812 (case-level bootstrap 95% interval [0.1575, 0.5774]; two-level question-and-answer cluster interval [0.1529, 0.6490]). The cross-encoder alone (0.4832) and its combination with the embedding term (0.4884) correlated more strongly than the full composite, and a word-count baseline reached 0.4897, with the categories in this benchmark differing in length. Scores of correct and partially correct answers were systematically below the human scores (mean bias −0.134; 38 of 64 answers under-scored), most strongly for concise and paraphrased answers, while verbose incorrect answers were over-scored. 19 of 21 metamorphic relations and 11 of 13 adversarial probes met author-set criteria. The benchmark is small, constructed by the study team, clustered within 8 questions, and its rater independence, blinding and ethics records are not documented, so the results are exploratory diagnostics and not validation of the evaluator. We set out the controls a confirmatory evaluation would need.

**Keywords—** automatic short-answer scoring; evaluator diagnostics; human agreement; cluster bootstrap; length dependence; metamorphic testing

---

## I. Introduction

Automatic scoring of short technical answers is used in interview preparation and coursework, where a numeric score and a feedback message follow a written or spoken answer. The score is usually judged by its agreement with human ratings, summarised in one correlation coefficient. That summary is only informative if it is accompanied by an account of how much of the agreement a trivial signal such as answer length would give, whether the answers were independent of one another, and which kinds of answers the scorer gets systematically wrong.

The literature documents each of these concerns for automatic graders in general. Scorers can be insensitive to content changes and can be gamed by surface features [1], [2], [9], [10]. Language-model judges show surface-form and verbosity sensitivity of varying size [3], [5], [6], and agreement with human raters depends on context and on where in the score range an answer falls [4], [15]. Behavioural testing with invariance and directional tests is an established way to probe such systems [11], [12]. Correlations computed over answers that are clustered within questions require cluster-aware uncertainty [13]. What is less often reported together, for a specific scorer on technical answers, is the agreement figure with its question-aware uncertainty, the simple baselines that explain it, the error pattern by answer type, and the behaviour under controlled perturbations.

This study reports those measurements for one composite evaluator, treating the evaluator as the system under measurement and not as a proposed scoring method. The evaluator combines an embedding-similarity term, a retrieval-based concept-coverage term and a cross-encoder term with fixed weights; hybrid and similarity-based graders are established, and no claim is made about the formulation.

We ran the deployed evaluator once on a benchmark of 64 answers to 8 questions, compared its scores with the consensus of three raters, and compared it with its own components and with word-count, lexical-overlap and an upstream cross-encoder baseline. We reported uncertainty at the case level and with two cluster-aware bootstraps over the 8 questions, examined the errors by answer category, and ran metamorphic and adversarial probes.

The agreement was modest and its question-aware interval was wide (Spearman 0.3812; [0.1529, 0.6490]). The full composite did not correlate better than the cross-encoder alone or than the cross-encoder plus embedding term, a word-count baseline correlated as strongly, correct and partially correct answers were under-scored in every category, and verbose incorrect answers were over-scored.

The research question is: *How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?* The contribution is exploratory measurement and diagnostic evidence: (1) agreement with three-rater human consensus reported with case-level and question-aware intervals; (2) component and baseline comparisons, including the finding that the full composite is not the best-correlating configuration and that a word-count baseline is competitive on this benchmark; (3) a systematic-error analysis by answer category; and (4) metamorphic and adversarial diagnostics with author-set criteria. This is not a validation study; Section VIII sets out why, and Section X lists what a confirmatory evaluation would need to control.

## II. Related Work

**Automatic short-answer scoring and agreement.** Work on automatic grading reports agreement with human raters as the standard outcome, and syntheses of language-model versus human scoring describe agreement as highly context-dependent [15]. A recent study of short-answer scoring reports that models perform well on fully correct and fully incorrect responses but degrade substantially on mid-range responses [4]. Hybrid graders that combine symbolic and language-model components have been reported for short-answer grading [8]. The present evaluator is a similarity-based composite, and the comparison here concerns a specific instance.

**Surface-form and verbosity sensitivity.** A study of code judges reports positive and negative biases from semantically neutral surface variation [3]. Studies of language-model judges name verbosity effects; one reports verbosity bias below 0.011 for 21 models under its protocol [5], and the MT-Bench study names verbosity as a judge bias [6]. Rubric-conditioned grading has been reported to be sensitive to synonym substitution [7]. These sources concern language-model judges and other setups and do not transfer directly to a pointwise similarity-based scorer; they establish that meaning-preserving variation can change automatic scores. The under-scoring of concise and paraphrased answers reported below is therefore a measurement of a known kind of sensitivity in one technical-answer setting.

**Gaming and adversarial probes.** Studies of automatic scoring report that scorers can be fooled by content-free or adversarially constructed answers [1], [2], [9], [10]. The adversarial probes here (keyword stuffing, injected instructions, negation, contradiction) re-measure this concern for one scorer.

**Behavioural and metamorphic testing.** CheckList-style invariance and directional tests and metamorphic testing catalogues for language models provide the method lineage for the perturbation tests here [11], [12].

**Agreement statistics and clustered data.** Intraclass-correlation forms must be specified when reported [14]; resampling for clustered data must respect the cluster structure [13], a reference concerning one-way clustered data, so the two-level bootstrap used here is a pragmatic extension whose behaviour with 8 clusters is coarse.

## III. The Evaluator Under Evaluation

The evaluator scores a candidate answer against a per-question rubric. S1 is the cosine similarity between sentence embeddings of the answer and the rubric text (`all-MiniLM-L6-v2`). S2 is a concept-coverage score computed from a similarity threshold of 0.30 against retrieval vectors built from the rubric's concept groups; S2 is multiplied by 0.60 when the cross-encoder score falls at or below 0.30 (S2_eff). R is the output of a cross-encoder given the question plus rubric reference answer as one text and the candidate answer as the other, mapped to [0, 1]. The base score is 0.15·S1 + 0.35·S2_eff + 0.50·R. The deployed score adds a bonus (0.03 per matched bonus concept) and subtracts a mistake penalty (capped at 0.30), is clipped to [0, 1], and is capped at 0.60 (the default) when a mandatory concept is missing. Grade bands are Poor (<0.40), Average, Good (≥0.60) and Excellent (≥0.75). The component-only configurations in Section VI use the stated weights without the bonus, the penalty or the cap.

The R component is a checkpoint derived from `cross-encoder/ms-marco-MiniLM-L-6-v2`. All 105 tensors were compared with the upstream file: embeddings and encoder layers 0–3 are bit-identical, layers 4–5, the pooler and the classifier differ, and 3,697,153 of 22,713,601 parameters (16.28%) differ in total. The training code, training data and hyperparameters could not be recovered. A stored training-run record lists a joint regression and pairwise-ranking objective with a validation Spearman value, but the data on which it was computed is not recorded, and the repository history contains a second, different fine-tuned checkpoint whose selection is not documented. Overlap between the training data and this benchmark therefore cannot be excluded. The model is not described here as off-the-shelf, and we make no claim about its training data.

## IV. Benchmark and Human Ratings

**Benchmark construction.** The benchmark has 64 answers to 8 questions (8 answers per question), written by the study team in 10 answer categories: concise correct, verbose correct, suboptimal correct, paraphrase, partial/incomplete, keyword-stuffed, contradictory, misconception, verbose wrong and incorrect. The questions cover arrays and hashing, linked lists, trees and breadth-first search, pointers and memory, dynamic programming, graphs and depth-first search, binary search, and operating-systems concurrency (question identifiers 1, 3, 7, 10, 15, 22, 41, 50). The category labels are author-assigned construction labels. The benchmark is author-constructed, small and not representative of natural candidate answers; the answers within a question are not independent.

**Human ratings.** Three raters scored all 64 answers on a continuous [0, 1] scale with anchored bands under a written rating protocol. The rating sheets given to the raters contained the question, the answer and score and comment fields; they contained no category label and no evaluator score. The final human score is the mean of the three raters for 54 answers. For 10 answers whose maximum pairwise rater difference exceeded 0.20, an adjudicator (the number and identity of adjudicators are not documented) assigned the final score with a one-sentence rationale; these are described as adjudicated cases, and the label used in the frozen file for them is a file identifier and not a statement about any qualification. The adjudicated cases are all 8 keyword-stuffed answers and 2 partial answers, so the human score for the keyword-stuffed category comes from adjudication alone. We call the resulting score *three-rater human consensus*.

**Table I. What the record documents about the human ratings.**

| Aspect | Status in the stored record |
|---|---|
| Rating protocol, scale anchors, adjudication rule (difference > 0.20) | frozen and hash-pinned |
| Raw rating files, final consensus file | hash-pinned; statistics reproduce from the files |
| Rating-sheet content | no category label, no evaluator score (header verified) |
| Rater identity, qualifications, recruitment | not documented (roles exist only as labels) |
| Independence from each other and from the study team | not documented |
| Whether raters were blinded beyond the sheet content | not documented; no attestation |
| Consent, compensation, ethics or institutional determination | not documented |
| Adjudicator number, identity, qualifications | not documented |
| When packages were sent and returned | not documented |

The gold scores are closely tied to the construction categories: for each rater, the between-category share of variance is about 0.98–0.99, so the human scores mostly reproduce the intended category ordering. Very high agreement among raters on such items reflects clearly separated categories and does not show that raters would agree on natural, ambiguous technical answers.

**Pilot overlap.** Questions 1, 3, 10 and 41 overlap those of an earlier 20-item single-rater pilot that is superseded and not used as a result here. Section VI-G reports the contrast.

## V. Analysis as Executed

All analyses are exploratory: the results of the deployed evaluator on these items were known before the sensitivity and baseline analyses were configured, and the benchmark has no held-out portion. The evaluator was run once as deployed; no parameter was fitted to the benchmark in the analyses reported here. No multiplicity control is applied.

**Statistics.** The primary statistic is Spearman's rank correlation between the evaluator score and the consensus score over the 64 answers. Kendall's τ-b, Pearson's r, mean absolute error, root mean squared error, Lin's concordance correlation coefficient, Bland–Altman bias and limits, within-question (question-demeaned) Spearman, leave-one-question-out and leave-one-rater-out values are reported as sensitivity analyses. **Three intervals appear in this paper and are not interchangeable.** The *case-level* interval is a percentile bootstrap that resamples the 64 answers as if independent (B = 2000). The *two-level cluster* interval resamples the 8 questions with replacement and then the answers within each drawn question (B = 10,000, seed 42). The *question-only* interval resamples whole questions and keeps all their answers (B = 10,000, seed 42). With 8 clusters, all percentile intervals are coarse. Every stored Spearman p-value in the frozen tables is a case-level, nominal p-value under independent-case assumptions; because answers are clustered within 8 questions, we treat such values as descriptive and do not use them as evidence of robustness.

**Baselines.** Baselines are word count (whitespace tokens), TF-IDF cosine, BM25, reference-token overlap, the upstream cross-encoder and the derived cross-encoder. Discrimination between correct-reference answers (concise correct, verbose correct, suboptimal correct, paraphrase; 22 answers) and adversarial answers (keyword-stuffed, misconception, contradictory, incorrect, verbose wrong; 34 answers) is summarised by the area under the ROC curve (AUROC) using the construction labels; partial answers are excluded. These labels were not derived from human scores or model outputs.

**Perturbation tests.** Three base answers were transformed by seven relations (paraphrase, irrelevant addition, concept deletion, negation, keyword injection, reordering, duplication), 21 relation checks in all, each with an author-set criterion. Thirteen adversarial probes (instruction override, score-manipulation header, keyword and buzzword stuffing, irrelevant jargon, repetition, plausible misconception, contradiction, negation, fake authority, formatting) were each given an author-set score ceiling.

## VI. Results

### A. Human agreement

The three raters' agreement was ICC(2,1) = 0.9528 (95% bootstrap interval [0.9290, 0.9689]), ICC(2,k) = 0.9838 ([0.9751, 0.9894]) and Krippendorff's α (interval scale) = 0.9523 ([0.9281, 0.9685]). These describe agreement on constructed items whose categories are well separated (Section IV) by raters whose independence is not documented, and they are not evidence of agreement on natural answers.

### B. Evaluator–human agreement

**Table II. Composite versus three-rater human consensus (n = 64 answers, 8 questions).**

| Quantity | Value | Interval and its type |
|---|---|---|
| Spearman ρ | 0.3812 | case-level [0.1575, 0.5774]; two-level cluster [0.1529, 0.6490]; question-only [0.3066, 0.5888] |
| Pearson r / Kendall τ-b | 0.4042 / 0.2715 | case-level [0.1846, 0.596] / [0.1168, 0.4295] |
| MAE / RMSE | 0.2920 / 0.3601 | case-level [0.2431, 0.3457] / [0.3008, 0.4184] |
| Bias (composite − human); Bland–Altman limits | −0.1338; [−0.7943, 0.5267] | descriptive |
| Lin's CCC | 0.3297 | descriptive |
| Within-question Spearman (demeaned) | 0.5796 | descriptive |
| Per-question Spearman (8 questions) | 0.44–0.90 (0.4364–0.9048) | descriptive, 8 answers each |
| Leave-one-question-out Spearman | 0.3517–0.4341 | sensitivity |
| Leave-one-rater-out Spearman (all 64 / 54 non-adjudicated) | 0.3552–0.3815 / 0.4147–0.4618 | sensitivity |

The stored Spearman p-value for the composite is 0.0018863, a case-level, nominal p-value under independent-case assumptions; the answers are clustered within 8 questions, and we do not treat it as confirmatory significance. As a question-aware descriptive check, a within-question permutation of the human scores (10,000 permutations) gave a one-sided p of 0.0001 for the composite (the resolution of the procedure). The point estimate and the intervals above are the primary summary. The two-level interval spans roughly 0.15–0.65, which is compatible with weak to moderately strong association.

Agreement within questions (0.5796) exceeded pooled agreement (0.3812). Per-question mean composite scores ranged from 0.066 (question 50) to 0.542 (question 3), whereas per-question mean human scores ranged from 0.385 to 0.492, so part of the lost agreement is a question-level offset in the evaluator's scale.

### C. Components and ablation

**Table III. Component and combination Spearman ρ with the consensus (case-level intervals, B = 2000; n = 64).**

| Configuration | ρ | Case-level 95% interval | MAE |
|---|---|---|---|
| S1 only | 0.2070 | [−0.0317, 0.4125] | 0.3171 |
| S2 only | 0.3021 | [0.0492, 0.5337] | 0.3251 |
| R (cross-encoder) only | 0.4832 | [0.2501, 0.6762] | 0.2763 |
| S1 + S2 (0.30/0.70) | 0.2894 | [0.0470, 0.4956] | 0.3042 |
| S1 + R (0.23/0.77) | 0.4884 | [0.2624, 0.6751] | 0.2790 |
| S2 + R (0.41/0.59) | 0.4171 | [0.1978, 0.6124] | 0.2674 |
| Full composite (with S2 damping, bonus, penalty, cap) | 0.3812 | [0.1575, 0.5774] | 0.2920 |

The full composite is not the best-correlating configuration: R alone and S1 + R exceed it. With question-aware resampling the difference between the composite and R alone is −0.102 (two-level 95% interval [−0.2849, 0.1174]) and between the composite and S1 + R is −0.1072 ([−0.2502, 0.0517]); both intervals include zero, so the data neither establish nor exclude a difference. The two-level intervals for the individual scorers are R alone 0.4832 [0.2460, 0.6983] and S1 + R 0.4884 [0.2537, 0.7120]. The combination rows use renormalised weights and omit the bonus, penalty and cap, so the table compares configurations and does not isolate the effect of any single design element. On the adversarial-versus-correct-reference discrimination (Section V), the composite's AUROC was 0.7206 [0.5836, 0.8926] and R alone 0.7821 [0.6477, 0.9279] (difference −0.0615, [−0.1676, 0.0659]). At the documented grade boundaries the composite accepted 2 of 34 adversarial answers at 0.60 and 0 of 34 at 0.75, while accepting only 0.3636 and 0.1364 of the correct-reference answers; at the same correct-reference acceptance rate R alone accepted 0 of 34 at both thresholds. On this constructed set the composite is not observed to be safer than R alone.

### D. Baselines

**Table IV. Baselines (Spearman ρ with the consensus; two-level cluster intervals from the X2-B analysis; AUROC for 22 correct-reference versus 34 adversarial answers).**

| Scorer | ρ | Two-level 95% interval | AUROC [interval] |
|---|---|---|---|
| Word count | 0.4897 | [0.2186, 0.7080] | 0.8864 [0.7838, 0.9630] |
| Derived cross-encoder (R) | 0.4825 | [0.2440, 0.6953] | 0.7821 [0.6422, 0.9254] |
| Reference-token overlap | 0.4301 | [0.1652, 0.6574] | 0.7834 [0.6334, 0.9249] |
| BM25 | 0.3812 | [0.1374, 0.6266] | 0.7259 [0.5909, 0.8681] |
| TF-IDF cosine | 0.2450 | [−0.0049, 0.5536] | 0.6364 [0.4787, 0.8121] |
| Upstream cross-encoder | 0.1454 | [−0.1532, 0.4535] | 0.5842 [0.4076, 0.7732] |

(The composite's two-level upper bound is 0.6490 in the X2-A run and 0.6473 in the X2-B run because the bootstrap streams differ; 0.6490 is used throughout.) A word-count baseline correlated with the consensus at 0.4897 and separated correct-reference from adversarial answers better (AUROC 0.8864) than the derived cross-encoder (0.7821) or the composite (0.7206). The differences between the derived cross-encoder and the word-count baseline are small relative to their intervals (ρ difference −0.0073 [−0.2217, 0.2148]). BM25 equals the composite's ρ to four decimals; we report this as observed and do not interpret it as equivalence.

The categories of this benchmark differ in length (Table V): (D) mean word counts are 115.6 for verbose correct answers and between 17.6 and 41.4 for every other category, and the incorrect categories are the shortest (keyword-stuffed 17.6, partial 18.4, incorrect 19.2, misconception 19.4), so in this benchmark word count is informative because of how the answers were constructed. Whether natural technical answers show the same length–quality relation is not known. The result raises the possibility that surface properties explain a substantial share of the benchmark's variance; it does not show that the evaluator uses length. The derived cross-encoder agreed with the consensus more than the upstream checkpoint (ρ difference 0.337, two-level [0.0418, 0.6057]), which is compatible with adaptation toward scoring such answers but cannot be separated from possible training–benchmark overlap (Section III).

### E. Systematic error patterns

The evaluator's scores were on average 0.134 below the human scores; 38 of 64 answers (59.4%) were under-scored (D). Table V gives category means. These are descriptive, with 2 to 8 answers per category and no intervals.

**Table V. Category means (descriptive; n = 2–8 per category).**

| Category | n | Mean words (D) | Mean human | Mean composite | Composite − human |
|---|---|---|---|---|---|
| Verbose correct | 8 | 115.6 | 0.984 | 0.591 | −0.393 |
| Concise correct | 8 | 37.5 | 0.912 | 0.397 | −0.515 |
| Paraphrase | 4 | 29.2 | 0.844 | 0.361 | −0.483 |
| Suboptimal correct | 2 | 34.5 | 0.725 | 0.304 | −0.421 |
| Partial/incomplete | 8 | 18.4 | 0.520 | 0.207 | −0.312 |
| Keyword-stuffed | 8 | 17.6 | 0.305 | 0.345 | +0.040 |
| Contradictory | 4 | 25.5 | 0.153 | 0.281 | +0.128 |
| Misconception | 8 | 19.4 | 0.108 | 0.228 | +0.120 |
| Verbose wrong | 8 | 41.4 | 0.105 | 0.324 | +0.219 |
| Incorrect | 6 | 19.2 | 0.087 | 0.159 | +0.072 |

Correct and partially correct answers were under-scored in every category, most strongly for concise correct (−0.515) and paraphrased (−0.483) answers, and incorrect categories were over-scored, most for verbose wrong answers (+0.219). Verbose correct answers were also under-scored (−0.393), so the pattern is a compressed scale that places correct answers in the 0.3–0.6 range, not a penalty confined to concise answers. The concise-correct mean is 0.194 below the verbose-correct mean on the evaluator scale and 0.072 below it on the human scale. The mechanism was not tested. We report no fairness analysis and make no fairness claim.

### F. Perturbation and adversarial diagnostics

Nineteen of 21 metamorphic relations met their criteria. The two failures were both keyword-injection relations (score after injection expected at or below 0.50; observed 0.5781 and 0.6644) on two of the three base answers. Eleven of 13 adversarial probes stayed below their author-set ceilings; the two exceeded were the contradiction probe (0.4617 against a ceiling of 0.35) and the negation probe (0.4328 against 0.25). The criteria and ceilings were set by the study team, and 21 and 13 are small counts, so these are diagnostics against author-chosen bounds and not a robustness estimate.

### G. Pilot overlap

The composite's Spearman was 0.7092 on the four questions overlapping the earlier pilot (32 answers) and 0.4249 on the four others (32 answers); for R alone the values were 0.5838 and 0.4490. These are point estimates on halves that also differ in question difficulty. The pattern is compatible with optimism from the pilot-based settings, but it is not a held-out validation and does not establish overlap sensitivity.

## VII. Discussion

**What the agreement result shows and does not show.** *Shows:* on this benchmark, the composite's ranking of answers agrees moderately with three-rater consensus, more within questions than pooled, with a wide question-aware interval. *Does not show:* agreement on natural answers, on other questions, or with raters of documented independence. *Prior work:* modest, context-dependent agreement is a common finding [15]. *Why it matters:* the pooled figure conceals a question-level scale offset (per-question composite means 0.066–0.542 against human means 0.385–0.492), which a single coefficient would not reveal. *Limit:* 8 questions.

**Why the full composite does not lead.** *Shows:* R alone and S1 + R correlate more strongly than the full composite here, and the difference has an interval including zero. *Does not show:* that the additional terms are useless in other settings; the composite includes a damping rule, a penalty and a cap intended to limit keyword-stuffing failures, and correlation with human scores does not measure that purpose. *Adjacent finding:* on the adversarial set, the composite is not observed to be safer than R alone. *Implication:* the data give no support for the added complexity on this benchmark; a design decision should await a benchmark in which these terms are exercised.

**Why a word-count baseline is competitive.** *Shows:* a trivial signal reaches ρ = 0.4897 and AUROC = 0.8864, and the categories differ in length. *Does not show:* that the evaluator learned length, or that length predicts quality in natural answers. *Implication:* a length-controlled benchmark is needed before agreement figures for this evaluator are interpreted as evidence of content sensitivity.

**Under-scoring of correct answers.** *Shows:* every correct or partially correct category is under-scored, most for concise and paraphrased answers, while verbose incorrect answers are over-scored. *Does not show:* the cause, generality, or any fairness property. *Prior work:* sensitivity of automatic scorers to surface form is documented [1], [3], [6], [7]; this is a measurement of it for one scorer on technical answers. *Limit:* 2–8 answers per category.

**Why publish an exploratory 64-answer study.** The study does not rest on the evaluator performing well. Its content is: multiple component and baseline comparisons on the same data; question-aware uncertainty next to case-level uncertainty; a systematic error decomposition; metamorphic and adversarial tests; the finding that the full composite does not lead and that a word-count baseline competes; the exposure of benchmark construction and length as confounds; and a precise agenda for confirmatory evaluation. These are measurable failure modes and uncertainty sources that later evaluations of technical-answer scorers can control for.

**Anticipated objections.** *Is N = 64 enough, and can 8 questions generalise?* No: the two-level interval spans about 0.15–0.65, the results are exploratory, and generalisation is not claimed. *Who wrote the questions and answers, and could the result be a construction artifact?* The study team constructed the answers by category; the category structure explains most of the human score variance and the length pattern (Sections IV, VI-D); artifact is possible and the benchmark cannot exclude it. *Were the raters blinded, independent, qualified?* Not documented (Table I); we do not claim it. *Why are human agreement figures so high?* The items are separated by construction. *Is p = 0.0018863 invalid because of clustering?* It is a nominal case-level value; we rely on question-aware intervals. *Is the cross-encoder reproducible?* Not fully; its training provenance is unrecoverable. *Is the pilot overlap contaminating the measurement?* It may; the contrast is reported and not resolved. *Why call it an evaluator paper if it is exploratory?* Because the contribution is the measurement and its diagnostics, labelled as exploratory throughout.

## VIII. Threats to Validity and Limitations

**Benchmark.** Author-constructed, 64 answers, 8 questions, answers clustered within questions, 2–8 answers per category, category labels assigned by the authors, category structure length-patterned, and the rubrics and reference material are project assets. The benchmark is not representative of natural candidate answers and is not externally validated.

**Human ratings.** Three-rater human consensus; rater identity, qualifications, independence, blinding beyond the sheet content, consent and ethics or institutional determination are not documented (Table I); the number and identity of adjudicators are not documented; the ratings' timing relative to the protocol freeze is not documented. The human scores are closely tied to the construction categories.

**Statistics.** Exploratory; results known before analysis; only 8 clusters, so cluster-aware intervals are coarse and the two-level bootstrap is a pragmatic extension; no multiplicity control; stored p-values are case-level and nominal.

**Model provenance.** The cross-encoder is a partially fine-tuned derivative with unrecoverable training data and code; overlap with the benchmark cannot be excluded; the Python environment used for the frozen results is not a recorded locked environment.

**Design comparisons.** The composite and the component rows differ in more than weights (damping, bonus, penalty, cap). No language-model-judge baseline was run. Category-level diagnostics rest on 2–8 answers. The metamorphic and adversarial criteria and ceilings are author-set with 21 and 13 checks.

**Not evaluated.** Natural candidate answers, real users, fairness, other question sets, other languages and spoken answers.

## IX. Reproducibility and Artifact Availability

Frozen inputs (benchmark, rating files, consensus file, case-level results) are hash-pinned in the project repository, and the bootstrap analyses were run with fixed seeds (42 for cluster bootstraps, 43 for the permutation test) and B = 10,000 (case-level B = 2000). The evaluator's cross-encoder file has SHA-256 `6a241a55…`. The repository has not been publicly released in this draft. Artifact availability differs from independent reproduction, which has not been performed. The Python environment used for the frozen results violates the project's declared package pins, so exact dependency reproduction is not guaranteed, and the cross-encoder cannot be re-derived from recorded training materials.

## X. Conclusion and Requirements for a Confirmatory Evaluation

On an author-constructed benchmark, a composite technical-answer evaluator agreed moderately with three-rater human consensus (ρ = 0.3812; two-level interval [0.1529, 0.6490]), had a lower Spearman point estimate than its cross-encoder component (the interval for the difference includes zero) and than a word-count baseline, under-scored correct answers systematically, and over-scored verbose incorrect ones. These are exploratory diagnostics, not validation. A confirmatory evaluation would need: many more questions, with the question count set by a precision target agreed in advance; answers not constructed by the scorer's authors and with length decoupled from quality; raters with documented provenance, qualifications, independence and blinding, consent and any required ethics determination; a protocol and analysis plan registered before the ratings, with question-level clustering built into the intervals; questions disjoint from any development or pilot material; documented cross-encoder training provenance; and comparison against a language-model-judge baseline and a length-only baseline.

## References

[1] A. Kabra, M. Bhatia, Y. Kumar, J. J. Li, and R. R. Shah, "Evaluation toolkit for robustness testing of automatic essay scoring systems," arXiv:2007.06796, 2020 (v5 2021; abstract read).
[2] D. E. Powers, J. C. Burstein, M. Chodorow, M. E. Fowles, and K. Kukich, "Stumping e-rater: Challenging the validity of automated essay scoring," *Comput. Hum. Behav.*, vol. 18, pp. 103–134, 2002.
[3] J. Moon, Y. Hwang, D. Lee, T. Kang, Y. Kim, and K. Jung, "Don't judge code by its cover: Exploring biases in LLM judges for code evaluation," in *Findings of the Association for Computational Linguistics: EACL 2026*, 2026, pp. 1364–1389, doi: 10.18653/v1/2026.findings-eacl.70.
[4] A. V. G. Schleifer, M. Ariely, B. Beigman Klebanov, A. Salman, and G. Alexandron, "Quality-conditioned agreement in automated short answer scoring: Mid-range degradation and the impact of task-specific adaptation," in *Proc. 21st Workshop on Innovative Use of NLP for Building Educational Applications (BEA)*, 2026, arXiv:2605.07647.
[5] J. D. Norman, M. U. Rivera, and D. A. Hughes, "Reliability without validity: A systematic, large-scale evaluation of LLM-as-a-judge models across agreement, consistency, and bias," arXiv:2606.19544, 2026 (preprint).
[6] L. Zheng *et al.*, "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena," in *Advances in Neural Information Processing Systems (NeurIPS), Datasets and Benchmarks Track*, 2023, arXiv:2306.05685.
[7] H. Deng, C. Farber, J. Lee, and D. Tang, "Rubric-conditioned LLM grading: Alignment, uncertainty, and robustness," arXiv:2601.08843, 2025 (preprint; abstract level).
[8] A. Willis and A. Third, "AMATI at BEA 2026 Shared Task 2: Automatic short answer grading with inductive logic programming and a large language model," in *Proc. BEA 2026*, 2026, pp. 1217–1223, doi: 10.18653/v1/2026.bea-1.89.
[9] A. Filighera, T. Steuer, and C. Rensing, "Fooling automatic short answer grading systems," in *Artificial Intelligence in Education (AIED 2020)*, Lecture Notes in Computer Science, Springer, 2020, doi: 10.1007/978-3-030-52237-7_15 (title-level use; volume/pages not verified).
[10] S. Yarmohammadtoosky *et al.*, "Enhancing security and strengthening defenses in automated short-answer grading systems," arXiv:2505.00061, 2025 (preprint; title-level use).
[11] M. T. Ribeiro, T. Wu, C. Guestrin, and S. Singh, "Beyond accuracy: Behavioral testing of NLP models with CheckList," in *Proc. ACL*, 2020.
[12] S. Cho, S. Ruberto, and V. Terragni, "Metamorphic testing of large language models for natural language processing," arXiv:2511.02108, 2025 (preprint; venue not verified).
[13] C. A. Field and A. H. Welsh, "Bootstrapping clustered data," *J. R. Stat. Soc. B*, vol. 69, no. 3, pp. 369–390, 2007.
[14] T. K. Koo and M. Y. Li, "A guideline of selecting and reporting intraclass correlation coefficients for reliability research," *J. Chiropr. Med.*, vol. 15, no. 2, pp. 155–163, 2016.
[15] H. Li, C. H. Chen, K. Fan, C. Young-Johnson, S. Lim, and Y. Feng, "Agreement between large language models and human raters in essay scoring: A research synthesis," arXiv:2512.14561, 2025 (preprint).
