# Paper 2 - research question and permitted contribution statements (LOCKED 2026-09-21; replaces the earlier list)
Type: exploratory measurement / diagnostic evaluator study. The contribution is the empirical measurement and diagnostic study, NOT the S1/S2/R formula. S1/S2/R is the system under evaluation, not a novel algorithm. Evidence: research/evidence/final/PAPER2_FINAL_CLAIM_MATRIX.md; literature context: research/literature/claude_web_research/P2_2026_BIAS_PASS.md and CLAIM_CHANGE_QUEUE.md.

## Locked research question
"How does a composite technical-answer evaluator agree with human consensus and simpler component baselines, and which answer types and perturbations reveal systematic evaluator errors?"

## Locked emphasis (in this order)
1. Exploratory agreement measurement [P2-A1..A6]: N=64 author-constructed answers, 8 question clusters, Spearman rho = 0.3812, case-bootstrap 95% CI [0.1575, 0.5774]; question-aware intervals are wider (two-level cluster bootstrap [0.1529, 0.6490]; this, not the p-value, is the inferential-robustness evidence). The stored p = 0.0018863 is a case-level, nominal p-value under independent-case assumptions (answers cluster within 8 questions); it is not a claim of robust confirmatory significance. Human-human: ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff alpha 0.9523 (raters not independently documented; reliability is not validity).
2. Component diagnostics [P2-B1..B5]: R-only 0.4832, S1+R 0.4884, full composite 0.3812. The full composite is not shown superior; frame it as safety-hardened with a measured agreement cost. Composite minus R-only -0.102 [-0.2849, 0.1174] includes zero.
3. Systematic answer-type error analysis [P2-R1]: concise-correct and paraphrased answers are under-scored (as are all correct/partial categories; verbose-wrong is over-scored). Frame this as a technical-interview-domain measurement of an established surface-form/evaluator-bias family, not as the discovery of evaluator bias.
4. Metamorphic/adversarial robustness diagnostics [P2-R2, P2-R3]: 19/21 metamorphic relations; 11/13 adversarial attacks contained against author-set ceilings (author-set, tiny N).

## Supporting record (not a contribution)
The blocked confirmatory round and the synthetic, unregistered precision-planning simulation for a future study.

## Not claimed
A validated evaluator; an accurate grader; human-level grading; reliable automated grading; fairness; bias-freedom; a superior composite; a novel hybrid scoring algorithm; an externally validated benchmark; expert or independent-committee raters; the discovery of evaluator bias.

## Mandatory limitations that travel with these contributions
Author-constructed N=64; 8 question clusters; possible construction/length artifact; pilot overlap; incomplete provenance/ethics records; incomplete CrossEncoder training provenance; systematic concise/paraphrase under-scoring; exploratory, not confirmatory (details in FINAL_LIMITATIONS.md).

Cross-paper ownership (locked): Paper 1 owns containment, authority boundary, tested failure handling and operational behaviour; Paper 2 owns evaluator agreement, evaluator diagnostics, error patterns and robustness; Paper 3 owns learned-policy versus simpler-policy behaviour under shared guardrails. One paper's contribution is not reused as another paper's novelty.
