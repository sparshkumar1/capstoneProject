# Mentor justification — the final three-paper plan (2026-09-21)

Written to be said out loud. Everything here traces to files in the repository; open items are stated as open. Nothing has been submitted, and I am not predicting acceptance anywhere.

## A. 30-second explanation
PrepAIred began as one capstone system for technical-interview practice. We audited it and found that its parts need different evidence, so the publication plan is now three papers. Paper 1 asks what we can actually show about the safety and failure handling of the assessment pipeline. Paper 3 asks, in simulation, what our learned difficulty controller adds over a constant one when both run under the same rule-based guardrail. The third paper is the integrated system itself, and it can only be written after a real study with people, which we have not started. An earlier evaluator paper is on hold.

## B. 1-minute explanation
The original capstone paper described the whole system at once, and some of its numbers came from early stages. During the audit we separated what was measured from what was only designed. Paper 1 is a dependability study: nine fixed attack programs against the code sandbox, fault injection, and a test of whether model-written feedback can reach the score fields, in one environment, with weakened controls so that the checks can be shown to detect a failure. Paper 3 is a controlled simulation: a reinforcement-learning difficulty controller against a controller that always keeps difficulty the same, under the identical guardrail; the result is equivalence within a margin we chose, and it says nothing about real learners. The system paper needs a new study. The evaluator paper, which compared the scoring component with human ratings, is on hold because the records about the raters and consent are incomplete.

## C. 3-minute explanation
Paper 1 goes to IEEE ICETC 2026. It claims only what its tests show: under one Windows, WSL2 and Docker setup, each of nine fixed programs met its criteria in five of five runs, and seven weakened controls showed the checks can register a breach. The ptrace result came from a text filter in the application, not from kernel-level containment, and the paper says so. The executor's status string could not tell contained from breached runs for five attacks, so the decisive evidence is host-side. Two defects on the baseline system, an evaluator outage stored as a zero score and a compiler timeout that left a container running, were absent after repair. That repair and re-test were done by the same AI coding agent that found the defects, so it is regression evidence, not independent replication, and the paper says that too. It reports no learning or user outcome; its link to education is assessment integrity.

Paper 3 goes to HCI International 2027, Adaptive Instructional Systems, which starts with an 800-word proposal due 9 October. The persona-level difference in tracking error between the learned and constant policies is −0.0350 with an interval of −0.0818 to +0.0021, inside a ±0.12 margin that we chose ourselves and cannot justify externally. Equivalence is not "no difference": the policies differ in behaviour and volatility. The guardrail activated on 563 of 1,250 turns but changed the action on only 99, so I do not call activations interventions. It is simulation only.

The system paper is different: it must evaluate the whole system with people. Today the implementation is audio plus text, not video; the hesitation signal at runtime is derived from the confidence score; and there are no constant or rule-based conditions in the live system. We have proposed a design, but ethics requirements are undetermined, so no data collection is allowed yet.

## D. Why three papers from one project?
Because the project has parts that need different evidence, and putting them together forced weak evidence to sit beside strong evidence. Each paper asks one question and reports only what its frozen or newly collected results support.

## E. Why isn't this just one paper?
A single paper would need attack programs, a controller comparison and a human study at once, and its claims would be limited by the weakest part. It would also hide that the controller result is simulation only and the human evidence does not exist yet.

## F. What is the contribution of P1?
Not a new method or escape result. It is a property-by-property account of what was and was not demonstrated for one pipeline, with independent oracles, deliberately weakened controls and attribution to the layer that produced each outcome, including the finding that a status string alone did not identify containment for five attacks.

## G. What is the contribution of the RL paper?
A matched comparison in which the constraint layer is held fixed, a pre-specified equivalence rule, and accounting that separates guardrail activations, action changes and no-ops. It is a statement about evidence needed before an adaptive decision is credited to a learned component, not a claim that the learned controller helps.

## H. What is the contribution of the system paper?
If the study is done: an integrated system described honestly by component status, and a controlled comparison of adaptation conditions on blinded, independently rated human outcomes. Today it has no results, so it has no contribution to claim beyond a design.

## I. Why is Paper 2 no longer part of the final publication set?
The scoring-component paper is exploratory (agreement 0.3812 with human reference scores on 64 constructed answers), and the raters', consent and ethics records are incomplete and cannot be recreated. Keeping it on hold avoids submitting something we cannot document. Its evidence is preserved and none of its claims are merged into the other papers.

## J. What still has to be done before the system paper can be submitted?
An ethics determination and consent process; a design and primary outcome fixed before data collection; runtime conditions for the non-adaptive and rule-based baselines; a decision on wiring the hesitation signal; a held-out question set; recruited participants; independent blinded raters with documented independence; the study and analysis; then the manuscript and a rendered-PDF check. The ICALT deadline is 15 January 2027; whether all of that fits is not established.

## K. What are the main limitations?
P1: one environment, fixed programs, author-written oracles, same-agent regression evidence, an untested follow-up channel, timeout mismatch. P3: authored simulator and personas, author-chosen margin, checkpoints trained against one default candidate for 24,576 steps, training and runtime state mismatches, no learner data, no IRT/CAT/Elo baseline. System: no human evidence, no video, unvalidated confidence score, evaluator not validated as an outcome measure. Across all: AI-use disclosure facts are still to be confirmed by us, and venue rules on AI disclosure and related submissions are partly unverified.

## If asked directly about tools
AI assistance was used in this project, including for coding and for drafting and checking manuscript text, and Paper 1 states that an AI coding agent designed and ran its test campaigns. I am confirming exact tools, versions and the sections they touched, and will disclose them where each venue's policy requires.
