"""Apply the audit-v2 corrections to paper2/manuscript.md. Each (old, new) pair must match exactly once."""
import re, sys, io
P = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts\paper2\manuscript.md"
t = open(P, encoding="utf-8").read()

# 0) renumber tables II..V -> III..VI in one pass (a new Table II is inserted below)
MAP = {"V": "VI", "IV": "V", "III": "IV", "II": "III"}
t = re.sub(r"Table (V|IV|III|II)\b", lambda m: "Table " + MAP[m.group(1)], t)

E = []
def rep(old, new):
    E.append((old, new))

# --- header comment
rep("<!-- PAPER 2 MANUSCRIPT DRAFT v1 (2026-09-21). Markdown source; venue not final. Exploratory measurement / diagnostic study. -->",
    "<!-- PAPER 2 MANUSCRIPT v2 (2026-09-21, independent-audit pass). Markdown source; venue not final; SUBMISSION GATE: HOLD (see venue/paper2/PAPER2_SUBMISSION_GATE.md). v1 preserved as manuscript_v1_archive.md. -->")

# --- abstract (rewritten; word count checked separately)
old_abs = re.search(r"\*\*Abstract—\*\* .*?\n", t).group(0)
new_abs = ("**Abstract—** Automatic scorers for short technical answers are usually reported with a single agreement figure, which hides how the scorer relates to human judgement across questions, which simpler signals explain its output, and where it errs. We report an exploratory measurement study of one composite evaluator (sentence-embedding similarity, retrieval-based concept coverage and a cross-encoder) on an author-constructed benchmark of 64 answers to 8 questions in 10 answer categories. The human reference score is the mean of three recorded ratings for 54 answers and an adjudicated score for 10. The composite's Spearman correlation with the human reference score was 0.3812 (case-level bootstrap interval [0.1575, 0.5774]; two-level question-and-answer cluster interval [0.1529, 0.6490]). The cross-encoder alone (0.4832) and its combination with the embedding term (0.4884) had higher point estimates than the full composite, with an interval for the difference that includes zero, and a word-count baseline reached 0.4897; word count was competitive on this benchmark, whose categories differ in length. Composite scores were on average 0.134 below the human reference (38 of 64 answers under-scored), most strongly for concise and paraphrased correct answers, while verbose incorrect answers were over-scored. Nineteen of 21 metamorphic relations and 11 of 13 adversarial probes met author-set criteria. The benchmark is small, constructed by the study team and clustered within 8 questions, and rater independence, blinding and ethics records are not documented, so the results are exploratory diagnostics, not validation. We list the controls a confirmatory evaluation would need.\n")
rep(old_abs, new_abs)

# --- introduction
rep("compared its scores with the consensus of three raters, and compared it with its own components and with word-count, lexical-overlap and an upstream cross-encoder baseline.",
    "compared its scores with human reference scores (the mean of three recorded ratings for 54 answers; adjudicated scores for 10), and compared it with its own components and with word-count, lexical-overlap and an upstream cross-encoder baseline.")
rep("The full composite did not correlate better than the cross-encoder alone or than the cross-encoder plus embedding term, a word-count baseline correlated as strongly, correct and partially correct answers were under-scored in every category, and verbose incorrect answers were over-scored.",
    "The full composite had lower point estimates than the cross-encoder alone and the cross-encoder plus embedding term (the intervals for the differences include zero), a word-count baseline correlated as strongly, correct and partially correct categories were under-scored on average, and verbose incorrect answers were over-scored.")
rep("*How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?*",
    "*How does a composite technical-answer evaluator agree with human reference scores and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?*")
rep("(1) agreement with three-rater human consensus reported with case-level and question-aware intervals;",
    "(1) agreement with human reference scores reported with case-level and question-aware intervals;")

# --- related work: shared foundational citation on injected instructions
rep("Studies of automatic scoring report that scorers can be fooled by content-free or adversarially constructed answers [1], [2], [9], [10]. The adversarial probes here (keyword stuffing, injected instructions, negation, contradiction) re-measure this concern for one scorer.",
    "Studies of automatic scoring report that scorers can be fooled by content-free or adversarially constructed answers [1], [2], [9], [10], and studies of LLM-based grading report that injected instructions can change grades [16]. The adversarial probes here (keyword stuffing, injected instructions, negation, contradiction) re-measure the general concern for one similarity-based scorer; the injected-instruction probes are not tests of a language-model grader.")

# --- Section IV: human ratings
rep("The final human score is the mean of the three raters for 54 answers. For 10 answers whose maximum pairwise rater difference exceeded 0.20, an adjudicator (the number and identity of adjudicators are not documented) assigned the final score with a one-sentence rationale; these are described as adjudicated cases, and the label used in the frozen file for them is a file identifier and not a statement about any qualification. The adjudicated cases are all 8 keyword-stuffed answers and 2 partial answers, so the human score for the keyword-stuffed category comes from adjudication alone. We call the resulting score *three-rater human consensus*.",
    "We call the score against which the evaluator is compared the *human reference score*. **For 54 answers the human reference is the mean of three recorded ratings; for 10 answers it is an adjudicated reference score.** The 10 are the answers whose maximum pairwise rater difference exceeded 0.20; an adjudicator (the number and identity of adjudicators are not documented) assigned the score with a one-sentence rationale. The frozen file labels these cases with a file identifier that is not used here as a statement about any qualification, and they are not described as an expert panel, expert consensus, independent adjudication or a gold standard. The 10 adjudicated cases are all 8 keyword-stuffed answers and 2 partial answers, so the human reference for the keyword-stuffed category comes from adjudication alone. The term *three-rater* is used only for statements about the 54 mean-of-three cases or about the three raters' raw ratings.")
rep("The gold scores are closely tied to the construction categories:", "The human reference scores are closely tied to the construction categories:")
rep("| Rating protocol, scale anchors, adjudication rule (difference > 0.20) | frozen and hash-pinned |\n| Raw rating files, final consensus file | hash-pinned; statistics reproduce from the files |",
    "| Rating protocol, scale anchors, adjudication rule (difference > 0.20) | frozen and hash-pinned |\n| Raw rating files, final reference-score file | hash-pinned; statistics reproduce from the files |")

# --- Section V statistics
rep("The primary statistic is Spearman's rank correlation between the evaluator score and the consensus score over the 64 answers.",
    "The primary statistic is Spearman's rank correlation between the evaluator score and the human reference score over the 64 answers.")

# new interval-type table inserted before the Baselines paragraph
rep("**Baselines.** Baselines are word count",
    "**Table II. The three interval types for the composite's Spearman correlation (never interchangeable).**\n\n"
    "| Estimate | Resampling method | Cluster unit | Interval | Interpretive role |\n|---|---|---|---|---|\n"
    "| Composite Spearman ρ = 0.3812 | Case-level percentile bootstrap, B = 2000 | none (64 answers treated as independent) | [0.1575, 0.5774] | Continuity with the earlier record; too narrow if answers cluster |\n"
    "| Same | Two-level bootstrap: draw 8 questions with replacement, then answers within each drawn question; B = 10,000, seed 42 | question, then answer | [0.1529, 0.6490] | Primary question-aware interval; a pragmatic extension, coarse with 8 clusters |\n"
    "| Same | Question-only bootstrap: draw whole questions, keep all their answers; B = 10,000, seed 42 | question | [0.3066, 0.5888] | Sensitivity; ignores answer-level sampling within a question |\n\n"
    "**Baselines.** Baselines are word count")

# --- Results: agreement
rep("### B. Evaluator–human agreement\n\n**Table III. Composite versus three-rater human consensus (n = 64 answers, 8 questions).**",
    "### B. Evaluator–human agreement\n\n**Table III. Composite versus human reference score (n = 64 answers, 8 questions).**")
rep("**Table IV. Component and combination Spearman ρ with the consensus (case-level intervals, B = 2000; n = 64).**",
    "**Table IV. Component and combination Spearman ρ with the human reference score (case-level intervals, B = 2000; n = 64).**")
rep("**Table V. Baselines (Spearman ρ with the consensus; two-level cluster intervals from the X2-B analysis; AUROC for 22 correct-reference versus 34 adversarial answers).**",
    "**Table V. Baselines (Spearman ρ with the human reference score; two-level cluster intervals from the X2-B analysis; AUROC intervals from the same two-level resampling; 22 correct-reference versus 34 adversarial answers).**")
rep("The stored Spearman p-value for the composite is 0.0018863, a case-level, nominal p-value under independent-case assumptions; the answers are clustered within 8 questions, and we do not treat it as confirmatory significance.",
    "The stored Spearman p-value for the composite is 0.0018863: a case-level, nominal p-value under independent-case assumptions. The 64 answers are clustered within 8 questions, so it is not a confirmatory significance test and is not used as evidence of evaluator validity.")
rep("The two-level interval spans roughly 0.15–0.65, which is compatible with weak to moderately strong association.",
    "The two-level interval spans roughly 0.15–0.65, which is compatible with a weak to moderately strong association. Fig. 1 shows the scores behind this coefficient.\n\n![Fig. 1](../figures/fig_p2_scatter.png)\n\n**Fig. 1.** Composite evaluator score against human reference score for the 64 constructed answers (Spearman 0.3812). Ring: adjudicated reference score (10 answers). Source: `paper2_case_level_results.csv`. The figure is descriptive and supports the compression of composite scores relative to the human reference described in Section VI-E.")

# component text
rep("The full composite is not the best-correlating configuration: R alone and S1 + R exceed it. With question-aware resampling the difference between the composite and R alone is −0.102 (two-level 95% interval [−0.2849, 0.1174]) and between the composite and S1 + R is −0.1072 ([−0.2502, 0.0517]); both intervals include zero, so the data neither establish nor exclude a difference.",
    "The full composite is not the configuration with the highest point estimate: R alone and S1 + R have higher Spearman point estimates. With question-aware resampling the difference between the composite and R alone is −0.102 (two-level 95% interval [−0.2849, 0.1174]) and between the composite and S1 + R is −0.1072 ([−0.2502, 0.0517]); both intervals include zero, so the data do not establish a difference (nor exclude one), and neither component is described as statistically superior.")
rep("On this constructed set the composite is not observed to be safer than R alone.",
    "On this constructed set the composite did not accept fewer adversarial answers than R alone.")

# baselines / length
rep("so in this benchmark word count is informative because of how the answers were constructed. Whether natural technical answers show the same length–quality relation is not known. The result raises the possibility that surface properties explain a substantial share of the benchmark's variance; it does not show that the evaluator uses length.",
    "so word count is competitive on this constructed benchmark, consistent with a length confound in how the answers were constructed. The finding is benchmark-level and exploratory: whether natural technical answers show the same length–quality relation is not known, and it does not show that the evaluator is inherently length-dependent or that the model learned length.")
rep("The derived cross-encoder agreed with the consensus more than the upstream checkpoint (ρ difference 0.337, two-level [0.0418, 0.6057]), which is compatible with adaptation toward scoring such answers but cannot be separated from possible training–benchmark overlap (Section III).",
    "The derived cross-encoder had a higher Spearman correlation with the human reference score than the upstream checkpoint (difference 0.337, two-level [0.0418, 0.6057]); this cannot be separated from possible training–benchmark overlap (Section III), and the direction of the difference is not interpreted as evidence about the training data.\n\n![Fig. 3](../figures/fig_p2_forest.png)\n\n**Fig. 3.** Spearman correlation with the human reference score for evaluator configurations and baselines, with two-level cluster intervals (B = 10,000). Composite from X2-A (upper bound 0.6490; 0.6473 in the X2-B run); baselines from X2-B. Rows containing S2 are omitted because the stored two-level interval is for S2_eff. Sources: `x2a_bootstrap_rho.csv`, `metrics_point_ci.csv`.")

# systematic error
rep("The evaluator's scores were on average 0.134 below the human scores; 38 of 64 answers (59.4%) were under-scored (D). Table VI gives category means. These are descriptive, with 2 to 8 answers per category and no intervals.",
    "The evaluator's scores were on average 0.134 below the human reference scores. An answer is *under-scored* when its composite score is lower than its human reference score; 38 of 64 answers (59.4%) were under-scored, none tied and 26 were over-scored (D). Table VI gives category means with sample sizes. These are descriptive, with 2 to 8 answers per category and no intervals.")
rep("Correct and partially correct answers were under-scored in every category, most strongly for concise correct (−0.515) and paraphrased (−0.483) answers, and incorrect categories were over-scored, most for verbose wrong answers (+0.219).",
    "In the five correct and partially correct categories the mean composite score was below the mean human reference, most strongly for concise correct (−0.515) and paraphrased (−0.483) answers, and the mean composite score exceeded the human reference in the five incorrect categories, most for verbose wrong answers (+0.219).")
rep("The mechanism was not tested. We report no fairness analysis and make no fairness claim.",
    "The mechanism was not tested. No fairness analysis was performed, and no fairness claim is made.\n\n![Fig. 2](../figures/fig_p2_category_gap.png)\n\n**Fig. 2.** Mean human reference score and mean composite score by answer category (n per category shown; descriptive, no intervals). Source: `paper2_case_level_results.csv`; the values equal Table VI.")

# pilot overlap
rep("The pattern is compatible with optimism from the pilot-based settings, but it is not a held-out validation and does not establish overlap sensitivity.",
    "Because the overlapping questions were available during earlier development, an optimistic reading of the higher value is possible; the contrast is not a held-out validation and does not establish overlap sensitivity. These are point estimates only.")

# discussion
rep("*Shows:* on this benchmark, the composite's ranking of answers agrees moderately with three-rater consensus,",
    "*Shows:* on this benchmark, the composite's ranking of answers agrees modestly with the human reference scores,")
rep("*Adjacent finding:* on the adversarial set, the composite is not observed to be safer than R alone.",
    "*Adjacent finding:* on the adversarial set, the composite did not accept fewer adversarial answers than R alone.")
rep("*Is p = 0.0018863 invalid because of clustering?* It is a nominal case-level value; we rely on question-aware intervals.",
    "*Does the stored p-value ignore clustering?* Yes; it is a nominal case-level value (Section VI-B), and we rely on question-aware intervals.")
rep("*Shows:* every correct or partially correct category is under-scored, most for concise and paraphrased answers, while verbose incorrect answers are over-scored.",
    "*Shows:* the mean composite score is below the mean human reference in every correct or partially correct category, most for concise and paraphrased answers, while verbose incorrect answers are over-scored on average.")

# limitations
rep("**Human ratings.** Three-rater human consensus; rater identity,", "**Human ratings.** Human reference scores (mean of three recorded ratings for 54 answers; adjudicated scores for 10); rater identity,")

# conclusion
rep("On an author-constructed benchmark, a composite technical-answer evaluator agreed moderately with three-rater human consensus (ρ = 0.3812; two-level interval [0.1529, 0.6490]), had a lower Spearman point estimate than its cross-encoder component (the interval for the difference includes zero) and than a word-count baseline, under-scored correct answers systematically, and over-scored verbose incorrect ones.",
    "On an author-constructed benchmark, a composite technical-answer evaluator agreed modestly with human reference scores (ρ = 0.3812; two-level interval [0.1529, 0.6490]), had a lower Spearman point estimate than its cross-encoder component (the interval for the difference includes zero) and than a word-count baseline, scored correct categories below the human reference on average, and over-scored verbose incorrect answers.")

# references
rep("[2] D. E. Powers, J. C. Burstein, M. Chodorow, M. E. Fowles, and K. Kukich, \"Stumping e-rater: Challenging the validity of automated essay scoring,\" *Comput. Hum. Behav.*, vol. 18, pp. 103–134, 2002.",
    "[2] D. E. Powers, J. C. Burstein, M. Chodorow, M. E. Fowles, and K. Kukich, \"Stumping e-rater: Challenging the validity of automated essay scoring,\" *Comput. Hum. Behav.*, vol. 18, no. 2, pp. 103–134, 2002, doi: 10.1016/S0747-5632(01)00052-8.")
rep("in *Proc. 21st Workshop on Innovative Use of NLP for Building Educational Applications (BEA)*, 2026, arXiv:2605.07647.",
    "arXiv:2605.07647, 2026 (preprint; the arXiv record states acceptance to the 21st BEA workshop, proceedings entry not verified).")
rep("[12] S. Cho, S. Ruberto, and V. Terragni, \"Metamorphic testing of large language models for natural language processing,\" arXiv:2511.02108, 2025 (preprint; venue not verified).",
    "[12] S. Cho, S. Ruberto, and V. Terragni, \"Metamorphic testing of large language models for natural language processing,\" in *Proc. IEEE Int. Conf. Softw. Maint. Evol. (ICSME)*, 2025, pp. 174–186, doi: 10.1109/ICSME64153.2025.00025.")
rep("[11] M. T. Ribeiro, T. Wu, C. Guestrin, and S. Singh, \"Beyond accuracy: Behavioral testing of NLP models with CheckList,\" in *Proc. ACL*, 2020.",
    "[11] M. T. Ribeiro, T. Wu, C. Guestrin, and S. Singh, \"Beyond accuracy: Behavioral testing of NLP models with CheckList,\" in *Proc. 58th Annu. Meeting Assoc. Comput. Linguistics (ACL)*, 2020, pp. 4902–4912, doi: 10.18653/v1/2020.acl-main.442.")
rep("[15] H. Li, C. H. Chen, K. Fan, C. Young-Johnson, S. Lim, and Y. Feng, \"Agreement between large language models and human raters in essay scoring: A research synthesis,\" arXiv:2512.14561, 2025 (preprint).",
    "[15] H. Li, C. H. Chen, K. Fan, C. Young-Johnson, S. Lim, and Y. Feng, \"Agreement between large language models and human raters in essay scoring: A research synthesis,\" arXiv:2512.14561, 2025 (preprint).\n[16] H. Li *et al.*, \"'Important You should give me full credits!': Exploring prompt injection attacks on LLM-based automatic grading systems,\" arXiv:2606.03090, 2026 (preprint).")
rep("[14] T. K. Koo and M. Y. Li, \"A guideline of selecting and reporting intraclass correlation coefficients for reliability research,\" *J. Chiropr. Med.*, vol. 15, no. 2, pp. 155–163, 2016.",
    "[14] T. K. Koo and M. Y. Li, \"A guideline of selecting and reporting intraclass correlation coefficients for reliability research,\" *J. Chiropr. Med.*, vol. 15, no. 2, pp. 155–163, 2016, doi: 10.1016/j.jcm.2016.02.012.")
rep("[13] C. A. Field and A. H. Welsh, \"Bootstrapping clustered data,\" *J. R. Stat. Soc. B*, vol. 69, no. 3, pp. 369–390, 2007.",
    "[13] C. A. Field and A. H. Welsh, \"Bootstrapping clustered data,\" *J. R. Stat. Soc. B*, vol. 69, no. 3, pp. 369–390, 2007, doi: 10.1111/j.1467-9868.2007.00593.x.")

bad = 0
for old, new in E:
    n = t.count(old)
    if n != 1:
        print("MISMATCH (%d):" % n, old[:90].replace("\n", " "))
        bad += 1
    else:
        t = t.replace(old, new)
if bad:
    sys.exit("aborting; nothing written")
open(P, "w", encoding="utf-8").write(t)
print("applied", len(E), "edits")
